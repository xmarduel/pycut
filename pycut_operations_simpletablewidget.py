
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class PyCutSimpleTableWidget(QtWidgets.QTableWidget):
    
    def __init__(self, parent=None):
        '''
        '''
        QtWidgets.QTableWidget.__init__(self, parent)

        self.parent = parent

        self.resizeColumnsToContents()
        # unlike the previous tutorial, we'll do background colours 'properly'. ;)
        self.setAlternatingRowColors(True)
        
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
    def setData(self, operations):
        self.clear()
        
        self.setColumnCount(4)
        self.setRowCount(len(operations))
    
        for i, op in enumerate(operations):
            
            
            item1 = QtWidgets.QTableWidgetItem(op["type"])
            self.setItem(i, 0, item1)
            item1.setFlags(item1.flags() ^ QtGui.Qt.ItemIsEditable)
            
            widget = QtWidgets.QWidget()
            btn_select_op = QtWidgets.QCheckBox()
            #btn_show_op.setText("Show")
            #btn_show_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/system-search.png'))
            #btn_show_op.setToolTip("Select")
            layout = QtWidgets.QHBoxLayout(widget)
            layout.addWidget(btn_select_op);
            layout.setAlignment(QtGui.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.setCellWidget(i, 1, widget)
            
            widget = QtWidgets.QWidget()
            btn_del_op = QtWidgets.QPushButton()
            btn_del_op.setText("Del")
            btn_del_op.setIcon(QtGui.QIcon(':/images/tango/22x22/actions/edit-clear.png'))
            btn_del_op.setToolTip("Delete")
            layout = QtWidgets.QHBoxLayout(widget)
            layout.addWidget(btn_del_op)
            layout.setAlignment(QtGui.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.setCellWidget(i, 2, widget)

            item0 = QtWidgets.QTableWidgetItem(op["Name"])
            self.setItem(i, 3, item0)
            item0.setFlags(item0.flags() ^ QtGui.Qt.ItemIsEditable)
            
            
        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
        
        self.itemSelectionChanged.connect(self.cb_row_selected)
        
    def cb_row_selected(self):
        '''
        '''
        # display op content
        item = self.selectedItems()[0]
        print(str(item.text()), item.row())
        
        self.parent.parent().parent().display_op_at_row(item.row())