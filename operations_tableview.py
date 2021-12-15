from typing import List
from typing import Any

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class CncOp:
    def __init__(self, data):
        self.name = data.get("Name", "op")
        self.cam_op = data.get("type", "Pocket")
        self.cutDepth = data.get("Deep", 0.125)
        self.paths = data.get("paths", [])      
        self.ramp = data.get("RampPlunge", False)
        self.combinaison = data.get("Combine", "Union")
        self.direction = data.get("Direction", "Conventional")
        self.units = data.get("Units", "inch")
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


class PMFDoubleSpinBox(QtWidgets.QDoubleSpinBox):
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

class PMFCheckBox(QtWidgets.QCheckBox):
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

class PMFComboBox(QtWidgets.QComboBox):
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

class PMFCheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        editor = PMFCheckBox(parent)

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
            print("onEditorStateChanged - PMFCheckBoxDelegate - editor", editor)
            checkWidget = editor.parent()
            self.commitData.emit(checkWidget)

    def setEditorData(self, checkWidget: QtWidgets.QWidget, index: QtCore.QModelIndex):
        checkBoxItem = checkWidget.layout().itemAt(0)
        checkBox : PMFCheckBox = checkBoxItem.widget()
        checkBox.set_value()

    def setModelData(self, checkWidget: QtWidgets.QWidget, model, index: QtCore.QModelIndex):
        print("PMFCheckBoxDelegate::setModelData - editor", checkWidget)

        checkBoxItem = checkWidget.layout().itemAt(0)
        checkBox : PMFCheckBox = checkBoxItem.widget()

        model.handleNewvalue(index, checkBox.isChecked())
        return

    def updateEditorGeometry(self, editor, option, index: QtCore.QModelIndex):
        editor.setGeometry(option.rect)

class PMFComboBoxDelegate(QtWidgets.QItemDelegate):
    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        col = index.column()

        self.items = []
        if col == 2:
            self.items = ["Pocket", "Inside", "Outside", "Engrave"]
        if col == 5:
            self.items = ["inch", "mm"]
        if col == 8:
            self.items = ["Union", "Intersection", "Difference", "Xor"]
        if col == 9:
            self.items = ["Conventional", "Climb"]
       

        editor = PMFComboBox(parent, self.items)

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
            print("onEditorCurrentIndexChanged - PMFComboBoxDelegate")
            self.commitData.emit(editor)

    def setEditorData(self, comboBox: PMFComboBox, index: QtCore.QModelIndex):
        comboBox.set_value()

    def setModelData(self, comboBox: PMFComboBox, model, index: QtCore.QModelIndex):
        model.handleNewvalue(index, comboBox.currentText())
        return

    def updateEditorGeometry(self, comboBox: PMFComboBox, option, index: QtCore.QModelIndex):
        comboBox.setGeometry(option.rect)

class PMFDoubleSpinBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index: QtCore.QModelIndex):
        editor = PMFDoubleSpinBox(parent)

        op = index.model().get_operation(index)
        attr = index.model().get_operation_attr(index)

        editor.assign_object(op)
        editor.assign_object_attribute(attr)

        # to flush an "setModelData" in place - it works!
        editor.valueChanged.connect(self.onEditorValueChanged)

        return editor

    def onEditorValueChanged(self):
        editor = self.sender()
        if editor:
            print("onEditorValueChanged - PMFDoubleSpinBoxDelegate")
            self.commitData.emit(editor)

    def setEditorData(self, spinBox: PMFDoubleSpinBox, index: QtCore.QModelIndex):
        spinBox.set_value()

    def setModelData(self, spinBox: PMFDoubleSpinBox, model, index: QtCore.QModelIndex):
        model.handleNewvalue(index, spinBox.value())
        return

    def updateEditorGeometry(self, editor: PMFDoubleSpinBox, option, index: QtCore.QModelIndex):
        editor.setGeometry(option.rect)


