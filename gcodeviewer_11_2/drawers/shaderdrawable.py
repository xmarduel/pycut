import ctypes
from enum import Enum

from functools import singledispatchmethod

from typing import List
from typing import Optional

from PySide6.QtGui import QVector3D
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QPainter

from PySide6.QtGui import QOpenGLFunctions

from PySide6.QtOpenGL import QOpenGLShaderProgram
from PySide6.QtOpenGL import QOpenGLBuffer
from PySide6.QtOpenGL import QOpenGLVertexArrayObject
from PySide6.QtOpenGL import QOpenGLTexture

from OpenGL import GL  # type: ignore [import-untyped]

from gcodeviewer_11_2.util.util import Util

import numpy as np

sNaN = float("NaN")


class VertexData:
    """ """
    class VertexDataType(Enum):
        VertexDataTypeLine = 0
        VertexDataTypeDash = 1
        VertexDataTypeDashDot = 2
        VertexDataTypePoint = 3
        VertexDataTypeTriangle = 4

    def __init__(self):
        self.position = QVector3D()
        self.color = QVector3D()
        self.data = QVector3D()
        self.type = VertexData.VertexDataType.VertexDataTypeLine

    @classmethod
    def fromVectors(cls, position: QVector3D, color: QVector3D, data: QVector3D, type: VertexDataType = VertexDataType.VertexDataTypeLine):
        vd = VertexData()
        vd.position = position
        vd.color = color
        vd.data = data
        vd.type = type
        return vd

    @classmethod
    def clone(cls, other: "VertexData"):
        vd = VertexData()
        vd.position = Util.cloneQVector3D(other.position)
        vd.color = Util.cloneQVector3D(other.color)
        vd.data = Util.cloneQVector3D(other.data)
        vd.type = other.type

        return vd

    @classmethod
    def VertexDataListToNumPy(cls, alist: List["VertexData"]):
        """
        https://nrotella.github.io/journal/first-steps-python-qt-opengl.html
        """

        def NaN_to_Val(val):
            # if qIsNaN(val):
            #    return 65536.0
            return val

        np_array = np.empty(10 * len(alist), dtype=ctypes.c_float)

        for k, vdata in enumerate(alist):
            np_array[10 * k + 0] = NaN_to_Val(vdata.position.x())
            np_array[10 * k + 1] = NaN_to_Val(vdata.position.y())
            np_array[10 * k + 2] = NaN_to_Val(vdata.position.z())

            np_array[10 * k + 3] = NaN_to_Val(vdata.color.x())
            np_array[10 * k + 4] = NaN_to_Val(vdata.color.y())
            np_array[10 * k + 5] = NaN_to_Val(vdata.color.z())

            np_array[10 * k + 6] = NaN_to_Val(vdata.data.x())
            np_array[10 * k + 7] = NaN_to_Val(vdata.data.y())
            np_array[10 * k + 8] = NaN_to_Val(vdata.data.z())

            np_array[10 * k + 9] = float(vdata.type.value)

        return np_array


