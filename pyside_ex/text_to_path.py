'''
This is a attempt to convert svt text to svg path...
'''
from typing import List

import freetype

from svgpathtools import wsvg, Line, QuadraticBezier, Path


   
class Char2SvgPath:
    '''
    # https://github.com/rougier/freetype-py/releases
    # https://github.com/rougier/freetype-py/blob/master/examples/glyph-vector-decompose.py
    '''

    CHAR_SIZE = 2048

    def __init__(self, char: str, font: str):
        '''
        fonts
         - './fonts/bitstream_vera_mono/VeraMono.ttf'
         - './fonts/ziggy/ZIGGS___.TTF'
         - './fonts/slaine/SLAINE.TTF'
         - 'C:\\Windows\\Fonts\\arial.ttf'
        '''
        self.char = char
        self.font = font

        # load font
        self.face = freetype.Face(self.font)

        # values for y-flip
        self.char_top = float(99999)
        self.top = float(99999)

        # values for x-translation
        self.char_leftmargin = float(99999)
        self.leftmargin = float(99999)

        '''
        The character widths and heights are specified in 1/64th of points. 
        A point is a physical distance, equaling 1/72th of an inch. Normally, it is not equivalent to a pixel.
        Value of 0 for the character width means ‘same as character height’, 
        value of 0 for the character height means ‘same as character width’. 
        
        Otherwise, it is possible to specify different character widths and heights.
        The horizontal and vertical device resolutions are expressed in dots-per-inch, or dpi. 
        Standard values are 72 or 96 dpi for display devices like the screen. 
        The resolution is used to compute the character pixel size from the character point size.
        Value of 0 for the horizontal resolution means ‘same as vertical resolution’, 
        value of 0 for the vertical resolution means ‘same as horizontal resolution’. 
        
        If both values are zero, 72 dpi is used for both dimensions.
        '''

        self.face.set_char_size(self.CHAR_SIZE, self.CHAR_SIZE) # -> x_ppem = y_ppem = 32

        # initialize a character - option FT_LOAD_NO_SCALE mandatory
        self.face.load_char(self.char, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_BITMAP)

        # to eval
        self.path = None

    def get_bbox(self) -> freetype.FT_BBox:
        '''
        print("BBOX = %d %d %d %d" % (bbox.xMin, bbox.xMax, bbox.yMin, bbox.yMax))
        '''
        outline : freetype.Outline = self.face.glyph.outline

        return outline.get_bbox()

    def set_top(self, top):
        self.top  = top

    def eval_top(self) -> float:
        '''
        '''
        outline : freetype.Outline = self.face.glyph.outline

        y = [t[1] for t in outline.points]

        self.char_top = max(y)
        self.top = max(y)

        return self.char_top

    def set_leftmargin(self, leftmargin):
        self.leftmargin  = leftmargin

    def eval_leftmargin(self) -> float:
        '''
        '''
        outline : freetype.Outline = self.face.glyph.outline

        x = [t[0] for t in outline.points]

        self.char_leftmargin = min(x)
        self.leftmargin = min(x)

        return self.char_leftmargin

    def get_kerning(self, prev):
        '''
        We’ll be converting a string character by character. 
        After converting this character to a path, you use the same method to convert the next character to a path,
        offset by the kerning:
        '''
        #o = Char2SvgPath(prev, self.font)
        #o_bbox = o.get_bbox()

        vector =  self.face.get_kerning(prev, self.char)
    
        print(dir(vector))
    
        print("kerning between %s and %s: x=%f  y=%f" % (prev, self.char, vector.x,  vector.y))
        
    def calc_path(self, fontsize: float) -> Path:
        '''
        fontsize: svg font-size in px
        '''
        def tuple2imag(t):
            return t[0] + t[1] * 1j

        
        if self.top == float(99999):
            self.eval_top()

        if self.leftmargin == float(99999):
            self.eval_leftmargin()

        top = self.top
        leftmargin = self.leftmargin

        # extra scaling
        scaling = fontsize / self.CHAR_SIZE
        
        '''
        You’ll need to flip the y values of the points in order to render
        the characters right-side-up:
        '''
        outline : freetype.Outline = self.face.glyph.outline


        # shift and flip the points
        outline_points = [ ((pt[0] - leftmargin) * scaling, (top - pt[1]) * scaling) for pt in outline.points ]

        '''
        The face has three lists of interest: the points, the tags, and the contours. 
        The points are the x/y coordinates of the start and end points of lines and  control points. 
        The tags indicate what type of point it is, where tag values of 0 are control points. 
        Finally, the contours are the end point list index for each shape. 
        Characters like i or ! have two shapes, most others have only one contour. 
        So, for each contour, we want to pick out only the tags and points for that contour.
        '''
        start, end = 0, 0
        paths = []

        for i in range(len(outline.contours)):
            end = outline.contours[i]
            points = outline_points[start:end + 1]
            points.append(points[0])
            tags = outline.tags[start:end + 1]
            tags.append(tags[0])

            '''
            Next, we want to split the points up into path segments, using the tags. If the tags are 0, 
            add the point to the current segment, else create a new segment, 
            so that control points stay with their path segments:
            '''
            segments = [[points[0], ], ]
            for j in range(1, len(points)):
                segments[-1].append(points[j])
                if tags[j] and j < (len(points) - 1):
                    segments.append([points[j], ])

            '''
            Then convert the segments to lines. 
            For lines with two control points (segment length 4), I could use the CubicBezier, 
            but I find that breaking it into two Quadratic Beziers where the end point for the first and 
            the start point of the second curve is the average of the control points, is more attractive:
            '''
            for segment in segments:
                #print("segment (len=%d)" % len(segment))

                if len(segment) == 2:
                    paths.append(Line(start=tuple2imag(segment[0]), end=tuple2imag(segment[1])))

                elif len(segment) == 3:
                    C12 = segment[1]

                    P1 = segment[0]
                    P2 = segment[2]
                
                    paths.append(QuadraticBezier(start=tuple2imag(P1), control=tuple2imag(C12), end=tuple2imag(P2)))
                                         
                elif len(segment) == 4:
                    C12 = segment[1]
                    C23 = segment[2]

                    P1 = segment[0]
                    P2 = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)
                    P3 = segment[3]

                    paths.append(QuadraticBezier(start=tuple2imag(P1), control=tuple2imag(C12), end=tuple2imag(P2)))
                    paths.append(QuadraticBezier(start=tuple2imag(P2), control=tuple2imag(C23), end=tuple2imag(P3)))

                elif len(segment) == 5:
                    C12 = segment[1]
                    C23 = segment[2]
                    C34 = segment[3]

                    P1 = segment[0]
                    P2 = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)
                    P3 = ((segment[2][0] + segment[3][0]) / 2.0, (segment[2][1] + segment[3][1]) / 2.0)
                    P4 = segment[4]

                    paths.append(QuadraticBezier(start=tuple2imag(P1), control=tuple2imag(C12), end=tuple2imag(P2)))
                    paths.append(QuadraticBezier(start=tuple2imag(P2), control=tuple2imag(C23), end=tuple2imag(P3)))
                    paths.append(QuadraticBezier(start=tuple2imag(P3), control=tuple2imag(C34), end=tuple2imag(P4)))

                elif len(segment) == 6:
                    C12 = segment[1]
                    C23 = segment[2]
                    C34 = segment[3]
                    C45 = segment[4]

                    P1 = segment[0]
                    P2 = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)
                    P3 = ((segment[2][0] + segment[3][0]) / 2.0, (segment[2][1] + segment[3][1]) / 2.0)
                    P4 = ((segment[3][0] + segment[4][0]) / 2.0, (segment[3][1] + segment[4][1]) / 2.0)
                    P5 = segment[5]

                    paths.append(QuadraticBezier(start=tuple2imag(P1), control=tuple2imag(C12), end=tuple2imag(P2)))
                    paths.append(QuadraticBezier(start=tuple2imag(P2), control=tuple2imag(C23), end=tuple2imag(P3)))
                    paths.append(QuadraticBezier(start=tuple2imag(P3), control=tuple2imag(C34), end=tuple2imag(P4)))
                    paths.append(QuadraticBezier(start=tuple2imag(P4), control=tuple2imag(C45), end=tuple2imag(P5)))

                else:
                    # with algo

                    # first
                    Ps = segment[0]
                    Ctrl = segment[1]
                    Pe = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)

                    paths.append(QuadraticBezier(start=tuple2imag(Ps), control=tuple2imag(Ctrl), end=tuple2imag(Pe)))

                    # second - ...
                    for k in range(2,len(segment)-2):
                        Ps = ((segment[k-1][0] + segment[k  ][0]) / 2.0, (segment[k-1][1] + segment[k  ][1]) / 2.0)
                        Ctrl = segment[k]
                        Pe = ((segment[k  ][0] + segment[k+1][0]) / 2.0, (segment[k  ][1] + segment[k+1][1]) / 2.0)
                        
                        paths.append(QuadraticBezier(start=tuple2imag(Ps), control=tuple2imag(Ctrl), end=tuple2imag(Pe)))

                    # last
                    N = len(segments) - 1
                    Ps = ((segment[N-2][0] + segment[N-1][0]) / 2.0, (segment[N-2][1] + segment[N-1][1]) / 2.0)
                    Ctrl = segment[N-1]
                    Pe = segment[N]

                    paths.append(QuadraticBezier(start=tuple2imag(Ps), control=tuple2imag(Ctrl), end=tuple2imag(Pe)))

            '''
            Set the start location to the end location and continue. 
            You can use the svgpathtools Path to merge the paths:
            '''
            start = end + 1

        self.path = Path(*paths)

        return self.path

    def write_path(self):
        print("hand made path: %s" % self.path.d())
        wsvg(self.path, filename="char2path_%s_convert.svg" % self.char)

    def freetype_decompose(self) -> str:
        '''
        '''
        outline : freetype.Outline = self.face.glyph.outline

        def move_to(a, ctx):
            ctx.append("M {},{}".format(a.x, a.y))

        def line_to(a, ctx):
            ctx.append("L {},{}".format(a.x, a.y))

        def conic_to(a, b, ctx):
            ctx.append("Q {},{} {},{}".format(a.x, a.y, b.x, b.y))

        def cubic_to(a, b, c, ctx):
            ctx.append("C {},{} {},{} {},{}".format(a.x, a.y, b.x, b.y, c.x, c.y))


        ctx= []
       
        outline.decompose(ctx, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to)

        svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <svg xmlns="http://www.w3.org/2000/svg"
                width="100mm"
                height="100mm"
                viewBox="0 0 100 100"
                version="1.1">
                <path
                    transform="translate(-0.82 0) matrix(1,0, 0,-1, 0,7.5857) scale(0.0051677)"
                    style="fill:none;stroke:#000000;stroke-width:2;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"
                    d="{}"
                />
            </svg>""".format(" ".join(ctx))

        print(svg)

        fp = open("char2path_%s_decompose.svg" % self.char, "w")
        fp.write(svg)
        fp.close()

        return svg



class String2SvgPaths:
    '''
    '''
    def __init__(self, text: str, font: str):
        self.text = text
        self.font = font

        self.top = 0
        self.leftmargin = 0

        self.paths : List[Path] = []

    def calc_top(self):
        top = 0
        for ch in self.text:
            o = Char2SvgPath(ch, self.font)
            o_top = o.eval_top()

            top = max(top, o_top)
        
        self.top = top

    def calc_leftmargin(self):
        o = Char2SvgPath(self.text[0], self.font)

        self.leftmargin = o.eval_leftmargin()
    
    def calc_paths(self, fontsize: float) -> List[Path]:
        '''
        '''
        self.calc_leftmargin()
        self.calc_top()

        paths = []

        for ch in self.text:
            o = Char2SvgPath(ch, self.font)
            o.set_top(self.top)
            o.set_leftmargin(self.leftmargin)
           
            paths.append(o.calc_path(fontsize))

        # now, all paths have to be shifted on the right with cumulativ values
        # the first one is Ok
        self.paths .append(paths[0])

        # TODO: find the right shift
        shift = 2048 * fontsize / Char2SvgPath.CHAR_SIZE
        for path in paths[1:]:
            path = path.translated(shift)
            self.paths.append(path)
            shift += 2048 * fontsize / Char2SvgPath.CHAR_SIZE

        return self.paths

    def write_paths(self):
        paths = ""
        for path in self.paths:
            paths += '        <path d="%s" />\n' % path.d()

        fp = open("text2paths_%s_convert.svg" % self.text, "w")

        fp.write("""<?xml version="1.0" ?>
<svg xmlns="http://www.w3.org/2000/svg" 
    xmlns:svg="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" 
    height="600mm" 
    width="600mm"
    version="1.1" 
    viewBox="0 0 600 600">
    <g
        id="text1437"
        style="fill:#ff2222:fill-opacity:0.5;font-size:10.5833px;line-height:1.25;font-family:Arial;-inkscape-font-specification:'Arial, Normal';stroke-width:0.264583">
%s
    </g>
</svg>  """ % paths)

        fp.close()

    

if __name__ == '__main__':
    char = 'B'
    font = 'C:\\Windows\\Fonts\\arial.ttf'

    fontsize = 10.5833 # px

    o = Char2SvgPath(char, font)

    # per freetype decompose -----------------------------------
    #svg = o.freetype_decompose()

    # convert per hand, shifting x and flipping y --------------
    o.calc_path(fontsize)
    o.write_path()


    oo = String2SvgPaths("Bac", font)
    # convert per hand, shifting x and flipping y --------------
    oo.calc_paths(fontsize)
    oo.write_paths()