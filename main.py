# This Python file uses the following encoding: utf-8

import sys
import os
import io

import json

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from PySide2 import QtSvg

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader

import svgviewer


class main(QtWidgets.QMainWindow):
    default_settings = {
        "px_per_inch" : 96,
        "Tabs": {
            "Units"       : "mm",
            "MaxCutDepth" : 1.0
        },
        "Tool" : {
            "Units"       : "mm",
            "Diameter"    : 1.0,
            "Angle"       : 2,
            "PassDepth"   : 3.0,
            "StepOver"    : 4.0,
            "Rapid"       : 5.0,
            "Plunge"      : 6.0,
            "Cut"         : 7.0,
        },
        "Material" : {
            "Units"       : "mm",
            "Thickness"   : 50.0,
            "ZOrigin"     : "Top",
            "Clearance"   : 10.0,
        },
        "CurveToLineConversion" : {
            "MinimumSegments"       : 1,
            "MinimumSegmentsLength" : 0.001,
        },
        "GCodeConversion" : {
            "Units"         : "mm",
            "ZeroLowerLeft" : True,
            "ZeroCenter"    : False,
            "XOffset"       : 1.0,
            "YOffset"       : 2.0,
            "MinX"          : 3.0,
            "MaxX"          : 4.0,
            "MinY"          : 5.0,
            "MaxY"          : 6.0,
        },
        "GCodeGeneration" : {
            "ReturnToZeroAtEnd" : True,
            "SpindleAutomatic"  : True,
        },
        "session" : {
            "svg" : "xxx.svg",
            "operations": [
                {
                    "type"       : "Pockect",
                    "Deep"       : 0.2,
                    "Name"       : "op1",
                    "RampPlunge" : True,
                    "Combine"    : "Union",
                    "Direction"  : "Conventional",
                    "Units"      : "mm",
                    "Margin"     : 0.0
                },
                {
                    "type": "Inside",
                    "Deep"       : 0.2,
                    "Name"       : "op1",
                    "RampPlunge" : True,
                    "Combine"    : "Union",
                    "Direction"  : "Conventional",
                    "Units"      : "mm",
                    "Margin"     : 0.0,
                    "Width"      : 1.1
                },
                {
                    "type": "Outside",
                    "Deep"       : 0.2,
                    "Name"       : "op1",
                    "RampPlunge" : True,
                    "Combine"    : "Union",
                    "Direction"  : "Conventional",
                    "Units"      : "mm",
                    "Margin"     : 0.0,
                    "Width"      : 1.1
                },
                {
                    "type": "Engrave",
                    "Deep"       : 0.2,
                    "Name"       : "op1",
                    "RampPlunge" : True,
                    "Combine"    : "Union",
                    "Direction"  : "Conventional",
                    "Units"      : "mm",
                    "Margin"     : 0.0
                },
                {
                    "type": "V Pocket",
                    "Name"       : "op2",
                    "Combine"    : "Union",
                    "Units"      : "mm",
                    "Margin"     : 0.0
                },
          
            ]
        }
    }
    
    def __init__(self):
        super(main, self).__init__()
        self.window = self.load_ui("form.ui")

        self.setCentralWidget(self.window)

        self.svg_viewer = self.init_svg_viewer()
        self.svg_material_viewer = self.init_material_viewer()
        self.current_op_widget = None

        # callbacks
        self.window.actionOpen_SVG.triggered.connect(self.cb_open_svg)
        self.window.actionSaveSettings.triggered.connect(self.cb_save_settings)
        self.window.actionOpenSettings.triggered.connect(self.cb_read_settings)

        # display material thickness/clearance
        self.window.doubleSpinBox_Material_Thickness.valueChanged.connect(self.cb_doubleSpinBox_Material_Thickness)
        self.window.doubleSpinBox_Material_Clearance.valueChanged.connect(self.cb_doubleSpinBox_Material_Clearance)

        self.window.comboBox_Operations_OpType.currentTextChanged.connect(self.display_op)
        
        
        default_thickness = self.window.doubleSpinBox_Material_Thickness.value()
        default_clearance = self.window.doubleSpinBox_Material_Clearance.value()
        self.display_material(thickness=default_thickness, clearance=default_clearance)
        
        self.display_svg(None)
        self.hide_op_widgets()

        self.window.pushButton_Operations_CreateNewOp.clicked.connect(self.cb_create_op)
        self.window.pushButton_Operations_AddOp.clicked.connect(self.cb_add_op)
        self.window.pushButton_Operations_CancelOp.clicked.connect(self.cb_cancel_op)
        
        self.window.comboBox_Tool_Units.currentTextChanged.connect(self.cb_update_tool_display)
        self.window.comboBox_GCodeConversion_Units.currentTextChanged.connect(self.cb_update_gcodeconversion_display)
        
        self.window.pushButton_MakeAll_inch.clicked.connect(self.cb_make_all_inch)
        self.window.pushButton_MakeAll_mm.clicked.connect(self.cb_make_all_mm)
        
        self.init_gui()
        
        self.set_settings(self.default_settings)

    def load_ui(self, ui):
        '''
        '''
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), ui)
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        window = loader.load(ui_file)
        ui_file.close()

        return window
    
    def init_gui(self):
        '''
        '''
        self.cb_update_tool_display()
        self.cb_update_gcodeconversion_display()
        
    def cb_save_settings(self):
        '''
        '''
        settings = {
            "px_per_inch" : 96,
            "Tabs": {
                "Units"      : self.window.comboBox_Tabs_Units.currentText(),
                "MaxCutDepth": self.window.doubleSpinBox_Tabs_MaxCutDepth.value()
            },
            "Tool" : {
                "Units"      : self.window.comboBox_Tool_Units.currentText(),
                "Diameter"   : self.window.doubleSpinBox_Tool_Diameter.value(),
                "Angle"      : self.window.spinBox_Tool_Angle.value(),
                "PassDepth"  : self.window.doubleSpinBox_Tool_PassDepth.value(),
                "StepOver"   : self.window.doubleSpinBox_Tool_StepOver.value(),
                "Rapid"      : self.window.spinBox_Tool_Rapid.value(),
                "Plunge"     : self.window.spinBox_Tool_Plunge.value(),
                "Cut"        : self.window.spinBox_Tool_Cut.value()
            },
            "Material" : {
                "Units"      : self.window.comboBox_Material_Units.currentText(),
                "Thickness"  : self.window.doubleSpinBox_Material_Thickness.value(),
                "ZOrigin"    : self.window.comboBox_Material_ZOrigin.currentText(),
                "Clearance"  : self.window.doubleSpinBox_Material_Clearance.value(),
            },
            "CurveToLineConversion" : {
                "MinimumSegments"       : self.window.doubleSpinBox_CurveToLineConversion_MinimumSegments.value(),
                "MinimumSegmentsLength" : self.window.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.value(),
            },
            "GCodeConversion" : {
                "Units"           : self.window.comboBox_GCodeConversion_Units.currentText(),
                "ZeroLowerLeft"   : self.window.radioButton_GCodeConversion_ZeroLowerLeft.isChecked(),
                "ZeroCenter"      : self.window.radioButton_GCodeConversion_ZeroCenter.isChecked(),
                "XOffset"         : self.window.doubleSpinBox_GCodeConversion_XOffset.value(),
                "YOffset"         : self.window.doubleSpinBox_GCodeConversion_YOffset.value(),
                "MinX"            : self.window.doubleSpinBox_GCodeConversion_MinX.value(),
                "MaxX"            : self.window.doubleSpinBox_GCodeConversion_MaxX.value(),
                "MinY"            : self.window.doubleSpinBox_GCodeConversion_MinY.value(),
                "MaxY"            : self.window.doubleSpinBox_GCodeConversion_MaxY.value(),
            },
            "GCodeGeneration" : {
                "ReturnToZeroAtEnd" : self.window.checkBox_GCodeGeneration_ReturnToZeroAtEnd.isChecked(),
                "SpindleAutomatic"  : self.window.checkBox_GCodeGeneration_SpindleAutomatic.isChecked(),
            },
            "session" : {
            "svg" : "xxx.svg",
            "operations": [
                {
                    "type"       : "Pockect",
                    "Deep"       : 0.2,
                    "Name"       : "op1",
                    "RampPlunge" : True,
                    "Combine"    : "Union",
                    "Direction"  : "Conventional",
                    "Units"      : "mm",
                    "Margin"     : 0.0
                },
                {
                    "type": "Inside",
                    "Deep"       : 0.2,
                    "Name"       : "op1",
                    "RampPlunge" : True,
                    "Combine"    : "Union",
                    "Direction"  : "Conventional",
                    "Units"      : "mm",
                    "Margin"     : 0.0,
                    "Width"      : 1.1
                },
                {
                    "type": "Outside",
                    "Deep"       : 0.2,
                    "Name"       : "op1",
                    "RampPlunge" : True,
                    "Combine"    : "Union",
                    "Direction"  : "Conventional",
                    "Units"      : "mm",
                    "Margin"     : 0.0,
                    "Width"      : 1.1
                },
                {
                    "type": "Engrave",
                    "Deep"       : 0.2,
                    "Name"       : "op1",
                    "RampPlunge" : True,
                    "Combine"    : "Union",
                    "Direction"  : "Conventional",
                    "Units"      : "mm",
                    "Margin"     : 0.0
                },
                {
                    "type": "V Pocket",
                    "Name"       : "op2",
                    "Combine"    : "Union",
                    "Units"      : "mm",
                    "Margin"     : 0.0
                },
          
            ]
        }
        }
        
        # write settings to json file
        print(settings)
        
        with open('settings.json', 'w') as json_file:
            json.dump(settings, json_file, indent=4)
        
    def cb_read_settings(self):
        # read json
        xfilter = "JSON Files (*.json)"
        json_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="open file", dir=".", filter=xfilter)
        
        with open(json_file) as f:
            settings = json.load(f)
            self.set_settings(settings)
        
    def set_settings(self, settings):
        '''
        '''
        # Tabs
        self.window.comboBox_Tabs_Units.setCurrentText(settings["Tabs"]["Units"])
        self.window.doubleSpinBox_Tabs_MaxCutDepth.setValue(settings["Tabs"]["MaxCutDepth"])
            
        # Tool
        self.window.comboBox_Tool_Units.setCurrentText(settings["Tool"]["Units"])
        self.window.doubleSpinBox_Tool_Diameter.setValue(settings["Tool"]["Diameter"])
        self.window.spinBox_Tool_Angle.setValue(settings["Tool"]["Angle"])
        self.window.doubleSpinBox_Tool_PassDepth.setValue(settings["Tool"]["PassDepth"])
        self.window.doubleSpinBox_Tool_StepOver.setValue(settings["Tool"]["StepOver"])
        self.window.spinBox_Tool_Rapid.setValue(settings["Tool"]["Rapid"])
        self.window.spinBox_Tool_Plunge.setValue(settings["Tool"]["Plunge"])
        self.window.spinBox_Tool_Cut.setValue(settings["Tool"]["Cut"])
        
        # Material
        self.window.comboBox_Material_Units.setCurrentText(settings["Material"]["Units"])
        self.window.doubleSpinBox_Material_Thickness.setValue(settings["Material"]["Thickness"])
        self.window.comboBox_Material_ZOrigin.setCurrentText(settings["Material"]["ZOrigin"])
        self.window.doubleSpinBox_Material_Clearance.setValue(settings["Material"]["Clearance"])
            
        # CurveToLineConversion 
        self.window.doubleSpinBox_CurveToLineConversion_MinimumSegments.setValue(settings["CurveToLineConversion"]["MinimumSegments"]),
        self.window.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setValue(settings["CurveToLineConversion"]["MinimumSegmentsLength"]),
            
        # GCodeConversion
        self.window.comboBox_GCodeConversion_Units.setCurrentText(settings["GCodeConversion"]["Units"])
        self.window.radioButton_GCodeConversion_ZeroLowerLeft.setChecked(settings["GCodeConversion"]["ZeroLowerLeft"])
        self.window.radioButton_GCodeConversion_ZeroCenter.setChecked(settings["GCodeConversion"]["ZeroCenter"])
        self.window.doubleSpinBox_GCodeConversion_XOffset.setValue(settings["GCodeConversion"]["XOffset"])
        self.window.doubleSpinBox_GCodeConversion_YOffset.setValue(settings["GCodeConversion"]["YOffset"])
        self.window.doubleSpinBox_GCodeConversion_MinX.setValue(settings["GCodeConversion"]["MinX"])
        self.window.doubleSpinBox_GCodeConversion_MaxX.setValue(settings["GCodeConversion"]["MaxX"])
        self.window.doubleSpinBox_GCodeConversion_MinY.setValue(settings["GCodeConversion"]["MinY"])
        self.window.doubleSpinBox_GCodeConversion_MaxY.setValue(settings["GCodeConversion"]["MaxY"])
            
        # GCodeGeneration 
        self.window.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setChecked(settings["GCodeGeneration"]["ReturnToZeroAtEnd"]),
        self.window.checkBox_GCodeGeneration_SpindleAutomatic.setChecked(settings["GCodeGeneration"]["SpindleAutomatic"]),
            
        # session
        svg = settings["session"]["svg"]
        if svg :
            # load
            pass
        
            operations = settings["session"]["operations"]
            
            for op in operations:
                #
                pass
        
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
        svg_viewer = svgviewer.SvgViewer(self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(svg_viewer)
        layout.addStretch()
        self.window.widget.setLayout(layout)
        
        return svg_viewer

    def display_svg(self, svg):
        '''
        '''
        self.svg_viewer.clean()

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
            self.svg_viewer.set_svg(img)
        else:
            fp = open(svg, "r");

            data = fp.read()
            img = bytes(data, 'utf-8')
            fp.close()

            self.svg_viewer.set_svg(img)

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

    def cb_doubleSpinBox_Material_Thickness(self):
        thickness = self.window.doubleSpinBox_Material_Thickness.value()
        clearance = self.window.doubleSpinBox_Material_Clearance.value()
        self.display_material(thickness=thickness, clearance=clearance)

    def cb_doubleSpinBox_Material_Clearance(self):
        thickness = self.window.doubleSpinBox_Material_Thickness.value()
        clearance = self.window.doubleSpinBox_Material_Clearance.value()
        self.display_material(thickness=thickness, clearance=clearance)


    def cb_create_op(self):
        '''
        '''
        self.show_op_widgets()

    def cb_add_op(self):
        '''
        '''
        self.hide_op_widgets()

    def cb_cancel_op(self):
        '''
        '''
        self.hide_op_widgets()

    def hide_op_widgets(self):
        '''
        '''
        self.window.comboBox_Operations_OpType.hide()
        self.window.doubleSpinBox_Operations_OpDepth.hide()
        self.window.label_Operations_OpDepth.hide()

        self.window.pushButton_Operations_AddOp.hide()
        self.window.pushButton_Operations_CancelOp.hide()

        if self.current_op_widget != None:
            self.current_op_widget.hide()

    def show_op_widgets(self):
        '''
        '''
        self.window.comboBox_Operations_OpType.show()
        self.window.doubleSpinBox_Operations_OpDepth.show()
        self.window.label_Operations_OpDepth.show()

        self.window.pushButton_Operations_AddOp.show()
        self.window.pushButton_Operations_CancelOp.show()

        if self.current_op_widget != None:
            self.current_op_widget.show()

        self.display_op()

    def display_op(self):
        '''
        '''
        op = self.window.comboBox_Operations_OpType.currentText()

        if self.current_op_widget != None:
            self.window.verticalLayoutOperations.removeWidget(self.current_op_widget)
            self.current_op_widget.deleteLater()

        mapp = {
            'Pocket'   : "op_pocket.ui",
            'Inside'   : "op_inside.ui",
            'Outside'  : "op_outside.ui",
            'Engrave'  : "op_engrave.ui",
            'V Pocket' : "op_vpocket.ui",
        }

        self.current_op_widget = self.load_ui(mapp[op])

        self.window.verticalLayoutOperations.insertWidget(5, self.current_op_widget, 0, QtGui.Qt.AlignLeft)

        if op == "V Pocket":
            self.window.doubleSpinBox_Operations_OpDepth.hide()
            self.window.label_Operations_OpDepth.hide()
        else:
            self.window.doubleSpinBox_Operations_OpDepth.show()
            self.window.label_Operations_OpDepth.show()

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
