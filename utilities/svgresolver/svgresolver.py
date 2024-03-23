# This Python file uses the following encoding: utf-8

VERSION = "1_1_0_alpha"

import os
import argparse
import io

from lxml import etree
import svgelements


class SvgSetMissingIds:
    """ """

    cnt = 1
    prefix = "pycut-xxx"

    NS = "{http://www.w3.org/2000/svg}"

    def __init__(self, filename: str):
        """ """
        self.filename = filename
        self.filename_id = os.path.splitext(self.filename)[0] + ".with_ids.svg"

        self.svg = None
        self.tree = None

    def process(self):
        parser = etree.XMLParser(remove_blank_text=True)
        self.tree = etree.parse(self.filename, parser)

        root = self.tree.getroot()

        self.add_id_to_elements(root)
        # self.write(root)
        self.get_svg_data(root)

    def add_id_to_elements(self, item: etree.Element):
        """for all shaped without "id", gives one "id" """
        for child in item:
            if not isinstance(child.tag, str):  # a comment ?
                continue

            if "id" not in child.attrib and child.tag.split(self.NS)[1] in [
                "circle",
                "ellipse",
                "line",
                "point",
                "polygon",
                "polyline",
                "rect",
                "path",
            ]:
                child.attrib["id"] = f"{self.prefix}-{self.cnt}"
                self.cnt += 1

            self.add_id_to_elements(child)

    def get_svg_data(self, root: etree.Element):
        """Get tree as StringIO"""
        tree_bytes = etree.tostring(self.tree, pretty_print=True)

        self.svg = io.StringIO(tree_bytes.decode())

    def write(self, root: etree.Element):
        """DEBUG"""
        doc = etree.ElementTree(root)

        doc.write(
            self.filename_id, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )


class SvgResolver:
    """ """

    NS = "{http://www.w3.org/2000/svg}"
    lf_format = "%.3f"

    def __init__(self, options):
        """ """
        self.filename = options.svg
        self.resolved_filename = os.path.splitext(self.filename)[0] + ".resolved.svg"

        self.handle = SvgSetMissingIds(self.filename)
        self.handle.process()  # use handle.svg as the source data

        self.drop_defs = options.drop_defs

        self.shapes = []
        self.groups = []

        # There are a few things I do not understand in the svg standard : for example
        # a width and height defined in "px" or in "mm" or in "in"
        # - defined in "px" -> use ppi=svgelements.DEFAULT_PPI (96)
        # - defined in "mm" -> use ppi=25.4
        # - defined in "in" -> use ppi=1

        source_data = self.filename
        source_data = self.handle.svg

        if options.units == "px":
            self.svg = svgelements.SVG.parse(
                source_data, reify=True, ppi=svgelements.DEFAULT_PPI
            )
        if options.units == "mm":
            self.svg = svgelements.SVG.parse(
                source_data, reify=True, ppi=25.4
            )  # so that there is no "scaling" : 1 inch = 25.4 mm
        if options.units == "in":
            self.svg = svgelements.SVG.parse(
                source_data, reify=True, ppi=1
            )  # so that there is no "scaling" : 1 inch <-> 96 px

        # print("======================================")
        # for e in list(self.svg.elements()):
        #    print(f"ID: {e.id} / {e.__class__.__name__}: {e}")
        # print("======================================")

        # to use the right id in the <use> stuff and the right style
        self.id_mapping = {}
        self.id_style = {}

        # we will write the resolved svg from the initial svg
        # parser = etree.XMLParser(remove_blank_text=True)
        # self.tree = etree.parse(self.filename, parser)
        self.tree = self.handle.tree

    def resolve(self):
        """
        The main routine

        It replaces the xml elements with the ones resolved by svgelements module
        """
        self.collect_shapes()
        self.collect_id_mapping()
        self.collect_style_mapping()

        root = self.tree.getroot()

        self.replace_elements(root)

        # output
        self.write_result(root)

    def collect_shapes(self):
        """ """
        self.shapes = []
        self.groups = []

        for e in self.svg.elements():
            if isinstance(e, svgelements.Text):
                # print("text")
                self.shapes.append(e)
            elif isinstance(e, svgelements.Path):
                # print("path")
                self.shapes.append(e)
            elif isinstance(e, svgelements.Shape):
                # print("shape")
                self.shapes.append(e)
            elif isinstance(e, svgelements.Group):
                self.groups.append(e)
            elif isinstance(e, svgelements.SVG):
                print("processing svg #id:", e.id)

    def collect_id_mapping(self):
        """
        every <use ...> item with an id is set into the mapping
        """
        for e in self.svg.elements():
            try:
                if e.values["tag"] == svgelements.SVG_TAG_USE:
                    """
                    'e' is not a Shape as in collect_shapes
                    but a SVGElement. This object helds the 'raw'
                    xml data and thus the initial 'id' of the xml element
                    """
                    id_ref = e.values["href"][1:]  # remove the '#'
                    print('... <use href="#%s" id="%s" ...> ' % (id_ref, e.id))
                    self.id_mapping.setdefault(id_ref, []).append(e.id)
            except Exception as e:
                pass

        print("ID MAPPING", self.id_mapping)

    def collect_style_mapping(self):
        """
        every <use ...> item with a style is set into the mapping
        """
        for e in self.svg.elements():
            try:
                if e.values["tag"] == svgelements.SVG_TAG_USE:
                    """
                    'e' is not a Shape as in collect_shapes
                    but a SVGElement. This object helds the 'raw'
                    xml data and thus the initial 'id' of the xml element
                    """
                    # print("... found a '<use>' tag !")
                    id_ref = e.values["href"][1:]  # remove the '#'
                    self.id_style.setdefault(id_ref, []).append(
                        e.values.get("style", {})
                    )
            except Exception as e:
                pass

        print("STYLE MAPPING", self.id_style)

    def replace_elements(self, item: etree.Element):
        """ """
        shape = self.get_svg_shape_for_use_item(item)
        group = self.get_svg_group_for_use_item(item)

        if shape:
            try:
                print("replacing shape for etree elt =", item.attrib["id"])
            except Exception as e:
                print("replacing shape for etree elt =", item)

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
                print("shape not recognized!", shape.__class__)

        if group:
            try:
                print("replacing group for etree elt =", item.attrib["id"])
            except Exception as e:
                print("replacing group for etree elt =", item)

            self.make_xml_group(item, group)

        if item.tag == "{http://www.w3.org/2000/svg}g":
            if "transform" in item.attrib:
                del item.attrib["transform"]

        # process the children
        for ch in item:
            if not isinstance(ch.tag, str):  # a comment ?
                continue
            # leaves defs unchanged
            if ch.tag == "{http://www.w3.org/2000/svg}defs":
                continue

            self.replace_elements(ch)

    def remove_defs(self, root: etree.ElementTree):
        """ """
        defs = None

        for ch in root:
            print("child", ch.tag)
            if ch.tag == self.NS + "defs":
                defs = ch

        if defs is not None:
            root.remove(defs)
        else:
            print("defs not found")

    def remove_auto_ids(self, item: etree.Element):
        """"""
        for child in item:
            if not isinstance(child.tag, str):  # a comment ?
                continue

            print("tag", child.tag)

            if "id" not in child.attrib:
                continue

            ns_tag = child.tag.split(self.NS)
            if len(ns_tag) == 1:
                tag = ns_tag[0]
            else:
                tag = ns_tag[1]

            if tag in [
                "circle",
                "ellipse",
                "line",
                "point",
                "polygon",
                "polyline",
                "rect",
                "path",
            ]:
                if "id" in child.attrib:
                    e_id: str = child.attrib["id"]
                    if e_id.startswith(SvgSetMissingIds.prefix):
                        del child.attrib["id"]

            self.remove_auto_ids(child)

    def write_result(self, root: etree.ElementTree):
        """ """
        if self.drop_defs:
            self.remove_defs(root)

        self.remove_auto_ids(root)

        doc = etree.ElementTree(root)

        doc.write(
            self.resolved_filename,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        )

        # maybe an extra formatter - needs xmllint
        tree = etree.parse(self.resolved_filename)
        tree_str = etree.tostring(tree, pretty_print=True)
        f = open(self.resolved_filename, "w")
        f.write(tree_str.decode("utf-8"))
        f.close()

        # formatted = self.resolved_filename + ".x"
        # os.system("xmllint --format %s > %s" % (self.resolved_filename, formatted))
        # shutil.move(formatted, self.resolved_filename)

    def resolve_id(self, shape: svgelements.Shape) -> str | None:
        """
        if not in "id_mapping":
            - return the id of the shape
        else:
            - return the id of the shape id mapping and remove this value
            from the mapping because just used
        """
        if shape.id in self.id_mapping:
            # in <use> hopefully
            return self.id_mapping[shape.id].pop(0)

        # was not a <use> but a normal element
        return shape.id

    def resolve_style(self, shape: svgelements.Shape):
        """
        if not in "id_style":
            - return the style of the shape
        else:
            - return the style of the shape id style and remove this value
            from the mapping because just used
        """
        if shape.id in self.id_style:
            # in <use> hopefully
            return self.id_style[shape.id].pop(0)

        # was not a <use> but a normal element
        return shape.values.get("style", "")

    def merge_styles(self, ref_style: str, style: str) -> str:
        """ """
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

            # only the opacity styles should be merged!
            the_style_opacity_items = {}
            for key in the_style:
                if key == "opacity":
                    the_style_opacity_items[key] = the_style[key]
                if key == "stroke-opacity":
                    the_style_opacity_items[key] = the_style[key]

            # merge dict
            the_ref_style.update(the_style_opacity_items)

            merge_style = []
            for key in the_ref_style:
                merge_style.append("%s:%s" % (key, the_ref_style[key]))

            return ";".join(merge_style)

        except:
            return ref_style

    @classmethod
    def eval_pt_transform(cls, pt, transform):
        """ """
        xx = transform.a * pt[0] + transform.b * pt[1] + transform.e
        yy = transform.c * pt[0] + transform.d * pt[1] + transform.f

        return (xx, yy)

    def make_xml_group(self, item: etree.Element, group: svgelements.Group):
        """ """
        print("replacing group items for etree elt =", group.id)

        def resolve_group_items(item, group_e):
            """ """
            for svge in group_e:
                if isinstance(svge, svgelements.Circle):
                    self.make_xml_circle(item, svge)

                elif isinstance(svge, svgelements.Rect):
                    self.make_xml_rect(item, svge)

                elif isinstance(svge, svgelements.Ellipse):
                    self.make_xml_ellipse(item, svge)

                elif isinstance(svge, svgelements.Polygon):
                    self.make_xml_polygon(item, svge)

                elif isinstance(svge, svgelements.SimpleLine):
                    self.make_xml_line(item, svge)

                elif isinstance(svge, svgelements.Polyline):
                    self.make_xml_polyline(item, svge)

                elif isinstance(svge, svgelements.Path):
                    self.make_xml_path(item, svge)

                elif isinstance(svge, svgelements.Text):
                    self.make_xml_text(item, svge)

                elif isinstance(svge, list):
                    resolve_group_items(item, svge)

        resolve_group_items(item, group)

        item.getparent().remove(item)

    def make_xml_circle(self, item: etree.Element, shape: svgelements.Shape):
        """ """
        print("Circle!")

        c = etree.Element("circle")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            c.attrib["id"] = the_id
        # else:
        #    c.attrib["id"] = shape.id

        # SHIT! when rotating, the cx,cy are not evaluated, but transformation matrix is given !
        cx, cy = self.eval_pt_transform((shape.cx, shape.cy), shape.transform)

        c.attrib["cx"] = self.lf_format % cx
        c.attrib["cy"] = self.lf_format % cy

        c.attrib["r"] = self.lf_format % shape.rx

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            c.attrib["style"] = style

        item.addnext(c)
        item.getparent().remove(item)

    def make_xml_rect(self, item: etree.Element, shape: svgelements.Shape):
        """ """
        print("Rect!")

        r = etree.Element("rect")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            r.attrib["id"] = the_id
        # else:
        #    c.attrib["id"] = shape.id

        # SHIT! when rotating, it is no more a rectangle!
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

        item.addnext(r)
        item.getparent().remove(item)

    def make_xml_ellipse(self, item: etree.Element, shape: svgelements.Shape):
        """ """
        print("Ellipse!")

        e = etree.Element("ellipse")

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

        item.addnext(e)
        item.getparent().remove(item)

    def make_xml_polygon(self, item: etree.Element, shape: svgelements.Shape):
        """ """
        print("Polygon!")

        p = etree.Element("polygon")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            p.attrib["id"] = the_id

        p.attrib["points"] = " ".join(
            ["%.3f,%.3f" % (pt.x, pt.y) for pt in shape.points]
        )

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            p.attrib["style"] = style

        item.addnext(p)
        item.getparent().remove(item)

    def make_xml_line(self, item: etree.Element, shape: svgelements.Shape):
        """ """
        print("SimpleLine!")

        the_id = self.resolve_id(shape)

        l = etree.Element("line")

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

        item.addnext(l)
        item.getparent().remove(item)

    def make_xml_polyline(self, item: etree.Element, shape: svgelements.Shape):
        """ """
        print("Polyline!")

        p = etree.Element("polyline")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            p.attrib["id"] = the_id

        p.attrib["points"] = " ".join(
            ["%.3f,%.3f" % (pt.x, pt.y) for pt in shape.points]
        )

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            p.attrib["style"] = style

        item.addnext(p)
        item.getparent().remove(item)

    def make_xml_path(self, item: etree.Element, shape: svgelements.Shape):
        """ """
        print("Path!")

        p = etree.Element("path")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            p.attrib["id"] = the_id

        p.attrib["d"] = shape.d()

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            p.attrib["style"] = style

        item.addnext(p)
        item.getparent().remove(item)

    def make_xml_text(self, item: etree.Element, shape: svgelements.Shape):
        """
        BUG: svgelements : shape.x and shape.y are **NOT** calculated!
        """
        print("Text!")

        t = etree.SubElement(item.getparent(), "text")

        the_id = self.resolve_id(shape)
        the_style = self.resolve_style(shape)

        if the_id != None:
            t.attrib["id"] = the_id

        t.attrib["x"] = self.lf_format % shape.x  # bug!
        t.attrib["y"] = self.lf_format % shape.y  # bug!

        # print(shape)

        t.text = shape.text

        # merge style of ref item with used item
        style = self.merge_styles(shape.values.get("style", {}), the_style)
        if style:
            t.attrib["style"] = style

        item.addnext(t)
        item.getparent().remove(item)

    def get_svg_shape_for_use_item(
        self, item: etree.Element
    ) -> svgelements.Shape | None:
        """ """
        if item.tag == "{http://www.w3.org/2000/svg}svg":
            return None
        if item.tag == "{http://www.w3.org/2000/svg}defs":
            return None

        if item.tag.endswith("use"):
            id_ref = item.attrib["href"][1:]  # not the '#'

            # get related shape
            for idx, shape in enumerate(self.shapes):
                if shape.id == id_ref:
                    # remove it from the list of shapes and give back
                    self.shapes.pop(idx)
                    return shape

        # not a "use" element, a simple one, but is also transformed...
        if "id" in item.attrib:
            id_item = item.attrib["id"]
            for idx, shape in enumerate(self.shapes):
                if shape.id == id_item:
                    # remove it from the list of shapes and give back
                    self.shapes.pop(idx)
                    return shape

        return None

    def get_svg_group_for_use_item(
        self, item: etree.Element
    ) -> svgelements.Shape | None:
        """ """
        if item.tag == "{http://www.w3.org/2000/svg}svg":
            return None
        if item.tag == "{http://www.w3.org/2000/svg}defs":
            return None

        if item.tag.endswith("use"):
            id_ref = item.attrib["href"][1:]  # not the '#'

            # get related group
            for idx, group in enumerate(self.groups):
                if group.id == id_ref:
                    # remove it from the list of shapes and give back
                    self.groups.pop(idx)
                    return group

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="svgresolver", description="svg defs-use / transformations resolver"
    )

    # argument
    parser.add_argument("svg", help="svg to resolve")
    parser.add_argument(
        "-u",
        "--units",
        dest="units",
        default="mm",
        help='viewbox units ("px", "mm" or "in")',
    )
    parser.add_argument(
        "--z",
        "--drop-defs",
        action="store_true",
        dest="drop_defs",
        default=False,
        help="do not keep defs in resolved svg",
    )

    # version info
    parser.add_argument("--version", action="version", version="%s" % VERSION)

    options = parser.parse_args()

    resolver = SvgResolver(options)
    resolver.resolve()
