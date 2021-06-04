# This Python file uses the following encoding: utf-8

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from PySide2 import QtSvg

import lxml.etree as ET

# https://stackoverflow.com/questions/53288926/qgraphicssvgitem-event-propagation-interactive-svg-viewer

class SvgItem(QtSvg.QGraphicsSvgItem):
    def __init__(self, id, renderer, parent=None):
        super(SvgItem, self).__init__(parent)
        self.id = id
        self.setSharedRenderer(renderer)
        self.setElementId(id)
        bounds = renderer.boundsOnElement(id)
        print("bounds=", bounds, bounds.topLeft())
        self.setPos(bounds.topLeft())
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

    def mousePressEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        print('svg item: ' + self.id + ' - mousePressEvent()')
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent'):
        print('svg item: ' + self.id + ' - mouseReleaseEvent()')
        super().mouseReleaseEvent(event)


class SvgViewer(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        super(SvgViewer, self).__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self,0,0,100,100)
        self._renderer = QtSvg.QSvgRenderer()
        self._renderer.setViewBox(QtCore.QRect(0,0,100,100))
        self.setScene(self._scene)
        self.items = []

    def set_svg(self, data):
        self.resetTransform()
        self._scene.clear()
        self._renderer.load(data)

        svg = data.decode('utf-8')
        root = ET.fromstring(svg)

        paths = root.findall(".//{http://www.w3.org/2000/svg}path")
        for path in paths:
            print(path.attrib)
            id = path.attrib['id']

            item =  SvgItem(id, self._renderer)
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

