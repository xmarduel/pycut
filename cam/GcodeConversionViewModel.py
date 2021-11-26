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

import time

from typing import List

import UnitConverter

from MaterialViewModel import MaterialViewModel
from ToolViewModel import ToolModel
from OperationsViewModel import OperationsViewModel
from OperationsViewModel import Operation
from TabsViewModel import TabsViewModel

import clipper as ClipperLib
import jscut


class GcodeConversionViewModel:
    '''
    '''
    def __init__(self, 
            materialViewModel: MaterialViewModel, 
            toolModel: ToolModel, 
            operationsViewModel: OperationsViewModel, 
            tabsViewModel: TabsViewModel):

        self.allowGen = True

        self.materialViewModel = materialViewModel
        self.toolModel = toolModel
        self.operationsViewModel = operationsViewModel
        self.tabsViewModel = tabsViewModel

        self.returnTo00 = False

        self.units = "mm"
        self.unitConverter: UnitConverter = UnitConverter(self.units)

        self.offsetX = 0
        self.offsetY = 0

        self.gcode = ""
        self.gcodeFilename = "gcode.gcode"

    @property
    def minX(self):
        return self.unitConverter.fromInch(self.operationsViewModel.minX / jscut.priv.path.inchToClipperScale) + self.offsetX

    @property
    def maxX(self):
        return self.unitConverter.fromInch(self.operationsViewModel.maxX / jscut.priv.path.inchToClipperScale) + self.offsetX
    
    @property
    def minY(self):
        return -(self.unitConverter.fromInch(self.operationsViewModel.maxY / jscut.priv.path.inchToClipperScale) + self.offsetY)
   
    @property
    def  maxY(self):
        return -(self.unitConverter.fromInch(self.operationsViewModel.minY / jscut.priv.path.inchToClipperScale) + self.offsetY)

    def zeroLowerLeft(self):
        self.allowGen = False
        self.offsetX = - self.unitConverter.fromInch(self.operationsViewModel.minX / jscut.priv.path.inchToClipperScale)
        self.offsetY = - self.unitConverter.fromInch(-self.operationsViewModel.maxY / jscut.priv.path.inchToClipperScale)
        self.allowGen = True
        self.generateGcode()

    def zeroCenter(self):
        self.allowGen = False
        self.offsetX = - self.unitConverter.fromInch((self.operationsViewModel.minX + self.operationsViewModel.maxX) / 2 / jscut.priv.path.inchToClipperScale)
        self.offsetY = - self.unitConverter.fromInch(-(self.operationsViewModel.minY + self.operationsViewModel.maxY) / 2 / jscut.priv.path.inchToClipperScale)
        self.allowGen = True
        self.generateGcode()

    def generateGcode(self):
        if not self.allowGen:
            return

        ops: List[Operation] = []
        for op in self.operationsViewModel.operations:
            if op.enabled:
                if op.toolPaths != None and len(op.toolPaths) > 0:
                    ops.append(op)
            
        if len(ops) == 0:
            return

        safeZ = self.unitConverter.fromInch(self.materialViewModel.matZSafeMove.toInch())
        rapidRate = self.unitConverter.fromInch(self.toolModel.rapidRate.toInch())
        plungeRate = self.unitConverter.fromInch(self.toolModel.plungeRate.toInch())
        cutRate = self.unitConverter.fromInch(self.toolModel.cutRate.toInch())
        passDepth = self.unitConverter.fromInch(self.toolModel.passDepth.toInch())
        topZ = self.unitConverter.fromInch(self.materialViewModel.matTopZ.toInch())
        tabCutDepth = self.unitConverter.fromInch(self.tabsViewModel.maxCutDepth.toInch())
        tabZ = topZ - tabCutDepth

        if passDepth <= 0:
            showAlert("Pass Depth is not greater than 0.", "alert-danger")
            return

        if self.units == "inch":
            scale = 1 / jscut.priv.path.inchToClipperScale
        else:
            scale = 25.4 / jscut.priv.path.inchToClipperScale

        tabGeometry = []
        for tab in self.tabsViewModel.tabs:
            if tab.enabled:
                offset = self.toolModel.diameter.toInch() / 2 * jscut.priv.path.inchToClipperScale
                geometry = jscut.priv.path.offset(tab.combinedGeometry, offset)
                tabGeometry = jscut.priv.path.clip(tabGeometry, geometry, ClipperLib.ClipType.ctUnion)

        gcode = ""
        if self.units == "inch":
            gcode += "G20         ; Set units to inches\r\n"
        else:
            gcode += "G21         ; Set units to mm\r\n"
        gcode += "G90         ; Absolute positioning\r\n"
        gcode += "G1 Z" + safeZ + " F" + rapidRate + "      ; Move to clearance level\r\n"

        for idx, op in enumerate(ops):
            cutDepth = self.unitConverter.fromInch(op.cutDepth.toInch())
            if cutDepth <= 0:
                showAlert("An operation has a cut depth which is not greater than 0.", "alert-danger")
                return

            gcode += "\r\n;"
            gcode += "\r\n; Operation:    " + idx
            gcode += "\r\n; Name:         " + op.name
            gcode += "\r\n; Type:         " + op.camOp
            gcode += "\r\n; Paths:        " + len(op.toolPaths)
            gcode += "\r\n; Direction:    " + op.direction
            gcode += "\r\n; Cut Depth:    " + cutDepth
            gcode += "\r\n; Pass Depth:   " + passDepth
            gcode += "\r\n; Plunge rate:  " + plungeRate
            gcode += "\r\n; Cut rate:     " + cutRate
            gcode += "\r\n;\r\n"

            gcode += jscut.priv.cam.getGcode({
                "paths":          op.toolPaths,
                "ramp":           op.ramp,
                "scale":          scale,
                "useZ":           op.camOp == "V Pocket",
                "offsetX":        self.offsetX,
                "offsetY":        self.offsetY,
                "decimal":        4,
                "topZ":           topZ,
                "botZ":           topZ - cutDepth,
                "safeZ":          safeZ,
                "passDepth":      passDepth,
                "plungeFeed":     plungeRate,
                "retractFeed":    rapidRate,
                "cutFeed":        cutRate,
                "rapidFeed":      rapidRate,
                "tabGeometry":    tabGeometry,
                "tabZ":           tabZ,
            })

        if self.returnTo00:
            gcode += "\r\n; Return to 0,0\r\n"
            gcode += "G0 X0 Y0 F" + rapidRate + "\r\n"

        self.gcode = gcode

