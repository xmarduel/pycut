# Copyright 2022 Xavier Marduel
#
# This file is part of pycut.
#
# pycut is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pycut is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pycut.  If not, see <http:#www.gnu.org/licenses/>.

import math

from typing import List
from typing import Tuple

from PySide6.QtCore import qIsNaN
from PySide6.QtGui import QVector3D

sNaN = float('NaN')

import math
import sys
import time

from typing import List

from PySide6.QtCore import qIsNaN
from PySide6.QtGui import QVector3D

sNaN = float('NaN')


class GcodeAtomicMvt:
    '''
    '''
    def __init__(self, x, y, z, feedrate):
        self.at_time = None
        self.pos = QVector3D(x,y,z)
        self.feedrate = feedrate # mm per minutes or inches per minutes

    @classmethod
    def interpolate(cls, coeff: float, pos1: QVector3D, pos2: QVector3D) -> QVector3D:
        x = pos1.x() + coeff * (pos2.x() - pos1.x())
        y = pos1.y() + coeff * (pos2.y() - pos1.y())
        z = pos1.z() + coeff * (pos2.z() - pos1.z())

        return QVector3D(x,y,z)

    def __repr__(self):
        return self.pos
    
    def __str__(self):
        return self.pos

class GcodeMiniParser:
    '''
    Basic parser **only** for pycut generated gcode...
    '''
    def __init__(self):
        '''
        '''
        self.gcode = ""

        self.idx = 0

        self.path : List[GcodeAtomicMvt] = []
        self.path_time = 0 # in seconds

    def reset(self):
        '''
        '''
        self.idx = 0
        self.path = []
        self.path_time = 0
    
    def get_path_time(self) -> float:
        '''
        '''
        return self.eval_path_time()
    
    def parse_gcode(self, gcode: str):
        '''
        '''
        self.reset()
        self.gcode = gcode

        lastX = sNaN
        lastY = sNaN
        lastZ = sNaN
        lastF = sNaN

        def parse() -> float:
            self.idx += 1
            while self.idx < len(self.gcode) and (self.gcode[self.idx] == ' ' or self.gcode[self.idx] == '\t'):
                self.idx += 1
            begin = self.idx
            while (self.idx < len(self.gcode) and self.gcode[self.idx] in "+-.0123456789"):
                self.idx += 1
            try:
                end = self.idx
                return float(self.gcode[begin:end])
            except Exception:
                return None

        while self.idx < len(self.gcode) :

            g = sNaN
            x = sNaN
            y = sNaN
            z = sNaN
            f = sNaN

            while self.idx < len(self.gcode) and self.gcode[self.idx] != '' and self.gcode[self.idx] != '\r' and self.gcode[self.idx] != '\n':
                letter = self.gcode[self.idx]
                if letter == 'G' or letter == 'g':
                    g = parse()
                elif letter == 'X' or letter == 'x':
                    x = parse()
                elif letter == 'Y' or letter == 'y':
                    y = parse()
                elif letter == 'Z' or letter == 'z':
                    z = parse()
                elif letter == 'F' or letter == 'f':
                    f = parse()
                else:
                    self.idx += 1

            if g == 0 or g == 1:
                if not qIsNaN(x):
                    if qIsNaN(lastX):
                        for j in range(len(self.path)):
                            self.path[j].pos.setX(x)
                    lastX = x

                if not qIsNaN(y):
                    if qIsNaN(lastY):
                        for j in range(len(self.path)):
                            self.path[j].pos.setY(y)
                    lastY = y

                if not qIsNaN(z):
                    if qIsNaN(lastZ):
                        for j in range(len(self.path)):
                            self.path[j].pos.setZ(z)
                    lastZ = z

                if not qIsNaN(f):
                    if qIsNaN(lastF):
                        for j in range(len(self.path)):
                            self.path[j].feedrate = f
                    lastF = f

                self.path.append(GcodeAtomicMvt(lastX, lastY, lastZ, lastF))

            while self.idx < len(self.gcode) and self.gcode[self.idx] != '\r' and self.gcode[self.idx] != '\n':
                self.idx += 1
            while self.idx < len(self.gcode) and (self.gcode[self.idx] == '\r' or self.gcode[self.idx] == '\n'):
                self.idx += 1

        # last thing
        self.eval_path_time()

    def eval_path_time(self) -> float:
        '''
        in seconds
        '''
        total_time = 0.0

        self.path[0].at_time = 0.0

        for idx, mvt in enumerate(self.path):
            if idx == 0:
                continue

            prev_idx = idx - 1
            prev_mvt = self.path[prev_idx]
           
            f = mvt.feedrate
            
            dist = mvt.pos.distanceToPoint(prev_mvt.pos)
            
            total_time = total_time + dist / f

            mvt.at_time = total_time * 60
        
        self.path_time = total_time * 60

        return self.path_time

    def get_mvt_index_for_time(self, atime: float):
        if atime == 0:
            return 0
        
        #for k, atomic_mvt in enumerate(self.path):
        #    if atomic_mvt.at_time > atime:
        #        return k - 1 

        #return k

        begin = 0
        end = len(self.path)
        
        while begin < end:
            i = math.floor((begin + end) / 2)
            if self.path[i].at_time < atime:
                begin = i + 1
            else:
                end = i
    
        return end


if __name__ == '__main__':
    gcodefile = sys.argv[1]
    
    fp = open(gcodefile, "r")
    gcode = fp.read()
    fp.close()

    t1 = time.time()
    parser = GcodeMiniParser()
    parser.parse_gcode(gcode)
    t2 = time.time()

    print("gcode time: ", parser.path_time)
    print("parser time:", t2-t1)
