# This file is a part of "pycut" application.

# This file was originally ported from "pointsegment.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

from typing import List
from typing import cast

from enum import Enum

from PySide6.QtGui import QVector3D

from gcodeviewer_11_2.parser.arcproperties import ArcProperties
from gcodeviewer_11_2.parser.splineproperties import SplineProperties


class PointSegment:
    """ """

    class Plane(Enum):
        XY = 0
        ZX = 1
        YZ = 2

    def __init__(self, point: QVector3D | None = None, axes: QVector3D | None = None, num: int | None = None):
        """ """
        self.m_toolhead = 0
        self.m_isMetric = True
        self.m_isAbsolute = True
        self.m_isInverseTimeFeed = False
        self.m_isZMovement = False
        self.m_isArc = False
        self.m_isSpline = False
        self.m_isFastTraverse = False
        self.m_lineNumber = -1
        self.m_arcProperties: ArcProperties | None = None
        self.m_splineProperties: SplineProperties | None = None
        self.m_speed = 0.0
        self.m_spindleSpeed = 0.0
        self.m_dwell = 0.0
        self.m_plane = self.Plane.XY

        self.m_point: QVector3D | None = None
        self.m_axes: QVector3D | None = None

        if point is not None and axes is not None and num != None:
            p = cast(QVector3D, point)
            x = cast(QVector3D, axes)
            n = cast(int, num)
            self.m_point = QVector3D(p.x(), p.y(), p.z())
            self.m_axes = QVector3D(x.x(), x.y(), x.z())
            self.m_lineNumber = n

    @classmethod
    def PointSegment_FromSegment(cls, ps: "PointSegment"):
        this = cls.PointSegment_FromQVector3D(ps.point(), ps.axes(), ps.getLineNumber())

        this.m_toolhead = ps.getToolhead()
        this.m_speed = ps.getSpeed()
        this.m_isMetric = ps.isMetric()
        this.m_isZMovement = ps.isZMovement()
        this.m_isFastTraverse = ps.isFastTraverse()
        this.m_isAbsolute = ps.isAbsolute()
        this.m_dwell = ps.getDwell()
        this.m_spindleSpeed = ps.getSpindleSpeed()

        if ps.isArc():
            this.setArcCenter(ps.center())
            this.setRadius(ps.getRadius())
            this.setIsClockwise(ps.isClockwise())
            this.m_plane = ps.plane()

        return this

    @classmethod
    def PointSegment_FromQVector3D(cls, point: QVector3D, axes: QVector3D, num: int):
        this = PointSegment()
        this.m_point = QVector3D(point.x(), point.y(), point.z())
        this.m_axes = QVector3D(axes.x(), axes.y(), axes.z())
        this.m_lineNumber = num

        return this

    @classmethod
    def PointSegment_FromVectorQVector3DQVector3D(
        cls,
        point: QVector3D,
        axes: QVector3D,
        num: int,
        center: QVector3D,
        radius: float,
        clockwise: bool,
    ):
        this = PointSegment(point, axes, num)

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

    def setIsSpline(self, isS: bool):
        self.m_isSpline = isS

    def isSpline(self) -> bool:
        return self.m_isSpline

    def setSplineControlPoints(self, cp1: QVector3D, cp2: QVector3D | None):
        if self.m_splineProperties == None:
            self.m_splineProperties = SplineProperties()

        self.m_splineProperties.controlPoint1 = QVector3D(cp1.x(), cp1.y(), cp1.z());
        
        if cp2 is not None:
            self.m_splineProperties.controlPoint2 = QVector3D(cp2.x(), cp2.y(), cp2.z())
    
        self.setIsSpline(True)

    def getSplineControlPoint1(self) -> QVector3D | None:
        if self.m_splineProperties != None:
            return self.m_splineProperties.controlPoint1
    
        return None

    def getSplineControlPoint2(self) -> QVector3D | None:
        if self.m_splineProperties != None:
             return self.m_splineProperties.controlPoint2
        
        return None

    def getSplineType(self) -> SplineProperties.SplineType:
        if self.m_splineProperties != None:
            return self.m_splineProperties.type
     
        return SplineProperties.SplineType.CUBIC_SPLINE

    def setSplineType(self, type: SplineProperties.SplineType):
        if self.m_splineProperties == None:
            self.m_splineProperties = SplineProperties()
    
        self.m_splineProperties.type = type;

    def getArcTurns(self) -> int:
        if self.m_arcProperties != None :
            return self.m_arcProperties.turns
        return 1
    
    def setArcTurns(self, turns: int):
        if self.m_arcProperties == None:
            self.m_arcProperties = ArcProperties()

        if turns > 0:
            self.m_arcProperties.turns = turns
        else:
            self.m_arcProperties.turns = 1

    def setAxes(self, axes: QVector3D):
        self.m_axes = axes
     
    def axes(self) -> QVector3D:
        return cast(QVector3D, self.m_axes)

    def isInverseTimeFeed(self) -> bool:
        return self.m_isInverseTimeFeed
    
    def setIsInverseTimeFeed(self, isInverseTimeFeed: bool):
        self.m_isInverseTimeFeed = isInverseTimeFeed

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

    def center(self) -> QVector3D:
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
