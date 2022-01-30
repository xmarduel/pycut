
import os
import math

from typing import List
from typing import Tuple
from typing import Dict

import tempfile

import xml.etree.ElementTree as etree

import numpy as np
import svgpathtools

import shapely
import shapely.geometry as shapely_geom

from  shapely_utils import ShapelyUtils

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
    PYCUT_SAMPLE_LEN_COEFF = 1 # is in jsCut 1.0/0.01 ie the same
    PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5 # is in jsCut 1

    @classmethod
    def set_arc_precision(cls, arc_min_segments_length):
        '''
        '''
        cls.PYCUT_SAMPLE_LEN_COEFF = 1.0 / arc_min_segments_length

    @classmethod
    def set_arc_min_nb_segments(cls, arc_min_nb_segments):
        '''
        '''
        cls.PYCUT_SAMPLE_MIN_NB_SEGMENTS = arc_min_nb_segments

    @classmethod
    def read_svg_shapes_as_paths(cls, svg: str) -> Dict[str,Tuple[Dict[str,str],svgpathtools.Path]] :
        '''
        '''
        svg_shapes = {}

        # a tmp file
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'temp_svg.svg')
            
            fp = open(filename, "w")
            fp.write(svg)
            fp.close()

            paths, attributes = svgpathtools.svg2paths(filename)

            for k, path in enumerate(paths):
                attribs = attributes[k]

                path_id = attribs.get('id', None)
                print("============= path %s =================" % path_id)
                #print(path)
                #print(attribs)

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
                        pts = segment.points([0.5, 1]) # shapely fix!
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

    
    def toShapelyLineString(self) -> shapely_geom.LineString:
        '''
        '''
        np_svg_path = self.discretize()

        coordinates = []

        for complex_pt in np_svg_path:
            pt = ( \
                int(complex_pt.real * (ShapelyUtils.inchToShapelyScale / 25.4)), \
                int(complex_pt.imag * (ShapelyUtils.inchToShapelyScale / 25.4))  \
            )

            coordinates.append(pt)

        line = shapely_geom.LineString(coordinates)

        return line

    def toShapelyPolygon(self) -> shapely_geom.Polygon:
        '''
        '''
        line = self.toShapelyLineString()
        poly = shapely_geom.Polygon(line)

        # set the right orientation for this polygon
        poly = shapely_geom.polygon.orient(poly)
    
        return poly

    @classmethod
    def fromShapelyLineString(cls, prefix: str, shapely_path: shapely_geom.LineString) -> 'SvgPath':
        '''
        '''
        pts = list(shapely_path.coords)

        discretized_svg_path : List[complex] = [ complex( \
                    pt[0] / (ShapelyUtils.inchToShapelyScale / 25.4), 
                    pt[1] / (ShapelyUtils.inchToShapelyScale / 25.4)) for pt in pts]

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
    def fromShapelyPolygon(cls, prefix: str, polygon: shapely_geom.Polygon) -> 'SvgPath':
        '''
        Note:
            only 1 path "def" consisting of 1: 
        '''
        factor = 1.0 / (ShapelyUtils.inchToShapelyScale / 25.4)
            
        poly_scaled = shapely.affinity.scale(polygon, xfact=factor, yfact=factor, zfact=factor, origin=(0,0))

        path_str = poly_scaled.svg()

        svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
            version="1.1">
            <g>
            %s
            </g> 
        </svg>''' % path_str

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'temp_svg.svg')
            
            fp = open(filename, "w")
            fp.write(svg)
            fp.close()

            paths, attributes = svgpathtools.svg2paths(filename)

            attribs = attributes[0]
            attribs["fill"] = "#000000"

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




    

