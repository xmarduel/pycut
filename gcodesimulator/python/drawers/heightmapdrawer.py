
import math
from enum import Enum
import ctypes

from typing import List

import numpy as np

from OpenGL import GL

from PySide6.QtGui import QVector2D
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QOpenGLFunctions
from PySide6.QtCore import QSize


from PySide6 import QtOpenGL

from gcodesimulator.python.drawers.shaderdrawable import ShaderDrawable
from gcodesimulator.python.drawers.gcodedrawer import GcodeDrawer

sNaN = float('NaN')


class HeightMapVertexData:
    NB_FLOATS_PER_VERTEX = 9 

    def __init__(self):
        self.pos0 = QVector2D()
        self.pos1 = QVector2D()
        self.pos2 = QVector2D()
        self.thisPos = QVector2D()
        self.vertex = sNaN

    @classmethod
    def VertexDataListToNumPy(cls, vertex_list: List['HeightMapVertexData']):
        '''
        '''
        def NaN_to_Val(val):
            #if qIsNaN(val):
            #    return 65536.0
            return val

        np_array = np.empty(cls.NB_FLOATS_PER_VERTEX * len(vertex_list), dtype=ctypes.c_float)
        
        for k, vdata in enumerate(vertex_list):
            np_array[9*k+0] = NaN_to_Val(vdata.pos0.x())
            np_array[9*k+1] = NaN_to_Val(vdata.pos0.y())
           
            np_array[9*k+2] = NaN_to_Val(vdata.pos1.x())
            np_array[9*k+3] = NaN_to_Val(vdata.pos1.y())

            np_array[9*k+4] = NaN_to_Val(vdata.pos2.x())
            np_array[9*k+5] = NaN_to_Val(vdata.pos2.y())
            
            np_array[9*k+6] = NaN_to_Val(vdata.thisPos.x())
            np_array[9*k+7] = NaN_to_Val(vdata.thisPos.y())

            np_array[9*k+8] = NaN_to_Val(vdata.vertex)

        return np_array


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

        self.pathFramebuffer = None
        self.pathRgbaTexture = self.m_texture  # in base class

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
        self.m_triangles = [] #  resolution * (resolution - 1) * 3
        
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

    def prepareDraw(self, context: QOpenGLFunctions):
        '''
        jscut work with the pathBuffer directly
        ... here we work with the vertexData List

        so we do not use the "self.m_gcodedrawer.pathBufferContent",
        but rather the self.m_gcodedrawer.m_triangles list
        '''
        self.m_shader_program.bind()


        context.glUniform1f(self.m_shader_program.uniformLocation("resolution"), self.m_gcodedrawer.resolution)
        context.glUniform1f(self.m_shader_program.uniformLocation("pathScale"), self.m_gcodedrawer.pathScale)
        context.glUniform1f(self.m_shader_program.uniformLocation("pathMinZ"), self.m_gcodedrawer.pathMinZ)
        context.glUniform1f(self.m_shader_program.uniformLocation("pathTopZ"), self.m_gcodedrawer.pathTopZ)
        #context.glUniformMatrix4fv(self.m_shader_program.uniformLocation("rotate"), False, self.rotate)
        #context.glUniform1i(self.m_shader_program.uniformLocation("heightMap", 0)

        #context.glUniform1f(self.m_shader_program.uniformLocation("resolution"), self.m_gcodedrawer.resolution)
        #context.glUniform1f(self.m_shader_program.uniformLocation("pathScale"), self.m_gcodedrawer.pathScale)
        #context.glUniform1f(self.m_shader_program.uniformLocation("pathMinZ"), self.m_gcodedrawer.pathMinZ)
        #context.glUniform1f(self.m_shader_program.uniformLocation("pathTopZ"), self.m_gcodedrawer.pathTopZ)
        self.m_shader_program.setUniformValue("rotate", self.rotate)
        self.m_shader_program.setUniformValue("heightMap", 0)

    def updateGeometry(self, context: QOpenGLFunctions):
        '''
        '''
        if not self.m_shader_program:
            return

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

        self.prepareDraw(context)

        if self.m_vao.isCreated():
            # Offset for pos0
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation0 = self.m_shader_program.attributeLocation("pos0")
            self.m_shader_program.enableAttributeArray(vertexLocation0)
            self.m_shader_program.setAttributeBuffer(vertexLocation0, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)

            # Offset for pos1
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = self.m_shader_program.attributeLocation("pos1")
            self.m_shader_program.enableAttributeArray(vertexLocation1)
            self.m_shader_program.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)    

            # Offset for pos2
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = self.m_shader_program.attributeLocation("pos2")
            self.m_shader_program.enableAttributeArray(vertexLocation2)
            self.m_shader_program.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)   

            # Offset for thisPos
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation3 = self.m_shader_program.attributeLocation("thisPos")
            self.m_shader_program.enableAttributeArray(vertexLocation3)
            self.m_shader_program.setAttributeBuffer(vertexLocation3, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)  

            # Offset for vertex
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            vertex = self.m_shader_program.attributeLocation("vertex")
            self.m_shader_program.enableAttributeArray(vertex)
            self.m_shader_program.setAttributeBuffer(vertex, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)
    

            self.m_vao.release()

        self.m_vbo.release()

        self.m_needsUpdateGeometry = False

    def draw(self, context: QOpenGLFunctions):
        '''
        '''
        if not self.m_shader_program:
            return

        if self.m_vao.isCreated():
            # Prepare vao
            self.m_vao.bind()
        else:
            self.prepareDraw(context)

            # Prepare vbo
            self.m_vbo.bind()

            # Offset for position
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation0 = self.m_shader_program.attributeLocation("pos0")
            self.m_shader_program.enableAttributeArray(vertexLocation0)
            self.m_shader_program.setAttributeBuffer(vertexLocation0, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)

            # Offset for pos1
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = self.m_shader_program.attributeLocation("pos1")
            self.m_shader_program.enableAttributeArray(vertexLocation1)
            self.m_shader_program.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)    

            # Offset for pos2
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = self.m_shader_program.attributeLocation("pos2")
            self.m_shader_program.enableAttributeArray(vertexLocation2)
            self.m_shader_program.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)   

            # Offset for thisPos
            offset += self.sizeof_vector2D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation3 = self.m_shader_program.attributeLocation("thisPos")
            self.m_shader_program.enableAttributeArray(vertexLocation3)
            self.m_shader_program.setAttributeBuffer(vertexLocation3, GL.GL_FLOAT, offset, 2, self.sizeof_vertexdata)  

            # Offset for vertex
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            vertex = self.m_shader_program.attributeLocation("vertex")
            self.m_shader_program.enableAttributeArray(vertex)
            self.m_shader_program.setAttributeBuffer(vertex, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)
    
                
        if len(self.m_triangles) != 0:
            if self.m_texture:
                self.m_texture.bind()
                self.m_shader_program.setUniformValue("texture", 0)
        
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
        
        self.m_shader_program.disableAttributeArray("pos0")
        self.m_shader_program.disableAttributeArray("pos1")
        self.m_shader_program.disableAttributeArray("pos2")
        self.m_shader_program.disableAttributeArray("thisPos")
        self.m_shader_program.disableAttributeArray("vertex")

        self.m_shader_program.release()

    def createPathTexture(self, context: QOpenGLFunctions):
        '''
        https://ghorwin.github.io/OpenGLWithQt-Tutorial/#_tutorial_09_render_in_eine_framebuffer_und_verwendung_von_kernel_effekten
        '''
        if not self.pathFramebuffer:
            self.pathFramebuffer = QtOpenGL.QOpenGLFramebufferObject(
                    QSize(self.m_gcodedrawer.resolution, self.m_gcodedrawer.resolution),
                    QtOpenGL.QOpenGLFramebufferObject.CombinedDepthStencil)
            
            self.pathFramebuffer.bind()

            self.pathRgbaTexture = QtOpenGL.QOpenGLTexture(QtOpenGL.QOpenGLTexture.Target2D)
            self.glActiveTexture(GL.GL_TEXTURE0)
            #self.pathRgbaTexture.bind(GL.GL_TEXTURE_2D)
            self.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.m_gcodedrawer.resolution, self.m_gcodedrawer.resolution, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
            self.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            self.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            self.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.pathRgbaTexture, 0)
            self.pathRgbaTexture.release()

            renderbuffer = QtOpenGL.QOpenGLBuffer()
            renderbuffer.bind(GL.GL_RENDERBUFFER)
            self.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_DEPTH_COMPONENT16, self.m_gcodedrawer.resolution, self.m_gcodedrawer.resolution)
            self.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_RENDERBUFFER, renderbuffer)
            renderbuffer.release()
            
            self.pathFramebuffer.release()
            self.pathRgbaTexture = self.pathFramebuffer.texture()
        
        self.pathFramebuffer.bind()
        self.m_gcodedrawer.draw(context)
        self.pathFramebuffer.release()
        self.needToCreatePathTexture = False
        self.needToDrawHeightMap = True