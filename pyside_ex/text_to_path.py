'''
Convert svg text to svg path(s)
'''

'''
with inkscape: can inkscape python module do that ? or do I need a subprocess command ?

command line:
> "C:\Program Files\Inkscape\bin\inkscape.com" in.svg  --export-text-to-path -o out.svg

-> all svg elements are converted! (not only text)
-> warning: transformations are kept, this is bad for pycut!

transformations have to be resolved in Inkscape, with ungroup/group operations
      
Inside python:
--------------

import subprocess
subprocess.call("inkscape.com in.svg --export-text-to-path -o out.svg", shell = True)
'''

import glob

from typing import List
from typing import Tuple

import freetype
from lxml import etree
from svgpathtools import wsvg, Line, QuadraticBezier, Path



class SvgTextObject:
    '''
    '''
    def __init__(self, elt: etree.Element):
        '''
        '''
        # the xml element as etree element object
        self.elt = elt
        self.elt_style = self.extract_style()

        self.font_family = self.elt_style.get("font-family", "arial")
        self.font_style = self.elt_style.get("font-style", "regular")
        self.font_size = self.elt_style.get("font-size", "10.5833px")

        self.text = self.extract_text()
        self.position = self.extract_position()
        self.id = self.extract_id()

    def extract_style(self):
        '''
        '''
        style : str = self.elt.attrib["style"]

        style_items = style.split(";")

        elt_style = {}

        for item in  style_items:
            key, value = item.split(":")

            elt_style[key] = value

        return elt_style

    def extract_text(self):
        '''
        The text value
        - as text data of the <text> etree element
        - as text data of the <tspan> etree children
        '''
        text = ""

        if len(self.elt):
            # has children
            for child in self.elt:
                if child.tag == "{http://www.w3.org/2000/svg}tspan":
                    text += child.text
        else:
            text = self.elt.text

        return text

    def extract_position(self):
        '''
        '''
        x = self.elt.attrib["x"]
        y = self.elt.attrib["y"]

        return (float(x), float(y))

    def extract_id(self):
        '''
        '''
        id = self.elt.attrib["id"]

        return id

    def to_path(self):
        '''
        '''
        fontfile = FontFiles.get_fontfile(self.font_family, self.font_style)

        if fontfile:
            converter = String2SvgPaths(self.text, fontfile)
            converter.calc_paths(self.font_size, self.position)

            # paths are stored in converter.paths
            pass



class SvgTextManager:
    '''
    collect <text> elements and make of them SvgTextObject objects
    '''
    def __init__(self, svgfile):
        '''
        '''
        self.svgfile = svgfile

        self.tree = etree.parse(svgfile)
        self.svgtextobjects = self.collect_svgtext_objects()

    def collect_svgtext_objects(self) -> List[SvgTextObject]:
        '''
        '''
        svgtextobjects = []

        elements = self.tree.findall(".//{http://www.w3.org/2000/svg}text")

        for elt in elements:
            o = SvgTextObject(elt)
            svgtextobjects.append(o)

        return svgtextobjects



class FontFiles:
    '''
    Create a dictionary of the type (font-family, font-style) -> font file
    
    in order to, from the svg text style font-family/font-style, to
    retrieve the right font file
    
    ex: font-family : Broadway
        font-style  : normal            -> 'C:\\Windows\\Fonts\\BROADW.TTF'

    PS: from Inkscape, there is also the following:
    
    -inkscape-font-specification:'Broadway, Normal'  --- can I use it ?

    
    '''
    lookup = None

    @classmethod
    def setupFonts(cls):
        '''
        look into the C:\\Windows\\Fonts folder and fill the lookup
        '''
        ttfs = glob.glob("C:\\Windows\\Fonts\\*.ttf")

        for ttf in ttfs:
            face = freetype.Face(ttf)
            family = face.postscript_name
            style = face.style_name
            
            cls.lookup[(family, style)] = ttf

    @classmethod
    def get_fontfile(cls, family: str, style: str):
        '''
        to improve
        '''
        if cls.lookup is None:
            cls.setupFonts()

        return cls.lookup[(family, style)]

    
   
