from typing import List
import math

from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore

import gcodesimulator_python.gcode_syntaxhighlighter as gcode_syntaxhighlighter
from gcodesimulator_python.gcodeminiparser import GcodeMiniParser


class GCodeFileViewerLineNumberArea(QtWidgets.QWidget):
    """ """

    def __init__(self, viewer: "GCodeFileViewer"):
        super().__init__(viewer)
        self.viewer = viewer

    def sizeHint(self):
        return QtCore.QSize(self.viewer.lineNumberAreaWidth(), 0)

    def paintEvent(self, event: QtGui.QPaintEvent):
        self.viewer.lineNumberAreaPaintEvent(event)
        super().paintEvent(event)


class GCodeFileViewer(QtWidgets.QPlainTextEdit):
    """ """

    def __init__(self, simulator):
        """ """
        super().__init__(simulator)

        self.simulator = simulator
        self.gcode = ""
        self.line_number_area = GCodeFileViewerLineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        # current "selected" line in data
        self.curr_line_no = 0

        # a mapping line_no -> cursor position
        self.line_no_2_position = None

        self.setMinimumWidth(100)
        self.setMaximumWidth(280)

        self.miniparser = GcodeMiniParser()

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def load_data(self, gcode, use_candle_parser: bool):
        """ """
        self.gcode = gcode
        self.curr_line_no = -1

        self.setPlainText(gcode)
        gcode_syntaxhighlighter.GCodeSyntaxHighlighter(self.document())

        self.miniparser.reset()

        if use_candle_parser == False:
            self.miniparser.parse_gcode(gcode)
        else:
            self.miniparser.parse_gcode_use_candle_parser(gcode)

        """
        very strange : 
        
           Qt : block = self.document().findBlockByLineNumber(self.curr_line_no)
           gives wrong results: the block is at the wrong position...
           
           so I make my own mapping line_no -> cursor position
        """
        self.line_no_2_position = self.make_line_no_position_map()

    def make_line_no_position_map(self):
        """ """
        line_no_2_position = {0: 0}  # first line

        for line_no, line in enumerate(self.gcode.split("\n")):
            line_no_2_position[line_no + 1] = 1 + line_no_2_position[line_no] + len(line)

        return line_no_2_position

    def highligh_current_line(self):
        """ """
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
        """
        set the cursor on the implied position
        """
        # print("on_simtime_from_js", simtime)

        # set cursor at line
        idx = self.miniparser.get_mvt_index_for_time(simtime)
        # print("-> path_idx", idx)
        try:
            if idx not in self.miniparser.path_idx_line_no:
                idx0 = idx
                while idx0 not in self.miniparser.path_idx_line_no:
                    idx0 -= 1
                    if idx0 == 0:
                        break
                idx = idx0

            self.curr_line_no = self.miniparser.path_idx_line_no[idx]

            # ---- small fix: if line is a comment, go to the next one

            # ---------------------------

            print("-> step : curr_line_no", self.curr_line_no)

            block = self.document().findBlockByLineNumber(self.curr_line_no)
            cursor = QtGui.QTextCursor(block)
            self.setTextCursor(cursor)

            # this is BAD!
            print("-> step: cursor pos", cursor.position(), " ==> line_no = ", cursor.blockNumber())

            if True:
                # fix Qt "findBlockByLineNumber" !
                pos = self.line_no_2_position[self.curr_line_no]
                cursor.setPosition(pos)
                self.setTextCursor(cursor)

            print("-> step: cursor pos", cursor.position(), " ==> line_no = ", cursor.blockNumber())

            self.highligh_current_line()

        except Exception as e:
            print(e)
            pass

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """ """
        cursor = self.cursorForPosition(event.pos())
        print("-> mouse: cursor pos", cursor.position(), " ==> line_no = ", cursor.blockNumber())
        self.curr_line_no = cursor.blockNumber()

        # from the python "miniparser"
        while self.curr_line_no not in self.miniparser.line_no_time_map and self.curr_line_no > 0:
            self.curr_line_no -= 1

        if self.curr_line_no == 0:
            simtime = 0
        else:
            simtime = self.miniparser.line_no_time_map[self.curr_line_no]

        self.simulator.set_simtime_from_textbrowser(simtime)

        super().mousePressEvent(event)

        self.highligh_current_line()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """ """
        super().keyPressEvent(event)

        self.highligh_current_line()

        if self.curr_line_no > -1:
            if event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_Up:
                if event.key() == QtCore.Qt.Key_Down:
                    self.curr_line_no += 1
                elif event.key() == QtCore.Qt.Key_Up:
                    self.curr_line_no -= 1

                # from the python "miniparser"
                try:
                    simtime = self.miniparser.line_no_time_map[self.curr_line_no]
                    self.simulator.set_simtime_from_textbrowser(simtime)
                except Exception as e:
                    pass

    # line numbering area

    def lineNumberAreaPaintEvent(self, event: QtGui.QPaintEvent):
        """ """
        painter = QtGui.QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QtCore.Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = " %d " % blockNumber
                painter.setPen(QtCore.Qt.black)
                painter.drawText(
                    0, top, self.line_number_area.width(), self.fontMetrics().height(), QtCore.Qt.AlignRight, number
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def lineNumberAreaWidth(self) -> int:
        digits = 1
        the_max = max(1, self.blockCount())
        while the_max >= 10:
            the_max /= 10
            digits = digits + 1

        # space = 3 + self.fontMetrics().width(QtGui.QLatin1Char('9')) * digits
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits + 6

        return space

    @QtCore.Slot(int)
    def updateLineNumberAreaWidth(self, newBlockCount: int):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @QtCore.Slot()
    def highlightCurrentLine(self):
        extraSelections: List[QtWidgets.QTextEdit.ExtraSelection] = []

        if self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()

            lineColor = QtGui.QColor(QtCore.Qt.yellow).lighter(160)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    @QtCore.Slot(QtCore.QRect, int)
    def updateLineNumberArea(self, rect: QtCore.QRect, dy: int):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, e: QtGui.QResizeEvent):
        """ """
        super().resizeEvent(e)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
