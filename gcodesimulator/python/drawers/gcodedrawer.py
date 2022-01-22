
import math

from typing import List

from enum import Enum

from PySide6.QtGui import QVector3D
from PySide6.QtCore import Slot

from PySide6.QtCore import qIsNaN

from gcodesimulator.python.parser.gcodeminiparser import GcodeMiniParser

from gcodesimulator.python.drawers.shaderdrawable import ShaderDrawable
from gcodesimulator.python.drawers.shaderdrawable import VertexData

sNaN = float('NaN')

M_PI = math.acos(-1)


class GcodeDrawer(ShaderDrawable) :
    '''
    '''
    class DrawMode(Enum):
        Vectors = 0
        Raster = 1

    def __init__(self, gcode: str, topZ: float, cutterDiameter: float, cutterHeight: float, cutterAngle:float = 180):
        super(GcodeDrawer, self).__init__()

        self.m_drawMode = GcodeDrawer.DrawMode.Vectors
        self.gcode = gcode

        self.m_miniParser : GcodeMiniParser = None
        self.path : List[List[float,float,float,float]] = None

        self.needToCreatePathTexture = False
        self.needToDrawHeightMap = False
    
        self.gpuMem = 2 * 1024 * 1024
        self.resolution = 1024

        if cutterAngle < 0 or cutterAngle > 180:
            cutterAngle = 180

        self.cutterDia = cutterDiameter
        self.cutterAngleRad = cutterAngle / 180 * M_PI
        self.isVBit = cutterAngle < 180
        self.cutterH = cutterHeight
        self.pathXOffset = 0
        self.pathYOffset = 0
        self.pathScale = 1
        self.pathMinZ = -1
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

    def updateData(self):
        if self.m_drawMode == GcodeDrawer.DrawMode.Vectors:
            return self.prepareVectors()
        elif self.m_drawMode == GcodeDrawer.DrawMode.Raster:
            return False

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

                    #if (index > pathVertexesPerLine)
                    #    console.log("oops...")
                    while index < pathVertexesPerLine:
                        f(200, 0, 0, 0, 1, 0)
                        index += 1
        
                else :
                    #console.log("cut")
                    # cut
                    planeContactAngle = math.asin((prevZ - z) / xyDist * math.sin(self.cutterAngleRad / 2) / math.cos(self.cutterAngleRad / 2))
                    #console.log("\nxyDist = ", xyDist)
                    #console.log("delta z = " + (z - prevZ))
                    #console.log("planeContactAngle = " + (planeContactAngle * 180 / math.PI))

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

                    #if (index != pathVertexesPerLine)
                    #    console.log("oops...")
                    #while (index < pathVertexesPerLine)
                    #    f(index++, 200, 0, 0, 0, 1, 0)
                
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

