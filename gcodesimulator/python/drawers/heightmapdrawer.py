
import math

from typing import List

from enum import Enum

import numpy as np

from PySide6.QtGui import QVector2D
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QColor

from PySide6 import QtOpenGL

from gcodesimulator.python.drawers.shaderdrawable import HeightMapVertexData, ShaderDrawable
from gcodesimulator.python.drawers.gcodedrawer import GcodeDrawer

from gcodesimulator.python.drawers.shaderdrawable import VertexData
from gcodesimulator.python.drawers.shaderdrawable import ToolVertexData

from OpenGL import GL


sNaN = float('NaN')

M_PI = math.acos(-1)


class HeightMapDrawer(ShaderDrawable):
    '''
    '''
    sizeof_vertexdata = 24
    sizeof_vector2D = 8
    sizeof_float = 4
    
    class DrawMode(Enum):
        Vectors = 0
        Raster = 1

    def __init__(self, gcodedrawer: GcodeDrawer):
        '''
        with a pointer of the gcodedrawer
        '''
        super(HeightMapDrawer, self).__init__()

        self.m_drawMode = HeightMapDrawer.DrawMode.Vectors

        self.m_gcodedrawer = gcodedrawer

        self.rotate = QMatrix4x4()
        self.rotate.setToIdentity()

    def updateData(self) -> bool :
        '''
        '''
        if self.m_drawMode == HeightMapDrawer.DrawMode.Vectors:
            return self.prepareVectors()
        elif self.m_drawMode == HeightMapDrawer.DrawMode.Raster:
            return False

    def prepareVectors(self) -> bool:
        # Clear all vertex data
        self.m_lines = []
        self.m_points = []
        self.m_triangles = [] #  resolution * (resolution - 1)
        
        resolution = self.m_gcodedrawer.resolution
        
        for y in range(resolution - 1):
            for x in range(resolution):
                left = x - 1
                if left < 0:
                    left = 0
                right = x + 1
                if right >= resolution:
                    right = resolution - 1
                if not (x & 1) ^ (y & 1):
                    for i in range(3):
                        vertex = HeightMapVertexData()
                        
                        vertex.pos0.setX(left)
                        vertex.pos0.setY(y + 1)
                        vertex.pos1.setX(x)
                        vertex.pos1.setY(y)
                        vertex.pos2.setX(right)
                        vertex.pos2.setY(y+1)
                        
                        if i == 0:
                            vertex.thisPos.setX(left)
                            vertex.thisPos.setY(y+1)
                        elif i == 1:
                            vertex.thisPos.setX(x)
                            vertex.thisPos.setY(y)
                        else:
                            vertex.thisPos.setX(right)
                            vertex.thisPos.setY(y+1)
                        
                        vertex.vertex = i

                        self.m_triangles.append(vertex)
                else:
                    for i in range(3):
                        vertex = HeightMapVertexData()
                        
                        vertex.pos0.setX(left)
                        vertex.pos0.setY(y)
                        vertex.pos1.setX(right)
                        vertex.pos1.setY(y)
                        vertex.pos2.setX(x)
                        vertex.pos2.setY(y+1)

                        if i == 0:
                            vertex.thisPos.setX(left)
                            vertex.thisPos.setY(y)
                        elif i == 1:
                            vertex.thisPos.setX(right)
                            vertex.thisPos.setY(y)
                        else:
                            vertex.thisPos.setX(x)
                            vertex.thisPos.setY(y+1)

                        vertex.vertex = i

                        self.m_triangles.append(vertex)
        

        self.update()

        return True

    def prepareDraw(self, shaderProgram: QtOpenGL.QOpenGLShaderProgram, context):
        '''
        jscut work with the pathBuffer directly
        ... here we work with the vertexData List

        so we do not use the "self.m_gcodedrawer.pathBufferContent",
        but rather the self.m_gcodedrawer.m_triangles list
        '''
        shaderProgram.bind()


        context.glUniform1f(shaderProgram.uniformLocation("resolution"), self.m_gcodedrawer.resolution)
        context.glUniform1f(shaderProgram.uniformLocation("pathScale"), self.m_gcodedrawer.pathScale)
        context.glUniform1f(shaderProgram.uniformLocation("pathMinZ"), self.m_gcodedrawer.pathMinZ)
        context.glUniform1f(shaderProgram.uniformLocation("pathTopZ"), self.m_gcodedrawer.pathTopZ)
        #context.glUniformMatrix4fv(shaderProgram.uniformLocation("rotate"), False, self.rotate)
        #context.glUniform1i(shaderProgram.uniformLocation("heightMap", 0)

        #context.glUniform1f(shaderProgram.uniformLocation("resolution"), self.m_gcodedrawer.resolution)
        #context.glUniform1f(shaderProgram.uniformLocation("pathScale"), self.m_gcodedrawer.pathScale)
        #context.glUniform1f(shaderProgram.uniformLocation("pathMinZ"), self.m_gcodedrawer.pathMinZ)
        #context.glUniform1f(shaderProgram.uniformLocation("pathTopZ"), self.m_gcodedrawer.pathTopZ)
        shaderProgram.setUniformValue("rotate", self.rotate)
        shaderProgram.setUniformValue("heightMap", 0)

    def updateGeometry(self, shaderProgram: QtOpenGL.QOpenGLShaderProgram, context):
        '''
        '''
        self.prepareDraw(shaderProgram, context)

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
            np_array = HeightMapVertexData.VertexDataListToNumPy(vertexData)
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
            # Offset for pos0
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation0 = shaderProgram.attributeLocation("pos0")
            shaderProgram.enableAttributeArray(vertexLocation0)
            shaderProgram.setAttributeBuffer(vertexLocation0, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)

            # Offset for pos1
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = shaderProgram.attributeLocation("pos1")
            shaderProgram.enableAttributeArray(vertexLocation1)
            shaderProgram.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)    

            # Offset for pos2
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = shaderProgram.attributeLocation("pos2")
            shaderProgram.enableAttributeArray(vertexLocation2)
            shaderProgram.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)   

            # Offset for thisPos
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation3 = shaderProgram.attributeLocation("thisPos")
            shaderProgram.enableAttributeArray(vertexLocation3)
            shaderProgram.setAttributeBuffer(vertexLocation3, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)  

            # Offset for vertex
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            vertex = shaderProgram.attributeLocation("vertex")
            shaderProgram.enableAttributeArray(vertex)
            shaderProgram.setAttributeBuffer(vertex, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)
    

            self.m_vao.release()

        self.m_vbo.release()

        self.m_needsUpdateGeometry = False

    def draw(self, shaderProgram: QtOpenGL.QOpenGLShaderProgram):
        '''
        '''
        if self.m_vao.isCreated():
            # Prepare vao
            self.m_vao.bind()
        else:
            # Prepare vbo
            self.m_vbo.bind()

            # Offset for position
            offset = 0

            # Offset for pos0
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation0 = shaderProgram.attributeLocation("pos0")
            shaderProgram.enableAttributeArray(vertexLocation0)
            shaderProgram.setAttributeBuffer(vertexLocation0, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)

            # Offset for pos1
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = shaderProgram.attributeLocation("pos1")
            shaderProgram.enableAttributeArray(vertexLocation1)
            shaderProgram.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)    

            # Offset for pos2
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = shaderProgram.attributeLocation("pos2")
            shaderProgram.enableAttributeArray(vertexLocation2)
            shaderProgram.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)   

            # Offset for thisPos
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation3 = shaderProgram.attributeLocation("thisPos")
            shaderProgram.enableAttributeArray(vertexLocation3)
            shaderProgram.setAttributeBuffer(vertexLocation3, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)  

            # Offset for vertex
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            vertex = shaderProgram.attributeLocation("vertex")
            shaderProgram.enableAttributeArray(vertex)
            shaderProgram.setAttributeBuffer(vertex, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)
    
                
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
        
        shaderProgram.disableAttributeArray("pos0")
        shaderProgram.disableAttributeArray("pos1")
        shaderProgram.disableAttributeArray("pos2")
        shaderProgram.disableAttributeArray("thisPos")
        shaderProgram.disableAttributeArray("vertex")

        shaderProgram.release()
