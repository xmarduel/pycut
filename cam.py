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
import sys

from typing import List
from typing import Dict

from val_with_unit import ValWithUnit

#import clipper_613 as ClipperLib
import clipper_642 as ClipperLib

import clipper_utils


class CamPath:
    '''
    CamPath has this format: {
      path:               Clipper path
      safeToClose:        Is it safe to close the path without retracting?
    }
    '''
    def __init__(self, path: ClipperLib.IntPointVector, safeToClose: bool = True):
        # clipper path
        self.path = path
        # is it safe to close the path without retracting?
        self.safeToClose = safeToClose


class cam:
    '''
    '''
    @staticmethod
    def dist(x1: float, y1: float, x2: float, y2: float) -> float :
        dx = x2 - x1
        dy = y2 - y1
        return dx * dx + dy * dy
    
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
        #ClipperLib.dumpPaths("geometry", geometry)

        current = clipper_utils.ClipperUtils.offset(geometry, -cutterDia / 2)

        if len(current) == 0:
            # cannot offset ! maybe geometry too narrow for the cutter
            return []

        bounds = clipper_utils.ClipperUtils.clone_pathvector(current)  # JSCUT: current.slice(0)
        allPaths : List[ClipperLib.IntPointVector] = []
        while len(current) != 0:
            if climb:
                for iv in current:
                    iv.reverse()
            allPaths = [p for p in current] + allPaths # JSCUT: current.concat(allPaths)
            current = clipper_utils.ClipperUtils.offset(current, -cutterDia * (1 - overlap))
            
        return cls.mergePaths(bounds, allPaths)

    @classmethod
    def outline(cls, geometry: ClipperLib.PathVector, cutterDia: float, isInside: bool, width: float, overlap: float, climb: bool) -> List[CamPath] :
        '''
        Compute paths for outline operation on Clipper geometry. 
        
        Returns array of CamPath.
        
        cutterDia and width are in Clipper units. 
        overlap is in the  range [0, 1).
        '''
        currentWidth = cutterDia
        allPaths  : List[ClipperLib.IntPointVector] = []
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
                reversed = []
                for path in current:
                    path_as_list = list(path)  # is a tuple!  JSCUT current reversed in place
                    path_as_list.reverse()
                    reversed.append(path_as_list)
                allPaths = reversed + allPaths  # JSCUT: allPaths = current.concat(allPaths)
            else:
                allPaths = [p for p in current] + allPaths  # JSCUT: allPaths = current.concat(allPaths)

            nextWidth = currentWidth + eachWidth
            if nextWidth > width and (width - currentWidth) > 0 :
                # >>> XAM fix
                last_delta = width - currentWidth
                if isInside:
                    last_delta = -last_delta
                # <<< XAM fix
                current = clipper_utils.ClipperUtils.offset(current, last_delta)
                if needReverse:
                    reversed = []
                    for path in current:
                        path_as_list = list(path)  # is a tuple!  JSCUT current reversed in place
                        path_as_list.reverse()
                        reversed.append(path_as_list)
                    allPaths = reversed + allPaths # JSCUT: allPaths = current.concat(allPaths)
                else:
                    allPaths = [p for p in current] + allPaths # JSCUT: allPaths = current.concat(allPaths)
                break
            
            currentWidth = nextWidth
            current = clipper_utils.ClipperUtils.offset(current, eachOffset)

        if len(allPaths) == 0: 
            # no possible paths! TODO . inform user
            return []

        return cls.mergePaths(bounds, allPaths)
        
    @classmethod
    def engrave(cls, geometry: ClipperLib.PathVector, climb: bool) -> List[CamPath] :
        '''
        Compute paths for engrave operation on Clipper geometry. 
        
        Returns array of CamPath.
        '''
        allPaths = []
        for xpath in geometry:
            path = clipper_utils.ClipperUtils.clone_intpointvector(xpath)  # JSCUT: path = paths.slice(0)
            if not climb:
                path.reverse()
            path.append(path[0])
            allPaths.append(path)
            
        campaths = cls.mergePaths(None, allPaths)
        for campath in campaths:
            campath.safeToClose = True
        return campaths

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
    def mergePaths(cls, _bounds: ClipperLib.PathVector, paths: List[ClipperLib.IntPointVector]) -> List[CamPath] :
        '''
        Try to merge paths. A merged path doesn't cross outside of bounds. 
        '''
        if _bounds and len(_bounds) > 0:
            bounds = _bounds
        else: 
            bounds = ClipperLib.PathVector()
 

        currentPath = list(paths[0]) # not as tuple, but as list
        
        pathEndPoint = currentPath[-1]
        pathStartPoint = currentPath[0]

        # close if start/end poitn not equal
        if pathEndPoint.X != pathStartPoint.X or pathEndPoint.Y != pathStartPoint.Y:
            currentPath.append(pathStartPoint)
        
        currentPoint = currentPath[-1]
        paths[0] = []

        mergedPaths : List[ClipperLib.IntPointVector] = [] 
        numLeft = len(paths) - 1

        while numLeft > 0 :
            closestPathIndex = None
            closestPointIndex = None
            closestPointDist = sys.maxsize
            for pathIndex, path in enumerate(paths):
                for pointIndex, point in enumerate(path):
                    dist = cam.distP(currentPoint, point)
                    if dist < closestPointDist:
                        closestPathIndex = pathIndex
                        closestPointIndex = pointIndex
                        closestPointDist = dist

            path = list(paths[closestPathIndex])
            paths[closestPathIndex] = []
            numLeft -= 1
            needNew = clipper_utils.ClipperUtils.crosses(bounds, currentPoint, path[closestPointIndex])

            # JSCUT path = path.slice(closestPointIndex, len(path)).concat(path.slice(0, closestPointIndex))
            path = path[closestPointIndex:] + path[:closestPointIndex]
            
            path.append(path[0])

            if needNew:
                mergedPaths.append(currentPath)
                currentPath = path
                currentPoint = currentPath[-1]
            else:
                currentPath = currentPath + path
                currentPoint = currentPath[-1]

        #ClipperLib.dumpPath("currentPath", currentPath)

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
    
    @classmethod
    def separateTabs(cls, origPath: ClipperLib.IntPointVector, tabs: List['Tab']) -> List[ClipperLib.IntPointVector]:
        '''
        from a "normal" tool path, split this path into a list of "partial" paths
        avoiding the tabs areas
        '''
        from pycut import Tab

        if len(tabs) == 0:
            return [origPath]

        clipper_path = ClipperLib.IntPointVector()
        for k, pt in enumerate(origPath):
            clipper_path.append(pt)

        print("origPath", origPath)
        print("origPath", clipper_path)
         
        clipper_paths = ClipperLib.PathVector()
        # 1. from the tabs, build clipper (closed) paths
        for tab_data in tabs:
            tab = Tab(tab_data)
            clipper_paths.append(tab.svg_path.toClipperPath())

        # 2. then "diff" the origin path with the tabs paths
        splitted_paths = clipper_utils.ClipperUtils.openpath_remove_tabs(clipper_path, clipper_paths)
        
        # 3. that's it
        print("splitted_paths", splitted_paths)

        paths = [list(path) for path in splitted_paths ]
        
        # >>> XAM merge some paths when possible (verflixt!)
        paths = cls.mergeCompatiblePaths(paths)
        # <<< XAM

        return paths

    @classmethod
    def mergeCompatiblePaths(cls, paths: List[ClipperLib.IntPointVector]):
        '''
        This is a post-processing step to clipper-6.4.2 where found seperated paths can be merged together,
        leading to less sepated paths
        '''
        # ------------------------------------------------------------------------------------------------
        def pathsAreCompatible(path1: ClipperLib.IntPointVector, path2: ClipperLib.IntPointVector) -> bool:
            '''
            test if the 2 paths have their end point/start point compatible (is the same)
            '''
            endPoint = path1[-1]
            startPoint = path2[0]

            if endPoint.X == startPoint.X and endPoint.Y == startPoint.Y:
                # can merge
                return True

            return False

        def mergePathIntoPath(path1: ClipperLib.IntPointVector, path2: ClipperLib.IntPointVector) -> bool:
            '''
            merge the 2 paths if their end point/start point are compatible (ie the same)
            '''
            endPoint = path1[-1]
            startPoint = path2[0]

            if endPoint.X == startPoint.X and endPoint.Y == startPoint.Y:
                # can merge
                path1 += path2[1:]
                return True

        def buildPathsCompatibilityTable(paths: List[ClipperLib.IntPointVector]) -> Dict[List,int]:
            '''
            for all paths in the list of paths, check first which ones can be merged
            '''
            compatibility_table = {}

            for i, path in enumerate(paths):
                for j, other_path in enumerate(paths):
                    if i == j:
                       continue
                    rc = pathsAreCompatible(path, other_path)
                    if rc:
                        if i in compatibility_table:
                            compatibility_table[i].append(j)
                        else: 
                            compatibility_table[i] = [j]
        
            return compatibility_table
        # ------------------------------------------------------------------------------------------------

        if len(paths) <= 1:
            return paths

        compatibility_table = buildPathsCompatibilityTable(paths)

        while len(compatibility_table) > 0:
            i = list(compatibility_table.keys())[0]
            path = paths[i]
            j = compatibility_table[i][0]
            path_to_be_merged = paths.pop(j)
            mergePathIntoPath(path, path_to_be_merged)
            compatibility_table = buildPathsCompatibilityTable(paths)

        return paths


    @classmethod
    def getGcode(cls, args):
        '''
        Convert paths to gcode. getGcode() assumes that the current Z position is at safeZ.
        getGcode()'s gcode returns Z to this position at the end.
        args must have:
          paths:          Array of CamPath
          ramp:           Ramp these paths?
          scale:          Factor to convert Clipper units to gcode units
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
          tabs:           List of tabs
          tabZ:           Level below which tabs are to be processed
        '''
        paths : List[CamPath] = args["paths"]
        ramp = args["ramp"]
        scale = args["scale"]
        offsetX = args["offsetX"]
        offsetY = args["offsetY"]
        decimal = args["decimal"]
        topZ = args["topZ"]
        botZ = args["botZ"]
        safeZ = args["safeZ"]
        passDepth = args["passDepth"]
        
        plungeFeedGcode = ' F%d' % args["plungeFeed"]
        retractFeedGcode = ' F%d' % args["retractFeed"]
        cutFeedGcode = ' F%d' % args["cutFeed"]
        rapidFeedGcode = ' F%d' % args["rapidFeed"]

        plungeFeed = args["plungeFeed"]
        retractFeed = args["retractFeed"]
        cutFeed = args["cutFeed"]
        rapidFeed = args["rapidFeed"]

        tabs = args["tabs"]
        tabZ = args["tabZ"]

        gcode = ""

        retractGcode = '; Retract\r\n' + \
            f'G1 Z' + safeZ.toFixed(decimal) + f'{rapidFeedGcode}\r\n'

        retractForTabGcode = '; Retract for tab\r\n' + \
            f'G1 Z' + tabZ.toFixed(decimal) + f'{rapidFeedGcode}\r\n'

        def getX(p: ClipperLib.IntPoint) :
            return p.X * scale + offsetX

        def getY(p : ClipperLib.IntPoint):
            return -p.Y * scale + offsetY

        def convertPoint(p: ClipperLib.IntPoint):
            result = ' X' + ValWithUnit(p.X * scale + offsetX, "-").toFixed(decimal) +  \
                     ' Y' + ValWithUnit(-p.Y * scale + offsetY, "-").toFixed(decimal)
            return result

        hasTabs = len(tabs) > 0

        for pathIndex, path in enumerate(paths):
            origPath = path.path
            if len(origPath) == 0:
                continue

            # split the path to cut into many partials paths to avoid tabs eraas
            separatedPaths = cls.separateTabs(origPath, tabs)

            gcode += \
                f'\r\n' + \
                f'; Path {pathIndex}\r\n'

            currentZ = safeZ
            finishedZ = topZ

            # need to cut at tabZ if tabs there
            exactTabZLevelDone = False

            while finishedZ > botZ:
                nextZ = max(finishedZ - passDepth, botZ)

                if hasTabs:
                    if nextZ == tabZ:
                        exactTabZLevelDone = True
                    elif nextZ < tabZ:
                        # a last cut at the exact tab height withput tabs 
                        if exactTabZLevelDone == False:
                            nextZ = tabZ
                            exactTabZLevelDone = True


                if (currentZ < safeZ and ((not path.safeToClose) or len(tabs) > 0)) :
                    gcode += retractGcode
                    currentZ = safeZ

                # check this - what does it mean ???
                if not hasTabs:
                    currentZ = finishedZ
                else:
                    currentZ = max(finishedZ, tabZ)
                
                gcode += '; Rapid to initial position\r\n' + \
                    'G1' + convertPoint(origPath[0]) + rapidFeedGcode + '\r\n'

                inTabsHeight = False
                
                if not hasTabs:
                    inTabsHeight = False
                    selectedPaths = [origPath]
                    gcode += 'G1 Z' + ValWithUnit(currentZ, "-").toFixed(decimal) + '\r\n'
                else:
                    if nextZ >= tabZ:
                        inTabsHeight = False
                        selectedPaths = [origPath]
                        gcode += 'G1 Z' + ValWithUnit(currentZ, "-").toFixed(decimal) + '\r\n'
                    else:
                        inTabsHeight = True
                        selectedPaths = separatedPaths

                for selectedPath in selectedPaths:
                    if len(selectedPath) == 0:
                        continue

                    executedRamp = False
                    if ramp:
                        minPlungeTime = (currentZ - nextZ) / plungeFeed
                        idealDist = cutFeed * minPlungeTime
                        totalDist = 0
                        for end in range(1, len(selectedPath)):
                            if totalDist > idealDist:
                                break

                            pt1 = selectedPath[end - 1]
                            pt2 = selectedPath[end]
                            totalDist += 2 * cam.dist(getX(pt1), getY(pt1), getX(pt2), getY(pt2))
                                
                        if totalDist > 0:
                            gcode += '; ramp\r\n'
                            executedRamp = True
                                    
                            #rampPath = selectedPath.slice(0, end)
                            rampPath = [ selectedPath[k] for k in range(0,end) ] 

                            #rampPathEnd = selectedPath.slice(0, end - 1).reverse()
                            rampPathEnd = [ selectedPath[k] for k in range(0,end-1) ]
                            rampPathEnd.reverse()

                            rampPath = rampPath + rampPathEnd
                                
                            distTravelled = 0
                            for i in range(1,len(rampPath)):
                                distTravelled += cam.dist(getX(rampPath[i - 1]), getY(rampPath[i - 1]), getX(rampPath[i]), getY(rampPath[i]))
                                newZ = currentZ + distTravelled / totalDist * (nextZ - currentZ)
                                gcode += 'G1' + convertPoint(rampPath[i]) + ' Z' + ValWithUnit(newZ, "-").toFixed(decimal)
                                if i == 1:
                                    gcode += ' F' + ValWithUnit(min(totalDist / minPlungeTime, cutFeed), "-").toFixed(decimal) + '\r\n'
                                else:
                                    gcode += '\r\n' 

                    if not inTabsHeight:
                        if not executedRamp:
                            gcode += \
                                '; plunge\r\n' + \
                                'G1 Z' + ValWithUnit(nextZ, "-").toFixed(decimal) + plungeFeedGcode + '\r\n'

                    if inTabsHeight:
                        # move to initial point of partial path
                        gcode += '; with Tabs: move to first point of partial path at safe height \r\n'
                        gcode += 'G1' + convertPoint(selectedPath[0]) + '\r\n'
                        gcode += \
                            '; plunge\r\n' + \
                            'G1 Z' + ValWithUnit(nextZ, "-").toFixed(decimal) + plungeFeedGcode + '\r\n'

                    currentZ = nextZ

                    gcode += '; cut\r\n'

                    # on a given height, generate series of G1
                    for i in range(1, len(selectedPath)):
                        point = selectedPath[i]
                        gcode += 'G1' + convertPoint(point)
                        if i == 1:
                            gcode += cutFeedGcode + '\r\n'
                        else:
                            gcode += '\r\n'
                    
                    if inTabsHeight:
                        # retract to safeZ before processing next separatedPath
                        gcode += retractGcode

                finishedZ = nextZ
            
            gcode += retractGcode

        return gcode