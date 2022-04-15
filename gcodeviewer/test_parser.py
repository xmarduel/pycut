
from typing import List

from PySide6.QtCore import QElapsedTimer
from PySide6.QtCore import QFile
from PySide6.QtCore import QTextStream
from PySide6.QtCore import QIODevice

from gcodeviewer.parser.gcodeviewparse import GcodeViewParse 
from gcodeviewer.parser.gcodepreprocessorutils import  GcodePreprocessorUtils  
from gcodeviewer.parser.gcodeparser import  GcodeParser 

from gcodeviewer.tables.gcodetablemodel import GCodeItem
from gcodeviewer.tables.gcodetablemodel import GCodeTableModel

PROGRESSMINLINES = 10000
PROGRESSSTEP     =  1000

global filename
filename = None

class GCodeLoader:
    '''
    '''
    def __init__(self, filename):
        self.filename = filename
        
        self.m_viewParser = GcodeViewParse()
        self.m_programModel = GCodeTableModel()

        
    def loadFile(self):
        file = QFile(self.filename)

        if not file.open(QIODevice.ReadOnly):
            print("Can't open file:\n" + self.filename)
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
        ####gp.setTraverseSpeed(self.m_settings.rapidSpeed())
        gp.setTraverseSpeed(100)

        print("Prepared to load: %s" % time.elapsed())
        time.start()

        # Block parser updates on table changes
        self.m_programLoading = True

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

                self.m_programModel.m_data.append(item)

        self.m_programModel.insertRow(self.m_programModel.rowCount())
        print("model filled: %s ms." % time.elapsed())

        time.start()

        arcPrecision = 0.0 # TODO self.m_settings.arcPrecision()
        arcDegreeMode = False # TODO self.m_settings.arcDegreeMode()

        all_lines = self.m_viewParser.getLinesFromParser(gp, arcPrecision, arcDegreeMode)

        #self.updateProgramEstimatedTime(all_lines)
        print("view parser filled: %s ms" % time.elapsed())

        self.m_programLoading = False


def main():
    '''
    '''
    codeLoader = GCodeLoader(filename)
    codeLoader.loadFile()


def main_profiled():
    """
    """
    import profile
    import pstats

    outfile = 'test_parser.bin'

    profile.run("main()", filename=outfile)
    p = pstats.Stats(outfile)

    # 1.
    p.sort_stats('cumulative')
    p.print_stats(100) # p.print_stats(50)

    # 2.
    p.sort_stats('time')
    p.print_stats(100) # p.print_stats(50)

    # 3.
    p.sort_stats('time', 'cumulative').print_stats(.5) # (.5, 'init')


if __name__ =='__main__':
    '''
    python -m cProfile -o test_parser.prof test_parser.py
    '''
    filename = "pycut_cnc_all_letters_op.nc"

    main()
    #main_profiled()