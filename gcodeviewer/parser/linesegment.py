# This file is a part of "pycut" application.

# This file was originally ported from "linesegment.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

from typing import List

from PySide6.QtGui import QVector3D

from gcodeviewer.parser.pointsegment import PointSegment


class LineSegment:
    '''
    '''
    def __init__(self):
        self.m_toolhead = 0  # DEFAULT TOOLHEAD ASSUMED TO BE 0!
        self.m_speed = 0.0
        self.m_spindleSpeed = 0.0
        self.m_dwell = 0.0
        self.m_first = None
        self.m_second = None

        # Line properties
        self.m_isZMovement = False
        self.m_isArc = False
        self.m_isClockwise = True
        self.m_isFastTraverse = False
        self.m_lineNumber = True
        self. m_drawn = False
        self.m_isMetric = True
        self.m_isAbsolute = True
        self.m_isHightlight = False
        self.m_vertexIndex = 0

        self.m_plane = PointSegment.Plane.XY

    def getLineNumber(self) -> int:
        return self.m_lineNumber

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

    def getStart(self) -> QVector3D:
        return self.m_first

    def setStart(self, vector: QVector3D):
        self.m_first = vector

    def getEnd(self) -> QVector3D:
        return self.m_second

    def setEnd(self, vector: QVector3D):
        self.m_second = vector

    def setToolHead(self, head: int):
        self.m_toolhead = head

    def getToolhead(self) -> int:
        return self.m_toolhead

    def setSpeed(self, s: float):
        self.m_speed = s

    def getSpeed(self) -> float:
        return self.m_speed

    def setIsZMovement(self, isZ: bool):
        self.m_isZMovement = isZ

    def isZMovement(self) -> bool:
        return self.isZMovement

    def setIsArc(self, isA: bool):
        self.m_isArc = isA

    def isArc(self) -> bool:
        return self.m_isArc

    def setIsFastTraverse(self, isF: bool):
        self.m_isFastTraverse = isF

    def isFastTraverse(self) -> bool:
        return self.m_isFastTraverse

    def contains(self, point: QVector3D) -> bool:
        line = self.getEnd() - self.getStart()
        pt = point - self.getStart()

        delta = (line - pt).length() - (line.length() - pt.length())

        return delta < 0.01

    def drawn(self) -> bool:
        return self.m_drawn

    def setDrawn(self, drawn: bool):
        self.m_drawn = drawn

    def isMetric(self) -> bool:
        return self.m_isMetric

    def setIsMetric(self, isMetric: bool):
        self.m_isMetric = isMetric

    def isAbsolute(self) -> bool:
        return self.m_isAbsolute

    def setIsAbsolute(self, isAbsolute: bool):
        self.m_isAbsolute = isAbsolute

    def isHightlight(self) -> bool:
        return self.m_isHightlight

    def setIsHightlight(self, isHightlight: bool):
        self.m_isHightlight = isHightlight

    def vertexIndex(self) -> int:
        return self.m_vertexIndex

    def setVertexIndex(self, vertexIndex: int):
        self.m_vertexIndex = vertexIndex

    def getSpindleSpeed(self) -> float:
        return self.m_spindleSpeed

    def setSpindleSpeed(self, spindleSpeed: float):
        self.m_spindleSpeed = spindleSpeed

    def getDwell(self)  -> float:
        return self.m_dwell

    def setDwell(self, dwell: float):
        self.m_dwell = dwell

    def isClockwise(self) -> bool:
        return self.m_isClockwise

    def setIsClockwise(self, isClockwise: bool):
        self.isClockwise = isClockwise

    def plane(self) -> PointSegment.Plane :
        return self.m_plane

    def setPlane(self, plane: PointSegment.Plane):
        self.m_plane = plane


