from typing import List
from typing import Any
from typing import Dict

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class TabItem:
    def __init__(self, data):
        self.x = data.get("center", [10,10])[0]
        self.y = data.get("center", [10,10])[1]
        self.radius = data.get("radius", 5)
       
        # not in the data
        self.enabled = data.get("enabled", False)

    def put_value(self, attr, value):
        '''
        '''
        setattr(self, attr, value)
        
    def __str__(self):
        '''
        '''
        return "tab: [%f:%f] %f - %s" % (self.x, self.y, self.radius, self.enabled)

    def to_dict(self) -> Dict[str, Any]:
        '''
        '''
        return {
            "center": [self.x, self.y],
            "radius": self.radius,
            "enabled": self.enabled
        }

class PyCutDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    '''
    '''

    def __init__(self, parent):
        '''
        '''
        QtWidgets.QDoubleSpinBox.__init__(self, parent)

        self.o = None
        self.attribute = ""

        self.setMinimum(0)
        self.setMaximum(1000)
        self.setSingleStep(1.0)

        self.valueChanged.connect(self.cb_spinbox)

    def cb_disconnect(self):
        '''
        '''
        self.valueChanged.disconnect(self.cb_spinbox)

    def cb_connect(self):
        '''
        '''
        self.valueChanged.connect(self.cb_spinbox)

    def assign_object(self, o):
        '''
        '''
        self.o = o

    def assign_object_attribute(self, attribute):
        '''
        '''
        self.attribute = attribute

    def set_value(self):
        '''
        '''
        self.cb_disconnect()

        try:
            val = getattr(self.o, self.attribute)
        except Exception:
            val = 0

        self.setValue(val)

        self.cb_connect()

    def cb_spinbox(self):
        '''
        '''
        val = self.value()
        self.o.put_value(self.attribute, val)

class PyCutDoubleSpinBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        editor = PyCutDoubleSpinBox(parent)

        tab = index.model().get_tab(index)
        attr = index.model().get_tab_attr(index)

        editor.assign_object(tab)
        editor.assign_object_attribute(attr)

        # to flush an "setModelData" in place - it works!
        editor.valueChanged.connect(self.onEditorValueChanged)

        return editor

    def onEditorValueChanged(self):
        editor = self.sender()
        if editor:
            self.commitData.emit(editor)

    def setEditorData(self, spinBox: PyCutDoubleSpinBox, index: QtCore.QModelIndex):
        spinBox.set_value()

    def setModelData(self, spinBox: PyCutDoubleSpinBox, model, index: QtCore.QModelIndex):
        model.handleNewvalue(index, spinBox.value())
        return

    def updateEditorGeometry(self, editor: PyCutDoubleSpinBox, option, index: QtCore.QModelIndex):
        editor.setGeometry(option.rect)


class PyCutCheckBox(QtWidgets.QCheckBox):
    '''
    '''
    def __init__(self, parent):
        '''
        '''
        QtWidgets.QCheckBox.__init__(self, parent)

        self.o = None
        self.attribute = ""

        self.stateChanged.connect(self.cb_checkbox)

    def cb_disconnect(self):
        '''
        '''
        self.stateChanged.disconnect(self.cb_checkbox)

    def cb_connect(self):
        '''
        '''
        self.stateChanged.connect(self.cb_checkbox)

    def assign_object(self, o):
        '''
        '''
        self.o = o

    def assign_object_attribute(self, attribute):
        '''
        '''
        self.attribute = attribute

    def set_value(self):
        '''
        '''
        self.cb_disconnect()

        uival = {True: QtCore.Qt.Checked, False: QtCore.Qt.Unchecked}[getattr(self.o, self.attribute)]

        self.setCheckState(uival)

        self.cb_connect()

    def cb_checkbox(self, index):
        '''
        '''
        val = {QtCore.Qt.Checked: True, QtCore.Qt.Unchecked: False}[self.checkState()]
        self.o.put_value(self.attribute, val)

class PyCutCheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        editor = PyCutCheckBox(parent)

        tab = index.model().get_tab(index)
        attr = index.model().get_tab_attr(index)

        editor.assign_object(tab)
        editor.assign_object_attribute(attr)

        # return editor # -> ugly checkbox on the left of the cell

        # -> for checkboxes to be centered: embed into a widget
        checkWidget = QtWidgets.QWidget(parent)
        checkLayout = QtWidgets.QHBoxLayout(checkWidget)
        checkLayout.addWidget(editor)
        checkLayout.setAlignment(QtCore.Qt.AlignCenter)
        checkLayout.setContentsMargins(0,0,0,0)

        # to flush an "setModelData" in place - it works!
        editor.stateChanged.connect(self.onEditorStateChanged)

        return checkWidget

    def onEditorStateChanged(self):
        editor = self.sender()
        if editor:
            checkWidget = editor.parent()
            self.commitData.emit(checkWidget)

    def setEditorData(self, checkWidget: QtWidgets.QWidget, index: QtCore.QModelIndex):
        checkBoxItem = checkWidget.layout().itemAt(0)
        checkBox : PyCutCheckBox = checkBoxItem.widget()
        checkBox.set_value()

    def setModelData(self, checkWidget: QtWidgets.QWidget, model, index: QtCore.QModelIndex):
        checkBoxItem = checkWidget.layout().itemAt(0)
        checkBox : PyCutCheckBox = checkBoxItem.widget()

        model.handleNewvalue(index, checkBox.isChecked())
        return

    def updateEditorGeometry(self, editor, option, index: QtCore.QModelIndex):
        editor.setGeometry(option.rect)


class PyCutTabsTableViewManager(QtWidgets.QWidget):

    def __init__(self, parent):
        '''
        '''
        QtWidgets.QWidget.__init__(self, parent)

        self.mainwindow = None
        self.svg_viewer = None

        self.model = None

        # main section of the window
        vbox = self.vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        # let's add two views of the same data source we just created:
        self.table = PyCutSimpleTableView(self)
        self.table.resizeColumnsToContents()
        self.table.setMinimumWidth(300)

        # bottom section of the window:
        # let's have a text input and a pushbutton that add an item to our model.
        hbox = QtWidgets.QHBoxLayout()

        # create the button, and hook it up to the slot below.
        self._button_add = QtWidgets.QPushButton("Create Tab")
        self._button_add.clicked.connect(self.add_item)
        self._button_add.setIcon(QtGui.QIcon(":/images/tango/32x32/actions/list-add"))

        hbox.addWidget(self._button_add)

        # add bottom to main window layout
        vbox.addLayout(hbox)

        # set layout on the window
        self.setLayout(vbox)

    def set_svg_viewer(self, svg_viewer):
        '''
        '''
        self.svg_viewer = svg_viewer
        self.mainwindow = svg_viewer.mainwindow

    def set_tabs(self, tabs):
        '''
        '''
        cnc_tabs = []
        for tab in tabs:
            cnc_tab = TabItem(tab)
            cnc_tabs.append(cnc_tab)
            
            
        self.model = PyCutSimpleTableModel(cnc_tabs, self.mainwindow)
        self.table.setModel(self.model)
        self.table.setup()

        self.vbox.addWidget(self.table)

    def get_tabs(self) -> List[Dict]:
        '''
        returns the list of tabs ready to be saved as json data
        '''
        tabs = []

        for tab in self.get_model_tabs():
            tab = tabs.to_dict()
            tabs.append(tab)

        return tabs

    def set_model(self, model):
        '''
        '''
        self.table.setModel(model)

    def get_model(self) -> 'PyCutSimpleTableModel' :
        '''
        '''
        return self.table.model()

    def get_model_tabs(self) -> List[TabItem]:
        '''
        '''
        return self.get_model().tabs

    def add_item(self):
        '''
        instruct the model to add an item
        '''
        self.table.addItem({
            "center": [10,10],
            "radius": 5,
            "enabled": True
            }
        )
        
        print("ADD")
        for tab in self.get_model_tabs():
            print(tab)

        # inform main window (draw tab in svg)
        model_tabs = self.get_model_tabs()
        tabs = [tab.to_dict() for tab in model_tabs]
        self.mainwindow.display_cnc_tabs(tabs)


