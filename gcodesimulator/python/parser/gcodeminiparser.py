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

sNaN = float('NaN')


class GcodeMiniParser:
    '''
    Basic parser **only** for pycut generated gcode...
    '''
    def __init__(self):
        '''
        '''
        self.gcode = ""

        self.idx = 0

        self.path : List[Tuple[float, float, float, float]] = []
        self.path_time = None

    def reset(self):
        '''
        '''
        self.idx = 0
        self.path = []
        self.path_time = None

    def get_path(self) -> List[Tuple[float, float, float, float]] :
        return self.path
    
    def get_path_time(self) -> float:
        self.eval_path_time()
        return self.path_time
    
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
                if self.gcode[self.idx] == 'G' or self.gcode[self.idx] == 'g':
                    g = parse()
                elif self.gcode[self.idx] == 'X' or self.gcode[self.idx] == 'x':
                    x = parse()
                elif self.gcode[self.idx] == 'Y' or self.gcode[self.idx] == 'y':
                    y = parse()
                elif self.gcode[self.idx] == 'Z' or self.gcode[self.idx] == 'z':
                    z = parse()
                elif self.gcode[self.idx] == 'F' or self.gcode[self.idx] == 'f':
                    f = parse()
                else:
                    self.idx += 1

            if g == 0 or g == 1:
                if not qIsNaN(x):
                    if qIsNaN(lastX):
                        for j in range(len(self.path)):
                            self.path[j][0] = x
                    lastX = x

                if not qIsNaN(y):
                    if qIsNaN(lastY):
                        for j in range(len(self.path)):
                            self.path[j][1] = y
                    lastY = y

                if not qIsNaN(z):
                    if qIsNaN(lastZ):
                        for j in range(len(self.path)):
                            self.path[j][2] = z
                    lastZ = z

                if not qIsNaN(f):
                    if qIsNaN(lastF):
                        for j in range(len(self.path)):
                            self.path[j][3] = f
                    lastF = f

                self.path.append([lastX, lastY, lastZ, lastF])

            while self.idx < len(self.gcode) and self.gcode[self.idx] != '\r' and self.gcode[self.idx] != '\n':
                self.idx += 1
            while self.idx < len(self.gcode) and (self.gcode[self.idx] == '\r' or self.gcode[self.idx] == '\n'):
                self.idx += 1

        # last thing
        self.eval_path_time()

    def eval_path_time(self):
        '''
        '''
        total_time = 0 

        for idx, point in enumerate(self.path):
            prevIdx = max(idx - 1, 0)
            prevPoint = self.path[prevIdx]
           
            x = point[0]
            y = point[1]
            z = point[2]
            f = point[3]
            
            prevX = prevPoint[0]
            prevY = prevPoint[1]
            prevZ = prevPoint[2]
            #prevF = prevPoint[3]
            
            dist = math.sqrt((x - prevX) * (x - prevX) + (y - prevY) * (y - prevY) + (z - prevZ) * (z - prevZ))
            
            total_time = total_time + dist / f * 60
        
        self.path_time = total_time