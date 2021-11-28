
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class PyCutSimpleTable(QtWidgets.QTableView):
    
    def __init__(self, operations, parent=None):
        '''
        '''
        QtWidgets.QTableView.__init__(self, parent)

        self.parent = parent

        self.resizeColumnsToContents()
        # Fixes the width of columns and the height of rows.
        try:
            self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
            
            self.verticalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
        except Exception:
            pass

        # unlike the previous tutorial, we'll do background colours 'properly'. ;)
        self.setAlternatingRowColors(True)
        
        model = PyCutSimpleTableModel(operations)
        self.setModel(model)
        
        self.horizontalHeader().setStretchLastSection(True)
        
class PyCutSimpleTableModel(QtCore.QAbstractTableModel):
    '''
    model for the table view
    '''
    def __init__(self, contents):
        super(PyCutSimpleTableModel, self).__init__()
        self.contents = contents
        self.header = ["Name", "type"]
        

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.contents)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        op = self.get_table_rowitem(index)
        attr = self.get_table_rowattr(index)

        if role == QtCore.Qt.DisplayRole:
            return op[attr]
        if role == QtCore.Qt.EditRole:
            return op[attr]

        return None

    def flags(self, index):
        flags = super(PyCutSimpleTableModel, self).flags(index)
        return flags

    def get_table_rowitem(self, index):
        return self.contents[index.row()]

    def get_table_rowattr(self, index):
        return self.header[index.column()]
