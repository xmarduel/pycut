import os
import math
import copy

from typing import List
from typing import Tuple
from typing import Dict

import io

import numpy as np

import svgelements
import xml.etree.ElementTree as etree

import shapely.geometry
import shapely.validation
from shapely.validation import make_valid
from shapely.validation import explain_validity

from shapely_matplotlib import MatplotLibUtils

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
    Transform svgelement 'Path' into a 'Shapely Polygon' object(s)

    - svgelement 'Path' are list of 'Segment(s)' and
    each segment has a list of points, given in format 'complex type' (a+bj)

    - a svg path can describe 1 or more Polygons, Polygons may have holes

    Convention:
    - a (instance) path from svgelements is noted: svg_path
    - a (string) svg <path> definition is noted: svg_path_d

    '''
    @classmethod
    def svg_paths_from_svg_string(cls, svg_str: str) -> List['SvgPath']:
        '''
        From a svg file content, read all paths (and those from the std svg shapes)
        '''
        data = io.StringIO(svg_str)

        svg = svgelements.SVG.parse(data,
              reify=True,
              ppi=25.4)  # so that there is no "scaling" : 1 inch = 25.4 mm
    
        paths = []
    
        for element in svg.elements():
            try:
                if element.values['visibility'] == 'hidden':
                    continue
            except (KeyError, AttributeError):
                pass
            if isinstance(element, svgelements.SVGText):
                pass # elements.append(element)
            elif isinstance(element, svgelements.Path):
                if len(element) != 0:
                    paths.append(element)
            elif isinstance(element, svgelements.Shape):
                e = svgelements.Path(element)
                e.reify()  # In some cases the shape could not have reified, the path must.
                if len(e) != 0:
                    paths.append(e)
            elif isinstance(element, svgelements.SVGImage):
                pass

        return [ SvgPath(path, orig_svg_str=svg_str) for path in paths ]

    @classmethod
    def read_svg_shapes_and_paths(cls, svg_str: str) -> Dict[str, 'SvgPath'] :
        '''
        From a svg file content, read all paths and their attributes
        and organize them as dictionary with key <path_id>, value SvgPath object
        '''
        paths_map = {}

        paths = cls.svg_paths_from_svg_string(svg_str)

        for path in paths:
            #print("=======================================================")
            print("============= svg : path %s =================" % path.p_id)
            #print("============= svg : path isclosed = %d ======" % path.closed)

            # ignore paths without id
            if path.p_id is None:
                continue

            paths_map[path.p_id] = path

        return paths_map

    @classmethod
    def from_svg_path_def(cls, d_def: str, p_id: str, shape_tag: str, shape_attrs: Dict[str,str]) -> 'SvgPath':
        '''
        Create a SvgPath
        '''
        path_data = ' d="%(value)s"' % { "value": d_def }
        path_data += ' id="%(value)s"' % { "value": p_id }


        for key in shape_attrs:
            if not (key == "d" or key == "id"):
                path_data += ' %(key)s="%(value)s"' % {"key": key, "value": shape_attrs[key]}

        svg_str = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" width="1000mm" height="1000mm" viewBox="0 0 1000 1000"
   xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
  <g id="layer">
    <path %(path_data)s/>
  </g>
</svg> """ % {"path_data": path_data }

        paths = cls.svg_paths_from_svg_string(svg_str)
        
        path = paths[0]
        path.shape_tag = shape_tag

        return path

    def __init__(self, svg_path: svgelements.Path, orig_svg_str=None):
        '''
        '''
        self.svg_path = svg_path

        self.p_d = svg_path.d()
        self.p_id = svg_path.values.get('id', "?")
        self.closed = self.eval_closed()

        self.shape_tag = svg_path.values["tag"]

        # I do not quite understand how the 'real' attributes are got from
        # They are **not** the xml attributes in all cases...
        
        self.shape_attrs = copy.deepcopy(svg_path.values["attributes"])
  
        if "tag" in self.shape_attrs:
            del self.shape_attrs["tag"]

        if orig_svg_str is not None:
            # read xml and get the **real** attribute
            root = etree.fromstring(orig_svg_str)

            #elements = root.xpath("//*[@id = '%s']" % self.p_id)  # lxml
            elements = root.findall(".//*[@id = '%s']" % self.p_id)

            if len(elements) == 1:
                elt = elements[0]
                attrib = elt.attrib
                #print("============= svg : attrib %s =================" % attrib)
                self.shape_attrs = attrib
            else:
                pass

        # the result of the import
        self.lines : List[shapely.geometry.LineString] = []
        self.polys : List[shapely.geometry.Polygon] = []
        self.points : List[shapely.geometry.Point] = []

    def eval_closed(self):
        '''
        '''
        return self.svg_path.segments()[-1].__class__.__name__ == "Close"

    def discretize_closed_path(self) -> np.array :
        '''
        '''
        return SvgPathDiscretizer(self.svg_path).discretize_closed_path()

    def discretize_open_path(self) -> np.array :
        '''
        '''
        return SvgPathDiscretizer(self.svg_path).discretize_open_path()

    def _is_simple_path(self) -> bool:
        '''
        check if path is a 'simple' one or a 'complex' one -
        in the sense there is no "jump" in the path (svg [mM]) excepted the initial one
        '''
        d_def = self.p_d

        nb_separate_paths = d_def.count("M") + d_def.count("m")

        return nb_separate_paths == 1

    def _is_subpath_closed(self) -> bool:
        '''
        check if a subpath is "closed"
        '''
        d_def = self.p_d

        nb_z = d_def.count("Z") + d_def.count("z") # one or zero

        return nb_z != 0
    
    def _generate_simple_svgpaths(self) -> List['SvgPath']:
        '''
        From an instance of SvgPath, generate a list of SvgPath
        where all subpaths of the object list are a 'simple' paths 
        '''
        # make all "m" -> "M" for the subpaths
        path_abs = self.svg_path.d(relative=False)    # thanks svgelements!                          

        # it's easy now
        subpaths = path_abs.split("M")

        svgpaths = []
        for k, subpath in enumerate(subpaths):
            subpath = subpath.strip()
            if not subpath:
                continue
            p_id = self.p_id + "___sub_%d" % k 
            
            shape_attrs = copy.deepcopy(self.shape_attrs)

            o = SvgPath.from_svg_path_def("M" + subpath, p_id, "path", shape_attrs)
            
            svgpaths.append(o)
        
        return svgpaths

    def import_subpath_as_linestring(self) -> shapely.geometry.LineString:
        '''
        '''
        pts = self.discretize_open_path()

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
    
    def import_as_point(self) -> List[shapely.geometry.Point]:
        '''
        only for circle shapes
        '''
        cx = float(self.shape_attrs['cx'])
        cy = float(self.shape_attrs['cy'])

        center = (cx, cy)

        return shapely.geometry.Point(center)

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
    def from_shapely_linestring(cls, prefix: str, linestring: shapely.geometry.LineString, safe_to_close: bool) -> 'SvgPath':
        '''
        '''
        path_str = linestring.svg(scale_factor=0.1)
        # gives an id
        path_str = path_str.replace('/>', ' id="%s" />' % prefix)

        if safe_to_close:
            path_str += " Z"

        svg_str = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
            version="1.1">
            <g>
            %s
            </g> 
        </svg>''' % path_str

        paths = cls.svg_paths_from_svg_string(svg_str)
        path = paths[0]
        
        return path

    @classmethod
    def from_shapely_polygon(cls, prefix: str, polygon: shapely.geometry.Polygon) -> 'SvgPath':
        '''
        '''
        path_str = polygon.svg(scale_factor=0.1)
        # gives an id
        path_str = path_str.replace('/>', ' id="%s" />' % prefix)

        svg_str = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
            version="1.1">
            <g>
            %s
            </g> 
        </svg>''' % path_str

        paths = cls.svg_paths_from_svg_string(svg_str)
        path = paths[0]

        return path

    @classmethod
    def from_circle_def(cls, center: List[float], radius: float) -> 'SvgPath':
        '''
        PyCut Tab import in svg viewer
        '''
        svg_str = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg" 
            version="1.1">
            <g>
                <circle id="pycut_tab" cx="%(cx)f" cy="%(cy)f" r="%(radius)f" />
            </g>  
        </svg>''' % {"cx": center[0], "cy": center[1], "radius": radius}

        paths = cls.svg_paths_from_svg_string(svg_str)
        path = paths[0]
        
        return path

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


