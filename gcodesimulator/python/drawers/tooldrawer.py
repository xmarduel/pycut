
import math
from turtle import position

from typing import List

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QColor

from PySide6 import QtOpenGLWidgets
from PySide6 import QtOpenGL

from gcodesimulator.python.drawers.shaderdrawable import ShaderDrawable, VertexData
from gcodesimulator.python.drawers.shaderdrawable import VertexData


sNaN = float('NaN')

M_PI = math.acos(-1)


class ToolDrawer(ShaderDrawable):
    '''
    '''
    arcs = 12

    def __init__(self):
        super(ToolDrawer, self).__init__()

        self.m_gpuMem = 2 * 1024 * 1024

        self.needToCreatePathTexture = False
        self.needToDrawHeightMap = False
        self.requestFrame = None

        self.gpuMem = 2 * 1024 * 1024
        self.resolution = 1024
        self.cutterDia = .125
        self.cutterAngleRad = M_PI
        self.isVBit = False
        self.cutterH = 0
        self.pathXOffset = 0
        self.pathYOffset = 0
        self.pathScale = 1
        self.pathMinZ = -1
        self.pathTopZ = 0
        self.stopAtTime = 9999999

        self.basicProgramUniformLocation = {}
        self.basicProgramAttributes = {}

    def onLinkBasicProgram(self, basicProgram: QtOpenGL.QOpenGLShaderProgram):
        '''
        '''
        self.basicProgramUniformLocation["scale"] = basicProgram.uniformLocation("scale")
        self.basicProgramUniformLocation["translate"] = basicProgram.uniformLocation("translate")
        self.basicProgramUniformLocation["rotate"] = basicProgram.uniformLocation("rotate")
        
        self.basicProgramAttributes["vPos"] = basicProgram.attributeLocation("vPos")
        self.basicProgramAttributes["vColor"] = basicProgram.attributeLocation("vColor")

    '''
    @staticmethod
    def lowerBound(data, offset: int, stride: int, begin: float, end: float, value) -> int :
        while begin < end:
            i = math.floor((begin + end) / 2)
            if data[offset + i * stride] < value:
                begin = i + 1
            else:
                end = i
        
        return end

    @staticmethod
    def mix(v0, v1, a):
        return v0 + (v1 - v0) * a
    '''

    def updateData(self) -> bool :
        numDivisions = 40
        #numTriangles = numDivisions * 4
        #cylNumVertexes = numTriangles * 3
        
        self.m_triangles = []
        
        r = 0.7
        g = 0.7 
        b = 0.0
        
        def addVertex(x: float, y: float, z:float):
            vertex = VertexData()
            vertex.position = QVector3D(x, y, z)
            vertex.color = QVector3D(r, g, b)
            
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
