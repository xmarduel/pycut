
import math
from typing import List

from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QVector3D

from PySide6.QtCore import QRegularExpression as QRegExp 

from pointsegment import PointSegment


def qQNaN():
    return None

def qIsNaN(val):
    return val is None


class GcodePreprocessorUtils :
    '''
    '''
    re = QRegExp("[Ff]([0-9.]+)")

    rx1 = QRegExp("\\(+[^\\(]*\\)+")
    rx2 = QRegExp(".*")

    M_PI = math.acos(-1)

    @classmethod 
    def overrideSpeed(cls, command: str, speed: float, original: float = None) -> str:
        if cls.re.indexIn(command) != -1:
            command.replace(cls.re, "F%d" % (cls.re.cap(1).toDouble() / 100 * speed))

            if original:
                 original = cls.re.cap(1).toDouble()
    
        return command
    
    @classmethod 
    def removeComment(cls, command: str) -> str:
        #Remove any comments within ( parentheses ) using regex "\([^\(]*\)"
        if '(' in command:
            command.remove(cls.rx1)

        # Remove any comment beginning with '' using regex ".*"
        if '' in command:
            command.remove(cls.rx2)

        return command.strip()
    
    @classmethod 
    def parseComment(cls, command: str) -> str:
        re = QRegExp("(\\([^\\(\\)]*\\)|[^].*)")

        if re.indexIn(command) != -1:
            return re.cap(1)

        return ""
    
    @classmethod 
    def truncateDecimals(cls, length: int, command: str) -> str:
        re = QRegExp("(\\d*\\.\\d*)")
        pos = 0
        pos = re.indexIn(command, pos)

        while pos != -1:
            format = "%%.%f" % length
            newNum = format % float(re.cap(1))
            command = command.left(pos) + newNum + command.mid(pos + re.matchedLength())
            pos += newNum.length() + 1
            pos = re.indexIn(command, pos)

        return command
    
    @classmethod 
    def removeAllWhitespace(cls, command: str) -> str:
        rx = QRegExp("\\s")

        return command.remove(rx)
        
    @classmethod 
    def parseCodes(cls, args: List[str], code: str) -> List[float]:
        l = []
        
        for s in args:
            if s.length() > 0 and s[0].toUpper() == code :
                l.append(s.mid(1).toDouble())
    
        return l
    
    @classmethod 
    def parseGCodes(cls, command: str) -> List[int]:
        re = QRegExp("[Gg]0*(\\d+)")

        codes = []
        pos = 0
        pos = re.indexIn(command, pos)

        while pos != -1:
            codes.append(re.cap(1).toInt())
            pos += re.matchedLength()
            pos = re.indexIn(command, pos)

        return codes
    
    @classmethod 
    def parseMCodes(cls, command: str) -> List[int]:
        re = QRegExp("[Mm]0*(\\d+)")

        codes = []
        pos = 0
        pos = re.indexIn(command, pos)

        while pos != -1:
            codes.append(re.cap(1).toInt())
            pos += re.matchedLength()
            pos = re.indexIn(command, pos)

        return codes
    
    @classmethod 
    def splitCommand(cls, command: str) -> List[str]:
        l = []
        readNumeric = False
        sb = ""

        ba = command.toLatin1()
        cmd = ba.constData(); # Direct access to string data

        for i in range(len(command)):
            c = cmd[i]

            if readNumeric and not cls.isDigit(c) and c != '.':
                readNumeric = False
                l.append(sb)
                sb.clear()
                if cls.isLetter(c):
                    sb.append(c)
            elif cls.isDigit(c) or c == '.' or c == '-':
                sb.append(c)
                readNumeric = True
            elif cls.isLetter(c):
                sb.append(c)

        if len(sb) > 0:
            l.append(sb)

        return l
    
    @classmethod 
    def parseCoord(cls, argList: List[str], c: str) -> float:
        for t in argList:
            if t.length() > 0 and t[0].toUpper() == c:
                return t.mid(1).toDouble()
    
        return qQNaN()
    
    @classmethod 
    def updatePointWithCommand(cls, initial: QVector3D, x: float, y: float, z: float, absoluteMode: bool) -> QVector3D:
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
    def updatePointWithCommand(cls, commandArgs: List[str], initial: QVector3D,  absoluteMode: bool) -> QVector3D:
        x = qQNaN()
        y = qQNaN()
        z = qQNaN()
        c = ""

        for i in range(len(commandArgs)):
            if len(commandArgs[i]) > 0:
                c = commandArgs[i].at(0).toUpper().toLatin1()
                if c == 'X':
                    x = commandArgs[i].mid(1).toDouble()
                elif c == 'Y':
                    y = commandArgs[i].mid(1).toDouble()
                elif c == 'Z':
                    z = commandArgs[i].mid(1).toDouble()

        return cls.updatePointWithCommand(initial, x, y, z, absoluteMode)
    
    @classmethod 
    def updatePointWithCommand(cls, command: str, initial: QVector3D, absoluteMode: bool) -> QVector3D:
        l = cls.splitCommand(command)
        return cls.updatePointWithCommand(l, initial, absoluteMode)
    
    @classmethod 
    def convertRToCenter(cls, start: QVector3D, end: QVector3D, radius: float, absoluteIJK: bool, clockwise: bool) -> QVector3D:
        R = radius
        center = QVector3D()

        x = end.x() - start.x()
        y = end.y() - start.y()

        h_x2_div_d = 4 * R * R - x * x - y * y
        if h_x2_div_d < 0: 
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
    def updateCenterWithCommand(cls, commandArgs: List[str], initial: QVector3D, nextPoint: QVector3D, absoluteIJKMode: bool, clockwise: bool) -> QVector3D:
        i = qQNaN()
        j = qQNaN()
        k = qQNaN()
        r = qQNaN()
        c = ""

        for t in commandArgs:
            if t.length() > 0:
                c = t[0].toUpper().toLatin1()
                if c == 'I':
                    i = t.mid(1).toDouble()
                elif c == 'J':
                    j = t.mid(1).toDouble()
                elif c == 'K':
                    k = t.mid(1).toDouble()
                elif c == 'R':
                    r = t.mid(1).toDouble()

        if qIsNaN(i) and qIsNaN(j) and qIsNaN(k):
            return cls.convertRToCenter(initial, nextPoint, r, absoluteIJKMode, clockwise)

        return cls.updatePointWithCommand(initial, i, j, k, absoluteIJKMode)
    
    @classmethod 
    def generateG1FromPoints(cls, start: QVector3D, end: QVector3D, absoluteMode: bool, precision: int) -> str:
        sb = "G1"

        if absoluteMode:
            if not qIsNaN(end.x()) : sb.append("X" + "%.4f" % end.x())
            if not qIsNaN(end.y()) : sb.append("Y" + "%.4f" % end.y())
            if not qIsNaN(end.z()) : sb.append("Z" + "%.4f" % end.z())
        else:
            if not qIsNaN(end.x()) : sb.append("X" + "%.4f" %  (end.x() - start.x()))
            if not qIsNaN(end.y()) : sb.append("Y" + "%.4f" %  (end.y() - start.y()))
            if not qIsNaN(end.z()) : sb.append("Z" + "%.4f" %  (end.z() - start.z()))

        return sb
    
    @classmethod 
    def getAngle(cls, start: QVector3D, end: QVector3D) -> float:
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
    def generatePointsAlongArcBDring(cls, plane: PointSegment.plane, start: QVector3D, end: QVector3D, center: QVector3D, clockwise: bool, R: float, minArcLength: float, arcPrecision: float, arcDegreeMode: bool) -> List[QVector3D]:
        radius = R

        # Rotate vectors according to plane
        m = QMatrix4x4()
        m.setToIdentity()
        if plane == PointSegment.plane.XY:
            pass
        elif plane == PointSegment.plane.ZX:
            m.rotate(90, 1.0, 0.0, 0.0)
        elif plane == PointSegment.plane.YZ:
            m.rotate(-90, 0.0, 1.0, 0.0)
            
        start = m * start
        end = m * end
        center = m * center

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
        

        return cls.generatePointsAlongArcBDring(plane, start, end, center, clockwise, radius, startAngle, sweep, numPoints)
    
    @classmethod 
    def generatePointsAlongArcBDring(cls, plane: PointSegment.plane, p1: QVector3D, p2: QVector3D, center: QVector3D, isCw: bool, radius: float, startAngle: float, sweep: float, numPoints: int) -> List[QVector3D]:
        # Prepare rotation matrix to restore plane
        m = QMatrix4x4()
        m.setToIdentity()
        
        if plane == PointSegment.plane.XY:
            pass
        elif plane == PointSegment.plane.ZX:
            m.rotate(-90, 1.0, 0.0, 0.0)
        elif plane == PointSegment.plane.YZ:
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

            segments.append(m * lineEnd)

        segments.append(m * p2)

        return segments
    
    @classmethod 
    def isDigit(cls, c: str) -> bool:
        return c.isdigit()
    
    @classmethod 
    def isLetter(cls, c: str) -> bool:
        return c.isalpha()
    
    @classmethod 
    def toUpper(cls, c: str) -> str:       
        return c.upper()