class PMFTableViewManager(QtWidgets.QWidget):

    def __init__(self, parent):
        '''
        '''
        QtWidgets.QWidget.__init__(self, parent)

        self.main_window = parent.parent().parent()

        self.model = None

        # main section of the window
        vbox = self.vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        # let's add two views of the same data source we just created:
        self.table = PMFSimpleTableView(self)
        self.table.resizeColumnsToContents()
        self.table.setMinimumWidth(800)

        # bottom section of the window:
        # let's have a text input and a pushbutton that add an item to our model.
        hbox = QtWidgets.QHBoxLayout()

        # create the button, and hook it up to the slot below.
        self._button_add = QtWidgets.QPushButton("Add Item")
        self._button_add.clicked.connect(self.add_item)
        self._button_add.setIcon(QtGui.QIcon(":/images/tango/32x32/actions/list-add"))

        hbox.addWidget(self._button_add)

        # add bottom to main window layout
        vbox.addLayout(hbox)

        # set layout on the window
        self.setLayout(vbox)

    def set_operations(self, operations):
        '''
        '''
        cnc_ops = []
        for op in operations:
            cnc_op = CncOp(op)
            cnc_ops.append(cnc_op)
            
            
        self.model = PMFSimpleTableModel(cnc_ops, self.main_window)
        self.table.setModel(self.model)
        self.table.setup()

        self.vbox.addWidget(self.table)

    def set_model(self, model):
        '''
        '''
        self.table.setModel(model)

    def get_model(self):
        '''
        '''
        return self.table.model()

    def add_item(self):
        # instruct the model to add an item
        self.table.addItem()
        
        print("ADD")
        for op in self.table.model().operations:
            print(op)


