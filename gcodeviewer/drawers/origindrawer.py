
from PySide6.QtGui import QVector3D

from gcodeviewer.drawers.shaderdrawable import ShaderDrawable
from gcodeviewer.drawers.shaderdrawable import VertexData

sNaN = float('NaN')


class OriginDrawer(ShaderDrawable):
    '''
    '''
    def __init__(self):
        super(OriginDrawer, self).__init__()

        self.m_lines = []

    def updateData(self):
        self.m_lines =  [ 
            # X-axis
            VertexData.fromVectors(QVector3D(0, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(9, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(10, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(8, 0.5, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors( QVector3D(8, 0.5, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(8, -0.5, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors( QVector3D(8, -0.5, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(10, 0, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),

            # Y-axis
            VertexData.fromVectors(QVector3D(0, 0, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0, 9, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0, 10, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0.5, 8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0.5, 8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(-0.5, 8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(-0.5, 8, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0, 10, 0), QVector3D(0.0, 1.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),

            # Z-axis
            VertexData.fromVectors(QVector3D(0, 0, 0), QVector3D(0.0, 0.0, 1.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0, 0, 9), QVector3D(0.0, 0.0, 1.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0, 0, 10), QVector3D(0.0, 0.0, 1.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0.5, 0, 8), QVector3D(0.0, 0.0, 1.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0.5, 0, 8), QVector3D(0.0, 0.0, 1.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(-0.5, 0, 8), QVector3D(0.0, 0.0, 1.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(-0.5, 0, 8), QVector3D(0.0, 0.0, 1.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(0, 0, 10), QVector3D(0.0, 0.0, 1.0), QVector3D(sNaN, sNaN, sNaN)),

            # 2x2 rect
            VertexData.fromVectors(QVector3D(1, 1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(-1, 1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(-1, 1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(-1, -1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(-1, -1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(1, -1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(1, -1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
            VertexData.fromVectors(QVector3D(1, 1, 0), QVector3D(1.0, 0.0, 0.0), QVector3D(sNaN, sNaN, sNaN)),
        ]

        return True



