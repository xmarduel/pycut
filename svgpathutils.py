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

from matplotlib_utils import MatplotLibUtils

from shapely_utils import ShapelyUtils


M_PI = math.acos(-1)



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
    def svg2paths_from_string(cls, svg: str) -> Tuple[List[svgpathtools.Path], List[Dict[str,str]]]:
        '''
        From a svg file content, read all paths and their attributes
        '''
        # a tmp file
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'temp_svg.svg')
            
            fp = open(filename, "w")
            fp.write(svg)
            fp.close()

            paths, attributes = svgpathtools.svg2paths(filename)

            return paths, attributes

        return None, None

    @classmethod
    def read_svg_shapes_as_paths(cls, svg: str) -> Dict[str, Tuple[Dict[str,str], svgpathtools.Path]] :
        '''
        From a svg file content, read all paths and their attributes
        and organize them as dictionary with key <path_id>, value <attribs, path>
        '''
        svg_shapes = {}

        paths, attributes = cls.svg2paths_from_string(svg)

        for k, path in enumerate(paths):
            attribs = attributes[k]

            path_id = attribs.get('id', None)
            print("============= path %s =================" % path_id)

            if path_id is None:
                continue
            svg_shapes[path_id] = (attribs, path)

        return svg_shapes

    def __init__(self, p_id: str, p_attrs: Dict[str,str]):
        '''
        '''
        # the 'id' of a svg <path> definition
        self.p_id = p_id
        # and the attributes of the <path>
        self.p_attrs = p_attrs

        # the transformation of the svg_path_d to a svgpathtools 'path'
        self.svg_path = svgpathtools.parse_path(self.p_attrs['d'])

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
        because shapely may find that it create an "invalid" polygon with the reason:
        
        >>>>> Self-intersection[184.211463517 186.153838406]

        This occurs if the sequence of points is like the following:

        184.24701507756535 186.2492779464199
        184.211463517 186.15383840599998
        184.211463517 186.153838406
        184.86553017294605 185.57132365078505

        so between 2 svg paths "segments", avoid duplicating the point at the end of the first segment and 
        the one at the beginning of the second segment.
        '''
        points = np.array([], dtype=np.complex128)

        first_pt = None
        
        for k, segment in enumerate(self.svg_path):
            if k == 0:
                # shapely fix : global initial pt
                first_pt = segment.point(0)

            if segment.__class__.__name__ == 'Line':
                # start and end points
                if len(self.svg_path) == 1:
                    pts = segment.points([0,1])
                else:
                    if k == 0:
                        pts = segment.points([0.5, 1]) # shapely fix!
                    else:
                        pts = segment.points([1])
                    
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

            points = np.concatenate((points, pts))

        # shapely fix : add as last point the "virtual" first one, the first "middle one" is already the "new" first
        #points = np.concatenate((points, [first_pt], [points[0]]))
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
        where all paths of the object list are a 'simple' paths 
        '''
        # make all "m" -> "M" for the separated paths
        path_abs = self.svg_path.d()    # thanks svgpathutils!                             

        # it's easy now
        paths = path_abs.split("M")

        svgpaths = []
        for k, sep_path in enumerate(paths):
            sep_path = sep_path.strip()
            if not sep_path:
                continue
            p_id = self.p_id + "___sep_%d" % k 
            p_attrs = copy.deepcopy(self.p_attrs)
            p_attrs["d"] = "M " + sep_path
            o = SvgPath(p_id, p_attrs)
            svgpaths.append(o)
        
        return svgpaths

    def _toShapelyLineString(self) -> shapely.geometry.LineString:
        '''
        '''
        np_svg_path = self.discretize()

        coordinates = [ (complex_pt.real, complex_pt.imag)  for complex_pt in np_svg_path ]

        line = shapely.geometry.LineString(coordinates)

        return line

    def _toShapelySimplePolygon(self) -> shapely.geometry.Polygon:
        '''
        '''
        np_svg_path = self.discretize()

        coordinates = [ (complex_pt.real, complex_pt.imag)  for complex_pt in np_svg_path ]

        poly = shapely.geometry.Polygon(coordinates)

        return poly

    def toShapelyPolygons(self) -> List[shapely.geometry.Polygon]:
        '''
        The main method to transform a svg path into a polygon or a list of polygons
        - if only 1 [Mm] inside the svg path, then it is a simple [closed] line ie a polygon without holes
        - if more than 1 [Mm] inside the svg path, then it is a polygon with holes
        -> split them, the one with the largest area is the exterior, the others are the holes

        -> Wow! not automatically! for example for 'i' and 'j' there are 2 [Mm] but no interior,
        indeed 'i' is composed of 2 distincts paths, as 'j' also is.

        -> so we have infact to check if the simple paths are included in the larger one, or not
        '''
        is_simple_path = self._is_simple_path()

        polys = []

        if is_simple_path == True:
            line = self._toShapelyLineString()
            poly = shapely.geometry.Polygon(line)

            # a warning if the inital polygon is not valid! 
            if not poly.is_valid:
                print("not valid poly", line)
                print(shapely.validation.explain_validity(poly))
                MatplotLibUtils.MatplotlibDisplay("not valid poly", line, force=True)
                #poly = make_valid(poly)
                #print(shapely.validation.explain_validity(poly))
                #MatplotLibUtils.MatplotlibDisplay("--> valid poly", poly, force=True)

            # set the right orientation for this polygon
            poly = shapely.geometry.polygon.orient(poly)
            polys.append(poly)
        else:
            # generate temporary svgpath objects with simple paths
            # to build polygon(s) with holes
            svgpaths = self._generate_simple_svgpaths()

            # from these simple path, build list of polygons
            # some of them will have holes, other not...
            data = {}
            for svgpath in svgpaths:
                linestring = svgpath._toShapelyLineString()
                s_polygon = svgpath._toShapelySimplePolygon()

                data[svgpath.p_id] = {
                    "id": svgpath.p_id,
                    "svgpath" : svgpath,
                    "linestring": linestring,
                    "s_polygon": s_polygon,
                    "area": s_polygon.area,
                    "exterior": None,
                    "interiors": []
                }

            data_sorted = []
            for p_id in data:
                data_sorted.append( data[p_id] )
            
            # sort from the largest area first
            data_sorted.sort(key=lambda x: -x.get('area'))
            
            # build the polygons one after the other, starting from the biggest one
            # NOTE: polygons SHOULD note overlap themselves
            
            # the first is the largest one
            xpoly = data_sorted[0]
            xpoly["exterior"] = xpoly["linestring"]

            xpolys = [xpoly]
            
            # the others
            for data in data_sorted[1:]:
                line = data["linestring"]

                is_hole = False
                for xpoly in xpolys: # the existing polys
                    if xpoly["s_polygon"].covers(line):
                        is_hole = True
                        xpoly["interiors"].append(line)
                        break

                if is_hole is False:
                    # is a separate polygon
                    data["exterior"] = line
                    xpolys.append(data) # append to the list of existing polys

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
                poly = ShapelyUtils.fixGenericPolygon(poly)
                polys.append(poly)

        return polys

    @classmethod
    def fromShapelyLineString(cls, prefix: str, shapely_path: shapely.geometry.LineString, safeToClose: bool) -> 'SvgPath':
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
    def fromShapelyPolygon(cls, prefix: str, polygon: shapely.geometry.Polygon) -> 'SvgPath':
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
    def fromCircleDef(cls, center:float, radius: float) -> 'SvgPath':
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
