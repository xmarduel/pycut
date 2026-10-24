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
        self.line = -1
        self.args = []


class GCodeTableModel(QtCore.QAbstractTableModel):
    """ """

    commandChanged = QtCore.Signal() # (int row, const QByteArray &oldValue, const QByteArray &newValue);
    commandsInserted = QtCore.Signal() # (int row, const QList<QByteArray> &commands);
    rowAdded = QtCore.Signal() # (int row);

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
                #self.m_data[index.row()].command = str(value)
                oldCommand = self.m_data[index.row()].command
                newCommand = value.toString().toUtf8()
                
                if newCommand != oldCommand:
                    self.m_data[index.row()].command = newCommand
                    self.m_data[index.row()].command.squeeze()
                    self.commandChanged.emit(index.row(), oldCommand, newCommand)

            elif index.column() == 2:
                self.m_data[index.row()].state = GCodeItem.States(value)
            elif index.column() == 3:
                self.m_data[index.row()].response = str(value)
                self.m_data[index.row()].response.squeeze()
            elif index.column() == 4:
                self.m_data[index.row()].line = int(value)
            elif index.column() == 5:
                self.m_data[index.row()].args = [str(value)]  ## FIXME: value.value<QList<QByteArray>>();

            self.dataChanged.emit(index, index)
            return True

        return False

    def setCommand(self, row: int, command: QtCore.QByteArray):
        self.m_data[row].command = command
        self.m_data[row].command.squeeze()
        self.m_data[row].args = []

        #index = self.index(row, 1)
        self.dataChanged.emit(self.index(row, 1), self.index(row, 5))

    def insertCommands(self, row: int, commands: List[QtCore.QByteArray]):
        self.insertRows(row, len(commands))

        for i, command in enumerate(commands):
            self.setCommand(row + i, command)

        self.commandsInserted.emit(row, commands)

    def addRow(self, row: int):
        self.insertRow(row)

        self.rowAdded.emit(row)

    def insertRows(self, row: int, count: int, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex = QtCore.QModelIndex()) -> bool:

        if row > self.rowCount():
            return False

        self.beginInsertRows(parent, row, row + count - 1)

        newData: List[GCodeItem] = []

        for i in range(row):
            newData.append(self.m_data[i])
            #self.m_data[i] = None

        for i in range(count):
            newData.append(GCodeItem())

        for i in range(row, len(self.m_data)):
            newData.append(self.m_data[i])
            #self.m_data[i] = None

        self.m_data = newData

        self.endInsertRows()

        return True    

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
