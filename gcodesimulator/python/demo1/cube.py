
import ctypes
import math
import numpy as np
import sys
from typing import List

from PySide6.QtCore import QSize
from PySide6.QtGui import (QOpenGLFunctions, QVector3D, QVector4D, QMatrix4x4)
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
    nb_float = 7
    bytes_size = nb_float * 4 #  4 bytes each
    # the size/offset do not strictly belong to the Vertex class, but are properties
    # of the generated numpy array. However it is pratical to have them here.
    size = {'position' : 3 , 'color': 4} # size in float of position/color
    offset = {'position' : 0, 'color': 12 } # offsets in np array in bytes

    def __init__(self, position: QVector3D, color: QVector4D):
        self.position = position
        self.color = color

    @classmethod
    def toNumpyArray(cls, vertices: List['Vertex']) -> np.ndarray:
        np_array = np.empty(len(vertices) * cls.nb_float, dtype=ctypes.c_float)

        for k, vertex in enumerate(vertices):
            np_array[7*k + 0] = vertex.position.x()
            np_array[7*k + 1] = vertex.position.y()
            np_array[7*k + 2] = vertex.position.z()
            np_array[7*k + 3] = vertex.color.x()
            np_array[7*k + 4] = vertex.color.y()
            np_array[7*k + 5] = vertex.color.z()
            np_array[7*k + 6] = vertex.color.w()

        return np_array


class Scene():
    '''
    A cube 
    '''
    def __init__(self):
        self.nb_vertex = 8
        self.nb_float = self.nb_vertex * Vertex.nb_float

        self.nb_triangles = 12
        self.nb_int = self.nb_triangles * 3

        # 8 vertices -> VertexBuffer
        vertices : List[Vertex] = []

        vertices.append( Vertex(QVector3D( 1, 1, 1), QVector4D(0,1,1,1)) )
        vertices.append( Vertex(QVector3D(-1, 1, 1), QVector4D(0,0,1,1)) )
        vertices.append( Vertex(QVector3D(-1,-1, 1), QVector4D(0,0,0,1)) )
        vertices.append( Vertex(QVector3D( 1,-1, 1), QVector4D(0,1,0,1)) )
        vertices.append( Vertex(QVector3D( 1,-1,-1), QVector4D(1,1,0,1)) )
        vertices.append( Vertex(QVector3D( 1, 1,-1), QVector4D(1,1,1,1)) )
        vertices.append( Vertex(QVector3D(-1, 1,-1), QVector4D(1,0,1,1)) )
        vertices.append( Vertex(QVector3D(-1,-1,-1), QVector4D(1,0,0,1)) )

        # fill the numpy array
        self.m_data = Vertex.toNumpyArray(vertices)

        # shared by 12 triangles -> IndexBuffer
        self.i_data = np.array([
                0,1,2, 
                0,2,3,  
                0,3,4, 
                0,4,5,  
                0,5,6, 
                0,6,1,
                1,6,7, 
                1,7,2,  
                7,4,3, 
                7,3,2,  
                4,7,6, 
                4,6,5], dtype=np.uint32)


    def const_vertex_data(self):
        return self.m_data.tobytes()

    def const_index_data(self):
        return self.i_data.tobytes()


class GLWidget(QOpenGLWidget, QOpenGLFunctions):
    vertex_code = """
    uniform mat4   model;
    uniform mat4   view;
    uniform mat4   projection;
    attribute vec3 position;
    attribute vec4 color;
    varying vec4   v_color;

    void main()
    {
        gl_Position = projection * view * model * vec4(position, 1.0);

        v_color = color;
    }  """

    fragment_code = """
    varying vec4 v_color;
    void main() { gl_FragColor = v_color; } """

    float_size = ctypes.sizeof(ctypes.c_float) # 4 bytes
    int_size = ctypes.sizeof(ctypes.c_uint32) # 4 bytes

    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)
        QOpenGLFunctions.__init__(self)

        self.scene = Scene()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer()
        self.ibo = QOpenGLBuffer()
        self.program = QOpenGLShaderProgram()

        self.proj = QMatrix4x4()
        self.proj.setToIdentity()
        self.view = QMatrix4x4()
        self.view.setToIdentity()
        self.view.translate(QVector3D(0,0,-5))
        self.model = QMatrix4x4()
        self.model.setToIdentity()

        self.theta = 0.0 # degrees
        self.phi = 0.0 # degrees

        self.timer = 0

        id = self.startTimer(1) 

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

        self.vbo.create() # QOpenGLBuffer.VertexBuffer
        self.vbo.bind()
        self.vbo.allocate(self.scene.const_vertex_data(), self.scene.nb_float * self.float_size)

        self.ibo.create() # QOpenGLBuffer.IndexBuffer
        self.ibo.bind()
        self.ibo.allocate(self.scene.const_index_data(), self.scene.nb_int * self.int_size)

        self.setup_vertex_attribs()

        self.program.release()
        vao_binder = None

    def setup_vertex_attribs(self):
        self.vbo.bind()

        modelLocation = self.program.uniformLocation("model")
        self.program.setUniformValue(modelLocation, self.model)

        projLocation = self.program.uniformLocation("projection")
        self.program.setUniformValue(projLocation, self.proj)

        viewLocation = self.program.uniformLocation("view")
        self.program.setUniformValue(viewLocation, self.view)

        # Offset for position
        offset = Vertex.offset['position']
        size = Vertex.size['position'] # nb float in a position "packet" 
        stride = Vertex.bytes_size # nb bytes in a vertex "packet" 

        vertexLocation = self.program.attributeLocation("position")
        self.program.enableAttributeArray(vertexLocation)
        self.program.setAttributeBuffer(vertexLocation, GL.GL_FLOAT, offset, size, stride)

        # Offset for color
        offset = Vertex.offset['color'] # size in bytes of preceding data (position = QVector3D)
        size = Vertex.size['color'] # nb float in a color "packet" 
        stride = Vertex.bytes_size # nb bytes in a vertex "packet" 

        colorLocation =  self.program.attributeLocation("color")
        self.program.enableAttributeArray(colorLocation)
        self.program.setAttributeBuffer(colorLocation, GL.GL_FLOAT, offset, size, stride)

        self.vbo.release()

    def paintGL(self):
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.glEnable(GL.GL_DEPTH_TEST)
       
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()
        
        modelLocation = self.program.uniformLocation("model")
        self.program.setUniformValue(modelLocation, self.model)

        projLocation = self.program.uniformLocation("projection")
        self.program.setUniformValue(projLocation, self.proj)

        viewLocation = self.program.uniformLocation("view")
        self.program.setUniformValue(viewLocation, self.view)

        # Filled cube
        self.glDrawElements(GL.GL_TRIANGLES, 12*3, GL.GL_UNSIGNED_INT, self.scene.const_index_data())

        self.program.release()
        vao_binder = None

    def resizeGL(self, width, height):
        ratio = width / float(height)
        self.proj.perspective(45.0, ratio, 2.0, 100.0)

    def timerEvent(self, event):
        self.timer += 0.25 * math.pi/180.0
        
        # Make cube rotate
        self.theta += 1.0 # degrees
        self.phi += 1.0 # degrees
        
        self.model = QMatrix4x4()
        self.model.setToIdentity()
        self.model.rotate(self.theta, 0, 0, 1)
        self.model.rotate(self.phi, 0, 1, 0)
        
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = Window()
    main_window.show()

    res = app.exec()
    sys.exit(res)