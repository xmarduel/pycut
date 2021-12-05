
from typing import List
from typing import Dict

import tempfile

import svgpathtools
import numpy as np
import clipper.clipper as ClipperLib

from clipper_utils import ClipperUtils


class SvgPath:
    '''
    Transform svgpathtools 'Path' to 'ClipperLib' path

    - svgpathtools 'Path' are list of 'Segment(s)' and
    each segment has a list of points, giveninto the 'complex' type (a+bj)

    - ClipperLib 'Path' are list of IntPoint (X,Y)

    so the transformation is straightforward

    Convention:
    - a svg <path> definition is noted: svg_path_d
    - a path from svgpathtools is noted: svg_path
    - the discretization of a svg_path results in a numpy array, noted: np_svg_path
    - a clipper path is noted: clipper_path  (a 'ClipperLib.IntPointVector')
    '''
    PYCUT_SAMPLE_LEN_COEFF = 2

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

        FIXME: Take care not to add twice the same points
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
                
                _pts = []
                for k in range(nb_samples):
                    _pts.append(segment.point(float(k)/float(nb_samples)))
                # and the last
                _pts.append(segment.point(1))

                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                incr = 1.0 / nb_samples

                samples = [x* incr for x in range(0, nb_samples)]
                pts = segment.points(samples)
                # and the last
                pts.append(segment.point(1))

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
    def fromClipperPath(cls, clipper_path: ClipperLib.IntPointVector) -> 'SvgPath':
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

        return SvgPath('clipper', {'d': svg_path.d()})


class SvgTransformer:
    '''
    '''
    def __init__(self, svg):
        self.svg = svg

        # a tmp file
        fp = open("xx.svg", 'w')
        fp.write(svg)
        fp.close()

        self.ini_svg_paths, self.ini_attribs = svgpathtools.svg2paths('xx.svg')

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
            dd = svg_path.p_attrs['d']

            all_paths += '<path id="%s_%d" style="fill:#111111;stroke-width:0;stroke:#00ff00"  d="%s" />'  % (id, k, dd)
        
        svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="100"
                height="100"
                viewBox="0 0 100 100"
                version="1.1">
                <style>svg { background-color: green; }</style>
                <g>
                 %s
                </g> 
             </svg>''' % all_paths

        print(svg)
        
        return svg
    

