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
import shapely.ops

from shapely_utils import ShapelyUtils
from shapely_svgpath_io import SvgPath
from shapely_matplotlib import MatplotLibUtils

from svgviewer import SvgViewer

from shapely_cam import cam
from shapely_cam import CamPath

from val_with_unit import ValWithUnit


class UnitConverter:
    """ """

    def __init__(self, units: str):
        """ """
        self.units = units

    def to_inch(self, x: float):
        """
        Convert x from the current unit to inch
        """
        if self.units == "inch":
            return x
        else:
            return x / 25.4

    def from_inch(self, x: float):
        """
        Convert x from inch to the current unit
        """
        if self.units == "inch":
            return ValWithUnit(x, "inch")
        else:
            return ValWithUnit(x * 25.4, "mm")

    def from_mm(self, x: float):
        """
        Convert x from mm to the current unit
        """
        if self.units == "inch":
            return ValWithUnit(x / 25.4, "inch")
        else:
            return ValWithUnit(x, "mm")


class GcodeModel:
    """ """

    ZERO_TOP_LEFT_OF_MATERIAL = 1
    ZERO_LOWER_LEFT_OF_MATERIAL = 2
    ZERO_LOWER_LEFT_OF_OP = 3
    ZERO_CENTER_OF_OP = 4

    XYRef = {
        ZERO_TOP_LEFT_OF_MATERIAL: "ZERO_TOP_LEFT_OF_MATERIAL",
        ZERO_LOWER_LEFT_OF_MATERIAL: "ZERO_LOWER_LEFT_OF_MATERIAL",
        ZERO_LOWER_LEFT_OF_OP: "ZERO_LOWER_LEFT_OF_OP",
        ZERO_CENTER_OF_OP: "ZERO_CENTER_OF_OP",
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
    """ """

    # FIXME : read from the size file
    size_x = 100.0
    size_y = 100.0

    def __init__(self):
        self.pxPerInch = 96


class ToolModel:
    """ """

    def __init__(self):
        self.units = "inch"
        self.diameter = ValWithUnit(0.125, self.units)
        self.angle = 180
        self.passdepth = ValWithUnit(0.125, self.units)
        self.overlap = 0.5
        self.rapidRate = ValWithUnit(100, self.units)
        self.plungeRate = ValWithUnit(5, self.units)
        self.cutRate = ValWithUnit(40, self.units)

    def get_cam_data(self):
        """
        convert to the gcode units FIXME actual per default mm
        """
        result = {
            "diameterTool": self.diameter.to_mm(),
            "passdepth": self.passdepth.to_mm(),
            "overlap": self.overlap,
        }

        return result


class MaterialModel:
    """ """

    def __init__(self):
        self.mat_units = "inch"
        self.mat_thickness = ValWithUnit(1.0, self.mat_units)
        self.mat_z_origin = "Top"
        self.mat_clearance = ValWithUnit(0.1, self.mat_units)

        # from the svg size, the dimension of the material in mm
        self.size_x = ValWithUnit(SvgModel.size_x, "mm")  # default
        self.size_y = ValWithUnit(SvgModel.size_x, "mm")  # default

    def set_material_size_x(self, x: ValWithUnit):
        self.size_x = x.to_mm()

    def set_material_size_y(self, y: ValWithUnit):
        self.size_y = y.to_mm()

    @property
    def matBotZ(self):
        if self.mat_z_origin == "Bottom":
            return 0
        else:
            return -self.mat_thickness

    @property
    def matTopZ(self):
        if self.mat_z_origin == "Top":
            return ValWithUnit(0, self.mat_units)
        else:
            return self.mat_thickness

    @property
    def matZSafeMove(self):
        if self.mat_z_origin == "Top":
            return self.mat_clearance
        else:
            return self.mat_thickness + self.mat_clearance


class Tab:
    """
    a Tab is defined by a circle with position (x,y)
    and height from the buttom of the material

    it's svg_path will be intersected with the toolpaths
    in case of 'Inside','Outside' and 'Engrave' - but ignored
    for 'Pocket'
    """

    height = ValWithUnit(2.0, "mm")

    def __init__(self, tab: Dict[str, Any]):
        """ """
        self.center = tab["center"]
        self.radius = tab["radius"]

        self.enabled = tab["enabled"]

        self.svg_path = SvgPath.from_circle_def(self.center, self.radius)

    @classmethod
    def set_height(cls, heigth: float, units: str):
        """
        from the TabsModel, common for all the tabs
        """
        cls.height = ValWithUnit(heigth, units)

    def pos_inside_tab(self, x: float, y: float, z: float, op_cut_depth: float):
        """
        ---------------------- 0

                          ---- z is negativ
         material
        ---------------------- height = 2
        ---------------------- op_cut_depth = 10

        """
        if op_cut_depth + z > self.height:
            # still above the tab
            return False

        dx = self.center.x - x
        dy = self.center.y - y

        return dx * dx + dy * dy <= self.radius * self.radius


class TabsModel:
    """ """

    def __init__(self, tabs: List[Dict[str, any]]):
        self.tabs: List[Dict[str, any]] = tabs

        self.units = "mm"  # default
        self.height = ValWithUnit(2.0, self.units)  # default

        Tab.set_height(self.height, self.units)

    def set_height(self, height: float, units: str):
        self.units = units
        self.height = ValWithUnit(height, units)

        Tab.set_height(self.height)

    def has_tabs(self):
        return len(self.tabs) > 0

    def pos_in_tab(self, x: float, y: float, z: float, op_cut_depth: float):
        for tab in self.tabs:
            if tab.pos_inside_tab(x, y, z, op_cut_depth):
                return True

        return False


class CncOp:
    """ """

    def __init__(self, operation: Dict[str, Any]):
        self.units: str = operation["units"]
        self.name: List[str] = operation["name"]
        self.paths: List[str] = operation["paths"]
        self.combinaison: str = operation["combinaison"]
        self.ramp_plunge = operation["ramp_plunge"]
        self.cam_op = operation["type"]
        self.direction = operation["direction"]
        self.cut_depth = ValWithUnit(operation["cut_depth"], self.units)

        self.enabled = operation.get("enabled", False)

        if "margin" in operation:
            self.margin = ValWithUnit(operation["margin"], self.units)
        else:
            self.margin = None

        if "width" in operation:
            self.width = ValWithUnit(operation["width"], self.units)
        else:
            self.width = None

        # the input
        self.svg_paths: List[SvgPath] = []  # to fill at "setup"
        # and the resulting svg paths from the combinaison, to be displayed in the svg viewer
        self.geometry_svg_paths: List[SvgPath] = []

        # the resulting paths from the op type & combinaison setting + enabled svg paths
        self.geometry: shapely.geometry.MultiPolygon | shapely.geometry.MultiLineString | shapely.geometry.MultiPoint = (
            None
        )

        # the resulting tool paths
        self.cam_paths: List[CamPath] = []
        # and the resulting tool paths, to be displayed in the svg viewer
        self.cam_paths_svg_paths: List[SvgPath] = []

    def put_value(self, attr: str, value: Any):
        """ """
        setattr(self, attr, value)

    def __str__(self):
        """ """
        return "op: %s %s [%f] %s" % (
            self.name,
            self.cam_op,
            self.cut_depth,
            self.enabled,
        )

    def setup(self, svg_viewer: SvgViewer):
        """ """
        self.svg_paths = [
            svg_viewer.svg_shapes[svg_path_id] for svg_path_id in self.paths
        ]

    def is_closed_paths_op(self) -> bool:
        """ """
        for svgpath in self.svg_paths:
            if not svgpath.closed:
                return False

        return True

    def is_opened_paths_op(self) -> bool:
        """ """
        for svgpath in self.svg_paths:
            if svgpath.closed:
                return False

        return True

    def combine_as_drill_or_peck(self):
        """
        generate the combinaison of the selected paths

        the generated geometry is a MultiPoint
        """
        shapely_points: List[shapely.geometry.Point] = []

        for svgpath in self.svg_paths:
            # consider only circles
            if svgpath.shape_tag == "circle":
                shapely_point = svgpath.import_as_point()
                shapely_points.append(shapely_point)

        self.geometry = shapely.geometry.MultiPoint(shapely_points)

    def combine(self) -> None:
        """
        generate the combinaison of the selected paths

        the generated geometry is a MultiPolygon
        """
        self.shapely_polygons: List[shapely.geometry.Polygon] = []
        self.shapely_lines: List[shapely.geometry.LineString] = []

        for svg_path in self.svg_paths:
            shapely_polygons = svg_path.import_as_polygons_list()
            self.shapely_polygons += shapely_polygons

        if len(self.shapely_polygons) == 0:
            return

        if len(self.shapely_polygons) == 1:
            self.geometry = shapely.geometry.MultiPolygon(self.shapely_polygons)
            return

        o = self.shapely_polygons[0]
        other = shapely.ops.unary_union(self.shapely_polygons[1:])

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
        if self.geometry.geom_type == "Polygon":
            # fix orientation
            self.geometry = ShapelyUtils.reorder_poly_points(self.geometry)

            self.geometry = shapely.geometry.polygon.orient(self.geometry)
            self.geometry = shapely.geometry.MultiPolygon([self.geometry])
        else:
            # fix orientation
            fixed_polys = []
            for poly in self.geometry.geoms:
                if not poly.geom_type == "Polygon":
                    continue
                # fix - do not start a poly from a convex corner
                poly = ShapelyUtils.reorder_poly_points(poly)

                fixed_poly = shapely.geometry.polygon.orient(poly)
                fixed_polys.append(fixed_poly)
            self.geometry = shapely.geometry.MultiPolygon(fixed_polys)

    def combine_opened_paths(self) -> None:
        """
        generate the combinaison of the selected paths

        the generated geometry is a MultiPolygon
        """
        self.shapely_polygons: List[shapely.geometry.Polygon] = []
        self.shapely_lines: List[shapely.geometry.LineString] = []

        for svg_path in self.svg_paths:
            shapely_lines = svg_path.import_as_lines_list()
            self.shapely_lines += shapely_lines

        if len(self.shapely_lines) == 1:
            self.geometry = shapely.geometry.MultiLineString(self.shapely_lines)
            return

        o = self.shapely_lines[0]
        other = shapely.ops.unary_union(self.shapely_lines[1:])

        if self.combinaison == "Union":
            geometry = o.union(other)
        if self.combinaison == "Intersection":
            geometry = o.intersection(other)
        if self.combinaison == "Difference":
            geometry = o.difference(other)
        if self.combinaison == "Xor":
            geometry = o.symmetric_difference(other)

        self.geometry = geometry

    def calculate_geometry(self, tool_model: ToolModel):
        """ """
        if self.is_closed_paths_op():
            if (
                self.cam_op == "Pocket"
                or self.cam_op == "Inside"
                or self.cam_op == "Outside"
                or self.cam_op == "Engrave"
            ):
                self.combine()
            if self.cam_op == "Drill" or self.cam_op == "Peck":
                self.combine_as_drill_or_peck()

            if self.cam_op == "Pocket":
                self.calculate_preview_geometry_pocket()
            elif self.cam_op == "Inside":
                self.calculate_preview_geometry_inside(tool_model)
            elif self.cam_op == "Outside":
                self.calculate_preview_geometry_outside(tool_model)
            elif self.cam_op == "Engrave":
                self.calculate_preview_geometry_engrave()
            elif self.cam_op == "Drill" or self.cam_op == "Peck":
                self.calculate_preview_geometry_drill(tool_model)

        if self.is_opened_paths_op():
            self.combine_opened_paths()

            if self.cam_op == "Engrave":
                self.calculate_opened_paths_preview_geometry_engrave()
            elif self.cam_op == "Inside":
                self.calculate_opened_paths_preview_geometry_inside(tool_model)
            elif self.cam_op == "Outside":
                self.calculate_opened_paths_preview_geometry_outside(tool_model)

    def calculate_opened_paths_preview_geometry_engrave(self):
        """ """
        for line in self.geometry.geoms:
            svg_path = SvgPath.from_shapely_linestring(
                "pycut_geometry_engrave", line, False
            )
            self.geometry_svg_paths.append(svg_path)

    def calculate_opened_paths_preview_geometry_inside(self, tool_model: ToolModel):
        """ """
        if self.geometry is not None:
            margin = self.margin.to_mm()

            if margin != 0:
                self.preview_geometry = ShapelyUtils.offsetMultiLine(
                    self.geometry, margin, "left"
                )
            else:
                self.preview_geometry = self.geometry

            if self.preview_geometry.geom_type == "LineString":
                self.preview_geometry = shapely.geometry.MultiLineString(
                    [self.preview_geometry]
                )

        self.geometry_svg_paths = []

        for line in self.preview_geometry.geoms:
            geometry_svg_path = SvgPath.from_shapely_linestring(
                "pycut_geometry_inside", line, False
            )
            self.geometry_svg_paths.append(geometry_svg_path)

    def calculate_opened_paths_preview_geometry_outside(self, tool_model: ToolModel):
        """ """
        if self.geometry is not None:
            margin = self.margin.to_mm()

            if margin != 0:
                self.preview_geometry = ShapelyUtils.offsetMultiLine(
                    self.geometry, margin, "right"
                )
            else:
                self.preview_geometry = self.geometry

            # 'right' in 'inside', and 'left' is 'outside'  hopefully
            if self.preview_geometry.geom_type == "LineString":
                self.preview_geometry = shapely.geometry.MultiLineString(
                    [self.preview_geometry]
                )

        self.geometry_svg_paths = []

        # should have 2 paths, one inner, one outer -> show the "ring"
        for line in self.preview_geometry.geoms:
            geometry_svg_path = SvgPath.from_shapely_linestring(
                "pycut_geometry_outside", line, False
            )
            self.geometry_svg_paths.append(geometry_svg_path)

    def calculate_preview_geometry_drill(self, tool_model: ToolModel):
        """
        as a pocket of diameter exactly cutter_dia
        """
        if self.geometry is not None:
            shapely_polygons: List[shapely.geometry.Polygon] = []
            for pt in self.geometry.geoms:
                center = pt.coords[0]
                radius = tool_model.diameter / 2.0

                svgpath = SvgPath.from_circle_def(center, radius)
                shapely_polygons += svgpath.import_as_polygons_list()

            self.preview_geometry = shapely.geometry.MultiPolygon(shapely_polygons)

            for poly in self.preview_geometry.geoms:
                geometry_svg_path = SvgPath.from_shapely_polygon(
                    "pycut_geometry_drill", poly
                )
                self.geometry_svg_paths.append(geometry_svg_path)

    def calculate_preview_geometry_pocket(self):
        """ """
        if self.geometry is not None:
            offset = self.margin.to_mm()

            # 'left' in 'inside', and 'right' is 'outside'
            self.geometry = ShapelyUtils.orientMultiPolygon(self.geometry)
            self.preview_geometry = ShapelyUtils.offsetMultiPolygon(
                self.geometry, offset, "left", consider_interiors_offsets=True
            )

            MatplotLibUtils.MatplotlibDisplay("preview pocket", self.preview_geometry)

            self.preview_geometry = ShapelyUtils.orientMultiPolygon(
                self.preview_geometry
            )

            MatplotLibUtils.MatplotlibDisplay(
                "preview pocket - oriented", self.preview_geometry
            )

            self.geometry_svg_paths = []

            for poly in self.preview_geometry.geoms:
                geometry_svg_path = SvgPath.from_shapely_polygon(
                    "pycut_geometry_pocket", poly
                )
                self.geometry_svg_paths.append(geometry_svg_path)

    def calculate_preview_geometry_inside(self, tool_model: ToolModel):
        """ """
        toolData = tool_model.get_cam_data()

        if self.geometry is not None:
            margin = self.margin.to_mm()

            width = self.width.to_mm()

            if width < toolData["diameterTool"]:
                width = toolData["diameterTool"]

            if margin != 0:
                geometry = ShapelyUtils.offsetMultiPolygon(
                    self.geometry, margin, "left"
                )
            else:
                geometry = self.geometry

            innergeometry = ShapelyUtils.offsetMultiPolygon(geometry, width, "left")
            self.preview_geometry = geometry.difference(innergeometry)

            if self.preview_geometry.geom_type == "Polygon":
                self.preview_geometry = shapely.geometry.MultiPolygon(
                    [self.preview_geometry]
                )

        self.geometry_svg_paths = []

        # should have 2 paths, one inner, one outer -> show the "ring"
        for poly in self.preview_geometry.geoms:
            geometry_svg_path = SvgPath.from_shapely_polygon(
                "pycut_geometry_pocket", poly
            )
            self.geometry_svg_paths.append(geometry_svg_path)

    def calculate_preview_geometry_outside(self, tool_model: ToolModel):
        """ """
        # shapely: first the outer, then the inner hole
        toolData = tool_model.get_cam_data()

        if self.geometry is not None:
            width = self.width.to_mm()

            if width < toolData["diameterTool"]:
                width = toolData["diameterTool"]

            margin = self.margin.to_mm()
            margin_plus_width = margin + width

            # 'right' in 'inside', and 'left' is 'outside'  hopefully
            geometry_outer = ShapelyUtils.offsetMultiPolygon(
                self.geometry,
                margin_plus_width,
                "right",
                resolution=16,
                join_style=1,
                mitre_limit=5,
            )
            geometry_inner = ShapelyUtils.offsetMultiPolygon(
                self.geometry,
                margin,
                "right",
                resolution=16,
                join_style=1,
                mitre_limit=5,
            )

            self.preview_geometry = geometry_outer.difference(geometry_inner)

            ## DEBUG
            # self.preview_geometry = geometry_outer
            ## DEBUG

            if self.preview_geometry.geom_type == "Polygon":
                self.preview_geometry = shapely.geometry.MultiPolygon(
                    [self.preview_geometry]
                )

        self.geometry_svg_paths = []

        # should have 2 paths, one inner, one outer -> show the "ring"
        for poly in self.preview_geometry.geoms:
            geometry_svg_path = SvgPath.from_shapely_polygon(
                "pycut_geometry_pocket", poly
            )
            self.geometry_svg_paths.append(geometry_svg_path)

    def calculate_preview_geometry_engrave(self):
        """ """
        for poly in self.geometry.geoms:
            svg_path = SvgPath.from_shapely_polygon("pycut_geometry_engrave", poly)
            self.geometry_svg_paths.append(svg_path)

    def calculate_toolpaths(
        self, svg_model: SvgModel, tool_model: ToolModel, material_model: MaterialModel
    ):
        """ """
        toolData = tool_model.get_cam_data()

        # name = self.name
        # ramp_plunge = self.ramp_plunge
        cam_op = self.cam_op
        direction = self.direction
        # cut_depth = self.cut_depth
        margin = self.margin
        width = self.width

        geometry = self.geometry

        offset = margin.to_mm()

        # if cam_op == "Outside" :
        #    #direction = "outer2inner"
        #    direction = "inner2outer"
        #    if direction == "outer2inner":
        #        # start from the outer ring and cam in the inside dir
        #        width = self.width.to_mm()
        #        if width < toolData["diameterTool"]:
        #            width = toolData["diameterTool"]
        #        offset += width
        #    else:
        #        # start from the inner ring and cam in the outside dir
        #        pass

        if self.geometry.geom_type == "MultiPoint":
            if cam_op == "Drill":
                self.cam_paths = cam.drill(geometry, toolData["diameterTool"])
            elif cam_op == "Peck":
                self.cam_paths = cam.peck(geometry, toolData["diameterTool"])

        if self.geometry.geom_type == "MultiPolygon":
            if cam_op != "Engrave":
                # 'left' for Inside OR pocket, 'right' for Outside
                geometry = ShapelyUtils.offsetMultiPolygon(
                    geometry,
                    offset,
                    "right" if cam_op == "Outside" else "left",
                    consider_interiors_offsets=True,
                )

            if cam_op == "Pocket":
                self.cam_paths = cam.pocket(
                    geometry,
                    toolData["diameterTool"],
                    toolData["overlap"],
                    direction == "Climb",
                )
            elif cam_op == "Inside" or cam_op == "Outside":
                width = width.to_mm()
                if width < toolData["diameterTool"]:
                    width = toolData["diameterTool"]
                self.cam_paths = cam.outline(
                    geometry,
                    toolData["diameterTool"],
                    cam_op == "Inside",
                    width,
                    toolData["overlap"],
                    direction == "Climb",
                )
            elif cam_op == "Engrave":
                self.cam_paths = cam.engrave(geometry, direction == "Climb")

        if self.geometry.geom_type == "MultiLineString":
            if cam_op == "Engrave":
                self.cam_paths = cam.engrave_opened_paths(
                    geometry, direction == "Climb"
                )
            elif cam_op == "Inside" or cam_op == "Outside":
                geometry = self.preview_geometry

                width = width.to_mm()
                if width < toolData["diameterTool"]:
                    width = toolData["diameterTool"]
                self.cam_paths = cam.outline_opened_paths(
                    geometry,
                    toolData["diameterTool"],
                    cam_op == "Inside",
                    width,
                    toolData["overlap"],
                    direction == "Climb",
                )

        # -------------------------------------------------------------------------------------

        for cam_path in self.cam_paths:
            svg_path = SvgPath.from_shapely_linestring(
                "pycut_toolpath", cam_path.path, cam_path.safe_to_close
            )
            self.cam_paths_svg_paths.append(svg_path)


class JobModel:
    """ """

    def __init__(
        self,
        svg_viewer: SvgViewer,
        cnc_ops: List[CncOp],
        material_model: MaterialModel,
        svg_model: SvgModel,
        tool_model: ToolModel,
        tabs_model: TabsModel,
        gcode_model: GcodeModel,
    ):
        self.svg_viewer = svg_viewer

        self.operations = cnc_ops

        self.svg_model = svg_model
        self.material_model = material_model
        self.tool_model = tool_model
        self.tabs_model = tabs_model
        self.gcode_model = gcode_model

        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0

        self.calculate_operation_cam_paths()
        self.find_min_max()

        self.gcode = ""

    def calculate_operation_cam_paths(self):
        for op in self.operations:
            if op.enabled:
                op.setup(self.svg_viewer)
                op.calculate_geometry(self.tool_model)
                op.calculate_toolpaths(
                    self.svg_model, self.tool_model, self.material_model
                )

    def find_min_max(self):
        minX = 0
        maxX = 0
        minY = 0
        maxY = 0
        foundFirst = False

        for op in self.operations:
            if op.enabled and op.cam_paths != None:
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
    """ """

    def __init__(self, job: JobModel):
        self.job = job

        self.material_model = job.material_model
        self.tool_model = job.tool_model
        self.tabs_model = job.tabs_model
        self.gcode_model = job.gcode_model

        self.units = self.gcode_model.units
        self.unit_converter = UnitConverter(self.units)

        self.offsetX = self.gcode_model.XOffset
        self.offsetY = self.gcode_model.YOffset

        self.flipXY = self.gcode_model.flipXY

        self.gcode = ""

    @property
    def minX(self):
        """
        only display value after gcode generation
        """
        if self.flipXY == False:
            # normal case
            return self.unit_converter.from_mm(self.job.minX) + self.offsetX
        else:
            # as flipped: is -maxY when "no flip"
            return self.unit_converter.from_mm(self.job.minY) - self.offsetY

    @property
    def maxX(self):
        """
        only display value after gcode generation
        """
        if self.flipXY == False:
            # normal case
            return self.unit_converter.from_mm(self.job.maxX) + self.offsetX
        else:
            # as flipped: is -minY when "no flip"
            return self.unit_converter.from_mm(self.job.maxY) - self.offsetY

    @property
    def minY(self):
        """
        only display value after gcode generation
        """
        if self.flipXY == False:
            # normal case
            return -self.unit_converter.from_mm(self.job.maxY) + self.offsetY
        else:
            # as flipped: is minX when "no flip"
            return self.unit_converter.from_mm(self.job.minX) + self.offsetX

    @property
    def maxY(self):
        """
        only display value after gcode generation
        """
        if self.flipXY == False:
            # normal case
            return -self.unit_converter.from_mm(self.job.minY) + self.offsetY
        else:
            # as flipped: is maxX when "no flip"
            return self.unit_converter.from_mm(self.job.maxX) + self.offsetX

    def generateGcode(self):
        if self.gcode_model.gcodeZero == GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL:
            self.generateGcode_zeroTopLeftOfMaterial()
        elif self.gcode_model.gcodeZero == GcodeModel.ZERO_LOWER_LEFT_OF_MATERIAL:
            self.generateGcode_zeroLowerLeftOfMaterial()
        elif self.gcode_model.gcodeZero == GcodeModel.ZERO_LOWER_LEFT_OF_OP:
            self.generateGcode_zeroLowerLeftOfOp()
        elif self.gcode_model.gcodeZero == GcodeModel.ZERO_CENTER_OF_OP:
            self.generateGcode_zeroCenterOfOp()

    def generateGcode_zeroTopLeftOfMaterial(self):
        self.offsetX = self.unit_converter.from_mm(0)
        self.offsetY = self.unit_converter.from_mm(0)
        self.generateGcodeAction()

    def generateGcode_zeroLowerLeftOfMaterial(self):
        self.offsetX = self.unit_converter.from_mm(0)
        self.offsetY = self.unit_converter.from_mm(self.material_model.size_y)
        self.generateGcodeAction()

    def generateGcode_zeroLowerLeftOfOp(self):
        self.offsetX = -self.unit_converter.from_mm(self.job.minX)
        self.offsetY = -self.unit_converter.from_mm(-self.job.maxY)
        self.generateGcodeAction()

    def generateGcode_zeroCenterOfOp(self):
        self.offsetX = -self.unit_converter.from_mm((self.job.minX + self.job.maxX) / 2)
        self.offsetY = -self.unit_converter.from_mm(
            -(self.job.minY + self.job.maxY) / 2
        )
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
        cnc_ops: List["CncOp"] = []
        for cnc_op in self.job.operations:
            if cnc_op.enabled:
                if len(cnc_op.cam_paths) > 0:
                    cnc_ops.append(cnc_op)

        if len(cnc_ops) == 0:
            return

        safeZ = self.unit_converter.from_mm(self.material_model.matZSafeMove.to_mm())
        rapidRate = int(self.unit_converter.from_mm(self.tool_model.rapidRate.to_mm()))
        plungeRate = int(
            self.unit_converter.from_mm(self.tool_model.plungeRate.to_mm())
        )
        cutRate = int(self.unit_converter.from_mm(self.tool_model.cutRate.to_mm()))
        passdepth = self.unit_converter.from_mm(self.tool_model.passdepth.to_mm())
        toolDiameter = self.unit_converter.from_mm(self.tool_model.diameter.to_mm())
        topZ = self.unit_converter.from_mm(self.material_model.matTopZ.to_mm())
        tabHeight = self.unit_converter.from_mm(self.tabs_model.height.to_mm())
        peckZ = self.unit_converter.from_mm(1.0)

        # if self.units == "inch":
        #    scale = 1.0
        # else:
        #    scale = 25.4
        scale = 1

        gcode = []
        if self.units == "inch":
            gcode.append("G20         ; Set units to inches")
        else:
            gcode.append("G21         ; Set units to mm")
        gcode.append("G90         ; Absolute positioning")
        gcode.append(
            f"G1 {safeZ.toFixed(4)}    F{rapidRate}      ; Move to clearance level"
        )

        if self.gcode_model.spindleControl:
            gcode.append("")
            gcode.append("; Start the spindle")
            gcode.append(f"M3 S{self.gcode_model.spindleSpeed}")

        gcode.append("")
        gcode.append(";")
        gcode.append("; Tool Info")
        gcode.append(f"; Diameter:    {toolDiameter}")
        gcode.append("")

        for idx, cnc_op in enumerate(cnc_ops):
            cut_depth = self.unit_converter.from_mm(cnc_op.cut_depth.to_mm())
            botZ = ValWithUnit(topZ - cut_depth, self.units)
            tabZ = self.unit_converter.from_mm(
                topZ.to_mm() - cut_depth.to_mm() + tabHeight.to_mm()
            )

            nb_paths = len(cnc_op.cam_paths)  # in use!

            gcode.append("")
            gcode.append(";")
            gcode.append(f"; Operation:    {idx+1}")
            gcode.append(f"; Name:         {cnc_op.name}")
            gcode.append(f"; Type:         {cnc_op.cam_op}")
            gcode.append(f"; Paths:        {nb_paths}")
            gcode.append(f"; Direction:    {cnc_op.direction}")
            gcode.append(f"; Cut Depth:    {cut_depth}")
            gcode.append(f"; Pass Depth:   {passdepth}")
            gcode.append(f"; Plunge rate:  {plungeRate}")
            gcode.append(f"; Cut rate:     {cutRate}")
            gcode.append(";")
            gcode.append("")

            tabs = self.tabs_model.tabs

            if cnc_op.cam_op == "Pocket":
                # ignore tabs in pocket op
                tabs = []

            gcode.extend(
                cam.getGcode(
                    {
                        "optype": cnc_op.cam_op,
                        "paths": cnc_op.cam_paths,
                        "ramp": cnc_op.ramp_plunge,
                        "scale": scale,
                        "offsetX": self.offsetX,
                        "offsetY": self.offsetY,
                        "decimal": 4,
                        "topZ": topZ,
                        "botZ": botZ,
                        "safeZ": safeZ,
                        "passdepth": passdepth,
                        "plungeFeed": plungeRate,
                        "retractFeed": rapidRate,
                        "cutFeed": cutRate,
                        "rapidFeed": rapidRate,
                        "tabs": tabs,
                        "tabZ": tabZ,
                        "peckZ": peckZ,
                        "flipXY": self.flipXY,
                    }
                )
            )

        if self.gcode_model.spindleControl:
            gcode.append("")
            gcode.append("; Stop the spindle")
            gcode.append("M5")

        if self.gcode_model.returnTo00:
            gcode.append("")
            gcode.append("; Return to 0,0")
            gcode.append(f"G0 X0 Y0 F{rapidRate}")

        if self.gcode_model.programEnd:
            gcode.append("")
            gcode.append("; Program End")
            gcode.append("M2")

        gcode = "\n".join(gcode)

        self.gcode = gcode
        self.job.gcode = gcode
