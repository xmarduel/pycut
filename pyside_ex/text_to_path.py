'''
'''

from svgpathtools import wsvg, Line, QuadraticBezier, Path

from freetype import Face


def tuple_to_imag(t):
    return t[0] + t[1] * 1j

def test():
    # load font
    #face = Face('./Vera.ttf')
    #face = Face('./fonts/ziggy/ZIGGS___.TTF')
    #face = Face('./fonts/slaine/SLAINE.TTF')
    face = Face('./fonts/bitstream_vera_mono/VeraMono.ttf')

    #face.set_char_size(16,16)
    face.set_char_size(24 * 32)
    # initialize a chareacter
    face.load_char('a')

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
    outline = face.glyph.outline
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
            if len(segment) == 2:
                paths.append(Line(start=tuple_to_imag(segment[0]),
                                  end=tuple_to_imag(segment[1])))
            elif len(segment) == 3:
                paths.append(QuadraticBezier(start=tuple_to_imag(segment[0]),
                                         control=tuple_to_imag(segment[1]),
                                         end=tuple_to_imag(segment[2])))
            elif len(segment) == 4:
                C = ((segment[1][0] + segment[2][0]) / 2.0,
                     (segment[1][1] + segment[2][1]) / 2.0)

                paths.append(QuadraticBezier(start=tuple_to_imag(segment[0]),
                                             control=tuple_to_imag(segment[1]),
                                             end=tuple_to_imag(C)))
                paths.append(QuadraticBezier(start=tuple_to_imag(C),
                                             control=tuple_to_imag(segment[2]),
                                             end=tuple_to_imag(segment[3])))


        '''
        Set the start location to the end location and continue. 
        You can use the svgpathtools Path to merge the paths:
        '''
        start = end + 1

    path = Path(*paths)
    wsvg(path, filename="text2path.svg")

if __name__ == '__main__':
    test()