# Copyright 2022 Xavier
#
# This file is part of pycut.
#
# pycut is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pycut is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pycut.  If not, see <http:#www.gnu.org/licenses/>.

import jscut


class ToolModel:
    '''
    '''
    def __init__(self):
        self.units = "inch"
        self.diameter = 0.125
        self.angle = 180
        self.passDepth = 0.125
        self.stepover = 0.4
        self.rapidRate = 100
        self.plungeRate = 5
        self.cutRate = 40

    def getCamArgs(self):
        result = {
            "diameterClipper": self.diameter.toInch() * jscut.priv.path.inchToClipperScale,
            "passDepthClipper": self.passDepth.toInch() * jscut.priv.path.inchToClipperScale,
            "stepover": self.stepover
        }

        if result.diameterClipper <= 0:
            #showAlert("Tool diameter must be greater than 0", "alert-danger")
            return None
        
        if result.stepover <= 0:
            #showAlert("Tool stepover must be geater than 0", "alert-danger")
            return None
        
        if result.stepover > 1:
            #showAlert("Tool stepover must be less than or equal to 1", "alert-danger")
            return None
        
        return result
        
