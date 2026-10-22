from enum import Enum
from typing import Dict

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QColor

from PySide6.QtCore import qIsNaN


def qQNaN():
    return float("NaN")


def qBound(amin, val, amax):
    return max(amin, min(val, amax))


class Util:
    """ """
    class RotationVector(Enum):
        RotationVectorX = 0
        RotationVectorY = 1
        RotationVectorZ = 2
        RotationVectorNone = 3

    vectors: Dict[RotationVector, QVector3D] = {}

    @classmethod
    def nVector(cls) -> QVector3D:
        return QVector3D(qQNaN(), qQNaN(), qQNaN());

    @classmethod
    def rotationVector(cls, vector: RotationVector) -> QVector3D:
        if len(cls.vectors) == 0:
            cls.vectors[Util.RotationVector.RotationVectorX] = QVector3D(1.0, 0.0, 0.0)
            cls.vectors[Util.RotationVector.RotationVectorY] = QVector3D(0.0, 1.0, 0.0)
            cls.vectors[Util.RotationVector.RotationVectorZ] = QVector3D(0.0, 0.0, 1.0)
            cls.vectors[Util.RotationVector.RotationVectorNone] = cls.nVector()
    
        return cls.vectors[vector]

    @classmethod
    def nMin(cls, v1: float, v2: float) -> float:
        if (not qIsNaN(v1)) and (not qIsNaN(v2)):
            return min(v1, v2)
        elif not qIsNaN(v1):
            return v1
        elif not qIsNaN(v2):
            return v2
        else:
            return qQNaN()

    @classmethod
    def nMax(cls, v1: float, v2: float) -> float:
        if (not qIsNaN(v1)) and (not qIsNaN(v2)):
            return max(v1, v2)
        elif not qIsNaN(v1):
            return v1
        elif not qIsNaN(v2):
            return v2
        else:
            return qQNaN()

    @classmethod
    def nMinVector(cls, v1: QVector3D, v2: QVector3D) -> QVector3D:
        return QVector3D(cls.nMin(v1.x(), v2.x()), cls.nMin(v1.y(), v2.y()), cls.nMin(v1.z(), v2.z()))

    @classmethod
    def nMaxVector(cls, v1: QVector3D, v2: QVector3D) -> QVector3D:
        return QVector3D(cls.nMax(v1.x(), v2.x()), cls.nMax(v1.y(), v2.y()), cls.nMax(v1.z(), v2.z()))

    @classmethod
    def colorToVector(cls, color: QColor) -> QVector3D:
        return QVector3D(color.redF(), color.greenF(), color.blueF())

    @classmethod
    def cloneQVector3D(cls, v: QVector3D) -> QVector3D:
        """faster than deepcopy"""
        return QVector3D(v.x(), v.y(), v.z())

    @classmethod
    def nIsNaN(cls, vector: QVector3D) -> bool:
        return qIsNaN(vector.x()) and qIsNaN(vector.y()) and qIsNaN(vector.z())

    @classmethod
    def nIsEqual(cls, v1: QVector3D, v2: QVector3D) -> bool:
        x_equal = v1.x() == v2.x() or (qIsNaN(v1.x()) and qIsNaN(v2.x()))
        y_equal = v1.y() == v2.y() or (qIsNaN(v1.y()) and qIsNaN(v2.y()))
        z_equal = v1.z() == v2.z() or (qIsNaN(v1.z()) and qIsNaN(v2.z()))
        
        return x_equal and y_equal and z_equal

    @classmethod
    def nAssign(cls, newValue: float, defaultValue: float = 0.0) -> float:
        return defaultValue if qIsNaN(newValue) else newValue
