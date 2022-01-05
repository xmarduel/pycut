
import os
import math

from typing import List
from typing import Dict

import tempfile

import xml.etree.ElementTree as ET

import svgpathtools
import numpy as np

#from clipper_613 import clipper_613 as ClipperLib
from clipper_642 import clipper_642 as ClipperLib

from clipper_utils import ClipperUtils

M_PI = math.acos(-1)


class SvgPath:
    '''
    Transform svgpathtools 'Path' to 'ClipperLib' path

    - svgpathtools 'Path' are list of 'Segment(s)' and
    each segment has a list of points, given in format 'complex type' (a+bj)

    - ClipperLib 'Path' are list of IntPoint (X,Y)

    so the transformation is straightforward

    Convention:
    - a svg <path> definition is noted: svg_path_d
    - a path from svgpathtools is noted: svg_path
    - the discretization of a svg_path results in a numpy array, noted: np_svg_path
    - a clipper path is noted: clipper_path  (a 'ClipperLib.IntPointVector')
    '''
    PYCUT_SAMPLE_LEN_COEFF = 100 # is in jsCut 1.0/0.01 ie the same
    PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5 # is in jsCut 1

    @classmethod
    def set_arc_precision(cls, arc_min_segments_length):
        '''
        '''
        cls.PYCUT_SAMPLE_LEN_COEFF = 1.0 / arc_min_segments_length

    def set_arc_min_nb_segments(cls, arc_min_nb_segments):
        '''
        '''
        cls.PYCUT_SAMPLE_MIN_NB_SEGMENTS = arc_min_nb_segments

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

        TODO: Take care not to add twice the same points
        - Arc
        - Beziers
        '''
        points = np.array([], dtype=np.complex128)
        
        for k, segment in enumerate(self.svg_path):
            if segment.__class__.__name__ == 'Line':
                # start and end
                if len(self.svg_path) == 1:
                    pts = segment.points([0,1])
                else:
                    if k < len(self.svg_path)-1:
                        pts = segment.points([0])
                    else:
                        pts = segment.points([0, 1])
            elif segment.__class__.__name__ == 'Arc':
                # no 'points' method for 'Arc'!
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                _pts = []
                for k in range(nb_samples+1):
                    _pts.append(segment.point(float(k)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                incr = 1.0 / nb_samples

                samples = [x* incr for x in range(0, nb_samples+1)]
                pts = segment.points(samples)

            points = np.concatenate((points, pts))

        return points

    def toClipperPath(self) -> ClipperLib.IntPointVector:
        '''
        '''
        np_svg_path = self.discretize()

        clipper_path = ClipperLib.IntPointVector()

        for complex_pt in np_svg_path:
            pt = ClipperLib.IntPoint( \
                int(complex_pt.real * (ClipperUtils.inchToClipperScale / 25.4)),
                int(complex_pt.imag * (ClipperUtils.inchToClipperScale / 25.4)))
            clipper_path.append(pt)

        return clipper_path

    @classmethod
    def fromCircleDef(cls, center, radius) -> 'SvgPath':
        '''
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
    def fromClipperPath(cls, prefix: str, clipper_path: ClipperLib.IntPointVector) -> 'SvgPath':
        '''
        '''
        discretized_svg_path : List[complex] = [ complex( \
                    pt.X / (ClipperUtils.inchToClipperScale / 25.4), 
                    pt.Y / (ClipperUtils.inchToClipperScale / 25.4)) for pt in clipper_path]


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
    def fromClipperPaths(cls, prefix: str, clipper_paths: ClipperLib.PathVector) -> 'SvgPath':
        '''
        Note:
            only 1 path "def" consisting of 2 or more lines : 
            for the path interior be filled in color -> fill-rule is 'evenodd'
        '''
        discretized_svg_paths = []
        for clipper_path in clipper_paths:
            discretized_svg_path : List[complex] = [ complex( \
                    pt.X / (ClipperUtils.inchToClipperScale / 25.4), 
                    pt.Y / (ClipperUtils.inchToClipperScale / 25.4)) for pt in clipper_path]
            
            discretized_svg_paths.append(discretized_svg_path)

        svg_path = svgpathtools.Path()

        for discretized_svg_path in discretized_svg_paths:
            for i in range(len(discretized_svg_path)-1):
                start = discretized_svg_path[i]
                end   = discretized_svg_path[i+1]

                svg_path.append(svgpathtools.Line(start, end))

        return SvgPath(prefix, {'d': svg_path.d(), 'fill-rule': 'evenodd'})


class SvgTransformer:
    '''
    '''
    def __init__(self, svg):
        self.svg = svg

        # a tmp file
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'pycut_svg.svg')
            # use path
            fp = open(path, 'w')
            fp.write(svg)
            fp.close()

            self.ini_svg_paths, self.ini_attribs = svgpathtools.svg2paths(path)

    def augment(self, svg_paths: List[SvgPath]) -> str:
        '''
        '''
        all_paths = ""

        for k, svg_path in enumerate(self.ini_svg_paths):
            init_attrib = self.ini_attribs[k]

            svg_attrs = ''
            for key, value in init_attrib.items():
                svg_attrs += ' %s="%s"' % (key, value)

            all_paths += '<path %s />' % svg_attrs

        for k, svg_path in enumerate(svg_paths):
            id = svg_path.p_id
            d_def = svg_path.p_attrs['d']

            stroke = '#00ff00'
            stroke_width = '0'
            
            fill = svg_path.p_attrs.get("fill", "#111111")
            fill_opacity = svg_path.p_attrs.get("fill-opacity", "1.0")
            fill_rule = svg_path.p_attrs.get("fill-rule", "nonzero")

            path = '<path id="%(id)s_%(counter)d" style="stroke:%(stroke)s;stroke-width:%(stroke_width)s;fill:%(fill)s;fill-opacity:%(fill_opacity)s;fill-rule:%(fill_rule)s;" \
              d="%(d_def)s" />' % {
                'id': id, 
                'counter': k, 
                'fill': fill,
                'stroke_width': stroke_width,
                'stroke': stroke,
                'fill_opacity': fill_opacity, 
                'fill_rule': fill_rule, 
                'd_def': d_def
            }

            all_paths += path + '\r\n'
        
        root = ET.fromstring(self.svg)
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

        for k, svg_path in enumerate(self.ini_svg_paths):
            init_attrib = self.ini_attribs[k]

            svg_attrs = ''
            for key, value in init_attrib.items():
                svg_attrs += ' %s="%s"' % (key, value)

            all_paths += '<path %s />' % svg_attrs

        for k, svg_path in enumerate(svg_paths):
            id = svg_path.p_id
            d_def = svg_path.p_attrs['d']

            stroke = '#00ff00'
            stroke_width = '0.2'
            
            fill = 'none'

            all_paths += '<path id="%(id)s_%(counter)d" style="stroke:%(stroke)s;stroke-width:%(stroke_width)s;fill:%(fill)s" d="%(d_def)s" />' % {
                'id': id, 
                'counter': k,
                'stroke_width': stroke_width,
                'stroke': stroke,
                'fill': fill,
                'd_def': d_def
            }
        
        root = ET.fromstring(self.svg)
        root_attrib = root.attrib

        svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="%s"
                height="%s"
                viewBox="%s"
                version="1.1">
                <style>svg { background-color: green; }</style>
                <g>
                 %s
                </g> 
             </svg>''' % (root_attrib["width"], root_attrib["height"], root_attrib["viewBox"], all_paths)

        #print(svg)
        
        return svg




    

