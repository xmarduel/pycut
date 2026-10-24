from PySide6.QtGui import QVector3D

from gcodeviewer_11_2.drawers.shaderdrawable import ShaderDrawable
from gcodeviewer_11_2.drawers.shaderdrawable import VertexData

sNaN = float("NaN")


class OriginDrawer(ShaderDrawable):
    """ """

    def __init__(self):
        super(OriginDrawer, self).__init__()

        self.m_lines = []

        self.setWorldScale(10.0)

    def updateData(self):
        self.m_lines = [
            # X-axis
            VertexData.fromVectors(QVector3D(0.0, 0.0, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(1.0, 0.0, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.8, 0.05, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.8, -0.05, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(10, 0.0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.8, 0.05, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.8, -0.05, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(1.0, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            # Y-axis
            VertexData.fromVectors(QVector3D(0, 0, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0, 1, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(-0.05, 0.8, 0), QVector3D(0.0, 1.0, 0.0),QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.05, 0.8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0, 1.0, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(-0.05, 0.8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.05, 0.8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0, 1.0, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            # Z-axis
            VertexData.fromVectors(QVector3D(0, 0, 0), QVector3D(0.0, 0.0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0, 0, 1.0), QVector3D(0.0, 0.0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0, 0, 1.0), QVector3D(0.0, 0.0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(-0.05, 0, 0.8), QVector3D(0.0, 0.0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(-0.05, 0, 0.8), QVector3D(0.0, 0.0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.05, 0, 0.8), QVector3D(0.0, 0.0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.05, 0, 0.8), QVector3D(0.0, 0.0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0, 0, 1.0), QVector3D(0.0, 0.0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            # 2x2 rect
            VertexData.fromVectors(QVector3D(0.1, 0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(-0.1, 0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(-0.1, 0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(-0.1, -0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(-0.1, -0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.1, -0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.1, -0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.1, 0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),

            # X-label
            VertexData.fromVectors(QVector3D(0.85, 0.3, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(1.0, 0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.85, 0.1, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(1.0, 0.3, 0), QVector3D(1.0, 0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),

            # Y-label
            VertexData.fromVectors(QVector3D(0.1, 1.0, 0), QVector3D(0, 1.0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.175, 0.9, 0), QVector3D(0, 1.0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.175, 0.9, 0), QVector3D(0, 1.0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.25, 1.0, 0), QVector3D(0, 1.0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.175, 0.9, 0), QVector3D(0, 1.0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.175, 0.8, 0), QVector3D(0, 1.0, 0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),

            # Z-label
            VertexData.fromVectors(QVector3D(0.1, 0, 0.8), QVector3D(0, 0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.25, 0, 0.8), QVector3D(0, 0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.1, 0, 0.8), QVector3D(0, 0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.25, 0, 1.0), QVector3D(0, 0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.1, 0, 1.0), QVector3D(0, 0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine),
            VertexData.fromVectors(QVector3D(0.25, 0, 1.0), QVector3D(0, 0, 1.0), QVector3D(), VertexData.VertexDataType.VertexDataTypeLine)
        ]

        return True
