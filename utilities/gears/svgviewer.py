# This Python file uses the following encoding: utf-8

from typing import List
from typing import Dict
from typing import Any

import math
import copy

from PySide6 import QtCore
from PySide6 import QtWidgets

from PySide6 import QtSvg
from PySide6 import QtSvgWidgets
from PySide6 import QtWebEngineWidgets

import xml.etree.ElementTree as etree


# https://stackoverflow.com/questions/53288926/qgraphicssvgitem-event-propagation-interactive-svg-viewer


class SvgItem(QtSvgWidgets.QGraphicsSvgItem):
    def __init__(
        self, id: str, view: "SvgViewer", renderer: QtSvg.QSvgRenderer, parent=None
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
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

        self.selected_effect = None
        self.makeGraphicsEffect()

    def makeGraphicsEffect(self):
        if self.selected_effect is None:
            self.selected_effect = QtWidgets.QGraphicsColorizeEffect()
            self.selected_effect.setColor(QtCore.Qt.darkYellow)
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

        super().mouseReleaseEvent(event)

    def colorizeWhenSelected(self):
        if self.isSelected():
            self.makeGraphicsEffect()
            self.setGraphicsEffect(self.selected_effect)
        else:
            self.setGraphicsEffect(None)
            self.selected_effect = None


class SvgViewerWidget(QtSvgWidgets.QSvgWidget):
    def __init__(self, parent):
        """ """
        super(SvgViewerWidget, self).__init__(parent)

        self.mainwindow = None

    def set_mainwindow(self, mainwindow):
        self.mainwindow = mainwindow

    def set_svg(self, svg: str):
        self.set_svg_string(svg)

    def set_svg_file(self, svg_file: str):
        """
        This sets the 'real' svg file data, not the later 'augmented' svg
        """
        self.load(svg_file)

    def set_svg_string(self, svg_string: str):
        """ """
        self.load(QtCore.QByteArray(svg_string))


class SvgViewer(QtWidgets.QGraphicsView):
    """
    The SvgViewer can 'only' load full svg files.
    It cannot increment the view with single "Paths"

    So when augmenting the view, we have to pass all cnc operations
    and build a custom svg file on its own with all these new paths.

    Note that still only the paths from the original svg are selectable.
    """

    zoomChanged = QtCore.Signal()

    # --------------------------------------------------

    TOOLPATHS = {"stroke": "#00ff00", "stroke-width": "0.2"}

    def __init__(self, parent):
        """ """
        super(SvgViewer, self).__init__(parent)
        self.mainwindow = None
        self.renderer = QtSvg.QSvgRenderer()

        self.setScene(QtWidgets.QGraphicsScene(self))

        # the content of the svg file as string
        self.svg = None

        # self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        # keep zoom factor (used when reloading augmented svg: zoom should be kept)
        self.current_zoom = self.zoomFactor()

    def set_mainwindow(self, mainwindow):
        self.mainwindow = mainwindow

    def reset(self):
        """
        Completely clean the scene on new svg
        """
        self.scene().clear()
        self.resetTransform()

    def set_svg(self, svg: str):
        """
        This sets the 'real' svg file data, not the later 'augmented' svg
        """
        self.reset()

        root = etree.fromstring(svg)

        viewbox = root.attrib["viewBox"].split()

        x = int(viewbox[0])
        y = int(viewbox[1])
        w = int(viewbox[2])
        h = int(viewbox[3])

        self.scene().setSceneRect(x, y, w, h)
        self.renderer.setViewBox(QtCore.QRect(x, y, w, h))

        viewbox_size = max(w, h)
        # eval initial zoom factor
        # self.current_zoom = 250.0 / viewbox_size

        self.svg = svg
        self.fill_svg_viewer(self.svg)

    def fill_svg_viewer(self, svg: str):
        """ """
        # python xml module can load with svg xml header with encoding utf-8
        tree = etree.fromstring(svg)
        elements = tree.findall(".//*")

        self.renderer.load(bytes(svg, "utf-8"))

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

            item = SvgItem(shape_id, self, self.renderer)
            self.scene().addItem(item)

        # zoom with the initial zoom factor
        self.scale(self.current_zoom, self.current_zoom)

    def wheelEvent(self, event):
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


class SvgWebEngineViewer(QtWebEngineWidgets.QWebEngineView):
    """ """

    def __init__(self, parent):
        """ """
        super(SvgWebEngineViewer, self).__init__(parent)
        self.setMinimumSize(800, 800)

        self.mainwindow = None

    def set_mainwindow(self, mainwindow):
        self.mainwindow = mainwindow

    def set_svg(self, svg: str):
        """ """
        self.setHtml(svg, baseUrl=QtCore.QUrl("qrc:/"))
