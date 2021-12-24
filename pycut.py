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
from typing import Dict
from typing import Any

import clipper.clipper as ClipperLib
from clipper_utils import ClipperUtils

from svgpathutils import SvgPath
from svgviewer import SvgViewer

from cam import cam

from val_with_unit import ValWithUnit

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
            return ValWithUnit(x, "inch")
        else:
            return ValWithUnit(x * 25.4, "mm")

class GcodeModel:
    '''
    '''
    def __init__(self):
        # --------------------------- not sure yet for these
        self.units = "mm"
        self.XOffset = 0.0
        self.YOffset = 0.0

        # ----------------------------
        self.returnTo00 = False

        self.spindleControl = True
        self.spindleSpeed = 1000

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
        self.diameter = ValWithUnit(0.125, self.units)
        self.angle = 180
        self.passDepth = ValWithUnit(0.125, self.units)
        self.stepover = 0.4
        self.rapidRate = ValWithUnit(100, self.units)
        self.plungeRate = ValWithUnit(5, self.units)
        self.cutRate = ValWithUnit(40, self.units)

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
        self.matThickness = ValWithUnit(1.0, self.matUnits)
        self.matZOrigin = "Top"
        self.matClearance = ValWithUnit(0.1, self.matUnits)

    @property
    def matBotZ(self):
        if self.matZOrigin == "Bottom":
            return 0
        else:
            return - self.matThickness

    @property
    def matTopZ(self):
        if self.matZOrigin == "Top":
            return ValWithUnit(0, self.matUnits)
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
    

        #self.enabled.subscribe(xxxx)
        #self.margin.subscribe(self.recombine)
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
        self.maxCutDepth = ValWithUnit(0, self.units)

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

