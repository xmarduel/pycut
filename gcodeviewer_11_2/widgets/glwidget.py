import math

from typing import List
from typing import cast
from typing import Optional

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from PySide6.QtGui import QVector3D

from PySide6.QtCore import QPointF
from PySide6.QtCore import Signal, Slot
from PySide6.QtCore import qFuzzyIsNull

from PySide6 import QtOpenGLWidgets
from PySide6 import QtOpenGL

from OpenGL import GL  # type: ignore [import-untyped]

from gcodeviewer_11_2.drawers.shaderdrawable import ShaderDrawable
from gcodeviewer_11_2.util.util import Util


ZOOMSTEP = 1.1


class GLWidget(QtOpenGLWidgets.QOpenGLWidget, QtGui.QOpenGLFunctions):
    """ """

    rotationChanged = Signal()
    resized = Signal()

    def __init__(self, parent=None):
        QtOpenGLWidgets.QOpenGLWidget.__init__(self, parent)
        QtGui.QOpenGLFunctions.__init__(self)

        self.m_shaderProgram = None

        self.m_rot = QPointF(90.0, 0.0)
        self.m_rotAnimationTarget = self.m_rot

        self.m_storedRot = QPointF(0.0, 0.0)
        self.m_pan = QPointF(0.0, 0.0)
        self.m_storedPan = QPointF(0.0, 0.0)
        self.m_lookAt = QVector3D(0.0, 0.0, 0.0)
        
        self.m_lastPos = QtCore.QPoint(0, 0)
        self.m_zoom = 1
        self.m_distance = 100.0
        self.m_perspective = False
        self.m_gestureProcessing = False

        self.m_spendTime = QtCore.QTime()
        self.m_spendTime.setHMS(0, 0, 0)

        self.m_estimatedTime = QtCore.QTime()
        self.m_estimatedTime.setHMS(0, 0, 0)
        
        self.m_vsync = False
        self.m_targetFps = 60

        self.m_updating = False

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.grabGesture(QtCore.Qt.GestureType.PanGesture)
        self.grabGesture(QtCore.Qt.GestureType.PinchGesture)

        fmt = QtGui.QSurfaceFormat() # format();
        fmt.setSamples(8)
        fmt.setSwapInterval(0)
        self.setFormat(fmt)

        # self.m_overlay = Overlay(self)

        QtCore.QTimer.singleShot(1000, self, GLWidget.onFramesTimer)

        self.m_viewLowerBounds = QVector3D(0.0, 0.0, 0.0)
        self.m_viewUpperBounds = QVector3D(0.0, 0.0, 0.0)
        self.m_viewRanges = QVector3D(0.0, 0.0, 0.0)

        self.m_modelLowerBounds = QVector3D(0.0, 0.0, 0.0)
        self.m_modelUpperBounds = QVector3D(0.0, 0.0, 0.0)
        self.m_modelRanges = QVector3D(0.0, 0.0, 0.0)

        self.m_lineWidth = 0.0
        self.m_pointSize = 0.0
        self.m_antialiasing = True
        self.m_msaa = True
        self.m_zBuffer = True
        self.m_frames = 0
        self.m_fps = 0
        self.m_animationFrame = 0
        self.m_vertices = 0
        self.m_timerPaint = QtCore.QBasicTimer()
        self.m_rotAnimationStart = QPointF(0.0, 0.0)
        self.m_rotAnimationTarget = QPointF(0.0, 0.0)
        self.m_animateView = False
        self.m_parserStatus = ""
        self.m_speedState = ""
        self.m_pinState = ""
        self.m_bufferState = ""
        self.m_cursorPos = QVector3D(0.0, 0.0, 0.0)
        self.m_updatesEnabled = False

        self.m_projectionMatrix = QtGui.QMatrix4x4()
        self.m_viewMatrix = QtGui.QMatrix4x4()

        self.m_planeDepth = 0.0
        self.m_windowSizeWorld = 0.0

        self.updateProjection()
        self.updateView()

        self.m_shaderDrawables: List[ShaderDrawable] = []
        self.m_shaderPrograms: Optional[QtOpenGL.QOpenGLShaderProgram] = None

        self.m_colorBackground = QtGui.QColor(255, 255, 255)
        self.m_colorText = QtGui.QColor()

        # self.m_overlay = Overlay()
       
        self.cmdFit = QtWidgets.QToolButton(self)
        self.cmdIsometric = QtWidgets.QToolButton(self)
        self.cmdTop = QtWidgets.QToolButton(self)
        self.cmdFront = QtWidgets.QToolButton(self)
        self.cmdLeft = QtWidgets.QToolButton(self)

        self.cmdFit.setMinimumSize(QtCore.QSize(24, 24))
        self.cmdIsometric.setMinimumSize(QtCore.QSize(24, 24))
        self.cmdTop.setMinimumSize(QtCore.QSize(24, 24))
        self.cmdFront.setMinimumSize(QtCore.QSize(24, 24))
        self.cmdLeft.setMinimumSize(QtCore.QSize(24, 24))

        self.cmdFit.setMaximumSize(QtCore.QSize(24, 24))
        self.cmdIsometric.setMaximumSize(QtCore.QSize(24, 24))
        self.cmdTop.setMaximumSize(QtCore.QSize(24, 24))
        self.cmdFront.setMaximumSize(QtCore.QSize(24, 24))
        self.cmdLeft.setMaximumSize(QtCore.QSize(24, 24))

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
        cmdIsometric_w = self.cmdIsometric.width()

        self.cmdIsometric.move(self.width() - self.cmdIsometric.width() - 8, 8)
        self.cmdTop.move(
            self.cmdIsometric.geometry().left() - self.cmdTop.width() - 8, 8
        )
        self.cmdLeft.move(
            self.width() - self.cmdLeft.width() - 8,
            self.cmdIsometric.geometry().bottom() + 8,
        )
        self.cmdFront.move(
            self.cmdLeft.geometry().left() - self.cmdFront.width() - 8,
            self.cmdIsometric.geometry().bottom() + 8,
        )
        self.cmdFit.move(
            self.width() - self.cmdFit.width() - 8, self.cmdLeft.geometry().bottom() + 8
        )

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

        if (
            hasattr(gl_widget_container, "m_currentDrawer")
            and gl_widget_container.m_currentDrawer is not None
        ):
            self.fitDrawable(gl_widget_container.m_currentDrawer)

    def calculateVolume(self, size: QtGui.QVector3D) -> float:
        return size.x() * size.y() * size.z()

    def addDrawable(self, drawable: ShaderDrawable):
        self.m_shaderDrawables.append(drawable)

    def fitDrawable(self, drawable: Optional[ShaderDrawable] = None):
        self.stopViewAnimation()

        if drawable != None:
            self.m_viewLowerBounds = Util.nAssign(drawable.getViewLowerBounds())
            self.m_viewUpperBounds = Util.nAssign(drawable.getViewUpperBounds())
            self.m_viewRanges = drawable.getViewRanges()

            self.m_modelLowerBounds = Util.nAssign(drawable.getModelLowerBounds())
            self.m_modelUpperBounds = Util.nAssign(drawable.getModelUpperBounds())
            self.m_modelRanges = drawable.getModelRanges()

            a = self.m_viewRanges.y() / 2 / 0.25 * 1.3 + (self.m_viewUpperBounds - self.m_viewLowerBounds).z() / 2;
            b = self.m_viewRanges.x() / 2 / 0.25 * 1.3 / (self.width() / self.height()) + (self.m_viewUpperBounds - self.m_viewLowerBounds).z() / 2
            
            self.m_distance = max(a, b)

            if self.m_distance == 0:
                self.m_distance = 200

            self.m_lookAt = QVector3D(
                (self.m_viewUpperBounds.x() - self.m_viewLowerBounds.x()) / 2 + self.m_viewLowerBounds.x(),
                (self.m_viewUpperBounds.z() - self.m_viewLowerBounds.z()) / 2 + self.m_viewLowerBounds.z(),
                -((self.m_viewUpperBounds.y() - self.m_viewLowerBounds.y()) / 2 + self.m_viewLowerBounds.y())
            )
        else:
            self.m_distance = 200
            self.m_lookAt = QVector3D()
            self.m_viewLowerBounds = QVector3D()
            self.m_viewUpperBounds = QVector3D()
            self.m_viewRanges = QVector3D()
            self.m_modelLowerBounds = QVector3D()
            self.m_modelUpperBounds = QVector3D()
            self.m_modelRanges = QVector3D()

        self.m_xPan = QPointF()
        self.m_zoom = 1

        self.updateProjection()
        self.updateView()

    def updateModelBounds(self, drawable: ShaderDrawable):
        self.m_modelLowerBounds = Util.nAssign(drawable.getModelLowerBounds())
        self.m_modelUpperBounds = Util.nAssign(drawable.getModelUpperBounds())
        self.m_modelRanges = drawable.getModelRanges()

    def normalizeAngle(self, angle: float) -> float:
        while angle < 0:
            angle += 360
        while angle > 360:
            angle -= 360

        return angle

    def beginViewAnimation(self):
        self.m_rotAnimationStart = self.m_rot
        self.m_animationFrame = 0
        self.m_animateView = True

    def stopViewAnimation(self):
        self.m_animateView = False

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
        """no animation yet"""
        self.m_rotAnimationTarget = QPointF(45,  405 if self.m_rot.y() > 180 else 45)

        # no animation. then
        self.m_rot = QPointF(45, 405 if self.m_rot.y() > 180 else 45)

        # self.beginViewAnimation()

    def setTopView(self):
        """no animation yet"""
        self.m_rotAnimationTarget = QPointF(90, 360 if self.m_rot.y() > 180 else 0)

        # no animation. then
        self.m_rot = QPointF(90, 360 if self.m_rot.y() > 180 else 0)

        # self.beginViewAnimation()

    def setFrontView(self):
        """no animation yet"""
        self.m_rotAnimationTarget = QPointF(0, 360 if self.m_rot.y() > 180 else  0)

        # no animation. then
        self.m_rot = QPointF(0, 360 if self.m_rot .y() > 180 else 0)

        # self.beginViewAnimation()

    def setLeftView(self):
        """no animation yet"""
        self.m_rotAnimationTarget = QPointF(0, 450 if self.m_rot.y() > 270 else 90)

        # no animation. then
        self.m_rot = QPointF(0, 450 if self.m_rot.y() > 270 else 90)

        # self.beginViewAnimation()

    def fps(self) -> int:
        return self.m_targetFps

    def setFps(self, fps: int):
        if fps <= 0:
            return

        self.m_targetFps = fps
        self.m_timerPaint.stop()

        self.setUpdatesEnabled(self.m_updatesEnabled)

    def parserStatus(self) -> str:
        return self.m_parserStatus

    def setParserStatus(self, parserStatus: str):
        self.m_parserStatus = parserStatus

    def bufferState(self) -> str:
        return self.m_bufferState

    def setBufferState(self, bufferState: str):
        self.m_bufferState = bufferState

    def cursorPos(self) -> QVector3D:
        return self.m_cursorPos

    def setCursorPos(self, cursorPos: QVector3D):
        self.m_cursorPos = cursorPos

    def zBuffer(self) -> bool:
        return self.m_zBuffer

    def setZBuffer(self, zBuffer: bool):
        self.m_zBuffer = zBuffer

    def updatesEnabled(self) -> bool:
        return self.m_updatesEnabled

    def setUpdatesEnabled(self, updatesEnabled: bool):
        self.m_updatesEnabled = updatesEnabled

        if updatesEnabled:
            self.m_timerPaint.start(0 if self.m_vsync else 1000 / self.m_targetFps, QtCore.Qt.TimerType.PreciseTimer, self)
        else:
            self.m_timerPaint.stop()

    def msaa(self) -> bool:
        return self.m_msaa

    def setMsaa(self, msaa: bool):
        self.m_msaa = msaa

    def colorBackground(self) -> QtGui.QColor:
        return self.m_colorBackground

    def setColorBackground(self, colorBackground: QtGui.QColor):
        self.m_colorBackground = colorBackground

    def colorText(self) -> QtGui.QColor:
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
        if vsync != self.m_vsync:
            self.m_vsync = vsync
            fmt = QtGui.QSurfaceFormat()
            fmt.setSwapInterval(1 if vsync else 0)
            self.setFormat(fmt)

    def speedState(self) -> str:
        return self.m_speedState

    def setSpeedState(self, speedState: str):
        self.m_speedState = speedState

    def perspective(self) ->  bool:
        return self.m_perspective

    def setPerspective(self, perspective: bool):
        self.m_perspective = perspective

        self.updateProjection()
        self.updateView()

    def updating(self) -> bool:
        return self.m_updating

    def setUpdating(self, updating: bool):
        self.m_updating = updating

    def pinState(self) -> str:
        return self.m_pinState

    def setPinState(self, pinState: str):
        self.m_pinState = pinState

    @Slot()
    def onFramesTimer(self):
        self.m_fps = self.m_frames
        self.m_frames = 0

        QtCore.QTimer.singleShot(1000, GLWidget.onFramesTimer)

    @Slot()
    def viewAnimation(self):
        t = self.m_animationFrame / (self.m_fps * 0.2)

        self.m_animationFrame += 1

        if t >= 1:
            self.stopViewAnimation()

        ec = QtCore.QEasingCurve(QtCore.QEasingCurve.OutExpo)
        val = ec.valueForProgress(t)

        self.m_rot = self.m_rotAnimationStart + (self.m_rotAnimationTarget - self.m_rotAnimationStart) * val


        self.updateView()

    def cleanup(self):
        pass

    def vertex_shader_source(self):
        return """#version 110
#define DATA_TYPE_LINE 0
#define DATA_TYPE_DASH 1
#define DATA_TYPE_DASH_DOT 2
#define DATA_TYPE_POINT 3
#define DATA_TYPE_TRIANGLE 4

uniform mat4 p_matrix;
uniform mat4 v_matrix;
uniform mat4 m_matrix;

attribute vec4 a_position;
attribute vec4 a_color;
attribute vec4 a_data;
attribute float a_type;

varying vec2 v_position;
varying vec4 v_color;
varying vec2 v_texture;
varying float v_type;
varying vec2 v_start;

mat4 mvp_matrix;

int type;

void main()
{
    mvp_matrix = p_matrix * v_matrix * m_matrix;

    v_type = a_type;
    type = int(v_type + 0.1);

    if (type == DATA_TYPE_LINE) {
    } else if (type == DATA_TYPE_DASH) {
        v_start = (mvp_matrix * a_data).xy;
        v_position = (mvp_matrix * a_position).xy;
    } else if (type == DATA_TYPE_DASH_DOT) {
        v_start = (mvp_matrix * a_data).xy;
        v_position = (mvp_matrix * a_position).xy;
    } else if (type == DATA_TYPE_POINT) {
        gl_PointSize = a_data.x;
    } else if (type == DATA_TYPE_TRIANGLE) {
        v_texture = a_data.yz;
    }

    v_color = a_color;
    gl_Position = mvp_matrix * a_position;
}
"""

    def fragment_shader_source(self):
        return """#version 110
#define DATA_TYPE_LINE 0
#define DATA_TYPE_DASH 1
#define DATA_TYPE_DASH_DOT 2
#define DATA_TYPE_POINT 3
#define DATA_TYPE_TRIANGLE 4

uniform sampler2D texture;

varying  vec4 v_color;
varying  vec2 v_position;
varying  vec2 v_texture;
varying  vec2 v_start;
varying  float v_type;

const float factor = 2.0;
int type;

void main()
{
    type = int(v_type + 0.1);

    if (type == DATA_TYPE_LINE) {
        gl_FragColor = v_color;
    } else if (type == DATA_TYPE_DASH) {
        vec2 sub = v_position - v_start;
        float coord = length(sub.x) > length(sub.y) ? gl_FragCoord.x : gl_FragCoord.y;
        if (cos(coord / factor) > 0.0) discard;
        gl_FragColor = v_color;
    } else if (type == DATA_TYPE_DASH_DOT) {
        vec2 sub = v_position - v_start;
        float coord = length(sub.x) > length(sub.y) ? gl_FragCoord.x : gl_FragCoord.y;
        float v = cos(coord / factor * 0.5);
        if (v > 0.0 && v < 0.95) discard;
        gl_FragColor = v_color;
    } else if (type == DATA_TYPE_POINT) {
        gl_FragColor = v_color;
    } else if (type == DATA_TYPE_TRIANGLE) {
        gl_FragColor = texture2D(texture, v_texture);
    }
}"""

    def initializeGL(self):
        self.initializeOpenGLFunctions()

        self.m_shaderProgram = QtOpenGL.QOpenGLShaderProgram()

        with_resource = False

        if with_resource:
            self.m_shaderProgram.addShaderFromSourceFile(
                QtOpenGL.QOpenGLShader.Vertex, ":/shaders/vshader.glsl"
            )
            self.m_shaderProgram.addShaderFromSourceFile(
                QtOpenGL.QOpenGLShader.Fragment, ":/shaders/fshader.glsl"
            )
        else:
            self.m_shaderProgram.addShaderFromSourceCode(
                QtOpenGL.QOpenGLShader.Vertex, self.vertex_shader_source()
            )
            self.m_shaderProgram.addShaderFromSourceCode(
                QtOpenGL.QOpenGLShader.Fragment, self.fragment_shader_source()
            )

        # Link shader pipeline
        self.m_shaderProgram.link()

    def paintGL(self):

        # if self.m_animateView:
        #     self.viewAnimation()

        # Segment counter
        vertices = 0

        # Clear viewport
        self.glClearColor(
            self.m_colorBackground.redF(),
            self.m_colorBackground.greenF(),
            self.m_colorBackground.blueF(),
            1.0,
        )
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Shader drawable points
        self.glEnable(GL.GL_PROGRAM_POINT_SIZE)

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

        if self.m_zBuffer:
            self.glEnable(GL.GL_DEPTH_TEST)

        if self.m_shaderProgram:
            # Draw 3d
            self.m_shaderProgram.bind()

            # Set modelview-projection matrix
            self.m_shaderProgram.setUniformValue("p_matrix", self.m_projectionMatrix)
            self.m_shaderProgram.setUniformValue("v_matrix", self.m_viewMatrix)

            # Update geometries in current opengl context
            for drawable in self.m_shaderDrawables:
                if drawable.needsUpdateGeometry():
                    drawable.updateGeometry(self.m_shaderProgram)

            # Draw geometries
            for drawable in self.m_shaderDrawables:
                if drawable.visible():
                    if drawable.windowScaling():
                        drawable.setWorldScale(self.m_windowSizeWorld * drawable.windowScale())
                
                    self.m_shaderProgram.setUniformValue("m_matrix", drawable.modelMatrix())
                    drawable.draw(self.m_shaderProgram)
                    vertices += drawable.getVertexCount()

            self.m_shaderProgram.release()

        self.glDisable(GL.GL_MULTISAMPLE)
        self.glDisable(GL.GL_LINE_SMOOTH)
        self.glDisable(GL.GL_POINT_SMOOTH)
        self.glDisable(GL.GL_BLEND)
        self.glDisable(GL.GL_DEPTH_TEST)

        # Draw 2D
        self.m_vertices = vertices
        # self.m_overlay.update()

        self.m_frames += 1
        self.update()

    def resizeGL(self, width: int, height: int):
        self.glViewport(0, 0, width, height)
        self.updateProjection()

        # self.m_overlay.resize(width, height)
        
        self.resized.emit()

    def updateProjection(self):
        # Reset projection
        self.m_projectionMatrix.setToIdentity()

        if self.m_perspective:
            zNear = 2.0
            zFar = self.m_distance * 10

            asp = self.width() / self.height()
            self.m_projectionMatrix.frustum(
                (-0.5 + self.m_pan.x()) * asp,
                (0.5 + self.m_pan.x()) * asp,
                -0.5 + self.m_pan.y(),
                0.5 + self.m_pan.y(),
                zNear,
                zFar
            )

            z = self.m_distance + (self.m_viewUpperBounds + self.m_viewLowerBounds).z() / 2 * self.m_zoom
            self.m_planeDepth = (1 / z - 1 / zNear) / (1 / zFar - 1 / zNear) * 2 - 1
        else:
            paddingScale = 1.3

            # Rollback plane to view
            if qFuzzyIsNull(self.m_viewRanges.length()):
                self.m_viewRanges = QVector3D(100, 100, 0) / paddingScale
        

            screenToWorld = max(
                self.m_viewRanges.x() / self.width(),
                self.m_viewRanges.y() / self.height()
            ) * paddingScale

            # 1000.0 - maximum z-coordinate
            clip = max(1000.0, self.m_viewRanges.length())

            self.m_projectionMatrix.ortho(
                (-self.width() / 2 + self.m_pan.x() * self.width()) * screenToWorld / self.m_zoom,
                (self.width() / 2 + self.m_pan.x() * self.width()) * screenToWorld / self.m_zoom,
                (-self.height() / 2 + self.m_pan.y() * self.height()) * screenToWorld / self.m_zoom,
                (self.height() / 2 + self.m_pan.y() * self.height()) * screenToWorld / self.m_zoom,
                -clip,
                clip
            )

            self.m_planeDepth = 0

    def updateView(self):

        if self.m_perspective:

            # Set view matrix
            self.m_viewMatrix.setToIdentity()

            ang = self.m_rot * math.pi / 180

            eye = self.m_lookAt + QVector3D(
                math.cos(ang.x()) * math.sin(ang.y()),
                math.sin(ang.x()),
                math.cos(ang.x()) * math.cos(ang.y())
            ) * self.m_distance

            up_x = math.fabs( -math.sin(ang.y() + math.pi if self.m_rot.x() < 0 else 0)) if self.m_rot.x() == 90 else 0
            up_y = math.cos(ang.x())
            up_z = math.fabs( -math.cos(ang.y() + math.pi if self.m_rot.x() < 0 else 0)) if self.m_rot.x() == 90 else 0

            up = QVector3D(up_x, up_y, up_z)

            self.m_viewMatrix.lookAt(eye, self.m_lookAt, up.normalized())

            self.m_viewMatrix.translate(self.m_lookAt)
            self.m_viewMatrix.scale(self.m_zoom)
            self.m_viewMatrix.translate(-self.m_lookAt)

            self.m_viewMatrix.rotate(-90, 1.0, 0.0, 0.0)

        else:
           
            self.m_viewMatrix.setToIdentity()

            ang = self.m_rot * math.pi / 180

            eye = self.m_lookAt + QVector3D(
                math.cos(ang.x()) * math.sin(ang.y()),
                math.sin(ang.x()),
                math.cos(ang.x()) * math.cos(ang.y())
            )

            up_x = -math.sin(ang.y() + (math.pi if self.m_rot.x() < 0 else 0)) if math.fabs(self.m_rot.x()) == 90 else 0
            up_y = math.cos(ang.x())
            up_z = -math.cos(ang.y() + (math.pi if self.m_rot.x() < 0 else 0)) if math.fabs(self.m_rot.x()) == 90 else 0

            up = QVector3D(up_x, up_y, up_z)

            self.m_viewMatrix.lookAt(eye, self.m_lookAt, up.normalized())
            self.m_viewMatrix.rotate(-90, 1.0, 0.0, 0.0)


        ivp, res = (self.m_projectionMatrix * self.m_viewMatrix).inverted()
        self.m_windowSizeWorld = (ivp.map(QVector3D(0, 1, self.m_planeDepth)) - ivp.map(QVector3D(0, 0, self.m_planeDepth))).length() * 2.0;

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.m_lastPos = event.pos()
        
        self.m_storedRot = self.m_rot
        self.m_storedPan = self.m_pan

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.m_gestureProcessing:
            self.m_lastPos = event.pos()
            self.m_storedRot = self.m_rot
            self.m_storedPan = self.m_pan

            return

        if (event.buttons() & QtCore.Qt.MouseButton.MiddleButton and (not (event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier))) or \
           (event.buttons() & QtCore.Qt.MouseButton.LeftButton and (not (event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier))):
            self.stopViewAnimation()

            self.m_rot.setY(self.normalizeAngle(self.m_storedRot.y() - (event.pos().x() - self.m_lastPos.x()) * 0.5))
            self.m_rot.setX(self.m_storedRot.x() + (event.pos().y() - self.m_lastPos.y()) * 0.5)

            if self.m_rot.x() < -90:
                self.m_rot.setX(-90)
            if self.m_rot.x() > 90:
                self.m_rot.setX(90)

            self.updateView()
            self.rotationChanged.emit()

        if (event.buttons() & QtCore.Qt.MouseButton.MiddleButton and (event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier)) or \
           (event.buttons() & QtCore.Qt.MouseButton.RightButton) or \
           (event.buttons() & QtCore.Qt.MouseButton.LeftButton   and (event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier)):
            self.m_pan.setX(self.m_storedPan.x() - (event.pos().x() - self.m_lastPos.x()) * 1 / self.width())
            self.m_pan.setY(self.m_storedPan.y() + (event.pos().y() - self.m_lastPos.y()) * 1 / self.height())

            self.updateProjection()

    def wheelEvent(self, we: QtGui.QWheelEvent):
        if True or we.angleDelta().manhattanLength() >= 120: # always zoom
            if self.m_zoom > 0.1 and we.angleDelta().y() < 0:
                self.m_pan.setX(self.m_pan.x() - (we.position().x() / self.width() - 0.5 + self.m_pan.x()) * (1 - 1 / ZOOMSTEP))
                self.m_pan.setY(self.m_pan.y() + (we.position().y() / self.height() - 0.5 - self.m_pan.y()) * (1 - 1 / ZOOMSTEP))

                self.m_zoom /= ZOOMSTEP

            elif self.m_zoom < 10 and we.angleDelta().y() > 0: 
        
                self.m_pan.setX(self.m_pan.x() - (we.position().x() / self.width() - 0.5 + self.m_pan.x()) * (1 - ZOOMSTEP))
                self.m_pan.setY(self.m_pan.y() + (we.position().y() / self.height() - 0.5 - self.m_pan.y()) * (1 - ZOOMSTEP))

                self.m_zoom *= ZOOMSTEP

            self.updateProjection()
            self.updateView()
        else:
            self.m_pan.setX(self.m_pan.x() - we.angleDelta().x() * 1 / self.width())
            self.m_pan.setY(self.m_pan.y() + we.angleDelta().y() * 1 / self.height())

            self.updateProjection()

    def event(self, event: QtCore.QEvent) -> bool:
        """ """
        if event.type() == QtCore.QEvent.Type.Gesture:
            gestureEvent = cast(QtWidgets.QGestureEvent, event)
            
            pinGesturePin =  gestureEvent.gesture(QtCore.Qt.GestureType.PinchGesture)
            panGesturePan = gestureEvent.gesture(QtCore.Qt.GestureType.PanGesture)

            if pinGesturePin:
                pinchGesture = cast(QtWidgets.QPinchGesture, pinGesturePin)
  
                if pinchGesture.state() == QtCore.Qt.GestureState.GestureStarted or pinchGesture.state() == QtCore.Qt.GestureState.GestureUpdated:
                    self.m_gestureProcessing = True

                    if (self.m_zoom * pinchGesture.scaleFactor()) > 0.1 and (self.m_zoom * pinchGesture.scaleFactor()) < 10.0:
                        relativeCenterPoint = self.mapFromGlobal(pinchGesture.centerPoint().toPoint())

                        self.m_pan.setX(self.m_pan.x() - (relativeCenterPoint.x() / self.width() - 0.5 + self.m_pan.x()) * (1 - pinchGesture.scaleFactor()))
                        self.m_pan.setY(self.m_pan.y() + (relativeCenterPoint.y() / self.height() - 0.5 - self.m_pan.y())* (1 - pinchGesture.scaleFactor()))

                        self.m_zoom *= pinchGesture.scaleFactor()

                    self.updateProjection();
                    self.updateView();
            
                elif pinchGesture.state() == QtCore.Qt.GestureState.GestureFinished or pinchGesture.state() == QtCore.Qt.GestureState.GestureCanceled:
            
                    self.m_gestureProcessing = False
            
            elif panGesturePan:
                panGesture = cast(QtWidgets.QPanGesture, panGesturePan)

                if panGesture.state() == QtCore.Qt.GestureState.GestureStarted or panGesture.state() == QtCore.Qt.GestureState.GestureUpdated:
            
                    self.m_gestureProcessing = True

                    self.m_pan.setX(self.m_pan.x() - (panGesture.delta().x()) * 1 / self.width())
                    self.m_pan.setY(self.m_pan.y() + (panGesture.delta().y()) * 1 / self.height())

                    self.updateProjection()
            
                elif panGesture.state() == QtCore.Qt.GestureState.GestureFinished or panGesture.state() == QtCore.Qt.GestureState.GestureCanceled:
            
                    self.m_gestureProcessing = False


        return QtOpenGLWidgets.QOpenGLWidget.event(self, event)

    def timerEvent(self, te: QtCore.QTimerEvent):
        if te.timerId() == self.m_timerPaint.timerId():
            self.update()
        else:
            QtOpenGLWidgets.QOpenGLWidget.timerEvent(self, te)

    def onVisualizatorRotationChanged(self):
        self.update()
        self.cmdIsometric.setChecked(False)
