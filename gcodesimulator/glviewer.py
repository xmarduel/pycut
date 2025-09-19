import math
import time
from collections import namedtuple
from enum import IntEnum

import numpy as np
import numpy.typing as npt

from typing import List
from typing import Dict
from typing import Any
from typing import cast

# works great !
from numba import jit  # type: ignore [import-untyped]

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import (
    QOpenGLFunctions,
    QVector2D,
    QVector3D,
    QMatrix4x4,
)

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from PySide6.QtOpenGL import (
    QOpenGLVertexArrayObject,
    QOpenGLBuffer,
    QOpenGLFramebufferObject,
    QOpenGLShaderProgram,
    QOpenGLShader,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL import GL  # type: ignore [import-untyped]

from PySide6.QtUiTools import QUiLoader

from gcodesimulator.gcodeminiparser import GcodeAtomicMvt
from gcodesimulator.gcodeminiparser import GcodeMiniParser

from gcodesimulator.gcodefileviewer import GCodeFileViewer

from gcodesimulator.ui_simcontrols import Ui_SimControlWidget

sNaN = float("NaN")

ZOOMSTEP = 1.1

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


@jit(nopython=True)
def make_scene_numba(resolution) -> npt.NDArray[np.float32]:
    print("START NUMBA!")

    meshNumVertexes = resolution * (resolution - 1)
    meshStride = 9

    arraySize = meshNumVertexes * 3 * meshStride
    array = np.zeros(arraySize, dtype=np.float32)

    pos = 0
    for y in range(resolution - 1):
        for x in range(resolution):
            left = x - 1
            if left < 0:
                left = 0
            right = x + 1
            if right >= resolution:
                right = resolution - 1
            if not (x & 1) ^ (y & 1):
                for i in range(3):
                    array[pos] = left
                    pos += 1
                    array[pos] = y + 1
                    pos += 1
                    array[pos] = x
                    pos += 1
                    array[pos] = y
                    pos += 1
                    array[pos] = right
                    pos += 1
                    array[pos] = y + 1
                    pos += 1
                    if i == 0:
                        array[pos] = left
                        pos += 1
                        array[pos] = y + 1
                        pos += 1
                    elif i == 1:
                        array[pos] = x
                        pos += 1
                        array[pos] = y
                        pos += 1
                    else:
                        array[pos] = right
                        pos += 1
                        array[pos] = y + 1
                        pos += 1

                    array[pos] = i
                    pos += 1
            else:
                for i in range(3):
                    array[pos] = left
                    pos += 1
                    array[pos] = y
                    pos += 1
                    array[pos] = right
                    pos += 1
                    array[pos] = y
                    pos += 1
                    array[pos] = x
                    pos += 1
                    array[pos] = y + 1
                    pos += 1
                    if i == 0:
                        array[pos] = left
                        pos += 1
                        array[pos] = y
                        pos += 1
                    elif i == 1:
                        array[pos] = right
                        pos += 1
                        array[pos] = y
                        pos += 1
                    else:
                        array[pos] = x
                        pos += 1
                        array[pos] = y + 1
                        pos += 1

                    array[pos] = i
                    pos += 1

    print("DONE!")
    return array


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


class Scene:
    class VertexData:
        # NB_FLOATS_PER_VERTEX = 12
        NB_FLOATS_PER_VERTEX = 9

        def __init__(self):
            self.pos1 = QVector3D()
            self.pos2 = QVector3D()

            self.startTime = sNaN
            self.endTime = sNaN
            self.command = sNaN

            # VBit
            # self.rawPos = QVector3D()

    def __init__(
        self,
        gcode: str,
        cutterDiameter: float,
        cutterHeight: float,
        cutterAngle: float,
        useCandleParser: bool,
    ):
        """ """
        self.gcode = gcode
        self.parser = GcodeMiniParser()

        if useCandleParser == False:
            self.parser.parse_gcode(self.gcode)
        else:
            self.parser.parse_gcode_use_candle_parser(self.gcode)

        self.topZ = 0.0
        self.cutterDiameter = cutterDiameter
        self.cutterAngle = cutterAngle
        self.cutterHeight = cutterHeight

        self.isVBit = self.cutterAngle < 180

        self.pathNumPoints = 0
        self.pathStride = 9
        self.pathVertexesPerLine = 18
        self.pathNumVertexes = 0

        self.totalTime = 0.0

        self.pathXOffset = 0.0
        self.pathYOffset = 0.0
        self.pathScale = 0.0
        self.pathMinZ = 0.0

        # make a scene
        self.vertices: List[Scene.VertexData] = self.make_scene()

        self.array: npt.NDArray[np.float32] = None  # all vertices as np float array
        # fill the numpy array from the scene ("path") and gets its buffer
        self.pathBufferContent = self.make_buffer()

    def make_scene(self):
        vertices: List[Scene.VertexData] = []

        # fill the numpy array - each vertex is composed of 9 float
        startTime = time.time()

        pathTopZ = self.topZ
        cutterDia = self.cutterDiameter
        if self.cutterAngle <= 0 or self.cutterAngle > 180:
            self.cutterAngle = 180
        cutterAngleRad = self.cutterAngle * math.pi / 180
        self.isVBit = isVBit = self.cutterAngle < 180
        cutterH = self.cutterHeight

        inputStride = 4

        self.pathNumPoints = len(self.parser.path)

        numHalfCircleSegments = 5

        if isVBit:
            self.pathStride = 12
            self.pathVertexesPerLine = 12 + numHalfCircleSegments * 6
        else:
            self.pathStride = 9
            self.pathVertexesPerLine = 18

        self.pathNumVertexes = self.pathNumPoints * self.pathVertexesPerLine
        # self.pathBufferContent = bufferContent = np.empty(self.pathNumVertexes, dtype=np.float32)

        path = self.parser.path

        minX = path[0].pos.x()
        maxX = path[0].pos.x()
        minY = path[0].pos.y()
        maxY = path[0].pos.y()
        minZ = path[0].pos.z()

        total_time = 0
        for idx, point in enumerate(path):
            prevIdx = max(idx - 1, 0)
            prevPoint = path[prevIdx]

            x = point.pos.x()
            y = point.pos.y()
            z = point.pos.z()
            feedrate = point.feedrate

            prevX = prevPoint.pos.x()
            prevY = prevPoint.pos.y()
            prevZ = prevPoint.pos.z()

            dist = math.sqrt(
                (x - prevX) * (x - prevX)
                + (y - prevY) * (y - prevY)
                + (z - prevZ) * (z - prevZ)
            )
            beginTime = total_time
            total_time = total_time + dist / feedrate * 60

            minX = min(minX, x)
            maxX = max(maxX, x)
            minY = min(minY, y)
            maxY = max(maxY, y)
            minZ = min(minZ, z)

            if isVBit:
                coneHeight = -min(z, prevZ, 0) + 0.1
                coneDia = (
                    coneHeight
                    * 2
                    * math.sin(cutterAngleRad / 2)
                    / math.cos(cutterAngleRad / 2)
                )

                if x == prevX and y == prevY:
                    rotAngle = 0
                else:
                    rotAngle = math.atan2(y - prevY, x - prevX)

                xyDist = math.sqrt(
                    (x - prevX) * (x - prevX) + (y - prevY) * (y - prevY)
                )

                # --------------------------------------------------------------------------------------------------
                def f(command, rawX, rawY, rawZ, rotCos, rotSin, zOffset=None):
                    if zOffset is None:
                        zOffset = 0

                    vertex = Scene.VertexData()
                    vertex.pos1 = QVector3D(prevX, prevY, prevZ + zOffset)
                    vertex.pos2 = QVector3D(x, y, z + zOffset)
                    vertex.startTime = beginTime
                    vertex.endTime = total_time
                    vertex.command = command

                    if isVBit:
                        vertex.rawPos = QVector3D(
                            rawX * rotCos - rawY * rotSin,
                            rawY * rotCos + rawX * rotSin,
                            rawZ,
                        )

                    vertices.append(vertex)

                # --------------------------------------------------------------------------------------------------

                if math.abs(z - prevZ) >= xyDist * math.pi / 2 * math.cos(
                    cutterAngleRad / 2
                ) / math.sin(cutterAngleRad / 2):
                    # console.log("plunge or retract")
                    # plunge or retract
                    index = 0

                    command = 100 if prevZ < z else 101
                    for circleIndex in range(1, numHalfCircleSegments * 2):
                        a1 = 2 * math.pi * circleIndex / numHalfCircleSegments / 2
                        a2 = 2 * math.pi * (circleIndex + 1) / numHalfCircleSegments / 2
                        f(
                            command,
                            coneDia / 2 * math.cos(a2),
                            coneDia / 2 * math.sin(a2),
                            coneHeight,
                            1,
                            0,
                        )
                        index += 1
                        f(command, 0, 0, 0, 1, 0)
                        index += 1
                        f(
                            command,
                            coneDia / 2 * math.cos(a1),
                            coneDia / 2 * math.sin(a1),
                            coneHeight,
                            1,
                            0,
                        )
                        index += 1

                    while index < self.pathVertexesPerLine:
                        f(200, 0, 0, 0, 1, 0)
                        index += 1

                else:
                    # cut
                    planeContactAngle = math.asin(
                        (prevZ - z)
                        / xyDist
                        * math.sin(cutterAngleRad / 2)
                        / math.cos(cutterAngleRad / 2)
                    )

                    index = 0
                    if True:
                        f(
                            100,
                            0,
                            -coneDia / 2,
                            coneHeight,
                            math.cos(rotAngle - planeContactAngle),
                            math.sin(rotAngle - planeContactAngle),
                        )
                        f(
                            101,
                            0,
                            -coneDia / 2,
                            coneHeight,
                            math.cos(rotAngle - planeContactAngle),
                            math.sin(rotAngle - planeContactAngle),
                        )
                        f(100, 0, 0, 0, 1, 0)
                        f(100, 0, 0, 0, 1, 0)
                        f(
                            101,
                            0,
                            -coneDia / 2,
                            coneHeight,
                            math.cos(rotAngle - planeContactAngle),
                            math.sin(rotAngle - planeContactAngle),
                        )
                        f(101, 0, 0, 0, 1, 0)
                        f(100, 0, 0, 0, 1, 0)
                        f(101, 0, 0, 0, 1, 0)
                        f(
                            100,
                            0,
                            coneDia / 2,
                            coneHeight,
                            math.cos(rotAngle + planeContactAngle),
                            math.sin(rotAngle + planeContactAngle),
                        )
                        f(
                            100,
                            0,
                            coneDia / 2,
                            coneHeight,
                            math.cos(rotAngle + planeContactAngle),
                            math.sin(rotAngle + planeContactAngle),
                        )
                        f(101, 0, 0, 0, 1, 0)
                        f(
                            101,
                            0,
                            coneDia / 2,
                            coneHeight,
                            math.cos(rotAngle + planeContactAngle),
                            math.sin(rotAngle + planeContactAngle),
                        )

                        index += 12

                    startAngle = rotAngle + math.pi / 2 - planeContactAngle
                    endAngle = rotAngle + 3 * math.pi / 2 + planeContactAngle
                    for circleIndex in range(1, numHalfCircleSegments):
                        a1 = startAngle + circleIndex / numHalfCircleSegments * (
                            endAngle - startAngle
                        )
                        a2 = startAngle + (circleIndex + 1) / numHalfCircleSegments * (
                            endAngle - startAngle
                        )
                        # console.log("a1,a2: " + (a1 * 180 / math.pi) + ", " + (a2 * 180 / math.pi))

                        f(
                            100,
                            coneDia / 2 * math.cos(a2),
                            coneDia / 2 * math.sin(a2),
                            coneHeight,
                            1,
                            0,
                        )
                        f(100, 0, 0, 0, 1, 0)
                        f(
                            100,
                            coneDia / 2 * math.cos(a1),
                            coneDia / 2 * math.sin(a1),
                            coneHeight,
                            1,
                            0,
                        )
                        f(
                            101,
                            coneDia / 2 * math.cos(a2 + math.pi),
                            coneDia / 2 * math.sin(a2 + math.pi),
                            coneHeight,
                            1,
                            0,
                        )
                        f(101, 0, 0, 0, 1, 0)
                        f(
                            101,
                            coneDia / 2 * math.cos(a1 + math.pi),
                            coneDia / 2 * math.sin(a1 + math.pi),
                            coneHeight,
                            1,
                            0,
                        )

                        index += 16

            else:
                for virtex in range(self.pathVertexesPerLine):
                    vertex = Scene.VertexData()
                    vertex.pos1 = QVector3D(prevX, prevY, prevZ)
                    vertex.pos2 = QVector3D(x, y, z)
                    vertex.startTime = beginTime
                    vertex.endTime = total_time
                    vertex.command = virtex

                    vertices.append(vertex)

        self.totalTime = total_time

        self.pathXOffset = -(minX + maxX) / 2
        self.pathYOffset = -(minY + maxY) / 2
        size = max(maxX - minX + 4 * cutterDia, maxY - minY + 4 * cutterDia)
        self.pathScale = 2 / size
        self.pathMinZ = minZ

        return vertices

    def make_buffer(self):
        self.array = np.empty(
            len(self.vertices) * Scene.VertexData.NB_FLOATS_PER_VERTEX, dtype=np.float32
        )

        for k, vertex in enumerate(self.vertices):
            self.array[9 * k + 0] = vertex.pos1.x()
            self.array[9 * k + 1] = vertex.pos1.y()
            self.array[9 * k + 2] = vertex.pos1.z()
            self.array[9 * k + 3] = vertex.pos2.x()
            self.array[9 * k + 4] = vertex.pos2.y()
            self.array[9 * k + 5] = vertex.pos2.z()
            self.array[9 * k + 6] = vertex.startTime
            self.array[9 * k + 7] = vertex.endTime
            self.array[9 * k + 8] = float(vertex.command)

        return self.array.tobytes()

    def buffer_size(self) -> int:
        """in bytes"""
        return (
            len(self.vertices)
            * Scene.VertexData.NB_FLOATS_PER_VERTEX
            * np.float32().itemsize
        )


class SceneHeightMap:
    class VertexData:
        NB_FLOATS_PER_VERTEX = 9

        def __init__(
            self,
            x0: float,
            y0: float,
            x1: float,
            y1: float,
            x2: float,
            y2: float,
            x3: float,
            y3: float,
            idx: int,
        ):
            self.vPos0 = QVector2D(x0, y0)
            self.vPos1 = QVector2D(x1, y1)
            self.vPos2 = QVector2D(x2, y2)
            self.vThisLoc = QVector2D(x3, y3)
            self.vertex = idx

    def __init__(self, resolution: int):
        self.resolution = resolution

        self.numTriangles = self.resolution * (self.resolution - 1)
        self.meshNumVertexes = self.numTriangles * 3

        # make a scene (eval vertices) -> much too slow
        """
        self.vertices: List[SceneHeightMap.VertexData] = self.make_scene()

        self.buffer = self.make_buffer()
        """

        # -> numba helps! fill the numpy array from the scene and gets its buffer
        self.np_array = make_scene_numba(self.resolution)
        self.buffer = self.np_array.tobytes()

    """
    def make_scene(self) -> List[VertexData]:
        vertices : List[SceneHeightMap.VertexData] = []

        def addVertex(x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, idx: int):
            vertex = SceneHeightMap.VertexData(x0, y0, x1, y1, x2, y2, x3, y3, idx)
            vertices.append(vertex)
        
        print("make_scene...")
        for y in range(self.resolution - 1):
            for x in range(self.resolution):
                left = x - 1
                if left < 0:
                    left = 0
                right = x + 1
                if right >= self.resolution:
                    right = self.resolution - 1
                if not ((x & 1) ^ (y & 1)):
                    pass
                    addVertex(left, y+1, x, y, right, y+1, left, y+1, 0) 
                    addVertex(left, y+1, x, y, right, y+1, x, y, 1)
                    addVertex(left, y+1, x, y, right, y+1, right, y+1, 2)
                else:
                    pass
                    addVertex(left, y, right, y, x, y+1, left, y, 0)
                    addVertex(left, y, right, y, x, y+1, right, y, 1)
                    addVertex(left, y, right, y, x, y+1, x, y+1, 2)

        print("DONE!")
        return vertices

    def make_buffer(self):
        print("make_buffer....")
        # fill the numpy array - each vertex is composed of 6 float
        array = np.empty(len(self.vertices) * SceneHeightMap.VertexData.NB_FLOATS_PER_VERTEX, dtype=np.float32)

        for k, vertex in enumerate(self.vertices):
            array[9 * k + 0] = vertex.vPos0.x()
            array[9 * k + 1] = vertex.vPos0.y()
            array[9 * k + 2] = vertex.vPos1.x()
            array[9 * k + 3] = vertex.vPos1.y()
            array[9 * k + 4] = vertex.vPos2.x()
            array[9 * k + 5] = vertex.vPos2.y()
            array[9 * k + 6] = vertex.vThisLoc.x()
            array[9 * k + 7] = vertex.vThisLoc.y()
            array[9 * k + 8] = vertex.vertex

        print("DONE!")

        return array.tobytes()

    def buffer_size(self) -> int:
        '''in bytes'''
        return len(self.vertices) * SceneHeightMap.VertexData.NB_FLOATS_PER_VERTEX * np.float32().itemsize
    """


class SceneCutter:
    class VertexData:
        NB_FLOATS_PER_VERTEX = 6

        def __init__(self):
            self.vPos = QVector3D()
            self.vColor = QVector3D()

    def __init__(self, cutterDiameter: float, cutterHeight: float, cutterAngle: float):
        """infact mormalize dim here"""
        self.cutterDiameter = cutterDiameter  # not used here
        self.cutterAngle = cutterAngle  # not used
        self.cutterHeight = cutterHeight  # not used here

        self.numDivisions = 40
        self.numTriangles = self.numDivisions * 4

        # make a scene
        self.vertices: List[SceneCutter.VertexData] = self.make_scene()

        # fill the numpy array from the scene and gets its buffer
        self.buffer = self.make_buffer()

    def make_scene(self) -> List[VertexData]:
        Color = namedtuple("Color", ["r", "g", "b"])

        cyl_color = Color(0.2, 0.5, 0.3)
        top_color = Color(0.0, 0.0, 0.0)

        vertices: List[SceneCutter.VertexData] = []

        def addVertex(x: float, y: float, z: float, color=cyl_color):
            vertex = SceneCutter.VertexData()
            vertex.vPos.setX(x)
            vertex.vPos.setY(y)
            vertex.vPos.setZ(z)

            vertex.vColor.setX(color.r)
            vertex.vColor.setY(color.g)
            vertex.vColor.setZ(color.b)

            vertices.append(vertex)

        # define vertices
        lastX = 0.5 * math.cos(0)
        lastY = 0.5 * math.sin(0)
        for i in range(self.numDivisions):
            j = i + 1
            if j == self.numDivisions:
                j = 0
            x = 0.5 * math.cos(j * 2 * math.pi / self.numDivisions)
            y = 0.5 * math.sin(j * 2 * math.pi / self.numDivisions)

            # 2 triangles for the cylinder "wall"
            addVertex(lastX, lastY, 0.0)
            addVertex(x, y, 0.0)
            addVertex(lastX, lastY, 1.0)

            addVertex(x, y, 0.0)
            addVertex(x, y, 1.0)
            addVertex(lastX, lastY, 1.0)

            # lower base -> cheese part
            addVertex(0, 0, 0.0)
            addVertex(x, y, 0.0, top_color)
            addVertex(lastX, lastY, 0.0, top_color)

            # upper base -> cheese part
            addVertex(0, 0, 1.0)
            addVertex(lastX, lastY, 1.0, top_color)
            addVertex(x, y, 1.0, top_color)

            lastX = x
            lastY = y

        return vertices

    def make_buffer(self):
        # fill the numpy array - each vertex is composed of 6 float
        array = np.zeros(
            len(self.vertices) * SceneCutter.VertexData.NB_FLOATS_PER_VERTEX,
            dtype=np.float32,
        )

        for k, vertex in enumerate(self.vertices):
            array[6 * k + 0] = vertex.vPos.x()
            array[6 * k + 1] = vertex.vPos.y()
            array[6 * k + 2] = vertex.vPos.z()
            array[6 * k + 3] = vertex.vColor.x()
            array[6 * k + 4] = vertex.vColor.y()
            array[6 * k + 5] = vertex.vColor.z()

        return array.tobytes()


class Drawable:
    path_shader_vs = "shaders/rasterizePathVertexShader.txt"
    path_shader_fs = "shaders/rasterizePathFragmentShader.txt"

    height_shader_vs = "shaders/renderHeightMapVertexShader.txt"
    height_shader_fs = "shaders/renderHeightMapFragmentShader.txt"

    #  the cutter
    basic_shader_vs = "shaders/basicVertexShader.txt"
    basic_shader_fs = "shaders/basicFragmentShader.txt"

    TEXTURE_INDEX_0 = 0

    GPU_COEFF = 1  # SMALL GPU !

    PYCUT_PREFIX = ""  # standalone: empty

    @classmethod
    def set_pycut_prefix(cls):
        """inside pycut"""
        cls.PYCUT_PREFIX = "gcodesimulator/"

    def __init__(
        self,
        gcode: str,
        cutter_diameter: float,
        cutter_height: float,
        cutter_angle: float,
        use_candle_parser: bool,
    ):
        RESOL = 1024 * Drawable.GPU_COEFF

        self.gpuMem = 2 * RESOL * RESOL
        self.resolution = RESOL

        self.SIZE_X = 800
        self.SIZE_Y = 800

        self.cutter_diameter = cutter_diameter
        self.cutter_height = cutter_height
        self.cutter_angle = cutter_angle

        self.use_candle_parser = use_candle_parser

        print("Scene path...")
        self.scene = Scene(
            gcode, cutter_diameter, cutter_height, cutter_angle, use_candle_parser
        )
        print("Scene cutter...")
        self.scene_cutter = SceneCutter(cutter_diameter, cutter_height, cutter_angle)
        print("Scene heightmap...")
        self.scene_heightmap = SceneHeightMap(self.resolution)

        self.cutterDia = self.scene.cutterDiameter
        self.cutterAngleRad = self.scene.cutterAngle * math.pi / 180
        self.isVBit = self.scene.isVBit
        self.cutterH = self.scene.cutterHeight
        self.pathXOffset = self.scene.pathXOffset
        self.pathYOffset = self.scene.pathYOffset
        self.pathScale = self.scene.pathScale
        self.pathMinZ = self.scene.pathMinZ
        self.pathTopZ = self.scene.topZ

        self.stopAtTime = 9999999  # end view
        self.rotate = QMatrix4x4()
        self.rotate.setToIdentity()

        # -----------------------------------------------

        self.needToCreatePathTexture = False
        self.needToDrawHeightMap = False
        self.requestFrame = None

        self.program_path = QOpenGLShaderProgram()
        self.vao_path = QOpenGLVertexArrayObject()
        self.vbo_path = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)

        self.program_heightmap = QOpenGLShaderProgram()
        self.vao_heightmap = QOpenGLVertexArrayObject()
        self.vbo_heightmap = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)

        self.program_cutter = QOpenGLShaderProgram()
        self.vao_cutter = QOpenGLVertexArrayObject()
        self.vbo_cutter = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)

        self.model = QMatrix4x4()
        self.model.setToIdentity()

        self.proj = QMatrix4x4()
        self.proj.setToIdentity()

        self.view = QMatrix4x4()
        self.view.setToIdentity()
        self.view.translate(QVector3D(0, 0, -5))

    def resize(self, width, height):
        self.SIZE_X = width
        self.SIZE_Y = height

    def clean(self):
        self.vbo_path.destroy()
        self.vbo_cutter.destroy()
        self.vbo_heightmap.destroy()
        del self.program_path
        del self.program_cutter
        del self.program_heightmap
        self.program_path = None
        self.program_cutter = None
        self.program_heightmap = None

    def initialize(self):
        """ """
        self.initialize_path()
        self.initialize_heightmap()
        self.initialize_cutter()

    def draw(self, gl: "GLView"):
        rc1 = self.pathFramebuffer.bind()
        gl.glEnable(GL.GL_DEPTH_TEST)

        self.create_path_texture(gl)

        rc2 = self.pathFramebuffer.bindDefault()

        # SAVE IMAGE: PATH
        # img = self.pathFramebuffer.toImage()
        # img.save("framebuffer_tex.jpg")

        self.draw_heightmap(gl)
        self.draw_cutter(gl)

    # -----------------------------------------------------------------

    def initialize_path(self):
        """ """
        self.program_path.addShaderFromSourceFile(
            QOpenGLShader.Vertex, self.PYCUT_PREFIX + self.path_shader_vs
        )
        self.program_path.addShaderFromSourceFile(
            QOpenGLShader.Fragment, self.PYCUT_PREFIX + self.path_shader_fs
        )
        self.program_path.link()

        if not self.program_path.isLinked():
            print("Failed to link program_path")
            raise RuntimeError("Linking error")

        self.program_path.bind()

        vbo_float_array = np.zeros(self.gpuMem, dtype=np.float32)

        self.vbo_path.create()  # QOpenGLBuffer.VertexBuffer
        self.vbo_path.setUsagePattern(QOpenGLBuffer.DynamicDraw)
        self.vbo_path.bind()

        self.vbo_path.allocate(
            vbo_float_array.tobytes(), vbo_float_array.size * np.float32().itemsize
        )

        self.setup_vao_path()

        self.program_path.release()

    def setup_vao_path(self):
        self.vao_path.create()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao_path)

        self.resolutionLocation = self.program_path.uniformLocation("resolution")
        self.cutterDiaLocation = self.program_path.uniformLocation("cutterDia")
        self.pathXYOffsetLocation = self.program_path.uniformLocation("pathXYOffset")
        self.pathScaleLocation = self.program_path.uniformLocation("pathScale")
        self.pathMinZLocation = self.program_path.uniformLocation("pathMinZ")
        self.pathTopZLocation = self.program_path.uniformLocation("pathTopZ")
        self.stopAtTimeLocation = self.program_path.uniformLocation("stopAtTime")

        self.program_path.setUniformValue1f(
            self.resolutionLocation, float(self.resolution)
        )
        self.program_path.setUniformValue1f(
            self.cutterDiaLocation, float(self.cutterDia)
        )
        self.program_path.setUniformValue(
            self.pathXYOffsetLocation, float(self.pathXOffset), float(self.pathYOffset)
        )
        self.program_path.setUniformValue1f(
            self.pathScaleLocation, float(self.pathScale)
        )
        self.program_path.setUniformValue1f(self.pathMinZLocation, float(self.pathMinZ))
        self.program_path.setUniformValue1f(self.pathTopZLocation, float(self.pathTopZ))
        self.program_path.setUniformValue1f(
            self.stopAtTimeLocation, float(self.stopAtTime)
        )

        self.vbo_path.bind()

        self.pos1Location = self.program_path.attributeLocation("pos1")
        self.pos2Location = self.program_path.attributeLocation("pos2")
        self.startTimeLocation = self.program_path.attributeLocation("startTime")
        self.endTimeLocation = self.program_path.attributeLocation("endTime")
        self.commandLocation = self.program_path.attributeLocation("command")
        self.rawPosLocation = self.program_path.attributeLocation("rawPos")

        stride = Scene.VertexData.NB_FLOATS_PER_VERTEX * np.float32().itemsize

        self.program_path.setAttributeBuffer(
            self.pos1Location, GL.GL_FLOAT, 0, 3, stride
        )
        self.program_path.enableAttributeArray(self.pos1Location)

        self.program_path.setAttributeBuffer(
            self.pos2Location, GL.GL_FLOAT, 3 * np.float32().itemsize, 3, stride
        )
        self.program_path.enableAttributeArray(self.pos2Location)

        self.program_path.setAttributeBuffer(
            self.startTimeLocation, GL.GL_FLOAT, 6 * np.float32().itemsize, 1, stride
        )
        self.program_path.enableAttributeArray(self.startTimeLocation)

        self.program_path.setAttributeBuffer(
            self.endTimeLocation, GL.GL_FLOAT, 7 * np.float32().itemsize, 1, stride
        )
        self.program_path.enableAttributeArray(self.endTimeLocation)

        self.program_path.setAttributeBuffer(
            self.commandLocation, GL.GL_FLOAT, 8 * np.float32().itemsize, 1, stride
        )
        self.program_path.enableAttributeArray(self.commandLocation)

        # if self.isVBit:
        #    self.program_path.setAttributeBuffer(self.rawPosLocation, GL.GL_FLOAT,   9* np.float32().itemsize, 3, stride)
        #    self.program_path.enableAttributeArray(self.rawPosLocation)

        # self.vbo_path.release()

        vao_binder = None

        # self.vbo_path.release()

    def create_path_texture(self, gl: "GLView"):
        """ """
        gl.glClearColor(0.0, 1.0, 0.0, 1.0)
        gl.glEnable(GL.GL_DEPTH_TEST)
        gl.glViewport(
            0,
            0,
            self.resolution * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
            self.resolution * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
        )
        gl.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.program_path.bind()
        self.vbo_path.bind()

        self.program_path.setUniformValue1f(
            self.resolutionLocation,
            float(self.resolution * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION),
        )
        self.program_path.setUniformValue1f(
            self.cutterDiaLocation, float(self.cutterDia)
        )
        self.program_path.setUniformValue(
            self.pathXYOffsetLocation, float(self.pathXOffset), float(self.pathYOffset)
        )
        self.program_path.setUniformValue1f(
            self.pathScaleLocation, float(self.pathScale)
        )
        self.program_path.setUniformValue1f(self.pathMinZLocation, float(self.pathMinZ))
        self.program_path.setUniformValue1f(self.pathTopZLocation, float(self.pathTopZ))
        self.program_path.setUniformValue1f(
            self.stopAtTimeLocation, float(self.stopAtTime)
        )

        self.program_path.enableAttributeArray(self.pos1Location)
        self.program_path.enableAttributeArray(self.pos2Location)
        self.program_path.enableAttributeArray(self.startTimeLocation)
        self.program_path.enableAttributeArray(self.endTimeLocation)
        self.program_path.enableAttributeArray(self.commandLocation)
        if self.isVBit:
            self.program_path.enableAttributeArray(self.rawPosLocation)

        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao_path)

        numTriangles = self.scene.pathNumVertexes // 3
        lastTriangle = 0
        maxTriangles = self.gpuMem // (
            self.scene.pathStride * 3 * np.float32().itemsize
        )

        while lastTriangle < numTriangles:
            n = min(numTriangles - lastTriangle, maxTriangles)

            """
            PROTOTYPE Float32Array(a.buffer, offset, length) : offset in bytes, length = #floats 
            pathBufferContent is a Float32Array
            pathBufferContent.buffer is an ArrayBuffer

            b = new Float32Array(pathBufferContent.buffer, lastTriangle * pathStride * 3 * Float32Array.BYTES_PER_ELEMENT, n * pathStride * 3)
            gl.bufferSubData(self.gl.ARRAY_BUFFER, 0, b)
            """

            # TRANSLATES TO

            start = lastTriangle * self.scene.pathStride * 3  # in float
            length = n * self.scene.pathStride * 3  # in float

            array_window = self.scene.array[start : start + length]

            """
            for k, vertexdata in enumerate(self.scene.vertices):
                print(f"{k} -> pos 1 = {vertexdata.pos1}")
                print(f"{k} -> pos 2 = {vertexdata.pos2}")
                print(f"{k} -> start/end time 2 = {vertexdata.startTime} - {vertexdata.endTime}")
                print(f"{k} -> command = {vertexdata.command}")
            """

            """for k in range(array_window.size):
                print(f"{k} -> byte = {array_window[k]}")
            """

            # PROTO write(offset, data, size) all in bytes
            self.vbo_path.write(
                0, array_window.tobytes(), array_window.size * np.float32().itemsize
            )

            # draw
            gl.glDrawArrays(GL.GL_TRIANGLES, 0, n * 3)  # n*3 "strides"

            lastTriangle += n

        # self.program_path.disableAttributeArray(self.pos1Location)
        # self.program_path.disableAttributeArray(self.pos2Location)
        # self.program_path.disableAttributeArray(self.startTimeLocation)
        # self.program_path.disableAttributeArray(self.endTimeLocation)
        # self.program_path.disableAttributeArray(self.commandLocation)
        # if self.isVBit:
        #    self.program_path.disableAttributeArray(self.rawPosLocation)

        # self.vbo_path.release()
        vao_binder = None

        self.program_path.release()
        self.vbo_path.release()

    # -----------------------------------------------------------------

    def initialize_heightmap(self):
        """ """
        self.program_heightmap.addShaderFromSourceFile(
            QOpenGLShader.Vertex, self.PYCUT_PREFIX + self.height_shader_vs
        )
        self.program_heightmap.addShaderFromSourceFile(
            QOpenGLShader.Fragment, self.PYCUT_PREFIX + self.height_shader_fs
        )
        self.program_heightmap.link()

        self.program_heightmap.bind()

        self.vbo_heightmap.create()
        self.vbo_heightmap.setUsagePattern(QOpenGLBuffer.StaticDraw)
        self.vbo_heightmap.bind()

        self.vbo_heightmap.allocate(
            self.scene_heightmap.buffer, len(self.scene_heightmap.buffer)
        )

        self.create_heightmap_texture()
        self.setup_vao_heightmap()

        self.program_heightmap.release()

    def setup_vao_heightmap(self):
        self.vao_heightmap.create()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao_heightmap)

        self.program_heightmap_resolutionLocation = (
            self.program_heightmap.uniformLocation("resolution")
        )
        self.program_heightmap_pathScaleLocation = (
            self.program_heightmap.uniformLocation("pathScale")
        )
        self.program_heightmap_pathMinZLocation = (
            self.program_heightmap.uniformLocation("pathMinZ")
        )
        self.program_heightmap_pathTopZLocation = (
            self.program_heightmap.uniformLocation("pathTopZ")
        )
        self.program_heightmap_rotateLocation = self.program_heightmap.uniformLocation(
            "rotate"
        )
        self.program_heightmap_heightMapLocation = (
            self.program_heightmap.uniformLocation("heightMap")
        )

        self.program_heightmap_pos0Location = self.program_heightmap.attributeLocation(
            "pos0"
        )
        self.program_heightmap_pos1Location = self.program_heightmap.attributeLocation(
            "pos1"
        )
        self.program_heightmap_pos2Location = self.program_heightmap.attributeLocation(
            "pos2"
        )
        self.program_heightmap_thisPos = self.program_heightmap.attributeLocation(
            "thisPos"
        )
        self.program_heightmap_vertex = self.program_heightmap.attributeLocation(
            "vertex"
        )

        self.vbo_heightmap.bind()

        stride = SceneHeightMap.VertexData.NB_FLOATS_PER_VERTEX * np.float32().itemsize

        self.program_heightmap.setAttributeBuffer(
            self.program_heightmap_pos0Location, GL.GL_FLOAT, 0, 2, stride
        )
        self.program_heightmap.enableAttributeArray(self.program_heightmap_pos0Location)

        self.program_heightmap.setAttributeBuffer(
            self.program_heightmap_pos1Location,
            GL.GL_FLOAT,
            2 * np.float32().itemsize,
            2,
            stride,
        )
        self.program_heightmap.enableAttributeArray(self.program_heightmap_pos1Location)

        self.program_heightmap.setAttributeBuffer(
            self.program_heightmap_pos2Location,
            GL.GL_FLOAT,
            4 * np.float32().itemsize,
            2,
            stride,
        )
        self.program_heightmap.enableAttributeArray(self.program_heightmap_pos2Location)

        self.program_heightmap.setAttributeBuffer(
            self.program_heightmap_thisPos,
            GL.GL_FLOAT,
            6 * np.float32().itemsize,
            2,
            stride,
        )
        self.program_heightmap.enableAttributeArray(self.program_heightmap_thisPos)

        self.program_heightmap.setAttributeBuffer(
            self.program_heightmap_vertex,
            GL.GL_FLOAT,
            8 * np.float32().itemsize,
            1,
            stride,
        )
        # self.program_heightmap.enableAttributeArray(self.program_heightmap_vertex)

        # self.vbo_heightmap.release()

        vao_binder = None
        # self.vbo_heightmap.release()

    def create_heightmap_texture(self):
        self.pathFramebuffer = QOpenGLFramebufferObject(
            QSize(
                self.resolution * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
                self.resolution * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
            ),
            QOpenGLFramebufferObject.CombinedDepthStencil,
        )
        # --------------------------------- the texture ------------------------------------------
        self.textureLocationID = self.program_heightmap.uniformLocation("heightMap")
        self.program_heightmap.setUniformValue(
            self.textureLocationID, self.TEXTURE_INDEX_0
        )  # the index of the texture
        # --------------------------------- the texture ------------------------------------------

    def draw_heightmap(self, gl: "GLView"):
        gl.glDisable(
            GL.GL_DEPTH_TEST
        )  # the "standard" framebuffer draw.... (learnopengl.com)
        gl.glEnable(GL.GL_DEPTH_TEST)  # as in jsCut! strange but so it is!
        gl.glClearColor(0.7, 0.2, 0.2, 0.0)
        gl.glViewport(
            0,
            0,
            self.SIZE_X * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
            self.SIZE_Y * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
        )
        gl.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.program_heightmap.bind()

        gl.glActiveTexture(self.TEXTURE_INDEX_0)
        gl.glBindTexture(GL.GL_TEXTURE_2D, self.pathFramebuffer.texture())

        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao_heightmap)
        # self.vao_heightmap.bind()
        self.vbo_heightmap.bind()

        self.program_heightmap.setUniformValue1f(
            self.program_heightmap_resolutionLocation, self.resolution
        )
        self.program_heightmap.setUniformValue1f(
            self.program_heightmap_pathScaleLocation, self.pathScale
        )
        self.program_heightmap.setUniformValue1f(
            self.program_heightmap_pathMinZLocation, self.pathMinZ
        )
        self.program_heightmap.setUniformValue1f(
            self.program_heightmap_pathTopZLocation, self.pathTopZ
        )
        self.program_heightmap.setUniformValue(
            self.program_heightmap_rotateLocation, self.rotate
        )
        self.program_heightmap.setUniformValue(
            self.program_heightmap_heightMapLocation, self.TEXTURE_INDEX_0
        )

        self.program_heightmap.enableAttributeArray(self.program_heightmap_pos0Location)
        self.program_heightmap.enableAttributeArray(self.program_heightmap_pos1Location)
        self.program_heightmap.enableAttributeArray(self.program_heightmap_pos2Location)
        self.program_heightmap.enableAttributeArray(self.program_heightmap_thisPos)
        # self.program_heightmap.enableAttributeArray(self.program_heightmap_vertex)

        gl.glDrawArrays(GL.GL_TRIANGLES, 0, self.scene_heightmap.meshNumVertexes)

        self.program_heightmap.disableAttributeArray(
            self.program_heightmap_pos0Location
        )
        self.program_heightmap.disableAttributeArray(
            self.program_heightmap_pos1Location
        )
        self.program_heightmap.disableAttributeArray(
            self.program_heightmap_pos2Location
        )
        self.program_heightmap.disableAttributeArray(self.program_heightmap_thisPos)
        # self.program_heightmap.disableAttributeArray(self.program_heightmap_vertex)

        vao_binder = None
        # self.vao_heightmap.release()

        gl.glBindTexture(GL.GL_TEXTURE_2D, 0)
        gl.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        # self.vbo_heightmap.release()

        self.program_heightmap.release()

        self.needToDrawHeightMap = False

    # -----------------------------------------------------------------

    def initialize_cutter(self):
        """ """
        self.program_cutter.addShaderFromSourceFile(
            QOpenGLShader.Vertex, self.PYCUT_PREFIX + self.basic_shader_vs
        )
        self.program_cutter.addShaderFromSourceFile(
            QOpenGLShader.Fragment, self.PYCUT_PREFIX + self.basic_shader_fs
        )
        self.program_cutter.link()

        self.program_cutter.bind()

        self.vbo_cutter.create()
        self.vbo_cutter.setUsagePattern(QOpenGLBuffer.StaticDraw)
        self.vbo_cutter.bind()

        self.vbo_cutter.allocate(
            self.scene_cutter.buffer, len(self.scene_cutter.buffer)
        )

        self.setup_vao_cutter()

        self.program_cutter.release()

    def setup_vao_cutter(self):
        self.vao_cutter.create()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao_cutter)

        self.scaleLocation = self.program_cutter.uniformLocation("scale")
        self.translateLocation = self.program_cutter.uniformLocation("translate")
        self.rotateLocation = self.program_cutter.uniformLocation("rotate")

        self.program_cutter.setUniformValue(
            self.scaleLocation,
            float(self.cutterDia * self.pathScale),
            float(self.cutterDia * self.pathScale),
            float(self.cutterH * self.pathScale),
        )
        self.program_cutter.setUniformValue(
            self.translateLocation,
            float((0 + self.pathXOffset) * self.pathScale),
            float((0 + self.pathYOffset) * self.pathScale),
            float((0 - self.pathTopZ) * self.pathScale),
        )
        self.program_cutter.setUniformValue(self.rotateLocation, self.rotate)

        self.vbo_cutter.bind()

        self.posLocation = self.program_cutter.attributeLocation("vPos")
        self.colLocation = self.program_cutter.attributeLocation("vColor")

        stride = SceneCutter.VertexData.NB_FLOATS_PER_VERTEX * np.float32().itemsize

        self.program_cutter.setAttributeBuffer(
            self.posLocation, GL.GL_FLOAT, 0, 3, stride
        )
        self.program_cutter.enableAttributeArray(self.posLocation)

        self.program_cutter.setAttributeBuffer(
            self.colLocation, GL.GL_FLOAT, 3 * np.float32().itemsize, 3, stride
        )
        self.program_cutter.enableAttributeArray(self.colLocation)

        # self.vbo_cutter.release()

        vao_binder = None

    def draw_cutter(self, gl: "GLView"):
        """ """

        def lowerBound(
            data, offset: int, stride: int, begin: int, end: int, value: float
        ):
            while begin < end:
                i = math.floor((begin + end) / 2)

                if data[offset + i * stride] < value:
                    begin = i + 1
                else:
                    end = i

            return end

        def mix(v0, v1, a):
            return v0 + (v1 - v0) * a

        i = lowerBound(
            self.scene.array,
            7,
            self.scene.pathStride * self.scene.pathVertexesPerLine,
            0,
            self.scene.pathNumPoints,
            self.stopAtTime,
        )
        x = 0.0
        y = 0.0
        z = 0.0

        if i < self.scene.pathNumPoints:
            offset = i * self.scene.pathStride * self.scene.pathVertexesPerLine
            beginTime = self.scene.array[offset + 6]
            endTime = self.scene.array[offset + 7]
            ratio = 0
            if endTime == beginTime:
                ratio = 0
            else:
                ratio = (self.stopAtTime - beginTime) / (endTime - beginTime)
            x = mix(self.scene.array[offset + 0], self.scene.array[offset + 3], ratio)
            y = mix(self.scene.array[offset + 1], self.scene.array[offset + 4], ratio)
            z = mix(self.scene.array[offset + 2], self.scene.array[offset + 5], ratio)

        else:
            offset = (i - 1) * self.scene.pathStride * self.scene.pathVertexesPerLine
            x = self.scene.array[offset + 3]
            y = self.scene.array[offset + 4]
            z = self.scene.array[offset + 5]

        gl.glEnable(GL.GL_DEPTH_TEST)

        self.program_cutter.bind()
        self.vbo_cutter.bind()

        self.program_cutter.setUniformValue(
            self.scaleLocation,
            float(self.cutterDia * self.pathScale),
            float(self.cutterDia * self.pathScale),
            float(self.cutterH * self.pathScale),
        )
        self.program_cutter.setUniformValue(
            self.translateLocation,
            float((x + self.pathXOffset) * self.pathScale),
            float((y + self.pathYOffset) * self.pathScale),
            float((z - self.pathTopZ) * self.pathScale),
        )
        self.program_cutter.setUniformValue(self.rotateLocation, self.rotate)

        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao_cutter)

        self.program_cutter.enableAttributeArray(self.posLocation)
        self.program_cutter.enableAttributeArray(self.colLocation)

        gl.glDrawArrays(GL.GL_TRIANGLES, 0, len(self.scene_cutter.vertices))

        # self.program_cutter.disableAttributeArray(self.posLocation)
        # self.program_cutter.disableAttributeArray(self.colLocation)

        vao_binder = None

        self.vbo_cutter.release()
        self.program_cutter.release()


