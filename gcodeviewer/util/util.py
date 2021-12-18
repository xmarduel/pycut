
from PySide6.QtGui import QVector3D
from PySide6.QtGui import QColor

from PySide6.QtCore import qIsNaN

def qQNaN():
    return float('NaN')

def qBound(amin, val, amax):
    return max(amin, min(val, amax))

    
    
class Util:

    @classmethod
    def nMin(v1: float, v2: float) -> float:
        if (not qIsNaN(v1)) and (not qIsNaN(v2)):
            return min(v1, v2)
        elif not qIsNaN(v1):
            return v1
        elif not qIsNaN(v2):
            return v2
        else:
            return qQNaN()

    @classmethod
    def nMax(v1: float, v2: float) -> float:
        if (not qIsNaN(v1)) and (not qIsNaN(v2)):
            return max(v1, v2)
        elif not qIsNaN(v1):
            return v1
        elif not qIsNaN(v2):
            return v2
        else:
            return qQNaN()

    @classmethod
    def colorToVector(cls, color: QColor) -> QVector3D:
        return QVector3D(color.redF(), color.greenF(), color.blueF())
