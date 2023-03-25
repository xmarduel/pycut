import os
import math
import copy

from typing import List
from typing import Tuple
from typing import Dict

import io

import numpy as np
import svgpathtools
import svgelements

import shapely.geometry
import shapely.validation
from shapely.validation import make_valid
from shapely.validation import explain_validity

from shapely_matplotlib import MatplotLibUtils


M_PI = math.acos(-1)

'''
SVG paths:

9.3.3. The "moveto" commands
============================
The "moveto" commands (M or m) must establish a new initial point and a new current point. 
The effect is as if the "pen" were lifted and moved to a new location. 
A path data segment (if there is one) must begin with a "moveto" command. 
Subsequent "moveto" commands (i.e., when the "moveto" is not the first command) represent 
the start of a new subpath

9.3.4. The "closepath" command
==============================
The "closepath" (Z or z) ends the current subpath by connecting it back to its initial point. 
An automatic straight line is drawn from the current point to the initial point of the current subpath. 
This path segment may be of zero length.

If a "closepath" is followed immediately by a "moveto", then the "moveto" identifies the start point 
of the next subpath. If a "closepath" is followed immediately by any other command, 
then the next subpath starts at the same initial point as the current subpath.
...
If a "closepath" is followed immediately by a "moveto", then the "moveto" identifies 
the start point of the next subpath. If a "closepath" is followed immediately by any other command, 
then the next subpath must start at the same initial point as the current subpath.


PYCUT IMPORT RULES:
1. subpaths are defined starting with [Mm]. Hopefully the path starts with [Mm]
2. every closed path (Zz) forms a polygon; if not it is a line
3. first point of a polygon|line (after a [Zz]) is given with the [Mm] data .
4. if not [Mm] after [Zz], initial point is the previous initial point
5. we use shapely to query if subpaths as interiors of polygons or if subpaths are separated polygons 
'''