class SvgPathDiscretizer:
    '''
    '''
    PYCUT_SAMPLE_LEN_COEFF = 10 # 10 points per "svg unit" ie arc of len 10 -> 100 pts discretization
    PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5 # is in jsCut 1

    def __init__(self, svg_path: svgelements.Path):
        '''
        '''
        self.svg_path = svg_path

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

    def discretize(self) -> np.array:
        '''
        '''
        if self.svg_path.closed:
            return self.discretize_closed_path()
        else:
            return self.discretize_open_path()
        
    def discretize_closed_path(self) -> np.array :
        '''
        Transform the svg_path (a list of svgelement Segments) into a list of 'complex' points
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

        first_seg = True
        
        for k, segment in enumerate(self.svg_path):

            if segment.__class__.__name__ == 'Move':
                continue
            if segment.__class__.__name__ == 'Close':
                continue
            
            ## ---------------------------------------
            if ignore_segment(k, segment) == True:
                continue
            ## ---------------------------------------

            if segment.__class__.__name__ == 'Line':
                # start and end points
                if first_seg :
                    _pts = [segment.point(0.0), segment.point(1.0)]
                else:
                    _pts = [segment.point(1.0)] 

                pts = [ complex(_pt.x,+ _pt.y) for _pt in _pts]
                    
            elif segment.__class__.__name__ == 'Arc':
                # no 'points' method for 'Arc'!
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                _pts = []
                if first_seg:
                    for p in range(0, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))
                else:
                    # not the first one
                    for p in range(1, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                _pts = [ complex(_pt.x,+ _pt.y) for _pt in _pts ]
                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                _pts = []

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                if first_seg:
                    for p in range(0, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))
                else:
                    # not the first one
                    for p in range(1, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                _pts = [ complex(_pt.x,+ _pt.y) for _pt in _pts ]
                pts = np.array(_pts, dtype=np.complex128)

            points = np.concatenate((points, pts))


            first_seg = False

        # for closed path, avoid first pt == last_point -- before shapely trick --
        def dist(pt0, pt1) :
            dx = (pt0.real - pt1.real)
            dy = (pt0.imag - pt1.imag)
            return dx * dx + dy * dy
            
        if dist(points[0], points[-1]) < 1.0e-5:
            points = points[0:-1]
              
        # shapely fix:
        extra_middle_point = (points[0] + points[1]) / 2.0

        points = np.concatenate(([extra_middle_point], points[1:], [points[0]]))

        return points

    def discretize_open_path(self) -> np.array :
        '''
        Transform the svg_path (a list of svgelement Segments) into a list of 'complex' points
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
        
        first_seg = True

        for k, segment in enumerate(self.svg_path):

            if segment.__class__.__name__ == 'Move':
                continue
            if segment.__class__.__name__ == 'Close':
                continue

            ## ---------------------------------------
            if ignore_segment(k, segment) == True:
                continue
            ## ---------------------------------------

            if segment.__class__.__name__ == 'Line':
                # start and end points
                if first_seg:
                    _pts = [segment.point(0.0), segment.point(1.0)] 
                else:
                    _pts = [segment.point(1.0)] 

                pts = [ complex(_pt.x,+ _pt.y) for _pt in _pts ]

            elif segment.__class__.__name__ == 'Arc':
                # no 'points' method for 'Arc'!
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                _pts = []

                if first_seg:
                    for p in range(0, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))
                else:
                    # not the first one
                    for p in range(1, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                _pts = [ complex(_pt.x,+ _pt.y) for _pt in _pts ]
                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                _pts = []

                if first_seg:
                    for p in range(0, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))
                else:
                    # not the first one
                    for p in range(1, nb_samples+1):
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                _pts = [ complex(_pt.x,+ _pt.y) for _pt in _pts ]
                pts = np.array(_pts, dtype=np.complex128)

            points = np.concatenate((points, pts))

            first_seg = False

        return points
