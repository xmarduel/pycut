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

import shapely
import shapely.geometry

from  shapely_utils import ShapelyUtils

from svgpathutils import SvgPath
from svgviewer import SvgViewer

from cam import cam
from cam import CamPath

from val_with_unit import ValWithUnit


class UnitConverter:
    '''
    '''
    def __init__(self, units: str):
        '''
        '''
        self.units = units

    def toInch(self, x: float):
        '''
        Convert x from the current unit to inch
        '''
        if self.units == "inch":
            return x
        else:
            return x / 25.4

    def fromInch(self, x: float):
        '''
        Convert x from inch to the current unit
        '''
        if self.units == "inch":
            return ValWithUnit(x, "inch")
        else:
            return ValWithUnit(x * 25.4, "mm")

    def fromMm(self, x: float):
        '''
        Convert x from mm to the current unit
        '''
        if self.units == "inch":
            return ValWithUnit(x / 25.4, "inch")
        else:
            return ValWithUnit(x, "mm")

class GcodeModel:
    '''
    '''
    ZERO_TOP_LEFT_OF_MATERIAL = 1
    ZERO_LOWER_LEFT_OF_MATERIAL = 2
    ZERO_LOWER_LEFT_OF_OP = 3
    ZERO_CENTER_OF_OP = 4

    XYRef = {
        ZERO_TOP_LEFT_OF_MATERIAL : "ZERO_TOP_LEFT_OF_MATERIAL",
        ZERO_LOWER_LEFT_OF_MATERIAL : "ZERO_LOWER_LEFT_OF_MATERIAL",
        ZERO_LOWER_LEFT_OF_OP : "ZERO_LOWER_LEFT_OF_OP",
        ZERO_CENTER_OF_OP : "ZERO_CENTER_OF_OP",
    }

    def __init__(self):
        # --------------------------- not sure yet for these
        self.units = "mm"
        self.XOffset = 0.0
        self.YOffset = 0.0

        self.gcodeZero = GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL

        self.flipXY = False

        # ----------------------------
        self.returnTo00 = False

        self.spindleControl = True
        self.spindleSpeed = 1000

        self.programEnd = False

