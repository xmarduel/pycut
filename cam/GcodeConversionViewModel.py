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

from typing import List

import clipper as ClipperLib

from OperationsViewModel import OperationsViewModel
from OperationsViewModel import Operation

import cam_op


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

class SvgViewModel:
    '''
    '''
    def __init__(self):
        self.pxPerInch = 96

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
            "diameterClipper": self.diameter.toInch() * cam_op.inchToClipperScale,
            "passDepthClipper": self.passDepth.toInch() * cam_op.inchToClipperScale,
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
        
class MaterialViewModel:
    '''
    '''
    def __init__(self):
        self.matUnits = "inch"
        self.matThickness = 1.0
        self.matZOrigin = "Top"
        self.matClearance = 0.1

    @property
    def matBotZ(self):
        if self.matZOrigin == "Bottom":
            return 0
        else:
            return - self.matThickness

    @property
    def matTopZ(self):
        if self.matZOrigin == "Top":
            return 0
        else:
            return self.matThickness

    @property
    def matZSafeMove(self):
        if self.matZOrigin == "Top":
            return self.matClearance
        else:
            return self.matThickness + self.matClearance

class Tab:
    '''
    '''
    def __init__(self,
            svgViewModel: SvgViewModel, 
            tabsViewModel: 'TabsViewModel', 
            tabsGroup, 
            rawPaths, 
            toolPathsChanged, 
            loading) :
        '''
        '''
        self.svgViewModel = svgViewModel
        self.tabsViewModel = tabsViewModel
        self.tabsGroup = tabsGroup
        self.rawPaths = rawPaths
        self.toolPathsChanged = toolPathsChanged
        self.loading = loading

        self.enabled = True
        self.margin = 0.0
        
        self.combinedGeometry = []
        self.combinedGeometrySvg = None

        tabsViewModel.unitConverter.addComputed(self.margin)

        def xxxx(newValue):
            if newValue:
                v = "visible"
            else:
                v = "hidden"
            if self.combinedGeometrySvg:
                self.combinedGeometrySvg.attr("visibility", v)
    

        self.enabled.subscribe(xxxx)
        self.margin.subscribe(self.recombine)
        self.recombine()

    def removeCombinedGeometrySvg(self):
        if self.combinedGeometrySvg:
            self.combinedGeometrySvg.remove()
            self.combinedGeometrySvg = None


    def recombine(self):
        if self.loading:
            return

        self.removeCombinedGeometrySvg()

        def alert(msg):
            showAlert(msg, "alert-warning")

        all = []
        for rawPath in self.rawPaths:
            geometry = cam_op.getClipperPathsFromSnapPath(rawPath.path, self.svgViewModel.pxPerInch, alert)
            if geometry != None:
                if rawPath.nonzero:
                    fillRule = ClipperLib.PolyFillType.pftNonZero
                else:
                    fillRule = ClipperLib.PolyFillType.pftEvenOdd
                all.append(cam_op.simplifyAndClean(geometry, fillRule))

        if len(all) == 0:
            self.combinedGeometry = []
        else :
            self.combinedGeometry = all[0]
            for o in all:
                self.combinedGeometry = cam_op.clip(self.combinedGeometry, o, ClipperLib.ClipType.ctUnion)

        offset = self.margin.toInch() * cam_op.inchToClipperScale
        if offset != 0:
            self.combinedGeometry = cam_op.offset(self.combinedGeometry, offset)

        if len(self.combinedGeometry) != 0:
            path = cam_op.getSnapPathFromClipperPaths(self.combinedGeometry, self.svgViewModel.pxPerInch())
            if path != None:
                self.combinedGeometrySvg = self.tabsGroup.path(path).attr("class", "tabsGeometry")

        self.enabled(True)
        self.toolPathsChanged()

class TabsViewModel:
    '''
    '''
    def __init__(self, 
            svgViewModel: SvgViewModel, 
            materialViewModel: MaterialViewModel, 
            selectionViewModel: 'SelectionViewModel', 
            tabsGroup, 
            toolPathsChanged):
    
        self.svgViewModel = svgViewModel
        self.materialViewModel = materialViewModel
        self.selectionViewModel = selectionViewModel
        self.tabsGroup = tabsGroup 
        self.toolPathsChanged = toolPathsChanged

        self.tabs: List[Tab] = []
        self.units = self.materialViewModel.matUnits
        self.maxCutDepth = 0

    def addTab(self):
        rawPaths = []

        for element in self.selectionViewModel.getSelection():
            rawPaths.append({
                'path': Snap.parsePathString(element.attr('d')),
                'nonzero': element.attr("fill-rule") != "evenodd",
            })

        self.selectionViewModel.clearSelection()
        tab = Tab(self.svgViewModel, self, self.tabsGroup, rawPaths, self.toolPathsChanged, False)
        self.tabs.append(tab)
        self.toolPathsChanged()

    def removeTab(self, tab):
        tab.removeCombinedGeometrySvg()
        self.tabs.remove(tab)
        self.toolPathsChanged()

    def clickOnSvg(self, elem) :
        if elem.attr("class") == "tabsGeometry":
            return True
        return False



class GcodeConversionViewModel:
    '''
    '''
    def __init__(self, 
            materialViewModel: MaterialViewModel, 
            toolModel: ToolModel, 
            operationsViewModel: OperationsViewModel, 
            tabsViewModel: TabsViewModel):

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
        return self.unitConverter.fromInch(self.operationsViewModel.minX / cam_op.inchToClipperScale) + self.offsetX

    @property
    def maxX(self):
        return self.unitConverter.fromInch(self.operationsViewModel.maxX / cam_op.inchToClipperScale) + self.offsetX
    
    @property
    def minY(self):
        return -(self.unitConverter.fromInch(self.operationsViewModel.maxY / cam_op.inchToClipperScale) + self.offsetY)
   
    @property
    def maxY(self):
        return -(self.unitConverter.fromInch(self.operationsViewModel.minY / cam_op.inchToClipperScale) + self.offsetY)

    def zeroLowerLeft(self):
        self.offsetX = - self.unitConverter.fromInch(self.operationsViewModel.minX / cam_op.inchToClipperScale)
        self.offsetY = - self.unitConverter.fromInch(-self.operationsViewModel.maxY / cam_op.inchToClipperScale)
        self.generateGcode()

    def zeroCenter(self):
        self.offsetX = - self.unitConverter.fromInch((self.operationsViewModel.minX + self.operationsViewModel.maxX) / 2 / cam_op.inchToClipperScale)
        self.offsetY = - self.unitConverter.fromInch(-(self.operationsViewModel.minY + self.operationsViewModel.maxY) / 2 / cam_op.inchToClipperScale)
        self.generateGcode()

    def generateGcode(self):
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
            scale = 1 / cam_op.inchToClipperScale
        else:
            scale = 25.4 / cam_op.inchToClipperScale

        tabGeometry = []
        for tab in self.tabsViewModel.tabs:
            if tab.enabled:
                offset = self.toolModel.diameter.toInch() / 2 * cam_op.inchToClipperScale
                geometry = cam_op.offset(tab.combinedGeometry, offset)
                tabGeometry = cam_op.clip(tabGeometry, geometry, ClipperLib.ClipType.ctUnion)

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

