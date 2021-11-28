
from typing import List

import tempfile

import svgpathtools
import numpy as np
import clipper.clipper as ClipperLib


class SvgPath:
    '''
    Transform svgpathtools 'Path' to 'ClipperLib' path

    - svgpathtools 'Path' are list of 'Segment(s)' and
    each segment has a list of points, giveninto the 'complex' type (a+bj)

    - ClipperLib 'Path' are list of IntPoint (X,Y)

    so the transformation is straightforward
    '''
    samples_coeff = 2

    inchToClipperScale = 100000  # Scale inch to Clipper
    cleanPolyDist = inchToClipperScale / 100000
    arcTolerance = inchToClipperScale / 40000

    def __init__(self, p_id: str, p_attrs):
        '''
        '''
        self.p_id = p_id
        self.p_attrs = p_attrs

    def discretize(self):
        '''
        Transform a list of svgpathtools Segments info complex points
        - Line: omly 2 points
        - Others: discretize
        '''
        path = svgpathtools.parse_path(self.p_attrs['d'])

        points = np.array([], dtype=np.complex128)
        
        for segment in path:
            if segment.__class__.__name__ == 'Line':
                # start and end
                pts = segment.points([0,1])
            elif segment.__class__.__name__ == 'Arc':
                seg_length = segment.length()

                nb_samples = int(seg_length * self.samples_coeff)
                
                # no 'points' method for 'Arc'!
                _pts = []
                for k in range(nb_samples):
                    _pts.append(segment.point(float(k)/float(nb_samples)))
                # and the last
                _pts.append(segment.point(1))

                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                nb_samples = int(seg_length * self.samples_coeff)
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
        discretized_svg_path = self.discretize()

        path = ClipperLib.IntPointVector()

        for ppc in discretized_svg_path:
            pt = ClipperLib.IntPoint(int(ppc.real*1000), int(ppc.imag*1000))
            path.append(pt)

        return path

    @classmethod
    def fromClipperPath(cls, clipper_path: ClipperLib.IntPointVector) -> 'SvgPath':
        '''
        '''
        svgpathtools_pts : List[complex] = [  \
                complex(pt.X / 1000, pt.Y / 1000) for pt in clipper_path]


        svgpathtools_path = svgpathtools.Path()

        for i in range(len(svgpathtools_pts)-1):
            start = svgpathtools_pts[i]
            end   = svgpathtools_pts[i+1]

            svgpathtools_path.append(svgpathtools.Line(start, end))

        svg_d = svgpathtools_path.d()

        return SvgPath('clipper', {'d': svg_d})


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
    

