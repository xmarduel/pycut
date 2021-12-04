# Copyright 2014 Xavier
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

import math

from typing import List

import clipper_utils
import clipper.clipper as ClipperLib


class CamPath:
    '''
    CamPath has this format: {
      path:               Clipper path
      safeToClose:        Is it safe to close the path without retracting?
    }
    '''
    def __init__(self, path: ClipperLib.PathVector, safeToClose: bool = True):
        # clipper path
        self.path = path
        # is it safe to close the path without retracting?
        self.safeToClase = safeToClose


class cam:
    '''
    '''
    @staticmethod
    def dist(x1: float, y1: float, x2: float, y2: float) -> float :
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx *dx + dy * dy)
    
    @staticmethod
    def distP(p1:ClipperLib.IntPoint, p2:ClipperLib.IntPoint) -> float :
        return cam.dist(p1.X, p1.Y, p2.X, p2.Y)

    @classmethod
    def pocket(cls, geometry: ClipperLib.PathVector, cutterDia: float, overlap: float, climb: bool) -> List[CamPath] :
        '''
        Compute paths for pocket operation on Clipper geometry. 
        
        Returns array of CamPath.
        
        cutterDia is in Clipper units. 
        overlap is in the range [0, 1).
        '''
        current = clipper_utils.ClipperUtils.offset(geometry, -cutterDia / 2)
        bounds = current.slice(0)
        allPaths = []
        while len(current) != 0:
            if climb:
                for i in range(len(current)):
                    current[i].reverse()
            allPaths = current.concat(allPaths)
            current = clipper_utils.ClipperUtils.offset(current, -cutterDia * (1 - overlap))
         
        return cls.mergePaths(bounds, allPaths)

    @classmethod
    def hspocket(cls, geometry: ClipperLib.PathVector, cutterDia: float, overlap: float, climb: bool) -> List[CamPath] :
        '''
        Compute paths for pocket operation on Clipper geometry. 
        
        Returns array of CamPath. 
        
        cutterDia is in Clipper units. 
        overlap is in the range [0, 1).
        '''
        
        return []
        '''
        memoryBlocks = []

        cGeometry = jscut.priv.path.convertPathsToCpp(memoryBlocks, geometry)

        resultPathsRef = Module._malloc(4)
        resultNumPathsRef = Module._malloc(4)
        resultPathSizesRef = Module._malloc(4)
        memoryBlocks.push(resultPathsRef)
        memoryBlocks.push(resultNumPathsRef)
        memoryBlocks.push(resultPathSizesRef)

        #extern "C" void hspocket(
        #    double** paths, int numPaths, int* pathSizes, double cutterDia,
        #    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes)
        Module.ccall(
            'hspocket',
            'void', ['number', 'number', 'number', 'number', 'number', 'number', 'number'],
            [cGeometry[0], cGeometry[1], cGeometry[2], cutterDia, resultPathsRef, resultNumPathsRef, resultPathSizesRef]);self

        result = jscut.priv.path.convertPathsFromCppToCamPath(memoryBlocks, resultPathsRef, resultNumPathsRef, resultPathSizesRef);

        for i in range(len(memoryBlocks)):
            Module._free(memoryBlocks[i])

        return result
        '''

    @classmethod
    def outline(cls, geometry: ClipperLib.PathVector, cutterDia: float, isInside: bool, width: float, overlap: float, climb: bool) -> List[CamPath] :
        '''
        Compute paths for outline operation on Clipper geometry. 
        
        Returns array of CamPath.
        
        cutterDia and width are in Clipper units. 
        overlap is in the  range [0, 1).
        '''
        currentWidth = cutterDia
        allPaths = []
        eachWidth = cutterDia * (1 - overlap)

        if isInside :
            current = clipper_utils.ClipperUtils.offset(geometry, -cutterDia / 2)
            bounds = clipper_utils.ClipperUtils.diff(current, clipper_utils.ClipperUtils.offset(geometry, -(width - cutterDia / 2)))
            eachOffset = -eachWidth
            needReverse = climb
        else :
            current = clipper_utils.ClipperUtils.offset(geometry, cutterDia / 2)
            bounds = clipper_utils.ClipperUtils.diff(clipper_utils.ClipperUtils.offset(geometry, width - cutterDia / 2), current)
            eachOffset = eachWidth
            needReverse = not climb

        while currentWidth <= width :
            if needReverse:
                for i in range(len(current)):
                    current[i].reverse()
            allPaths = current.concat(allPaths)
            nextWidth = currentWidth + eachWidth
            if nextWidth > width and width - currentWidth > 0 :
                current = clipper_utils.ClipperUtils.offset(current, width - currentWidth)
                if needReverse:
                    for i in range(len(current)):
                        current[i].reverse()
                allPaths = current.concat(allPaths)
                break
            
            currentWidth = nextWidth
            current = clipper_utils.ClipperUtils.offset(current, eachOffset)
        
        return cls.mergePaths(bounds, allPaths)
        
    @classmethod
    def engrave(cls, geometry: ClipperLib.PathVector, climb: bool) -> List[CamPath] :
        '''
        Compute paths for engrave operation on Clipper geometry. 
        
        Returns array of CamPath.
        '''
        allPaths = []
        for paths in geometry:
            path = paths.slice(0)
            if not climb:
                path.reverse()
            path.append(path[0])
            allPaths.append(path)
            
        campaths = cls.mergePaths(None, allPaths)
        for campath in campaths:
            campath.safeToClose = True
        return campaths

    @classmethod
    def vPocket(cls, geometry: ClipperLib.PathVector, cutterAngle:float, passDepth:float, maxDepth: float) -> List[CamPath] :
        if cutterAngle <= 0 or cutterAngle >= 180:
            return []

        return []
        '''
        memoryBlocks = []

        cGeometry = clipper_utils.ClipperUtils.convertPathsToCpp(memoryBlocks, geometry)

        resultPathsRef = Module._malloc(4);
        resultNumPathsRef = Module._malloc(4);
        resultPathSizesRef = Module._malloc(4);
        memoryBlocks.append(resultPathsRef);
        memoryBlocks.append(resultNumPathsRef);
        memoryBlocks.append(resultPathSizesRef);

        #extern "C" void vPocket(
        #    int debugArg0, int debugArg1,
        #    double** paths, int numPaths, int* pathSizes,
        #    double cutterAngle, double passDepth, double maxDepth,
        #    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes)self, self, 
        Module.ccall(
            'vPocket',
            'void', ['number', 'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number'],
            [miscViewModel.debugArg0(), miscViewModel.debugArg1(), cGeometry[0], cGeometry[1], cGeometry[2], cutterAngle, passDepth, maxDepth, resultPathsRef, resultNumPathsRef, resultPathSizesRef]);

        result = jscut.priv.path.convertPathsFromCppToCamPath(memoryBlocks, resultPathsRef, resultNumPathsRef, resultPathSizesRef)

        for memoryBlock in memoryBlocks:
            Module._free(memoryBlock)

        return result
        '''

    @classmethod
    def mergePaths(cls, bounds: ClipperLib.PathVector, paths: ClipperLib.PathVector) -> List[CamPath] :
        '''
        Try to merge paths. A merged path doesn't cross outside of bounds. 
        
        Returns array of CamPath.
        '''
        if len(paths) == 0:
            return None

        currentPath = paths[0]
        currentPath.append(currentPath[0])
        currentPoint = currentPath[-1]
        paths[0] = []

        mergedPaths : ClipperLib.PathVector = [] 
        numLeft = len(paths) - 1

        while numLeft > 0 :
            closestPathIndex = None
            closestPointIndex = None
            closestPointDist = None
            for pathIndex, path in enumerate(paths):
                for pointIndex, point in enumerate(path):
                    dist = cam.distP(currentPoint, point)
                    if closestPointDist == None or dist < closestPointDist:
                        closestPathIndex = pathIndex
                        closestPointIndex = pointIndex
                        closestPointDist = dist

            path = paths[closestPathIndex]
            paths[closestPathIndex] = []
            numLeft -= 1
            needNew = clipper_utils.ClipperUtils.crosses(bounds, currentPoint, path[closestPointIndex])
            path = path.slice(closestPointIndex, len(path)).concat(path.slice(0, closestPointIndex))
            path.append(path[0])

            if needNew:
                mergedPaths.append(currentPath)
                currentPath = path
                currentPoint = currentPath[-1]
            else:
                currentPath = currentPath + [path]
                currentPoint = currentPath[-1]

        mergedPaths.append(currentPath)

        camPaths : List[CamPath] = []
        for path in mergedPaths:
            safeToClose = not clipper_utils.ClipperUtils.crosses(bounds, path[0], path[-1])
            camPaths.append( CamPath(path, safeToClose) )

        return camPaths

    @classmethod
    def getClipperPathsFromCamPaths(cls, cam_paths) :
        '''
        Convert array of CamPath to array of Clipper path
        '''
        result = []
        for cam_path in cam_paths:
            result.append(cam_path.path)
        return result
    

    displayedCppTabError1 = False
    displayedCppTabError2 = False

    @classmethod
    def separateTabs(cls, cutterPath, tabGeometry):
        '''
        '''
        if len(tabGeometry) == 0:
            return [cutterPath]
        '''
        if typeof Module == 'undefined':
            if not displayedCppTabError1:
                showAlert("Failed to load cam-cpp.js; tabs will be missing. This message will not repeat.", "alert-danger", False)
                displayedCppTabError1 = True
            
            return cutterPath

        memoryBlocks = []

        cCutterPath = jscut.priv.path.convertPathsToCpp(memoryBlocks, [cutterPath]);
        cTabGeometry = jscut.priv.path.convertPathsToCpp(memoryBlocks, tabGeometry);

        errorRef = Module._malloc(4);
        resultPathsRef = Module._malloc(4);
        resultNumPathsRef = Module._malloc(4);
        resultPathSizesRef = Module._malloc(4);
        memoryBlocks.append(errorRef);
        memoryBlocks.append(resultPathsRef);
        memoryBlocks.append(resultNumPathsRef);
        memoryBlocks.append(resultPathSizesRef);

        #extern "C" void separateTabs(
        #    double** pathPolygons, int numPaths, int* pathSizes,
        #    double** tabPolygons, int numTabPolygons, int* tabPolygonSizes,
        #    bool& error,
        #    double**& resultPaths, int& resultNumPaths, int*& resultPathSizes)
        Module.ccall(
            'separateTabs',
            'void', ['number', 'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number'],
            [cCutterPath[0], cCutterPath[1], cCutterPath[2], cTabGeometry[0], cTabGeometry[1], cTabGeometry[2], errorRef, resultPathsRef, resultNumPathsRef, resultPathSizesRef]);

        if Module.HEAPU32[errorRef >> 2] and  not displayedCppTabError2:
            showAlert("Internal error processing tabs; tabs will be missing. This message will not repeat.", "alert-danger", False)
            displayedCppTabError2 = True

        result = jscut.priv.path.convertPathsFromCpp(memoryBlocks, resultPathsRef, resultNumPathsRef, resultPathSizesRef)

        for memoryBlock in memoryBlocks:
            Module._free(memoryBlock)

        return result
        '''



    @classmethod
    def getGcode(cls, args):
        '''
        Convert paths to gcode. getGcode() assumes that the current Z position is at safeZ.
        getGcode()'s gcode returns Z to this position at the end.
        args must have:
          paths:          Array of CamPath
          ramp:           Ramp these paths?
          scale:          Factor to convert Clipper units to gcode units
          useZ:           Use Z coordinates in paths? (optional, defaults to False)
          offsetX:        Offset X (gcode units)
          offsetY:        Offset Y (gcode units)
          decimal:        Number of decimal places to keep in gcode
          topZ:           Top of area to cut (gcode units)
          botZ:           Bottom of area to cut (gcode units)
          safeZ:          Z position to safely move over uncut areas (gcode units)
          passDepth:      Cut depth for each pass (gcode units)
          plungeFeed:     Feedrate to plunge cutter (gcode units)
          retractFeed:    Feedrate to retract cutter (gcode units)
          cutFeed:        Feedrate for horizontal cuts (gcode units)
          rapidFeed:      Feedrate for rapid moves (gcode units)
          tabGeometry:    Tab geometry (optional)
          tabZ:           Z position over tabs (required if tabGeometry is not empty) (gcode units)
        '''
        paths : List[CamPath] = args["paths"]
        ramp = args["ramp"]
        scale = args["scale"]
        useZ = args["useZ"]
        offsetX = args["offsetX"]
        offsetY = args["offsetY"]
        decimal = args["decimal"]
        topZ = args["topZ"]
        botZ = args["botZ"]
        safeZ = args["safeZ"]
        passDepth = args["passDepth"]
        
        plungeFeedGcode = ' F' + args["plungeFeed"]
        retractFeedGcode = ' F' + args["retractFeed"]
        cutFeedGcode = ' F' + args["cutFeed"]
        rapidFeedGcode = ' F' + args["rapidFeed"]

        plungeFeed = ' F' + args["plungeFeed"]
        retractFeed = ' F' + args["retractFeed"]
        cutFeed = ' F' + args["cutFeed"]
        rapidFeed = ' F' + args["rapidFeed"]

        tabGeometry = args["tabGeometry"]
        tabZ = args["tabZ"]

        if useZ == None:
            useZ = False

        if tabGeometry == None or tabZ <= botZ:
            tabGeometry = []
            tabZ = botZ

        gcode = ""

        retractGcode = '; Retract\r\n' + \
            'G1 Z' + safeZ.toFixed(decimal) + rapidFeedGcode + '\r\n'

        retractForTabGcode = '; Retract for tab\r\n' + \
            'G1 Z' + tabZ.toFixed(decimal) + rapidFeedGcode + '\r\n'

        def getX(p: ClipperLib.IntPoint) :
            return p.X * scale + offsetX

        def getY(p : ClipperLib.IntPoint):
            return -p.Y * scale + offsetY

        def convertPoint(p: ClipperLib.IntPoint):
            result = ' X' + (p.X * scale + offsetX).toFixed(decimal) + ' Y' + (-p.Y * scale + offsetY).toFixed(decimal)
            if useZ:
                result += ' Z' + (p.Z * scale + topZ).toFixed(decimal)
            return result

        for pathIndex, path in enumerate(paths):
            origPath = path.path
            if len(origPath) == 0:
                continue
            separatedPaths = cls.separateTabs(origPath, tabGeometry)

            gcode += \
                '\r\n' + \
                '; Path ' + pathIndex + '\r\n'

            currentZ = safeZ
            finishedZ = topZ
            while finishedZ > botZ:
                nextZ = math.max(finishedZ - passDepth, botZ)
                if (currentZ < safeZ and ((not path.safeToClose) or tabGeometry.length > 0)) :
                    gcode += retractGcode
                    currentZ = safeZ

                if len(tabGeometry)== 0:
                    currentZ = finishedZ
                else:
                    currentZ = math.max(finishedZ, tabZ)
                
                gcode += '; Rapid to initial position\r\n' + \
                    'G1' + convertPoint(origPath[0]) + rapidFeedGcode + '\r\n' + \
                    'G1 Z' + currentZ.toFixed(decimal) + '\r\n'

                if nextZ >= tabZ or useZ:
                    selectedPaths = [origPath]
                else:
                    selectedPaths = separatedPaths

                for selectedIndex, selectedPath in enumerate(selectedPaths):
                    if len(selectedPath) == 0:
                        continue

                    if not useZ:
                        if selectedIndex & 1:
                            selectedZ = tabZ
                        else:
                            selectedZ = nextZ

                        if selectedZ < currentZ:
                            executedRamp = False
                            if ramp:
                                minPlungeTime = (currentZ - selectedZ) / plungeFeed
                                idealDist = cutFeed * minPlungeTime
                                totalDist = 0
                                for end in range(1, len(selectedPath)):
                                    if totalDist > idealDist:
                                        break

                                    pt1 = selectedPath[end - 1]
                                    pt2 = selectedPath[end]
                                    totalDist += 2 * cam.distP(pt1, pt2)
                                
                                if totalDist > 0:
                                    gcode += '; ramp\r\n'
                                    executedRamp = True
                                    rampPath = selectedPath.slice(0, end).concat(selectedPath.slice(0, end - 1).reverse())
                                    distTravelled = 0
                                    for i in range(1,len(rampPath)):
                                        distTravelled += cam.dist(getX(rampPath[i - 1]), getY(rampPath[i - 1]), getX(rampPath[i]), getY(rampPath[i]))
                                        newZ = currentZ + distTravelled / totalDist * (selectedZ - currentZ)
                                        gcode += 'G1' + convertPoint(rampPath[i]) + ' Z' + newZ.toFixed(decimal)
                                        if i == 1:
                                            gcode += ' F' + math.min(totalDist / minPlungeTime, cutFeed).toFixed(decimal) + '\r\n'
                                        else:
                                            gcode += '\r\n' 

                            if not executedRamp:
                                gcode += \
                                    '; plunge\r\n' + \
                                    'G1 Z' + selectedZ.toFixed(decimal) + plungeFeedGcode + '\r\n'
                        elif selectedZ > currentZ:
                            gcode += retractForTabGcode
                        
                        currentZ = selectedZ

                    gcode += '; cut\r\n'

                    for point in selectedPath:
                        gcode += 'G1' + convertPoint(point)
                        if i == 1:
                            gcode += cutFeedGcode + '\r\n'
                        else:
                            gcode += '\r\n'

                finishedZ = nextZ
                if useZ:
                    break
            
            gcode += retractGcode

        return gcode
