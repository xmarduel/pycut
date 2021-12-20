
import sys

from typing import List

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QOpenGLFunctions

from PySide6.QtOpenGL import QOpenGLShaderProgram
from PySide6.QtOpenGL import QOpenGLBuffer
from PySide6.QtOpenGL import QOpenGLVertexArrayObject
from PySide6.QtOpenGL import QOpenGLTexture

from OpenGL import GL

from util.util import Util
from util.util import qQNaN


sNan = 65536.0  # ???

class VertexData:
    def __init__(self):
        self.position = QVector3D()
        self.color = QVector3D()
        self.start = QVector3D()


class ShaderDrawable(QOpenGLFunctions):
    '''
    '''
    def __init__(self):
        '''
        '''
        super().__init__()

        self.m_lineWidth = 0.0
        self.m_pointSize = 0.0
        self.m_visible = True
        self.m_lines : List[VertexData] = []
        self.m_points : List[VertexData] = []
        self. m_triangles  : List[VertexData]  = []
        self.m_texture : QOpenGLTexture = None

        self.m_vbo : QOpenGLBuffer = None
        self.m_vao : QOpenGLVertexArrayObject = None

        self.m_needsUpdateGeometry = False
    
    def update(self):
        self.m_needsUpdateGeometry = True

    def draw(self, shaderProgram: QOpenGLShaderProgram):
        if not self.m_visible:
            return

        if self.m_vao.isCreated():
            # Prepare vao
            self.m_vao.bind()
        else:
            # Prepare vbo
            self.m_vbo.bind()

            # Offset for position
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation = shaderProgram.attributeLocation("a_position")
            shaderProgram.enableAttributeArray(vertexLocation)
            shaderProgram.setAttributeBuffer(vertexLocation, GL.GL_FLOAT, offset, 3, sys.getsizeof(VertexData))

            # Offset for color
            offset = sys.getsizeof(QVector3D)

            # Tell OpenGL programmable pipeline how to locate vertex color data
            color = shaderProgram.attributeLocation("a_color")
            shaderProgram.enableAttributeArray(color)
            shaderProgram.setAttributeBuffer(color, GL.GL_FLOAT, offset, 3, sys.getsizeof(VertexData))

            # Offset for line start point
            offset += sys.getsizeof(QVector3D)

            # Tell OpenGL programmable pipeline how to locate vertex line start point
            start = shaderProgram.attributeLocation("a_start")
            shaderProgram.enableAttributeArray(start)
            shaderProgram.setAttributeBuffer(start, GL.GL_FLOAT, offset, 3, sys.getsizeof(VertexData))
    

        if len(self.m_triangles) != 0:
            if self.m_texture:
                self.m_texture.bind()
                shaderProgram.setUniformValue("texture", 0)
        
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.m_triangles))

        if len(self.m_lines) != 0:
            GL.glLineWidth(self.m_lineWidth)
            GL.glDrawArrays(GL.GL_LINES, len(self.m_triangles), len(self.m_lines))

        if len(self.m_points) != 0:
            GL.glDrawArrays(GL.GL_POINTS, len(self.m_triangles) + len(self.m_lines), len(self.m_points))

        if self.m_vao.isCreated():
            self.m_vao.release()
        else:
            self.m_vbo.release()

    def needsUpdateGeometry(self) -> bool:
        return self.m_needsUpdateGeometry

    def updateGeometry(self, shaderProgram : QOpenGLShaderProgram = None):
        # Init in context
        if not self.m_vbo.isCreated():
            self.init()

        if self.m_vao.isCreated():
            # Prepare vao
            self.m_vao.bind()

        # Prepare vbo
        self.m_vbo.bind()

        # Update vertex buffer
        if self.updateData():
            # Fill vertices buffer
            vertexData = self.m_triangles # FIXME a copy ??
            vertexData += self.m_lines
            vertexData += self.m_points
            self.m_vbo.allocate(vertexData.constData(), len(vertexData) * sys.getsizeof(VertexData))
        else:
            self.m_vbo.release()        
            if self.m_vao.isCreated():
                self.m_vao.release()
            self.m_needsUpdateGeometry = False
            return

        if self.m_vao.isCreated():
            # Offset for position
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation = shaderProgram.attributeLocation("a_position")
            shaderProgram.enableAttributeArray(vertexLocation)
            shaderProgram.setAttributeBuffer(vertexLocation, GL.GL_FLOAT, offset, 3, sys.getsizeof(VertexData))

            # Offset for color
            offset = sys.getsizeof(QVector3D)

            # Tell OpenGL programmable pipeline how to locate vertex color data
            color = shaderProgram.attributeLocation("a_color")
            shaderProgram.enableAttributeArray(color)
            shaderProgram.setAttributeBuffer(color, GL.GL_FLOAT, offset, 3, sys.getsizeof(VertexData))

            # Offset for line start point
            offset += sys.getsizeof(QVector3D)

            # Tell OpenGL programmable pipeline how to locate vertex line start point
            start = shaderProgram.attributeLocation("a_start")
            shaderProgram.enableAttributeArray(start)
            shaderProgram.setAttributeBuffer(start, GL.GL_FLOAT, offset, 3, sys.getsizeof(VertexData))

            self.m_vao.release()

        self.m_vbo.release()

        self.m_needsUpdateGeometry = False

    def getSizes(self) -> QVector3D:
        return QVector3D(0, 0, 0)

    def getMinimumExtremes(self) -> QVector3D:
        return QVector3D(0, 0, 0)

    def getMaximumExtremes(self) -> QVector3D:
        return QVector3D(0, 0, 0)

    def getVertexCount(self) -> int:
        return self.m_lines.count() + self.m_points.count() + self.m_triangles.count()

    def lineWidth(self) -> float:
        return self.m_lineWidth

    def setLineWidth(self, lineWidth: float):
        self.m_lineWidth = lineWidth

    def visible(self) -> bool:
        return self.m_visible

    def setVisible(self, visible: bool):
        self.m_visible = visible

    def pointSize(self) -> float:
        return self.m_pointSize

    def setPointSize(self, pointSize: float) :
        self.m_pointSize = pointSize

    def updateData(self) -> bool:
        # Test data
        self.m_lineslines = {
            {QVector3D(0, 0, 0), QVector3D(1, 0, 0), QVector3D(sNan, 0, 0)},
            {QVector3D(10, 0, 0), QVector3D(1, 0, 0), QVector3D(sNan, 0, 0)},
            {QVector3D(0, 0, 0), QVector3D(0, 1, 0), QVector3D(sNan, 0, 0)},
            {QVector3D(0, 10, 0), QVector3D(0, 1, 0), QVector3D(sNan, 0, 0)},
            {QVector3D(0, 0, 0), QVector3D(0, 0, 1), QVector3D(sNan, 0, 0)},
            {QVector3D(0, 0, 10), QVector3D(0, 0, 1), QVector3D(sNan, 0, 0)}
        }

        return True

    def init(self):
        # Init openGL functions
        self.initializeOpenGLFunctions()

        # Create buffers
        self.m_vao.create()
        self.m_vbo.create()



