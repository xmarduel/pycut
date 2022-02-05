
import ctypes
import numpy as np
import sys
from typing import List
from PySide6.QtCore import Signal, SIGNAL, SLOT, Qt, QSize, QPointF
from PySide6.QtGui import (QOpenGLFunctions,
    QVector2D, QMatrix4x4)
from PySide6.QtOpenGL import (QOpenGLVertexArrayObject, QOpenGLBuffer,
    QOpenGLShaderProgram, QOpenGLShader)
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL import GL


class Window(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.gl_widget = GLWidget()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.gl_widget)
        self.setLayout(main_layout)

        self.setWindowTitle(self.tr("Hello GL"))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(Window, self).keyPressEvent(event)


class Scene():
    def __init__(self):
        self.m_vertex = 6
        self.m_triangles = 2
        self.nb_float = self.m_vertex * 2

        vertices : List[QVector2D] = []
        # first triangle
        vertices.append(QVector2D(-1,-1))
        vertices.append(QVector2D(1,1))
        vertices.append(QVector2D(-1,1))
        # second triangle
        vertices.append(QVector2D(1,1))
        vertices.append(QVector2D(-1,-1))
        vertices.append(QVector2D(1,-1))

        # each vertex is composed of 2 float
        np_array = np.empty(self.nb_float, dtype=ctypes.c_float)

        for k, vertex in enumerate(vertices):
            np_array[2*k + 0] = vertex.x()
            np_array[2*k + 1] = vertex.y()

        self.m_data = np_array
        
        print("DATA", self.m_data)

    def const_data(self):
        return self.m_data.tobytes()

    def float_count(self):
        return self.nb_float
          
    def vertex_count(self):
        return self.m_vertex

    def triangles_count(self):
        return  self.m_triangles


class GLWidget(QOpenGLWidget, QOpenGLFunctions):
    vertex_code = """
    attribute vec2 position;
    void main(){ gl_Position = vec4(position, 0.0, 1.0); } """

    fragment_code = """
    uniform vec4 color;
    void main() { gl_FragColor = color; } """


    x_rotation_changed = Signal(int)
    y_rotation_changed = Signal(int)
    z_rotation_changed = Signal(int)

    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)
        QOpenGLFunctions.__init__(self)

        self._x_rot = 0
        self._y_rot = 0
        self._z_rot = 0
        self._last_pos = QPointF()
        self.scene = Scene()
        self.vao = QOpenGLVertexArrayObject()
        self._scene_vbo = QOpenGLBuffer()
        self.program = QOpenGLShaderProgram()
        self._proj_matrix_loc = 0
        self._mv_matrix_loc = 0
        self._normal_matrix_loc = 0
        self._light_pos_loc = 0
        self.proj = QMatrix4x4()
        self.camera = QMatrix4x4()
        self.world = QMatrix4x4()

    def x_rotation(self):
        return self._x_rot

    def y_rotation(self):
        return self._y_rot

    def z_rotation(self):
        return self._z_rot

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def normalize_angle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def set_xrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._x_rot:
            self._x_rot = angle
            self.x_rotation_changed.emit(angle)
            self.update()

    def set_yrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._y_rot:
            self._y_rot = angle
            self.y_rotation_changed.emit(angle)
            self.update()

    def set_zrotation(self, angle):
        angle = self.normalize_angle(angle)
        if angle != self._z_rot:
            self._z_rot = angle
            self.z_rotation_changed.emit(angle)
            self.update()

    def cleanup(self):
        self.makeCurrent()
        self._scene_vbo.destroy()
        del self.program
        self.program = None
        self.doneCurrent()


    def initializeGL(self):
        self.context().aboutToBeDestroyed.connect(self.cleanup)
        self.initializeOpenGLFunctions()
        self.glClearColor(0, 0, 0, 0)

        self.program = QOpenGLShaderProgram()


        self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, self.vertex_code)
        self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, self.fragment_code)
        self.program.link()

        self.program.bind()

        self.vao.create()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)

        self._scene_vbo.create()
        self._scene_vbo.bind()
        float_size = ctypes.sizeof(ctypes.c_float)
        self._scene_vbo.allocate(self.scene.const_data(), self.scene.float_count() * float_size)

        self.setup_vertex_attribs()

        self.program.release()
        vao_binder = None

    def setup_vertex_attribs(self):
        self._scene_vbo.bind()

        # Offset for position
        offset = 0
        stride = 2 # nb float in a "packet" 
        sizeof_vertex = 2 * 4  # 2 * 4 bytes

        vertexLocation = self.program.attributeLocation("position")
        self.program.enableAttributeArray(vertexLocation)
        self.program.setAttributeBuffer(vertexLocation, GL.GL_FLOAT, offset, stride, sizeof_vertex)

        colorLocation = self.program.uniformLocation("color")
        self.program.setUniformValue(colorLocation, 0.0, 0.0, 1.0, 1.0)

        self._scene_vbo.release()

    def paintGL(self):
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.glEnable(GL.GL_DEPTH_TEST)
       
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()
        self.glDrawArrays(GL.GL_TRIANGLES, 0, self.scene.vertex_count())
        self.program.release()
        vao_binder = None

    def resizeGL(self, width, height):
        pass

    def mousePressEvent(self, event):
        self._last_pos = event.position()

    def mouseMoveEvent(self, event):
        pos = event.position()
        dx = pos.x() - self._last_pos.x()
        dy = pos.y() - self._last_pos.y()

        if event.buttons() & Qt.LeftButton:
            self.set_xrotation(self._x_rot + 8 * dy)
            self.set_yrotation(self._y_rot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.set_xrotation(self._x_rot + 8 * dy)
            self.set_zrotation(self._z_rot + 8 * dx)

        self._last_pos = pos


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = Window()
    main_window.resize(main_window.sizeHint())
    main_window.show()

    res = app.exec()
    sys.exit(res)