class PyCutSimpleTableView(QtWidgets.QTableView):
    '''
    '''
    def __init__(self, parent=None):
        '''
        '''
        QtWidgets.QTableView.__init__(self, parent)

        self.resizeColumnsToContents()
        # Fixes the width of columns and the height of rows.
        try:
            #self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
            #self.verticalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
            pass
        except Exception:
            pass  # PySide

        self.setAlternatingRowColors(True)

    def setup(self):
        '''
        self.header =  [
            "x",                        # [0] float
            "y",                        # [1] float
            "radius",                   # [2] float
            "enabled",                  # [3] checkbox
            "del",                      # [4] button
        ]
        '''
        delegate = PyCutDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(0, delegate)

        delegate = PyCutDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(1, delegate)

        delegate = PyCutDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(2, delegate)

        delegate = PyCutCheckBoxDelegate(self)
        self.setItemDelegateForColumn(3, delegate)

        # Make the combo boxes / check boxes / others specials always displayed.
        for k in range(self.model().rowCount(None)):
            self.openPersistentEditor(self.model().index(k, 0)) # x
            self.openPersistentEditor(self.model().index(k, 1)) # y
            self.openPersistentEditor(self.model().index(k, 2)) # radius
            self.openPersistentEditor(self.model().index(k, 3)) # enabled
            

        for row in range(self.model().rowCount(None)):
            btn_del_tab = QtWidgets.QPushButton()
            btn_del_tab.setText("")
            btn_del_tab.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/edit-clear.png'))
            btn_del_tab.setToolTip("DeleteTab")
            btn_del_tab.clicked.connect(self.cb_delete_tab)
            self.setIndexWidget(self.model().index(row, 4), btn_del_tab)

        # setup a right grid size
        vwidth = self.verticalHeader().width()
        hwidth = self.horizontalHeader().length()
        swidth = self.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        fwidth = self.frameWidth() * 2

        #self.setFixedWidth(vwidth + hwidth + swidth + fwidth)
        #self.setMinimumWidth(vwidth + hwidth + swidth + fwidth)

        self.resizeColumnsToContents() # now!

        self.setColumnWidth(0, 70)  # x
        self.setColumnWidth(1, 70)  # y
        self.setColumnWidth(2, 60)  # radius quite small

    def cb_delete_tab(self):
        index = self.currentIndex()
        idx = index.row()
        # instruct the model to del an item
        self.model().delItem(idx)
        
        print("DEL")
        for tab in self.model().tabs:
            print(tab)

        # inform main window (draw tab in svg)
        model_tabs = self.model().tabs
        tabs = [tab.to_dict() for tab in model_tabs]
        self.parent().mainwindow.display_cnc_tabs(tabs)
        
    def addItem(self, tab_data):
        self.model().addItem(tab_data)
        self.setup()  # to show the editors on a new item


class PyCutSimpleTableModel(QtCore.QAbstractTableModel):
    '''
    model for the table view
    '''
    def __init__(self, tabs: List[Any], mainwindow):
        super(PyCutSimpleTableModel, self).__init__()
        
        self.tabs = tabs
        self.mainwindow = mainwindow

        self.header =  [
            "x",                       # [0] int
            "y",                       # [1] int
            "radius",                  # [2] int
            "enabled",                 # [3] checkbox
            "del",                     # [4] button
        ]

        self.cnt = 0
        
    def handleNewvalue(self, index: QtCore.QModelIndex, value: Any):
        row = index.row()
        col = index.column()

        attrib = self.header[col]

        # update pycut GUI
        if attrib in ["x", "y", "radius", "enabled"]:
            cnc_tab = self.tabs[row]
            setattr(cnc_tab, attrib, value)

            tabs = [tab.to_dict() for tab in self.tabs]
            self.mainwindow.display_cnc_tabs(tabs)

    def __str__(self):
        self.cnt += 1
        data = "--------------------------------\n"
        for tab in self.tabs:
            data += str(tab) + "\n"
        return data

    def dump(self):
        self.cnt += 1
        print("--------------------------------", self.cnt)
        for tab in self.tabs:
            print(tab)

    def headerData(self, col: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.EditRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.tabs)

    def columnCount(self, parent):
        return len(self.header)

    def setData(self, index: QtCore.QModelIndex, value, role = QtCore.Qt.EditRole):
        '''
        for the cells without delegate
        '''
        tab = self.get_tab(index)
        attr = self.get_tab_attr(index)

        if role == QtCore.Qt.EditRole:
            setattr(tab, attr, value)

    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.EditRole):
        tab = self.get_tab(index)
        attr = self.get_tab_attr(index)

        # for check box, data is displayed in the "editor"
        col = index.column()

        if col == 4:  # button
            return None


        # for checkboxes only
        if col == 3:   # checkbox
            return None

        if role == QtCore.Qt.DisplayRole:
            val = getattr(tab, attr)

            return val
        if role == QtCore.Qt.EditRole:
            val = getattr(tab, attr)

            return val

        return None

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags :
        flags = super(PyCutSimpleTableModel, self).flags(index)

        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled

        return flags

    def addItem(self, tab_data):
        tab = TabItem(tab_data)

        idx = len(self.tabs)

        self.beginInsertRows(QtCore.QModelIndex(), idx, idx)
        self.tabs.append(tab)
        self.endInsertRows()

    def delItem(self, idx):
        tab = self.tabs[idx]

        self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
        self.tabs.remove(tab)
        self.endRemoveRows()

    def swapItems(self, idx1, idx2):
        self.beginResetModel()
        self.tabs[idx1], self.tabs[idx2] = self.tabs[idx2], self.tabs[idx1]
        self.endResetModel()
        
    def get_tab(self, index):
        return self.tabs[index.row()]

    def get_tab_attr(self, index):
        return self.header[index.column()]
  
