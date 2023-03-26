
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class GCodeControlsWidget(QtWidgets.QWidget):
    '''
    '''
    def __init__(self, parent):
        '''
        '''
        QtWidgets.QWidget.__init__(self, parent)

        self.timer = None # QtCore.QTimer()
        self.timer_dir = ""
        self.timer_timeout = 50

        self.tblProgram = None

        # main section of the window
        vbox = self.vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 10, 0)

        hbox = self.hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        slider = self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 1000)

        vbox.addWidget(slider)
        vbox.addLayout(hbox)

        self.to_begin = QtWidgets.QPushButton()
        self.to_begin.setText("")
        self.to_begin.setToolTip("Begin")
        
        self.step_backward = QtWidgets.QPushButton()
        self.step_backward.setText("")
        self.step_backward.setToolTip("Step Backward")
        self.step_backward.setAutoRepeat(True)
        
        self.backward = QtWidgets.QPushButton()
        self.backward.setText("")
        self.backward.setToolTip("Backward")
        
        self.stop = QtWidgets.QPushButton()
        self.stop.setText("")
        self.stop.setToolTip("Pause")
        
        self.forward = QtWidgets.QPushButton()
        self.forward.setText("")
        self.forward.setToolTip("Forward")

        self.step_forward = QtWidgets.QPushButton()
        self.step_forward.setText("")
        self.step_forward.setToolTip("Setp Forward")
        self.step_forward.setAutoRepeat(True)

        self.to_end = QtWidgets.QPushButton()
        self.to_end.setText("")
        self.to_end.setToolTip("End")

        self.to_begin.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/media-skip-backward.png"))
        self.step_backward.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/media-seek-backward.png"))
        self.backward.setIcon(QtGui.QIcon(":/images/media-playback-back.png"))
        self.stop.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/media-playback-pause.png"))
        self.forward.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/media-playback-start.png"))
        self.step_forward.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/media-seek-forward.png"))
        self.to_end.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/media-skip-forward.png"))

        hbox.addWidget(self.to_begin)
        hbox.addWidget(self.step_backward)
        hbox.addWidget(self.backward)
        hbox.addWidget(self.stop)
        hbox.addWidget(self.forward)
        hbox.addWidget(self.step_forward)
        hbox.addWidget(self.to_end)

        self.setLayout(vbox)

        # the callbacks
        self.to_begin.clicked.connect(self.do_on_begin)
        self.step_backward.clicked.connect(self.do_step_backward)
        self.backward.clicked.connect(self.do_backward)
        self.stop.clicked.connect(self.do_stop)
        self.forward.clicked.connect(self.do_forward)
        self.step_forward.clicked.connect(self.do_step_forward)
        self.to_end.clicked.connect(self.do_to_end)

        self.slider.valueChanged.connect(self.do_slider)

    def setTblProgram(self, tblProgram):
        '''
        '''
        self.tblProgram = tblProgram

        model = self.tblProgram.model()
        
        if model:
            self.slider.setRange(0, model.rowCount())

    def do_on_begin(self):
        '''
        '''
        self.slider.setValue(0)
        self.tblProgram.selectRow(0)

    def do_step_backward(self):
        '''
        '''
        value = self.slider.value()

        new_value = value - 1
        
        if new_value < 0:
            new_value = self.slider.maximum()

        self.slider.setValue(new_value)

        self.tblProgram.selectRow(new_value)

    def do_backward(self):
        '''
        '''
        if self.timer is None:
            self.timer = QtCore.QTimer()
            self.timer_dir = "b"
            self.timer.timeout.connect(self.do_step_backward)
            self.timer.start(self.timer_timeout)
        else:
            if self.timer_dir == "b":
                pass
            else:
                self.do_stop()
                self.do_backward()

    def do_stop(self):
        '''
        '''
        if self.timer:
            self.timer.timeout.disconnect()
            self.timer = None
            self.timer_dir = ""

    def do_forward(self):
        '''
        '''
        if self.timer is None:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.do_step_forward)
            self.timer_dir = "f"
            self.timer.start(self.timer_timeout)
        else:
            if self.timer_dir == "f":
                pass
            else:
                self.do_stop()
                self.do_forward()

    def do_step_forward(self):
        '''
        '''
        value = self.slider.value()

        #print("======================================================")
        #print("do_step_forward: curr pos = ", value)
        
        if value >= self.slider.maximum()-2:
            new_value = 0
        else:
            new_value = value + 1

        #print("do_step_forward: new pos = ", new_value , "(max=", self.slider.maximum(), ")")
            
        self.slider.setValue(new_value)

        self.tblProgram.selectRow(new_value)

    def do_to_end(self):
        '''
        '''
        value = self.slider.maximum()

        self.slider.setValue(value)
        self.tblProgram.selectRow(value) 

    def do_slider(self):
        '''
        '''
        value = self.slider.value()

        print("value: ", value)

        # set cursor in gcode table at right row
        self.tblProgram.selectRow(value-1)

    def set_slider_pos(self, value):
        '''
        coming from the table cursor selection
        '''
        print("set_slider_pos: ", value)

        if True:
            self.slider.valueChanged.disconnect(self.do_slider)
            self.slider.setValue(value)
            self.slider.valueChanged.connect(self.do_slider)