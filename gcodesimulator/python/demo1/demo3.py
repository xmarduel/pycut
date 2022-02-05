
import ctypes
import numpy as np
import sys
from typing import List

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import (QOpenGLFunctions, QVector2D, QVector4D)
from PySide6.QtOpenGL import (QOpenGLVertexArrayObject, QOpenGLBuffer, QOpenGLShaderProgram, QOpenGLShader)
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

class Vertex:
    def __init__(self, position: QVector2D, color: QVector4D):
        self.position = position
        self.color = color

class Scene():
    def __init__(self):
        self.m_vertex = 6
        self.nb_float = self.m_vertex * ( 2 + 4 )

        vertices : List[Vertex] = []

        # first triangle
        vertex1 = Vertex(QVector2D(-1,-1),  QVector4D(0,0,1,1))
        vertex2 = Vertex(QVector2D(1,1), QVector4D(1,0,0,1))
        vertex3 = Vertex(QVector2D(-1,1), QVector4D(1,1,0,1))
        # second triangle
        vertex4 = Vertex(QVector2D(1,1), QVector4D(1,0,0,1))
        vertex5 = Vertex(QVector2D(-1,-1), QVector4D(0,0,1,1))
        vertex6 = Vertex(QVector2D(1,-1), QVector4D(0,1,0,1) )

        # collect vertices
        vertices.append(vertex1)
        vertices.append(vertex2)
        vertices.append(vertex3)
        vertices.append(vertex4)
        vertices.append(vertex5)
        vertices.append(vertex6)

        # ill the numpy array - each vertex is composed of 6 float
        np_array = np.empty(self.nb_float, dtype=ctypes.c_float)

        for k, vertex in enumerate(vertices):
            np_array[6*k + 0] = vertex.position.x()
            np_array[6*k + 1] = vertex.position.y()
            np_array[6*k + 2] = vertex.color.x()
            np_array[6*k + 3] = vertex.color.y()
            np_array[6*k + 4] = vertex.color.z()
            np_array[6*k + 5] = vertex.color.w()

        self.m_data = np_array

    def const_data(self):
        return self.m_data.tobytes()

    def float_count(self):
        return self.nb_float
          
    def vertex_count(self):
        return self.m_vertex


class GLWidget(QOpenGLWidget, QOpenGLFunctions):
    vertex_code = """
    attribute vec2 position;
    attribute vec4 color;
    varying vec4 v_color;
    void main()
    {
        gl_Position = vec4(position, 0.0, 1.0);
        v_color= color;
    } """

    fragment_code = """
    varying vec4 v_color;
    void main() { gl_FragColor = v_color; } """


    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)
        QOpenGLFunctions.__init__(self)

        self.scene = Scene()
        self.vao = QOpenGLVertexArrayObject()
        self._scene_vbo = QOpenGLBuffer()
        self.program = QOpenGLShaderProgram()

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

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
        stride = 2 # nb float in a position "packet" 
        sizeof_vertex = 6 * 4  # 6 * 4 bytes

        vertexLocation = self.program.attributeLocation("position")
        self.program.enableAttributeArray(vertexLocation)
        self.program.setAttributeBuffer(vertexLocation, GL.GL_FLOAT, offset, stride, sizeof_vertex)

        # Offset for color
        offset = 8 # size of preceding data (position = QVector2D)
        stride = 4 # nb float in a color "packet" 

        colorLocation =  self.program.attributeLocation("color")
        self.program.enableAttributeArray(colorLocation)
        self.program.setAttributeBuffer(colorLocation, GL.GL_FLOAT, offset, stride, sizeof_vertex)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = Window()
    main_window.resize(main_window.sizeHint())
    main_window.show()

    res = app.exec()
    sys.exit(res)