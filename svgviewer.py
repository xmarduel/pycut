# This Python file uses the following encoding: utf-8

from typing import List

import math
import copy

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6 import QtSvg
from PySide6 import QtSvgWidgets

import xml.etree.ElementTree as etree

from svgpathutils import SvgPath

from val_with_unit import ValWithUnit


# https://stackoverflow.com/questions/53288926/qgraphicssvgitem-event-propagation-interactive-svg-viewer

class SvgItem(QtSvgWidgets.QGraphicsSvgItem):
    def __init__(self, id, view, renderer, parent=None):
        super(SvgItem, self).__init__(parent)
        self.view = view
        self.setSharedRenderer(renderer)
        self.setElementId(id)
        bounds = renderer.boundsOnElement(id)
        #print("bounds on id=", bounds)
        #print("bounds  rect=", self.boundingRect())
        self.setPos(bounds.topLeft())
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

        self.selected_effect = None
        self.makeGraphicsEffect()

    def makeGraphicsEffect(self):
        if self.selected_effect is None:
            self.selected_effect = QtWidgets.QGraphicsColorizeEffect()
            self.selected_effect.setColor(QtCore.Qt.darkYellow)
            self.selected_effect.setStrength(1)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        print('svg item: ' + self.elementId() + ' - mousePressEvent()  isSelected=' + str(self.isSelected()))
        print('svg item: ' + str(self.pos()))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        print('svg item: ' + self.elementId() + ' - mouseReleaseEvent() isSelected=' + str(self.isSelected()))
        print('svg item: ' + str(self.pos()))
        if self.elementId().startswith("pycut_tab"):
            # actualize tab object and the mainwindow tabs table
            str_idx = self.elementId().split("pycut_tab_")[1]
            idx = int(str_idx)
            tabs = self.view.tabs
            tab = tabs[idx]
            radius = tab["radius"]
            center = [int(self.pos().x()), int(self.pos().y())]
            center[0] = center[0] + radius
            center[1] = center[1] + radius
            tab["center"] = center
            # brutal force - redraw tabs list with new model
            #self.view.mainwindow.assign_tabs(tabs)
            # -> strange behaviour, all spinboxes cells are selected

            # so update the model
            model = self.view.mainwindow.ui.tabsview_manager.get_model()
            model.tabs[idx].x = center[0]
            model.tabs[idx].y = center[1]
            model.dataChanged.emit(model.index(idx, 0), model.index(idx,1))
            # ok, but to avoid event chaining, I 've got this flag "in_dnd"

        super().mouseReleaseEvent(event)

    def colorizeWhenSelected(self):
        if self.isSelected():
            self.makeGraphicsEffect()
            self.setGraphicsEffect(self.selected_effect)
        else:
            self.setGraphicsEffect(None)
            self.selected_effect = None


