"""
a GUI app to view/generate gears for hobbymat MD65 as SVG.

Tip: use blender to import the svg, solidify/bool items to produce
     an stl file for 3D printing.
Blender: when importing svg, curve to mesh, clean by hand the blender mesh
         at the teeths.
"""
VERSION = "1_0_0"

import sys
import argparse

from typing import Tuple

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtWebEngineWidgets

import gear_mainwindow
import svgviewer
import generate_gear_svg



class GearMainWindow(QtWidgets.QMainWindow):
    """ """

    def __init__(self, options):
        """ """
        super(GearMainWindow, self).__init__()

        self.ui = gear_mainwindow.Ui_mainwindow()
        self.ui.setupUi(self)

        self.signaler = MouseButtonSignaler()

        self.setWindowTitle("Gears")

        self.svg_viewer = self.setup_svg_viewer()
        self.svg_viewer.set_mainwindow(self)

        self.svg_viewer_2_gears_animated = self.setup_svg_viewer_2_gears_animated()
        self.svg_viewer_2_gears_animated.set_mainwindow(self)

        self.svg_viewer_2_gears_static = self.setup_svg_viewer_2_gears_static()
        self.svg_viewer_2_gears_static.set_mainwindow(self)

        self.ui.generate_svg.clicked.connect(self.cb_generate_svg)
        self.ui.save_svg.clicked.connect(self.cb_save_svg_file)

        self.ui.nb_teeths.valueChanged.connect(self.cb_nb_teeths)

        self.ui.foot_height.valueChanged.connect(self.cb_generate_svg)
        self.ui.head_height.valueChanged.connect(self.cb_generate_svg)
        self.ui.ratio_teeth_gap_base.valueChanged.connect(self.cb_generate_svg)
        self.ui.curvature.valueChanged.connect(self.cb_generate_svg)
        self.ui.ratio_teeth_head_base.valueChanged.connect(self.cb_generate_svg)
        self.ui.reinforcment_radius.valueChanged.connect(self.cb_generate_svg)

        self.signaler.installOn(self.ui.label_foot_height)
        self.signaler.installOn(self.ui.label_head_height)
        self.signaler.installOn(self.ui.label_ratio_teeth_gap_base)
        self.signaler.installOn(self.ui.label_curvature)
        self.signaler.installOn(self.ui.label_ratio_teeth_head_base)
        self.signaler.installOn(self.ui.label_reinforcment_radius)

        self.signaler.mouseButtonEvent.connect(self.mouseButtonEventHandler)

        self.ui.button_foot_height_reset.clicked.connect(self.cb_reset_foot_height)
        self.ui.button_head_height_reset.clicked.connect(self.cb_reset_head_height)
        self.ui.button_ratio_teeth_gap_base_reset.clicked.connect(self.cb_reset_ratio_teeth_gap_base)
        self.ui.button_curvature_reset.clicked.connect(self.cb_reset_curvature)
        self.ui.button_ratio_teeth_head_base_reset.clicked.connect(self.cb_reset_ratio_teeth_head_base)

        self.cb_reset_foot_height()
        self.cb_reset_head_height()
        self.cb_reset_curvature()
        self.cb_reset_ratio_teeth_gap_base()
        self.cb_reset_ratio_teeth_head_base()

        self.ui.actionTutorial.triggered.connect(self.cb_show_tutorial_qt)
        self.ui.actionAbout_Qt.triggered.connect(self.cb_show_about_qt)
        self.ui.actionAbout_Gears.triggered.connect(self.cb_show_about_gears)
    
    def mouseButtonEventHandler(self, obj: QtWidgets.QWidget, ev: QtGui.QMouseEvent):
        """ """
        name = obj.objectName()
        html_file = f"./doc/help_{name}.html"

        with open(html_file) as f:
            html = f.read()
            self.ui.tooltip_info.setHtml(html)
        
    def setup_svg_viewer(self) -> svgviewer.SvgViewer:
        """ """
        svg_widget = self.ui.svgwidget_1_gear
        layout = svg_widget.layout()

        svg_viewer = svgviewer.SvgViewer(svg_widget)
        svg_viewer.set_mainwindow(self)

        layout.addWidget(svg_viewer)
        layout.setStretch(0, 1)

        return svg_viewer
    
    def setup_svg_viewer_2_gears_animated(self) -> svgviewer.SvgWebEngineViewer:
        """ """
        svg_widget = self.ui.svgwidget_2_gears_animated
        layout = svg_widget.layout()

        svg_viewer_animated = svgviewer.SvgWebEngineViewer(svg_widget)
        svg_viewer_animated.set_mainwindow(self)

        layout.addWidget(svg_viewer_animated)
        layout.setStretch(0, 1)

        return svg_viewer_animated

    def setup_svg_viewer_2_gears_static(self) -> svgviewer.SvgWebEngineViewer:
        """ """
        svg_widget = self.ui.svgwidget_2_gears_static
        layout = svg_widget.layout()

        svg_viewer_static = svgviewer.SvgWebEngineViewer(svg_widget)
        svg_viewer_static.set_mainwindow(self)

        layout.addWidget(svg_viewer_static)
        layout.setStretch(0, 1)

        return svg_viewer_static

    def display_svg(self, svg_string:str):
        """ """
        self.svg_viewer.set_svg(svg_string)

    def display_svg_animated(self, svg_string:str):
        """ """
        self.svg_viewer_2_gears_animated.set_svg(svg_string)

    def display_svg_static(self, svg_string:str):
        """ """
        self.svg_viewer_2_gears_static.set_svg(svg_string)

    def cb_reset_foot_height(self):
        """ """
        self.ui.foot_height.setValue(1.25)

    def cb_reset_head_height(self):
        """ """
        self.ui.head_height.setValue(1.0)

    def cb_reset_curvature(self):
        """ """
        self.ui.curvature.setValue(9.0 / 4.0 * (self.ui.foot_height.value() + self.ui.head_height.value()))
    
    def cb_reset_ratio_teeth_gap_base(self):
        """ """
        self.ui.ratio_teeth_gap_base.setValue(0.6)

    def cb_reset_ratio_teeth_head_base(self):
        """ """
        self.ui.ratio_teeth_head_base.setValue(0.4)

    def cb_nb_teeths(self):
        """ """
        nb_teeths = self.ui.nb_teeths.value()
        modul = self.ui.modul.value()

        gear_diameter = modul * nb_teeths

        self.ui.gear_diameter.setValue(gear_diameter)

        self.cb_generate_svg()
    
    def cb_generate_svg(self) -> Tuple[str, str, str]:
        """ """
        maker = generate_gear_svg.GearMaker()
        generate_gear_svg.GearMaker.set_params(
            {
                "NB_TEETHS": self.ui.nb_teeths.value(),
                "FOOT_HEIGHT": self.ui.foot_height.value(),
                "HEAD_HEIGHT": self.ui.head_height.value(),
                "TEETH_CURVATURE": self.ui.curvature.value(),
                "RATIO_TEETH_GAP_BASE": self.ui.ratio_teeth_gap_base.value(),
                "RATIO_TEETH_HEAD_BASE": self.ui.ratio_teeth_head_base.value(),
                "REINFORCMENT_RADIUS": self.ui.reinforcment_radius.value()
            }
        )

        svg1 = maker.make_svg_gear()
        self.display_svg(svg1)

        svg2 = maker.make_svg_gears_static()
        self.display_svg_static(svg2)

        svg3 = maker.make_svg_gears_animated()
        self.display_svg_animated(svg3)

        return (svg1, svg2, svg3)

    def cb_save_svg_file(self):
        """ """
        maker = generate_gear_svg.GearMaker()
        generate_gear_svg.GearMaker.set_params(
            {
                "NB_TEETHS": self.ui.nb_teeths.value(),
                "FOOT_HEIGHT": self.ui.foot_height.value(),
                "HEAD_HEIGHT": self.ui.head_height.value(),
                "TEETH_CURVATURE": self.ui.curvature.value(),
                "RATIO_TEETH_GAP_BASE": self.ui.ratio_teeth_gap_base.value(),
                "RATIO_TEETH_HEAD_BASE": self.ui.ratio_teeth_head_base.value(),
                "REINFORCMENT_RADIUS": self.ui.reinforcment_radius.value()
            }
        )

        svg = maker.make_svg_gear()
        self.display_svg(svg)

        fp = open("gear_%i.svg" % self.ui.nb_teeths.value(), "w")
        fp.write(svg)
        fp.close()

        svg = maker.make_svg_gears_static()
        self.display_svg_static(svg)

        fp = open("gears_%i_static.svg" % self.ui.nb_teeths.value(), "w")
        fp.write(svg)
        fp.close()

        svg = maker.make_svg_gears_animated()
        self.display_svg_animated(svg)

        fp = open("gears_%i_animated.svg" % self.ui.nb_teeths.value(), "w")
        fp.write(svg)
        fp.close()

    def cb_show_tutorial_qt(self):
        """ """
        dlg = QtWidgets.QDialog(self)

        htmlview = QtWebEngineWidgets.QWebEngineView(dlg)
        htmlview.setMinimumSize(1100, 600)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(htmlview)

        dlg.setLayout(main_layout)
        dlg.setWindowTitle("PyCut Tutorial")
        dlg.setModal(True)

        filename = "./doc/gears.html"
        file = QtCore.QFile(filename)
        if file.open(QtCore.QIODevice.ReadOnly):
            data = str(file.readAll(), "utf-8")  # explicit encoding
        else:
            data = "ERROR"

        file.close()

        htmlview.setHtml(data, baseUrl=QtCore.QUrl("qrc:/"))

        dlg.show()

    def cb_show_about_qt(self):
        QtWidgets.QApplication.instance().aboutQt()

    def cb_show_about_gears(self):
        dlg = QtWidgets.QDialog(self)

        view = QtWidgets.QTextBrowser(dlg)
        view.setReadOnly(True)
        view.setMinimumSize(500, 500)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(view)

        dlg.setLayout(main_layout)
        dlg.setWindowTitle("Gears Relnotes")
        dlg.setModal(True)

        try:
            view.setSource(QtCore.QUrl.fromLocalFile("./doc/about.html"))
        except Exception as msg:
            view.setHtml(self.notfound % {"message": str(msg)})

        dlg.show()


class MouseButtonSignaler(QtCore.QObject):
    """ 
    click on QLabel
    """
    mouseButtonEvent = QtCore.Signal(QtWidgets.QWidget, QtGui.QMouseEvent)

    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
  
    def installOn(self, widget: QtWidgets.QWidget):
        """ """
        widget.installEventFilter(self)

    def eventFilter(self, obj: QtCore.QObject, ev: QtCore.QEvent):
        """ """
        ev_ok = ev.type() == QtCore.QEvent.MouseButtonRelease

        if ev_ok and obj.isWidgetType():
            self.mouseButtonEvent.emit(obj, ev)

        return False


def main():
    parser = argparse.ArgumentParser(
        prog="gear", description="Read the doc!"
    )

    # version info
    parser.add_argument("--version", action="version", version="f{VERSION}")

    options = parser.parse_args()

    app = QtWidgets.QApplication([])
    app.setApplicationName("gear")

    mainwindow = GearMainWindow(options)
    mainwindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    """
    """
    main()
