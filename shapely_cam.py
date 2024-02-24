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

import sys
import math

from math import sqrt

from typing import List
from typing import Dict
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt
from shapely_svgpath_io import SvgPath

from val_with_unit import ValWithUnit

import shapely
import shapely.geometry
import shapely.ops

from shapely_utils import ShapelyUtils
from shapely_ext import ShapelyMultiPolygonOffset
from shapely_ext import ShapelyMultiPolygonOffsetInteriors
from shapely_matplotlib import MatplotLibUtils

PI = math.pi


class CamPath:
    """
    CamPath has this format: {
      path:               Shapely LineString
      safe_to_close:      Is it safe to close the path without retracting?
    }
    """

    def __init__(self, path: shapely.geometry.LineString, safe_to_close: bool = True):
        # shapely linestring
        self.path = path
        # is it safe to close the path without retracting?
        self.safe_to_close = safe_to_close


class cam:
    """ """

    @classmethod
    def drill(
        cls, multipoint: shapely.geometry.MultiPoint, cutter_dia: float
    ) -> List[CamPath]:
        """
        Compute paths for drill operation on Shapely multipoint
        """
        camPaths = []

        for point in multipoint.geoms:
            pt = point.coords[0]

            camPath = CamPath(shapely.geometry.Point(pt), True)
            camPaths.append(camPath)

        return camPaths

    @classmethod
    def peck(
        cls, multipoint: shapely.geometry.MultiPoint, cutter_dia: float
    ) -> List[CamPath]:
        """
        Compute paths for peck operation on Shapely multipoint
        """
        camPaths = []

        for point in multipoint.geoms:
            pt = point.coords[0]

            camPath = CamPath(shapely.geometry.Point(pt), False)
            camPaths.append(camPath)

        return camPaths

    @classmethod
    def helix(
        cls,
        multipoint: shapely.geometry.MultiPoint,
        cutter_dia: float,
    ) -> List[CamPath]:
        """
        Only for circles, ellipses and rectangles !

        It will be performed from the center of the circle/ellipse/rectangle

        The helix drills down until the cut depth.
        At each revolution, an amount of "helix_revolution_depth" is cut in the z direction.

        This means, given the cut rate and the helix diameter, the helix plunge rate is calculated
        """
        camPaths = []

        for point in multipoint.geoms:
            pt = point.coords[0]

            camPath = CamPath(shapely.geometry.Point(pt), False)
            camPaths.append(camPath)

        return camPaths

    @classmethod
    def pocket(
        cls,
        multipoly: shapely.geometry.MultiPolygon,
        cutter_dia: float,
        overlap: float,
        climb: bool,
    ) -> List[CamPath]:
        """
        Compute paths for pocket operation on Shapely multipolygon.

        Returns array of CamPath.

        cutter_dia is in "UserUnit" units.
        overlap is in the range [0, 1).
        """
        pc = PocketCalculator(multipoly, cutter_dia, overlap, climb)
        pc.pocket()
        return pc.cam_paths

    @classmethod
    def spirale_pocket(
        cls,
        svgpaths,
        multipoly: shapely.geometry.MultiPolygon,
        cutter_dia: float,
        overlap: float,
        climb: bool,
    ) -> List[CamPath]:
        """
        Compute paths for pocket operation on Shapely multipolygon.

        Returns array of CamPath.

        cutter_dia is in "UserUnit" units.
        overlap is in the range [0, 1).
        """
        pc = SpiralePocketCalculator(svgpaths, multipoly, cutter_dia, overlap, climb)
        pc.pocket()
        return pc.cam_paths

    @classmethod
    def outline(
        cls,
        geometry: shapely.geometry.MultiPolygon,
        cutter_dia: float,
        is_inside: bool,
        width: float,
        overlap: float,
        climb: bool,
    ) -> List[CamPath]:
        """
        Compute paths for outline operation on Shapely geometry "MultiPolygon".

        Returns array of CamPath.

        cutter_dia and width are in Shapely units.
        overlap is in the  range [0, 1).
        """
        # use lines, not polygons
        multiline = ShapelyUtils.multipoly_exteriors_to_multiline(geometry)

        currentWidth = cutter_dia
        allPaths: List[shapely.geometry.LineString] = []
        eachWidth = cutter_dia * (1 - overlap)

        if is_inside:
            # because we always start from the outer ring -> we go "inside"
            current = ShapelyUtils.offset_multiline(multiline, cutter_dia / 2, "left")
            offset = ShapelyUtils.offset_multiline(
                multiline, width - cutter_dia / 2, "left"
            )
            # bounds = ShapelyUtils.diff(current, offset)
            bounds = current
            eachOffset = eachWidth
            needReverse = climb
        else:
            direction = "inner2outer"
            # direction = "outer2inner"

            if direction == "inner2outer":
                # because we always start from the inner ring -> we go "outside"
                current = ShapelyUtils.offset_multiline(
                    multiline, cutter_dia / 2, "right"
                )
                offset = ShapelyUtils.offset_multiline(
                    multiline, width - cutter_dia / 2, "right"
                )
                # bounds = ShapelyUtils.diff(current, offset)
                bounds = current
            else:
                # because we always start from the outer ring -> we go "inside"
                current = ShapelyUtils.offset_multiline(
                    multiline, cutter_dia / 2, "left"
                )
                offset = ShapelyUtils.offset_multiline(
                    multiline, width - cutter_dia / 2, "left"
                )
                # bounds = ShapelyUtils.diff(current, offset)
                bounds = current

            eachOffset = eachWidth
            needReverse = not climb

            # TEST
            # allPaths = [p for p in current.geoms]

        while True and currentWidth <= width:
            if needReverse:
                reversed = []
                for path in current.geoms:
                    coords = list(
                        path.coords
                    )  # is a tuple!  JSCUT current reversed in place
                    coords.reverse()
                    reversed.append(shapely.geometry.LineString(coords))
                allPaths = (
                    reversed + allPaths
                )  # JSCUT: allPaths = current.concat(allPaths)
            else:
                allPaths = [
                    p for p in current.geoms
                ] + allPaths  # JSCUT: allPaths = current.concat(allPaths)

            nextWidth = currentWidth + eachWidth
            if nextWidth > width and (width - currentWidth) > 0:
                # >>> XAM fix
                last_delta = width - currentWidth
                # <<< XAM fix
                current = ShapelyUtils.offset_multiline(current, last_delta, "left")
                if current:
                    current = ShapelyUtils.simplify_multiline(current, 0.01)

                if current:
                    if needReverse:
                        reversed = []
                        for path in current.geoms:
                            coords = list(
                                path.coords
                            )  # is a tuple!  JSCUT current reversed in place
                            coords.reverse()
                            reversed.append(shapely.geometry.LineString(coords))
                        allPaths = (
                            reversed + allPaths
                        )  # JSCUT: allPaths = current.concat(allPaths)
                    else:
                        allPaths = [
                            p for p in current.geoms
                        ] + allPaths  # JSCUT: allPaths = current.concat(allPaths)
                    break

            currentWidth = nextWidth

            if not current:
                break

            current = ShapelyUtils.offset_multiline(
                current, eachOffset, "left", resolution=16
            )
            if current:
                current = ShapelyUtils.simplify_multiline(current, 0.01)
                print("--- next toolpath")
            else:
                break

        if len(allPaths) == 0:
            # no possible paths! TODO . inform user
            return []

        # merge_paths need MultiPolygon
        bounds = ShapelyUtils.multiline_to_multipoly(bounds)

        return cls.merge_paths(bounds, allPaths)

    @classmethod
    def outline_opened_paths(
        cls,
        geometry: shapely.geometry.MultiLineString,
        cutter_dia: float,
        is_inside: bool,
        width: float,
        overlap: float,
        climb: bool,
    ) -> List[CamPath]:
        """
        Compute paths for outline operation on Shapely geometry "MultiLineString".

        Returns array of CamPath.

        cutter_dia and width are in Shapely units.
        overlap is in the  range [0, 1).
        """
        # use lines, not polygons
        multiline = geometry

        currentWidth = cutter_dia
        allPaths: List[shapely.geometry.LineString] = []
        eachWidth = cutter_dia * (1 - overlap)

        if is_inside:
            # because we always start from the outer ring -> we go "inside"
            current = ShapelyUtils.offset_multiline(multiline, 0.0, "left")
            offset = ShapelyUtils.offset_multiline(multiline, width - 0.0, "left")
            # bounds = ShapelyUtils.diff(current, offset)
            bounds = current
            eachOffset = eachWidth
            needReverse = climb
        else:
            direction = "inner2outer"
            # direction = "outer2inner"

            if direction == "inner2outer":
                # because we always start from the inner ring -> we go "outside"
                current = ShapelyUtils.offset_multiline(multiline, 0.0, "right")
                offset = ShapelyUtils.offset_multiline(multiline, width - 0.0, "right")
                # bounds = ShapelyUtils.diff(current, offset)
                bounds = current
            else:
                # because we always start from the outer ring -> we go "inside"
                current = ShapelyUtils.offset_multiline(multiline, 0.0, "left")
                offset = ShapelyUtils.offset_multiline(multiline, width - 0.0, "left")
                # bounds = ShapelyUtils.diff(current, offset)
                bounds = current

            eachOffset = eachWidth
            needReverse = not climb

            # TEST
            # allPaths = [p for p in current.geoms]

        while True and currentWidth <= width:
            if needReverse:
                reversed = []
                for path in current.geoms:
                    coords = list(
                        path.coords
                    )  # is a tuple!  JSCUT current reversed in place
                    coords.reverse()
                    reversed.append(shapely.geometry.LineString(coords))
                allPaths = (
                    reversed + allPaths
                )  # JSCUT: allPaths = current.concat(allPaths)
            else:
                allPaths = [
                    p for p in current.geoms
                ] + allPaths  # JSCUT: allPaths = current.concat(allPaths)

            nextWidth = currentWidth + eachWidth
            if nextWidth > width and (width - currentWidth) > 0:
                # >>> XAM fix
                last_delta = width - currentWidth
                # <<< XAM fix
                current = ShapelyUtils.offset_multiline(current, last_delta, "left")
                if current:
                    current = ShapelyUtils.simplify_multiline(current, 0.01)

                if current:
                    if needReverse:
                        reversed = []
                        for path in current.geoms:
                            coords = list(
                                path.coords
                            )  # is a tuple!  JSCUT current reversed in place
                            coords.reverse()
                            reversed.append(shapely.geometry.LineString(coords))
                        allPaths = (
                            reversed + allPaths
                        )  # JSCUT: allPaths = current.concat(allPaths)
                    else:
                        allPaths = [
                            p for p in current.geoms
                        ] + allPaths  # JSCUT: allPaths = current.concat(allPaths)
                    break

            currentWidth = nextWidth

            if not current:
                break

            current = ShapelyUtils.offset_multiline(
                current, eachOffset, "left", resolution=16
            )
            if current:
                current = ShapelyUtils.simplify_multiline(current, 0.01)
                print("--- next toolpath")
            else:
                break

        if len(allPaths) == 0:
            # no possible paths! TODO . inform user
            return []

        # merge_paths need MultiPolygon
        bounds = shapely.geometry.MultiPolygon()

        return cls.merge_paths(bounds, allPaths, closed_path=False)

    @classmethod
    def engrave(
        cls, geometry: shapely.geometry.MultiPolygon, climb: bool
    ) -> List[CamPath]:
        """
        Compute paths for engrave operation on Shapely multipolygon.

        Returns array of CamPath.
        """
        # use lines, not polygons
        multiline_ext = ShapelyUtils.multipoly_exteriors_to_multiline(geometry)
        multiline_int = ShapelyUtils.multipoly_interiors_to_multiline(geometry)

        full_line = shapely.ops.linemerge(
            list(multiline_ext.geoms) + list(multiline_int.geoms)
        )

        if full_line.geom_type == "LineString":
            camPaths = [CamPath(full_line, False)]
            return camPaths

        allPaths = []
        for line in full_line.geoms:
            coords = list(line.coords)  # JSCUT: path = paths.slice(0)
            if not climb:
                coords.reverse()

            coords.append(coords[0])
            allPaths.append(shapely.geometry.LineString(coords))

        camPaths = [CamPath(path, False) for path in allPaths]
        return camPaths

    @classmethod
    def engrave_opened_paths(
        cls, geometry: shapely.geometry.MultiLineString, climb: bool
    ) -> List[CamPath]:
        """
        Compute paths for engrave operation on Shapely multiplinestring.

        Returns array of CamPath.
        """
        allPaths = []
        for line in geometry.geoms:
            coords = list(line.coords)  # JSCUT: path = paths.slice(0)
            if not climb:
                coords.reverse()

            # coords.append(coords[0])  # what's this ??
            allPaths.append(shapely.geometry.LineString(coords))

        camPaths = [CamPath(path, False) for path in allPaths]
        return camPaths

    @classmethod
    def merge_paths(
        cls,
        _bounds: shapely.geometry.MultiPolygon,
        paths: List[shapely.geometry.LineString],
        closed_path=True,
    ) -> List[CamPath]:
        """
        Try to merge paths. A merged path doesn't cross outside of bounds AND the interior polygons
        """
        # cnt = MatplotLibUtils.display("mergePath", shapely.geometry.MultiLineString(paths), force=True)

        if _bounds and len(_bounds.geoms) > 0:
            bounds = _bounds
        else:
            bounds = shapely.geometry.MultiPolygon()

        ext_lines = ShapelyUtils.multipoly_exteriors_to_multiline(bounds)
        int_polys = []
        for poly in bounds.geoms:
            if poly.interiors:
                for interior in poly.interiors:
                    int_poly = shapely.geometry.Polygon(interior)
                    int_polys.append(int_poly)
        if int_polys:
            int_multipoly = shapely.geometry.MultiPolygon(int_polys)
        else:
            int_multipoly = None

        # std list
        thepaths = [list(path.coords) for path in paths]

        #####
        # thepaths = thepaths[19:22]
        #####

        paths = thepaths

        currentPath = paths[0]

        pathEndPoint = currentPath[-1]
        pathStartPoint = currentPath[0]

        # close if start/end points not equal - in case of closed_path geometry -
        if closed_path == True:
            if (
                pathEndPoint[0] != pathStartPoint[0]
                or pathEndPoint[1] != pathStartPoint[1]
            ):
                currentPath = currentPath + [pathStartPoint]

        currentPoint = currentPath[-1]
        paths[0] = []  # empty

        mergedPaths: List[shapely.geometry.LineString] = []
        numLeft = len(paths) - 1

        while numLeft > 0:
            closestPathIndex = None
            closestPointIndex = None
            closestPointDist = sys.maxsize
            for pathIndex, path in enumerate(paths):
                for pointIndex, point in enumerate(path):
                    dist = cam.distP(currentPoint, point)
                    if dist < closestPointDist:
                        closestPathIndex = pathIndex
                        closestPointIndex = pointIndex
                        closestPointDist = dist

            path = paths[closestPathIndex]
            paths[closestPathIndex] = []  # empty
            numLeft -= 1
            needNew = ShapelyUtils.crosses(
                ext_lines, currentPoint, path[closestPointIndex]
            )
            if (not needNew) and int_multipoly:
                needNew = ShapelyUtils.crosses(
                    int_multipoly, currentPoint, path[closestPointIndex]
                )

            # JSCUT path = path.slice(closestPointIndex, len(path)).concat(path.slice(0, closestPointIndex))
            path = path[closestPointIndex:] + path[:closestPointIndex]
            path.append(path[0])

            if needNew:
                mergedPaths.append(currentPath)
                currentPath = path
                currentPoint = currentPath[-1]
            else:
                currentPath = currentPath + path
                currentPoint = currentPath[-1]

        mergedPaths.append(currentPath)

        camPaths: List[CamPath] = []
        for path in mergedPaths:
            safe_to_close = not ShapelyUtils.crosses(bounds, path[0], path[-1])

            if closed_path == False:
                safe_to_close = False

            camPaths.append(CamPath(shapely.geometry.LineString(path), safe_to_close))

        return camPaths

    @staticmethod
    def dist(x1: float, y1: float, x2: float, y2: float) -> float:
        dx = x2 - x1
        dy = y2 - y1
        return dx * dx + dy * dy

    @staticmethod
    def distP(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return dx * dx + dy * dy

    @classmethod
    def getGcode(cls, args) -> List[str]:
        """
        Convert paths to gcode. getGcode() assumes that the current Z position is at safeZ.
        getGcode()'s gcode returns Z to this position at the end.
        args must have:
          optype:         Type of Op.
          paths:          Array of CamPath
          ramp:           Ramp these paths?
          scale:          Factor to convert Clipper units to gcode units
          offsetX:        Offset X (gcode units)
          offsetY:        Offset Y (gcode units)
          decimal:        Number of decimal places to keep in gcode
          topZ:           Top of area to cut (gcode units)
          botZ:           Bottom of area to cut (gcode units)
          safeZ:          Z position to safely move over uncut areas (gcode units)
          passdepth:      Cut depth for each pass (gcode units)
          plungeFeed:     Feedrate to plunge cutter (gcode units)
          retractFeed:    Feedrate to retract cutter (gcode units)
          cutFeed:        Feedrate for horizontal cuts (gcode units)
          rapidFeed:      Feedrate for rapid moves (gcode units)
          toolDiameter:
          helixRevolutionDepth: depth of an helix revolution (theoretical)
          helixPlungeRate:      helix plunge rate (theoretical)
          tabs:           List of tabs
          tabZ:           Level below which tabs are to be processed
          peckZ:          Level to retract when pecking
          flipXY          toggle X with Y
        """
        optype = args["optype"]
        paths: List[CamPath] = args["paths"]
        ramp = args["ramp"]
        scale = args["scale"]
        offsetX = args["offsetX"]
        offsetY = args["offsetY"]
        decimal = args["decimal"]
        topZ = args["topZ"]
        botZ = args["botZ"]
        safeZ = args["safeZ"]
        passdepth = args["passdepth"]

        plungeFeedGcode = " F%d" % args["plungeFeed"]
        retractFeedGcode = " F%d" % args["retractFeed"]
        cutFeedGcode = " F%d" % args["cutFeed"]
        rapidFeedGcode = " F%d" % args["rapidFeed"]

        plungeFeed = args["plungeFeed"]
        retractFeed = args["retractFeed"]
        cutFeed = args["cutFeed"]
        rapidFeed = args["rapidFeed"]

        tabs = args["tabs"]
        tabZ = args["tabZ"]

        peckZ = args["peckZ"]

        flipXY = args["flipXY"]

        gcode = []

        retractGcode = [
            "; Retract",
            "G1 Z" + safeZ.to_fixed(decimal) + f"{rapidFeedGcode}",
        ]

        retractForTabGcode = [
            "; Retract for tab",
            "G1 Z" + tabZ.to_fixed(decimal) + f"{rapidFeedGcode}",
        ]

        retractForPeck = [
            "; Retract for peck",
            "G1 Z" + peckZ.to_fixed(decimal) + f"{rapidFeedGcode}",
        ]

        def getX(p: Tuple[float, float]):
            return p[0] * scale + offsetX

        def getY(p: Tuple[float, float]):
            return -p[1] * scale + offsetY

        def convertPoint(p: Tuple[float, float]):
            x = p[0] * scale + offsetX
            y = -p[1] * scale + offsetY

            if flipXY is False:
                result = (
                    " X"
                    + ValWithUnit(x, "-").to_fixed(decimal)
                    + " Y"
                    + ValWithUnit(y, "-").to_fixed(decimal)
                )
            else:
                result = (
                    " X"
                    + ValWithUnit(-y, "-").to_fixed(decimal)
                    + " Y"
                    + ValWithUnit(x, "-").to_fixed(decimal)
                )

            return result

        def convertPoint3D(p: Tuple[float, float, float]):
            x = p[0] * scale + offsetX
            y = -p[1] * scale + offsetY
            z = p[2]

            if flipXY is False:
                result = (
                    " X"
                    + ValWithUnit(x, "-").to_fixed(decimal)
                    + " Y"
                    + ValWithUnit(y, "-").to_fixed(decimal)
                    + " Z"
                    + ValWithUnit(z, "-").to_fixed(decimal)
                )
            else:
                result = (
                    " X"
                    + ValWithUnit(-y, "-").to_fixed(decimal)
                    + " Y"
                    + ValWithUnit(x, "-").to_fixed(decimal)
                    + " Z"
                    + ValWithUnit(z, "-").to_fixed(decimal)
                )

            return result

        # special case
        if optype == "Helix":
            SEG_LEN = 0.1

            tool_diameter = args["toolDiameter"]
            helix_width = args["helixWidth"]
            helix_revolution_depth = args["helixRevolutionDepth"]
            helix_plunge_rate = args["helixPlungeRate"]

            cut_depth = -botZ

            for campath in paths:
                center = (campath.path.coords.xy[0][0], campath.path.coords.xy[1][0])

                circle_travel_radius = (helix_width - tool_diameter) / 2.0
                circle_travel = 2 * PI * circle_travel_radius
                helix_plunge_rate = cutFeed * helix_revolution_depth / circle_travel

                print("HELIX_CIRCLE_TRAVEL_RADIUS = ", circle_travel_radius)
                print("HELIX_PLUNGE_RATE = ", helix_plunge_rate)

                # well we wish an helix plunge rate as integer.
                # So the helix_revolution_depth will be somehow "corrected"

                helix_plunge_rate = math.floor(helix_plunge_rate) + 1
                helix_revolution_depth = circle_travel * helix_plunge_rate / cutFeed

                print("FIXED - HELIX_PLUNGE_RATE = ", helix_plunge_rate)
                print("FIXED - HELIX_REVOLUTION_DEPTH = ", helix_revolution_depth)

                nb_pts_per_revolution = math.floor(circle_travel / SEG_LEN)

                nb_helixes = math.floor(cut_depth / helix_revolution_depth)

                helix_revolution_depth_last = (
                    cut_depth - nb_helixes * helix_revolution_depth
                )

                # calculate all the pts with z component
                pts = []

                # the helix revolutions
                for i in range(0, nb_helixes):
                    for k in range(nb_pts_per_revolution):
                        x = math.cos(2 * PI * k / nb_pts_per_revolution)
                        y = math.sin(2 * PI * k / nb_pts_per_revolution)

                        height = helix_revolution_depth  # shorter name

                        z = -i * height - k * height / nb_pts_per_revolution

                        xx = center[0] + circle_travel_radius * x
                        yy = center[1] + circle_travel_radius * y

                        pts.append([xx, yy, z])

                # and the last one

                if helix_revolution_depth_last > 0.0:
                    for k in range(nb_pts_per_revolution):
                        x = math.cos(2 * PI * k / nb_pts_per_revolution)
                        y = math.sin(2 * PI * k / nb_pts_per_revolution)

                        height = helix_revolution_depth
                        last_height = helix_revolution_depth_last

                        z = (
                            -nb_helixes * height
                            - k * last_height / nb_pts_per_revolution
                        )

                        xx = center[0] + circle_travel_radius * x
                        yy = center[1] + circle_travel_radius * y

                        pts.append([xx, yy, z])

                # and the last flat circle

                for k in range(nb_pts_per_revolution + 1):
                    x = math.cos(2 * PI * k / nb_pts_per_revolution)
                    y = math.sin(2 * PI * k / nb_pts_per_revolution)

                    z = -cut_depth

                    xx = center[0] + circle_travel_radius * x
                    yy = center[1] + circle_travel_radius * y

                    pts.append([xx, yy, z])

                # the gcode
                gcode.append("; Rapid to op center position")
                gcode.append("G1" + convertPoint(center) + rapidFeedGcode)

                gcode.append("; Slow to op initial position")
                pt0 = pts[0]
                gcode.append("G1" + convertPoint(pt0) + cutFeedGcode)

                for k, pt in enumerate(pts):
                    if k == 0:
                        gcode.append(
                            "G1" + convertPoint3D(pt) + f" F{helix_plunge_rate}"
                        )
                    else:
                        gcode.append("G1" + convertPoint3D(pt))

            gcode.extend(retractGcode)

            gcode.append("; Rapid to op center position")
            gcode.append("G1" + convertPoint(center) + rapidFeedGcode)

            return gcode

        # tabs are globals - but maybe this path does not hits any tabs
        crosses_tabs = False
        # --> crosses_tabs will be fixed later

        for pathIndex, path in enumerate(paths):
            origPath = path.path
            if len(origPath.coords) == 0:
                continue

            # split the path to cut into many partials paths to avoid tabs areas
            tab_separator = TabsSeparator(tabs)
            tab_separator.separate(origPath)

            separated_paths = tab_separator.separated_paths
            crosses_tabs = tab_separator.crosses_tabs

            gcode.append("")
            gcode.append(f"; Path {pathIndex+1}")

            currentZ = safeZ
            finishedZ = topZ

            # need to cut at tabZ if tabs there
            exactTabZLevelDone = False

            while finishedZ > botZ:
                nextZ = max(finishedZ - passdepth, botZ)

                if crosses_tabs:
                    if nextZ == tabZ:
                        exactTabZLevelDone = True
                    elif nextZ < tabZ:
                        # a last cut at the exact tab height withput tabs
                        if exactTabZLevelDone == False:
                            nextZ = tabZ
                            exactTabZLevelDone = True

                if currentZ <= tabZ and ((not path.safe_to_close) or crosses_tabs):
                    if optype == "Peck":
                        gcode.extend(retractForPeck)
                        currentZ = peckZ
                    else:
                        gcode.extend(retractGcode)
                        currentZ = safeZ
                elif currentZ < safeZ and (not path.safe_to_close):
                    if optype == "Peck":
                        gcode.extend(retractForPeck)
                        currentZ = peckZ
                    else:
                        gcode.extend(retractGcode)
                        currentZ = safeZ

                # check this - what does it mean ???
                if not crosses_tabs:
                    currentZ = finishedZ
                else:
                    currentZ = max(finishedZ, tabZ)

                gcode.append("; Rapid to initial position")
                gcode.append(
                    "G1" + convertPoint(list(origPath.coords)[0]) + rapidFeedGcode
                )

                inTabsHeight = False

                if not crosses_tabs:
                    inTabsHeight = False
                    selectedPaths = [origPath]
                    gcode.append("G1 Z" + ValWithUnit(currentZ, "-").to_fixed(decimal))
                else:
                    if nextZ >= tabZ:
                        inTabsHeight = False
                        selectedPaths = [origPath]
                        gcode.append(
                            "G1 Z" + ValWithUnit(currentZ, "-").to_fixed(decimal)
                        )
                    else:
                        inTabsHeight = True
                        selectedPaths = separated_paths

                for selectedPath in selectedPaths:
                    if selectedPath.is_empty:
                        continue

                    executedRamp = False
                    minPlungeTime = (currentZ - nextZ) / plungeFeed
                    if ramp and minPlungeTime > 0:
                        minPlungeTime = (currentZ - nextZ) / plungeFeed
                        idealDist = cutFeed * minPlungeTime
                        totalDist = 0
                        for end in range(1, len(list(selectedPath.coords))):
                            if totalDist > idealDist:
                                break

                            pt1 = list(selectedPath.coords)[end - 1]
                            pt2 = list(selectedPath.coords)[end]
                            totalDist += 2 * cam.dist(
                                getX(pt1), getY(pt1), getX(pt2), getY(pt2)
                            )

                        if totalDist > 0:
                            # rampPath = selectedPath.slice(0, end)
                            rampPath = [
                                list(selectedPath.coords)[k] for k in range(0, end)
                            ]

                            # rampPathEnd = selectedPath.slice(0, end - 1).reverse()
                            rampPathEnd = [
                                list(selectedPath.coords)[k] for k in range(0, end - 1)
                            ]
                            rampPathEnd.reverse()

                            rampPath = rampPath + rampPathEnd

                            if inTabsHeight:
                                # move to initial point of partial path
                                gcode.append(
                                    "; Tab: move to first point of partial path at safe height"
                                )
                                gcode.append("G1" + convertPoint(rampPath[1]))
                                gcode.append("; plunge")
                                gcode.append(
                                    "G1 Z"
                                    + ValWithUnit(nextZ, "-").to_fixed(decimal)
                                    + plungeFeedGcode
                                )

                            gcode.append("; ramp")
                            executedRamp = True

                            distTravelled = 0
                            for i in range(1, len(rampPath)):
                                distTravelled += cam.dist(
                                    getX(rampPath[i - 1]),
                                    getY(rampPath[i - 1]),
                                    getX(rampPath[i]),
                                    getY(rampPath[i]),
                                )
                                newZ = currentZ + distTravelled / totalDist * (
                                    nextZ - currentZ
                                )
                                gcode_line_start = (
                                    "G1"
                                    + convertPoint(rampPath[i])
                                    + " Z"
                                    + ValWithUnit(newZ, "-").to_fixed(decimal)
                                )
                                if i == 1:
                                    gcode.append(
                                        gcode_line_start
                                        + " F"
                                        + ValWithUnit(
                                            math.floor(
                                                min(totalDist / minPlungeTime, cutFeed)
                                            ),
                                            "-",
                                        ).to_fixed(decimal)
                                    )
                                else:
                                    gcode.append(gcode_line_start)

                    if not inTabsHeight:
                        if not executedRamp:
                            gcode.append("; plunge")
                            gcode.append(
                                "G1 Z"
                                + ValWithUnit(nextZ, "-").to_fixed(decimal)
                                + plungeFeedGcode
                            )

                    if inTabsHeight:
                        # move to initial point of partial path
                        gcode.append(
                            "; Tab: move to first point of partial path at safe height"
                        )
                        gcode.append("G1" + convertPoint(list(selectedPath.coords)[0]))
                        gcode.append("; plunge")
                        gcode.append(
                            "G1 Z"
                            + ValWithUnit(nextZ, "-").to_fixed(decimal)
                            + plungeFeedGcode
                        )

                    currentZ = nextZ

                    gcode.append("; cut")

                    # on a given height, generate series of G1
                    for i, pt in enumerate(selectedPath.coords):
                        if i == 0:
                            continue

                        gcode_line_start = "G1" + convertPoint(pt)
                        if i == 1:
                            gcode.append(gcode_line_start + " " + cutFeedGcode)
                        else:
                            gcode.append(gcode_line_start)

                    if inTabsHeight:
                        # retract to safeZ before processing next separated_paths item
                        gcode.extend(retractGcode)

                finishedZ = nextZ

            gcode.extend(retractGcode)

        return gcode


class TabsSeparator:
    """ """

    def __init__(self, tabs: List[Dict[str, any]]):
        self.tabs = tabs

        self.separated_paths: List[shapely.geometry.LineString] = []
        self.crosses_tabs = False  # init

    def separate(self, path: shapely.geometry.LineString):
        """
        from a "normal" tool path, split this path into a list of "partial" paths
        avoiding the tabs areas
        """
        from gcode_generator import Tab

        if len(self.tabs) == 0:
            self.separated_paths = [path]
            return

        pts = list(path.coords)

        shapely_openpath = shapely.geometry.LineString(pts)

        # print("origPath", origPath)
        # print("origPath", shapely_openpath)

        shapely_tabs_ = []
        # 1. from the tabs, build shapely tab polygons
        for tab_def in self.tabs:
            tab = Tab(tab_def)
            shapely_tabs = tab.svg_path.import_as_polygons_list()
            shapely_tabs_ += shapely_tabs

        # hey, multipolygons are good...
        shapely_tabs = shapely.ops.unary_union(shapely_tabs_)
        if shapely_tabs.geom_type == "Polygon":
            shapely_tabs = shapely.geometry.MultiPolygon([shapely_tabs])
        if shapely_tabs.geom_type == "GeometryCollection":
            for geom in shapely_tabs.geoms:
                if geom.geom_type == "MultiPolygon":
                    shapely_tabs = geom
                if geom.geom_type == "Polygon":
                    shapely_tabs = geom

        if not shapely_openpath.intersects(shapely_tabs):
            self.separated_paths = [path]
            return

        self.crosses_tabs = True

        # 2. then "diff" the origin path with the tabs paths
        shapely_splitted_paths = shapely_openpath.difference(shapely_tabs)

        # 3. that's it
        # print("splitted_paths", shapely_splitted_paths)

        if shapely_splitted_paths.geom_type == "LineString":
            shapely_splitted_paths = shapely.geometry.MultiLineString(
                [shapely_splitted_paths]
            )

        paths: List[shapely.geometry.LineString] = list(shapely_splitted_paths.geoms)

        # >>> XAM merge some paths when possible
        paths = self.merge_compatible_paths(paths)
        # <<< XAM

        self.separated_paths = paths

    def merge_compatible_paths(
        self, paths: List[shapely.geometry.LineString]
    ) -> List[shapely.geometry.LineString]:
        """
        This is a post-processing step to shapely where calculated separated paths can be merged together,
        leading to less separated paths
        """

        # ------------------------------------------------------------------------------------------------
        def paths_are_compatible(
            path1: shapely.geometry.LineString, path2: shapely.geometry.LineString
        ) -> bool:
            """
            test if the 2 paths have their end point/start point compatible (the same)
            """
            boundary1_len = len(list(path1.boundary.geoms))
            boundary2_len = len(list(path2.boundary.geoms))

            # print("boundary1_len =", boundary1_len)
            # print("boundary2_len =", boundary2_len)

            if boundary1_len == 0 or boundary2_len == 0:
                return False

            endPoint = path1.boundary.geoms[1]
            startPoint = path2.boundary.geoms[0]

            return endPoint == startPoint

        def merge_path_into_path(
            path1: shapely.geometry.LineString, path2: shapely.geometry.LineString
        ) -> Tuple[bool, shapely.geometry.LineString]:
            """
            merge the 2 paths if their end point/start point are compatible (ie the same)
            """
            if paths_are_compatible(path1, path2):
                # can merge
                path1 = shapely.ops.linemerge([path1, path2])
                return True, path1

            return False, path1

        def build_paths_compatibility_table(
            paths: List[shapely.geometry.LineString],
        ) -> Dict[List, int]:
            """
            for all paths in the list of paths, check first which ones can be merged
            """
            compatibility_table = {}

            for i, path in enumerate(paths):
                for j, other_path in enumerate(paths):
                    if i == j:
                        continue
                    rc = paths_are_compatible(path, other_path)
                    if rc:
                        if i in compatibility_table:
                            compatibility_table[i].append(j)
                        else:
                            compatibility_table[i] = [j]

            return compatibility_table

        # ------------------------------------------------------------------------------------------------

        if len(paths) <= 1:
            return paths

        # mlines = shapely.geometry.MultiLineString(paths)
        # cnt = MatplotLibUtils.display("offset - as LineString|MultiLineString (from linestring)", mlines, force=True)

        compatibility_table = build_paths_compatibility_table(paths)

        while len(compatibility_table) > 0:
            i = list(compatibility_table.keys())[0]
            j = compatibility_table[i][0]

            if i < j:
                path_to_be_merged = paths.pop(j)
                path = paths.pop(i)
            else:
                path = paths.pop(i)
                path_to_be_merged = paths.pop(j)

            _, merged_path = merge_path_into_path(path, path_to_be_merged)

            paths.append(merged_path)
            compatibility_table = build_paths_compatibility_table(paths)

        return paths


class PocketCalculator:
    """ """

    def __init__(
        self,
        multipoly: shapely.geometry.MultiPolygon,
        cutter_dia: float,
        overlap: float,
        climb: bool,
    ):
        """
        cutter_dia is in user units.
        overlap is in the range [0, 1].
        """
        self.multipoly = multipoly

        self.cutter_dia = cutter_dia
        self.overlap = overlap
        self.climb = climb

        self.resolution = 16
        self.join_style = 1
        self.mitre_limit = 5.0

        # result of a the calculation
        self.cam_paths: List[CamPath] = []

        # temp variables
        self.all_paths: List[shapely.geometry.LineString] = []

    def pocket(self):
        """
        main algo - build self.cam_paths
        """
        # use polygons exteriors lines - offset them and and diff with the offseted interiors if any
        multipoly = ShapelyUtils.orient_multipolygon(self.multipoly)

        # cnt = MatplotLibUtils.display("multipoly pocket init", multipoly, force=True)

        # the exterior
        current = self.offset_multipolygon(
            multipoly, self.cutter_dia / 2, "left", consider_interiors_offsets=True
        )

        # cnt = MatplotLibUtils.display(
        #    "multipoly pocket first offset", current, force=True
        # )

        if len(current.geoms) == 0:
            # cannot offset ! maybe geometry too narrow for the cutter
            return []

        # bound must be the exterior enveloppe + the interiors polygons
        # no! the bounds are from the first offset with width cutter_dia / 2
        # bounds = multipoly
        bounds = shapely.geometry.MultiPolygon(current)

        # --------------------------------------------------------------------

        while True:
            # if climb:
            #    for line in current:
            #        line.reverse()

            # FIX when the remaining is to small -> of offset that could spread out
            """
            break when the material has been fully removed
            example:
            - circle r = 1.75
            - cutter dia = 3.0 => r = 1.5
            - overlap = 0.5
            => first path in the "small circle" rr = 0.25 , not that the material then has been fully remove
            => but offset of rr = 0.25 amount 1.5 = cuttter_dia *(1 - overlap)  => overflow outside the small circle !!

            CONDITION TO BREAK: the remaining small circle in fully into the "material cut"

            cuts = [ shapely.geometry.Point(xi,yi).buffer(cutter_dia / 2.0) for (xi,yi) in exteriors.coords ]
            material_cut = shapely.ops.unary_union([cuts])
            remaining_poly = current   : current.covered_by(material_cut)
            """
            exteriors = ShapelyUtils.multipoly_exteriors_to_multiline(current)

            self.collect_paths(exteriors)

            # -------------------------------------------- break ?
            if True:
                cuts = []
                for poly in current.geoms:
                    cuts += [
                        shapely.geometry.Point(xi, yi).buffer(self.cutter_dia / 2.0)
                        for (xi, yi) in poly.exterior.coords
                    ]
                material_cut = shapely.ops.unary_union(cuts)
                if current.covered_by(material_cut):
                    break
            # ------------------------------------------- break ?

            current = self.offset_multipolygon(
                current,
                self.cutter_dia * (1 - self.overlap),
                "left",
                consider_interiors_offsets=False,
            )

            """
            BUG: it can be that the offset return "empty" event if the whole material is not fully cut!

            ex: cutter on rectangle [10 , 3.3] x [20 , 6,7]    (y middle = 5)

            with an amount of 1.8 ( cutter_dia = 3 , step_over = 0.6 => amount = 1.8) the offset is really empty
            (because the cutter goes from the left to 3.3+1.8 = 5.1 and from the right to 6.7-1.8 = 4.9)  
            
            To avoid this, we should check if the material has been fully cut: 
            1. get the polygon defined by the exteriors
            2. are there some points outside the reach of the cutter ? 
            3. xxx ??? yyy

            PS: JsCut suffers from the same bug!
            """

            if not current:
                break
            current = ShapelyUtils.simplify_multipoly(current, 0.001)
            if not current:
                break
            current = ShapelyUtils.orient_multipolygon(current)

        # last: make beautiful interiors, only 1 step
        interiors = self.offset_multipolygon_interiors(
            multipoly, self.cutter_dia / 2, "left", consider_exteriors_offsets=True
        )
        interiors_offsets = ShapelyUtils.multipoly_exteriors_to_multiline(interiors)
        self.collect_paths(interiors_offsets)
        # - done !

        self.merge_paths(bounds, self.all_paths)

    def offset_multipolygon(
        self,
        multipoly: shapely.geometry.MultiPolygon,
        amount: float,
        side: str,
        consider_interiors_offsets=False,
    ) -> shapely.geometry.MultiPolygon:
        """
        Generate offseted polygons.
        """
        offseter = ShapelyMultiPolygonOffset(multipoly)
        return offseter.offset(
            amount,
            side,
            consider_interiors_offsets,
            self.resolution,
            self.join_style,
            self.mitre_limit,
        )

    def offset_multipolygon_interiors(
        self,
        multipoly: shapely.geometry.MultiPolygon,
        amount: float,
        side: str,
        consider_exteriors_offsets=False,
    ) -> shapely.geometry.MultiPolygon:
        """
        Generate offseted polygons from the polygons interiors
        """
        offseter = ShapelyMultiPolygonOffsetInteriors(multipoly)
        return offseter.offset(
            amount,
            side,
            consider_exteriors_offsets,
            self.resolution,
            self.join_style,
            self.mitre_limit,
        )

    def collect_paths(self, multiline: shapely.geometry.MultiLineString):
        """ """
        lines_ok = []

        for line in multiline.geoms:
            if len(list(line.coords)) > 0:
                lines_ok.append(line)

        self.all_paths = lines_ok + self.all_paths

    def merge_paths(
        self,
        _bounds: shapely.geometry.MultiPolygon,
        paths: List[shapely.geometry.LineString],
    ) -> List[CamPath]:
        """
        Try to merge paths. A merged path doesn't cross outside of bounds AND the interior polygons
        """
        # cnt = MatplotLibUtils.display("mergePath", shapely.geometry.MultiLineString(paths), force=True)

        if _bounds and len(_bounds.geoms) > 0:
            bounds = _bounds
        else:
            bounds = shapely.geometry.MultiPolygon()

        ext_lines = ShapelyUtils.multipoly_exteriors_to_multiline(bounds)
        int_polys = []
        for poly in bounds.geoms:
            if poly.interiors:
                for interior in poly.interiors:
                    int_poly = shapely.geometry.Polygon(interior)
                    int_polys.append(int_poly)
        if int_polys:
            int_multipoly = shapely.geometry.MultiPolygon(int_polys)
        else:
            int_multipoly = None

        # std list
        thepaths = [list(path.coords) for path in paths]
        paths = thepaths

        currentPath = paths[0]

        pathEndPoint = currentPath[-1]
        pathStartPoint = currentPath[0]

        # close if start/end point not equal - why ? I could have simple lines!
        if pathEndPoint[0] != pathStartPoint[0] or pathEndPoint[1] != pathStartPoint[1]:
            currentPath = currentPath + [pathStartPoint]

        currentPoint = currentPath[-1]
        paths[0] = []  # empty

        mergedPaths: List[shapely.geometry.LineString] = []
        numLeft = len(paths) - 1

        while numLeft > 0:
            closestPathIndex = None
            closestPointIndex = None
            closestPointDist = sys.maxsize
            for pathIndex, path in enumerate(paths):
                for pointIndex, point in enumerate(path):
                    dist = PocketCalculator.distP(currentPoint, point)
                    if dist < closestPointDist:
                        closestPathIndex = pathIndex
                        closestPointIndex = pointIndex
                        closestPointDist = dist

            path = paths[closestPathIndex]
            paths[closestPathIndex] = []  # empty
            numLeft -= 1
            needNew = ShapelyUtils.crosses(
                ext_lines, currentPoint, path[closestPointIndex]
            )
            if (not needNew) and int_multipoly:
                needNew = ShapelyUtils.crosses(
                    int_multipoly, currentPoint, path[closestPointIndex]
                )

            # JSCUT path = path.slice(closestPointIndex, len(path)).concat(path.slice(0, closestPointIndex))
            path = path[closestPointIndex:] + path[:closestPointIndex]
            path.append(path[0])

            if needNew:
                mergedPaths.append(currentPath)
                currentPath = path
                currentPoint = currentPath[-1]
            else:
                currentPath = currentPath + path
                currentPoint = currentPath[-1]

        mergedPaths.append(currentPath)

        cam_paths: List[CamPath] = []
        for path in mergedPaths:
            safe_to_close = not ShapelyUtils.crosses(bounds, path[0], path[-1])
            cam_paths.append(CamPath(shapely.geometry.LineString(path), safe_to_close))

        self.cam_paths = cam_paths

    @staticmethod
    def distP(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return dx * dx + dy * dy


class SpiralePocketCalculator:

    def __init__(
        self,
        svgpaths,
        multipoly: shapely.geometry.MultiPolygon,
        cutter_dia: float,
        overlap: float,
        climb: bool,
    ):
        """
        cutter_dia is in user units.
        overlap is in the range [0, 1].
        """
        self.svgpaths = svgpaths

        self.multipoly = multipoly

        self.cutter_dia = cutter_dia
        self.overlap = overlap
        self.climb = climb

        self.resolution = 16
        self.join_style = 1
        self.mitre_limit = 5.0

        # result of a the calculation
        self.cam_paths: List[CamPath] = []

        # temp variables
        self.pts: List[Tuple] = []

    def pocket(self):
        """
        main algo - build self.cam_paths
        """
        svgpath = self.svgpaths[0]

        shape = svgpath.shape_tag

        if shape == "circle":
            spirale = SpiralePocketCalculator.Circle(self)
            self.pts = spirale.calc()
        if shape == "ellipse":
            spirale = SpiralePocketCalculator.Ellipse(self)
            self.pts = spirale.calc()
        if shape == "rect":
            spirale = SpiralePocketCalculator.Rectangle(self)
            self.pts = spirale.calc()

        self.cam_paths = [CamPath(shapely.geometry.LineString(self.pts), True)]

    class Circle:
        SEGMENT_LEN = 1.0  # mm

        def __init__(self, pocket: "SpiralePocketCalculator"):
            """ """
            self.svgpath = svgpath = pocket.svgpaths[0]

            if svgpath.shape_tag == "circle":
                r = float(svgpath.shape_attrs.get("r"))
                self.pocket_radius = r

                cx = float(svgpath.shape_attrs.get("cx"))
                cy = float(svgpath.shape_attrs.get("cy"))
                self.center = [cx, cy]
            elif svgpath.shape_tag == "ellipse":
                rx = float(svgpath.shape_attrs.get("rx"))
                ry = float(svgpath.shape_attrs.get("ry"))
                self.pocket_radius = min(rx, ry)

                cx = float(svgpath.shape_attrs.get("cx"))
                cy = float(svgpath.shape_attrs.get("cy"))
                self.center = [cx, cy]
            elif svgpath.shape_tag == "rect":
                w = float(svgpath.shape_attrs.get("width"))
                h = float(svgpath.shape_attrs.get("height"))
                self.pocket_radius = min(w, h) / 2.0

                x = float(svgpath.shape_attrs.get("x"))
                y = float(svgpath.shape_attrs.get("y"))

                self.center = [x + w / 2, y + h / 2]
            else:
                self.pocket_radius = 20.0  # FIXME - get it from the geometry
                self.center = [0.0, 0.0]

            self.plunge_rate = 22  # FIXME - get it from the Tool Model
            self.cut_rate = 250  # FIXME - get it from the Tool Model

            self.pocket = pocket

            overlap = self.pocket.overlap

            self.cut_arm_size = self.pocket.cutter_dia / 2.0 * (1.0 - overlap)

            if svgpath.shape_tag == "ellipse":
                rx = float(svgpath.shape_attrs.get("rx"))
                ry = float(svgpath.shape_attrs.get("ry"))

                coeff = max(rx / ry, ry / rx)

                self.cut_arm_size /= coeff

            if svgpath.shape_tag == "rect":
                w = float(svgpath.shape_attrs.get("width"))
                h = float(svgpath.shape_attrs.get("height"))

                coeff = max(w / h, h / w)

                self.cut_arm_size /= coeff

            print("SPIRALE: CUT_SIZE = ", self.cut_arm_size)

            self.nb_arms = math.floor(
                (self.pocket_radius - self.pocket.cutter_dia / 2.0) / self.cut_arm_size
            )

            print("NB_ARMS = ", self.nb_arms)

            # on each speudo circle of length 2pi*r there are
            #  - 2pi*r           segments of lenght 1, or
            #  - 2pi*r / len_seg segments of length len_seg
            #
            # Just sum them:
            #    NB_POINTS = SUM n=1..NB_CIRCLES [2pi * R_n]
            #    R_o = 0
            #    R_n = R_n-1 + CUT_SIZE
            #        = n*CUT_SIZE
            #    => NB_POINTS = 2*pi SUM k=n..NB_CIRCLES [n*CUT_SIZE]

            self.nb_points = math.floor(
                (2 * PI / SpiralePocketCalculator.Circle.SEGMENT_LEN)
                * self.cut_arm_size
                * self.nb_arms
                * (self.nb_arms + 1)
                / 2.0
            )

            print("NB_POINTS = ", self.nb_points)

            self.pocket_radius_minus_cutter = (
                self.pocket_radius - self.pocket.cutter_dia / 2.0
            )

            self.pocket_radius_minus_cutter_squared = (
                self.pocket_radius_minus_cutter * self.pocket_radius_minus_cutter
            )

            self.x = []
            self.y = []
            self.z = []

        def calc(self) -> List[Tuple]:
            """
            Prepare arrays x, y
            """
            # list of angles : will be sqrt'ed
            angles = np.linspace(
                0, (2 * PI * self.nb_arms) * (2 * PI * self.nb_arms), self.nb_points
            )

            # when the radius of the spirale is increasing,
            # the delta(angles) must decrease for small increments in angle
            # at every point
            t = np.sqrt(angles)

            # list of radiuses : will be sqrt'ed
            r = np.linspace(0, self.pocket_radius_minus_cutter_squared, self.nb_points)
            r = np.sqrt(r)  # -> max is POCKET_RADIUS_M_CUTTER

            # because the angles progression is of sqrt, so has to be the
            # progression of the radiuses!

            x = self.center[0] + r * np.cos(t)
            y = self.center[1] + r * np.sin(t)

            # last circle
            dt = t[-1] - t[-2]
            print(
                "dt =",
                dt,
                " => nb pts on circle/last spirale [est] = ",
                math.floor(2 * PI / dt),
                " => nb pts on circle",
                math.floor(
                    2
                    * PI
                    * self.pocket_radius_minus_cutter
                    / SpiralePocketCalculator.Circle.SEGMENT_LEN
                ),
            )

            # discretized circle with N points
            N = math.floor(2 * PI / dt)
            # N = math.floor(2 * pi * POCKET_RADIUS_M_CUTTER / SEGMENT_LEN)

            N = N * 2  # fine resolution for the pocket boundary

            r_circle = np.linspace(
                self.pocket_radius_minus_cutter, self.pocket_radius_minus_cutter, N
            )
            t_circle = t[-1] + np.linspace(0, 2 * PI, N)

            dx = self.center[0] + r_circle * np.cos(t_circle)
            dy = self.center[1] + r_circle * np.sin(t_circle)

            x = np.concatenate([x, dx])
            y = np.concatenate([y, dy])

            pts = [[xx, yy] for xx, yy in zip(x, y)]

            return pts

    class Rectangle(Circle):
        def __init__(self, pocket: "SpiralePocketCalculator"):
            super().__init__(pocket)

            w = float(self.svgpath.shape_attrs.get("width"))
            h = float(self.svgpath.shape_attrs.get("height"))

            x = float(self.svgpath.shape_attrs.get("x"))
            y = float(self.svgpath.shape_attrs.get("y"))

            r = min(w, h) / 2.0

            center = [x + w / 2, y + h / 2]

            self.tx = center[0]
            self.ty = center[1]

            self.scale_x = w / 2
            self.scale_y = h / 2

            print("CENTER", self.tx, self.ty)
            print("SCALE", r, self.scale_x, self.scale_y)

            self.c1 = 0.0
            self.c2 = 1.0

        def calc(self):
            pts = super().calc()

            # TODO - better mapping 'cos not good at the border of the square

            rectangle_pts = [
                (self.to_square_x(x, y), self.to_square_y(x, y)) for (x, y) in pts
            ]

            w = float(self.svgpath.shape_attrs.get("width"))
            h = float(self.svgpath.shape_attrs.get("height"))

            x = float(self.svgpath.shape_attrs.get("x"))
            y = float(self.svgpath.shape_attrs.get("y"))

            diameter = self.pocket.cutter_dia

            centers = [
                [x + w - diameter, y + h - diameter],
                [x + diameter, y + h - diameter],
                [x + diameter, y + diameter],
                [x + w - diameter, y + diameter],
            ]

            rectangle_pts += [[x + w - diameter, y + h / 2.0]]

            for k, center in enumerate(centers):
                c = SvgPath.from_circle_def(
                    center,
                    self.pocket.cutter_dia,
                )
                c.import_svgpath()
                c_svgpaths = [c]
                c_multipoly = shapely.geometry.MultiPolygon(c.polys)
                spirale = SpiralePocketCalculator(
                    c_svgpaths,
                    c_multipoly,
                    self.pocket.cutter_dia,
                    self.pocket.overlap,
                    self.pocket.climb,
                )
                spirale.pocket()

                rectangle_pts += [center]
                rectangle_pts += spirale.pts
                rectangle_pts += [center]

            # last perfect contour

            """
            *----------------*
            |                |
            |                | start - go cw (svg y dir)
            |                |
            *----------------*
            """
            dw = w / 2 - self.pocket.cutter_dia / 2.0
            dh = h / 2 - self.pocket.cutter_dia / 2.0

            pt0 = [self.center[0] + dw, self.center[1]]
            pt1 = [self.center[0] + dw, self.center[1] + dh]
            pt2 = [self.center[0] - dw, self.center[1] + dh]
            pt3 = [self.center[0] - dw, self.center[1] - dh]
            pt4 = [self.center[0] + dw, self.center[1] - dh]
            pt5 = [self.center[0] + dw, self.center[1]]

            contours_pts = [pt0, pt1, pt2, pt3, pt4, pt5]

            rectangle_pts += contours_pts

            return rectangle_pts

        def normalize(self, u, v):
            return [
                (u - self.tx) / self.pocket_radius,
                (v - self.ty) / self.pocket_radius,
            ]

        def to_square_x(self, u, v):
            """
            from unit circle to unit square

            x = ½ √( 2 + u² - v² + 2u√2 ) - ½ √( 2 + u² - v² - 2u√2 )
            y = ½ √( 2 - u² + v² + 2v√2 ) - ½ √( 2 - u² + v² - 2v√2 )
            """
            u, v = self.normalize(u, v)

            uu = u * u
            vv = v * v

            sgn_u = 0.0 if u == 0.0 else (1 if u > 0 else -1)
            sgn_v = 0.0 if v == 0.0 else (1 if v > 0 else -1)

            # stretch method
            if u == 0.0 and v == 0.0:
                x = 0

            if uu >= vv:
                x = sgn_u * sqrt(uu + vv)
            else:
                if v == 0.0:
                    x = 0.0
                else:
                    x = sgn_v * sqrt(uu + vv) * u / v

            x1 = x

            # ellipse method
            a = 2 + uu - vv + 2 * u * sqrt(2)
            b = 2 + uu - vv - 2 * u * sqrt(2)

            a = a if a > 0.0 else 0.0
            b = b if b > 0.0 else 0.0

            x = 0.5 * sqrt(a) - 0.5 * sqrt(b)

            x2 = x

            # the middle of the two
            x = (self.c1 * x1 + self.c2 * x2) / (self.c1 + self.c2)

            return self.tx + self.scale_x * x

        def to_square_y(self, u, v):
            """
            from unit circle to unit square

            x = ½ √( 2 + u² - v² + 2u√2 ) - ½ √( 2 + u² - v² - 2u√2 )
            y = ½ √( 2 - u² + v² + 2v√2 ) - ½ √( 2 - u² + v² - 2v√2 )
            """
            u, v = self.normalize(u, v)

            uu = u * u
            vv = v * v

            sgn_u = 0.0 if u == 0.0 else (1 if u > 0 else -1)
            sgn_v = 0.0 if v == 0.0 else (1 if v > 0 else -1)

            # stretch method
            if u == 0.0 and v == 0.0:
                x = 0.0

            if uu >= vv:
                if u == 0.0:
                    y = 0.0
                else:
                    y = sgn_u * sqrt(uu + vv) * v / u
            else:
                y = sgn_v * sqrt(uu + vv)

            y1 = y

            # ellipse method
            a = 2 - uu + vv + 2 * v * sqrt(2)
            b = 2 - uu + vv - 2 * v * sqrt(2)

            a = a if a > 0.0 else 0.0
            b = b if b > 0.0 else 0.0

            y = 0.5 * sqrt(a) - 0.5 * sqrt(b)

            y2 = y

            # the  middle of the two
            y = (self.c1 * y1 + self.c2 * y2) / (self.c1 + self.c2)

            return self.ty + self.scale_y * y

    class Ellipse(Circle):
        def __init__(self, pocket: "SpiralePocketCalculator"):
            super().__init__(pocket)

            cx = float(self.svgpath.shape_attrs.get("cx"))
            cy = float(self.svgpath.shape_attrs.get("cy"))

            rx = float(self.svgpath.shape_attrs.get("rx"))
            ry = float(self.svgpath.shape_attrs.get("ry"))

            r = min(rx, ry)

            # cutter trajectory is on the "inner circle"
            r -= self.pocket.cutter_dia / 2.0

            self.tx = cx
            self.ty = cy

            self.scale_x = (rx - self.pocket.cutter_dia / 2.0) / r
            self.scale_y = (ry - self.pocket.cutter_dia / 2.0) / r

        def calc(self):
            """just stretch"""
            pts = super().calc()

            ellipse_pts = [
                (
                    self.tx + (x - self.tx) * self.scale_x,
                    self.ty + (y - self.ty) * self.scale_y,
                )
                for (x, y) in pts
            ]

            return ellipse_pts
