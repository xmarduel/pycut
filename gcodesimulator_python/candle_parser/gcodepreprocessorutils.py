# This file is a part of "pycut" application.

# This file was originally ported from "gcodepreprocessorutils.cpp" class
# of "Candle" application written by Hayrullin Denis Ravilevich
# (https://github.com/Denvi/Candle)

# Copyright 2020-2030 Xavier Marduel

import math
import re

from typing import List
from typing import Any

from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QVector3D

from PySide6.QtCore import qIsNaN
from PySide6.QtCore import QRegularExpression

from gcodeviewer.parser.pointsegment import PointSegment

from gcodeviewer.util.util import qQNaN



class GcodePreprocessorUtils :
    '''
    '''
    re_speed = QRegularExpression("[Ff]([0-9.]+)")

    rx1_comment_parenthesis = QRegularExpression("\\(+[^\\(]*\\)+")
    #[rx2_comment_commapoint = QRegularExpression(";.*")

    re_comment = QRegularExpression("(\\([^\\(\\)]*\\)|[^].*)")

    re_truncate_decimals = QRegularExpression("(\\d*\\.\\d*)")

    M_PI = math.acos(-1)

    @classmethod 
    def overrideSpeed(cls, command: str, speed: float, original: float = None) -> str:
        '''
        Searches the command string for an 'f' and replaces the speed value
        between the 'f' and the next space with a percentage of that speed.
        In that way all speed values become a ratio of the provided speed
        and don't get overridden with just a fixed speed.
        '''
        match = cls.re_speed.match(command)
        if match.hasMatch():
            command = "F%d" % float(match.captured(1)) / 100 * speed

            # BUG: original does not comes back
            if original:
                original = float(match.captured(1))
    
        return command
        # return command, original
    
    @classmethod 
    def removeComment(cls, command: str) -> str:
        '''
        Removes any comments within parentheses or beginning with a semi-colon.
        '''
        res = command

        #Remove any comments within ( parentheses ) using regex "\([^\(]*\)"
        match = cls.rx1_comment_parenthesis.match(command)
        if match.hasMatch():
            #comment = match.captured(0)
            idx = match.capturedStart()
            len = match.capturedLength()
            res = res[:idx] + res[idx+len:]

        # Remove any comment beginning with ';' using regex ";.*"
        if ';' in res:
            idx = res.index(";")
            res = res[:idx]

        return res.strip()
    
    @classmethod 
    def parseComment(cls, command: str) -> str:
        '''
        Searches for a comment in the input string and returns the first match.
        '''
        match = cls.re_comment.match(command)
        if match.hasMatch():
            return match.captured(1)

        return ""
    
    @classmethod 
    def truncateDecimals(cls, length: int, command: str) -> str:
        res = command
        pos = 0
        match = cls.re_truncate_decimals.match(res, pos)

        while match.hasMatch():
            pos = match.capturedStart()
            len = match.capturedLength()

            newNum = "%.*f" % (length, float(match.captured(1)))
            res = res[:pos] + newNum + res[pos + len:]
            pos += len(newNum) + 1
            match = cls.re_truncate_decimals.match(res, pos)

        return res
    
    @classmethod 
    def removeAllWhitespace(cls, command: str) -> str:
        #rx = QRegularExpression("\\s")
        #return command.remove(rx)

        return command.replace(" ", "")
        
    @classmethod 
    def parseCodes(cls, args: List[str], code: str) -> List[float]:
        l = []
        
        for s in args:
            if len(s) > 0 and s[0].upper() == code :
                l.append(float(s[1:]))
    
        return l
    
    @classmethod 
    def parseGCodes(cls, command: str) -> List[int]:
        re = QRegularExpression("[Gg]0*(\\d+)")

        codes = []
        pos = 0
        match = re.match(command, pos)

        while match.hasMatch():
            codes.append(int(match.captured(1)))
            pos += match.capturedLength()
            match = re.match(command, pos)

        return codes
    
    @classmethod 
    def parseMCodes(cls, command: str) -> List[int]:
        re = QRegularExpression("[Mm]0*(\\d+)")

        codes = []
        pos = 0
        match = re.match(command, pos)

        while match.hasMatch():
            codes.append(int(match.captured(1)))
            pos += match.capturedLength()
            match = re.match(command, pos)

        return codes

    @classmethod 
    def updatePointWithCommand(cls, command: str, initial: QVector3D, absoluteMode: bool) -> QVector3D:
        '''
        Update a point given the arguments of a command.
        '''
        if command.__class__.__name__ == 'str':
            l = cls.splitCommand(command)
            return cls.updatePointWithCommand(l, initial, absoluteMode)
        else:
            return cls.updatePointWithCommand_FromStringList(command, initial, absoluteMode)
            
    @classmethod 
    def updatePointWithCommand_FromStringList(cls, commandArgs: List[str], initial: QVector3D,  absoluteMode: bool) -> QVector3D:
        '''
        Update a point given the arguments of a command, using a pre-parsed list.
        '''
        x = qQNaN()
        y = qQNaN()
        z = qQNaN()
        c = ""

        for command in commandArgs:
            if len(command) > 0:
                #c = command.upper().toLatin1()
                c = command[0].upper()
                if c == 'X':
                    x = float(command[1:])
                elif c == 'Y':
                    y = float(command[1:])
                elif c == 'Z':
                    z = float(command[1:])

        return cls.updatePointWithCommand_FromVector3D(initial, x, y, z, absoluteMode)

    @classmethod 
    def updatePointWithCommand_FromVector3D(cls, initial: QVector3D, x: float, y: float, z: float, absoluteMode: bool) -> QVector3D:
        '''
        Update a point given the new coordinates.
        '''
        newPoint = QVector3D(initial.x(), initial.y(), initial.z())

        if absoluteMode:
            if not qIsNaN(x) : newPoint.setX(x)
            if not qIsNaN(y) : newPoint.setY(y)
            if not qIsNaN(z) : newPoint.setZ(z)
        else:
            if not qIsNaN(x) : newPoint.setX(newPoint.x() + x)
            if not qIsNaN(y) : newPoint.setY(newPoint.y() + y)
            if not qIsNaN(z) : newPoint.setZ(newPoint.z() + z)

        return newPoint

    @classmethod
    def updateCenterWithCommand(cls, commandArgs: List[str], initial: QVector3D, nextPoint: QVector3D, absoluteIJKMode: bool, clockwise: bool) -> QVector3D:
        i = qQNaN()
        j = qQNaN()
        k = qQNaN()
        r = qQNaN()
        c = ""

        for t in commandArgs:
            if len(t) > 0:
                # c = t[0].upper().toLatin1()
                c = t[0].upper()
                if c == 'I':
                    i = float(t[1:])
                elif c == 'J':
                    j = float(t[1:])
                elif c == 'K':
                    k = float(t[1:])
                elif c == 'R':
                    r = float(t[1:])

        if qIsNaN(i) and qIsNaN(j) and qIsNaN(k):
            return cls.convertRToCenter(initial, nextPoint, r, absoluteIJKMode, clockwise)

        return cls.updatePointWithCommand_FromVector3D(initial, i, j, k, absoluteIJKMode)

    @classmethod 
    def generateG1FromPoints(cls, start: QVector3D, end: QVector3D, absoluteMode: bool, precision: int) -> str:
        sb = "G1"

        if absoluteMode:
            if not qIsNaN(end.x()) : sb.append("X" + "%.*f" % (precision, end.x()))
            if not qIsNaN(end.y()) : sb.append("Y" + "%.*f" % (precision, end.y()))
            if not qIsNaN(end.z()) : sb.append("Z" + "%.*f" % (precision, end.z()))
        else:
            if not qIsNaN(end.x()) : sb.append("X" + "%.*f" % (precision, end.x() - start.x()))
            if not qIsNaN(end.y()) : sb.append("Y" + "%.*f" % (precision, end.y() - start.y()))
            if not qIsNaN(end.z()) : sb.append("Z" + "%.*f" % (precision, end.z() - start.z()))

        return sb

    @classmethod 
    def splitCommand(cls, command: str) -> List[str]:
        '''
        Splits a gcode command by each word/argument, doesn't care about spaces.
        This command is about the same speed as the string.split(" ") command,
        but might be a little faster using precompiled regex.
        '''
        l = []
        readNumeric = False
        sb = ""

        # NO UNICODE STUFF
        #ba = command.encode(encoding="latin_1")
        #cmd = ba.decode() # Direct access to string data

        for c in command:
            if readNumeric and not c.isdigit() and c != '.':
                readNumeric = False
                l.append(sb)
                sb = ""
                if c.isalpha():
                    sb += c
            elif c.isdigit() or c == '.' or c == '-':
                sb += c
                readNumeric = True
            elif c.isalpha():
                sb += c

        if len(sb) > 0:
            l.append(sb)

        return l

    @classmethod 
    def parseCoord(cls, argList: List[str], c: str) -> float:
        '''
        TODO: Replace everything that uses this with a loop that loops through
        the string and creates a hash with all the values.
        '''
        for t in argList:
            if len(t) > 0 and t[0].upper() == c:
                return float(t[1:])
    
        return qQNaN()

    @classmethod 
    def convertRToCenter(cls, start: QVector3D, end: QVector3D, radius: float, absoluteIJK: bool, clockwise: bool) -> QVector3D:
        R = radius
        center = QVector3D()

        x = end.x() - start.x()
        y = end.y() - start.y()

        h_x2_div_d = 4 * R * R - x * x - y * y
        if h_x2_div_d < 0: 
            #print("Error computing arc radius.")
            if math.fabs(h_x2_div_d) < 1.0e-4 :
                h_x2_div_d = 0
            else:
                print("Error computing arc radius.")

        h_x2_div_d = (-math.sqrt(h_x2_div_d)) / math.hypot(x, y)

        if not clockwise:
            h_x2_div_d = -h_x2_div_d

        # Special message from gcoder to software for which radius
        # should be used.
        if R < 0:
            h_x2_div_d = -h_x2_div_d
            # TODO: Places that use this need to run ABS on radius.
            radius = -radius

        offsetX = 0.5 * (x - (y * h_x2_div_d))
        offsetY = 0.5 * (y + (x * h_x2_div_d))

        if not absoluteIJK:
            center.setX(start.x() + offsetX)
            center.setY(start.y() + offsetY)
        else:
            center.setX(offsetX)
            center.setY(offsetY)

        return center
    
    @classmethod 
    def getAngle(cls, start: QVector3D, end: QVector3D) -> float:
        '''
        Return the angle in radians when going from start to end.
        '''
        deltaX = end.x() - start.x()
        deltaY = end.y() - start.y()

        angle = 0.0

        if deltaX != 0: # prevent div by 0
            # it helps to know what quadrant you are in
            if deltaX > 0 and deltaY >= 0: # 0 - 90
                angle = math.atan(deltaY / deltaX)
            elif deltaX < 0 and deltaY >= 0: # 90 to 180
                angle = cls.M_PI - math.fabs(math.atan(deltaY / deltaX))
            elif deltaX < 0 and deltaY < 0: # 180 - 270
                angle = cls.M_PI + math.fabs(math.atan(deltaY / deltaX))
            elif deltaX > 0 and deltaY < 0:  # 270 - 360
                angle = cls.M_PI * 2 - math.fabs(math.atan(deltaY / deltaX))
        else:
            # 90 deg
            if deltaY > 0:
                angle = cls.M_PI / 2.0
            #270 deg
            else:
                angle = cls.M_PI * 3.0 / 2.0

        return angle

    @classmethod 
    def calculateSweep(cls, startAngle: float, endAngle: float, isCw: bool) -> float:
        sweep = 0.0

        # Full circle
        if startAngle == endAngle:
            sweep = cls.M_PI * 2
        #Arcs
        else:
            # Account for full circles and end angles of 0/360
            if endAngle == 0:
                endAngle = cls.M_PI * 2
            
            # Calculate distance along arc.
            if (not isCw) and endAngle < startAngle:
                sweep = (cls.M_PI * 2 - startAngle) + endAngle
            elif isCw and endAngle > startAngle:
                sweep = (cls.M_PI * 2 - endAngle) + startAngle
            else:
                sweep = math.fabs(endAngle - startAngle)

        return sweep
    
    @classmethod
    def generatePointsAlongArcBDring(cls, plane: PointSegment.Plane, start: QVector3D, end: QVector3D, center: QVector3D, clockwise: bool, R: float, minArcLength: float, arcPrecision: float, LAST_ARG: Any) -> List[QVector3D]:
        '''
        DUMMY DISPATCH
        '''
        if isinstance(LAST_ARG, bool):
            return cls.generatePointsAlongArcBDring_Arc(plane, start, end, center, clockwise, R, minArcLength, arcPrecision, LAST_ARG)
        else:
            return cls.generatePointsAlongArcBDring_Num(plane, start, end, center, clockwise, R, minArcLength, arcPrecision, LAST_ARG)

    @classmethod 
    def generatePointsAlongArcBDring_Arc(cls, plane: PointSegment.Plane, start: QVector3D, end: QVector3D, center: QVector3D, clockwise: bool, R: float, minArcLength: float, arcPrecision: float, arcDegreeMode: bool) -> List[QVector3D]:
        '''
        Generates the points along an arc including the start and end points.
        '''
        radius = R

        # Rotate vectors according to plane
        m = QMatrix4x4()
        m.setToIdentity()
        if plane == PointSegment.Plane.XY:
            pass
        elif plane == PointSegment.Plane.ZX:
            m.rotate(90, 1.0, 0.0, 0.0)
        elif plane == PointSegment.Plane.YZ:
            m.rotate(-90, 0.0, 1.0, 0.0)
            
        start = m.map(start)  # m * start
        end = m.map(end)  # m * end
        center = m.map(center)  # m * center

        # Check center
        if qIsNaN(center.length()):
            return []

        # Calculate radius if necessary.
        if radius == 0:
            radius = math.sqrt(math.pow((start.x() - center.x(), 2.0) + math.pow(end.y() - center.y(), 2.0)))

        startAngle = cls.getAngle(center, start)
        endAngle = cls.getAngle(center, end)
        sweep = cls.calculateSweep(startAngle, endAngle, clockwise)

        # Convert units.
        arcLength = sweep * radius

        numPoints = 0

        if arcDegreeMode and arcPrecision > 0:
            numPoints = max(1.0, sweep / (cls.M_PI * arcPrecision / 180))
        else:
            if arcPrecision <= 0 and minArcLength > 0:
                arcPrecision = minArcLength
            
            numPoints = math.ceil(arcLength/arcPrecision)
        

        return cls.generatePointsAlongArcBDring_Num(plane, start, end, center, clockwise, radius, startAngle, sweep, numPoints)
    
    @classmethod 
    def generatePointsAlongArcBDring_Num(cls, plane: PointSegment.Plane, p1: QVector3D, p2: QVector3D, center: QVector3D, isCw: bool, radius: float, startAngle: float, sweep: float, numPoints: int) -> List[QVector3D]:
        '''
        Generates the points along an arc including the start and end points.
        '''
        # Prepare rotation matrix to restore plane
        m = QMatrix4x4()
        m.setToIdentity()
        
        if plane == PointSegment.Plane.XY:
            pass
        elif plane == PointSegment.Plane.ZX:
            m.rotate(-90, 1.0, 0.0, 0.0)
        elif plane == PointSegment.Plane.YZ:
            m.rotate(90, 0.0, 1.0, 0.0)

        lineEnd = QVector3D(p2.x(), p2.y(), p1.z())
        segments = []
        angle = 0.0

        # Calculate radius if necessary.
        if radius == 0:
            radius = math.sqrt(math.pow((p1.x() - center.x()), 2.0) + math.pow((p1.y() - center.y()), 2.0))

        zIncrement = (p2.z() - p1.z()) / numPoints

        for i in range(numPoints):
            if isCw:
                angle = (startAngle - i * sweep / numPoints)
            else:
               angle = (startAngle + i * sweep / numPoints)

            if angle >= cls.M_PI * 2:
                angle = angle - cls.M_PI * 2

            lineEnd.setX(math.cos(angle) * radius + center.x())
            lineEnd.setY(math.sin(angle) * radius + center.y())
            lineEnd.setZ(lineEnd.z() + zIncrement)

            #segments.append(m * lineEnd)
            segments.append(m .map(lineEnd))

        #segments.append(m * p2)
        segments.append(m .map(p2))

        return segments

