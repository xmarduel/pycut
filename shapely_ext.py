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

from typing import Literal
from typing import cast

from shapely import BufferJoinStyle
import shapely.geometry

from shapely_matplotlib import MatplotLibUtils
from shapely_utils import ShapelyUtils


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
        join_style: BufferJoinStyle | Literal["round", "mitre", "bevel"],
        mitre_limit: float,
    ) -> shapely.geometry.MultiPolygon:
        """
        Generate offseted polygons.
        """
        polys = []

        for poly in self.multipoly.geoms:
            linearring = shapely.geometry.LinearRing(poly.exterior)

            # cnt = MatplotLibUtils.display(
            #    "poly/linearring to offset", linearring
            # )

            linestring = ShapelyUtils.linearring_to_linestring(linearring)

            # cnt = MatplotLibUtils.display(
            #    "poly/linestring to offset", linestring
            # )

            offset = linestring.parallel_offset(
                amount,
                side,
                resolution=resolution,
                join_style=join_style,
                mitre_limit=mitre_limit,
            )

            # cnt = MatplotLibUtils.display(
            #    f"offset {side} - as LineString|MultiLineString (from linearring)",
            #    ext_offset,
            # )

            # simplfy resulting offset  !WICHTIG!
            # print("offset: ", ext_offset)
            if offset.geom_type == "LineString":
                offset = cast(shapely.geometry.LineString, offset) 

                # cnt = MatplotLibUtils.display(
                #    f"offset {side} - as LineString|MultiLineString (from linearring)",
                #    offset,
                # )
                print(
                    "(1) offset length = ", offset.length, len(list(offset.coords)))
                
                offset = ShapelyUtils.simplify_line(offset, 0.005)
                
                if offset.geom_type == 'LineString':
                    print("(2) offset length = ", offset.length, len(list(offset.coords)))
                if offset.geom_type == 'MultiLineString':
                    pass

                # cnt = MatplotLibUtils.display(
                #    f"offset {side} - as LineString|MultiLineString (from linestring)",
                #    ext_offset,
                # )
            elif offset.geom_type == "MultiLineString":
                offset = cast(shapely.geometry.MultiLineString, offset) 
                offset = ShapelyUtils.simplify_multiline(offset, 0.005)

            # from the offseted lines, build a multipolygon that we diff with the interiors
            exterior_multipoly = ShapelyUtils.build_multipoly_from_offsets([offset])
            # print("exterior_multipoly VALID ? ", exterior_multipoly.is_valid)

            # MatplotLibUtils.display(
            #    "geom multipoly from ext offset", exterior_multipoly)

            # now consider the interiors
            if poly.interiors:
                interior_polys = []
                for interior in poly.interiors:
                    ipoly = shapely.geometry.Polygon(interior)

                    # simplify the polygon
                    # this may be important so that the offset becomes Ok (example: tudor [AD])
                    # where of offset is a MultiLineString instead of a Linestring
                    simp_poly = ipoly.simplify(0.001)

                    if simp_poly.geom_type == 'Polygon':
                        simp_poly = cast(shapely.geometry.Polygon, simp_poly) 
                        ipoly = shapely.geometry.polygon.orient(simp_poly)

                        interior_polys.append(ipoly)

                interior_multipoly = ShapelyUtils.build_multipoly_from_list_of_polygons(
                    interior_polys
                )

                # cnt = MatplotLibUtils.display(
                #    "starting interior offset from", interior_multipoly)

                # consider interiors offsets
                if consider_interiors_offsets == True:
                    interior_multipoly = ShapelyUtils.offset_multipolygon(
                        interior_multipoly, amount, "right"
                    )

                    # cnt = MatplotLibUtils.display(
                    #    "interior first offset", interior_multipoly)

                # the diff is the solution
                try:
                    # if not exterior_multipoly.is_valid():
                    #    cnt = MatplotLibUtils.display(
                    #        "diff ext", exterior_multipoly)

                    # if not interior_multipoly.is_valid():
                    #    cnt = MatplotLibUtils.display(
                    #        "diff int", interior_multipoly)

                    sol_poly = exterior_multipoly.difference(interior_multipoly)

                    # cnt = MatplotLibUtils.display(
                    #    "diff of interior offseting", sol_poly)

                except Exception as e:
                    print("ERROR difference")
                    print(e)
                    print("exterior_multipoly VALID ?", exterior_multipoly.is_valid)
                    print("interior_multipoly VALID ?", interior_multipoly.is_valid)
                    raise

                if sol_poly.geom_type == "Polygon":
                    poly = cast(shapely.geometry.Polygon, sol_poly)
                    polys.append(poly)
                elif sol_poly.geom_type == "MultiPolygon":
                    multi_poly = cast(shapely.geometry.MultiPolygon, sol_poly)
                    for poly in multi_poly.geoms:
                        polys.append(poly)
                elif sol_poly.geom_type == "GeometryCollection":
                    collection = cast(shapely.geometry.GeometryCollection, sol_poly)
                    for geom in collection.geoms:
                        if geom.geom_type == "Polygon":
                            poly = cast(shapely.geometry.Polygon, geom)
                            polys.append(poly)
                        elif geom.geom_type == "MultiPolygon":
                            multi_poly = cast(shapely.geometry.MultiPolygon, geom)
                            for poly in multi_poly.geoms:
                                polys.append(poly)

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
        join_style: BufferJoinStyle | Literal["round", "mitre", "bevel"],
        mitre_limit: float,
    ) -> shapely.geometry.MultiPolygon:
        """
        main method
        """
        polys : list[shapely.geometry.Polygon] = []

        # MatplotLibUtils.display("geometry", self.multipoly)

        for poly in self.multipoly.geoms:
            if not poly.interiors:
                continue

            linestrings = []
            for interior in poly.interiors:
                linestring = shapely.geometry.LineString(interior)
                linestrings.append(linestring)

            int_offsets = []
            for linestring in linestrings:
                int_offset = linestring.parallel_offset(
                    amount,
                    side,
                    resolution=resolution,
                    join_style=join_style,
                    mitre_limit=mitre_limit,
                )

                int_offsets.append(int_offset)

            # from the offseted lines, build a multipolygon that we will diff with the exterior
            interior_multipoly = ShapelyUtils.build_multipoly_from_offsets(int_offsets)

            # MatplotLibUtils.display("interior_multipoly", interior_multipoly)

            if not interior_multipoly.is_valid:
                interior_multipoly = ShapelyUtils.fix_multipoly(interior_multipoly)

            exterior_multipoly = ShapelyUtils.offset_multipolygon(
                self.multipoly, amount, "left", consider_interiors_offsets=True
            )

            # MatplotLibUtils.display("exterior_multipoly", exterior_multipoly)

            # only exterior
            exterior_multipoly = ShapelyUtils.remove_multipoly_holes(exterior_multipoly)

            # this simplify may be important so that the offset becomes Ok (example: letter "B")
            exterior_multipoly = ShapelyUtils.simplify_multipoly(
                exterior_multipoly, 0.001
            )
            exterior_multipoly = ShapelyUtils.orient_multipolygon(exterior_multipoly)

            # MatplotLibUtils.display("exterior_multipoly", exterior_multipoly)

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
                    poly = cast(shapely.geometry.Polygon, sol_poly)
                    polys.append(poly)
                elif sol_poly.geom_type == "MultiPolygon":
                    multi_poly = cast(shapely.geometry.MultiPolygon, sol_poly)
                    for poly in multi_poly.geoms:
                        polys.append(poly)
                elif sol_poly.geom_type == "GeometryCollection":
                    collection = cast(shapely.geometry.GeometryCollection, sol_poly)
                    for geom in collection.geoms:
                        if geom.geom_type == "Polygon":
                            poly = cast(shapely.geometry.Polygon, geom)
                            polys.append(poly)
                        elif geom.geom_type == "MultiPolygon":
                            xgeom = cast(shapely.geometry.MultiPolygon, geom)
                            for poly in xgeom.geoms:
                                polys.append(poly)

            else:  # without exterior
                for poly in interior_multipoly.geoms:
                    if poly.geom_type == "Polygon":
                        poly = cast(shapely.geometry.Polygon, poly)
                        polys.append(poly)

        o_multipoly = ShapelyUtils.build_multipoly_from_list_of_polygons(polys)

        # ensure orientation
        o_multipoly = ShapelyUtils.orient_multipolygon(o_multipoly)

        return o_multipoly
