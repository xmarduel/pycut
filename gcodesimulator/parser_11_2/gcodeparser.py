# This file is a part of "pycut" application.

# This file was originally ported from "gcodeparser.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

from functools import singledispatchmethod
import math

from typing import List
from typing import cast

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QMatrix4x4
from PySide6.QtCore import qIsNaN

from gcodesimulator.parser_11_2.pointsegment import PointSegment
from gcodesimulator.parser_11_2.gcodepreprocessorutils import GcodePreprocessorUtils
from gcodesimulator.parser_11_2.splineproperties import SplineProperties

from gcodesimulator.util.util import Util


class GcodeParser:
    """ """

    def __init__(self, parent=None):
        """ """
        # Current state
        self.m_isMetric = True
        self.m_inAbsoluteMode = True
        self.m_inAbsoluteIJKMode = False
        self.m_isInverseTimeFeed = False
        self.m_lastGcodeCommand = -1
        self.m_commandNumber = 0

        self.m_currentPoint = QVector3D(0, 0, 0)
        self.m_currentAxes = QVector3D(0, 0, 0)
        self.m_currentPlane = PointSegment.Plane.XY

        # Settings
        self.m_speedOverride = -1
        self.m_truncateDecimalLength = 40
        self.m_removeAllWhitespace = True
        self.m_convertArcsToLines = False
        self.m_smallArcThreshold = 1.0
        # Not configurable outside, but maybe it should be.
        self.m_smallArcSegmentLength = 0.3
        self.m_lastSpeed = 0
        self.m_traverseSpeed = 300
        self.m_lastSpindleSpeed = 0
        self.m_lastSplinePQ = QVector3D(0, 0, 0)  # Last P,Q from previous G5 for auto-matching

        # The gcode.
        self.m_points: List[PointSegment] = []

        self.reset()

    def getConvertArcsToLines(self) -> bool:
        return self.m_convertArcsToLines

    def setConvertArcsToLines(self, convertArcsToLines: bool):
        self.m_convertArcsToLines = convertArcsToLines

    def getRemoveAllWhitespace(self) -> bool:
        return self.m_removeAllWhitespace

    def setRemoveAllWhitespace(self, removeAllWhitespace: bool):
        self.m_removeAllWhitespace = removeAllWhitespace

    def getSmallArcSegmentLength(self) -> float:
        return self.m_smallArcSegmentLength

    def setSmallArcSegmentLength(self, smallArcSegmentLength: float):
        self.m_smallArcSegmentLength = smallArcSegmentLength

    def getSmallArcThreshold(self) -> float:
        return self.m_smallArcThreshold

    def setSmallArcThreshold(self, smallArcThreshold: float):
        self.m_smallArcThreshold = smallArcThreshold

    def getSpeedOverride(self) -> float:
        return self.m_speedOverride

    def setSpeedOverride(self, speedOverride: float):
        self.m_speedOverride = speedOverride

    def getTruncateDecimalLength(self) -> int:
        return self.m_truncateDecimalLength

    def setTruncateDecimalLength(self, truncateDecimalLength: int):
        self.m_truncateDecimalLength = truncateDecimalLength

    def reset(self, initialPoint: QVector3D | None = None, initialAxes: QVector3D | None = None):
        # print("reseting gp %s" % initialPoint)

        if initialPoint is None:
            # initialPoint = QVector3D(qQNaN(), qQNaN(), qQNaN()) # CANDLE: this line!
            initialPoint = QVector3D(0.0, 0.0, 0.0)

        if initialAxes is None:
            # initialPAxes = QVector3D(qQNaN(), qQNaN(), qQNaN()) # CANDLE: this line!
            initialAxes = QVector3D(0.0, 0.0, 0.0)

        self.m_points = []

        # The unspoken home location.
        self.m_currentPoint = initialPoint
        self.m_initialAxes = initialAxes
        self.m_currentPlane = PointSegment.Plane.XY
        self.m_points.append(
            PointSegment.PointSegment_FromQVector3D(self.m_currentPoint, self.m_initialAxes, -1)
        )

    @singledispatchmethod
    def addCommand(self, command) -> PointSegment | None:
        raise NotImplementedError("Cannot addCommand command")

    @addCommand.register
    def _(self, command: str) -> PointSegment | None:
        stripped = GcodePreprocessorUtils.removeComment(command)
        args = GcodePreprocessorUtils.splitCommand(stripped)
        return self.addCommand(args)

    @addCommand.register
    def _(self, command: list) -> PointSegment | None:
        if len(command) == 0:
            return None

        return self.processCommand(command)

    def getCurrentPoint(self) -> QVector3D:
        return self.m_currentPoint

    def expandArc(self) -> List[PointSegment]:
        startSegment = self.m_points[-2]
        lastSegment = self.m_points[-1]

        empty: List[PointSegment] = []

        # Can only expand arcs.
        if not lastSegment.isArc():
            return empty

        # Get precalculated stuff.
        start = startSegment.point()
        end = lastSegment.point()
        center = lastSegment.center()
        radius = lastSegment.getRadius()
        clockwise = lastSegment.isClockwise()
        plane = startSegment.plane()

        #
        # Start expansion.
        #

        expandedPoints = GcodePreprocessorUtils.generatePointsAlongArcBDring_Arc(
            plane,
            start,
            end,
            center,
            clockwise,
            radius,
            self.m_smallArcThreshold,
            self.m_smallArcSegmentLength,
            False,
            lastSegment.getArcTurns()
        )

        # Validate output of expansion.
        if len(expandedPoints) == 0:
            return empty

        # Remove the last point now that we're about to expand it.
        self.m_points.pop(-1)
        self.m_commandNumber = self.m_commandNumber - 1

        # Initialize return value
        psl = []

        # Create line segments from points.

        # skip first element.
        for k in range(1, len(expandedPoints) - 1):
            temp = PointSegment.PointSegment_FromQVector3D(
                expandedPoints[k + 1], QVector3D(), self.m_commandNumber
            )
            self.m_commandNumber += 1
            temp.setIsMetric(lastSegment.isMetric())
            self.m_points.append(temp)
            psl.append(temp)

        # Update the new endpoint.
        self.m_currentPoint.setX(self.m_points[-1].point().x())
        self.m_currentPoint.setY(self.m_points[-1].point().y())
        self.m_currentPoint.setZ(self.m_points[-1].point().z())

        return psl

    def preprocessCommands(self, commands: List[str]) -> List[str]:
        result: List[str] = []

        for command in commands:
            result.extend(self.preprocessCommand(command))

        return result

    def preprocessCommand(self, command: str) -> List[str]:
        result: List[str] = []
        hasComment = False

        # Remove comments from command.
        newCommand = GcodePreprocessorUtils.removeComment(command)
        rawCommand = newCommand
        hasComment = len(newCommand) != len(command)

        if self.m_removeAllWhitespace:
            newCommand = GcodePreprocessorUtils.removeAllWhitespace(newCommand)

        if len(newCommand) > 0:
            # Override feed speed
            if self.m_speedOverride > 0:
                newCommand = GcodePreprocessorUtils.overrideSpeed(
                    newCommand, self.m_speedOverride
                )

            if self.m_truncateDecimalLength > 0:
                newCommand = GcodePreprocessorUtils.truncateDecimals(
                    self.m_truncateDecimalLength, newCommand
                )

            # If this is enabled we need to parse the gcode as we go along.
            if self.m_convertArcsToLines:  # || this.expandCannedCycles) {
                arcLines = self.convertArcsToLines(newCommand)
                if len(arcLines) > 0:
                    result.extend(arcLines)
                else:
                    result.append(newCommand)

            elif hasComment:
                # Maintain line level comment.
                result.append(command.replace(rawCommand, newCommand))
            else:
                result.append(newCommand)

        elif hasComment:
            # Reinsert comment-only lines.
            result.append(command)

        return result

    def convertArcsToLines(self, command: str) -> List[str]:
        result: List[str] = []

        start = self.m_currentPoint

        ps = self.addCommand(command)

        if ps == None or not cast(PointSegment, ps).isArc():
            return result

        psl = self.expandArc()

        if len(psl) == 0:
            return result

        # Create an array of new commands out of the of the segments in psl.
        # Don't add them to the gcode parser since it is who expanded them.
        for segment in psl:
            end = segment.point()
            result.append(
                GcodePreprocessorUtils.generateG1FromPoints(
                    start, end, self.m_inAbsoluteMode, self.m_truncateDecimalLength
                )
            )
            start = segment.point()

        return result

    def getPointSegmentList(self) -> List[PointSegment]:
        return self.m_points

    def getTraverseSpeed(self) -> float:
        return self.m_traverseSpeed

    def setTraverseSpeed(self, traverseSpeed: float):
        self.m_traverseSpeed = traverseSpeed

    def getCommandNumber(self) -> int:
        return self.m_commandNumber - 1

    def processCommand(self, args: List[str]) -> PointSegment:
        movementGCodes: List[float] = [ 0.0, 1.0, 2.0, 3.0, 5.0, 5.1, 38.2 ]

        gCodes = []
        ps = None

        # Handle F code
        speed = GcodePreprocessorUtils.parseCoord(args, "F")
        if not qIsNaN(speed):
            if self.m_isMetric:
                self.m_lastSpeed = speed
            else:
                self.m_lastSpeed = speed * 25.4

        # Handle S code
        spindleSpeed = GcodePreprocessorUtils.parseCoord(args, "S")
        if not qIsNaN(spindleSpeed):
            self.m_lastSpindleSpeed = spindleSpeed

        # handle G codes.
        gCodes = GcodePreprocessorUtils.parseCodes(args, "G")

        # If there was no command, add the implicit one to the party.
        S1 = set(movementGCodes)
        S2 = set(gCodes)

        containsMovementGCode =  len(S1.intersection(S2)) > 0
        
        if not containsMovementGCode:
            gCodes.append(self.m_lastGcodeCommand)

        for code in gCodes:
            ps = self.handleGCode(code, args)

        return cast(PointSegment, ps)

    def handleMCode(self, code: float, args: List[str]):
        spindleSpeed = GcodePreprocessorUtils.parseCoord(args, "S")
        if not qIsNaN(spindleSpeed):
            self.m_lastSpindleSpeed = spindleSpeed

    def handleGCode(self, code: float, args: List[str]) -> PointSegment:
        ps = None

        nextPoint = GcodePreprocessorUtils.updatePointWithCommand_FromStringList(
            args, self.m_currentPoint, self.m_inAbsoluteMode
        )
        nextAxes = GcodePreprocessorUtils.updateAxesWithCommand(
            args, self.m_currentAxes, self.m_inAbsoluteMode
        )


        if code == 0.0:
            ps = self.addLinearPointSegment(nextPoint, nextAxes, True)
        elif code == 1.0:
            ps = self.addLinearPointSegment(nextPoint, nextAxes, False)
        elif code == 38.2:
            ps = self.addLinearPointSegment(nextPoint, nextAxes, False)
        elif code == 2.0:
            ps = self.addArcPointSegment(nextPoint, nextAxes, True, args)
        elif code == 3.0:
            ps = self.addArcPointSegment(nextPoint, nextAxes, False, args)
        elif code == 5.0:
            ps = self.addSplinePointSegment(nextPoint, nextAxes, SplineProperties.SplineType.CUBIC_SPLINE, args)
        elif code == 5.1:
            ps = self.addSplinePointSegment(nextPoint, nextAxes, SplineProperties.SplineType.QUADRATIC_SPLINE, args)
        elif code == 17.0:
            self.m_currentPlane = PointSegment.Plane.XY
        elif code == 18.0:
            self.m_currentPlane = PointSegment.Plane.ZX
        elif code == 19.0:
            self.m_currentPlane = PointSegment.Plane.YZ
        elif code == 20.0:
            self.m_isMetric = False
        elif code == 21.0:
            self.m_isMetric = True
        elif code == 90.0:
            self.m_inAbsoluteMode = True
        elif code == 90.1:
            self.m_inAbsoluteIJKMode = True
        elif code == 91.0:
            self.m_inAbsoluteMode = False
        elif code == 91.1:
            self.m_inAbsoluteIJKMode = False
        elif code == 93.0:
            self.m_isInverseTimeFeed = True
        elif code == 94.0:
            self.m_isInverseTimeFeed = False

        if code == 0.0 or code == 1.0 or code == 2.0 or code == 3.0 or code == 5.0 or code == 5.1 or code == 38.2:
            self.m_lastGcodeCommand = code

        return cast(PointSegment, ps)

    def addLinearPointSegment(
        self, nextPoint: QVector3D, nextAxes: QVector3D, fastTraverse: bool
    ) -> PointSegment:
        ps = PointSegment.PointSegment_FromQVector3D(nextPoint, nextAxes, self.m_commandNumber)

        self.m_commandNumber += 1

        zOnly = False

        # Check for z-only
        if ( Util.nIsEqual(self.m_currentAxes, nextAxes)
            and self.m_currentPoint.x() == nextPoint.x()
            and self.m_currentPoint.y() == nextPoint.y()
            and self.m_currentPoint.z() != nextPoint.z()
        ):
            zOnly = True

        ps.setIsMetric(self.m_isMetric)
        ps.setIsZMovement(zOnly)
        ps.setIsFastTraverse(fastTraverse)
        ps.setIsAbsolute(self.m_inAbsoluteMode)
        ps.setIsInverseTimeFeed(self.m_isInverseTimeFeed)
        ps.setSpeed(self.m_traverseSpeed if fastTraverse else self.m_lastSpeed)
        ps.setSpindleSpeed(self.m_lastSpindleSpeed)
        self.m_points.append(ps)

        # Save off the endpoint.
        self.m_currentPoint = nextPoint
        self.m_nextAxes = nextAxes

        return ps

    def addArcPointSegment(
        self, nextPoint: QVector3D, nextAxes: QVector3D, clockwise: bool, args: List[str]
    ) -> PointSegment:
        ps = PointSegment.PointSegment_FromQVector3D(nextPoint, nextAxes, self.m_commandNumber)

        self.m_commandNumber += 1

        center: QVector3D = GcodePreprocessorUtils.updateCenterWithCommand(
            args, self.m_currentPoint, nextPoint, self.m_inAbsoluteIJKMode, clockwise
        )
        radius = GcodePreprocessorUtils.parseCoord(args, "R")
        pValue = GcodePreprocessorUtils.parseCoord(args, 'P')

        # Calculate radius if necessary.
        if qIsNaN(radius):
            m = QMatrix4x4()
            m.setToIdentity()

            if self.m_currentPlane == PointSegment.Plane.XY:
                pass
            elif self.m_currentPlane == PointSegment.Plane.ZX:
                m.rotate(90, 1.0, 0.0, 0.0)
            elif self.m_currentPlane == PointSegment.Plane.YZ:
                m.rotate(-90, 0.0, 1.0, 0.0)

            # x1 = (m * self.m_currentPoint).x()
            x1 = m.map(self.m_currentPoint).x()
            # x2 = (m * center).x()
            x2 = m.map(center).x()

            # y1 = (m * self.m_currentPoint).y()
            y1 = m.map(self.m_currentPoint).y()
            # y2 = (m * center).y()
            y2 = m.map(center).y()

            radius = math.sqrt(math.pow((x1 - x2), 2.0) + math.pow((y1 - y2), 2.0))

        ps.setIsMetric(self.m_isMetric)
        ps.setArcCenter(center)
        ps.setIsArc(True)
        ps.setRadius(radius)
        ps.setIsClockwise(clockwise)
        ps.setIsAbsolute(self.m_inAbsoluteMode)
        ps.setIsInverseTimeFeed(self.m_isInverseTimeFeed)
        ps.setSpeed(self.m_lastSpeed)
        ps.setSpindleSpeed(self.m_lastSpindleSpeed)
        ps.setPlane(self.m_currentPlane)
        if not qIsNaN(pValue):
            ps.setArcTurns(int(pValue))
             
        self.m_points.append(ps)

        # Save off the endpoint.
        self.m_currentPoint = nextPoint
        return ps

    def addSplinePointSegment(self, nextPoint: QVector3D, nextAxes: QVector3D, type: SplineProperties.SplineType, args: List[str]) -> PointSegment:
        self.m_commandNumber += 1

        ps = PointSegment(nextPoint, nextAxes, self.m_commandNumber)

        # Parse control point offsets
        I = GcodePreprocessorUtils.parseCoord(args, 'I')
        J = GcodePreprocessorUtils.parseCoord(args, 'J')
        P = GcodePreprocessorUtils.parseCoord(args, 'P')
        Q = GcodePreprocessorUtils.parseCoord(args, 'Q')

        if type == SplineProperties.SplineType.CUBIC_SPLINE:
            # G5: Two control points
            if qIsNaN(I) and qIsNaN(J):
                # Auto-match: I,J = -(previous P,Q) per Marlin/LinuxCNC spec
                # "as if I and J are the negation of the previous P and Q"
                if self.m_lastSplinePQ is None:
                    # No previous spline - use default I,J = (0,0)
                    cp1 = self.m_currentPoint
                else:
                    cp1 = self.m_currentPoint + QVector3D(
                        -self.m_lastSplinePQ.x(),
                        -self.m_lastSplinePQ.y(),
                        0
                    )
                
            else:
                # Explicit I,J
                cp1 = self.m_currentPoint + QVector3D(
                    0 if qIsNaN(I) else I,
                    0 if qIsNaN(J) else J,
                    0
                )

            cp2 = nextPoint + QVector3D(
                0 if qIsNaN(P) else P,
                0 if qIsNaN(Q) else Q,
                0
            )

            ps.setSplineControlPoints(cp1, cp2)

            # Store P,Q for next auto-match
            self.m_lastSplinePQ = QVector3D(
                0 if qIsNaN(P) else P,
                0 if qIsNaN(Q) else Q,
                0
            )

        else:
            # G5.1: One control point
            cp1 = self.m_currentPoint + QVector3D(
                0 if qIsNaN(I) else I,
                0 if qIsNaN(J) else J,
                0
            )
            ps.setSplineControlPoints(cp1, None)

        ps.setIsSpline(True)
        ps.setSplineType(type)
        ps.setIsMetric(self.m_isMetric)
        ps.setIsAbsolute(self.m_inAbsoluteMode)
        ps.setIsInverseTimeFeed(self.m_isInverseTimeFeed)
        ps.setSpeed(self.m_lastSpeed)
        ps.setSpindleSpeed(self.m_lastSpindleSpeed)
        ps.setPlane(self.m_currentPlane)

        self.m_points.append(ps)
        self.m_currentPoint = nextPoint

        return ps

    def setLastGcodeCommand(self, num: float):
        self.m_lastGcodeCommand = num
