import json

from typing import Dict
from typing import Any

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtWebEngineWidgets
from PySide6 import QtWebEngineCore
from PySide6 import QtWebChannel


class WebGlViewer(QtWebEngineWidgets.QWebEngineView):
    '''
    usage:
        w = PyCutWebGlWrapper()
        w.set_webgl_data(data)
        w.show_gcode()
    '''
    notfound = '''<html>
<head>
<title>A Sample Page</title>
</head>
<body>
<h1>Html Display failed</h1>
<p>%(message)s</p>
</body>
</html>'''


    simtime_received_from_js = QtCore.Signal(float)

    def __init__(self, parent: QtWidgets.QWidget):
        '''
        '''
        super(WebGlViewer, self).__init__(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        shader_basicFragmentShader = self.get_shader_source(":/javascript/js/shaders/basicFragmentShader.txt")
        shader_basicVertexShader = self.get_shader_source(":/javascript/js/shaders/basicVertexShader.txt")
        shader_rasterizePathFragmentShader = self.get_shader_source(":/javascript/js/shaders/rasterizePathFragmentShader.txt")
        shader_rasterizePathVertexShader = self.get_shader_source(":/javascript/js/shaders/rasterizePathVertexShader.txt")
        shader_renderHeightMapFragmentShader = self.get_shader_source(":/javascript/js/shaders/renderHeightMapFragmentShader.txt")
        shader_renderHeightMapVertexShader = self.get_shader_source(":/javascript/js/shaders/renderHeightMapVertexShader.txt")

        self.data = {
            "width": 500,
            "height" : 500,
            "gcode": "",
            "cutterDiameter" : 3.175, 
            "cutterHeight" : 2 * 25.4,
            "cutterAngle" : 180,
            #"elementsUrl" : "http://api.jscut.org/js",
            #"elementsUrl" : ":/javascript/js/shaders", # CORS problem by "get"

            #"simulation_strategy" : "with_number_of_steps",
            "simulation_strategy": "with_step_size",
            "simulation_step_size" : 0.05,
            "simulation_nb_steps": 10000,

            "basicFragmentShader": shader_basicFragmentShader,
            "basicVertexShader": shader_basicVertexShader,
            "rasterizePathFragmentShader": shader_rasterizePathFragmentShader,
            "rasterizePathVertexShader": shader_rasterizePathVertexShader,
            "renderHeightMapFragmentShader": shader_renderHeightMapFragmentShader,
            "renderHeightMapVertexShader": shader_renderHeightMapVertexShader
        }

        # communication between qt and javascript html editor
        self.talkie = TalkyTalky(self)
        self.register_talkie()

        self.show()

    def register_talkie(self):
        self.page = QtWebEngineCore.QWebEnginePage(self)
        self.setPage(self.page)

        if self.page.webChannel() is None:
            channel = QtWebChannel.QWebChannel(self.page)
            channel.registerObject("talkie", self.talkie)
            self.page.setWebChannel(channel)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        width = self.size().width()
        height = self.size().height()

        square_size = min(width, height)

        self.data["width"] = square_size - 100
        self.data["height"] = square_size - 100
        
        self.show_gcode()

        return super().resizeEvent(event)
    
    def set_data(self, data: Dict[str, Any]):
        '''
        '''
        self.data["gcode"] = data["gcode"]
        self.data["cutterDiameter"] = data["cutterDiameter"]
        self.data["cutterHeight"] = data["cutterHeight"]
        self.data["cutterAngle"] = data["cutterAngle"]

    def show_gcode(self):
        '''
        '''
        try:
            self.setHtml(jscut_webgl)
        except Exception as err:
            self.setHtml(self.notfound % {'message': str(err)})

    def get_shader_source(self, shader_filename: str) -> str:
        '''
        '''
        fd = QtCore.QFile(shader_filename)

        shader_source = ""

        if fd.open(QtCore.QIODevice.ReadOnly | QtCore.QFile.Text):
            shader_source = QtCore.QTextStream(fd).readAll()
            fd.close()

        return shader_source

    def set_simtime(self, simtime: float):
        '''
        '''
        self.talkie.set_simtime(simtime)

    def received_simtime_from_js_side(self, simtime: float):
        '''
        '''
        # set cursor on gcode file browser
        self.simtime_received_from_js.emit(simtime)


jscut_webgl = """
<html lang="en">
<head>
<style>

input[type=range] {
  height: 25px;
  -webkit-appearance: none;
  margin: 10px 0;
  width: 100%;
}
input[type=range]:focus {
  outline: none;
}
input[type=range]::-webkit-slider-runnable-track {
  width: 100%;
  height: 5px;
  cursor: pointer;
  animate: 0.2s;
  box-shadow: 0px 0px 0px #000000;
  background: #2497E3;
  border-radius: 1px;
  border: 0px solid #000000;
}
input[type=range]::-webkit-slider-thumb {
  box-shadow: 0px 0px 0px #000000;
  border: 1px solid #2497E3;
  height: 18px;
  width: 18px;
  border-radius: 25px;
  background: #A1D0FF;
  cursor: pointer;
  -webkit-appearance: none;
  margin-top: -7px;
}
input[type=range]:focus::-webkit-slider-runnable-track {
  background: #2497E3;
}
input[type=range]::-moz-range-track {
  width: 100%;
  height: 5px;
  cursor: pointer;
  animate: 0.2s;
  box-shadow: 0px 0px 0px #000000;
  background: #2497E3;
  border-radius: 1px;
  border: 0px solid #000000;
}
input[type=range]::-moz-range-thumb {
  box-shadow: 0px 0px 0px #000000;
  border: 1px solid #2497E3;
  height: 18px;
  width: 18px;
  border-radius: 25px;
  background: #A1D0FF;
  cursor: pointer;
}
input[type=range]::-ms-track {
  width: 100%;
  height: 5px;
  cursor: pointer;
  animate: 0.2s;
  background: transparent;
  border-color: transparent;
  color: transparent;
}
input[type=range]::-ms-fill-lower {
  background: #2497E3;
  border: 0px solid #000000;
  border-radius: 2px;
  box-shadow: 0px 0px 0px #000000;
}
input[type=range]::-ms-fill-upper {
  background: #2497E3;
  border: 0px solid #000000;
  border-radius: 2px;
  box-shadow: 0px 0px 0px #000000;
}
input[type=range]::-ms-thumb {
  margin-top: 1px;
  box-shadow: 0px 0px 0px #000000;
  border: 1px solid #2497E3;
  height: 18px;
  width: 18px;
  border-radius: 25px;
  background: #A1D0FF;
  cursor: pointer;
}
input[type=range]:focus::-ms-fill-lower {
  background: #2497E3;
}
input[type=range]:focus::-ms-fill-upper {
  background: #2497E3;
}


#bloc1, #bloc2, #bloc3, #bloc4, #bloc5, #bloc6, #bloc7
{
    display:inline;
}

</style>

<title>GCODE Simulator</title>

<script type="text/javascript" src="qrc:/qtwebchannel/qwebchannel.js"></script>
<script type="text/javascript" src="qrc:/javascript/lib/jquery-2.1.1.min.js"></script>
<script type="text/javascript" src="qrc:/javascript/lib/gl-matrix-2.2.0-min.js"></script>
<script type="text/javascript" src="qrc:/javascript/lib/webgl-utils.js"></script>
<script type="text/javascript" src="qrc:/javascript/api/js/parseGcode.js"></script>
<script type="text/javascript" src="qrc:/javascript/js/RenderPath.js"></script>

</head>
<body>


<script>
var gcode_simulator = null;
var auto_runner = null;
var current_time = 0;
var time_step = 0;

var talkie = null;
var simtime_from_python = false;



function showAtTime(simtime) {
  if (gcode_simulator) {
    const simtime_slider = document.getElementById('simtime_slider');
    simtime_slider.value = simtime;
  
    sliderChangeSimTime(simtime);
  }
}

function sliderChangeSimTime(simtime) {
  if (gcode_simulator) {
    gcode_simulator.timeChanged(0, simtime);
    current_time = simtime;

    if (talkie !== null && simtime_from_python === false && auto_runner === null) {
      talkie.js_inform_python_for_simtime(parseFloat(simtime)); 
    }
  }
}

function increaseTime() {
  if (gcode_simulator) {
    var new_current_time = current_time + time_step;
    if (new_current_time > gcode_simulator.maxTime) {
      new_current_time = 0;
    }

    const simtime_slider = document.getElementById('simtime_slider');
    simtime_slider.value = new_current_time;
  
    sliderChangeSimTime(new_current_time);

    auto_runner = setTimeout(increaseTime, 1);
  }
}

function run() {
  if (gcode_simulator) {
    if (auto_runner === null) {
      auto_runner = setTimeout(increaseTime, 1);
    }
  }
}

function decreaseTime() {
  if (gcode_simulator) {
    var new_current_time = current_time - time_step;
    if (new_current_time < 0) {
      new_current_time = gcode_simulator.maxTime;
    }

    const simtime_slider = document.getElementById('simtime_slider');
    simtime_slider.value = new_current_time;

    sliderChangeSimTime(new_current_time);
  
    auto_runner = setTimeout(decreaseTime, 1);
  }
}

function run_back() {
  if (gcode_simulator) {
    if (auto_runner === null) {
      auto_runner = setTimeout(decreaseTime, 1);
    }
  }
}

function pause() {
  if (gcode_simulator) {
    if (auto_runner !== null) {
      clearTimeout(auto_runner);
    }
    auto_runner = null;

    // inform python on "stop"
    talkie.js_inform_python_for_simtime(parseFloat(current_time)); 
  }
}

function step_backward() {
  if (gcode_simulator) {
    var new_current_time = current_time - time_step;
    if (new_current_time < 0) {
      new_current_time = gcode_simulator.maxTime;
    }

    const simtime_slider = document.getElementById('simtime_slider');
    simtime_slider.value = new_current_time;

    sliderChangeSimTime(new_current_time);
  }
}

function step_forward() {
  if (gcode_simulator) {
    var new_current_time = current_time + time_step;
    if (new_current_time > gcode_simulator.maxTime) {
      new_current_time = 0;
    }

    const simtime_slider = document.getElementById('simtime_slider');
    simtime_slider.value = new_current_time;

    sliderChangeSimTime(new_current_time);

  }
}

function to_begin() {
  if (gcode_simulator) {

    const simtime_slider = document.getElementById('simtime_slider');
    simtime_slider.value = 0;

    sliderChangeSimTime(0);
  }
}

function to_end() {
  if (gcode_simulator) {

    const simtime_slider = document.getElementById('simtime_slider');
    simtime_slider.value = gcode_simulator.maxTime;

    sliderChangeSimTime(gcode_simulator.maxTime);
  }
}
</script>

<!-- Controls with parameters bound to simulator -->

<div>
    <canvas id="glCanvas" width="500" height="500"></canvas>
    <br />
    <input id="simtime_slider" type="range" min="0" max="1000" value="1000" step="1" oninput="sliderChangeSimTime(this.value)"></input>
    <div id="block_container">
      <div id="bloc1"><button type="button" onclick="to_begin()"><img src="qrc:/images/tango/22x22/actions/media-skip-backward.png"/></button> </div>  
      <div id="bloc2"><button type="button" onclick="step_backward()"><img src="qrc:/images/tango/22x22/actions/media-seek-backward.png"/></button> </div>  
      <div id="bloc3"><button type="button" onclick="run_back()"><img src="qrc:/images/media-playback-back.png"/></button> </div>
      <div id="bloc4"><button type="button" onclick="pause()"><img src="qrc:/images/tango/22x22/actions/media-playback-pause.png"/></button> </div>
      <div id="bloc5"><button type="button" onclick="run()"><img src="qrc:/images/tango/22x22/actions/media-playback-start.png"/></button> </div>
      <div id="bloc6"><button type="button" onclick="step_forward()"><img src="qrc:/images/tango/22x22/actions/media-seek-forward.png"/></button> </div>
      <div id="bloc7"><button type="button" onclick="to_end()"><img src="qrc:/images/tango/22x22/actions/media-skip-forward.png"/></button> </div>
    </div>
    <div>Click twice a button or move the mouse outside the buttons to refresh the view!</div>
  </div>
</div>

</div>

</body>

<!-- the rendering -->
<script>
class GCodeSimulator {
  constructor(simdata) {
    this.height = simdata["height"];
    this.width = simdata["width"];

    this.gcode = simdata["gcode"];

    this.cutterDiameter = simdata["cutterDiameter"];
    this.cutterAngle = simdata["cutterAngle"];
    this.cutterHeight = simdata["cutterHeight"];

    this.elementsUrl = simdata["elementsUrl"];
    
    // this will be calculated
    this.parsedGcode = null;
    this.time1 = 0;
    this.time2 = 0;
    this.maxTimeRounded = 0;
    this.maxTime = 0;
    this.filled = false; 
    this.renderPath = null;

    // simulation runner settings
    this.simulation_strategy = simdata["simulation_strategy"];
    this.simulation_step_size = simdata["simulation_step_size"];
    this.simulation_nb_steps = simdata["simulation_nb_steps"];

    // shader code
    this.shaders = {
      "basicFragmentShader": simdata["basicFragmentShader"],
      "basicVertexShader": simdata["basicVertexShader"],
      "rasterizePathFragmentShader": simdata["rasterizePathFragmentShader"],
      "rasterizePathVertexShader": simdata["rasterizePathVertexShader"],
      "renderHeightMapFragmentShader": simdata["renderHeightMapFragmentShader"],
      "renderHeightMapVertexShader": simdata["renderHeightMapVertexShader"]
    };
  }

  simulate () {
    this.parsedGcode = jscut.parseGcode({}, this.gcode);
    this.ready();
  }

  timeChanged(oldValue, newValue) {
    if (this.renderPath) {
      this.renderPath.setStopAtTime(newValue);
    }
  }

  ready () {
    self = this;
    window.requestAnimationFrame(function () {
      const time_widget = null;
      self.renderPath = startRenderPath({}, document.getElementById("glCanvas"), time_widget, self.shaders, function (renderPath) {
        renderPath.fillPathBuffer(self.parsedGcode, 0, self.cutterDiameter, self.cutterAngle, self.cutterHeight);
        self.maxTime = renderPath.totalTime;
        self.maxTimeRounded = Math.ceil(renderPath.totalTime * 10) / 10;
        self.time1 = self.maxTimeRounded;
        self.time2 = self.maxTimeRounded;
        self.filled = true;

        const simtime_slider = document.getElementById('simtime_slider');
        simtime_slider.min = 0;
        if ( self.maxTimeRounded > 0 ) {
          simtime_slider.max = self.maxTimeRounded;
          simtime_slider.value = self.maxTimeRounded;
          
          if (self.simulation_strategy == "with_number_of_steps") {
            // set the number of steps, step size is calculated from this
            simtime_slider.step = simtime_slider.max / self.simulation_nb_steps;
            time_step = self.maxTimeRounded / self.simulation_nb_steps;
          } 
          if (self.simulation_strategy == "with_step_size") {
            // set the time step, number of steps calculated from this
            time_step = self.simulation_step_size;
            simtime_slider.step = time_step;
          }
        }
      });
    });
  }
}
</script>


<script>
document.addEventListener("DOMContentLoaded", function () {
    
    // It is safest to set up this apparatus after the page has finished loading
    
    'use strict';

    const canvas = document.querySelector("#glCanvas");
    // Initialisierung des GL Kontexts
    const gl = canvas.getContext("webgl");

    // Nur fortfahren, wenn WebGL verfügbar ist und funktioniert
    if (!gl) {
        alert("Unable to initialize WebGL. Your browser or machine may not support it.");
        return;
    }

    // Setze clear color auf schwarz, vollständig sichtbar
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    // Lösche den color buffer mit definierter clear color
    gl.clear(gl.COLOR_BUFFER_BIT);

    new QWebChannel(qt.webChannelTransport, function(channel) {
        // All the functions we use to communicate with the Python code are here   

        talkie = channel.objects.talkie; // global variable

        // An example of receiving information pushed from the Python side
        // It's really neat how this looks just like the Python code
        talkie.send_data_js_side.connect(function(data) {
            const simdata = JSON.parse(data);

            // size of canvas from outside
            const gl_canvas = document.getElementById('glCanvas');
            gl_canvas.width = simdata["width"];
            gl_canvas.height = simdata["height"];

            // size of slider from outside
            const simtime_slider = document.getElementById('simtime_slider');
            var square_width = Math.min(simdata["width"], simdata["height"]);
            simtime_slider.style.width = square_width;


            gcode_simulator = new GCodeSimulator(simdata);
            gcode_simulator.simulate();      
        });

        talkie.send_simtime_js_side.connect(function(data) {
          const simtime = JSON.parse(data);
          
          simtime_from_python = true; 
          showAtTime(simtime);  
          simtime_from_python = false;    
        }); 
        
        talkie.fill_webgl();
    });

});
</script>

</html>"""


class TalkyTalky(QtCore.QObject):
    '''
    '''
    send_data_js_side = QtCore.Signal(str)
    send_simtime_js_side = QtCore.Signal(float)

    def __init__(self, widget: WebGlViewer):
        super().__init__()
        self.widget = widget
  
    @QtCore.Slot() 
    def fill_webgl(self):
        '''
        js is waiting for a json structure
        '''
        jsondata = json.dumps(self.widget.data, indent = 4) 
        
        self.send_data_js_side.emit(jsondata)

    @QtCore.Slot() 
    def set_simtime(self, simtime: float):
        '''
        set the sim time from the outside into js (from the gcode file browser per example)
        '''
        #print("TalkyTalky::set_simtime", simtine)

        self.send_simtime_js_side.emit(simtime)

    @QtCore.Slot(float) 
    def js_inform_python_for_simtime(self, simtime: float):
        '''
        get the sim time from the js and send it to "listeners" (to the gcode file browser per example)
        '''
        #print("TalkyTalky::js_inform_python_for_simtime", simtime)

        # inform listeners
        self.widget.received_simtime_from_js_side(simtime)