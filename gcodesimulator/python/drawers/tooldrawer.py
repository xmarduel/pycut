
import math
from enum import Enum
import ctypes

from typing import List

import numpy as np

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QOpenGLFunctions

from PySide6 import QtOpenGL

from gcodesimulator.python.drawers.shaderdrawable import ShaderDrawable
from gcodesimulator.python.drawers.gcodedrawer import GcodeDrawer

from gcodesimulator.python.drawers.gcodedrawer import VertexData

from OpenGL import GL

M_PI = math.acos(-1)


class ToolVertexData:
    NB_FLOATS_PER_VERTEX = 6

    def __init__(self):
        self.vPos = QVector3D()
        self.vColor = QVector3D()

    @classmethod
    def VertexDataListToNumPy(cls, vertex_list: List['ToolVertexData']):
        '''
        '''
        def NaN_to_Val(val):
            #if qIsNaN(val):
            #    return 65536.0
            return val

        np_array = np.empty(cls.NB_FLOATS_PER_VERTEX * len(vertex_list), dtype=ctypes.c_float)
        
        for k, vdata in enumerate(vertex_list):
            np_array[6*k+0] = NaN_to_Val(vdata.vPos.x())
            np_array[6*k+1] = NaN_to_Val(vdata.vPos.y())
            np_array[6*k+2] = NaN_to_Val(vdata.vPos.z())

            np_array[6*k+3] = NaN_to_Val(vdata.vColor.x())
            np_array[6*k+4] = NaN_to_Val(vdata.vColor.y())
            np_array[6*k+5] = NaN_to_Val(vdata.vColor.z())

        return np_array



class ToolDrawer(ShaderDrawable):
    '''
    '''
    sizeof_vertexdata = 24
    sizeof_vector3D = 12
    sizeof_float = 4
    
    class DrawMode(Enum):
        Vectors = 0
        Raster = 1

    def __init__(self, gcodedrawer: GcodeDrawer):
        '''
        with a pointer of the gcodedrawer
        '''
        super(ToolDrawer, self).__init__()

        self.m_drawMode = ToolDrawer.DrawMode.Vectors

        self.m_gcodedrawer = gcodedrawer

        self.rotate = QMatrix4x4()
        self.rotate.setToIdentity()

    @staticmethod
    def lowerBound(vertex_list : List[VertexData], stopAtTime: float) -> int :
        '''
        get the highest index in the vertex list where endTime < stopAtTime 
        '''
        begin = 0
        end = len(vertex_list)

        while begin < end:
            idx = math.floor((begin + end) / 2)
            if vertex_list[idx].endTime < stopAtTime:
                begin = idx + 1
            else:
                end = idx
        
        return end

    @staticmethod
    def mix(v0, v1, a):
        return v0 + (v1 - v0) * a

    def updateData(self) -> bool :
        '''
        '''
        if self.m_drawMode == ToolDrawer.DrawMode.Vectors:
            return self.prepareVectors()
        elif self.m_drawMode == ToolDrawer.DrawMode.Raster:
            return False

    def prepareVectors(self) -> bool:
        # Clear all vertex data
        self.m_lines = []
        self.m_points = []
        self.m_triangles = []

        numDivisions = 40
        
        r = 0.7
        g = 0.7 
        b = 0.0
        
        def addVertex(x: float, y: float, z:float):
            vertex = ToolVertexData()
            vertex.vPos = QVector3D(x, y, z)
            vertex.vColor = QVector3D(r, g, b)
            
            self.m_triangles.append(vertex)

        lastX = 0.5 * math.cos(0)
        lastY = 0.5 * math.sin(0)
        
        for i in range(numDivisions):
            j = i + 1
            if j == numDivisions:
                j = 0
            x = 0.5 * math.cos(j * 2 * M_PI / numDivisions)
            y = 0.5 * math.sin(j * 2 * M_PI / numDivisions)

            addVertex(lastX, lastY, 0)
            addVertex(x, y, 0)
            addVertex(lastX, lastY, 1)
            addVertex(x, y, 0)
            addVertex(x, y, 1)
            addVertex(lastX, lastY, 1)
            addVertex(0, 0, 0)
            addVertex(x, y, 0)
            addVertex(lastX, lastY, 0)
            addVertex(0, 0, 1)
            addVertex(lastX, lastY, 1)
            addVertex(x, y, 1)

            lastX = x
            lastY = y

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

        idx = ToolDrawer.lowerBound(self.m_gcodedrawer.m_triangles, self.m_gcodedrawer.stopAtTime)
        
        if idx < self.m_gcodedrawer.pathNumPoints:

            beginTime = self.m_gcodedrawer.m_triangles[idx].startTime
            endTime = self.m_gcodedrawer.m_triangles[idx].endTime
            
            if endTime == beginTime:
                ratio = 0
            else:
                ratio = (self.m_gcodedrawer.stopAtTime - beginTime) / (endTime - beginTime)

            x = ToolDrawer.mix(self.m_gcodedrawer.m_triangles[idx].pos1.x(), self.m_gcodedrawer.m_triangles[idx].pos2.x(), ratio)
            y = ToolDrawer.mix(self.m_gcodedrawer.m_triangles[idx].pos1.y(), self.m_gcodedrawer.m_triangles[idx].pos2.y(), ratio)
            z = ToolDrawer.mix(self.m_gcodedrawer.m_triangles[idx].pos1.z(), self.m_gcodedrawer.m_triangles[idx].pos2.z(), ratio)

        else:

            x = self.m_gcodedrawer.m_triangles[idx-1].pos2.x()
            y = self.m_gcodedrawer.m_triangles[idx-1].pos2.y()
            z = self.m_gcodedrawer.m_triangles[idx-2].pos2.z()

        self.m_shader_program.setUniformValue("scale", QVector3D(self.m_gcodedrawer.cutterDia, self.m_gcodedrawer.cutterDia, self.m_gcodedrawer.cutterH) * self.m_gcodedrawer.pathScale)
        self.m_shader_program.setUniformValue("translate", QVector3D((x + self.m_gcodedrawer.pathXOffset), (y + self.m_gcodedrawer.pathYOffset), (z - self.m_gcodedrawer.pathTopZ)) * self.m_gcodedrawer.pathScale)
        self.m_shader_program.setUniformValue("rotate", self.rotate)

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

        self.prepareDraw(context)

        # Update vertex buffer
        if self.updateData():
            # Fill vertices buffer
            vertexData = []
            vertexData += self.m_triangles
            vertexData += self.m_lines
            vertexData += self.m_points

            # python handling of vbo - with numpy -
            np_array = ToolVertexData.VertexDataListToNumPy(vertexData)
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
            # Offset for vPos
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = self.m_shader_program.attributeLocation("vPos")
            self.m_shader_program.enableAttributeArray(vertexLocation1)
            self.m_shader_program.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for vColor
            offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = self.m_shader_program.attributeLocation("vColor")
            self.m_shader_program.enableAttributeArray(vertexLocation2)
            self.m_shader_program.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)    

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

            # Offset for vPos
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = self.m_shader_program.attributeLocation("vPos")
            self.m_shader_program.enableAttributeArray(vertexLocation1)
            self.m_shader_program.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for vColor
            offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = self.m_shader_program.attributeLocation("vColor")
            self.m_shader_program.enableAttributeArray(vertexLocation2)
            self.m_shader_program.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)    

                
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
        
        self.m_shader_program.disableAttributeArray("vPos")
        self.m_shader_program.disableAttributeArray("vColor")

        self.m_shader_program.release()
