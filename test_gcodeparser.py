import argparse
import sys

from typing import List

from PySide6.QtCore import QElapsedTimer
from PySide6.QtCore import QTime
from PySide6.QtCore import Qt
from PySide6.QtCore import QFile
from PySide6.QtCore import QTextStream
from PySide6.QtCore import QIODevice

from PySide6 import QtWidgets
from PySide6 import QtCore

from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QProgressDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QApplication

from PySide6.QtGui import QVector3D
from PySide6.QtCore import qIsNaN

from gcodeviewer.parser.gcodeviewparse import GcodeViewParse 
from gcodeviewer.parser.gcodepreprocessorutils import  GcodePreprocessorUtils  
from gcodeviewer.parser.gcodeparser import  GcodeParser 

from gcodeviewer.tables.gcodetablemodel import GCodeItem
from gcodeviewer.tables.gcodetablemodel import GCodeTableModel

from gcodeviewer.drawers.gcodedrawer import GcodeDrawer

from gcodeviewer.parser.linesegment import LineSegment

from gcodeviewer.util.util import Util
from gcodeviewer.util.util import qQNaN

import ui_testGlWindow


def main(filename):
    fp = open(filename, "r")
    data = fp.readlines()
    fp.close()

    parser = GcodeViewParse()    
    parser.toObjRedux(data, 0.01, True)


PROGRESSMINLINES = 10000
PROGRESSSTEP     =  1000


sNan = 65536.0  # ???


class TestGlWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = ui_testGlWindow.Ui_testGlWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("PyCut")

        self.m_programFileName = None

        self.m_viewParser = GcodeViewParse()
        self.m_programModel = GCodeTableModel()

        self.m_codeDrawer = GcodeDrawer()
        self.m_codeDrawer.setViewParser(self.m_viewParser)

        #self.ui.glwVisualizer.addDrawable(self.m_originDrawer)
        self.ui.glwVisualizer.addDrawable(self.m_codeDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_probeDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_toolDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_heightMapBorderDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_heightMapGridDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_heightMapInterpolationDrawer)
        #self.ui.glwVisualizer.addDrawable(self.m_selectionDrawer)
        self.ui.glwVisualizer.fitDrawable()

        self.loadFile("pycut_gcode.gcode")

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
        # self.m_programModel.data().reserve(data.count()) ->
        self.m_programModel.m_data = [] ## ?? None for _ in range(len(data)) ]

        progress = QProgressDialog ("Opening file...", "Abort", 0, len(data), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setFixedSize(progress.sizeHint())
        if len(data) > PROGRESSMINLINES:
            progress.show()
            progress.setStyleSheet("QProgressBar {text-align: center qproperty-format: \"\"}")

        item = GCodeItem()

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

        print("model filled: %s" % time.elapsed())
        time.start()

        #self.updateProgramEstimatedTime(self.m_viewParser.getLinesFromParser(gp, self.m_settings.arcPrecision(), self.m_settings.arcDegreeMode()))
        #print("view parser filled: %s" % time.elapsed())

        self.m_programLoading = False

        # Set table model
        self.ui.tblProgram.setModel(self.m_programModel)
        self.ui.tblProgram.horizontalHeader().restoreState(headerState)

        # Update tableview
        #connect(self.ui.tblProgram.selectionModel(), SIGNAL(currentChanged(QModelIndex,QModelIndex)), this, SLOT(onTableCurrentChanged(QModelIndex,QModelIndex)))
        self.ui.tblProgram.selectionModel().currentChanged.connect(self.onTableCurrentChanged)
        
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
                idx1 = list[i].getLineNumber()
                idx2 = int(self.m_currentModel.data(self.m_currentModel.index(idx1.row(), 4)))
                list[i].setIsHightlight(idx1 <= idx2)
            
        # Update vertices on current cell changed
        else:

            lineFirst = int(self.m_currentModel.data(self.m_currentModel.index(idx1.row(), 4)))
            lineLast = int(self.m_currentModel.data(self.m_currentModel.index(idx2.row(), 4)))
            if lineLast < lineFirst:
                #qSwap(lineLast, lineFirst)
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
        row = idx1.row()
        xxx = self.m_currentModel.index(idx1.row(), 4)
        
        line = int(self.m_currentModel.data(self.m_currentModel.index(idx1.row(), 4)))
        if line > 0 and lineIndexes[line] != "":
            pos = QVector3D(list[lineIndexes[line][-1]].getEnd())
            if self.m_codeDrawer.getIgnoreZ():
                self.m_selectionDrawer.setEndPosition(QVector3D(pos.x(), pos.y(), 0))
            else:
                self.m_selectionDrawer.setEndPosition(pos)
        else:
            self.m_selectionDrawer.setEndPosition(QVector3D(sNan, sNan, sNan))
        
        self.m_selectionDrawer.update()


#if __name__ =='__main__':
#    '''
#    '''
#    parser = argparse.ArgumentParser(prog="test_gcodeparser", description="test gcode parser in python")

#    # argument
#    parser.add_argument('gcodefilename', help="gcode file to specify")

#    arguments = parser.parse_args()

#    main(arguments.gcodefilename)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    mainwindow = TestGlWindow()
    mainwindow.show()
    sys.exit(app.exec())
