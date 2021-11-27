
from typing import List

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
            else:  # 'Arc', 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                nb_samples = seg_length * self.samples_coeff
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
                complex(int(pt.X / 1000), int(pt.Y / 1000)) for pt in clipper_path]


        svgpathtools_path = svgpathtools.Path()

        for i in range(len(svgpathtools_pts)-1):
            start = svgpathtools_pts[i]
            end   = svgpathtools_pts[i+1]

            svgpathtools_path.append(svgpathtools.Line(start, end))

        svg_d = svgpathtools_path.d()

        return SvgPath('clipper', {'d': svg_d})

