# This Python file uses the following encoding: utf-8

from typing import List

import math

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6 import QtSvg
from PySide6 import QtSvgWidgets

import lxml.etree as ET

from svgpathutils import SvgPath
from svgpathutils import SvgTransformer


# https://stackoverflow.com/questions/53288926/qgraphicssvgitem-event-propagation-interactive-svg-viewer

class SvgItem(QtSvgWidgets.QGraphicsSvgItem):
    def __init__(self, id, renderer, parent=None):
        super(SvgItem, self).__init__(parent)
        self.setSharedRenderer(renderer)
        self.setElementId(id)
        bounds = renderer.boundsOnElement(id)
        print("bounds on id=", bounds)
        print("bounds  rect=", self.boundingRect())
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
        print('svg item: ' + self.elementId() + ' - mousePressEvent()' + str(self.isSelected()))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        print('svg item: ' + self.elementId() + ' - mouseReleaseEvent()' + str(self.isSelected()))
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

    def __init__(self, parent):
        super(SvgViewer, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self,0,0,100,100)
        self.renderer = QtSvg.QSvgRenderer()
        self.renderer.setViewBox(QtCore.QRect(0,0,100,100))
        self.setScene(self.scene)

        # the content of the svf file as string
        self.svg = None
        # dictionnay path id -> path d def for all path definition in the svg
        self.svg_path_d = {}

        # the graphical items in the view
        self.items : List[SvgItem] = []
        # ordered list of selected items - TODO
        self.selected_items : List[SvgItem] = []

        #self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

    def clean(self):
        self.scene.clear()
        self.resetTransform()

        self.items : List[SvgItem] = []
        self.selected_items : List[SvgItem] = []

    def set_svg(self, svg: str):
        '''
        This sets the 'real' svg file data, not the later 'augmented' svg
        '''
        self.svg = svg
        self.fill_svg_viewer(self.svg)

    def fill_svg_viewer(self, svg: str):
        '''
        '''
        self.clean()

        self.renderer.load(bytes(svg, 'utf-8'))

        root = ET.fromstring(svg)

        paths = root.findall(".//{http://www.w3.org/2000/svg}path")
        for path in paths:
            print("svg : found path %s" % path.attrib['id'])
            id = path.attrib['id']
            dd = path.attrib['d']

            self.svg_path_d[id] = dd

            item = SvgItem(id, self.renderer)
            self.scene.addItem(item)

            self.items.append(item)

        # bad zoom
        self.zoomIn()
        self.zoomIn()

    def get_svg_path_d(self, p_id):
        return self.svg_path_d[p_id]

    def mousePressEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
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

    def zoomBy(self, factor):
        currentZoom = self.zoomFactor()
        if (factor < 1 and currentZoom < 0.1) or (factor > 1 and currentZoom > 10) :
            return
        self.scale(factor, factor)
        self.zoomChanged.emit()

    def display_geometry_op(self, svg_paths: List[SvgPath]):
        '''
        The list of svg_paths results of the operation 'combinaison' of the 
        svg selected path 'items' in the graphics view

        The resulting svg_paths will the displayed in black together with the original svg
        '''
        transformer = SvgTransformer(self.svg)
        augmented_svg = transformer.augment(svg_paths)

        self.fill_svg_viewer(augmented_svg)

    def display_toolpaths_op(self, svg_paths: List[SvgPath]):
        '''
        The list of svg_paths results of the toolpath calculation

        The resulting svg_paths will the displayed in yellow together with the original svg
        '''
        transformer = SvgTransformer(self.svg)
        augmented_svg = transformer.augment_with_lines(svg_paths)

        self.fill_svg_viewer(augmented_svg)

    def display_op(self, cnc_op):
        '''
        The list of svg_paths results of the toolpath calculation

        The resulting svg_paths will the displayed in yellow together with the original svg
        '''
        transformer = SvgTransformer(self.svg)
        augmented_svg = transformer.augment(cnc_op.geometry_svg_paths)

        transformer = SvgTransformer(augmented_svg)
        augmented_svg = transformer.augment_with_lines(cnc_op.cam_paths_svg_paths)

        self.fill_svg_viewer(augmented_svg)
