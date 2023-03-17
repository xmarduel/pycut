# This Python file uses the following encoding: utf-8

VERSION = "0_3_8"

import sys
import os
import json
import argparse
import pathlib

from typing import List

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6.QtUiTools import QUiLoader

# TEST simulator with python
# from gcodesimulator.python.parser.gcodeminiparser import GcodeMiniParser
#import gcodesimulator.python.widgets.glwidget_container as glwidget_simulator_container

import shapely_svgpath_io

from val_with_unit import ValWithUnit

import svgviewer
import gcodeviewer.widgets.glwidget_container as glwidget_container
import gcodesimulator.webglviewer as webglviewer
import gcodesimulator.gcodefileviewer as gcodefileviewer

import operations_tableview
import tabs_tableview
import settings.colorpicker as colorpicker

import material_widget

from gcode_generator import GcodeModel
from gcode_generator import ToolModel
from gcode_generator import SvgModel
from gcode_generator import MaterialModel
from gcode_generator import TabsModel
from gcode_generator import CncOp
from gcode_generator import JobModel
from gcode_generator import Tab

from gcode_generator import GcodeGenerator

import resources_rc
from ui_mainwindow import Ui_mainwindow

class PyCutMainWindow(QtWidgets.QMainWindow):
    '''
    '''
    default_settings = {
        "svg": {
            "px_per_inch" : 96,
        },
        "Tabs": {
            "units"       : "mm",
            "height"      : 1.0,
            "tabs"        : []
        },
        "Tool" : {
            "Units"       : "mm",
            "Diameter"    : 1.0,
            "Angle"       : 180,
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
            "MinimumSegments"       : 5,
            "MinimumSegmentsLength" : 0.01,
        },
        "GCodeConversion" : {
            "Units"         : "mm",
            "FlipXY"        : False,
            "XOffset"       : 0.0,
            "YOffset"       : 0.0,
            "XYReference"   : "ZERO_TOP_LEFT_OF_MATERIAL"
        },
        "GCodeGeneration" : {
            "ReturnToZeroAtEnd" : True,
            "SpindleControl"    : True,
            "SpindleSpeed"      : 1000,
            "ProgramEnd"        : True 
        }
    }
    
    def __init__(self, options):
        '''
        '''
        super(PyCutMainWindow, self).__init__()

        self.recent_jobs = self.read_recent_jobs()

        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)

        self.setWindowTitle("PyCut")
        self.setWindowIcon(QtGui.QIcon(":/images/tango/32x32/categories/applications-system.png"))

        self.build_recent_jobs_submenu()

        self.operations = []
        self.tabs = []

        # a job to keep the generated gcode in memory (and save it)
        self.job = None

        # open/read/write job settings
        self.jobfilename = None

        self.webgl_viewer = None
        self.gcode_textviewer = None

        self.svg_viewer = self.setup_svg_viewer()
        self.svg_material_viewer = self.setup_material_viewer()
        self.webgl_viewer = self.setup_webgl_viewer()
        self.candle_viewer = self.setup_candle_viewer()

        self.ui.tabsview_manager.set_svg_viewer(self.svg_viewer)
        self.ui.operationsview_manager.set_svg_viewer(self.svg_viewer)

        # callbacks
        self.ui.pushButton_SaveGcode.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/document-save-as.png'))
        self.ui.pushButton_SaveGcode.clicked.connect(self.cb_save_gcode)

        self.ui.actionOpenSvg.triggered.connect(self.cb_open_svg)
        self.ui.actionNewJob.triggered.connect(self.cb_new_job)
        self.ui.actionOpenJob.triggered.connect(self.cb_open_job)
        self.ui.actionSaveJobAs.triggered.connect(self.cb_save_job_as)
        self.ui.actionSaveJob.triggered.connect(self.cb_save_job)

        self.ui.actionSettings.triggered.connect(self.cb_open_settings_dialog)

        self.ui.actionTutorial.triggered.connect(self.cb_show_tutorial)
        self.ui.actionAboutQt.triggered.connect(self.cb_show_about_qt)
        self.ui.actionAboutPyCut.triggered.connect(self.cb_show_about_pycut)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QtWidgets.QApplication.instance().aboutQt)

        # display material thickness/clearance
        self.ui.doubleSpinBox_Material_Thickness.valueChanged.connect(self.cb_display_material_thickness)
        self.ui.doubleSpinBox_Material_Clearance.valueChanged.connect(self.cb_display_material_clearance)


        default_thickness = self.ui.doubleSpinBox_Material_Thickness.value()
        default_clearance = self.ui.doubleSpinBox_Material_Clearance.value()
        self.svg_material_viewer.display_material(thickness=default_thickness, clearance=default_clearance)
        
        self.ui.spinBox_CurveToLineConversion_MinimumNbSegments.valueChanged.connect(self.cb_curve_min_segments)
        self.ui.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.valueChanged.connect(self.cb_curve_min_segments_length)

        self.display_svg(None)
        
        self.ui.comboBox_Tabs_Units.currentTextChanged.connect(self.cb_update_tabs_display)
        self.ui.comboBox_Tool_Units.currentTextChanged.connect(self.cb_update_tool_display)
        self.ui.comboBox_Material_Units.currentTextChanged.connect(self.cb_update_material_display)
        self.ui.comboBox_GCodeConversion_Units.currentTextChanged.connect(self.cb_update_gcodeconversion_display)

        self.ui.checkBox_GCodeGeneration_SpindleControl.clicked.connect(self.cb_spindle_control)

        self.ui.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.clicked.connect(self.cb_generate_gcode)
        self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.clicked.connect(self.cb_generate_gcode)
        self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfOp.clicked.connect(self.cb_generate_gcode)
        self.ui.pushButton_GCodeConversion_ZeroCenterOfOp.clicked.connect(self.cb_generate_gcode)


        self.ui.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/view-refresh.png'))
        self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/view-refresh.png'))
        self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfOp.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/view-refresh.png'))
        self.ui.pushButton_GCodeConversion_ZeroCenterOfOp.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/view-refresh.png'))

        self.ui.buttonGroup_GCodeConversion.setId(self.ui.pushButton_GCodeConversion_ZeroTopLeftOfMaterial, GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL)
        self.ui.buttonGroup_GCodeConversion.setId(self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial, GcodeModel.ZERO_LOWER_LEFT_OF_MATERIAL)
        self.ui.buttonGroup_GCodeConversion.setId(self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfOp, GcodeModel.ZERO_LOWER_LEFT_OF_OP)
        self.ui.buttonGroup_GCodeConversion.setId(self.ui.pushButton_GCodeConversion_ZeroCenterOfOp, GcodeModel.ZERO_CENTER_OF_OP)
        
        self.ui.checkBox_Tabs_hideAllTabs.clicked.connect(self.cb_tabs_hide_all)
        self.ui.checkBox_Tabs_hideDisabledTabs.clicked.connect(self.cb_tabs_hide_disabled)

        self.init_gui()

        if options.load_job is not None:
            if os.path.exists(options.load_job):
                self.open_job(options.load_job)
            else:
                # alert
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("PyCut")
                msgBox.setText("Job File %s not found" % options.load_job)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
                msgBox.exec()


        self.layoutToggleLeftSideAction = QtGui.QAction(QtGui.QIcon(":/images/left-area.png"), "hide/show",
                self, shortcut=QtGui.QKeySequence.Back,
                statusTip="Show/Hide Left Side", triggered=self.toggleLeftSide)
        self.layoutToggleLeftSideAction.setCheckable(True)
        self.layoutToggleLeftSideAction.setToolTip("Show/Hide Left Side View") # still not shown

        self.layoutToggleMiddleAreaAction = QtGui.QAction(QtGui.QIcon(":/images/bellow-area.png"), "hide/show",
                self, shortcut=QtGui.QKeySequence.Forward,
                statusTip="Show/Hide Op. Table", triggered=self.toggleMiddleArea)
        self.layoutToggleMiddleAreaAction.setCheckable(True)
        self.layoutToggleMiddleAreaAction.setToolTip("Show/Hide Op. Table View") # still not shown

        self.layoutToggleRightSideAction = QtGui.QAction(QtGui.QIcon(":/images/right-area.png"), "hide/show",
                self, shortcut=QtGui.QKeySequence.Forward,
                statusTip="Show/Hide Right Side", triggered=self.toggleRightSide)
        self.layoutToggleRightSideAction.setCheckable(True)
        self.layoutToggleRightSideAction.setToolTip("Show/Hide Right Side View") # still not shown

        self.menuBar().addAction(self.layoutToggleLeftSideAction)
        self.menuBar().addAction(self.layoutToggleMiddleAreaAction)
        self.menuBar().addAction(self.layoutToggleRightSideAction)
        

        #job_no = 4 # DEBUGGING SHORTCUT
        
        #if job_no == 1:
        #    self.open_job("./jobs/cnc_three_rects.json")
        #elif job_no == 2:
        #    self.open_job("./jobs/cnc_three_rects_with_circle.json")
        #elif job_no == 3:
        #    self.open_job("./jobs/cnc_all_letters.json")
        #elif job_no == 4:
        #    self.open_job("./jobs/cnc_control_panel.json")

        # these callbacks only after have loading a job
        self.ui.doubleSpinBox_GCodeConversion_XOffset.valueChanged.connect(self.cb_generate_gcode_x_offset)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.valueChanged.connect(self.cb_generate_gcode_y_offset)
        self.ui.checkBox_GCodeConversion_FlipXY.clicked.connect(self.cb_generate_gcode)


        self.setWindowState(QtCore.Qt.WindowMaximized)

    def toggleLeftSide(self):
        '''
        '''
        if self.layoutToggleLeftSideAction.isChecked():
            self.ui.scrollArea_left.hide()
        else:
            self.ui.scrollArea_left.show()

    def toggleMiddleArea(self):
        '''
        '''
        if self.layoutToggleMiddleAreaAction.isChecked():
            self.ui.operationsview_manager.hide()
        else:
            self.ui.operationsview_manager.show()

    def toggleRightSide(self):
        '''
        '''
        if self.layoutToggleRightSideAction.isChecked():
            self.ui.scrollArea_right.hide()
        else:
            self.ui.scrollArea_right.show()

    def cb_open_settings_dialog(self):
        '''
        '''
        global settings_dialog

        def fill_dialog():
            settings_dialog.colorpicker_Tabs_fill.setColor(QtGui.QColor(svgviewer.SvgViewer.TABS["fill"]))
            settings_dialog.doubleSpinBox_Tabs_fill_opacity.setValue(float(svgviewer.SvgViewer.TABS["fill-opacity"]))
            settings_dialog.doubleSpinBox_Tabs_fill_opacity_disabled.setValue(float(svgviewer.SvgViewer.TABS["fill-opacity-disabled"]))

            settings_dialog.colorpicker_Toolpath_stroke.setColor(QtGui.QColor(svgviewer.SvgViewer.TOOLPATHS["stroke"]))
            settings_dialog.doubleSpinBox_Toolpath_stroke_width.setValue(float(svgviewer.SvgViewer.TOOLPATHS["stroke-width"]))

            settings_dialog.colorpicker_GeometryPreview_fill.setColor(QtGui.QColor(svgviewer.SvgViewer.GEOMETRY_PREVIEW["fill"]))
            settings_dialog.doubleSpinBox_GeometryPreview_fill_opacity.setValue(float(svgviewer.SvgViewer.GEOMETRY_PREVIEW["fill-opacity"]))
        

        def setDefaults():
            self.svg_viewer.set_default_settings()
            fill_dialog()

        def setOK():
            settings = {
                "TABS" : {
                    "stroke": "#aa4488",
                    "stroke-width": "0",
                    "fill": settings_dialog.colorpicker_Tabs_fill.color().name(),
                    "fill-opacity": str(settings_dialog.doubleSpinBox_Tabs_fill_opacity.value()),
                    "fill-opacity-disabled": str(settings_dialog.doubleSpinBox_Tabs_fill_opacity_disabled.value()),
                },
                "GEOMETRY_PREVIEW" : {
                    "stroke": "#ff0000",
                    "stroke-width": "0",
                    "fill": settings_dialog.colorpicker_GeometryPreview_fill.color().name(),
                    "fill-opacity": str(settings_dialog.doubleSpinBox_GeometryPreview_fill_opacity.value()),
                },
                "TOOLPATHS" : {
                    "stroke": settings_dialog.colorpicker_Toolpath_stroke.color().name(),
                    "stroke-width": str(settings_dialog.doubleSpinBox_Toolpath_stroke_width.value()),
                }
            }
            self.svg_viewer.set_settings(settings)
            settings_dialog.close()

        def setCancel():
            settings_dialog.close()

        loader = QUiLoader(None)
        loader.registerCustomWidget(colorpicker.ColorPicker)

        settings_dialog = loader.load("./settings/settings.ui")
        fill_dialog()
        settings_dialog.cmdDefaults.clicked.connect(setDefaults)
        settings_dialog.cmdOK.clicked.connect(setOK)
        settings_dialog.cmdCancel.clicked.connect(setCancel)

        settings_dialog.exec()

    def cb_show_tutorial(self):
        dlg = QtWidgets.QDialog(self)

        view = QtWidgets.QTextBrowser(dlg)
        view.setReadOnly(True)
        view.setMinimumSize(800,500)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(view)

        dlg.setLayout(mainLayout)
        dlg.setWindowTitle("PyCut Tutorial")
        dlg.setModal(True)

        try:
            view.setSource(QtCore.QUrl.fromLocalFile(":/doc/tutorial.html"))
        except Exception as msg:
            view.setHtml(self.notfound % {'message':str(msg)})

        dlg.show()

    def cb_show_about_qt(self):
        QtWidgets.QApplication.instance().aboutQt()

    def cb_show_about_pycut(self):
        dlg = QtWidgets.QDialog(self)

        view = QtWidgets.QTextBrowser(dlg)
        view.setReadOnly(True)
        view.setMinimumSize(800,500)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(view)

        dlg.setLayout(mainLayout)
        dlg.setWindowTitle("PyCut Relnotes")
        dlg.setModal(True)

        try:
            view.setSource(QtCore.QUrl.fromLocalFile(":/doc/about.html"))
        except Exception as msg:
            view.setHtml(self.notfound % {'message':str(msg)})

        dlg.show()

    def cb_save_gcode(self):
        '''
        '''
        if self.job:
            jobname = os.path.basename(self.jobfilename)
            jobname = os.path.splitext(jobname)[0]

            opname = self.job.operations[0].name

            filename = "pycut_%s_%s.nc" % (jobname, opname)

            gcode = self.job.gcode
            gcode = gcode.replace('\r\n', '\n')

            if os.path.exists(filename):
                k = 1
                filename = "pycut_%s_%s_%d.nc" % (jobname, opname, k)
                while os.path.exists(filename):
                    k += 1
                    filename = "pycut_%s_%s_%d.nc" % (jobname, opname, k)

            fp = open(filename, "w")
            fp.write(gcode)
            fp.close()

            # status bar -> msg
            self.statusBar().showMessage("Saved GCode to \"%s\"" % filename, 3000)

    def display_gcode(self, gcode: str):
        '''
        display gcode in webgl!
        '''
        simulator_data =  {
            "gcode": gcode,
            "cutterHeight": 3 * 4.0,
            "cutterDiameter": self.ui.doubleSpinBox_Tool_Diameter.value(),
            "cutterAngle": self.ui.spinBox_Tool_Angle.value(),
        }
        
        self.webgl_viewer.set_data(simulator_data)
        self.webgl_viewer.show_gcode()

        self.gcode_textviewer.load_data(gcode)

        self.candle_viewer.loadData(gcode)

    def load_ui(self, uifile: str):
        '''
        old method th load ui, not OK when a QMainWindow ui file
        has to be loaded, OK when simple widget.
        Kept here to remember how it works (quite well infact, and
        no need to generate an Ui_XXXX.py file)
        '''
        loader = QUiLoader(self)
        loader.registerCustomWidget(operations_tableview.PyCutOperationsTableViewManager)
        loader.registerCustomWidget(tabs_tableview.PyCutTabsTableViewManager)
        
        widget = loader.load(uifile)

        return widget

    def init_gui(self):
        '''
        set the default settings in the gui 
        '''
        self.apply_settings(self.default_settings)

        #self.cb_update_tabs_display()
        #self.cb_update_tool_display()
        #self.cb_update_material_display()
        #self.cb_update_gcodeconversion_display()
    
    def get_current_settings(self):
        '''
        '''
        settings = {
            "svg": {
                "px_per_inch" : 96,
            }, 
            "Tabs": {
                "units"      : self.ui.comboBox_Tabs_Units.currentText(),
                "height"     : self.ui.doubleSpinBox_Tabs_Height.value(),
                "tabs"       : self.tabs
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
                "MinimumSegments"       : self.ui.spinBox_CurveToLineConversion_MinimumNbSegments.value(),
                "MinimumSegmentsLength" : self.ui.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.value(),
            },
            "GCodeConversion" : {
                "Units"           : self.ui.comboBox_GCodeConversion_Units.currentText(),
                "FlipXY"          : self.ui.checkBox_GCodeConversion_FlipXY.isChecked(),
                "XOffset"         : self.ui.doubleSpinBox_GCodeConversion_XOffset.value(),
                "YOffset"         : self.ui.doubleSpinBox_GCodeConversion_YOffset.value(),
                "XYReference"     : GcodeModel.XYRef[self.ui.buttonGroup_GCodeConversion.checkedId()]
            },
            "GCodeGeneration" : {
                "ReturnToZeroAtEnd" : self.ui.checkBox_GCodeGeneration_ReturnToZeroAtEnd.isChecked(),
                "SpindleControl"    : self.ui.checkBox_GCodeGeneration_SpindleControl.isChecked(),
                "SpindleSpeed"      : self.ui.spinBox_GCodeGeneration_SpindleSpeed.value(),
                "ProgramEnd"        : self.ui.checkBox_GCodeGeneration_ProgramEnd.isChecked(),
            }
        }
        
        return settings

    def apply_settings(self, settings):
        '''
        '''
        # Tabs
        self.ui.comboBox_Tabs_Units.setCurrentText(settings["Tabs"]["units"])
        self.ui.doubleSpinBox_Tabs_Height.setValue(settings["Tabs"]["height"])
            
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
        self.ui.spinBox_CurveToLineConversion_MinimumNbSegments.setValue(settings["CurveToLineConversion"]["MinimumSegments"]),
        self.ui.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setValue(settings["CurveToLineConversion"]["MinimumSegmentsLength"]),
            
        # GCodeConversion
        self.ui.comboBox_GCodeConversion_Units.setCurrentText(settings["GCodeConversion"]["Units"])
        self.ui.checkBox_GCodeConversion_FlipXY.setChecked(settings["GCodeConversion"]["FlipXY"])
        self.ui.doubleSpinBox_GCodeConversion_XOffset.setValue(settings["GCodeConversion"]["XOffset"])
        self.ui.doubleSpinBox_GCodeConversion_YOffset.setValue(settings["GCodeConversion"]["YOffset"])
            
        if settings["GCodeConversion"]["XYReference"] == "ZERO_TOP_LEFT_OF_MATERIAL":
            self.ui.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.setChecked(True)
        elif settings["GCodeConversion"]["XYReference"] == "ZERO_LOWER_LEFT_OF_MATERIAL":
            self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setChecked(True)
        elif settings["GCodeConversion"]["XYReference"] == "ZERO_LOWER_LEFT_OF_OP":
            self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfOp.setChecked(True)
        elif settings["GCodeConversion"]["XYReference"] == "ZERO_CENTER_OF_OP":
            self.ui.pushButton_GCodeConversion_ZeroCenterOfOp.setChecked(True)

        # GCodeGeneration 
        self.ui.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setChecked(settings["GCodeGeneration"]["ReturnToZeroAtEnd"])
        self.ui.checkBox_GCodeGeneration_SpindleControl.setChecked(settings["GCodeGeneration"]["SpindleControl"])
        self.ui.spinBox_GCodeGeneration_SpindleSpeed.setValue(settings["GCodeGeneration"]["SpindleSpeed"])
        self.ui.checkBox_GCodeGeneration_ProgramEnd.setChecked(settings["GCodeGeneration"]["ProgramEnd"])

    def cb_open_svg(self):
        '''
        not a job, a svg only -> no operations
        '''
        xfilter = "SVG Files (*.svg)"
        svg_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="open file", dir=".", filter=xfilter)

        if svg_file:
            svg_file = self.minify_path(svg_file)

            self.svg_file = svg_file
            
            # clean current job (table)
            self.operations = []
            self.ui.operationsview_manager.set_operations(self.operations)

            # clean current tabs (table)
            self.tabs = []
            self.ui.tabsview_manager.set_tabs(self.tabs)
            
            self.display_svg(self.svg_file)
 
    def cb_new_job(self):
        '''
        '''
        self.svg_file = None
        self.display_svg(self.svg_file)

        # clean current job (operations table)
        self.operations = []
        self.ui.operationsview_manager.set_operations(self.operations)

        # clean current job (tabs table)
        self.tabs = []
        self.ui.tabsview_manager.set_tabs(self.tabs)

    def cb_open_recent_job_file(self):
        '''
        '''
        sender = self.sender()
        jobfilename = sender.text()

        self.ui.doubleSpinBox_GCodeConversion_XOffset.valueChanged.disconnect(self.cb_generate_gcode_x_offset)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.valueChanged.disconnect(self.cb_generate_gcode_y_offset)
        self.ui.checkBox_GCodeConversion_FlipXY.clicked.disconnect(self.cb_generate_gcode)

        self.open_job(jobfilename)
        
        self.ui.doubleSpinBox_GCodeConversion_XOffset.valueChanged.connect(self.cb_generate_gcode_x_offset)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.valueChanged.connect(self.cb_generate_gcode_y_offset)
        self.ui.checkBox_GCodeConversion_FlipXY.clicked.connect(self.cb_generate_gcode)

    def cb_open_job(self):
        '''
        '''
        # read json
        xfilter = "JSON Files (*.json)"
        jobfilename, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="open file", dir=".", filter=xfilter)

        jobfilename = self.minify_path(jobfilename)
        
        self.ui.doubleSpinBox_GCodeConversion_XOffset.valueChanged.disconnect(self.cb_generate_gcode_x_offset)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.valueChanged.disconnect(self.cb_generate_gcode_y_offset)
        self.ui.checkBox_GCodeConversion_FlipXY.clicked.disconnect(self.cb_generate_gcode)

        self.open_job(jobfilename)

        self.prepend_recent_jobs(jobfilename)
        
        self.ui.doubleSpinBox_GCodeConversion_XOffset.valueChanged.connect(self.cb_generate_gcode_x_offset)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.valueChanged.connect(self.cb_generate_gcode_y_offset)
        self.ui.checkBox_GCodeConversion_FlipXY.clicked.connect(self.cb_generate_gcode)

    def open_job(self, jobfilename: str):
        with open(jobfilename) as f:
            self.jobfilename = jobfilename

            job = json.load(f)
        
            self.svg_file = job["svg_file"]
            self.operations = job["operations"]
            self.tabs = job["settings"]["Tabs"].get("tabs", [])
        
            # display
            self.display_svg(self.svg_file)
            
            # and fill the whole gui
            self.apply_settings(job["settings"])

            # fill operations table
            self.ui.operationsview_manager.set_operations(self.operations)

            # fill tabs table
            self.ui.tabsview_manager.set_tabs(self.tabs)
        
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

        if jobfilename:
            jobfilename = self.minify_path(jobfilename)

            with open(jobfilename, 'w') as json_file:
                json.dump(job, json_file, indent=2)

            self.jobfilename = jobfilename
    
    def cb_curve_min_segments(self):
        '''
        what is it good for ?
        seems to be redundant with cb_curve_min_segments_length
        '''
        value = self.ui.spinBox_CurveToLineConversion_MinimumNbSegments.value()
        shapely_svgpath_io.SvgPath.set_arc_min_nb_segments(value)

    def cb_curve_min_segments_length(self):
        '''
        '''
        value = self.ui.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.value()
        shapely_svgpath_io.SvgPath.set_arc_precision(value)

    def cb_update_tabs_display(self):
        '''
        This updates the legends of the tsbs model widget **and** the values
        '''
        tabs_units = self.ui.comboBox_Tabs_Units.currentText()
        
        if tabs_units == "inch":
            self.ui.doubleSpinBox_Tabs_Height.setValue( self.ui.doubleSpinBox_Tabs_Height.value() / 25.4 )
            self.ui.doubleSpinBox_Tabs_Height.setSingleStep(0.04)

        if tabs_units == "mm":
            self.ui.doubleSpinBox_Tabs_Height.setValue( self.ui.doubleSpinBox_Tabs_Height.value() * 25.4 )
            self.ui.doubleSpinBox_Tabs_Height.setSingleStep(1.0)

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

            self.ui.doubleSpinBox_Material_Thickness.setSingleStep(0.04)
            self.ui.doubleSpinBox_Material_Clearance.setSingleStep(0.04)

        if material_units == "mm":
            self.ui.doubleSpinBox_Material_Thickness.setValue( self.ui.doubleSpinBox_Material_Thickness.value() * 25.4 )
            self.ui.doubleSpinBox_Material_Clearance.setValue( self.ui.doubleSpinBox_Material_Clearance.value() * 25.4 )

            self.ui.doubleSpinBox_Material_Thickness.setSingleStep(1.0)
            self.ui.doubleSpinBox_Material_Clearance.setSingleStep(1.0)

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

        self.svg_material_viewer.display_unit(material_units)
        self.svg_material_viewer.display_material(thickness=thickness, clearance=clearance)

    def cb_display_material_clearance(self):
        '''
        svg display only in mm
        '''
        material_units = self.ui.comboBox_Material_Units.currentText()

        thickness = ValWithUnit(self.ui.doubleSpinBox_Material_Thickness.value(), material_units).toMm()
        clearance = ValWithUnit(self.ui.doubleSpinBox_Material_Clearance.value(), material_units).toMm()

        self.svg_material_viewer.display_material(thickness=thickness, clearance=clearance)

    def cb_spindle_control(self):
        val = self.ui.checkBox_GCodeGeneration_SpindleControl.isChecked()
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
        svg_viewer.set_mainwindow(self)
        
        layout.addWidget(svg_viewer)
        layout.setStretch(0, 1)
        
        return svg_viewer

    def setup_candle_viewer(self):
        '''
        '''
        viewer = self.ui.viewer
        layout = viewer.layout()
        
        candle_viewer = glwidget_container.GLWidgetContainer(viewer)

        layout.addWidget(candle_viewer)
        layout.setStretch(0, 1)
        
        return candle_viewer

    def setup_webgl_viewer(self):
        '''
        '''
        simulator = self.ui.simulator
        layout = simulator.layout()
        
        self.webgl_viewer = webglviewer.WebGlViewer(simulator)
        self.gcode_textviewer = gcodefileviewer.GCodeFileViewer(simulator, self.webgl_viewer)

        self.webgl_viewer.simtime_received_from_js.connect(self.gcode_textviewer.on_simtime_from_js)

        layout.addWidget(self.webgl_viewer)
        layout.addWidget(self.gcode_textviewer)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)
        
        return self.webgl_viewer

    def display_svg(self, svg):
        '''
        '''
        self.svg_viewer.clean()

        if svg is None:
            
            svg = '''<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"
                width="100mm"
                height="100mm"
                viewBox="0 0 100 100"
                version="1.1">
                <g id="text" style="font-style:normal;font-weight:normal;font-size:10.5833px;line-height:1.25;font-family:sans-serif;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.264583">
        <path
          d="m 26.769591,31.043861 q 0.470254,0.516763 0.7183,1.266069 0.253214,0.749306 0.253214,1.700149 0,0.950844 -0.258381,1.705317 -0.253214,0.749306 -0.713133,1.250566 -0.475422,0.52193 -1.126543,0.785479 -0.645953,0.263549 -1.477941,0.263549 -0.811317,0 -1.477941,-0.268717 -0.661456,-0.268716 -1.126543,-0.780311 -0.465086,-0.511595 -0.7183,-1.255734 -0.248046,-0.744138 -0.248046,-1.700149 0,-0.940508 0.248046,-1.684646 0.248046,-0.749306 0.723468,-1.281572 0.454751,-0.506427 1.126543,-0.775144 0.676959,-0.268716 1.472773,-0.268716 0.82682,0 1.483109,0.273884 0.661456,0.268717 1.121375,0.769976 z m -0.09302,2.966218 q 0,-1.498612 -0.671792,-2.309929 -0.671791,-0.816485 -1.834507,-0.816485 -1.173051,0 -1.844843,0.816485 -0.666624,0.811317 -0.666624,2.309929 0,1.514115 0.682127,2.320265 0.682127,0.800982 1.82934,0.800982 1.147213,0 1.824172,-0.800982 0.682127,-0.80615 0.682127,-2.320265 z"
          style="stroke-width:0.264583"
          id="pycut_path45" />
        <path
          d="m 34.366003,34.898911 q 0,0.702797 -0.201538,1.286739 -0.201537,0.578774 -0.568439,0.981849 -0.341063,0.382405 -0.80615,0.594277 -0.459918,0.206705 -0.976681,0.206705 -0.449584,0 -0.816485,-0.09818 -0.361734,-0.09818 -0.738971,-0.30489 v 2.41845 h -0.971514 v -7.901302 h 0.971514 v 0.604613 q 0.387572,-0.325561 0.868162,-0.542601 0.485757,-0.222208 1.033525,-0.222208 1.043861,0 1.622635,0.790647 0.583942,0.785479 0.583942,2.185906 z m -1.00252,0.02584 q 0,-1.04386 -0.356566,-1.560623 -0.356567,-0.516763 -1.095537,-0.516763 -0.418578,0 -0.842323,0.180867 -0.423746,0.180867 -0.811318,0.475422 v 3.271108 q 0.41341,0.186034 0.707965,0.253213 0.299723,0.06718 0.676959,0.06718 0.811318,0 1.266069,-0.547768 0.454751,-0.547768 0.454751,-1.622635 z"
          style="stroke-width:0.264583"
          id="pycut_path47" />
        <path
          d="m 40.711849,35.069443 h -4.252957 q 0,0.532265 0.160196,0.930173 0.160197,0.392739 0.439248,0.645953 0.268717,0.248046 0.635619,0.372069 0.372069,0.124023 0.816485,0.124023 0.589109,0 1.183386,-0.232543 0.599445,-0.237711 0.852659,-0.465087 h 0.05168 v 1.059364 q -0.490925,0.206705 -1.00252,0.346231 -0.511595,0.139526 -1.074866,0.139526 -1.4366,0 -2.24275,-0.775144 -0.80615,-0.780312 -0.80615,-2.211744 0,-1.41593 0.769976,-2.247918 0.775144,-0.831988 2.036045,-0.831988 1.167884,0 1.798334,0.682127 0.635619,0.682126 0.635619,1.93786 z m -0.945676,-0.744139 q -0.0052,-0.764808 -0.387572,-1.183386 -0.377237,-0.418578 -1.152381,-0.418578 -0.780312,0 -1.245398,0.459919 -0.459919,0.459919 -0.52193,1.142045 z"
          style="stroke-width:0.264583"
          id="pycut_path49" />
        <path
          d="m 47.011185,37.854794 h -0.971513 v -3.286611 q 0,-0.397907 -0.04651,-0.744138 -0.04651,-0.351399 -0.170532,-0.547769 -0.12919,-0.21704 -0.372069,-0.320393 -0.242878,-0.10852 -0.63045,-0.10852 -0.397908,0 -0.831988,0.19637 -0.434081,0.19637 -0.831988,0.50126 v 4.309801 h -0.971514 v -5.77224 h 0.971514 v 0.640786 q 0.454751,-0.377237 0.940508,-0.589109 0.485757,-0.211873 0.997352,-0.211873 0.93534,0 1.426265,0.563271 0.490924,0.563272 0.490924,1.622635 z"
          style="stroke-width:0.264583"
          id="pycut_path51" />
        <path
          d="M 57.088056,37.854794 H 56.12171 v -0.614948 q -0.12919,0.08785 -0.351398,0.248046 -0.217041,0.155029 -0.423746,0.248046 -0.242878,0.118856 -0.558104,0.19637 -0.315225,0.08268 -0.73897,0.08268 -0.780312,0 -1.322913,-0.516763 -0.5426,-0.516762 -0.5426,-1.317745 0,-0.656288 0.279051,-1.059363 0.28422,-0.408243 0.80615,-0.640786 0.527098,-0.232543 1.266069,-0.315225 0.73897,-0.08268 1.586461,-0.124023 v -0.149861 q 0,-0.330728 -0.118855,-0.547769 -0.113688,-0.21704 -0.330728,-0.341063 -0.206705,-0.118855 -0.496093,-0.160196 -0.289387,-0.04134 -0.604612,-0.04134 -0.382404,0 -0.852658,0.103352 -0.470254,0.09819 -0.971514,0.289387 h -0.05168 v -0.987017 q 0.284219,-0.07751 0.821652,-0.170531 0.537433,-0.09302 1.059364,-0.09302 0.60978,0 1.059363,0.103352 0.454751,0.09819 0.78548,0.341063 0.32556,0.237711 0.496092,0.614948 0.170531,0.377237 0.170531,0.93534 z M 56.12171,36.433696 v -1.607132 q -0.444416,0.02584 -1.049028,0.07752 -0.599445,0.05168 -0.950843,0.149861 -0.418578,0.118855 -0.676959,0.372069 -0.258382,0.248046 -0.258382,0.687294 0,0.496092 0.299723,0.749306 0.299722,0.248046 0.914669,0.248046 0.511596,0 0.935341,-0.19637 0.423745,-0.201537 0.785479,-0.480589 z"
          style="stroke-width:0.264583"
          id="pycut_path53" />
        <path
          d="m 68.348317,35.658552 q 0,0.449584 -0.211873,0.888832 -0.206705,0.439248 -0.583942,0.744138 -0.41341,0.330728 -0.966346,0.516763 -0.547768,0.186034 -1.322912,0.186034 -0.831988,0 -1.498612,-0.155028 -0.661456,-0.155029 -1.348751,-0.459919 V 36.0978 h 0.07235 q 0.583942,0.485757 1.348751,0.749306 0.764808,0.263549 1.4366,0.263549 0.950843,0 1.477941,-0.356566 0.532266,-0.356566 0.532266,-0.950843 0,-0.511595 -0.253214,-0.754474 -0.248046,-0.242878 -0.759641,-0.377237 -0.387572,-0.103352 -0.842323,-0.170531 -0.449584,-0.06718 -0.956011,-0.170532 -1.02319,-0.21704 -1.519283,-0.738971 -0.490924,-0.527097 -0.490924,-1.369421 0,-0.966346 0.816485,-1.581293 0.816485,-0.620116 2.072218,-0.620116 0.811318,0 1.488277,0.155029 0.676959,0.155029 1.198889,0.382405 v 1.209224 h -0.07235 q -0.439248,-0.372069 -1.157548,-0.614947 -0.713133,-0.248046 -1.462438,-0.248046 -0.821653,0 -1.322913,0.341063 -0.496092,0.341063 -0.496092,0.878496 0,0.48059 0.248046,0.754474 0.248046,0.273884 0.873329,0.418578 0.330728,0.07235 0.940508,0.175699 0.60978,0.103353 1.033525,0.211873 0.857826,0.227375 1.291907,0.687294 0.434081,0.459919 0.434081,1.286739 z"
          style="stroke-width:0.264583"
          id="pycut_path55" />
        <path
          d="m 76.058415,30.160197 -2.800854,7.694597 h -1.364253 l -2.800854,-7.694597 h 1.095537 l 2.413281,6.769591 2.413282,-6.769591 z"
          style="stroke-width:0.264583"
          id="pycut_path57" />
        <path
          d="m 83.64449,37.286355 q -0.630451,0.289387 -1.379757,0.506427 -0.744138,0.211873 -1.441767,0.211873 -0.899168,0 -1.648473,-0.248046 -0.749306,-0.248046 -1.276404,-0.744139 -0.532266,-0.501259 -0.821653,-1.250565 -0.289387,-0.754474 -0.289387,-1.762161 0,-1.844843 1.074866,-2.909374 1.080034,-1.069699 2.961051,-1.069699 0.656288,0 1.338415,0.160197 0.687294,0.155029 1.477941,0.532265 v 1.214393 h -0.09302 Q 83.386108,31.803503 83.081218,31.601965 82.776328,31.400428 82.481774,31.266069 82.125207,31.105873 81.670456,31.00252 81.220873,30.894 80.647266,30.894 q -1.291907,0 -2.04638,0.831988 -0.749306,0.82682 -0.749306,2.24275 0,1.493444 0.785479,2.325432 0.78548,0.826821 2.139398,0.826821 0.496092,0 0.987017,-0.09818 0.496092,-0.09819 0.868161,-0.253214 v -1.886184 h -2.061883 v -0.899167 h 3.074738 z"
          style="stroke-width:0.264583"
          id="pycut_path59" />
        <path
          d="m 51.92043,48.200382 q 0,1.410762 -0.723468,2.227247 -0.723468,0.816486 -1.93786,0.816486 -1.224728,0 -1.948195,-0.816486 -0.718301,-0.816485 -0.718301,-2.227247 0,-1.410762 0.718301,-2.227247 0.723467,-0.821652 1.948195,-0.821652 1.214392,0 1.93786,0.821652 0.723468,0.816485 0.723468,2.227247 z m -1.00252,0 q 0,-1.121375 -0.439248,-1.663975 -0.439249,-0.547769 -1.21956,-0.547769 -0.790647,0 -1.229895,0.547769 -0.434081,0.5426 -0.434081,1.663975 0,1.085202 0.439248,1.648473 0.439249,0.558104 1.224728,0.558104 0.775144,0 1.214392,-0.552936 0.444416,-0.558104 0.444416,-1.653641 z"
          style="stroke-width:0.264583"
          id="pycut_path61" />
        <path
          d="m 57.026044,46.371042 h -0.05168 q -0.21704,-0.05168 -0.423745,-0.07235 -0.201537,-0.02584 -0.480589,-0.02584 -0.449584,0 -0.868162,0.201537 -0.418577,0.19637 -0.806149,0.511595 v 4.097928 h -0.971514 v -5.772239 h 0.971514 v 0.852658 q 0.578774,-0.465086 1.018022,-0.656288 0.444416,-0.19637 0.904335,-0.19637 0.253214,0 0.366901,0.0155 0.113688,0.01033 0.341064,0.04651 z"
          style="stroke-width:0.264583"
          id="pycut_path63" />
        <path
          d="m 26.769591,57.502111 q 0.470254,0.516762 0.7183,1.266068 0.253214,0.749306 0.253214,1.700149 0,0.950844 -0.258381,1.705317 -0.253214,0.749306 -0.713133,1.250566 -0.475422,0.52193 -1.126543,0.785479 -0.645953,0.263549 -1.477941,0.263549 -0.811317,0 -1.477941,-0.268717 -0.661456,-0.268716 -1.126543,-0.780311 -0.465086,-0.511595 -0.7183,-1.255733 -0.248046,-0.744139 -0.248046,-1.70015 0,-0.940508 0.248046,-1.684646 0.248046,-0.749306 0.723468,-1.281571 0.454751,-0.506428 1.126543,-0.775144 0.676959,-0.268717 1.472773,-0.268717 0.82682,0 1.483109,0.273884 0.661456,0.268717 1.121375,0.769977 z m -0.09302,2.966217 q 0,-1.498611 -0.671792,-2.309929 -0.671791,-0.816485 -1.834507,-0.816485 -1.173051,0 -1.844843,0.816485 -0.666624,0.811318 -0.666624,2.309929 0,1.514115 0.682127,2.320265 0.682127,0.800982 1.82934,0.800982 1.147213,0 1.824172,-0.800982 0.682127,-0.80615 0.682127,-2.320265 z"
          style="stroke-width:0.264583"
          id="path65" />
        <path
          d="m 34.366003,61.35716 q 0,0.702797 -0.201538,1.286739 -0.201537,0.578774 -0.568439,0.981849 -0.341063,0.382405 -0.80615,0.594277 -0.459918,0.206705 -0.976681,0.206705 -0.449584,0 -0.816485,-0.09818 -0.361734,-0.09819 -0.738971,-0.30489 v 2.418449 h -0.971514 v -7.901301 h 0.971514 v 0.604612 q 0.387572,-0.325561 0.868162,-0.542601 0.485757,-0.222208 1.033525,-0.222208 1.043861,0 1.622635,0.790647 0.583942,0.785479 0.583942,2.185906 z m -1.00252,0.02584 q 0,-1.04386 -0.356566,-1.560623 -0.356567,-0.516763 -1.095537,-0.516763 -0.418578,0 -0.842323,0.180867 -0.423746,0.180867 -0.811318,0.475422 v 3.271108 q 0.41341,0.186034 0.707965,0.253213 0.299723,0.06718 0.676959,0.06718 0.811318,0 1.266069,-0.547769 0.454751,-0.547768 0.454751,-1.622635 z"
          style="stroke-width:0.264583"
          id="pycut_path67" />
        <path
          d="m 40.711849,61.527692 h -4.252957 q 0,0.532265 0.160196,0.930173 0.160197,0.392739 0.439248,0.645953 0.268717,0.248046 0.635619,0.372069 0.372069,0.124023 0.816485,0.124023 0.589109,0 1.183386,-0.232543 0.599445,-0.237711 0.852659,-0.465086 h 0.05168 v 1.059363 q -0.490925,0.206705 -1.00252,0.346231 -0.511595,0.139526 -1.074866,0.139526 -1.4366,0 -2.24275,-0.775144 -0.80615,-0.780312 -0.80615,-2.211744 0,-1.41593 0.769976,-2.247918 0.775144,-0.831988 2.036045,-0.831988 1.167884,0 1.798334,0.682127 0.635619,0.682127 0.635619,1.93786 z m -0.945676,-0.744138 q -0.0052,-0.764809 -0.387572,-1.183387 -0.377237,-0.418578 -1.152381,-0.418578 -0.780312,0 -1.245398,0.459919 -0.459919,0.459919 -0.52193,1.142046 z"
          style="stroke-width:0.264583"
          id="pycut_path69" />
        <path
          d="m 47.011185,64.313043 h -0.971513 v -3.286611 q 0,-0.397907 -0.04651,-0.744138 -0.04651,-0.351399 -0.170532,-0.547769 -0.12919,-0.21704 -0.372069,-0.320393 -0.242878,-0.10852 -0.63045,-0.10852 -0.397908,0 -0.831988,0.19637 -0.434081,0.19637 -0.831988,0.50126 v 4.309801 h -0.971514 v -5.772239 h 0.971514 v 0.640785 q 0.454751,-0.377237 0.940508,-0.589109 0.485757,-0.211873 0.997352,-0.211873 0.93534,0 1.426265,0.563271 0.490924,0.563272 0.490924,1.622635 z"
          style="stroke-width:0.264583"
          id="pycut_path71" />
        <path
          d="M 57.088056,64.313043 H 56.12171 v -0.614948 q -0.12919,0.08785 -0.351398,0.248046 -0.217041,0.155029 -0.423746,0.248046 -0.242878,0.118856 -0.558104,0.19637 -0.315225,0.08268 -0.73897,0.08268 -0.780312,0 -1.322913,-0.516763 -0.5426,-0.516762 -0.5426,-1.317744 0,-0.656289 0.279051,-1.059364 0.28422,-0.408242 0.80615,-0.640786 0.527098,-0.232543 1.266069,-0.315225 0.73897,-0.08268 1.586461,-0.124023 v -0.149861 q 0,-0.330728 -0.118855,-0.547769 -0.113688,-0.21704 -0.330728,-0.341063 -0.206705,-0.118855 -0.496093,-0.160196 -0.289387,-0.04134 -0.604612,-0.04134 -0.382404,0 -0.852658,0.103352 -0.470254,0.09819 -0.971514,0.289387 h -0.05168 v -0.987016 q 0.284219,-0.07752 0.821652,-0.170532 0.537433,-0.09302 1.059364,-0.09302 0.60978,0 1.059363,0.103352 0.454751,0.09819 0.78548,0.341064 0.32556,0.23771 0.496092,0.614947 0.170531,0.377237 0.170531,0.935341 z M 56.12171,62.891945 v -1.607132 q -0.444416,0.02584 -1.049028,0.07751 -0.599445,0.05168 -0.950843,0.149861 -0.418578,0.118855 -0.676959,0.372069 -0.258382,0.248046 -0.258382,0.687294 0,0.496093 0.299723,0.749306 0.299722,0.248046 0.914669,0.248046 0.511596,0 0.935341,-0.196369 0.423745,-0.201538 0.785479,-0.48059 z"
          style="stroke-width:0.264583"
          id="pycut_path73" />
        <path
          d="m 65.578469,62.313171 q 0,1.012855 -0.620115,1.560623 -0.614948,0.547769 -1.653641,0.547769 -0.248046,0 -0.661456,-0.04651 -0.41341,-0.04134 -0.692462,-0.103352 v -0.956011 h 0.05684 q 0.211872,0.07235 0.52193,0.149861 0.310058,0.07751 0.635618,0.07751 0.475422,0 0.754474,-0.10852 0.284219,-0.10852 0.418577,-0.310058 0.139526,-0.206705 0.1757,-0.506427 0.04134,-0.299722 0.04134,-0.692462 v -4.490668 h -1.627803 v -0.816485 h 2.650993 z"
          style="stroke-width:0.264583"
          id="pycut_path75" />
        <path
          d="m 72.410069,61.429507 q 0,1.410762 -0.723468,2.227247 -0.723468,0.816485 -1.93786,0.816485 -1.224727,0 -1.948195,-0.816485 -0.7183,-0.816485 -0.7183,-2.227247 0,-1.410762 0.7183,-2.227247 0.723468,-0.821653 1.948195,-0.821653 1.214392,0 1.93786,0.821653 0.723468,0.816485 0.723468,2.227247 z m -1.00252,0 q 0,-1.121375 -0.439248,-1.663976 -0.439248,-0.547768 -1.21956,-0.547768 -0.790647,0 -1.229895,0.547768 -0.434081,0.542601 -0.434081,1.663976 0,1.085202 0.439249,1.648473 0.439248,0.558104 1.224727,0.558104 0.775144,0 1.214392,-0.552937 0.444416,-0.558103 0.444416,-1.65364 z"
          style="stroke-width:0.264583"
          id="pycut_path77" />
        <path
          d="m 78.993628,61.382998 q 0,0.723468 -0.206705,1.302242 -0.201537,0.578774 -0.547768,0.971514 -0.366902,0.408243 -0.80615,0.614948 -0.439249,0.201537 -0.966346,0.201537 -0.490925,0 -0.857826,-0.118855 -0.366902,-0.113688 -0.723468,-0.310058 l -0.06201,0.268717 h -0.909502 v -8.040828 h 0.971514 v 2.873201 q 0.408242,-0.335896 0.868161,-0.547769 0.459919,-0.21704 1.033525,-0.21704 1.023191,0 1.6123,0.785479 0.594277,0.78548 0.594277,2.216912 z m -1.00252,0.02584 q 0,-1.033525 -0.341063,-1.565791 -0.341063,-0.537433 -1.100704,-0.537433 -0.423746,0 -0.857826,0.186035 -0.434081,0.180867 -0.80615,0.470254 v 3.307281 q 0.41341,0.186035 0.707965,0.258381 0.299722,0.07235 0.676959,0.07235 0.80615,0 1.260901,-0.527098 0.459918,-0.532265 0.459918,-1.663976 z"
          style="stroke-width:0.264583"
          id="pycut_path79" />
        </g>
             </svg>'''
            self.svg_viewer.set_svg(svg)
        else:
            fp = open(svg, "r")
            svg = fp.read()
            fp.close()

            # extract dimension of material as global variables in the SvgModel
            sizeXstr, sizeYstr = svgviewer.extract_svg_dimensions(svg)

            suffix = ""
            
            if "mm" in sizeXstr:
                suffix = "mm"
                sizeX, sizeY = float(sizeXstr.split("mm")[0]), float(sizeYstr.split("mm")[0])
            elif "in" in sizeXstr:
                suffix = "in"
                sizeX, sizeY = float(sizeXstr.split("in")[0]), float(sizeYstr.split("in")[0])
            else:
                sizeX, sizeY = float(sizeXstr), float(sizeYstr)

            self.ui.doubleSpinBox_SvgModelWidth.setValue(sizeX)
            self.ui.doubleSpinBox_SvgModelHeight.setValue(sizeY)

            self.ui.doubleSpinBox_SvgModelWidth.setSuffix(suffix)
            self.ui.doubleSpinBox_SvgModelHeight.setSuffix(suffix)

            SvgModel.sizeX = sizeX
            SvgModel.sizeY = sizeY

            self.svg_viewer.set_svg(svg)
            # and the tabs if any
            self.svg_viewer.set_tabs(self.tabs)

    def assign_tabs(self, tabs: List[Tab]):
        '''
        '''
        self.tabs = tabs
        self.ui.tabsview_manager.set_tabs(self.tabs)
    
    def display_cnc_tabs(self, tabs: List[Tab]):
        '''
        '''
        self.tabs = tabs
        self.svg_viewer.set_tabs(self.tabs)

    def cb_tabs_hide_disabled(self):
        val = self.ui.checkBox_Tabs_hideDisabledTabs.isChecked()
        self.svg_viewer.SVGVIEWER_HIDE_TABS_DISABLED = val
        self.svg_viewer.reinit()

    def cb_tabs_hide_all(self):
        val = self.ui.checkBox_Tabs_hideAllTabs.isChecked()
        self.svg_viewer.SVGVIEWER_HIDE_TABS_ALL = val
        self.svg_viewer.reinit()

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
        # the SVG dimensions
        materialModel.setMaterialSizeX(self.svg_viewer.get_svg_size_x())
        materialModel.setMaterialSizeY(self.svg_viewer.get_svg_size_y())

        toolModel = ToolModel()
        toolModel.units = settings["Tool"]["Units"]
        toolModel.diameter = ValWithUnit(settings["Tool"]["Diameter"], toolModel.units)
        toolModel.angle = settings["Tool"]["Angle"]
        toolModel.passDepth = ValWithUnit(settings["Tool"]["PassDepth"], toolModel.units)
        toolModel.stepover = settings["Tool"]["StepOver"]
        toolModel.rapidRate = ValWithUnit(settings["Tool"]["Rapid"], toolModel.units)
        toolModel.plungeRate = ValWithUnit(settings["Tool"]["Plunge"], toolModel.units)
        toolModel.cutRate = ValWithUnit(settings["Tool"]["Cut"], toolModel.units)
        
        tabsmodel = TabsModel([tab for tab in self.tabs if tab["enabled"] == True])
        tabsmodel.units = settings["Tabs"]["units"]
        tabsmodel.height = ValWithUnit(settings["Tabs"]["height"], tabsmodel.units)

        gcodeModel = GcodeModel()
        gcodeModel.units = settings["GCodeConversion"]["Units"]
        gcodeModel.flipXY = settings["GCodeConversion"]["FlipXY"]
        gcodeModel.XOffset = settings["GCodeConversion"]["XOffset"]
        gcodeModel.YOffset = settings["GCodeConversion"]["YOffset"]
        gcodeModel.returnTo00 = settings["GCodeGeneration"]["ReturnToZeroAtEnd"]
        gcodeModel.spindleControl = settings["GCodeGeneration"]["SpindleControl"]
        gcodeModel.spindleSpeed = settings["GCodeGeneration"]["SpindleSpeed"]
        gcodeModel.programEnd = settings["GCodeGeneration"]["ProgramEnd"]
        
        gcodeModel.gcodeZero = GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL
        if self.ui.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.isChecked():
            gcodeModel.gcodeZero = GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL
        if self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.isChecked():
            gcodeModel.gcodeZero = GcodeModel.ZERO_LOWER_LEFT_OF_MATERIAL
        if self.ui.pushButton_GCodeConversion_ZeroLowerLeftOfOp.isChecked():
            gcodeModel.gcodeZero = GcodeModel.ZERO_LOWER_LEFT_OF_OP
        if self.ui.pushButton_GCodeConversion_ZeroCenterOfOp.isChecked():
            gcodeModel.gcodeZero = GcodeModel.ZERO_CENTER_OF_OP

        cnc_ops = self.get_jobmodel_operations()

        job = JobModel(self.svg_viewer, cnc_ops, materialModel, svgModel, toolModel, tabsmodel, gcodeModel)

        return job  

    def cb_generate_gcode(self):
        '''
        '''
        self.job = job = self.get_jobmodel()

        ok = self.jobmodel_check_operations()
        if not ok:
            return

        ok = self.jobmodel_check_toolpaths()
        if not ok:
            return

        generator = GcodeGenerator(job)
        generator.generateGcode()

        self.after_gcode_generation(generator)

    def cb_generate_gcode_x_offset(self):
        '''
        '''
        self.job = job = self.get_jobmodel()

        ok = self.jobmodel_check_toolpaths()
        if not ok:
            return

        generator = GcodeGenerator(job)
        generator.setXOffset(self.ui.doubleSpinBox_GCodeConversion_XOffset.value())
        #generator.generateGcode()

        self.after_gcode_generation(generator)

    def cb_generate_gcode_y_offset(self):
        '''
        '''
        self.job = job = self.get_jobmodel()

        ok = self.jobmodel_check_toolpaths()
        if not ok:
            return

        generator = GcodeGenerator(job)
        generator.setYOffset(self.ui.doubleSpinBox_GCodeConversion_YOffset.value())
        #generator.generateGcode()

        self.after_gcode_generation(generator)

    def jobmodel_check_operations(self):
        '''
        '''
        has_operations = len(self.job.operations) > 0

        if not has_operations:
            # alert
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("PyCut")
            msgBox.setText("The Job has no operations!")
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
            msgBox.exec()
            
        return has_operations

    def jobmodel_check_toolpaths(self):
        '''
        '''
        has_toolpaths = False
        for op in self.job.operations:
            if len(op.cam_paths) > 0:
                has_toolpaths = True

        if not has_toolpaths:
            # alert
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("PyCut")
            msgBox.setText("The Job has no toolpaths!")
            msgBox.setInformativeText("Maybe is the geometry too narrow for the cutter?")
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
            msgBox.exec()
            
        return has_toolpaths

    def after_gcode_generation(self, generator: GcodeGenerator):
        '''
        '''
        # with the resulting calculation, we can fill the min/max in X/Y as well as the offsets
        self.ui.doubleSpinBox_GCodeConversion_XOffset.valueChanged.disconnect(self.cb_generate_gcode_x_offset)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.valueChanged.disconnect(self.cb_generate_gcode_y_offset)

        self.ui.doubleSpinBox_GCodeConversion_XOffset.setValue(generator.offsetX)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.setValue(generator.offsetY)
        
        self.ui.doubleSpinBox_GCodeConversion_XOffset.valueChanged.connect(self.cb_generate_gcode_x_offset)
        self.ui.doubleSpinBox_GCodeConversion_YOffset.valueChanged.connect(self.cb_generate_gcode_y_offset)

        self.ui.doubleSpinBox_GCodeConversion_MinX.setValue(generator.minX)
        self.ui.doubleSpinBox_GCodeConversion_MinY.setValue(generator.minY)
        self.ui.doubleSpinBox_GCodeConversion_MaxX.setValue(generator.maxX)
        self.ui.doubleSpinBox_GCodeConversion_MaxY.setValue(generator.maxY)

        self.svg_viewer.display_job_toolpaths(generator.job.operations)
        
        # gcode viewer/simulator
        gcode = generator.gcode
        self.display_gcode(gcode)

    def read_recent_jobs(self):
        '''
        Returns the list of recent jobs fron the setting file
        '''
        self.recent_jobs = []

        if not os.path.exists("./recent_jobs.json"):
            fp = open("./recent_jobs.json", "w")
            json.dump([], fp, indent=2)  
            fp.close()

        with open("./recent_jobs.json", "r") as f:
            self.recent_jobs = json.load(f)

        return self.recent_jobs

    def write_recent_jobs(self):
        '''
        Write the list of recent jobs to the settings file
        '''
        with open("./recent_jobs.json", 'w') as json_file:
            json.dump(self.recent_jobs, json_file, indent=2)   

    def prepend_recent_jobs(self, jobfile):
        '''
        '''
        self.recent_jobs.insert(0, jobfile)
        self.recent_jobs = self.recent_jobs[:5]

    def closeEvent(self, event):
        # do stuff
        self.write_recent_jobs()
        event.accept() # let the window close

    def build_recent_jobs_submenu(self):
        '''
        '''
        for jobfilename in self.recent_jobs:
            icon = QtGui.QIcon.fromTheme("edit-paste")
            item = QtGui.QAction(icon, jobfilename, self.ui.menuOpen_Recent_Jobs)
            item.triggered.connect(self.cb_open_recent_job_file)
            self.ui.menuOpen_Recent_Jobs.addAction(item)

    def minify_path(self, apath):
        '''
        '''
        cwd = os.getcwd()
        cwd = pathlib.PurePath(cwd).as_posix()

        if apath.startswith(cwd):
            apath = apath.split(cwd)[1]
            apath = apath[1:]  # remove the leading slash

        return apath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="PyCut", description="PyCut CAM program - Read the doc!")

    # argument
    parser.add_argument('-job', "--jobfile", dest="load_job", help="load job file")

    # version info
    parser.add_argument("--version", action='version', version='%s' % VERSION)

    options = parser.parse_args()

    app = QtWidgets.QApplication([])
    app.setApplicationName("PyCut")

    mainwindow = PyCutMainWindow(options)
    mainwindow.show()
    sys.exit(app.exec())
