import argparse
import sys

from typing import List

from PySide6.QtCore import QElapsedTimer
from PySide6.QtCore import QFile
from PySide6.QtCore import QTextStream
from PySide6.QtCore import QIODevice

from gcodeviewer.parser.gcodeviewparse import GcodeViewParse 
from gcodeviewer.parser.gcodepreprocessorutils import  GcodePreprocessorUtils  
from gcodeviewer.parser.gcodeparser import  GcodeParser 

from gcodeviewer.tables.gcodetablemodel import GCodeItem

PROGRESSMINLINES = 10000
PROGRESSSTEP     =  1000


class CandleParser:
    '''
    '''
    def __init__(self, filename: str):
        self.filename = filename
        self.m_viewParser = GcodeViewParse()
        self.linesegments = []

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

        arcPrecision = 0.2 # TODO self.m_settings.arcPrecision()  # default is 0.1
        arcDegreeMode = False # TODO self.m_settings.arcDegreeMode()

        self.linesegments = self.m_viewParser.getLinesFromParser(gp, arcPrecision, arcDegreeMode)


def main(filename):
    '''
    '''
    codeLoader = CandleParser(filename)
    codeLoader.loadFile()
    
    print("DONE!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="gcode_candle_parser", description="Parse gcode")

    # argument
    parser.add_argument("gcodefile", help="gcode file")
    
    options = parser.parse_args()

    main(options.gcodefile)
    sys.exit(0)

'''
python -m cProfile -o test_parser.prof test_parser.py
'''