class GLView(QOpenGLWidget, QOpenGLFunctions):
    """ """

    rotationChanged = QtCore.Signal()
    resized = QtCore.Signal()

    def __init__(
        self,
        gcode: str,
        cutter_diameter: float,
        cutter_height: float,
        cutter_angle: float,
        use_candle_parser: bool,
    ):
        QOpenGLWidget.__init__(self)
        QOpenGLFunctions.__init__(self)

        self.setGeometry(0, 0, 800, 800)

        self.drawable = Drawable(
            gcode, cutter_diameter, cutter_height, cutter_angle, use_candle_parser
        )

        self.m_xRot = 90.0
        self.m_xRot = 0.0  # PYCUT
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
        self.m_lastPos = QPoint(0, 0)
        self.m_zoom = 10.0
        self.m_distance = 10.0
        self.m_xMin = 0.0
        self.m_xMax = 0.0
        self.m_yMin = 0.0
        self.m_yMax = 0.0
        self.m_zMin = 0.0
        self.m_zMax = 0.0
        self.m_xSize = 0.0
        self.m_ySize = 0.0
        self.m_zSize = 0.0

        self.m_xRotTarget = 90.0
        self.m_yRotTarget = 0.0
        self.m_xRotStored = 0.0
        self.m_yRotStored = 0.0

        self.updateProjection()
        self.updateView()

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

        if Drawable.PYCUT_PREFIX == "":
            self.cmdFit.setIcon(QtGui.QIcon("./pics/fit_1.png"))
            self.cmdIsometric.setIcon(QtGui.QIcon("./pics/cube.png"))
            self.cmdTop.setIcon(QtGui.QIcon("./pics/cubeTop.png"))
            self.cmdFront.setIcon(QtGui.QIcon("./pics/cubeFront.png"))
            self.cmdLeft.setIcon(QtGui.QIcon("./pics/cubeLeft.png"))
        else:
            self.cmdFit.setIcon(QtGui.QIcon(":/images/candle/fit_1.png"))
            self.cmdIsometric.setIcon(QtGui.QIcon(":/images/candle/cube.png"))
            self.cmdTop.setIcon(QtGui.QIcon(":/images/candle/cubeTop.png"))
            self.cmdFront.setIcon(QtGui.QIcon(":/images/candle/cubeFront.png"))
            self.cmdLeft.setIcon(QtGui.QIcon(":/images/candle/cubeLeft.png"))

        self.cmdFit.setVisible(False)

        # self.cmdFit.clicked.connect(self.on_cmdFit_clicked)
        self.cmdIsometric.clicked.connect(self.on_cmdIsometric_clicked)
        self.cmdTop.clicked.connect(self.on_cmdTop_clicked)
        self.cmdFront.clicked.connect(self.on_cmdFront_clicked)
        self.cmdLeft.clicked.connect(self.on_cmdLeft_clicked)

        self.rotationChanged.connect(self.onVisualizatorRotationChanged)
        self.resized.connect(self.placeVisualizerButtons)

        self.on_cmdIsometric_clicked()

    def placeVisualizerButtons(self):
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
        self.fitDrawable()

    def calculateVolume(self, size: QtGui.QVector3D) -> float:
        return size.x() * size.y() * size.z()

    def fitDrawable(self):
        self.updateExtremes()

        a = self.m_ySize / 2 / 0.25 * 1.3 + (self.m_zMax - self.m_zMin) / 2
        b = (
            self.m_xSize / 2 / 0.25 * 1.3 / (self.width() / self.height())
            + (self.m_zMax - self.m_zMin) / 2
        )

        self.m_distance = max(a, b)

        if self.m_distance == 0:
            self.m_distance = 10

        self.m_xLookAt = (self.m_xMax - self.m_xMin) / 2 + self.m_xMin
        self.m_zLookAt = -((self.m_yMax - self.m_yMin) / 2 + self.m_yMin)
        self.m_yLookAt = (self.m_zMax - self.m_zMin) / 2 + self.m_zMin

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

    def updateExtremes(self):
        self.m_xMin = self.drawable.scene.getMinimumExtremes().x()
        self.m_xMax = self.drawable.scene.getMaximumExtremes().x()

        self.m_yMin = self.drawable.scene.getMinimumExtremes().y()
        self.m_yMax = self.drawable.scene.getMaximumExtremes().y()

        self.m_zMin = self.drawable.scene.getMinimumExtremes().z()
        self.m_zMax = self.drawable.scene.getMaximumExtremes().z()

        self.m_xSize = self.m_xMax - self.m_xMin
        self.m_ySize = self.m_yMax - self.m_yMin
        self.m_zSize = self.m_zMax - self.m_zMin

    def setIsometricView(self):
        """no animation yet"""
        self.m_xRotTarget = 45
        self.m_yRotTarget = 405 if self.m_yRot > 180 else 45

        self.m_xRot = 45
        self.m_yRot = 405 if self.m_yRot > 180 else 45

    def setTopView(self):
        """no animation yet"""
        self.m_xRotTarget = 90
        self.m_yRotTarget = 360 if self.m_yRot > 180 else 0

        self.m_xRot = 90
        self.m_yRot = 360 if self.m_yRot > 180 else 0

    def setFrontView(self):
        """no animation yet"""
        self.m_xRotTarget = 0
        self.m_yRotTarget = 360 if self.m_yRot > 180 else 0

        self.m_xRot = 0
        self.m_yRot = 360 if self.m_yRot > 180 else 0

    def setLeftView(self):
        """no animation yet"""
        self.m_xRotTarget = 0
        self.m_yRotTarget = 450 if self.m_yRot > 270 else 90

        self.m_xRot = 0
        self.m_yRot = 450 if self.m_yRot > 270 else 90

    def updateProjection(self):
        # Reset projection
        self.drawable.proj.setToIdentity()

        asp = self.width() / self.height()
        self.drawable.proj.frustum(
            (-0.5 + self.m_xPan) * asp,
            (0.5 + self.m_xPan) * asp,
            -0.5 + self.m_yPan,
            0.5 + self.m_yPan,
            2,
            self.m_distance * 2,
        )

    def updateView(self):
        # Set view matrix
        self.drawable.view.setToIdentity()

        r = self.m_distance
        angY = math.pi / 180 * self.m_yRot
        angX = math.pi / 180 * self.m_xRot

        eye = QtGui.QVector3D(
            r * math.cos(angX) * math.sin(angY) + self.m_xLookAt,
            r * math.sin(angX) + self.m_yLookAt,
            r * math.cos(angX) * math.cos(angY) + self.m_zLookAt,
        )

        center = QtGui.QVector3D(self.m_xLookAt, self.m_yLookAt, self.m_zLookAt)

        xRot = math.pi if self.m_xRot < 0 else 0

        up = QtGui.QVector3D(
            -math.sin(angY + xRot) if math.fabs(self.m_xRot) == 90 else 0,
            math.cos(angX),
            -math.cos(angY + xRot) if math.fabs(self.m_xRot) == 90 else 0,
        )

        self.drawable.view.lookAt(eye, center, up.normalized())

        self.drawable.view.translate(self.m_xLookAt, self.m_yLookAt, self.m_zLookAt)
        self.drawable.view.scale(self.m_zoom, self.m_zoom, self.m_zoom)
        self.drawable.view.translate(-self.m_xLookAt, -self.m_yLookAt, -self.m_zLookAt)

        self.drawable.view.rotate(-90, 1.0, 0.0, 0.0)

        # PYCUT WANTS THE ROTATION ONLY
        self.drawable.rotate.setToIdentity()
        self.drawable.rotate.rotate(-90, 1.0, 0.0, 0.0)
        self.drawable.rotate.rotate(angX * 180 / math.pi, 1.0, 0.0, 0.0)
        self.drawable.rotate.rotate(-angY * 180 / math.pi, 0.0, 0.0, 1.0)
        # PYCUT WANTS THE ROTATION ONLY

    def set_model_position(self, position: QVector3D):
        self.drawable.model.setToIdentity()
        self.drawable.model.translate(position)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.m_lastPos = event.position()  # type: ignore [assignment]
        self.m_xLastRot = self.m_xRot
        self.m_yLastRot = self.m_yRot
        self.m_xLastPan = self.m_xPan
        self.m_yLastPan = self.m_yPan

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if (
            event.buttons() & QtGui.Qt.MouseButton.MiddleButton
            and (not (event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier))
        ) or event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.m_yRot = self.normalizeAngle(
                self.m_yLastRot - (event.position().x() - self.m_lastPos.x()) * 0.5
            )
            self.m_xRot = (
                self.m_xLastRot + (event.position().y() - self.m_lastPos.y()) * 0.5
            )

            if self.m_xRot < -90:
                self.m_xRot = -90
            if self.m_xRot > 90:
                self.m_xRot = 90

            self.updateView()
            self.rotationChanged.emit()

        if (
            event.buttons() & QtCore.Qt.MouseButton.MiddleButton
            and event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier
        ) or event.buttons() & QtCore.Qt.MouseButton.RightButton:
            self.m_xPan = self.m_xLastPan - (
                event.position().x() - self.m_lastPos.x()
            ) * 1 / (float)(self.width())
            self.m_yPan = self.m_yLastPan + (
                event.position().y() - self.m_lastPos.y()
            ) * 1 / (float)(self.height())

            self.updateProjection()

        self.update()

    def wheelEvent(self, we: QtGui.QWheelEvent):
        if self.m_zoom > 0.001 and we.angleDelta().y() < 0:
            self.m_xPan -= (
                (float)(we.position().x() / self.width() - 0.5 + self.m_xPan)
            ) * (1 - 1 / ZOOMSTEP)
            self.m_yPan += (
                (float)(we.position().y() / self.height() - 0.5 - self.m_yPan)
            ) * (1 - 1 / ZOOMSTEP)

            self.m_zoom /= ZOOMSTEP

            # XAM
            self.drawable.pathScale /= ZOOMSTEP
            # XAM

        elif self.m_zoom < 10 and we.angleDelta().y() > 0:
            self.m_xPan -= (
                (float)(we.position().x() / self.width() - 0.5 + self.m_xPan)
            ) * (1 - ZOOMSTEP)
            self.m_yPan += (
                (float)(we.position().y() / self.height() - 0.5 - self.m_yPan)
            ) * (1 - ZOOMSTEP)

            self.m_zoom *= ZOOMSTEP

            # XAM
            self.drawable.pathScale *= ZOOMSTEP
            # XAM

        self.updateProjection()
        self.updateView()

        self.update()

    def onVisualizatorRotationChanged(self):
        self.update()

    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------

    def sizeHint(self):
        return QSize(800, 800)

    def cleanup(self):
        self.makeCurrent()
        self.drawable.clean()
        self.doneCurrent()

    def initializeGL(self):
        self.context().aboutToBeDestroyed.connect(self.cleanup)
        self.initializeOpenGLFunctions()
        self.glClearColor(0.2, 0.7, 0.7, 1)
        self.glViewport(
            0,
            0,
            800 * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
            800 * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
        )

        self.drawable.initialize()

    def paintGL(self):
        self.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.glEnable(GL.GL_DEPTH_TEST)

        self.drawable.draw(self)

        self.updateProjection()
        self.updateView()

        # self.update()

    def resizeGL(self, width, height):
        quadra_size = min(width, height)

        xoffset = width - quadra_size // 2
        yoffset = height - quadra_size // 2

        self.glViewport(
            xoffset,
            yoffset,
            quadra_size * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
            quadra_size * GCodeSimulatorSettings.OPENGL_FB_RESOLUTION,
        )

        ratio = width / float(height)
        self.drawable.resize(quadra_size, quadra_size)
        self.drawable.proj.perspective(45.0, ratio, 2.0, 100.0)

        self.update()

    def setStopAtTime(self, stopAtTime: float):
        self.drawable.stopAtTime = math.floor(stopAtTime)
        self.update()


