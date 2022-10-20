# -*- coding: utf-8 -*-

VERSION = "0_9_0"

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

import os
import sys
import io
import importlib
import glob
import argparse

from typing import List

import xml.etree.ElementTree as etree
import numpy as np

import freetype
from svgpathtools import wsvg, Line, QuadraticBezier, Path, parse_path
from svgpathtools import path as xxpath

#import ziafont
import gpos

import svgtext2svgpaths_fonts_specs


class PathWithAttribs:
    '''
    Wrapper on Path class to contains the attribs as well
    '''
    def __init__(self, path: Path, id: str, attribs: any):
        self.path = path
        self.attribs = attribs
        self.id = id


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
        self.font_style = self.elt_style.get("font-style", "normal")
        self.font_weight = self.elt_style.get("font-weight", "") # no weight
        self.font_stretch = self.elt_style.get("font-stretch", "") # not narrow

        # some fonts can be given in '<name>'
        if self.font_family.startswith("'") and self.font_family.endswith("'"):
            self.font_family = self.font_family[1:-1]

        self.font_size = self.elt_style.get("font-size", "10.5833px")

        self.font_size_float = float(self.font_size[:-2])

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

    def to_paths(self) -> List[PathWithAttribs]:
        '''
        '''
        fontfile = FontFiles.get_fontfile(self.font_family, 
                self.font_style, 
                self.font_weight, 
                self.font_stretch)

        if fontfile:
            converter = String2SvgPaths(self.text, fontfile)
            all_paths = converter.calc_paths(self.font_size_float, self.position)

            return [ PathWithAttribs(path, self.id, self.elt_style) for path in all_paths ]

        return []


class SvgTextConverter:
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

    def convert_texts(self) -> List[List[Path]]:
        '''
        '''
        return [ o.to_paths() for o in self.svgtextobjects ]

    def transform_text(self) -> str:
        '''
        return a "new" sbg strong containing path elements instead of text elements 
        '''
        paths = self.convert_texts()
    
        transf_tree = etree.parse(self.svgfile)
        transf_root = transf_tree.getroot()

        # from transf_tree:
        # 1. remove all text elements
        # 2. insert all path elements 
        
        for k, text_as_paths in enumerate(paths):
            for p, path_with_attribs in enumerate(text_as_paths):
                element = self.make_xml_etree_element(p, path_with_attribs)
                transf_root.append(element)

        #for text_el in transf_root.findall('text'):
        #    # using root.findall() to avoid removal during traversal
        #    transf_root.remove(text_el)
        etree.register_namespace("", "http://www.w3.org/2000/svg" )

        transf_svg = etree.tostring(transf_root)

        return transf_svg

    def make_xml_etree_element(self, p: int, wpath: PathWithAttribs) -> etree.Element :
        '''
        '''
        element = etree.Element("path")
        element.attrib = {
            "id": "%s_%d" % (wpath.id, p),
            "fill": wpath.attribs.get("fill", "#000000"),
            "fill-opacity": wpath.attribs.get("fill-opacity", "1.0"),
            "d":  wpath.path.d()
        }

        return element


