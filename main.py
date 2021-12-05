# This Python file uses the following encoding: utf-8

import sys
import os
import io

import json

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

import svgviewer
import webglviewer
import svgmaterial
import operations_simpletablewidget

from cnc_op import CncOp
from cnc_op import JobModel

from pycut import ToolModel
from pycut import SvgModel
from pycut import MaterialModel
from pycut import TabsModel

from pycut import GcodeGenerator

import resources_rc


class PyCutMainWindow(QtWidgets.QMainWindow):
    default_settings = {
        "svg": {
            "px_per_inch" : 96,
        },
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
            "Rapid"       : 500,
            "Plunge"      : 100,
            "Cut"         : 200,
        },
        "Material" : {
            "Units"       : "mm",
            "Thickness"   : 50.0,
            "ZOrigin"     : "Top",
            "Clearance"   : 10.0,
        },
        "CurveToLineConversion" : {
            "MinimumSegments"       : 1,
            "MinimumSegmentsLength" : 0.01,
        },
        "GCodeConversion" : {
            "Units"         : "mm",
            "ZeroLowerLeft" : True,
            "ZeroCenter"    : False,
            "XOffset"       : 1.0,
            "YOffset"       : 2.0,
        },
        "GCodeGeneration" : {
            "ReturnToZeroAtEnd" : True,
            "SpindleAutomatic"  : True,
            "SpindleSpeed"      : 1000
        }
    }
    
    def __init__(self):
        super(PyCutMainWindow, self).__init__()
        self.window = self.load_ui("main.ui")

        # the full data
        self.job = None
        # the operation displayed ("expanded")
        self.current_op = None
        self.current_op_widget = None
        
        self.setCentralWidget(self.window)

        self.svg_viewer = self.setup_svg_viewer()
        self.svg_material_viewer = self.setup_material_viewer()
        self.webgl_viewer = self.setup_webgl_viewer()

        # callbacks
        self.window.actionOpenSvg.triggered.connect(self.cb_open_svg)
        self.window.actionOpenJob.triggered.connect(self.cb_open_job)

        # display material thickness/clearance
        self.window.doubleSpinBox_Material_Thickness.valueChanged.connect(self.cb_display_material_thickness)
        self.window.doubleSpinBox_Material_Clearance.valueChanged.connect(self.cb_display_material_clearance)


        default_thickness = self.window.doubleSpinBox_Material_Thickness.value()
        default_clearance = self.window.doubleSpinBox_Material_Clearance.value()
        self.svg_material_viewer.display_material(thickness=default_thickness, clearance=default_clearance)
        
        self.display_svg(None)
        self.hide_op_widgets()

        self.window.comboBox_Operations_OpType.currentTextChanged.connect(self.display_op_widgets)

        self.window.pushButton_Operations_CreateNewOp.clicked.connect(self.cb_create_op)
        self.window.pushButton_Operations_SaveOp.clicked.connect(self.cb_save_op)
        self.window.pushButton_Operations_CancelOp.clicked.connect(self.cb_cancel_op)
        
        self.window.comboBox_Tool_Units.currentTextChanged.connect(self.cb_update_tool_display)
        self.window.comboBox_GCodeConversion_Units.currentTextChanged.connect(self.cb_update_gcodeconversion_display)
        
        self.window.pushButton_MakeAll_inch.clicked.connect(self.cb_make_all_inch)
        self.window.pushButton_MakeAll_mm.clicked.connect(self.cb_make_all_mm)
        
        self.window.pushButton_ShowHideSettings.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-down_16x16.png"))
        self.window.pushButton_ShowHideSettings.clicked.connect(self.cb_show_hide_settings)

        self.window.pushButton_ShowHideTabs.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-down_16x16.png"))
        self.window.pushButton_ShowHideTabs.clicked.connect(self.cb_show_hide_tabs)
        
        self.window.pushButton_ShowHideTool.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-down_16x16.png"))
        self.window.pushButton_ShowHideTool.clicked.connect(self.cb_show_hide_tool)

        self.window.checkBox_GCodeGeneration_SpindleAutomatic.clicked.connect(self.cb_spindle_automatic)

        self.window.pushButton_GenerateGCode.clicked.connect(self.cb_generate_g_code)

        self.init_gui()
        
        #self.open_job("./jobs/cnc_three_rects.json")
        #self.open_job("./jobs/cnc_three_rects_with_circle.json")
        self.open_job("./jobs/cnc_one_rect.json")

        self.display_gcode_file("gcode.gcode")

    def display_gcode_file(self, filename):
        '''
        display gcode in webgl!
        '''
        fp = open(filename, "r")
        gcode = fp.read()
        fp.close()

        simulator_data =  {
            "width": "400",
            "height" : "400",
            "gcode": gcode,
            "cutterDiameter" : "4", 
            "cutterHeight" : "20",
            #"cutterAngle" : undefined,
            "elementsUrl" : "http://api.jscut.org/elements"
        }
        
        str_simulator_data = str(simulator_data)
        str_simulator_data = str(str_simulator_data).replace("'", '"')

        self.webgl_viewer.set_webgl_data(str_simulator_data)
        self.webgl_viewer.show_gcode()

    def load_ui(self, uifile):
        '''
        '''
        loader = QUiLoader(self)
        loader.registerCustomWidget(operations_simpletablewidget.PyCutSimpleTableWidget)
        
        window = loader.load(uifile)

        return window
    
    def cb_show_hide_settings(self):
        '''
        '''
        if self.window.grid_Settings.isHidden():
            self.window.grid_Settings.show()
            self.window.pushButton_ShowHideSettings.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-down_16x16.png"))
        else:
            self.window.grid_Settings.hide()
            self.window.pushButton_ShowHideSettings.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-right_16x16.png"))

    def cb_show_hide_tabs(self):
        '''
        '''
        if self.window.grid_Tabs.isHidden():
            self.window.grid_Tabs.show()
            self.window.pushButton_ShowHideTabs.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-down_16x16.png"))
        else:
            self.window.grid_Tabs.hide()
            self.window.pushButton_ShowHideTabs.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-right_16x16.png"))

    def cb_show_hide_tool(self):
        '''
        '''
        if self.window.grid_Tool.isHidden():
            self.window.grid_Tool.show()
            self.window.pushButton_ShowHideTool.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-down_16x16.png"))
        else:
            self.window.grid_Tool.hide()
            self.window.pushButton_ShowHideTool.setIcon(QtGui.QIcon(":/images/tango_inofficial/caret-right_16x16.png"))

    def init_gui(self):
        '''
        set the default settings in the gui 
        '''
        self.apply_settings(self.default_settings)

        self.cb_update_tool_display()
        self.cb_update_gcodeconversion_display()
    
    def get_current_settings(self):
        '''
        '''
        settings = {
            "svg": {
                "px_per_inch" : 96,
            }, 
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
                "YOffset"         : self.window.doubleSpinBox_GCodeConversion_YOffset.value()
            },
            "GCodeGeneration" : {
                "ReturnToZeroAtEnd" : self.window.checkBox_GCodeGeneration_ReturnToZeroAtEnd.isChecked(),
                "SpindleAutomatic"  : self.window.checkBox_GCodeGeneration_SpindleAutomatic.isChecked(),
                "SpindleSpeed"      : self.window.checkBox_GCodeGeneration_SpindleSpeed.value(),
            }
        }
        
        return settings

    def apply_settings(self, settings):
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
            
        # GCodeGeneration 
        self.window.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setChecked(settings["GCodeGeneration"]["ReturnToZeroAtEnd"]),
        self.window.checkBox_GCodeGeneration_SpindleAutomatic.setChecked(settings["GCodeGeneration"]["SpindleAutomatic"]),
        self.window.spinBox_GCodeGeneration_SpindleSpeed.setValue(settings["GCodeGeneration"]["SpindleSpeed"]),


    @QtCore.Slot()
    def cb_open_svg(self):
        '''
        not a job, a svg only -> no oerations
        '''
        xfilter = "SVG Files (*.svg)"
        svg_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="open file", dir=".", filter=xfilter)

        if svg_file:
            self.svg_file = svg_file
            self.operations = []
            
            self.display_svg(self.svg_file)
            self.display_operations(self.operations)
 
    def cb_open_job(self):
        '''
        '''
        # read json
        xfilter = "JSON Files (*.json)"
        json_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="open file", dir=".", filter=xfilter)
        
        self.open_job(json_file)
        
    def open_job(self, json_file):
        with open(json_file) as f:
            self.job = job = json.load(f)
        
            self.svg_file = job["svg_file"]
            self.operations = job["operations"]
        
            # display
            self.display_svg(self.svg_file)
            # display operations in table
            self.display_operations(self.operations)
            
            # and fill the whole gui
            self.apply_settings(job["settings"])
        
    def save_job(self):
        '''
        '''
        job = {
            "svg_file" : self.svg_file,
            "operations": self.operations,
            "settings": self.get_current_settings()
        }
            
        job_file_name = 'job_%s.json' % self.svg 
        
        with open(job_file_name, 'w') as json_file:
            json.dump(job, json_file, indent=2)   
            
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
        self.window.comboBox_Material_Units.setCurrentText("mm")
        self.window.comboBox_GCodeConversion_Units.setCurrentText("mm")
        
        self.cb_update_tool_display()
        self.cb_update_gcodeconversion_display()
        
    def cb_update_tool_display(self):
        '''
        This updates the legends of the tool model widget
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
        This updates the legends of the gcode_conversion model widget
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

    def cb_display_material_thickness(self):
        thickness = self.window.doubleSpinBox_Material_Thickness.value()
        clearance = self.window.doubleSpinBox_Material_Clearance.value()
        self.svg_material_viewer.display_material(thickness=thickness, clearance=clearance)

    def cb_display_material_clearance(self):
        thickness = self.window.doubleSpinBox_Material_Thickness.value()
        clearance = self.window.doubleSpinBox_Material_Clearance.value()
        self.svg_material_viewer.display_material(thickness=thickness, clearance=clearance)

    def cb_spindle_automatic(self):
        val = self.window.checkBox_GCodeGeneration_SpindleAutomatic.isChecked()
        self.window.spinBox_GCodeGeneration_SpindleSpeed.setEnabled(val)

    def setup_material_viewer(self):
        '''
        '''
        return svgmaterial.SvgMaterialWidget(self.window.widget_display_material)

    def setup_svg_viewer(self):
        '''
        '''
        svg = self.window.svg
        layout = svg.layout()
        
        svg_viewer = svgviewer.SvgViewer(svg)
        
        layout.addWidget(svg_viewer)
        layout.addStretch(0)
        
        return svg_viewer

    def setup_webgl_viewer(self):
        '''
        '''
        webgl = self.window.webgl
        layout = webgl.layout()
        
        webgl_viewer = webglviewer.WebGlViewer(webgl)

        layout.addWidget(webgl_viewer)
        layout.stretch(0)
        
        return webgl_viewer

    def display_svg(self, svg):
        '''
        '''
        self.svg_viewer.clean()

        if svg is None:
            
            svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="100"
                height="100"
                viewBox="0 0 100 100"
                version="1.1">
                <style>svg { background-color: green; }</style>
                <g>
                  <path id="p1" style="fill:#d40000;stroke-width:1;stroke:#00ff00"
                    d="M 20,20 H 60 V 80 H 20 Z" />
                  <path id="p2" style="fill:#0000ff;stroke-width:0"
                    d="M 40,40 H 70 V 90 H 40 Z" />
                </g>
             </svg>'''
            self.svg_viewer.set_svg(svg)
        else:
            fp = open(svg, "r")
            svg = fp.read()
            fp.close()

            self.svg_viewer.set_svg(svg)

    def display_operations(self, operations):
        '''
        '''
        self.window.tableWidget_Operations_ViewOps.setData(operations)

    def cb_create_op(self):
        '''
        '''
        self.show_op_widgets()
        self.window.comboBox_Operations_OpType.show()
        self.window.comboBox_Operations_OpType.setEnabled(True)

        # now the real stuff - svg entities ("paths") have been selected
        # -> they can be "combined" with the operation setting (Union, Interection, XOR, Diff)

        # 1- first, we calculate the resuting paths as results of the combination.
        # -> we display as svg this results (as in jscut) in black in the svg viewer
        operation = self.operation
        operation["paths"] = self.svg_viewer.selected_items

        cnc_op = CncOp(operation)
        cnc_op.setup(self.svg_viewer)
        cnc_op.calculate_geometry()

        # 1- the gcode 'region'
        self.svg_viewer.display_cnc_op(cnc_op.geometry_svg_paths)

        # 2- the gcode calculation and display
        # TODO

    def cb_save_op(self):
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

        self.window.pushButton_Operations_SaveOp.hide()
        self.window.pushButton_Operations_CancelOp.hide()

        if self.current_op_widget != None:
            self.current_op_widget.hide()

    def show_op_widgets(self):
        '''
        '''
        self.window.comboBox_Operations_OpType.show()
        self.window.doubleSpinBox_Operations_OpDepth.show()
        self.window.label_Operations_OpDepth.show()

        self.window.pushButton_Operations_SaveOp.show()
        self.window.pushButton_Operations_CancelOp.show()

        if self.current_op_widget != None:
            self.current_op_widget.show()

        self.display_op_widgets()    
        
    def display_op_widgets(self):
        '''
        '''
        op_type = self.window.comboBox_Operations_OpType.currentText()

        self.display_op_widgets_type(op_type)

    def display_op_at_row(self, row):
        '''
        callback on row selection
        '''
        operation = self.operations[row]
        
        self.window.comboBox_Operations_OpType.show()
        self.window.comboBox_Operations_OpType.setEnabled(False)
        
        self.window.doubleSpinBox_Operations_OpDepth.show()
        self.window.label_Operations_OpDepth.show()
        
        self.window.comboBox_Operations_OpType.setCurrentText(operation["type"])
        self.display_op_widgets_type(operation["type"])

        self.display_operation(operation)
        self.display_operation_on_svg_canvas(operation)
       
    def display_op_widgets_type(self, op_type):
        '''
        '''
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

        self.current_op_widget = self.load_ui(mapp[op_type])

        self.window.verticalLayoutOperations.insertWidget(5, self.current_op_widget, 0, QtGui.Qt.AlignLeft)

        if op_type == "V Pocket":
            self.window.doubleSpinBox_Operations_OpDepth.hide()
            self.window.label_Operations_OpDepth.hide()
        else:
            self.window.doubleSpinBox_Operations_OpDepth.show()
            self.window.label_Operations_OpDepth.show()

        self.window.layout()
        
        # fill widget with default values
        
        if op_type == "Pocket":
            operation = {
                "Name": "-- op pocket --",
                "paths": [],
                "type": "Pocket",
                "Deep": 0.2,       
                "RampPlunge": True,
                "Combine": "Union",
                "Direction": "Conventional",
                "Units": "mm",
                "Margin": 0.1
            }
        if op_type == "Inside":
            operation = {
                "Name": "-- op inside --",
                "paths": [],
                "type": "Inside",
                "Deep": 0.2,       
                "RampPlunge": True,
                "Combine": "Union",
                "Direction": "Conventional",
                "Units": "mm",
                "Margin": 0.1,
                "Width": 1.1
            }
        if op_type == "Outside":
            operation = {
                "Name": "-- op outside --",
                "paths": [],
                "type": "Outside",
                "Deep": 0.2,       
                "RampPlunge": True,
                "Combine": "Difference",
                "Direction": "Conventional",
                "Units": "mm",
                "Margin": 0.1,
                "Width": 1.1
            }
        if op_type == "Engrave":
            operation = {
                "Name": "-- op outside --",
                "paths": [],
                "type": "Engrave",
                "RampPlunge": True,
                "Combine": "Xor",
                "Direction": "Conventional",
                "Units": "mm",
                "Margin": 0.1,
            }
        if op_type == "V Pocket":
            operation = {
                "Name": "-- op v-pocket --",
                "paths": [],
                "type": "V Pocket",
                "Combine": "Union",
                "Units": "mm",
                "Margin": 0.1,
            }
        self.display_operation(operation)
        
    def display_operation(self, operation):
        '''
        '''
        if operation["type"] == "Pocket":
            self.current_op_widget.lineEdit_Name.setText(operation["Name"])
            self.current_op_widget.checkBox_RampPlunge.setChecked(operation["RampPlunge"])
            self.current_op_widget.comboBox_Combine.setCurrentText(operation["Combine"])  # "Union", "Intersect",  "Diff", "Xor"
            self.current_op_widget.comboBox_Direction.setCurrentText(operation["Direction"])  # "Conventional", "Plunge"
            self.current_op_widget.comboBox_Units.setCurrentText(operation["Units"]) # mm, "inch"
            self.current_op_widget.doubleSpinBox_Margin.setValue(operation["Margin"])
        if operation["type"] == "Inside":
            self.current_op_widget.lineEdit_Name.setText(operation["Name"])
            self.current_op_widget.checkBox_RampPlunge.setChecked(operation["RampPlunge"])
            self.current_op_widget.comboBox_Combine.setCurrentText(operation["Combine"])  # "Intersect",  "Diff", "Xor"
            self.current_op_widget.comboBox_Direction.setCurrentText(operation["Direction"])  # "Plunge"
            self.current_op_widget.comboBox_Units.setCurrentText(operation["Units"])
            self.current_op_widget.doubleSpinBox_Margin.setValue(operation["Margin"])
            self.current_op_widget.doubleSpinBox_Width.setValue(operation["Width"])
        if operation["type"] == "Outside":
            self.current_op_widget.lineEdit_Name.setText(operation["Name"])
            self.current_op_widget.checkBox_RampPlunge.setChecked(operation["RampPlunge"])
            self.current_op_widget.comboBox_Combine.setCurrentText(operation["Combine"])  # "Intersect",  "Diff", "Xor"
            self.current_op_widget.comboBox_Direction.setCurrentText(operation["Direction"])  # "Plunge"
            self.current_op_widget.comboBox_Units.setCurrentText(operation["Units"])
            self.current_op_widget.doubleSpinBox_Margin.setValue(operation["Margin"])
            self.current_op_widget.doubleSpinBox_Width.setValue(operation["Width"])
        if operation["type"] == "Engrave":
            self.current_op_widget.lineEdit_Name.setText(operation["Name"])
            self.current_op_widget.checkBox_RampPlunge.setChecked(operation["RampPlunge"])
            self.current_op_widget.comboBox_Combine.setCurrentText(operation["Combine"])  # "Intersect",  "Diff", "Xor"
            self.current_op_widget.comboBox_Direction.setCurrentText(operation["Direction"])  # "Plunge"
            self.current_op_widget.comboBox_Units.setCurrentText(operation["Units"])
            self.current_op_widget.doubleSpinBox_Margin.setValue(operation["Margin"])
        if operation["type"] == "V Pocket":
            self.current_op_widget.lineEdit_Name.setText(operation["Name"])
            self.current_op_widget.comboBox_Combine.setCurrentText(operation["Combine"])  # "Intersect",  "Diff", "Xor"  
            self.current_op_widget.comboBox_Units.setCurrentText(operation["Units"])
            self.current_op_widget.doubleSpinBox_Margin.setValue(operation["Margin"])
        
    def display_operation_on_svg_canvas(self, operation):
        '''
        '''
        cnc_op = CncOp(operation)
        cnc_op.setup(self.svg_viewer)
        cnc_op.calculate_geometry()

        self.svg_viewer.display_cnc_op(cnc_op.geometry_svg_paths)

    def cb_generate_g_code(self):
        '''
        '''
        cnc_ops = []
        for op in self.operations:
            cnc_op = CncOp(op)  
            cnc_ops.append(cnc_op)

        materialModel = MaterialModel()
        svgModel = SvgModel()
        toolModel = ToolModel()
        tabsmodel = TabsModel(svgModel, materialModel, None, None)
        
        job = JobModel(self.svg_viewer, cnc_ops, materialModel, svgModel, toolModel, tabsmodel)
        generator = GcodeGenerator(job)
        generator.generateGcode()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    pycut = PyCutMainWindow()
    pycut.show()
    sys.exit(app.exec())