class SimulationControls(QtWidgets.QWidget):
    """ """

    simtime_changed = QtCore.Signal(float)

    # -----------------------------------------------------------------------------
    class SimulatorRunner(QtCore.QObject):
        """ """

        current_tick_changed = QtCore.Signal(int)

        def __init__(self, parent: "SimulationControls", init_tick: int, end_tick: int):
            QtCore.QObject.__init__(self, parent)

            self.sim_controls = parent

            self.base_speed = 1
            self.speed = 1

            self.direction = "forward"  # 'backward

            self.init_tick = init_tick
            self.end_tick = end_tick

            self.total_tick = self.end_tick - self.init_tick

            self.current_tick = self.init_tick

            self.set_current_tick(self.end_tick)
            self.current_tick_changed.connect(
                self.sim_controls.OnSimAtTickFromSimulatorRunner
            )

            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.run)

            self.timer_on = False

        def set_speed(self, coeff):
            self.speed = self.base_speed * coeff

            if self.timer_on == True:
                self.stop_timer()
                self.start_timer()

        def set_current_tick(self, current_tick):
            """ """
            self.current_tick = current_tick
            self.current_tick_changed.emit(self.current_tick)

        def step_forward(self):
            """ """
            self.current_tick += 1 * self.speed
            self.current_tick_changed.emit(self.current_tick)

        def step_backward(self):
            """ """
            self.current_tick -= 1 * self.speed
            self.current_tick_changed.emit(self.current_tick)

        def start_timer(self):
            timeout = 1.0
            if self.timer_on == False:
                self.timer_on = True
                self.timer.start(timeout)

        def stop_timer(self):
            if self.timer_on == True:
                self.timer.stop()
                self.timer_on = False

        def run(self):
            """
            callback on timer
            """
            if self.direction == "forward":
                current_tick = self.current_tick + 1 * self.speed

                if current_tick >= self.end_tick:
                    current_tick = self.init_tick

            else:
                current_tick = self.current_tick - 1 * self.speed

                if current_tick < 0:
                    current_tick = self.end_tick

            self.set_current_tick(current_tick)

    # -----------------------------------------------------------------------------

    def __init__(self, parent, gl_widget: GLView, gcode_textviewer: GCodeFileViewer):
        QtWidgets.QWidget.__init__(self)

        loader = QUiLoader(parent)

        self.control = loader.load(Drawable.PYCUT_PREFIX + "simcontrols.ui")
        # self.control = cast(QWidget, Ui_SimControlWidget())

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(self.control)

        self.gl_widget = gl_widget
        self.gcode_textviewer = gcode_textviewer

        self.control.pushButton_ToEnd.clicked.connect(self.OnSimToEnd)
        self.control.pushButton_Rewind.clicked.connect(self.OnSimAtStart)
        self.control.pushButton_RunForward.clicked.connect(self.OnSimRunForward)
        self.control.pushButton_RunBackward.clicked.connect(self.OnSimRunBackward)
        self.control.pushButton_StepForward.clicked.connect(self.OnSimStepForward)
        self.control.pushButton_StepBackward.clicked.connect(self.OnSimStepBackward)
        self.control.pushButton_Pause.clicked.connect(self.OnSimPause)

        self.slider_start = 0
        self.slider_end = int(self.gl_widget.drawable.scene.totalTime * 1000)
        self.slider_tick = 1

        self.control.horizontalSlider_Position.setMinimum(self.slider_start)
        self.control.horizontalSlider_Position.setMaximum(self.slider_end)
        self.control.horizontalSlider_Position.setSingleStep(self.slider_tick)
        self.control.horizontalSlider_Position.valueChanged.connect(self.OnSimAtTick)

        self.control.spinBox_SpeedFactor.valueChanged.connect(self.OnSpeedChange)
        self.control.spinBox_SpeedFactor.setMinimum(1)
        self.control.spinBox_SpeedFactor.setMaximum(9999)

        self.simulation_runner = SimulationControls.SimulatorRunner(
            self, 0, self.slider_end
        )

        self.control.spinBox_SpeedFactor.setValue(200)

        self.control.horizontalSlider_Position.setValue(self.slider_end)

        # signal
        self.simtime_changed.connect(self.gcode_textviewer.on_simtime_from_js)

    def OnSimAtStart(self):
        self.control.horizontalSlider_Position.setValue(0)

    def OnSimToEnd(self):
        self.control.horizontalSlider_Position.setValue(self.slider_end)

    def OnSimRewind(self):
        self.control.horizontalSlider_Position.setValue(0)

    def OnSimAtTick(self, tick: int):
        # inform openGL simulation
        self.gl_widget.setStopAtTime(tick / 1000.0)

        # set value directly in simulation runner-> no callback
        self.simulation_runner.current_tick = tick

        self.simtime_changed.emit(tick / 1000.0)

    def OnSimAtTickFromSimulatorRunner(self, tick: int):
        # inform openGL simulation
        self.gl_widget.setStopAtTime(tick / 1000.0)
        # inform the scrollbar
        self.control.horizontalSlider_Position.setValue(tick)

    def OnSimAtTickFromTextBrowser(self, tick: int):
        self.simtime_changed.disconnect(self.gcode_textviewer.on_simtime_from_js)

        # inform openGL simulation
        self.gl_widget.setStopAtTime(tick / 1000.0)
        # inform the scrollbar
        self.control.horizontalSlider_Position.setValue(tick)

        self.simtime_changed.connect(self.gcode_textviewer.on_simtime_from_js)

    def OnSimStepForward(self):
        self.simulation_runner.step_forward()

    def OnSimRunForward(self):
        self.simulation_runner.direction = "forward"
        self.simulation_runner.start_timer()

    def OnSimRunBackward(self):
        self.simulation_runner.direction = "backward"
        self.simulation_runner.start_timer()

    def OnSimStepBackward(self):
        self.simulation_runner.step_backward()

    def OnSimPause(self):
        self.simulation_runner.stop_timer()

    def OnSpeedChange(self, value: int):
        self.simulation_runner.set_speed(int(value))


