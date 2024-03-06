# This Python file uses the following encoding: utf-8

VERSION = "0_6_0"

import sys
import os
import json
import argparse
import pathlib
import math

import posixpath
import ntpath

import xml.etree.ElementTree as etree

from typing import List
from typing import Dict
from typing import Tuple

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6 import QtWebEngineWidgets

from PySide6.QtUiTools import QUiLoader

from PySide6.QtCore import QRegularExpression

import shapely_svgpath_io

from val_with_unit import ValWithUnit

import svgviewer
import gcodeviewer.widgets.glwidget_container as glwidget_container

import gcodesimulator_webgl.viewer as gcodesimulator_webgl_viewer
import gcodesimulator_python.viewer as gcodesimulator_python_viewer
import gcodesimulator_python.glviewer as gcodesimulator_python_glviewer
from gcodesimulator_python.gcodeminiparser import GcodeMiniParser

gcodesimulator_python_glviewer.Drawable.set_pycut_prefix()

import operations_tableview
import tabs_tableview
import viewers_settings.colorpicker as colorpicker

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
    """ """

    SIMULATOR_WEB_GL = False
    SIMULATOR_PYOPENGL = True

    default_settings = {
        "svg": {
            "px_per_inch": 96,
        },
        "Tabs": {"units": "mm", "height": 1.0, "tabs": []},
        "Tool": {
            "units": "mm",
            "diameter": 3.0,
            "angle": 180,
            "passdepth": 1.0,
            "overlap": 0.4,
            "rapid": 500,
            "plunge": 100,
            "cut": 250,
            "helix_pitch": 0.1,
        },
        "Material": {
            "units": "mm",
            "thickness": 10.0,
            "z_origin": "Top",
            "clearance": 2.5,
        },
        "CurveToLineConversion": {
            "minimum_segments": 5,
            "minimum_segments_length": 0.01,
        },
        "GCodeConversion": {
            "units": "mm",
            "flip_xy": False,
            "x_offset": 0.0,
            "y_offset": 0.0,
            "xy_reference": "ZERO_TOP_LEFT_OF_MATERIAL",
        },
        "GCodeGeneration": {
            "return_to_zero_at_end": True,
            "spindle_control": True,
            "spindle_speed": 1000,
            "program_end": True,
        },
    }

    def __init__(self, options):
        """ """
        super(PyCutMainWindow, self).__init__()

        self.recent_jobs = self.read_recent_jobs()

        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)

        # simulator: python ON, webgl OFF
        if self.SIMULATOR_WEB_GL == False:
            self.ui.tabWidget.setTabVisible(2, False)
        if self.SIMULATOR_PYOPENGL == False:
            self.ui.tabWidget.setTabVisible(3, False)

        self.setWindowTitle("PyCut")
        self.setWindowIcon(
            QtGui.QIcon(":/images/tango/32x32/categories/applications-system.png")
        )

        self.build_recent_jobs_submenu()

        self.operations = []
        self.tabs: List[Dict[str, any]] = []

        # a job to keep the generated gcode in memory (and save it)
        self.job = None

        # open/read/write job settings
        self.jobfilename = None

        self.simulator_webgl_viewer = None
        self.simulator_python_viewer = None

        self.svg_viewer = self.setup_svg_viewer()
        self.svg_material_viewer = self.setup_material_viewer()
        self.simulator_webgl_viewer = self.setup_simulator_webgl_viewer()
        # self.simulator_python_viewer = self.setup_simulator_python_viewer() # no! only with gcode data
        self.candle_viewer = self.setup_candle_viewer()

        self.ui.tabsview_manager.set_svg_viewer(self.svg_viewer)
        self.ui.operationsview_manager.set_svg_viewer(self.svg_viewer)

        # callbacks
        self.ui.SaveGcode.setIcon(
            QtGui.QIcon(":/images/tango/22x22/actions/document-save-as.png")
        )
        self.ui.SaveGcode.clicked.connect(self.cb_save_gcode)

        self.ui.actionOpenSvg.triggered.connect(self.cb_open_svg)
        self.ui.actionNewJob.triggered.connect(self.cb_new_job)
        self.ui.actionOpenJob.triggered.connect(self.cb_open_job)
        self.ui.actionSaveJobAs.triggered.connect(self.cb_save_job_as)
        self.ui.actionSaveJob.triggered.connect(self.cb_save_job)

        self.ui.actionSettings.triggered.connect(self.cb_open_viewers_settings_dialog)

        self.ui.actionOpenGCode.triggered.connect(self.cb_open_gcode)

        self.ui.actionTutorial.triggered.connect(self.cb_show_tutorial_qt)
        self.ui.actionAboutQt.triggered.connect(self.cb_show_about_qt)
        self.ui.actionAboutPyCut.triggered.connect(self.cb_show_about_pycut)

        self.aboutQtAct = QtGui.QAction(
            "About &Qt",
            self,
            statusTip="Show the Qt library's About box",
            triggered=QtWidgets.QApplication.instance().aboutQt,
        )

        # display material thickness/clearance
        self.ui.Material_Thickness.valueChanged.connect(
            self.cb_display_material_thickness
        )
        self.ui.Material_Clearance.valueChanged.connect(
            self.cb_display_material_clearance
        )

        default_thickness = self.ui.Material_Thickness.value()
        default_clearance = self.ui.Material_Clearance.value()
        self.svg_material_viewer.display_material(
            thickness=default_thickness, clearance=default_clearance
        )

        self.ui.CurveToLineConversion_MinimumNbSegments.valueChanged.connect(
            self.cb_curve_min_segments
        )
        self.ui.CurveToLineConversion_MinimumSegmentsLength.valueChanged.connect(
            self.cb_curve_min_segments_length
        )

        self.display_svg(None)

        self.ui.Tabs_Units.currentTextChanged.connect(self.cb_update_tabs_display)
        self.ui.Tool_Units.currentTextChanged.connect(self.cb_update_tool_display)
        self.ui.Material_Units.currentTextChanged.connect(
            self.cb_update_material_display
        )
        self.ui.GCodeConversion_Units.currentTextChanged.connect(
            self.cb_update_gcodeconversion_display
        )

        self.ui.GCodeGeneration_SpindleControl.clicked.connect(self.cb_spindle_control)

        self.ui.GCodeConversion_ZeroTopLeftOfMaterial.clicked.connect(
            self.cb_generate_gcode
        )
        self.ui.GCodeConversion_ZeroLowerLeftOfMaterial.clicked.connect(
            self.cb_generate_gcode
        )
        self.ui.GCodeConversion_ZeroLowerLeftOfOp.clicked.connect(
            self.cb_generate_gcode
        )
        self.ui.GCodeConversion_ZeroCenterOfOp.clicked.connect(self.cb_generate_gcode)

        self.ui.GCodeConversion_ZeroTopLeftOfMaterial.setIcon(
            QtGui.QIcon(":/images/tango/22x22/actions/view-refresh.png")
        )
        self.ui.GCodeConversion_ZeroLowerLeftOfMaterial.setIcon(
            QtGui.QIcon(":/images/tango/22x22/actions/view-refresh.png")
        )
        self.ui.GCodeConversion_ZeroLowerLeftOfOp.setIcon(
            QtGui.QIcon(":/images/tango/22x22/actions/view-refresh.png")
        )
        self.ui.GCodeConversion_ZeroCenterOfOp.setIcon(
            QtGui.QIcon(":/images/tango/22x22/actions/view-refresh.png")
        )

        self.ui.buttonGroup_GCodeConversion.setId(
            self.ui.GCodeConversion_ZeroTopLeftOfMaterial,
            GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL,
        )
        self.ui.buttonGroup_GCodeConversion.setId(
            self.ui.GCodeConversion_ZeroLowerLeftOfMaterial,
            GcodeModel.ZERO_LOWER_LEFT_OF_MATERIAL,
        )
        self.ui.buttonGroup_GCodeConversion.setId(
            self.ui.GCodeConversion_ZeroLowerLeftOfOp,
            GcodeModel.ZERO_LOWER_LEFT_OF_OP,
        )
        self.ui.buttonGroup_GCodeConversion.setId(
            self.ui.GCodeConversion_ZeroCenterOfOp,
            GcodeModel.ZERO_CENTER_OF_OP,
        )

        self.ui.Tabs_hideAllTabs.clicked.connect(self.cb_tabs_hide_all)
        self.ui.Tabs_hideDisabledTabs.clicked.connect(self.cb_tabs_hide_disabled)

        self.init_gui()

        if options.job is not None:
            if os.path.exists(options.job):
                self.open_job(options.job)
            else:
                # alert
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("PyCut")
                msgBox.setText("Job File %s not found" % options.job)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
                msgBox.exec()

        elif options.gcode is not None:
            if os.path.exists(options.gcode):
                self.open_gcode(options.gcode)
            else:
                # alert
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("PyCut")
                msgBox.setText("GCode File %s not found" % options.gcode)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
                msgBox.exec()

        self.menubarToggleLeftBottomSidesButton = QtGui.QAction(
            QtGui.QIcon(":/images/left-bottom-areas.png"),
            "hide/show",
            self,
            shortcut=QtGui.QKeySequence.Back,
            statusTip="Show/Hide Left/Bottom Sides",
            triggered=self.toggle_left_bottom_sides,
        )
        self.menubarToggleLeftBottomSidesButton.setCheckable(True)
        self.menubarToggleLeftBottomSidesButton.setToolTip(
            "Show/Hide Left/Bottom Sides View"
        )

        self.menubarToggleLeftSideButton = QtGui.QAction(
            QtGui.QIcon(":/images/left-area.png"),
            "hide/show",
            self,
            shortcut=QtGui.QKeySequence.Back,
            statusTip="Show/Hide Left Side",
            triggered=self.toggle_left_side,
        )
        self.menubarToggleLeftSideButton.setCheckable(True)
        self.menubarToggleLeftSideButton.setToolTip(
            "Show/Hide Left Side View"
        )  # still not shown

        self.menubarToggleMiddleAreaButton = QtGui.QAction(
            QtGui.QIcon(":/images/bellow-area.png"),
            "hide/show",
            self,
            shortcut=QtGui.QKeySequence.Forward,
            statusTip="Show/Hide Op. Table",
            triggered=self.toggle_middle_area,
        )
        self.menubarToggleMiddleAreaButton.setCheckable(True)
        self.menubarToggleMiddleAreaButton.setToolTip(
            "Show/Hide Op. Table View"
        )  # still not shown

        self.menubarToggleRightSideButton = QtGui.QAction(
            QtGui.QIcon(":/images/right-area.png"),
            "hide/show",
            self,
            shortcut=QtGui.QKeySequence.Forward,
            statusTip="Show/Hide Right Side",
            triggered=self.toggle_right_side,
        )
        self.menubarToggleRightSideButton.setCheckable(True)
        self.menubarToggleRightSideButton.setToolTip(
            "Show/Hide Right Side View"
        )  # still not shown

        self.menuBar().addAction(self.menubarToggleLeftBottomSidesButton)
        self.menuBar().addAction(self.menubarToggleLeftSideButton)
        self.menuBar().addAction(self.menubarToggleMiddleAreaButton)
        self.menuBar().addAction(self.menubarToggleRightSideButton)

        # some buttons (3) to quickly set/unset the geometry preview color to a predefined "custom" color
        # self.menubarGeometryPreviewRedColorButton = QtGui.QAction(QtGui.QPixmap(":images/media-record-red.png"), "",
        #        self, shortcut=QtGui.QKeySequence.Back,
        #        statusTip="Geometry Preview in Red", triggered=self.set_unset_geometry_preview_custom_color_red)
        # self.menubarGeometryPreviewRedColorButton.setCheckable(True)

        # self.menubarGeometryPreviewGreenColorButton = QtGui.QAction(QtGui.QIcon(":images/media-record-green.png"), "",
        #        self, shortcut=QtGui.QKeySequence.Back,
        #        statusTip="Geometry Preview in Green", triggered=self.set_unset_geometry_preview_custom_color_green)
        # self.menubarGeometryPreviewGreenColorButton.setCheckable(True)

        # self.menubarGeometryPreviewBlueColorButton = QtGui.QAction(QtGui.QIcon(":images/media-record-blue.png"), "",
        #        self, shortcut=QtGui.QKeySequence.Back,
        #        statusTip="Geometry Preview in Blue", triggered=self.set_unset_geometry_preview_custom_color_blue)
        # self.menubarGeometryPreviewBlueColorButton.setCheckable(True)

        # self.menuBar().addAction(self.menubarGeometryPreviewRedColorButton)
        # self.menuBar().addAction(self.menubarGeometryPreviewGreenColorButton)
        # self.menuBar().addAction(self.menubarGeometryPreviewBlueColorButton)

        # these callbacks only after have loading a job
        self.ui.GCodeConversion_XOffset.valueChanged.connect(
            self.cb_generate_gcode_x_offset
        )
        self.ui.GCodeConversion_YOffset.valueChanged.connect(
            self.cb_generate_gcode_y_offset
        )
        self.ui.GCodeConversion_FlipXY.clicked.connect(self.cb_generate_gcode)

        self.setWindowState(QtCore.Qt.WindowMaximized)

    """
    def set_unset_geometry_preview_custom_color_red(self):
        '''
        '''
        if self.menubarGeometryPreviewRedColorButton.isChecked():
            # reset other buttons
            self.menubarGeometryPreviewGreenColorButton.setChecked(False)
            self.menubarGeometryPreviewGreenColorButton.setIcon(QtGui.QIcon(":images/media-record-green.png"))
            self.menubarGeometryPreviewBlueColorButton.setChecked(False)
            self.menubarGeometryPreviewBlueColorButton.setIcon(QtGui.QIcon(":images/media-record-blue.png"))

            self.svg_viewer.set_settings_geometry_preview_custom_color("#ff0000")
            self.menubarGeometryPreviewRedColorButton.setIcon(QtGui.QIcon(":images/media-record-red-dark.png"))
        else:
            self.svg_viewer.set_settings_geometry_preview_custom_color_reset()
            self.menubarGeometryPreviewRedColorButton.setIcon(QtGui.QIcon(":images/media-record-red.png"))

    def set_unset_geometry_preview_custom_color_green(self):
        '''
        '''
        if self.menubarGeometryPreviewGreenColorButton.isChecked():
            # reset other buttons
            self.menubarGeometryPreviewRedColorButton.setChecked(False)
            self.menubarGeometryPreviewRedColorButton.setIcon(QtGui.QIcon(":images/media-record-red.png"))
            self.menubarGeometryPreviewBlueColorButton.setChecked(False)
            self.menubarGeometryPreviewBlueColorButton.setIcon(QtGui.QIcon(":images/media-record-blue.png"))

            self.svg_viewer.set_settings_geometry_preview_custom_color("#00ff00")
            self.menubarGeometryPreviewGreenColorButton.setIcon(QtGui.QIcon(":images/media-record-green-dark.png"))
        else:
            self.svg_viewer.set_settings_geometry_preview_custom_color_reset()
            self.menubarGeometryPreviewGreenColorButton.setIcon(QtGui.QIcon(":images/media-record-green.png"))

    def set_unset_geometry_preview_custom_color_blue(self):
        '''
        '''
        if self.menubarGeometryPreviewBlueColorButton.isChecked():
            # reset other buttons
            self.menubarGeometryPreviewRedColorButton.setChecked(False)
            self.menubarGeometryPreviewRedColorButton.setIcon(QtGui.QIcon(":images/media-record-red.png"))
            self.menubarGeometryPreviewGreenColorButton.setChecked(False)
            self.menubarGeometryPreviewGreenColorButton.setIcon(QtGui.QIcon(":images/media-record-green.png"))

            self.svg_viewer.set_settings_geometry_preview_custom_color("#0000ff")
            self.menubarGeometryPreviewBlueColorButton.setIcon(QtGui.QIcon(":images/media-record-blue-dark.png"))
        else:
            self.svg_viewer.set_settings_geometry_preview_custom_color_reset()
            self.menubarGeometryPreviewBlueColorButton.setIcon(QtGui.QIcon(":images/media-record-blue.png"))
    """

    def toggle_left_bottom_sides(self):
        """ """
        if self.menubarToggleLeftBottomSidesButton.isChecked():
            self.ui.scrollArea_left.hide()
            self.ui.operationsview_manager.hide()
        else:
            self.ui.scrollArea_left.show()
            self.ui.operationsview_manager.show()

    def toggle_left_side(self):
        """ """
        if self.menubarToggleLeftSideButton.isChecked():
            self.ui.scrollArea_left.hide()
        else:
            self.ui.scrollArea_left.show()

    def toggle_middle_area(self):
        """ """
        if self.menubarToggleMiddleAreaButton.isChecked():
            self.ui.operationsview_manager.hide()
        else:
            self.ui.operationsview_manager.show()

    def toggle_right_side(self):
        """ """
        if self.menubarToggleRightSideButton.isChecked():
            self.ui.scrollArea_right.hide()
        else:
            self.ui.scrollArea_right.show()

    """
    def cb_show_tutorial_qt(self):
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
    """

    def cb_show_tutorial_qt(self):
        """ """
        dlg = QtWidgets.QDialog(self)

        htmlView = QtWebEngineWidgets.QWebEngineView(dlg)
        htmlView.setMinimumSize(1100, 600)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(htmlView)

        dlg.setLayout(mainLayout)
        dlg.setWindowTitle("PyCut Tutorial")
        dlg.setModal(True)

        fileName = ":/tutorial.html"
        file = QtCore.QFile(fileName)
        if file.open(QtCore.QIODevice.ReadOnly):
            data = str(file.readAll(), "utf-8")  # explicit encoding
        else:
            data = "ERROR"

        file.close()

        htmlView.setHtml(data, baseUrl=QtCore.QUrl("qrc:/"))

        dlg.show()

    def cb_show_about_qt(self):
        QtWidgets.QApplication.instance().aboutQt()

    def cb_show_about_pycut(self):
        dlg = QtWidgets.QDialog(self)

        view = QtWidgets.QTextBrowser(dlg)
        view.setReadOnly(True)
        view.setMinimumSize(800, 500)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(view)

        dlg.setLayout(mainLayout)
        dlg.setWindowTitle("PyCut Relnotes")
        dlg.setModal(True)

        try:
            view.setSource(QtCore.QUrl.fromLocalFile(":/about.html"))
        except Exception as msg:
            view.setHtml(self.notfound % {"message": str(msg)})

        dlg.show()

    def cb_save_gcode(self):
        """ """
        if self.job:
            jobname = os.path.basename(self.jobfilename)
            jobname = os.path.splitext(jobname)[0]

            opname = self.job.operations[0].name

            filename = "%s_%s.nc" % (jobname, opname)

            gcode = self.job.gcode

            if os.path.exists(filename):
                k = 1
                filename = "%s_%s_%d.nc" % (jobname, opname, k)
                while os.path.exists(filename):
                    k += 1
                    filename = "%s_%s_%d.nc" % (jobname, opname, k)

            fp = open(filename, "w")
            fp.write(gcode)
            fp.close()

            # status bar -> msg
            self.statusBar().showMessage('Saved GCode to "%s"' % filename, 3000)

    def display_gcode(self, gcode: str):
        """
        display gcode in webgl!
        display gcode in python!

        and candle viewer!
        """
        simulator_data = {
            "gcode": gcode,
            "cutterHeight": 3 * 4.0,
            "cutterDiameter": self.ui.Tool_Diameter.value(),
            "cutterAngle": self.ui.Tool_Angle.value(),
        }

        if self.simulator_webgl_viewer is not None:
            self.simulator_webgl_viewer.set_data(simulator_data)

        # -----------------------------------------------------------------

        simulator_data_python = {
            "gcode": gcode,
            "cutter_height": 3 * 4.0,
            "cutter_diameter": self.ui.Tool_Diameter.value(),
            "cutter_angle": self.ui.Tool_Angle.value(),
            "use_candle_parser": True,
        }

        self.setup_simulator_python_viewer(simulator_data_python)

        # -----------------------------------------------------------------

        self.candle_viewer.loadData(gcode)

    def load_ui(self, uifile: str):
        """
        old method th load ui, not OK when a QMainWindow ui file
        has to be loaded, OK when simple widget.
        Kept here to remember how it works (quite well infact, and
        no need to generate an Ui_XXXX.py file)
        """
        loader = QUiLoader(self)
        loader.registerCustomWidget(
            operations_tableview.PyCutOperationsTableViewManager
        )
        loader.registerCustomWidget(tabs_tableview.PyCutTabsTableViewManager)

        widget = loader.load(uifile)

        return widget

    def init_gui(self):
        """
        set the default settings in the gui
        """
        self.apply_settings(self.default_settings)

        # self.cb_update_tabs_display()
        # self.cb_update_tool_display()
        # self.cb_update_material_display()
        # self.cb_update_gcodeconversion_display()

    def get_current_viewers_settings(self):
        """ """
        viewers_settings = {
            "svg_viewer": self.svg_viewer.get_settings(),
            "gcode_viewer": {},
            "gcode_simulator": gcodesimulator_python_glviewer.GCodeSimulatorSettings.get_settings(),
        }

        return viewers_settings

    def get_current_settings(self):
        """ """
        settings = {
            "svg": {
                "px_per_inch": 96,
            },
            "Tabs": {
                "units": self.ui.Tabs_Units.currentText(),
                "height": self.ui.Tabs_Height.value(),
                "tabs": self.tabs,
            },
            "Tool": {
                "units": self.ui.Tool_Units.currentText(),
                "diameter": self.ui.Tool_Diameter.value(),
                "angle": self.ui.Tool_Angle.value(),
                "passdepth": self.ui.Tool_PassDepth.value(),
                "overlap": self.ui.Tool_Overlap.value(),
                "rapid": self.ui.Tool_Rapid.value(),
                "plunge": self.ui.Tool_Plunge.value(),
                "cut": self.ui.Tool_Cut.value(),
                "helix_pitch": self.ui.Tool_HelixPitch.value(),
            },
            "Material": {
                "units": self.ui.Material_Units.currentText(),
                "thickness": self.ui.Material_Thickness.value(),
                "z_origin": self.ui.Material_ZOrigin.currentText(),
                "clearance": self.ui.Material_Clearance.value(),
            },
            "CurveToLineConversion": {
                "minimum_segments": self.ui.CurveToLineConversion_MinimumNbSegments.value(),
                "minimum_segments_length": self.ui.CurveToLineConversion_MinimumSegmentsLength.value(),
            },
            "GCodeConversion": {
                "units": self.ui.GCodeConversion_Units.currentText(),
                "flip_xy": self.ui.GCodeConversion_FlipXY.isChecked(),
                "x_offset": self.ui.GCodeConversion_XOffset.value(),
                "y_offset": self.ui.GCodeConversion_YOffset.value(),
                "xy_reference": GcodeModel.XYRef[
                    self.ui.buttonGroup_GCodeConversion.checkedId()
                ],
            },
            "GCodeGeneration": {
                "return_to_zero_at_end": self.ui.GCodeGeneration_ReturnToZeroAtEnd.isChecked(),
                "spindle_control": self.ui.GCodeGeneration_SpindleControl.isChecked(),
                "spindle_speed": self.ui.GCodeGeneration_SpindleSpeed.value(),
                "program_end": self.ui.GCodeGeneration_ProgramEnd.isChecked(),
            },
        }

        return settings

    def apply_settings(self, settings):
        """ """
        # Tabs
        self.ui.Tabs_Units.setCurrentText(settings["Tabs"]["units"])
        self.ui.Tabs_Height.setValue(settings["Tabs"]["height"])

        # Tool
        self.ui.Tool_Units.setCurrentText(settings["Tool"]["units"])
        self.ui.Tool_Diameter.setValue(settings["Tool"]["diameter"])
        self.ui.Tool_Angle.setValue(settings["Tool"]["angle"])
        self.ui.Tool_PassDepth.setValue(settings["Tool"]["passdepth"])
        self.ui.Tool_Overlap.setValue(settings["Tool"]["overlap"])
        self.ui.Tool_Rapid.setValue(settings["Tool"]["rapid"])
        self.ui.Tool_Plunge.setValue(settings["Tool"]["plunge"])
        self.ui.Tool_Cut.setValue(settings["Tool"]["cut"])
        self.ui.Tool_HelixPitch.setValue(settings["Tool"]["helix_pitch"])

        # Material
        self.ui.Material_Units.setCurrentText(settings["Material"]["units"])
        self.ui.Material_Thickness.setValue(settings["Material"]["thickness"])
        self.ui.Material_ZOrigin.setCurrentText(settings["Material"]["z_origin"])
        self.ui.Material_Clearance.setValue(settings["Material"]["clearance"])

        # CurveToLineConversion
        self.ui.CurveToLineConversion_MinimumNbSegments.setValue(
            settings["CurveToLineConversion"]["minimum_segments"]
        )
        self.ui.CurveToLineConversion_MinimumSegmentsLength.setValue(
            settings["CurveToLineConversion"]["minimum_segments_length"]
        )

        # GCodeConversion
        self.ui.GCodeConversion_Units.setCurrentText(
            settings["GCodeConversion"]["units"]
        )
        self.ui.GCodeConversion_FlipXY.setChecked(
            settings["GCodeConversion"]["flip_xy"]
        )
        self.ui.GCodeConversion_XOffset.setValue(
            settings["GCodeConversion"]["x_offset"]
        )
        self.ui.GCodeConversion_YOffset.setValue(
            settings["GCodeConversion"]["y_offset"]
        )

        if settings["GCodeConversion"]["xy_reference"] == "ZERO_TOP_LEFT_OF_MATERIAL":
            self.ui.GCodeConversion_ZeroTopLeftOfMaterial.setChecked(True)
        elif (
            settings["GCodeConversion"]["xy_reference"] == "ZERO_LOWER_LEFT_OF_MATERIAL"
        ):
            self.ui.GCodeConversion_ZeroLowerLeftOfMaterial.setChecked(True)
        elif settings["GCodeConversion"]["xy_reference"] == "ZERO_LOWER_LEFT_OF_OP":
            self.ui.GCodeConversion_ZeroLowerLeftOfOp.setChecked(True)
        elif settings["GCodeConversion"]["xy_reference"] == "ZERO_CENTER_OF_OP":
            self.ui.GCodeConversion_ZeroCenterOfOp.setChecked(True)

        # GCodeGeneration
        self.ui.GCodeGeneration_ReturnToZeroAtEnd.setChecked(
            settings["GCodeGeneration"]["return_to_zero_at_end"]
        )
        self.ui.GCodeGeneration_SpindleControl.setChecked(
            settings["GCodeGeneration"]["spindle_control"]
        )
        self.ui.GCodeGeneration_SpindleSpeed.setValue(
            settings["GCodeGeneration"]["spindle_speed"]
        )
        self.ui.GCodeGeneration_ProgramEnd.setChecked(
            settings["GCodeGeneration"]["program_end"]
        )

    def apply_viewers_settings(self, viewers_settings):
        """ """
        self.svg_viewer.set_settings(viewers_settings["svg_viewer"])

        gcodesimulator_python_glviewer.GCodeSimulatorSettings.OPENGL_FB = (
            viewers_settings["gcode_simulator"]["fb"]
        )

    def cb_open_viewers_settings_dialog(self):
        """ """
        global viewers_settings_dialog

        def fill_dialog():
            viewers_settings_dialog.colorpicker_Tabs_fill.setColor(
                QtGui.QColor(svgviewer.SvgViewer.TABS_SETTINGS["fill"])
            )
            viewers_settings_dialog.Tabs_fill_opacity.setValue(
                float(svgviewer.SvgViewer.TABS_SETTINGS["fill-opacity"])
            )
            viewers_settings_dialog.Tabs_fill_opacity_disabled.setValue(
                float(svgviewer.SvgViewer.TABS_SETTINGS["fill-opacity-disabled"])
            )

            viewers_settings_dialog.colorpicker_Toolpath_stroke.setColor(
                QtGui.QColor(svgviewer.SvgViewer.TOOLPATHS["stroke"])
            )
            viewers_settings_dialog.Toolpath_stroke_width.setValue(
                float(svgviewer.SvgViewer.TOOLPATHS["stroke-width"])
            )

            viewers_settings_dialog.colorpicker_GeometryPreview_fill.setColor(
                QtGui.QColor(svgviewer.SvgViewer.GEOMETRY_PREVIEW_CLOSED_PATHS["fill"])
            )
            viewers_settings_dialog.GeometryPreview_fill_opacity.setValue(
                float(svgviewer.SvgViewer.GEOMETRY_PREVIEW_CLOSED_PATHS["fill-opacity"])
            )

            viewers_settings_dialog.colorpicker_GeometryPreview_stroke.setColor(
                QtGui.QColor(
                    svgviewer.SvgViewer.GEOMETRY_PREVIEW_OPENED_PATHS["stroke"]
                )
            )
            viewers_settings_dialog.GeometryPreview_stroke_opacity.setValue(
                float(
                    svgviewer.SvgViewer.GEOMETRY_PREVIEW_OPENED_PATHS["stroke-opacity"]
                )
            )
            viewers_settings_dialog.GeometryPreview_stroke_width.setValue(
                float(svgviewer.SvgViewer.GEOMETRY_PREVIEW_OPENED_PATHS["stroke-width"])
            )

            if gcodesimulator_python_glviewer.GCodeSimulatorSettings.OPENGL_FB == 1:
                viewers_settings_dialog.radioButton_GCODE_SIMULATOR_FB_1.setChecked(
                    True
                )
                viewers_settings_dialog.radioButton_GCODE_SIMULATOR_FB_2.setChecked(
                    False
                )
            else:
                viewers_settings_dialog.radioButton_GCODE_SIMULATOR_FB_1.setChecked(
                    False
                )
                viewers_settings_dialog.radioButton_GCODE_SIMULATOR_FB_2.setChecked(
                    True
                )

        def set_defaults():
            self.svg_viewer.set_default_settings()
            # gcodesimulator_python_glviewer.GCodeSimulatorSettings.OPENGL_FB =  GCodeSimulatorSettings.DEFAULT_OPENGL_FB

            fill_dialog()

        def set_ok():
            settings = {
                "TABS_SETTINGS": {
                    "stroke": "#aa4488",
                    "stroke-width": "0",
                    "fill": viewers_settings_dialog.colorpicker_Tabs_fill.color().name(),
                    "fill-opacity": str(
                        viewers_settings_dialog.Tabs_fill_opacity.value()
                    ),
                    "fill-opacity-disabled": str(
                        viewers_settings_dialog.Tabs_fill_opacity_disabled.value()
                    ),
                },
                "GEOMETRY_PREVIEW_CLOSED_PATHS": {
                    "stroke": "#ff0000",
                    "stroke-width": "0",
                    "stroke-opacity": "1.0",
                    "fill": viewers_settings_dialog.colorpicker_GeometryPreview_fill.color().name(),
                    "fill-opacity": str(
                        viewers_settings_dialog.GeometryPreview_fill_opacity.value()
                    ),
                },
                "GEOMETRY_PREVIEW_OPENED_PATHS": {
                    "stroke": viewers_settings_dialog.colorpicker_GeometryPreview_stroke.color().name(),
                    "stroke-width": str(
                        viewers_settings_dialog.GeometryPreview_stroke_width.value()
                    ),
                    "stroke-opacity": str(
                        viewers_settings_dialog.GeometryPreview_stroke_opacity.value()
                    ),
                    "fill": "none",
                    "fill-opacity": "1.0",
                },
                "TOOLPATHS": {
                    "stroke": viewers_settings_dialog.colorpicker_Toolpath_stroke.color().name(),
                    "stroke-width": str(
                        viewers_settings_dialog.Toolpath_stroke_width.value()
                    ),
                },
            }
            self.svg_viewer.set_settings(settings)

            if viewers_settings_dialog.radioButton_GCODE_SIMULATOR_FB_1.isChecked():
                gcodesimulator_python_glviewer.GCodeSimulatorSettings.OPENGL_FB = 1
            else:
                gcodesimulator_python_glviewer.GCodeSimulatorSettings.OPENGL_FB = 2

            viewers_settings_dialog.close()

        def set_cancel():
            viewers_settings_dialog.close()

        loader = QUiLoader(None)
        loader.registerCustomWidget(colorpicker.ColorPicker)

        viewers_settings_dialog = loader.load("./viewers_settings/viewers_settings.ui")
        fill_dialog()
        viewers_settings_dialog.cmdDefaults.clicked.connect(set_defaults)
        viewers_settings_dialog.cmdOK.clicked.connect(set_ok)
        viewers_settings_dialog.cmdCancel.clicked.connect(set_cancel)

        viewers_settings_dialog.exec()

    def cb_open_svg(self):
        """
        not a job, a svg only -> no operations
        """
        xfilter = "SVG Files (*.svg)"
        svg_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="open file", dir=".", filter=xfilter
        )

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
        """ """
        self.svg_file = None
        self.display_svg(self.svg_file)

        # clean current job (operations table)
        self.operations = []
        self.ui.operationsview_manager.set_operations(self.operations)

        # clean current job (tabs table)
        self.tabs = []
        self.ui.tabsview_manager.set_tabs(self.tabs)

    def cb_open_recent_job_file(self):
        """ """
        sender = self.sender()
        jobfilename = sender.text()

        self.ui.GCodeConversion_XOffset.valueChanged.disconnect(
            self.cb_generate_gcode_x_offset
        )
        self.ui.GCodeConversion_YOffset.valueChanged.disconnect(
            self.cb_generate_gcode_y_offset
        )
        self.ui.GCodeConversion_FlipXY.clicked.disconnect(self.cb_generate_gcode)

        self.open_job(jobfilename)

        self.ui.GCodeConversion_XOffset.valueChanged.connect(
            self.cb_generate_gcode_x_offset
        )
        self.ui.GCodeConversion_YOffset.valueChanged.connect(
            self.cb_generate_gcode_y_offset
        )
        self.ui.GCodeConversion_FlipXY.clicked.connect(self.cb_generate_gcode)

    def cb_open_job(self):
        """ """
        # read json
        xfilter = "JSON Files (*.json)"
        jobfilename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="open file", dir=".", filter=xfilter
        )

        jobfilename = self.minify_path(jobfilename)

        try:
            self.ui.GCodeConversion_XOffset.valueChanged.disconnect(
                self.cb_generate_gcode_x_offset
            )
            self.ui.GCodeConversion_YOffset.valueChanged.disconnect(
                self.cb_generate_gcode_y_offset
            )
            self.ui.GCodeConversion_FlipXY.clicked.disconnect(self.cb_generate_gcode)
        except Exception as e:
            print(e)
            pass

        self.open_job(jobfilename)

        self.ui.GCodeConversion_XOffset.valueChanged.connect(
            self.cb_generate_gcode_x_offset
        )
        self.ui.GCodeConversion_YOffset.valueChanged.connect(
            self.cb_generate_gcode_y_offset
        )
        self.ui.GCodeConversion_FlipXY.clicked.connect(self.cb_generate_gcode)

    def open_job(self, jobfilename: str):
        cwd = os.getcwd()

        common_prefix = [os.path.commonprefix([cwd, jobfilename])]
        jobfilename = os.path.relpath(jobfilename, common_prefix[0])

        with open(jobfilename) as f:
            self.jobfilename = jobfilename

            self.prepend_recent_jobs(jobfilename)

            job = json.load(f)

            self.svg_file = job["svg_file"]  # relativ to job or absolute

            if os.path.isabs(self.svg_file):
                svg_file = self.svg_file
            else:
                if os.path.isabs(jobfilename):
                    jobdir = os.path.dirname(jobfilename)
                    svg_file = os.path.join(jobdir, self.svg_file)
                else:
                    abs_jobfilename = os.path.abspath(jobfilename)
                    abs_jobdir = os.path.dirname(abs_jobfilename)
                    svg_file = os.path.join(abs_jobdir, self.svg_file)

            if not os.path.exists(svg_file):
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("PyCut")
                msgBox.setText("Svg File %s not found" % svg_file)
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
                msgBox.exec()
                return

            self.operations = job["operations"]
            self.tabs = job["settings"]["Tabs"].get("tabs", [])

            # display
            self.display_svg(svg_file)

            # and fill the whole gui
            self.apply_settings(job["settings"])
            if "viewers_settings" in job:
                self.apply_viewers_settings(job["viewers_settings"])

            # fill operations table
            self.ui.operationsview_manager.set_operations(self.operations)

            # fill tabs table
            self.ui.tabsview_manager.set_tabs(self.tabs)

    def cb_save_job(self):
        """ """
        operations = self.ui.operationsview_manager.get_operations()

        job = {
            "svg_file": self.svg_file,
            "operations": operations,
            "settings": self.get_current_settings(),
            "viewers_settings": self.get_current_viewers_settings(),
        }

        with open(self.jobfilename, "w") as json_file:
            json.dump(job, json_file, indent=2)

    def cb_save_job_as(self):
        """ """
        xfilter = "JSON Files (*.json)"

        operations = self.ui.operationsview_manager.get_operations()

        job = {
            "svg_file": self.svg_file,
            "operations": operations,
            "settings": self.get_current_settings(),
            "viewers_settings": self.get_current_viewers_settings(),
        }

        # open file dialog for a file name
        jobfilename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, caption="Save As", dir=".", filter=xfilter
        )

        if jobfilename:
            jobfilename = self.minify_path(jobfilename)

            """
            get the svg file path relativ to the job file
            if both paths start from the cwd
            """
            if not os.path.isabs(jobfilename) and not os.path.isabs(self.svg_file):
                svg_file_fix = self.get_relpath_relativ_to_the_other(
                    self.svg_file, jobfilename
                )
            else:
                svg_file_fix = self.svg_file

            job["svg_file"] = svg_file_fix

            with open(jobfilename, "w") as json_file:
                json.dump(job, json_file, indent=2)

            self.jobfilename = jobfilename

    def cb_open_gcode(self, gcodefilename):
        """ """
        # read gcode
        xfilter = "GCODE Files (*.nc *.ncc, *.ngc, *.gcode)"
        gcodefilename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="open file", dir=".", filter=xfilter
        )

        gcodefilename = self.minify_path(gcodefilename)

        self.open_gcode(gcodefilename)

    def open_gcode(self, gcodefilename: str):
        with open(gcodefilename) as f:
            gcode = f.read()

            tool_diameter_keyword_0 = "; Diameter:"

            found = False
            # try to get the tool diameter from the gcode comments
            lines = gcode.split("\n")
            for line in lines:
                if line.startswith(tool_diameter_keyword_0):
                    data = line.split(tool_diameter_keyword_0)[1].strip()
                    tool_diameter = float(data)
                    self.ui.Tool_Diameter.setValue(tool_diameter)
                    found = True
                    break

            if not found:
                tool_diameter_keyword1 = "\(tool -> ([0-9.]+) mm end mill\)"
                tool_diameter_keyword2 = "\(TOOL DIA.([0-9.]+)\)"

                res = [
                    QRegularExpression(tool_diameter_keyword1),
                    QRegularExpression(tool_diameter_keyword2),
                ]
                pos = 0
                for line in lines:
                    for re in res:
                        m = re.match(line, pos)
                        if m.hasMatch():
                            data = m.captured(1)
                            tool_diameter = float(data)
                            self.ui.Tool_Diameter.setValue(tool_diameter)
                            found = True
                            break
                    if found:
                        break

            if not found:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("PyCut")
                msgBox.setText(
                    "No tool diameter found in file, using current tool diameter for GCode Simulator"
                )
                msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
                msgBox.exec()

            self.display_gcode(gcode)

            # go on the gcode simulation view
            self.ui.tabWidget.setCurrentIndex(3)

            # quick stats
            miniparser = GcodeMiniParser()
            miniparser.parse_gcode(gcode)
            path_time = math.floor(miniparser.path_time)
            self.ui.GCodeStatistics_RunTime.setText(
                f"{path_time//60} [min] {path_time%60} [s]"
            )

    def cb_curve_min_segments(self):
        """
        what is it good for ?
        seems to be redundant with cb_curve_min_segments_length
        """
        value = self.ui.CurveToLineConversion_MinimumNbSegments.value()
        shapely_svgpath_io.SvgPathDiscretizer.set_arc_min_nb_segments(value)

    def cb_curve_min_segments_length(self):
        """ """
        value = self.ui.CurveToLineConversion_MinimumSegmentsLength.value()
        if value != 0:
            shapely_svgpath_io.SvgPathDiscretizer.set_arc_precision(value)

    def cb_update_tabs_display(self):
        """
        This updates the legends of the tsbs model widget **and** the values
        """
        tabs_units = self.ui.Tabs_Units.currentText()

        if tabs_units == "inch":
            self.ui.Tabs_Height.setValue(self.ui.Tabs_Height.value() / 25.4)
            self.ui.Tabs_Height.setSingleStep(0.04)

        if tabs_units == "mm":
            self.ui.Tabs_Height.setValue(self.ui.Tabs_Height.value() * 25.4)
            self.ui.Tabs_Height.setSingleStep(1.0)

    def cb_update_tool_display(self):
        """
        This updates the legends of the tool model widget **and** the values
        """
        tool_units = self.ui.Tool_Units.currentText()

        if tool_units == "inch":
            self.ui.label_Tool_Diameter_UnitsDescr.setText("inch")
            self.ui.label_Tool_Angle_UnitsDescr.setText("degrees")
            self.ui.label_Tool_PassDepth_UnitsDescr.setText("inch")
            self.ui.label_Tool_Overlap_UnitsDescr.setText("[0:1[")
            self.ui.label_Tool_Rapid_UnitsDescr.setText("inch/min")
            self.ui.label_Tool_Plunge_UnitsDescr.setText("inch/min")
            self.ui.label_Tool_Cut_UnitsDescr.setText("inch/min")
            self.ui.label_Tool_HelixPitch_UnitsDescr.setText("inch/min")

            self.ui.Tool_Diameter.setValue(self.ui.Tool_Diameter.value() / 25.4)
            self.ui.Tool_PassDepth.setValue(self.ui.Tool_PassDepth.value() / 25.4)
            self.ui.Tool_Rapid.setValue(self.ui.Tool_Rapid.value() / 25.4)
            self.ui.Tool_Plunge.setValue(self.ui.Tool_Plunge.value() / 25.4)
            self.ui.Tool_Cut.setValue(self.ui.Tool_Cut.value() / 25.4)
            self.ui.Tool_HelixPitch.setValue(self.ui.Tool_HelixPitch.value() / 25.4)

        if tool_units == "mm":
            self.ui.label_Tool_Diameter_UnitsDescr.setText("mm")
            self.ui.label_Tool_Angle_UnitsDescr.setText("degrees")
            self.ui.label_Tool_PassDepth_UnitsDescr.setText("mm")
            self.ui.label_Tool_Overlap_UnitsDescr.setText("[0:1[")
            self.ui.label_Tool_Rapid_UnitsDescr.setText("mm/min")
            self.ui.label_Tool_Plunge_UnitsDescr.setText("mm/min")
            self.ui.label_Tool_Cut_UnitsDescr.setText("mm/min")
            self.ui.label_Tool_HelixPitch_UnitsDescr.setText("mm/min")

            self.ui.Tool_Diameter.setValue(self.ui.Tool_Diameter.value() * 25.4)
            self.ui.Tool_PassDepth.setValue(self.ui.Tool_PassDepth.value() * 25.4)
            self.ui.Tool_Rapid.setValue(self.ui.Tool_Rapid.value() * 25.4)
            self.ui.Tool_Plunge.setValue(self.ui.Tool_Plunge.value() * 25.4)
            self.ui.Tool_Cut.setValue(self.ui.Tool_Cut.value() * 25.4)
            self.ui.Tool_HelixPitch.setValue(self.ui.Tool_HelixPitch.value() * 25.4)

    def cb_update_material_display(self):
        """
        This updates the legends of the material model widget **and** the values
        """
        material_units = self.ui.Material_Units.currentText()

        if material_units == "inch":
            self.ui.Material_Thickness.setValue(
                self.ui.Material_Thickness.value() / 25.4
            )
            self.ui.Material_Clearance.setValue(
                self.ui.Material_Clearance.value() / 25.4
            )

            self.ui.Material_Thickness.setSingleStep(0.04)
            self.ui.Material_Clearance.setSingleStep(0.04)

        if material_units == "mm":
            self.ui.Material_Thickness.setValue(
                self.ui.Material_Thickness.value() * 25.4
            )
            self.ui.Material_Clearance.setValue(
                self.ui.Material_Clearance.value() * 25.4
            )

            self.ui.Material_Thickness.setSingleStep(1.0)
            self.ui.Material_Clearance.setSingleStep(1.0)

    def cb_update_gcodeconversion_display(self):
        """
        This updates the legends of the gcode_conversion model widget **and** the values
        """
        gcodeconversion_units = self.ui.GCodeConversion_Units.currentText()

        if gcodeconversion_units == "inch":
            self.ui.label_GCodeConversion_XOffset_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_YOffset_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_MinX_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_MaxX_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_MinY_UnitsDescr.setText("inch")
            self.ui.label_GCodeConversion_MaxY_UnitsDescr.setText("inch")

            self.ui.GCodeConversion_XOffset.setValue(
                self.ui.GCodeConversion_XOffset.value() / 25.4
            )
            self.ui.GCodeConversion_YOffset.setValue(
                self.ui.GCodeConversion_YOffset.value() / 25.4
            )
            self.ui.GCodeConversion_MinX.setValue(
                self.ui.GCodeConversion_MinX.value() / 25.4
            )
            self.ui.GCodeConversion_MaxX.setValue(
                self.ui.GCodeConversion_MaxX.value() / 25.4
            )
            self.ui.GCodeConversion_MinY.setValue(
                self.ui.GCodeConversion_MinY.value() / 25.4
            )
            self.ui.GCodeConversion_MaxY.setValue(
                self.ui.GCodeConversion_MaxY.value() / 25.4
            )

        if gcodeconversion_units == "mm":
            self.ui.label_GCodeConversion_XOffset_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_YOffset_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_MinX_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_MaxX_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_MinY_UnitsDescr.setText("mm")
            self.ui.label_GCodeConversion_MaxY_UnitsDescr.setText("mm")

            self.ui.GCodeConversion_XOffset.setValue(
                self.ui.GCodeConversion_XOffset.value() * 25.4
            )
            self.ui.GCodeConversion_YOffset.setValue(
                self.ui.GCodeConversion_YOffset.value() * 25.4
            )
            self.ui.GCodeConversion_MinX.setValue(
                self.ui.GCodeConversion_MinX.value() * 25.4
            )
            self.ui.GCodeConversion_MaxX.setValue(
                self.ui.GCodeConversion_MaxX.value() * 25.4
            )
            self.ui.GCodeConversion_MinY.setValue(
                self.ui.GCodeConversion_MinY.value() * 25.4
            )
            self.ui.GCodeConversion_MaxY.setValue(
                self.ui.GCodeConversion_MaxY.value() * 25.4
            )

    def cb_display_material_thickness(self):
        """
        svg display only in mm
        """
        material_units = self.ui.Material_Units.currentText()

        thickness = ValWithUnit(
            self.ui.Material_Thickness.value(), material_units
        ).to_mm()
        clearance = ValWithUnit(
            self.ui.Material_Clearance.value(), material_units
        ).to_mm()

        self.svg_material_viewer.display_unit(material_units)
        self.svg_material_viewer.display_material(
            thickness=thickness, clearance=clearance
        )

    def cb_display_material_clearance(self):
        """
        svg display only in mm
        """
        material_units = self.ui.Material_Units.currentText()

        thickness = ValWithUnit(
            self.ui.Material_Thickness.value(), material_units
        ).to_mm()
        clearance = ValWithUnit(
            self.ui.Material_Clearance.value(), material_units
        ).to_mm()

        self.svg_material_viewer.display_material(
            thickness=thickness, clearance=clearance
        )

    def cb_spindle_control(self):
        val = self.ui.GCodeGeneration_SpindleControl.isChecked()
        self.ui.GCodeGeneration_SpindleSpeed.setEnabled(val)

    def setup_material_viewer(self):
        """ """
        return material_widget.MaterialWidget(self.ui.widget_display_material)

    def setup_svg_viewer(self):
        """ """
        svg = self.ui.svg
        layout = svg.layout()

        svg_viewer = svgviewer.SvgViewer(svg)
        svg_viewer.set_mainwindow(self)

        layout.addWidget(svg_viewer)
        layout.setStretch(0, 1)

        return svg_viewer

    def setup_candle_viewer(self):
        """ """
        viewer = self.ui.viewer
        layout = viewer.layout()

        candle_viewer = glwidget_container.GLWidgetContainer(viewer)

        layout.addWidget(candle_viewer)
        layout.setStretch(0, 1)

        return candle_viewer

    def setup_simulator_webgl_viewer(self):
        """ """
        if self.SIMULATOR_WEB_GL == False:
            return

        container = self.ui.simulator_webgl
        layout = container.layout()

        self.simulator_webgl_viewer = gcodesimulator_webgl_viewer.GCodeViewer(container)

        layout.addWidget(self.simulator_webgl_viewer)
        layout.setStretch(0, 1)

        return self.simulator_webgl_viewer

    def setup_simulator_python_viewer(self, data):
        """ """
        if self.SIMULATOR_PYOPENGL == False:
            return

        container = self.ui.simulator_python
        layout = container.layout()

        if self.simulator_python_viewer != None:
            self.simulator_python_viewer.setVisible(False)
            layout.removeWidget(self.simulator_python_viewer)

        self.simulator_python_viewer = gcodesimulator_python_viewer.GCodeViewer(
            container, data
        )

        layout.addWidget(self.simulator_python_viewer)
        layout.setStretch(0, 1)

        return self.simulator_python_viewer

    def display_svg(self, svg_file):
        """
        em 	The default font size - usually the height of a character.
        ex 	The height of the character x
        px 	Pixels
        pt 	Points (1 / 72 of an inch)
        pc 	Picas (1 / 6 of an inch)
        cm 	Centimeters
        mm 	Millimeters
        in Inches
        """
        if svg_file is None:
            return

        fp = open(svg_file, "r")
        svg = fp.read()
        fp.close()

        def extract_svg_dimensions(svg: str) -> Tuple[int, int]:
            """
            Dimension of the svg are of importance when making gcode from the lower left
            side of the material
            """
            tree = etree.fromstring(svg)
            tree_attrib = tree.attrib

            w = tree_attrib["width"]
            h = tree_attrib["height"]

            return w, h

        # extract dimension of material as global variables in the SvgModel
        size_xstr, size_ystr = extract_svg_dimensions(svg)

        suffix = ""

        if "mm" in size_xstr:
            suffix = "mm"
            size_x, size_y = float(size_xstr.split("mm")[0]), float(
                size_ystr.split("mm")[0]
            )
        elif "cm" in size_xstr:
            suffix = "mm"
            size_x, size_y = 10 * float(size_xstr.split("cm")[0]), 10 * float(
                size_ystr.split("cm")[0]
            )
        elif "in" in size_xstr:
            suffix = "in"
            size_x, size_y = float(size_xstr.split("in")[0]), float(
                size_ystr.split("in")[0]
            )
        elif "px" in size_xstr:
            suffix = "mm"
            size_x, size_y = float(size_xstr.split("px")[0]), float(
                size_ystr.split("px")[0]
            )
        else:
            suffix = "mm"
            size_x, size_y = float(size_xstr), float(size_ystr)

        self.ui.SvgModelWidth.setValue(size_x)
        self.ui.SvgModelHeight.setValue(size_y)

        self.ui.SvgModelWidth.setSuffix(suffix)
        self.ui.SvgModelHeight.setSuffix(suffix)

        SvgModel.size_x = size_x
        SvgModel.size_y = size_y

        self.svg_viewer.set_svg(svg)
        # and the tabs if any
        self.svg_viewer.set_tabs(self.tabs)

    def assign_tabs(self, tabs: List[Tab]):
        """ """
        self.tabs = tabs
        self.ui.tabsview_manager.set_tabs(self.tabs)

    def display_cnc_tabs(self, tabs: List[Tab]):
        """ """
        self.tabs = tabs
        self.svg_viewer.set_tabs(self.tabs)

    def cb_tabs_hide_disabled(self):
        val = self.ui.Tabs_hideDisabledTabs.isChecked()
        self.svg_viewer.SVGVIEWER_HIDE_TABS_DISABLED = val
        self.svg_viewer.reinit()

    def cb_tabs_hide_all(self):
        val = self.ui.Tabs_hideAllTabs.isChecked()
        self.svg_viewer.SVGVIEWER_HIDE_TABS_ALL = val
        self.svg_viewer.reinit()

    def display_cnc_ops_geometry(self, operations: List[operations_tableview.OpItem]):
        """ """
        settings = self.get_current_settings()

        tool_model = ToolModel()
        tool_model.units = settings["Tool"]["units"]
        tool_model.diameter = ValWithUnit(
            settings["Tool"]["diameter"], tool_model.units
        )
        tool_model.angle = settings["Tool"]["angle"]
        tool_model.passdepth = ValWithUnit(
            settings["Tool"]["passdepth"], tool_model.units
        )
        tool_model.overlap = settings["Tool"]["overlap"]
        tool_model.rapidRate = ValWithUnit(settings["Tool"]["rapid"], tool_model.units)
        tool_model.plungeRate = ValWithUnit(
            settings["Tool"]["plunge"], tool_model.units
        )
        tool_model.cutRate = ValWithUnit(settings["Tool"]["cut"], tool_model.units)
        tool_model.helixPitch = ValWithUnit(
            settings["Tool"]["helix_pitch"], tool_model.units
        )

        cnc_ops = []

        for op_model in operations:
            if not op_model.enabled:
                continue

            cnc_op = CncOp(
                {
                    "units": op_model.units,
                    "name": op_model.name,
                    "paths": op_model.paths,
                    "combinaison": op_model.combinaison,
                    "ramp_plunge": op_model.ramp_plunge,
                    "type": op_model.cam_op,
                    "direction": op_model.direction,
                    "cut_depth": op_model.cut_depth,
                    "margin": op_model.margin,
                    "width": op_model.width,
                    "enabled": op_model.enabled,
                }
            )

            cnc_ops.append(cnc_op)

        for cnc_op in cnc_ops:
            cnc_op.setup(self.svg_viewer)
            cnc_op.calculate_geometry(tool_model)

        self.svg_viewer.reinit()
        self.svg_viewer.display_job_geometry(cnc_ops)

    def get_jobmodel_operations(self) -> List[CncOp]:
        """ """
        cnc_ops: List[CncOp] = []

        for op_model in self.ui.operationsview_manager.get_model_operations():
            if not op_model.enabled:
                continue

            cnc_op = CncOp(
                {
                    "units": op_model.units,
                    "name": op_model.name,
                    "paths": op_model.paths,
                    "combinaison": op_model.combinaison,
                    "ramp_plunge": op_model.ramp_plunge,
                    "type": op_model.cam_op,
                    "direction": op_model.direction,
                    "cut_depth": op_model.cut_depth,
                    "margin": op_model.margin,
                    "width": op_model.width,
                    "enabled": op_model.enabled,
                }
            )

            cnc_ops.append(cnc_op)

        return cnc_ops

    def get_jobmodel(self) -> JobModel:
        """ """
        settings = self.get_current_settings()

        svg_model = SvgModel()
        svg_model.pxPerInch = 96
        material_model = MaterialModel()
        material_model.mat_units = settings["Material"]["units"]
        material_model.mat_thickness = ValWithUnit(
            settings["Material"]["thickness"], material_model.mat_units
        )
        material_model.mat_z_origin = settings["Material"]["z_origin"]
        material_model.mat_clearance = ValWithUnit(
            settings["Material"]["clearance"], material_model.mat_units
        )
        # the SVG dimensions
        material_model.set_material_size_x(self.svg_viewer.get_svg_size_x())
        material_model.set_material_size_y(self.svg_viewer.get_svg_size_y())

        tool_model = ToolModel()
        tool_model.units = settings["Tool"]["units"]
        tool_model.diameter = ValWithUnit(
            settings["Tool"]["diameter"], tool_model.units
        )
        tool_model.angle = settings["Tool"]["angle"]
        tool_model.passdepth = ValWithUnit(
            settings["Tool"]["passdepth"], tool_model.units
        )
        tool_model.overlap = settings["Tool"]["overlap"]
        tool_model.rapidRate = ValWithUnit(settings["Tool"]["rapid"], tool_model.units)
        tool_model.plungeRate = ValWithUnit(
            settings["Tool"]["plunge"], tool_model.units
        )
        tool_model.cutRate = ValWithUnit(settings["Tool"]["cut"], tool_model.units)
        tool_model.helixPitch = ValWithUnit(
            settings["Tool"]["helix_pitch"], tool_model.units
        )

        tabsmodel = TabsModel([tab for tab in self.tabs if tab["enabled"] == True])
        tabsmodel.units = settings["Tabs"]["units"]
        tabsmodel.height = ValWithUnit(settings["Tabs"]["height"], tabsmodel.units)

        gcode_model = GcodeModel()
        gcode_model.units = settings["GCodeConversion"]["units"]
        gcode_model.flipXY = settings["GCodeConversion"]["flip_xy"]
        gcode_model.XOffset = settings["GCodeConversion"]["x_offset"]
        gcode_model.YOffset = settings["GCodeConversion"]["y_offset"]
        gcode_model.returnTo00 = settings["GCodeGeneration"]["return_to_zero_at_end"]
        gcode_model.spindleControl = settings["GCodeGeneration"]["spindle_control"]
        gcode_model.spindleSpeed = settings["GCodeGeneration"]["spindle_speed"]
        gcode_model.programEnd = settings["GCodeGeneration"]["program_end"]

        gcode_model.gcodeZero = GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL
        if self.ui.GCodeConversion_ZeroTopLeftOfMaterial.isChecked():
            gcode_model.gcodeZero = GcodeModel.ZERO_TOP_LEFT_OF_MATERIAL
        if self.ui.GCodeConversion_ZeroLowerLeftOfMaterial.isChecked():
            gcode_model.gcodeZero = GcodeModel.ZERO_LOWER_LEFT_OF_MATERIAL
        if self.ui.GCodeConversion_ZeroLowerLeftOfOp.isChecked():
            gcode_model.gcodeZero = GcodeModel.ZERO_LOWER_LEFT_OF_OP
        if self.ui.GCodeConversion_ZeroCenterOfOp.isChecked():
            gcode_model.gcodeZero = GcodeModel.ZERO_CENTER_OF_OP

        cnc_ops = self.get_jobmodel_operations()

        job = JobModel(
            self.svg_viewer,
            cnc_ops,
            material_model,
            svg_model,
            tool_model,
            tabsmodel,
            gcode_model,
        )

        return job

    def cb_generate_gcode(self):
        """ """
        self.job = job = self.get_jobmodel()

        ok = self.jobmodel_check_operations()
        if not ok:
            return

        ok = self.jobmodel_check_toolpaths()
        if not ok:
            return

        generator = GcodeGenerator(job)
        generator.generate_gcode()

        self.after_gcode_generation(generator)

    def cb_generate_gcode_x_offset(self):
        """ """
        self.job = job = self.get_jobmodel()

        ok = self.jobmodel_check_toolpaths()
        if not ok:
            return

        generator = GcodeGenerator(job)
        generator.set_x_offset(self.ui.GCodeConversion_XOffset.value())
        # generator.generate_gcode()

        self.after_gcode_generation(generator)

    def cb_generate_gcode_y_offset(self):
        """ """
        self.job = job = self.get_jobmodel()

        ok = self.jobmodel_check_toolpaths()
        if not ok:
            return

        generator = GcodeGenerator(job)
        generator.set_y_offset(self.ui.GCodeConversion_YOffset.value())
        # generator.generate_gcode()

        self.after_gcode_generation(generator)

    def jobmodel_check_operations(self):
        """ """
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
        """ """
        has_toolpaths = False
        for op in self.job.operations:
            if len(op.cam_paths) > 0:
                has_toolpaths = True

        if not has_toolpaths:
            # alert
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("PyCut")
            msgBox.setText("The Job has no toolpaths!")
            msgBox.setInformativeText(
                "Maybe is the geometry too narrow for the cutter?"
            )
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
            msgBox.exec()

        return has_toolpaths

    def after_gcode_generation(self, generator: GcodeGenerator):
        """ """
        # with the resulting calculation, we can fill the min/max in X/Y as well as the offsets
        self.ui.GCodeConversion_XOffset.valueChanged.disconnect(
            self.cb_generate_gcode_x_offset
        )
        self.ui.GCodeConversion_YOffset.valueChanged.disconnect(
            self.cb_generate_gcode_y_offset
        )

        self.ui.GCodeConversion_XOffset.setValue(generator.offsetX)
        self.ui.GCodeConversion_YOffset.setValue(generator.offsetY)

        self.ui.GCodeConversion_XOffset.valueChanged.connect(
            self.cb_generate_gcode_x_offset
        )
        self.ui.GCodeConversion_YOffset.valueChanged.connect(
            self.cb_generate_gcode_y_offset
        )

        self.ui.GCodeConversion_MinX.setValue(generator.minX)
        self.ui.GCodeConversion_MinY.setValue(generator.minY)
        self.ui.GCodeConversion_MaxX.setValue(generator.maxX)
        self.ui.GCodeConversion_MaxY.setValue(generator.maxY)

        self.svg_viewer.display_job(generator.job)

        # gcode viewer/simulator
        gcode = generator.gcode

        # quick stats
        miniparser = GcodeMiniParser()
        miniparser.parse_gcode(gcode)
        path_time = math.floor(miniparser.path_time)
        self.ui.GCodeStatistics_RunTime.setText(
            f"{path_time//60} [min] {path_time%60} [s]"
        )

        self.display_gcode(gcode)

    def read_recent_jobs(self):
        """
        Returns the list of recent jobs fron the setting file
        """
        self.recent_jobs = []

        if not os.path.exists("./recent_jobs.json"):
            fp = open("./recent_jobs.json", "w")
            json.dump([], fp, indent=2)
            fp.close()

        with open("./recent_jobs.json", "r") as f:
            self.recent_jobs = json.load(f)

        return self.recent_jobs

    def write_recent_jobs(self):
        """
        Write the list of recent jobs to the settings file
        """
        with open("./recent_jobs.json", "w") as json_file:
            json.dump(self.recent_jobs, json_file, indent=2)

    def prepend_recent_jobs(self, jobfile):
        """ """
        # consider unix style if not absolute
        if not os.path.isabs(jobfile):
            jobfile_unix = jobfile.replace(ntpath.sep, posixpath.sep)
        else:
            jobfile_unix = jobfile

        if jobfile_unix.startswith("./"):
            jobfile_unix = jobfile_unix[2:]

        # remove duplicated
        if jobfile_unix in self.recent_jobs:
            self.recent_jobs.remove(jobfile_unix)

        self.recent_jobs.insert(0, jobfile_unix)

        self.recent_jobs = self.recent_jobs[:5]

    def closeEvent(self, event):
        # do stuff
        self.write_recent_jobs()
        event.accept()  # let the window close

    def build_recent_jobs_submenu(self):
        """ """
        for jobfilename in self.recent_jobs:
            icon = QtGui.QIcon.fromTheme("edit-paste")
            item = QtGui.QAction(icon, jobfilename, self.ui.menuOpen_Recent_Jobs)
            item.triggered.connect(self.cb_open_recent_job_file)
            self.ui.menuOpen_Recent_Jobs.addAction(item)

    def minify_path(self, apath):
        """ """
        cwd = os.getcwd()
        cwd = pathlib.PurePath(cwd).as_posix()

        if apath.startswith(cwd):
            apath = apath.split(cwd)[1]
            apath = apath[1:]  # remove the leading slash

        return apath

    def get_relpath_relativ_to_the_other(self, p1, p2):
        """
        Both paths are relativ to cwd

        ex:
          p1 = 'misc_private/cnc1310/test_svgs/backlash.svg'
          p2 = 'jobs/jj.json'

          => pp1 = '../misc_private/cnc1310/test_svgs/backlash.svg'

        ex:
          p1 = 'misc_private/cnc1310/test_svgs/backlash.svg'
          p2 = 'misc_private/jobs/jj.json'

          => pp1 = '../cnc1310/test_svgs/backlash.svg'
        """
        common_prefix = os.path.commonprefix([p1, p2])

        p1_from_common_prefix = os.path.relpath(p1, common_prefix)
        p2_from_common_prefix = os.path.relpath(p2, common_prefix)

        p1_from_common_prefix = pathlib.PurePath(p1_from_common_prefix).as_posix()
        p2_from_common_prefix = pathlib.PurePath(p2_from_common_prefix).as_posix()

        p2_nb_slashes = p2_from_common_prefix.count("/")
        relative_p1 = "/".join(p2_nb_slashes * [".."]) + "/" + p1_from_common_prefix

        return relative_p1


