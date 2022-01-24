
import math
from enum import Enum
import ctypes

from typing import List
from typing import Tuple

import numpy as np

from PySide6 import QtOpenGL

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QOpenGLFunctions

from PySide6.QtCore import Slot

from OpenGL import GL

from gcodesimulator.python.parser.gcodeminiparser import GcodeMiniParser

from gcodesimulator.python.drawers.shaderdrawable import ShaderDrawable


sNaN = float('NaN')

M_PI = math.acos(-1)



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

        np_array = np.empty(cls.NB_FLOATS_PER_VERTEX * len(vertex_list), dtype=ctypes.c_float)
        
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


class GcodeDrawer(ShaderDrawable) :
    '''
    '''
    sizeof_vertexdata = 36
    sizeof_vector3D = 12
    sizeof_float = 4

    class DrawMode(Enum):
        Vectors = 0
        Raster = 1

    def __init__(self, gcode: str, topZ: float, cutterDiameter: float, cutterHeight: float, cutterAngle:float = 180):
        super(GcodeDrawer, self).__init__()

        self.m_drawMode = GcodeDrawer.DrawMode.Vectors
        self.gcode = gcode

        self.m_miniParser : GcodeMiniParser = None
        self.path : List[Tuple[float,float,float,float]] = None

        self.needToCreatePathTexture = False
        self.needToDrawHeightMap = False
    
        self.resolution = 1024 // 4  #  python not so powerfull as javascript...
        self.gpuMem = 2 * self.resolution * self.resolution

        if cutterAngle < 0 or cutterAngle > 180:
            cutterAngle = 180

        self.cutterDia = cutterDiameter
        self.cutterAngleRad = cutterAngle / 180 * M_PI
        self.isVBit = cutterAngle < 180
        self.cutterH = cutterHeight
        self.pathXOffset = 0
        self.pathYOffset = 0
        self.pathScale = 1
        self.pathMinZ = 0
        self.pathTopZ = topZ
        self.stopAtTime = 9999999

        self.pathNumPoints = 0
        self.pathStride = 9
        self.pathVertexesPerLine = 18
        self.pathNumVertexes = 0
        self.totalTime = 0

    def setMiniParser(self, miniParser: GcodeMiniParser):
        self.m_miniParser = miniParser

    def miniParser(self) -> GcodeMiniParser :
        return self.m_miniParser 

    def update(self):
        self.m_geometryUpdated = False
        super().update()

    def getSizes(self) -> QVector3D :
        xs = [item[0] for item in self.path]
        ys = [item[1] for item in self.path]
        zs = [item[2] for item in self.path]

        xmin = QVector3D(min(xs), min(ys), min(zs))
        xmax = QVector3D(max(xs), max(ys), max(zs))

        return QVector3D(xmax.x() - xmin.x(), xmax.y() - xmin.y(), xmax.z() - xmin.z())

    def getMinimumExtremes(self) -> QVector3D :
        xs = [item[0] for item in self.path]
        ys = [item[1] for item in self.path]
        zs = [item[2] for item in self.path]

        xmin = QVector3D(min(xs), min(ys), min(zs))

        if self.m_ignoreZ:
            xmin.setZ(0)

        return xmin

    def getMaximumExtremes(self) -> QVector3D :
        xs = [item[0] for item in self.path]
        ys = [item[1] for item in self.path]
        zs = [item[2] for item in self.path]

        xmax = QVector3D(max(xs), max(ys), max(zs))

        if self.m_ignoreZ:
            xmax.setZ(0)

        return xmax

    @Slot()
    def onTimerVertexUpdate(self):
        self.update()

    def setStopAtTime(self, t):
        self.stopAtTime = t
        self.needToCreatePathTexture = True
        self.update()

    def updateData(self):
        if self.m_drawMode == GcodeDrawer.DrawMode.Vectors:
            return self.prepareVectors()
        elif self.m_drawMode == GcodeDrawer.DrawMode.Raster:
            return False

    def prepareVectors(self) -> bool: 
        print("preparing vectors : %s" % self)

        self.m_miniParser.parse_gcode(self.gcode)
        self.path = path = self.m_miniParser.path

        # Clear all vertex data
        self.m_lines = []
        self.m_points = []
        self.m_triangles = []

        # Delete texture on mode change
        if self.m_texture:
            self.m_texture.destroy()
            self.m_texture = None
        
        self.needToCreatePathTexture = True
        
        #self.requestFrame()
        
        self.pathNumPoints = len(path)
        numHalfCircleSegments = 5

        if self.isVBit:
            self.pathStride = 12
            pathVertexesPerLine = 12 + numHalfCircleSegments * 6
        else:
            self.pathStride = 9
            pathVertexesPerLine = 18

        self.pathNumVertexes = len(path) * pathVertexesPerLine

        minX = path[0][0]
        maxX = path[0][0]
        minY = path[0][1]
        maxY = path[0][1]
        minZ = path[0][2]

        total_time = 0
        for idx, point in enumerate(path):
            prevIdx = max(idx - 1, 0)
            prevPoint = self.path[prevIdx]
           
            x = point[0]
            y = point[1]
            z = point[2]
            f = point[3]
            
            prevX = prevPoint[0]
            prevY = prevPoint[1]
            prevZ = prevPoint[2]
            
            dist = math.sqrt((x - prevX) * (x - prevX) + (y - prevY) * (y - prevY) + (z - prevZ) * (z - prevZ))
            beginTime = total_time
            total_time = total_time + dist / f * 60

            minX = min(minX, x)
            maxX = max(maxX, x)
            minY = min(minY, y)
            maxY = max(maxY, y)
            minZ = min(minZ, z)

            if self.isVBit:
                coneHeight = -min(z, prevZ, 0) + 0.1
                coneDia = coneHeight * 2 * math.sin(self.cutterAngleRad / 2) / math.cos(self.cutterAngleRad / 2)

                if x == prevX and y == prevY:
                    rotAngle = 0
                else:
                    rotAngle = math.atan2(y - prevY, x - prevX)
                
                xyDist = math.sqrt((x - prevX) * (x - prevX) + (y - prevY) * (y - prevY))

                # --------------------------------------------------------------------------------------------------
                def f(command, rawX, rawY, rawZ, rotCos, rotSin, zOffset=None):
                    if zOffset is None:
                        zOffset = 0
                   
                    vertex = VertexData()
                    vertex.pos1 = QVector3D(prevX, prevY, prevZ + zOffset)
                    vertex.pos2 = QVector3D(x, y, z + zOffset)
                    vertex.startTime = beginTime
                    vertex.endTime = total_time
                    vertex.command = command
                    vertex.rawPos = QVector3D(rawX * rotCos - rawY * rotSin, rawY * rotCos + rawX * rotSin, rawZ)
                
                    self.m_triangles.append(vertex)
                # --------------------------------------------------------------------------------------------------

                if math.abs(z - prevZ) >= xyDist * M_PI / 2 * math.cos(self.cutterAngleRad / 2) / math.sin(self.cutterAngleRad / 2):
                    #console.log("plunge or retract")
                    #plunge or retract
                    index = 0

                    command = 100 if prevZ < z else 101
                    for circleIndex in range(1, numHalfCircleSegments*2):
                        a1 = 2 * M_PI * circleIndex / numHalfCircleSegments/2
                        a2 = 2 * M_PI * (circleIndex + 1) / numHalfCircleSegments/2
                        f(command, coneDia / 2 * math.cos(a2), coneDia / 2 * math.sin(a2), coneHeight, 1, 0)
                        index += 1
                        f(command, 0, 0, 0, 1, 0)
                        index += 1
                        f(command, coneDia / 2 * math.cos(a1), coneDia / 2 * math.sin(a1), coneHeight, 1, 0)
                        index += 1

                    while index < pathVertexesPerLine:
                        f(200, 0, 0, 0, 1, 0)
                        index += 1
        
                else:
                    # cut
                    planeContactAngle = math.asin((prevZ - z) / xyDist * math.sin(self.cutterAngleRad / 2) / math.cos(self.cutterAngleRad / 2))

                    index = 0
                    if True:
                        f(100, 0, -coneDia / 2, coneHeight, math.cos(rotAngle - planeContactAngle), math.sin(rotAngle - planeContactAngle))
                        f(101, 0, -coneDia / 2, coneHeight, math.cos(rotAngle - planeContactAngle), math.sin(rotAngle - planeContactAngle))
                        f(100, 0, 0, 0, 1, 0)
                        f(100, 0, 0, 0, 1, 0)
                        f(101, 0, -coneDia / 2, coneHeight, math.cos(rotAngle - planeContactAngle), math.sin(rotAngle - planeContactAngle))
                        f(101, 0, 0, 0, 1, 0)
                        f(100, 0, 0, 0, 1, 0)
                        f(101, 0, 0, 0, 1, 0)
                        f(100, 0, coneDia / 2, coneHeight, math.cos(rotAngle + planeContactAngle), math.sin(rotAngle + planeContactAngle))
                        f(100, 0, coneDia / 2, coneHeight, math.cos(rotAngle + planeContactAngle), math.sin(rotAngle + planeContactAngle))
                        f(101, 0, 0, 0, 1, 0)
                        f(101, 0, coneDia / 2, coneHeight, math.cos(rotAngle + planeContactAngle), math.sin(rotAngle + planeContactAngle))
                     
                        index += 12
       
                    startAngle = rotAngle + math.PI / 2 - planeContactAngle
                    endAngle = rotAngle + 3 * math.PI / 2 + planeContactAngle
                    for circleIndex in range(1,numHalfCircleSegments):
                        a1 = startAngle + circleIndex / numHalfCircleSegments * (endAngle - startAngle)
                        a2 = startAngle + (circleIndex + 1) / numHalfCircleSegments * (endAngle - startAngle)
                        #console.log("a1,a2: " + (a1 * 180 / math.PI) + ", " + (a2 * 180 / math.PI))

                        f(100, coneDia / 2 * math.cos(a2), coneDia / 2 * math.sin(a2), coneHeight, 1, 0)
                        f(100, 0, 0, 0, 1, 0)
                        f(100, coneDia / 2 * math.cos(a1), coneDia / 2 * math.sin(a1), coneHeight, 1, 0)
                        f(101, coneDia / 2 * math.cos(a2 + math.PI), coneDia / 2 * math.sin(a2 + math.PI), coneHeight, 1, 0)
                        f(101, 0, 0, 0, 1, 0)
                        f(101, coneDia / 2 * math.cos(a1 + math.PI), coneDia / 2 * math.sin(a1 + math.PI), coneHeight, 1, 0)

                        index += 16
                
            else :
                # recall: pathVertexesPerLine = 18

                for virtex in range(pathVertexesPerLine):
                    vertex = VertexData()
                    vertex.pos1 = QVector3D(prevX, prevY, prevZ)
                    vertex.pos2 = QVector3D(x, y, z)
                    vertex.startTime = beginTime
                    vertex.endTime = total_time
                    vertex.command = virtex

                    self.m_triangles.append(vertex)

        
        self.totalTime = total_time

        self.pathXOffset = -(minX + maxX) / 2
        self.pathYOffset = -(minY + maxY) / 2
        size = max(maxX - minX + 4 * self.cutterDia, maxY - minY + 4 * self.cutterDia)
        self.pathScale = 2 / size
        self.pathMinZ = minZ
        self.stopAtTime = total_time

        self.update()
    
        return True

    def prepareDraw(self, context: QOpenGLFunctions):

        self.m_shader_program.bind()

        context.glUniform1f(self.m_shader_program.uniformLocation("resolution"), self.resolution)
        context.glUniform1f(self.m_shader_program.uniformLocation("cutterDia"), self.cutterDia)
        #context.glUniform2f(self.m_shader_program.uniformLocation("pathXYOffset"), pathXOffset, pathYOffset)
        context.glUniform1f(self.m_shader_program.uniformLocation("pathMinZ"), self.pathMinZ)
        ##context.glUniform1f(self.m_shader_program.uniformLocation("pathTopZ"), pathTopZ)
        context.glUniform1f(self.m_shader_program.uniformLocation("stopAtTime"), self.stopAtTime)

        #self.m_shader_program.setUniformValue("resolution", self.resolution)
        #self.m_shader_program.setUniformValue("cutterDia", self.cutterDia) # error: float! ???
        self.m_shader_program.setUniformValue("pathXYOffset", self.pathXOffset, self.pathYOffset)
        #self.m_shader_program.setUniformValue("pathScale", self.pathScale)
        #self.m_shader_program.setUniformValue("pathMinZ", self.pathMinZ)
        ##self.m_self.m_shader_program.setUniformValue("pathTopZ", self.pathTopZ)
        #self.m_shader_program.setUniformValue("stopAtTime", self.stopAtTime)

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

        self.prepareDraw(context)

        if self.m_vao.isCreated():
            # Offset for pos1
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation1 = self.m_shader_program.attributeLocation("pos1")
            self.m_shader_program.enableAttributeArray(vertexLocation1)
            self.m_shader_program.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for pos2
            offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = self.m_shader_program.attributeLocation("pos2")
            self.m_shader_program.enableAttributeArray(vertexLocation2)
            self.m_shader_program.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for raw pos
            #offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            #vertexRawPos = self.m_shader_program.attributeLocation("rawPos")
            #self.m_shader_program.enableAttributeArray(vertexRawPos)
            #self.m_shader_program.setAttributeBuffer(vertexRawPos, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for start time
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            startTime = self.m_shader_program.attributeLocation("startTime")
            self.m_shader_program.enableAttributeArray(startTime)
            self.m_shader_program.setAttributeBuffer(startTime, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            # Offset for end time
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            endTime = self.m_shader_program.attributeLocation("endTime")
            self.m_shader_program.enableAttributeArray(endTime)
            self.m_shader_program.setAttributeBuffer(endTime, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            # Offset for command
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            command = self.m_shader_program.attributeLocation("command")
            self.m_shader_program.enableAttributeArray(command)
            self.m_shader_program.setAttributeBuffer(command, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)
    
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
            vertexLocation1 = self.m_shader_program.attributeLocation("pos1")
            self.m_shader_program.enableAttributeArray(vertexLocation1)
            self.m_shader_program.setAttributeBuffer(vertexLocation1, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for pos2
            offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation2 = self.m_shader_program.attributeLocation("pos2")
            self.m_shader_program.enableAttributeArray(vertexLocation2)
            self.m_shader_program.setAttributeBuffer(vertexLocation2, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for raw pos
            #offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex position data
            #vertexRawPos = self.m_shader_program.attributeLocation("rawPos")
            #self.m_shader_program.enableAttributeArray(vertexRawPos)
            #self.m_shader_program.setAttributeBuffer(vertexRawPos, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata)

            # Offset for start time
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            startTime = self.m_shader_program.attributeLocation("startTime")
            self.m_shader_program.enableAttributeArray(startTime)
            self.m_shader_program.setAttributeBuffer(startTime, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            # Offset for end time
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            endTime = self.m_shader_program.attributeLocation("endTime")
            self.m_shader_program.enableAttributeArray(endTime)
            self.m_shader_program.setAttributeBuffer(endTime, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            # Offset for command
            offset += self.sizeof_float

            # Tell OpenGL programmable pipeline how to locate vertex color data
            command = self.m_shader_program.attributeLocation("command")
            self.m_shader_program.enableAttributeArray(command)
            self.m_shader_program.setAttributeBuffer(command, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

                
        if len(self.m_triangles) != 0:
            if self.m_texture:
                self.m_texture.bind()
                self.m_shader_program.setUniformValue("texture", 0)
        
            
            numTriangles = len(self.m_triangles)
            lastTriangle = 0
            maxTriangles = math.floor(self.gpuMem / self.pathStride / 3 / (VertexData.NB_FLOATS_PER_VERTEX * 4))

            # TODO -------------------------------------------
            '''
            while lastTriangle < numTriangles:
                n = min(numTriangles - lastTriangle, maxTriangles)
                
                b = np.empty(0, dtype=ctypes.c_float) # TODO !! ??
                b = new Float32Array(pathBufferContent.buffer, 
                        lastTriangle * self.pathStride * 3 * (VertexData.NB_FLOATS_PER_VERTEX * 4), 
                        n * self.pathStride * 3)
                
                context.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, b)
                context.glDrawArrays(GL.GL_TRIANGLES, 0, n * 3)
                lastTriangle += n
            '''

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
        
        self.m_shader_program.disableAttributeArray("pos1")
        self.m_shader_program.disableAttributeArray("pos2")
        self.m_shader_program.disableAttributeArray("startTime")
        self.m_shader_program.disableAttributeArray("endTime")
        self.m_shader_program.disableAttributeArray("command")
        self.m_shader_program.disableAttributeArray("rawPos")

        self.m_shader_program.release()
