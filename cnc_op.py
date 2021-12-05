
from typing import List

from ValWithUnit import ValWithUnit

from svgpathutils import SvgPath
from svgviewer import SvgViewer

from cam import cam

import clipper.clipper as ClipperLib
import clipper_utils
from clipper_utils import ClipperUtils

from pycut import ToolModel
from pycut import SvgModel
from pycut import MaterialModel
from pycut import TabsModel


class CncOp:
    '''
    '''
    def __init__(self, operation):
        self.operation = operation
        self.enabled = operation.get("enabled", False)

        self.units = self.operation["Units"]

        self.name = self.operation["Name"]
        self.ramp = self.operation["RampPlunge"]
        self.cam_op = self.operation["type"]
        self.direction = self.operation["Direction"]
        self.cutDepth = ValWithUnit(self.operation["Deep"], self.units)
        self.margin = ValWithUnit(self.operation["Margin"], self.units)
        
        # the input
        self.svg_paths : List[SvgPath] = [] # to fill at "setup"
        # the input "transformed"
        self.clipper_paths : List[List[ClipperLib.IntPoint]] = []
        
        # the resulting paths from the op combinaison setting + selected scg paths
        self.geometry = ClipperLib.PathVector()
        # and the resulting svg paths from the combinaison, to be displayed
        # in the svg viewer
        self.geometry_svg_paths : List[SvgPath] = []

        self.cam_paths = []

    def setup(self, svg_viewer: SvgViewer):
        '''
        '''
        for svg_path_id in self.operation["paths"]:

            svg_path_d = svg_viewer.get_svg_path_d(svg_path_id)
            svg_path = SvgPath(svg_path_id, {'d': svg_path_d})

            self.svg_paths.append(svg_path)
   
    def calculate_geometry(self):
        '''
        '''
        for svg_path in self.svg_paths:
            clipper_path = svg_path.toClipperPath()
            self.clipper_paths.append(clipper_path)

        clipType = {
            "Union": ClipperLib.ClipType.ctUnion,
            "Intersection": ClipperLib.ClipType.ctIntersection,
            "Difference": ClipperLib.ClipType.ctDifference,
            "Xor": ClipperLib.ClipType.ctXor,
        } [self.operation["Combine"]] 
        
        self.geometry = ClipperUtils.combine(self.clipper_paths, clipType)

        ClipperLib.dumpPaths("geometry", self.geometry)

        for clipper_path in self.geometry:
            svg_path = SvgPath.fromClipperPath(clipper_path)
            self.geometry_svg_paths.append(svg_path)

    def calculate_toolpaths(self,  svgModel: SvgModel, toolModel: ToolModel, materialModel: MaterialModel):
        '''
        '''
        toolData = toolModel.getCamData()

        name = self.name
        ramp = self.ramp
        cam_op = self.cam_op
        direction = self.direction
        cutDepth = self.cutDepth
        margin = self.margin

        geometry = self.geometry
        offset = margin.toInch() * ClipperUtils.inchToClipperScale
        if cam_op == "Pocket" or cam_op == "V Pocket" or cam_op == "Inside":
            offset = -offset
        if cam_op != "Engrave" and offset != 0:
            geometry = ClipperUtils.offset(geometry, offset)

        if cam_op == "Pocket":
            self.cam_paths = cam.pocket(geometry, toolData["diameterClipper"], 1 - toolData["stepover"], direction == "Climb")
        elif cam_op == "V Pocket":
            self.cam_paths = cam.vPocket(geometry, toolModel.angle, toolData["passDepthClipper"], cutDepth.toInch() * ClipperUtils.inchToClipperScale, toolData["stepover"], direction == "Climb")
        elif cam_op == "Inside" or cam_op == "Outside":
            width = width.toInch() * ClipperUtils.inchToClipperScale
            if width < toolData["passDepthClipper"]:
                width = toolData["passDepthClipper"]
            self.cam_paths = cam.outline(geometry, toolData["passDepthClipper"], cam_op == "Inside", width, 1 - toolData["stepover"], direction == "Climb")
        elif cam_op == "Engrave":
            self.cam_paths = cam.engrave(geometry, direction == "Climb")

        #path = ClipperUtils.getSnapPathFromClipperPaths(cam.getClipperPathsFromCamPaths(self.cam_paths), svgModel.pxPerInch)
        
        #if path != None and len(path):
        #    self.toolPathSvg = self.cam_pathsGroup.path(path).attr("class", "toolPath")


class JobModel:
    '''
    '''
    def __init__(self, 
            svg_viewer,
            cnc_ops: List[CncOp], 
            materialModel: MaterialModel, 
            svgModel: SvgModel, 
            toolModel: ToolModel,
            tabsModel: TabsModel):

        self.svg_viewer = svg_viewer
        
        self.operations = cnc_ops
        
        self.svgModel = svgModel
        self.materialModel = materialModel
        self.toolModel = toolModel
        self.tabsModel = tabsModel

        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0

        self.calculate_operation_cam_paths()
        self.findMinMax()

    def calculate_operation_cam_paths(self):
        for op in self.operations:
            if op.enabled :
                op.setup(self.svg_viewer)
                op.calculate_geometry()
                op.calculate_toolpaths(self.svgModel, self.toolModel, self.materialModel)
    
    def findMinMax(self):
        minX = 0
        maxX = 0
        minY = 0
        maxY = 0
        foundFirst = False

        for op in self.operations:
            if op.enabled and op.cam_paths != None :
                for cam_path in op.cam_paths:
                    toolPath = cam_path.path
                    for point in toolPath:
                        if not foundFirst:
                            minX = point.X
                            maxX = point.X
                            minY = point.Y
                            maxY = point.Y
                            foundFirst = True
                        else:
                            minX = min(minX, point.X)
                            minY = min(minY, point.Y)
                            maxX = max(maxX, point.X)
                            maxY = max(maxY, point.Y)
                        
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY

