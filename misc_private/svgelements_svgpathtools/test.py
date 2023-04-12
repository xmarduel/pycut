
import copy
import math

from typing import List

import numpy as np

import svgpathtools
import svgelements

class SvgPath1:
    '''
    svgpathtools
    '''
    PYCUT_SAMPLE_LEN_COEFF = 10 # 10 points per "svg unit" ie arc of len 10 -> 100 pts discretization
    PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5 # is in jsCut 1

    def __init__(self, svg_path: svgpathtools.Path, attribs):
        self.svg_path = svg_path
        self.attribs = attribs
        self.tag = "?"
        self.p_id = attribs['id']
        self.p_d = svg_path.d()
        self.path_closed = svg_path.isclosedac() or svg_path.closed

    @classmethod
    def read_paths_from_file(cls, svgfilename) -> List['SvgPath1']:
        '''
        '''
        paths, attributes = svgpathtools.svg2paths(svgfilename)
        
        svgpaths = []
        
        for k in range(len(paths)):
            svgpaths.append(SvgPath1(paths[k], attributes[k]))

        return svgpaths

    def dump(self):
        for seg in self.svg_path:
            print(seg)

    def is_closed(self) -> bool :
        return self.svg_path.isclosedac()
    
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

        first_seg = True
        
        for k, segment in enumerate(self.svg_path):

            ## ---------------------------------------
            if ignore_segment(k, segment) == True:
                continue
            ## ---------------------------------------

            if segment.__class__.__name__ == 'Line':
                if first_seg:
                    # start and end points
                    pts = segment.points([0, 1])
                else:
                    # not the start point (avoid duplicated)
                    pts = segment.points([1])
                    
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
                    for p in range(1, nb_samples+1):
                        # not the start point (avoid duplicated)
                        _pts.append(segment.point(float(p)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            else:  # 'QuadraticBezier', 'CubicBezier'
                seg_length = segment.length()

                _pts = []

                ### SVGPATHTOOLS BUG !!!
                if seg_length == math.inf:  # WTF!

                    p1 = segment.start
                    p2 = segment.end

                    line = svgpathtools.Line(p1, p2)

                    # start and end points
                    if first_seg:
                        _pts = line.points([0, 1])
                    else:
                        _pts = line.points([1])

                else:

                    nb_samples = int(seg_length * self.PYCUT_SAMPLE_LEN_COEFF)
                    nb_samples = max(nb_samples, self.PYCUT_SAMPLE_MIN_NB_SEGMENTS)
                
                    if first_seg:
                        for p in range(0, nb_samples+1):
                            _pts.append(segment.point(float(p)/float(nb_samples)))
                    else:
                        # not the start point (avoid duplicated)
                        for p in range(1, nb_samples+1):
                            _pts.append(segment.point(float(p)/float(nb_samples)))

                pts = np.array(_pts, dtype=np.complex128)

            points = np.concatenate((points, pts))


            first_seg = False

        # shapely fix :
        extra_middle_point = (points[0] + points[1]) / 2.0

        points = np.concatenate(([extra_middle_point], points[1:], [points[0]]))

        return points

class SvgPath2:
    '''
    svgelements
    '''
    PYCUT_SAMPLE_LEN_COEFF = 10 # 10 points per "svg unit" ie arc of len 10 -> 100 pts discretization
    PYCUT_SAMPLE_MIN_NB_SEGMENTS = 5 # is in jsCut 1

    def __init__(self, svg_path: svgelements.Path):
        self.svg_path = svg_path
        self.attribs = copy.deepcopy(svg_path.values)
        self.tag = svg_path.values["tag"]
        self.p_id = svg_path.values['id']
        self.p_d = svg_path.d()
        self.path_closed = svg_path.closed()

        # not so happy with this
        del self.attribs[""]
        del self.attribs["svg"]
        del self.attribs["width"]
        del self.attribs["height"]
        del self.attribs["version"]
        del self.attribs["tag"]
    

    @classmethod
    def read_paths_from_file(cls, svgfilename)  -> List['SvgPath2']:
        svg = svgelements.SVG.parse(svgfilename,
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

        return [ SvgPath2(path) for path in paths ]
  
    def dump(self):
        for seg in self.svg_path.segments():
            print(seg)

    def is_closed(self) -> bool :
        return self.svg_path.segments()[-1].__class__.__name__ == "Close"
     
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

                _pts_complex = [ complex(_pt.x,+ _pt.y) for _pt in _pts]
                    
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

                _pts_complex = [ complex(_pt.x,+ _pt.y) for _pt in _pts]

                pts = np.array(_pts_complex, dtype=np.complex128)

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

                _pts_complex = [ complex(_pt.x,+ _pt.y) for _pt in _pts]

                pts = np.array(_pts, dtype=np.complex128)

            points = np.concatenate((points, pts))


            first_seg = False

        # shapely fix:
        extra_middle_point = (points[0] + points[1]) / 2.0

        points = np.concatenate(([extra_middle_point], points[1:], [points[0]]))

        return points


def main():
    '''
    compare results of svgpathtools and svgelements
    '''
    svgfilename = "C:\\Users\\xavie\\Documents\\GITHUB\\pycut\\misc_private\cnc1310\\cnc1310-s55-90x113mm_clamp.resolved.svg"
    svgfilename = "C:\\Users\\xavie\\Documents\\GITHUB\\pycut\\misc_private\svg\\two_circles.svg"

    #svgpathtools
    xpaths = SvgPath1.read_paths_from_file(svgfilename)

    # svgelements
    ypaths = SvgPath2.read_paths_from_file(svgfilename)

    print(" Nb paths (svgpathtools) = %d" % len(xpaths))
    print(" Nb paths (svgelements)  = %d" % len(ypaths))

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++\n")

    for k in range(len(xpaths)):
        xpaths[k].dump()
        print("is closed ? ", xpaths[k].is_closed())
        print("---------------------------------------------------")
        ypaths[k].dump()
        print("is closed ? ", ypaths[k].is_closed())

        print("\n\n")

    # discretisation
    xpts = xpaths[0].discretize_closed_path()
    #print(xpts)
    ypts = ypaths[0].discretize_closed_path()
    #print(ypts)
    

if __name__ == '__main__':
    main()