def main():
    parser = argparse.ArgumentParser(
        prog="PyCut", description="PyCut CAM program - Read the doc!"
    )

    # argument
    parser.add_argument(
        "-j", "--job", dest="job", nargs="?", default=None, help="load job file | empty"
    )
    parser.add_argument(
        "-g",
        "--gcode",
        dest="gcode",
        nargs="?",
        default=None,
        help="load gcode file | empty",
    )

    # version info
    parser.add_argument("--version", action="version", version="f{VERSION}")

    options = parser.parse_args()

    app = QtWidgets.QApplication([])
    app.setApplicationName("PyCut")

    mainwindow = PyCutMainWindow(options)
    mainwindow.show()
    sys.exit(app.exec())


def main_profiled():
    """ """
    import profile
    import pstats

    outfile = "prof_pycut.bin"

    profile.run("main()", filename=outfile)
    p = pstats.Stats(outfile)

    # 1.
    p.sort_stats("cumulative")
    p.print_stats(100)  # p.print_stats(50)

    # 2.
    p.sort_stats("time")
    p.print_stats(100)  # p.print_stats(50)

    # 3.
    p.sort_stats("time", "cumulative").print_stats(0.5)  # (.5, 'init')


if __name__ == "__main__":
    """
    python -m cProfile -o test_parser.prof test_parser.py
    """
    filename = "pycut_cnc_all_letters_op.nc"

    main()
    # main_profiled()
