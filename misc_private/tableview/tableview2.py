import sys

from typing import List
from typing import Any

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


operations = [
    {
        "name": "op1",
        "paths": ["p1", "p2"],
        "type": "Pocket",
        "cut_depth": 0.125,
        "ramp_plunge": True,
        "combinaison": "Union",
        "direction": "Conventional",
        "units": "inch",
        "margin": 0.0,
    },
    {
        "name": "op2",
        "paths": ["p1", "p2"],
        "type": "Inside",
        "cut_depth": 0.125,
        "ramp_plunge": True,
        "combinaison": "Union",
        "direction": "Conventional",
        "units": "inch",
        "margin": 0.0,
        "width": 0.0,
    },
    {
        "name": "op3",
        "paths": ["p1", "p2"],
        "type": "Outside",
        "cut_depth": 0.125,
        "ramp_plunge": True,
        "combinaison": "Union",
        "direction": "Conventional",
        "units": "inch",
        "margin": 0.0,
        "width": 0.0,
    },
    {
        "name": "op4",
        "paths": ["p4"],
        "type": "Engrave",
        "cut_depth": 1.125,
        "ramp_plunge": False,
        "combinaison": "Difference",
        "direction": "Climb",
        "units": "mm",
    },
]


class CncOp:
    def __init__(self, data):
        self.name = data.get("name", "op")
        self.cam_op = data.get("type", "Pocket")
        self.cut_depth = data.get("cut_depth", 0.125)
        self.paths = data.get("paths", [])
        self.ramp_plunge = data.get("ramp_plunge", False)
        self.combinaison = data.get("combinaison", "Union")
        self.direction = data.get("direction", "Conventional")
        self.units = data.get("units", "inch")
        self.margin = data.get("margin", 0.0)

        # not in the data
        self.enabled = False

    def put_value(self, attr, value):
        """ """
        setattr(self, attr, value)

    def __str__(self):
        """ """
        return "op: %s %s [%f] %s %s %s %f" % (
            self.name,
            self.cam_op,
            self.cut_depth,
            self.ramp,
            self.enabled,
            self.combinaison,
            self.cut_depth,
        )


class PMFDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    """ """

    def __init__(self, parent):
        """ """
        QtWidgets.QDoubleSpinBox.__init__(self, parent)

        self.o = None
        self.attribute = ""

        self.setMinimum(0)
        self.setMaximum(100)
        self.setSingleStep(0.001)
        self.setDecimals(3)

        self.valueChanged.connect(self.cb_spinbox)

    def cb_disconnect(self):
        """ """
        self.valueChanged.disconnect(self.cb_spinbox)

    def cb_connect(self):
        """ """
        self.valueChanged.connect(self.cb_spinbox)

    def assign_object(self, o):
        """ """
        self.o = o

    def assign_object_attribute(self, attribute):
        """ """
        self.attribute = attribute

    def set_value(self):
        """ """
        self.cb_disconnect()

        try:
            val = getattr(self.o, self.attribute)
        except Exception:
            val = 0

        self.setValue(val)

        self.cb_connect()

    def cb_spinbox(self):
        """ """
        val = self.value()
        self.o.put_value(self.attribute, val)


class PMFCheckBox(QtWidgets.QCheckBox):
    """ """

    def __init__(self, parent):
        """ """
        QtWidgets.QCheckBox.__init__(self, parent)

        self.o = None
        self.attribute = ""

        self.stateChanged.connect(self.cb_checkbox)

    def cb_disconnect(self):
        """ """
        self.stateChanged.disconnect(self.cb_checkbox)

    def cb_connect(self):
        """ """
        self.stateChanged.connect(self.cb_checkbox)

    def assign_object(self, o):
        """ """
        self.o = o

    def assign_object_attribute(self, attribute):
        """ """
        self.attribute = attribute

    def set_value(self):
        """ """
        self.cb_disconnect()

        uival = {True: QtCore.Qt.Checked, False: QtCore.Qt.Unchecked}[
            getattr(self.o, self.attribute)
        ]

        self.setCheckState(uival)

        self.cb_connect()

    def cb_checkbox(self, index):
        """ """
        val = {QtCore.Qt.Checked: True, QtCore.Qt.Unchecked: False}[self.checkState()]
        self.o.put_value(self.attribute, val)


