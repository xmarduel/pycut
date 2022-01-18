
import math

from typing import List

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from PySide6 import QtOpenGLWidgets
from PySide6 import QtOpenGL

from OpenGL import GL

from PySide6.QtCore import Signal, Slot
from PySide6.QtCore import qIsNaN

from gcodeviewer.drawers.shaderdrawable import ShaderDrawable

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
        return """#ifdef GL_ES
// Set default precision to medium
precision mediump int;
precision mediump float;
#endif

uniform mat4 mvp_matrix;
uniform mat4 mv_matrix;

attribute vec4 a_position;
attribute vec4 a_color;
attribute vec4 a_start;

varying vec4 v_color;
varying vec2 v_position;
varying vec2 v_start;
varying vec2 v_texture;

bool isNan(float val)
{
    return (val > 65535.0);
}

void main()
{
    // Calculate interpolated vertex position & line start point
    v_position = (mv_matrix * a_position).xy;

    if (!isNan(a_start.x) && !isNan(a_start.y)) {
        v_start = (mv_matrix * a_start).xy;
        v_texture = vec2(65536.0, 0);
    } else {
        // v_start.x should be Nan to draw solid lines
        v_start = a_start.xy;

        // set texture coord
        v_texture = a_start.yz;

        // set point size
        if (isNan(a_start.y) && !isNan(a_start.z)) gl_PointSize = a_start.z;
    }

    // Calculate vertex position in screen space
    gl_Position = mvp_matrix * a_position;

    v_color = a_color;
}
"""

    def fragment_shader_source(self):
        return """#ifdef GL_ES
// Set default precision to medium
precision mediump int;
precision mediump float;
#endif

//Dash grid (px) = factor * pi;
const float factor = 2.0;

varying vec4 v_color;
varying vec2 v_position;
varying vec2 v_start;
varying vec2 v_texture;

uniform sampler2D texture;

bool isNan(float val)
{
    return (val > 65535.0);
}

void main()
{
    // Draw dash lines
    if (!isNan(v_start.x)) {
        vec2 sub = v_position - v_start;
        float coord = length(sub.x) > length(sub.y) ? gl_FragCoord.x : gl_FragCoord.y;
        if (cos(coord / factor) > 0.0) discard;
    }

    // Set fragment color
    if (!isNan(v_texture.x)) {
        gl_FragColor = texture2D(texture, v_texture);
    } else {
        gl_FragColor = v_color;
    }
}"""


    def initializeGL(self):
        self.initializeOpenGLFunctions()

        self.m_shaderProgram = QtOpenGL.QOpenGLShaderProgram()

        with_resource = False

        if with_resource:
            # Compile vertex shader
            self.m_shaderProgram.addShaderFromSourceFile(QtOpenGL.QOpenGLShader.Vertex, ":/shaders/vshader.glsl")
            # Compile fragment shader
            self.m_shaderProgram.addShaderFromSourceFile(QtOpenGL.QOpenGLShader.Fragment, ":/shaders/fshader.glsl")
        else:
            _vertex_shader = self.vertex_shader_source()
            _fragment_shader = self.fragment_shader_source()

            self.m_shaderProgram.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Vertex, _vertex_shader)
            self.m_shaderProgram.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Fragment, _fragment_shader)
            
        # Link shader pipeline
        self.m_shaderProgram.link()

    def paintGL(self):
        # Segment counter
        vertices = 0

        # Clear viewport
        self.glClearColor(self.m_colorBackground.redF(), self.m_colorBackground.greenF(), self.m_colorBackground.blueF(), 1.0)
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
            self.m_shaderProgram.setUniformValue("mvp_matrix", self.m_projectionMatrix * self.m_viewMatrix)
            self.m_shaderProgram.setUniformValue("mv_matrix", self.m_viewMatrix)

            # Update geometries in current opengl context
            for drawable in self.m_shaderDrawables:
                if drawable.needsUpdateGeometry():
                    drawable.updateGeometry(self.m_shaderProgram)

            # Draw geometries
            for drawable in self.m_shaderDrawables:
                drawable.draw(self.m_shaderProgram)
                if drawable.visible():
                    vertices += drawable.getVertexCount()

            self.m_shaderProgram.release()

        # Draw 2D
        self.glDisable(GL.GL_DEPTH_TEST)
        self.glDisable(GL.GL_MULTISAMPLE)
        self.glDisable(GL.GL_LINE_SMOOTH)
        self.glDisable(GL.GL_BLEND)

        if True:  # no timer event because commented (actually crash on painter) 
            pass

            '''
            painter = QtGui.QPainter(self)

            painter.beginNativePainting()
            painter.endNativePainting()

            pen = QtGui.QPen(self.m_colorText)
            painter.setPen(pen)

            x = 10
            y = self.height() - 60

            painter.drawText(QtCore.QPoint(x, y), "X: %0.*f ... %0.*f" % (3, self.m_xMin , 3,self.m_xMax))
            painter.drawText(QtCore.QPoint(x, y + 15), "Y: %0.*f ... %0.*f" % (3, self.m_yMin, 3, self.m_yMax))
            painter.drawText(QtCore.QPoint(x, y + 30), "Z: %0.*f ... %0.*f" % (3, self.m_zMin, 3, self.m_zMax))
            painter.drawText(QtCore.QPoint(x, y + 45), "%0.*f / %0.*f / %0.*f" % (3, self.m_xSize, 3, self.m_ySize, 3, self.m_zSize))

            fm = QtGui.QFontMetrics(painter.font())

            painter.drawText(QtCore.QPoint(x, fm.height() + 10), self.m_parserStatus)
            painter.drawText(QtCore.QPoint(x, fm.height() * 2 + 10), self.m_speedState)
            painter.drawText(QtCore.QPoint(x, fm.height() * 3 + 10), self.m_pinState)

            xstr = "Vertices: %d" % vertices
            painter.drawText(QtCore.QPoint(self.width() - fm.horizontalAdvance(xstr) - 10, y + 30), xstr)
            xstr = "FPS: %d" % self.m_fps
            painter.drawText(QtCore.QPoint(self.width() - fm.horizontalAdvance(xstr) - 10, y + 45), xstr)

            xstr = self.m_spendTime.toString("hh:mm:ss") + " / " + self.m_estimatedTime.toString("hh:mm:ss")
            painter.drawText(QtCore.QPoint(self.width() - fm.horizontalAdvance(xstr) - 10, y), xstr)

            xstr = self.m_bufferState
            painter.drawText(QtCore.QPoint(self.width() - fm.horizontalAdvance(xstr) - 10, y + 15), xstr)

            self.m_frames += 1
            '''

        self.m_frames += 1
        self.update()

    def resizeGL(self, width: int, height: int):
        self.glViewport(0, 0, width, height)
        self.updateProjection()
        self.resized.emit()

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

