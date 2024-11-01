# This file is a part of "pycut" application.

# This file was originally ported from "pointsegment.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

from typing import List
from typing import cast

from enum import Enum

from PySide6.QtGui import QVector3D

from gcodesimulator_python.candle_parser.arcproperties import ArcProperties


class PointSegment:
    """ """

    class Plane(Enum):
        XY = 0
        ZX = 1
        YZ = 2

    def __init__(self, vec: QVector3D | None = None, num: int | None = None):
        """ """
        self.m_toolhead = 0
        self.m_isMetric = True
        self.m_isAbsolute = True
        self.m_isZMovement = False
        self.m_isArc = False
        self.m_isFastTraverse = False
        self.m_lineNumber = -1
        self.m_arcProperties: ArcProperties | None = None
        self.m_speed = 0.0
        self.m_spindleSpeed = 0.0
        self.m_dwell = 0.0
        self.m_plane = self.Plane.XY

        self.m_point: QVector3D | None = None

        if vec != None and num != None:
            v = cast(QVector3D, vec)
            n = cast(int, num)
            self.m_point = QVector3D(v.x(), v.y(), v.z())
            self.m_lineNumber = n

    @classmethod
    def PointSegment_FromSegment(cls, ps: "PointSegment"):
        this = cls.PointSegment_FromQVector3D(ps.point(), ps.getLineNumber())

        this.m_toolhead = ps.getToolhead()
        this.m_speed = ps.getSpeed()
        this.m_isMetric = ps.isMetric()
        this.m_isZMovement = ps.isZMovement()
        this.m_isFastTraverse = ps.isFastTraverse()
        this.m_isAbsolute = ps.isAbsolute()

        if ps.isArc():
            this.setArcCenter(ps.center())
            this.setRadius(ps.getRadius())
            this.setIsClockwise(ps.isClockwise())
            this.m_plane = ps.plane()

        return this

    @classmethod
    def PointSegment_FromQVector3D(cls, b: QVector3D, num: int):
        this = PointSegment()
        this.m_point = QVector3D(b.x(), b.y(), b.z())
        this.m_lineNumber = num

        return this

    @classmethod
    def PointSegment_FromVectorQVector3DQVector3D(
        cls,
        point: QVector3D,
        num: int,
        center: QVector3D,
        radius: float,
        clockwise: bool,
    ):
        this = PointSegment(point, num)

        this.m_isArc = True
        this.m_arcProperties = ArcProperties()
        this.m_arcProperties.center = QVector3D(center.x(), center.y(), center.z())
        this.m_arcProperties.radius = radius
        this.m_arcProperties.isClockwise = clockwise

    def setPoint(self, m_point: QVector3D):
        self.m_point = m_point

    def point(self) -> QVector3D:
        return cast(QVector3D, self.m_point)

    def points(self) -> List[float]:
        points = []

        pt = cast(QVector3D, self.m_point)

        points.append(pt.x())
        points.append(pt.y())

        return points

    def setToolHead(self, head: int):
        self.m_toolhead = head

    def getToolhead(self) -> int:
        return self.m_toolhead

    def setLineNumber(self, num: int):
        self.m_lineNumber = num

    def getLineNumber(self) -> int:
        return self.m_lineNumber

    def setSpeed(self, s: float):
        self.m_speed = s

    def getSpeed(self) -> float:
        return self.m_speed

    def setIsZMovement(self, isZ: bool):
        self.m_isZMovement = isZ

    def isZMovement(self) -> bool:
        return self.m_isZMovement

    def setIsMetric(self, m_isMetric: bool):
        self.m_isMetric = m_isMetric

    def isMetric(self) -> bool:
        return self.m_isMetric

    def setIsArc(self, isA: bool):
        self.m_isArc = isA

    def isArc(self) -> bool:
        return self.m_isArc

    def setIsFastTraverse(self, isF: bool):
        self.m_isFastTraverse = isF

    def isFastTraverse(self) -> bool:
        return self.m_isFastTraverse

    def setArcCenter(self, center: QVector3D):
        if self.m_arcProperties is None:
            self.m_arcProperties = ArcProperties()

        self.m_arcProperties.center = center

    def centerPoints(self) -> List[float]:
        points = []

        if self.m_arcProperties != None:
            arcProps = cast(ArcProperties, self.m_arcProperties)
            if arcProps.center != None:
                points.append(arcProps.center.x())
                points.append(arcProps.center.y())
                points.append(arcProps.center.z())

        return points

    def center(self) -> QVector3D | None:
        if self.m_arcProperties != None:
            arcProps = cast(ArcProperties, self.m_arcProperties)
            return arcProps.center

        return QVector3D(0, 0, 0)

    def setIsClockwise(self, clockwise: bool):
        if self.m_arcProperties == None:
            self.m_arcProperties = ArcProperties()

        arcProps = cast(ArcProperties, self.m_arcProperties)
        arcProps.isClockwise = clockwise

    def isClockwise(self) -> bool:
        if self.m_arcProperties != None:
            arcProps = cast(ArcProperties, self.m_arcProperties)
            if arcProps.center != None:
                return arcProps.isClockwise

        return False

    def setRadius(self, rad: float):
        if self.m_arcProperties == None:
            self.m_arcProperties = ArcProperties()

        arcProps = cast(ArcProperties, self.m_arcProperties)
        arcProps.radius = rad

    def getRadius(self) -> float:
        if self.m_arcProperties != None:
            arcProps = cast(ArcProperties, self.m_arcProperties)
            if arcProps.center != None:
                return arcProps.radius

        return 0.0

    def convertToMetric(self):
        if self.m_isMetric:
            return

        self.m_isMetric = True
        self.m_point.setX(self.m_point.x() * 25.4)
        self.m_point.setY(self.m_point.y() * 25.4)
        self.m_point.setZ(self.m_point.z() * 25.4)

        if self.m_isArc and self.m_arcProperties != None:
            self.m_arcProperties.center.setX(self.m_arcProperties.center.x() * 25.4)
            self.m_arcProperties.center.setY(self.m_arcProperties.center.y() * 25.4)
            self.m_arcProperties.center.setZ(self.m_arcProperties.center.z() * 25.4)
            self.m_arcProperties.radius *= 25.4

    def isAbsolute(self) -> bool:
        return self.m_isAbsolute

    def setIsAbsolute(self, isAbsolute: bool):
        self.m_isAbsolute = isAbsolute

    def plane(self) -> "PointSegment.Plane":
        return self.m_plane

    def setPlane(self, plane: "PointSegment.Plane"):
        self.m_plane = plane

    def getSpindleSpeed(self) -> float:
        return self.m_spindleSpeed

    def setSpindleSpeed(self, spindleSpeed: float):
        self.m_spindleSpeed = spindleSpeed

    def getDwell(self) -> float:
        return self.m_dwell

    def setDwell(self, dwell: float):
        self.m_dwell = dwell