class GCodeSimulator(QtWidgets.QWidget):
    """ """

    def __init__(self, parent: QtWidgets.QWidget, options: Dict[str, Any]):
        QtWidgets.QWidget.__init__(self)

        use_candle_parser = True

        self.gcode = gcode = options["gcode"]
        self.cutter_diameter = cutter_diameter = options["cutter_diameter"]
        self.cutter_height = cutter_height = options["cutter_height"]
        self.cutter_angle = cutter_angle = options["cutter_angle"]

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.gcode_textviewer = GCodeFileViewer(self)
        self.gcode_textviewer.load_data(gcode, use_candle_parser)

        self.gl_with_controls_layout = QtWidgets.QVBoxLayout()

        self.gl_widget = GLView(
            gcode, cutter_diameter, cutter_height, cutter_angle, use_candle_parser
        )
        self.gl_with_controls_layout.addWidget(self.gl_widget)

        self.controls = SimulationControls(self, self.gl_widget, self.gcode_textviewer)
        self.gl_with_controls_layout.addWidget(self.controls)

        self.gl_with_controls_layout.setStretch(0, 1)
        self.gl_with_controls_layout.setStretch(1, 0)

        layout.addLayout(self.gl_with_controls_layout)
        layout.addWidget(self.gcode_textviewer)

        layout.setStretch(0, 0)
        layout.setStretch(1, 0)

    def set_simtime_from_textbrowser(self, simtime: float):
        """slot on signal from gcode text browser "select line" """
        tick = math.floor(simtime * 1000)
        self.controls.OnSimAtTickFromTextBrowser(tick)


class GCodeSimulatorSettings:
    """ """

    class OpenGlFbType(IntEnum):
        # do not change these values!
        FB_STANDARD = 1
        FB_DOUBLE = 2

    OPENGL_FB_RESOLUTION = OpenGlFbType.FB_DOUBLE

    @classmethod
    def get_settings(cls):
        return {
            "fb": cls.OPENGL_FB_RESOLUTION,
        }

    @classmethod
    def set_opengl_fb_type(cls, fb_type: OpenGlFbType):
        print("OpenGL FB type: ", fb_type)
        cls.OPENGL_FB_RESOLUTION = fb_type
