
import math

from typing import List

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QColor

from gcodeviewer.drawers.shaderdrawable import ShaderDrawable, VertexData
from gcodeviewer.util.util import Util

sNan = 65536.0


class SelectionDrawer(ShaderDrawable):
    '''
    '''
    def __init__(self):
        super(SelectionDrawer, self).__init__()

        self.m_points = []

        self.m_startPosition = QVector3D(0,0,0)
        self.m_endPosition = QVector3D(0,0,0)
        self.m_color = QColor(120,200,200)

    def startPosition(self) -> QVector3D: 
        return self.m_startPosition

    def setStartPosition(self, startPosition: QVector3D):
        self.m_startPosition = startPosition

    def color(self) -> QColor :
        return self.m_color

    def setColor(self, color: QColor) :
        self.m_color = color

    def endPosition(self) -> QVector3D :
        return self.m_endPosition

    def setEndPosition(self, endPosition: QVector3D) :
        self.m_endPosition = endPosition

    def updateData(self) -> bool :
        self.m_points = []

        vertex = VertexData()

        vertex.color = Util.colorToVector(self.m_color)
        vertex.position = self.m_endPosition
        vertex.start = QVector3D(sNan, sNan, self.m_pointSize)
        self.m_points.append(vertex)

        return True

