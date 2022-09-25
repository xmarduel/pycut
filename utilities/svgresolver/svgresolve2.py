# This Python file uses the following encoding: utf-8

VERSION = "1_0_0"

import os
import argparse

from lxml import etree
import svgelements


class SvgResolver:
    '''
    '''
    lf_format = "%.3f"

    def __init__(self, filename: str):
        '''
        '''
        self.filename = filename
        self.resolved_filename = os.path.splitext(filename)[0] + '.resolved.svg'
        
        self.shapes = []
        self.svg = svgelements.SVG.parse(filename, reify=True, ppi=25.4)  # so that there is no "scaling"

        # to use the right id in the <use> stuff and the right style
        self.id_mapping = {}
        self.id_style = {}

        # we will write the resolved svg from the initial svg
        parser = etree.XMLParser(remove_blank_text=True)
        self.tree = etree.parse(filename, parser)

    def resolve(self):
        '''
        The main routine

        It replaces the xml elements with the ones resolved by svgelements module
        '''
        self.collect_shapes()
        self.collect_id_mapping()
        self.collect_style_mapping()

        root = self.tree.getroot()

        self.replace_elements(root)

        # output
        self.write_result(root)

    def collect_shapes(self):
        '''
        '''
        self.shapes = []

        for e in self.svg.elements():
            if isinstance(e, svgelements.Text):
                #print("text")
                self.shapes.append(e)
            elif isinstance(e, svgelements.Path):
                #print("path")
                self.shapes.append(e)
            elif isinstance(e, svgelements.Shape):
                #print("shape")
                self.shapes.append(e)

    def collect_id_mapping(self):
        '''
        every <use ...> item with an id is set into the mapping
        '''
        for e in self.svg.elements():
            try:
                if e.values["tag"] == svgelements.SVG_TAG_USE:
                    '''
                    'e' is not a Shape as in collect_shapes
                    but a SVGElement. This object helds the 'raw'
                    xml data and thus the initial 'id' of the xml element
                    '''
                    id_ref = e.values["href"][1:] # remove the '#'
                    print('... <use href="#%s" id="%s" ...> ' % (id_ref, e.id))
                    self.id_mapping.setdefault(id_ref, []).append(e.id)
            except Exception as e:
                pass

        print("ID MAPPING", self.id_mapping)

    def collect_style_mapping(self):
        '''
        every <use ...> item with a style is set into the mapping
        '''
        for e in self.svg.elements():
            try:
                if e.values["tag"] == svgelements.SVG_TAG_USE:
                    '''
                    'e' is not a Shape as in collect_shapes
                    but a SVGElement. This object helds the 'raw'
                    xml data and thus the initial 'id' of the xml element
                    '''
                    #print("... found a '<use>' tag !")
                    id_ref = e.values["href"][1:] # remove the '#'
                    self.id_style.setdefault(id_ref, []).append(e.values.get("style", {}))
            except Exception as e:
                pass

        print("STYLE MAPPING", self.id_style)

    def replace_elements(self, item: etree.Element):
        '''
        '''
        shape = self.get_svg_shape_for_item(item)

        if shape:
            if isinstance(shape, svgelements.Circle):
                self.make_xml_circle(item, shape)

            elif isinstance(shape, svgelements.Rect):
                self.make_xml_rect(item, shape)

            elif isinstance(shape, svgelements.Ellipse):
                self.make_xml_ellipse(item, shape)

            elif isinstance(shape, svgelements.Polygon):
                self.make_xml_polygon(item, shape)

            elif isinstance(shape, svgelements.SimpleLine):
                self.make_xml_line(item, shape)

            elif isinstance(shape, svgelements.Polyline):
                self.make_xml_polyline(item, shape)

            elif isinstance(shape, svgelements.Path):
                self.make_xml_path(item, shape)

            elif isinstance(shape, svgelements.Text):
                self.make_xml_text(item, shape)

            else:
                print ("shape not recognized!", shape.__class__)

        if item.tag.endswith("g"):
            if "transform" in item.attrib:
                del item.attrib["transform"]

        # process the children
        for ch in item:
            self.replace_elements(ch)

    def write_result(self, root:etree.ElementTree):
        '''
        '''
        doc = etree.ElementTree(root)

        doc.write(self.resolved_filename, 
                pretty_print=True, 
                xml_declaration=True, 
                encoding='utf-8')

    def resolve_id(self, shape: svgelements.Shape) -> str|None:
        '''
        if not in "id_mapping":
            - return the id of the shape
        else:
            - return the id of the shape id mapping and remove this value
            from the mapping because just used
        '''
        if shape.id in self.id_mapping:
            # in <use> hopefully
            return self.id_mapping[shape.id].pop(0)

        # was not a <use> but a normal element
        return shape.id

    def resolve_style(self, shape: svgelements.Shape):
        '''
        if not in "id_style":
            - return the style of the shape
        else:
            - return the style of the shape id style and remove this value
            from the mapping because just used
        '''
        if shape.id in self.id_style:
            # in <use> hopefully
            return self.id_style[shape.id].pop(0)

        # was not a <use> but a normal element
        return shape.values["style"]

    def merge_styles(self, ref_style:str, style: str) -> str:
        '''
        '''
        if len(style) == 0:
            return ref_style

        try:
            the_ref_style = {}
            the_style = {}

            ref_style_items = ref_style.split(";")
            for item in ref_style_items:
                key, value = item.split(":")
                the_ref_style[key] = value

            style_items = style.split(";")
            for item in style_items:
                key, value = item.split(":")
                the_style[key] = value

            # merge dict
            the_ref_style.update(the_style)

            merge_style = []
            for key in the_ref_style:
                merge_style.append("%s:%s" % (key, the_ref_style[key]))
     
            return ";".join(merge_style)

        except:
            return ref_style 

    def make_xml_circle(self, item: etree.Element, shape: svgelements.Shape):
        '''
        '''
        print("Circle!")

        c = etree.SubElement(item.getparent(), "circle")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            c.attrib["id"] = the_id
        #else:
        #    c.attrib["id"] = shape.id

        c.attrib["cx"] = self.lf_format % shape.cx
        c.attrib["cy"] = self.lf_format % shape.cy
        c.attrib["r"] = self.lf_format % shape.rx

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            c.attrib["style"] = style

        item.getparent().remove(item)

    def make_xml_rect(self, item: etree.Element, shape: svgelements.Shape):
        '''
        '''
        print("Rect!")

        r = etree.SubElement(item.getparent(), "rect")
        
        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            r.attrib["id"] = the_id

        r.attrib["width"] = self.lf_format % shape.width
        r.attrib["height"] = self.lf_format % shape.height
        r.attrib["x"] = self.lf_format % shape.x
        r.attrib["y"] = self.lf_format % shape.y
        r.attrib["rx"] = self.lf_format % shape.rx
        r.attrib["ry"] = self.lf_format % shape.ry

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            r.attrib["style"] = style

        item.getparent().remove(item)

    def make_xml_ellipse(self, item: etree.Element, shape: svgelements.Shape):
        '''
        '''
        print("Ellipse!")

        e = etree.SubElement(item.getparent(), "ellipse")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            e.attrib["id"] = the_id

        e.attrib["cx"] = self.lf_format % shape.cx
        e.attrib["cy"] = self.lf_format % shape.cy
        e.attrib["rx"] = self.lf_format % shape.rx
        e.attrib["ry"] = self.lf_format % shape.ry

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            e.attrib["style"] = style

        item.getparent().remove(item)

    def make_xml_polygon(self, item: etree.Element, shape: svgelements.Shape):
        '''
        '''
        print("Polygon!")

        p = etree.SubElement(item.getparent(), "polygon")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            p.attrib["id"] = the_id

        p.attrib["points"] =  " ".join(["%.3f,%.3f" % (pt.x, pt.y) for pt in shape.points])
            
        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            p.attrib["style"] = style

        item.getparent().remove(item)

    def make_xml_line(self, item: etree.Element, shape: svgelements.Shape):
        '''
        '''
        print("SimpleLine!")

        l = etree.SubElement(item.getparent(), "line")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            l.attrib["id"] = the_id

        l.attrib["x1"] = self.lf_format % shape.x1
        l.attrib["y1"] = self.lf_format % shape.y1
        l.attrib["x2"] = self.lf_format % shape.x2
        l.attrib["y2"] = self.lf_format % shape.y2

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            l.attrib["style"] = style

        item.getparent().remove(item)

    def make_xml_polyline(self, item: etree.Element, shape: svgelements.Shape):
        '''
        '''
        print("Polyline!")

        p = etree.SubElement(item.getparent(), "polyline")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            p.attrib["id"] = the_id

        p.attrib["points"] =  " ".join(["%.3f,%.3f" %(pt.x, pt.y) for pt in shape.points])
            
        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            p.attrib["style"] = style

        item.getparent().remove(item)

    def make_xml_path(self, item: etree.Element, shape: svgelements.Shape):
        '''
        '''
        print("Path!")

        p = etree.SubElement(item.getparent(), "path")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            p.attrib["id"] = the_id

        p.attrib["d"] = shape.d()

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            p.attrib["style"] = style
        
        item.getparent().remove(item)

    def make_xml_text(self, item: etree.Element, shape: svgelements.Shape):
        '''
        BUG: svgelements : shape.x and shape.y are **NOT** calculated!
        '''
        print("Text!")

        t = etree.SubElement(item.getparent(), "text")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            t.attrib["id"] = the_id

        t.attrib["x"] = self.lf_format % shape.x  # bug!
        t.attrib["y"] = self.lf_format % shape.y  # bug!

        #print(shape)

        t.text = shape.text

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            t.attrib["style"] = style

        item.getparent().remove(item)

    def get_svg_shape_for_item(self, item: etree.Element) -> svgelements.Shape | None:
        '''
        '''
        if item.getparent() == None:
            return None
        if item.getparent().tag.endswith("defs"):
            return None

        if item.tag.endswith("use"):
        
            id_ref = item.attrib["href"][1:] # not the '#'

            # get related shape
            for idx, shape in enumerate(self.shapes):
                if shape.id == id_ref:
                    # remove it from the list of shapes and give back
                    self.shapes.pop(idx)
                    return shape

        else:
            
            for idx, shape in enumerate(self.shapes):
                if shape.id == item.attrib["id"]:
                    # remove it from the list of shapes and give back
                    self.shapes.pop(idx)
                    return shape

        return None



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="svgresolver", description="svg defs-use / transformations resolver")

    # argument
    parser.add_argument("svg", help="svg to resolve")

    # version info
    parser.add_argument("--version", action='version', version='%s' % VERSION)

    options = parser.parse_args()
    
    resolver = SvgResolver(options.svg)
    resolver.resolve()