

from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore

import gcodesimulator.gcode_syntaxhighlighter as gcode_syntaxhighlighter
from gcodesimulator.python.parser.gcodeminiparser import GcodeMiniParser


class GCodeFileViewer(QtWidgets.QPlainTextEdit):
    '''
    '''
    def __init__(self, parent, webgl_viewer):
        '''
        '''
        super().__init__()

        self.webgl_viewer = webgl_viewer
        self.gcode = ""

        # current "selected" line in data
        self.curr_line_nb = -1

        self.setMinimumWidth(100)
        self.setMaximumWidth(280)

        self.miniparser = GcodeMiniParser()

    def load_data(self, gcode):
        '''
        '''
        self.gcode = gcode
        self.curr_line_nb = -1

        self.setPlainText(gcode)
        gcode_syntaxhighlighter.GCodeSyntaxHighlighter(self.document())

        self.miniparser.reset()
        self.miniparser.parse_gcode(gcode)
        self.miniparser.eval_path_time()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        '''
        '''
        cursor = self.cursorForPosition(event.pos())
        
        self.curr_line_nb = cursor.blockNumber()
        # from the python "miniparser"
        simtime = self.miniparser.path_time_map[self.curr_line_nb]

        self.webgl_viewer.show_simulation_at_time(simtime)

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        '''
        '''
        cursor = self.cursorForPosition(event.pos())
        
        self.curr_line_nb = cursor.blockNumber()
        # from the python "miniparser"
        simtime = self.miniparser.path_time_map[self.curr_line_nb]

        self.webgl_viewer.show_simulation_at_time(simtime)

        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        '''
        '''
        super().keyPressEvent(event)

        if self.curr_line_nb > -1:
            if event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_Up:
                if event.key() == QtCore.Qt.Key_Down:
                    self.curr_line_nb += 1
                elif event.key() == QtCore.Qt.Key_Up:
                    self.curr_line_nb -= 1

                # from the python "miniparser"
                simtime = self.miniparser.path_time_map[self.curr_line_nb]

                self.webgl_viewer.show_simulation_at_time(simtime)