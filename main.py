# This Python file uses the following encoding: utf-8

import sys
import json

from typing import List
from typing import Any

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from ValWithUnit import ValWithUnit

import svgviewer
import webglviewer
import operations_tableview

import material_widget


from pycut import GcodeModel
from pycut import ToolModel
from pycut import SvgModel
from pycut import MaterialModel
from pycut import TabsModel
from pycut import CncOp
from pycut import JobModel

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
            "XOffset"       : 0.0,
            "YOffset"       : 0.0,
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
        
        self.setCentralWidget(self.window)

        xx = self.window.parent()

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
        
        self.window.comboBox_Tabs_Units.currentTextChanged.connect(self.cb_update_tabs_display)
        self.window.comboBox_Tool_Units.currentTextChanged.connect(self.cb_update_tool_display)
        self.window.comboBox_Material_Units.currentTextChanged.connect(self.cb_update_material_display)
        self.window.comboBox_GCodeConversion_Units.currentTextChanged.connect(self.cb_update_gcodeconversion_display)
        
        self.window.pushButton_MakeAll_inch.clicked.connect(self.cb_make_all_inch)
        self.window.pushButton_MakeAll_mm.clicked.connect(self.cb_make_all_mm)
        

        self.window.checkBox_GCodeGeneration_SpindleAutomatic.clicked.connect(self.cb_spindle_automatic)

        self.window.pushButton_GCodeConversion_ZeroLowerLeft.clicked.connect(self.cb_generate_g_code_zerolowerleft)
        self.window.pushButton_GCodeConversion_ZeroCenter.clicked.connect(self.cb_generate_g_code_zerocenter)

        self.window.doubleSpinBox_GCodeConversion_XOffset.valueChanged.connect(self.cb_generate_g_code)
        self.window.doubleSpinBox_GCodeConversion_YOffset.valueChanged.connect(self.cb_generate_g_code)

        self.init_gui()

        self.open_job("./jobs/cnc_three_rects.json")
        #self.open_job("./jobs/cnc_three_rects_with_circle.json")
        #self.open_job("./jobs/cnc_one_rect.json")

    def display_gcode_file(self, filename):
        '''
        display gcode in webgl!
        '''
        fp = open(filename, "r")
        gcode = fp.read()
        fp.close()

        self.display_gcode(gcode)

    def display_gcode(self, gcode: str):
        '''
        display gcode in webgl!
        '''
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
        loader.registerCustomWidget(operations_tableview.PMFTableViewManager)
        
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

        self.cb_update_tabs_display()
        self.cb_update_tool_display()
        self.cb_update_material_display()
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
                "XOffset"         : self.window.doubleSpinBox_GCodeConversion_XOffset.value(),
                "YOffset"         : self.window.doubleSpinBox_GCodeConversion_YOffset.value()
            },
            "GCodeGeneration" : {
                "ReturnToZeroAtEnd" : self.window.checkBox_GCodeGeneration_ReturnToZeroAtEnd.isChecked(),
                "SpindleAutomatic"  : self.window.checkBox_GCodeGeneration_SpindleAutomatic.isChecked(),
                "SpindleSpeed"      : self.window.spinBox_GCodeGeneration_SpindleSpeed.value(),
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
        self.window.doubleSpinBox_GCodeConversion_XOffset.setValue(settings["GCodeConversion"]["XOffset"])
        self.window.doubleSpinBox_GCodeConversion_YOffset.setValue(settings["GCodeConversion"]["YOffset"])
            
        # GCodeGeneration 
        self.window.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setChecked(settings["GCodeGeneration"]["ReturnToZeroAtEnd"]),
        self.window.checkBox_GCodeGeneration_SpindleAutomatic.setChecked(settings["GCodeGeneration"]["SpindleAutomatic"]),
        self.window.spinBox_GCodeGeneration_SpindleSpeed.setValue(settings["GCodeGeneration"]["SpindleSpeed"]),

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
            
            # and fill the whole gui
            self.apply_settings(job["settings"])

            # fill operations table
            self.window.operationsview_manager.set_operations(self.operations)
        
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
        not the tool

        TODO: the ops (cutDeepth) ?
        '''
        self.window.comboBox_Tabs_Units.setCurrentText("inch")
        self.window.comboBox_Material_Units.setCurrentText("inch")
        self.window.comboBox_GCodeConversion_Units.setCurrentText("inch")
    
    def cb_make_all_mm(self):
        '''
        not the tool

        TODO: the ops (cutDeepth) ?
        '''
        self.window.comboBox_Tabs_Units.setCurrentText("mm")
        self.window.comboBox_Material_Units.setCurrentText("mm")
        self.window.comboBox_GCodeConversion_Units.setCurrentText("mm")
        
    def cb_update_tabs_display(self):
        '''
        This updates the legends of the tsbs model widget **and** the values
        '''
        tabs_units = self.window.comboBox_Tabs_Units.currentText()
        
        if tabs_units == "inch":
            self.window.doubleSpinBox_Tabs_MaxCutDepth.setValue( self.window.doubleSpinBox_Tabs_MaxCutDepth.value() / 25.4 )

        if tabs_units == "mm":
            self.window.doubleSpinBox_Tabs_MaxCutDepth.setValue( self.window.doubleSpinBox_Tabs_MaxCutDepth.value() * 25.4 )
    
    def cb_update_tool_display(self):
        '''
        This updates the legends of the tool model widget **and** the values
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

            self.window.doubleSpinBox_Tool_Diameter.setValue( self.window.doubleSpinBox_Tool_Diameter.value() / 25.4 )
            self.window.doubleSpinBox_Tool_PassDepth.setValue( self.window.doubleSpinBox_Tool_PassDepth.value() / 25.4 )
            self.window.spinBox_Tool_Rapid.setValue( self.window.spinBox_Tool_Rapid.value() / 25.4 )
            self.window.spinBox_Tool_Plunge.setValue( self.window.spinBox_Tool_Plunge.value() / 25.4 )
            self.window.spinBox_Tool_Cut.setValue( self.window.spinBox_Tool_Cut.value() / 25.4 )

        if tool_units == "mm":
            self.window.label_Tool_Diameter_UnitsDescr.setText("mm")
            self.window.label_Tool_Angle_UnitsDescr.setText("degrees")
            self.window.label_Tool_PassDepth_UnitsDescr.setText("mm")
            self.window.label_Tool_StepOver_UnitsDescr.setText("]0:1]")
            self.window.label_Tool_Rapid_UnitsDescr.setText("mm/min")
            self.window.label_Tool_Plunge_UnitsDescr.setText("mm/min")
            self.window.label_Tool_Cut_UnitsDescr.setText("mm/min")

            self.window.doubleSpinBox_Tool_Diameter.setValue( self.window.doubleSpinBox_Tool_Diameter.value() * 25.4 )
            self.window.doubleSpinBox_Tool_PassDepth.setValue( self.window.doubleSpinBox_Tool_PassDepth.value() * 25.4 )
            self.window.spinBox_Tool_Rapid.setValue( self.window.spinBox_Tool_Rapid.value() * 25.4 )
            self.window.spinBox_Tool_Plunge.setValue( self.window.spinBox_Tool_Plunge.value() * 25.4 )
            self.window.spinBox_Tool_Cut.setValue( self.window.spinBox_Tool_Cut.value() * 25.4 )

    def cb_update_material_display(self):
        '''
        This updates the legends of the material model widget **and** the values
        '''
        material_units = self.window.comboBox_Material_Units.currentText()
        
        if material_units == "inch":
            self.window.doubleSpinBox_Material_Thickness.setValue( self.window.doubleSpinBox_Material_Thickness.value() / 25.4 )
            self.window.doubleSpinBox_Material_Clearance.setValue( self.window.doubleSpinBox_Material_Clearance.value() / 25.4 )

        if material_units == "mm":
            self.window.doubleSpinBox_Material_Thickness.setValue( self.window.doubleSpinBox_Material_Thickness.value() * 25.4 )
            self.window.doubleSpinBox_Material_Clearance.setValue( self.window.doubleSpinBox_Material_Clearance.value() * 25.4 )

    def cb_update_gcodeconversion_display(self):
        '''
        This updates the legends of the gcode_conversion model widget **and** the values
        '''
        gcodeconversion_units = self.window.comboBox_GCodeConversion_Units.currentText()
        
        if gcodeconversion_units == "inch":
            self.window.label_GCodeConversion_XOffset_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_YOffset_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_MinX_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_MaxX_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_MinY_UnitsDescr.setText("inch")
            self.window.label_GCodeConversion_MaxY_UnitsDescr.setText("inch")

            self.window.doubleSpinBox_GCodeConversion_XOffset.setValue( self.window.doubleSpinBox_GCodeConversion_XOffset.value() / 25.4 )
            self.window.doubleSpinBox_GCodeConversion_YOffset.setValue(self.window.doubleSpinBox_GCodeConversion_YOffset.value() / 25.4 )
            self.window.doubleSpinBox_GCodeConversion_MinX.setValue(self.window.doubleSpinBox_GCodeConversion_MinX.value() / 25.4 )
            self.window.doubleSpinBox_GCodeConversion_MaxX.setValue(self.window.doubleSpinBox_GCodeConversion_MaxX.value() / 25.4 )
            self.window.doubleSpinBox_GCodeConversion_MinY.setValue(self.window.doubleSpinBox_GCodeConversion_MinY.value() / 25.4 )
            self.window.doubleSpinBox_GCodeConversion_MaxY.setValue(self.window.doubleSpinBox_GCodeConversion_MaxY.value() / 25.4 )
            
        if gcodeconversion_units == "mm":
            self.window.label_GCodeConversion_XOffset_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_YOffset_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_MinX_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_MaxX_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_MinY_UnitsDescr.setText("mm")
            self.window.label_GCodeConversion_MaxY_UnitsDescr.setText("mm")

            self.window.doubleSpinBox_GCodeConversion_XOffset.setValue( self.window.doubleSpinBox_GCodeConversion_XOffset.value() * 25.4 )
            self.window.doubleSpinBox_GCodeConversion_YOffset.setValue(self.window.doubleSpinBox_GCodeConversion_YOffset.value() * 25.4 )
            self.window.doubleSpinBox_GCodeConversion_MinX.setValue(self.window.doubleSpinBox_GCodeConversion_MinX.value() * 25.4 )
            self.window.doubleSpinBox_GCodeConversion_MaxX.setValue(self.window.doubleSpinBox_GCodeConversion_MaxX.value() * 25.4 )
            self.window.doubleSpinBox_GCodeConversion_MinY.setValue(self.window.doubleSpinBox_GCodeConversion_MinY.value() * 25.4 )
            self.window.doubleSpinBox_GCodeConversion_MaxY.setValue(self.window.doubleSpinBox_GCodeConversion_MaxY.value() * 25.4 )
            
    def cb_display_material_thickness(self):
        '''
        svg display only in mm
        '''
        material_units = self.window.comboBox_Material_Units.currentText()

        thickness = ValWithUnit(self.window.doubleSpinBox_Material_Thickness.value(), material_units).toMm()
        clearance = ValWithUnit(self.window.doubleSpinBox_Material_Clearance.value(), material_units).toMm()

        self.svg_material_viewer.display_material(thickness=thickness, clearance=clearance)

    def cb_display_material_clearance(self):
        '''
        svg display only in mm
        '''
        material_units = self.window.comboBox_Material_Units.currentText()

        thickness = ValWithUnit(self.window.doubleSpinBox_Material_Thickness.value(), material_units).toMm()
        clearance = ValWithUnit(self.window.doubleSpinBox_Material_Clearance.value(), material_units).toMm()

        self.svg_material_viewer.display_material(thickness=thickness, clearance=clearance)

    def cb_spindle_automatic(self):
        val = self.window.checkBox_GCodeGeneration_SpindleAutomatic.isChecked()
        self.window.spinBox_GCodeGeneration_SpindleSpeed.setEnabled(val)

    def setup_material_viewer(self):
        '''
        '''
        return material_widget.MaterialWidget(self.window.widget_display_material)

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

    def display_cnc_ops_geometry(self, ops_model: List[Any]):
        '''
        '''
        settings = self.get_current_settings()

        toolModel = ToolModel() 
        toolModel.units = settings["Tool"]["Units"]
        toolModel.diameter = ValWithUnit(settings["Tool"]["Diameter"], toolModel.units)
        toolModel.angle = settings["Tool"]["Angle"]
        toolModel.passDepth = ValWithUnit(settings["Tool"]["PassDepth"], toolModel.units)
        toolModel.stepover = settings["Tool"]["StepOver"]
        toolModel.rapidRate = ValWithUnit(settings["Tool"]["Rapid"], toolModel.units)
        toolModel.plungeRate = ValWithUnit(settings["Tool"]["Plunge"], toolModel.units)
        toolModel.cutRate = ValWithUnit(settings["Tool"]["Cut"], toolModel.units)

        cnc_ops = []

        for op_model in ops_model:
            if not op_model.enabled:
                continue

            cnc_op = CncOp(
            {
                "Units": op_model.units,
                "Name": op_model.name,
                "paths": op_model.paths,
                "Combine": op_model.combinaison,
                "RampPlunge": op_model.ramp,
                "type": op_model.cam_op,
                "Direction": op_model.direction,
                "Deep": op_model.cutDepth,
                "Margin": op_model.margin,
                "Width": op_model.width,

                "enabled": op_model.enabled
            })

            cnc_ops.append(cnc_op)

        
        for cnc_op in cnc_ops:
            cnc_op.setup(self.svg_viewer)
            cnc_op.calculate_geometry(toolModel)

        self.svg_viewer.reinit()
        self.svg_viewer.display_job_geometry(cnc_ops)

    def get_jobmodel_operations(self):
        '''
        '''
        cnc_ops = []

        for op_model in self.window.operationsview_manager.get_model().operations:
            if not op_model.enabled:
                continue

            cnc_op = CncOp(
            {
                "Units": op_model.units,
                "Name": op_model.name,
                "paths": op_model.paths,
                "Combine": op_model.combinaison,
                "RampPlunge": op_model.ramp,
                "type": op_model.cam_op,
                "Direction": op_model.direction,
                "Deep": op_model.cutDepth,
                "Margin": op_model.margin,
                "Width": op_model.width,

                "enabled": op_model.enabled
            })

            cnc_ops.append(cnc_op)

        return cnc_ops

    def get_jobmodel(self) -> JobModel:
        '''
        '''
        settings = self.get_current_settings()

        svgModel = SvgModel()
        svgModel.pxPerInch = 96
        materialModel = MaterialModel()
        materialModel.matUnits = settings["Material"]["Units"]
        materialModel.matThickness = ValWithUnit(1.0, materialModel.matUnits)
        materialModel.matZOrigin = settings["Material"]["ZOrigin"]
        materialModel.matClearance = ValWithUnit(0.1, materialModel.matUnits)
        toolModel = ToolModel()
        toolModel.units = settings["Tool"]["Units"]
        toolModel.diameter = ValWithUnit(settings["Tool"]["Diameter"], toolModel.units)
        toolModel.angle = settings["Tool"]["Angle"]
        toolModel.passDepth = ValWithUnit(settings["Tool"]["PassDepth"], toolModel.units)
        toolModel.stepover = settings["Tool"]["StepOver"]
        toolModel.rapidRate = ValWithUnit(settings["Tool"]["Rapid"], toolModel.units)
        toolModel.plungeRate = ValWithUnit(settings["Tool"]["Plunge"], toolModel.units)
        toolModel.cutRate = ValWithUnit(settings["Tool"]["Cut"], toolModel.units)
        tabsmodel = TabsModel(svgModel, materialModel, None, None)
        gcodeModel = GcodeModel()
        gcodeModel.units = settings["GCodeConversion"]["Units"]
        gcodeModel.XOffset = settings["GCodeConversion"]["XOffset"]
        gcodeModel.YOffset = settings["GCodeConversion"]["YOffset"]
        gcodeModel.returnTo00 = settings["GCodeGeneration"]["ReturnToZeroAtEnd"]
        gcodeModel.spindleControl = settings["GCodeGeneration"]["SpindleAutomatic"]
        gcodeModel.spindleSpeed = settings["GCodeGeneration"]["SpindleSpeed"]

        cnc_ops = self.get_jobmodel_operations()

        job = JobModel(self.svg_viewer, cnc_ops, materialModel, svgModel, toolModel, tabsmodel, gcodeModel)

        return job  
        
    def cb_generate_g_code_zerolowerleft(self):
        '''
        '''
        job = self.get_jobmodel()

        for cnc_op in job.operations:
            cnc_op.setup(self.svg_viewer)
            cnc_op.calculate_geometry(job.toolModel)

        generator = GcodeGenerator(job)
        generator.generateGcode_zeroLowerLeft()

        self.after_gcode_generation(generator, job.operations)

    def cb_generate_g_code_zerocenter(self):
        '''
        '''
        job = self.get_jobmodel()

        for cnc_op in job.operations:
            cnc_op.setup(self.svg_viewer)
            cnc_op.calculate_geometry(job.toolModel)

        generator = GcodeGenerator(job)
        generator.generateGcode_zeroCenter()

        self.after_gcode_generation(generator, job.operations)

    def cb_generate_g_code(self):
        '''
        '''
        job = self.get_jobmodel()

        for cnc_op in job.operations:
            cnc_op.setup(self.svg_viewer)
            cnc_op.calculate_geometry(job.toolModel)

        generator = GcodeGenerator(job)
        generator.generateGcode()

        self.after_gcode_generation(generator, job.operations)

    def after_gcode_generation(self, generator, cnc_ops):
        # with the resulting calculation, we can fill the min/max in X/Y as well as the offsets
        self.window.doubleSpinBox_GCodeConversion_XOffset.setValue(generator.offsetX)
        self.window.doubleSpinBox_GCodeConversion_YOffset.setValue(generator.offsetY)
        self.window.doubleSpinBox_GCodeConversion_MinX.setValue(generator.minX)
        self.window.doubleSpinBox_GCodeConversion_MinY.setValue(generator.minY)
        self.window.doubleSpinBox_GCodeConversion_MaxX.setValue(generator.maxX)
        self.window.doubleSpinBox_GCodeConversion_MaxY.setValue(generator.maxY)

        gcode = generator.gcode
        self.display_gcode(gcode)

        self.svg_viewer.display_job(cnc_ops)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    pycut = PyCutMainWindow()
    pycut.show()
    sys.exit(app.exec())
