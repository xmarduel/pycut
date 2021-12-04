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

import clipper.clipper as ClipperLib


from clipper_utils import ClipperUtils

from cnc_op import CncOp
from cnc_op import JobModel

import cam


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

class SvgModel:
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

    def getCamData(self):
        result = {
            "diameterClipper": self.diameter.toInch() * ClipperUtils.inchToClipperScale,
            "passDepthClipper": self.passDepth.toInch() * ClipperUtils.inchToClipperScale,
            "stepover": self.stepover
        }
        
        return result
        
class MaterialModel:
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
            svgViewModel: SvgModel, 
            tabsModel: 'TabsModel', 
            tabsGroup, 
            rawPaths, 
            toolPathsChanged, 
            loading) :
        '''
        '''
        self.svgViewModel = svgViewModel
        self.tabsModel = tabsModel
        self.tabsGroup = tabsGroup
        self.rawPaths = rawPaths
        self.toolPathsChanged = toolPathsChanged
        self.loading = loading

        self.enabled = True
        self.margin = 0.0
        
        self.combinedGeometry = []
        self.combinedGeometrySvg = None

        tabsModel.unitConverter.addComputed(self.margin)

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
            geometry = ClipperUtils.getClipperPathsFromSnapPath(rawPath.path, self.svgViewModel.pxPerInch, alert)
            if geometry != None:
                if rawPath.nonzero:
                    fillRule = ClipperLib.PolyFillType.pftNonZero
                else:
                    fillRule = ClipperLib.PolyFillType.pftEvenOdd
                all.append(ClipperUtils.simplifyAndClean(geometry, fillRule))

        if len(all) == 0:
            self.combinedGeometry = []
        else :
            self.combinedGeometry = all[0]
            for o in all:
                self.combinedGeometry = ClipperUtils.clip(self.combinedGeometry, o, ClipperLib.ClipType.ctUnion)

        offset = self.margin.toInch() * ClipperUtils.inchToClipperScale
        if offset != 0:
            self.combinedGeometry = ClipperUtils.offset(self.combinedGeometry, offset)

        if len(self.combinedGeometry) != 0:
            path = ClipperUtils.getSnapPathFromClipperPaths(self.combinedGeometry, self.svgViewModel.pxPerInch())
            if path != None:
                self.combinedGeometrySvg = self.tabsGroup.path(path).attr("class", "tabsGeometry")

        self.enabled(True)
        self.toolPathsChanged()

class TabsModel:
    '''
    '''
    def __init__(self, 
            svgViewModel: SvgModel, 
            materialModel: MaterialModel, 
            tabsGroup, 
            toolPathsChanged):
    
        self.svgViewModel = svgViewModel
        self.materialModel = materialModel
        self.tabsGroup = tabsGroup 
        self.toolPathsChanged = toolPathsChanged

        self.tabs: List[Tab] = []
        self.units = self.materialModel.matUnits
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



