
import math

from typing import List
from typing import Tuple

import shapely.geometry
from shapely.validation import make_valid

import matplotlib.pyplot as plt


class ShapelyUtils:
    '''
    Helper functions on Shapely
    '''
    @classmethod
    def diff(cls, paths1: shapely.geometry.MultiLineString, paths2: shapely.geometry.MultiLineString) -> shapely.geometry.MultiLineString:
        '''
        Return difference between to Clipper geometries. Returns new geometry.
        '''
        diffs = [path1.difference(path2) for (path1,path2) in zip(paths1.geoms, paths2.geoms) ]

        return shapely.geometry.MultiLineString(diffs)

    @classmethod
    def simplifyMultiLine(cls, multiline: shapely.geometry.MultiLineString, tol: float) -> shapely.geometry.MultiLineString:
        '''
        '''
        lines = []
        for line in multiline.geoms:
            xline = line.simplify(tol)
            if xline:
                lines.append(xline)
        
        if lines:
            res = shapely.geometry.MultiLineString(lines)
        else:
            res = None

        return res

    @classmethod
    def simplifyMultiPoly(cls, multipoly: shapely.geometry.MultiPolygon, tol: float) -> shapely.geometry.MultiPolygon:
        '''
        '''
        polys = []
        for poly in multipoly.geoms:
            xpoly = poly.simplify(tol)
            if xpoly:
                polys.append(xpoly)
        
        if polys:
            res = shapely.geometry.MultiPolygon(polys)
        else:
            res = None

        return res

    @classmethod
    def offsetLine(cls, line: shapely.geometry.LineString, amount: float, side: str, resolution=16, join_style=1, mitre_limit=5.0) -> shapely.geometry.LineString:
        '''
        '''
        return line.parallel_offset(amount, side, resolution=resolution, join_style=join_style, mitre_limit=mitre_limit)

    @classmethod
    def offsetMultiLine(cls, multiline: shapely.geometry.MultiLineString, amount: float, side: str, resolution=16, join_style=1, mitre_limit=5.0) -> shapely.geometry.MultiLineString:
        '''
        '''
        offseted_lines = [cls.offsetLine(line, amount, side, resolution, join_style, mitre_limit) for line in multiline.geoms ]
        
        # resulting linestring can be empty
        filtered_lines = []
        
        for geom in offseted_lines:
            if geom.geom_type == 'LineString':
                if geom.is_empty:
                    continue
                filtered_lines.append(geom)
            if geom.geom_type == 'MultiLineString':
                for line in geom.geoms:
                    if line.is_empty:
                        continue
                    filtered_lines.append(line)
         
        if len(filtered_lines) == 0:
            return None

        offsetted = shapely.geometry.MultiLineString(filtered_lines)

        return offsetted

    @classmethod
    def orientMultiPolygon(cls, multipoly: shapely.geometry.MultiPolygon):
        '''
        '''
        geoms = []
        for geom in multipoly.geoms:
            xgeom = shapely.geometry.polygon.orient(geom)
            geoms .append(xgeom)
        xmultipoly = shapely.geometry.MultiPolygon(geoms)

        return xmultipoly

    @classmethod
    def offsetMultiPolygon(cls, geometry: shapely.geometry.MultiPolygon, amount: float, side, ginterior=False, resolution=16, join_style=1, mitre_limit=5.0) -> shapely.geometry.MultiPolygon :
        '''
        '''
        offseted_polys = []

        for poly in geometry.geoms:
            linestring = cls.polyExteriorToLineString(poly)

            linestring_offset = linestring.parallel_offset(amount, side, resolution=resolution, join_style=join_style, mitre_limit=5.0)

            if linestring_offset.geom_type == 'LineString':
                if len(list(linestring_offset.coords)) <=  2:
                    continue
            lines_ok = []
            if linestring_offset.geom_type == 'MultiLineString':
                for line in linestring_offset.geoms:
                    if len(list(line.coords)) <=  2:
                        continue
                    lines_ok.append(line)
                linestring_offset = shapely.geometry.MultiLineString(lines_ok)


            if poly.interiors:
                # with interiors
                interior_polys = []
                for interior in poly.interiors:
                    ipoly = shapely.geometry.Polygon(interior)
                    print("ipoly VALID ? ", ipoly.is_valid)
                       
                    if ipoly.is_valid == False:
                        xx = []
                        yy = []

                        ipoly = make_valid(ipoly)
                        print(" --> ipoly VALID ? ", ipoly.is_valid)
                        print(" --> ipoly AREA ? ", ipoly.area)
    
                        DEBUG = True
                            
                        for iipoly in ipoly.geoms:
                            if iipoly.geom_type == 'Polygon':

                                if DEBUG:
                                    x1,y1 = iipoly.exterior.coords.xy
                                    xx.append(x1)
                                    yy.append(y1)

                                if iipoly.area < 1.0e-5:
                                    continue
                                interior_polys.append(iipoly)
                                     
                        if DEBUG:
                            x1 = xx[0]
                            y1 = yy[0]
                        
                            x2 = xx[1]
                            y2 = yy[1]
                 
                            plt.plot(x1,y1, 'bo-')
                            plt.plot(x2,y2, 'r+--')
                            plt.show()

                    else:
                        interior_polys.append(ipoly)
                
                mpoly = shapely.geometry.MultiPolygon(interior_polys)
                if ginterior == True:
                    mpoly = ShapelyUtils.orientMultiPolygon(mpoly)
                    mpoly = ShapelyUtils.offsetMultiPolygon(mpoly, amount, 'right')

                if linestring_offset.geom_type == 'LineString':
                    epoly = shapely.geometry.Polygon(linestring_offset)
                else:
                    epolys = []
                    for line in linestring_offset.geoms:
                        epoly = shapely.geometry.Polygon(line)
                        epolys.append(epoly)
                    epoly = shapely.geometry.MultiPolygon(epolys)

                print("epoly VALID ? ", epoly.is_valid)

                # the diff is the solution
                try:
                    sol_poly = epoly.difference(mpoly)
                except Exception as e :
  
                    x1,y1 = linestring.coords.xy
                    ipoly = interior_polys[0]
                    x2,y2 = ipoly.exterior.coords.xy
                    plt.plot(x1,y1, 'bo-')
                    plt.plot(x2,y2, 'r+--')
                    plt.show()

                    print("ERROR difference")
                    print(e)
                    raise

                if sol_poly.geom_type == 'Polygon':
                    offseted_polys.append(sol_poly)
                elif sol_poly.geom_type == 'MultiPolygon':
                    for geom in sol_poly.geoms:
                        if geom.geom_type == 'Polygon':
                            offseted_polys.append(geom)

            else: # without interiors
                if linestring_offset.geom_type == 'LineString':
                    if len(list(linestring_offset.coords)) > 2:
                        offseted_polys.append(shapely.geometry.Polygon(linestring_offset))
                else:
                    for line in linestring_offset.geoms:
                        if len(list(line.coords)) > 2:
                            offseted_polys.append(shapely.geometry.Polygon(line))
                        

        offsetted = shapely.geometry.MultiPolygon(offseted_polys)

        return offsetted

    @classmethod
    def polyExteriorToLineString(cls, poly: shapely.geometry.Polygon):
        '''
        '''
        print(" ------------------------  poly to linestring ---")

        linestring = shapely.geometry.LineString(poly.exterior)

        return linestring

    @classmethod
    def polyToLinearRing(cls, poly: shapely.geometry.Polygon):
        '''
        '''
        print(" ------------------------  poly to linestring ---")

        linearring = shapely.geometry.LinearRing(list(poly.exterior.coords))

        return linearring

    @classmethod
    def multiPolyToMultiLine(cls, multipoly: shapely.geometry.MultiPolygon) -> shapely.geometry.MultiLineString:
        '''
        '''
        lines = []

        for poly in multipoly.geoms:
            line = cls.polyExteriorToLineString(poly)
            lines.append(line)
        
        multiline = shapely.geometry.MultiLineString(lines)
        
        return multiline

    @classmethod
    def crosses(cls, bounds: shapely.geometry.MultiPolygon, p1: Tuple[int,int], p2: Tuple[int,int]):
        '''
        Does the line from p1 to p2 cross outside of bounds?
        '''
        if bounds == None:
            return True
        if p1[0] == p2[0] and p1[0] == p2[0]:
            return False

        # JSCUT clipper.AddPath([p1, p2], ClipperLib.PolyType.ptSubject, False)
        # JSCUT clipper.AddPaths(bounds, ClipperLib.PolyType.ptClip, True)

        p1_p2 = shapely.geometry.LineString([p1,p2])

       
        result = p1_p2.intersection(bounds)
    
        if result.is_empty is True:
            return False
            #child : ClipperLib.PolyNode = result.GetFirst() 
            #points = child.Contour
            #if len(points) == 2:
            #    if points[0].X == p1.X and points[1].X == p2.X and points[0].Y == p1.Y and points[1].Y == p2.Y :
            #        return False
            #    if points[0].X == p2.X and points[1].X == p1.X and points[0].Y == p2.Y and points[1].Y == p1.Y :
            #        return False

       
        if result.geom_type == 'Point':
            if result.x == p1[0] and result.y == p1[1] :
                return False
            if result.x == p2[0] and result.y == p2[1] :
                return False
            
            
        return True

    @classmethod
    def union_list_of_polygons(cls, poly_list: List[shapely.geometry.Polygon]) -> shapely.geometry.MultiPolygon :
        '''
        '''
        first = poly_list[0]

        geometry = first
        
        for poly in poly_list[1:]:
            geometry = geometry.union(poly)

        return geometry

    @classmethod
    def reorder_poly_points(cls, poly: shapely.geometry.Polygon) -> shapely.geometry.Polygon:
        '''
        Problem: shapely bug when outsiding a polygon where the stating point
        in a convex corner: at that point, the offset line 'outside' is uncorrect.

        Solution: start the list of points at a point in the middle of a segment
        (if there is one)  
        '''
        if not poly.geom_type == 'Polygon':
            return poly
            
        pts = list(poly.exterior.coords)

        # ----------------------------------------------------
        def is_inside_segment(pt, pt_left, pt_right):
            ab = (pt[0] - pt_left[0], pt[1], pt_left[1])
            ac = (pt[0] - pt_right[0], pt[1], pt_right[1])

            if (ab[0]*ab[0] + ab[1]*ab[1]) < 0.00001:
                return False
            if (ac[0]*ac[0] + ac[1]*ac[1]) < 0.00001:
                return False

            s1 = ab[0]
            s1 = ab[1]

            s2 = ac[0]
            s2 = ac[1]
            
            # a segment ?
            if math.fabs(s1*s2 - s2*s1) > 0.00001:
                return False

            # inside the segment ?
            x = pt[0]
            x1 = pt_left[0]
            x2 = pt_right[0]

            #y = pt[1]
            #y1 = pt_left[1]
            #y2 = pt_right[1]

            if math.fabs(x2-x1) < 0.00001:
                return False

            alpha = (x-x1)/(x2-x1)

            return alpha > 0
        # -----------------------------------------------------

        k_ok = None
        
        for k, pt in enumerate(pts):
            pt_prev = pts[k-1] 
            if k < len(pts) -1:
                pt_next = pts[k+1]
            else: 
                pt_next = pts[0]

            if is_inside_segment(pt, pt_prev, pt_next):
                k_ok = k
                break

        # k_ok is the right start!

        if k is not None:
            pts = pts[k_ok:] + pts[:k_ok]

            return shapely.geometry.Polygon(pts)

        return poly