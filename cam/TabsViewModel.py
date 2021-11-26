# Copyright 2022 Xavier
#
# This file is part of pycut.
#
# jscut is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jscut is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jscut.  If not, see <http:#www.gnu.org/licenses/>.

from typing import List


import clipper as ClipperLib
import Snap
import jscut

from SvgViewModel import SvgViewModel
from MaterialViewModel import MaterialViewModel
from SelectionViewModel import SelectionViewModel
from TabsViewModel import TabsViewModel

class Tab:
    '''
    '''
    def __init__(self,
            svgViewModel: SvgViewModel, 
            tabsViewModel: TabsViewModel, 
            tabsGroup, 
            rawPaths, 
            toolPathsChanged, 
            loading) :
        '''
        '''
        self.svgViewModel = svgViewModel
        self.tabsViewModel = tabsViewModel
        self.tabsGroup = tabsGroup
        self.rawPaths = rawPaths
        self.toolPathsChanged = toolPathsChanged
        self.loading = loading

        self.enabled = True
        self.margin = 0.0
        
        self.combinedGeometry = []
        self.combinedGeometrySvg = None

        tabsViewModel.unitConverter.addComputed(self.margin)

        def xxxx(newValue):
            if newValue:
                v = "visible"
            else:
                v = "hidden"
            if self.combinedGeometrySvg:
                self.combinedGeometrySvg.attr("visibility", v)
    

        self.enabled.subscribe(xxxx)
        self.margin.subscribe(self.recombine)
        self.recombine()

    def removeCombinedGeometrySvg(self):
        if self.combinedGeometrySvg:
            self.combinedGeometrySvg.remove()
            self.combinedGeometrySvg = None


    def recombine(self):
        if self.loading:
            return

        self.removeCombinedGeometrySvg()

        def alert(msg):
            showAlert(msg, "alert-warning")

        all = []
        for rawPath in self.rawPaths:
            geometry = jscut.priv.path.getClipperPathsFromSnapPath(rawPath.path, self.svgViewModel.pxPerInch, alert)
            if geometry != None:
                if rawPath.nonzero:
                    fillRule = ClipperLib.PolyFillType.pftNonZero
                else:
                    fillRule = ClipperLib.PolyFillType.pftEvenOdd
                all.append(jscut.priv.path.simplifyAndClean(geometry, fillRule))

        if len(all) == 0:
            self.combinedGeometry = []
        else :
            self.combinedGeometry = all[0]
            for o in all:
                self.combinedGeometry = jscut.priv.path.clip(self.combinedGeometry, o, ClipperLib.ClipType.ctUnion)

        offset = self.margin.toInch() * jscut.priv.path.inchToClipperScale
        if offset != 0:
            self.combinedGeometry = jscut.priv.path.offset(self.combinedGeometry, offset)

        if len(self.combinedGeometry) != 0:
            path = jscut.priv.path.getSnapPathFromClipperPaths(self.combinedGeometry, self.svgViewModel.pxPerInch())
            if path != None:
                self.combinedGeometrySvg = self.tabsGroup.path(path).attr("class", "tabsGeometry")

        self.enabled(True)
        self.toolPathsChanged()


class TabsViewModel:
    '''
    '''
    def __init__(self, 
            svgViewModel: SvgViewModel, 
            materialViewModel: MaterialViewModel, 
            selectionViewModel: SelectionViewModel, 
            tabsGroup, 
            toolPathsChanged):
    
        self.svgViewModel = svgViewModel
        self.materialViewModel = materialViewModel
        self.selectionViewModel = selectionViewModel
        self.tabsGroup = tabsGroup 
        self.toolPathsChanged = toolPathsChanged

        self.tabs: List[Tab] = []
        self.units = self.materialViewModel.matUnits
        self.maxCutDepth = 0

    def addTab(self):
        rawPaths = []

        for element in self.selectionViewModel.getSelection():
            rawPaths.append({
                'path': Snap.parsePathString(element.attr('d')),
                'nonzero': element.attr("fill-rule") != "evenodd",
            })

        self.selectionViewModel.clearSelection()
        tab = Tab(self.svgViewModel, self, self.tabsGroup, rawPaths, self.toolPathsChanged, False)
        self.tabs.append(tab)
        self.toolPathsChanged()

    def removeTab(self, tab):
        tab.removeCombinedGeometrySvg()
        self.tabs.remove(tab)
        self.toolPathsChanged()

    def clickOnSvg(self, elem) :
        if elem.attr("class") == "tabsGeometry":
            return True
        return False