class PMFComboBox(QtWidgets.QComboBox):
    """ """

    def __init__(self, parent, items):
        """ """
        QtWidgets.QComboBox.__init__(self, parent)

        self.o = None
        self.attribute = ""

        self.items = items

        self.currentIndexChanged.connect(self.cb_combobox)

    def cb_disconnect(self):
        """ """
        self.currentIndexChanged.disconnect(self.cb_combobox)

    def cb_connect(self):
        """ """
        self.currentIndexChanged.connect(self.cb_combobox)

    def assign_object(self, o):
        """ """
        self.o = o

    def assign_object_attribute(self, attribute):
        """ """
        self.attribute = attribute

    def fill_control(self):
        """ """
        self.cb_disconnect()
        self.clear()
        self.add_items(self.items)
        self.cb_connect()

    def set_value(self):
        """ """
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
        """ """
        val = self.itemText(index)

        self.o.put_value(self.attribute, val)


class PMFCheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(
        self, parent, option, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
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
        checkLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        checkLayout.setContentsMargins(0, 0, 0, 0)

        # to flush an "setModelData" in place - it works!
        editor.stateChanged.connect(self.onEditorStateChanged)

        return checkWidget

    def onEditorStateChanged(self):
        editor = self.sender()
        if editor:
            print("onEditorStateChanged - PMFCheckBoxDelegate - editor", editor)
            checkWidget = editor.parent()
            self.commitData.emit(checkWidget)

    def setEditorData(
        self,
        checkWidget: QtWidgets.QWidget,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        checkBoxItem = checkWidget.layout().itemAt(0)
        checkBox: PMFCheckBox = checkBoxItem.widget()
        checkBox.set_value()

    def setModelData(
        self,
        checkWidget: QtWidgets.QWidget,
        model,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        print("PMFCheckBoxDelegate::setModelData - editor", checkWidget)

        checkBoxItem = checkWidget.layout().itemAt(0)
        checkBox: PMFCheckBox = checkBoxItem.widget()

        model.handleNewvalue(index, checkBox.isChecked())
        return

    def updateEditorGeometry(
        self, editor, option, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
        editor.setGeometry(option.rect)


class PMFComboBoxDelegate(QtWidgets.QItemDelegate):
    def createEditor(
        self, parent, option, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
        col = index.column()

        self.items = []
        if col == 2:
            self.items = [
                "Pocket",
                "Inside",
                "Outside",
                "Engrave",
                "Drill",
                "Peck",
                "Helix",
            ]
        if col == 7:
            self.items = ["Union", "Intersection", "Difference", "Xor"]
        if col == 8:
            self.items = ["Conventional", "Climb"]
        if col == 9:
            self.items = ["inch", "mm"]

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

    def setEditorData(
        self,
        comboBox: PMFComboBox,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        comboBox.set_value()

    def setModelData(
        self,
        comboBox: PMFComboBox,
        model,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        model.handleNewvalue(index, comboBox.currentText())
        return

    def updateEditorGeometry(
        self,
        comboBox: PMFComboBox,
        option,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        comboBox.setGeometry(option.rect)


class PMFDoubleSpinBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(
        self, parent, option, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
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

    def setEditorData(
        self,
        spinBox: PMFDoubleSpinBox,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        spinBox.set_value()

    def setModelData(
        self,
        spinBox: PMFDoubleSpinBox,
        model,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        model.handleNewvalue(index, spinBox.value())
        return

    def updateEditorGeometry(
        self,
        editor: PMFDoubleSpinBox,
        option,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        editor.setGeometry(option.rect)


class PMFTableViewManager(QtWidgets.QWidget):

    def __init__(self, parent):
        """ """
        QtWidgets.QWidget.__init__(self, parent)

        cnc_ops = []
        for op in operations:
            cnc_op = CncOp(op)
            cnc_ops.append(cnc_op)

        # main section of the window
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        # let's add two views of the same data source we just created:
        self.table = PMFSimpleTableView(self)
        self.table.resizeColumnsToContents()
        self.table.setMinimumWidth(800)

        self.model = PMFSimpleTableModel(cnc_ops)
        self.table.setModel(self.model)
        self.table.setup()

        vbox.addWidget(self.table)

        # bottom section of the window:
        # let's have a text input and a pushbutton that add an item to our model.
        hbox = QtWidgets.QHBoxLayout()

        # create the button, and hook it up to the slot below.
        self._button_add = QtWidgets.QPushButton("Add Item")
        self._button_add.clicked.connect(self.add_item)
        self._button_add.setIcon(QtGui.QIcon("./images/tango/32x32/actions/list-add"))

        # create the button, and hook it up to the slot below.
        self._button_up = QtWidgets.QPushButton("")
        self._button_up.clicked.connect(self.up_item)
        self._button_up.setIcon(QtGui.QIcon("./images/tango/32x32/actions/go-up"))

        # create the button, and hook it up to the slot below.
        self._button_down = QtWidgets.QPushButton("")
        self._button_down.clicked.connect(self.down_item)
        self._button_down.setIcon(QtGui.QIcon("./images/tango/32x32/actions/go-down"))

        hbox.addWidget(self._button_add)
        hbox.addWidget(self._button_up)
        hbox.addWidget(self._button_down)

        # add bottom to main window layout
        vbox.addLayout(hbox)

        # set layout on the window
        self.setLayout(vbox)

    def set_operations(self, operations):
        """ """
        cnc_ops = []
        for op in operations:
            cnc_op = CncOp(op)
            cnc_ops.append(cnc_op)

        self.model = PMFSimpleTableModel(cnc_ops)
        self.table.setModel(self.model)
        self.table.setup()

        self.vbox.addWidget(self._table)

    def set_model(self, model):
        """ """
        self.table.setModel(model)

    def add_item(self):
        # instruct the model to add an item
        self.table.add_item()

        print("ADD")
        for op in self.table.model().operations:
            print(op)

    def del_item(self):
        index = self.table.currentIndex()
        idx = index.row()
        # instruct the model to del an item
        self.table.del_item(idx)

        print("DEL")
        for op in self.table.model().operations:
            print(op)

    def down_item(self):
        index = self.table.currentIndex()
        idx = index.row()
        if idx < self.table.model().rowCount(None) - 1:
            self.table.swap_items(idx, idx + 1)

        # to be sure to update the table... and all its delegates
        self.table.setup()

        print("DOWN")
        for op in self.table.model().operations:
            print(op)

    def up_item(self):
        index = self.table.currentIndex()
        idx = index.row()
        if idx > 0:
            self.table.swap_items(idx, idx - 1)

        # to be sure to update the table... and all its delegates
        self.table.setup()

        print("UP")
        for op in self.table.model().operations:
            print(op)


class PMFSimpleTableView(QtWidgets.QTableView):
    """ """

    def __init__(self, parent=None):
        """ """
        QtWidgets.QTableView.__init__(self, parent)

        self.parent = parent

        self.resizeColumnsToContents()
        # Fixes the width of columns and the height of rows.
        try:
            # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
            # self.verticalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
            pass
        except Exception:
            pass  # PySide

        self.setAlternatingRowColors(True)

    def setup(self):
        """ """
        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(2, delegate)

        delegate = PMFCheckBoxDelegate(self)
        self.setItemDelegateForColumn(3, delegate)

        delegate = PMFDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(5, delegate)

        delegate = PMFCheckBoxDelegate(self)
        self.setItemDelegateForColumn(6, delegate)

        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(7, delegate)

        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(8, delegate)

        delegate = PMFComboBoxDelegate(self)
        self.setItemDelegateForColumn(9, delegate)

        delegate = PMFDoubleSpinBoxDelegate(self)
        self.setItemDelegateForColumn(10, delegate)

        # Make the combo boxes / check boxes / others spacials always displayed.
        for k in range(self.model().rowCount(None)):
            self.openPersistentEditor(self.model().index(k, 2))
            self.openPersistentEditor(self.model().index(k, 3))
            self.openPersistentEditor(self.model().index(k, 5))
            self.openPersistentEditor(self.model().index(k, 6))
            self.openPersistentEditor(self.model().index(k, 7))
            self.openPersistentEditor(self.model().index(k, 8))
            self.openPersistentEditor(self.model().index(k, 9))
            self.openPersistentEditor(self.model().index(k, 10))

        for row in range(self.model().rowCount(None)):
            btn_gcode_op = QtWidgets.QPushButton()
            btn_gcode_op.setText("")
            btn_gcode_op.setIcon(
                QtGui.QIcon("./images/tango/22x22/actions/view-refresh.png")
            )
            btn_gcode_op.setToolTip("generate G-Code")
            btn_gcode_op.clicked.connect(self.cb_gen_gcode_op)
            self.setIndexWidget(self.model().index(row, 1), btn_gcode_op)

            btn_del_op = QtWidgets.QPushButton()
            btn_del_op.setText("")
            btn_del_op.setIcon(
                QtGui.QIcon("./images/tango/22x22/actions/edit-clear.png")
            )
            btn_del_op.setToolTip("Delete Op")
            btn_del_op.clicked.connect(self.cb_delete_op)
            self.setIndexWidget(self.model().index(row, 11), btn_del_op)

        # setup a right grid size
        vwidth = self.verticalHeader().width()
        hwidth = self.horizontalHeader().length()
        swidth = self.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        fwidth = self.frameWidth() * 2

        # self.setFixedWidth(vwidth + hwidth + swidth + fwidth)
        # self.setMinimumWidth(vwidth + hwidth + swidth + fwidth)

        self.resizeColumnsToContents()  # now!

        self.setColumnWidth(0, 100)  # name
        self.setColumnWidth(4, 100)  # paths

    def add_item(self):
        self.model().add_item()
        self.setup()  # to show the editors on a new item

    def del_item(self, idx):
        self.model().del_item(idx)

    def swap_items(self, idx1, idx2):
        self.model().swap_items(idx1, idx2)

    def cb_delete_op(self):
        index = self.currentIndex()
        idx = index.row()
        # instruct the model to del this item
        self.del_item(idx)

    def cb_gen_gcode_op(self):
        index = self.currentIndex()
        idx = index.row()
        # instruct the model to generate the g-code for this item
        pass  # TODO

    def cb_select(self):
        index = self.currentIndex()
        idx = index.row()
        # re-generate geometries and preview genometries for all selected
        pass  # TODO


class PMFSimpleTableModel(QtCore.QAbstractTableModel):
    """
    model for the table view
    """

    def __init__(self, operations):
        super(PMFSimpleTableModel, self).__init__()

        self.operations = operations

        self.header = [
            "name",  # [0] str
            "gen gcode",  # [1] button
            "cam_op",
            "enabled",  # [3] checkbox
            "paths",  # [4] str
            "cut_depth",  # [5] float
            "ramp_plunge",  # [6] checkbox
            "combinaison",
            "direction",
            "units",
            "margin",  # [10] float
            "del",  # [11] buttont
        ]

        self.cnt = 0

    def handleNewvalue(self, index: QtCore.QModelIndex, value: Any):
        print("--------------------------------", "handleNewvalue")

        row = index.row()
        col = index.column()

        attrib = self.header[col]

        print("handleNewvalue OLD -> %s" % (str(self.operations[row])))
        print("handleNewvalue NEW -> %s %s" % (attrib, value))

        # TODO: action on pycut GUI

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

    def headerData(
        self,
        col,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.ItemDataRole.EditRole,
    ):
        if (
            orientation == QtCore.Qt.Orientation.Horizontal
            and role == QtCore.Qt.ItemDataRole.DisplayRole
        ):
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.operations)

    def columnCount(self, parent):
        return len(self.header)

    def setData(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        value,
        role: int = QtCore.Qt.ItemDataRole.EditRole,
    ):
        """
        for the cells without delegate
        """
        op = self.get_operation(index)
        attr = self.get_operation_attr(index)

        if role == QtCore.Qt.ItemDataRole.EditRole:
            setattr(op, attr, value)

    def data(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        role: int = QtCore.Qt.ItemDataRole.EditRole,
    ) -> Any:
        op = self.get_operation(index)
        attr = self.get_operation_attr(index)

        # for check box, data is displayed in the "editor"
        col = index.column()

        if col == 1:  # button
            return None
        if col == 11:  # button
            return None

        # for checkboxes only
        if col == 3:  # checkbox
            return None
        if col == 6:  # checkbox
            return None

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            val = getattr(op, attr)

            if col == 4:  # make a string of the list
                # list of svg paths ids
                val = str(val)

            return val
        if role == QtCore.Qt.ItemDataRole.EditRole:
            val = getattr(op, attr)

            if col == 4:
                # list of svg paths ids
                val = str(val)

            return val

        return None

    def flags(self, index):
        flags = super(PMFSimpleTableModel, self).flags(index)

        flags |= QtCore.Qt.ItemFlag.ItemIsEditable
        flags |= QtCore.Qt.ItemFlag.ItemIsSelectable
        flags |= QtCore.Qt.ItemFlag.ItemIsEnabled
        flags |= QtCore.Qt.ItemFlag.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemFlag.ItemIsDropEnabled

        return flags

    def add_item(self):
        op = CncOp({})

        self.beginInsertRows(
            QtCore.QModelIndex(), len(self.operations), len(self.operations)
        )
        self.operations.append(op)
        self.endInsertRows()

    def del_item(self, idx):
        op = self.operations[idx]

        self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
        self.operations.remove(op)
        self.endRemoveRows()

        self.dump()

    def swap_items(self, idx1, idx2):
        self.beginResetModel()
        self.operations[idx1], self.operations[idx2] = (
            self.operations[idx2],
            self.operations[idx1],
        )
        self.endResetModel()

        self.dump()

    def get_operation(self, index):
        return self.operations[index.row()]

    def get_operation_attr(self, index):
        return self.header[index.column()]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.view = PMFTableViewManager(self)
        self.setCentralWidget(self.view)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