class SvgViewer(QtWidgets.QGraphicsView):
    '''
    The SvgViewer can 'only' load full svg files.
    It cannot increment the view with single "Paths"

    So when augmenting the view, we have to pass all cnc operations
    and build a custom svg file on its own with all these new paths.

    This is possible with the help of the svgpathtools.

    Note that still only the paths from the original svg are selectable.
    '''
    zoomChanged = QtCore.Signal()

    SVGVIEWER_HIDE_TABS_DISABLED = False
    SVGVIEWER_HIDE_TABS_ALL = False

    TABS =  {
        "stroke": "#aa4488",
        "stroke-width": "0",
        "fill": "#aa4488",
        "fill-opacity": "1.0",
        "fill-opacity-disabled": "0.3"
    }

    GEOMETRY_PREVIEW =  {
        "stroke": "#ff0000",
        "stroke-width": "0",
        "fill": "#ff0000",
        "fill-opacity": "1.0"
    }

    TOOLPATHS =  {
        "stroke": "#00ff00",
        "stroke-width": "0.2"
    }

    DEFAULT_TABS =  {
        "stroke": "#aa4488",
        "stroke-width": "0",
        "fill": "#aa4488",
        "fill-opacity": "1.0",
        "fill-opacity-disabled": "0.3"
    }

    DEFAULT_GEOMETRY_PREVIEW =  {
        "stroke": "#ff0000",
        "stroke-width": "0",
        "fill": "#ff0000",
        "fill-opacity": "1.0"
    }

    DEFAULT_TOOLPATHS =  {
        "stroke": "#00ff00",
        "stroke-width": "0.2"
    }


    def __init__(self, parent):
        super(SvgViewer, self).__init__(parent)
        self.mainwindow = None
        self.scene = QtWidgets.QGraphicsScene(self)
        self.renderer = QtSvg.QSvgRenderer()

        self.setScene(self.scene)

        # a "state" I would like to avoid, between mouse "down" and mouse "up"
        self.in_dnd = False

        # the content of the svf file as string
        self.svg = None
        # and the extra tabs contained in the job description
        self.tabs = []

        # dictionnay path id -> path d def for all path definition in the svg
        self.svg_path_d = {}

        # when loading a svg with shapes that are not <path>
        self.svg_shapes = {} # path id -> circle, ellipse, rect, polygon, etc

        # the graphical items in the view
        self.items : List[SvgItem] = []
        # ordered list of selected items
        self.selected_items : List[SvgItem] = []

        #self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        # keep zoom factor (used when reloading augmented svg: zoom should be kept)
        self.currentZoom = self.zoomFactor()

    @classmethod
    def set_settings(cls, settings):
        cls.TABS = copy.deepcopy(settings["TABS"])
        cls.GEOMETRY_PREVIEW = copy.deepcopy(settings["GEOMETRY_PREVIEW"])
        cls.TOOLPATHS = copy.deepcopy(settings["TOOLPATHS"])

    @classmethod
    def set_default_settings(cls):
        cls.TABS = copy.deepcopy(cls.DEFAULT_TABS)
        cls.GEOMETRY_PREVIEW = copy.deepcopy(cls.DEFAULT_GEOMETRY_PREVIEW)
        cls.TOOLPATHS = copy.deepcopy(cls.DEFAULT_TOOLPATHS)
    
    def set_mainwindow(self, mainwindow):
        self.mainwindow = mainwindow

    def get_svg_size_x(self) -> ValWithUnit:
        '''
        get the width of the svg given in units "mm", "cm" or "in" (see Inkscape)
        '''
        root = etree.fromstring(self.svg)

        width = root.attrib["width"]

        if "mm" in width:
            w, units = width.split("mm")
            return ValWithUnit(int(w), "mm")
        elif "in"  in width:
            w, units = width.split("in")
            return ValWithUnit(int(w), "inch")
        elif "cm"  in width:
            w, units = width.split("cm")
            return ValWithUnit(int(w*10), "mm")

        return None

    def get_svg_size_y(self) -> ValWithUnit:
        '''
        get the height of the svg given in units "mm", "cm" or "in" (see Inkscape)
        '''
        root = etree.fromstring(self.svg)

        height = root.attrib["height"]

        if "mm" in height:
            h, units = height.split("mm")
            return ValWithUnit(int(h), "mm")
        elif "in"  in height:
            h, units = height.split("in")
            return ValWithUnit(int(h), "inch")
        elif "cm"  in height:
            h, units = height.split("cm")
            return ValWithUnit(int(h*10), "mm")

        return None

    def get_selected_items_ids(self) -> List[str]:
        '''
        return list of selected svg paths
        '''
        return [ item.elementId() for item in self.selected_items ]

    def clean(self):
        self.scene.clear()
        self.resetTransform()

        self.svg_path_d = {}
        self.svg_shapes = {}

        self.items : List[SvgItem] = []
        self.selected_items : List[SvgItem] = []

    def set_svg(self, svg: str):
        '''
        This sets the 'real' svg file data, not the later 'augmented' svg
        '''
        root = etree.fromstring(svg)

        viewBox = root.attrib["viewBox"].split()

        x = int(viewBox[0])
        y = int(viewBox[1])
        w = int(viewBox[2])
        h = int(viewBox[3])

        self.scene.setSceneRect(x,y,w,h)
        self.renderer.setViewBox(QtCore.QRect(x,y,w,h))

        viewbox_size = max(w, h)
        # eval initial zoom factor
        self.currentZoom = 250.0 / viewbox_size

        # TODO -----------------------------------------------------
        # TODO -----------------------------------------------------
        
        svg = self.svg_text_to_paths(svg)

        # TODO -----------------------------------------------------
        # TODO -----------------------------------------------------
         
        self.svg = svg
        self.fill_svg_viewer(self.svg)

    def fill_svg_viewer(self, svg: str):
        '''
        '''
        self.clean()

        # read all shapes with svgpathtools : when not only <path>(s) in the svg
        self.svg_shapes = SvgPath.read_svg_shapes_as_paths(svg)

        self.renderer.load(bytes(svg, 'utf-8'))

        # python xml module can load with svg xml header with encoding utf-8
        tree = etree.fromstring(svg)
        elements = tree.findall('.//*')

        shapes_types = [
        	"path",
            "rect",
            "circle",
            "ellipse",
            "polygon",
            "line",
            "polyline"
        ]

        shapes : List[etree.ElementTree] = []
        
        for element in elements:
            if not element.tag.startswith("{http://www.w3.org/2000/svg}"):
                continue
            
            tag = element.tag.split("{http://www.w3.org/2000/svg}")[1]
            
            if tag in shapes_types:
                shapes.append(element)

        for shape in shapes:
            shape_id = shape.attrib.get('id', None)

            print("svg : found shape %s : id='%s'" % (shape.tag, shape_id))

            if shape_id is None:
                print("    -> ignoring")
                continue

            attribs, path = self.svg_shapes[shape_id]

            self.svg_path_d[shape_id] = path.d()

            item = SvgItem(shape_id, self, self.renderer)
            self.scene.addItem(item)

            self.items.append(item)

            # tabs can be dragged
            if shape_id.startswith("pycut_tab"):
                item.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

            # pycut generated paths cannot be selected
            if shape_id.startswith("pycut"):
                item.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

        # zoom with the initial zoom factor
        self.scale(self.currentZoom, self.currentZoom)

    def set_tabs(self, tabs: List['Tab']):
        '''
        '''
        if not self.in_dnd:
            self.tabs = tabs
            self.display_tabs(self.tabs)

    def get_svg_path_d(self, p_id: str) -> str:
        return self.svg_path_d[p_id]

    def mousePressEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        self.in_dnd = True

        print('SvgViewer - mousePressEvent()')
        super().mousePressEvent(event)
        print("    --> List of selected items")
        for item in self.items:
            print("    item %s -> %s" % (item.elementId(), item.isSelected()))
            item.colorizeWhenSelected()

        self.update_selected_items_list()

    def mouseReleaseEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        print('SvgViewer - mouseReleaseEvent()')
        super().mouseReleaseEvent(event)
        print("    --> List of selected items")
        for item in self.items:
            print("    item %s -> %s" % (item.elementId(), item.isSelected()))
            item.colorizeWhenSelected()

        self.update_selected_items_list()

        self.in_dnd = False

    def update_selected_items_list(self):
        '''
        by comparing the current one with the new evaluation of
        the selected items
        '''
        selected_items = []
        for item in self.items:
            if item.isSelected():
                selected_items.append(item)

        if len(selected_items) == 0:
            self.selected_items = []
        else:
            # compare old/new
            oldLen = len(self.selected_items)
            newLen = len(selected_items)

            if newLen < oldLen:
                # remove lost items
                items_to_remove = []
                for item in self.selected_items:
                    if not item in selected_items:
                        items_to_remove.append(item)
                # finally
                for item in items_to_remove:
                    if item in self.selected_items:
                        self.selected_items.remove(item)

            if newLen > oldLen:
                # append the new items
                for item in selected_items:
                    if not item in self.selected_items:
                        self.selected_items.append(item)

        print("    ---> List ordered selected item:")
        for item in self.selected_items:
            print("        %s -> %s" % (item.elementId(), item.isSelected()))

    def wheelEvent(self, event):
        self.zoomBy(math.pow(1.2, event.angleDelta().y() / 240.0))

    def storeZoomFactor(self):
        self.currentZoom = self.zoomFactor()

    def zoomFactor(self):
        return self.transform().m11()

    def zoomIn(self):
        self.zoomBy(2)

    def zoomOut(self):
        self.zoomBy(0.5)

    def resetZoom(self):
        if self.zoomFactor() != 1 :
            self.resetTransform()
            self.zoomChanged.emit()

    def zoomBy(self, factor: float):
        ''' allow very strong zoom (100)
        useful when the svg viewBox is very small '''
        currentZoom = self.zoomFactor()
        if (factor < 1 and currentZoom < 0.1) or (factor > 1 and currentZoom > 100) :
            return
        self.scale(factor, factor)
        self.storeZoomFactor()
        self.zoomChanged.emit()

    def reinit(self):
        '''
        '''
        self.clean()
        self.fill_svg_viewer(self.svg)
        self.display_tabs(self.tabs)

    def make_tabs_svg_paths(self, tabs: List['Tab']) -> List[any]:
        '''
        '''
        from gcode_generator import Tab

        tabs_svg_paths = []

        for tab in tabs:
            show = True
            if self.SVGVIEWER_HIDE_TABS_ALL:
                show = False
            if self.SVGVIEWER_HIDE_TABS_DISABLED and tab["enabled"] == False:
                show = False

            if show == False:
                continue

            tab_svg_path = Tab(tab).make_svg_path()
            tab_svg_path.p_attrs['stroke'] = self.TABS["stroke"]
            tab_svg_path.p_attrs['stroke-width'] = self.TABS["stroke-width"]
            tab_svg_path.p_attrs['fill'] = self.TABS["fill"]
            tab_svg_path.p_attrs['fill-opacity'] = self.TABS["fill-opacity"]

            if tab["enabled"] == False:
                tab_svg_path.p_attrs['fill-opacity'] = self.TABS["fill-opacity-disabled"]
            
            tabs_svg_paths.append(tab_svg_path)

        return tabs_svg_paths
    
    def make_cnc_ops_preview_geometry_svg_paths(self, cnc_ops: List['CncOp']) -> List[any]:
        '''
        '''
        geometry_svg_paths = []

        for cnc_op in cnc_ops:
            for geometry_svg_path in cnc_op.geometry_svg_paths:
                geometry_svg_path.p_attrs['stroke'] = self.GEOMETRY_PREVIEW["stroke"]
                geometry_svg_path.p_attrs['stroke-width'] = self.GEOMETRY_PREVIEW["stroke-width"]
                geometry_svg_path.p_attrs['fill'] = self.GEOMETRY_PREVIEW["fill"]
                geometry_svg_path.p_attrs['fill-opacity'] = self.GEOMETRY_PREVIEW["fill-opacity"]

            geometry_svg_paths += cnc_op.geometry_svg_paths

        return geometry_svg_paths

    def make_toolpaths_svg_paths(self, cnc_ops: List['CncOp']) -> List[any]:
        '''
        '''
        cam_paths_svg_paths = []
        
        for cnc_op in cnc_ops:
            for cam_svg_path in cnc_op.cam_paths_svg_paths:
                cam_svg_path.p_attrs['stroke'] = self.TOOLPATHS["stroke"]
                cam_svg_path.p_attrs['stroke-width'] = self.TOOLPATHS["stroke-width"]
                cam_svg_path.p_attrs['fill'] = 'none'

            cam_paths_svg_paths += cnc_op.cam_paths_svg_paths

        return cam_paths_svg_paths
    
    def display_tabs(self, tabs: List['Tab']):
        '''
        '''
        # the tabs
        tabs_svg_paths = self.make_tabs_svg_paths(tabs)

        transformer = SvgTransformer(self.svg)
        augmented_svg = transformer.augment(tabs_svg_paths)

        # done
        self.fill_svg_viewer(augmented_svg)

    def display_job_geometry(self, cnc_ops: List['CncOp']):
        '''
        The list of "preview geometries" results of the geometries calculation for given ops
        The resulting geometries will the displayed in black together with the original svg and tabs
        '''
        # display preview geometries
        geometry_svg_paths = self.make_cnc_ops_preview_geometry_svg_paths(cnc_ops)
        
        transformer = SvgTransformer(self.svg)
        augmented_svg = transformer.augment(geometry_svg_paths)

        # then the tabs
        tabs_svg_paths = self.make_tabs_svg_paths(self.tabs)

        transformer = SvgTransformer(augmented_svg)
        augmented_svg = transformer.augment(tabs_svg_paths)

        # done
        self.fill_svg_viewer(augmented_svg)

    def display_job_toolpaths(self, cnc_ops: List['CncOp']):
        '''
        The list of svg_paths results of the toolpath calculation for given ops
        The resulting svg_paths will the displayed in green together with the original svg, tabs and preview geometries
        '''
        # display preview geometries
        geometry_svg_paths = self.make_cnc_ops_preview_geometry_svg_paths(cnc_ops)

        transformer = SvgTransformer(self.svg)
        augmented_svg = transformer.augment(geometry_svg_paths)

        # then the tabs
        tabs_svg_paths = self.make_tabs_svg_paths(self.tabs)

        transformer = SvgTransformer(augmented_svg)
        augmented_svg = transformer.augment(tabs_svg_paths)

        # then the toolpaths
        cam_paths_svg_paths = self.make_toolpaths_svg_paths(cnc_ops)

        transformer = SvgTransformer(augmented_svg)
        augmented_svg = transformer.augment(cam_paths_svg_paths)

        # done
        self.fill_svg_viewer(augmented_svg)

    def svg_text_to_paths(self, svg: str) -> str :
        '''
        The super mega method: transform all text elements into path elements
        '''
        return svg  # TODO


