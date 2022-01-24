
from typing import List
from typing import Any

from PySide6.QtGui import QVector3D

from PySide6.QtGui import QOpenGLFunctions

from PySide6.QtOpenGL import QOpenGLShaderProgram
from PySide6.QtOpenGL import QOpenGLBuffer
from PySide6.QtOpenGL import QOpenGLVertexArrayObject
from PySide6.QtOpenGL import QOpenGLTexture


class ShaderDrawable(QOpenGLFunctions):
    '''
    '''
    sizeof_vertexdata = 36
    sizeof_vector3D = 12
    sizeof_float = 4

    def __init__(self):
        '''
        '''
        QOpenGLFunctions.__init__(self)

        self.m_shader_program : QOpenGLShaderProgram = None
        self.m_texture : QOpenGLTexture = None

        self.m_needsUpdateGeometry = True
        self.m_visible = True
        self.m_lineWidth = 1.0
        self.m_pointSize = 1.0
        
        self.m_lines : List[Any] = []
        self.m_points : List[Any] = []
        self.m_triangles : List[Any] = []
        
        self.m_vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.m_vao = QOpenGLVertexArrayObject()
    
    def init(self):
        # Init openGL functions
        self.initializeOpenGLFunctions()

        # Create buffers
        self.m_vao.create()
        self.m_vbo.create()

    def setShaderProgram(self, shaderProgram):
        self.m_shader_program = shaderProgram

    def update(self):
        self.m_needsUpdateGeometry = True

    def needsUpdateGeometry(self) -> bool:
        return self.m_needsUpdateGeometry

    def updateGeometry(self):
        '''
        overloaded in derived classes
        '''
        pass

    def updateData(self) -> bool:
        '''
        Test data
        '''
        self.m_lines = []
        self.m_points = []
        self.m_triangles = []

        return True

    def draw(self):
        '''
        overloaded in derived classes
        '''
        pass

    def getSizes(self) -> QVector3D:
        return QVector3D(0, 0, 0)

    def getMinimumExtremes(self) -> QVector3D:
        return QVector3D(0, 0, 0)

    def getMaximumExtremes(self) -> QVector3D:
        return QVector3D(0, 0, 0)

    def getVertexCount(self) -> int:
        return len(self.m_lines) + len(self.m_points) + len(self.m_triangles)

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


