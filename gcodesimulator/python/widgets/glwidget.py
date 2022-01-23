
import math

from typing import List
from typing import Dict

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from PySide6 import QtOpenGLWidgets
from PySide6 import QtOpenGL

from OpenGL import GL

from PySide6.QtCore import Signal, Slot
from PySide6.QtCore import qIsNaN

from gcodesimulator.python.drawers.shaderdrawable import ShaderDrawable
from gcodesimulator.python.drawers.gcodedrawer import GcodeDrawer
from gcodesimulator.python.drawers.tooldrawer import ToolDrawer
from gcodesimulator.python.drawers.heightmapdrawer import HeightMapDrawer

M_PI = math.acos(-1)
ZOOMSTEP = 1.1


class GLWidget(QtOpenGLWidgets.QOpenGLWidget, QtGui.QOpenGLFunctions):
    '''
    '''
    rotationChanged = Signal()
    resized = Signal()

    def __init__(self, parent=None):
        QtOpenGLWidgets.QOpenGLWidget.__init__(self, parent)
        QtGui.QOpenGLFunctions.__init__(self)

        self.m_shaderProgram = None
        self.m_shaderHeightMapProgram = None
        self.m_shaderBasicProgram = None

        self.pathBuffer = None  # vbo

        self.pathFramebuffer = None
        self.pathRgbaTexture = None

        self.m_xRot = 90.0 
        self.m_yRot = 0.0 
        self.m_xLastRot = 0.0 
        self.m_yLastRot = 0.0 
        self.m_xPan = 0.0 
        self.m_yPan = 0.0 
        self.m_xLastPan = 0.0 
        self.m_yLastPan = 0.0 
        self.m_xLookAt = 0.0
        self.m_yLookAt = 0.0
        self.m_zLookAt = 0.0
        self.m_lastPos = QtCore.QPoint(0, 0)
        self.m_zoom = 1
        self.m_distance = 100.0 
        self.m_xMin = 0.0 
        self.m_xMax = 0.0 
        self.m_yMin = 0.0
        self.m_yMax = 0.0 
        self.m_zMin = 0.0
        self.m_zMax = 0.0 
        self.m_xSize = 0.0 
        self.m_ySize = 0.0 
        self.m_zSize = 0.0 
        self.m_lineWidth = 0.0 
        self.m_pointSize = 0.0 
        self.m_antialiasing = True
        self.m_msaa = True
        self.m_zBuffer = True
        self.m_frames = 0
        self.m_fps = 0
        self.m_animationFrame = 0
        self.m_timerPaint = QtCore.QBasicTimer()
        self.m_xRotTarget = 90.0 
        self.m_yRotTarget = 0.0 
        self.m_xRotStored = 0.0  
        self.m_yRotStored = 0.0 
        self.m_animateView = False
        self.m_parserStatus = ""
        self.m_speedState = ""
        self.m_pinState = ""
        self.m_bufferState = ""
        self.m_updatesEnabled = False

        self.m_projectionMatrix = QtGui.QMatrix4x4()
        self.m_viewMatrix = QtGui.QMatrix4x4()

        self.m_colorBackground = QtGui.QColor(255,255,255)
        self.m_colorText = QtGui.QColor()

        self.m_shaderDrawables : List[ShaderDrawable] = []

        self.updateProjection()
        self.updateView()

        self.m_spendTime = QtCore.QTime()
        self.m_spendTime.setHMS(0, 0, 0)

        self.m_estimatedTime = QtCore.QTime()
        self.m_estimatedTime.setHMS(0, 0, 0)

        self.m_vsync = False
        self.m_targetFps = 60

        self.cmdFit = QtWidgets.QToolButton(self)
        self.cmdIsometric = QtWidgets.QToolButton(self)
        self.cmdTop = QtWidgets.QToolButton(self)
        self.cmdFront = QtWidgets.QToolButton(self)
        self.cmdLeft = QtWidgets.QToolButton(self)

        self.cmdFit.setMinimumSize(QtCore.QSize(24,24))
        self.cmdIsometric.setMinimumSize(QtCore.QSize(24,24))
        self.cmdTop.setMinimumSize(QtCore.QSize(24,24))
        self.cmdFront.setMinimumSize(QtCore.QSize(24,24))
        self.cmdLeft.setMinimumSize(QtCore.QSize(24,24))

        self.cmdFit.setMaximumSize(QtCore.QSize(24,24))
        self.cmdIsometric.setMaximumSize(QtCore.QSize(24,24))
        self.cmdTop.setMaximumSize(QtCore.QSize(24,24))
        self.cmdFront.setMaximumSize(QtCore.QSize(24,24))
        self.cmdLeft.setMaximumSize(QtCore.QSize(24,24))

        self.cmdFit.setToolTip("Fit")
        self.cmdIsometric.setToolTip("Isometric view")
        self.cmdTop.setToolTip("Top view")
        self.cmdFront.setToolTip("Front view")
        self.cmdLeft.setToolTip("Left view")

        self.cmdFit.setIcon(QtGui.QIcon(":/images/candle/fit_1.png"))
        self.cmdIsometric.setIcon(QtGui.QIcon(":/images/candle/cube.png"))
        self.cmdTop.setIcon(QtGui.QIcon(":/images/candle/cubeTop.png"))
        self.cmdFront.setIcon(QtGui.QIcon(":/images/candle/cubeFront.png"))
        self.cmdLeft.setIcon(QtGui.QIcon(":/images/candle/cubeLeft.png"))

        self.cmdFit.clicked.connect(self.on_cmdFit_clicked)
        self.cmdIsometric.clicked.connect(self.on_cmdIsometric_clicked)
        self.cmdTop.clicked.connect(self.on_cmdTop_clicked)
        self.cmdFront.clicked.connect(self.on_cmdFront_clicked)
        self.cmdLeft.clicked.connect(self.on_cmdLeft_clicked)

        self.rotationChanged.connect(self.onVisualizatorRotationChanged)
        self.resized.connect(self.placeVisualizerButtons)     

        QtCore.QTimer.singleShot(1000, self.onFramesTimer)

    def placeVisualizerButtons(self):
        w = self.width()
        cmdIsometric_w =  self.cmdIsometric.width() 

        self.cmdIsometric.move(self.width() - self.cmdIsometric.width() - 8, 8)
        self.cmdTop.move(self.cmdIsometric.geometry().left() - self.cmdTop.width() - 8, 8)
        self.cmdLeft.move(self.width() - self.cmdLeft.width() - 8, self.cmdIsometric.geometry().bottom() + 8)
        self.cmdFront.move(self.cmdLeft.geometry().left() - self.cmdFront.width() - 8, self.cmdIsometric.geometry().bottom() + 8)
        self.cmdFit.move(self.width() - self.cmdFit.width() - 8, self.cmdLeft.geometry().bottom() + 8)

    def on_cmdTop_clicked(self):
        self.setTopView()
        self.updateView()

        self.onVisualizatorRotationChanged()

    def on_cmdFront_clicked(self):
        self.setFrontView()
        self.updateView()

        self.onVisualizatorRotationChanged()

    def on_cmdLeft_clicked(self):
        self.setLeftView()
        self.updateView()

        self.onVisualizatorRotationChanged()

    def on_cmdIsometric_clicked(self):
        self.setIsometricView()
        self.updateView()

        self.onVisualizatorRotationChanged()

    def on_cmdFit_clicked(self):
        splitter = self.parent()
        gl_widget_container = splitter.parent()

        if hasattr(gl_widget_container, "m_currentDrawer") and gl_widget_container.m_currentDrawer is not None:
            self.fitDrawable(gl_widget_container.m_currentDrawer)

    def calculateVolume(self, size: QtGui.QVector3D) -> float:
        return size.x() * size.y() * size.z()
        
    def addDrawable(self, drawable: ShaderDrawable):
        self.m_shaderDrawables.append(drawable)

    def fitDrawable(self, drawable : ShaderDrawable = None):
        self.stopViewAnimation()

        if drawable != None:
            self.updateExtremes(drawable)

            a = self.m_ySize / 2 / 0.25 * 1.3 + \
                (self.m_zMax - self.m_zMin) / 2
            b = self.m_xSize / 2 / 0.25 * 1.3 / (self.width() / self.height()) + \
                (self.m_zMax - self.m_zMin) / 2
        
            self.m_distance = max(a, b)

            if self.m_distance == 0:
                self.m_distance = 200

            self.m_xLookAt = (self.m_xMax - self.m_xMin) / 2 + self.m_xMin
            self.m_zLookAt = -((self.m_yMax - self.m_yMin) / 2 + self.m_yMin)
            self.m_yLookAt = (self.m_zMax - self.m_zMin) / 2 + self.m_zMin
        else :
            self.m_distance = 200
            self.m_xLookAt = 0
            self.m_yLookAt = 0
            self.m_zLookAt = 0

            self.m_xMin = 0
            self.m_xMax = 0
            self.m_yMin = 0
            self.m_yMax = 0
            self.m_zMin = 0
            self.m_zMax = 0

            self.m_xSize = 0
            self.m_ySize = 0
            self.m_zSize = 0

        self.m_xPan = 0
        self.m_yPan = 0
        self.m_zoom = 1

        self.updateProjection()
        self.updateView()

    def normalizeAngle(self, angle: float) -> float:
        while angle < 0: 
            angle += 360
        while angle > 360: 
            angle -= 360

        return angle

    def beginViewAnimation(self):
        self.m_xRotStored = self.m_xRot
        self.m_yRotStored = self.m_yRot
        self.m_animationFrame = 0
        self.m_animateView = True

    def stopViewAnimation(self):
        self.m_animateView = False

    def updateExtremes(self, drawable: ShaderDrawable):
        if not qIsNaN(drawable.getMinimumExtremes().x()): 
            self.m_xMin = drawable.getMinimumExtremes().x() 
        else: 
            self.m_xMin = 0
        
        if not qIsNaN(drawable.getMaximumExtremes().x()): 
            self.m_xMax = drawable.getMaximumExtremes().x() 
        else: self.m_xMax = 0
        
        if not qIsNaN(drawable.getMinimumExtremes().y()): 
            self.m_yMin = drawable.getMinimumExtremes().y() 
        else: 
            self.m_yMin = 0
        
        if not qIsNaN(drawable.getMaximumExtremes().y()):
             self.m_yMax = drawable.getMaximumExtremes().y() 
        else: 
            self.m_yMax = 0
        
        if not qIsNaN(drawable.getMinimumExtremes().z()):
             self.m_zMin = drawable.getMinimumExtremes().z()
        else: 
            self.m_zMin = 0
        
        if not qIsNaN(drawable.getMaximumExtremes().z()): 
            self.m_zMax = drawable.getMaximumExtremes().z() 
        else: 
            self.m_zMax = 0

        self.m_xSize = self.m_xMax - self.m_xMin
        self.m_ySize = self.m_yMax - self.m_yMin
        self.m_zSize = self.m_zMax - self.m_zMin
    
    def antialiasing(self) -> bool:
        return self.m_antialiasing

    def setAntialiasing(self, antialiasing: bool):
        self.m_antialiasing = antialiasing

    def spendTime(self) -> QtCore.QTime:
        return self.m_spendTime

    def setSpendTime(self, spendTime: QtCore.QTime):
        self.m_spendTime = spendTime

    def estimatedTime(self) -> QtCore.QTime:
        return self.m_estimatedTime

    def setEstimatedTime(self, estimatedTime: QtCore.QTime):
        self.m_estimatedTime = estimatedTime

    def lineWidth(self) -> float:
        return self.m_lineWidth

    def setLineWidth(self, lineWidth: float):
        self.m_lineWidth = lineWidth

    def setIsometricView(self):
        ''' no animation yet '''
        self.m_xRotTarget = 45
        self.m_yRotTarget = 405 if self.m_yRot > 180 else 45

        self.m_xRot = 45
        self.m_yRot = 405 if self.m_yRot > 180 else 45

        #self.beginViewAnimation()

    def setTopView(self):
        ''' no animation yet '''
        self.m_xRotTarget = 90
        self.m_yRotTarget = 360 if self.m_yRot > 180 else 0

        self.m_xRot = 90
        self.m_yRot = 360 if self.m_yRot > 180 else 0

        #self.beginViewAnimation()

    def setFrontView(self):
        ''' no animation yet '''
        self.m_xRotTarget = 0
        self.m_yRotTarget = 360 if self.m_yRot > 180 else 0

        self.m_xRot = 0
        self.m_yRot = 360 if self.m_yRot > 180 else 0

        #self.beginViewAnimation()

    def setLeftView(self):
        ''' no animation yet '''
        self.m_xRotTarget = 0
        self.m_yRotTarget = 450 if self.m_yRot > 270 else 90

        self.m_xRot= 0
        self.m_yRot = 450 if self.m_yRot > 270 else 90

        #self.beginViewAnimation()

    def fps(self) -> int:
        return self.m_targetFps

    def setFps(self, fps: int):
        if fps <= 0:
            return

        self.m_targetFps = fps
        self.m_timerPaint.stop()

        value = 0 if self.m_vsync else 1000.0 / fps
        self.m_timerPaint.start(value, QtGui.Qt.PreciseTimer, self)

    def parserStatus(self) -> str:
        return self.m_parserStatus

    def setParserStatus(self, parserStatus: str):
        self.m_parserStatus = parserStatus

    def bufferState(self) -> str:
        return self.m_bufferState

    def setBufferState(self, bufferState: str):
        self.m_bufferState = bufferState

    def zBuffer(self) -> bool:
        return self.m_zBuffer

    def setZBuffer(self, zBuffer: bool):
        self.m_zBuffer = zBuffer

    def updatesEnabled(self) -> bool:
        return self.m_updatesEnabled 

    def setUpdatesEnabled(self, updatesEnabled: bool):
        self.m_updatesEnabled = updatesEnabled

    def msaa(self) -> bool:
        return self.m_msaa

    def setMsaa(self, msaa: bool):
        self.m_msaa = msaa

    def colorBackground(self) -> QtGui.QColor :
        return self.m_colorBackground

    def setColorBackground(self, colorBackground: QtGui.QColor):
        self.m_colorBackground = colorBackground

    def colorText(self) -> QtGui.QColor :
        return self.m_colorText

    def setColorText(self, colorText: QtGui.QColor):
        self.m_colorText = colorText

    def pointSize(self) -> float:
        return self.m_pointSize

    def setPointSize(self, pointSize: float):
        self.m_pointSize = pointSize

    def vsync(self) -> bool:
        return self.m_vsync

    def setVsync(self, vsync: bool):
        self.m_vsync = vsync

    def speedState(self) -> str:
        return self.m_speedState

    def setSpeedState(self, speedState: str):
        self.m_speedState = speedState

    def pinState(self) -> str:
        return self.m_pinState

    def setPinState(self, pinState: str):
        self.m_pinState = pinState

    @Slot()
    def onFramesTimer(self):
        self.m_fps = self.m_frames
        self.m_frames = 0

        QtCore.QTimer.singleShot(1000, self.onFramesTimer)

    @Slot()
    def viewAnimation(self):
        t = self.m_animationFrame / (self.m_fps * 0.2)

        self.m_animationFrame += 1

        if t >= 1: 
            self.stopViewAnimation()

        ec = QtCore.QEasingCurve(QtCore.QEasingCurve.OutExpo)
        val = ec.valueForProgress(t)

        self.m_xRot = self.m_xRotStored + (self.m_xRotTarget - self.m_xRotStored) * val
        self.m_yRot = self.m_yRotStored + (self.m_yRotTarget - self.m_yRotStored) * val

        self.updateView()

    def cleanup(self):
        pass

    def vertex_shader_source(self):
        return """
uniform float resolution;
uniform float cutterDia;
uniform vec2 pathXYOffset;
uniform float pathScale;
uniform float pathMinZ;
uniform float pathTopZ;
uniform float stopAtTime;

attribute vec3 pos1;
attribute vec3 pos2;
attribute vec3 rawPos;
attribute float startTime;
attribute float endTime;
attribute float command;

varying vec4 color;
varying vec2 center;
varying float radius;
varying float enable;

void main(void) {
    enable = 1.0;

    vec3 clampedPos2;

    clampedPos2 = pos2;
    if(stopAtTime < startTime)
        enable = 0.0;
    else if(stopAtTime < endTime)
        clampedPos2 = pos1 + (pos2-pos1)*(stopAtTime-startTime)/(endTime-startTime);

    vec3 lower, upper;
    if(pos1.z < pos2.z) {
        lower = vec3((pos1.xy+pathXYOffset)*pathScale, pos1.z);
        upper = vec3((clampedPos2.xy+pathXYOffset)*pathScale, clampedPos2.z);
    } else {
        lower = vec3((clampedPos2.xy+pathXYOffset)*pathScale, clampedPos2.z);
        upper = vec3((pos1.xy+pathXYOffset)*pathScale, pos1.z);
    }

    // command 00-02: lower circle triangle 1
    // command 03-05: lower circle triangle 2
    // command 06-08: upper circle triangle 1
    // command 09-11: upper circle triangle 2
    // command 12-14: connecting line triangle 1
    // command 15-17: connecting line triangle 2
    // command 100: pos1 + rawPos
    // command 101: clampedPos2 + rawPos
    // command 200: discard

    int i = int(command);
    vec3 thisPos;
    if(i < 6)
        thisPos = lower;
    else
        thisPos = upper;

    center = (thisPos.xy*resolution + resolution)/2.0;
    color = vec4(0.0, 1.0, 1.0, 1.0);
    float r = cutterDia*pathScale/2.0;

    if(i < 12) {
        radius = r*resolution/2.0;
        vec2 offset;
        if(i == 0 || i == 6)
            offset = vec2(-r, -r);
        else if(i == 1 || i == 7)
            offset = vec2(r, r);
        else if(i == 2 || i == 8)
            offset = vec2(-r, r);
        else if(i == 3 || i == 9)
            offset = vec2(-r, -r);
        else if(i == 4 || i == 10)
            offset = vec2(r, -r);
        else if(i == 5 || i == 11)
            offset = vec2(r, r);
        gl_Position = vec4(thisPos.xy + offset, thisPos.z, 1.0);
    } else {
        radius = 0.0;
        vec2 delta = normalize(lower.xy - upper.xy) * r;
        float l = length(delta);
        if(i == 12)
            gl_Position = vec4(upper.x+delta.y, upper.y-delta.x, upper.z, 1.0);
        else if(i == 13)
            gl_Position = vec4(lower.x+delta.y, lower.y-delta.x, lower.z, 1.0);
        else if(i == 14)
            gl_Position = vec4(upper.x-delta.y, upper.y+delta.x, upper.z, 1.0);
        else if(i == 15)
            gl_Position = vec4(upper.x-delta.y, upper.y+delta.x, upper.z, 1.0);
        else if(i == 16)
            gl_Position = vec4(lower.x+delta.y, lower.y-delta.x, lower.z, 1.0);
        else if(i == 17)
            gl_Position = vec4(lower.x-delta.y, lower.y+delta.x, lower.z, 1.0);
        else if(i == 100)
            gl_Position = vec4((pos1.xy+rawPos.xy+pathXYOffset)*pathScale, pos1.z+rawPos.z, 1.0);
        else if(i == 101)
            gl_Position = vec4((clampedPos2.xy+rawPos.xy+pathXYOffset)*pathScale, clampedPos2.z+rawPos.z, 1.0);
        else if(i == 200) {
            gl_Position = vec4(0, 0, 0, 1.0);
            enable = 0.0;
        }
    }

    float bottom = pathMinZ;
    if(bottom == pathTopZ)
        bottom = pathTopZ - 1.0;

    // color.r = normalized cut depth
    color.r = (gl_Position.z - pathTopZ) / (bottom - pathTopZ);

    gl_Position.z = 1.9999 * (gl_Position.z - bottom) / (pathTopZ - bottom) - 1.0;
}
"""

    def fragment_shader_source(self):
        return """//precision mediump float;

varying vec4 color;
varying vec2 center;
varying float radius;
varying float enable;

void main(void) {
    gl_FragColor = color;
    if(enable == 0.0 || radius > 0.0 && distance(gl_FragCoord.xy, center) > radius)
        discard;
}"""

    def vertex_shader_heightmap_source(self):
        return """
uniform float resolution;
uniform float pathScale;
uniform float pathMinZ;
uniform float pathTopZ;
uniform mat4 rotate;
uniform sampler2D heightMap;

attribute vec2 pos0;
attribute vec2 pos1;
attribute vec2 pos2;
attribute vec2 thisPos;
attribute float vertex;

varying vec4 color;

vec3 getPos(in vec2 p) {
    return vec3(
        p * 2.0 / resolution - vec2(1.0, 1.0),
        texture2D(heightMap, p/resolution).r);
}

void main(void) {
    vec3 p0 = getPos(pos0);
    vec3 p1 = getPos(pos1);
    vec3 p2 = getPos(pos2);
    vec3 tp = getPos(thisPos);

    vec4 topColor = vec4(1.0, 1.0, 1.0, 1.0);
    vec4 botColor = vec4(0.0, 0.0, 1.0, 1.0);
    vec4 transitionColor = vec4(0.0, 0.0, 0.0, 1.0);

    float transition = min(.4, 100.0*max(abs(p0.z-p1.z), abs(p0.z-p2.z)));
    color = mix(topColor, botColor, tp.z);
    color = mix(color, transitionColor, transition);

    // try to make it look like it does to people with red-green color blindness
    // for usability testing.
    //color.rg = vec2((color.r+color.g)/2.0, (color.r+color.g)/2.0);

    vec4 p = vec4(tp.xy, -tp.z*(pathTopZ-pathMinZ)*pathScale, 1.0);

    mat4 offset = mat4(
        1.0,    0.0,    0.0,    0.0,
        0.0,    1.0,    0.0,    0.0,
        0.0,    0.0,    1.0,    0.0,
        0.0,    0.0,    -3.5,   1.0
    );

    float left = -.6;
    float right = .6;
    float top = .6;
    float bot = -.6;
    float near = 2.0;
    float far = 5.0;
    mat4 camera = mat4(
        2.0*near/(right-left),      0.0,                    0.0,                        0.0,
        0.0,                        2.0*near/(top-bot),     0.0,                        0.0,
        (right+left)/(right-left),  (top+bot)/(top-bot),    (far+near)/(near-far),      -1,
        0.0,                        0.0,                    2.0*far*near/(near-far),    0.0
    );

    gl_Position = camera * offset * rotate * p;
}

        """

    def fragment_shader_heightmap_source(self):
        return """//precision mediump float;

varying vec4 color;

void main(void) {
    gl_FragColor = color;
}
        """
    
    def vertex_shader_basic_source(self):
        return """
uniform vec3 scale;
uniform vec3 translate;
uniform mat4 rotate;

attribute vec3 vPos;
attribute vec3 vColor;

varying vec4 color;

void main(void) {
    mat4 translateScale = mat4(
        scale.x,        0.0,            0.0,                0.0,
        0.0,            scale.y,        0.0,                0.0,
        0.0,            0.0,            scale.z,            0.0,
        translate.x,    translate.y,    translate.z,        1.0
    );

    float left = -.6;
    float right = .6;
    float top = .6;
    float bot = -.6;
    float near = 2.0;
    float far = 5.0;
    mat4 camera = mat4(
        2.0*near/(right-left),      0.0,                    0.0,                        0.0,
        0.0,                        2.0*near/(top-bot),     0.0,                        0.0,
        (right+left)/(right-left),  (top+bot)/(top-bot),    (far+near)/(near-far),      -1,
        0.0,                        0.0,                    2.0*far*near/(near-far),    0.0
    );

    gl_Position = camera * (rotate * translateScale * vec4(vPos, 1.0) + vec4(0.0, 0.0, -3.5, 0.0));
    color = vec4(vColor, 1.0);
}
    """

    def fragment_shader_basic_source(self):
        return """
//precision mediump float;

varying vec4 color;

void main(void) {
    gl_FragColor = color;
}
    """

    def initializeGL(self):
        self.initializeOpenGLFunctions()

        self.m_shaderProgram = QtOpenGL.QOpenGLShaderProgram()

        rc1 = self.m_shaderProgram.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Vertex, self.vertex_shader_source())
        rc2 = self.m_shaderProgram.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Fragment, self.fragment_shader_source())
            
        if not rc1 or not rc2:
            print(self.m_shaderProgram.log())

        # Link shader pipeline
        rc = self.m_shaderProgram.link()

        if not rc:
            print(self.m_shaderProgram.log())

        # ----------------------------------------------------------

        self.m_shaderHeightMapProgram = QtOpenGL.QOpenGLShaderProgram()

        rc1 = self.m_shaderHeightMapProgram.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Vertex, self.vertex_shader_heightmap_source())
        rc2 = self.m_shaderHeightMapProgram.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Fragment, self.fragment_shader_heightmap_source())
        
        if not rc1 or not rc2:
            print(self.m_shaderHeightMapProgram.log())

        # Link shader pipeline
        rc = self.m_shaderHeightMapProgram.link()

        if not rc:
            print(self.m_shaderHeightMapProgram.log())
        
        # ----------------------------------------------------------

        self.m_shaderBasicProgram = QtOpenGL.QOpenGLShaderProgram()

        rc1 = self.m_shaderBasicProgram.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Vertex, self.vertex_shader_basic_source())
        rc2 = self.m_shaderBasicProgram.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Fragment, self.fragment_shader_basic_source())
        
        if not rc1 or not rc2:
            print(self.m_shaderBasicProgram.log())

        # Link shader pipeline
        rc = self.m_shaderBasicProgram.link()

        if not rc:
            print(self.m_shaderBasicProgram.link())
        
    def paintGL(self):
        '''
        '''
        if not self.m_shaderProgram or not self.m_shaderHeightMapProgram or not self.m_shaderBasicProgram:
            return

        gcodedrawer : GcodeDrawer = self.m_shaderDrawables[0]
        heightmapdrawer : HeightMapDrawer = self.m_shaderDrawables[1]
        tooldrawer : ToolDrawer = self.m_shaderDrawables[2]
       
        
        #if not self.pathBuffer:
        #    self.pathBuffer = QtOpenGL.QOpenGLBuffer()
        #    self.pathBuffer.bind(GL.GL_ARRAY_BUFFER)
        #    self.gl.bufferData(GL.GL_ARRAY_BUFFER, gcodedrawer.gpuMem, GL.GL_DYNAMIC_DRAW)
        #    # --> ???
        #    self.pathBuffer.release()
    
        resolution = gcodedrawer.resolution

        # Clear viewport
        self.glClearColor(self.m_colorBackground.redF(), self.m_colorBackground.greenF(), self.m_colorBackground.blueF(), 1.0)
        self.glEnable(GL.GL_DEPTH_TEST)
        self.glViewport(0, 0, resolution, resolution)
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Update settings
        if self.m_antialiasing:
            if self.m_msaa:
                self.glEnable(GL.GL_MULTISAMPLE)
            else:
                self.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
                self.glEnable(GL.GL_LINE_SMOOTH)
                self.glHint(GL.GL_POINT_SMOOTH_HINT, GL.GL_NICEST)
                self.glEnable(GL.GL_POINT_SMOOTH)

                self.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
                self.glEnable(GL.GL_BLEND)
        
        if self.m_shaderProgram:
            if gcodedrawer.needsUpdateGeometry():
                gcodedrawer.updateGeometry(self.m_shaderProgram, self)
        if self.m_shaderHeightMapProgram:
            if heightmapdrawer.needsUpdateGeometry():
                heightmapdrawer.updateGeometry(self.m_shaderHeightMapProgram, self)
        if self.m_shaderBasicProgram:
            if tooldrawer.needsUpdateGeometry():
                tooldrawer.updateGeometry(self.m_shaderBasicProgram, self)

        if self.m_shaderProgram:
            gcodedrawer.draw(self.m_shaderProgram)
        if self.m_shaderHeightMapProgram:
            gcodedrawer.draw(self.m_shaderHeightMapProgram)
        if self.m_shaderBasicProgram:
            tooldrawer.draw(self.m_shaderBasicProgram)

        self.m_shaderProgram.release()
        self.m_shaderHeightMapProgram.release()
        self.m_shaderBasicProgram.release()

        self.m_frames += 1
        self.update()

    def resizeGL(self, width: int, height: int):
        self.glViewport(0, 0, width, height)
        self.updateProjection()
        self.resized.emit()

    def createPathTexture(self):
        '''
        '''
        if not self.m_shaderProgram or not self.m_shaderHeightMapProgram or not self.m_shaderBasicProgram:
            return

        gcodedrawer : GcodeDrawer = self.m_shaderDrawables[0]

        if not self.pathFramebuffer:
            self.pathFramebuffer = QtOpenGL.QOpenGLFramebufferObject()
            self.pathFramebuffer.bind()

            self.pathRgbaTexture = QtOpenGL.QOpenGLTexture()
            self.glActiveTexture(GL.GL_TEXTURE0)
            self.pathRgbaTexture.bind(GL.GL_TEXTURE_2D)
            self.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, gcodedrawer.resolution, gcodedrawer.resolution, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
            self.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            self.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            self.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.pathRgbaTexture, 0)
            self.pathRgbaTexture.release()

            renderbuffer = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.PixelUnpackBuffer) # CHECKME
            renderbuffer.bind(GL.GL_RENDERBUFFER)
            self.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_DEPTH_COMPONENT16, gcodedrawer.resolution, gcodedrawer.resolution)
            self.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_RENDERBUFFER, renderbuffer)
            renderbuffer.release()
            
            self.pathFramebuffer.release()
        
        self.pathFramebuffer.bind(GL.GL_FRAMEBUFFER)
        ###self.drawPath()  ## TODO
        self.pathFramebuffer.release()
        self.needToCreatePathTexture = False
        self.needToDrawHeightMap = True


    def updateProjection(self):
        # Reset projection
        self.m_projectionMatrix.setToIdentity()

        asp = self.width() / self.height()
        self.m_projectionMatrix.frustum( \
                (-0.5 + self.m_xPan) * asp, \
                (0.5 + self.m_xPan) * asp,
                -0.5 + self.m_yPan, \
                0.5 + self.m_yPan, 2, self.m_distance * 2)

    def updateView(self):
        # Set view matrix
        self.m_viewMatrix.setToIdentity()

        r = self.m_distance
        angY = M_PI / 180 * self.m_yRot
        angX = M_PI / 180 * self.m_xRot

        eye = QtGui.QVector3D( \
            r * math.cos(angX) * math.sin(angY) + self.m_xLookAt, \
            r * math.sin(angX) + self.m_yLookAt, \
            r * math.cos(angX) * math.cos(angY) + self.m_zLookAt)
        
        center = QtGui.QVector3D(self.m_xLookAt, self.m_yLookAt, self.m_zLookAt)

        xRot = M_PI if self.m_xRot < 0 else 0

        up = QtGui.QVector3D( \
            -math.sin(angY + xRot) if math.fabs(self.m_xRot) == 90 else 0, 
            math.cos(angX), 
            -math.cos(angY + xRot) if math.fabs(self.m_xRot) == 90 else 0)

        self.m_viewMatrix.lookAt(eye, center, up.normalized())

        self.m_viewMatrix.translate(self.m_xLookAt, self.m_yLookAt, self.m_zLookAt)
        self.m_viewMatrix.scale(self.m_zoom, self.m_zoom, self.m_zoom)
        self.m_viewMatrix.translate(-self.m_xLookAt, -self.m_yLookAt, -self.m_zLookAt)

        self.m_viewMatrix.rotate(-90, 1.0, 0.0, 0.0)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.m_lastPos = event.pos()
        self.m_xLastRot = self.m_xRot
        self.m_yLastRot = self.m_yRot
        self.m_xLastPan = self.m_xPan
        self.m_yLastPan = self.m_yPan

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if (event.buttons() & QtGui.Qt.MiddleButton and (not(event.modifiers() & QtGui.Qt.ShiftModifier))) or event.buttons() & QtCore.Qt.LeftButton:

            self.stopViewAnimation()

            self.m_yRot = self.normalizeAngle(self.m_yLastRot - (event.pos().x() - self.m_lastPos.x()) * 0.5)
            self.m_xRot = self.m_xLastRot + (event.pos().y() - self.m_lastPos.y()) * 0.5

            if self.m_xRot < -90:
                self.m_xRot = -90
            if self.m_xRot > 90:
                self.m_xRot = 90

            self.updateView()
            self.rotationChanged.emit()
    

        if (event.buttons() & QtCore.Qt.MiddleButton and event.modifiers() & QtGui.Qt.ShiftModifier) or event.buttons() & QtCore.Qt.RightButton:
            self.m_xPan = self.m_xLastPan - (event.pos().x() - self.m_lastPos.x()) * 1 / (float)(self.width())
            self.m_yPan = self.m_yLastPan + (event.pos().y() - self.m_lastPos.y()) * 1 / (float)(self.height())

            self.updateProjection()

    def wheelEvent(self, we: QtGui.QWheelEvent):
        if self.m_zoom > 0.1 and we.angleDelta().y() < 0:
            self.m_xPan -= ((float)(we.position().x() / self.width() - 0.5 + self.m_xPan)) * (1 - 1 / ZOOMSTEP)
            self.m_yPan += ((float)(we.position().y() / self.height() - 0.5 - self.m_yPan)) * (1 - 1 / ZOOMSTEP)

            self.m_zoom /= ZOOMSTEP
        elif self.m_zoom < 10 and we.angleDelta().y() > 0:
            self.m_xPan -= ((float)(we.position().x() / self.width() - 0.5 + self.m_xPan)) * (1 - ZOOMSTEP)
            self.m_yPan += ((float)(we.position().y() / self.height() - 0.5 - self.m_yPan)) * (1 - ZOOMSTEP)

            self.m_zoom *= ZOOMSTEP

        self.updateProjection()
        self.updateView()

    def timerEvent(self, te: QtCore.QTimerEvent):
        #return
        if te.timerId() == self.m_timerPaint.timerId():
            if self.m_animateView:
                self.viewAnimation()
            if self.m_updatesEnabled:
                self.update()
        else:
            self.timerEvent(te)

    def onVisualizatorRotationChanged(self):
        self.update()
        self.cmdIsometric.setChecked(False)

