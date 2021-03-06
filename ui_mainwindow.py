# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QDoubleSpinBox, QFormLayout, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QSplitter, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

from operations_tableview import PyCutOperationsTableViewManager
from tabs_tableview import PyCutTabsTableViewManager

class Ui_mainwindow(object):
    def setupUi(self, mainwindow):
        if not mainwindow.objectName():
            mainwindow.setObjectName(u"mainwindow")
        mainwindow.resize(1226, 1049)
        self.actionOpenSvg = QAction(mainwindow)
        self.actionOpenSvg.setObjectName(u"actionOpenSvg")
        self.actionNewJob = QAction(mainwindow)
        self.actionNewJob.setObjectName(u"actionNewJob")
        self.actionOpenJob = QAction(mainwindow)
        self.actionOpenJob.setObjectName(u"actionOpenJob")
        self.actionSaveJobAs = QAction(mainwindow)
        self.actionSaveJobAs.setObjectName(u"actionSaveJobAs")
        self.actionSaveJob = QAction(mainwindow)
        self.actionSaveJob.setObjectName(u"actionSaveJob")
        self.actionTutorial = QAction(mainwindow)
        self.actionTutorial.setObjectName(u"actionTutorial")
        self.actionAboutQt = QAction(mainwindow)
        self.actionAboutQt.setObjectName(u"actionAboutQt")
        self.actionAboutPyCut = QAction(mainwindow)
        self.actionAboutPyCut.setObjectName(u"actionAboutPyCut")
        self.actionSettings = QAction(mainwindow)
        self.actionSettings.setObjectName(u"actionSettings")
        self.centralwidget = QWidget(mainwindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.scrollArea_left = QScrollArea(self.centralwidget)
        self.scrollArea_left.setObjectName(u"scrollArea_left")
        self.scrollArea_left.setMinimumSize(QSize(320, 0))
        self.scrollArea_left.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 318, 986))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, -1, 9, -1)
        self.verticalLayoutSettingsContent = QVBoxLayout()
        self.verticalLayoutSettingsContent.setObjectName(u"verticalLayoutSettingsContent")
        self.verticalLayoutSettingsContent.setContentsMargins(-1, -1, -1, 20)
        self.label_SvgSettings = QLabel(self.scrollAreaWidgetContents)
        self.label_SvgSettings.setObjectName(u"label_SvgSettings")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_SvgSettings.setFont(font)
        self.label_SvgSettings.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutSettingsContent.addWidget(self.label_SvgSettings)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, -1, -1, -1)
        self.label_PxPerInch = QLabel(self.scrollAreaWidgetContents)
        self.label_PxPerInch.setObjectName(u"label_PxPerInch")
        font1 = QFont()
        font1.setBold(True)
        self.label_PxPerInch.setFont(font1)

        self.horizontalLayout.addWidget(self.label_PxPerInch)

        self.doubleSpinBox_PxPerInch = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_PxPerInch.setObjectName(u"doubleSpinBox_PxPerInch")
        self.doubleSpinBox_PxPerInch.setEnabled(False)
        self.doubleSpinBox_PxPerInch.setMaximum(999.990000000000009)
        self.doubleSpinBox_PxPerInch.setValue(1.000000000000000)

        self.horizontalLayout.addWidget(self.doubleSpinBox_PxPerInch)


        self.verticalLayoutSettingsContent.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(8, -1, -1, -1)
        self.label_SvgModelWidth = QLabel(self.scrollAreaWidgetContents)
        self.label_SvgModelWidth.setObjectName(u"label_SvgModelWidth")
        self.label_SvgModelWidth.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_SvgModelWidth)

        self.doubleSpinBox_SvgModelWidth = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_SvgModelWidth.setObjectName(u"doubleSpinBox_SvgModelWidth")
        self.doubleSpinBox_SvgModelWidth.setEnabled(False)
        self.doubleSpinBox_SvgModelWidth.setMaximum(999.990000000000009)

        self.horizontalLayout_4.addWidget(self.doubleSpinBox_SvgModelWidth)


        self.verticalLayoutSettingsContent.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(8, -1, -1, -1)
        self.label_SvgModelHeight = QLabel(self.scrollAreaWidgetContents)
        self.label_SvgModelHeight.setObjectName(u"label_SvgModelHeight")
        self.label_SvgModelHeight.setFont(font1)

        self.horizontalLayout_3.addWidget(self.label_SvgModelHeight)

        self.doubleSpinBox_SvgModelHeight = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_SvgModelHeight.setObjectName(u"doubleSpinBox_SvgModelHeight")
        self.doubleSpinBox_SvgModelHeight.setEnabled(False)
        self.doubleSpinBox_SvgModelHeight.setMaximum(999.990000000000009)

        self.horizontalLayout_3.addWidget(self.doubleSpinBox_SvgModelHeight)


        self.verticalLayoutSettingsContent.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addLayout(self.verticalLayoutSettingsContent)

        self.verticalLayoutToolContent = QVBoxLayout()
        self.verticalLayoutToolContent.setObjectName(u"verticalLayoutToolContent")
        self.verticalLayoutToolContent.setContentsMargins(-1, -1, -1, 20)
        self.label_Tool = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool.setObjectName(u"label_Tool")
        self.label_Tool.setFont(font)
        self.label_Tool.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutToolContent.addWidget(self.label_Tool)

        self.gridLayout_Tool = QGridLayout()
        self.gridLayout_Tool.setObjectName(u"gridLayout_Tool")
        self.gridLayout_Tool.setContentsMargins(8, 0, -1, 0)
        self.label_Tool_Plunge_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Plunge_UnitsDescr.setObjectName(u"label_Tool_Plunge_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Plunge_UnitsDescr, 6, 1, 1, 1)

        self.label_Tool_Diameter_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Diameter_UnitsDescr.setObjectName(u"label_Tool_Diameter_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Diameter_UnitsDescr, 1, 1, 1, 1)

        self.label_Tool_StepOver = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_StepOver.setObjectName(u"label_Tool_StepOver")
        self.label_Tool_StepOver.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_StepOver, 4, 0, 1, 1)

        self.spinBox_Tool_Rapid = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_Tool_Rapid.setObjectName(u"spinBox_Tool_Rapid")
        self.spinBox_Tool_Rapid.setMaximum(1000)
        self.spinBox_Tool_Rapid.setValue(500)

        self.gridLayout_Tool.addWidget(self.spinBox_Tool_Rapid, 5, 2, 1, 1)

        self.label_Tool_Units = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Units.setObjectName(u"label_Tool_Units")
        self.label_Tool_Units.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Units, 0, 0, 1, 1)

        self.label_Tool_PassDepth = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_PassDepth.setObjectName(u"label_Tool_PassDepth")
        self.label_Tool_PassDepth.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_PassDepth, 3, 0, 1, 1)

        self.label_Tool_Rapid_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Rapid_UnitsDescr.setObjectName(u"label_Tool_Rapid_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Rapid_UnitsDescr, 5, 1, 1, 1)

        self.label_Tool_Plunge = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Plunge.setObjectName(u"label_Tool_Plunge")
        self.label_Tool_Plunge.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Plunge, 6, 0, 1, 1)

        self.label_Tool_Angle_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Angle_UnitsDescr.setObjectName(u"label_Tool_Angle_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Angle_UnitsDescr, 2, 1, 1, 1)

        self.label_Tool_Cut_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Cut_UnitsDescr.setObjectName(u"label_Tool_Cut_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Cut_UnitsDescr, 7, 1, 1, 1)

        self.label_Tool_Angle = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Angle.setObjectName(u"label_Tool_Angle")
        self.label_Tool_Angle.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Angle, 2, 0, 1, 1)

        self.label_Tool_Rapid = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Rapid.setObjectName(u"label_Tool_Rapid")
        self.label_Tool_Rapid.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Rapid, 5, 0, 1, 1)

        self.spinBox_Tool_Angle = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_Tool_Angle.setObjectName(u"spinBox_Tool_Angle")
        self.spinBox_Tool_Angle.setMaximum(180)
        self.spinBox_Tool_Angle.setValue(180)

        self.gridLayout_Tool.addWidget(self.spinBox_Tool_Angle, 2, 2, 1, 1)

        self.label_Tool_StepOver_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_StepOver_UnitsDescr.setObjectName(u"label_Tool_StepOver_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_StepOver_UnitsDescr, 4, 1, 1, 1)

        self.doubleSpinBox_Tool_Diameter = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_Tool_Diameter.setObjectName(u"doubleSpinBox_Tool_Diameter")
        self.doubleSpinBox_Tool_Diameter.setDecimals(3)
        self.doubleSpinBox_Tool_Diameter.setMaximum(32.000000000000000)
        self.doubleSpinBox_Tool_Diameter.setValue(1.000000000000000)

        self.gridLayout_Tool.addWidget(self.doubleSpinBox_Tool_Diameter, 1, 2, 1, 1)

        self.label_Tool_Diameter = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Diameter.setObjectName(u"label_Tool_Diameter")
        self.label_Tool_Diameter.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Diameter, 1, 0, 1, 1)

        self.spinBox_Tool_Plunge = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_Tool_Plunge.setObjectName(u"spinBox_Tool_Plunge")
        self.spinBox_Tool_Plunge.setMaximum(1000)
        self.spinBox_Tool_Plunge.setValue(100)

        self.gridLayout_Tool.addWidget(self.spinBox_Tool_Plunge, 6, 2, 1, 1)

        self.label_Tool_PassDepth_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_PassDepth_UnitsDescr.setObjectName(u"label_Tool_PassDepth_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_PassDepth_UnitsDescr, 3, 1, 1, 1)

        self.label_Tool_Cut = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Cut.setObjectName(u"label_Tool_Cut")
        self.label_Tool_Cut.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Cut, 7, 0, 1, 1)

        self.doubleSpinBox_Tool_StepOver = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_Tool_StepOver.setObjectName(u"doubleSpinBox_Tool_StepOver")
        self.doubleSpinBox_Tool_StepOver.setDecimals(3)
        self.doubleSpinBox_Tool_StepOver.setMaximum(1.000000000000000)
        self.doubleSpinBox_Tool_StepOver.setSingleStep(0.010000000000000)
        self.doubleSpinBox_Tool_StepOver.setValue(0.400000000000000)

        self.gridLayout_Tool.addWidget(self.doubleSpinBox_Tool_StepOver, 4, 2, 1, 1)

        self.comboBox_Tool_Units = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_Tool_Units.addItem("")
        self.comboBox_Tool_Units.addItem("")
        self.comboBox_Tool_Units.setObjectName(u"comboBox_Tool_Units")

        self.gridLayout_Tool.addWidget(self.comboBox_Tool_Units, 0, 1, 1, 1)

        self.doubleSpinBox_Tool_PassDepth = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_Tool_PassDepth.setObjectName(u"doubleSpinBox_Tool_PassDepth")
        self.doubleSpinBox_Tool_PassDepth.setDecimals(3)
        self.doubleSpinBox_Tool_PassDepth.setMaximum(10.000000000000000)
        self.doubleSpinBox_Tool_PassDepth.setSingleStep(0.500000000000000)
        self.doubleSpinBox_Tool_PassDepth.setValue(0.200000000000000)

        self.gridLayout_Tool.addWidget(self.doubleSpinBox_Tool_PassDepth, 3, 2, 1, 1)

        self.spinBox_Tool_Cut = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_Tool_Cut.setObjectName(u"spinBox_Tool_Cut")
        self.spinBox_Tool_Cut.setMaximum(1000)
        self.spinBox_Tool_Cut.setValue(200)

        self.gridLayout_Tool.addWidget(self.spinBox_Tool_Cut, 7, 2, 1, 1)


        self.verticalLayoutToolContent.addLayout(self.gridLayout_Tool)


        self.verticalLayout_2.addLayout(self.verticalLayoutToolContent)

        self.verticalLayoutCurveToLineConversion = QVBoxLayout()
        self.verticalLayoutCurveToLineConversion.setObjectName(u"verticalLayoutCurveToLineConversion")
        self.verticalLayoutCurveToLineConversion.setContentsMargins(-1, -1, -1, 20)
        self.labelCurveToLineConversion = QLabel(self.scrollAreaWidgetContents)
        self.labelCurveToLineConversion.setObjectName(u"labelCurveToLineConversion")
        self.labelCurveToLineConversion.setFont(font)
        self.labelCurveToLineConversion.setStyleSheet(u"background-color: rgb(196, 196, 196);")

        self.verticalLayoutCurveToLineConversion.addWidget(self.labelCurveToLineConversion)

        self.formLayoutCurveToLineConversion = QFormLayout()
        self.formLayoutCurveToLineConversion.setObjectName(u"formLayoutCurveToLineConversion")
        self.formLayoutCurveToLineConversion.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayoutCurveToLineConversion.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.formLayoutCurveToLineConversion.setVerticalSpacing(6)
        self.formLayoutCurveToLineConversion.setContentsMargins(8, 0, -1, -1)
        self.label_CurveToLineConversion_MinimumNbSegments = QLabel(self.scrollAreaWidgetContents)
        self.label_CurveToLineConversion_MinimumNbSegments.setObjectName(u"label_CurveToLineConversion_MinimumNbSegments")
        self.label_CurveToLineConversion_MinimumNbSegments.setFont(font1)

        self.formLayoutCurveToLineConversion.setWidget(0, QFormLayout.LabelRole, self.label_CurveToLineConversion_MinimumNbSegments)

        self.spinBox_CurveToLineConversion_MinimumNbSegments = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox_CurveToLineConversion_MinimumNbSegments.setObjectName(u"spinBox_CurveToLineConversion_MinimumNbSegments")
        self.spinBox_CurveToLineConversion_MinimumNbSegments.setEnabled(True)
        self.spinBox_CurveToLineConversion_MinimumNbSegments.setMinimum(1)
        self.spinBox_CurveToLineConversion_MinimumNbSegments.setValue(5)

        self.formLayoutCurveToLineConversion.setWidget(0, QFormLayout.FieldRole, self.spinBox_CurveToLineConversion_MinimumNbSegments)

        self.label_CurveToLineConversion_MinimumSegmentsLength = QLabel(self.scrollAreaWidgetContents)
        self.label_CurveToLineConversion_MinimumSegmentsLength.setObjectName(u"label_CurveToLineConversion_MinimumSegmentsLength")
        self.label_CurveToLineConversion_MinimumSegmentsLength.setFont(font1)

        self.formLayoutCurveToLineConversion.setWidget(1, QFormLayout.LabelRole, self.label_CurveToLineConversion_MinimumSegmentsLength)

        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setObjectName(u"doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength")
        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setMaximum(1.000000000000000)
        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setSingleStep(0.010000000000000)
        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setValue(0.010000000000000)

        self.formLayoutCurveToLineConversion.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength)


        self.verticalLayoutCurveToLineConversion.addLayout(self.formLayoutCurveToLineConversion)


        self.verticalLayout_2.addLayout(self.verticalLayoutCurveToLineConversion)

        self.verticalLayoutTabsContent = QVBoxLayout()
        self.verticalLayoutTabsContent.setObjectName(u"verticalLayoutTabsContent")
        self.verticalLayoutTabsContent.setContentsMargins(-1, -1, -1, 0)
        self.label_Tabs = QLabel(self.scrollAreaWidgetContents)
        self.label_Tabs.setObjectName(u"label_Tabs")
        self.label_Tabs.setEnabled(True)
        self.label_Tabs.setFont(font)
        self.label_Tabs.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutTabsContent.addWidget(self.label_Tabs)

        self.tabsGlobals = QWidget(self.scrollAreaWidgetContents)
        self.tabsGlobals.setObjectName(u"tabsGlobals")
        self.tabsGlobals.setMinimumSize(QSize(0, 0))
        self.verticalLayout_4 = QVBoxLayout(self.tabsGlobals)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(8, 0, 0, 9)
        self.formLayout_Tabs = QFormLayout()
        self.formLayout_Tabs.setObjectName(u"formLayout_Tabs")
        self.formLayout_Tabs.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_Tabs.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_TabsUnits = QLabel(self.tabsGlobals)
        self.label_TabsUnits.setObjectName(u"label_TabsUnits")
        self.label_TabsUnits.setFont(font1)

        self.formLayout_Tabs.setWidget(0, QFormLayout.LabelRole, self.label_TabsUnits)

        self.comboBox_Tabs_Units = QComboBox(self.tabsGlobals)
        self.comboBox_Tabs_Units.addItem("")
        self.comboBox_Tabs_Units.addItem("")
        self.comboBox_Tabs_Units.setObjectName(u"comboBox_Tabs_Units")
        self.comboBox_Tabs_Units.setEnabled(True)

        self.formLayout_Tabs.setWidget(0, QFormLayout.FieldRole, self.comboBox_Tabs_Units)

        self.label_Tabs_Height = QLabel(self.tabsGlobals)
        self.label_Tabs_Height.setObjectName(u"label_Tabs_Height")
        self.label_Tabs_Height.setFont(font1)

        self.formLayout_Tabs.setWidget(1, QFormLayout.LabelRole, self.label_Tabs_Height)

        self.doubleSpinBox_Tabs_Height = QDoubleSpinBox(self.tabsGlobals)
        self.doubleSpinBox_Tabs_Height.setObjectName(u"doubleSpinBox_Tabs_Height")
        self.doubleSpinBox_Tabs_Height.setEnabled(True)
        self.doubleSpinBox_Tabs_Height.setDecimals(3)

        self.formLayout_Tabs.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_Tabs_Height)

        self.label = QLabel(self.tabsGlobals)
        self.label.setObjectName(u"label")

        self.formLayout_Tabs.setWidget(2, QFormLayout.LabelRole, self.label)

        self.checkBox_Tabs_hideAllTabs = QCheckBox(self.tabsGlobals)
        self.checkBox_Tabs_hideAllTabs.setObjectName(u"checkBox_Tabs_hideAllTabs")
        self.checkBox_Tabs_hideAllTabs.setFont(font1)

        self.formLayout_Tabs.setWidget(2, QFormLayout.FieldRole, self.checkBox_Tabs_hideAllTabs)

        self.checkBox_Tabs_hideDisabledTabs = QCheckBox(self.tabsGlobals)
        self.checkBox_Tabs_hideDisabledTabs.setObjectName(u"checkBox_Tabs_hideDisabledTabs")
        self.checkBox_Tabs_hideDisabledTabs.setFont(font1)

        self.formLayout_Tabs.setWidget(3, QFormLayout.FieldRole, self.checkBox_Tabs_hideDisabledTabs)


        self.verticalLayout_4.addLayout(self.formLayout_Tabs)


        self.verticalLayoutTabsContent.addWidget(self.tabsGlobals)

        self.tabsview_manager = PyCutTabsTableViewManager(self.scrollAreaWidgetContents)
        self.tabsview_manager.setObjectName(u"tabsview_manager")
        self.tabsview_manager.setMinimumSize(QSize(0, 200))

        self.verticalLayoutTabsContent.addWidget(self.tabsview_manager)

        self.verticalLayoutTabsContent.setStretch(2, 1)

        self.verticalLayout_2.addLayout(self.verticalLayoutTabsContent)

        self.scrollArea_left.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_2.addWidget(self.scrollArea_left)

        self.centralArea = QWidget(self.centralwidget)
        self.centralArea.setObjectName(u"centralArea")
        self.centralArea.setMinimumSize(QSize(400, 0))
        self.centralArea.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.centralArea)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 0, 4, 0)
        self.splitter = QSplitter(self.centralArea)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        self.svg = QWidget()
        self.svg.setObjectName(u"svg")
        self.verticalLayout_3 = QVBoxLayout(self.svg)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tabWidget.addTab(self.svg, "")
        self.viewer = QWidget()
        self.viewer.setObjectName(u"viewer")
        self.verticalLayout_9 = QVBoxLayout(self.viewer)
        self.verticalLayout_9.setSpacing(4)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.viewer, "")
        self.simulator = QWidget()
        self.simulator.setObjectName(u"simulator")
        self.horizontalLayout_5 = QHBoxLayout(self.simulator)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.tabWidget.addTab(self.simulator, "")
        self.splitter.addWidget(self.tabWidget)
        self.operationsview_manager = PyCutOperationsTableViewManager(self.splitter)
        self.operationsview_manager.setObjectName(u"operationsview_manager")
        self.operationsview_manager.setMinimumSize(QSize(0, 200))
        self.operationsview_manager.setMaximumSize(QSize(16777215, 400))
        self.splitter.addWidget(self.operationsview_manager)

        self.verticalLayout.addWidget(self.splitter)

        self.pushButton_SaveGcode = QPushButton(self.centralArea)
        self.pushButton_SaveGcode.setObjectName(u"pushButton_SaveGcode")

        self.verticalLayout.addWidget(self.pushButton_SaveGcode)


        self.horizontalLayout_2.addWidget(self.centralArea)

        self.scrollArea_right = QScrollArea(self.centralwidget)
        self.scrollArea_right.setObjectName(u"scrollArea_right")
        self.scrollArea_right.setMinimumSize(QSize(200, 0))
        self.scrollArea_right.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 314, 986))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayoutMaterial = QVBoxLayout()
        self.verticalLayoutMaterial.setObjectName(u"verticalLayoutMaterial")
        self.verticalLayoutMaterial.setContentsMargins(-1, -1, -1, 20)
        self.labelMaterial = QLabel(self.scrollAreaWidgetContents_2)
        self.labelMaterial.setObjectName(u"labelMaterial")
        self.labelMaterial.setFont(font)
        self.labelMaterial.setStyleSheet(u"background-color: rgb(200, 200, 200);")

        self.verticalLayoutMaterial.addWidget(self.labelMaterial)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.widget_display_material = QWidget(self.scrollAreaWidgetContents_2)
        self.widget_display_material.setObjectName(u"widget_display_material")
        self.widget_display_material.setMinimumSize(QSize(200, 150))
        self.widget_display_material.setMaximumSize(QSize(200, 150))

        self.horizontalLayout_6.addWidget(self.widget_display_material)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)


        self.verticalLayoutMaterial.addLayout(self.horizontalLayout_6)

        self.formLayout_Material = QFormLayout()
        self.formLayout_Material.setObjectName(u"formLayout_Material")
        self.formLayout_Material.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_Material.setFormAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)
        self.label_Material_Units = QLabel(self.scrollAreaWidgetContents_2)
        self.label_Material_Units.setObjectName(u"label_Material_Units")
        self.label_Material_Units.setFont(font1)

        self.formLayout_Material.setWidget(0, QFormLayout.LabelRole, self.label_Material_Units)

        self.comboBox_Material_Units = QComboBox(self.scrollAreaWidgetContents_2)
        self.comboBox_Material_Units.addItem("")
        self.comboBox_Material_Units.addItem("")
        self.comboBox_Material_Units.setObjectName(u"comboBox_Material_Units")

        self.formLayout_Material.setWidget(0, QFormLayout.FieldRole, self.comboBox_Material_Units)

        self.label_Material_Thickness = QLabel(self.scrollAreaWidgetContents_2)
        self.label_Material_Thickness.setObjectName(u"label_Material_Thickness")
        self.label_Material_Thickness.setFont(font1)

        self.formLayout_Material.setWidget(1, QFormLayout.LabelRole, self.label_Material_Thickness)

        self.doubleSpinBox_Material_Thickness = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.doubleSpinBox_Material_Thickness.setObjectName(u"doubleSpinBox_Material_Thickness")
        self.doubleSpinBox_Material_Thickness.setMaximum(100.000000000000000)
        self.doubleSpinBox_Material_Thickness.setValue(50.000000000000000)

        self.formLayout_Material.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_Material_Thickness)

        self.label_Material_ZOrigin = QLabel(self.scrollAreaWidgetContents_2)
        self.label_Material_ZOrigin.setObjectName(u"label_Material_ZOrigin")
        self.label_Material_ZOrigin.setFont(font1)

        self.formLayout_Material.setWidget(2, QFormLayout.LabelRole, self.label_Material_ZOrigin)

        self.comboBox_Material_ZOrigin = QComboBox(self.scrollAreaWidgetContents_2)
        self.comboBox_Material_ZOrigin.addItem("")
        self.comboBox_Material_ZOrigin.addItem("")
        self.comboBox_Material_ZOrigin.setObjectName(u"comboBox_Material_ZOrigin")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_Material_ZOrigin.sizePolicy().hasHeightForWidth())
        self.comboBox_Material_ZOrigin.setSizePolicy(sizePolicy)

        self.formLayout_Material.setWidget(2, QFormLayout.FieldRole, self.comboBox_Material_ZOrigin)

        self.label_Material_Clearance = QLabel(self.scrollAreaWidgetContents_2)
        self.label_Material_Clearance.setObjectName(u"label_Material_Clearance")
        self.label_Material_Clearance.setFont(font1)
        self.label_Material_Clearance.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_Material.setWidget(3, QFormLayout.LabelRole, self.label_Material_Clearance)

        self.doubleSpinBox_Material_Clearance = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.doubleSpinBox_Material_Clearance.setObjectName(u"doubleSpinBox_Material_Clearance")
        self.doubleSpinBox_Material_Clearance.setMaximum(100.000000000000000)
        self.doubleSpinBox_Material_Clearance.setValue(20.000000000000000)

        self.formLayout_Material.setWidget(3, QFormLayout.FieldRole, self.doubleSpinBox_Material_Clearance)


        self.verticalLayoutMaterial.addLayout(self.formLayout_Material)


        self.verticalLayout_5.addLayout(self.verticalLayoutMaterial)

        self.verticalLayoutGCodeConversion = QVBoxLayout()
        self.verticalLayoutGCodeConversion.setObjectName(u"verticalLayoutGCodeConversion")
        self.verticalLayoutGCodeConversion.setContentsMargins(-1, -1, -1, 20)
        self.label_GCcodeConversion = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCcodeConversion.setObjectName(u"label_GCcodeConversion")
        self.label_GCcodeConversion.setFont(font)
        self.label_GCcodeConversion.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutGCodeConversion.addWidget(self.label_GCcodeConversion)

        self.gridLayout_GCodeConversion = QGridLayout()
        self.gridLayout_GCodeConversion.setObjectName(u"gridLayout_GCodeConversion")
        self.label_GCodeConversion_YOffset_UnitsDescr = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_YOffset_UnitsDescr.setObjectName(u"label_GCodeConversion_YOffset_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_YOffset_UnitsDescr, 7, 1, 1, 1)

        self.label_GCodeConversion_YOffset = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_YOffset.setObjectName(u"label_GCodeConversion_YOffset")
        self.label_GCodeConversion_YOffset.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_YOffset, 7, 0, 1, 1)

        self.doubleSpinBox_GCodeConversion_MinY = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.doubleSpinBox_GCodeConversion_MinY.setObjectName(u"doubleSpinBox_GCodeConversion_MinY")
        self.doubleSpinBox_GCodeConversion_MinY.setEnabled(False)
        self.doubleSpinBox_GCodeConversion_MinY.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MinY.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_MinY, 10, 2, 1, 1)

        self.label_GCodeConversion_GCodeUnits = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_GCodeUnits.setObjectName(u"label_GCodeConversion_GCodeUnits")
        self.label_GCodeConversion_GCodeUnits.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_GCodeUnits, 0, 0, 1, 1)

        self.doubleSpinBox_GCodeConversion_MaxX = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.doubleSpinBox_GCodeConversion_MaxX.setObjectName(u"doubleSpinBox_GCodeConversion_MaxX")
        self.doubleSpinBox_GCodeConversion_MaxX.setEnabled(False)
        self.doubleSpinBox_GCodeConversion_MaxX.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MaxX.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_MaxX, 9, 2, 1, 1)

        self.label_GCodeConversion_MaxY = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MaxY.setObjectName(u"label_GCodeConversion_MaxY")
        self.label_GCodeConversion_MaxY.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxY, 11, 0, 1, 1)

        self.label_GCodeConversion_MinX_UnitsDescr = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MinX_UnitsDescr.setObjectName(u"label_GCodeConversion_MinX_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinX_UnitsDescr, 8, 1, 1, 1)

        self.checkBox_GCodeConversion_FlipXY = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_GCodeConversion_FlipXY.setObjectName(u"checkBox_GCodeConversion_FlipXY")
        self.checkBox_GCodeConversion_FlipXY.setEnabled(True)
        font2 = QFont()
        font2.setBold(True)
        font2.setKerning(False)
        self.checkBox_GCodeConversion_FlipXY.setFont(font2)

        self.gridLayout_GCodeConversion.addWidget(self.checkBox_GCodeConversion_FlipXY, 5, 0, 1, 2)

        self.doubleSpinBox_GCodeConversion_MinX = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.doubleSpinBox_GCodeConversion_MinX.setObjectName(u"doubleSpinBox_GCodeConversion_MinX")
        self.doubleSpinBox_GCodeConversion_MinX.setEnabled(False)
        self.doubleSpinBox_GCodeConversion_MinX.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MinX.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_MinX, 8, 2, 1, 1)

        self.doubleSpinBox_GCodeConversion_MaxY = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.doubleSpinBox_GCodeConversion_MaxY.setObjectName(u"doubleSpinBox_GCodeConversion_MaxY")
        self.doubleSpinBox_GCodeConversion_MaxY.setEnabled(False)
        self.doubleSpinBox_GCodeConversion_MaxY.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MaxY.setMaximum(1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MaxY.setValue(0.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_MaxY, 11, 2, 1, 1)

        self.label_GCodeConversion_MinX = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MinX.setObjectName(u"label_GCodeConversion_MinX")
        self.label_GCodeConversion_MinX.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinX, 8, 0, 1, 1)

        self.label_GCodeConversion_MaxX = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MaxX.setObjectName(u"label_GCodeConversion_MaxX")
        self.label_GCodeConversion_MaxX.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxX, 9, 0, 1, 1)

        self.label_GCodeConversion_XOffset_UnitsDescr = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_XOffset_UnitsDescr.setObjectName(u"label_GCodeConversion_XOffset_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_XOffset_UnitsDescr, 6, 1, 1, 1)

        self.label_GCodeConversion_MaxY_UnitsDescr = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MaxY_UnitsDescr.setObjectName(u"label_GCodeConversion_MaxY_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxY_UnitsDescr, 11, 1, 1, 1)

        self.label_GCodeConversion_MaxX_UnitsDescr = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MaxX_UnitsDescr.setObjectName(u"label_GCodeConversion_MaxX_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxX_UnitsDescr, 9, 1, 1, 1)

        self.doubleSpinBox_GCodeConversion_YOffset = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.doubleSpinBox_GCodeConversion_YOffset.setObjectName(u"doubleSpinBox_GCodeConversion_YOffset")
        self.doubleSpinBox_GCodeConversion_YOffset.setMinimum(-100.000000000000000)
        self.doubleSpinBox_GCodeConversion_YOffset.setMaximum(100.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_YOffset, 7, 2, 1, 1)

        self.label_GCodeConversion_MinY_UnitsDescr = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MinY_UnitsDescr.setObjectName(u"label_GCodeConversion_MinY_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinY_UnitsDescr, 10, 1, 1, 1)

        self.doubleSpinBox_GCodeConversion_XOffset = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.doubleSpinBox_GCodeConversion_XOffset.setObjectName(u"doubleSpinBox_GCodeConversion_XOffset")
        self.doubleSpinBox_GCodeConversion_XOffset.setMinimum(-100.000000000000000)
        self.doubleSpinBox_GCodeConversion_XOffset.setMaximum(100.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_XOffset, 6, 2, 1, 1)

        self.label_GCodeConversion_MinY = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MinY.setObjectName(u"label_GCodeConversion_MinY")
        self.label_GCodeConversion_MinY.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinY, 10, 0, 1, 1)

        self.label_GCodeConversion_XOffset = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_XOffset.setObjectName(u"label_GCodeConversion_XOffset")
        self.label_GCodeConversion_XOffset.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_XOffset, 6, 0, 1, 1)

        self.comboBox_GCodeConversion_Units = QComboBox(self.scrollAreaWidgetContents_2)
        self.comboBox_GCodeConversion_Units.addItem("")
        self.comboBox_GCodeConversion_Units.addItem("")
        self.comboBox_GCodeConversion_Units.setObjectName(u"comboBox_GCodeConversion_Units")

        self.gridLayout_GCodeConversion.addWidget(self.comboBox_GCodeConversion_Units, 0, 1, 1, 1)

        self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial = QPushButton(self.scrollAreaWidgetContents_2)
        self.buttonGroup_GCodeConversion = QButtonGroup(mainwindow)
        self.buttonGroup_GCodeConversion.setObjectName(u"buttonGroup_GCodeConversion")
        self.buttonGroup_GCodeConversion.addButton(self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial)
        self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.setObjectName(u"pushButton_GCodeConversion_ZeroTopLeftOfMaterial")
        self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.setFont(font1)
        icon = QIcon()
        iconThemeName = u":/images/tango/22x22/actions/view-refresh.png"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.setIcon(icon)
        self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.setCheckable(True)
        self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.setChecked(True)

        self.gridLayout_GCodeConversion.addWidget(self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial, 1, 0, 1, 3)

        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial = QPushButton(self.scrollAreaWidgetContents_2)
        self.buttonGroup_GCodeConversion.addButton(self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial)
        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setObjectName(u"pushButton_GCodeConversion_ZeroLowerLeftOfMaterial")
        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setFont(font1)
        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setIcon(icon)
        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setCheckable(True)

        self.gridLayout_GCodeConversion.addWidget(self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial, 2, 0, 1, 3)

        self.pushButton_GCodeConversion_ZeroLowerLeftOfOp = QPushButton(self.scrollAreaWidgetContents_2)
        self.buttonGroup_GCodeConversion.addButton(self.pushButton_GCodeConversion_ZeroLowerLeftOfOp)
        self.pushButton_GCodeConversion_ZeroLowerLeftOfOp.setObjectName(u"pushButton_GCodeConversion_ZeroLowerLeftOfOp")
        self.pushButton_GCodeConversion_ZeroLowerLeftOfOp.setFont(font1)
        self.pushButton_GCodeConversion_ZeroLowerLeftOfOp.setIcon(icon)
        self.pushButton_GCodeConversion_ZeroLowerLeftOfOp.setCheckable(True)

        self.gridLayout_GCodeConversion.addWidget(self.pushButton_GCodeConversion_ZeroLowerLeftOfOp, 3, 0, 1, 3)

        self.pushButton_GCodeConversion_ZeroCenterOfOp = QPushButton(self.scrollAreaWidgetContents_2)
        self.buttonGroup_GCodeConversion.addButton(self.pushButton_GCodeConversion_ZeroCenterOfOp)
        self.pushButton_GCodeConversion_ZeroCenterOfOp.setObjectName(u"pushButton_GCodeConversion_ZeroCenterOfOp")
        self.pushButton_GCodeConversion_ZeroCenterOfOp.setFont(font1)
        self.pushButton_GCodeConversion_ZeroCenterOfOp.setIcon(icon)
        self.pushButton_GCodeConversion_ZeroCenterOfOp.setCheckable(True)

        self.gridLayout_GCodeConversion.addWidget(self.pushButton_GCodeConversion_ZeroCenterOfOp, 4, 0, 1, 3)


        self.verticalLayoutGCodeConversion.addLayout(self.gridLayout_GCodeConversion)


        self.verticalLayout_5.addLayout(self.verticalLayoutGCodeConversion)

        self.verticalLayoutGCodeGeneration = QVBoxLayout()
        self.verticalLayoutGCodeGeneration.setObjectName(u"verticalLayoutGCodeGeneration")
        self.labelGCodeGeneration = QLabel(self.scrollAreaWidgetContents_2)
        self.labelGCodeGeneration.setObjectName(u"labelGCodeGeneration")
        self.labelGCodeGeneration.setFont(font)
        self.labelGCodeGeneration.setStyleSheet(u"background-color: rgb(188, 188, 188);")

        self.verticalLayoutGCodeGeneration.addWidget(self.labelGCodeGeneration)

        self.formLayout_GCodeGeneration = QFormLayout()
        self.formLayout_GCodeGeneration.setObjectName(u"formLayout_GCodeGeneration")
        self.formLayout_GCodeGeneration.setFormAlignment(Qt.AlignCenter)
        self.label_GCodeGeneration_ReturnToZeroAtEnd = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setObjectName(u"label_GCodeGeneration_ReturnToZeroAtEnd")
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setFont(font1)
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_GCodeGeneration.setWidget(0, QFormLayout.LabelRole, self.label_GCodeGeneration_ReturnToZeroAtEnd)

        self.checkBox_GCodeGeneration_ReturnToZeroAtEnd = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setObjectName(u"checkBox_GCodeGeneration_ReturnToZeroAtEnd")

        self.formLayout_GCodeGeneration.setWidget(0, QFormLayout.FieldRole, self.checkBox_GCodeGeneration_ReturnToZeroAtEnd)

        self.label_GCodeGeneration_SpindleControl = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeGeneration_SpindleControl.setObjectName(u"label_GCodeGeneration_SpindleControl")
        self.label_GCodeGeneration_SpindleControl.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(1, QFormLayout.LabelRole, self.label_GCodeGeneration_SpindleControl)

        self.checkBox_GCodeGeneration_SpindleControl = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_GCodeGeneration_SpindleControl.setObjectName(u"checkBox_GCodeGeneration_SpindleControl")
        self.checkBox_GCodeGeneration_SpindleControl.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(1, QFormLayout.FieldRole, self.checkBox_GCodeGeneration_SpindleControl)

        self.label_GCodeGeneration_SpindleSpeed = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeGeneration_SpindleSpeed.setObjectName(u"label_GCodeGeneration_SpindleSpeed")
        self.label_GCodeGeneration_SpindleSpeed.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(2, QFormLayout.LabelRole, self.label_GCodeGeneration_SpindleSpeed)

        self.spinBox_GCodeGeneration_SpindleSpeed = QSpinBox(self.scrollAreaWidgetContents_2)
        self.spinBox_GCodeGeneration_SpindleSpeed.setObjectName(u"spinBox_GCodeGeneration_SpindleSpeed")
        self.spinBox_GCodeGeneration_SpindleSpeed.setMaximum(25000)
        self.spinBox_GCodeGeneration_SpindleSpeed.setSingleStep(50)

        self.formLayout_GCodeGeneration.setWidget(2, QFormLayout.FieldRole, self.spinBox_GCodeGeneration_SpindleSpeed)

        self.label_GCodeGeneration_ProgramEnd = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeGeneration_ProgramEnd.setObjectName(u"label_GCodeGeneration_ProgramEnd")
        self.label_GCodeGeneration_ProgramEnd.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(3, QFormLayout.LabelRole, self.label_GCodeGeneration_ProgramEnd)

        self.checkBox_GCodeGeneration_ProgramEnd = QCheckBox(self.scrollAreaWidgetContents_2)
        self.checkBox_GCodeGeneration_ProgramEnd.setObjectName(u"checkBox_GCodeGeneration_ProgramEnd")
        self.checkBox_GCodeGeneration_ProgramEnd.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(3, QFormLayout.FieldRole, self.checkBox_GCodeGeneration_ProgramEnd)


        self.verticalLayoutGCodeGeneration.addLayout(self.formLayout_GCodeGeneration)


        self.verticalLayout_5.addLayout(self.verticalLayoutGCodeGeneration)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)

        self.verticalLayout_5.setStretch(3, 1)
        self.scrollArea_right.setWidget(self.scrollAreaWidgetContents_2)

        self.horizontalLayout_2.addWidget(self.scrollArea_right)

        self.horizontalLayout_2.setStretch(1, 1)
        mainwindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(mainwindow)
        self.statusbar.setObjectName(u"statusbar")
        mainwindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(mainwindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1226, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuJobs = QMenu(self.menubar)
        self.menuJobs.setObjectName(u"menuJobs")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        mainwindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuJobs.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpenSvg)
        self.menuFile.addSeparator()
        self.menuJobs.addAction(self.actionNewJob)
        self.menuJobs.addAction(self.actionOpenJob)
        self.menuJobs.addAction(self.actionSaveJobAs)
        self.menuJobs.addAction(self.actionSaveJob)
        self.menuHelp.addAction(self.actionTutorial)
        self.menuHelp.addAction(self.actionAboutQt)
        self.menuHelp.addAction(self.actionAboutPyCut)
        self.menuSettings.addAction(self.actionSettings)

        self.retranslateUi(mainwindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(mainwindow)
    # setupUi

    def retranslateUi(self, mainwindow):
        mainwindow.setWindowTitle(QCoreApplication.translate("mainwindow", u"main", None))
        self.actionOpenSvg.setText(QCoreApplication.translate("mainwindow", u"Open SVG", None))
        self.actionNewJob.setText(QCoreApplication.translate("mainwindow", u"New Job", None))
        self.actionOpenJob.setText(QCoreApplication.translate("mainwindow", u"Open Job...", None))
        self.actionSaveJobAs.setText(QCoreApplication.translate("mainwindow", u"Save Job As...", None))
        self.actionSaveJob.setText(QCoreApplication.translate("mainwindow", u"Save Job", None))
        self.actionTutorial.setText(QCoreApplication.translate("mainwindow", u"Tutorial", None))
        self.actionAboutQt.setText(QCoreApplication.translate("mainwindow", u"About &Qt", None))
        self.actionAboutPyCut.setText(QCoreApplication.translate("mainwindow", u"About PyCut", None))
        self.actionSettings.setText(QCoreApplication.translate("mainwindow", u"Settings...", None))
        self.label_SvgSettings.setText(QCoreApplication.translate("mainwindow", u" Svg Settings", None))
        self.label_PxPerInch.setText(QCoreApplication.translate("mainwindow", u"user units scale factor", None))
        self.label_SvgModelWidth.setText(QCoreApplication.translate("mainwindow", u"width", None))
        self.doubleSpinBox_SvgModelWidth.setSuffix(QCoreApplication.translate("mainwindow", u"mm", None))
        self.label_SvgModelHeight.setText(QCoreApplication.translate("mainwindow", u"height", None))
        self.doubleSpinBox_SvgModelHeight.setSuffix(QCoreApplication.translate("mainwindow", u"mm", None))
        self.label_Tool.setText(QCoreApplication.translate("mainwindow", u" Tool (shared for all operations)", None))
        self.label_Tool_Plunge_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Diameter_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_StepOver.setText(QCoreApplication.translate("mainwindow", u"Step Over", None))
#if QT_CONFIG(tooltip)
        self.spinBox_Tool_Rapid.setToolTip(QCoreApplication.translate("mainwindow", u"The speed the tool moves while not cutting", None))
#endif // QT_CONFIG(tooltip)
        self.label_Tool_Units.setText(QCoreApplication.translate("mainwindow", u"Units", None))
        self.label_Tool_PassDepth.setText(QCoreApplication.translate("mainwindow", u"Pass Depth", None))
        self.label_Tool_Rapid_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Plunge.setText(QCoreApplication.translate("mainwindow", u"Plunge", None))
        self.label_Tool_Angle_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Cut_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Angle.setText(QCoreApplication.translate("mainwindow", u"Angle", None))
        self.label_Tool_Rapid.setText(QCoreApplication.translate("mainwindow", u"Rapid", None))
        self.label_Tool_StepOver_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Diameter.setText(QCoreApplication.translate("mainwindow", u"Diameter", None))
#if QT_CONFIG(tooltip)
        self.spinBox_Tool_Plunge.setToolTip(QCoreApplication.translate("mainwindow", u"The speed the tool plunges downwards into the material", None))
#endif // QT_CONFIG(tooltip)
        self.label_Tool_PassDepth_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Cut.setText(QCoreApplication.translate("mainwindow", u"Cut", None))
        self.comboBox_Tool_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.comboBox_Tool_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

#if QT_CONFIG(tooltip)
        self.spinBox_Tool_Cut.setToolTip(QCoreApplication.translate("mainwindow", u"The speed the tool moves horizontally during cutting", None))
#endif // QT_CONFIG(tooltip)
        self.labelCurveToLineConversion.setText(QCoreApplication.translate("mainwindow", u" Curve To Line Conversion", None))
        self.label_CurveToLineConversion_MinimumNbSegments.setText(QCoreApplication.translate("mainwindow", u"Minimum Segments", None))
        self.label_CurveToLineConversion_MinimumSegmentsLength.setText(QCoreApplication.translate("mainwindow", u"Minimum Segments Length                ", None))
        self.label_Tabs.setText(QCoreApplication.translate("mainwindow", u" Tabs", None))
        self.label_TabsUnits.setText(QCoreApplication.translate("mainwindow", u"Units", None))
        self.comboBox_Tabs_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.comboBox_Tabs_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.label_Tabs_Height.setText(QCoreApplication.translate("mainwindow", u"Height", None))
        self.label.setText("")
        self.checkBox_Tabs_hideAllTabs.setText(QCoreApplication.translate("mainwindow", u"Hide all Tabs", None))
        self.checkBox_Tabs_hideDisabledTabs.setText(QCoreApplication.translate("mainwindow", u"Hide disabled Tabs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.svg), QCoreApplication.translate("mainwindow", u"SVG", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.viewer), QCoreApplication.translate("mainwindow", u"GCode Viewer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.simulator), QCoreApplication.translate("mainwindow", u"GCode Simulator", None))
        self.pushButton_SaveGcode.setText(QCoreApplication.translate("mainwindow", u"Save Gcode", None))
        self.labelMaterial.setText(QCoreApplication.translate("mainwindow", u" Material", None))
        self.label_Material_Units.setText(QCoreApplication.translate("mainwindow", u"Units", None))
        self.comboBox_Material_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.comboBox_Material_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.label_Material_Thickness.setText(QCoreApplication.translate("mainwindow", u"Thickness", None))
        self.label_Material_ZOrigin.setText(QCoreApplication.translate("mainwindow", u"Z Origin", None))
        self.comboBox_Material_ZOrigin.setItemText(0, QCoreApplication.translate("mainwindow", u"Top", None))
        self.comboBox_Material_ZOrigin.setItemText(1, QCoreApplication.translate("mainwindow", u"Bottom", None))

        self.label_Material_Clearance.setText(QCoreApplication.translate("mainwindow", u"Cleareance                                     ", None))
        self.label_GCcodeConversion.setText(QCoreApplication.translate("mainwindow", u" GCode Conversion", None))
        self.label_GCodeConversion_YOffset_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_YOffset.setText(QCoreApplication.translate("mainwindow", u"Y Offset", None))
        self.label_GCodeConversion_GCodeUnits.setText(QCoreApplication.translate("mainwindow", u"Gcode Units", None))
        self.label_GCodeConversion_MaxY.setText(QCoreApplication.translate("mainwindow", u"Max Y", None))
        self.label_GCodeConversion_MinX_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.checkBox_GCodeConversion_FlipXY.setText(QCoreApplication.translate("mainwindow", u"Flip X/Y", None))
        self.label_GCodeConversion_MinX.setText(QCoreApplication.translate("mainwindow", u"Min X", None))
        self.label_GCodeConversion_MaxX.setText(QCoreApplication.translate("mainwindow", u"Max X", None))
        self.label_GCodeConversion_XOffset_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MaxY_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MaxX_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MinY_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MinY.setText(QCoreApplication.translate("mainwindow", u"Min Y", None))
        self.label_GCodeConversion_XOffset.setText(QCoreApplication.translate("mainwindow", u"X Offset", None))
        self.comboBox_GCodeConversion_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.comboBox_GCodeConversion_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.pushButton_GCodeConversion_ZeroTopLeftOfMaterial.setText(QCoreApplication.translate("mainwindow", u"Zero top left Material       ", None))
        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setText(QCoreApplication.translate("mainwindow", u"Zero lower left (Material)", None))
        self.pushButton_GCodeConversion_ZeroLowerLeftOfOp.setText(QCoreApplication.translate("mainwindow", u"Zero lower left (Op)         ", None))
        self.pushButton_GCodeConversion_ZeroCenterOfOp.setText(QCoreApplication.translate("mainwindow", u"Zero center (Op)               ", None))
        self.labelGCodeGeneration.setText(QCoreApplication.translate("mainwindow", u" GCode Generation", None))
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setText(QCoreApplication.translate("mainwindow", u"Return to 0,0 at end", None))
        self.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setText("")
        self.label_GCodeGeneration_SpindleControl.setText(QCoreApplication.translate("mainwindow", u"Spindle automatic", None))
        self.checkBox_GCodeGeneration_SpindleControl.setText(QCoreApplication.translate("mainwindow", u"[M3/M5]", None))
        self.label_GCodeGeneration_SpindleSpeed.setText(QCoreApplication.translate("mainwindow", u"Spindle speed", None))
        self.label_GCodeGeneration_ProgramEnd.setText(QCoreApplication.translate("mainwindow", u"Program End", None))
        self.checkBox_GCodeGeneration_ProgramEnd.setText(QCoreApplication.translate("mainwindow", u"[M2]", None))
        self.menuFile.setTitle(QCoreApplication.translate("mainwindow", u"File", None))
        self.menuJobs.setTitle(QCoreApplication.translate("mainwindow", u"Jobs", None))
        self.menuHelp.setTitle(QCoreApplication.translate("mainwindow", u"Help", None))
        self.menuSettings.setTitle(QCoreApplication.translate("mainwindow", u"Settings", None))
    # retranslateUi

