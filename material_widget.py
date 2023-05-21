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
        clearance_level1 = 85 - clearance

        clearance_display_value = clearance
        thickness_display_value = thickness

        if self.material_units == "inch":
            clearance_display_value = float(clearance) / 25.4
            thickness_display_value = float(thickness) / 25.4

        img_str = '''
        <svg viewBox='0 0 200 150' xmlns='http://www.w3.org/2000/svg'>
        <g>
            <!--  <rect x="90" y="85" width="100" height="%(thickness)d" fill="green" stroke="black" stroke-width="2px"   stroke-linejoin="round"/> --> <!-- not visible -->
            <rect x="80" y="95" width="100" height="%(thickness)d" fill="red"   stroke="black" stroke-width="2px"  stroke-linejoin="round"/> -->

            <polyline points="80,95    90,85  190,85                   180,95                    80,95"  fill="green" stroke="black" stroke-width="2px"  stroke-linejoin="round"/>
            <polyline points="180,95  190,85  190,%(thickness_level1)d 180,%(thickness_level2)d  180,95" fill="blue"  stroke="black" stroke-width="2px"  stroke-linejoin="round"/>

            <!-- bit -->
            <polyline points="130,%(bit_top)d 130,%(clearance_level1)d 150,%(clearance_level1)d  150,%(bit_top)d" fill="white" stroke="black" stroke-width="2px"/>
            <!-- bit base -->
            <rect x="100" y="%(bit_top)d" width="100" height="10" fill="black"   stroke="black" stroke-width="2px"  stroke-linejoin="round"/> -->


            <!-- legends levels -->
            <polyline points="25,%(clearance_level1)d   70,%(clearance_level1)d" fill="white" stroke="black" stroke-width="2px" stroke-dasharray="8,8"/>
            <polyline points="25,85                     70,85"                   fill="white" stroke="black" stroke-width="2px" stroke-dasharray="8,8"/>
            <polyline points="25,%(thickness_level2)d   70,%(thickness_level2)d" fill="white" stroke="black" stroke-width="2px" stroke-dasharray="8,8"/>

            <!-- machine top -->
            <rect x="50" y="0" width="150" height="10" fill="black"   stroke="black" stroke-width="2px"  stroke-linejoin="round"/> -->

            <!-- legends -->
            <text x="0" y="%(clearance_level1)d" fill="black">%(clearance_disp).2f</text>
            <text x="0" y="90"                   fill="black">0.0</text>
            <text x="0" y="%(thickness_level2)d" fill="black">%(thickness_disp).2f</text>

        </g>
        </svg>''' % {
            "thickness": 2*thickness,
            "thickness_disp": thickness_display_value, 
            "clearance_disp": clearance_display_value, 
            "thickness_level1": 85 + 2*thickness, 
            "thickness_level2": 95 + 2*thickness, 
            "clearance_level1": clearance_level1,
            "bit_top": clearance_level1 - 50
        }

        img = bytes(img_str, encoding='utf-8')

        self.load(img)
