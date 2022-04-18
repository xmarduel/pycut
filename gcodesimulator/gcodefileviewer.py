

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
        self.curr_line_no = -1

        self.setMinimumWidth(100)
        self.setMaximumWidth(280)

        self.miniparser = GcodeMiniParser()

    def load_data(self, gcode):
        '''
        '''
        self.gcode = gcode
        self.curr_line_no = -1

        self.setPlainText(gcode)
        gcode_syntaxhighlighter.GCodeSyntaxHighlighter(self.document())

        self.miniparser.reset()
        self.miniparser.parse_gcode(gcode)

    def highlightCurrentLine(self):
        '''
        '''
        extraSelections = []

        selection = QtWidgets.QTextEdit.ExtraSelection()

        lineColor = QtGui.QColor(QtGui.Qt.yellow).lighter(160)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extraSelections.append(selection)    

        self.setExtraSelections(extraSelections)

    @QtCore.Slot(float) 
    def on_simtime_from_js(self, simtime: float):
        '''
        set the cursor on the implied position
        '''
        #print("on_simtime_from_js", simtime)

        # set cursor at line
        idx = self.miniparser.get_path_idx_for_time(simtime)
        #print("-> path_idx", idx)
        try:
            if idx not in self.miniparser.path_idx_line_no:
                idx0 = idx
                while idx0 not in self.miniparser.path_idx_line_no:
                    idx0 -= 1
                    if idx0 == 0:
                        break
                idx = idx0
            
            self.curr_line_no = self.miniparser.path_idx_line_no[idx]
            print("-> curr_line_no", self.curr_line_no)
        
            block = self.document().findBlockByLineNumber(self.curr_line_no)
            cursor = QtGui.QTextCursor(block)
            self.setTextCursor(cursor)
            #self.moveCursor(QtGui.QTextCursor.End)

            self.highlightCurrentLine()


        except Exception as e:
            print(e)
            pass

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        '''
        '''
        cursor = self.cursorForPosition(event.pos())
        print("-> cursor pos", cursor.position())
        self.curr_line_no = cursor.blockNumber()

        # from the python "miniparser"
        simtime = self.miniparser.line_no_time_map[self.curr_line_no]

        self.webgl_viewer.show_simulation_at_time(simtime)

        super().mousePressEvent(event)

        self.highlightCurrentLine()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        '''
        '''
        super().keyPressEvent(event)

        self.highlightCurrentLine()

        if self.curr_line_no > -1:
            if event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_Up:
                if event.key() == QtCore.Qt.Key_Down:
                    self.curr_line_no += 1
                elif event.key() == QtCore.Qt.Key_Up:
                    self.curr_line_no -= 1

                # from the python "miniparser"
                simtime = self.miniparser.line_no_time_map[self.curr_line_no]

                self.webgl_viewer.show_simulation_at_time(simtime)