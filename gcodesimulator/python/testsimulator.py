

from xml.dom.expatbuilder import parseFragmentString

import sys

from PySide6 import QtWidgets

import gcodesimulator.python.widgets.glwidget_container as glwidget_simulator_container


class TestMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(TestMainWindow, self).__init__()

        self.setWindowTitle("Test GL")

        gl_central_widget = glwidget_simulator_container.GLWidgetContainer(self)
        gl_central_widget.loadFile("jscut.gcode")

        self.setCentralWidget(gl_central_widget)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    mainwindow = TestMainWindow()
    mainwindow.show()
    sys.exit(app.exec())