class SvgPath:
    '''
    Transform svgpathtools 'Path' into a 'Shapely Polygon' object(s)

    - svgpathtools 'Path' are list of 'Segment(s)' and
    each segment has a list of points, given in format 'complex type' (a+bj)

    - a svg path can describe 1 or more Polygons, Polygons may have holes

    Convention:
    - a path from svgpathtools is noted: svg_path
    - a svg <path> definition is noted: svg_path_d
    - the discretization of a svg_path results in a numpy array, noted: np_svg_path
    '''
    PYCUT_SAMPLE_LEN_COEFF = 10 # 10 points per "svg unit" ie arc of len 10 -> 100 pts discretization
    PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5 # is in jsCut 1

    DISCRETIZATION_USE_MODULE = 'SVGPATHTOOLS'
    #DISCRETIZATION_USE_MODULE = 'SVGELEMENTS'

    @classmethod
    def set_arc_precision(cls, arc_precision: float):
        '''
        '''
        cls.PYCUT_SAMPLE_LEN_COEFF = 1.0 / arc_precision

    @classmethod
    def set_arc_min_nb_segments(cls, arc_min_nb_segments: int):
        '''
        '''
        cls.PYCUT_SAMPLE_MIN_NB_SEGMENTS = arc_min_nb_segments

    @classmethod
    def svg2paths_from_string(cls, svg_str: str) -> Tuple[List[svgpathtools.Path], List[Dict[str,str]]]:
        '''
        From a svg file content, read all paths and their attributes
        '''
        data = io.StringIO(svg_str)

        return svgpathtools.svg2paths(data)

    @classmethod
    def read_svg_shapes_as_paths(cls, svg_str: str) -> Dict[str, Tuple[svgpathtools.Path, Dict[str,str]]] :
        '''
        From a svg file content, read all paths and their attributes
        and organize them as dictionary with key <path_id>, value (path, attribs)
        '''
        svg_shapes = {}

        paths, attributes = cls.svg2paths_from_string(svg_str)

        for k, path in enumerate(paths):
            attribs = attributes[k]

            path_id = attribs.get('id', None)
            print("============= svg : path %s =================" % path_id)

            # ignore paths without id
            if path_id is None:
                continue

            svg_shapes[path_id] = (path, attribs)

        return svg_shapes

    def __init__(self, p_id: str, p_attrs: Dict[str,str]):
        '''
        '''
        # the 'id' of a svg <path> definition
        self.p_id = p_id
        # the attributes of the <path> definition
        self.p_attrs = p_attrs

        # svgpathtools: the svgpath as instance of type 'svgpathtools.Path' extracted from the string p_attrs["d"]
        if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
            self.svg_path : svgpathtools.Path = svgpathtools.parse_path(self.p_attrs['d']) 
        # svgelements
        elif self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
            self.svg_path : svgelements.Path = svgelements.Path(self.p_attrs['d'])
        else:
            self.svg_path = None

        # the result of the import
        self.lines : List[shapely.geometry.LineString] = []
        self.polys : List[shapely.geometry.Polygon] = []

    def discretize_closed_path(self) -> np.array :
        '''
        Transform the svg_path (a list of svgpathtools Segments) into a list of 'complex' points
        - Line: only 2 points
        - Arc: discretize per hand
        - QuadraticBezier, CubicBezier: discretize per hand

        SHAPELY TRICK: shapely does not handle correctly Linestring which start/end point is a corner
        => add in the first calculated segment a "middle point" and set this middle point as starting
        point of the path. Finally, at the end of the path, the "old" starting point in then the **last**
        point of the path 

        SHAPELY WARNING: it is **extremely important** not to duplicate identical points (or nearly identical) 
        because shapely may find that it creates an "invalid" polygon with the reason:
        
        >>>>> Self-intersection[184.211463517 186.153838406]

        This occurs if the sequence of points is like the following:

        184.24701507756535 186.2492779464199
        184.211463517 186.15383840599998
        184.211463517 186.153838406
        184.86553017294605 185.57132365078505

        so between 2 svg paths "segments", avoid duplicating the point at the end of the first segment and 
        the one at the beginning of the second segment.
        '''
        SEGMENT_IGNORE_THRESHOLD = 1.0e-5
        # -----------------------------------------------------------------
        def ignore_segment(k, segment) -> bool:
            '''
            for letters, very small segments can lead to unvalid geometries.
            We can fix them with the "make_valid" function but I would like
            to avoid this. It seems to be caused by very little segments which 
            are somehow wrong (or rounding values stuff makes them wrong).
            '''
            if segment.length() < SEGMENT_IGNORE_THRESHOLD :
                print("segment[%i]: %lf  -> ignoring" % (k, segment.length()) )
                return True

            return False
        # ------------------------------------------------------------------
        points = np.array([], dtype=np.complex128)

        first_pt = None
        
        for k, segment in enumerate(self.svg_path):

            ## ---------------------------------------
            if ignore_segment(k, segment) == True:
                continue
            ## ---------------------------------------
            
            if k == 0:
                # shapely fix : global initial pt
                first_pt = segment.point(0)

            if segment.__class__.__name__ == 'Line':
                # start and end points
                if len(self.svg_path) == 1:
                    if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
                        pts = segment.points([0,1])
                    #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
                    #    pts = [segment.point(0.0), segment.point(1.0)]
                else:
                    if k == 0:
                        if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
                            pts = segment.points([0.5, 1]) # shapely fix!
                        #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
                        #    pts = [segment.point(0.5), segment.point(1.0)] # shapely fix!
                    else:
                        if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
                            pts = segment.points([1])
                        #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
                        #    pts = [segment.point(1.0)] # shapely fix!
                    
            elif segment.__class__.__name__ == 'Arc':
                # no 'points' method for 'Arc'!
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                _pts = []
                if k == 0:
                    for p in range(0, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))
                else:
                    # not the first one
                    for p in range(1, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                _pts = []

                ### SVGPATHTOOLS BUG !!!
                if seg_length == math.inf:  # WTF!

                    p1 = segment.start
                    p2 = segment.end

                    if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
                        line = svgpathtools.Line(p1, p2)
                    #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
                    #    line = svgelements.Line(p1, p2)

                    # start and end points
                    if len(self.svg_path) == 1:
                        _pts = line.points([0,1])
                    else:
                        if k == 0:
                            _pts = line.points([0.5, 1]) # shapely fix!
                        else:
                            _pts = line.points([1])

                else:

                    nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                    nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                    # not the first one
                    for p in range(1, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            points = np.concatenate((points, pts))

        # shapely fix : add as last point the "virtual" first one, the first "middle one" is already the "new" first

        # distance between the last pt and and stored first pt

        if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
            line = svgpathtools.Line(points[-1], first_pt)
        #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
        #    line = svgelements.Line(points[-1], first_pt)

        # test it
        ignore = ignore_segment(-1, line)

        if ignore == True:
            pass
        else:
            points = np.concatenate((points, [first_pt]))

        #print(points)

        return points

    def discretize_opened_path(self) -> np.array :
        '''
        Transform the svg_path (a list of svgpathtools Segments) into a list of 'complex' points
        - Line: only 2 points
        - Arc: discretize per hand
        - QuadraticBezier, CubicBezier: discretize per hand

        WE DO NOT APPLY OUR SHAPELY TRICK FOR CLOSED PATHS

        SHAPELY WARNING: it is **extremely important** not to duplicate identical points (or nearly identical) 
        because shapely may find that it creates an "invalid" polygon with the reason:
        
        >>>>> Self-intersection[184.211463517 186.153838406]

        This occurs if the sequence of points is like the following:

        184.24701507756535 186.2492779464199
        184.211463517 186.15383840599998
        184.211463517 186.153838406
        184.86553017294605 185.57132365078505

        so between 2 svg paths "segments", avoid duplicating the point at the end of the first segment and 
        the one at the beginning of the second segment.
        '''
        SEGMENT_IGNORE_THRESHOLD = 1.0e-5
        # -----------------------------------------------------------------
        def ignore_segment(k, segment) -> bool:
            '''
            for letters, very small segments can lead to unvalid geometries.
            We can fix them with the "make_valid" function but I would like
            to avoid this. It seems to be caused by very little segments which 
            are somehow wrong (or rounding values stuff makes them wrong).
            '''
            if segment.length() < SEGMENT_IGNORE_THRESHOLD :
                print("segment[%i]: %lf  -> ignoring" % (k, segment.length()) )
                return True

            return False
        # ------------------------------------------------------------------
        points = np.array([], dtype=np.complex128)
        
        for k, segment in enumerate(self.svg_path):

            ## ---------------------------------------
            if ignore_segment(k, segment) == True:
                continue
            ## ---------------------------------------

            if segment.__class__.__name__ == 'Line':
                # start and end points
                if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
                    pts = segment.points([0, 1])
                #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
                #    pts = [segment.point(0.0), segment.point(1.0)] 
                else:
                    if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
                        pts = segment.points([1])
                    #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
                    #    pts = [segment.point(1.0)] 
                    
            elif segment.__class__.__name__ == 'Arc':
                # no 'points' method for 'Arc'!
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                _pts = []
                if k == 0:
                    for p in range(0, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))
                else:
                    # not the first one
                    for p in range(1, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                _pts = []

                ### SVGPATHTOOLS BUG !!!
                if seg_length == math.inf:  # WTF!

                    p1 = segment.start
                    p2 = segment.end

                    if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
                        line = svgpathtools.Line(p1, p2)
                    #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
                    #    line = svgelements.Line(p1, p2)

                    # start and end points
                    if len(self.svg_path) == 1:
                        _pts = line.points([0,1])
                    else:
                        if k == 0:
                            _pts = line.points([0, 1])
                        else:
                            _pts = line.points([1])

                else:

                    nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                    nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                    # not the first one
                    for p in range(1, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            points = np.concatenate((points, pts))

        return points

    def _is_simple_path(self) -> bool:
        '''
        check if path is a 'simple' one or a 'complex' one -
        in the sense there is no "jump" in the path (svg [mM]) excepted the initial one
        '''
        d_def = self.p_attrs["d"]

        nb_separate_paths = d_def.count("M") + d_def.count("m")

        return nb_separate_paths == 1

    def _is_subpath_closed(self) -> bool:
        '''
        check if a subpath is "closed"
        '''
        d_def = self.p_attrs["d"]

        nb_z = d_def.count("Z") + d_def.count("z") # one or zero

        return nb_z != 0
    
    def _generate_simple_svgpaths(self) -> List['SvgPath']:
        '''
        From an instance of SvgPath, generate a list of SvgPath
        where all subpaths of the object list are a 'simple' paths 
        '''
        # make all "m" -> "M" for the subpaths
        path_abs = self.svg_path.d()    # thanks svgpathtools! ... but closing "Z" is/are missing!                          

        # it's easy now
        subpaths = path_abs.split("M")

        svgpaths = []
        for k, subpath in enumerate(subpaths):
            subpath = subpath.strip()
            if not subpath:
                continue
            p_id = self.p_id + "___sub_%d" % k 
            p_attrs = copy.deepcopy(self.p_attrs)
            p_attrs["d"] = "M " + subpath + " Z"  # FIXME: how to know ??
            o = SvgPath(p_id, p_attrs)
            svgpaths.append(o)
        
        return svgpaths

    def import_subpath_as_linestring(self) -> shapely.geometry.LineString:
        '''
        '''
        pts = self.discretize_opened_path()

        coordinates = [ (complex_pt.real, complex_pt.imag)  for complex_pt in pts ]

        line = shapely.geometry.LineString(coordinates)

        return line

    def import_subpath_as_polygon(self) -> shapely.geometry.Polygon:
        '''
        '''
        pts = self.discretize_closed_path()

        coordinates = [ (complex_pt.real, complex_pt.imag)  for complex_pt in pts ]

        poly = shapely.geometry.Polygon(coordinates)

        return poly

    def import_as_lines_list(self) -> List[shapely.geometry.LineString]:
        '''
        '''
        self.import_svgpath()

        return self.lines

    def import_as_polygons_list(self) -> List[shapely.geometry.Polygon]:
        '''
        '''
        self.import_svgpath(process_holes=True)

        return self.polys
    
    def import_as_multipolygons_list(self) -> List[shapely.geometry.MultiPolygon]:
        '''
        we pack separated polys into multipolys

        Thus there can be a list of multipolys if not all polys are separated
        '''
        self.import_svgpath(process_holes=True)

        polyss_well_separated = [ [self.polys[0]] ]

        for poly in self.polys[1:]:
            inserted = False
            for poly_list in polyss_well_separated:
                if poly.intersection(shapely.geometry.MultiPolygon(poly_list)).is_empty:
                    # well separated
                    inserted = True
                    poly_list.append(poly)
                    break

            if inserted == False:
                # a new, independent multipoly 
                polyss_well_separated.append( [poly] )
        

        multipolys = [ shapely.geometry.MultiPolygon(polys) for polys in polyss_well_separated ]

        return multipolys

    def import_svgpath(self, process_holes=False):
        '''
        The main method to import a svg path : shapely lines/polygons are created
        - if only 1 [Mm] inside the svg path, then it is a simple line or (of closed) polygon without holes
        - if more than 1 [Mm] inside the svg path, then it is a polygon with holes or a "separated" poly
        -> split them, the one with the largest area is the exterior, the others are the holes

        -> Wow! not automatically! for example for 'i' and 'j' there are 2 [Mm] but no interior,
        indeed 'i' is composed of 2 distincts paths, as 'j' also is.

        -> so we have infact to check if the subpaths are included in largers one, or not
        '''
        is_simple_path = self._is_simple_path()

        if is_simple_path == True:
            is_closed = self._is_subpath_closed()

            if not is_closed:
                line = self.import_subpath_as_linestring()
                self.lines.append(line)
            else:
                poly = self.import_subpath_as_polygon()
            
                # a warning if the inital polygon is not valid!
                valid_poly = self.fix_simple_polygon(poly)

                if valid_poly != None:
                    poly = valid_poly

                # set the right orientation for this polygon
                poly = shapely.geometry.polygon.orient(poly)
                self.polys.append(poly)
        else:
            # Generate temporary svgpath objects with simple paths
            # to build polygon(s) with holes.
            subpaths = self._generate_simple_svgpaths()

            # From these subpaths, build a list of polygons without holes.
            # The holes will be handled later.
            subpaths_db = {}
            for subpath in subpaths:
                is_closed = subpath._is_subpath_closed()

                if not is_closed:
                    line = subpath.import_subpath_as_linestring()
                    self.lines.append(line)
                else:
                    polygon = subpath.import_subpath_as_polygon()

                    valid_poly = self.fix_simple_polygon(polygon)

                    if valid_poly != None:
                        polygon = valid_poly

                    subpaths_db[subpath.p_id] = {
                        "id": subpath.p_id,
                        "svgpath" : subpath,
                        "polygon": polygon,
                        "area": polygon.area,
                        "exterior": polygon.exterior,
                        "interiors": [] # init
                    }

            subpaths_db_sorted = []
            for p_id in subpaths_db:
                subpaths_db_sorted.append( subpaths_db[p_id] )
            
            # sort from the largest area first
            subpaths_db_sorted.sort(key=lambda x: -x.get('area'))
            
            # build the 'real' polygons one after the other, starting from the biggest one
            
            # the first is the largest one
            subpath_poly_data = subpaths_db_sorted[0]

            xpolys = [subpath_poly_data]
            
            # the others
            for subpath_poly_data in subpaths_db_sorted[1:]:
                exterior = subpath_poly_data["exterior"]

                is_hole = False

                if process_holes:
                    for xpoly in xpolys: # the existing polys
                        if xpoly["polygon"].covers(exterior):
                            is_hole = True
                            xpoly["interiors"].append(exterior)
                            break

                if is_hole is False:
                    # it is a separated polygon
                    xpolys.append(subpath_poly_data)

                # sort the list - the smallest are the first to be searched
                xpolys.sort(key=lambda x: x.get('area'))

            # ok, time to build the "real" polygons
            all_polys = []
            for subpath_poly_data in xpolys:
                if subpath_poly_data["interiors"]:
                    poly = shapely.geometry.Polygon(subpath_poly_data["exterior"], holes=subpath_poly_data["interiors"])
                else:
                    poly = shapely.geometry.Polygon(subpath_poly_data["exterior"])

                all_polys.append(poly)

            # wow, for some letters (D, P) there is a problem (TO INQUIRE)
            # D: exterior/interior is wrong
            # P: interior in wrong 
            for poly in all_polys:
                poly = self.fix_complex_poly(poly)
                self.polys.append(poly)

    @classmethod
    def from_shapely_linestring(cls, prefix: str, shapely_path: shapely.geometry.LineString, safeToClose: bool) -> 'SvgPath':
        '''
        '''
        pts = list(shapely_path.coords)

        discretized_svg_path : List[complex] = [ complex(pt[0], pt[1]) for pt in pts]

        svg_path = svgpathtools.Path()

        for i in range(len(discretized_svg_path)-1):
            start = discretized_svg_path[i]
            end   = discretized_svg_path[i+1]

            svg_path.append(svgpathtools.Line(start, end))

        # last one : from end point to start point
        if safeToClose:
            start = discretized_svg_path[-1]
            end   = discretized_svg_path[0]

        svg_path.append(svgpathtools.Line(start, end))

        return SvgPath(prefix, {'d': svg_path.d()})

    @classmethod
    def from_shapely_polygon(cls, prefix: str, polygon: shapely.geometry.Polygon) -> 'SvgPath':
        '''
        '''
        path_str = polygon.svg(scale_factor=0.1)

        svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
            version="1.1">
            <g>
            %s
            </g> 
        </svg>''' % path_str

        paths, attributes = cls.svg2paths_from_string(svg)

        attribs = attributes[0]

        return SvgPath(prefix, attribs) 

    @classmethod
    def from_circle_def(cls, center: List[float], radius: float) -> 'SvgPath':
        '''
        PyCut Tab import in svg viewer
        '''
        svg = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg" 
            version="1.1">
            <g>
                <circle cx="%(cx)d" cy="%(cy)d" r="%(radius)d" />
            </g>  
        </svg>''' % {"cx": center[0], "cy": center[1], "radius": radius}


        paths, _ = cls.svg2paths_from_string(svg)

        svg_path = paths[0]

        return SvgPath("pycut_tab", {'d': svg_path.d() + " Z"})

    @classmethod
    def fix_simple_polygon(cls, polygon: shapely.geometry.Polygon) -> shapely.geometry.Polygon :
        '''
        A simple polygon is a polygon without holes!
        '''
        if polygon.is_valid:
            return polygon

        print("not valid poly", polygon)
        print(shapely.validation.explain_validity(polygon))
        MatplotLibUtils.MatplotlibDisplay("not valid poly", polygon, force=True)
        
        valid_poly = make_valid(polygon)

        if valid_poly.geom_type == 'Polygon':
            return valid_poly

        elif valid_poly.geom_type == 'MultiPolygon':
            # take the largest one! CHECKME
            largest_area = -1
            largest_poly = None
            for poly in valid_poly.geoms:
                area = poly.area
                if area > largest_area:
                    largest_area = area
                    largest_poly = poly

            return largest_poly

        elif valid_poly.geom_type == 'GeometryCollection':
            # take the largest Polygon
            largest_area = -1
            largest_poly = None

            for geom in valid_poly.geoms:
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
    def fix_complex_poly(cls, polygon: shapely.geometry.Polygon) -> shapely.geometry.Polygon :
        '''
        A complex polygon is a polygon with holes!
        '''
        if polygon.is_valid:
            return polygon

        exterior = polygon.exterior
        interiors = polygon.interiors

        ext_poly = shapely.geometry.Polygon(exterior)
        if not ext_poly.is_valid:
            ext_poly = cls.fix_simple_polygon(ext_poly)

        if not interiors:
            ext_linestring = shapely.geometry.LineString(ext_poly.exterior)

            fixed_poly = shapely.geometry.Polygon(ext_linestring)
        else:
            fixed_interiors : List[shapely.geometry.Polygon] = []
            for interior in interiors:
                int_poly = shapely.geometry.Polygon(interior)

                if not int_poly.is_valid:
                    int_poly = cls.fix_simple_polygon(int_poly)

                fixed_interiors.append(int_poly)

            ext_linestring = shapely.geometry.LineString(ext_poly.exterior)
            holes_linestrings = [shapely.geometry.LineString(int_poly.exterior) for int_poly in fixed_interiors] 

            fixed_poly = shapely.geometry.Polygon(ext_linestring, holes=holes_linestrings)

        return fixed_poly
