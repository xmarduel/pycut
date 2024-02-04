from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore

from PySide6.QtCore import QRegularExpression


class GCodeSyntaxHighlightDelegate(QtWidgets.QStyledItemDelegate):
    """
    Html of QTextDocument can be painted

    Note: QPlainTextEdit document FAILS to be painted...
    """

    HTML_STYLES = {
        "comment": "color:darkGreen;font-style:italic",
        "keyword": "color:blue;font-weight:bold",
        "numbers": "color:brown",
        "numbersZ": "color:magenta",
    }

    # The rules
    rules = [
        # From ';' until a newline
        (r";[^\n]*", 0, HTML_STYLES["comment"]),
        # Positions Numeric literals
        (r"\b[XY][+-]?[0-9]+(?:\.[0-9]+)?\b", 0, HTML_STYLES["numbers"]),
        (r"\b[Z][+-]?[0-9]+(?:\.[0-9]+)?\b", 0, HTML_STYLES["numbersZ"]),
        # Others Numeric literals
        (r"\b[GSMF][0-9]+?\b", 0, HTML_STYLES["keyword"]),
    ]

    # Build a QRegularExpression for each pattern
    RULES = [(QRegularExpression(pat), index, style) for (pat, index, style) in rules]

    def __init__(self, parent):
        """ """
        super().__init__(parent)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        painter.save()

        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        painter.translate(options.rect.left(), options.rect.top())

        doc = QtGui.QTextDocument()
        doc.setHtml(self.makeHtml(index.data()))
        doc.drawContents(painter)

        painter.restore()

    def makeHtml(self, text: str):
        """ """
        html_parts = {}

        for expression, nth, style in self.RULES:
            nth = 0
            match = expression.match(text, offset=0)
            index = match.capturedStart()

            while index >= 0:
                # We actually want the index of the nth match
                index = match.capturedStart(nth)
                length = match.capturedLength(nth)

                ####self.setFormat(index, length, format)
                html_parts[index] = '<span style="%s">%s</span>' % (
                    style,
                    text[index : index + length],
                )

                # check the rest of the string

                match = expression.match(text, offset=index + length)
                index = match.capturedStart()

        # sorted by index
        keys = list(html_parts.keys())
        keys.sort()

        htmls = []
        for key in keys:
            htmls.append(html_parts[key])

        html = "<p>" + "&nbsp;".join(htmls) + "</p>"
        # print("------------------------------------------")
        # print("TEXT -> ", text)
        # print("HTML -> ", html)
        return html


class GCodeTableView(QtWidgets.QTableView):
    """ """

    def __init__(self, parent=None):
        """ """
        super().__init__(parent)

        self.parent = parent

        # table properties
        self.setObjectName("tblProgram")
        font = QtGui.QFont()
        font.setPointSize(9)
        self.setFont(font)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.AnyKeyPressed
            | QtWidgets.QAbstractItemView.DoubleClicked
            | QtWidgets.QAbstractItemView.EditKeyPressed
            | QtWidgets.QAbstractItemView.SelectedClicked
        )
        self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setGridStyle(QtCore.Qt.DashLine)
        self.horizontalHeader().setMinimumSectionSize(50)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().setVisible(True)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(12)
        self.setShowGrid(False)

    def setup(self):
        """ """
        delegate = GCodeSyntaxHighlightDelegate(self)
        self.setItemDelegateForColumn(1, delegate)