class PMFSimpleTableView(QtWidgets.QTableView):
    '''
    '''
    def __init__(self, parent=None):
        '''
        '''
        QtWidgets.QTableView.__init__(self, parent)

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
            "gcode",                    # [1] button
            "cam_op",
            "enabled",                  # [3] checkbox
            "paths",                    # [4] str
            "units",
            "cutDepth",                 # [6] float
            "ramp",                     # [7] checkbox
            "combinaison",
            "direction",
            "margin",                   # [10] float
            "width",                    # [11] float
            "del",                      # [12] button
            "up",                       # [13] button
            "down",                     # [14] button
        ]
        '''
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(2, delegate)

        delegate = PMFCheckBoxDelegate(self)
        self.setItemDelegateForColumn(3, delegate)
        
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(5, delegate)

        delegate = PMFDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(6, delegate)
        
        delegate = PMFCheckBoxDelegate(self)
        self.setItemDelegateForColumn(7, delegate)
    
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(8, delegate)
        
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(9, delegate)

        delegate = PMFDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(10, delegate)

        delegate = PMFDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(11, delegate)

        # Make the combo boxes / check boxes / others spacials always displayed.
        for k in range(self.model().rowCount(None)):
            self.openPersistentEditor(self.model().index(k, 2)) # cam_op
            self.openPersistentEditor(self.model().index(k, 3)) #   enabled
            self.openPersistentEditor(self.model().index(k, 5)) # units
            self.openPersistentEditor(self.model().index(k, 6)) #          cutDepth
            self.openPersistentEditor(self.model().index(k, 7)) #   ramp
            self.openPersistentEditor(self.model().index(k, 8)) # combinaison
            self.openPersistentEditor(self.model().index(k, 9)) # direction
            self.openPersistentEditor(self.model().index(k, 10)) #          margin
            self.openPersistentEditor(self.model().index(k, 11)) #          width

        for row in range(self.model().rowCount(None)):
            btn_gcode_op = QtWidgets.QPushButton()
            btn_gcode_op.setText("")
            btn_gcode_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/view-refresh.png'))
            btn_gcode_op.setToolTip("generate G-Code")
            btn_gcode_op.clicked.connect(self.cb_gen_gcode_op)
            self.setIndexWidget(self.model().index(row, 1), btn_gcode_op)
        
            btn_del_op = QtWidgets.QPushButton()
            btn_del_op.setText("")
            btn_del_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/edit-clear.png'))
            btn_del_op.setToolTip("Delete Op")
            btn_del_op.clicked.connect(self.cb_delete_op)
            self.setIndexWidget(self.model().index(row, 12), btn_del_op)

            btn_up_op = QtWidgets.QPushButton()
            btn_up_op.setText("")
            btn_up_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/go-up.png'))
            btn_up_op.setToolTip("Up")
            btn_up_op.clicked.connect(self.cb_move_up_op)
            self.setIndexWidget(self.model().index(row, 13), btn_up_op)

            btn_dw_op = QtWidgets.QPushButton()
            btn_dw_op.setText("")
            btn_dw_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/go-down.png'))
            btn_dw_op.setToolTip("Down")
            btn_dw_op.clicked.connect(self.cb_move_down_op)
            self.setIndexWidget(self.model().index(row, 14), btn_dw_op)

        # setup a right grid size
        vwidth = self.verticalHeader().width()
        hwidth = self.horizontalHeader().length()
        swidth = self.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        fwidth = self.frameWidth() * 2

        #self.setFixedWidth(vwidth + hwidth + swidth + fwidth)
        #self.setMinimumWidth(vwidth + hwidth + swidth + fwidth)

        self.resizeColumnsToContents() # now!

        self.setColumnWidth(0, 100)  # name
        self.setColumnWidth(4, 100)  # paths

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
        self.setup()
        
        print("DOWN")
        for op in self.model().operations:
            print(op)
        
    def cb_move_up_op(self):
        index = self.currentIndex()
        idx = index.row()
        if idx > 0:
            self.model().swapItems(idx, idx - 1)

        # to be sure to update the table... and all its delegates
        self.setup()
        
        print("UP")
        for op in self.model().operations:
            print(op)

    def addItem(self):
        self.model().addItem()
        self.setup()  # to show the editors on a new item

    def cb_gen_gcode_op(self):
        index = self.currentIndex()
        idx = index.row()
        # instruct the model to generate the g-code for all selected items
        self.model().generate_gcode()


class PMFSimpleTableModel(QtCore.QAbstractTableModel):
    '''
    model for the table view
    '''
    def __init__(self, operations, main_window):
        super(PMFSimpleTableModel, self).__init__()
        
        self.operations = operations
        self.main_window = main_window

        self.header =  [
            "name",                     # [0] str
            "gcode",                    # [1] button
            "cam_op",
            "enabled",                  # [3] checkbox
            "paths",                    # [4] str
            "units",
            "cutDepth",                 # [6] float
            "ramp",                     # [7] checkbox
            "combinaison",
            "direction",
            "margin",                   # [10] float
            "width",                    # [11] float
            "del",                      # [12] button
            "up",                       # [13] button
            "down",                     # [14] button
        ]

        self.cnt = 0



    def generate_gcode(self):
        '''
        '''    
        self.main_window.parent().cb_generate_g_code()
        
    def handleNewvalue(self, index: QtCore.QModelIndex, value: Any):
        print("--------------------------------", "handleNewvalue")

        row = index.row()
        col = index.column()

        attrib = self.header[col]

        print("handleNewvalue OLD -> %s" % (str(self.operations[row])))
        print("handleNewvalue NEW -> %s %s" % (attrib, value))

        # TODO: action on pycut GUI
        if attrib in ["enabled", "margin", "width", "combinaison", "cam_ops"]:
            cnc_op = self.operations[row]
            setattr(cnc_op, attrib, value)

            self.main_window.parent().display_cnc_ops_geometry(self.operations)

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

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.operations)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        op = self.get_operation(index)
        attr = self.get_operation_attr(index)

        # for check box, data is displayed in the "editor"
        col = index.column()

        if col == 1:  # button
            return None
        if col == 12:  # button
            return None
        if col == 13:  # button
            return None
        if col == 14:  # button
            return None

        # for checkboxes only
        if col == 3:   # checkbox
            return None
        if col == 7:   # checkbox
            return None

        if role == QtCore.Qt.DisplayRole:
            val = getattr(op, attr)

            if col == 4:  # make a string of the list
                # list of svg paths ids
                val = str(val)

            return val
        if role == QtCore.Qt.EditRole:
            val = getattr(op, attr)

            if col == 4:
                # list of svg paths ids
                val = str(val)

            return val

        return None

    def flags(self, index):
        flags = super(PMFSimpleTableModel, self).flags(index)

        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled

        return flags

    def addItem(self):
        op = CncOp({})

        self.beginInsertRows(QtCore.QModelIndex(), len(self.operations), len(self.operations))
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
  
