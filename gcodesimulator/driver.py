
VERSION = "1_0_0"

import sys
import argparse

from typing import Dict

from PySide6.QtWidgets import QApplication, QMainWindow

import viewer


class MainWindow(QMainWindow):
    """ """

    def __init__(self, options: Dict[str, str]):
        QMainWindow.__init__(self)

        fp = open(options["gcodefile"], "r")
        gcode = fp.read()
        fp.close()

        options["gcode"] = gcode

        self.simulator = viewer.GCodeViewer(self, options)
        self.setCentralWidget(self.simulator)

        self.setWindowTitle(self.tr("GCode Simulator (QOpenGL)"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="driver", description="Simulate gcode")

    # argument
    parser.add_argument("gcodefile", help="gcode file")
    # options
    parser.add_argument("--cutterdiameter", dest="cutter_diameter", type=float, default=6.0, help="cutter diameter (mm)")
    parser.add_argument("--cutterheight", dest="cutter_height", type=float, default=30.0, help="cutter height (mm)")
    parser.add_argument("--cutterangle", dest="cutter_angle", type=float, default=180.0, help="cutter angle (degree) - not used yet")
    parser.add_argument("--candleparser", dest="use_candle_parser", action='store_true', default=False, help="use candle parser")
    
    # version info
    parser.add_argument("--version", action='version', version=f"{VERSION}")

    options = parser.parse_args()

    app = QApplication([])

    main_window = MainWindow(vars(options))
    main_window.show()

    res = app.exec()
    sys.exit(res)