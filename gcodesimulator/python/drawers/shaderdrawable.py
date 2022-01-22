
import ctypes

from typing import List

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QOpenGLFunctions

from PySide6.QtCore import qIsNaN

from PySide6.QtOpenGL import QOpenGLShaderProgram
from PySide6.QtOpenGL import QOpenGLBuffer
from PySide6.QtOpenGL import QOpenGLVertexArrayObject
from PySide6.QtOpenGL import QOpenGLTexture

from OpenGL import GL

from gcodeviewer.util.util import Util

import numpy as np

sNaN = float('NaN')


class VertexData:
    #NB_FLOATS_PER_VERTEX = 12
    NB_FLOATS_PER_VERTEX = 9 

    def __init__(self):
        self.pos1 = QVector3D()
        self.pos2 = QVector3D()
        #self.rawPos = QVector3D()
        self.startTime = sNaN
        self.endTime = sNaN
        self.command = sNaN

    @classmethod
    def VertexDataListToNumPy(cls, vertex_list: List['VertexData']):
        '''
        '''
        def NaN_to_Val(val):
            #if qIsNaN(val):
            #    return 65536.0
            return val

        np_array = np.empty(VertexData.NB_FLOATS_PER_VERTEX * len(vertex_list), dtype=ctypes.c_float)
        
        for k, vdata in enumerate(vertex_list):
            np_array[9*k+0] = NaN_to_Val(vdata.pos1.x())
            np_array[9*k+1] = NaN_to_Val(vdata.pos1.y())
            np_array[9*k+2] = NaN_to_Val(vdata.pos1.z())

            np_array[9*k+3] = NaN_to_Val(vdata.pos2.x())
            np_array[9*k+4] = NaN_to_Val(vdata.pos2.y())
            np_array[9*k+5] = NaN_to_Val(vdata.pos2.z())

            #np_array[12*k+6] = NaN_to_Val(vdata.rawPos.x())
            #np_array[12*k+7] = NaN_to_Val(vdata.rawPos.y())
            #np_array[12*k+8] = NaN_to_Val(vdata.rawPos.z())

            np_array[9*k+6] = NaN_to_Val(vdata.startTime)
            np_array[9*k+7] = NaN_to_Val(vdata.endTime)
            np_array[9*k+8] = NaN_to_Val(vdata.command)

        return np_array


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

        self.m_needsUpdateGeometry = True
        self.m_visible = True
        self.m_lineWidth = 1.0
        self.m_pointSize = 1.0
        self.m_texture : QOpenGLTexture = None
        self.m_lines : List[VertexData] = []
        self.m_points : List[VertexData] = []
        self.m_triangles : List[VertexData] = []
        
        self.m_vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.m_vao = QOpenGLVertexArrayObject()
    
    def init(self):
        # Init openGL functions
        self.initializeOpenGLFunctions()

        # Create buffers
        self.m_vao.create()
        self.m_vbo.create()

    def update(self):
        self.m_needsUpdateGeometry = True

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
            vertexData = []
            vertexData += self.m_triangles
            vertexData += self.m_lines
            vertexData += self.m_points

            # python handling of vbo - with numpy -
            np_array = VertexData.VertexDataListToNumPy(vertexData)
            np_bytes = np_array.tobytes()

            self.m_vbo.allocate(len(np_bytes))
            self.m_vbo.write(0, np_bytes, len(np_bytes))
        else:
            self.m_vbo.release()        
            if self.m_vao.isCreated():
                self.m_vao.release()
            self.m_needsUpdateGeometry = False
            return

        if self.m_vao.isCreated():
            # Offset for position1
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = shaderProgram.attributeLocation("pos1")
            shaderProgram.enableAttributeArray(vertexLocation1)
            shaderProgram.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for position2
            offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex color data
            vertexLocation2 = shaderProgram.attributeLocation("pos2")
            shaderProgram.enableAttributeArray(vertexLocation2)
            shaderProgram.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for rawPos
            #offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex color data
            #vertexRawPos = shaderProgram.attributeLocation("rawPos")
            #shaderProgram.enableAttributeArray(vertexRawPos)
            #shaderProgram.setAttributeBuffer(vertexRawPos, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for line startTime
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex line start time
            startTime = shaderProgram.attributeLocation("startTime")
            shaderProgram.enableAttributeArray(startTime)
            shaderProgram.setAttributeBuffer(startTime, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            # Offset for line endTime
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex line end time
            endTime = shaderProgram.attributeLocation("endTime")
            shaderProgram.enableAttributeArray(endTime)
            shaderProgram.setAttributeBuffer(endTime, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            # Offset for line command
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex line command
            command = shaderProgram.attributeLocation("command")
            shaderProgram.enableAttributeArray(command)
            shaderProgram.setAttributeBuffer(command, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            self.m_vao.release()

        self.m_vbo.release()

        self.m_needsUpdateGeometry = False

    def updateData(self) -> bool:
        '''
        Test data
        '''
        self.m_triangles = [
        ]

        return True

    def draw(self, shaderProgram: QOpenGLShaderProgram):
        if not self.m_visible:
            return

        if self.m_vao.isCreated():
            # Prepare vao
            self.m_vao.bind()
        else:
            # Prepare vbo
            self.m_vbo.bind()

            # Offset for position1
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = shaderProgram.attributeLocation("pos1")
            shaderProgram.enableAttributeArray(vertexLocation1)
            shaderProgram.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for position2
            offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = shaderProgram.attributeLocation("pos2")
            shaderProgram.enableAttributeArray(vertexLocation2)
            shaderProgram.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for raw pos
            #offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            #vertexRawPos = shaderProgram.attributeLocation("rawPos")
            #shaderProgram.enableAttributeArray(vertexRawPos)
            #shaderProgram.setAttributeBuffer(vertexRawPos, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for start time
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            startTime = shaderProgram.attributeLocation("startTime")
            shaderProgram.enableAttributeArray(startTime)
            shaderProgram.setAttributeBuffer(startTime, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            # Offset for end time
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            endTime = shaderProgram.attributeLocation("endTime")
            shaderProgram.enableAttributeArray(endTime)
            shaderProgram.setAttributeBuffer(endTime, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            # Offset for command
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            command = shaderProgram.attributeLocation("command")
            shaderProgram.enableAttributeArray(command)
            shaderProgram.setAttributeBuffer(command, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)
    

        if len(self.m_triangles) != 0:
            if self.m_texture:
                self.m_texture.bind()
                shaderProgram.setUniformValue("texture", 0)
        
            self.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.m_triangles))

        if len(self.m_lines) != 0:
            self.glLineWidth(self.m_lineWidth)
            self.glDrawArrays(GL.GL_LINES, len(self.m_triangles), len(self.m_lines))

        if len(self.m_points) != 0:
            self.glDrawArrays(GL.GL_POINTS, len(self.m_triangles) + len(self.m_lines), len(self.m_points))

        if self.m_vao.isCreated():
            self.m_vao.release()
        else:
            self.m_vbo.release()

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