class FontDb:
    '''
('72', 'black')
('72', 'bold')
('72', 'bold italic')
('72', 'condensed')
('72', 'condensed bold')
('72', 'italic')
('72', 'light')
('72 monospace', 'bold')
('72 monospace', 'regular')
('72', 'regular')
('agency fb', 'bold')
('agency fb', 'regular')
('algerian', 'regular')
('book antiqua', 'bold')
('book antiqua', 'bold italic')
('book antiqua', 'italic')
('arial', 'regular')
('arial', 'bold')
('arial', 'bold italic')
('arial', 'italic')
('arial', 'narrow')
('arial', 'narrow bold')
('arial', 'narrow bold italic')
('arial', 'narrow italic')
('arial', 'black')
('arial monospaced for sap', 'bold')
('arial monospaced for sap', 'regular')
('arial rounded mt bold', 'regular')
('bahnschrift', 'regular')
('baskerville old face', 'regular')
('bauhaus 93', 'regular')
('bell mt', 'regular')
('bell mt', 'bold')
('bell mt', 'italic')
('bernard mt condensed', 'regular')
('book antiqua', 'regular')
('bodoni mt', 'bold')
('bodoni mt', 'bold italic')
('bodoni mt', 'black italic')
('bodoni mt', 'black')
('bodoni mt', 'condensed bold')
('bodoni mt', 'condensed bold italic')
('bodoni mt', 'condensed italic')
('bodoni mt', 'condensed')
('bodoni mt', 'italic')
('bodoni mt', 'poster compressed')
('bodoni mt', 'regular')
('bookman old style', 'regular')
('bookman old style', 'bold')
('bookman old style', 'bold italic')
('bookman old style', 'italic')
('bradley hand itc', 'regular')
('britannic bold', 'regular')
('berlin sans fb', 'bold')
('berlin sans fb demi', 'bold')
('berlin sans fb', 'regular')
('broadway', 'regular')
('brush script mt', 'italic')
('bookshelf symbol 7', 'regular')
('calibri', 'regular')
('calibri', 'bold')
('calibri', 'italic')
('calibri', 'light')
('calibri', 'light italic')
('calibri', 'bold italic')
('californian fb', 'bold')
('californian fb', 'italic')
('californian fb', 'regular')
('calisto mt', 'regular')
('calisto mt', 'bold')
('calisto mt', 'bold italic')
('calisto mt', 'italic')
('cambria', 'bold')
('cambria', 'italic')
('cambria', 'bold italic')
('candara', 'regular')
('candara', 'bold')
('candara', 'italic')
('candara', 'light')
('candara', 'light italic')
('candara', 'bold italic')
('castellar', 'regular')
('century schoolbook', 'regular')
('centaur', 'regular')
('century', 'regular')
('chiller', 'regular')
('colonna mt', 'regular')
('comic sans ms', 'regular')
('comic sans ms', 'bold')
('comic sans ms', 'italic')
('comic sans ms', 'bold italic')
('consolas', 'regular')
('consolas', 'bold')
('consolas', 'italic')
('consolas', 'bold italic')
('constantia', 'regular')
('constantia', 'bold')
('constantia', 'italic')
('constantia', 'bold italic')
('cooper black', 'regular')
('copperplate gothic bold', 'regular')
('copperplate gothic light', 'regular')
('corbel', 'regular')
('corbel', 'bold')
('corbel', 'italic')
('corbel', 'light')
('corbel', 'light italic')
('corbel', 'bold italic')
('courier new', 'regular')
('courier new', 'bold')
('courier new', 'bold italic')
('courier new', 'italic')
('curlz mt', 'regular')
('dubai', 'bold')
('dubai', 'light')
('dubai', 'medium')
('dubai', 'regular')
('ebrima', 'regular')
('ebrima', 'bold')
('elephant', 'regular')
('elephant', 'italic')
('engravers mt', 'regular')
('eras bold itc', 'regular')
('eras demi itc', 'regular')
('eras light itc', 'regular')
('eras medium itc', 'regular')
('felix titling', 'regular')
('forte', 'regular')
('franklin gothic book', 'regular')
('franklin gothic book', 'italic')
('franklin gothic demi', 'regular')
('franklin gothic demi cond', 'regular')
('franklin gothic demi', 'italic')
('franklin gothic heavy', 'regular')
('franklin gothic heavy', 'italic')
('franklin gothic medium', 'regular')
('franklin gothic medium cond', 'regular')
('franklin gothic medium', 'italic')
('freestyle script', 'regular')
('french script mt', 'regular')
('footlight mt light', 'regular')
('gabriola', 'regular')
('gadugi', 'regular')
('gadugi', 'bold')
('garamond', 'regular')
('garamond', 'bold')
('garamond', 'italic')
('georgia', 'regular')
('georgia', 'bold')
('georgia', 'italic')
('georgia', 'bold italic')
('gigi', 'regular')
('gill sans mt', 'bold italic')
('gill sans mt', 'bold')
('gill sans mt condensed', 'regular')
('gill sans mt', 'italic')
('gill sans ultra bold condensed', 'regular')
('gill sans ultra bold', 'regular')
('gill sans mt', 'regular')
('gloucester mt extra condensed', 'regular')
('gill sans mt ext condensed bold', 'regular')
('century gothic', 'regular')
('century gothic', 'bold')
('century gothic', 'bold italic')
('century gothic', 'italic')
('goudy old style', 'regular')
('goudy old style', 'bold')
('goudy old style', 'italic')
('goudy stout', 'regular')
('harlow solid italic', 'italic')
('harrington', 'regular')
('haettenschweiler', 'regular')
('microsoft himalaya', 'regular')
('hololens mdl2 assets', 'regular')
('high tower text', 'regular')
('high tower text', 'italic')
('iabg logo', 'normal')
('impact', 'regular')
('imprint mt shadow', 'regular')
('informal roman', 'regular')
('ink free', 'regular')
('blackadder itc', 'regular')
('edwardian script itc', 'regular')
('kristen itc', 'regular')
('javanese text', 'regular')
('jokerman', 'regular')
('juice itc', 'regular')
('kunstler script', 'regular')
('wide latin', 'regular')
('lucida bright', 'regular')
('lucida bright', 'demibold')
('lucida bright', 'demibold italic')
('lucida bright', 'italic')
('lucida calligraphy', 'italic')
('leelawadee ui', 'bold')
('leelawadee', 'regular')
('leelawadee', 'bold')
('leelawadee ui', 'regular')
('leelawadee ui', 'semilight')
('lucida fax', 'regular')
('lucida fax', 'demibold')
('lucida fax', 'demibold italic')
('lucida fax', 'italic')
('lucida handwriting', 'italic')
('lucida sans', 'regular')
('lucida sans', 'demibold roman')
('lucida sans', 'demibold italic')
('lucida sans', 'italic')
('lucida sans typewriter', 'regular')
('lucida sans typewriter', 'bold')
('lucida sans typewriter', 'bold oblique')
('lucida sans typewriter', 'oblique')
('lucida console', 'regular')
('lucida sans unicode', 'regular')
('magneto', 'bold')
('maiandra gd', 'regular')
('malgun gothic', 'regular')
('malgun gothic', 'bold')
('malgun gothic', 'semilight')
('marlett', 'regular')
('matura mt script capitals', 'regular')
('microsoft sans serif', 'regular')
('mistral', 'regular')
('myanmar text', 'regular')
('myanmar text', 'bold')
('modern no. 20', 'regular')
('mongolian baiti', 'regular')
('microsoft uighur', 'bold')
('microsoft uighur', 'regular')
('microsoft yi baiti', 'regular')
('monotype corsiva', 'regular')
('mt extra', 'regular')
('mv boli', 'regular')
('niagara engraved', 'regular')
('niagara solid', 'regular')
('nirmala ui', 'regular')
('nirmala ui', 'bold')
('nirmala ui', 'semilight')
('microsoft new tai lue', 'regular')
('microsoft new tai lue', 'bold')
('ocr a extended', 'regular')
('old english text mt', 'regular')
('onyx', 'regular')
('ms outlook', 'regular')
('palatino linotype', 'regular')
('palatino linotype', 'bold')
('palatino linotype', 'bold italic')
('palatino linotype', 'italic')
('palace script mt', 'regular')
('papyrus', 'regular')
('parchment', 'regular')
('perpetua', 'bold italic')
('perpetua', 'bold')
('perpetua', 'italic')
('perpetua titling mt', 'bold')
('perpetua titling mt', 'light')
('perpetua', 'regular')
('microsoft phagspa', 'regular')
('microsoft phagspa', 'bold')
('playbill', 'regular')
('poor richard', 'regular')
('pristina', 'regular')
('rage italic', 'regular')
('ravie', 'regular')
('ms reference sans serif', 'regular')
('ms reference specialty', 'regular')
('rockwell condensed', 'bold')
('rockwell condensed', 'regular')
('rockwell', 'regular')
('rockwell', 'bold')
('rockwell', 'bold italic')
('rockwell extra bold', 'regular')
('rockwell', 'italic')
('sapdings', 'normal')
('sapgui-belize-icons', 'regular')
('sapgui-icons', 'regular')
('sapicons', 'normal')
('century schoolbook', 'bold')
('century schoolbook', 'bold italic')
('century schoolbook', 'italic')
('script mt bold', 'regular')
('segoe mdl2 assets', 'regular')
('segoe print', 'regular')
('segoe print', 'bold')
('segoe script', 'regular')
('segoe script', 'bold')
('segoe ui', 'regular')
('segoe ui', 'bold')
('segoe ui', 'italic')
('segoe ui', 'light')
('segoe ui', 'semilight')
('segoe ui', 'bold italic')
('segoe ui', 'black')
('segoe ui', 'black italic')
('segoe ui emoji', 'regular')
('segoe ui historic', 'regular')
('segoe ui', 'light italic')
('segoe ui', 'semibold')
('segoe ui', 'semibold italic')
('segoe ui', 'semilight italic')
('segoe ui symbol', 'regular')
('showcard gothic', 'regular')
('simsun-extb', 'regular')
('snap itc', 'regular')
('stencil', 'regular')
('sylfaen', 'regular')
('symbol', 'regular')
('tahoma', 'regular')
('tahoma', 'bold')
('microsoft tai le', 'regular')
('microsoft tai le', 'bold')
('tw cen mt', 'bold italic')
('tw cen mt', 'bold')
('tw cen mt condensed', 'bold')
('tw cen mt condensed extra bold', 'regular')
('tw cen mt condensed', 'regular')
('tw cen mt', 'italic')
('tw cen mt', 'regular')
('tempus sans itc', 'regular')
('times new roman', 'regular')
('times new roman', 'bold')
('times new roman', 'bold italic')
('times new roman', 'italic')
('trebuchet ms', 'regular')
('trebuchet ms', 'bold')
('trebuchet ms', 'bold italic')
('trebuchet ms', 'italic')
('verdana', 'regular')
('verdana', 'bold')
('verdana', 'italic')
('verdana', 'bold italic')
('viner hand itc', 'regular')
('vivaldi', 'italic')
('vladimir script', 'regular')
('webdings', 'regular')
('wingdings', 'regular')
('wingdings 2', 'regular')
('wingdings 3', 'regular')
    '''
    pass


