from typing import List

from PySide6.QtCore import QElapsedTimer
from PySide6.QtCore import QFile
from PySide6.QtCore import QTextStream
from PySide6.QtCore import QIODevice
from PySide6.QtCore import qIsNaN

from PySide6.QtGui import QVector3D

from gcodesimulator_python.candle_parser.gcodeviewparse import GcodeViewParse
from gcodesimulator_python.candle_parser.gcodepreprocessorutils import (
    GcodePreprocessorUtils,
)
from gcodesimulator_python.candle_parser.gcodeparser import GcodeParser

from gcodeviewer.util.util import qQNaN


PROGRESSMINLINES = 10000
PROGRESSSTEP = 1000

sNan = 65536.0  # ???
sNan = float("NaN")


class CandleParser:
    """ """

    def __init__(self, filename: str):
        self.filename = filename
        self.m_viewParser = GcodeViewParse()
        self.linesegments = []

        # store mapping of gcode instruction no -> fileline no
        self.lineno2filelineno = {}

    def loadFile(self):
        file = QFile(self.filename)

        if not file.open(QIODevice.ReadOnly):
            print(f"Can't open file: {self.filename}\n")
            return

        # Prepare text stream
        textStream = QTextStream(file)

        # Read lines
        data = []
        while not textStream.atEnd():
            data.append(textStream.readLine())

        # Load lines
        self.loadData(data)

    def loadData(self, data: List[str]):
        time = QElapsedTimer()
        time.start()

        # Reset parsers
        self.m_viewParser.reset()

        # Prepare parser
        gp = GcodeParser()
        gp.setTraverseSpeed(2000)  # self.m_settings.rapidSpeed() -> from cmdline
        gp.reset(QVector3D(qQNaN(), qQNaN(), 0))

        print("Prepared to load: %s" % time.elapsed())
        time.start()

        filelineno = -1
        self.lineno2filelineno = {}

        while len(data) > 0:
            filelineno += 1

            command = data.pop(0)

            # Trim command
            trimmed = command.strip()

            if len(trimmed) > 0:
                # Split command
                stripped = GcodePreprocessorUtils.removeComment(command)
                args = GcodePreprocessorUtils.splitCommand(stripped)

                ps = gp.addCommand(args)

                if ps:
                    self.lineno2filelineno[ps.m_lineNumber] = filelineno

        arcPrecision = 0.2  # TODO self.m_settings.arcPrecision()  # default is 0.1
        arcDegreeMode = False  # TODO self.m_settings.arcDegreeMode()

        self.linesegments = self.m_viewParser.getLinesFromParser(
            gp, arcPrecision, arcDegreeMode
        )
