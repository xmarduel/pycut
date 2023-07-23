
import sys
import math

from typing import List
from typing import Dict

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6 import QtSvg
from PySide6 import QtSvgWidgets

from PySide6 import QtOpenGLWidgets


from enum import Enum



class RendererType(Enum):
        Native = 0
        OpenGL = 1
        Image = 2


class SvgView(QtWidgets.QGraphicsView):
    '''
    '''
    def __init__(self):
        '''
        '''
        super(SvgView, self).__init__()

        self.x_ratio = 1.0
        self.y_ratio = 1.0

        self.m_renderer = RendererType.Native

        self.m_svgItem = None  # QGraphicsSvgItem
        self.m_backgroundItem = None  # QGraphicsRectItem
        self.m_outlineItem = None  # QGraphicsRectItem

        self.m_image = None

        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        # Prepare background check-board pattern
        tilePixmap = QtGui.QPixmap(64, 64)
        tilePixmap.fill(QtCore.Qt.white)
        tilePainter = QtGui.QPainter(tilePixmap)
        color = QtGui.QColor(220, 220, 220)
        tilePainter.fillRect(0, 0, 32, 32, color)
        tilePainter.fillRect(32, 32, 32, 32, color)
        tilePainter.end()

        self.setBackgroundBrush(tilePixmap)

        self.renderer1 = None
        self.renderer2 = None

    def drawBackground(self, p: QtGui.QPainter, rect: QtCore.QRectF) :
        p.save()
        p.resetTransform()
        p.drawTiledPixmap(self.viewport().rect(), self.backgroundBrush().texture())
        p.restore()


    def svgSize(self) -> QtCore.QSize :
        '''
        '''
        if self.m_svgItem:
            return self.m_svgItem.boundingRect().size().toSize()
        else:
            return QtCore.QSize()

    def openFile(self, file_name: str) -> bool:
        '''
        '''
        if file_name == "c1.svg" :
            #self.import_as_file(file_name)
            self.import_as_items(1, file_name, ["c1a", "c1b"])
            
        if file_name == "c2.svg":
            #self.import_as_file(file_name)
            self.import_as_items(2, file_name, ["r2", "c2"])

    def import_as_file(self, file_name: str):
        '''
        '''
        s = self.scene()

        draw_background = False
        if self.m_backgroundItem:
            draw_background = self.m_backgroundItem.isVisible()
            
        draw_outline = True
        if self.m_outlineItem:
            draw_outline = self.m_outlineItem.isVisible()

        svg_item = QtSvgWidgets.QGraphicsSvgItem(file_name)
        if not svg_item.renderer().isValid():
            return False
            
        self.renderer1 = svg_item.renderer()

        #s.reset() ## XM : do not clear!
        self.resetTransform()

        self.m_svgItem = svg_item
        self.m_svgItem.setFlags(QtWidgets.QGraphicsItem.ItemClipsToShape)
        self.m_svgItem.setCacheMode(QtWidgets.QGraphicsItem.NoCache)
        self.m_svgItem.setZValue(0)

        print("boundingRect SVG-1 item-file", self.m_svgItem.boundingRect())
        print("boundingRect SVG-1 item-file", self.m_svgItem.boundingRect().size().toSize())

        self.m_backgroundItem = QtWidgets.QGraphicsRectItem(self.m_svgItem.boundingRect())
        self.m_backgroundItem.setBrush(QtCore.Qt.white)
        self.m_backgroundItem.setPen(QtCore.Qt.NoPen)
        self.m_backgroundItem.setVisible(draw_background)
        self.m_backgroundItem.setZValue(-1)

        self.m_outlineItem = QtWidgets.QGraphicsRectItem(self.m_svgItem.boundingRect())
        outline = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DashLine)
        outline.setCosmetic(True)
        self.m_outlineItem.setPen(outline)
        self.m_outlineItem.setBrush(QtCore.Qt.NoBrush)
        self.m_outlineItem.setVisible(draw_outline)
        self.m_outlineItem.setZValue(1)

        s.addItem(self.m_backgroundItem)
        s.addItem(self.m_svgItem)
        s.addItem(self.m_outlineItem)

        s.setSceneRect(self.m_outlineItem.boundingRect().adjusted(-10, -10, 10, 10))

    def import_as_items(self, index: int, file_name: str, items_names: List[str]):
        '''
        '''
        #self.resetTransform()

        if index == 1:
            renderer = self.renderer1 = QtSvg.QSvgRenderer(file_name)
        if index == 2:
            renderer = self.renderer2 = QtSvg.QSvgRenderer(file_name)
        

        # items of file
        for item_name in items_names:
            item = QtSvgWidgets.QGraphicsSvgItem()
            item.setSharedRenderer(renderer)
            item.setElementId(item_name)
            item.setZValue(0)
        
            print("boundingRect SVG-2 item", item_name, item.boundingRect())

            bounds = renderer.boundsOnElement(item_name)
            item.setPos(bounds.topLeft())

            self.scene().addItem(item)
            item.setVisible(True)

            r2Item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(100,100,100,100))
            r2Item.setBrush(QtCore.Qt.red)
            r2Item.setPen(QtCore.Qt.NoPen)
            r2Item.setVisible(True)
            r2Item.setZValue(-0.5)

            self.scene().addItem(r2Item)


    def setRenderer(self, type: RendererType):
        self.m_renderer = type

        if self.m_renderer == RendererType.OpenGL:
            self.setViewport(QtOpenGLWidgets.QOpenGLWidget())
        else:
            self.setViewport(QtWidgets.QWidget())

    def renderer(self) -> QtSvg.QSvgRenderer | None:
        if self.m_svgItem:
            return self.m_svgItem.renderer()
        return None

    def setAntialiasing(self, antialiasing: bool): 
        self.setRenderHint(QtGui.QPainter.Antialiasing, antialiasing)

    def setViewBackground(self, enable: bool):
        if not self.m_backgroundItem:
           return

        self.m_backgroundItem.setVisible(enable)

    def setViewOutline(self, enable: bool):
        if not self.m_outlineItem:
            return

        self.m_outlineItem.setVisible(enable)

    def zoomFactor(self) -> float:
        return self.transform().m11()

    def zoomIn(self):
        self.zoomBy(2)

    def zoomOut(self):
        self.zoomBy(0.5)

    def resetZoom(self):
        pass
        #if not qFuzzyCompare(zoomFactor(), qreal(1)):
        #    resetTransform()
        #    emit zoomChanged()

    def paintEvent(self, event: QtGui.QPaintEvent):

        if self.m_renderer == RendererType.Image:
            if self.m_image.size() != self.viewport().size():
                self.m_image = QtGui.QImage(self.viewport().size(), QtGui.QImage.Format_ARGB32_Premultiplied)
            
            image_painter = QtGui.QPainter(self.m_image)
            super().render(image_painter)
            image_painter.end()

            p = QtGui.QPainter(self.viewport())
            p.drawImage(0, 0, self.m_image)

        else:
            super().paintEvent(event)
        
    def wheelEvent(self, event: QtGui.QWheelEvent):
        self.zoomBy(math.pow(1.2, event.angleDelta().y() / 240.0))

    def zoomBy(self, factor: float):
        currentZoom = self.zoomFactor()
        if ((factor < 1 and currentZoom < 0.1) or (factor > 1 and currentZoom > 10)):
            return
        self.scale(factor, factor)
        #emit zoomChanged()



class SvgMainWindow(QtWidgets.QMainWindow):
    '''
    '''
    def __init__(self):
        '''
        '''
        super(SvgMainWindow, self).__init__()

        self.m_view = SvgView()

        self.setCentralWidget(self.m_view)

        self.setRenderer(RendererType.Native)

        #self.loadFile("bubbles.svg")
        self.loadFile("c1.svg")
        self.loadFile("c2.svg")

    def loadFile(self, file_name: str) -> bool:
        '''
        '''
        if not self.m_view.openFile(file_name):
            return False

        available_size = self.screen().availableGeometry().size()
        self.resize(self.m_view.sizeHint().expandedTo(available_size / 4) + QtCore.QSize(80, 80 + self.menuBar().height()))

        return True
        
    def setRenderer(self, render_mode: RendererType):
        '''
        '''
        self.m_view.setRenderer(render_mode)


def main():
    '''
    '''
    app = QtWidgets.QApplication([])
    app.setApplicationName("PyCut")

    mainwindow = SvgMainWindow()
    mainwindow.show()
    sys.exit(app.exec())

if __name__ =='__main__':
    main()