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

import shapely.geometry  # type: ignore [import-untyped]
import shapely.ops  # type: ignore [import-untyped]

from shapely.geometry.base import JOIN_STYLE  # type: ignore [import-untyped]

from shapely_utils import ShapelyUtils
from shapely_matplotlib import MatplotLibUtils


class ShapelyMultiPolygonOffset:
    """
    The class to perform an offset of a polygon.
    It has to take care of the possible offseted interiors of the polygon
    """

    def __init__(self, multipoly: shapely.geometry.MultiPolygon):
        """ """
        # input
        self.multipoly = multipoly

    def offset(
        self,
        amount: float,
        side: str,
        consider_interiors_offsets: bool,
        resolution: int,
        join_style: JOIN_STYLE,
        mitre_limit: float,
    ) -> shapely.geometry.MultiPolygon:
        """
        Generate offseted polygons.
        """
        polys = []

        for poly in self.multipoly.geoms:
            linearring = shapely.geometry.LineString(poly.exterior)
            # offset of a linearring is !BUGGY!
            linestring = ShapelyUtils.linearring_to_linestring(linearring)
            # unfortunately this generates others PYCUT bugs !!  (pocketing - FIXME - ) so reset
            linestring = linearring

            # cnt = MatplotLibUtils.display(
            #    "linestring to offset", linestring, force=True
            # )

            # shapely 2.0 fix : if amount = 0
            if amount != 0.0:
                ext_offset = linestring.parallel_offset(
                    amount,
                    side,
                    resolution=resolution,
                    join_style=join_style,
                    mitre_limit=mitre_limit,
                )
            else:
                ext_offset = shapely.geometry.LineString(linestring)

            # cnt = MatplotLibUtils.display(
            #    f"offset {side} - as LineString|MultiLineString (from linestring)",
            #    ext_offset,
            #    force=True,
            # )

            # simplfy resulting offset  !WICHTIG!
            # print("offset: ", ext_offset)
            if ext_offset.geom_type == "LineString":
                # cnt = MatplotLibUtils.display(
                #    f"offset {side} - as LineString|MultiLineString (from linestring)",
                #    ext_offset,
                #    force=True,
                # )
                print(
                    "offset length (1)= ",
                    ext_offset.length,
                    len(list(ext_offset.coords)),
                )
                ext_offset = ext_offset.simplify(0.005)
                print(
                    "offset length (2)= ",
                    ext_offset.length,
                    len(list(ext_offset.coords)),
                )
                # cnt = MatplotLibUtils.display(
                #    f"offset {side} - as LineString|MultiLineString (from linestring)",
                #    ext_offset,
                #    force=True,
                # )
            elif ext_offset.geom_type == "MultiLineString":
                lines = []
                for line in ext_offset.geoms:
                    # print("offset length (1)= ", line.length, len(list(line.coords)))
                    s_line = line.simplify(0.005)
                    # print("offset length (2)= ", s_line.length, len(list(s_line.coords)))
                    lines.append(s_line)
                ext_offset = shapely.geometry.MultiLineString(lines)

            # from the offseted lines, build a multipolygon that we diff with the interiors
            exterior_multipoly = ShapelyUtils.build_multipoly_from_offsets([ext_offset])
            # print("exterior_multipoly VALID ? ", exterior_multipoly.is_valid)

            # MatplotLibUtils.display(
            #    "geom multipoly from ext offset", exterior_multipoly, force=True
            # )

            # now consider the interiors
            if poly.interiors:
                interior_polys = []
                for interior in poly.interiors:
                    ipoly = shapely.geometry.Polygon(interior)

                    # simplify the polygon
                    # this may be important so that the offset becomes Ok (example: tudor [AD])
                    # where of offset is a MultiLineString instead of a Linestring
                    ipoly = ipoly.simplify(0.001)
                    ipoly = shapely.geometry.polygon.orient(ipoly)

                    interior_polys.append(ipoly)

                interior_multipoly = ShapelyUtils.build_multipoly_from_list_of_polygons(
                    interior_polys
                )

                # cnt = MatplotLibUtils.display(
                #    "starting interior offset from", interior_multipoly, force=True
                # )

                # consider interiors offsets
                if consider_interiors_offsets == True:
                    interior_multipoly = ShapelyUtils.offset_multipolygon(
                        interior_multipoly, amount, "right"
                    )

                    # cnt = MatplotLibUtils.display(
                    #    "interior first offset", interior_multipoly, force=True
                    # )

                # the diff is the solution
                try:
                    # if not exterior_multipoly.is_valid():
                    #    cnt = MatplotLibUtils.display(
                    #        "diff ext", exterior_multipoly, force=True
                    #    )

                    # if not interior_multipoly.is_valid():
                    #    cnt = MatplotLibUtils.display(
                    #        "diff int", interior_multipoly, force=True
                    #    )

                    sol_poly = exterior_multipoly.difference(interior_multipoly)

                    # cnt = MatplotLibUtils.display(
                    #    "diff of interior offseting", sol_poly, force=True
                    # )

                except Exception as e:
                    print("ERROR difference")
                    print(e)
                    print("exterior_multipoly VALID ?", exterior_multipoly.is_valid)
                    print("interior_multipoly VALID ?", interior_multipoly.is_valid)
                    raise

                if sol_poly.geom_type == "Polygon":
                    polys.append(sol_poly)
                elif sol_poly.geom_type == "MultiPolygon":
                    for geom in sol_poly.geoms:
                        polys.append(geom)
                elif sol_poly.geom_type == "GeometryCollection":
                    for geom in sol_poly.geoms:
                        if geom.geom_type == "Polygon":
                            polys.append(geom)
                        elif geom.geom_type == "MultiPolygon":
                            for geomc in sol_poly.geoms:
                                polys.append(geomc)

            else:  # polygon without interiors
                for poly in exterior_multipoly.geoms:
                    if poly.geom_type == "Polygon":
                        polys.append(poly)

        o_multipoly = ShapelyUtils.build_multipoly_from_list_of_polygons(polys)

        # ensure orientation
        o_multipoly = ShapelyUtils.orient_multipolygon(o_multipoly)

        return o_multipoly


