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

import sys

from typing import List
from typing import Dict
from typing import Tuple

from val_with_unit import ValWithUnit

import shapely.geometry
import shapely.ops
from shapely_utils import ShapelyUtils


class CamPath:
    '''
    CamPath has this format: {
      path:               Shapely path
      safeToClose:        Is it safe to close the path without retracting?
    }
    '''
    def __init__(self, path: shapely.geometry.LineString, safeToClose: bool = True):
        # shapely path
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
    def distP(p1:Tuple[int,int], p2:Tuple[int,int]) -> float :
        return cam.dist(p1[0], p1[1], p2[0], p2[1])

    @classmethod
    def pocket(cls, geometry: shapely.geometry.MultiPolygon, cutterDia: float, overlap: float, climb: bool) -> List[CamPath] :
        '''
        Compute paths for pocket operation on Shapely geometry. 
        
        Returns array of CamPath.
        
        cutterDia is in "UserUnit" units. 
        overlap is in the range [0, 1).
        '''
        print("pocketing ", geometry)
        
        # use polygons exteriors lines - offset them and and diff with the interiors if any
        geometry = ShapelyUtils.orientMultiPolygon(geometry)

        ShapelyUtils.MatplotlibDisplay("geom pocket init", geometry)

        # the exterior
        multi_offset = ShapelyUtils.offsetMultiPolygon(geometry, cutterDia / 2, 'left', ginterior=True)

        #for offset in multi_offset:
        #    ShapelyUtils.MatplotlibDisplay("first_offset", offset)
        
        current = ShapelyUtils.offsetMultiPolygonAsMultiPolygon(geometry, cutterDia / 2, 'left', ginterior=True)
        current = ShapelyUtils.simplifyMultiPoly(current, 0.001)
        current = ShapelyUtils.orientMultiPolygon(current)

        for geom in current.geoms:
            ShapelyUtils.MatplotlibDisplay("geom pocket init after simplify", geom)

        print("pocketing - initial offset dia/2", current)

        if not current:
            return []
            
        if len(current.geoms) == 0:
            # cannot offset ! maybe geometry too narrow for the cutter
            return []

        bounds = geometry

        allPaths : List[shapely.geometry.LineString] = []

        # -------------------------------------------------------------
        def collect_paths(multi_offset, allPaths):
            lines_ok = []
            
            for offset in multi_offset:
                if offset.geom_type == 'LineString':
                    if len(list(offset.coords)) > 0:
                        lines_ok.append(offset)

                    print("---- SIMPLIFY #nb pts = ", len(list(offset.coords)))
                    print("---- SIMPLIFY len = ", offset.length)

                if offset.geom_type == 'MultiLineString':
                    for geom in offset.geoms:
                        if geom.geom_type == 'LineString':
                            if len(list(geom.coords)) > 0:
                                lines_ok.append(geom)

                            print("---- SIMPLIFY #nb pts = ", len(list(geom.coords)))
                            print("---- SIMPLIFY len = ", geom.length)

            allPaths = lines_ok + allPaths

            return allPaths
        # -------------------------------------------------------------

        while True:
            #if climb:
            #    for line in current:
            #        line.reverse()

            allPaths = collect_paths(multi_offset, allPaths)

            multi_offset = ShapelyUtils.offsetMultiPolygon(current, cutterDia * (1 - overlap), 'left')
            current = ShapelyUtils.offsetMultiPolygonAsMultiPolygon(current, cutterDia * (1 - overlap), 'left')
            if not current:
                allPaths = collect_paths(multi_offset, allPaths)
                break
            current = ShapelyUtils.simplifyMultiPoly(current, 0.001)
            if not current:
                allPaths = collect_paths(multi_offset, allPaths)
                break
            current = ShapelyUtils.orientMultiPolygon(current)
           
            if not multi_offset:
                break
            
        #for path in allPaths:
        #    ShapelyUtils.MatplotlibDisplay("final path", path)

        return cls.mergePaths(bounds, allPaths)

    @classmethod
    def outline(cls, geometry: shapely.geometry.MultiPolygon, cutterDia: float, isInside: bool, width: float, overlap: float, climb: bool) -> List[CamPath] :
        '''
        Compute paths for outline operation on Shapely geometry. 
        
        Returns array of CamPath.
        
        cutterDia and width are in Shapely units. 
        overlap is in the  range [0, 1).
        '''
        print("INITIAL geometry")
        print(geometry)

        # use lines, not polygons
        multiline = ShapelyUtils.multiPolyToMultiLine(geometry)
        print("INITIAL multiline")
        print(multiline)

        currentWidth = cutterDia
        allPaths  : List[shapely.geometry.LineString] = []
        eachWidth = cutterDia * (1 - overlap)

        if isInside :
            # because we always start from the outer ring -> we go "inside"
            current = ShapelyUtils.offsetMultiLine(multiline, cutterDia /2, 'left')
            offset = ShapelyUtils.offsetMultiLine(multiline, width - cutterDia / 2, 'left')
            #bounds = ShapelyUtils.diff(current, offset)
            bounds = current
            eachOffset = eachWidth
            needReverse = climb
        else :
            direction = "inner2outer"
            #direction = "outer2inner"

            if direction == "inner2outer":
                # because we always start from the inner ring -> we go "outside"
                current = ShapelyUtils.offsetMultiLine(multiline, cutterDia /2, 'right')
                offset = ShapelyUtils.offsetMultiLine(multiline, width - cutterDia / 2, 'right')
                #bounds = ShapelyUtils.diff(current, offset)
                bounds = current
            else:
                # because we always start from the outer ring -> we go "inside"
                current = ShapelyUtils.offsetMultiLine(multiline, cutterDia /2, 'left')
                offset = ShapelyUtils.offsetMultiLine(multiline, width - cutterDia / 2, 'left')
                #bounds = ShapelyUtils.diff(current, offset)
                bounds = current

            eachOffset = eachWidth
            needReverse = not climb

            # TEST
            #allPaths = [p for p in current.geoms] 

        while True and currentWidth <= width :
            if needReverse:
                reversed = []
                for path in current.geoms:
                    coords = list(path.coords)  # is a tuple!  JSCUT current reversed in place
                    coords.reverse()
                    reversed.append(shapely.geometry.LineString(coords))
                allPaths = reversed + allPaths  # JSCUT: allPaths = current.concat(allPaths)
            else:
                allPaths = [p for p in current.geoms] + allPaths  # JSCUT: allPaths = current.concat(allPaths)

            nextWidth = currentWidth + eachWidth
            if nextWidth > width and (width - currentWidth) > 0 :
                # >>> XAM fix
                last_delta = width - currentWidth
                # <<< XAM fix
                current = ShapelyUtils.offsetMultiLine(current, last_delta, 'left')
                if current :
                    current = ShapelyUtils.simplifyMultiLine(current, 0.01)
                
                if current:
                    if needReverse:
                        reversed = []
                        for path in current.geoms:
                            coords = list(path.coords)  # is a tuple!  JSCUT current reversed in place
                            coords.reverse()
                            reversed.append(shapely.geometry.LineString(coords))
                        allPaths = reversed + allPaths # JSCUT: allPaths = current.concat(allPaths)
                    else:
                        allPaths = [p for p in current.geoms] + allPaths # JSCUT: allPaths = current.concat(allPaths)
                    break
            
            currentWidth = nextWidth

            if not current:
                break

            current = ShapelyUtils.offsetMultiLine(current, eachOffset, 'left', resolution=16)
            if current:
                current = ShapelyUtils.simplifyMultiLine(current, 0.01)
                print("--- next toolpath")
                print(current)
            else:
                break

        if len(allPaths) == 0: 
            # no possible paths! TODO . inform user
            return []

        return cls.mergePaths(bounds, allPaths)
        
    @classmethod
    def engrave(cls, geometry: shapely.geometry.MultiPolygon, climb: bool) -> List[CamPath] :
        '''
        Compute paths for engrave operation on Shapely geometry. 
        
        Returns array of CamPath.
        '''
        # use lines, not polygons
        multiline = ShapelyUtils.multiPolyToMultiLine(geometry)
        print("INITIAL multiline")
        print(multiline)

        full_line = shapely.ops.linemerge(list(multiline.geoms))

        if full_line.geom_type == 'LineString':
            camPaths = [ CamPath( full_line, False) ]
            return camPaths

        allPaths = []
        for line in full_line:
            coords = list(line.coords)  # JSCUT: path = paths.slice(0)
            if not climb:
                coords.reverse()
        
            coords.append(coords[0])
            allPaths.append(shapely.geometry.LineString(coords))
            
        camPaths = [ CamPath(path, False)  for path in allPaths ]
        return camPaths

    @classmethod
    def mergePaths(cls, _bounds: shapely.geometry.MultiPolygon, paths: List[shapely.geometry.LineString]) -> List[CamPath] :
        '''
        Try to merge paths. A merged path doesn't cross outside of bounds. 
        '''
        if _bounds and len(_bounds.geoms) > 0:
            bounds = _bounds
        else: 
            bounds = shapely.geometry.MultiPolygon()
 

        # std list
        thepaths = [ list(path.coords) for path in paths ]
        paths = thepaths

        currentPath = paths[0]
        
        pathEndPoint = currentPath[-1]
        pathStartPoint = currentPath[0]

        # close if start/end point not equal
        if pathEndPoint[0] != pathStartPoint[0] or pathEndPoint[1] != pathStartPoint[1]:
            currentPath = currentPath + [pathStartPoint]
        
        currentPoint = currentPath[-1]
        paths[0] = [] # empty

        mergedPaths : List[shapely.geometry.LineString] = [] 
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

            path = paths[closestPathIndex]
            paths[closestPathIndex] = [] # empty
            numLeft -= 1
            needNew = ShapelyUtils.crosses(bounds, currentPoint, path[closestPointIndex])

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

        #print(currentPath)

        mergedPaths.append(currentPath)

        camPaths : List[CamPath] = []
        for path in mergedPaths:
            safeToClose = not ShapelyUtils.crosses(bounds, path[0], path[-1])
            camPaths.append( CamPath( shapely.geometry.LineString(path), safeToClose) )

        return camPaths

    @classmethod
    def separateTabs(cls, origPath: shapely.geometry.LineString, tabs: List['Tab']) -> List[shapely.geometry.LineString]:
        '''
        from a "normal" tool path, split this path into a list of "partial" paths
        avoiding the tabs areas
        '''
        from gcode_generator import Tab

        if len(tabs) == 0:
            return [origPath]

        pts = list(origPath.coords)

        shapely_openpath = shapely.geometry.LineString(pts)

        print("origPath", origPath)
        print("origPath", shapely_openpath)
         
        shapely_tabs_ = []
        # 1. from the tabs, build shapely (closed) tab polygons
        for tab_data in tabs:
            tab = Tab(tab_data)
            shapely_tabs = tab.svg_path.toShapelyPolygons()
            shapely_tabs_ += shapely_tabs

        # hey, multipolygons are good...
        shapely_tabs = shapely.geometry.MultiPolygon(shapely_tabs_)

        # 2. then "diff" the origin path with the tabs paths
        shapely_splitted_paths = shapely_openpath.difference(shapely_tabs)

        # 3. that's it
        print("splitted_paths", shapely_splitted_paths)

        if shapely_splitted_paths.geom_type == 'LineString':
            shapely_splitted_paths = shapely.geometry.MultiLineString([shapely_splitted_paths])

        # back to shapely...
        paths : List[shapely.geometry.LineString] = []
        for shapely_splitted_path in shapely_splitted_paths.geoms:
            intpt_vector = []
            xy = shapely_splitted_path.xy
            for ptX, ptY in zip(xy[0], xy[1]):
                intpt_vector.append((ptX, ptY))
            paths.append(intpt_vector)
        
        # >>> XAM merge some paths when possible
        paths = cls.mergeCompatiblePaths(paths)
        # <<< XAM

        shapely_paths = [shapely.geometry.LineString(path) for path in paths]
        return shapely_paths

    @classmethod
    def mergeCompatiblePaths(cls, paths: List[shapely.geometry.LineString]) -> List[shapely.geometry.LineString]:
        '''
        This is a post-processing step to clipper-6.4.2 where found separated paths can be merged together,
        leading to less separated paths
        '''
        # ------------------------------------------------------------------------------------------------
        def pathsAreCompatible(path1: shapely.geometry.LineString, path2: shapely.geometry.LineString) -> bool:
            '''
            test if the 2 paths have their end point/start point compatible (the same)
            '''
            endPoint = path1[-1]
            startPoint = path2[0]

            if endPoint[0] == startPoint[0] and endPoint[1] == startPoint[1]:
                # can merge
                return True

            return False

        def mergePathIntoPath(path1: shapely.geometry.LineString, path2: shapely.geometry.LineString) -> bool:
            '''
            merge the 2 paths if their end point/start point are compatible (ie the same)
            '''
            endPoint = path1[-1]
            startPoint = path2[0]

            if endPoint[0] == startPoint[0]and endPoint[1] == startPoint[1]:
                # can merge
                path1 += path2[1:]
                return True

        def buildPathsCompatibilityTable(paths: List[shapely.geometry.LineString]) -> Dict[List,int]:
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
          flipXY          toggle X with Y
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

        flipXY = args["flipXY"]

        gcode = ""

        retractGcode = '; Retract\r\n' + \
            f'G1 Z' + safeZ.toFixed(decimal) + f'{rapidFeedGcode}\r\n'

        retractForTabGcode = '; Retract for tab\r\n' + \
            f'G1 Z' + tabZ.toFixed(decimal) + f'{rapidFeedGcode}\r\n'

        def getX(p: Tuple[int,int]) :
            return p[0] * scale + offsetX

        def getY(p : Tuple[int,int]):
            return -p[1] * scale + offsetY

        def convertPoint(p: Tuple[int,int]):
            x = p[0] * scale + offsetX
            y = -p[1] * scale + offsetY

            if flipXY is False:
                result = ' X' + ValWithUnit(x, "-").toFixed(decimal) +  \
                         ' Y' + ValWithUnit(y, "-").toFixed(decimal)
            else:
                result = ' X' + ValWithUnit(-y, "-").toFixed(decimal) +  \
                         ' Y' + ValWithUnit(x, "-").toFixed(decimal)

            return result

        hasTabs = len(tabs) > 0

        for pathIndex, path in enumerate(paths):
            origPath = path.path
            if len(origPath.coords) == 0:
                continue

            # split the path to cut into many partials paths to avoid tabs eraas
            #separatedPaths = cls.separateTabs(origPath, tabs)
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
                    'G1' + convertPoint(list(origPath.coords)[0]) + rapidFeedGcode + '\r\n'

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
                    if selectedPath.is_empty:
                        continue

                    executedRamp = False
                    minPlungeTime = (currentZ - nextZ) / plungeFeed
                    if ramp and minPlungeTime > 0:
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
                        gcode += '; Tab: move to first point of partial path at safe height \r\n'
                        gcode += 'G1' + convertPoint(list(selectedPath.coords)[0]) + '\r\n'
                        gcode += \
                            '; plunge\r\n' + \
                            'G1 Z' + ValWithUnit(nextZ, "-").toFixed(decimal) + plungeFeedGcode + '\r\n'

                    currentZ = nextZ

                    gcode += '; cut\r\n'

                    # on a given height, generate series of G1
                    for i, pt in enumerate(selectedPath.coords):
                        if i == 0:
                            continue
                        
                        gcode += 'G1' + convertPoint(pt)
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