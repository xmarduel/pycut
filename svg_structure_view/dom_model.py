from typing import Any

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtXml

'''
Shoun't it pure python with lxml ? and no QDomNode ? '''

class DomItem:
    '''
    '''
    def __init__(self, node: QtXml.QDomNode, row: int, parent: 'DomItem' = None):
        self.domNode = node
        self.childItems = {} # QHash<int, DomItem>
        self.parentItem = parent
        self.rowNumber = row

    def child(self, i: int) -> 'DomItem':
        if i in self.childItems:
            return self.childItems[i]

        #if child does not yet exist, create it
        if (i >= 0 and i < self.domNode.childNodes().count()):
            childNode = QtXml.QDomNode(self.domNode.childNodes().item(i))
            childItem = DomItem(childNode, i, self)
            self.childItems[i] = childItem
    
            return childItem

        return None

    def parent(self) -> 'DomItem':
        return self.parent

    def node(self) ->  QtXml.QDomNode:
        return self.domNode

    def row(self) -> int:
        return self.rowNumber


class DomModel(QtWidgets.QAbstractItemModel):
    '''
    https://doc.qt.io/qtforpython/overviews/qtwidgets-itemviews-simpledommodel-example.html
    '''
    def __init__(self, document: QtXml.QDomDocument, parent = None):
        '''
        '''
        super().__init__(parent)
        
        self.domDocument = document
        self.rootItem = DomItem(document, None)

    def data(self, index: QtCore.QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        item : DomItem = index.internalPointer()

        node : QtXml.QDomNode = item.node()

        if index.column() == 0:
            return node.nodeName()
        elif index.column() == 1:
            attributeMap = node.attributes()
            attributes = []
            for key, attribute in attributeMap:
                attributes << attribute.nodeName() + "=\"" + attribute.nodeValue() + '"'
            
            return attributes.join(' ')
        elif index.column() == 2:
            return node.nodeValue().split('\n').join(' ')
        else:
            pass
    
        return None

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return super().flags(index)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Attributes"
            elif section == 2:
                return "Value"
            else:
                return None

        return None

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex :
        '''
        creates a model index for the item with the given row, column, and parent in the model
        '''
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
    
        return QtCore.QModelIndex()

    def parent(self, child: QtCore.QModelIndex) -> QtCore.QModelIndex :
        if not child.isValid():
            return QtCore.QModelIndex()

        childItem : DomItem = child.internalPointer()
        parentItem : DomItem = childItem.parent()

        if (not parentItem) or (parentItem == self.rootItem):
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int :
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return len(parentItem.node().childNodes())

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return 3

