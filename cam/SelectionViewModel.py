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

import jscut
import showAlert

from pycut import SvgViewModel
from pycut import MaterialViewModel

class SelectionViewModel:
    '''
    '''
    def __init__(self, 
            svgViewModel: SvgViewModel, 
            materialViewModel: MaterialViewModel,
            selectionGroup):
            
        self.svgViewModel = svgViewModel
        self.materialViewModel = materialViewModel
        self.selectionGroup = selectionGroup

        self.selMinNumSegments = 1
        self.selMinSegmentLength = 0.01
        self.selNumSelected = 0
    
    def clickOnSvg(self, elem):
        def alertMsg(msg):
            showAlert(msg, "alert-warning")

        if elem.attr("class") == "selectedPath":
            elem.remove()
            self.selNumSelected(self.selNumSelected() - 1)
            return True

        path = jscut.priv.path.getLinearSnapPathFromElement(elem, 
                self.selMinNumSegments, 
                self.selMinSegmentLength.toInch() * self.svgViewModel.pxPerInch,
                alertMsg)

        if path != None:
            newPath = self.selectionGroup.path(path)
            newPath.attr("class", "selectedPath")
            if elem.attr("fill-rule") == "evenodd":
                newPath.attr("fill-rule", "evenodd")
            self.selNumSelected = self.selNumSelected + 1

        return True

    def getSelection(self):
        return self.selectionGroup.selectAll("path")

    def clearSelection(self):
        self.selectionGroup.selectAll("path").remove()
        self.selNumSelected = 0
