
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


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
        
        self.setColumnCount(5)
        self.setRowCount(len(operations))
    
        for i, op in enumerate(operations):
            item0 = QtWidgets.QTableWidgetItem(op["Name"])
            self.setItem(i, 0, item0)
            item0.setFlags(item0.flags() ^ QtGui.Qt.ItemIsEditable)
            
            item1 = QtWidgets.QTableWidgetItem(op["type"])
            self.setItem(i, 1, item1)
            item1.setFlags(item1.flags() ^ QtGui.Qt.ItemIsEditable)
            
            widget = QtWidgets.QWidget()
            btn_show_op = QtWidgets.QPushButton()
            btn_show_op.setText("Show")
            layout = QtWidgets.QHBoxLayout(widget)
            layout.addWidget(btn_show_op);
            layout.setAlignment(QtGui.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.setCellWidget(i, 2, widget)
            
            widget = QtWidgets.QWidget()
            btn_generate_gcode_op = QtWidgets.QPushButton()
            btn_generate_gcode_op.setText("Generate GCode")
            layout = QtWidgets.QHBoxLayout(widget)
            layout.addWidget(btn_generate_gcode_op);
            layout.setAlignment(QtGui.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.setCellWidget(i, 3, widget)
            
            widget = QtWidgets.QWidget()
            btn_del_op = QtWidgets.QPushButton()
            btn_del_op.setText("Del")
            layout = QtWidgets.QHBoxLayout(widget)
            layout.addWidget(btn_del_op);
            layout.setAlignment(QtGui.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.setCellWidget(i, 4, widget)
            
        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
        
        self.itemSelectionChanged.connect(self.cb_row_selected)
        
    def cb_row_selected(self):
        '''
        '''
        # display op content
        item = self.selectedItems()[0]
        print(str(item.text()), item.row())
        
        self.parent.parent().parent().display_op()
        self.parent.parent().parent().display_op_at_row(item.row())