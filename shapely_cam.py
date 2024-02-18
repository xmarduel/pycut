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

from typing import List
from typing import Dict
from typing import Tuple

from val_with_unit import ValWithUnit

import shapely.geometry
import shapely.ops

from shapely_utils import ShapelyUtils
from shapely_ext import ShapelyMultiPolygonOffset
from shapely_ext import ShapelyMultiPolygonOffsetInteriors
from shapely_matplotlib import MatplotLibUtils


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
            # HACK LineString with 2 identical point? not future proof...
            camPath = CamPath(shapely.geometry.LineString([pt, pt]), True)
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
            # HACK LineString with 2 identical point? not future proof...
            camPath = CamPath(shapely.geometry.LineString([pt, pt]), False)
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
        multiline = ShapelyUtils.multiPolyToMultiLine(geometry)

        currentWidth = cutter_dia
        allPaths: List[shapely.geometry.LineString] = []
        eachWidth = cutter_dia * (1 - overlap)

        if is_inside:
            # because we always start from the outer ring -> we go "inside"
            current = ShapelyUtils.offsetMultiLine(multiline, cutter_dia / 2, "left")
            offset = ShapelyUtils.offsetMultiLine(
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
                current = ShapelyUtils.offsetMultiLine(
                    multiline, cutter_dia / 2, "right"
                )
                offset = ShapelyUtils.offsetMultiLine(
                    multiline, width - cutter_dia / 2, "right"
                )
                # bounds = ShapelyUtils.diff(current, offset)
                bounds = current
            else:
                # because we always start from the outer ring -> we go "inside"
                current = ShapelyUtils.offsetMultiLine(
                    multiline, cutter_dia / 2, "left"
                )
                offset = ShapelyUtils.offsetMultiLine(
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
                current = ShapelyUtils.offsetMultiLine(current, last_delta, "left")
                if current:
                    current = ShapelyUtils.simplifyMultiLine(current, 0.01)

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

            current = ShapelyUtils.offsetMultiLine(
                current, eachOffset, "left", resolution=16
            )
            if current:
                current = ShapelyUtils.simplifyMultiLine(current, 0.01)
                print("--- next toolpath")
            else:
                break

        if len(allPaths) == 0:
            # no possible paths! TODO . inform user
            return []

        # merge_paths need MultiPolygon
        bounds = ShapelyUtils.multiLineToMultiPoly(bounds)

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
            current = ShapelyUtils.offsetMultiLine(multiline, 0.0, "left")
            offset = ShapelyUtils.offsetMultiLine(multiline, width - 0.0, "left")
            # bounds = ShapelyUtils.diff(current, offset)
            bounds = current
            eachOffset = eachWidth
            needReverse = climb
        else:
            direction = "inner2outer"
            # direction = "outer2inner"

            if direction == "inner2outer":
                # because we always start from the inner ring -> we go "outside"
                current = ShapelyUtils.offsetMultiLine(multiline, 0.0, "right")
                offset = ShapelyUtils.offsetMultiLine(multiline, width - 0.0, "right")
                # bounds = ShapelyUtils.diff(current, offset)
                bounds = current
            else:
                # because we always start from the outer ring -> we go "inside"
                current = ShapelyUtils.offsetMultiLine(multiline, 0.0, "left")
                offset = ShapelyUtils.offsetMultiLine(multiline, width - 0.0, "left")
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
                current = ShapelyUtils.offsetMultiLine(current, last_delta, "left")
                if current:
                    current = ShapelyUtils.simplifyMultiLine(current, 0.01)

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

            current = ShapelyUtils.offsetMultiLine(
                current, eachOffset, "left", resolution=16
            )
            if current:
                current = ShapelyUtils.simplifyMultiLine(current, 0.01)
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
        multiline_ext = ShapelyUtils.multiPolyToMultiLine(geometry)
        multiline_int = ShapelyUtils.multiPolyIntToMultiLine(geometry)

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

        ext_lines = ShapelyUtils.multiPolyToMultiLine(bounds)
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

        def getX(p: Tuple[int, int]):
            return p[0] * scale + offsetX

        def getY(p: Tuple[int, int]):
            return -p[1] * scale + offsetY

        def convertPoint(p: Tuple[int, int]):
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
        main algo
        """
        # use polygons exteriors lines - offset them and and diff with the offseted interiors if any
        multipoly = ShapelyUtils.orientMultiPolygon(self.multipoly)

        # cnt = MatplotLibUtils.display("multipoly pocket init", multipoly, force=True)

        # the exterior
        current = self.offsetMultiPolygon(
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
            exteriors = ShapelyUtils.multiPolyToMultiLine(current)

            self.collectPaths(exteriors)

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

            current = self.offsetMultiPolygon(
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
            current = ShapelyUtils.simplifyMultiPoly(current, 0.001)
            if not current:
                break
            current = ShapelyUtils.orientMultiPolygon(current)

        # last: make beautiful interiors, only 1 step
        interiors = self.offsetMultiPolygonInteriors(
            multipoly, self.cutter_dia / 2, "left", consider_exteriors_offsets=True
        )
        interiors_offsets = ShapelyUtils.multiPolyToMultiLine(interiors)
        self.collectPaths(interiors_offsets)
        # - done !

        self.merge_paths(bounds, self.all_paths)

    def offsetMultiPolygon(
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

    def offsetMultiPolygonInteriors(
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

    def collectPaths(self, multiline: shapely.geometry.MultiLineString):
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

        ext_lines = ShapelyUtils.multiPolyToMultiLine(bounds)
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
