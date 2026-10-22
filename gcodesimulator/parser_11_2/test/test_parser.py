import argparse
import sys

from typing import List

from PySide6.QtCore import QElapsedTimer
from PySide6.QtCore import QFile
from PySide6.QtCore import QTextStream
from PySide6.QtCore import QIODevice

from gcodesimulator.parser_11_2.gcodeviewparse import GcodeViewParse
from gcodesimulator.parser_11_2.gcodepreprocessorutils import GcodePreprocessorUtils
from gcodesimulator.parser_11_2.gcodeparser import GcodeParser
from gcodesimulator.parser_11_2.linesegment import LineSegment

from gcodeviewer.tables.gcodetablemodel import GCodeItem

PROGRESSMINLINES = 10000
PROGRESSSTEP = 1000


class CandleParser:
    """ """

    def __init__(self, filename: str):
        self.filename = filename
        self.m_viewParser = GcodeViewParse()
        self.linesegments: List[LineSegment] = []

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
        gp.setTraverseSpeed(100)  # self.m_settings.rapidSpeed()

        print("Prepared to load: %s" % time.elapsed())
        time.start()

        while len(data) > 0:
            command = data.pop(0)

            # Trim command
            trimmed = command.strip()

            if len(trimmed) > 0:
                # Split command
                stripped = GcodePreprocessorUtils.removeComment(command)
                args = GcodePreprocessorUtils.splitCommand(stripped)

                gp.addCommand(args)

                item = GCodeItem()

                item.command = trimmed
                item.state = GCodeItem.States.InQueue
                item.line = gp.getCommandNumber()
                item.args = args

        arcPrecision = 0.2  # TODO self.m_settings.arcPrecision()  # default is 0.1
        arcDegreeMode = False  # TODO self.m_settings.arcDegreeMode()

        self.linesegments = self.m_viewParser.updateFromParser(
            gp, arcPrecision, arcDegreeMode, False
        )


def main(fname):
    """ """
    codeLoader = CandleParser(fname)
    codeLoader.loadFile()

    print("DONE!")

ffname = None

def main_profiled_run():
    """ """
    global ffname
    
    codeLoader = CandleParser(ffname)
    codeLoader.loadFile()

    print("DONE!")


def main_profiled(fname):
    """ """
    global ffname
    import profile
    import pstats

    ffname = fname

    outfile = "test_parser.bin"

    profile.run("main_profiled_run()", filename=outfile)
    p = pstats.Stats(outfile)

    # 1.
    p.sort_stats("cumulative")
    p.print_stats(100)  # p.print_stats(50)

    # 2.
    p.sort_stats("time")
    p.print_stats(100)  # p.print_stats(50)

    # 3.
    p.sort_stats("time", "cumulative").print_stats(0.5)  # (.5, 'init')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="gcode_candle_parser", description="Parse gcode"
    )

    # argument
    parser.add_argument("gcodefile", help="gcode file")

    options = parser.parse_args()

    #main(options.gcodefile)
    main_profiled(options.gcodefile)

    sys.exit(0)

"""
python3 -m cProfile -o test_parser.prof test_parser.py  ../../tests/g5.gcode
"""
