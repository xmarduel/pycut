import argparse
import sys

from typing import List

from PySide6.QtCore import QTime
from PySide6.QtCore import Qt
from PySide6.QtCore import QFile
from PySide6.QtCore import QTextStream
from PySide6.QtCore import QIODevice

from PySide6 import QtWidgets

from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QProgressDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QApplication

from PySide6.QtGui import QVector3D
#from PySide6.QtCore import qIsNaN

from gcodeviewer.parser.gcodeviewparse import GcodeViewParse 
from gcodeviewer.parser.gcodepreprocessorutils import  GcodePreprocessorUtils  
from gcodeviewer.parser.gcodeparser import  GcodeParser 

from gcodeviewer.tables.gcodetablemodel import GCodeItem
from gcodeviewer.tables.gcodetablemodel import GCodeTableModel

from gcodeviewer.drawers.gcodedrawer import GcodeDrawer

from gcodeviewer.util.util import Util


def main(filename):
    fp = open(filename, "r")
    data = fp.readlines()
    fp.close()

    parser = GcodeViewParse()    
    parser.toObjRedux(data, 0.01, True)
    
    
if __name__ =='__main__':
    '''
    '''
    parser = argparse.ArgumentParser(prog="test_gcodeparser", description="test gcode parser in python")

    # argument
    parser.add_argument('gcodefilename', help="gcode file to specify")

    arguments = parser.parse_args()

    main(arguments.gcodefilename)


PROGRESSMINLINES = 10000
PROGRESSSTEP     =  1000


class frmMain(QMainWindow):

    def __init__(self):
        super(frmMain, self).__init__()

        self.ui = Ui_testGlWindow()
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
        time = QTime()
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
        self.ui.chkHeightMapUse.setChecked(False)
        self.ui.grpHeightMap.setProperty("overrided", False)
        self.style().unpolish(self.ui.grpHeightMap)
        self.ui.grpHeightMap.ensurePolished()

        # Reset tableview
        headerState = self.ui.tblProgram.horizontalHeader().saveState()
        self.ui.tblProgram.setModel(None)

        # Prepare parser
        gp = GcodeParser()
        gp.setTraverseSpeed(self.m_settings.rapidSpeed())
        if self.m_codeDrawer.getIgnoreZ(): 
            gp.reset(QVector3D(Util.qQNaN(), Util.qQNaN(), 0))

        print("Prepared to load: %s" % time.elapsed())
        time.start()

        # Block parser updates on table changes
        self.m_programLoading = True

        # Prepare model
        self.m_programModel.data().clear()
        self.m_programModel.data().reserve(data.count())

        progress = QProgressDialog ("Opening file...", "Abort", 0, len(data), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setFixedSize(progress.sizeHint())
        if data.count() > PROGRESSMINLINES:
            progress.show()
            progress.setStyleSheet("QProgressBar {text-align: center qproperty-format: \"\"}")

        item = GCodeItem()

        while len(data) > 0:
    
            command = data.pop()

            # Trim command
            trimmed = command.trimmed()

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

                self.m_programModel.data().append(item)
            

            if progress.isVisible() and (data.count() % PROGRESSSTEP == 0) :
                progress.setValue(progress.maximum() - data.count())
                QApplication.instance().processEvents()
                if progress.wasCanceled() :
                    break
            
        progress.close()

        self.m_programModel.insertRow(self.m_programModel.rowCount())

        print("model filled: %s" % time.elapsed())
        time.start()

        self.updateProgramEstimatedTime(self.m_viewParser.getLinesFromParser(gp, self.m_settings.arcPrecision(), self.m_settings.arcDegreeMode()))
        print("view parser filled: %s" % time.elapsed())

        self.m_programLoading = False

        # Set table model
        self.ui.tblProgram.setModel(self.m_programModel)
        self.ui.tblProgram.horizontalHeader().restoreState(headerState)

        # Update tableview
        #connect(self.ui.tblProgram.selectionModel(), SIGNAL(currentChanged(QModelIndex,QModelIndex)), this, SLOT(onTableCurrentChanged(QModelIndex,QModelIndex)))
        self.ui.tblProgram.selectionModel().currentChanged.connect(self.onTableCurrentChanged)
        
        self.ui.tblProgram.selectRow(0)

        #  Update code drawer
        self.m_codeDrawer.update()
        self.ui.glwVisualizer.fitDrawable(self.m_codeDrawer)

        self.resetHeightmap()
        self.updateControlsState()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    mainwindow = frmMain()
    mainwindow.show()
    sys.exit(app.exec())