class CncOp:
    '''
    '''
    def __init__(self, operation: Dict[str,Any]):
        self.units = operation["Units"]
        self.name = operation["Name"]
        self.paths = operation["paths"]
        self.combinaison = operation["Combine"]
        self.ramp = operation["RampPlunge"]
        self.cam_op = operation["type"]
        self.direction = operation["Direction"]
        self.cutDepth = ValWithUnit(operation["Deep"], self.units)

        self.enabled = operation.get("enabled", False)

        if "Margin" in operation:
            self.margin = ValWithUnit(operation["Margin"], self.units)
        else:
            self.margin = None

        if "Width" in operation:
            self.width = ValWithUnit(operation["Width"], self.units)
        else:
            self.width = None
        
        # the input
        self.svg_paths : List[SvgPath] = [] # to fill at "setup"
        # the input "transformed"
        self.clipper_paths : List[List[ClipperLib.IntPoint]] = []
        
        # the resulting paths from the op combinaison setting + enabled svg paths
        self.geometry = ClipperLib.PathVector()
        # and the resulting svg paths from the combinaison, to be displayed
        # in the svg viewer
        self.geometry_svg_paths : List[SvgPath] = []

        self.cam_paths = []
        # and the resulting svg paths, to be displayed
        # in the svg viewer
        self.cam_paths_svg_paths : List[SvgPath] = []

    def put_value(self, attr, value):
        '''
        '''
        setattr(self, attr, value)

    def __str__(self):
        '''
        '''
        return "op: %s %s [%f] %s" % (self.name, self.cam_op, self.Deep, self.enabled)

    def setup(self, svg_viewer: SvgViewer):
        '''
        '''
        for svg_path_id in self.paths:

            svg_path_d = svg_viewer.get_svg_path_d(svg_path_id)
            svg_path = SvgPath(svg_path_id, {'d': svg_path_d})

            self.svg_paths.append(svg_path)
   
    def combine(self):
        '''
        '''
        for svg_path in self.svg_paths:
            clipper_path = svg_path.toClipperPath()
            self.clipper_paths.append(clipper_path)

        clipType = {
            "Union": ClipperLib.ClipType.ctUnion,
            "Intersection": ClipperLib.ClipType.ctIntersection,
            "Difference": ClipperLib.ClipType.ctDifference,
            "Xor": ClipperLib.ClipType.ctXor,
        } [self.combinaison] 
        
        geometry = ClipperUtils.combine(self.clipper_paths, clipType)

        self.geometry = ClipperUtils.simplifyAndClean(geometry, ClipperLib.PolyFillType.pftNonZero)
        #self.geometry = geometry

        #ClipperLib.dumpPaths("geometry", self.geometry)
        
    def calculate_geometry(self, toolModel: ToolModel):
        '''
        '''
        self.combine()

        if self.cam_op == "Pocket":
            self.calculate_preview_geometry_pocket()
        elif self.cam_op == "Inside":
            self.calculate_preview_geometry_inside(toolModel)
        elif self.cam_op == "Outside":
            self.calculate_preview_geometry_outside(toolModel)
        elif self.cam_op == "Engrave":
            self.calculate_preview_geometry_engrave()
        elif self.cam_op == "VPocket":
            self.calculate_preview_geometry_vpocket()

    def calculate_preview_geometry_pocket(self):
        '''
        '''
        if len(self.geometry) != 0:
            offset = self.margin.toInch() * ClipperUtils.inchToClipperScale
            offset = -offset

            self.preview_geometry = ClipperUtils.offset(self.geometry, offset)

            for clipper_path in self.preview_geometry:
                svg_path = SvgPath.fromClipperPath("geometry_pocket", clipper_path)
                self.geometry_svg_paths.append(svg_path)

    def calculate_preview_geometry_inside(self, toolModel: ToolModel):
        '''
        '''
        if len(self.geometry) != 0:
            offset = self.margin.toInch() * ClipperUtils.inchToClipperScale
            offset = -offset

            if offset != 0:
                geometry = ClipperUtils.offset(self.geometry, offset)
            else:
                geometry = self.geometry

            toolData = toolModel.getCamData()
               
            width = self.width.toInch() * ClipperUtils.inchToClipperScale
        
            if width < toolData["diameterClipper"]:
                width = toolData["diameterClipper"]
        
            self.preview_geometry = ClipperUtils.diff(geometry, ClipperUtils.offset(geometry, -width))

            #ClipperLib.dumpPaths("geometry", self.preview_geometry)

        # should have 2 paths, one inner, one outer -> show the "ring"
        if len(self.preview_geometry) > 1:
            self.geometry_svg_paths = [SvgPath.fromClipperPaths("geometry_inside", self.preview_geometry)]

    def calculate_preview_geometry_outside(self, toolModel: ToolModel):
        '''
        '''
        if len(self.geometry) != 0:
            offset = self.margin.toInch() * ClipperUtils.inchToClipperScale
           
            if offset != 0:
                geometry = ClipperUtils.offset(self.geometry, offset)
            else:
                geometry = self.geometry
            
            toolData = toolModel.getCamData()
            
            width = self.width.toInch() * ClipperUtils.inchToClipperScale
            if width < toolData["diameterClipper"]:
                width = toolData["diameterClipper"]
                  
            self.preview_geometry = ClipperUtils.diff(ClipperUtils.offset(geometry, width), geometry)

            #ClipperLib.dumpPaths("preview geometry", self.preview_geometry)

        # should have 2 paths, one inner, one outer -> show the "ring"
        if len(self.preview_geometry) > 1:
            self.geometry_svg_paths = [SvgPath.fromClipperPaths("geometry_outside", self.preview_geometry)]

    def calculate_preview_geometry_engrave(self):
        '''
        '''
        for clipper_path in self.geometry:
            svg_path = SvgPath.fromClipperPath("geometry_engrave", clipper_path)
            self.geometry_svg_paths.append(svg_path)

    def calculate_preview_geometry_vpocket(self):
        '''
        '''
        pass

    def calculate_toolpaths(self, svgModel: SvgModel, toolModel: ToolModel, materialModel: MaterialModel):
        '''
        '''
        toolData = toolModel.getCamData()

        name = self.name
        ramp = self.ramp
        cam_op = self.cam_op
        direction = self.direction
        cutDepth = self.cutDepth
        margin = self.margin
        width = self.width

        geometry = self.geometry
        
        offset = margin.toInch() * ClipperUtils.inchToClipperScale

        if cam_op == "Pocket" or cam_op == "V Pocket" or cam_op == "Inside":
            offset = -offset
        if cam_op != "Engrave" and offset != 0:
            geometry = ClipperUtils.offset(geometry, offset)

        if cam_op == "Pocket":
            self.cam_paths = cam.pocket(geometry, toolData["diameterClipper"], 1 - toolData["stepover"], direction == "Climb")
        elif cam_op == "V Pocket":
            self.cam_paths = cam.vPocket(geometry, toolModel.angle, toolData["passDepthClipper"], cutDepth.toInch() * ClipperUtils.inchToClipperScale, toolData["stepover"], direction == "Climb")
        elif cam_op == "Inside" or cam_op == "Outside":
            width = width.toInch() * ClipperUtils.inchToClipperScale
            if width < toolData["diameterClipper"]:
                width = toolData["diameterClipper"]
            self.cam_paths = cam.outline(geometry, toolData["diameterClipper"], cam_op == "Inside", width, 1 - toolData["stepover"], direction == "Climb")
        elif cam_op == "Engrave":
            self.cam_paths = cam.engrave(geometry, direction == "Climb")

        #path = ClipperUtils.getSnapPathFromClipperPaths(cam.getClipperPathsFromCamPaths(self.cam_paths), svgModel.pxPerInch)
        
        #if path != None and len(path):
        #    self.toolPathSvg = self.cam_pathsGroup.path(path).attr("class", "toolPath")

        for cam_path in self.cam_paths:
            svg_path = SvgPath.fromClipperPath("campath", cam_path.path)
            self.cam_paths_svg_paths.append(svg_path)

