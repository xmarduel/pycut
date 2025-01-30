# This Python file uses the following encoding: utf-8

from typing import List
from typing import Dict
from typing import Any

import math
import copy

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

from PySide6 import QtSvg
from PySide6 import QtSvgWidgets

import xml.etree.ElementTree as etree

from gcode_generator import CncOp, JobModel
from shapely_svgpath_io import SvgPath

from val_with_unit import ValWithUnit


# https://stackoverflow.com/questions/53288926/qgraphicssvgitem-event-propagation-interactive-svg-viewer


class SvgViewer(QtWidgets.QGraphicsView):
    """ """

    zoomChanged = QtCore.Signal()

    SVGVIEWER_HIDE_TABS_DISABLED = False
    SVGVIEWER_HIDE_TABS_ALL = False

    TABS_SETTINGS = {
        "stroke": "#aa4488",
        "stroke-width": "0",
        "fill": "#aa4488",
        "fill-opacity": "1.0",
        "fill-opacity-disabled": "0.3",
    }

    DEFAULT_TABS_SETTINGS = {
        "stroke": "#aa4488",
        "stroke-width": "0",
        "fill": "#aa4488",
        "fill-opacity": "1.0",
        "fill-opacity-disabled": "0.3",
    }

    # --------------------------------------------------

    GEOMETRY_PREVIEW_CLOSED_PATHS_DEFAULTS = {
        "stroke": "#ff0000",
        "stroke-width": "0",
        "stroke-opacity": "1.0",
        "fill": "#ff0000",
        "fill-opacity": "1.0",
    }

    GEOMETRY_PREVIEW_CLOSED_PATHS = {
        "stroke": "#ff0000",
        "stroke-width": "0",
        "stroke-opacity": "1.0",
        "fill": "#ff0000",
        "fill-opacity": "1.0",
    }

    # to overwrite temporarely the settings
    GEOMETRY_PREVIEW_CLOSED_PATHS_CUSTOM = {
        "stroke": "",
        "stroke-width": "",
        "stroke-opacity": "",
        "fill": "",
        "fill-opacity": "",
    }

    # --------------------------------------------------

    GEOMETRY_PREVIEW_OPENED_PATHS_DEFAULTS = {
        "stroke": "#ff0000",
        "stroke-width": "1.0",
        "stroke-opacity": "1.0",
        "fill": "none",
        "fill-opacity": "1.0",
    }

    GEOMETRY_PREVIEW_OPENED_PATHS = {
        "stroke": "#ff0000",
        "stroke-width": "1.0",
        "stroke-opacity": "1.0",
        "fill": "none",
        "fill-opacity": "1.0",
    }

    TOOLPATHS = {"stroke": "#00ff00", "stroke-width": "0.2"}

    DEFAULT_TOOLPATHS = {"stroke": "#00ff00", "stroke-width": "0.2"}

    def __init__(self, parent: QtWidgets.QWidget | None):
        """ """
        super(SvgViewer, self).__init__(parent)
        self.mainwindow = None
        self.renderer = QtSvg.QSvgRenderer()

        self.setScene(QtWidgets.QGraphicsScene(self))

        # a "state" I would like to avoid, between mouse "down" and mouse "up"
        self.in_dnd = False

        # the content of the svg file as string
        self.svg = ""
        # and the extra tabs contained in the job description
        self.tabs: List[Dict[str, Any]] = []

        # when loading a svg with shapes
        self.svg_shapes: Dict[str, SvgPath] = {}  # path id -> SvgPath

        # the graphical items in the view
        self.svg_items: List[SvgItem] = []
        # ordered list of selected items
        self.selected_items: List[SvgItem] = []

        # extra items (geometry selections / tabs / toolpaths)
        self.extra_items: List[SvgItem] = []
        self.extra_renderers: List[QtSvg.QSvgRenderer] = []

        # self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setViewportUpdateMode(
            QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        # keep zoom factor (used when reloading augmented svg: zoom should be kept)
        self.current_zoom = self.zoomFactor()

    @classmethod
    def set_settings_geometry_preview_custom_color(cls, color: str):
        cls.GEOMETRY_PREVIEW_CLOSED_PATHS_CUSTOM["fill"] = color

    @classmethod
    def set_settings_geometry_preview_custom_color_reset(cls):
        cls.GEOMETRY_PREVIEW_CLOSED_PATHS_CUSTOM["fill"] = ""

    @classmethod
    def set_settings(cls, settings):
        cls.TABS_SETTINGS = copy.deepcopy(settings["TABS_SETTINGS"])
        cls.GEOMETRY_PREVIEW_CLOSED_PATHS = copy.deepcopy(
            settings["GEOMETRY_PREVIEW_CLOSED_PATHS"]
        )
        cls.GEOMETRY_PREVIEW_OPENED_PATHS = copy.deepcopy(
            settings["GEOMETRY_PREVIEW_OPENED_PATHS"]
        )
        cls.TOOLPATHS = copy.deepcopy(settings["TOOLPATHS"])

    @classmethod
    def set_default_settings(cls):
        cls.TABS_SETTINGS = copy.deepcopy(cls.DEFAULT_TABS_SETTINGS)
        cls.GEOMETRY_PREVIEW_CLOSED_PATHS = copy.deepcopy(
            cls.GEOMETRY_PREVIEW_CLOSED_PATHS_DEFAULTS
        )
        cls.GEOMETRY_PREVIEW_OPENED_PATHS = copy.deepcopy(
            cls.GEOMETRY_PREVIEW_OPENED_PATHS_DEFAULTS
        )
        cls.TOOLPATHS = copy.deepcopy(cls.DEFAULT_TOOLPATHS)

    @classmethod
    def get_settings(cls):
        return {
            "TABS_SETTINGS": cls.TABS_SETTINGS,
            "GEOMETRY_PREVIEW_CLOSED_PATHS": cls.GEOMETRY_PREVIEW_CLOSED_PATHS,
            "GEOMETRY_PREVIEW_OPENED_PATHS": cls.GEOMETRY_PREVIEW_OPENED_PATHS,
            "TOOLPATHS": cls.TOOLPATHS,
        }

    def set_mainwindow(self, mainwindow):
        self.mainwindow = mainwindow

    def get_svg_size_x(self) -> ValWithUnit | None:
        """
        get the width of the svg given in units "mm", "cm" or "in" (see Inkscape)
        """
        root = etree.fromstring(self.svg)

        width = root.attrib["width"]

        if "mm" in width:
            w, units = width.split("mm")
            return ValWithUnit(int(w), "mm")
        elif "in" in width:
            w, units = width.split("in")
            return ValWithUnit(int(w), "inch")
        elif "cm" in width:
            w, units = width.split("cm")
            return ValWithUnit(int(w * 10), "mm")

        return None

    def get_svg_size_y(self) -> ValWithUnit | None:
        """
        get the height of the svg given in units "mm", "cm" or "in" (see Inkscape)
        """
        root = etree.fromstring(self.svg)

        height = root.attrib["height"]

        if "mm" in height:
            h, units = height.split("mm")
            return ValWithUnit(int(h), "mm")
        elif "in" in height:
            h, units = height.split("in")
            return ValWithUnit(int(h), "inch")
        elif "cm" in height:
            h, units = height.split("cm")
            return ValWithUnit(int(h * 10), "mm")

        return None

    def get_selected_items_ids(self) -> List[str]:
        """
        return list of selected svg paths
        """
        return [item.elementId() for item in self.selected_items]

    def reset(self):
        """
        Completely clean the scene on new svg
        """
        self.scene().clear()
        self.resetTransform()

        self.svg_shapes = {}

        self.svg_items = []
        self.selected_items = []

        self.extra_items = []
        self.extra_renderers = []

    def clean(self):
        """
        Remove only the "extra_items", not the base svg file items
        """
        for svg_item in self.extra_items:
            self.scene().removeItem(svg_item)

        self.extra_items = []
        self.extra_renderers = []

    def reinit(self):
        """ """
        self.clean()

        self.display_tabs(self.tabs)

    def set_svg(self, svg: str):
        """
        This sets the 'real' svg file data, not the later 'augmented' svg
        """
        self.reset()

        root = etree.fromstring(svg)

        viewBox = root.attrib["viewBox"].split()

        x = int(viewBox[0])
        y = int(viewBox[1])
        w = int(viewBox[2])
        h = int(viewBox[3])

        self.scene().setSceneRect(x, y, w, h)
        self.renderer.setViewBox(QtCore.QRect(x, y, w, h))

        viewbox_size = max(w, h)
        # eval initial zoom factor
        self.current_zoom = 250.0 / viewbox_size

        # TODO -----------------------------------------------------
        # TODO -----------------------------------------------------

        svg = self.svg_text_to_paths(svg)

        # TODO -----------------------------------------------------
        # TODO -----------------------------------------------------

        self.svg = svg
        self.fill_svg_viewer(self.svg)

    def fill_svg_viewer(self, svg: str):
        """ """
        # read all shapes/paths of the svg with svgelement as "paths"
        self.svg_shapes = SvgPath.read_svg_shapes_and_paths(svg)

        renderer = self.renderer
        renderer.load(bytes(svg, "utf-8"))

        # python xml module can load with svg xml header with encoding utf-8
        tree = etree.fromstring(svg)
        elements = tree.findall(".//*")

        shapes_types = [
            "path",
            "rect",
            "circle",
            "ellipse",
            "polygon",
            "line",
            "polyline",
        ]

        shapes: List[etree.Element] = []

        images_types = ["image"]

        images: List[etree.Element] = []

        for element in elements:
            tag = element.tag

            if not tag.startswith("{http://www.w3.org/2000/svg}"):
                # ignore non svg elements
                continue

            tag = tag.split("{http://www.w3.org/2000/svg}")[1]

            if tag in images_types:
                images.append(element)

        for image in images:
            image_id = image.attrib.get("id", None)

            if image_id is None:
                print("    -> ignoring")
                continue

            item = SvgItem(image_id, self, renderer)
            # does not work
            self.scene().addItem(item)

            self.svg_items.append(item)

        for element in elements:
            if not element.tag.startswith("{http://www.w3.org/2000/svg}"):
                continue

            tag = element.tag.split("{http://www.w3.org/2000/svg}")[1]

            if tag in shapes_types:
                shapes.append(element)

        for shape in shapes:
            shape_id = shape.attrib.get("id", None)

            # print("svg : found shape %s : id='%s'" % (shape.tag, shape_id))

            if shape_id is None:
                print("    -> ignoring")
                continue

            item = SvgItem(shape_id, self, renderer)
            self.scene().addItem(item)

            self.svg_items.append(item)

    def fill_svg_viewer_extra_items(self, svg: str):
        """ """
        renderer = QtSvg.QSvgRenderer()
        renderer.load(bytes(svg, "utf-8"))

        self.extra_renderers.append(renderer)

        # python xml module can load with svg xml header with encoding utf-8
        tree = etree.fromstring(svg)
        elements = tree.findall(".//*")

        shapes_types = [
            "path",
            "rect",
            "circle",
            "ellipse",
            "polygon",
            "line",
            "polyline",
        ]

        shapes: List[etree.Element] = []

        for element in elements:
            if not element.tag.startswith("{http://www.w3.org/2000/svg}"):
                continue

            tag = element.tag.split("{http://www.w3.org/2000/svg}")[1]

            if tag in shapes_types:
                shapes.append(element)

        for shape in shapes:
            shape_id = shape.attrib.get("id", None)

            # print("svg : found shape %s : id='%s'" % (shape.tag, shape_id))

            if shape_id is None:
                print("    -> ignoring")
                continue

            item = SvgItem(shape_id, self, renderer)
            self.scene().addItem(item)

            self.extra_items.append(item)

            # tabs can be dragged
            if shape_id.startswith("pycut_tab"):
                item.setFlag(
                    QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True
                )

            # pycut generated paths cannot be selected
            if shape_id.startswith("pycut"):
                item.setFlag(
                    QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False
                )

    def set_tabs(self, tabs: List[Dict[str, Any]]):
        """ """
        if not self.in_dnd:
            # remove tabs
            self.clean()

            # redraw tabs
            self.tabs = tabs
            self.display_tabs(self.tabs)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.in_dnd = True

        print("SvgViewer - mousePressEvent()")
        super().mousePressEvent(event)

        # is there a modifier ?
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        print("    --> Modifiers  : ", modifiers.name)

        do_reset_selection = False

        if modifiers.name == "ControlModifier":
            do_reset_selection = False
        else:
            do_reset_selection = True

        print("    --> List of selected items")
        for item in self.svg_items:
            print("    item %s -> %s" % (item.elementId(), item.isSelected()))
            item.colorizeWhenSelected()

        self.update_selected_items_list(do_reset_selection)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        print("SvgViewer - mouseReleaseEvent()")
        super().mouseReleaseEvent(event)

        # is there a modifier ?
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        print("    --> Modifiers  : ", modifiers.name)

        if modifiers.name == "ControlModifier":
            do_reset_selection = False
        else:
            do_reset_selection = True

        print("    --> List of selected items")
        for item in self.svg_items:
            print("    item %s -> %s" % (item.elementId(), item.isSelected()))
            item.colorizeWhenSelected()

        self.update_selected_items_list(do_reset_selection)

        self.in_dnd = False

    def update_selected_items_list(self, do_reset_selection: bool):
        """
        by comparing the current one with the new evaluation of
        the selected items

        when *not** reseting the selection (with modifier),
        the selection ordering has to be preserved
        """
        selected_items = []
        for item in self.svg_items:
            if item.isSelected():
                selected_items.append(item)

        if len(selected_items) == 0:
            self.selected_items = []
            return

        if do_reset_selection:
            self.selected_items = selected_items
            return

        # no reseting -> compare old/new to preserve ordering of selections
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

    def wheelEvent(self, event: QtGui.QWheelEvent):
        self.zoomBy(math.pow(1.2, event.angleDelta().y() / 240.0))

    def storeZoomFactor(self):
        self.current_zoom = self.zoomFactor()

    def zoomFactor(self):
        return self.transform().m11()

    def zoomIn(self):
        self.zoomBy(2)

    def zoomOut(self):
        self.zoomBy(0.5)

    def resetZoom(self):
        if self.zoomFactor() != 1:
            self.resetTransform()
            self.zoomChanged.emit()

    def zoomBy(self, factor: float):
        """allow very strong zoom (100)
        useful when the svg viewBox is very small"""
        current_zoom = self.zoomFactor()
        if (factor < 1 and current_zoom < 0.1) or (factor > 1 and current_zoom > 100):
            return
        self.scale(factor, factor)
        self.storeZoomFactor()
        self.zoomChanged.emit()

    def make_tabs_svg_paths(self, tabs: List[Dict[str, Any]]) -> List[SvgPath]:
        """ """
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

            o_tab = Tab(tab)

            o_tab.svg_path.shape_attrs["stroke"] = self.TABS_SETTINGS["stroke"]
            o_tab.svg_path.shape_attrs["stroke-width"] = self.TABS_SETTINGS[
                "stroke-width"
            ]
            o_tab.svg_path.shape_attrs["fill"] = self.TABS_SETTINGS["fill"]
            o_tab.svg_path.shape_attrs["fill-opacity"] = self.TABS_SETTINGS[
                "fill-opacity"
            ]

            if not tab["enabled"]:
                o_tab.svg_path.shape_attrs["fill-opacity"] = self.TABS_SETTINGS[
                    "fill-opacity-disabled"
                ]

            tabs_svg_paths.append(o_tab.svg_path)

        return tabs_svg_paths

    def make_cnc_ops_preview_geometry_svg_paths(
        self, cnc_ops: List[CncOp]
    ) -> List[SvgPath]:
        """ """
        geometry_svg_paths = []

        for cnc_op in cnc_ops:
            for geometry_svg_path in cnc_op.geometry_svg_paths:
                if geometry_svg_path.eval_closed():
                    # polygons
                    geometry_svg_path.shape_attrs["stroke"] = (
                        self.GEOMETRY_PREVIEW_CLOSED_PATHS["stroke"]
                    )
                    geometry_svg_path.shape_attrs["stroke-width"] = (
                        self.GEOMETRY_PREVIEW_CLOSED_PATHS["stroke-width"]
                    )
                    geometry_svg_path.shape_attrs["stroke-opacity"] = (
                        self.GEOMETRY_PREVIEW_CLOSED_PATHS["stroke-opacity"]
                    )

                    if self.GEOMETRY_PREVIEW_CLOSED_PATHS_CUSTOM["fill"] != "":
                        geometry_svg_path.shape_attrs["fill"] = (
                            self.GEOMETRY_PREVIEW_CLOSED_PATHS_CUSTOM["fill"]
                        )
                    else:
                        geometry_svg_path.shape_attrs["fill"] = (
                            self.GEOMETRY_PREVIEW_CLOSED_PATHS["fill"]
                        )

                    geometry_svg_path.shape_attrs["fill-opacity"] = (
                        self.GEOMETRY_PREVIEW_CLOSED_PATHS["fill-opacity"]
                    )
                else:
                    # lines
                    geometry_svg_path.shape_attrs["stroke"] = (
                        self.GEOMETRY_PREVIEW_OPENED_PATHS["stroke"]
                    )

                    if geometry_svg_path.p_id.startswith("pycut_geometry_opened_path"):
                        # do not overwrite
                        pass
                    else:
                        geometry_svg_path.shape_attrs["stroke-width"] = (
                            self.GEOMETRY_PREVIEW_OPENED_PATHS["stroke-width"]
                        )

                    geometry_svg_path.shape_attrs["stroke-opacity"] = (
                        self.GEOMETRY_PREVIEW_OPENED_PATHS["stroke-opacity"]
                    )
                    geometry_svg_path.shape_attrs["fill"] = "none"
                    geometry_svg_path.shape_attrs["fill-opacity"] = (
                        self.GEOMETRY_PREVIEW_OPENED_PATHS["fill-opacity"]
                    )

            geometry_svg_paths += cnc_op.geometry_svg_paths

        return geometry_svg_paths

    def make_toolpaths_svg_paths(self, cnc_ops: List["CncOp"]) -> List[SvgPath]:
        """ """
        cam_paths_svg_paths = []

        for cnc_op in cnc_ops:
            for cam_svg_path in cnc_op.cam_paths_svg_paths:
                cam_svg_path.shape_attrs["stroke"] = self.TOOLPATHS["stroke"]
                cam_svg_path.shape_attrs["stroke-width"] = self.TOOLPATHS[
                    "stroke-width"
                ]
                cam_svg_path.shape_attrs["fill"] = "none"

            cam_paths_svg_paths += cnc_op.cam_paths_svg_paths

        return cam_paths_svg_paths

    def display_tabs(self, tabs: List[Dict[str, Any]]):
        """ """
        # the tabs as paths
        svg_paths = self.make_tabs_svg_paths(tabs)

        self.display_extra_paths(svg_paths)

    def display_job_preview_geometry(self, cnc_ops: List["CncOp"]):
        """
        The list of "preview geometries" results of the geometries calculation for given ops
        The resulting geometries will the displayed in black together with the original svg and tabs
        """
        # preview geometries as svg paths
        svg_paths = self.make_cnc_ops_preview_geometry_svg_paths(cnc_ops)

        self.display_extra_paths(svg_paths)

    def display_job_toolpaths(self, cnc_ops: List["CncOp"]):
        """
        The list of svg_paths results of the toolpath calculation for given ops
        The resulting svg_paths will the displayed in green together with the original svg, tabs and preview geometries
        """
        # the toolpaths as svg paths
        svg_paths = self.make_toolpaths_svg_paths(cnc_ops)

        self.display_extra_paths(svg_paths)

    def display_job(self, job: JobModel):
        """ """
        self.display_job_preview_geometry(job.operations)
        self.display_job_toolpaths(job.operations)

    def display_extra_paths(self, svg_paths: List[SvgPath]):
        """to display extra items in the viewer: paths calculated from
        - tabs
        - preview geometries
        - tool paths
        """
        maker = SvgMaker(self.svg)
        extra_items_svg = maker.build(svg_paths)

        # done
        self.fill_svg_viewer_extra_items(extra_items_svg)

    def svg_text_to_paths(self, svg: str) -> str:
        """
        The super mega method: transform all text elements into path elements
        """
        return svg  # TODO


