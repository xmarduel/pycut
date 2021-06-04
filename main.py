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


class main(QtWidgets.QMainWindow):
    def __init__(self):
        super(main, self).__init__()
        self.window = self.load_ui("form.ui")

        self.setCentralWidget(self.window)

        self.svgviewer = self.init_svg_viewer()
        self.svg_material_viewer = self.init_material_viewer()
        self.current_op_widget = None

        # callbacks
        self.window.actionOpen_SVG.triggered.connect(self.cb_open_svg)

        # display material thickness/clearance
        self.window.doubleSpinBox_Material_Thickness.valueChanged.connect(self.cb_doubleSpinBoxThickness)
        self.window.doubleSpinBox_Material_Clearance.valueChanged.connect(self.cb_doubleSpinBoxClearance)

        self.window.comboBoxOperation.currentTextChanged.connect(self.display_op)
        
        
        default_thickness = self.window.doubleSpinBox_Material_Thickness.value()
        default_clearance = self.window.doubleSpinBox_Material_Clearance.value()
        self.display_material(thickness=default_thickness, clearance=default_clearance)
        
        self.display_svg(None)
        self.display_op()
        
        self.window.comboBox_Tool_Units.currentTextChanged.connect(self.cb_update_tool_display)
        self.window.comboBox_GCodeConversion_Units.currentTextChanged.connect(self.cb_update_gcodeconversion_display)
        
        self.window.pushButton_MakeAll_inch.clicked.connect(self.cb_make_all_inch)
        self.window.pushButton_MakeAll_mm.clicked.connect(self.cb_make_all_mm)
        
        self.init_gui()

    def load_ui(self, ui):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), ui)
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        #window = loader.load(ui_file, self)
        window = loader.load(ui_file)
        ui_file.close()

        return window
    
    def cb_make_all_inch(self):
        '''
        '''
        self.window.comboBox_Tabs_Units.setCurrentText("inch")
        self.window.comboBox_Tool_Units.setCurrentText("inch")
        self.window.comboBox_Material_Units.setCurrentText("inch")
        self.window.comboBox_GCodeConversion_Units.setCurrentText("inch")
         
        self.init_gui()
    
    def cb_make_all_mm(self):
        '''
        '''
        self.window.comboBox_Tabs_Units.setCurrentText("mm")
        self.window.comboBox_Tool_Units.setCurrentText("mm")
        self.window.comboBox_Material_Units.setCurrentText("mm")
        self.window.comboBox_GCodeConversion_Units.setCurrentText("mm")
        
        self.init_gui()
    
    def init_gui(self):
        '''
        '''
        self.cb_update_tool_display()
        self.cb_update_gcodeconversion_display()
        
    def cb_update_tool_display(self):
        '''
        '''
        tool_units = self.window.comboBox_Tool_Units.currentText()
        
        if tool_units == "inch":
            self.window.label_Tool_Diameter_UnitsDescr.setText("inch")
            self.window.label_Tool_Angle_UnitsDescr.setText("degrees")
            self.window.label_Tool_PassDepth_UnitsDescr.setText("inch")
            self.window.label_Tool_StepOver_UnitsDescr.setText("]0:1]")
            self.window.label_Tool_Rapid_UnitsDescr.setText("inch/min")
            self.window.label_Tool_Plunge_UnitsDescr.setText("inch/min")
            self.window.label_Tool_Cut_UnitsDescr.setText("inch/min")
        if tool_units == "mm":
            self.window.label_Tool_Diameter_UnitsDescr.setText("mm")
            self.window.label_Tool_Angle_UnitsDescr.setText("degrees")
            self.window.label_Tool_PassDepth_UnitsDescr.setText("mm")
            self.window.label_Tool_StepOver_UnitsDescr.setText("]0:1]")
            self.window.label_Tool_Rapid_UnitsDescr.setText("mm/min")
            self.window.label_Tool_Plunge_UnitsDescr.setText("mm/min")
            self.window.label_Tool_Cut_UnitsDescr.setText("mm/min")

    def cb_update_gcodeconversion_display(self):
        '''
        '''
        gcodeconversion_units = self.window.comboBox_GCodeConversion_Units.currentText()
        
        if gcodeconversion_units == "inch":
            self.window.label_GCodeConversion_XOffset_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_YOffset_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_MinX_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_MaxX_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_MinY_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_MaxY_UnitsDescr.setText("inch")
            
        if gcodeconversion_units == "mm":
            self.window.label_GCodeConversion_XOffset_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_YOffset_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_MinX_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_MaxX_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_MinY_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_MaxY_UnitsDescr.setText("mm")
            
            
        
    def init_svg_viewer(self):
        '''
        '''
        svgviewer = SvgViewer(self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(svgviewer)
        layout.addStretch()
        self.window.widget.setLayout(layout)
        
        return svgviewer

    def display_svg(self, svg):
        '''
        '''
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
            
            img = b'''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="100"
                height="100"
                viewBox="0 0 100 100"
                version="1.1">
                <style>svg { background-color: green; }</style>
                <g>
                  <path id="rect10"
                    style="fill:#d40000;stroke-width:0.328797"
                    d="M 20,20 H 60 V 80 H 20 Z" />
                </g>
             </svg>'''
            self.svgviewer.set_svg(img)
        else:
            fp = open(svg, "r");

            data = fp.read()
            img = bytes(data, 'utf-8')
            fp.close()

            self.svgviewer.set_svg(img)

    def init_material_viewer(self):
        '''
        '''
        svg_material_viewer = QtSvg.QSvgWidget()

        renderer = svg_material_viewer.renderer()
        renderer.setAspectRatioMode(QtCore.Qt.KeepAspectRatio)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(svg_material_viewer)

        self.window.widget_display_material.setLayout(layout)
        
        return svg_material_viewer
        
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

        self.svg_material_viewer.load(img)

    def cb_doubleSpinBoxThickness(self):
        thickness = self.window.doubleSpinBoxThickness.value()
        clearance = self.window.doubleSpinBoxClearance.value()
        self.display_material(thickness=thickness, clearance=clearance)

    def cb_doubleSpinBoxClearance(self):
        thickness = self.window.doubleSpinBoxThickness.value()
        clearance = self.window.doubleSpinBoxClearance.value()
        self.display_material(thickness=thickness, clearance=clearance)

    def display_op(self):
        '''
        '''
        op = self.window.comboBoxOperation.currentText()

        if self.current_op_widget != None:
            self.window.verticalLayoutOperations.removeWidget(self.current_op_widget)
            self.current_op_widget.deleteLater()
 
        if op == "Pocket":
            self.current_op_widget = self.load_ui("op_pocket.ui")
            self.window.verticalLayoutOperations.addWidget(self.current_op_widget)
        if op == "Inside":
            self.current_op_widget = self.load_ui("op_inside.ui")
            self.window.verticalLayoutOperations.addWidget(self.current_op_widget)
        if op == "Outside":
            self.current_op_widget = self.load_ui("op_outside.ui")
            self.window.verticalLayoutOperations.addWidget(self.current_op_widget)
        if op == "Engrave":
            self.current_op_widget = self.load_ui("op_engrave.ui")
            self.window.verticalLayoutOperations.addWidget(self.current_op_widget)
        if op == "V Pocket":
            self.current_op_widget = self.load_ui("op_vpocket.ui")
            self.window.verticalLayoutOperations.addWidget(self.current_op_widget)

        self.window.layout()


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
