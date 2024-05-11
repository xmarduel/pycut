"""
a GUI app to view/generate gears for hobbymat MD65 as SVG.

Tip: use blender to import the svg, solidify/bool items to produce
     an stl file for 3D printing.
"""
VERSION = "1_0_0"

import sys
import argparse

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

import gear_mainwindow
import svgviewer
import generate_gear_svg


SVG_GEAR_TPL = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   width="400mm"
   height="400mm"
   viewBox="-200 -200 400 400"
   version="1.1"
   id="gear_hobbymat">
   <g>
     %(GEAR)s
     %(REINFORCEMENT)s
     %(BEARING)s
   </g>
</svg>
"""

class GearMainWindow(QtWidgets.QMainWindow):
    """ """

    def __init__(self, options):
        """ """
        super(GearMainWindow, self).__init__()

        self.ui = gear_mainwindow.Ui_mainwindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Gears")

        self.svg_viewer = self.setup_svg_viewer()
        self.svg_viewer.set_mainwindow(self)

        self.ui.generate_svg.clicked.connect(self.cb_generate_svg)
        self.ui.load_svg.clicked.connect(self.cb_load_svg_file)
        self.ui.save_svg.clicked.connect(self.cb_save_svg_file)

        self.ui.nb_teeths.valueChanged.connect(self.cb_generate_svg)

        self.ui.foot_height.valueChanged.connect(self.cb_generate_svg)
        self.ui.head_height.valueChanged.connect(self.cb_generate_svg)
        self.ui.curvature.valueChanged.connect(self.cb_generate_svg)
        self.ui.ratio_gear_gap_teeth.valueChanged.connect(self.cb_generate_svg)
        self.ui.ratio_teeth_head_base.valueChanged.connect(self.cb_generate_svg)
        self.ui.reinforcment_radius.valueChanged.connect(self.cb_generate_svg)

        self.ui.button_foot_height_reset.clicked.connect(self.cb_reset_foot_height)
        self.ui.button_head_height_reset.clicked.connect(self.cb_reset_head_height)
        self.ui.button_curvature_reset.clicked.connect(self.cb_reset_curvature)
        self.ui.button_ratio_gear_gap_teeth_reset.clicked.connect(self.cb_reset_ratio_gear_gap_teeth)
        self.ui.button_ratio_teeth_head_base_reset.clicked.connect(self.cb_reset_ratio_teeth_head_base)

        self.cb_reset_foot_height()
        self.cb_reset_head_height()
        self.cb_reset_curvature()
        self.cb_reset_ratio_gear_gap_teeth()
        self.cb_reset_ratio_teeth_head_base()
    
    def setup_svg_viewer(self):
        """ """
        svg_widget = self.ui.svg_viewer
        layout = svg_widget.layout()

        svg_viewer = svgviewer.XSvgViewer(svg_widget)
        svg_viewer.set_mainwindow(self)

        layout.addWidget(svg_viewer)
        layout.setStretch(0, 1)

        return svg_viewer
    
    def display_svg_file(self, svg_file:str):
        """ """
        if svg_file is None:
            return

        fp = open(svg_file, "r")
        svg = fp.read()
        fp.close()

        self.svg_viewer.set_svg(svg)

    def display_svg_string(self, svg_string:str):
        """ """
        self.svg_viewer.set_svg(svg_string)

    def cb_load_svg_file(self):
        """ """
        # select svg file
        xfilter = "SVG Files (*.svg)"
        svgfile, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="load file", dir=".", filter=xfilter
        )

        self.display_svg_file(svgfile)

    def cb_reset_foot_height(self):
        """ """
        self.ui.foot_height.setValue(1.25)

    def cb_reset_head_height(self):
        """ """
        self.ui.head_height.setValue(1.0)

    def cb_reset_curvature(self):
        """ """
        self.ui.curvature.setValue(9.0 / 4.0 * (self.ui.foot_height.value() + self.ui.head_height.value()))
    
    def cb_reset_ratio_gear_gap_teeth(self):
        """ """
        self.ui.ratio_gear_gap_teeth.setValue(7.0 / 5.0)

    def cb_reset_ratio_teeth_head_base(self):
        """ """
        self.ui.ratio_teeth_head_base.setValue(3.0 / 7.0)

    def cb_generate_svg(self) -> str:
        """ """
        maker = generate_gear_svg.GearMaker()
        generate_gear_svg.GearMaker.set_params(
            {
                "NB_TEETHS": self.ui.nb_teeths.value(),
                "FOOT_HEIGHT": self.ui.foot_height.value(),
                "HEAD_HEIGHT": self.ui.head_height.value(),
                "TEETH_CURVATURE": self.ui.curvature.value(),
                "RATIO_GEAR_GAP_TEETH": self.ui.ratio_gear_gap_teeth.value(),
                "RATIO_TEETH_HEAD_BASE": self.ui.ratio_teeth_head_base.value(),
                "REINFORCMENT_RADIUS": self.ui.reinforcment_radius.value()
            }
        )

        svg = SVG_GEAR_TPL %  { 
            "GEAR": maker.get_gear(),
            "REINFORCEMENT": maker.get_reinforcement(),
            "BEARING": maker.get_bearing() 
        }

        self.display_svg_string(svg)

        return svg

    def cb_save_svg_file(self):
        """ """
        svg = self.cb_generate_svg()

        fp = open("gear_%i.svg" % self.ui.nb_teeths.value(), "w")
        fp.write(svg)
        fp.close()


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