class SvgModel:
    '''
    '''
    # FIXME : read from the size file
    sizeX = 100.0
    sizeY = 100.0

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
        ''' 
        convert to the gcode units FIXME actual per default mm 
        '''
        result = {
            "diameterTool": self.diameter.toMm(),
            "passDepthTool": self.passDepth.toMm(),
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

        # from the svg size, the dimension of the material in mm
        self.sizeX = ValWithUnit(SvgModel.sizeX, "mm") # default
        self.sizeY = ValWithUnit(SvgModel.sizeX, "mm") # default

    def setMaterialSizeX(self, x: ValWithUnit):
        self.sizeX = x.toMm()

    def setMaterialSizeY(self, y: ValWithUnit):
        self.sizeY = y.toMm()

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
    a Tab is defined by a circle with position (x,y)
    and height from the buttom of the material
    '''
    height = ValWithUnit(2.0, "mm")

    def __init__(self, tab: Dict[str, Any]) :
        '''
        '''
        self.center = tab["center"]
        self.radius = tab["radius"]

        self.enabled = tab["enabled"]

        self.svg_path = self.make_svg_path()

    @classmethod
    def set_height(cls, heigth: float, units: str):
        '''
        from the TabsModel, common for all the tabs
        '''
        cls.height = ValWithUnit(heigth, units)

    def make_svg_path(self):
        '''
        '''
        path = SvgPath.fromCircleDef(self.center, self.radius)

        return path

    def posInsideTab(self, x: float, y: float, z: float, op_cut_depth: float):
        '''
        ---------------------- 0

                          ---- z is negativ
         material
        ---------------------- height = 2
        ---------------------- op_cut_depth = 10

        '''
        if op_cut_depth + z > self.height:
            # still above the tab
            return False

        dx = self.center.x - x
        dy = self.center.y - y

        return (dx*dx + dy*dy <= self.radius*self.radius)

class TabsModel:
    '''
    '''
    def __init__(self, tabs: List[Tab]):

        self.tabs: List[Tab] = tabs

        self.units = "mm"  # default
        self.height = ValWithUnit(2.0, self.units) # default

        Tab.set_height(self.height, self.units)

    def set_height(self, height: float, units: str):
        self.units = units
        self.height = ValWithUnit(height, units)

        Tab.set_height(self.height)

    def hasTabs(self):
        return len(self.tabs) > 0

    def posInTab(self, x: float, y: float, z: float, op_cut_depth: float):
        for tab in self.tabs:
            if tab.posInsideTab(x, y, z, op_cut_depth):
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
        # and the resulting svg paths from the combinaison, to be displayed in the svg viewer
        self.geometry_svg_paths : List[SvgPath] = []
        
        # the resulting paths from the op combinaison setting + enabled svg paths
        self.geometry : shapely.geometry.MultiPolygon = None
        
        # the resulting tool paths
        self.cam_paths : List[CamPath] = []
        # and the resulting tool paths, to be displayed in the svg viewer
        self.cam_paths_svg_paths : List[SvgPath] = []

    def put_value(self, attr: str, value: Any):
        '''
        '''
        setattr(self, attr, value)

    def __str__(self):
        '''
        '''
        return "op: %s %s [%f] %s" % (self.name, self.cam_op, self.cutDepth, self.enabled)

    def setup(self, svg_viewer: SvgViewer):
        '''
        '''
        for svg_path_id in self.paths:

            svg_path_d = svg_viewer.get_svg_path_d(svg_path_id)
            svg_path = SvgPath(svg_path_id, {'d': svg_path_d})

            self.svg_paths.append(svg_path)

    def combine(self):
        '''
        generate the combinaison of the selected paths

        the generated geometry is a MultiPolygon
        '''
        self.shapely_polygons : List[shapely.geometry.Polygon] = []

        for svg_path in self.svg_paths:
            shapely_polygons = svg_path.toShapelyPolygons()
            self.shapely_polygons += shapely_polygons

        if len(self.shapely_polygons) == 0:
            return
        
        if len(self.shapely_polygons) == 1:
            self.geometry = shapely.geometry.MultiPolygon(self.shapely_polygons)
            return

        o = self.shapely_polygons[0]
        #other = shapely.geometry.MultiPolygon(self.shapely_polygons[1:])
        other = ShapelyUtils.union_polygons(self.shapely_polygons[1:])

        if self.combinaison == "Union":
            geometry = o.union(other)
        if self.combinaison == "Intersection":
            geometry = o.intersection(other)
        if self.combinaison == "Difference":
            geometry = o.difference(other)
        if self.combinaison == "Xor":
            geometry = o.symmetric_difference(other)
        
        self.geometry = geometry

        # what!! result may be not well orienteted!!
        if self.geometry.geom_type == 'Polygon':
            # fix orientation
            self.geometry = ShapelyUtils.reorder_poly_points(self.geometry)

            self.geometry = shapely.geometry.polygon.orient(self.geometry)
            self.geometry = shapely.geometry.MultiPolygon([self.geometry])
        else:
            # fix orientation
            fixed_polys = []
            for poly in self.geometry:
                if not poly.geom_type == 'Polygon':
                    continue
                # fix - do not start a poly from a convex corner
                poly = ShapelyUtils.reorder_poly_points(poly)

                fixed_poly = shapely.geometry.polygon.orient(poly)
                fixed_polys.append(fixed_poly)
            self.geometry = shapely.geometry.MultiPolygon(fixed_polys)

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

    def calculate_preview_geometry_pocket(self):
        '''
        '''
        if self.geometry is not None:
            offset = self.margin.toMm()

            # 'left' in 'inside', and 'right' is 'outside'
            self.geometry = ShapelyUtils.orientMultiPolygon(self.geometry)
            _, self.preview_geometry = ShapelyUtils.offsetMultiPolygon(self.geometry, offset, 'left', ginterior=True)
            
            ShapelyUtils.MatplotlibDisplay("preview pocket", self.preview_geometry)
            
            self.preview_geometry = ShapelyUtils.orientMultiPolygon(self.preview_geometry)

            ShapelyUtils.MatplotlibDisplay("preview pocket - oriented", self.preview_geometry)

            self.geometry_svg_paths = []

            for poly in self.preview_geometry.geoms:
                geometry_svg_path = SvgPath.fromShapelyPolygon("pycut_geometry_pocket", poly)
                self.geometry_svg_paths.append(geometry_svg_path)
        
    def calculate_preview_geometry_inside(self, toolModel: ToolModel):
        '''
        '''
        if self.geometry is not None:
            margin = self.margin.toMm()
            
            if margin != 0:
                _, geometry = ShapelyUtils.offsetMultiPolygon(self.geometry, margin, 'left')
            else:
                geometry = self.geometry

            toolData = toolModel.getCamData()

            width = self.width.toMm()

            if width < toolData["diameterTool"]:
                width = toolData["diameterTool"]

            _, innergeometry = ShapelyUtils.offsetMultiPolygon(geometry, width, 'left')
            self.preview_geometry = geometry.difference(innergeometry)

            if self.preview_geometry.geom_type == 'Polygon':
                self.preview_geometry = shapely.geometry.MultiPolygon([self.preview_geometry])

        self.geometry_svg_paths = []
         
        # should have 2 paths, one inner, one outer -> show the "ring"
        for poly in self.preview_geometry.geoms:
            geometry_svg_path = SvgPath.fromShapelyPolygon("pycut_geometry_pocket", poly)
            self.geometry_svg_paths.append(geometry_svg_path)
        
    def calculate_preview_geometry_outside(self, toolModel: ToolModel):
        '''
        '''
        # shapely: first the outer, then the inner hole
        toolData = toolModel.getCamData()

        if self.geometry is not None:
            width = self.width.toMm()
            if width < toolData["diameterTool"]:
                width = toolData["diameterTool"]

            margin = self.margin.toMm()
            margin_plus_width = margin + width

            # 'right' in 'inside', and 'left' is 'outside'  hopefully
            _, geometry_outer = ShapelyUtils.offsetMultiPolygon(self.geometry, margin_plus_width, 'right', resolution=16, join_style=1, mitre_limit=5)
            _, geometry_inner = ShapelyUtils.offsetMultiPolygon(self.geometry, margin           , 'right', resolution=16, join_style=1, mitre_limit=5)
            
            self.preview_geometry = geometry_outer.difference(geometry_inner)
            self.preview_geometry = shapely.geometry.polygon.orient(self.preview_geometry) # check if necessary!

            if self.preview_geometry.geom_type == 'Polygon':
                self.preview_geometry = shapely.geometry.MultiPolygon([self.preview_geometry])

        self.geometry_svg_paths = []
         
        # should have 2 paths, one inner, one outer -> show the "ring"
        for poly in self.preview_geometry.geoms:
            geometry_svg_path = SvgPath.fromShapelyPolygon("pycut_geometry_pocket", poly)
            self.geometry_svg_paths.append(geometry_svg_path)

    def calculate_preview_geometry_engrave(self):
        '''
        '''
        for poly in self.geometry.geoms:
            svg_path = SvgPath.fromShapelyPolygon("pycut_geometry_engrave", poly)
            self.geometry_svg_paths.append(svg_path)

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

        offset = margin.toMm()

        #if cam_op == "Outside" :
        #    #direction = "outer2inner"
        #    direction = "inner2outer"
        #    if direction == "outer2inner":
        #        # start from the outer ring and cam in the inside dir
        #        width = self.width.toMm()
        #        if width < toolData["diameterTool"]:
        #            width = toolData["diameterTool"]
        #        offset += width
        #    else:
        #        # start from the inner ring and cam in the outside dir
        #        pass 

        if cam_op != "Engrave" :
            # 'left' for Inside OR pocket, 'right' for Outside
            _, geometry = ShapelyUtils.offsetMultiPolygon(geometry, offset, 'right' if cam_op == 'Outside' else 'left', ginterior = True)

        if cam_op == "Pocket":
            self.cam_paths = cam.pocket(geometry, toolData["diameterTool"], 1 - toolData["stepover"], direction == "Climb")
        elif cam_op == "Inside" or cam_op == "Outside":
            width = width.toMm()
            if width < toolData["diameterTool"]:
                width = toolData["diameterTool"]
            self.cam_paths = cam.outline(geometry, toolData["diameterTool"], cam_op == "Inside", width, 1 - toolData["stepover"], direction == "Climb")
        elif cam_op == "Engrave":
            self.cam_paths = cam.engrave(geometry, direction == "Climb")

        for cam_path in self.cam_paths:
            svg_path = SvgPath.fromShapelyLineString("pycut_toolpath", cam_path.path, cam_path.safeToClose)
            self.cam_paths_svg_paths.append(svg_path)

class JobModel:
    '''
    '''
    def __init__(self,
            svg_viewer: SvgViewer,
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
                    for point in toolPath.coords:
                        if not foundFirst:
                            minX = point[0]
                            maxX = point[0]
                            minY = point[1]
                            maxY = point[1]
                            foundFirst = True
                        else:
                            minX = min(minX, point[0])
                            minY = min(minY, point[1])
                            maxX = max(maxX, point[0])
                            maxY = max(maxY, point[1])

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

        self.flipXY = self.gcodeModel.flipXY

        self.gcode = ""

    @property
    def minX(self):
        '''
        only display value after gcode generation
        '''
        if self.flipXY == False:
            # normal case
            return self.unitConverter.fromMm(self.job.minX) + self.offsetX
        else:
            # as flipped: is -maxY when "no flip"
            return self.unitConverter.fromMm(self.job.minY) - self.offsetY

    @property
    def maxX(self):
        '''
        only display value after gcode generation
        '''
        if self.flipXY == False:
            # normal case
            return self.unitConverter.fromMm(self.job.maxX) + self.offsetX
        else:
            # as flipped: is -minY when "no flip"
            return self.unitConverter.fromMm(self.job.maxY) - self.offsetY

    @property
    def minY(self):
        '''
        only display value after gcode generation
        '''
        if self.flipXY == False:
            # normal case
            return  -self.unitConverter.fromMm(self.job.maxY) + self.offsetY
        else:
            # as flipped: is minX when "no flip"
            return self.unitConverter.fromMm(self.job.minX) + self.offsetX

    @property
    def maxY(self):
        '''
        only display value after gcode generation
        '''
        if self.flipXY == False:
            # normal case
            return  -self.unitConverter.fromMm(self.job.minY) + self.offsetY
        else:
            # as flipped: is maxX when "no flip"
            return self.unitConverter.fromMm(self.job.maxX) + self.offsetX

    def generateGcode(self):
        if self.gcodeModel.gcodeZero == GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL:
            self.generateGcode_zeroTopLeftOfMaterial()
        elif self.gcodeModel.gcodeZero == GcodeModel.ZERO_LOWER_LEFT_OF_MATERIAL:
            self.generateGcode_zeroLowerLeftOfMaterial()
        elif self.gcodeModel.gcodeZero == GcodeModel.ZERO_LOWER_LEFT_OF_OP:
            self.generateGcode_zeroLowerLeftOfOp()
        elif self.gcodeModel.gcodeZero == GcodeModel.ZERO_CENTER_OF_OP:
            self.generateGcode_zeroCenterOfOp()

    def generateGcode_zeroTopLeftOfMaterial(self):
        self.offsetX = self.unitConverter.fromMm(0)
        self.offsetY = self.unitConverter.fromMm(0)
        self.generateGcodeAction()

    def generateGcode_zeroLowerLeftOfMaterial(self):
        self.offsetX = self.unitConverter.fromMm(0)
        self.offsetY = self.unitConverter.fromMm(self.materialModel.sizeY)
        self.generateGcodeAction()

    def generateGcode_zeroLowerLeftOfOp(self):
        self.offsetX = - self.unitConverter.fromMm(self.job.minX)
        self.offsetY = - self.unitConverter.fromMm(-self.job.maxY)
        self.generateGcodeAction()

    def generateGcode_zeroCenterOfOp(self):
        self.offsetX = - self.unitConverter.fromMm((self.job.minX + self.job.maxX) / 2)
        self.offsetY = - self.unitConverter.fromMm(-(self.job.minY + self.job.maxY) / 2)
        self.generateGcodeAction()

    def setXOffset(self, value: float):
        self.offsetX = value
        self.generateGcodeAction()

    def setYOffset(self, value: float):
        self.offsetY = value
        self.generateGcodeAction()

    def setFlipXY(self, value: float):
        self.flipXY = value
        self.generateGcodeAction()

    def generateGcodeAction(self):
        cnc_ops: List['CncOp'] = []
        for cnc_op in self.job.operations:
            if cnc_op.enabled:
                if len(cnc_op.cam_paths) > 0:
                    cnc_ops.append(cnc_op)

        if len(cnc_ops) == 0:
            return

        safeZ = self.unitConverter.fromMm(self.materialModel.matZSafeMove.toMm())
        rapidRate = int(self.unitConverter.fromMm(self.toolModel.rapidRate.toMm()))
        plungeRate = int(self.unitConverter.fromMm(self.toolModel.plungeRate.toMm()))
        cutRate = int(self.unitConverter.fromMm(self.toolModel.cutRate.toMm()))
        passDepth = self.unitConverter.fromMm(self.toolModel.passDepth.toMm())
        topZ = self.unitConverter.fromMm(self.materialModel.matTopZ.toMm())
        tabHeight = self.unitConverter.fromMm(self.tabsModel.height.toMm())

        #if self.units == "inch":
        #    scale = 1.0
        #else:
        #    scale = 25.4
        scale = 1

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
            cutDepth = self.unitConverter.fromMm(cnc_op.cutDepth.toMm())
            botZ = ValWithUnit(topZ - cutDepth, self.units)
            tabZ = self.unitConverter.fromMm(topZ.toMm() - cutDepth.toMm() + tabHeight.toMm())

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
                "offsetX":        self.offsetX,
                "offsetY":        self.offsetY,
                "decimal":        4,
                "topZ":           topZ,
                "botZ":           botZ,
                "safeZ":          safeZ,
                "passDepth":      passDepth,
                "plungeFeed":     plungeRate,
                "retractFeed":    rapidRate,
                "cutFeed":        cutRate,
                "rapidFeed":      rapidRate,
                "tabs":           self.tabsModel.tabs,
                "tabZ":           tabZ,
                "flipXY":         self.flipXY
            })

        if self.gcodeModel.spindleControl:
            gcode += f"\r\n; Stop the spindle\r\n"
            gcode += f"M5 \r\n"

        if self.gcodeModel.returnTo00:
            gcode += f"\r\n; Return to 0,0\r\n"
            gcode += f"G0 X0 Y0 F{rapidRate}\r\n"

        if self.gcodeModel.programEnd:
            gcode += f"\r\n; Program End\r\n"
            gcode += f"M2 \r\n"

        self.gcode = gcode
        self.job.gcode = gcode

