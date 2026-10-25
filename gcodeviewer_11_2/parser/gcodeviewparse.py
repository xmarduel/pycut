# This file is a part of "pycut" application.

# This file was originally ported from "gcodeviewparse.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

import math

from typing import List
from typing import Dict
from typing import Any
from typing import Optional
from typing import cast

from enum import Enum

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QMatrix4x4

from PySide6 import QtCore
from PySide6.QtCore import qIsNaN

from gcodeviewer_11_2.parser.linesegment import LineSegment
from gcodeviewer_11_2.parser.gcodeparser import GcodeParser
from gcodeviewer_11_2.parser.gcodepreprocessorutils import GcodePreprocessorUtils

from gcodesimulator.util.util import Util
from gcodesimulator.util.util import qQNaN


class GcodeViewParse:
    """ """

    class RotationAxis(Enum):
        RotationAxisA = 0
        RotationAxisB = 1
        RotationAxisC = 2

    def __init__(self, parent=None):
        self.absoluteMode = True
        self.absoluteIJK = False

        self.currentLine = 0  # for assigning line numbers to segments.

        self.m_lineSegments: List[LineSegment] = []
        self.m_lineSegmentsIndexes: List[List[int]] = [[]]

        # Parsing state.
        self.lastPoint: QVector3D = None

        self.m_axesRotationVectors: Dict[GcodeViewParse.RotationAxis, QVector3D] = {}

        self.setAxisRotationVector(GcodeViewParse.RotationAxis.RotationAxisA, Util.rotationVector(Util.RotationVector.RotationVectorX))
        self.setAxisRotationVector(GcodeViewParse.RotationAxis.RotationAxisB, Util.rotationVector(Util.RotationVector.RotationVectorX))
        self.setAxisRotationVector(GcodeViewParse.RotationAxis.RotationAxisC, Util.rotationVector(Util.RotationVector.RotationVectorX))

        # Parsed object
        self.m_viewLowerBounds = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_viewUpperBounds = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_modelLowerBounds = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_modelUpperBounds = QVector3D(qQNaN(), qQNaN(), qQNaN())

        self.m_modelMinLineLength = qQNaN()
       
        # Debug
        self.debug = True

    def getViewLowerBounds(self) -> QVector3D:
        return self.m_viewLowerBounds

    def getViewUpperBounds(self) -> QVector3D:
        return self.m_viewUpperBounds

    def getModelLowerBounds(self) -> QVector3D:
        return self.m_modelLowerBounds

    def getModelUpperBounds(self) -> QVector3D:
        return self.m_modelUpperBounds

    def updateViewBounds(self, point: QVector3D):
        self.m_viewLowerBounds = Util.nMinVector(self.m_viewLowerBounds, point)
        self.m_viewUpperBounds = Util.nMaxVector(self.m_viewUpperBounds, point)

    def updateModelBounds(self, point: QVector3D):
        self.m_modelLowerBounds = Util.nMinVector(self.m_modelLowerBounds, point)
        self.m_modelUpperBounds = Util.nMaxVector(self.m_modelUpperBounds, point)

    def updateModelMinLineLength(self, start: QVector3D, end: QVector3D):
        length = (start - end).length()

        if (not qIsNaN(length)) and length != 0:
            if qIsNaN(self.m_modelMinLineLength):
                self.m_modelMinLineLength = length
            else: 
                self.m_modelMinLineLength = min(self.m_modelMinLineLength, length)

    def reset(self):
        self.m_lineSegments = []
        self.m_lineSegmentsIndexes = []

        self.currentLine = 0

        self.m_viewLowerBounds = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_viewUpperBounds = QVector3D(qQNaN(), qQNaN(), qQNaN())

        self.m_modelLowerBounds = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_modelUpperBounds = QVector3D(qQNaN(), qQNaN(), qQNaN())
        
        self.m_modelMinLineLength = qQNaN()

    def getModelMinLineLength(self) -> float:
        return self.m_modelMinLineLength

    def getModelResolution(self) -> QtCore.QSize:
        return QtCore.QSize(
            ((self.m_modelUpperBounds.x() - self.m_modelLowerBounds.x()) / self.m_modelMinLineLength) + 1,
            ((self.m_modelUpperBounds.y() - self.m_modelLowerBounds.y()) / self.m_modelMinLineLength) + 1,
        )

    def setAxisRotationVector(self, axis: RotationAxis, vector: QVector3D):
        self.m_axesRotationVectors[axis] = vector

    def getAxisRotationVector(self, axis: RotationAxis) -> QVector3D:
        return self.m_axesRotationVectors[axis]

    def axisRotationUsed(self, axis: RotationAxis) -> bool:
        if len(self.m_lineSegments) > 0:
            if axis == GcodeViewParse.RotationAxis.RotationAxisA:
                if not qIsNaN(self.m_lineSegments[-1].axesEnd().x()):
                    return True
            elif axis == GcodeViewParse.RotationAxis.RotationAxisB:
                if not qIsNaN(self.m_lineSegments[-1].axesEnd().y()):
                    return True
            elif axis == GcodeViewParse.RotationAxis.RotationAxisC:
                if not qIsNaN(self.m_lineSegments[-1].axesEnd().z()):
                    return True
    
        return False

    '''
    def toObjRedux(
        self, gcode: List[str], arcPrecision: float, arcDegreeMode: bool
    ) -> List[LineSegment]:
        gp = GcodeParser()

        for s in gcode:
            gp.addCommand(s)

        return self.getLinesFromParser(gp, arcPrecision, arcDegreeMode)
    '''

    def updateFromParser(
        self, gp: GcodeParser, arcPrecision: float, arcDegreeMode: bool, isCancelled: Any
    ) -> List[LineSegment]:
        psl = gp.getPointSegmentList()
        # For a line segment list ALL arcs must be converted to lines.
        minArcLength = 0.1
        rotationDelta = 5.0

        start: Optional[QVector3D] = None
        end: Optional[QVector3D] = None

        startAxes: Optional[QVector3D] = None
        endAxes: Optional[QVector3D] = None

        startRotation = QMatrix4x4()
        endRotation = QMatrix4x4()

        index = 0
        lineIndex = 0

        # Prepare segments indexes
        self.m_lineSegmentsIndexes = [[] for _ in range(len(psl))]

        for segment in psl:
            ps = segment
            isMetric = ps.isMetric()
            ps.convertToMetric()

            end = ps.point()
            endAxes = ps.axes()

            # start is null for the first iteration.
            if start is not None:
                # Expand arc for graphics.
                if ps.isArc():
                    points = GcodePreprocessorUtils.generatePointsAlongArcBDring_Arc(
                        ps.plane(),
                        cast(QVector3D, start),
                        cast(QVector3D, end),
                        ps.center(),
                        ps.isClockwise(),
                        ps.getRadius(),
                        minArcLength,
                        arcPrecision,
                        arcDegreeMode,
                        ps.getArcTurns()
                    )
                    # Create line segments from points.
                    segments = len(points)
                    if segments > 0:
                        rotation = Util.nAssign(cast(QVector3D, startAxes).x()) - Util.nAssign(endAxes.x())
                        segmentRotation = rotation / segments

                        startPoint = start
                        for nextPoint in points:
                            if nextPoint == startPoint:
                                continue

                            if not Util.nIsNaN(self.m_axesRotationVectors[GcodeViewParse.RotationAxis.RotationAxisA]):
                                endRotation.rotate(segmentRotation, self.m_axesRotationVectors[GcodeViewParse.RotationAxis.RotationAxisA])
                                 
                            #ls = LineSegment(startRotation * startPoint, endRotation * nextPoint, lineIndex)
                            ls = LineSegment()

                            # ls.setIsArc(ps.isArc())
                            # ls.setIsClockwise(ps.isClockwise())
                            # ls.setPlane(ps.plane())
                            # ls.setIsFastTraverse(ps.isFastTraverse())
                            # ls.setIsZMovement(ps.isZMovement())
                            # ls.setIsMetric(isMetric)
                            # ls.setIsAbsolute(ps.isAbsolute())
                            # ls.setIsInverseTimeFeed(ps.isInverseTimeFeed())
                            # ls.setSpeed(ps.getSpeed())
                            # ls.setSpindleSpeed(ps.getSpindleSpeed())
                            # ls.setDwell(ps.getDwell())
                            # ls.setModelStart(startPoint)
                            # ls.setModelEnd(nextPoint)
                            # ls.setAxesStart(*startAxes)
                            # ls.setAxesEnd(*endAxes)
                            # ls.setIndex(index++)

                            #this->updateViewBounds(ls->getEnd());
                            #this->updateModelBounds(nextPoint);

                            ls.m_flags.isArc = ps.m_isArc
                            ls.m_flags.isClockwise = ps.isClockwise()
                            ls.m_plane = ps.m_plane
                            ls.m_flags.isFastTraverse = ps.m_isFastTraverse
                            ls.m_flags.isZMovement = ps.m_isZMovement
                            ls.m_flags.isMetric = isMetric
                            ls.m_flags.isAbsolute = ps.m_isAbsolute
                            ls.m_flags.isInverseTimeFeed = ps.m_isInverseTimeFeed
                            ls.m_speed = ps.m_speed
                            ls.m_spindleSpeed = ps.m_spindleSpeed
                            ls.m_dwell = ps.m_dwell
                            ls.m_modelStart = startPoint
                            ls.m_modelEnd = nextPoint
                            ls.m_axesStart = startAxes
                            ls.m_axesEnd = endAxes
                            index = index + 1 
                            ls.m_index = index

                            ls.m_first = startPoint * startRotation
                            ls.m_second = nextPoint * endRotation
                            ls.m_lineIndex = lineIndex

                            self.updateViewBounds(ls.getEnd())
                            self.updateModelBounds(nextPoint)

                            self.m_lineSegments.append(ls)
                            self.m_lineSegmentsIndexes[ps.getLineNumber()].append(len(self.m_lineSegments) - 1)

                            startPoint = nextPoint
                            startRotation = endRotation

                        lineIndex += 1

                # Expand spline for graphics
                elif ps.isSpline():
                    points = GcodePreprocessorUtils.generatePointsAlongSpline(
                        start, 
                        end,
                        cast(QVector3D, ps.getSplineControlPoint1()),
                        ps.getSplineControlPoint2())

                    # Create line segments from points
                    segments = len(points)
                    if segments > 0:
                        rotation = Util.nAssign(cast(QVector3D, startAxes).x()) - Util.nAssign(endAxes.x())
                        segmentRotation = rotation / segments

                        startPoint = start
                        for nextPoint in points:
                            if not Util.nIsNaN(self.m_axesRotationVectors[GcodeViewParse.RotationAxis.RotationAxisA]):
                                endRotation.rotate(segmentRotation, self.m_axesRotationVectors[GcodeViewParse.RotationAxis.RotationAxisA])

                            #ls = LineSegment(startRotation * startPoint, endRotation * nextPoint, lineIndex);
                            ls = LineSegment()

                            #ls->setIsSpline(true);
                            #ls->setIsFastTraverse(ps->isFastTraverse());
                            #ls->setIsZMovement(ps->isZMovement());
                            #ls->setIsMetric(isMetric);
                            #ls->setIsAbsolute(ps->isAbsolute());
                            #ls->setIsInverseTimeFeed(ps->isInverseTimeFeed());
                            #ls->setSpeed(ps->getSpeed());
                            #ls->setSpindleSpeed(ps->getSpindleSpeed());
                            #ls->setDwell(ps->getDwell());
                            #ls->setModelStart(startPoint);
                            #ls->setModelEnd(nextPoint);
                            #ls->setAxesStart(*startAxes);
                            #ls->setAxesEnd(*endAxes);
                            #ls->setIndex(index++);

                            #this->updateViewBounds(ls->getEnd());
                            #this->updateModelBounds(nextPoint);

                            ls.m_flags.isSpline = True
                            ls.m_flags.isFastTraverse = ps.m_isFastTraverse
                            ls.m_flags.isZMovement = ps.m_isZMovement
                            ls.m_flags.isMetric = isMetric
                            ls.m_flags.isAbsolute = ps.m_isAbsolute
                            ls.m_flags.isInverseTimeFeed = ps.m_isInverseTimeFeed
                            ls.m_speed = ps.m_speed
                            ls.m_spindleSpeed = ps.m_spindleSpeed
                            ls.m_dwell = ps.m_dwell
                            ls.m_modelStart = startPoint
                            ls.m_modelEnd = nextPoint
                            ls.m_axesStart = startAxes
                            ls.m_axesEnd = endAxes
                            index = index + 1 
                            ls.m_index = index

                            ls.m_first = startPoint * startRotation
                            ls.m_second = nextPoint * endRotation
                            ls.m_lineIndex = lineIndex
                      
                            self.updateViewBounds(ls.getEnd())
                            self.updateModelBounds(nextPoint)                           

                            self.m_lineSegments.append(ls)
                            self.m_lineSegmentsIndexes[ps.getLineNumber()].append(len(self.m_lineSegments) - 1)

                            startPoint = nextPoint
                            startRotation = endRotation
                    
                        lineIndex += 1
                
                # Line
                else:
                    startPoint = start

                    rotation = Util.nAssign(cast(QVector3D, startAxes).x()) - Util.nAssign(endAxes.x())
                    segments = int(max(math.fabs(rotation / rotationDelta), 1))
                    segmentVector = (end - startPoint) / segments
                    segmentRotation = rotation / segments

                    # Create line segments on axis rotation
                    for i in range(0, segments):
                
                        nextPoint =  startPoint + segmentVector if segments > 1 else end

                        if not Util.nIsNaN(self.m_axesRotationVectors[GcodeViewParse.RotationAxis.RotationAxisA]):
                            endRotation.rotate(segmentRotation, self.m_axesRotationVectors[GcodeViewParse.RotationAxis.RotationAxisA])
                        
                        #ls = new LineSegment(startRotation * startPoint, endRotation * nextPoint, lineIndex);
                        ls = LineSegment()
                        ls.m_first = startPoint * startRotation
                        ls.m_second = nextPoint * endRotation
                        ls.m_lineIndex = lineIndex

                        # ls.setIsArc(ps.isArc())
                        # ls.setIsFastTraverse(ps.isFastTraverse())
                        # ls.setIsZMovement(ps.isZMovement())
                        # ls.setIsMetric(isMetric)
                        # ls.setIsAbsolute(ps.isAbsolute())
                        # ls.setSpeed(ps.getSpeed())
                        # ls.setSpindleSpeed(ps.getSpindleSpeed())
                        # ls.setDwell(ps.getDwell())

                        ls.m_flags.isArc = ps.m_isArc
                        ls.m_flags.isFastTraverse = ps.m_isFastTraverse
                        ls.m_flags.isZMovement = ps.m_isZMovement
                        ls.m_flags.isMetric = isMetric
                        ls.m_flags.isAbsolute = ps.m_isAbsolute
                        ls.m_flags.isInverseTimeFeed = ps.m_isInverseTimeFeed
                        ls.m_speed = ps.m_speed
                        ls.m_spindleSpeed = ps.m_spindleSpeed
                        ls.m_dwell = ps.m_dwell

                        ls.m_modelStart = startPoint
                        ls.m_modelEnd = nextPoint
                        ls.m_axesStart = startAxes
                        ls.m_axesEnd = endAxes
                        ls.m_index = index

                        self.updateViewBounds(ls.getEnd())
                        self.updateModelBounds(nextPoint)
                        self.updateModelMinLineLength(startPoint, nextPoint)

                        self.m_lineSegments.append(ls)
                        self.m_lineSegmentsIndexes[ps.getLineNumber()].append(len(self.m_lineSegments) - 1)

                        startPoint = nextPoint
                        startRotation = endRotation

                    index += 1 
                    lineIndex += 1

            start = end
            startAxes = endAxes

            if isCancelled: #  and isCancelled():
                return []

        return self.m_lineSegments

    def getLineSegments(self) -> List[LineSegment]:
        return self.m_lineSegments

    def getLineSegmentsIndexes(self) -> List[List[int]]:
        return self.m_lineSegmentsIndexes