class GcodeGenerator:
    '''
    '''
    def __init__(self, 
            materialModel: MaterialModel, 
            toolModel: ToolModel, 
            tabsModel: TabsModel,
            jobModel: JobModel):

        self.materialModel = materialModel
        self.toolModel = toolModel
        self.tabsModel = tabsModel
        self.jobModel = jobModel

        self.returnTo00 = False

        self.units = "mm"
        self.unitConverter: UnitConverter = UnitConverter(self.units)

        self.offsetX = 0
        self.offsetY = 0

        self.gcode = ""
        self.gcodeFilename = "gcode.gcode"

    @property
    def minX(self):
        return self.unitConverter.fromInch(self.jobModel.minX / ClipperUtils.inchToClipperScale) + self.offsetX

    @property
    def maxX(self):
        return self.unitConverter.fromInch(self.jobModel.maxX / ClipperUtils.inchToClipperScale) + self.offsetX
    
    @property
    def minY(self):
        return -(self.unitConverter.fromInch(self.jobModel.maxY / ClipperUtils.inchToClipperScale) + self.offsetY)
   
    @property
    def maxY(self):
        return -(self.unitConverter.fromInch(self.jobModel.minY / ClipperUtils.inchToClipperScale) + self.offsetY)

    def zeroLowerLeft(self):
        self.offsetX = - self.unitConverter.fromInch(self.jobModel.minX / ClipperUtils.inchToClipperScale)
        self.offsetY = - self.unitConverter.fromInch(-self.jobModel.maxY / ClipperUtils.inchToClipperScale)
        self.generateGcode()

    def zeroCenter(self):
        self.offsetX = - self.unitConverter.fromInch((self.jobModel.minX + self.jobModel.maxX) / 2 / ClipperUtils.inchToClipperScale)
        self.offsetY = - self.unitConverter.fromInch(-(self.jobModel.minY + self.jobModel.maxY) / 2 / ClipperUtils.inchToClipperScale)
        self.generateGcode()

    def generateGcode(self):
        cnc_ops: List[CncOp] = []
        for cnc_op in self.jobModel.operations:
            if cnc_op.enabled:
                if len(cnc_op.cam_paths) > 0:
                    cnc_ops.append(cnc_op)
            
        if len(cnc_ops) == 0:
            return

        safeZ = self.unitConverter.fromInch(self.materialModel.matZSafeMove.toInch())
        rapidRate = self.unitConverter.fromInch(self.toolModel.rapidRate.toInch())
        plungeRate = self.unitConverter.fromInch(self.toolModel.plungeRate.toInch())
        cutRate = self.unitConverter.fromInch(self.toolModel.cutRate.toInch())
        passDepth = self.unitConverter.fromInch(self.toolModel.passDepth.toInch())
        topZ = self.unitConverter.fromInch(self.materialModel.matTopZ.toInch())
        tabCutDepth = self.unitConverter.fromInch(self.tabsModel.maxCutDepth.toInch())
        tabZ = topZ - tabCutDepth

        if self.units == "inch":
            scale = 1 / ClipperUtils.inchToClipperScale
        else:
            scale = 25.4 / ClipperUtils.inchToClipperScale

        tabGeometry = []
        for tab in self.tabsModel.tabs:
            if tab.enabled:
                offset = self.toolModel.diameter.toInch() / 2 * ClipperUtils.inchToClipperScale
                geometry = ClipperUtils.offset(tab.combinedGeometry, offset)
                tabGeometry = ClipperUtils.clip(tabGeometry, geometry, ClipperLib.ClipType.ctUnion)

        gcode = ""
        if self.units == "inch":
            gcode += "G20         ; Set units to inches\r\n"
        else:
            gcode += "G21         ; Set units to mm\r\n"
        gcode += "G90         ; Absolute positioning\r\n"
        gcode += "G1 Z" + safeZ + " F" + rapidRate + "      ; Move to clearance level\r\n"

        for idx, cnc_op in enumerate(cnc_ops):
            cutDepth = self.unitConverter.fromInch(cnc_op.cutDepth.toInch())

            gcode += "\r\n;"
            gcode += "\r\n; Operation:    " + idx
            gcode += "\r\n; Name:         " + cnc_op.name
            gcode += "\r\n; Type:         " + cnc_op.cam_op
            gcode += "\r\n; Paths:        " + len(cnc_op.cam_paths)
            gcode += "\r\n; Direction:    " + cnc_op.direction
            gcode += "\r\n; Cut Depth:    " + cutDepth
            gcode += "\r\n; Pass Depth:   " + passDepth
            gcode += "\r\n; Plunge rate:  " + plungeRate
            gcode += "\r\n; Cut rate:     " + cutRate
            gcode += "\r\n;\r\n"

            gcode += cam.cam.getGcode({
                "paths":          cnc_op.cam_paths,
                "ramp":           cnc_op.ramp,
                "scale":          scale,
                "useZ":           cnc_op.cam_op == "V Pocket",
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