class JobModel:
    '''
    '''
    def __init__(self, 
            svg_viewer,
            cnc_ops: List[CncOp], 
            materialModel: MaterialModel, 
            svgModel: SvgModel, 
            toolModel: ToolModel,
            tabsModel: TabsModel,
            gcodeModel: GcodeModel):

        self.svg_viewer = svg_viewer
        
        self.operations = cnc_ops
        
        self.svgModel = svgModel
        self.materialModel = materialModel
        self.toolModel = toolModel
        self.tabsModel = tabsModel
        self.gcodeModel = gcodeModel

        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0

        self.calculate_operation_cam_paths()
        self.findMinMax()

        self.gcode = ""

    def calculate_operation_cam_paths(self):
        for op in self.operations:
            if op.enabled :
                op.setup(self.svg_viewer)
                op.calculate_geometry(self.toolModel)
                op.calculate_toolpaths(self.svgModel, self.toolModel, self.materialModel)
    
    def findMinMax(self):
        minX = 0
        maxX = 0
        minY = 0
        maxY = 0
        foundFirst = False

        for op in self.operations:
            if op.enabled and op.cam_paths != None :
                for cam_path in op.cam_paths:
                    toolPath = cam_path.path
                    for point in toolPath:
                        if not foundFirst:
                            minX = point.X
                            maxX = point.X
                            minY = point.Y
                            maxY = point.Y
                            foundFirst = True
                        else:
                            minX = min(minX, point.X)
                            minY = min(minY, point.Y)
                            maxX = max(maxX, point.X)
                            maxY = max(maxY, point.Y)
                        
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY



