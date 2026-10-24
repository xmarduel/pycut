from typing import List

from enum import Enum

from PySide6 import QtGui
from PySide6.QtGui import QVector3D
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QPolygon
from PySide6.QtGui import QColor
from PySide6.QtGui import QImage

from PySide6.QtCore import QPoint
from PySide6.QtCore import QTimer, Slot

from PySide6.QtCore import qIsNaN

from PySide6.QtOpenGL import QOpenGLTexture

from gcodeviewer_11_2.parser.linesegment import LineSegment
from gcodeviewer_11_2.parser.gcodeviewparse import GcodeViewParse

from gcodeviewer_11_2.drawers.shaderdrawable import ShaderDrawable
from gcodeviewer_11_2.drawers.shaderdrawable import VertexData

from gcodeviewer_11_2.util.util import Util
from gcodeviewer_11_2.util.util import qBound

import numpy as np

sNaN = float("NaN")


class GcodeDrawer(ShaderDrawable):
    """ """

    class GrayscaleCode(Enum):
        S = 0
        Z = 1

    class DrawMode(Enum):
        Vectors = 0
        Raster = 1

    polygon = QPolygon()
    

    def __init__(self):
        super(GcodeDrawer, self).__init__()

        self.m_viewParser = None  # GcodeViewParse(self)

        self.m_drawMode = GcodeDrawer.DrawMode.Vectors
        self.m_simplify = True
        self.m_simplifyPrecision = 0.0
        self.m_ignoreZ = False
        self.m_grayscaleSegments = False
        self.m_grayscaleCode = GcodeDrawer.GrayscaleCode.S
        self.m_grayscaleMin = 0
        self.m_grayscaleMax = 255

        self.m_start = Util.nVector()
        self.m_end = Util.nVector()

        self.m_timerVertexUpdate = QTimer()

        self.m_timerVertexUpdate.timeout.connect(self.onTimerVertexUpdate)
        self.m_timerVertexUpdate.start(20)

        self.m_colorNormal = QColor(255, 0, 0)
        self.m_colorDrawn = QColor(0, 255, 0)
        self.m_colorHighlight = QColor(25, 25, 30)
        self.m_colorZMovement = QColor(255, 0, 0)
        self.m_colorStart = QColor(255, 0, 0)
        self.m_colorEnd = QColor(255, 0, 0)

        self.m_timerVertexUpdate = QTimer()

        self.m_image = QImage()
        self.m_indexes: List[int] = []
        self.m_geometryUpdated = False

        self.m_pointSize = 6

    def update(self):
        self.m_indexes = []
        self.m_geometryUpdated = False
        super().update()

    def update_indexes(self, indexes: List[int]):
        # Store segments to update
        self.m_indexes += indexes

    def updateData(self) -> bool:
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
        else:
            return True

    def drawPainter(self, painter: QtGui.QPainter, projection: QMatrix4x4, ratio: float):

        GcodeDrawer.polygon = QPolygon( [QPoint(0, 0), QPoint(-4, 32), QPoint(4, 32), QPoint(0, 0) ] )

        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        if not Util.nIsNaN(self.m_start):
            painter.save()

            painter.translate((projection.map(self.m_start)).toPoint())
            painter.scale(1, -1)

            painter.setPen(QtGui.QPen(self.m_colorStart))
            painter.setBrush(QtGui.QBrush(self.m_colorStart))
            painter.drawPolygon(GcodeDrawer.polygon)

            painter.restore()

        if not Util.nIsNaN(self.m_end):
            painter.translate((projection.map(self.m_end)).toPoint())
            painter.scale(1, -1)

            painter.setPen(QtGui.QPen(self.m_colorEnd))
            painter.setBrush(QtGui.QBrush(self.m_colorEnd))
            painter.drawPolygon(GcodeDrawer.polygon)

    def getSegmentType(self, segment: LineSegment) -> int:
        return segment.isFastTraverse() + segment.isZMovement() * 2
    
    def getSegmentLength(self, segment: LineSegment) -> float:
        return (segment.getEnd() - segment.getStart()).length()

    def getViewLowerBounds(self) -> QVector3D:
        v = self.m_viewParser.getViewLowerBounds()
        if self.m_ignoreZ:
            v.setZ(0)

        return v

    def getViewUpperBounds(self) -> QVector3D:
        v = self.m_viewParser.getViewUpperBounds()
        if self.m_ignoreZ: 
            v.setZ(0)

        return v

    def getModelLowerBounds(self) -> QVector3D:
        return self.m_viewParser.getModelLowerBounds()

    def getModelUpperBounds(self) -> QVector3D:
        return self.m_viewParser.getModelUpperBounds()
    
    def setViewParser(self, viewParser: GcodeViewParse):
        self.m_viewParser = viewParser

    def viewParser(self) -> GcodeViewParse:
        return self.m_viewParser

    def simplify(self) -> bool:
        return self.m_simplify

    def setSimplify(self, simplify: bool):
        self.m_simplify = simplify

    def simplifyPrecision(self) -> float:
        return self.m_simplifyPrecision

    def setSimplifyPrecision(self, simplifyPrecision: float):
        self.m_simplifyPrecision = simplifyPrecision

    def geometryUpdated(self) -> bool:
        return self.m_geometryUpdated

    def colorNormal(self) -> QColor:
        return self.m_colorNormal

    def setColorNormal(self, colorNormal: QColor):
        self.m_colorNormal = colorNormal

    def colorHighlight(self) -> QColor:
        return self.m_colorHighlight

    def setColorHighlight(self, colorHighlight: QColor):
        self.m_colorHighlight = colorHighlight

    def colorZMovement(self) -> QColor:
        return self.m_colorZMovement

    def setColorZMovement(self, colorZMovement: QColor):
        self.m_colorZMovement = colorZMovement

    def colorDrawn(self) -> QColor:
        return self.m_colorDrawn

    def setColorDrawn(self, colorDrawn: QColor):
        self.m_colorDrawn = colorDrawn

    def colorStart(self) -> QColor:
        return self.m_colorStart

    def setColorStart(self, colorStart: QColor):
        self.m_colorStart = colorStart

    def colorEnd(self) -> QColor:
        return self.m_colorEnd

    def setColorEnd(self, colorEnd: QColor):
        self.m_colorEnd = colorEnd

    def getIgnoreZ(self) -> bool:
        return self.m_ignoreZ

    def setIgnoreZ(self, ignoreZ: bool):
        self.m_ignoreZ = ignoreZ

    def getGrayscaleSegments(self) -> bool:
        return self.m_grayscaleSegments

    def setGrayscaleSegments(self, grayscaleSegments: bool):
        self.m_grayscaleSegments = grayscaleSegments

    def grayscaleCode(self) -> GrayscaleCode:
        return self.m_grayscaleCode

    def setGrayscaleCode(self, grayscaleCode: GrayscaleCode):
        self.m_grayscaleCode = grayscaleCode

    def grayscaleMin(self) -> int:
        return self.m_grayscaleMin

    def setGrayscaleMin(self, grayscaleMin: int):
        self.m_grayscaleMin = grayscaleMin

    def grayscaleMax(self) -> int:
        return self.m_grayscaleMax

    def setGrayscaleMax(self, grayscaleMax: int):
        self.m_grayscaleMax = grayscaleMax

    def drawMode(self) -> DrawMode:
        return self.m_drawMode

    def setDrawMode(self, drawMode: DrawMode):
        self.m_drawMode = drawMode

    @Slot()
    def onTimerVertexUpdate(self):
        if len(self.m_indexes):
            super().update()

    def prepareVectors(self) -> bool:
        """ """
        # Clear all vertex data
        self.m_lines = []
        self.m_points = []
        self.m_triangles = []

        self.m_start = Util.nVector()
        self.m_end = Util.nVector()

        # Delete texture on mode change
        if self.m_texture:
            self.m_texture.destroy()
            self.m_texture = None

        lineSegments = self.m_viewParser.getLineSegments()
        isFirstPointAdded = False
        lineSegmentsCount = len(lineSegments)
        vertex = VertexData()

        i = 0
        # i will be changed in the while-loop!
        while i < len(lineSegments):
            lineSegmentBegin = lineSegments[i]
            lineSegmentEnd = lineSegmentBegin

            # Find first point of toolpath
            if not isFirstPointAdded:
                if qIsNaN(lineSegmentBegin.getEnd().x()) or qIsNaN(lineSegmentBegin.getEnd().y()):
                    i += 1
                    continue

                # Store toolpath first point
                self.m_start = lineSegmentBegin.getEnd()
                if self.m_ignoreZ or qIsNaN(self.m_start.z()):
                    self.m_start.setZ(0)

                isFirstPointAdded = True
                i += 1
                continue

            # Prepare vertices
            if lineSegmentBegin.isFastTraverse():
                vertex.type = VertexData.VertexDataType.VertexDataTypeDash
                vertex.data = lineSegmentBegin.getStart()
            else:
                vertex.type = VertexData.VertexDataType.VertexDataTypeLine

            # Store vertex index
            lineSegmentBegin.setVertexIndex(len(self.m_lines))

            # Simplify geometry
            lineSegmentType = self.getSegmentType(lineSegmentBegin)

            if self.m_simplify and i < len(lineSegments) - 1:
                length = self.getSegmentLength(lineSegmentBegin)
                lineSegment = None

                for j in range(i+1, lineSegmentsCount):
                    lineSegment = lineSegments[j]
                    if self.getSegmentType(lineSegment) != lineSegmentType:
                        break

                    length += self.getSegmentLength(lineSegment)
                    if length > self.m_simplifyPrecision:
                        break

                    lineSegmentEnd = lineSegment
                    lineSegmentEnd.setVertexIndex(len(self.m_lines))
                    i = j

            # Set color
            vertex.color = self.getSegmentColorVector(lineSegmentEnd)

            # Line start
            vertex.position = lineSegmentBegin.getStart()
            if self.m_ignoreZ or qIsNaN(vertex.position.z()):
                vertex.position.setZ(0)
            self.m_lines.append(VertexData.clone(vertex))

            # Line end
            vertex.position = lineSegmentEnd.getEnd()
            if self.m_ignoreZ or qIsNaN(vertex.position.z()):
                vertex.position.setZ(0)
            self.m_lines.append(VertexData.clone(vertex))

            # Store last toolpath point
            if  i == lineSegmentsCount - 1:
                self.m_end = lineSegmentEnd.getEnd()
                if self.m_ignoreZ or qIsNaN(self.m_end.z()):
                    self.m_end.setZ(0)

            # do not forget to increment the variable i
            i += 1

        self.m_geometryUpdated = True
        self.m_indexes = []
        return True

    def updateVectors(self) -> bool:
        UPDATE_WITH_VERTEX_DATA = True

        # Update vertices
        lines = self.m_viewParser.getLines()

        # Update vertices for each line segment
        for i in self.m_indexes:
            # Update vertex pair
            if i < 0 or i > len(lines) - 1:
                continue

            line = lines[i]

            vertexIdx = line.vertexIndex()
            if vertexIdx >= 0:
                color = self.getSegmentColorVector(line)

                # Update vertex array
                if UPDATE_WITH_VERTEX_DATA:
                    self.m_lines[vertexIdx + 0].color = color
                    self.m_lines[vertexIdx + 1].color = color
                else:
                    color_data = np.zeros(3, dtype=np.float32)
                    color_data[0] = color.x()
                    color_data[1] = color.y()
                    color_data[2] = color.z()

                    itemsize = np.float32().itemsize
                    # PROTO write(offset, data, size) all in bytes
                    bufferIndexA = ((vertexIdx + 0) * 10 + 3) * itemsize
                    bufferIndexB = ((vertexIdx + 1) * 10 + 3) * itemsize

                    color_bytes = color_data.tobytes()

                    self.m_vbo.write(bufferIndexA, color_bytes, 3 * itemsize)
                    self.m_vbo.write(bufferIndexB, color_bytes, 3 * itemsize)

        self.m_indexes = []

        return True if UPDATE_WITH_VERTEX_DATA else False

    def prepareRaster(self) -> bool:
        maxImageSize = 8192

        # Generate image
        image = QImage()

        if (
            self.m_viewParser.getModelResolution().width() <= maxImageSize
            and self.m_viewParser.getModelResolution().height() <= maxImageSize
        ):
            image = QImage(
                self.m_viewParser.getModelResolution(), QImage.Format.Format_RGB888
            )
            image.fill(QColor("white"))

            lines = self.m_viewParser.getLineSegments()

            pixelSize = self.m_viewParser.getModelMinLineLength()
            origin = self.m_viewParser.getViewLowerBounds()

            for line in lines:
                if not qIsNaN(line.getEnd().length()):
                    self.setImagePixelColor(
                        image,
                        (line.getEnd().x() - origin.x()) / pixelSize,
                        (line.getEnd().y() - origin.y()) / pixelSize,
                        self.getSegmentColor(line).rgb(),
                    )

        # Create vertices array
        # Clear all vertex data
        self.m_lines = []
        self.m_points = []
        self.m_triangles = []

        if self.m_texture:
            self.m_texture.destroy()
            self.m_texture = None

        vertices: List[VertexData] = []
        vertex = VertexData()

        # Set color
        vertex.color = Util.colorToVector(QColor("red"))

        # Set data type
        vertex.type = VertexData.VertexDataType.VertexDataTypeTriangle

        # Rect
        vertex.data = QVector3D(0, 0, 0)
        vertex.position = QVector3D(
            self.getViewLowerBounds().x(), self.getViewLowerBounds().y(), 0
        )
        vertices.append(VertexData.clone(vertex))

        vertex.data = QVector3D(0, 1, 1)
        vertex.position = QVector3D(
            self.getViewUpperBounds().x(), self.getViewUpperBounds().y(), 0
        )
        vertices.append(VertexData.clone(vertex))

        vertex.data = QVector3D(0, 0, 1)
        vertex.position = QVector3D(
            self.getViewLowerBounds().x(), self.getViewLowerBounds().y(), 0
        )
        vertices.append(VertexData.clone(vertex))

        vertex.data = QVector3D(0, 0, 0)
        vertex.position = QVector3D(
            self.getViewLowerBounds().x(), self.getViewLowerBounds().y(), 0
        )
        vertices.append(VertexData.clone(vertex))

        vertex.data = QVector3D(0, 1, 0)
        vertex.position = QVector3D(
            self.getViewUpperBounds().x(), self.getViewUpperBounds().y(), 0
        )
        vertices.append(VertexData.clone(vertex))

        vertex.data = QVector3D(0, 1, 1)
        vertex.position = QVector3D(
            self.getViewUpperBounds().x(), self.getViewUpperBounds().y(), 0
        )
        vertices.append(VertexData.clone(vertex))

        if not image.isNull():
            self.m_texture = QOpenGLTexture(image)
            self.m_triangles += vertices
            self.m_image = image
        else:
            for i in range(len(vertices)):
                vertices[i].data = QVector3D()
            self.m_lines += vertices
            self.m_image = QImage()

        self.m_geometryUpdated = True
        self.m_indexes = []
        return True

    def updateRaster(self) -> bool:
        if not self.m_image is None:
            lines = self.m_viewParser.getLineSegments()

            pixelSize = self.m_viewParser.getModelMinLineLength()
            origin = self.m_viewParser.getViewLowerBounds()

            for idx in self.m_indexes:
                line = lines[idx]
                self.setImagePixelColor(
                    self.m_image,
                    (line.getEnd().x() - origin.x()) / pixelSize,
                    (line.getEnd().y() - origin.y()) / pixelSize,
                    self.getSegmentColor(line).rgb(),
                )

            if self.m_texture:
                self.m_texture.setData(
                    QOpenGLTexture.PixelFormat.RGB,
                    QOpenGLTexture.PixelType.UInt8,
                    self.m_image.bits(),
                )

        self.m_indexes = []
        return False

    def getSegmentColorVector(self, segment: LineSegment) -> QVector3D:
        return Util.colorToVector(self.getSegmentColor(segment))

    def getSegmentColor(self, segment: LineSegment) -> QColor:
        if segment.isHighlight():
            return self.m_colorHighlight # QVector3D(0.57, 0.51, 0.9);
        elif segment.isDrawn(): 
            return self.m_colorDrawn # QVector3D(0.85, 0.85, 0.85);
        elif segment.isFastTraverse(): 
            return self.m_colorNormal # QVector3D(0.0, 0.0, 0.0);
        elif segment.isZMovement(): 
            return self.m_colorZMovement # QVector3D(1.0, 0.0, 0.0);
        elif self.m_grayscaleSegments:
            if self.m_grayscaleCode == GcodeDrawer.GrayscaleCode.S:
                return QColor.fromHsl(
                    0, 
                    0, 
                    qBound(
                        0, 
                        int(255 - 255.0 / (self.m_grayscaleMax - self.m_grayscaleMin) * segment.getSpindleSpeed()), 
                    255))
            elif self.m_grayscaleCode == GcodeDrawer.GrayscaleCode.Z:
                return QColor.fromHsl(
                    0, 
                    0, 
                    qBound(
                        0, 
                        int(255 - 255.0 / (self.m_grayscaleMax - self.m_grayscaleMin) * segment.getStart().z()), 
                        255))
    
        return self.m_colorNormal # QVector3D(0.0, 0.0, 0.0);

    def setImagePixelColor(self, image: QImage, x: float, y: float, color: int):
        """
        QRgb = int
        """
        if qIsNaN(x) or qIsNaN(y):
            return

        ix = (int)(x)
        iy = (int)(y)

        image.setPixel(ix, iy, color)

        pixel = image.scanLine(int(y))

        # TODO
        # *(pixel + (int)x * 3) = qRed(color)
        # *(pixel + (int)x * 3 + 1) = qGreen(color)
        # *(pixel + (int)x * 3 + 2) = qBlue(color)
