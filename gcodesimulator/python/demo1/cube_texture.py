
import ctypes
import math
import numpy as np
import sys

from PySide6.QtCore import QSize
from PySide6.QtGui import (QOpenGLFunctions, QVector2D, QVector3D, QVector4D, QMatrix4x4, QImage)
from PySide6.QtWidgets import (QApplication, QMainWindow)

from PySide6.QtOpenGL import (QOpenGLVertexArrayObject, QOpenGLBuffer, QOpenGLShaderProgram, QOpenGLShader, QOpenGLTexture)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL import GL


class Window(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.gl_widget = GLWidget()

        self.setCentralWidget(self.gl_widget)
        self.setWindowTitle(self.tr("Hello GL"))

class Vertex:
    nb_float = 9
    bytes_size = nb_float * 4 #  4 bytes each
    size = {'position' : 3 , 'color': 4, 'texcoord': 2} # size in float of position/texcoord
    offset = {'position' : 0, 'color': 12, 'texcoord': 28 } # offsets in np array in bytes

    def __init__(self, position: QVector3D, color: QVector4D, texcoord: QVector2D):
        self.position = position
        self.color = color
        self.texcoord = texcoord

class Scene():
    '''
    A cube with 24 vertices "not shared"
    '''
    def __init__(self):
        self.nb_float = 0
        self.nb_int = 0

        vtype = [('position', np.float32, 3),
                 ('color', np.float32, 4),
                 ('texcoord', np.float32, 2)]
        itype = np.uint32
        
        # 8 points constituting a cube
        p = np.array([[1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1],
                  [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1]],
                  dtype=float)

        c = np.array([[0,1,1,1], [0,0,1,1], [0,0,0,1], [0,1,0,1],
                  [1,1,0,1], [1,1,1,1], [1,0,1,1], [1,0,0,1]],
                  dtype=float)

        # Texture coords
        t = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])

        faces_p = [0, 1, 2, 3,  0, 3, 4, 5,   0, 5, 6, 1,   1, 6, 7, 2,  7, 4, 3, 2,   4, 7, 6, 5]
        faces_t = [0, 1, 2, 3,  0, 1, 2, 3,   0, 1, 2, 3,   3, 2, 1, 0,  0, 1, 2, 3,   0, 1, 2, 3]

        # list of vertices : 6 faces with for each 4 vertices : use faces_p indexes 
        self.vertices = np.zeros(24, vtype)
        self.vertices['position'] = p[faces_p]
        self.vertices['color'] = c[faces_p]
        self.vertices['texcoord'] = t[faces_t]

        print(self.vertices)

        # index buffer
        self.filled = np.resize(np.array([0, 1, 2, 0, 2, 3], dtype=itype), 6 * (2 * 3))
        self.filled += np.repeat(4 * np.arange(6, dtype=itype), 6)

        self.nb_float = 24 * Vertex.nb_float
        self.nb_int = 36

        self.textureData = QImage("./crate.png")

    def const_vertex_data(self):
        return self.vertices.tobytes()

    def const_index_data(self):
        return self.filled.tobytes()

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

    vertex_code_tex = """
    uniform mat4   model;
    uniform mat4   view;
    uniform mat4   projection;
    attribute vec3 position;
    attribute vec2 texcoord;   // Vertex texture coordinates
    varying vec2   v_texcoord;   // Interpolated fragment texture coordinates (out)

    void main()
    {
        // Assign varying variables
        v_texcoord  = texcoord;

        // Final position
        gl_Position = projection * view * model * vec4(position,1.0);
    } """


    fragment_code_tex = """
    uniform sampler2D texture; // Texture
    varying vec2 v_texcoord;   // Interpolated fragment texture coordinates (in)
    void main()
    {
        // Get texture color
        gl_FragColor = texture2D(texture, v_texcoord);
    } """

    float_size = ctypes.sizeof(ctypes.c_float) # 4 bytes
    int_size = ctypes.sizeof(ctypes.c_uint32) # 4 bytes

    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)
        QOpenGLFunctions.__init__(self)

        self.scene = Scene()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer()
        self.ibo = QOpenGLBuffer()
        self.texture = QOpenGLTexture(QOpenGLTexture.Target2D)
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
        #self.ibo.destroy()
        del self.program
        self.program = None
        self.doneCurrent()

    def initializeGL(self):
        self.context().aboutToBeDestroyed.connect(self.cleanup)
        self.initializeOpenGLFunctions()
        self.glClearColor(0, 0, 0, 0)

        self.program = QOpenGLShaderProgram()

        #self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, self.vertex_code)
        #self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, self.fragment_code)
        self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, self.vertex_code_tex)
        self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, self.fragment_code_tex)
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

        # ------------------------- the texture ---------------------------------------------
        self.texture.create()
        # Wrap style
        self.texture.setWrapMode(QOpenGLTexture.ClampToBorder)
        #self.texture.setBorderColor(Qt.red)

        # Texture Filtering
        self.texture.setMinificationFilter(QOpenGLTexture.NearestMipMapLinear)
        self.texture.setMagnificationFilter(QOpenGLTexture.Linear)

        # Kopiere Daten in Texture und Erstelle Mipmap
        self.texture.setData(self.scene.textureData)
        # bind texture to index "0"
        self.texture.bind(0)
        # -------------------------------------------------------------------------------------

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


        offset = Vertex.offset['texcoord'] # size in bytes of preceding data (position = QVector3D / color = QVector4D)
        size = Vertex.size['texcoord'] # nb float in a color "texcoord" 
        stride = Vertex.bytes_size # nb bytes in a vertex "texcoord" 

        texLocation =  self.program.attributeLocation("texcoord")
        self.program.enableAttributeArray(texLocation)
        self.program.setAttributeBuffer(texLocation, GL.GL_FLOAT, offset, size, stride)

        # --------------------------------- the texture ------------------------------------------
        # uniform for fragment texture
        textureLocationID = self.program.attributeLocation("texture")
        self.program.setUniformValue(textureLocationID, 0) # the index
        # --------------------------------- the texture ------------------------------------------

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