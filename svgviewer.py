# This Python file uses the following encoding: utf-8

from typing import List

import math

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6 import QtSvg
from PySide6 import QtSvgWidgets

import lxml.etree as ET

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
    zoomChanged = QtCore.Signal()

    def __init__(self, parent):
        super(SvgViewer, self).__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self,0,0,100,100)
        self._renderer = QtSvg.QSvgRenderer()
        self._renderer.setViewBox(QtCore.QRect(0,0,100,100))
        self.setScene(self._scene)

        self.svg = None
        self.path_d = {}

        self.items = []
        self.selected_items = []

        #self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

    def set_svg(self, data):
        self._scene.clear()
        self.resetTransform()
        self._renderer.load(data)

        svg = data.decode('utf-8')
        self.svg = svg

        root = ET.fromstring(svg)

        paths = root.findall(".//{http://www.w3.org/2000/svg}path")
        for path in paths:
            print("svg : found path %s" % path.attrib['id'])
            id = path.attrib['id']
            dd = path.attrib['d']

            self.path_d[id] = dd

            item = SvgItem(id, self._renderer)
            self._scene.addItem(item)

            self.items.append(item)

    def get_path_d(self, p_id):
        return self.path_d[p_id]
    
    def clean(self):
        for item in self.items:
            self._scene.removeItem(item)

        self.items = []
        self.selected_items = []

    def mousePressEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        print('SvgViewer - mousePressEvent()')
        super().mousePressEvent(event)
        print("    --> List of selected items")
        for item in self.items:
            print("    item %s -> %s" % (item.elementId(), item.isSelected()))
            item.colorizeWhenSelected()

    def mouseReleaseEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        print('SvgViewer - mouseReleaseEvent()')
        super().mouseReleaseEvent(event)
        print("    --> List of selected items")
        for item in self.items:
            print("    item %s -> %s" % (item.elementId(), item.isSelected()))
            item.colorizeWhenSelected()


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

    def display_op_svg_paths(self, combined_svg_paths: List['SvgPath']):
        '''
        '''
        for svg_path in combined_svg_paths:
            id = svg_path.p_id
            dd = svg_path.p_attrs['d']

            img = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="100"
                height="100"
                viewBox="0 0 100 100"
                version="1.1">
                <style>svg { background-color: green; }</style>
                <g>
                  <path id="%s" style="fill:#111111;stroke-width:1;stroke:#00ff00"  d="%s" />
                </g> 
             </svg>''' % (id, dd)
        
            data = img.encode('utf-8')

            self.set_svg(data)


            
