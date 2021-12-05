# Copyright 2022 Xavier
#
# This file is part of pycut.
#
# pycut is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pycut is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pycut.  If not, see <http:#www.gnu.org/licenses/>.

import time
import math

from typing import List

import clipper.clipper as ClipperLib

import Snap

import cam
import clipper_utils

from pycut import ToolModel
from pycut import MaterialModel
from pycut import SvgModel


class Operation:
    '''
    '''
    def __init__(self, 
            svgViewModel : SvgModel, 
            materialViewModel : MaterialModel, 
            operationsViewModel : 'OperationsViewModel', 
            toolModel : ToolModel, 
            combinedGeometryGroup, 
            toolPathsGroup, 
            rawPaths, 
            toolPathsChanged, 
            loading):
        
        self.svgViewModel = svgViewModel
        self.materialViewModel = materialViewModel
        self.operationsViewModel = operationsViewModel
        self.toolModel = toolModel

        self.combinedGeometryGroup = combinedGeometryGroup
        self.toolPathsGroup = toolPathsGroup
        self.rawPaths = rawPaths
        self.toolPathsChanged = toolPathsChanged
        self.loading = loading

        self.units = self.materialViewModel.matUnits
        
        self.showDetail = False
        self.name = ""
        
        self.enabled = True
        self.ramp = False
        self.combineOp = "Union"
        self.camOp = "Pocket"
        self.direction = "Conventional"
        self.cutDepth = 0
        self.margin = 0.0
        self.width = 0.0

        self.combinedGeometry = []
        self.combinedGeometrySvg = None
        self.toolPaths = []
        self.toolPathSvg = None

        self.generatingToolpath = False

        self.cutDepth.fromInch(toolModel.passDepth.toInch())

    def toggleDetail(self):
        self.showDetail(not self.showDetail)

    def removeCombinedGeometrySvg(self):
        if self.combinedGeometrySvg:
            self.combinedGeometrySvg.remove()
            self.combinedGeometrySvg = None

    def removeToolPaths(self):
        if self.toolPathSvg:
            self.toolPathSvg.remove()
            self.toolPathSvg = None
            self.toolPaths = []

    def recombine(self):
        def alertMsg(msg):
            pass
            #showAlert(msg, "alert-warning")

        self.removeCombinedGeometrySvg()
        self.removeToolPaths()

        all = []
        for rawPath in self.rawPaths:
            geometry = clipper_utils.ClipperUtils.getClipperPathsFromSnapPath(rawPath, self.svgViewModel.pxPerInch, alertMsg)
            
            if geometry != None:
                if rawPath.nonzero:
                    fillRule = ClipperLib.PolyFillType.pftNonZero
                else:
                    fillRule = ClipperLib.PolyFillType.pftEvenOdd
                all.append(clipper_utils.ClipperUtils.simplifyAndClean(geometry, fillRule))

        if len(all) == 0:
            self.combinedGeometry = []
        else:
            self.combinedGeometry = all[0]
            clipType = ClipperLib.ClipType.ctUnion
            if self.combineOp() == "Intersect":
                clipType = ClipperLib.ClipType.ctIntersection
            elif self.combineOp() == "Diff":
                clipType = ClipperLib.ClipType.ctDifference
            elif self.combineOp() == "Xor":
                clipType = ClipperLib.ClipType.ctXor
            for item in all:
                self.combinedGeometry = clipper_utils.ClipperUtils.clip(self.combinedGeometry, item, clipType)

        previewGeometry = self.combinedGeometry

        if len(previewGeometry) != 0:
            offset = self.margin.toInch() * clipper_utils.ClipperUtils.inchToClipperScale
            if self.camOp == "Pocket" or self.camOp == "V Pocket" or self.camOp == "Inside":
                offset = -offset
            if self.camOp() != "Engrave" and offset != 0:
                previewGeometry = clipper_utils.ClipperUtils.offset(previewGeometry, offset)

            if self.camOp == "Inside" or self.camOp == "Outside" :
                toolCamArgs = self.toolModel.getCamArgs()
                if toolCamArgs != None:
                    width = self.width.toInch() * clipper_utils.ClipperUtils.inchToClipperScale
                    if width < toolCamArgs.diameterClipper:
                        width = toolCamArgs.diameterClipper
                    if self.camOp == "Inside":
                        previewGeometry = clipper_utils.ClipperUtils.diff(previewGeometry, clipper_utils.ClipperUtils.offset(previewGeometry, -width))
                    else:
                        previewGeometry = clipper_utils.ClipperUtils.diff(clipper_utils.ClipperUtils.offset(previewGeometry, width), previewGeometry)

        if len(previewGeometry) != 0:
            path = clipper_utils.ClipperUtils.getSnapPathFromClipperPaths(previewGeometry, self.svgViewModel.pxPerInch)
            if path != None:
                self.combinedGeometrySvg = self.combinedGeometryGroup.path(path).attr("class", "combinedGeometry")

        self.enabled(True)

    def generateToolPath(self):
        toolCamArgs = self.toolModel.getCamData()
        if toolCamArgs == None:
            return

        startTime = time.time()
        if self.options.profile:
            print("generateToolPath...")

        self.generatingToolpath = True
        self.removeToolPaths()

        geometry = self.combinedGeometry
        offset = self.margin.toInch() * clipper_utils.ClipperUtils.inchToClipperScale
        if self.camOp == "Pocket" or self.camOp == "V Pocket" or self.camOp == "Inside":
            offset = -offset
        if self.camOp != "Engrave" and offset != 0:
            geometry = clipper_utils.ClipperUtils.offset(geometry, offset)

        if self.camOp == "Pocket":
            self.toolPaths(cam.cam.pocket(geometry, toolCamArgs.diameterClipper, 1 - toolCamArgs.stepover, self.direction == "Climb"))
        elif self.camOp == "V Pocket":
            self.toolPaths(cam.cam.vPocket(geometry, self.toolModel.angle, toolCamArgs.passDepthClipper, self.cutDepth.toInch() * jscut.priv.path.inchToClipperScale, toolCamArgs.stepover, self.direction == "Climb"))
        elif self.camOp == "Inside" or self.camOp == "Outside":
            width = self.width.toInch() * clipper_utils.ClipperUtils.inchToClipperScale
            if width < toolCamArgs.diameterClipper:
                width = toolCamArgs.diameterClipper
            self.toolPaths(cam.cam.outline(geometry, toolCamArgs.diameterClipper, self.camOp() == "Inside", width, 1 - toolCamArgs.stepover, self.direction == "Climb"))
        elif self.camOp == "Engrave":
            self.toolPaths(cam.cam.engrave(geometry, self.direction() == "Climb"))

        path = clipper_utils.ClipperUtils.getSnapPathFromClipperPaths(cam.cam.getClipperPathsFromCamPaths(self.toolPaths()), self.svgViewModel.pxPerInch())
        if path != None and len(path):
            self.toolPathSvg = self.toolPathsGroup.path(path).attr("class", "toolPath")

        if self.options.profile:
            print("generateToolPath: " + (time.time() - startTime))

        self.enabled = True
        self.generatingToolpath = False
        self.toolPathsChanged()


