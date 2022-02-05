
import ctypes
import numpy as np
import sys
from typing import List

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import (QOpenGLFunctions, QVector2D)
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
    def __init__(self,  position: QVector2D):
        self.position = position

    @staticmethod
    def size_in_bytes():
        return 2 * 4  # 2 float 

class Scene():
    def __init__(self):
        self.nb_vertex = 6
        self.nb_float = self.nb_vertex * 2

        vertices : List[Vertex] = []

        # collect vertices - first triangle
        vertices.append( Vertex(QVector2D(-1,-1)) )
        vertices.append( Vertex(QVector2D(1,1)) )
        vertices.append( Vertex(QVector2D(-1,1)) )
        # collect vertices - second triangle
        vertices.append( Vertex(QVector2D(1,1)) )
        vertices.append( Vertex(QVector2D(-1,-1)) )
        vertices.append( Vertex(QVector2D(1,-1)) )

        # fill the numpy array - each vertex is composed of 2 float
        self.m_data = np.empty(self.nb_float, dtype=ctypes.c_float)

        for k, vertex in enumerate(vertices):
             self.m_data[2*k + 0] = vertex.position.x()
             self.m_data[2*k + 1] = vertex.position.y()

    def const_data(self):
        return self.m_data.tobytes()


class GLWidget(QOpenGLWidget, QOpenGLFunctions):
    vertex_code = """
    attribute vec2 position;
    void main(){ gl_Position = vec4(position, 0.0, 1.0); } """

    fragment_code = """
    uniform vec4 color;
    void main() { gl_FragColor = color; } """

    float_size = ctypes.sizeof(ctypes.c_float) # 4 bytes

    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)
        QOpenGLFunctions.__init__(self)

        self.scene = Scene()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer()
        self.program = QOpenGLShaderProgram()

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def cleanup(self):
        self.makeCurrent()
        self.vbo.destroy()
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

        self.vbo.create()
        self.vbo.bind()
        self.vbo.allocate(self.scene.const_data(), self.scene.nb_float * self.float_size)

        self.setup_vertex_attribs()

        self.program.release()
        vao_binder = None

    def setup_vertex_attribs(self):
        self.vbo.bind()

        # Offset for position
        offset = 0
        stride = 2 # nb float in a position "packet" 

        vertexLocation = self.program.attributeLocation("position")
        self.program.enableAttributeArray(vertexLocation)
        self.program.setAttributeBuffer(vertexLocation, GL.GL_FLOAT, offset, stride, Vertex.size_in_bytes())

        colorLocation = self.program.uniformLocation("color")
        self.program.setUniformValue(colorLocation, 0.0, 0.0, 1.0, 1.0)

        self.vbo.release()

    def paintGL(self):
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.glEnable(GL.GL_DEPTH_TEST)
       
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()
        self.glDrawArrays(GL.GL_TRIANGLES, 0, self.scene.nb_vertex)
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