class Char2SvgPath:
    '''
    '''
    CHAR_SIZE = 2048

    def __init__(self, char: str, font: str):
        '''
        fonts
         - './fonts/bitstream_vera_mono/VeraMono.ttf'
         - './fonts/ziggy/ZIGGS___.TTF'
         - './fonts/slaine/SLAINE.TTF'
         - 'C:\\Windows\\Fonts\\arial.ttf'
         - 'C:\\Windows\\Fonts\\BROADW.ttf'
        '''
        self.char = char
        self.font = font

        # load font
        self.face = freetype.Face(self.font)

        self.face.set_char_size(self.CHAR_SIZE, self.CHAR_SIZE) # -> x_ppem = y_ppem = 32
        
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
        # initialize a character - option FT_LOAD_NO_SCALE mandatory
        self.face.load_char(self.char, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_BITMAP)

        # glyph info
        self.glyph_index = self.face.get_char_index(self.char)
        self.glyph_adv = self.face.get_advance(self.glyph_index, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_BITMAP)

        self.bbox = self.face.glyph.outline.get_bbox()

        # evaluating the path:
        # --------------------

        # values for y-flip - if not set, use bbox
        self.yflip_value = None
        # values for x-translation - if not set, use bbox
        self.xshift_value = None

        # to eval
        self.path = None

    def set_yflip_value(self, val):
        '''
        '''
        self.yflip_value  = val

    def set_xshift_value(self, val):
        '''
        '''
        self.xshift_value  = val

    def get_kerning(self, prev):
        '''
        We’ll be converting a string character by character. 
        After converting this character to a path, you use the same method to convert the next character to a path,
        offset by the kerning

        Humm...
        '''
        o = Char2SvgPath(prev, self.font)
        

        vector =  self.face.get_kerning(o.glyph_index, self.glyph_index)
    
        print(dir(vector))
    
        print("kerning between %s and %s: x=%f  y=%f" % (prev, self.char, vector.x,  vector.y))
        
    def calc_shift(self, next_ch: str):
        '''
        '''
        # actually without kerning! still Ok!
        # oo = Char2SvgPath(next_ch, self.font)

        shift = self.glyph_adv 

        return shift

    def calc_path(self, fontsize: float) -> Path:
        '''
        fontsize: svg font-size in px
        '''
        def tuple2complex(t):
            return t[0] + t[1] * 1j

        
        yflip = self.yflip_value
        if yflip == None:
            yflip = self.bbox.yMax

        xshift = self.xshift_value
        if  xshift == None:
            xshift = self.bbox.xMin

        # extra scaling
        scaling = fontsize / self.CHAR_SIZE
        
        '''
        You’ll need to flip the y values of the points in order to render
        the characters right-side-up:
        '''
        outline : freetype.Outline = self.face.glyph.outline


        # shift and flip the points
        outline_points = [ ((pt[0] - xshift) * scaling, (yflip - pt[1]) * scaling) for pt in outline.points ]

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
            '''
            for segment in segments:
                #print("segment (len=%d)" % len(segment))

                if len(segment) == 2:
                    paths.append(Line(start=tuple2complex(segment[0]), end=tuple2complex(segment[1])))

                elif len(segment) == 3:
                    C12 = segment[1]

                    P1 = segment[0]
                    P2 = segment[2]
                
                    paths.append(QuadraticBezier(start=tuple2complex(P1), control=tuple2complex(C12), end=tuple2complex(P2)))
                                         
                elif len(segment) == 4:
                    C12 = segment[1]
                    C23 = segment[2]

                    P1 = segment[0]
                    P2 = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)
                    P3 = segment[3]

                    paths.append(QuadraticBezier(start=tuple2complex(P1), control=tuple2complex(C12), end=tuple2complex(P2)))
                    paths.append(QuadraticBezier(start=tuple2complex(P2), control=tuple2complex(C23), end=tuple2complex(P3)))

                elif len(segment) == 5:
                    C12 = segment[1]
                    C23 = segment[2]
                    C34 = segment[3]

                    P1 = segment[0]
                    P2 = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)
                    P3 = ((segment[2][0] + segment[3][0]) / 2.0, (segment[2][1] + segment[3][1]) / 2.0)
                    P4 = segment[4]

                    paths.append(QuadraticBezier(start=tuple2complex(P1), control=tuple2complex(C12), end=tuple2complex(P2)))
                    paths.append(QuadraticBezier(start=tuple2complex(P2), control=tuple2complex(C23), end=tuple2complex(P3)))
                    paths.append(QuadraticBezier(start=tuple2complex(P3), control=tuple2complex(C34), end=tuple2complex(P4)))

                else:
                    # with algo
                    N = len(segment) - 1

                    # first
                    Ps = segment[0]
                    Ctrl = segment[1]
                    Pe = ((segment[1][0] + segment[2][0]) / 2.0, (segment[1][1] + segment[2][1]) / 2.0)

                    paths.append(QuadraticBezier(start=tuple2complex(Ps), control=tuple2complex(Ctrl), end=tuple2complex(Pe)))

                    # second - ...
                    for k in range(2,len(segment)-2):
                        Ps = ((segment[k-1][0] + segment[k  ][0]) / 2.0, (segment[k-1][1] + segment[k  ][1]) / 2.0)
                        Ctrl = segment[k]
                        Pe = ((segment[k  ][0] + segment[k+1][0]) / 2.0, (segment[k  ][1] + segment[k+1][1]) / 2.0)
                        
                        paths.append(QuadraticBezier(start=tuple2complex(Ps), control=tuple2complex(Ctrl), end=tuple2complex(Pe)))

                    # last
                    Ps = ((segment[N-2][0] + segment[N-1][0]) / 2.0, (segment[N-2][1] + segment[N-1][1]) / 2.0)
                    Ctrl = segment[N-1]
                    Pe = segment[N]

                    paths.append(QuadraticBezier(start=tuple2complex(Ps), control=tuple2complex(Ctrl), end=tuple2complex(Pe)))

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

        self.test_position = [0,0]
        # but has to be re-evaluated for right positionning
        self.pos = [0,0]

        self.string_top = 0
        self.string_leftmargin = 0

        self.paths : List[Path] = []

    def calc_string_position(self, fontsize, text_pos):
        self.text_position = list(text_pos)

        self.calc_string_top()
        self.calc_string_leftmargin()

        self.pos = list(text_pos)

        self.pos[0] += self.string_leftmargin * fontsize / Char2SvgPath.CHAR_SIZE 
        self.pos[1] -= self.string_top * fontsize / Char2SvgPath.CHAR_SIZE 
    

    def calc_string_top(self):
        top = 0
        for ch in self.text:
            o = Char2SvgPath(ch, self.font)
            o_top = o.bbox.yMax

            top = max(top, o_top)
        
        self.string_top = top

    def calc_string_leftmargin(self):
        o = Char2SvgPath(self.text[0], self.font)

        self.string_leftmargin = o.bbox.xMin
    
    def calc_paths(self, fontsize: float, position=(0,0)) -> List[Path]:
        '''
        '''
        self.calc_string_leftmargin()
        self.calc_string_top()

        paths : List[Path] = []

        shifts = []
        shift = 0

        for k, ch in enumerate(self.text):
            o = Char2SvgPath(ch, self.font)
            o.set_yflip_value(self.string_top)
            o.set_xshift_value(self.string_leftmargin)
           
            paths.append(o.calc_path(fontsize))

            if k != len(self.text) -1:
                # accumulate the shifts
                shift += o.calc_shift(self.text[k+1])
                shifts.append(shift)

        # now, all paths have to be shifted on the right with the cumulativ values
        # the first char is Ok, has been already shifted from its bbox.xMin
        self.paths.append(paths[0])

        for k, path in enumerate(paths[1:]):
            path = path.translated(shifts[k]  * fontsize / Char2SvgPath.CHAR_SIZE )
            self.paths.append(path)

        # svg positioning
        self.calc_string_position(fontsize, position)

        pos_paths = []
        translate_pos = self.pos[0] + self.pos[1] * 1j
        
        for k, path in enumerate(self.paths):
            path = path.translated(translate_pos)
            pos_paths.append(path)

        self.paths = pos_paths

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
        id="%s"
        style="fill:#ff2222;fill-opacity:0.5;line-height:1.25;stroke-width:0.264583">
%s
    </g>
</svg>  """ % (self.text, paths))

        fp.close()

    
'''
Inkscape font 30 pt leads to a font-size of 10.5833 "px"

-> resolution 96px per inch

30 pt = 40 px   (yes!)
    -> 40.0/96 inches
    -> 40.0/96* 25.4 mm
    -> 10.5833 mm
    -> font-size = 10.5833 px!

'''

if __name__ == '__main__':

    char = 'B'
    font = 'C:\\Windows\\Fonts\\arial.ttf'
    #font = 'C:\\Windows\\Fonts\\BROADW.TTF'

    fontsize = 10.5833 # px

    o = Char2SvgPath(char, font)

    # convert single char shifting x and flipping y --------------
    o.calc_path(fontsize)
    o.write_path()

    pos = (9.2248564, 17.575741)

    # convert whole string
    oo = String2SvgPaths("Bac", font)
    oo.calc_paths(fontsize, pos)
    oo.write_paths()

    manager = SvgTextManager("C:\\Users\\marduel\\PRIVATE\\pycut\\svg\\B.svg")