class ShaderDrawable(QOpenGLFunctions):
    """ """

    sizeof_vertexdata = 40  # the "stride" of the vertex array: 3xQVector3D
    sizeof_vector3D = 12  # size of every attribute in a VertexData item

    def __init__(self):
        """ """
        QOpenGLFunctions.__init__(self)

        self.m_needsUpdateGeometry = True
        self.m_visible = True
        self.m_lineWidth = 1.0
        self.m_pointSize = 1.0
        self.m_texture: Optional[QOpenGLTexture] = None
        self.m_lines: List[VertexData] = []
        self.m_points: List[VertexData] = []
        self.m_triangles: List[VertexData] = []

        self.m_worldScale = 1.0
        self.m_windowScaling = False
        self.m_windowScale = 1.0

        self.m_modelMatrix = QMatrix4x4() 
        self.m_translationMatrix = QMatrix4x4() 
        self.m_rotationMatrix = QMatrix4x4() 
        self.m_scaleMatrix = QMatrix4x4() 

        self.m_vbo = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)
        self.m_vao = QOpenGLVertexArrayObject()

    def init(self):
        # Init openGL functions
        self.initializeOpenGLFunctions()

        # Create buffers
        self.m_vao.create()
        self.m_vbo.create()

    def dispose(self):
        if self.m_vao.isCreated():
            self.m_vao.destroy()
        if self.m_vbo.isCreated():
            self.m_vbo.destroy()

    def update(self):
        self.m_needsUpdateGeometry = True

    def needsUpdateGeometry(self) -> bool:
        return self.m_needsUpdateGeometry

    def updateGeometry(self, shaderProgram: QOpenGLShaderProgram):
        # Init in context
        if not self.m_vbo.isCreated():
            self.init()

        if self.m_vao.isCreated():
            # Prepare vao
            self.m_vao.bind()

        # Prepare vbo
        self.m_vbo.bind()

        # Update vertex buffer
        if self.updateData():
            #print("ShaderDrawable::updateGeometry: self.updateData() is True")

            # Fill vertices buffer
            vertexData = []
            vertexData += self.m_triangles
            vertexData += self.m_lines
            vertexData += self.m_points

            # python handling of vbo - with numpy -
            np_array = VertexData.VertexDataListToNumPy(vertexData)
            np_bytes = np_array.tobytes()

            self.m_vbo.allocate(len(np_bytes))
            self.m_vbo.write(0, np_bytes, len(np_bytes))
        else:
            #print("ShaderDrawable::updateGeometry: self.updateData() is False")

            self.m_vbo.release()
            if self.m_vao.isCreated():
                self.m_vao.release()
            self.m_needsUpdateGeometry = False
            return

        if self.m_vao.isCreated():
            # Offset for position
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation = shaderProgram.attributeLocation("a_position")
            shaderProgram.enableAttributeArray(vertexLocation)
            shaderProgram.setAttributeBuffer(
                vertexLocation, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata
            )

            # Offset for color
            offset += ShaderDrawable.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex color data
            color = shaderProgram.attributeLocation("a_color")
            shaderProgram.enableAttributeArray(color)
            shaderProgram.setAttributeBuffer(
                color, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata
            )

            # Offset for line start point
            offset += ShaderDrawable.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex line start point
            data = shaderProgram.attributeLocation("a_data")
            shaderProgram.enableAttributeArray(data)
            shaderProgram.setAttributeBuffer(
                data, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata
            )

            offset += ShaderDrawable.sizeof_vector3D # sizeof(QVector3D);

            type = shaderProgram.attributeLocation("a_type")
            shaderProgram.enableAttributeArray(type)
            shaderProgram.setAttributeBuffer(type, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

            self.m_vao.release()

        self.m_vbo.release()

        self.m_needsUpdateGeometry = False

    def updateData(self) -> bool:
        """
        Test data
        """
        return False

    def draw(self, shaderProgram: QOpenGLShaderProgram):
        if not self.m_visible:
            return

        if self.m_vao.isCreated():
            # Prepare vao
            self.m_vao.bind()
        else:
            # Prepare vbo
            self.m_vbo.bind()

            # Offset for position
            offset = 0

            # Tell OpenGL programmable pipeline how to locate vertex position data
            vertexLocation = shaderProgram.attributeLocation("a_position")
            shaderProgram.enableAttributeArray(vertexLocation)
            shaderProgram.setAttributeBuffer(
                vertexLocation, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata
            )

            # Offset for color
            offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex color data
            color = shaderProgram.attributeLocation("a_color")
            shaderProgram.enableAttributeArray(color)
            shaderProgram.setAttributeBuffer(
                color, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata
            )

            # Offset for line start point
            offset += self.sizeof_vector3D

            # Tell OpenGL programmable pipeline how to locate vertex line start point
            data = shaderProgram.attributeLocation("a_data")
            shaderProgram.enableAttributeArray(data)
            shaderProgram.setAttributeBuffer(
                data, GL.GL_FLOAT, offset, 3, self.sizeof_vertexdata
            )

            offset += self.sizeof_vector3D

            type = shaderProgram.attributeLocation("a_type")
            shaderProgram.enableAttributeArray(type)
            shaderProgram.setAttributeBuffer(type, GL.GL_FLOAT, offset, 1, self.sizeof_vertexdata)

        if len(self.m_triangles) != 0:
            if self.m_texture:
                self.m_texture.bind()
                # shaderProgram.setUniformValue("texture", 0)  # OLD
                textureLocationID = shaderProgram.uniformLocation("texture")
                shaderProgram.setUniformValue(textureLocationID, 0)

            self.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.m_triangles))

        if len(self.m_lines) != 0:
            self.glLineWidth(self.m_lineWidth)
            self.glDrawArrays(GL.GL_LINES, len(self.m_triangles), len(self.m_lines))

        if len(self.m_points) != 0:
            self.glDrawArrays(
                GL.GL_POINTS,
                len(self.m_triangles) + len(self.m_lines),
                len(self.m_points),
            )

        if self.m_vao.isCreated():
            self.m_vao.release()
        else:
            self.m_vbo.release()

    def drawPainter(self, painter: QPainter, projection: QMatrix4x4, ratio: float):
        pass

    def getViewRanges(self) -> QVector3D:
        return Util.nAssign(self.getViewUpperBounds()) - Util.nAssign(self.getViewLowerBounds())

    def getViewLowerBounds(self) -> QVector3D:
        return QVector3D()

    def getViewUpperBounds(self) -> QVector3D:
        return QVector3D()

    def getModelRanges(self) -> QVector3D:
        return Util.nAssign(self.getModelUpperBounds()) - Util.nAssign(self.getModelLowerBounds())

    def getModelLowerBounds(self) -> QVector3D:
        return QVector3D()

    def getModelUpperBounds(self) -> QVector3D:
        return QVector3D()

    def getVertexCount(self) -> int:
        return len(self.m_lines) + len(self.m_points) + len(self.m_triangles)

    def lineWidth(self) -> float:
        return self.m_lineWidth

    def setLineWidth(self, lineWidth: float):
        self.m_lineWidth = lineWidth

    def visible(self) -> bool:
        return self.m_visible

    def setVisible(self, visible: bool):
        self.m_visible = visible

    def pointSize(self) -> float:
        return self.m_pointSize

    def setPointSize(self, pointSize: float):
        self.m_pointSize = pointSize


    def modelMatrix(self) -> QMatrix4x4:
        return self.m_modelMatrix

    def setModelMatrix(self, modelMatrix: QMatrix4x4):
        self.m_modelMatrix = modelMatrix

    def  rotation(self) -> QMatrix4x4:
        return self.m_rotationMatrix

    @singledispatchmethod
    def setRotation(self, first, second = None):
        raise NotImplementedError("Cannot run 'setRotation' method with %r" % first)

    @setRotation.register
    def _(self, rotation: QMatrix4x4):
        self.m_rotationMatrix = rotation
        self.m_modelMatrix = self.m_translationMatrix.map(self.m_rotationMatrix).map(self.m_scaleMatrix)

    @setRotation.register
    def _(self, angle: float, axis: QVector3D):
        self.m_rotationMatrix.setToIdentity()
        self.m_rotationMatrix.rotate(angle, axis)
        self.m_modelMatrix = self.m_translationMatrix.map(self.m_rotationMatrix).map(self.m_scaleMatrix)

    def translation(self) -> QMatrix4x4:
        return self.m_translationMatrix

    @singledispatchmethod
    def setTranslation(self, translation):
        raise NotImplementedError("Cannot run 'setTranslation' method with %r" % translation)

    @setTranslation.register
    def _(self, translation: QMatrix4x4):
        self.m_translationMatrix = translation;
        self.m_modelMatrix = self.m_translationMatrix * self.m_rotationMatrix * self.m_scaleMatrix

    @setTranslation.register
    def _(self, translation: QVector3D):
        self.m_translationMatrix.setToIdentity()
        self.m_translationMatrix.translate(translation)
        self.m_modelMatrix = self.m_translationMatrix * self.m_rotationMatrix * self.m_scaleMatrix

    def scale(self) -> QMatrix4x4:
        return self.m_translationMatrix

    def setScale(self, scale: QMatrix4x4):
        self.m_scaleMatrix = scale
        self.m_modelMatrix = self.m_translationMatrix * self.m_rotationMatrix * self.m_scaleMatrix

    def worldScale(self) -> float:
        return self.m_worldScale

    def setWorldScale(self, scale: float):
        self.m_worldScale = scale
        self.m_scaleMatrix.setToIdentity()
        self.m_scaleMatrix.scale(scale)
        self.m_modelMatrix = self.m_translationMatrix * self.m_rotationMatrix * self.m_scaleMatrix

    def windowScaling(self) -> bool:
        return self.m_windowScaling

    def setWindowScaling(self, windowScaling: bool):
        self.m_windowScaling = windowScaling

    def windowScale(self) -> float:
        return self.m_windowScale

    def setWindowScale(self, windowScale: float):
        self.m_windowScale = windowScale