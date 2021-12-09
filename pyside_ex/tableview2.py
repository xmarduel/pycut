import sys

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


operations = [
    {
      "Name": "op1",
      "paths": ["p1", "p2"],
      "type": "Pocket",
      "Deep": 0.125,       
      "RampPlunge": True,
      "Combine": "Union",
      "Direction": "Conventional",
      "Units": "inch",
      "Margin": 0.0
    },
    {
      "Name": "op2",
      "paths": ["p1", "p2"],
      "type": "Inside",
      "Deep": 0.125,
      "RampPlunge": True,
      "Combine": "Union",
      "Direction": "Conventional",
      "Units": "inch",
      "Margin": 0.0,
      "Width": 0.0
    },
    {
      "Name": "op3",
      "paths": ["p1", "p2"],
      "type": "Outside",
      "Deep": 0.125,
      "RampPlunge": True,
      "Combine": "Union",
      "Direction": "Conventional",
      "Units": "inch",
      "Margin": 0.0,
      "Width": 0.0
    },
    {
      "Name": "op4",
      "paths": ["p1", "p2"],
      "type": "Engrave",
      "Deep": 0.125,
      "RampPlunge": False,
      "Combine": "Union",
      "Direction": "Conventional",
      "Units": "mm"
    }
]

class CncOp:
    def __init__(self):
        self.Name = "op1"
        self.paths = ["p1", "p2"]
        self.cam_op = "Pocket"
        self.Deep = 0.125      
        self.RampPlunge = True
        self.Combine = "Union"
        self.Direction = "Conventional"
        self.Units = "inch"
        self.Margin = 0.0
        
    def set_data(self, json):
        self.Name = json["Name"]
        self.paths = str(json["paths"])
        self.cam_op = json["type"]
        self.Deep = json["Deep"]    
        self.RampPlunge = json["RampPlunge"]
        self.Combine = json["Combine"]
        self.Direction = json["Direction"]
        self.Units = json["Units"]
        self.Margin = json.get("Margin", 0.0)

    def put_value(self, attr, value):
        setattr(self, attr, value)
    
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
    def createEditor(self, parent, option, index):
        editor = PMFCheckBox(parent)

        op = index.model().get_operation(index)
        attr = index.model().get_operation_attr(index)

        editor.assign_object(op)
        editor.assign_object_attribute(attr)

        return editor

    def setEditorData(self, checkBox, index):
        checkBox.set_value()

    def setModelData(self, checkBox, model, index):
        return

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class PMFComboBoxDelegate(QtWidgets.QItemDelegate):
    def createEditor(self, parent, option, index):
        col = index.column()

        self.items = []
        if col == 1:
            self.items = ["Pocket", "Inside", "Outside", "Engrave"]
        if col == 5:
            self.items = ["Union", "Intersection", "Difference", "Xor"]
        if col == 6:
            self.items = ["Conventional", "Climb"]
        if col == 7:
            self.items = ["inch", "mm"]

        editor = PMFComboBox(parent, self.items)

        op = index.model().get_operation(index)
        attr = index.model().get_operation_attr(index)

        editor.assign_object(op)
        editor.assign_object_attribute(attr)
        editor.fill_control()

        return editor

    def setEditorData(self, comboBox, index):
        comboBox.set_value()

    def setModelData(self, comboBox, model, index):
        return

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class PMFTableViewManager(QtWidgets.QWidget):

    def __init__(self, parent):
        '''
        '''
        QtWidgets.QWidget.__init__(self, parent)

        self.model = None

        # main section of the window
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        # let's add two views of the same data source we just created:
        self._table = PMFSimpleTable(self)
        #self._table.resizeColumnsToContents()
        #self._table.setMinimumWidth(800)
        
        cnc_ops = []
        for op in operations:
            cnc_op = CncOp()
            cnc_op.set_data(op)
            cnc_ops.append(cnc_op)
            
            
        self.model = PMFSimpleTableModel(cnc_ops)
        self._table.setModel(self.model)
        self._table.setup()

        vbox.addWidget(self._table)

        # bottom section of the window:
        # let's have a text input and a pushbutton that add an item to our model.
        hbox = QtWidgets.QHBoxLayout()

        # create the button, and hook it up to the slot below.
        self._button_add = QtWidgets.QPushButton("Add Item")
        self._button_add.clicked.connect(self.add_item)
        self._button_add.setIcon(QtGui.QIcon(":/images/tango/32x32/actions/list-add"))

        # create the button, and hook it up to the slot below.
        self._button_up = QtWidgets.QPushButton("")
        self._button_up.clicked.connect(self.up_item)
        self._button_up.setIcon(QtGui.QIcon(":/images/tango/32x32/actions/go-up"))

        # create the button, and hook it up to the slot below.
        self._button_down = QtWidgets.QPushButton("")
        self._button_down.clicked.connect(self.down_item)
        self._button_down.setIcon(QtGui.QIcon(":/images/tango/32x32/actions/go-down"))

        self._button_del = QtWidgets.QPushButton("")
        self._button_del.clicked.connect(self.del_item)
        self._button_del.setIcon(QtGui.QIcon(":/images/tango/32x32/actions/list-remove"))

        hbox.addWidget(self._button_add)
        hbox.addWidget(self._button_up)
        hbox.addWidget(self._button_down)
        hbox.addWidget(self._button_del)

        # add bottom to main window layout
        vbox.addLayout(hbox)

        # set layout on the window
        self.setLayout(vbox)

    def hide_mgmt_btns(self):
        '''
        '''
        self._button_add.hide()
        self._button_up.hide()
        self._button_down.hide()
        self._button_del.hide()

    def show_mgmt_btns(self):
        '''
        '''
        self._button_add.show()
        self._button_up.show()
        self._button_down.show()
        self._button_del.show()

    def set_model(self, model):
        '''
        '''
        self._table.setModel(model)

    def add_item(self):
        # instruct the model to add an item
        self._table.addItem()

    def del_item(self):
        index = self._table.currentIndex()
        idx = index.row()
        # instruct the model to del an item
        self._table.delItem(idx)

    def down_item(self):
        index = self._table.currentIndex()
        idx = index.row()
        if idx < self._table.model().rowCount(None) - 1:
            self._table.swapItems(idx, idx + 1)

        # to be sure to update the table... # BUGGY sonce
        #model = PMFSimpleTableModel(s)
        #self.set_model(model)
        #self.setup_table()

    def up_item(self):
        index = self._table.currentIndex()
        idx = index.row()
        if idx > 0:
            self._table.swapItems(idx, idx - 1)

        # to be sure to update the table... # BUGGY sonce
        #model = PMFSimpleTableModel()
        #self.set_model(model)
        #self.setup_table()


