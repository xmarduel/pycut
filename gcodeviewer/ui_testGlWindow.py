# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'testGlWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.2.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QHeaderView, QMainWindow, QMenuBar, QSizePolicy,
    QSplitter, QTableView, QVBoxLayout, QWidget)

class Ui_testGlWindow(object):
    def setupUi(self, testGlWindow):
        if not testGlWindow.objectName():
            testGlWindow.setObjectName(u"testGlWindow")
        testGlWindow.resize(952, 847)
        testGlWindow.setAcceptDrops(True)
        icon = QIcon()
        icon.addFile(u":/images/candle_256.png", QSize(), QIcon.Normal, QIcon.Off)
        testGlWindow.setWindowIcon(icon)
        testGlWindow.setStyleSheet(u"")
        self.centralWidget = QWidget(testGlWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.horizontalLayout_5 = QHBoxLayout(self.centralWidget)
        self.horizontalLayout_5.setSpacing(9)
        self.horizontalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(9, 9, 5, 9)
        self.grpProgram = QGroupBox(self.centralWidget)
        self.grpProgram.setObjectName(u"grpProgram")
        self.grpProgram.setFlat(False)
        self.verticalLayout_17 = QVBoxLayout(self.grpProgram)
        self.verticalLayout_17.setSpacing(7)
        self.verticalLayout_17.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(8, 8, 8, 8)
        self.splitter = QSplitter(self.grpProgram)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(12)
        self.frame = QWidget(self.splitter)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(0, 200))
        self.frame.setStyleSheet(u"border: 1px solid gray;")
        self.verticalLayout_8 = QVBoxLayout(self.frame)
        self.verticalLayout_8.setSpacing(6)
        self.verticalLayout_8.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(1, 1, 1, 1)
        self.splitter.addWidget(self.frame)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout_7 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_7.setSpacing(9)
        self.verticalLayout_7.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.tblProgram = QTableView(self.layoutWidget)
        self.tblProgram.setObjectName(u"tblProgram")
        font = QFont()
        font.setPointSize(9)
        self.tblProgram.setFont(font)
        self.tblProgram.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tblProgram.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)
        self.tblProgram.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.tblProgram.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblProgram.setGridStyle(Qt.DashLine)
        self.tblProgram.horizontalHeader().setMinimumSectionSize(50)
        self.tblProgram.horizontalHeader().setHighlightSections(False)
        self.tblProgram.verticalHeader().setVisible(False)

        self.verticalLayout_7.addWidget(self.tblProgram)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout_17.addWidget(self.splitter)

        self.verticalLayout_17.setStretch(0, 1)

        self.horizontalLayout_5.addWidget(self.grpProgram)

        self.horizontalLayout_5.setStretch(0, 100)
        testGlWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(testGlWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 952, 21))
        testGlWindow.setMenuBar(self.menuBar)

        self.retranslateUi(testGlWindow)

        QMetaObject.connectSlotsByName(testGlWindow)
    # setupUi

    def retranslateUi(self, testGlWindow):
        testGlWindow.setWindowTitle(QCoreApplication.translate("testGlWindow", u"Candle", None))
        self.grpProgram.setTitle(QCoreApplication.translate("testGlWindow", u"G-code program", None))
    # retranslateUi

