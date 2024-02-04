import math

from typing import List

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QColor

from gcodeviewer.drawers.shaderdrawable import ShaderDrawable, VertexData
from gcodeviewer.drawers.shaderdrawable import VertexData
from gcodeviewer.util.util import Util

sNaN = float("NaN")

M_PI = math.acos(-1)


class ToolDrawer(ShaderDrawable):
    """ """

    arcs = 12

    def __init__(self):
        super(ToolDrawer, self).__init__()

        self.m_toolDiameter = 3.0
        self.m_toolLength = 15.0
        self.m_endLength = 3.0
        self.m_toolPosition = QVector3D(0, 0, 0)
        self.m_rotationAngle = 0.0
        self.m_toolAngle = 0.0
        self.m_color = QColor(1.0, 0.6, 4.0)

    def toolDiameter(self) -> float:
        return self.m_toolDiameter

    def setToolDiameter(self, toolDiameter: float):
        self.m_toolDiameter = toolDiameter

    def toolLength(self) -> float:
        return self.m_toolLength

    def setToolLength(self, toolLength: float):
        self.m_toolLength = toolLength

    def toolPosition(self) -> QVector3D:
        return self.m_toolPosition

    def setToolPosition(self, toolPosition: QVector3D):
        self.m_toolPosition = toolPosition

    def rotationAngle(self) -> float:
        return self.m_rotationAngle

    def setRotationAngle(self, rotationAngle: float):
        self.m_rotationAngle = rotationAngle

    def rotate(self, angle: float):
        self.setRotationAngle(self.normalizeAngle(self.m_rotationAngle + angle))

    def toolAngle(self) -> float:
        return self.m_toolAngle

    def setToolAngle(self, toolAngle: float):
        self.m_toolAngle = toolAngle

    def color(self) -> QColor:
        return self.m_color

    def setColor(self, color: QColor):
        self.m_color = color

    def normalizeAngle(self, angle: float) -> float:
        while angle < 0:
            angle += 360
        while angle > 360:
            angle -= 360

        return angle

    def updateData(self) -> bool:
        # Clear data
        self.m_lines = []
        self.m_points = []

        # Prepare vertex
        vertex = VertexData()
        vertex.color = Util.colorToVector(self.m_color)  # QVector3D(1.0, 0.6, 0.0)
        vertex.start = QVector3D(sNaN, sNaN, sNaN)

        # Draw lines
        for i in range(self.arcs):
            x = self.m_toolPosition.x() + self.m_toolDiameter / 2 * math.cos(
                self.m_rotationAngle / 180 * M_PI + (2 * M_PI / self.arcs) * i
            )
            y = self.m_toolPosition.y() + self.m_toolDiameter / 2 * math.sin(
                self.m_rotationAngle / 180 * M_PI + (2 * M_PI / self.arcs) * i
            )

            # Side lines
            vertex.position = QVector3D(
                x, y, self.m_toolPosition.z() + self.m_endLength
            )
            self.m_lines.append(VertexData.clone(vertex))

            vertex.position = QVector3D(
                x, y, self.m_toolPosition.z() + self.m_toolLength
            )
            self.m_lines.append(VertexData.clone(vertex))

            # Bottom lines
            vertex.position = QVector3D(
                self.m_toolPosition.x(),
                self.m_toolPosition.y(),
                self.m_toolPosition.z(),
            )
            self.m_lines.append(VertexData.clone(vertex))
            vertex.position = QVector3D(
                x, y, self.m_toolPosition.z() + self.m_endLength
            )
            self.m_lines.append(VertexData.clone(vertex))

            # Top lines
            vertex.position = QVector3D(
                self.m_toolPosition.x(),
                self.m_toolPosition.y(),
                self.m_toolPosition.z() + self.m_toolLength,
            )
            self.m_lines.append(VertexData.clone(vertex))
            vertex.position = QVector3D(
                x, y, self.m_toolPosition.z() + self.m_toolLength
            )
            self.m_lines.append(VertexData.clone(vertex))

            # Zero Z lines
            vertex.position = QVector3D(
                self.m_toolPosition.x(), self.m_toolPosition.y(), 0
            )
            self.m_lines.append(VertexData.clone(vertex))
            vertex.position = QVector3D(x, y, 0)
            self.m_lines.append(VertexData.clone(vertex))

        # Draw circles
        # Bottom
        self.m_lines += self.createCircle(
            QVector3D(
                self.m_toolPosition.x(),
                self.m_toolPosition.y(),
                self.m_toolPosition.z() + self.m_endLength,
            ),
            self.m_toolDiameter / 2,
            20,
            vertex.color,
        )

        # Top
        self.m_lines += self.createCircle(
            QVector3D(
                self.m_toolPosition.x(),
                self.m_toolPosition.y(),
                self.m_toolPosition.z() + self.m_toolLength,
            ),
            self.m_toolDiameter / 2,
            20,
            vertex.color,
        )

        # Zero Z circle
        if self.m_endLength == 0:
            self.m_lines += self.createCircle(
                QVector3D(self.m_toolPosition.x(), self.m_toolPosition.y(), 0),
                self.m_toolDiameter / 2,
                20,
                vertex.color,
            )

        return True

    def createCircle(
        self, center: QVector3D, radius: float, arcs: int, color: QVector3D
    ) -> List[VertexData]:
        # Vertices
        circle: List[VertexData] = []

        # Prepare vertex
        vertex = VertexData()

        vertex.color = color
        vertex.start = QVector3D(sNaN, sNaN, sNaN)

        # Create line loop
        for i in range(self.arcs + 1):
            angle = 2 * M_PI * i / self.arcs
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)

            if i > 1:
                circle.append(VertexData.clone(circle[-1]))
            elif i == self.arcs:
                circle.append(VertexData.clone(circle[0]))

            vertex.position = QVector3D(x, y, center.z())
            circle.append(VertexData.clone(vertex))

        return circle