class PMFSimpleTable(QtWidgets.QTableView):
    '''
    '''
    def __init__(self, parent=None):
        '''
        '''
        QtWidgets.QTableView.__init__(self, parent)

        self.parent = parent

        #self.resizeColumnsToContents()
        # Fixes the width of columns and the height of rows.
        try:
            self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
            self.verticalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
        except Exception:
            pass  # PySide

        # unlike the previous tutorial, we'll do background colours 'properly'. ;)
        self.setAlternatingRowColors(True)

    def setup(self):
        '''
        '''
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(1, delegate)
        
        delegate = PMFCheckBoxDelegate(self)
        self.setItemDelegateForColumn(4, delegate)
    
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(5, delegate)
        
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(6, delegate)
        
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(7, delegate)

        # Make the combo boxes / check boxes / others spacials always displayed.
        for k in range(self.model().rowCount(None)):
            self.openPersistentEditor(self.model().index(k, 1))
            self.openPersistentEditor(self.model().index(k, 4))
            self.openPersistentEditor(self.model().index(k, 5))
            self.openPersistentEditor(self.model().index(k, 6))
            self.openPersistentEditor(self.model().index(k, 7))

        

        # setup a right grid size
        vwidth = self.verticalHeader().width()
        hwidth = self.horizontalHeader().length()
        swidth = self.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        fwidth = self.frameWidth() * 2

        #self.setFixedWidth(vwidth + hwidth + swidth + fwidth)
        self.setMinimumWidth(vwidth + hwidth + swidth + fwidth)

    def addItem(self):
        self.model().addItem()
        self.setup()  # to show the editors on a new item

    def delItem(self, idx):
        self.model().delItem(idx)

    def swapItems(self, idx1, idx2):
        self.model().swapItems(idx1, idx2)


class PMFSimpleTableModel(QtCore.QAbstractTableModel):
    '''
    model for the table view
    '''
    def __init__(self, operations):
        super(PMFSimpleTableModel, self).__init__()
        
        self.operations = operations

        self.header =  ["Name",
          "cam_op",
          "paths",
          "Deep",
          "RampPlunge",
          "Combine",
          "Direction",
          "Units",
          "Margin"
        ]
        
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
        
        if col == 4:
            return None

        if role == QtCore.Qt.DisplayRole:
            val = getattr(op, attr)
            return val
        if role == QtCore.Qt.EditRole:
            val = getattr(op, attr)
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
        op = CncOp()

        self.beginInsertRows(QtCore.QModelIndex(), len(self.operations), len(self.operations))
        self.operations.append(op)
        self.endInsertRows()

    def delItem(self, idx):
        op = self.operations[idx]

        self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
        self.operations.remove(op)
        self.endRemoveRows()

    def swapItems(self, idx1, idx2):
        self.operations[idx1], self.operations[idx2] = self.operations[idx2], self.operations[idx1]
        if idx1 < idx2:
            self.dataChanged.emit(self.index(idx1, 0), self.index(idx2, 0))   # BUGGY : "delegate" editors not updated
        else:
            self.dataChanged.emit(self.index(idx2, 0), self.index(idx1, 0))   # BUGGY : "delegate" editors not updated

    def get_operation(self, index):
        return self.operations[index.row()]

    def get_operation_attr(self, index):
        return self.header[index.column()]
  

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.view = PMFTableViewManager(self)
        self.setCentralWidget(self.view)
  
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()