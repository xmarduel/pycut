'''
'''
import freetype

from svgpathtools import wsvg, Line, QuadraticBezier, Path





def outline_decompose(outline):
    '''
    # https://github.com/rougier/freetype-py/releases
    # https://github.com/rougier/freetype-py/blob/master/examples/glyph-vector-decompose.py
    '''
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
   version="1.1"
   >
    <path
      transform="scale(0.00338) scale(10)"
      style="fill:none;stroke:#000000;stroke-width:2;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"
      d="{}"
    />
</svg>
""".format(" ".join(ctx))

    print(svg)

    fp = open("text2path_decompose.svg", "w")
    fp.write(svg)
    fp.close()


def make_svgpathtools_path(outline):
    '''
    '''
    def tuple_to_imag(t):
        return t[0] + t[1] * 1j

    y = [t[1] for t in outline.points]
    # flip the points
    outline_points = [(p[0], max(y) - p[1]) for p in outline.points]

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
                paths.append(Line(start=tuple_to_imag(segment[0]), end=tuple_to_imag(segment[1])))

            elif len(segment) == 3:
                C12 = segment[1]

                P1 = segment[0]
                P2 = segment[2]
                
                paths.append(QuadraticBezier(start=tuple_to_imag(P1), control=tuple_to_imag(C12), end=tuple_to_imag(P2)))
                                         
            elif len(segment) == 4:
                C12 = segment[1]
                C23 = segment[2]

                P1 = segment[0]
                P2 = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)
                P3 = segment[3]

                paths.append(QuadraticBezier(start=tuple_to_imag(P1), control=tuple_to_imag(C12), end=tuple_to_imag(P2)))
                paths.append(QuadraticBezier(start=tuple_to_imag(P2), control=tuple_to_imag(C23), end=tuple_to_imag(P3)))

            elif len(segment) == 5:
                C12 = segment[1]
                C23 = segment[2]
                C34 = segment[3]

                P1 = segment[0]
                P2 = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)
                P3 = ((segment[2][0] + segment[3][0]) / 2.0, (segment[2][1] + segment[3][1]) / 2.0)
                P4 = segment[4]

                paths.append(QuadraticBezier(start=tuple_to_imag(P1), control=tuple_to_imag(C12), end=tuple_to_imag(P2)))
                paths.append(QuadraticBezier(start=tuple_to_imag(P2), control=tuple_to_imag(C23), end=tuple_to_imag(P3)))
                paths.append(QuadraticBezier(start=tuple_to_imag(P3), control=tuple_to_imag(C34), end=tuple_to_imag(P4)))

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

                paths.append(QuadraticBezier(start=tuple_to_imag(P1), control=tuple_to_imag(C12), end=tuple_to_imag(P2)))
                paths.append(QuadraticBezier(start=tuple_to_imag(P2), control=tuple_to_imag(C23), end=tuple_to_imag(P3)))
                paths.append(QuadraticBezier(start=tuple_to_imag(P3), control=tuple_to_imag(C34), end=tuple_to_imag(P4)))
                paths.append(QuadraticBezier(start=tuple_to_imag(P4), control=tuple_to_imag(C45), end=tuple_to_imag(P5)))

            else:
                pass

        '''
        Set the start location to the end location and continue. 
        You can use the svgpathtools Path to merge the paths:
        '''
        start = end + 1

    path = Path(*paths)
    print("hand made path: %s" % path.d())
    wsvg(path, filename="text2path.svg")


    bbox = outline.get_bbox()
    print("BBOX = %d %d %d %d" % (bbox.xMin, bbox.xMax, bbox.yMin, bbox.yMax))



def make_svg_path():
    # load font
    #face = Face('./fonts/bitstream_vera_mono/VeraMono.ttf')
    #face = Face('./fonts/ziggy/ZIGGS___.TTF')
    #face = Face('./fonts/slaine/SLAINE.TTF')
    face = freetype.Face('C:\\Windows\\Fonts\\arial.ttf')

    face.set_char_size(48 * 64)
    # initialize a chareacter
    #face.load_char('a', freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_BITMAP)
    face.load_char('B', freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_BITMAP)

    '''
    We’ll be converting a string character by character. 
    After converting this character to a path, you use the same method to convert the next character to a path,
    offset by the kerning:
    '''
    face.get_kerning('a', 'b')

    '''
    You’ll need to flip the y values of the points in order to render
    the characters right-side-up:
    '''
    outline : freetype.Outline = face.glyph.outline


    # per freetype decompose -----------------------------------
    outline_decompose(outline)

    # per hand -------------------------------------------------
    make_svgpathtools_path(outline)
    
    

if __name__ == '__main__':
    make_svg_path()