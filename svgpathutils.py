
import os
import math
import copy
import re
import string

from typing import List
from typing import Tuple
from typing import Dict

import tempfile

import xml.etree.ElementTree as etree

import numpy as np
import svgpathtools
import shapely.geometry

from shapely_utils import ShapelyUtils


M_PI = math.acos(-1)



class SvgPath:
    '''
    Transform svgpathtools 'Path' into a 'Shapely LineString' object

    - svgpathtools 'Path' are list of 'Segment(s)' and
    each segment has a list of points, given in format 'complex type' (a+bj)

    - Shapely LineString are list of Points[2]

    so the transformation is straightforward

    Convention:
    - a path from svgpathtools is noted: svg_path
    - a svg <path> definition is noted: svg_path_d
    - the discretization of a svg_path results in a numpy array, noted: np_svg_path
    - a shapely path (LineString) is noted: shapely_path
    '''
    PYCUT_SAMPLE_LEN_COEFF = 10 # 10 points per "svg unit" ie arc of len 10 -> 100 pts discretization
    PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5 # is in jsCut 1

    @classmethod
    def set_arc_precision(cls, arc_precision):
        '''
        '''
        cls.PYCUT_SAMPLE_LEN_COEFF = 1.0 / arc_precision

    @classmethod
    def set_arc_min_nb_segments(cls, arc_min_nb_segments):
        '''
        '''
        cls.PYCUT_SAMPLE_MIN_NB_SEGMENTS = arc_min_nb_segments

    @classmethod
    def svg2paths_from_string(cls, svg: str) :
        '''
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
    def read_svg_shapes_as_paths(cls, svg: str) -> Dict[str,Tuple[Dict[str,str],svgpathtools.Path]] :
        '''
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

    def __init__(self, p_id: str, p_attrs: Dict):
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
                        pts = segment.points([0.5]) # shapely fix!
                    elif k < len(self.svg_path)-1:
                        pts = segment.points([0])
                    else:
                        pts = segment.points([0, 1])
                    
            elif segment.__class__.__name__ == 'Arc':
                # no 'points' method for 'Arc'!
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                _pts = []
                if k == 0:
                    for k in range(1, nb_samples+1):
                        _pts.append(segment.point(float(k)/float(nb_samples)))
                else:
                    for k in range(0, nb_samples+1):
                        _pts.append(segment.point(float(k)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                _pts = []
                if k == 0:
                    for k in range(1, nb_samples+1):
                        _pts.append(segment.point(float(k)/float(nb_samples)))
                else:
                    for k in range(0, nb_samples+1):
                        _pts.append(segment.point(float(k)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            points = np.concatenate((points, pts))

        # shapely fix : add as last point the "virtual" first one, the first "middle one" is already the "new" first
        #points = np.concatenate((points, [first_pt], [points[0]]))
        points = np.concatenate((points, [first_pt]))
        #print(points)

        return points

    def _toShapelyLineString(self) -> shapely.geometry.LineString:
        '''
        '''
        np_svg_path = self.discretize()

        coordinates = [ (complex_pt.real, complex_pt.imag)  for complex_pt in np_svg_path ]

        line = shapely.geometry.LineString(coordinates)

        return line

    def _isSimplePath(self) -> bool:
        '''
        check if path is "simple" closed path or path with hole(s)
        '''
        d_def = self.p_attrs["d"]

        nb_separate_paths = d_def.count("M")
        nb_separate_paths = nb_separate_paths + d_def.count("m")

        return nb_separate_paths == 1

    def _generateSeparatedSvgPath(self) -> List['SvgPath']:
        '''
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

    def toShapelyPolygons(self) -> List[shapely.geometry.Polygon]:
        '''
        The main method to transform a svg path into a polygon or a list of polygons
        - if only 1 [Mm] inside the svg path, then it is a simple closed line ie a polygon without holes
        - if more than 1 [Mm] inside the svg path, then it is a polygon with holes
        -> split them, the "longuest" one is the exterior, the others are the holes

        -> Wow! not automatically! for exmaple for i and j there are 2 [Mm] but no interior,
        indeed i is composed of 2 distincts paths, as j also is.

        -> so we have infact to check if the smaller path in included in the larger one, or not
        '''
        is_simple_path = self._isSimplePath()

        if is_simple_path == True:
            line = self._toShapelyLineString()
            poly = shapely.geometry.Polygon(line)

            # set the right orientation for this polygon
            poly = shapely.geometry.polygon.orient(poly)
            others = []
        else:
            # generate temporary svgpath objects with the separated paths
            # to build a polygon with holes
            svgpaths = self._generateSeparatedSvgPath()

            data = {}
            for svgpath in svgpaths:
                data[svgpath.p_id] = {
                    "svgpath" : svgpath,
                    "linestring": svgpath._toShapelyLineString(),
                    "exterior": False
                }

            max_length = -1
            my_length_p_id = ""
            for p_id in data:
                svgpath = data[p_id]["svgpath"]
                length = svgpath.svg_path.length()
                if length > max_length:
                    max_length = length
                    my_length_p_id = p_id

            data[my_length_p_id]["exterior"] = True    
                
            # ok, time to build the polygon
            exterior = data[my_length_p_id]["linestring"]
            interiors = []
            for p_id in data:
                if data[p_id]["exterior"] == False:
                    interiors.append(data[p_id]["linestring"])

            larger = shapely.geometry.Polygon(exterior)
            holes = []
            separs = []
            for interior_line in interiors:
                if larger.covers(interior_line):
                    holes.append(interior_line)
                else:
                    #ShapelyUtils.MatplotlibLineStringDebug("xx", interior_line)
                    separs.append(interior_line)

            if holes:
                poly = shapely.geometry.Polygon(exterior, holes=holes)
            else:
                poly = shapely.geometry.Polygon(exterior)

            _others = []
            
            for separ in separs:
                # very necessary!
                simplyfied_separ =  separ.simplify(0.001)
                other = shapely.geometry.Polygon(simplyfied_separ)
                _others.append(other)
            
            others = [ShapelyUtils.fixGenericPolygon(other) for other in _others]

            # wow, some some letters (D, P)
            # D: exterior/interior is wrong
            # P: interior in wrong 
            poly = ShapelyUtils.fixGenericPolygon(poly)

            #ShapelyUtils.MatplotlibPolygonDebug("poly", poly)

            # seems to be OK
            #fp = open("toShapelyPolygon.svg", "w")
            #fp.write('<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" version="1.1"><g style="stroke-width:0.264583">' + poly.svg(scale_factor=0.1) + '</g></svg>')
            #fp.close()

        return [poly] + others

    @classmethod
    def fromShapelyLineString(cls, prefix: str, shapely_path: shapely.geometry.LineString) -> 'SvgPath':
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

        fp = open("fromShapelyPolygon.svg", "w")
        fp.write(svg)
        fp.close()

        paths, attributes = cls.svg2paths_from_string(svg)

        attribs = attributes[0]
        attribs["fill"] = "#ff0000"

        return SvgPath(prefix, attribs) 

    @classmethod
    def fromCircleDef(cls, center, radius) -> 'SvgPath':
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



class SvgTransformer:
    '''
    '''
    def __init__(self, svg):
        self.svg = svg

    def collect_shapes(self) -> List[etree.ElementTree]:
        '''
        '''
        # python xml module can load with svg xml header with encoding utf-8
        tree = etree.fromstring(self.svg)
        elements = tree.findall('.//*')

        shapes_types = [
        	"path",
            "rect",
            "circle",
            "ellipse",
            "polygon",
            "line",
            "polyline"
        ]

        shapes : List[etree.ElementTree] = []
        
        for element in elements:
            if not element.tag.startswith("{http://www.w3.org/2000/svg}"):
                continue
            
            tag = element.tag.split("{http://www.w3.org/2000/svg}")[1]
            
            if tag in shapes_types:
                shapes.append(element)

        return shapes
        
    def augment(self, svg_paths: List[SvgPath]) -> str:
        '''
        '''
        all_paths = ""

        shapes = self.collect_shapes()

        for shape in shapes:
            shape_id = shape.attrib.get('id', None)

            print("svg : found shape %s : %s" % (shape.tag, shape_id))

            if shape_id is None:
                print("      -> ignoring")
                continue

            tag = shape.tag.split("}")[1]
            svg_attrs = ''
            for key, value in shape.attrib.items():
                svg_attrs += ' %s="%s"' % (key, value)

            all_paths += '<%s %s/>\r\n' % (tag, svg_attrs)

        for k, svg_path in enumerate(svg_paths):
            p_id = svg_path.p_id
            d_def = svg_path.p_attrs['d']

            stroke = '#00ff00'
            stroke_width = '0'
            
            fill = svg_path.p_attrs.get("fill", "#111111")
            fill_opacity = svg_path.p_attrs.get("fill-opacity", "1.0")
            fill_rule = svg_path.p_attrs.get("fill-rule", "nonzero")

            path = '<path id="%(id)s_%(counter)d" style="stroke:%(stroke)s;stroke-width:%(stroke_width)s;fill:%(fill)s;fill-opacity:%(fill_opacity)s;fill-rule:%(fill_rule)s;" \
              d="%(d_def)s" />' % {
                'id': p_id, 
                'counter': k, 
                'fill': fill,
                'stroke_width': stroke_width,
                'stroke': stroke,
                'fill_opacity': fill_opacity, 
                'fill_rule': fill_rule, 
                'd_def': d_def
            }

            all_paths += path + '\r\n'
        
        root = etree.fromstring(self.svg)
        root_attrib = root.attrib
        
        svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="%s"
                height="%s"
                viewBox="%s"
                version="1.1">
                <g>
                  %s
                </g> 
             </svg>''' % (root_attrib["width"], root_attrib["height"], root_attrib["viewBox"], all_paths)

        #print(svg)
        
        return svg

    def augment_with_toolpaths(self, svg_paths: List[SvgPath]) -> str:
        '''
        TODO: eval the best stroke-width in function of the item size

        40x40 mm -> stroke-width = 0.2 ok
        1x1 mm   -> stroke-width = 0.01 ok
        '''
        all_paths = ""

        shapes = self.collect_shapes()

        for shape in shapes:
            shape_id = shape.attrib.get('id', None)

            print("svg : found shape %s : %s" % (shape.tag, shape_id))

            if shape_id is None:
                print("     -> ignoring")

            tag = shape.tag.split("}")[1]
            svg_attrs = ''
            for key, value in shape.attrib.items():
                svg_attrs += ' %s="%s"' % (key, value)

            all_paths += '<%s %s/>\r\n' % (tag, svg_attrs)

        for k, svg_path in enumerate(svg_paths):
            p_id = svg_path.p_id
            d_def = svg_path.p_attrs['d']

            stroke = '#00ff00'
            stroke_width = '0.2'
            
            fill = 'none'

            all_paths += '<path id="%(id)s_%(counter)d" style="stroke:%(stroke)s;stroke-width:%(stroke_width)s;fill:%(fill)s" d="%(d_def)s" />' % {
                'id': p_id, 
                'counter': k,
                'stroke_width': stroke_width,
                'stroke': stroke,
                'fill': fill,
                'd_def': d_def
            }
        
        root = etree.fromstring(self.svg)
        root_attrib = root.attrib

        svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="%s"
                height="%s"
                viewBox="%s"
                version="1.1">
                <g>
                 %s
                </g> 
             </svg>''' % (root_attrib["width"], root_attrib["height"], root_attrib["viewBox"], all_paths)

        #print(svg)
        
        return svg




    

