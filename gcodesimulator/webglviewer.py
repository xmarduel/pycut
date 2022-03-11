import os
import json

from typing import Dict
from typing import Any

from PySide6 import QtCore
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

    send_data_js_side = QtCore.Signal(str)

    def __init__(self, parent):
        '''
        '''
        super(WebGlViewer, self).__init__(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.data = {
            "width": 460,
            "height" : 460,
            "gcode": "",
            "cutterDiameter" : 3.175, 
            "cutterHeight" : 25.4,
            "cutterAngle" : 180,
            "elementsUrl" : "http://api.jscut.org/js"
            #"elementsUrl" : "qrc:/javascript/js/shaders" # CORS problem by "get"
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

    def set_data(self, data: Dict[str, Any]):
        '''
        '''
        self.data["gcode"] = data["gcode"]
        self.data["cutterDiameter"] = data["cutterDiameter"]
        #self.data["cutterHeight"] = data["cutterHeight"]
        self.data["cutterAngle"] = data["cutterAngle"]

    def show_gcode(self):
        '''
        '''
        try:
            self.setHtml(jscut_webgl)
        except Exception as err:
            self.setHtml(self.notfound % {'message': str(err)})




jscut_webgl = """
<html lang="en">
<head>
<style>

.slider {
  -webkit-appearance: none;
  width: 100%;
  height: 25px;
  background: #d3d3d3;
  outline: none;
  opacity: 0.7;
  -webkit-transition: .2s;
  transition: opacity .2s;
}

.slider:hover {
  opacity: 1;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 25px;
  height: 25px;
  background: #04AA6D;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 25px;
  height: 25px;
  background: #04AA6D;
  cursor: pointer;
}

#bloc1, #bloc2, #bloc3, #bloc4
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
var runner = null;
var current_time = 0;

function sliderChangeVal(newVal) {
  if (gcode_simulator) {
    gcode_simulator.timeChanged(0, newVal);
    current_time = newVal;
  }
}

function increaseTime() {
  current_time = current_time + 0.01;
  if (current_time > gcode_simulator.maxTime) {
    current_time = 0;
  }

  gcode_simulator.timeChanged(0, current_time);
  const input_slider = document.getElementById('input_slider');
  input_slider.value = current_time;
  
  runner = setTimeout(increaseTime, 1);
}

function run() {
  if (gcode_simulator) {
    if (runner === null) {
      runner = setTimeout(increaseTime, 1);
    }
  }
}

function pause() {
  if (gcode_simulator) {
    if (runner !== null) {
      clearTimeout(runner);
    }
    runner = null;
  }
}

function to_begin() {
  if (gcode_simulator) {
    current_time = 0;

    gcode_simulator.timeChanged(0, current_time);

    const input_slider = document.getElementById('input_slider');
    input_slider.value = current_time;
  }
}

function to_end() {
  if (gcode_simulator) {
    current_time = gcode_simulator.maxTime;

    gcode_simulator.timeChanged(0, current_time);

    const input_slider = document.getElementById('input_slider');
    input_slider.value = current_time;
  }
}
</script>

<!-- Controls with parameters bound to simulator -->

<div>
    <canvas id="glCanvas" width="460" height="460"></canvas>
    <input id="input_slider" type="range" min="1" max="10000" value="5000" oninput="sliderChangeVal(this.value)" style="width: 460px"></input>
    <div id="block_container">
      <div id="bloc1"><button type="button" onclick="to_begin()"><img src="qrc:/images/tango/22x22/actions/media-skip-backward.png"/></button> </div>  
      <div id="bloc2"><button type="button" onclick="run()"><img src="qrc:/images/tango/22x22/actions/media-playback-start.png"/></button> </div>
      <div id="bloc3"><button type="button" onclick="pause()"><img src="qrc:/images/tango/22x22/actions/media-playback-pause.png"/></button> </div>
      <div id="bloc4"><button type="button" onclick="to_end()"><img src="qrc:/images/tango/22x22/actions/media-skip-forward.png"/></button> </div>
    </div>
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
      self.renderPath = startRenderPath({}, document.getElementById("glCanvas"), null, self.elementsUrl , function (renderPath) {
        renderPath.fillPathBuffer(self.parsedGcode, 0, self.cutterDiameter, self.cutterAngle, self.cutterHeight);
        self.maxTime = renderPath.totalTime;
        self.maxTimeRounded = Math.ceil(renderPath.totalTime * 10) / 10;
        self.time1 = self.maxTimeRounded;
        self.time2 = self.maxTimeRounded;
        self.filled = true;

        const input_slider = document.getElementById('input_slider');
        input_slider.min = 0;
        if ( self.maxTimeRounded > 0 ) {
          input_slider.max = self.maxTimeRounded + 2;
          input_slider.value = self.maxTimeRounded + 2;
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

        var talkie = channel.objects.talkie; // global variable

        // An example of receiving information pushed from the Python side
        // It's really neat how this looks just like the Python code
        talkie.send_data_js_side.connect(function(data) {
            var simdata = JSON.parse(data);

            gcode_simulator = new GCodeSimulator(simdata);
            gcode_simulator.simulate();      
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
    send_error_annotation = QtCore.Signal(int, int, str, str)

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
