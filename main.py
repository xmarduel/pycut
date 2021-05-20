# This Python file uses the following encoding: utf-8
import sys
import os
import io

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from PySide2 import QtSvg

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader

import lxml.etree as ET

# https://stackoverflow.com/questions/53288926/qgraphicssvgitem-event-propagation-interactive-svg-viewer

class SvgItem(QtSvg.QGraphicsSvgItem):
    def __init__(self, id, renderer, parent=None):
        super(SvgItem, self).__init__(parent)
        self.id = id
        self.setSharedRenderer(renderer)
        self.setElementId(id)
        bounds = renderer.boundsOnElement(id)
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
        self._scene = QtWidgets.QGraphicsScene(self)
        self._renderer = QtSvg.QSvgRenderer()
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


class main(QtWidgets.QMainWindow):
    def __init__(self):
        super(main, self).__init__()
        self.window = self.load_ui()

        self.setCentralWidget(self.window)

        self.svgviewer = None
        self.svg_material_viewer = None

        self.init_svg_viewer()
        self.display_svg(None)

        # callbacks
        self.window.actionOpen_SVG.triggered.connect(self.cb_open_svg)

        # display material thickness/clearance
        self.window.doubleSpinBoxThickness.valueChanged.connect(self.cb_doubleSpinBoxThickness)
        self.window.doubleSpinBoxClearance.valueChanged.connect(self.cb_doubleSpinBoxClearance)

        default_thickness = self.window.doubleSpinBoxThickness.value()
        default_clearance = self.window.doubleSpinBoxClearance.value()
        self.display_material(thickness=default_thickness, clearance=default_clearance)

    def load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        #window = loader.load(ui_file, self)
        window = loader.load(ui_file)
        ui_file.close()

        return window

    def init_svg_viewer(self):
        '''
        '''
        self.svgviewer = SvgViewer(self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.svgviewer)
        layout.addStretch()
        self.window.widget.setLayout(layout)

    def display_svg(self, svg):
        '''
        '''
        if self.svgviewer:
            self.svgviewer.clean()

        if svg is None:
            img = b'''
            <svg viewBox='0 0 108 95' xmlns='http://www.w3.org/2000/svg'>
              <g transform='scale(0.1)'>
                <path id="p2" d='M249,699v43h211v-43h-64l-2,3l-2,4l-4,3c0,0-1,2-2,2h-4c-2,0-3,0-4,1c-1,1-3,1-3,
                  2l-3,4c0,1-1,2-2,2h-4c0,0-2,1-3,0l-3-1c-1,0-3-1-3-2c-1-1,0-2-1-3l-1-3c-1-1-2-1-3-1c-1,0-4,
                  0-4-1c0-2,0-3-1-4v-3v-3z'/>
                <path id="p3" d='M385,593c0,9-6,15-13,15c-7,0-13-6-13-15c0-8,12-39,14-39c1,0,12,31,12,39'/>
              </g>
            </svg>'''
            self.svgviewer.set_svg(img)
        else:
            fp = open(svg, "r");

            data = fp.read()
            img = bytes(data, 'utf-8')
            fp.close()

            self.svgviewer.set_svg(img)

    def display_material(self, thickness, clearance):
        '''
        '''
        thickness_level1 = 75 + thickness
        thickness_level2 = 75 + thickness + 10

        clearance_level1 = 75 - clearance

        img_str = '''
        <svg viewBox='0 0 200 150' xmlns='http://www.w3.org/2000/svg'>
         <g>
            <rect x="90" y="75" width="100" height="%(thickness)d" fill="white" stroke="black" stroke-width="5px" stroke-linejoin="round" />
            <rect x="80" y="85" width="100" height="%(thickness)d" fill="white" stroke="black" stroke-width="5px" stroke-linejoin="round"/>

            <polyline points="80,85    90,75  190,75                   180,85                    80,85" fill="white" stroke="black" stroke-width="5px" stroke-linejoin="round"/>
            <polyline points="180,85  190,75  190,%(thickness_level1)d 180,%(thickness_level2)d 180,85" fill="white" stroke="black" stroke-width="5px" stroke-linejoin="round"/>

            <!-- bit -->
            <polyline points="130,0 130,%(clearance_level1)d 150,%(clearance_level1)d  150,0" fill="white" stroke="black" stroke-width="5px"/>

            <!-- legends levels -->
            <polyline points="25,%(clearance_level1)d   70,%(clearance_level1)d" fill="white" stroke="black" stroke-width="3px" stroke-dasharray="8,8"/>
            <polyline points="25,85                     70,85"                   fill="white" stroke="black" stroke-width="3px" stroke-dasharray="8,8"/>
            <polyline points="25,%(thickness_level2)d   70,%(thickness_level2)d" fill="white" stroke="black" stroke-width="3px" stroke-dasharray="8,8"/>

            <!-- legends -->
            <text x="0" y="%(clearance_level1)d" fill="black">%(clearance)d</text>
            <text x="0" y="90"                   fill="black">0.0</text>
            <text x="0" y="%(thickness_level2)d" fill="black">%(thickness)d</text>

          </g>
        </svg>''' % {"thickness": thickness, "clearance": clearance, "thickness_level1": thickness_level1, "thickness_level2": thickness_level2, "clearance_level1": clearance_level1}

        img = bytes(img_str, encoding='utf-8')

        if self.svg_material_viewer is None:
            self.svg_material_viewer = QtSvg.QSvgWidget()


            renderer = self.svg_material_viewer.renderer()
            renderer.setAspectRatioMode(QtCore.Qt.KeepAspectRatio)


            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.svg_material_viewer)

            self.window.widget_display_material.setLayout(layout)
            self.svg_material_viewer.load(img)

        else:
            self.svg_material_viewer.load(img)

    def cb_doubleSpinBoxThickness(self):
        thickness = self.window.doubleSpinBoxThickness.value()
        clearance = self.window.doubleSpinBoxClearance.value()
        self.display_material(thickness=thickness, clearance=clearance)

    def cb_doubleSpinBoxClearance(self):
        thickness = self.window.doubleSpinBoxThickness.value()
        clearance = self.window.doubleSpinBoxClearance.value()
        self.display_material(thickness=thickness, clearance=clearance)

    @QtCore.Slot()
    def cb_open_svg(self):
        '''
        '''
        xfilter = "SVG Files (*.svg)"
        svg, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="open file", dir=".", filter=xfilter)

        if svg:
            self.display_svg(svg)



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = main()
    widget.show()
    sys.exit(app.exec_())