class ShapelyMultiPolygonOffsetInteriors:
    """
    The class to perform an offset 'right' (goint to the exterior) of the interior of a polygon.
    It has to take care of the offseted exterior of the polygon
    """

    def __init__(self, multipoly: shapely.geometry.MultiPolygon):
        """ """
        self.multipoly = multipoly

    def offset(
        self,
        amount: float,
        side: str,
        consider_exteriors_offsets: bool,
        resolution: int,
        join_style: int,
        mitre_limit: float,
    ) -> shapely.geometry.MultiPolygon | None:
        """
        main method
        """
        polys = []

        MatplotLibUtils.display("geometry", self.multipoly, force=False)

        for poly in self.multipoly.geoms:
            if not poly.interiors:
                continue

            linestrings = []
            for interior in poly.interiors:
                linestring = shapely.geometry.LineString(interior)
                linestrings.append(linestring)

            int_offsets = []
            for linestring in linestrings:
                # shapely 2.0 fix : if amount = 0
                if amount != 0.0:
                    int_offset = linestring.parallel_offset(
                        amount,
                        side,
                        resolution=resolution,
                        join_style=join_style,
                        mitre_limit=mitre_limit,
                    )
                else:
                    int_offset = shapely.geometry.LineString(linestring)

                int_offsets.append(int_offset)

            # from the offseted lines, build a multipolygon that we will diff with the exterior
            interior_multipoly = ShapelyUtils.build_multipoly_from_offsets(int_offsets)

            MatplotLibUtils.display(
                "interior_multipoly", interior_multipoly, force=False
            )

            if not interior_multipoly.is_valid:
                interior_multipoly = ShapelyUtils.fix_multipoly(interior_multipoly)

            exterior_multipoly = ShapelyUtils.offset_multipolygon(
                self.multipoly, amount, "left", consider_interiors_offsets=True
            )

            MatplotLibUtils.display(
                "exterior_multipoly", exterior_multipoly, force=False
            )

            # only exterior
            exterior_multipoly = ShapelyUtils.remove_multipoly_holes(exterior_multipoly)

            # this simplify may be important so that the offset becomes Ok (example: letter "B")
            exterior_multipoly = ShapelyUtils.simplify_multipoly(
                exterior_multipoly, 0.001
            )
            exterior_multipoly = ShapelyUtils.orient_multipolygon(exterior_multipoly)

            MatplotLibUtils.display(
                "exterior_multipoly", exterior_multipoly, force=False
            )

            if consider_exteriors_offsets == True:
                # the diff ** with ~POLY ** is the solution
                try:
                    o_interior_is_contained_in_o_exterior = exterior_multipoly.contains(
                        interior_multipoly
                    )
                    print(
                        "XXXXXX offset -> interior_offset_is_contained_in_exterior_offset",
                        o_interior_is_contained_in_o_exterior,
                    )

                    if o_interior_is_contained_in_o_exterior:
                        sol_poly = exterior_multipoly.intersection(interior_multipoly)
                    else:
                        # big problem!
                        sol_poly = (
                            interior_multipoly  # bug: can cut outside the exterior...
                        )
                        sol_poly = exterior_multipoly  # TEST -> GOOD !

                except Exception as e:
                    print("ERROR intersection")
                    print(e)
                    print("interior_multipoly VALID ?", interior_multipoly.is_valid)
                    print("exterior_multipoly VALID ?", exterior_multipoly.is_valid)
                    raise

                if sol_poly.geom_type == "Polygon":
                    polys.append(sol_poly)
                elif sol_poly.geom_type == "MultiPolygon":
                    for geom in sol_poly.geoms:
                        polys.append(geom)
                elif sol_poly.geom_type == "GeometryCollection":
                    for geom in sol_poly.geoms:
                        if geom.geom_type == "Polygon":
                            polys.append(geom)
                        elif geom.geom_type == "MultiPolygon":
                            for poly in geom.geoms:
                                polys.append(poly)

            else:  # without exterior
                for poly in interior_multipoly.geoms:
                    if poly.geom_type == "Polygon":
                        polys.append(poly)

        o_multipoly = ShapelyUtils.build_multipoly_from_list_of_polygons(polys)

        # ensure orientation
        o_multipoly = ShapelyUtils.orient_multipolygon(o_multipoly)

        return o_multipoly
