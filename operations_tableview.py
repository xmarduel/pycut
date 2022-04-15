from typing import List
from typing import Any
from typing import Dict

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class OpItem:
    def __init__(self, data):
        self.name = data.get("Name", "op")
        self.cam_op = data.get("type", "Pocket")
        self.cutDepth = data.get("Deep", 3.175)
        self.paths = data.get("paths", [])      
        self.ramp = data.get("RampPlunge", False)
        self.combinaison = data.get("Combine", "Union")
        self.direction = data.get("Direction", "Conventional")
        self.units = data.get("Units", "mm")
        self.margin = data.get("Margin", 0.0)
        self.width = data.get("Width", 0.0)

        # not in the data
        self.enabled = False

    def put_value(self, attr, value):
        '''
        '''
        setattr(self, attr, value)
        
    def __str__(self):
        '''
        '''
        return "op: %s %s [%f] %s %s %s %f" % (self.name, self.cam_op, self.cutDepth, self.ramp, self.enabled, self.combinaison, self.cutDepth)

    def to_dict(self) -> Dict[str, Any]:
        '''
        '''
        return {
            "Name": self.name,
            "type": self.cam_op,
            "Deep": self.cutDepth,
            "paths": self.paths,  
            "RampPlunge": self.ramp ,
            "Combine": self.combinaison,
            "Direction": self.direction,
            "Units": self.units,
            "Margin": self.margin ,
            "Width": self.width 
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
        self.setMaximum(100)
        self.setSingleStep(0.1)
        self.setDecimals(3)

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

class PyCutComboBox(QtWidgets.QComboBox):
    '''
    '''

    def __init__(self, parent, items):
        '''
        '''
        QtWidgets.QComboBox.__init__(self, parent)

        self.o = None
        self.attribute = ""
        
        self.items = items

        self.currentIndexChanged.connect(self.cb_combobox)

    def cb_disconnect(self):
        '''
        '''
        self.currentIndexChanged.disconnect(self.cb_combobox)

    def cb_connect(self):
        '''
        '''
        self.currentIndexChanged.connect(self.cb_combobox)

    def assign_object(self, o):
        '''
        '''
        self.o = o

    def assign_object_attribute(self, attribute):
        '''
        '''
        self.attribute = attribute

    def fill_control(self):
        '''
        '''
        self.cb_disconnect()
        self.clear()
        self.addItems(self.items)
        self.cb_connect()

    def set_value(self):
        '''
        '''
        self.cb_disconnect()

        # values can be strings or integers or of any other type -> use only strings in control
        val = str(getattr(self.o, self.attribute))

        # basic check
        if val not in self.items:
            idx = 0  # to avoid an exception
        else:
            idx = self.items.index(val)

        self.setCurrentIndex(idx)

        self.cb_connect()

    def cb_combobox(self, index):
        '''
        '''
        val = self.itemText(index)

        self.o.put_value(self.attribute, val)

class PyCutDoubleSpinBoxDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.xeditors = {}

    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        editor = PyCutDoubleSpinBox(parent)

        op = index.model().get_operation(index)
        attr = index.model().get_operation_attr(index)

        editor.assign_object(op)
        editor.assign_object_attribute(attr)

        # to flush an "setModelData" in place - it works!
        editor.valueChanged.connect(self.onEditorValueChanged)

        self.xeditors[(index.row(), index.column())] = editor

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

class PyCutCheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        editor = PyCutCheckBox(parent)

        op = index.model().get_operation(index)
        attr = index.model().get_operation_attr(index)

        editor.assign_object(op)
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

class PyCutComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        col = index.column()

        self.items = []
        if col == 1:
            self.items = ["Pocket", "Inside", "Outside", "Engrave"]
        if col == 4:
            self.items = ["inch", "mm"]
        if col == 7:
            self.items = ["Union", "Intersection", "Difference", "Xor"]
        if col == 8:
            self.items = ["Conventional", "Climb"]
       

        editor = PyCutComboBox(parent, self.items)

        op = index.model().get_operation(index)
        attr = index.model().get_operation_attr(index)

        editor.assign_object(op)
        editor.assign_object_attribute(attr)
        editor.fill_control()

        # to flush a "setModelData" in place - it works! but model still has old value -
        editor.currentIndexChanged.connect(self.onEditorCurrentIndexChanged)

        return editor

    def onEditorCurrentIndexChanged(self, idx):
        editor = self.sender()
        if editor:
            self.commitData.emit(editor)

    def setEditorData(self, comboBox: PyCutComboBox, index: QtCore.QModelIndex):
        comboBox.set_value()

    def setModelData(self, comboBox: PyCutComboBox, model, index: QtCore.QModelIndex):
        model.handleNewvalue(index, comboBox.currentText())
        return

    def updateEditorGeometry(self, comboBox: PyCutComboBox, option, index: QtCore.QModelIndex):
        comboBox.setGeometry(option.rect)


class PyCutOperationsTableViewManager(QtWidgets.QWidget):

    def __init__(self, parent):
        '''
        '''
        super().__init__(parent)

        self.mainwindow = None
        self.svg_viewer = None

        self.model = None

        # main section of the window
        vbox = self.vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        # let's add two views of the same data source we just created:
        self.table = PyCutSimpleTableView(self)
        self.table.resizeColumnsToContents()
        self.table.setMinimumWidth(800)

        # bottom section of the window:
        # let's have a text input and a pushbutton that add an item to our model.
        hbox_add = QtWidgets.QHBoxLayout()

        # create the button, and hook it up to the slot below.
        self._button_add = QtWidgets.QPushButton("Create Operation")
        self._button_add.clicked.connect(self.add_item)
        self._button_add.setIcon(QtGui.QIcon(':/images/milling-machine-op.png'))

        hbox_add.addWidget(self._button_add)


        hbox_gen = QtWidgets.QHBoxLayout()

        self._button_gen = QtWidgets.QPushButton("Generate GCode")
        self._button_gen.clicked.connect(self.gen_gcode)
        self._button_gen.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/view-refresh.png"))

        hbox_gen.addWidget(self._button_gen)

        # add bottom to main window layout
        vbox.addLayout(hbox_add)
        vbox.addLayout(hbox_gen)

        # set layout on the window
        self.setLayout(vbox)

    def set_svg_viewer(self, svg_viewer):
        '''
        '''
        self.svg_viewer = svg_viewer
        self.mainwindow = svg_viewer.mainwindow

    def set_operations(self, operations):
        '''
        '''
        cnc_ops = []
        for op in operations:
            cnc_op = OpItem(op)
            cnc_ops.append(cnc_op)
            
            
        self.model = PyCutSimpleTableModel(cnc_ops, self.mainwindow)
        # so that the model known the view
        self.model.set_view(self.table)
        
        self.table.setModel(self.model)
        self.table.setup()

        self.vbox.addWidget(self.table)

    def get_operations(self) -> List[Dict]:
        '''
        returns the list of operations ready to br saved as json data
        '''
        ops = []

        for operation in self.get_model_operations():
            op = operation.to_dict()
            ops.append(op)

        return ops

    def set_model(self, model):
        '''
        '''
        self.table.setModel(model)

    def get_model(self) -> 'PyCutSimpleTableModel' :
        '''
        '''
        return self.table.model()

    def get_model_operations(self) -> List[OpItem]:
        '''
        '''
        return self.get_model().operations

    def add_item(self):
        '''
        instruct the model to add an item
        '''
        paths = self.svg_viewer.get_selected_items_ids()
        self.table.addItem({
            "paths": paths
            }
        )
        
        print("ADD")
        for op in self.get_model_operations():
            print(op)

    def gen_gcode(self):
        '''
        '''
        # instruct the model to generate the g-code for all selected items
        self.model.generate_gcode()


class PyCutSimpleTableView(QtWidgets.QTableView):
    '''
    '''
    def __init__(self, parent=None):
        '''
        '''
        super().__init__(parent)

        self.parent = parent

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
            "name",                     # [0] str
            "cam_op",
            "enabled",                  # [2] checkbox
            "paths",                    # [3] str
            "units",
            "cutDepth",                 # [5] float
            "ramp",                     # [6] checkbox
            "combinaison",
            "direction",
            "margin",                   # [9] float
            "width",                    # [10] float
            "del",                      # [11] button
            "up",                       # [12] button
            "down",                     # [13] button
        ]
        '''
        delegate = PyCutComboBoxDelegate(self)
        self.setItemDelegateForColumn(1, delegate)

        delegate = PyCutCheckBoxDelegate(self)
        self.setItemDelegateForColumn(2, delegate)

        delegate = PyCutComboBoxDelegate(self)
        self.setItemDelegateForColumn(4, delegate)

        delegate = PyCutDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(5, delegate)
        
        delegate = PyCutCheckBoxDelegate(self)
        self.setItemDelegateForColumn(6, delegate)
    
        delegate = PyCutComboBoxDelegate(self)
        self.setItemDelegateForColumn(7, delegate)
        
        delegate = PyCutComboBoxDelegate(self)
        self.setItemDelegateForColumn(8, delegate)

        self.delegate_col_margin = delegate = PyCutDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(9, delegate)

        self.delegate_col_width = delegate = PyCutDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(10, delegate)

        self.setup_persistent_editors()

    def setup_persistent_editors(self):
        '''
        '''
        # Make the combo boxes / check boxes / others specials always displayed.
        for k in range(self.model().rowCount(None)):
            self.openPersistentEditor(self.model().index(k, 1)) # cam_op
            self.openPersistentEditor(self.model().index(k, 2)) #   enabled
            self.openPersistentEditor(self.model().index(k, 4)) # units
            self.openPersistentEditor(self.model().index(k, 5)) #       cutDepth
            self.openPersistentEditor(self.model().index(k, 6)) #   ramp
            self.openPersistentEditor(self.model().index(k, 7)) # combinaison
            self.openPersistentEditor(self.model().index(k, 8)) # direction
            self.openPersistentEditor(self.model().index(k, 9)) #      margin
            self.openPersistentEditor(self.model().index(k, 10)) #      width

        for row in range(self.model().rowCount(None)):
            btn_del_op = QtWidgets.QPushButton()
            btn_del_op.setText("")
            btn_del_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/edit-clear.png'))
            btn_del_op.setToolTip("Delete Op")
            btn_del_op.clicked.connect(self.cb_delete_op)
            self.setIndexWidget(self.model().index(row, 11), btn_del_op)

            btn_up_op = QtWidgets.QPushButton()
            btn_up_op.setText("")
            btn_up_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/go-up.png'))
            btn_up_op.setToolTip("Up")
            btn_up_op.clicked.connect(self.cb_move_up_op)
            self.setIndexWidget(self.model().index(row, 12), btn_up_op)

            btn_dw_op = QtWidgets.QPushButton()
            btn_dw_op.setText("")
            btn_dw_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/go-down.png'))
            btn_dw_op.setToolTip("Down")
            btn_dw_op.clicked.connect(self.cb_move_down_op)
            self.setIndexWidget(self.model().index(row, 13), btn_dw_op)

        self.resizeColumnsToContents() # now!

        self.setColumnWidth(3, 90)  # paths
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.enable_disable_cells()

    def cb_delete_op(self):
        index = self.currentIndex()
        idx = index.row()
        # instruct the model to del an item
        self.model().delItem(idx)
        
        print("DEL")
        for op in self.model().operations:
            print(op)

    def cb_move_down_op(self):
        index = self.currentIndex()
        idx = index.row()
        if idx < self.model().rowCount(None) - 1:
            self.model().swapItems(idx, idx + 1)

        # to be sure to update the table... and all its delegates
        self.setup_persistent_editors()
        
        print("DOWN")
        for op in self.model().operations:
            print(op)
        
    def cb_move_up_op(self):
        index = self.currentIndex()
        idx = index.row()
        if idx > 0:
            self.model().swapItems(idx, idx - 1)

        # to be sure to update the table... and all its delegates
        self.setup_persistent_editors()
        
        print("UP")
        for op in self.model().operations:
            print(op)

    def addItem(self, op_data):
        self.model().addItem(op_data)
        self.setup_persistent_editors()  # to show the editors on a new item

    def enable_disable_cells(self):
        margin = {'Pocket': True, 'Inside': True, 'Outside': True, 'Engrave': False} 
        width = {'Pocket': False, 'Inside': True, 'Outside': True, 'Engrave': False} 

        for row in range(self.model().rowCount(None)):
            cam_op = self.model().operations[row].cam_op
            
            self.delegate_col_margin.xeditors[(row, 9)].setEnabled(margin[cam_op]) 
            self.delegate_col_width.xeditors[(row, 10)].setEnabled(width[cam_op]) 


class PyCutSimpleTableModel(QtCore.QAbstractTableModel):
    '''
    model for the table view
    '''
    def __init__(self, operations: List[Any], mainwindow):
        super().__init__()
        
        self.operations = operations
        self.mainwindow = mainwindow
        self.view = None

        self.header =  [
            "name",                     # [0] str
            "cam_op",
            "enabled",                  # [2] checkbox
            "paths",                    # [3] str
            "units",
            "cutDepth",                 # [5] float
            "ramp",                     # [6] checkbox
            "combinaison",
            "direction",
            "margin",                   # [9] float
            "width",                    # [10] float
            "del",                      # [11] button
            "up",                       # [12] button
            "down",                     # [13] button
        ]

        self.cnt = 0

    def set_view(self, view: PyCutSimpleTableView):
        '''
        '''
        self.view = view

    def generate_gcode(self):
        '''
        '''    
        self.mainwindow.cb_generate_gcode()
        
    def handleNewvalue(self, index: QtCore.QModelIndex, value: Any):
        row = index.row()
        col = index.column()

        attrib = self.header[col]

        # update pycut GUI
        if attrib in ["cam_op", "enabled", "paths", "units", "cutDepth", "ramp", "combinaison", "margin", "width"]:
            cnc_op = self.operations[row]
            setattr(cnc_op, attrib, value)

            self.mainwindow.display_cnc_ops_geometry(self.operations)

        if self.view is not None:
            self.view.enable_disable_cells()

    def __str__(self):
        self.cnt += 1
        data = "--------------------------------\n"
        for op in self.operations:
            data += str(op) + "\n"
        return data

    def dump(self):
        self.cnt += 1
        print("--------------------------------", self.cnt)
        for op in self.operations:
            print(op)

    def headerData(self, col: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.EditRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.operations)

    def columnCount(self, parent):
        return len(self.header)

    def setData(self, index: QtCore.QModelIndex, value, role = QtCore.Qt.EditRole):
        '''
        for the cells without delegate
        '''
        op = self.get_operation(index)
        attr = self.get_operation_attr(index)

        if role == QtCore.Qt.EditRole:
            setattr(op, attr, value)

    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.EditRole):
        op = self.get_operation(index)
        attr = self.get_operation_attr(index)

        # for check box, data is displayed in the "editor"
        col = index.column()

        if col == 11:  # button
            return None
        if col == 12:  # button
            return None
        if col == 13:  # button
            return None

        # for checkboxes only
        if col == 2:   # checkbox
            return None
        if col == 6:   # checkbox
            return None

        if role == QtCore.Qt.DisplayRole:
            val = getattr(op, attr)

            if col == 3:  # make a string of the list
                # list of svg paths ids
                val = str(val)

            return val
        if role == QtCore.Qt.EditRole:
            val = getattr(op, attr)

            if col == 3:
                # list of svg paths ids
                val = str(val)

            return val

        return None

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags :
        flags = super().flags(index)

        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled

        return flags

    def addItem(self, op_data):
        op = OpItem(op_data)

        idx = len(self.operations)

        self.beginInsertRows(QtCore.QModelIndex(), idx, idx)
        self.operations.append(op)
        self.endInsertRows()

    def delItem(self, idx):
        op = self.operations[idx]

        self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
        self.operations.remove(op)
        self.endRemoveRows()

    def swapItems(self, idx1, idx2):
        self.beginResetModel()
        self.operations[idx1], self.operations[idx2] = self.operations[idx2], self.operations[idx1]
        self.endResetModel()
        
    def get_operation(self, index):
        return self.operations[index.row()]

    def get_operation_attr(self, index):
        return self.header[index.column()]
  
