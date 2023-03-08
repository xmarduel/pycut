
import math

from typing import List
from typing import Tuple

import shapely.geometry
from shapely.validation import make_valid
from shapely.validation import explain_validity

from matplotlib_utils import MatplotLibUtils


class ShapelyUtils:
    '''
    Helper functions on Shapely
    '''
    MAPLOTLIB_DEBUG = False
    #MAPLOTLIB_DEBUG = True
    cnt = 1 # matplotlin figures

    @classmethod
    def diff(cls, paths1: shapely.geometry.MultiLineString, paths2: shapely.geometry.MultiLineString) -> shapely.geometry.MultiLineString:
        '''
        Return difference between to Clipper geometries. Returns new geometry.
        '''
        diffs = [path1.difference(path2) for (path1,path2) in zip(paths1.geoms, paths2.geoms) ]

        return shapely.geometry.MultiLineString(diffs)

    @classmethod
    def crosses(cls, bounds: shapely.geometry.MultiPolygon, p1: Tuple[int,int], p2: Tuple[int,int]) -> bool:
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

        if bounds.geom_type == 'MultiPolygon':
            compound = shapely.geometry.GeometryCollection([bounds, p1_p2])
            MatplotLibUtils.MatplotlibDisplay("mergePath bounds check crosses (multipoly) : %d" % cls.cnt, compound, force=False)
        if bounds.geom_type == 'MultiLineString':
            compound = shapely.geometry.GeometryCollection([bounds, p1_p2])
            MatplotLibUtils.MatplotlibDisplay("mergePath bounds check crosses (multilines) : %d" % cls.cnt, compound, force=False)
       
        result = p1_p2.intersection(bounds)

        print("crosses: result intersection empty ? ", result.is_empty)
    
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
        if result.geom_type == 'LineString':
            return True
        if result.geom_type == 'MultiLineString':
            return True
            
            
        return True

    @classmethod
    def simplifyMultiLine(cls, multiline: shapely.geometry.MultiLineString, tol: float) -> shapely.geometry.MultiLineString | None:
        '''
        Ensure the simplification of a MultiLine is a Multiline or None
        '''
        lines = []
        for line in multiline.geoms:
            xline = line.simplify(tol)
            if xline and xline.geom_type == 'LineString':
                lines.append(xline)
        
        if lines:
            res = shapely.geometry.MultiLineString(lines)
        else:
            res = None

        return res

    @classmethod
    def simplifyMultiPoly(cls, multipoly: shapely.geometry.MultiPolygon, tol: float) -> shapely.geometry.MultiPolygon | None:
        '''
        Ensure the simplification of a MultiPolygon is a MultiPolygon or None
        '''
        polys = []
        for poly in multipoly.geoms:
            xpoly = poly.simplify(tol)
            if xpoly and xpoly.geom_type == 'Polygon':
                polys.append(xpoly)
        
        if polys:
            res = shapely.geometry.MultiPolygon(polys)
        else:
            res = None

        return res

    @classmethod
    def offsetLine(cls, line: shapely.geometry.LineString, amount: float, side: str, resolution=16, join_style=1, mitre_limit=5.0) -> shapely.geometry.LineString | shapely.geometry.MultiLineString:
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
    def orientMultiPolygon(cls, multipoly: shapely.geometry.MultiPolygon) -> shapely.geometry.MultiPolygon:
        '''
        '''
        geoms = []
        for geom in multipoly.geoms:
            xgeom = shapely.geometry.polygon.orient(geom)
            geoms.append(xgeom)
        
        xmultipoly = shapely.geometry.MultiPolygon(geoms)

        return xmultipoly

    @classmethod
    def offsetMultiPolygon(cls, geometry: shapely.geometry.MultiPolygon, amount: float, side, ginterior=False, resolution=16, join_style=1, mitre_limit=5.0) -> Tuple[List[shapely.geometry.MultiLineString], shapely.geometry.MultiPolygon] :
        '''
        Generate offseted lines from the polygons. All the produced lines are good 
        to store in the toolpaths.

        The returned MultiPolygon is generated from these, but after having eliminated the degenerated ones
        '''
        offsets = [] # for each poly in the multipoly - each item can be of various types
        polys = []

        for poly in geometry.geoms:

            linestring = shapely.geometry.LineString(poly.exterior)

            ext_offset = linestring.parallel_offset(amount, side, resolution=resolution, join_style=join_style, mitre_limit=5.0)
            
            # from the offseted lines, build a multipolygon that we diff with the interiors
            exterior_multipoly = cls.buildMultiPolyFromOffsets([ext_offset])
            print("exterior_multipoly VALID ? ", exterior_multipoly.is_valid)
            
            if not exterior_multipoly.is_valid:
                exterior_multipoly = cls.fixMultipoly(exterior_multipoly)

            # now consider the interiors
            if poly.interiors:

                # consider interiors and their offsets
                interior_polys = []
                for interior in poly.interiors:
                    ipoly = shapely.geometry.Polygon(interior)
                    interior_polys.append(ipoly)
                
                interior_multipoly = ShapelyUtils.buildMultiPolyFromListOfPolygons(interior_polys)

                if ginterior == True:
                    MatplotLibUtils.MatplotlibDisplay("starting interior offset from", interior_multipoly)

                    interior_offset, _ = ShapelyUtils.offsetMultiPolygon(interior_multipoly, amount, 'right')
                    
                    for k, offset in enumerate(interior_offset):
                        MatplotLibUtils.MatplotlibDisplay("interior offseting (linestring) %d" % k, offset)
                    
                    # the diff is the solution
                    interior_multipoly = ShapelyUtils.buildMultiPolyFromOffsets(interior_offset)
                
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
                    offset = shapely.geometry.LineString(sol_poly.exterior)
                    offsets.append(offset)
                    polys.append(sol_poly)
                elif sol_poly.geom_type == 'MultiPolygon':
                    _offsets = []
                    for geom in sol_poly.geoms:
                        if geom.geom_type == 'Polygon':
                            offset = shapely.geometry.LineString(geom.exterior)
                            _offsets.append(offset)
                            polys.append(geom)
                    offset = shapely.geometry.MultiLineString(_offsets)
                    offsets.append(offset)

            else: # without interiors
                offsets.append(ext_offset)

                for poly in exterior_multipoly.geoms:
                    if poly.geom_type == 'Polygon':
                        polys.append(poly)

        multipoly = shapely.geometry.MultiPolygon(polys)
        # ensure orientation
        multipoly = ShapelyUtils.orientMultiPolygon(multipoly)

        return offsets, multipoly

    @classmethod
    def offsetMultiPolygonInteriors(cls, geometry: shapely.geometry.MultiPolygon, amount: float, side, gexterior=False, resolution=16, join_style=1, mitre_limit=5.0) -> Tuple[List[shapely.geometry.MultiLineString], shapely.geometry.MultiPolygon] :
        '''
        Generate offseted lines from the polygons. All the produced lines are good 
        to store in the toolpaths.

        The returned MultiPolygon is generated from these, but after having eliminated the degenerated ones
        '''
        offsets = [] # for each poly in the multipoly - each item can be of various types
        polys = []

        MatplotLibUtils.MatplotlibDisplay("geometry", geometry, force=False)

        for poly in geometry.geoms:

            if not poly.interiors: 
                continue

            linestrings = []
            for interior in poly.interiors:
                linestring = shapely.geometry.LineString(interior)
                linestrings.append(linestring)

            int_offsets = []
            for linestring in linestrings:
                int_offset = linestring.parallel_offset(amount, side, resolution=resolution, join_style=join_style, mitre_limit=5.0)
                int_offsets.append(int_offset)

            # from the offseted lines, build a multipolygon that we diff with the exterior
            interior_multipoly = cls.buildMultiPolyFromOffsets(int_offsets)
            print("exterior_multipoly VALID ? ", interior_multipoly.is_valid)

            MatplotLibUtils.MatplotlibDisplay("interior_multipoly", interior_multipoly, force=False)
            
            if not interior_multipoly.is_valid:
                interior_multipoly = cls.fixMultipoly(interior_multipoly)

            _, exterior_multipolyX = ShapelyUtils.offsetMultiPolygon(geometry, amount, 'left', ginterior=True)

            MatplotLibUtils.MatplotlibDisplay("exterior_multipolyX", exterior_multipolyX, force=False)

            # only exterior
            exterior_multipoly = cls.removeHolesMultipoly(exterior_multipolyX)

            # this simplify may be important so that the offset becomes Ok (example: letter "B") 
            exterior_multipoly = ShapelyUtils.simplifyMultiPoly(exterior_multipoly, 0.001)
            exterior_multipoly = ShapelyUtils.orientMultiPolygon(exterior_multipoly)

            MatplotLibUtils.MatplotlibDisplay("exterior_multipoly", exterior_multipoly, force=False)

            #both = shapely.geometry.MultiPolygon(list(interior_multipoly.geoms) + list(exterior_multipoly.geoms))
            #MatplotLibUtils.MatplotlibDisplay("interior_exterior_multipoly", both, force=True)

            if gexterior == True:
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
                    offset = shapely.geometry.LineString(sol_poly)
                    offsets.append(offset)
                elif sol_poly.geom_type == 'MultiLineString':
                    for line in sol_poly.geoms:
                        offset = shapely.geometry.LineString(line)
                        offsets.append(offset)
                elif sol_poly.geom_type == 'Polygon':
                    offset = shapely.geometry.LineString(list(sol_poly.exterior.coords))
                    offsets.append(offset)
                    polys.append(sol_poly)
                elif sol_poly.geom_type == 'MultiPolygon':
                    _offsets = []
                    for geom in sol_poly.geoms:
                        offset = shapely.geometry.LineString(geom.exterior)
                        _offsets.append(offset)
                        polys.append(geom)
                    offset = shapely.geometry.MultiLineString(_offsets)
                    offsets.append(offset)
                elif sol_poly.geom_type == 'GeometryCollection':
                    _offsets = []
                    for geom in sol_poly.geoms:
                        if geom.geom_type == 'Polygon':
                            offset = shapely.geometry.LineString(geom.exterior)
                            _offsets.append(offset)
                            polys.append(geom)
                        elif geom.geom_type == 'MultiPolygon':
                            for poly in geom.geoms:
                                offset = shapely.geometry.LineString(poly.exterior)
                                _offsets.append(offset)
                                polys.append(poly)
                        elif geom.geom_type == 'Linestring':
                            offset = shapely.geometry.LineString(line)
                            _offsets.append(offset)
                        elif geom.geom_type == 'MultiLinestring':
                            for line in geom.geoms:
                                offset = shapely.geometry.LineString(line)
                                _offsets.append(offset)
                    offset = shapely.geometry.MultiLineString(_offsets)
                    offsets.append(offset)

            else: # without exterior
                offsets.append(int_offset)

                for poly in interior_multipoly.geoms:
                    if poly.geom_type == 'Polygon':
                        polys.append(poly)

        multipoly = shapely.geometry.MultiPolygon(polys)
        # ensure orientation
        multipoly = ShapelyUtils.orientMultiPolygon(multipoly)

        return offsets, multipoly

    @classmethod
    def buildMultiPolyFromOffsets(cls, multi_offset: List[shapely.geometry.LineString|shapely.geometry.MultiLineString]) -> shapely.geometry.MultiPolygon:
        '''
        offset is the direct result of an parallel_offset operation -> can be of various type

        We filter the degenerated lines
        '''
        polygons = []

        for offset in multi_offset:
            lines_ok = []
            if offset.geom_type == 'LineString':
                if len(list(offset.coords)) <=  2:
                    pass
                else:
                    lines_ok.append(offset)
            elif offset.geom_type == 'MultiLineString':
                for geom in offset.geoms:
                    if geom.geom_type == 'LineString':
                        if len(list(geom.coords)) <=  2:
                            continue
                        lines_ok.append(geom)
            else:
                1/0
                
            for line_ok in lines_ok:
                polygon = shapely.geometry.Polygon(line_ok)

                if  polygon.is_valid:
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

    @classmethod
    def buildMultiPolyFromListOfPolygons(cls, polygons: List[shapely.geometry.Polygon]) -> shapely.geometry.MultiPolygon:
        '''
        '''
        union = shapely.ops.unary_union(polygons)

        if union.geom_type == 'Polygon':
            multipoly = shapely.geometry.MultiPolygon([union])
        elif union.geom_type == 'MultiPolygon':
            multipoly = union
        elif union.geom_type == 'GeometryCollection':
            polygons = []
            for item in union.geoms:
                if item.geom_type == 'Polygon':
                    polygons.append(item)
                elif union.geom_type == 'MultiPolygon':
                    polygons = polygons + list(union.geoms)
            multipoly = shapely.geometry.MultiPolygon(polygons)    
        
        # ensure orientation
        multipoly = ShapelyUtils.orientMultiPolygon(multipoly)
        print("multipoly VALID ?", multipoly.is_valid)

        return multipoly

    @classmethod
    def multiPolyToMultiLine(cls, multipoly: shapely.geometry.MultiPolygon) -> shapely.geometry.MultiLineString:
        '''
        '''
        lines = []

        for poly in multipoly.geoms:
            line = shapely.geometry.LineString(poly.exterior)
            lines.append(line)
        
        multiline = shapely.geometry.MultiLineString(lines)
        
        return multiline

    @classmethod
    def multiPolyIntToMultiLine(cls, multipoly: shapely.geometry.MultiPolygon) -> shapely.geometry.MultiLineString:
        '''
        '''
        lines = []

        for poly in multipoly.geoms:
            for interior in poly.interiors:
                line = shapely.geometry.LineString(interior)
                lines.append(line)
        
        multiline = shapely.geometry.MultiLineString(lines)
        
        return multiline

    @classmethod
    def multiLineToMultiPoly(cls, multiline: shapely.geometry.MultiLineString) -> shapely.geometry.MultiPolygon:
        '''
        '''
        polys = []

        for line in multiline.geoms:
            poly = shapely.geometry.Polygon(line)
            polys.append(poly)

        multipoly = shapely.geometry.MultiPolygon(polys)
        multipoly = make_valid(multipoly)
        
        return multipoly

    @classmethod
    def removeHolesMultipoly(cls, multipoly: shapely.geometry.MultiPolygon) -> shapely.geometry.MultiPolygon:
        epolys = []
        
        for poly in multipoly.geoms:
            line = shapely.geometry.LineString(poly.exterior)
            epoly = shapely.geometry.Polygon(line)

            epolys.append(epoly)

        return shapely.geometry.MultiPolygon(epolys)

    @classmethod
    def union_polygons(cls, poly_list: List[shapely.geometry.Polygon]) -> shapely.geometry.MultiPolygon :
        '''
        union the polygons together of after the other
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

    @classmethod
    def fixMultipoly(cls, multipoly: shapely.geometry.MultiPolygon) -> shapely.geometry.MultiPolygon :
        '''
        '''
        valid_polys = []

        for poly in multipoly.geoms:
            if not poly.is_valid:
                fixed_poly = cls.fixGenericPolygon(poly)
                valid_polys.append(fixed_poly)
            else:
                valid_polys.append(poly)

        return shapely.geometry.MultiPolygon(valid_polys)

    @classmethod
    def fixSimplePolygon(cls, polygon: shapely.geometry.Polygon) -> shapely.geometry.Polygon :
        '''
        '''
        valid = make_valid(polygon)

        if valid.geom_type == 'Polygon':
            return valid

        elif valid.geom_type == 'MultiPolygon':
            # take the largest one! CHECKME
            largest_area = -1
            largest_poly = None
            for poly in valid.geoms:
                area = poly.area
                if area > largest_area:
                    largest_area = area
                    largest_poly = poly

            return largest_poly

        elif valid.geom_type == 'GeometryCollection':
            # shit - FIXME  # take the largest Polygon
            largest_area = -1
            largest_poly = None

            for geom in valid.geoms:
                if geom.geom_type == 'Polygon':
                    area = geom.area
                    if area > largest_area:
                        largest_area = area
                        largest_poly = geom
                elif geom.geom_type == 'MultiLineString':
                    pass
                elif geom.geom_type == 'LineString':
                    pass
                
            return largest_poly

        return None

    @classmethod
    def fixGenericPolygon(cls, polygon: shapely.geometry.Polygon) -> shapely.geometry.Polygon :
        '''
        fix exterior and interiors if not valid
        '''
        if polygon.is_valid:
            return polygon

        exterior = polygon.exterior
        interiors = polygon.interiors

        ext_poly = shapely.geometry.Polygon(exterior)
        if not ext_poly.is_valid:
            ext_poly = cls.fixSimplePolygon(ext_poly)

        if not interiors:
            ext_linestring = shapely.geometry.LineString(ext_poly.exterior)

            fixed_poly = shapely.geometry.Polygon(ext_linestring)
        else:
            fixed_interiors : List[shapely.geometry.Polygon] = []
            for interior in interiors:
                int_poly = shapely.geometry.Polygon(interior)

                if not int_poly.is_valid:
                    int_poly = cls.fixSimplePolygon(int_poly)

                fixed_interiors.append(int_poly)

            ext_linestring = shapely.geometry.LineString(ext_poly.exterior)
            holes_linestrings = [shapely.geometry.LineString(int_poly.exterior) for int_poly in fixed_interiors] 

            fixed_poly = shapely.geometry.Polygon(ext_linestring, holes=holes_linestrings)

        return fixed_poly
