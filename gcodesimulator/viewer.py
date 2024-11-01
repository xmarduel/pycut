"""
the viewer includes
- the gcode simulator - in pyside6-opengl + its controls
- the gcode file browser
"""

import math

from typing import Any, Dict

from PySide6 import QtWidgets

from gcodesimulator import glviewer
from gcodesimulator import gcodefileviewer


class GCodeViewer(QtWidgets.QWidget):
    """ """

    def __init__(self, parent: QtWidgets.QWidget, options: Dict[str, Any]):
        QtWidgets.QWidget.__init__(self)

        self.gcode = gcode = options["gcode"]
        self.cutter_diameter = cutter_diameter = options["cutter_diameter"]
        self.cutter_height = cutter_height = options["cutter_height"]
        self.cutter_angle = cutter_angle = options["cutter_angle"]

        self.use_candle_parser = use_candle_parser = options["use_candle_parser"]

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.gcode_textbrowser = gcodefileviewer.GCodeFileViewer(self)
        self.gcode_textbrowser.setMinimumWidth(250)
        self.gcode_textbrowser.load_data(gcode, use_candle_parser)

        self.gl_with_controls_layout = QtWidgets.QVBoxLayout()

        self.gcode_glviewer = glviewer.GLView(
            gcode, cutter_diameter, cutter_height, cutter_angle, use_candle_parser
        )
        self.gl_with_controls_layout.addWidget(self.gcode_glviewer)

        self.controls = glviewer.SimulationControls(
            self, self.gcode_glviewer, self.gcode_textbrowser
        )
        self.gl_with_controls_layout.addWidget(self.controls)

        self.gl_with_controls_layout.setStretch(0, 1)
        self.gl_with_controls_layout.setStretch(1, 0)

        layout.addLayout(self.gl_with_controls_layout)
        layout.addWidget(self.gcode_textbrowser)

        layout.setStretch(0, 0)
        layout.setStretch(1, 0)

    def set_simtime_from_textbrowser(self, simtime: float):
        """slot on signal from gcode text browser "select line" """
        tick = math.floor(simtime * 1000)
        self.controls.OnSimAtTickFromTextBrowser(tick)
