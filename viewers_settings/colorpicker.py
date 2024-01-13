from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class ColorPicker(QtWidgets.QWidget):
    '''
    '''
    colorSelected = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.m_layout = QtWidgets.QHBoxLayout(self)
        self.m_frame = QtWidgets.QFrame(self)
        self.m_button = QtWidgets.QToolButton(self)

        self.m_frame.setFrameShape(QtWidgets.QFrame.Box)

        self.m_button.setText("...")
        self.m_color = QtGui.QColor("black")

        self.m_layout.setSpacing(10)
        self.m_layout.setContentsMargins(0, 0, 0, 0)
        self.m_layout.addWidget(self.m_frame, 1)
        self.m_layout.addWidget(self.m_button)


        self.m_button.clicked.connect(self.onButtonClicked)

    def color(self) -> QtGui.QColor:
        return self.m_color

    def setColor(self, color: QtGui.QColor):
        self.m_color = color
        self.m_frame.setStyleSheet("background-color: %s" % color.name())

    def onButtonClicked(self):
        color = QtWidgets.QColorDialog.getColor(self.m_color, self)

        if color.isValid():
            self.setColor(color)
            self.colorSelected.emit(color)

