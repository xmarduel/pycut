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
        self.filename = filename
        self.resolved_filename = os.path.splitext(filename)[0] + '.resolved.svg'
        
        self.shapes = []
        self.svg = svgelements.SVG.parse(filename, reify=True, ppi=25.4)  # so that there is no "scaling"

        # to use the right id in the <use> stuff
        self.id_mapping = {}

    def collect_shapes(self):
        '''
        '''
        self.shapes = []

        for e in self.svg.elements():
            if isinstance(e, svgelements.Text):
                #print("text")
                self.shapes.append(e)
                #self.id_mapping.setdefault(e.id, []).append(e.id)
            elif isinstance(e, svgelements.Path):
                #print("path")
                self.shapes.append(e)
                #self.id_mapping.setdefault(e.id, []).append(e.id)
            elif isinstance(e, svgelements.Shape):
                #print("shape")
                self.shapes.append(e)
                #self.id_mapping.setdefault(e.id, []).append(e.id)
            else:
                try:
                    print("ignore", e.__class__, e.id, e.values["href"])
                    if e.values["tag"] == "use":
                        print("... could it be a '<use>' ding ?  ... yes")
                        id_ref = e.values["href"][1:] # remove the '#'
                        self.id_mapping.setdefault(id_ref, []).append(e.id)
                except Exception as e:
                    pass

        print("ID MAPPING", self.id_mapping)
        
    def get_id(self, shape):
        '''
        '''
        if shape.id in self.id_mapping:
            # in <use> hopefully
            return self.id_mapping[shape.id].pop(0)

        # was not a <use> but a normal element
        return shape.id

    def make_xml_circle(self, parent, shape):
        '''
        '''
        print("Circle!")

        c = etree.SubElement(parent, "circle")
        c.attrib["id"] = self.get_id(shape)

        c.attrib["cx"] = self.lf_format % shape.cx
        c.attrib["cy"] = self.lf_format % shape.cy
        c.attrib["r"] = self.lf_format % shape.rx
        c.attrib["style"] = shape.values["style"]
        
    def make_xml_rect(self, parent, shape):
        '''
        '''
        print("Rect!")

        r = etree.SubElement(parent, "rect")
        r.attrib["id"] = self.get_id(shape)

        r.attrib["width"] = self.lf_format % shape.width
        r.attrib["height"] = self.lf_format % shape.height
        r.attrib["x"] = self.lf_format % shape.x
        r.attrib["y"] = self.lf_format % shape.y
        r.attrib["rx"] = self.lf_format % shape.rx
        r.attrib["ry"] = self.lf_format % shape.ry

        if "style" in shape.values:
            r.attrib["style"] = shape.values["style"]

    def make_xml_ellipse(self, parent, shape):
        '''
        '''
        print("Ellipse!")

        e = etree.SubElement(parent, "ellipse")
        e.attrib["id"] = self.get_id(shape)

        e.attrib["cx"] = self.lf_format % shape.cx
        e.attrib["cy"] = self.lf_format % shape.cy
        e.attrib["rx"] = self.lf_format % shape.rx
        e.attrib["ry"] = self.lf_format % shape.ry

        if "style" in shape.values:
            e.attrib["style"] = shape.values["style"]

    def make_xml_polygon(self, parent, shape):
        '''
        '''
        print("Polygon!")

        p = etree.SubElement(parent, "polygon")
        p.attrib["id"] = self.get_id(shape)

        p.attrib["points"] =  " ".join(["%.3f,%.3f" % (pt.x, pt.y) for pt in shape.points])
            
        if "style" in shape.values:
            p.attrib["style"] = shape.values["style"]

        if "stroke-width" in shape.values:
            p.attrib["stroke-width"] = shape.values["stroke-width"]
        if "stroke" in shape.values:
            p.attrib["stroke"] = shape.values["stroke"]
        if "fill" in shape.values:
            p.attrib["fill"] = shape.values["fill"]
        if "opacity" in shape.values:
            p.attrib["opacity"] = shape.values["opacity"]

    def make_xml_line(self, parent, shape):
        '''
        '''
        print("SimpleLine!")

        l = etree.SubElement(parent, "line")
        l.attrib["id"] = self.get_id(shape)

        l.attrib["x1"] = self.lf_format % shape.x1
        l.attrib["y1"] = self.lf_format % shape.y1
        l.attrib["x2"] = self.lf_format % shape.x2
        l.attrib["y2"] = self.lf_format % shape.y2

        if "style" in shape.values:
            l.attrib["style"] = shape.values["style"]
        if "stroke-width" in shape.values:
            l.attrib["stroke-width"] = shape.values["stroke-width"]
        if "stroke" in shape.values:
            l.attrib["stroke"] = shape.values["stroke"]
        if "fill" in shape.values:
            l.attrib["fill"] = shape.values["fill"]

    def make_xml_polyline(self, parent, shape):
        '''
        '''
        print("Polyline!")

        p = etree.SubElement(parent, "polyline")
        p.attrib["id"] = self.get_id(shape)

        p.attrib["points"] =  " ".join(["%.3f,%.3f" %(pt.x, pt.y) for pt in shape.points])
            
        if "style" in shape.values:
            p.attrib["style"] = shape.values["style"]
        if "fill" in shape.values:
            p.attrib["fill"] = shape.values["fill"]
        if "stroke" in shape.values:
            p.attrib["stroke"] = shape.values["stroke"]

    def make_xml_path(self, parent, shape):
        '''
        '''
        print("Path!")

        p = etree.SubElement(parent, "path")
        p.attrib["id"] = self.get_id(shape)

        p.attrib["d"] = shape.d()

        if "style" in shape.values:
            p.attrib["style"] = shape.values["style"]

    def make_xml_text(self, parent, shape):
        '''
        BUG: svgelements : shape.x and shape.y are **NOT** calculated!
        '''
        print("Text!")

        p = etree.SubElement(parent, "text")
        p.attrib["id"] = self.get_id(shape)

        p.attrib["x"] = self.lf_format % shape.x  # bug!
        p.attrib["y"] = self.lf_format % shape.y  # bug!

        #print(shape)

        p.text = shape.text

        if "style" in shape.values:
            p.attrib["style"] = shape.values["style"]

    def resolve(self):
        '''
        '''
        self.collect_shapes()
    
        # ---- lxml -----------------------------------------

        NSMAP={None : "http://www.w3.org/2000/svg", "xlink":"http://www.w3.org/1999/xlink", "svg":"http://www.w3.org/2000/svg"} 
 
        asvg = etree.Element("svg", nsmap=NSMAP)
   
        asvg.attrib["width"] = self.svg.values["width"]
        asvg.attrib["height"] = self.svg.values["height"]
        asvg.attrib["viewBox"] = self.svg.values["viewBox"]
        asvg.attrib["version"] = self.svg.values["version"]
        asvg.attrib["id"] = self.svg.values["id"]

        g = etree.SubElement(asvg, "g")
        g.attrib["id"] = "layer1"

        for shape in self.shapes:
            if isinstance(shape, svgelements.Circle):
                self.make_xml_circle(g, shape)

            elif isinstance(shape, svgelements.Rect):
                self.make_xml_rect(g, shape)
           
            elif isinstance(shape, svgelements.Ellipse):
                self.make_xml_ellipse(g, shape)

            elif isinstance(shape, svgelements.Polygon):
                self.make_xml_polygon(g, shape)

            elif isinstance(shape, svgelements.SimpleLine):
                self.make_xml_line(g, shape)

            elif isinstance(shape, svgelements.Polyline):
                self.make_xml_polyline(g, shape)

            elif isinstance(shape, svgelements.Path):
                self.make_xml_path(g, shape)

            elif isinstance(shape, svgelements.Text):
                self.make_xml_text(g, shape)

            else:
                print ("shape not recognized!", shape.__class__)

        root = etree.ElementTree(asvg)
        root.write(self.resolved_filename, 
                pretty_print=True, 
                xml_declaration=True, 
                encoding='utf-8')

    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="svgresolver", description="svg defs-use / transformations resolver - Read the doc!")

    # argument
    parser.add_argument('-i', "--input", dest="input", help="input svg to resolve")

    # version info
    parser.add_argument("--version", action='version', version='%s' % VERSION)

    options = parser.parse_args()
    
    resolver = SvgResolver(options.input)
    resolver.resolve()