class FontFiles:
    '''
    Create a dictionary of the type [font-family] -> [font-style] -> font file
    
    in order to, from the svg text style font-family/font-style/font-weight/font-stretch, to
    retrieve the right font file
    
    ex: font-family:broadway  font-style:normal   font-weight:normal  font-strech:normal  -> 'C:\\Windows\\Fonts\\BROADW.TTF'

        font-family:arial     font-style:normal   font-weight:normal  -> "regular"
        font-family:arial     font-style:normal   font-weight:bold    -> "bold"
        font-family:arial     font-style:italic   font-weight:bold    -> "bold italic"
        font-family:arial     font-style:italic   font-weight:normal  -> "italic"
    '''
    fonts_dir = ["C:\\Windows\\Fonts"]
    fonts_family_alias = { 'sans-serif': 'microsoft sans serif' }

    lookup = None

    @classmethod
    def setupFonts(cls):
        '''
        '''
        cls.fonts_dir = svgtext2svgpaths_fonts_specs.fonts_dir
        cls.fonts_family_alias = svgtext2svgpaths_fonts_specs.fonts_family_alias

        cls.lookup = {}

        for font_dir in cls.fonts_dir:
            ttfs = glob.glob(os.path.join(font_dir, "*.ttf"))

            for ttf in ttfs:
                face = freetype.Face(ttf)
                family = face.family_name.decode("ascii", "strict").lower()
                style = face.style_name.decode("ascii", "strict").lower()
            
                if family not in cls.lookup:
                    cls.lookup[family] = {}

                cls.lookup[family][style] = ttf

        for family in cls.lookup:
            print("----------------", family)
            for style in cls.lookup[family]:
                print("    %-20s  -> %s" % (style, cls.lookup[family][style]))

    @classmethod
    def build_font_styles(cls, style: str, weight: str, stretch: str) -> List[str] :
        '''
        to improve
        '''
        # there can be many font styles probes!
        font_styles = []

        def build_font_style(style: str, weight: str, stretch: str) -> str:
            # resulting font style
            font_style = []
            if stretch not in ["", "normal"]:
                font_style.append(stretch)
            if weight not in ["", "normal"]:
                font_style.append(weight)
            if style not in ["", "normal"]:
                font_style.append(style)

            font_style = " ".join(font_style)

            return font_style


        font_styles.append(build_font_style(style, weight, stretch))

        # next case: "normal" can be "regular" / "condensed" can be "narrow"
        if style in ["", "normal"]:
            if stretch == "condensed":
                font_styles.append(build_font_style("regular", weight, "narrow"))
                font_styles.append(build_font_style("regular", weight, "condensed"))
            else:
                font_styles.append(build_font_style("regular", weight, stretch)) 

        return font_styles


    @classmethod
    def get_fontfile(cls, family: str, style: str, weight: str, stretch: str):
        '''
        '''
        if cls.lookup is None:
            cls.setupFonts()

        family = family.lower()
        weight = weight.lower()
        style = style.lower()
        stretch = stretch.lower()
        
        if not family in cls.lookup:
            if family in cls.fonts_family_alias:
                family = cls.fonts_family_alias[family]

        if family in cls.lookup:
            font_styles = cls.build_font_styles(style, weight, stretch)
            
            for font_style in font_styles:
                if font_style in cls.lookup[family]:
                    return cls.lookup[family][font_style]

            print("font '%s' style '%s' not found - ignore" % (family, font_styles))    
            return None
       
        else:
            print("font '%s' not found - ignore" % family)    
            
        return None

   