class SvgTransformer:
    '''
    '''
    def __init__(self, svg: str):
        self.svg = svg

    def collect_shapes(self) -> List[etree.ElementTree]:
        '''
        '''
        # python xml module can load with svg xml header with encoding utf-8
        tree = etree.fromstring(self.svg)
        elements = tree.findall('.//*')

        shapes_types = [
        	"path",
            "rect",
            "circle",
            "ellipse",
            "polygon",
            "line",
            "polyline"
        ]

        shapes : List[etree.ElementTree] = []
        
        for element in elements:
            if not element.tag.startswith("{http://www.w3.org/2000/svg}"):
                continue
            
            tag = element.tag.split("{http://www.w3.org/2000/svg}")[1]
            
            if tag in shapes_types:
                shapes.append(element)

        return shapes
        
    def augment(self, svg_paths: List[SvgPath]) -> str:
        '''
        '''
        all_paths = ""

        shapes = self.collect_shapes()

        for shape in shapes:
            shape_id = shape.attrib.get('id', None)

            print("svg : found shape %s : %s" % (shape.tag, shape_id))

            if shape_id is None:
                print("      -> ignoring")
                continue

            tag = shape.tag.split("}")[1]
            svg_attrs = ''
            for key, value in shape.attrib.items():
                svg_attrs += ' %s="%s"' % (key, value)

            all_paths += '<%s %s/>\r\n' % (tag, svg_attrs)

        for k, svg_path in enumerate(svg_paths):
            p_id = svg_path.p_id
            d_def = svg_path.p_attrs['d']

            # defaults
            stroke = svg_path.p_attrs.get("stroke", '#00ff00')
            stroke_width = svg_path.p_attrs.get("stroke-width", '0')
            fill = svg_path.p_attrs.get("fill", "#111111")
            fill_opacity = svg_path.p_attrs.get("fill-opacity", "1.0")
            fill_rule = svg_path.p_attrs.get("fill-rule", "nonzero")

            path = '<path id="%(id)s_%(counter)d" style="stroke:%(stroke)s;stroke-width:%(stroke_width)s;fill:%(fill)s;fill-opacity:%(fill_opacity)s;fill-rule:%(fill_rule)s;" \
              d="%(d_def)s" />' % {
                'id': p_id, 
                'counter': k, 
                'fill': fill,
                'stroke_width': stroke_width,
                'stroke': stroke,
                'fill_opacity': fill_opacity, 
                'fill_rule': fill_rule, 
                'd_def': d_def
            }

            all_paths += path + '\r\n'
        
        root = etree.fromstring(self.svg)
        root_attrib = root.attrib
        
        svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="%s"
                height="%s"
                viewBox="%s"
                version="1.1">
                <g>
                  %s
                </g> 
             </svg>''' % (root_attrib["width"], root_attrib["height"], root_attrib["viewBox"], all_paths)
        
        return svg


def extract_svg_dimensions(svg: str):
    '''
    Dimension of the svg are of importance when making gcode from the lower left 
    side of the material
    '''
    tree = etree.fromstring(svg)
    tree_attrib = tree.attrib

    w = tree_attrib["width"]
    h = tree_attrib["height"]

    return w, h

