
import ctypes
import sys
from typing import List

import numpy as np

from PySide6.QtCore import QSize
from PySide6.QtGui import (QOpenGLFunctions, QVector2D)
from PySide6.QtWidgets import (QApplication, QMainWindow)

from PySide6.QtOpenGL import (QOpenGLVertexArrayObject, QOpenGLBuffer, QOpenGLShaderProgram, QOpenGLShader)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL import GL


class Window(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.gl_widget = GLWidget()

        self.setCentralWidget(self.gl_widget)
        self.setWindowTitle(self.tr("Hello GL"))

class Vertex:
    nb_float = 2
    bytes_size = nb_float * 4 #  4 bytes each
    # the size/offset do not strictly belong to the Vertex class, but are properties
    # of the generated numpy array. However it is pratical to have them here.
    size = {'position' : 2 } # size in float of position
    offset = {'position' : 0 } # offsets in np array

    def __init__(self,  position: QVector2D):
        self.position = position

    @classmethod
    def toNumpyArray(cls, vertices: List['Vertex']) -> np.ndarray:
        # fill the numpy array - each vertex is composed of 2 float
        np_array = np.empty(len(vertices) * cls.nb_float, dtype=ctypes.c_float)

        for k, vertex in enumerate(vertices):
            np_array[2*k + 0] = vertex.position.x()
            np_array[2*k + 1] = vertex.position.y()

        return np_array


class Scene():
    def __init__(self):
        self.nb_vertex = 6
        self.nb_float = self.nb_vertex * Vertex.nb_float

        vertices : List[Vertex] = []

        # define vertices - first triangle
        vertices.append( Vertex(QVector2D(-1,-1)) )
        vertices.append( Vertex(QVector2D(1,1)) )
        vertices.append( Vertex(QVector2D(-1,1)) )
        # define vertices - second triangle
        vertices.append( Vertex(QVector2D(1,1)) )
        vertices.append( Vertex(QVector2D(-1,-1)) )
        vertices.append( Vertex(QVector2D(1,-1)) )

        # fill the numpy array
        self.m_data = Vertex.toNumpyArray(vertices)

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

        # the uniform stuff
        colorLocation = self.program.uniformLocation("color")
        self.program.setUniformValue(colorLocation, 0.0, 0.0, 1.0, 1.0)

        # Offset for position
        offset = Vertex.offset['position']
        size = Vertex.size['position'] # nb float in a position "packet" 
        stride = Vertex.bytes_size # nb bytes in a Vertex 

        vertexLocation = self.program.attributeLocation("position")
        self.program.enableAttributeArray(vertexLocation)
        self.program.setAttributeBuffer(vertexLocation, GL.GL_FLOAT, offset, size, stride)

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
    main_window.show()

    res = app.exec()
    sys.exit(res)