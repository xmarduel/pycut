import argparse
import sys

from typing import List

from PySide6.QtCore import QElapsedTimer
from PySide6.QtCore import QTime
from PySide6.QtCore import Qt
from PySide6.QtCore import QFile
from PySide6.QtCore import QTextStream
from PySide6.QtCore import QIODevice
from PySide6.QtCore import qIsNaN

from PySide6.QtGui import QVector3D

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from PySide6.QtWidgets import QProgressDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QApplication

from gcodeviewer.drawers.gcodedrawer import GcodeDrawer
from gcodeviewer.drawers.origindrawer import OriginDrawer
from gcodeviewer.drawers.tooldrawer import ToolDrawer
from gcodeviewer.drawers.selectiondrawer import SelectionDrawer

from gcodeviewer.parser.gcodeviewparse import GcodeViewParse 
from gcodeviewer.parser.gcodepreprocessorutils import  GcodePreprocessorUtils  
from gcodeviewer.parser.gcodeparser import  GcodeParser 

from gcodeviewer.tables.gcodetablemodel import GCodeItem
from gcodeviewer.tables.gcodetablemodel import GCodeTableModel

from gcodeviewer.parser.linesegment import LineSegment

from gcodeviewer.util.util import qQNaN

from gcodeviewer.widgets.glwidget import GLWidget

from ui_testGlWindow import Ui_testGlWindow


PROGRESSMINLINES = 10000
PROGRESSSTEP     =  1000

sNan = 65536.0  # ???
sNan = float('NaN')


class TestGlWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(TestGlWindow, self).__init__()

        self.ui = Ui_testGlWindow()
        self.ui.setupUi(self)

        self.ui.glwVisualizer = GLWidget(self.ui.frame)
        self.ui.frame.layout().addWidget(self.ui.glwVisualizer)

        self.setWindowTitle("PyCut")

        self.m_programFileName = None

        self.m_viewParser = GcodeViewParse()
        self.m_programModel = GCodeTableModel()

        self.m_codeDrawer = GcodeDrawer()
        self.m_codeDrawer.setViewParser(self.m_viewParser)
        self.m_codeDrawer.update()

        self.m_originDrawer = OriginDrawer()
        self.m_originDrawer.setLineWidth(2.0)
        self.m_originDrawer.update()

        self.m_toolDrawer = ToolDrawer()
        self.m_toolDrawer.setToolPosition(QVector3D(0, 0, 0))
        self.m_toolDrawer.update()

        self.m_selectionDrawer = SelectionDrawer()
        self.m_selectionDrawer.update()



        self.ui.glwVisualizer.addDrawable(self.m_originDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_codeDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_probeDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_toolDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_selectionDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_heightMapBorderDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_heightMapGridDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_heightMapInterpolationDrawer)
        
        self.ui.glwVisualizer.fitDrawable()

        self.ui.glwVisualizer.rotationChanged.connect(self.onVisualizatorRotationChanged)
        #self.ui.glwVisualizer.resized.connect(self.placeVisualizerButtons)
        self.m_programModel.dataChanged.connect(self.onTableCellChanged)

        self.ui.tblProgram.setModel(self.m_programModel)
        self.ui.tblProgram.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        #self.ui.tblProgram.verticalScrollBar().actionTriggered.connect(self.onScroolBarAction)
        self.ui.tblProgram.selectionModel().currentChanged.connect(self.onTableCurrentChanged)   
        # 

        self.ui.tblProgram.hideColumn(2)
        self.ui.tblProgram.hideColumn(3)
        self.ui.tblProgram.hideColumn(4)
        self.ui.tblProgram.hideColumn(5)
    
        self.clearTable()

        #self.loadFile("pycut_gcode.gcode")
        self.loadFile("jscut_gcode.gcode")

    def loadFile(self, fileName):
        file = QFile(fileName)

        if not file.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, self.windowTitle(), "Can't open file:\n" + fileName)
            return

        # Set filename
        self.m_programFileName = fileName

        # Prepare text stream
        textStream = QTextStream(file)

        # Read lines
        data = []
        while not textStream.atEnd():
            data.append(textStream.readLine())

        # Load lines
        self.loadData(data)

    def loadData(self, data: List[str]):
        time = QElapsedTimer()
        time.start()

        # Reset tables
        self.clearTable()
        #self.m_probeModel.clear()
        #self.m_programHeightmapModel.clear()
        self.m_currentModel = self.m_programModel

        # Reset parsers
        self.m_viewParser.reset()
        #self.m_probeParser.reset()

        # Reset code drawer
        self.m_currentDrawer = self.m_codeDrawer
        self.m_codeDrawer.update()
        self.ui.glwVisualizer.fitDrawable(self.m_codeDrawer)
        self.updateProgramEstimatedTime([])

        # Update interface
        #self.ui.chkHeightMapUse.setChecked(False)
        #self.ui.grpHeightMap.setProperty("overrided", False)
        #self.style().unpolish(self.ui.grpHeightMap)
        #self.ui.grpHeightMap.ensurePolished()

        # Reset tableview
        headerState = self.ui.tblProgram.horizontalHeader().saveState()
        self.ui.tblProgram.setModel(None)

        # Prepare parser
        gp = GcodeParser()
        ####gp.setTraverseSpeed(self.m_settings.rapidSpeed())
        gp.setTraverseSpeed(100)

        if self.m_codeDrawer.getIgnoreZ(): 
            gp.reset(QVector3D(qQNaN(), qQNaN(), 0))

        print("Prepared to load: %s" % time.elapsed())
        time.start()

        # Block parser updates on table changes
        self.m_programLoading = True

        # Prepare model
        self.m_programModel.m_data.clear()
        self.m_programModel.m_data = []

        progress = QProgressDialog ("Opening file...", "Abort", 0, len(data), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setFixedSize(progress.sizeHint())
        if len(data) > PROGRESSMINLINES:
            progress.show()
            progress.setStyleSheet("QProgressBar {text-align: center qproperty-format: \"\"}")

        while len(data) > 0:
    
            command = data.pop(0)

            # Trim command
            trimmed = command.strip()

            if len(trimmed) > 0:
                # Split command
                stripped = GcodePreprocessorUtils.removeComment(command)
                args = GcodePreprocessorUtils.splitCommand(stripped)

#               PointSegment *ps = gp.addCommand(args)
                gp.addCommand(args)

    #            if (ps && (qIsNaN(ps.point().x()) || qIsNaN(ps.point().y()) || qIsNaN(ps.point().z())))
    #                       qDebug() << "nan point segment added:" << *ps.point()

                item = GCodeItem()

                item.command = trimmed
                item.state = GCodeItem.States.InQueue
                item.line = gp.getCommandNumber()
                item.args = args

                self.m_programModel.m_data.append(item)
            

            if progress.isVisible() and (len(data) % PROGRESSSTEP == 0) :
                progress.setValue(progress.maximum() - len(data))
                QApplication.instance().processEvents()
                if progress.wasCanceled() :
                    break
            
        progress.close()

        self.m_programModel.insertRow(self.m_programModel.rowCount())

        print("model filled: %s ms." % time.elapsed())
        time.start()

        arcPrecision = 0.0 # TODO self.m_settings.arcPrecision()
        arcDegreeMode = False # TODO self.m_settings.arcDegreeMode()

        all_lines = self.m_viewParser.getLinesFromParser(gp, arcPrecision, arcDegreeMode)

        #self.updateProgramEstimatedTime(all_lines)
        print("view parser filled: %s" % time.elapsed())

        self.m_programLoading = False

        # Set table model
        self.ui.tblProgram.setModel(self.m_programModel)
        self.ui.tblProgram.horizontalHeader().restoreState(headerState)

        # Update tableview
        self.ui.tblProgram.selectRow(0)

        # Update code drawer
        self.m_codeDrawer.update()
        self.ui.glwVisualizer.fitDrawable(self.m_codeDrawer)

        #self.resetHeightmap()
        #self.updateControlsState()

    def clearTable(self):
        self.m_programModel.clear()
        self.m_programModel.insertRow(0)

    def updateProgramEstimatedTime(self, lines: List[LineSegment]) -> QTime:
        time = 0

        for line in lines:
            ls = LineSegment(line)
            #  foreach (LineSegment *ls, lines) {
            length = (ls.getEnd() - ls.getStart()).length()

            if not qIsNaN(length) and not qIsNaN(ls.getSpeed()) and ls.getSpeed() != 0 :
                cond1 = self.ui.slbFeedOverride.isChecked() and not ls.isFastTraverse()
                cond2 =  self.ui.slbRapidOverride.isChecked() and ls.isFastTraverse()
                
                speed = ls.getSpeed()
                val1 = (speed * self.ui.slbFeedOverride.value() / 100)
                val2 = speed
                
                if cond1:
                    time += val1
                else:
                    if cond2:
                        time += val1
                    else:
                        time += val2   # Update for rapid override

#        qDebug() << "length/time:" << length << ((self.ui.chkFeedOverride->isChecked() && !ls->isFastTraverse())
#                                                 ? (ls->getSpeed() * self.ui.txtFeed->value() / 100) : ls->getSpeed())
#                 << time

#        if (qIsNaN(length)) qDebug() << "length nan:" << i << ls->getLineNumber() << ls->getStart() << ls->getEnd()
#        if (qIsNaN(ls->getSpeed())) qDebug() << "speed nan:" << ls->getSpeed()
    

        time *= 60

        t = QTime()

        t.setHMS(0, 0, 0)
        t = t.addSecs(time)

        self.ui.glwVisualizer.setSpendTime(QTime(0, 0, 0))
        self.ui.glwVisualizer.setEstimatedTime(t)

        return t

    def onTableCurrentChanged(self, idx1: QtCore.QModelIndex, idx2: QtCore.QModelIndex) :
        # Update toolpath hightlighting
        if idx1.row() > self.m_currentModel.rowCount() - 2:
            idx1 = self.m_currentModel.index(self.m_currentModel.rowCount() - 2, 0)
        if idx2.row() > self.m_currentModel.rowCount() - 2:
            idx2 = self.m_currentModel.index(self.m_currentModel.rowCount() - 2, 0)

        parser = self.m_currentDrawer.viewParser()
        list = parser.getLineSegmentList()
        lineIndexes = parser.getLinesIndexes()

        # Update linesegments on cell changed
        if not self.m_currentDrawer.geometryUpdated():
            for i in range(len(list)):
                jdx1 = list[i].getLineNumber()
                jdx2 = int(self.m_currentModel.data(self.m_currentModel.index(idx1.row(), 4)))
                list[i].setIsHightlight(jdx1 <= jdx2)
            
        # Update vertices on current cell changed
        else:
            lineFirst = int(self.m_currentModel.data(self.m_currentModel.index(idx1.row(), 4)))
            lineLast = int(self.m_currentModel.data(self.m_currentModel.index(idx2.row(), 4)))
            if lineLast < lineFirst:
                lineLast, lineFirst = lineFirst, lineLast

#        qDebug() << "table current changed" << idx1.row() << idx2.row() << lineFirst << lineLast

            indexes = []
            for i in range(lineFirst + 1, lineLast+1):
                for l in  lineIndexes[i]:
                    list[l].setIsHightlight(idx1.row() > idx2.row())
                    indexes.append(l)

            if len(indexes) == 0:
                self.m_selectionDrawer.setEndPosition(QVector3D(sNan, sNan, sNan))
            else:
                if self.m_codeDrawer.getIgnoreZ():
                    self.m_selectionDrawer.setEndPosition(QVector3D( \
                        list[indexes[-1]].getEnd().x(), \
                        list[indexes[-1]].getEnd().y(), \
                        0))
                else:
                    self.m_selectionDrawer.setEndPosition(list[indexes[-1]].getEnd())
            self.m_selectionDrawer.update()

            if len(indexes) > 0:
                self.m_currentDrawer.update(indexes)
        

        # Update selection marker
        
        line = int(self.m_currentModel.data(self.m_currentModel.index(idx1.row(), 4)))
        if line > 0 and lineIndexes[line] != "":
            pos = list[lineIndexes[line][-1]].getEnd()
            if self.m_codeDrawer.getIgnoreZ():
                self.m_selectionDrawer.setEndPosition(QVector3D(pos.x(), pos.y(), 0))
            else:
                self.m_selectionDrawer.setEndPosition(pos)
        else:
            self.m_selectionDrawer.setEndPosition(QVector3D(sNan, sNan, sNan))
        
        self.m_selectionDrawer.update()

    def onTableCellChanged(self, i1: QtCore.QModelIndex, i2: QtCore.QModelIndex):

        model : GCodeTableModel = self.sender()

        if i1.column() != 1:
            return

        # Inserting new line at end
        if i1.row() == (model.rowCount() - 1) and str(model.data(model.index(i1.row(), 1))) != "":
            model.setData(model.index(model.rowCount() - 1, 2), GCodeItem.States.InQueue)
            model.insertRow(model.rowCount())
            
            if not self.m_programLoading:
                self.ui.tblProgram.setCurrentIndex(model.index(i1.row() + 1, 1))
        # Remove last line
        '''elif (i1.row() != (model.rowCount() - 1) and str(model.data(model.index(i1.row(), 1))) == "": 
            self.ui.tblProgram.setCurrentIndex(model.index(i1.row() + 1, 1))
            self.m_tableModel.removeRow(i1.row())
        '''

        if not self.m_programLoading:

            # Clear cached args
            model.setData(model.index(i1.row(), 5), None)

            # Drop heightmap cache
            #if self.m_currentModel == self.m_programModel:
            #    self.m_programHeightmapModel.clear()

            # Update visualizer
            self.updateParser()

            # Hightlight w/o current cell changed event (double hightlight on current cell changed)
            alist = self.m_viewParser.getLineSegmentList()
            
            #for (int i = 0 i < list.count() and list[i].getLineNumber() <= m_currentModel.data(m_currentModel.index(i1.row(), 4)).toInt() i++):
            #    alist[i].setIsHightlight(True)

            k = 0
            while True:
                if not (k < len(alist) and alist[k].getLineNumber() <= (int)(self.m_currentModel.data(self.m_currentModel.index(i1.row(), 4)))):
                    break

                alist[k].setIsHightlight(True)

                k += 1

    def updateParser(self):

        time = QElapsedTimer()

        print("updating parser:")
        time.start()

        parser = self.m_currentDrawer.viewParser()

        gp = GcodeParser()
        #gp.setTraverseSpeed(m_settings.rapidSpeed())
        gp.setTraverseSpeed(100)
        if self.m_codeDrawer.getIgnoreZ():
            gp.reset(QVector3D(qQNaN(), qQNaN(), 0))

        self.ui.tblProgram.setUpdatesEnabled(False)

        progress = QProgressDialog("Updating...", "Abort", 0, self.m_currentModel.rowCount() - 2, self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setFixedSize(progress.sizeHint())

        if self.m_currentModel.rowCount() > PROGRESSMINLINES:
            progress.show()
            progress.setStyleSheet("QProgressBar {text-align: center qproperty-format: \"\"}")

        for i in range(self.m_currentModel.rowCount()):
            # Get stored args
            args = self.m_currentModel.m_data[i].args

            # Store args if none
            if len(args) == 0: 
                stripped = GcodePreprocessorUtils.removeComment(self.m_currentModel.m_data[i].command)
                args = GcodePreprocessorUtils.splitCommand(stripped)
                self.m_currentModel.m_data[i].args = args

            # Add command to parser
            gp.addCommand(args)

            # Update table model
            self.m_currentModel.m_data[i].state = GCodeItem.States.InQueue
            self.m_currentModel.m_data[i].response = ""
            self.m_currentModel.m_data[i].line = gp.getCommandNumber()

            if progress.isVisible() and (i % PROGRESSSTEP == 0):
                progress.setValue(i)
                QApplication.instance().processEvents()
                if progress.wasCanceled():
                    break
        
        progress.close()

        self.ui.tblProgram.setUpdatesEnabled(True)

        parser.reset()

        
        arcPrecision = 0.0 # TODO self.m_settings.arcPrecision()
        arcDegreeMode = False # TODO self.m_settings.arcDegreeMode()
        
        all_lines = parser.getLinesFromParser(gp, arcPrecision(), arcDegreeMode())
        
        #self.updateProgramEstimatedTime(all_lines)

        self.m_currentDrawer.update()
        self.ui.glwVisualizer.updateExtremes(self.m_currentDrawer)
        #self.updateControlsState()

        if self.m_currentModel == self.m_programModel:
            self.m_fileChanged = True

        print("Update parser time: %s" % time.elapsed())

    def onVisualizatorRotationChanged(self):
        pass
        #self.ui.cmdIsometric.setChecked(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    mainwindow = TestGlWindow()
    mainwindow.show()
    sys.exit(app.exec())
