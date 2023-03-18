import os
import math
import copy

from typing import List
from typing import Tuple
from typing import Dict

import tempfile

import numpy as np
import svgpathtools

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
1. subpaths are defined stating with [Mm]. Hopefully the path starts with [Mn]
2. every closed path (Zz) form a polygon, if not this is a line
3. first point of a polygon|line (after a [Zz]) is given with the [Mm] data .
4. if not [Mm] after [Zz], initial point is the previous initial point
5. we use shapely to query if subpaths as interiors of polygons of form separates polygons|lines
6. if not completely contained/outside, the path as polygon is ignored for pycut
7. lines are actually completely ignored 

So rewrite this module... actually such a bad algo...
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
        # a tmp file
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'temp_svg.svg')
            
            fp = open(filename, "w")
            fp.write(svg_str)
            fp.close()

            paths, attributes = svgpathtools.svg2paths(filename)

            return paths, attributes

        return None, None

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

        # the svgpath as instance of type 'svgpathtools.Path' extracted from p_attrs["d"]
        self.svg_path : svgpathtools.Path = None
        
        # the transformation of the svg_path_d to a svgpathtools 'path'
        
        if self.DISCRETIZATION_USE_MODULE == 'SVGPATHTOOLS':
            # svgpathtools
            self.svg_path : svgpathtools.Path = svgpathtools.parse_path(self.p_attrs['d']) 
        #if self.DISCRETIZATION_USE_MODULE == 'SVGELEMENTS':
        #    # svgelements
        #    self.svg_path = svgelements.Path(self.p_attrs['d'])

    def discretize(self) -> np.array :
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

    def _is_simple_path(self) -> bool:
        '''
        check if path is a "simple" one or 'complex' - in the sense there 
        is no "jump" in the path (svg [mM])
        '''
        d_def = self.p_attrs["d"]

        nb_separate_paths = d_def.count("M")
        nb_separate_paths = nb_separate_paths + d_def.count("m")

        return nb_separate_paths == 1

    def _generate_simple_svgpaths(self) -> List['SvgPath']:
        '''
        From an instance of SvgPath, generate a list of SvgPath
        where all subpaths of the object list are a 'simple' paths 
        '''
        # make all "m" -> "M" for the subpaths
        path_abs = self.svg_path.d()    # thanks svgpathtools!                             

        # it's easy now
        subpaths = path_abs.split("M")

        svgpaths = []
        for k, subpath in enumerate(subpaths):
            subpath = subpath.strip()
            if not subpath:
                continue
            p_id = self.p_id + "___sub_%d" % k 
            p_attrs = copy.deepcopy(self.p_attrs)
            p_attrs["d"] = "M " + subpath
            o = SvgPath(p_id, p_attrs)
            svgpaths.append(o)
        
        return svgpaths

    def import_as_linestring(self) -> shapely.geometry.LineString:
        '''
        '''
        np_svg_path = self.discretize()

        coordinates = [ (complex_pt.real, complex_pt.imag)  for complex_pt in np_svg_path ]

        line = shapely.geometry.LineString(coordinates)

        return line

    def import_as_polygon(self) -> shapely.geometry.Polygon:
        '''
        '''
        np_svg_path = self.discretize()

        coordinates = [ (complex_pt.real, complex_pt.imag)  for complex_pt in np_svg_path ]

        poly = shapely.geometry.Polygon(coordinates)

        return poly

    def import_as_polygons_list(self) -> List[shapely.geometry.Polygon]:
        '''
        The main method to transform a svg path into a polygon or a list of polygons
        - if only 1 [Mm] inside the svg path, then it is a simple [closed] line ie a polygon without holes
        - if more than 1 [Mm] inside the svg path, then it is a polygon with holes
        -> split them, the one with the largest area is the exterior, the others are the holes

        -> Wow! not automatically! for example for 'i' and 'j' there are 2 [Mm] but no interior,
        indeed 'i' is composed of 2 distincts paths, as 'j' also is.

        -> so we have infact to check if the subpaths are included in largers one, or not
        '''
        is_simple_path = self._is_simple_path()

        polys = []

        if is_simple_path == True:
            line = self.import_as_linestring()
            poly = shapely.geometry.Polygon(line)

            # a warning if the inital polygon is not valid! 
            if not poly.is_valid:
                print("not valid poly", line)
                print(shapely.validation.explain_validity(poly))
                MatplotLibUtils.MatplotlibDisplay("not valid poly", line, force=True)
                
                # try this:
                valid_poly = self.fix_simple_polygon(poly)

                if valid_poly != None:
                    poly = valid_poly
                    print("-> fixed to valid poly", poly)
                    MatplotLibUtils.MatplotlibDisplay("fixed valid poly", poly, force=True)
               


            # set the right orientation for this polygon
            poly = shapely.geometry.polygon.orient(poly)
            polys.append(poly)
        else:
            # Generate temporary svgpath objects with simple paths
            # to build polygon(s) with holes.
            svgpaths = self._generate_simple_svgpaths()

            # From these subpaths, build a list of polygons without holes.
            # The holes will be handled later.
            data = {}
            for svgpath in svgpaths:
                is_closed = True  # TODO

                if not is_closed:
                    continue

                polygon = svgpath.import_as_polygon()

                data[svgpath.p_id] = {
                    "id": svgpath.p_id,
                    "svgpath" : svgpath,
                    "polygon": polygon,
                    "area": polygon.area,
                    "exterior": polygon.exterior,
                    "interiors": [] # init
                }

            data_sorted = []
            for p_id in data:
                data_sorted.append( data[p_id] )
            
            # sort from the largest area first
            data_sorted.sort(key=lambda x: -x.get('area'))
            
            # build the 'real' polygons one after the other, starting from the biggest one
            # NOTE: polygons SHOULD note overlap themselves
            # NOTE: polygons which interect previous ones will be ignored 
            # FIXME: result should be a List of  valid shapely Polygon|MultiPolygon
            
            # the first is the largest one
            xpoly = data_sorted[0]

            xpolys = [xpoly]
            
            # the others
            for data in data_sorted[1:]:
                exterior = data["exterior"]

                is_hole = False
                for xpoly in xpolys: # the existing polys
                    if xpoly["polygon"].covers(exterior):
                        is_hole = True
                        xpoly["interiors"].append(exterior)
                        break

                if is_hole is False:
                    # it is a separate polygon  FIXME: check completely separated
                    xpolys.append(data) # append to the list of existing, well separated polys

                # sort the list - the smallest are the first to be searched
                xpolys.sort(key=lambda x: x.get('area'))

            # ok, time to build the "real" polygons
            all_polys = []
            for xpoly in xpolys:
                if xpoly["interiors"]:
                    poly = shapely.geometry.Polygon(xpoly["exterior"], holes=xpoly["interiors"])
                else:
                    poly = shapely.geometry.Polygon(xpoly["exterior"])

                all_polys.append(poly)

            # wow, for some letters (D, P) there is a problem (TO INQUIRE)
            # D: exterior/interior is wrong
            # P: interior in wrong 
            polys = []
            for poly in all_polys:
                poly = self.fix_complex_poly(poly)
                polys.append(poly)

        return polys

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

        return SvgPath(prefix, {'d': svg_path.d(), 'fill-rule': 'nonzero'})

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
    def from_circle_def(cls, center:float, radius: float) -> 'SvgPath':
        '''
        PyCut Tab import in svg viewer
        '''
        NB_SEGMENTS = 12
        angles = [ float(k * M_PI )/ (NB_SEGMENTS) for k in range(NB_SEGMENTS*2 +1)]

        discretized_svg_path : List[complex] = [ complex( \
                    center[0] + radius*math.cos(angle), 
                    center[1] + radius*math.sin(angle) ) for angle in angles]

        svg_path = svgpathtools.Path()

        for i in range(len(discretized_svg_path)-1):
            start = discretized_svg_path[i]
            end   = discretized_svg_path[i+1]

            svg_path.append(svgpathtools.Line(start, end))

        return SvgPath("pycut_tab", {'d': svg_path.d()})

    @classmethod
    def fix_simple_polygon(cls, polygon: shapely.geometry.Polygon) -> shapely.geometry.Polygon :
        '''
        A simple polygon is a polygon without holes!
        '''
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
