
from typing import List

from enum import Enum

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QColor
from PySide6.QtGui import QImage

from PySide6.QtCore import QTimer, Slot

from PySide6.QtCore import qIsNaN

from PySide6.QtOpenGL import QOpenGLTexture
from PySide6.QtOpenGL import QOpenGLBuffer

from gcodeviewer.parser.linesegment import LineSegment
from gcodeviewer.parser.gcodeviewparse import GcodeViewParse

from gcodeviewer.drawers.shaderdrawable import ShaderDrawable
from gcodeviewer.drawers.shaderdrawable import VertexData

from gcodeviewer.util.util import Util
from gcodeviewer.util.util import qBound

sNaN = float('NaN')


class GcodeDrawer(ShaderDrawable) :
    '''
    '''
    class GrayscaleCode(Enum):
        S = 0
        Z  = 1

    class DrawMode(Enum):
        Vectors = 0
        Raster = 1

    def __init__(self):
        super(GcodeDrawer, self).__init__()

        self.m_viewParser = None # GcodeViewParse(self)

        self.m_drawMode = GcodeDrawer.DrawMode.Vectors
        self.m_simplify = True
        self.m_simplifyPrecision = 0.0
        self.m_ignoreZ = False
        self.m_grayscaleSegments = False
        self.m_grayscaleCode = GcodeDrawer.GrayscaleCode.S
        self.m_grayscaleMin = 0
        self.m_grayscaleMax = 255
   
        self.m_colorNormal = QColor(255,0,0)
        self.m_colorDrawn = QColor(0,255,0)
        self.m_colorHighlight = QColor(25,25,30)
        self.m_colorZMovement = QColor(255,0,0)
        self.m_colorStart = QColor(255,0,0)
        self.m_colorEnd = QColor(255,0,0)

        self.m_timerVertexUpdate = QTimer()

        self.m_image = QImage()
        self.m_indexes : List[int] = []
        self.m_geometryUpdated = False

        self.m_pointSize = 6

        self.m_timerVertexUpdate.timeout.connect(self.onTimerVertexUpdate)
        self.m_timerVertexUpdate.start(100)

    def update(self):
        self.m_indexes = []
        self.m_geometryUpdated = False
        super().update()

    def update_indexes(self, indexes: List[int]):
        # Store segments to update
        self.m_indexes += indexes

    def updateData(self):
        if self.m_drawMode == GcodeDrawer.DrawMode.Vectors:
            if len(self.m_indexes) == 0:
                return self.prepareVectors()
            else:
                return self.updateVectors()
        elif self.m_drawMode == GcodeDrawer.DrawMode.Raster:
            if len(self.m_indexes) == 0:
                return self.prepareRaster()
            else:
                return self.updateRaster()

    def getSizes(self) -> QVector3D :
        min = self.m_viewParser.getMinimumExtremes()
        max = self.m_viewParser.getMaximumExtremes()

        return QVector3D(max.x() - min.x(), max.y() - min.y(), max.z() - min.z())

    def getMinimumExtremes(self) -> QVector3D :
        v = self.m_viewParser.getMinimumExtremes()
        if self.m_ignoreZ:
            v.setZ(0)

        return v

    def getMaximumExtremes(self) -> QVector3D :
        v = self.m_viewParser.getMaximumExtremes()
        if self.m_ignoreZ:
            v.setZ(0)

        return v

    def setViewParser(self, viewParser: GcodeViewParse):
        self.m_viewParser = viewParser

    def viewParser(self) -> GcodeViewParse :
        return self.m_viewParser 

    def simplify(self) -> bool :
        return self.m_simplify

    def setSimplify(self, simplify: bool):
        self.m_simplify = simplify

    def simplifyPrecision(self) -> float :
        return self.m_simplifyPrecision

    def setSimplifyPrecision(self, simplifyPrecision: float):
        self.m_simplifyPrecision = simplifyPrecision

    def geometryUpdated(self) -> bool :
        return self.m_geometryUpdated

    def colorNormal(self) -> QColor :
        return self.m_colorNormal

    def setColorNormal(self, colorNormal: QColor):
        self.m_colorNormal = colorNormal

    def colorHighlight(self) -> QColor :
        return self.m_colorHighlight

    def setColorHighlight(self, colorHighlight: QColor):
        self.m_colorHighlight = colorHighlight

    def colorZMovement(self) -> QColor :
        return self.m_colorZMovement

    def setColorZMovement(self, colorZMovement: QColor):
        self.m_colorZMovement = colorZMovement

    def colorDrawn(self) -> QColor :
        return self.m_colorDrawn

    def setColorDrawn(self, colorDrawn: QColor):
        self.m_colorDrawn = colorDrawn

    def colorStart(self) -> QColor :
        return self.m_colorStart

    def setColorStart(self, colorStart: QColor):
        self.m_colorStart = colorStart

    def colorEnd(self) -> QColor :
        return self.m_colorEnd

    def setColorEnd(self, colorEnd: QColor):
        self.m_colorEnd = colorEnd

    def getIgnoreZ(self) -> bool:
        return self.m_ignoreZ

    def setIgnoreZ(self, ignoreZ: bool):
        self.m_ignoreZ = ignoreZ

    def getGrayscaleSegments(self) -> bool :
        return self.m_grayscaleSegments

    def setGrayscaleSegments(self, grayscaleSegments: bool):
        self.m_grayscaleSegments = grayscaleSegments

    def grayscaleCode(self) -> GrayscaleCode :
        return self.m_grayscaleCode

    def setGrayscaleCode(self, grayscaleCode: GrayscaleCode):
        self.m_grayscaleCode = grayscaleCode

    def grayscaleMin(self) -> int:
        return self.m_grayscaleMin

    def setGrayscaleMin(self, grayscaleMin: int):
        self.m_grayscaleMin = grayscaleMin

    def grayscaleMax(self) -> int :
        return self.m_grayscaleMax

    def setGrayscaleMax(self, grayscaleMax: int):
        self.m_grayscaleMax = grayscaleMax

    def drawMode(self) -> DrawMode :
        return self.m_drawMode

    def setDrawMode(self, drawMode: DrawMode):
        self.m_drawMode = drawMode

    @Slot()
    def onTimerVertexUpdate(self):
        if len(self.m_indexes):
            super().update()

    def prepareVectors(self) -> bool: 
        print("preparing vectors : %s" % self)

        lines = self.m_viewParser.getLines()

        print("lines count: %d" % len(lines))

        vertex = VertexData()

        # Clear all vertex data
        self.m_lines = []
        self.m_points = []
        self.m_triangles = []

        # Delete texture on mode change
        if self.m_texture:
            self.m_texture.destroy()
            self.m_texture = None


        drawFirstPoint = True
        i = 0
        # i will be changed in the while-loop!
        while i < len(lines):
         
            line = lines[i]

            if qIsNaN(line.getEnd().z()):
                i += 1
                continue

            # Find first point of toolpath
            if drawFirstPoint:

                if qIsNaN(line.getEnd().x()) or qIsNaN(line.getEnd().y()) :
                    i += 1
                    continue

                # Draw first toolpath point
                vertex.color = Util.colorToVector(self.m_colorStart)
                vertex.position = line.getEnd()
                if self.m_ignoreZ :
                    vertex.position.setZ(0)
                vertex.start = QVector3D(sNaN, sNaN, self.m_pointSize)
                self.m_points.append(VertexData.clone(vertex))

                drawFirstPoint = False
                continue

            # Prepare vertices
            if line.isFastTraverse():
                vertex.start = line.getStart()
            else:
                vertex.start = QVector3D(sNaN, sNaN, sNaN)

            # Simplify geometry
            j = i
            if self.m_simplify and i < len(lines) - 1:
                start = line.getEnd() - line.getStart()
                next = QVector3D()
                length = start.length()
                straight = False

                ddo = True
                
                while ddo :
                    line.setVertexIndex(len(self.m_lines)) # Store vertex index
                    i += 1
                    
                    if i < len(lines) - 1:
                        next = lines[i].getEnd() - lines[i].getStart()
                        length += next.length()
                        # straight = start.crossProduct(start.normalized(), next.normalized()).length() < 0.025
                    
                    # Split short & straight lines
                    ddo = (length < self.m_simplifyPrecision or straight) \
                        and i < len(lines) \
                        and self.getSegmentType(lines[i]) == self.getSegmentType(lines[j])
                i -= 1
            else :
                line.setVertexIndex(len(self.m_lines)) # Store vertex index

            # Set color
            vertex.color = self.getSegmentColorVector(lines[i])

            # Line start
            vertex.position = lines[j].getStart()
            if self.m_ignoreZ:
                vertex.position.setZ(0)
            self.m_lines.append(VertexData.clone(vertex))

            # Line end
            vertex.position = lines[i].getEnd()
            if self.m_ignoreZ:
                vertex.position.setZ(0)
            self.m_lines.append(VertexData.clone(vertex))

            # Draw last toolpath point
            if i == len(lines) - 1:
                vertex.color = Util.colorToVector(self.m_colorEnd)
                vertex.position = lines[i].getEnd()
                if self.m_ignoreZ :
                    vertex.position.setZ(0)
                vertex.start = QVector3D(sNaN, sNaN, self.m_pointSize)
                self.m_points.append(VertexData.clone(vertex))
        
            # do not forget to increment the variable i
            i += 1

        self.m_geometryUpdated = True
        self.m_indexes = []
        return True

    def updateVectors(self) -> bool: 
        # Update vertices
        lines = self.m_viewParser.getLines()

        # Map buffer
        data = self.m_vbo.map(QOpenGLBuffer.WriteOnly)

        # Update vertices for each line segment
        for i in self.m_indexes:
            #Update vertex pair
            if i < 0 or i > len(lines) - 1 :
                continue

            line = lines[i]

            vertexIndex = line.vertexIndex()
            if vertexIndex >= 0:
                # Update vertex array            
                if data:
                    data[vertexIndex].color = self.getSegmentColorVector(line)
                    data[vertexIndex + 1].color = data[vertexIndex].color
                else:
                    self.m_lines[vertexIndex].color = self.getSegmentColorVector(line)
                    self.m_lines[vertexIndex + 1].color = self.m_lines[vertexIndex].color

        self.m_indexes = []
        if data:
            self.m_vbo.unmap()
        
        return not data

    def prepareRaster(self) -> bool: 
        maxImageSize = 8192

        print("preparing raster: %s" % self)

        # Generate image
        image = QImage()

        print("image info: %s %s" % (self.m_viewParser.getResolution(), self.m_viewParser.getMinLength()))

        if self.m_viewParser.getResolution().width() <= maxImageSize and self.m_viewParser.getResolution().height() <= maxImageSize:
    
            image = QImage(self.m_viewParser.getResolution(), QImage.Format_RGB888)
            image.fill(QColor("white"))

            lines = self.m_viewParser.getLines()
            print("lines count: %d" % len(lines))

            pixelSize = self.m_viewParser.getMinLength()
            origin = self.m_viewParser.getMinimumExtremes()

            for line in lines:
                if not qIsNaN(line.getEnd().length()):
                    self.setImagePixelColor(image, 
                            (line.getEnd().x() - origin.x()) / pixelSize,
                            (line.getEnd().y() - origin.y()) / pixelSize, 
                            self.getSegmentColor(line).rgb())


        # Create vertices array
        # Clear all vertex data
        self.m_lines = []
        self.m_points = []
        self.m_triangles = []

        if self.m_texture:
            self.m_texture.destroy()
            self.m_texture = None
    

        vertices :List[VertexData] = []
        vertex = VertexData()

        # Set color
        vertex.color = Util.colorToVector(QColor("red"))

        # Rect
        vertex.start = QVector3D(sNaN, 0, 0)
        vertex.position = QVector3D(self.getMinimumExtremes().x(), self.getMinimumExtremes().y(), 0)
        vertices.append(vertex)

        vertex.start = QVector3D(sNaN, 1, 1)
        vertex.position = QVector3D(self.getMaximumExtremes().x(), self.getMaximumExtremes().y(), 0)
        vertices.append(vertex)

        vertex.start = QVector3D(sNaN, 0, 1)
        vertex.position = QVector3D(self.getMinimumExtremes().x(), self.getMaximumExtremes().y(), 0)
        vertices.append(vertex)

        vertex.start = QVector3D(sNaN, 0, 0)
        vertex.position = QVector3D(self.getMinimumExtremes().x(), self.getMinimumExtremes().y(), 0)
        vertices.append(vertex)

        vertex.start = QVector3D(sNaN, 1, 0)
        vertex.position = QVector3D(self.getMaximumExtremes().x(), self.getMinimumExtremes().y(), 0)
        vertices.append(vertex)

        vertex.start = QVector3D(sNaN, 1, 1)
        vertex.position = QVector3D(self.getMaximumExtremes().x(), self.getMaximumExtremes().y(), 0)
        vertices.append(vertex)

        if not image.isNull():
            self.m_texture = QOpenGLTexture(image)
            self.m_triangles += vertices
            self.m_image = image
        else:
            for i in range(len(vertices)):
                vertices[i].start = QVector3D(sNaN, sNaN, sNaN)
            self.m_lines += vertices
            self.m_image = QImage()
    
        self.m_geometryUpdated = True
        self.m_indexes = []
        return True

    def updateRaster(self) -> bool:
        if not self.m_image is None:
            lines = self.m_viewParser.getLines()

            pixelSize = self.m_viewParser.getMinLength()
            origin = self.m_viewParser.getMinimumExtremes()

            for idx in self.m_indexes:
                line = lines[idx]
                self.setImagePixelColor( \
                    self.m_image, \
                    (line.getEnd().x() - origin.x()) / pixelSize,
                    (line.getEnd().y() - origin.y()) / pixelSize,
                    self.getSegmentColor(line.rgb()))

            if self.m_texture:
                self.m_texture.setData(QOpenGLTexture.RGB, QOpenGLTexture.UInt8, self.m_image.bits())

        self.m_indexes = []
        return False

    def getSegmentType(self, segment: LineSegment) -> int :
        return segment.isFastTraverse() + segment.isZMovement() * 2

    def getSegmentColorVector(self, segment: LineSegment) -> QVector3D:
        return Util.colorToVector(self.getSegmentColor(segment))

    def getSegmentColor(self, segment: LineSegment) -> QColor:
        if segment.drawn(): 
            return self.m_colorDrawn  # QVector3D(0.85, 0.85, 0.85)
        elif segment.isHightlight():
            return self.m_colorHighlight  # QVector3D(0.57, 0.51, 0.9)
        elif segment.isFastTraverse():
            return self.m_colorNormal  # QVector3D(0.0, 0.0, 0.0)
        elif segment.isZMovement():
            return self.m_colorZMovement  # QVector3D(1.0, 0.0, 0.0)
        elif self.m_grayscaleSegments:
            if self.m_grayscaleCode == GcodeDrawer.GrayscaleCode.S:
                return QColor.fromHsl(0, 0, qBound(0, 255 - 255.0 / (self.m_grayscaleMax - self.m_grayscaleMin) * segment.getSpindleSpeed(), 255))
            elif self.m_grayscaleCode ==  GcodeDrawer. GrayscaleCode.Z:
                return QColor.fromHsl(0, 0, qBound(0, 255 - 255.0 / (self.m_grayscaleMax - self.m_grayscaleMin) * segment.getStart().z(), 255))
    
        return self.m_colorNormal  # QVector3D(0.0, 0.0, 0.0)

    def setImagePixelColor(image: QImage, x: float, y: float, color: int) : 
        '''
        QRgb = int
        '''
        if (qIsNaN(x) or qIsNaN(y)) :
            print("Error updating pixel %d %d" %(x,y))
            return

        ix = (int)(x)
        iy = (int)(y)

        image.setPixel(ix, iy, color)
        
        pixel = image.scanLine(int(y))
        
        # TODO
        #*(pixel + (int)x * 3) = qRed(color)
        #*(pixel + (int)x * 3 + 1) = qGreen(color)
        #*(pixel + (int)x * 3 + 2) = qBlue(color)

