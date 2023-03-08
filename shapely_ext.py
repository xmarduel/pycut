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

import shapely.geometry
import shapely.ops
from shapely.validation import make_valid
from shapely.geometry.base import JOIN_STYLE

from shapely_utils import ShapelyUtils
from matplotlib_utils import MatplotLibUtils


class ShapelyPolygonOffset:
    '''
    The class to perform an offset of a polygon.
    It has to take care of the possible interiors of the polygon
    '''
    def __init__(self, poly: shapely.geometry.Polygon):
        '''
        '''
        # input
        self.poly = poly

        # output: results of the offset operation
        # - the resulting multi polygon
        self.res_multipoly : shapely.geometry.MultiPolygon = None 

        # Note that some lines can be "degenerated" : we take them into account for the cam paths
        # but maybe do not corespond to any polygon.
        # this means: the exteriors of the multi polygons do not correspond to the full cam paths TO CHECK

    def offset(self, amount:float, side: str, consider_interiors_offsets: bool, resolution: int, join_style: JOIN_STYLE, mitre_limit:float):
        '''
        '''
        linestring = shapely.geometry.LineString(self.poly.exterior)

        # LineString or MultiLineString
        ext_offset = linestring.parallel_offset(amount, side, resolution=resolution, join_style=join_style, mitre_limit=mitre_limit)
            
        # from the offsetted lines, build a multipolygon that we will diff with the interiors
        exterior_multipoly = ShapelyPolygonOffset.buildMultiPolyFromOffset(ext_offset)
            
        # now consider the interiors
        if self.poly.interiors:

            interior_polys = []
            for interior in self.poly.interiors:
                ipoly = shapely.geometry.Polygon(interior)

                # simplify the polygon 
                # this may be important so that the offset becomes Ok (example: tudor [AD])
                # where of offset is a MultiLineString instead of a Linestring 
                ipoly = ipoly.simplify(0.001)
                ipoly = shapely.geometry.polygon.orient(ipoly)
                
                interior_polys.append(ipoly)
                
            interior_multipoly = ShapelyUtils.buildMultiPolyFromListOfPolygons(interior_polys)

            # consider interiors and their offsets
            if consider_interiors_offsets == True:
                MatplotLibUtils.MatplotlibDisplay("starting interior offset from", interior_multipoly)

                interiors_polys = []

                for interior in interior_multipoly.geoms:
                    interior_offseter = ShapelyPolygonOffset(interior)
                    interior_offseter.offset(amount, 'right', False, resolution, join_style, mitre_limit)

                    i_multipoly = interior_offseter.res_multipoly

                    interiors_polys = interiors_polys + list(i_multipoly.geoms)
                    
                for k, i_poly in enumerate(interiors_polys):
                    MatplotLibUtils.MatplotlibDisplay("interior offseting (linestring) %d" % k, i_poly)
                    
                interior_multipoly = ShapelyUtils.buildMultiPolyFromListOfPolygons(interiors_polys)

                MatplotLibUtils.MatplotlibDisplay("resulting multipolygon of interior offset", interior_multipoly)

            # the diff is the solution
            try:
                sol_poly = exterior_multipoly.difference(interior_multipoly)
                
                MatplotLibUtils.MatplotlibDisplay("diff of interior offseting", sol_poly)
            except Exception as e :
                print("ERROR difference")
                print(e)
                print("exterior_multipoly VALID ?", exterior_multipoly.is_valid)
                print("interior_multipoly VALID ?", interior_multipoly.is_valid)
                raise

            if sol_poly.geom_type == 'Polygon':
                self.res_multipoly = shapely.geometry.MultiPolygon([sol_poly])
            elif sol_poly.geom_type == 'MultiPolygon':
                self.res_multipoly = sol_poly
            elif sol_poly.geom_type == 'GeometryCollection':
                polys = []
                for geom in sol_poly:
                    if geom.geom_type == 'Polygon':
                        polys.append(geom)
                    if geom.geom_type == 'MultiPolygon':
                        for pp in geom.geoms:
                           polys.append(pp)
                self.res_multipoly = shapely.geometry.MultiPolygon(polys)
                    
        else: # without interiors
            self.res_multipoly = exterior_multipoly

    @staticmethod
    def buildMultiPolyFromOffset(offset: shapely.geometry.LineString|shapely.geometry.MultiLineString) -> shapely.geometry.MultiPolygon:
        '''
        offset is the direct result of an parallel_offset operation -> can be of various type

        We filter the degenerated lines

        Warning: shapely offset of a Linestring can produce a MultiLineString.
        This is a problem!

        Example: an interior offset 'right' (-> become bigger) should be a LineString, not
        a MultiineString. As pycut builds from this offset polygons to diff with the offset
        of the exterior, this is a huge problem. See Tudor "AD"
        Hint: simplify the interior first, then maybe the offset is "ok" i.e. is 
        a simple LineString

        Todo: considering interiors offseted 'right', pycut could the MultiLineString 
        into a single LineString ?
        '''
        lines_ok = []
        if offset.geom_type == 'LineString':
            if len(list(offset.coords)) <=  2:
                pass
            else:
                lines_ok.append(offset)
        elif offset.geom_type == 'MultiLineString':
            for geom in offset.geoms:
                if len(list(geom.coords)) <=  2:
                    continue
                lines_ok.append(geom)
                
        # I guess all lines are valid, this is 
        # the point of the LineString/MultiLine returned value of an offset,
        # but can any line construct a valid polygon ?

        # unfortunately, there is no "make_valid" on LineString, LinearRing
       
        # so we make a "make_valid" on resulting polygons
        polygons = []
        
        for line_ok in lines_ok:
            polygon = shapely.geometry.Polygon(line_ok)

            if polygon.is_valid:
                polygons.append(polygon)
            else:
                res = polygon.make_valid()
                # hoping the result is valid!
                if res.geom_type == 'Polygon':
                    polygons.append(polygon)
                if res.geom_type == 'MultiPolygon':
                    for poly in res.geoms:
                        polygons.append(polygon)
                if res.geom_type == 'GeometryCollection':
                    for geom in res.geoms:
                        if geom.geom_type == 'Polygon':
                            polygons.append(polygon)
                        if geom.geom_type == 'MultiPolygon':
                            for poly in geom.geoms:
                                polygons.append(polygon)

        polygons_ok = []
        for poly in polygons:
            polygon = shapely.geometry.polygon.orient(poly)
            polygons_ok.append(polygon)

        multipoly = ShapelyUtils.buildMultiPolyFromListOfPolygons(polygons)

        return multipoly