class Char2SvgPath:
    '''
    '''
    CHAR_SIZE = 2048

    def __init__(self, char: str, font: str, load_gpos_table=True):
        '''
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
        self.face.load_char(self.char, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_BITMAP | freetype.FT_KERNING_UNSCALED)

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

        # GPOS kerning - with ziafont !
        if load_gpos_table:
            self.gpos = self.get_gpos_table()

    def get_gpos_table(self):
        '''
        from ziafont!
        '''
        import struct
        from datetime import datetime, timedelta
        from collections import namedtuple

        Table = namedtuple('Table', ['checksum', 'offset', 'length'])

        class FontReader(io.BytesIO):
            ''' Class for reading from Font File '''
            # TTF/OTF is big-endian (>)

            def readuint32(self, offset: int=None) -> int:
                ''' Read 32-bit unsigned integer '''
                if offset:
                     self.seek(offset)
                return struct.unpack('>I', self.read(4))[0]

            def readuint16(self, offset: int=None) -> int:
                ''' Read 16-bit unsigned integer '''
                if offset:
                    self.seek(offset)
                return struct.unpack('>H', self.read(2))[0]

            def readuint8(self, offset: int=None) -> int:
                ''' Read 8-bit unsigned integer '''
                if offset:
                    self.seek(offset)
                return struct.unpack('>B', self.read(1))[0]

            def readint8(self, offset: int=None) -> int:
                ''' Read 8-bit signed integer '''
                if offset:
                    self.seek(offset)
                return struct.unpack('>b', self.read(1))[0]

            def readdate(self, offset: int=None) -> datetime:
                ''' Read datetime '''
                if offset:
                    self.seek(offset)
                mtime = self.readuint32() * 0x100000000 + self.readuint32()
                fontepoch = datetime(1904, 1, 1)
                mdate = fontepoch + timedelta(seconds=mtime)
                return mdate

            def readint16(self, offset: int=None) -> int:
                ''' Read 16-bit signed integer '''
                if offset:
                    self.seek(offset)
                return struct.unpack('>h', self.read(2))[0]

            def readshort(self, offset: int=None) -> float:
                ''' Read "short" fixed point number (S1.14) '''
                x = self.readint16()
                return float(x) * 2**-14

            def readvaluerecord(self, fmt: int) -> dict:
                ''' Read a GPOS "ValueRecord" into a dictionary. Zero values will be omitted. '''
                record = {}
                if fmt & 0x0001:
                    record['x'] = self.readint16()
                if fmt & 0x0002:
                    record['y'] = self.readint16()
                if fmt & 0x0004:
                    record['xadvance'] = self.readint16()
                if fmt & 0x0008:
                    record['yadvance'] = self.readint16()
                if fmt & 0x0010:
                    record['xpladeviceoffset'] = self.readuint16()
                if fmt & 0x0020:
                    record['ypladeviceoffset'] = self.readuint16()
                if fmt & 0x0040:
                    record['xadvdeviceoffset'] = self.readuint16()
                if fmt & 0x0080:
                    record['yadvdeviceoffset'] = self.readuint16()
                return record

        with open(self.font, 'rb') as f:
            self.fontfile = FontReader(f.read())

            self.fontfile.seek(0)
            scalartype = self.fontfile.readuint32()
            numtables = self.fontfile.readuint16()
            searchrange = self.fontfile.readuint16()
            entryselector = self.fontfile.readuint16()
            rangeshift = self.fontfile.readuint16()   # numtables*16-searchrange

            # Table Directory (table 5)
            self.tables = {}
            for i in range(numtables):
                tag = self.fontfile.read(4).decode()
                self.tables[tag] = Table(checksum=self.fontfile.readuint32(),
                                offset=self.fontfile.readuint32(),
                                length=self.fontfile.readuint32())
            #for table in self.tables.keys():
            #    if table != 'head':
            #        self._verifychecksum(table)

            if 'glyf' not in self.tables:
                raise ValueError('Unsupported font (no glyf table).')


            if 'GPOS' in self.tables:
                return gpos.Gpos(self.tables['GPOS'].offset, self.fontfile)
            else:
                return None


    def set_yflip_value(self, val):
        '''
        '''
        self.yflip_value  = val

    def set_xshift_value(self, val):
        '''
        '''
        self.xshift_value  = val
        
    def calc_shift(self, next_ch: str):
        '''
        '''
        self.face.has_kerning
        
        shift = self.glyph_adv 

        adv = 0

        if self.face.has_kerning:
            if self.gpos:
                # Only getting x-advance for first glyph.
                next_cc = Char2SvgPath(next_ch, self.font, load_gpos_table=False)
                adv = self.gpos.kern(self.glyph_index, next_cc.glyph_index)[0].get('xadvance', 0)
            else:
                vector = self.face.get_kerning(self.char, next_ch)
                adv = vector.x

        #x += std::floor((glyph.lsb_delta - prevRsbDelta + kerning + 31) / 64.0);

        return shift + adv

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
        You'll need to flip the y values of the points in order to render
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

    def calc_path_freetype_decompose(self, fontsize: float) -> Path:
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


        ctx : List[str] = []
       
        outline.decompose(ctx, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to)

        path_str = " ".join(ctx)

        # build a Path instance
        path = parse_path(path_str)

        # this path is not at the right position - it has to be scaled, shifted and flipped
        yflip = self.yflip_value
        if yflip == None:
            yflip = self.bbox.yMax

        xshift = self.xshift_value
        if  xshift == None:
            xshift = self.bbox.xMin

        # extra scaling
        scaling = fontsize / self.CHAR_SIZE

        # let's go
        path = path.translated(-xshift)
        
        # flipping means a special transformation ... matrix(1,0,  0,-1,  0,7.5857)
        apath = Path()
        
        tf = np.identity(3)
        tf[1][1] = -1
        for seg in path:
            aseg = xxpath.transform(seg, tf)
            apath.append(aseg)
        
        # and the companion translation
        path = apath.translated(yflip * 1j)

        # finally
        path = path.scaled(scaling, scaling)

        self.path = path

        return self.path

    def write_path(self, prefix=""):
        print("path %s: %s" % (prefix, self.path.d()))
        wsvg(self.path, filename="char2path_%s_%s_convert.svg" % (self.char, prefix))


class String2SvgPaths:
    '''
    '''
    def __init__(self, text: str, font: str):
        self.text = text
        self.font = font

        self.text_position = [0,0]
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
        style="fill:#ff2222;fill-opacity:0.5;line-height:1.25;stroke:none;stroke-width:0.264583">
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


def test_char(char: str, font: str):
    '''
    char = 'B'
    font = 'C:\\Windows\\Fonts\\arial.ttf'
    #font = 'C:\\Windows\\Fonts\\BROADW.TTF'
    '''

    fontsize = 10.5833 # px

    o = Char2SvgPath(char, font)

    # convert single char shifting x and flipping y --------------
    o.calc_path(fontsize)
    o.write_path("A")

    o.calc_path_freetype_decompose(fontsize)
    o.write_path("B")

    pos = (9.2248564, 17.575741)

    # convert whole string
    oo = String2SvgPaths("Bac", font)
    oo.calc_paths(fontsize, pos)
    oo.write_paths()

    # ziafont test
    
    #ziafont.set_fontsize(22.5778)
    #font = ziafont.Font('C:\\Windows\\Fonts\\arial.ttf')
    #font.str2svg("BB  CC  AA  BB").svg()

    #resolver = String2SvgPaths(options.svg)
    #resolver.resolve()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="svgtext2svgpath", description="svg text to xvg path")

    # argument
    parser.add_argument("svg", help="svg to transform")
    
    # version info
    parser.add_argument("--version", action='version', version='%s' % VERSION)

    options = parser.parse_args()

    converter = SvgTextConverter(options.svg)
    paths = converter.convert_texts()
    
    for text_as_paths in paths:
        print("-------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------")
        for p, path_with_attribs in enumerate(text_as_paths):
            attribs = path_with_attribs.attribs
            path = path_with_attribs.path
            elt_id = path_with_attribs.id

            style = "fill:%s;fill-opacity:%s;" % (attribs.get("fill", "#000000"), attribs.get("fill-opacity", "1.0"))
            
            print('<path id="%s_%d" style=\"%s\" d="%s" />' % (elt_id, p, style, path.d()))


    # or the full svg with the paths
    svg = converter.transform_text()
    print(svg)
