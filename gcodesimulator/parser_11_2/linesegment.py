# This file is a part of "pycut" application.

# This file was originally ported from "linesegment.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

from typing import List

from PySide6.QtGui import QVector3D

from gcodesimulator.parser_11_2.pointsegment import PointSegment


class LineSegment:
    """ """

    def __init__(self):
        self.m_toolhead = 0  # DEFAULT TOOLHEAD ASSUMED TO BE 0!
        self.m_speed = 0.0
        self.m_spindleSpeed = 0.0
        self.m_dwell = 0.0
        self.m_first = None
        self.m_second = None

        self.m_modelStart = None
        self.m_modelEnd = None
        self.m_axesStart = None
        self.m_axesEnd = None

        # Segment index
        self.m_index = -1
        
        # G-code program line index
        self.m_lineIndex = -1

        self.m_vertexIndex = -1

        # Line properties
        self.m_flags = {
            "isAbsolute" : True,
            "isArc" : False,
            "isClockwise" : False,
            "isDrawn" : False,
            "isFastTraverse" : False,
            "isHightlight" : False,
            "isMetric" : True,
            "isSpline":  False,
            "isZMovement" : False,
            "isInverseTimeFeed": False
        }

        self.m_plane = PointSegment.Plane.XY

    def getLineNumber(self) -> int:
        return self.m_lineIndex

    def getStart(self) -> QVector3D:
        return self.m_first

    def setStart(self, vector: QVector3D):
        self.m_first = vector

    def getEnd(self) -> QVector3D:
        return self.m_second

    def setEnd(self, vector: QVector3D):
        self.m_second = vector

    def modelStart(self) -> QVector3D:
        return self.m_modelStart

    def setModelStart(self,  modelStart: QVector3D):
        self.m_modelStart = modelStart

    def modelEnd(self) -> QVector3D:
        return self.m_modelEnd

    def setModelEnd(self, modelEnd: QVector3D):
        self.m_modelEnd = modelEnd

    def axesStart(self) -> QVector3D:
        return self.m_axesStart

    def setAxesStart(self, axesStart: QVector3D):
        self.m_axesStart = axesStart

    def axesEnd(self) -> QVector3D:
        return self.m_axesEnd

    def setAxesEnd(self, axesEnd: QVector3D):
        self.m_axesEnd = axesEnd

    def setToolHead(self, head: int):
        self.m_toolhead = head

    def getToolhead(self) -> int:
        return self.m_toolhead

    def setSpeed(self, s: float):
        self.m_speed = s

    def getSpeed(self) -> float:
        return self.m_speed

    def isAbsolute(self) -> bool:
        return self.m_isAbsolute

    def setIsAbsolute(self, isAbsolute: bool):
        self.m_isAbsolute = isAbsolute

    def setIsArc(self, isA: bool):
        self.m_flags["isArc"] = isA

    def isArc(self) -> bool:
        return self.m_flags["isArc"]

    def isClockwise(self) -> bool:
        return self.m_flags["isClockwise"]

    def setIsClockwise(self, isClockwise: bool):
        self.m_flags["isClockwise"] = isClockwise

    def drawn(self) -> bool:
        return self.m_flags["isDrawn"]

    def setDrawn(self, drawn: bool):
        self.m_flags["isDrawn"] = drawn

    def setIsFastTraverse(self, isF: bool):
        self.m_flags["isFastTraverse"] = isF

    def isFastTraverse(self) -> bool:
        return self.m_flags["isFastTraverse"]

    def isHightlight(self) -> bool:
        return self.m_flags["isHightlight"]

    def setIsHightlight(self, isHightlight: bool):
        self.m_flags["isHightlight"] = isHightlight

    def isMetric(self) -> bool:
        return self.m_flags["isMetric"]

    def setIsMetric(self, isMetric: bool):
        self.m_flags["isMetric"] = isMetric

    def setIsSpline(self, isS: bool):
        self.m_flags["isSpline"] = isS

    def isSpline(self) -> bool:
        return self.m_flags["isSpline"]

    def isZMovement(self) -> bool:
        return self.m_flags["isZMovement"]
    
    def setIsZMovement(self, isZ: bool):
        self.m_flags["isZMovement"] = isZ

    def isInverseTimeFeed(self) -> bool:
        return self.m_flags["isInverseTimeFeed"]
    
    def setIsInverseTimeFeed(self, isTimeFeed: bool):
        self.m_flags["isInverseTimeFeed"] = isTimeFeed

    def vertexIndex(self) -> int:
        return self.m_vertexIndex

    def setVertexIndex(self, vertexIndex: int):
        self.m_vertexIndex = vertexIndex

    def getSpindleSpeed(self) -> float:
        return self.m_spindleSpeed

    def setSpindleSpeed(self, spindleSpeed: float):
        self.m_spindleSpeed = spindleSpeed

    def getDwell(self) -> float:
        return self.m_dwell

    def setDwell(self, dwell: float):
        self.m_dwell = dwell

    def plane(self) -> PointSegment.Plane:
        return self.m_plane

    def setPlane(self, plane: PointSegment.Plane):
        self.m_plane = plane

    def index(self) -> int:
        return self.m_index

    def setIndex(self, index: int):
        self.m_index = index

    def getPointArray(self) -> List[QVector3D]:
        pointarr = []
        pointarr.append(self.m_first)
        pointarr.append(self.m_second)
        return pointarr

    def getPoints(self) -> List[float]:
        points = []
        points.append(self.m_first.x())
        points.append(self.m_first.y())
        points.append(self.m_first.z())
        points.append(self.m_second.x())
        points.append(self.m_second.y())
        points.append(self.m_second.z())
        return points

    def contains(self, point: QVector3D) -> bool:
        line = self.getEnd() - self.getStart()
        pt = point - self.getStart()

        delta = (line - pt).length() - (line.length() - pt.length())

        return delta < 0.01

