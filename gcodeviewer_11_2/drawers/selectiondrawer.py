from PySide6.QtGui import QVector3D
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPen
from PySide6.QtGui import QBrush
from PySide6.QtGui import QPolygon
from PySide6.QtCore import QPoint

from gcodeviewer_11_2.drawers.shaderdrawable import ShaderDrawable

sNaN = float("NaN")


class SelectionDrawer(ShaderDrawable):
    """ """

    polygon = QPolygon()

    def __init__(self):
        super(SelectionDrawer, self).__init__()

        self.m_points = []

        self.m_position = QVector3D(0, 0, 0)
        self.m_color = QColor(120, 200, 200)

    def position(self) -> QVector3D:
        return self.m_position

    def setPosition(self, position: QVector3D):
        self.m_position = position

    def color(self) -> QColor:
        return self.m_color

    def setColor(self, color: QColor):
        self.m_color = color


    def drawPainter(self, painter: QPainter, projection: QMatrix4x4, ratio: float):
        SelectionDrawer.polygon = QPolygon([ QPoint(0, 0), QPoint(-4, 32), QPoint(4, 32), QPoint(0, 0) ])

        painter.translate((projection.map(self.m_position)).toPoint())
        painter.scale(1, -1)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.m_color))
        painter.setBrush(QBrush(self.m_color))
        painter.drawPolygon(SelectionDrawer.polygon)
