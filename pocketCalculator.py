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
from typing import List

import shapely.geometry
import shapely.ops

from shapely_utils import ShapelyUtils
from shapely_ext import ShapelyPolygonOffset
from shapely_ext import ShapelyPolygonOffsetInteriors

from matplotlib_utils import MatplotLibUtils


class CamPath:
    '''
    CamPath has this format: {
      path:               Shapely LineString
      safeToClose:        Is it safe to close the path without retracting?
    }
    '''
    def __init__(self, path: shapely.geometry.LineString, safeToClose: bool = True):
        # shapely linestring
        self.path = path
        # is it safe to close the path without retracting?
        self.safeToClose = safeToClose


class PocketCalculator:
    '''
    !!EXPERIMENTAL!!
    '''
    def __init__(self, poly: shapely.geometry.Polygon, cutter_dia: float, overlap: float, climb: bool):
        '''
        cutter_dia is in user units. 
        overlap is in the range [0, 1].
        '''
        self.poly = poly
        self.cutter_dia = cutter_dia
        self.overlap = overlap
        self.climb = climb

        # result of a the calculation
        self.camPath : List[CamPath] = [] 

        # temp variables
        self.allPaths : List[shapely.geometry.LineString] = []

    def collect_paths(self, offset_poly: shapely.geometry.MultiPolygon):
        '''
        ''' 
        for poly in offset_poly.geoms:
            offset = poly.exterior
            if len(list(offset.coords)) > 0:
                self.allPaths.append(offset)

    def calculate(self):
        '''
        main algo
        '''
        MatplotLibUtils.MatplotlibDisplay("poly pocket init", self.poly)
        
        # use polygon exterior line - offset if and and diff with the offsetted interiors if any
        poly = shapely.geometry.polygon.orient(self.poly)

        # the exterior
        offset_poly = self.offsetPolygon(poly, self.cutter_dia / 2, 'left')
        
        offset_poly = ShapelyUtils.simplifyMultiPoly(offset_poly, 0.001)
        offset_poly = ShapelyUtils.orientMultiPolygon(offset_poly)

        if len(offset_poly.geoms) == 0:
            # cannot offset ! maybe geometry too narrow for the cutter
            return []
                
        for geom in offset_poly.geoms:
            MatplotLibUtils.MatplotlibDisplay("geom pocket init after simplify", geom)

        # bound must be the exterior enveloppe + the interiors polygons
        #bounds = geometry 

        # no! the bounds are from the first offset with width cutter_dia / 2
        bounds = shapely.geometry.MultiPolygon(offset_poly)

        # --------------------------------------------------------------------
      
        while True:
            #if climb:
            #    for line in current:
            #        line.reverse()

            self.collect_paths(offset_poly)

            offset_poly = self.offsetMultiPolygon(offset_poly, self.cutter_dia * (1 - self.overlap), 'left')
            
            if len(offset_poly.geoms) == 0:
                # cannot offset ! maybe geometry too narrow for the cutter
                break
            offset_poly = ShapelyUtils.simplifyMultiPoly(offset_poly, 0.001)
            if not offset_poly:
                break
            offset_poly = ShapelyUtils.orientMultiPolygon(offset_poly)

        # last: make beautiful interiors, only 1 step
        interiors_offsets = self.offsetPolygonInteriors(self.poly, self.cutter_dia / 2, 'left')
        self.collect_paths(interiors_offsets)
        # - done !

        self.mergePaths(bounds, self.allPaths)

    def offsetPolygon(self, poly: shapely.geometry.Polygon, amount: float, side: str, resolution=16, join_style=1, mitre_limit=5.0) -> shapely.geometry.MultiPolygon:
        '''
        '''
        offsetter = ShapelyPolygonOffset(poly)
        return offsetter.offset(amount, side, True, resolution, join_style, mitre_limit)
    
    def offsetMultiPolygon(self, multipoly: shapely.geometry.MultiPolygon, amount: float, side: str, resolution=16, join_style=1, mitre_limit=5.0) -> shapely.geometry.MultiPolygon:
        '''
        '''
        polys = []

        for poly in multipoly.geoms:
            offsetter = ShapelyPolygonOffset(poly)
            multipoly = offsetter.offset(amount, side, False, resolution, join_style, mitre_limit)

            polys.extend(list(multipoly.geoms))
        
        return shapely.geometry.MultiPolygon(polys)

    def offsetPolygonInteriors(self, poly: shapely.geometry.Polygon, amount: float, side: str, resolution=16, join_style=1, mitre_limit=5.0) -> shapely.geometry.MultiPolygon:
        '''
        '''
        offsetter = ShapelyPolygonOffsetInteriors(poly)
        return offsetter.offset(amount, side, True, resolution, join_style, mitre_limit)
    
    @classmethod
    def mergePaths(cls, _bounds: shapely.geometry.MultiPolygon, paths: List[shapely.geometry.LineString]) -> List[CamPath] :
        '''
        Try to merge paths. A merged path doesn't cross outside of bounds AND the interior polygons
        '''
        #MatplotLibUtils.MatplotlibDisplay("mergePath", shapely.geometry.MultiLineString(paths), force=True)

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
        thepaths = [ list(path.coords) for path in paths ]
        paths = thepaths

        currentPath = paths[0]
        
        pathEndPoint = currentPath[-1]
        pathStartPoint = currentPath[0]

        # close if start/end point not equal - why ? I could have simple lines!
        if pathEndPoint[0] != pathStartPoint[0] or pathEndPoint[1] != pathStartPoint[1]:
            currentPath = currentPath + [pathStartPoint]
        
        currentPoint = currentPath[-1]
        paths[0] = [] # empty

        mergedPaths : List[shapely.geometry.LineString] = [] 
        numLeft = len(paths) - 1

        while numLeft > 0 :
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
            paths[closestPathIndex] = [] # empty
            numLeft -= 1
            needNew = ShapelyUtils.crosses(ext_lines, currentPoint, path[closestPointIndex])
            if (not needNew) and int_multipoly:
                needNew = ShapelyUtils.crosses(int_multipoly, currentPoint, path[closestPointIndex])

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

        camPaths : List[CamPath] = []
        for path in mergedPaths:
            safeToClose = not ShapelyUtils.crosses(bounds, path[0], path[-1])
            camPaths.append( CamPath( shapely.geometry.LineString(path), safeToClose) )

        return camPaths