class ShapelyPolygonOffsetInteriors:
    '''
    '''
    def __init__(self, poly: shapely.geometry.Polygon):
        '''
        '''
        self.poly = poly

        # result of the offset operation
        self.res_offsets : List[shapely.geometry.LineString] = [] 
        self.res_multipoly : shapely.geometry.MultiPolygon = None

    def offset(self, amount:float, side: str, consider_exteriors: bool, resolution: int, join_style: int, mitre_limit:float):
        '''
        '''
        offsets : List[shapely.geometry.LineString] = []
        polys: List[shapely.geometry.Polygon] = []

        if not self.poly.interiors: 
            self.res_offsets = []
            self.res_polys = []
            return

        linestrings = []
        for interior in self.poly.interiors:
            linestring = shapely.geometry.LineString(interior)
            linestrings.append(linestring)

        int_offsets : List[shapely.geometry.LineString|shapely.geometry.MultiLineString] = []
        for linestring in linestrings:
            int_offset = linestring.parallel_offset(amount, side, resolution=resolution, join_style=join_style, mitre_limit=mitre_limit)
            int_offsets.append(int_offset)

        # from the offseted lines, build a multipolygon that we diff with the exterior
        interior_multipoly = ShapelyUtils.buildMultiPolyFromOffsets(int_offsets)
        print("exterior_multipoly VALID ? ", interior_multipoly.is_valid)

        MatplotLibUtils.MatplotlibDisplay("interior_multipoly", interior_multipoly, force=False)
            
        if not interior_multipoly.is_valid:
            interior_multipoly = ShapelyUtils.fixMultipoly(interior_multipoly)

        offsetter = ShapelyPolygonOffset(self.poly)
        offsetter.offset(amount, 'left', True, resolution, join_style, mitre_limit)

        exterior_multipolyX = offsetter.res_multipoly


        MatplotLibUtils.MatplotlibDisplay("exterior_multipolyX", exterior_multipolyX, force=False)

        # only exterior
        exterior_multipoly = ShapelyUtils.removeHolesMultipoly(exterior_multipolyX)

        # this simplify may be important so that the offset becomes Ok (example: letter "B") 
        exterior_multipoly = ShapelyUtils.simplifyMultiPoly(exterior_multipoly, 0.001)
        exterior_multipoly = ShapelyUtils.orientMultiPolygon(exterior_multipoly)

        MatplotLibUtils.MatplotlibDisplay("exterior_multipoly", exterior_multipoly, force=False)

        #both = shapely.geometry.MultiPolygon(list(interior_multipoly.geoms) + list(exterior_multipoly.geoms))
        #MatplotLibUtils.MatplotlibDisplay("interior_exterior_multipoly", both, force=True)

        if consider_exteriors == True:
            # the diff ** with ~POLY ** is the solution
            try:
                interior_is_contained_in_exterior = exterior_multipoly.contains(interior_multipoly)
                print("XXXXXX offset -> interior_is_contained_in_exterior", interior_is_contained_in_exterior)

                if interior_is_contained_in_exterior:
                    sol_poly = exterior_multipoly.intersection(interior_multipoly)
                else:
                    # big problem! should actually never happens... (g letter)
                    sol_poly = interior_multipoly  # bug: can cut outside the exterior...
                
            except Exception as e :
                print("ERROR difference")
                print(e)
                print("interior_multipoly VALID ?", interior_multipoly.is_valid)
                print("exterior_multipoly VALID ?", exterior_multipoly.is_valid)
                raise

            if sol_poly.geom_type == 'LineString':
                offsets.append(sol_poly)
            elif sol_poly.geom_type == 'MultiLineString':
                offsets = offsets + sol_poly.geoms
            elif sol_poly.geom_type == 'Polygon':
                offset = shapely.geometry.LineString(sol_poly.exterior)
                offsets.append(offset)
                polys.append(sol_poly)
            elif sol_poly.geom_type == 'MultiPolygon':
                for geom in sol_poly.geoms:
                    offsets.append(shapely.geometry.LineString(geom.exterior))
                    polys.append(geom)
            elif sol_poly.geom_type == 'GeometryCollection':
                for geom in sol_poly.geoms:
                    if geom.geom_type == 'Polygon':
                        offsets.append(shapely.geometry.LineString(geom.exterior))
                        polys.append(geom)
                    elif geom.geom_type == 'MultiPolygon':
                        for poly in geom.geoms:
                            offsets.append(shapely.geometry.LineString(poly.exterior))
                            polys.append(poly)
                    elif geom.geom_type == 'Linestring':
                        offsets.append(shapely.geometry.LineString(line))
                    elif geom.geom_type == 'MultiLinestring':
                        for line in geom.geoms:
                            offsets.append(shapely.geometry.LineString(line))

        else: # without exterior offsets
            offsets.append(int_offset)

            for poly in interior_multipoly.geoms:
                if poly.geom_type == 'Polygon':
                    polys.append(poly)

        self.res_offsets = offsets
        self.res_multipoly = shapely.ops.unary_union(polys)

        if self.res_multipoly.geom_type == 'Polygon':
            self.res_multipoly = shapely.geometry.MultiPolygon([self.res_multipoly])

