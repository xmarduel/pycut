
VERSION = "1_0_0"

import argparse
import sys

from typing import Dict

from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow

import webglviewer
import gcodefileviewer

import resources_rc


class GCodeSimulator(QtWidgets.QWidget):
    """ """
    def __init__(self, parent, options: Dict[str, str]):
        QtWidgets.QWidget.__init__(self)

        simulator_data =  {
            "gcode": options["gcode"],
            "cutterHeight": options["cutter_height"],
            "cutterDiameter": options["cutter_diameter"],
            "cutterAngle": options["cutter_angle"]
        }

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.gcode_glviewer = webglviewer.WebGlViewer(self)
        self.gcode_glviewer.set_data(simulator_data)
        self.gcode_glviewer.show_gcode()
        
        self.gcode_textviewer = gcodefileviewer.GCodeFileViewer(self, self.gcode_glviewer)
        self.gcode_textviewer.load_data(simulator_data["gcode"])

        layout.addWidget(self.gcode_glviewer)
        layout.addWidget(self.gcode_textviewer)

        layout.setStretch(0, 1)
        layout.setStretch(1, 0)


class MainWindow(QMainWindow):
    """ """

    def __init__(self, options: Dict[str, str]):
        QMainWindow.__init__(self)
        self.setGeometry(0, 0, 900, 700)

        fp = open(options["gcodefile"], "r")
        gcode = fp.read()
        fp.close()

        options["gcode"] = gcode

        self.simulator = GCodeSimulator(self, options)
        self.setCentralWidget(self.simulator)

        self.setWindowTitle(self.tr("GCode Simulator (WebGL)"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="simulator", description="Simulate gcode")

    # argument
    parser.add_argument("gcodefile", help="gcode file")
    # options
    parser.add_argument("--cutterdiameter", dest="cutter_diameter", type=float, default=6.0, help="cutter diameter (mm)")
    parser.add_argument("--cutterheight",   dest="cutter_height", type=float, default=30.0, help="cutter height (mm)")
    parser.add_argument("--cutterangle",   dest="cutter_angle", type=float, default=180.0, help="cutter angle (degree) - not used yet")
    
    # version info
    parser.add_argument("--version", action='version', version=f"{VERSION}")

    options = parser.parse_args()

    app = QApplication([])

    main_window = MainWindow(vars(options))
    main_window.show()

    res = app.exec()
    sys.exit(res)