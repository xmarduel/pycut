
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

from gcodesimulator.python.drawers.gcodedrawer import GcodeDrawer
from gcodesimulator.python.drawers.tooldrawer import ToolDrawer

from gcodesimulator.python.parser.gcodeminiparser import  GcodeMiniParser 

from gcodesimulator.python.widgets.glwidget import GLWidget

sNan = float('NaN')

PROGRESSMINLINES = 10000
PROGRESSSTEP     =  1000


class GLWidgetContainer(QtWidgets.QWidget):
    '''
    '''
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.glwVisualizer = GLWidget(self)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)

        # slider properties
        self.slider.setObjectName(u"sliderSimulator")
        self.slider.valueChanged.connect(self.onSliderValueChanged)
        
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.glwVisualizer)
        layout.addWidget(self.slider)

        self.glwVisualizer.setMinimumHeight(100)
        
        self.m_programFileName = None

        self.m_gcodeMiniParser = GcodeMiniParser()

        topZ = 0.0
        cutterDiameter = 3.175
        cutterHeight = 25.4
        cutterAngle = 180

        fp = open("gcodesimulator/jscut.gcode", "r")
        ggcode = fp.read()
        fp.close()

        self.m_codeDrawer = GcodeDrawer(ggcode, topZ, cutterDiameter, cutterHeight,cutterAngle )
        self.m_codeDrawer.setMiniParser(self.m_gcodeMiniParser)
        self.m_codeDrawer.update()

        #self.m_toolDrawer = ToolDrawer()
        #self.m_toolDrawer.setToolPosition(QVector3D(0, 0, 0))
        #self.m_toolDrawer.update()

        self.glwVisualizer.addDrawable(self.m_codeDrawer)
        #self.glwVisualizer.addDrawable(self.m_toolDrawer)
        
        self.glwVisualizer.fitDrawable()

    def loadFile(self, fileName):
        file = QFile(fileName)

        if not file.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, self.windowTitle(), "Can't open file:\n" + fileName)
            return

        # Set filename
        self.m_programFileName = fileName

        # Read file
        gcode = file.readAll().decode()

        # Load lines
        self.loadData(gcode)

    def loadData(self, simulation_data):

        gcode =  simulation_data["gcode"] 

        # Reset parsers
        #self.m_gcodeMiniParser.reset()

        # Reset code drawer
        self.m_currentDrawer = self.m_codeDrawer
        self.m_codeDrawer.update()
        
        try:
            self.glwVisualizer.fitDrawable(self.m_codeDrawer)
        except Exception:
            pass
        
        # Block parser updates on gcode changes
        self.m_programLoading = True
        self.m_gcodeMiniParser.parse_gcode(gcode)
        self.m_programLoading = False

        # Setup slider
        path_time = self.m_gcodeMiniParser.get_path_time()

        self.slider.setMinimum(0)
        self.slider.setMaximum(path_time)
        self.slider.setSingleStep(path_time / 1000.0)
        
        # Update code drawer
        self.m_codeDrawer.update()
        try:
            self.glwVisualizer.fitDrawable(self.m_codeDrawer)
        except Exception:
            pass

        self.update()

    def onSliderValueChanged(self) :
        '''
        '''
        self.m_codeDrawer.setStopAtTime(self.slider.value())
    


