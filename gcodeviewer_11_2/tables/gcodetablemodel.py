from enum import Enum

from typing import List
from typing import Any

from PySide6 import QtCore
from PySide6 import QtGui


class GCodeItem:
    class States(Enum):
        InQueue = 0
        Sent = 1
        Processed = 2
        Skipped = 3

    def __init__(self):
        self.command = ""
        self.state = GCodeItem.States.InQueue
        self.response = ""
        self.line = 0
        self.args = []


class GCodeTableModel(QtCore.QAbstractTableModel):
    """ """

    def __init__(self, parent=None):
        super(GCodeTableModel, self).__init__()

        self.m_data: List[GCodeItem] = []
        self.m_headers = ["#", "Command", "State", "Response", "Line", "Args"]

    def data(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        role=QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid():
            return None  # QVariant()

        if index.row() >= len(self.m_data):
            return None  # QVariant()

        if (
            role == QtCore.Qt.ItemDataRole.DisplayRole
            or role == QtCore.Qt.ItemDataRole.EditRole
        ):
            if index.column() == 0:
                return (
                    "" if index.row() == self.rowCount() - 1 else str(index.row() + 1)
                )
            elif index.column() == 1:
                return self.m_data[index.row()].command
            elif index.column() == 2:
                if index.row() == self.rowCount() - 1:
                    return ""
                if self.m_data[index.row()].state == GCodeItem.States.InQueue:
                    return "In queue"
                elif self.m_data[index.row()].state == GCodeItem.States.Sent:
                    return "Sent"
                elif self.m_data[index.row()].state == GCodeItem.States.Processed:
                    return "Processed"
                elif self.m_data[index.row()].state == GCodeItem.States.Skipped:
                    return "Skipped"
                else:
                    return "Unknown"
            elif index.column() == 3:
                return self.m_data[index.row()].response
            elif index.column() == 4:
                return self.m_data[index.row()].line
            elif index.column() == 5:
                return self.m_data[index.row()].args

        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            return QtCore.Qt.AlignmentFlag.AlignVCenter

        if role == QtCore.Qt.ItemDataRole.FontRole:
            if index.column() == 1:  # text items are bold.
                font = QtGui.QFont()
                font.setBold(True)
                return font

        return None  # QVariant()

    def setData(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        value: Any,
        role=QtCore.Qt.ItemDataRole.EditRole,
    ) -> bool:
        if index.isValid() and role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return False
            elif index.column() == 1:
                self.m_data[index.row()].command = str(value)
            elif index.column() == 2:
                self.m_data[index.row()].state = GCodeItem.States(value)
            elif index.column() == 3:
                self.m_data[index.row()].response = str(value)
            elif index.column() == 4:
                self.m_data[index.row()].line = int(value)
            elif index.column() == 5:
                self.m_data[index.row()].args = [str(value)]  ## FIXME: toStringList()

            self.dataChanged.emit(index, index)
            return True

        return False

    def insertRow(
        self,
        row: int,
        parent: (
            QtCore.QModelIndex | QtCore.QPersistentModelIndex
        ) = QtCore.QModelIndex(),
    ) -> bool:
        if row > self.rowCount():
            return False

        self.beginInsertRows(parent, row, row)
        self.m_data.insert(row, GCodeItem())
        self.endInsertRows()

        return True

    def removeRow(
        self,
        row: int,
        parent: (
            QtCore.QModelIndex | QtCore.QPersistentModelIndex
        ) = QtCore.QModelIndex(),
    ) -> bool:
        self.beginRemoveRows(parent, row, row)
        self.m_data.pop(row)
        self.endRemoveRows()

        return True

    def removeRows(
        self,
        row: int,
        count: int,
        parent: (
            QtCore.QModelIndex | QtCore.QPersistentModelIndex
        ) = QtCore.QModelIndex(),
    ) -> bool:
        self.beginRemoveRows(parent, row, row + count - 1)
        self.m_data = self.m_data[:row] + self.m_data[row + count :]
        self.endRemoveRows()

        return True

    def clear(self):
        self.beginResetModel()
        self.m_data = []
        self.endResetModel()

    def rowCount(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex = QtCore.QModelIndex(),
    ) -> int:
        return len(self.m_data)

    def columnCount(
        self,
        parent: (
            QtCore.QModelIndex | QtCore.QPersistentModelIndex
        ) = QtCore.QModelIndex(),
    ) -> int:
        return 6

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None  # QVariant()
        if orientation == QtCore.Qt.Orientation.Horizontal:
            return self.m_headers[section]
        else:
            return str(section + 1)

    def flags(
        self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags

        if index.column() == 1:
            # not editable
            return super().flags(index) | ~QtCore.Qt.ItemFlag.ItemIsEditable
        else:
            return super().flags(index)
