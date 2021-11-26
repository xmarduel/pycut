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


class UnitConverter:
    '''
    '''
    def __init__(self, units: str):
        '''
        '''
        self.units = units

    def toInch(self, x):
        '''
        Convert x from the current unit to inch
        '''
        if self.units == "inch":
            return x
        else:
            return x / 25.4
    
    def fromInch(self, x):
        '''
        Convert x from inch to the current unit
        '''
        if self.units == "inch":
            return x
        else:
            return x * 25.4