class OperationsViewModel:
    '''
    '''
    def __init__(self, 
            svgViewModel: SvgModel, 
            materialViewModel: MaterialModel, 
            selectionViewModel : 'SelectionModel', 
            toolModel: ToolModel, 
            combinedGeometryGroup, 
            toolPathsGroup, 
            toolPathsChanged):

        self.svgViewModel = svgViewModel
        self.materialViewModel = materialViewModel
        self.selectionViewModel = selectionViewModel
        self.toolModel = toolModel

        self.combinedGeometryGroup = combinedGeometryGroup
        self.toolPathsGroup = toolPathsGroup
        self.toolPathsChanged = toolPathsChanged

        self.operations: List[Operation] = [] 
        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0

    def findMinMax(self):
        minX = 0
        maxX = 0
        minY = 0
        maxY = 0
        foundFirst = False

        for op in self.operations:
            if op.enabled and op.toolPaths != None :
                op_toolPaths = op.toolPaths
                for toolPath_ in op_toolPaths:
                    toolPath = toolPath_.path
                    for point in toolPath:
                        if not foundFirst:
                            minX = point.X
                            maxX = point.X
                            minY = point.Y
                            maxY = point.Y
                            foundFirst = True
                        else:
                            minX = math.min(minX, point.X)
                            minY = math.min(minY, point.Y)
                            maxX = math.max(maxX, point.X)
                            maxY = math.max(maxY, point.Y)
                        
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY

    def addOperation(self):
        rawPaths = []

        selection = self.selectionViewModel.getSelection()

        for element in selection:
            rawPaths.append({
                'path': Snap.parsePathString(element.attr('d')),
                'nonzero': element.attr("fill-rule") != "evenodd",
            })
        
        self.selectionViewModel.clearSelection()
        
        op = Operation(
                self.options, 
                self.svgViewModel, 
                self.materialViewModel, 
                self, 
                self.toolModel, 
                self.combinedGeometryGroup, 
                self.toolPathsGroup, 
                rawPaths, 
                self.toolPathsChanged, False)
        self.operations.append(op)

    def removeOperation(self, operation: Operation) :
        operation.removeCombinedGeometrySvg()
        operation.removeToolPaths()
        self.operations.remove(operation)

    def clickOnSvg(self, elem) :
        if elem.attr("class") == "combinedGeometry" or elem.attr("class") == "toolPath":
            return True
        return False