class SvgItem(QtSvgWidgets.QGraphicsSvgItem):
    def __init__(
        self, id: str, view: SvgViewer, renderer: QtSvg.QSvgRenderer, parent=None
    ):
        super(SvgItem, self).__init__(parent)
        self.view = view
        self.setSharedRenderer(renderer)
        self.setElementId(id)

        # set the position of the item
        bounds = renderer.boundsOnElement(id)
        # print("bounds on id=", bounds)
        # print("bounds  rect=", self.boundingRect())
        self.setPos(bounds.topLeft())

        # and its flags
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        self.selected_effect = None
        self.makeGraphicsEffect()

    def makeGraphicsEffect(self):
        if self.selected_effect is None:
            self.selected_effect = QtWidgets.QGraphicsColorizeEffect()
            self.selected_effect.setColor(QtCore.Qt.GlobalColor.darkYellow)
            self.selected_effect.setStrength(1)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        print(
            "svg item: "
            + self.elementId()
            + " - mousePressEvent()  isSelected="
            + str(self.isSelected())
        )
        print("svg item: " + str(self.pos()))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        print(
            "svg item: "
            + self.elementId()
            + " - mouseReleaseEvent() isSelected="
            + str(self.isSelected())
        )
        print("svg item: " + str(self.pos()))
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
            # self.view.mainwindow.assign_tabs(tabs)
            # -> strange behaviour, all spinboxes cells are selected

            # so update the model
            mainwindow: Any = self.view.mainwindow

            model = mainwindow.ui.tabsview_manager.get_model()
            model.tabs[idx].x = center[0]
            model.tabs[idx].y = center[1]
            model.dataChanged.emit(model.index(idx, 0), model.index(idx, 1))
            # ok, but to avoid event chaining, I 've got this flag "in_dnd"

        super().mouseReleaseEvent(event)

    def colorizeWhenSelected(self):
        if self.isSelected():
            self.makeGraphicsEffect()
            self.setGraphicsEffect(self.selected_effect)
        else:
            self.setGraphicsEffect(None)
            self.selected_effect = None


class SvgMaker:
    """
    To build a "compatible" svg with extra calculated svg paths, while the width/height of the svg data
    is identical to the initial svg
    """

    def __init__(self, initial_svg: str):
        """the initial svg"""
        self.initial_svg = initial_svg

    def build(self, svg_paths: List[SvgPath]) -> str:
        """ """
        paths_str = []

        for k, svg_path in enumerate(svg_paths):
            p_id = svg_path.p_id
            d_def = svg_path.p_d

            # defaults
            stroke = svg_path.shape_attrs.get("stroke", "#00ff00")
            stroke_width = svg_path.shape_attrs.get("stroke-width", "0")
            fill = svg_path.shape_attrs.get("fill", "#111111")
            fill_opacity = svg_path.shape_attrs.get("fill-opacity", "1.0")
            fill_rule = svg_path.shape_attrs.get("fill-rule", "nonzero")

            # here we append to the default "id" the counter
            path_str = (
                '<path id="%(id)s_%(counter)d" style="stroke:%(stroke)s;stroke-width:%(stroke_width)s;fill:%(fill)s;fill-opacity:%(fill_opacity)s;fill-rule:%(fill_rule)s;" \
              d="%(d_def)s" />'
                % {
                    "id": p_id,
                    "counter": k,
                    "fill": fill,
                    "stroke_width": stroke_width,
                    "stroke": stroke,
                    "fill_opacity": fill_opacity,
                    "fill_rule": fill_rule,
                    "d_def": d_def,
                }
            )

            paths_str.append(path_str)

        root = etree.fromstring(self.initial_svg)
        root_attrib = root.attrib

        svg = """<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="%s"
                height="%s"
                viewBox="%s"
                version="1.1">
                <g>
                  %s
                </g> 
             </svg>""" % (
            root_attrib["width"],
            root_attrib["height"],
            root_attrib["viewBox"],
            "\n".join(paths_str),
        )

        return svg
