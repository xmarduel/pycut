# This file is a part of "pycut" application.
# This file was originally ported from "gcodeviewparse.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

from typing import List

from PySide6.QtGui import QVector3D

from PySide6 import QtCore
from PySide6.QtCore import qIsNaN

from linesegment import LineSegment
from gcodeparser import GcodeParser
from gcodepreprocessorutils import GcodePreprocessorUtils

from util.util import Util
from util.util import qQNaN


class GcodeViewParse : 
    '''
    '''
    def __init__(self, parent = None):
        self.absoluteMode = True
        self.absoluteIJK = False

        # Parsed object
        self.m_min = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_max = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_minLength = qQNaN()

        self.m_lines : List[LineSegment] = []
        self.m_lineIndexes : List[List[int]] = [[]]   

        # Parsing state.
        self.lastPoint : QVector3D = None
        self.currentLine  = 0  # for assigning line numbers to segments.

        # Debug
        self.debug = True 
    
    def getMinimumExtremes(self) -> QVector3D : 
        return self.m_min

    def getMaximumExtremes(self) -> QVector3D :
        return self.m_max

    def getMinLength(self) -> float :
        return self.m_minLength

    def getResolution(self) -> QtCore.QSize :
        return QtCore.QSize( \
                ((self.m_max.x() - self.m_min.x()) / self.m_minLength) + 1,  \
                ((self.m_max.y() - self.m_min.y()) / self.m_minLength) + 1)

    def toObjRedux(self, gcode: List[str], arcPrecision: float, arcDegreeMode: bool) -> List[LineSegment]:
        gp = GcodeParser()

        for s in gcode:
            gp.addCommand(s)

        return self.getLinesFromParser(gp, arcPrecision, arcDegreeMode)
    
    def getLineSegmentList(self) -> List[LineSegment]:
        return self.m_lines

    def getLinesFromParser(self, gp: GcodeParser, arcPrecision: float, arcDegreeMode: bool) -> List[LineSegment]:
        psl = gp.getPointSegmentList()
        # For a line segment list ALL arcs must be converted to lines.
        minArcLength = 0.1

        start = None
        end = None

        # Prepare segments indexes
        self.m_lineIndexes = [ [] for _ in range(len(psl)) ]

        lineIndex = 0
        for segment in psl:
            ps = segment
            isMetric = ps.isMetric()
            ps.convertToMetric()

            end = ps.point()

            # start is null for the first iteration.
            if start != None:           
                # Expand arc for graphics.            
                if ps.isArc():
                    points = GcodePreprocessorUtils.generatePointsAlongArcBDring(ps.plane(),
                        start, end, 
                        ps.center(), 
                        ps.isClockwise(), 
                        ps.getRadius(), 
                        minArcLength, 
                        arcPrecision, 
                        arcDegreeMode)
                    # Create line segments from points.
                    if len(points) > 0:
                        startPoint = start
                        for nextPoint in points:
                            if nextPoint == startPoint:
                                continue
                            ls = LineSegment.LineSegment_FromVector3Ds(startPoint, nextPoint, lineIndex)
                            ls.setIsArc(ps.isArc())
                            ls.setIsClockwise(ps.isClockwise())
                            ls.setPlane(ps.plane())
                            ls.setIsFastTraverse(ps.isFastTraverse())
                            ls.setIsZMovement(ps.isZMovement())
                            ls.setIsMetric(isMetric)
                            ls.setIsAbsolute(ps.isAbsolute())
                            ls.setSpeed(ps.getSpeed())
                            ls.setSpindleSpeed(ps.getSpindleSpeed())
                            ls.setDwell(ps.getDwell())
                            self.testExtremes_Vector3D(nextPoint)
                            self.m_lines.append(ls)
                            self.m_lineIndexes[ps.getLineNumber()].append(len(self.m_lines) - 1)
                            startPoint = nextPoint
                        
                        lineIndex += 1

                # Line
                else:
                    ls = LineSegment.LineSegment_FromVector3Ds(start, end, lineIndex)
                    lineIndex += 1
                    ls.setIsArc(ps.isArc())
                    ls.setIsFastTraverse(ps.isFastTraverse())
                    ls.setIsZMovement(ps.isZMovement())
                    ls.setIsMetric(isMetric)
                    ls.setIsAbsolute(ps.isAbsolute())
                    ls.setSpeed(ps.getSpeed())
                    ls.setSpindleSpeed(ps.getSpindleSpeed())
                    ls.setDwell(ps.getDwell())
                    self.testExtremes_Vector3D(end)
                    self.testLength(start, end)
                    self.m_lines.append(ls)
                    self.m_lineIndexes[ps.getLineNumber()].append(len(self.m_lines) - 1)
        
            start = end

        return self.m_lines

    def getLines(self) -> List[LineSegment]:
        return self.m_lines

    def getLinesIndexes(self) -> List[List[int]]: 
        return self.m_lineIndexes

    def reset(self):
        self.m_lines = []
        self.m_lineIndexes = []
    
        self.currentLine = 0
        self.m_min = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_max = QVector3D(qQNaN(), qQNaN(), qQNaN())
        self.m_minLength = qQNaN()

    def testExtremes_Vector3D(self, p3d: QVector3D):
        self.testExtremes(p3d.x(), p3d.y(), p3d.z())

    def testExtremes(self, x: float, y: float, z: float):
        self.m_min.setX(Util.nMin(self.m_min.x(), x))
        self.m_min.setY(Util.nMin(self.m_min.y(), y))
        self.m_min.setZ(Util.nMin(self.m_min.z(), z))

        self.m_max.setX(Util.nMax(self.m_max.x(), x))
        self.m_max.setY(Util.nMax(self.m_max.y(), y))
        self.m_max.setZ(Util.nMax(self.m_max.z(), z))

    def testLength(self, start: QVector3D, end: QVector3D):
        length = (start - end).length()
        if (not qIsNaN(length)) and length != 0:
            if qIsNaN(self.m_minLength):
                self.m_minLength = length
            else:
                self.m_minLength = min(self.m_minLength, length)

