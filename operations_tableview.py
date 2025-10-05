from typing import List
from typing import Any
from typing import Dict
from typing import cast

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from svgviewer import SvgViewer


class OpItem:
    def __init__(self, data):
        self.name = data.get("name", "op")
        self.cam_op = data.get("type", "Pocket")
        self.cut_depth = data.get("cut_depth", 3.175)
        self.paths = data.get("paths", [])
        self.ramp_plunge = data.get("ramp_plunge", False)
        self.combinaison = data.get("combinaison", "Union")
        self.direction = data.get("direction", "Conventional")
        self.units = data.get("units", "mm")
        self.margin = data.get("margin", 0.0)
        self.width = data.get("width", 0.0)

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
            self.ramp_plunge,
            self.enabled,
            self.combinaison,
            self.cut_depth,
        )

    def to_dict(self) -> Dict[str, Any]:
        """ """
        return {
            "name": self.name,
            "type": self.cam_op,
            "cut_depth": self.cut_depth,
            "paths": self.paths,
            "ramp_plunge": self.ramp_plunge,
            "combinaison": self.combinaison,
            "direction": self.direction,
            "units": self.units,
            "margin": self.margin,
            "width": self.width,
        }


class PyCutDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    """ """

    def __init__(self, parent):
        """ """
        QtWidgets.QDoubleSpinBox.__init__(self, parent)

        self.o = None
        self.attribute = ""

        self.setMinimum(0)
        self.setMaximum(100)
        self.setSingleStep(0.1)
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


class PyCutCheckBox(QtWidgets.QCheckBox):
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


class PyCutComboBox(QtWidgets.QComboBox):
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
        self.addItems(self.items)
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


class PyCutDoubleSpinBoxDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.xeditors = {}

    def createEditor(
        self, parent, option, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
        editor = PyCutDoubleSpinBox(parent)

        model = cast(PyCutSimpleTableModel, index.model())

        op = model.get_operation(index)
        attr = model.get_operation_attr(index)

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

    def setEditorData(
        self,
        spinBox: PyCutDoubleSpinBox,  # type: ignore [override]
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        spinBox.set_value()

    def setModelData(
        self,
        spinBox: PyCutDoubleSpinBox,  # type: ignore [override]
        model,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        model.handleNewvalue(index, spinBox.value())

    def updateEditorGeometry(
        self,
        editor: PyCutDoubleSpinBox,  # type: ignore [override]
        option,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        editor.setGeometry(option.rect)


class PyCutCheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(
        self, parent, option, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
        editor = PyCutCheckBox(parent)

        model = cast(PyCutSimpleTableModel, index.model())

        op = model.get_operation(index)
        attr = model.get_operation_attr(index)

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
            checkWidget = editor.parent()
            self.commitData.emit(checkWidget)

    def setEditorData(
        self,
        checkWidget: QtWidgets.QWidget,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        checkBoxItem = checkWidget.layout().itemAt(0)
        checkBox = cast(PyCutCheckBox, checkBoxItem.widget())
        checkBox.set_value()

    def setModelData(
        self,
        checkWidget: QtWidgets.QWidget,
        model,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        checkBoxItem = checkWidget.layout().itemAt(0)
        checkBox = cast(PyCutCheckBox, checkBoxItem.widget())

        model.handleNewvalue(index, checkBox.isChecked())

    def updateEditorGeometry(
        self, editor, option, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
        editor.setGeometry(option.rect)


class PyCutComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.xeditors = {}

    def createEditor(
        self, parent, option, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
        col = index.column()

        self.items = []
        if col == 1:
            self.items = [
                "Pocket",
                "Inside",
                "Outside",
                "Engrave",
                "Drill",
                "Peck",
                "Helix",
            ]
        if col == 4:
            self.items = ["inch", "mm"]
        if col == 7:
            self.items = ["Union", "Intersection", "Difference", "Xor"]
        if col == 8:
            self.items = ["Conventional", "Climb"]

        editor = PyCutComboBox(parent, self.items)

        model = cast(PyCutSimpleTableModel, index.model())

        op = model.get_operation(index)
        attr = model.get_operation_attr(index)

        editor.assign_object(op)
        editor.assign_object_attribute(attr)
        editor.fill_control()

        # to flush a "setModelData" in place - it works! but model still has old value -
        editor.currentIndexChanged.connect(self.onEditorCurrentIndexChanged)

        self.xeditors[(index.row(), index.column())] = editor

        return editor

    def onEditorCurrentIndexChanged(self, idx):
        editor = self.sender()
        if editor:
            self.commitData.emit(editor)

    def setEditorData(
        self,
        comboBox: PyCutComboBox,  # type: ignore [override]
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        comboBox.set_value()

    def setModelData(
        self,
        comboBox: PyCutComboBox,  # type: ignore [override]
        model,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        model.handleNewvalue(index, comboBox.currentText())
        return

    def updateEditorGeometry(
        self,
        comboBox: PyCutComboBox,  # type: ignore [override]
        option,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ):
        comboBox.setGeometry(option.rect)


class PyCutOperationsTableViewManager(QtWidgets.QWidget):
    def __init__(self, parent):
        """ """
        super().__init__(parent)

        self.mainwindow = None
        self.svg_viewer: SvgViewer = None

        self.model = None

        # main section of the window
        vbox = self.vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(10)

        # let's add two views of the same data source we just created:
        self.table = PyCutSimpleTableView(self)

        # bottom section of the window:
  
        # create the button, and hook it up to the slot below.
        self._button_add = QtWidgets.QPushButton("Create Operation")
        self._button_add.clicked.connect(self.add_item)
        self._button_add.setIcon(
            QtGui.QIcon(":/images/tango/22x22/categories/applications-system.png")
        )

        self._button_gen = QtWidgets.QPushButton("Generate GCode")
        self._button_gen.clicked.connect(self.gen_gcode)
        self._button_gen.setIcon(QtGui.QIcon(":/images/milling-machine-op.png"))

        # add bottom to main window layout
        vbox.addWidget(self._button_gen)
        vbox.addWidget(self._button_add)
        vbox.addWidget(self.table)

        vbox.setStretch(2, 1)

        # set layout on the window
        self.setLayout(vbox)

    def set_svg_viewer(self, svg_viewer: SvgViewer):
        """ """
        self.svg_viewer = svg_viewer
        self.mainwindow = svg_viewer.mainwindow

    def set_operations(self, operations: List[Dict[str, str]]):
        """ """
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
        """
        returns the list of operations ready to br saved as json data
        """
        ops = []

        for operation in self.get_model_operations():
            op = operation.to_dict()
            ops.append(op)

        return ops

    def set_model(self, model):
        """ """
        self.table.setModel(model)

    def get_model(self) -> "PyCutSimpleTableModel":
        """ """
        return self.table.model()

    def get_model_operations(self) -> List[OpItem]:
        """ """
        return self.get_model().operations

    def add_item(self):
        """
        instruct the model to add an item
        """
        paths = self.svg_viewer.get_selected_items_ids()
        self.table.add_item({"paths": paths})

        print("ADD")
        for op in self.get_model_operations():
            print(op)

    def gen_gcode(self):
        """ """
        # instruct the model to generate the g-code for all selected items
        self.model.generate_gcode()


class PyCutSimpleTableView(QtWidgets.QTableView):
    """ """

    def __init__(self, parent: PyCutOperationsTableViewManager):
        """ """
        super().__init__(parent)

        self.manager = parent

        # Fixes the width of columns and the height of rows.
        try:
            # self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
            # self.verticalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
            pass
        except Exception:
            pass  # PySide

        self.setAlternatingRowColors(True)

        self.resizeColumnsToContents()
        self.setMinimumWidth(800)

    def setup(self):
        """
        self.header =  [
            "name",                     # [0] str
            "cam_op",
            "enabled",                  # [2] checkbox
            "paths",                    # [3] str
            "units",
            "cut_depth",                # [5] float
            "ramp_plunge",              # [6] checkbox
            "combinaison",
            "direction",
            "margin",                   # [9] float
            "width",                    # [10] float
            "del",                      # [11] button
            "up",                       # [12] button
            "down",                     # [13] button
        ]
        """
        self.delegate_col_op = delegate = PyCutComboBoxDelegate(self)
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
        """ """
        # Make the combo boxes / check boxes / others specials always displayed.
        for k in range(self.model().rowCount(None)):
            self.openPersistentEditor(self.model().index(k, 1))  # cam_op
            self.openPersistentEditor(self.model().index(k, 2))  #   enabled

            # self.openPersistentEditor(self.model().index(k, 3))  #   paths

            self.openPersistentEditor(self.model().index(k, 4))  # units
            self.openPersistentEditor(self.model().index(k, 5))  #       cut_depth
            self.openPersistentEditor(self.model().index(k, 6))  #   ramp
            self.openPersistentEditor(self.model().index(k, 7))  # combinaison
            self.openPersistentEditor(self.model().index(k, 8))  # direction
            self.openPersistentEditor(self.model().index(k, 9))  #      margin
            self.openPersistentEditor(self.model().index(k, 10))  #      width

        for row in range(self.model().rowCount(None)):
            btn_del_op = QtWidgets.QPushButton()
            btn_del_op.setText("")
            btn_del_op.setIcon(
                QtGui.QIcon(":/images/tango/22x22/actions/edit-clear.png")
            )
            btn_del_op.setToolTip("Delete Op")
            btn_del_op.clicked.connect(self.cb_delete_op)
            self.setIndexWidget(self.model().index(row, 11), btn_del_op)

            btn_up_op = QtWidgets.QPushButton()
            btn_up_op.setText("")
            btn_up_op.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/go-up.png"))
            btn_up_op.setToolTip("Up")
            btn_up_op.clicked.connect(self.cb_move_up_op)
            self.setIndexWidget(self.model().index(row, 12), btn_up_op)

            btn_dw_op = QtWidgets.QPushButton()
            btn_dw_op.setText("")
            btn_dw_op.setIcon(QtGui.QIcon(":/images/tango/22x22/actions/go-down.png"))
            btn_dw_op.setToolTip("Down")
            btn_dw_op.clicked.connect(self.cb_move_down_op)
            self.setIndexWidget(self.model().index(row, 13), btn_dw_op)

        self.resizeColumnsToContents()  # now!

        self.setColumnWidth(3, 90)  # paths
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.enable_disable_cells()
        self.enable_disable_drill_and_peck_ops()

    def cb_delete_op(self):
        index = self.currentIndex()
        idx = index.row()
        # instruct the model to del an item
        self.model().del_item(idx)

        print("DEL")
        for op in self.model().operations:
            print(op)

    def cb_move_down_op(self):
        index = self.currentIndex()
        idx = index.row()
        if idx < self.model().rowCount(None) - 1:
            self.model().swap_items(idx, idx + 1)

        # to be sure to update the table... and all its delegates
        self.setup_persistent_editors()

        print("DOWN")
        for op in self.model().operations:
            print(op)

    def cb_move_up_op(self):
        index = self.currentIndex()
        idx = index.row()
        if idx > 0:
            self.model().swap_items(idx, idx - 1)

        # to be sure to update the table... and all its delegates
        self.setup_persistent_editors()

        print("UP")
        for op in self.model().operations:
            print(op)

    def add_item(self, op_data):
        self.model().add_item(op_data)
        self.setup_persistent_editors()  # to show the editors on a new item

    def enable_disable_cells(self):
        margin = {
            "Pocket": True,
            "Inside": True,
            "Outside": True,
            "Engrave": False,
            "Drill": False,
            "Peck": False,
            "Helix": False,
        }
        width = {
            "Pocket": False,
            "Inside": True,
            "Outside": True,
            "Engrave": False,
            "Drill": False,
            "Peck": False,
            "Helix": True,
        }

        for row in range(self.model().rowCount(None)):
            op = self.model().operations[row]
            cam_op = op.cam_op

            self.delegate_col_margin.xeditors[(row, 9)].setEnabled(margin[cam_op])
            self.delegate_col_width.xeditors[(row, 10)].setEnabled(width[cam_op])

    # HOW to do that : "Drill" and "Peck" and "Helix" only for "circle" shapes
    # HOW to do that : "Pocket" not for "line" and "polyline" shapes
    def enable_disable_drill_and_peck_ops(self):
        """ """
        for row in range(self.model().rowCount(None)):
            op = self.model().operations[row]
            paths = op.paths

            for path_id in paths:

                if not path_id in self.manager.svg_viewer.svg_shapes:
                    continue

                tag = self.manager.svg_viewer.svg_shapes[path_id].shape_tag

                comboxbox = self.delegate_col_op.xeditors[(row, 1)]
                model = comboxbox.model()

                item_pocket = model.item(0)
                # item_inside = model.item(1)
                # item_outside = model.item(2)
                # item_engrave = model.item(3)
                item_drill = model.item(4)
                item_peck = model.item(5)
                item_helix = model.item(6)

                if tag == "circle":
                    item_drill.setEnabled(True)
                    item_peck.setEnabled(True)
                else:
                    item_drill.setEnabled(False)
                    item_peck.setEnabled(False)

                if (
                    tag == "circle"
                    or tag == "ellipse"
                    or tag == "rect"
                    or tag == "polygon"
                    or (tag == "path" and True)  # FIXME   "is closed"
                ):
                    item_helix.setEnabled(True)
                else:
                    item_helix.setEnabled(False)

                if tag == "line" or tag == "polyline":
                    item_pocket.setEnabled(False)
                else:
                    item_pocket.setEnabled(True)


class PyCutSimpleTableModel(QtCore.QAbstractTableModel):
    """
    model for the table view
    """

    def __init__(self, operations: List[OpItem], mainwindow):
        super().__init__()

        self.operations = operations
        self.mainwindow = mainwindow
        self.view: PyCutSimpleTableView | None = None

        self.header = [
            "name",  # [0] str
            "cam_op",
            "enabled",  # [2] checkbox
            "paths",  # [3] str
            "units",
            "cut_depth",  # [5] float
            "ramp_plunge",  # [6] checkbox
            "combinaison",
            "direction",
            "margin",  # [9] float
            "width",  # [10] float
            "del",  # [11] button
            "up",  # [12] button
            "down",  # [13] button
        ]

        self.cnt = 0

    def set_view(self, view: PyCutSimpleTableView):
        """ """
        self.view = view

    def generate_gcode(self):
        """ """
        self.mainwindow.cb_generate_gcode()

    def handleNewvalue(self, index: QtCore.QModelIndex, value: Any):
        row = index.row()
        col = index.column()

        attrib = self.header[col]

        # update pycut GUI
        if attrib in [
            "cam_op",
            "enabled",
            "paths",
            "units",
            "cut_depth",
            "ramp_plunge",
            "combinaison",
            "margin",
            "width",
        ]:
            cnc_op = self.operations[row]
            setattr(cnc_op, attrib, value)

            self.mainwindow.display_cnc_ops_geometry(self.operations)

        if self.view is not None:
            self.view.enable_disable_cells()
            self.view.enable_disable_drill_and_peck_ops()

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
        col: int,
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
            if index.column() != 3:
                setattr(op, attr, value)
            else:
                items = eval(value)  # string to list
                setattr(op, attr, items)

    def data(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        role: int = QtCore.Qt.ItemDataRole.EditRole,
    ):
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
        if col == 2:  # checkbox
            return None
        if col == 6:  # checkbox
            return None

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            val = getattr(op, attr)

            if col == 3:  # make a string of the list
                # list of svg paths ids
                val = str(val)

            return val

        if role == QtCore.Qt.ItemDataRole.EditRole:
            val = getattr(op, attr)

            if col == 3:
                # list of svg paths ids
                val = str(val)

            return val

        # if role == QtCore.Qt.ToolTipRole:
        #    if col == 3:
        #        val = getattr(op, attr)
        #        return val

        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            # non-existant paths marked as red
            paths = op.paths
            for path_id in paths:
                view = cast(PyCutSimpleTableView, self.view)
                if not path_id in view.manager.svg_viewer.svg_shapes:
                    return QtGui.QBrush(QtCore.Qt.GlobalColor.red)  # red background

        return None

    def flags(
        self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ) -> QtCore.Qt.ItemFlag:
        flags = super().flags(index)

        flags |= QtCore.Qt.ItemFlag.ItemIsEditable
        flags |= QtCore.Qt.ItemFlag.ItemIsSelectable
        flags |= QtCore.Qt.ItemFlag.ItemIsEnabled
        flags |= QtCore.Qt.ItemFlag.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemFlag.ItemIsDropEnabled

        return flags

    def add_item(self, op_data):
        op = OpItem(op_data)

        idx = len(self.operations)

        self.beginInsertRows(QtCore.QModelIndex(), idx, idx)
        self.operations.append(op)
        self.endInsertRows()

    def del_item(self, idx: int):
        op = self.operations[idx]

        self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
        self.operations.remove(op)
        self.endRemoveRows()

    def swap_items(self, idx1: int, idx2: int):
        self.beginResetModel()
        self.operations[idx1], self.operations[idx2] = (
            self.operations[idx2],
            self.operations[idx1],
        )
        self.endResetModel()

    def get_operation(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex):
        return self.operations[index.row()]

    def get_operation_attr(
        self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ):
        return self.header[index.column()]
