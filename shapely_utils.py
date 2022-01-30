
from typing import Tuple

import shapely.geometry as shapely_geom


class ShapelyUtils:
    '''
    Wrapper functions on Shapely
    '''
    inchToShapelyScale = 1  # Scale inch to Shapely
    cleanPolyDist = inchToShapelyScale / 1

    arcTolerance = 2.5 # like jscut

    
    @classmethod
    def diff(cls, paths1: shapely_geom.MultiLineString, paths2: shapely_geom.MultiLineString) ->  shapely_geom.MultiLineString:
        '''
        Return difference between to Clipper geometries. Returns new geometry.
        '''
        diffs = [path1.difference(path2) for (path1,path2) in zip(paths1.geoms, paths2.geoms) ]

        return shapely_geom.MultiLineString(diffs)
    

    @classmethod
    def simplifyMultiLine(cls, multiline: shapely_geom.LineString, tol: float) -> shapely_geom.MultiLineString:
        '''
        '''
        lines = []
        for line in multiline.geoms:
            xline = line.simplify(tol)
            if xline:
                lines.append(xline)
        
        if lines:
            res = shapely_geom.MultiLineString(lines)
        else:
            res = None

        return res

    @classmethod
    def offsetLine(cls, line: shapely_geom.LineString, amount: float, side, resolution=16, join_style=1, mitre_limit=5.0) -> shapely_geom.LineString:
        '''
        '''
        return line.parallel_offset(amount, side, resolution=resolution, join_style=join_style, mitre_limit=mitre_limit)

    @classmethod
    def offsetMultiLine(cls, multiline: shapely_geom.MultiLineString, amount: float, side, resolution=16, join_style=1, mitre_limit=5.0) -> shapely_geom.MultiLineString:
        '''
        '''
        offseted_lines = [cls.offsetLine(line, amount, side, resolution, join_style, mitre_limit) for line in multiline.geoms ]
        
        #  resulting linestring can be empty -> end of loop
        filtered_lines = []
        for geom in offseted_lines:
            if geom.__class__.__name__ == 'LineString':
                if geom.is_empty:
                    continue
                filtered_lines.append(geom)
            if geom.__class__.__name__ == 'MultiLineString':
                for line in geom.geoms:
                    if line.is_empty:
                        continue
                    filtered_lines.append(line)
         
        if len(filtered_lines) == 0:
            return None

        offsetted = shapely_geom.MultiLineString(filtered_lines)

        return offsetted

    @classmethod
    def offsetMultiPolygon(cls, geometry: shapely_geom.MultiPolygon, amount: float, side, resolution=16, join_style=1, mitre_limit=5.0):
        '''
        '''
        offseted_polys = []

        for poly in geometry.geoms:
            linestring = cls.polyToLineString(poly)

            linestring_offset = linestring.parallel_offset(amount, side, resolution=resolution, join_style=join_style, mitre_limit=5.0)

            print("-- offset linestring")
            print(linestring_offset)

            if linestring_offset.__class__.__name__ == 'LineString':
                offseted_polys.append(shapely_geom.Polygon(linestring_offset))
            else:
                for line in linestring_offset.geoms:
                    try:
                        offseted_polys.append(shapely_geom.Polygon(line))
                    except Exception:
                        pass

            
        offsetted = shapely_geom.MultiPolygon(offseted_polys)

        return offsetted

    @classmethod
    def polyToLineString(cls, poly: shapely_geom.Polygon):
        '''
        '''
        print(" ------------------------  poly to linestring ---")
        print(poly)
        #print(poly.is_ccw)

        linestring = shapely_geom.LineString(poly.exterior)
        
        print(linestring)
        #print(linestring.is_ccw)
        print(" ------------------------ ")

        return linestring

    @classmethod
    def polyToLinearRing(cls, poly: shapely_geom.Polygon):
        '''
        '''
        print(" ------------------------  poly to linestring ---")
        print(poly)
        #print(poly.is_ccw)

        linearring = shapely_geom.LinearRing(list(poly.exterior.coords))
        
        print(linearring)
        #print(linearring.is_ccw)
        print(" ------------------------ ")

        return linearring

    @classmethod
    def multiPolyToMultiLine(cls, multipoly: shapely_geom.MultiPolygon) -> shapely_geom.MultiLineString:
        '''
        '''
        lines = []

        for poly in multipoly.geoms:
            line = cls.polyToLineString(poly)
            lines.append(line)
        
        multiline = shapely_geom.MultiLineString(lines)
        
        return multiline

    @classmethod
    def crosses(cls, bounds, p1: Tuple[int,int], p2: Tuple[int,int]):
        '''
        Does the line from p1 to p2 cross outside of bounds?
        '''
        if bounds == None:
            return True
        if p1[0] == p2[0] and p1[0] == p2[0]:
            return False

        # JSCUT clipper.AddPath([p1, p2], ClipperLib.PolyType.ptSubject, False)
        # JSCUT clipper.AddPaths(bounds, ClipperLib.PolyType.ptClip, True)

        p1_p2 = shapely_geom.LineString([p1,p2])

       
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

       
        if result.__class__.__name__ == 'Point':
            if result.x == p1[0] and result.y == p1[1] :
                return False
            if result.x == p2[0] and result.y == p2[1] :
                return False
            
            
        return True
