# This Python file uses the following encoding: utf-8

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

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        print('svg item: ' + self.elementId() + ' - mousePressEvent()')
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        print('svg item: ' + self.elementId() + ' - mouseReleaseEvent()')
        super().mouseReleaseEvent(event)


class SvgViewer(QtWidgets.QGraphicsView):
    zoomChanged = QtCore.Signal()

    def __init__(self, parent):
        super(SvgViewer, self).__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self,0,0,100,100)
        self._renderer = QtSvg.QSvgRenderer()
        self._renderer.setViewBox(QtCore.QRect(0,0,100,100))
        self.setScene(self._scene)
        self.items = []

        #self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

    def set_svg(self, data):
        self._scene.clear()
        self.resetTransform()
        self._renderer.load(data)

        svg = data.decode('utf-8')
        root = ET.fromstring(svg)

        paths = root.findall(".//{http://www.w3.org/2000/svg}path")
        for path in paths:
            print("svg : found path %s" % path.attrib['id'])
            id = path.attrib['id']

            item = SvgItem(id, self._renderer)
            self._scene.addItem(item)

            self.items.append(item)

    def clean(self):
        for item in self.items:
            self._scene.removeItem(item)


    def mousePressEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        print('SvgViewer - mousePressEvent()')
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        print('SvgViewer - mouseReleaseEvent()')
        super().mouseReleaseEvent(event)


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
