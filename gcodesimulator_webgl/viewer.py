"""
the viewer includes
- the gcode simulator - in webgl + its controls
- the gcode file browser
"""

from typing import Dict

from PySide6 import QtWidgets

from gcodesimulator_webgl import webglviewer
from gcodesimulator_webgl import gcodefileviewer


class GCodeViewer(QtWidgets.QWidget):
    """ """

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.gcode_glviewer = webglviewer.WebGlViewer(self)
        self.gcode_textbrowser = gcodefileviewer.GCodeFileViewer(
            self, self.gcode_glviewer
        )

        layout.addWidget(self.gcode_glviewer)
        layout.addWidget(self.gcode_textbrowser)

        layout.setStretch(0, 1)
        layout.setStretch(1, 0)

    def set_data(self, simulator_data: Dict[str, str]):
        self.gcode_glviewer.set_data(simulator_data)
        self.gcode_glviewer.show_gcode()

        self.gcode_textbrowser.load_data(simulator_data["gcode"])
