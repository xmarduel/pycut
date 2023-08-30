
from PySide6.QtCore import QRegularExpression

from PySide6.QtGui import QColor
from PySide6.QtGui import QTextCharFormat
from PySide6.QtGui import QFont
from PySide6.QtGui import QSyntaxHighlighter


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


STYLES = {
    'comment': format('darkGreen', 'italic'),
    'keyword': format('blue', 'bold'),
    'tool': format('red', 'bold'),
    'poskeyword': format('blue'),
    'numbers': format('brown'),
    'numbersZ': format('magenta'),
}


class GCodeSyntaxHighlighter (QSyntaxHighlighter):
    """
    Syntax highlighter for the GCode language.
    """
    def __init__(self, document):
        super(GCodeSyntaxHighlighter, self).__init__(document)

        # The rules
        rules = [

            # From ';' until a newline
            (r'[;(][^\n]*', 0, STYLES['comment']),

            # Positions Numeric literals
            (r'\b[XY][+-]?[0-9]+(?:\.[0-9]+)?\b', 0, STYLES['numbers']),
            (r'\b[Z][+-]?[0-9]+(?:\.[0-9]+)?\b', 0, STYLES['numbersZ']),

            # Others Positional Numeric literals
            (r'\b[R][0-9]+(?:\.[0-9]+)?\b', 0, STYLES['poskeyword']),

            # Others Numeric literals
            (r'\b[GSMFH][0-9]+(?:\.[0-9]+)?\b', 0, STYLES['keyword']),

            # Tools
            (r'\b[T][0-9]+(?:\.[0-9]+)?\b', 0, STYLES['tool'])
        ]

        # Build a QRegularExpression for each pattern
        self.rules = [ (QRegularExpression(pat), index, fmt) for (pat, index, fmt) in rules ]

    def highlightBlock(self, text):
        """
        Apply syntax highlighting to the given block of text.
        """
        for expression, nth, format in self.rules:
            nth = 0
            match = expression.match(text, offset=0)
            index = match.capturedStart()

            while index >= 0:
                # We actually want the index of the nth match
                index = match.capturedStart(nth)
                length = match.capturedLength(nth)
                self.setFormat(index, length, format)
                # check the rest of the string

                match = expression.match(text, offset=index + length)
                index = match.capturedStart()

        self.setCurrentBlockState(0)

    def match_multiline(self, text, delimiter, in_state, style):
        """
        """
        return False
