# This Python file uses the following encoding: utf-8

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6 import QtSvg
from PySide6 import QtSvgWidgets

class MaterialWidget(QtSvgWidgets.QSvgWidget):
    '''
    Display as nice SVG picture the settings "clearance" and "thickness"

    Unfortunately it does not scale "nicely" when using inches.
    So all values are in mm

    mm:
      -> step size of spinboxes is "1.0"
      -> update "display values" to show "inch" values

    inch:
      -> step size of spinboxes is "1.0/25.4" = 0.04
      -> update "display values" to show "inch" values


    '''
    def __init__(self, parent: QtWidgets.QWidget=None):
        super(MaterialWidget, self).__init__(parent)

        renderer = self.renderer()
        renderer.setAspectRatioMode(QtCore.Qt.KeepAspectRatio)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self)

        parent.setLayout(layout)

        self.material_units = "mm"
 
    def display_unit(self, material_units: str):
        '''
        '''
        self.material_units = material_units

    def display_material(self, thickness=50, clearance=10):
        '''
        '''
        thickness_level1 = 75 + thickness
        thickness_level2 = 75 + thickness + 10

        clearance_level1 = 75 - clearance

        clearance_display_value = clearance
        thickness_display_value = thickness

        if self.material_units == "inch":
            clearance_display_value = float(clearance) / 25.4
            thickness_display_value = float(thickness) / 25.4

        img_str = '''
        <svg viewBox='0 0 200 150' xmlns='http://www.w3.org/2000/svg'>
        <g>
            <rect x="90" y="75" width="100" height="%(thickness)d" fill="white" stroke="black" stroke-width="5px" stroke-linejoin="round" />
            <rect x="80" y="85" width="100" height="%(thickness)d" fill="white" stroke="black" stroke-width="5px" stroke-linejoin="round"/>

            <polyline points="80,85    90,75  190,75                   180,85                    80,85" fill="white" stroke="black" stroke-width="5px" stroke-linejoin="round"/>
            <polyline points="180,85  190,75  190,%(thickness_level1)d 180,%(thickness_level2)d 180,85" fill="white" stroke="black" stroke-width="5px" stroke-linejoin="round"/>

            <!-- bit -->
            <polyline points="130,0 130,%(clearance_level1)d 150,%(clearance_level1)d  150,0" fill="white" stroke="black" stroke-width="5px"/>

            <!-- legends levels -->
            <polyline points="25,%(clearance_level1)d   70,%(clearance_level1)d" fill="white" stroke="black" stroke-width="3px" stroke-dasharray="8,8"/>
            <polyline points="25,85                     70,85"                   fill="white" stroke="black" stroke-width="3px" stroke-dasharray="8,8"/>
            <polyline points="25,%(thickness_level2)d   70,%(thickness_level2)d" fill="white" stroke="black" stroke-width="3px" stroke-dasharray="8,8"/>

            <!-- legends -->
            <text x="0" y="%(clearance_level1)d" fill="black">%(clearance_disp).2f</text>
            <text x="0" y="90"                   fill="black">0.0</text>
            <text x="0" y="%(thickness_level2)d" fill="black">%(thickness_disp).2f</text>

        </g>
        </svg>''' % {"thickness": thickness,"thickness_disp": thickness_display_value, "clearance_disp": clearance_display_value, "thickness_level1": thickness_level1, "thickness_level2": thickness_level2, "clearance_level1": clearance_level1}

        img = bytes(img_str, encoding='utf-8')

        self.load(img)