class GcodeGenerator:
    '''
    '''
    def __init__(self, job: JobModel):
        self.job = job

        self.materialModel = job.materialModel
        self.toolModel = job.toolModel
        self.tabsModel = job.tabsModel
        self.gcodeModel = job.gcodeModel

        self.units = self.gcodeModel.units
        self.unitConverter = UnitConverter(self.units)

        self.offsetX = self.gcodeModel.XOffset
        self.offsetY = self.gcodeModel.YOffset

        self.gcode = ""

    @property
    def minX(self):
        return self.unitConverter.fromInch(self.job.minX / ClipperUtils.inchToClipperScale) + self.offsetX

    @property
    def maxX(self):
        return self.unitConverter.fromInch(self.job.maxX / ClipperUtils.inchToClipperScale) + self.offsetX
    
    @property
    def minY(self):
        return  -self.unitConverter.fromInch(self.job.maxY / ClipperUtils.inchToClipperScale) + self.offsetY
   
    @property
    def maxY(self):
        return  -self.unitConverter.fromInch(self.job.minY / ClipperUtils.inchToClipperScale) + self.offsetY

    def generateGcode_zeroLowerLeft(self):
        self.offsetX = - self.unitConverter.fromInch(self.job.minX / ClipperUtils.inchToClipperScale)
        self.offsetY = - self.unitConverter.fromInch(-self.job.maxY / ClipperUtils.inchToClipperScale)
        self.generateGcode()

    def generateGcode_zeroCenter(self):
        self.offsetX = - self.unitConverter.fromInch((self.job.minX + self.job.maxX) / 2 / ClipperUtils.inchToClipperScale)
        self.offsetY = - self.unitConverter.fromInch(-(self.job.minY + self.job.maxY) / 2 / ClipperUtils.inchToClipperScale)
        self.generateGcode()

    def setXOffset(self, value):
        self.offsetX = value
        self.generateGcode()

    def setYOffset(self, value):
        self.offsetY = value
        self.generateGcode()

    def generateGcode(self):
        cnc_ops: List['CncOp'] = []
        for cnc_op in self.job.operations:
            if cnc_op.enabled:
                if len(cnc_op.cam_paths) > 0:
                    cnc_ops.append(cnc_op)
            
        if len(cnc_ops) == 0:
            return

        safeZ = self.unitConverter.fromInch(self.materialModel.matZSafeMove.toInch())
        rapidRate = int(self.unitConverter.fromInch(self.toolModel.rapidRate.toInch()))
        plungeRate = int(self.unitConverter.fromInch(self.toolModel.plungeRate.toInch()))
        cutRate = int(self.unitConverter.fromInch(self.toolModel.cutRate.toInch()))
        passDepth = self.unitConverter.fromInch(self.toolModel.passDepth.toInch())
        topZ = self.unitConverter.fromInch(self.materialModel.matTopZ.toInch())
        tabCutDepth = self.unitConverter.fromInch(self.tabsModel.maxCutDepth.toInch())
        tabZ = ValWithUnit(topZ - tabCutDepth, self.gcodeModel.units) # CHEKME

        if self.units == "inch":
            scale = 1.0 / ClipperUtils.inchToClipperScale
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
        gcode += "G1 Z%s    F%d      ; Move to clearance level\r\n" % (safeZ.toFixed(4), rapidRate)

        if self.gcodeModel.spindleControl:
            gcode += f"\r\n; Start the spindle\r\n"
            gcode += f"M3 S{self.gcodeModel.spindleSpeed}\r\n"

        for idx, cnc_op in enumerate(cnc_ops):
            cutDepth = self.unitConverter.fromInch(cnc_op.cutDepth.toInch())

            nb_paths = len(cnc_op.cam_paths)  # in use!

            gcode += f"\r\n;"
            gcode += f"\r\n; Operation:    {idx}"
            gcode += f"\r\n; Name:         {cnc_op.name}"
            gcode += f"\r\n; Type:         {cnc_op.cam_op}"
            gcode += f"\r\n; Paths:        {nb_paths}"
            gcode += f"\r\n; Direction:    {cnc_op.direction}"
            gcode += f"\r\n; Cut Depth:    {cutDepth}"
            gcode += f"\r\n; Pass Depth:   {passDepth}"
            gcode += f"\r\n; Plunge rate:  {plungeRate}"
            gcode += f"\r\n; Cut rate:     {cutRate}"
            gcode += f"\r\n;\r\n"

            gcode += cam.getGcode({
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

        if self.gcodeModel.spindleControl:
            gcode += f"\r\n; Stop the spindle\r\n"
            gcode += f"M5 \r\n"

        if self.gcodeModel.returnTo00:
            gcode += f"\r\n; Return to 0,0\r\n"
            gcode += f"G0 X0 Y0 F {rapidRate}\r\n"

        self.gcode = gcode
        self.job.gcode = gcode

