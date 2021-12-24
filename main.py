# This Python file uses the following encoding: utf-8

import sys
import os
import json

from typing import List

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6.QtUiTools import QUiLoader

from val_with_unit import ValWithUnit

import svgviewer
import gcodeviewer.widgets.glwidget_container as glwidget_container
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
from ui_mainwindow import Ui_mainwindow

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

        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)

        self.setWindowTitle("PyCut")
        self.setWindowIcon(QtGui.QIcon(":/images/tango/32x32/categories/applications-system.png"))

        # a job to keep the generated gcode in memory (and save it)
        self.job = None

        # open/read/write job settings
        self.jobfilename = None

        self.svg_viewer = self.setup_svg_viewer()
        self.svg_material_viewer = self.setup_material_viewer()
        self.webgl_viewer = self.setup_webgl_viewer()
        self.candle_viewer = self.setup_candle_viewer()

        self.ui.operationsview_manager.set_svg_viewer(self.svg_viewer)

        # callbacks
        self.ui.pushButton_SaveGcode.clicked.connect(self.cb_save_gcode)

        self.ui.actionOpenSvg.triggered.connect(self.cb_open_svg)
        self.ui.actionNewJob.triggered.connect(self.cb_new_job)
        self.ui.actionOpenJob.triggered.connect(self.cb_open_job)
        self.ui.actionSaveJobAs.triggered.connect(self.cb_save_job_as)
        self.ui.actionSaveJob.triggered.connect(self.cb_save_job)

        # display material thickness/clearance
        self.ui.doubleSpinBox_Material_Thickness.valueChanged.connect(self.cb_display_material_thickness)
        self.ui.doubleSpinBox_Material_Clearance.valueChanged.connect(self.cb_display_material_clearance)


        default_thickness = self.ui.doubleSpinBox_Material_Thickness.value()
        default_clearance = self.ui.doubleSpinBox_Material_Clearance.value()
        self.svg_material_viewer.display_material(thickness=default_thickness, clearance=default_clearance)
        
        self.display_svg(None)
        
        self.ui.comboBox_Tabs_Units.currentTextChanged.connect(self.cb_update_tabs_display)
        self.ui.comboBox_Tool_Units.currentTextChanged.connect(self.cb_update_tool_display)
        self.ui.comboBox_Material_Units.currentTextChanged.connect(self.cb_update_material_display)
        self.ui.comboBox_GCodeConversion_Units.currentTextChanged.connect(self.cb_update_gcodeconversion_display)

        self.ui.checkBox_GCodeGeneration_SpindleAutomatic.clicked.connect(self.cb_spindle_automatic)

        self.ui.pushButton_GCodeConversion_ZeroLowerLeft.clicked.connect(self.cb_generate_g_code_zerolowerleft)
        self.ui.pushButton_GCodeConversion_ZeroCenter.clicked.connect(self.cb_generate_g_code_zerocenter)

        self.ui.doubleSpinBox_GCodeConversion_XOffset.valueChanged.connect(self.cb_generate_g_code)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.valueChanged.connect(self.cb_generate_g_code)

        self.init_gui()

        self.open_job("./jobs/cnc_three_rects.json")
        #self.open_job("./jobs/cnc_three_rects_with_circle.json")
        #self.open_job("./jobs/cnc_one_rect.json")

    def cb_save_gcode(self):
        '''
        '''
        if self.job:
            gcode = self.job.gcode
            gcode = gcode.replace('\r\n', '\n')

            filename = "pycut_gcode.gcode"

            if os.path.exists(filename):
                k = 1
                filename = "pycut_gcode-%d.gcode" % k
                while os.path.exists(filename):
                    k += 1
                    filename = "pycut_gcode-%d.gcode" % k

            fp = open(filename, "w")
            fp.write(gcode)
            fp.close()
        
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

        self.candle_viewer.loadData(gcode.split("\r\n"))

    def load_ui(self, uifile):
        '''
        old method th load ui, not OK when a QMainWindow ui file
        has to be loaded, OK when simple widget.
        Kept here to remember how it works (quite well infact, and
        no need to generate an Ui_XXXX.py file)
        '''
        loader = QUiLoader(self)
        loader.registerCustomWidget(operations_tableview.PMFTableViewManager)
        
        widget = loader.load(uifile)

        return widget

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
                "Units"      : self.ui.comboBox_Tabs_Units.currentText(),
                "MaxCutDepth": self.ui.doubleSpinBox_Tabs_MaxCutDepth.value()
            },
            "Tool" : {
                "Units"      : self.ui.comboBox_Tool_Units.currentText(),
                "Diameter"   : self.ui.doubleSpinBox_Tool_Diameter.value(),
                "Angle"      : self.ui.spinBox_Tool_Angle.value(),
                "PassDepth"  : self.ui.doubleSpinBox_Tool_PassDepth.value(),
                "StepOver"   : self.ui.doubleSpinBox_Tool_StepOver.value(),
                "Rapid"      : self.ui.spinBox_Tool_Rapid.value(),
                "Plunge"     : self.ui.spinBox_Tool_Plunge.value(),
                "Cut"        : self.ui.spinBox_Tool_Cut.value()
            },
            "Material" : {
                "Units"      : self.ui.comboBox_Material_Units.currentText(),
                "Thickness"  : self.ui.doubleSpinBox_Material_Thickness.value(),
                "ZOrigin"    : self.ui.comboBox_Material_ZOrigin.currentText(),
                "Clearance"  : self.ui.doubleSpinBox_Material_Clearance.value(),
            },
            "CurveToLineConversion" : {
                "MinimumSegments"       : self.ui.doubleSpinBox_CurveToLineConversion_MinimumSegments.value(),
                "MinimumSegmentsLength" : self.ui.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.value(),
            },
            "GCodeConversion" : {
                "Units"           : self.ui.comboBox_GCodeConversion_Units.currentText(),
                "XOffset"         : self.ui.doubleSpinBox_GCodeConversion_XOffset.value(),
                "YOffset"         : self.ui.doubleSpinBox_GCodeConversion_YOffset.value()
            },
            "GCodeGeneration" : {
                "ReturnToZeroAtEnd" : self.ui.checkBox_GCodeGeneration_ReturnToZeroAtEnd.isChecked(),
                "SpindleAutomatic"  : self.ui.checkBox_GCodeGeneration_SpindleAutomatic.isChecked(),
                "SpindleSpeed"      : self.ui.spinBox_GCodeGeneration_SpindleSpeed.value(),
            }
        }
        
        return settings

    def apply_settings(self, settings):
        '''
        '''
        # Tabs
        self.ui.comboBox_Tabs_Units.setCurrentText(settings["Tabs"]["Units"])
        self.ui.doubleSpinBox_Tabs_MaxCutDepth.setValue(settings["Tabs"]["MaxCutDepth"])
            
        # Tool
        self.ui.comboBox_Tool_Units.setCurrentText(settings["Tool"]["Units"])
        self.ui.doubleSpinBox_Tool_Diameter.setValue(settings["Tool"]["Diameter"])
        self.ui.spinBox_Tool_Angle.setValue(settings["Tool"]["Angle"])
        self.ui.doubleSpinBox_Tool_PassDepth.setValue(settings["Tool"]["PassDepth"])
        self.ui.doubleSpinBox_Tool_StepOver.setValue(settings["Tool"]["StepOver"])
        self.ui.spinBox_Tool_Rapid.setValue(settings["Tool"]["Rapid"])
        self.ui.spinBox_Tool_Plunge.setValue(settings["Tool"]["Plunge"])
        self.ui.spinBox_Tool_Cut.setValue(settings["Tool"]["Cut"])
        
        # Material
        self.ui.comboBox_Material_Units.setCurrentText(settings["Material"]["Units"])
        self.ui.doubleSpinBox_Material_Thickness.setValue(settings["Material"]["Thickness"])
        self.ui.comboBox_Material_ZOrigin.setCurrentText(settings["Material"]["ZOrigin"])
        self.ui.doubleSpinBox_Material_Clearance.setValue(settings["Material"]["Clearance"])
            
        # CurveToLineConversion 
        self.ui.doubleSpinBox_CurveToLineConversion_MinimumSegments.setValue(settings["CurveToLineConversion"]["MinimumSegments"]),
        self.ui.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setValue(settings["CurveToLineConversion"]["MinimumSegmentsLength"]),
            
        # GCodeConversion
        self.ui.comboBox_GCodeConversion_Units.setCurrentText(settings["GCodeConversion"]["Units"])
        self.ui.doubleSpinBox_GCodeConversion_XOffset.setValue(settings["GCodeConversion"]["XOffset"])
        self.ui.doubleSpinBox_GCodeConversion_YOffset.setValue(settings["GCodeConversion"]["YOffset"])
            
        # GCodeGeneration 
        self.ui.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setChecked(settings["GCodeGeneration"]["ReturnToZeroAtEnd"]),
        self.ui.checkBox_GCodeGeneration_SpindleAutomatic.setChecked(settings["GCodeGeneration"]["SpindleAutomatic"]),
        self.ui.spinBox_GCodeGeneration_SpindleSpeed.setValue(settings["GCodeGeneration"]["SpindleSpeed"]),

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
 
    def cb_new_job(self):
        '''
        '''
        # clean current job (table)
        self.ui.operationsview_manager.set_operations([])

    def cb_open_job(self):
        '''
        '''
        # read json
        xfilter = "JSON Files (*.json)"
        jobfilename, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="open file", dir=".", filter=xfilter)
        
        self.open_job(jobfilename)
        
    def open_job(self, jobfilename):
        with open(jobfilename) as f:
            self.jobfilename = jobfilename

            job = json.load(f)
        
            self.svg_file = job["svg_file"]
            self.operations = job["operations"]
        
            # display
            self.display_svg(self.svg_file)
            
            # and fill the whole gui
            self.apply_settings(job["settings"])

            # fill operations table
            self.ui.operationsview_manager.set_operations(self.operations)
        
    def cb_save_job(self):
        '''
        '''
        operations = self.ui.operationsview_manager.get_operations()

        job = {
            "svg_file" : self.svg_file,
            "operations": operations,
            "settings": self.get_current_settings()
        }
        
        with open(self.jobfilename, 'w') as json_file:
            json.dump(job, json_file, indent=2)   

    def cb_save_job_as(self):
        '''
        '''
        xfilter = "JSON Files (*.json)"
        
        operations = self.ui.operationsview_manager.get_operations()

        job = {
            "svg_file" : self.svg_file,
            "operations": operations,
            "settings": self.get_current_settings()
        }
            
        # open file dialog for a file name
        jobfilename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="Save As", dir=".", filter=xfilter)

        with open(jobfilename, 'w') as json_file:
            json.dump(job, json_file, indent=2)

        self.jobfilename = jobfilename
    
    def cb_update_tabs_display(self):
        '''
        This updates the legends of the tsbs model widget **and** the values
        '''
        tabs_units = self.ui.comboBox_Tabs_Units.currentText()
        
        if tabs_units == "inch":
            self.ui.doubleSpinBox_Tabs_MaxCutDepth.setValue( self.ui.doubleSpinBox_Tabs_MaxCutDepth.value() / 25.4 )

        if tabs_units == "mm":
            self.ui.doubleSpinBox_Tabs_MaxCutDepth.setValue( self.ui.doubleSpinBox_Tabs_MaxCutDepth.value() * 25.4 )
    
    def cb_update_tool_display(self):
        '''
        This updates the legends of the tool model widget **and** the values
        '''
        tool_units = self.ui.comboBox_Tool_Units.currentText()
        
        if tool_units == "inch":
            self.ui.label_Tool_Diameter_UnitsDescr.setText("inch")
            self.ui.label_Tool_Angle_UnitsDescr.setText("degrees")
            self.ui.label_Tool_PassDepth_UnitsDescr.setText("inch")
            self.ui.label_Tool_StepOver_UnitsDescr.setText("]0:1]")
            self.ui.label_Tool_Rapid_UnitsDescr.setText("inch/min")
            self.ui.label_Tool_Plunge_UnitsDescr.setText("inch/min")
            self.ui.label_Tool_Cut_UnitsDescr.setText("inch/min")

            self.ui.doubleSpinBox_Tool_Diameter.setValue( self.ui.doubleSpinBox_Tool_Diameter.value() / 25.4 )
            self.ui.doubleSpinBox_Tool_PassDepth.setValue( self.ui.doubleSpinBox_Tool_PassDepth.value() / 25.4 )
            self.ui.spinBox_Tool_Rapid.setValue( self.ui.spinBox_Tool_Rapid.value() / 25.4 )
            self.ui.spinBox_Tool_Plunge.setValue( self.ui.spinBox_Tool_Plunge.value() / 25.4 )
            self.ui.spinBox_Tool_Cut.setValue( self.ui.spinBox_Tool_Cut.value() / 25.4 )

        if tool_units == "mm":
            self.ui.label_Tool_Diameter_UnitsDescr.setText("mm")
            self.ui.label_Tool_Angle_UnitsDescr.setText("degrees")
            self.ui.label_Tool_PassDepth_UnitsDescr.setText("mm")
            self.ui.label_Tool_StepOver_UnitsDescr.setText("]0:1]")
            self.ui.label_Tool_Rapid_UnitsDescr.setText("mm/min")
            self.ui.label_Tool_Plunge_UnitsDescr.setText("mm/min")
            self.ui.label_Tool_Cut_UnitsDescr.setText("mm/min")

            self.ui.doubleSpinBox_Tool_Diameter.setValue( self.ui.doubleSpinBox_Tool_Diameter.value() * 25.4 )
            self.ui.doubleSpinBox_Tool_PassDepth.setValue( self.ui.doubleSpinBox_Tool_PassDepth.value() * 25.4 )
            self.ui.spinBox_Tool_Rapid.setValue( self.ui.spinBox_Tool_Rapid.value() * 25.4 )
            self.ui.spinBox_Tool_Plunge.setValue( self.ui.spinBox_Tool_Plunge.value() * 25.4 )
            self.ui.spinBox_Tool_Cut.setValue( self.ui.spinBox_Tool_Cut.value() * 25.4 )

    def cb_update_material_display(self):
        '''
        This updates the legends of the material model widget **and** the values
        '''
        material_units = self.ui.comboBox_Material_Units.currentText()
        
        if material_units == "inch":
            self.ui.doubleSpinBox_Material_Thickness.setValue( self.ui.doubleSpinBox_Material_Thickness.value() / 25.4 )
            self.ui.doubleSpinBox_Material_Clearance.setValue( self.ui.doubleSpinBox_Material_Clearance.value() / 25.4 )

        if material_units == "mm":
            self.ui.doubleSpinBox_Material_Thickness.setValue( self.ui.doubleSpinBox_Material_Thickness.value() * 25.4 )
            self.ui.doubleSpinBox_Material_Clearance.setValue( self.ui.doubleSpinBox_Material_Clearance.value() * 25.4 )

    def cb_update_gcodeconversion_display(self):
        '''
        This updates the legends of the gcode_conversion model widget **and** the values
        '''
        gcodeconversion_units = self.ui.comboBox_GCodeConversion_Units.currentText()
        
        if gcodeconversion_units == "inch":
            self.ui.label_GCodeConversion_XOffset_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_YOffset_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_MinX_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_MaxX_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_MinY_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_MaxY_UnitsDescr.setText("inch")

            self.ui.doubleSpinBox_GCodeConversion_XOffset.setValue( self.ui.doubleSpinBox_GCodeConversion_XOffset.value() / 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_YOffset.setValue(self.ui.doubleSpinBox_GCodeConversion_YOffset.value() / 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_MinX.setValue(self.ui.doubleSpinBox_GCodeConversion_MinX.value() / 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_MaxX.setValue(self.ui.doubleSpinBox_GCodeConversion_MaxX.value() / 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_MinY.setValue(self.ui.doubleSpinBox_GCodeConversion_MinY.value() / 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_MaxY.setValue(self.ui.doubleSpinBox_GCodeConversion_MaxY.value() / 25.4 )
            
        if gcodeconversion_units == "mm":
            self.ui.label_GCodeConversion_XOffset_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_YOffset_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_MinX_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_MaxX_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_MinY_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_MaxY_UnitsDescr.setText("mm")

            self.ui.doubleSpinBox_GCodeConversion_XOffset.setValue( self.ui.doubleSpinBox_GCodeConversion_XOffset.value() * 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_YOffset.setValue(self.ui.doubleSpinBox_GCodeConversion_YOffset.value() * 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_MinX.setValue(self.ui.doubleSpinBox_GCodeConversion_MinX.value() * 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_MaxX.setValue(self.ui.doubleSpinBox_GCodeConversion_MaxX.value() * 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_MinY.setValue(self.ui.doubleSpinBox_GCodeConversion_MinY.value() * 25.4 )
            self.ui.doubleSpinBox_GCodeConversion_MaxY.setValue(self.ui.doubleSpinBox_GCodeConversion_MaxY.value() * 25.4 )
            
    def cb_display_material_thickness(self):
        '''
        svg display only in mm
        '''
        material_units = self.ui.comboBox_Material_Units.currentText()

        thickness = ValWithUnit(self.ui.doubleSpinBox_Material_Thickness.value(), material_units).toMm()
        clearance = ValWithUnit(self.ui.doubleSpinBox_Material_Clearance.value(), material_units).toMm()

        self.svg_material_viewer.display_material(thickness=thickness, clearance=clearance)

    def cb_display_material_clearance(self):
        '''
        svg display only in mm
        '''
        material_units = self.ui.comboBox_Material_Units.currentText()

        thickness = ValWithUnit(self.ui.doubleSpinBox_Material_Thickness.value(), material_units).toMm()
        clearance = ValWithUnit(self.ui.doubleSpinBox_Material_Clearance.value(), material_units).toMm()

        self.svg_material_viewer.display_material(thickness=thickness, clearance=clearance)

    def cb_spindle_automatic(self):
        val = self.ui.checkBox_GCodeGeneration_SpindleAutomatic.isChecked()
        self.ui.spinBox_GCodeGeneration_SpindleSpeed.setEnabled(val)

    def setup_material_viewer(self):
        '''
        '''
        return material_widget.MaterialWidget(self.ui.widget_display_material)

    def setup_svg_viewer(self):
        '''
        '''
        svg = self.ui.svg
        layout = svg.layout()
        
        svg_viewer = svgviewer.SvgViewer(svg)
        
        layout.addWidget(svg_viewer)
        layout.addStretch(0)
        
        return svg_viewer

    def setup_candle_viewer(self):
        '''
        '''
        viewer = self.ui.viewer
        layout = viewer.layout()
        
        candle_viewer = glwidget_container.GLWidgetContainer(viewer)

        layout.addWidget(candle_viewer)
        layout.stretch(1)
        
        return candle_viewer

    def setup_webgl_viewer(self):
        '''
        '''
        webgl = self.ui.simulator
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

    def display_cnc_ops_geometry(self, operations: List[operations_tableview.OpItem]):
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

        for op_model in operations:
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

    def get_jobmodel_operations(self) -> List[CncOp]:
        '''
        '''
        cnc_ops : List[CncOp] = []

        for op_model in self.ui.operationsview_manager.get_model_operations():
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
        materialModel.matThickness = ValWithUnit(settings["Material"]["Thickness"], materialModel.matUnits)
        materialModel.matZOrigin = settings["Material"]["ZOrigin"]
        materialModel.matClearance = ValWithUnit(settings["Material"]["Clearance"], materialModel.matUnits)
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
        self.job = job = self.get_jobmodel()

        for cnc_op in job.operations:
            cnc_op.setup(self.svg_viewer)
            cnc_op.calculate_geometry(job.toolModel)

        generator = GcodeGenerator(job)
        generator.generateGcode_zeroLowerLeft()

        self.after_gcode_generation(generator)

    def cb_generate_g_code_zerocenter(self):
        '''
        '''
        self.job = job = self.get_jobmodel()

        for cnc_op in job.operations:
            cnc_op.setup(self.svg_viewer)
            cnc_op.calculate_geometry(job.toolModel)

        generator = GcodeGenerator(job)
        generator.generateGcode_zeroCenter()

        self.after_gcode_generation(generator)

    def cb_generate_g_code(self):
        '''
        '''
        if self.ui.checkBox_GCodeConversion_ZeroLowerLeft_AsDefault.isChecked():
            self.cb_generate_g_code_zerolowerleft()
            return

        if self.ui.checkBox_GCodeConversion_ZeroCenter_AsDefault.isChecked():
            self.cb_generate_g_code_zerocenter()
            return

        self.job = job = self.get_jobmodel()

        for cnc_op in job.operations:
            cnc_op.setup(self.svg_viewer)

        generator = GcodeGenerator(job)
        generator.generateGcode()

        self.after_gcode_generation(generator)

    def after_gcode_generation(self, generator: GcodeGenerator):
        '''
        '''
        # with the resulting calculation, we can fill the min/max in X/Y as well as the offsets
        self.ui.doubleSpinBox_GCodeConversion_XOffset.setValue(generator.offsetX)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.setValue(generator.offsetY)
        self.ui.doubleSpinBox_GCodeConversion_MinX.setValue(generator.minX)
        self.ui.doubleSpinBox_GCodeConversion_MinY.setValue(generator.minY)
        self.ui.doubleSpinBox_GCodeConversion_MaxX.setValue(generator.maxX)
        self.ui.doubleSpinBox_GCodeConversion_MaxY.setValue(generator.maxY)

        gcode = generator.gcode
        self.display_gcode(gcode)

        self.svg_viewer.display_job(generator.job.operations)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    mainwindow = PyCutMainWindow()
    mainwindow.show()
    sys.exit(app.exec())
