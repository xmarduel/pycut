
from PySide6.QtGui import QVector3D

from gcodeviewer.drawers.shaderdrawable import ShaderDrawable

from gcodeviewer.drawers.shaderdrawable import VertexDataFrom3V

sNan = 65536.0  # ???


class OriginDrawer(ShaderDrawable):
    '''
    '''
    def __init__(self):
        super(OriginDrawer, self).__init__()

        self.m_lines = []

    def updateData(self):
        self.m_lines =  [ 
            # X-axis
            VertexDataFrom3V(QVector3D(0, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(9, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(10, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(8, 0.5, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V( QVector3D(8, 0.5, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(8, -0.5, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V( QVector3D(8, -0.5, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(10, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),

            # Y-axis
            VertexDataFrom3V(QVector3D(0, 0, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0, 9, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0, 10, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0.5, 8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0.5, 8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(-0.5, 8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(-0.5, 8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0, 10, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNan, sNan, sNan)),

            # Z-axis
            VertexDataFrom3V(QVector3D(0, 0, 0), QVector3D(0.0, 0.0, 1.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0, 0, 9), QVector3D(0.0, 0.0, 1.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0, 0, 10), QVector3D(0.0, 0.0, 1.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0.5, 0, 8), QVector3D(0.0, 0.0, 1.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0.5, 0, 8), QVector3D(0.0, 0.0, 1.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(-0.5, 0, 8), QVector3D(0.0, 0.0, 1.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(-0.5, 0, 8), QVector3D(0.0, 0.0, 1.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(0, 0, 10), QVector3D(0.0, 0.0, 1.0), QVector3D(sNan, sNan, sNan)),

            # 2x2 rect
            VertexDataFrom3V(QVector3D(1, 1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(-1, 1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(-1, 1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(-1, -1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(-1, -1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(1, -1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(1, -1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
            VertexDataFrom3V(QVector3D(1, 1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNan, sNan, sNan)),
        ]

        return True



