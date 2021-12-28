# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.2.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QSplitter,
    QStatusBar, QTabWidget, QVBoxLayout, QWidget)

from operations_tableview import PyCutOperationsTableViewManager
from tabs_tableview import PyCutTabsTableViewManager

class Ui_mainwindow(object):
    def setupUi(self, mainwindow):
        if not mainwindow.objectName():
            mainwindow.setObjectName(u"mainwindow")
        mainwindow.resize(1226, 1006)
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
        self.centralwidget = QWidget(mainwindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayoutLeft = QVBoxLayout()
        self.verticalLayoutLeft.setObjectName(u"verticalLayoutLeft")
        self.verticalLayoutSettingsContent = QVBoxLayout()
        self.verticalLayoutSettingsContent.setObjectName(u"verticalLayoutSettingsContent")
        self.verticalLayoutSettingsContent.setContentsMargins(-1, -1, -1, 20)
        self.label_SvgSettings = QLabel(self.centralwidget)
        self.label_SvgSettings.setObjectName(u"label_SvgSettings")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_SvgSettings.setFont(font)
        self.label_SvgSettings.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutSettingsContent.addWidget(self.label_SvgSettings)

        self.grid_Settings = QWidget(self.centralwidget)
        self.grid_Settings.setObjectName(u"grid_Settings")
        self.grid_Settings.setMinimumSize(QSize(0, 22))
        self.verticalLayout_6 = QVBoxLayout(self.grid_Settings)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_PxPerInch = QLabel(self.grid_Settings)
        self.label_PxPerInch.setObjectName(u"label_PxPerInch")
        font1 = QFont()
        font1.setBold(True)
        self.label_PxPerInch.setFont(font1)

        self.horizontalLayout.addWidget(self.label_PxPerInch)

        self.spinBox_PxPerInch = QSpinBox(self.grid_Settings)
        self.spinBox_PxPerInch.setObjectName(u"spinBox_PxPerInch")
        self.spinBox_PxPerInch.setMaximum(126)
        self.spinBox_PxPerInch.setValue(96)

        self.horizontalLayout.addWidget(self.spinBox_PxPerInch)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_6.addLayout(self.verticalLayout_2)


        self.verticalLayoutSettingsContent.addWidget(self.grid_Settings)


        self.verticalLayoutLeft.addLayout(self.verticalLayoutSettingsContent)

        self.verticalLayoutToolContent = QVBoxLayout()
        self.verticalLayoutToolContent.setObjectName(u"verticalLayoutToolContent")
        self.verticalLayoutToolContent.setContentsMargins(-1, -1, -1, 20)
        self.label_Tool = QLabel(self.centralwidget)
        self.label_Tool.setObjectName(u"label_Tool")
        self.label_Tool.setFont(font)
        self.label_Tool.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutToolContent.addWidget(self.label_Tool)

        self.grid_Tool = QWidget(self.centralwidget)
        self.grid_Tool.setObjectName(u"grid_Tool")
        self.gridLayout_2 = QGridLayout(self.grid_Tool)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_Tool = QGridLayout()
        self.gridLayout_Tool.setObjectName(u"gridLayout_Tool")
        self.label_Tool_Plunge_UnitsDescr = QLabel(self.grid_Tool)
        self.label_Tool_Plunge_UnitsDescr.setObjectName(u"label_Tool_Plunge_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Plunge_UnitsDescr, 6, 1, 1, 1)

        self.label_Tool_Diameter_UnitsDescr = QLabel(self.grid_Tool)
        self.label_Tool_Diameter_UnitsDescr.setObjectName(u"label_Tool_Diameter_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Diameter_UnitsDescr, 1, 1, 1, 1)

        self.label_Tool_StepOver = QLabel(self.grid_Tool)
        self.label_Tool_StepOver.setObjectName(u"label_Tool_StepOver")
        self.label_Tool_StepOver.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_StepOver, 4, 0, 1, 1)

        self.spinBox_Tool_Rapid = QSpinBox(self.grid_Tool)
        self.spinBox_Tool_Rapid.setObjectName(u"spinBox_Tool_Rapid")
        self.spinBox_Tool_Rapid.setMaximum(1000)
        self.spinBox_Tool_Rapid.setValue(500)

        self.gridLayout_Tool.addWidget(self.spinBox_Tool_Rapid, 5, 2, 1, 1)

        self.label_Tool_Units = QLabel(self.grid_Tool)
        self.label_Tool_Units.setObjectName(u"label_Tool_Units")
        self.label_Tool_Units.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Units, 0, 0, 1, 1)

        self.label_Tool_PassDepth = QLabel(self.grid_Tool)
        self.label_Tool_PassDepth.setObjectName(u"label_Tool_PassDepth")
        self.label_Tool_PassDepth.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_PassDepth, 3, 0, 1, 1)

        self.label_Tool_Rapid_UnitsDescr = QLabel(self.grid_Tool)
        self.label_Tool_Rapid_UnitsDescr.setObjectName(u"label_Tool_Rapid_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Rapid_UnitsDescr, 5, 1, 1, 1)

        self.label_Tool_Plunge = QLabel(self.grid_Tool)
        self.label_Tool_Plunge.setObjectName(u"label_Tool_Plunge")
        self.label_Tool_Plunge.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Plunge, 6, 0, 1, 1)

        self.label_Tool_Angle_UnitsDescr = QLabel(self.grid_Tool)
        self.label_Tool_Angle_UnitsDescr.setObjectName(u"label_Tool_Angle_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Angle_UnitsDescr, 2, 1, 1, 1)

        self.label_Tool_Cut_UnitsDescr = QLabel(self.grid_Tool)
        self.label_Tool_Cut_UnitsDescr.setObjectName(u"label_Tool_Cut_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Cut_UnitsDescr, 7, 1, 1, 1)

        self.label_Tool_Angle = QLabel(self.grid_Tool)
        self.label_Tool_Angle.setObjectName(u"label_Tool_Angle")
        self.label_Tool_Angle.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Angle, 2, 0, 1, 1)

        self.label_Tool_Rapid = QLabel(self.grid_Tool)
        self.label_Tool_Rapid.setObjectName(u"label_Tool_Rapid")
        self.label_Tool_Rapid.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Rapid, 5, 0, 1, 1)

        self.spinBox_Tool_Angle = QSpinBox(self.grid_Tool)
        self.spinBox_Tool_Angle.setObjectName(u"spinBox_Tool_Angle")
        self.spinBox_Tool_Angle.setMaximum(180)
        self.spinBox_Tool_Angle.setValue(180)

        self.gridLayout_Tool.addWidget(self.spinBox_Tool_Angle, 2, 2, 1, 1)

        self.label_Tool_StepOver_UnitsDescr = QLabel(self.grid_Tool)
        self.label_Tool_StepOver_UnitsDescr.setObjectName(u"label_Tool_StepOver_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_StepOver_UnitsDescr, 4, 1, 1, 1)

        self.doubleSpinBox_Tool_Diameter = QDoubleSpinBox(self.grid_Tool)
        self.doubleSpinBox_Tool_Diameter.setObjectName(u"doubleSpinBox_Tool_Diameter")
        self.doubleSpinBox_Tool_Diameter.setDecimals(3)
        self.doubleSpinBox_Tool_Diameter.setMaximum(32.000000000000000)
        self.doubleSpinBox_Tool_Diameter.setValue(1.000000000000000)

        self.gridLayout_Tool.addWidget(self.doubleSpinBox_Tool_Diameter, 1, 2, 1, 1)

        self.label_Tool_Diameter = QLabel(self.grid_Tool)
        self.label_Tool_Diameter.setObjectName(u"label_Tool_Diameter")
        self.label_Tool_Diameter.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Diameter, 1, 0, 1, 1)

        self.spinBox_Tool_Plunge = QSpinBox(self.grid_Tool)
        self.spinBox_Tool_Plunge.setObjectName(u"spinBox_Tool_Plunge")
        self.spinBox_Tool_Plunge.setMaximum(1000)
        self.spinBox_Tool_Plunge.setValue(100)

        self.gridLayout_Tool.addWidget(self.spinBox_Tool_Plunge, 6, 2, 1, 1)

        self.label_Tool_PassDepth_UnitsDescr = QLabel(self.grid_Tool)
        self.label_Tool_PassDepth_UnitsDescr.setObjectName(u"label_Tool_PassDepth_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_PassDepth_UnitsDescr, 3, 1, 1, 1)

        self.label_Tool_Cut = QLabel(self.grid_Tool)
        self.label_Tool_Cut.setObjectName(u"label_Tool_Cut")
        self.label_Tool_Cut.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Cut, 7, 0, 1, 1)

        self.doubleSpinBox_Tool_StepOver = QDoubleSpinBox(self.grid_Tool)
        self.doubleSpinBox_Tool_StepOver.setObjectName(u"doubleSpinBox_Tool_StepOver")
        self.doubleSpinBox_Tool_StepOver.setDecimals(3)
        self.doubleSpinBox_Tool_StepOver.setMaximum(1.000000000000000)
        self.doubleSpinBox_Tool_StepOver.setSingleStep(0.010000000000000)
        self.doubleSpinBox_Tool_StepOver.setValue(0.400000000000000)

        self.gridLayout_Tool.addWidget(self.doubleSpinBox_Tool_StepOver, 4, 2, 1, 1)

        self.comboBox_Tool_Units = QComboBox(self.grid_Tool)
        self.comboBox_Tool_Units.addItem("")
        self.comboBox_Tool_Units.addItem("")
        self.comboBox_Tool_Units.setObjectName(u"comboBox_Tool_Units")

        self.gridLayout_Tool.addWidget(self.comboBox_Tool_Units, 0, 1, 1, 1)

        self.doubleSpinBox_Tool_PassDepth = QDoubleSpinBox(self.grid_Tool)
        self.doubleSpinBox_Tool_PassDepth.setObjectName(u"doubleSpinBox_Tool_PassDepth")
        self.doubleSpinBox_Tool_PassDepth.setDecimals(3)
        self.doubleSpinBox_Tool_PassDepth.setMaximum(10.000000000000000)
        self.doubleSpinBox_Tool_PassDepth.setSingleStep(0.500000000000000)
        self.doubleSpinBox_Tool_PassDepth.setValue(0.200000000000000)

        self.gridLayout_Tool.addWidget(self.doubleSpinBox_Tool_PassDepth, 3, 2, 1, 1)

        self.spinBox_Tool_Cut = QSpinBox(self.grid_Tool)
        self.spinBox_Tool_Cut.setObjectName(u"spinBox_Tool_Cut")
        self.spinBox_Tool_Cut.setMaximum(1000)
        self.spinBox_Tool_Cut.setValue(200)

        self.gridLayout_Tool.addWidget(self.spinBox_Tool_Cut, 7, 2, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout_Tool, 1, 0, 1, 1)


        self.verticalLayoutToolContent.addWidget(self.grid_Tool)


        self.verticalLayoutLeft.addLayout(self.verticalLayoutToolContent)

        self.verticalLayoutTabsContent = QVBoxLayout()
        self.verticalLayoutTabsContent.setObjectName(u"verticalLayoutTabsContent")
        self.verticalLayoutTabsContent.setContentsMargins(-1, -1, -1, 20)
        self.label_Tabs = QLabel(self.centralwidget)
        self.label_Tabs.setObjectName(u"label_Tabs")
        self.label_Tabs.setEnabled(True)
        self.label_Tabs.setFont(font)
        self.label_Tabs.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutTabsContent.addWidget(self.label_Tabs)

        self.grid_Tabs = QWidget(self.centralwidget)
        self.grid_Tabs.setObjectName(u"grid_Tabs")
        self.grid_Tabs.setMinimumSize(QSize(0, 44))
        self.verticalLayout_4 = QVBoxLayout(self.grid_Tabs)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.formLayout_Tabs = QFormLayout()
        self.formLayout_Tabs.setObjectName(u"formLayout_Tabs")
        self.formLayout_Tabs.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_Tabs.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_TabsUnits = QLabel(self.grid_Tabs)
        self.label_TabsUnits.setObjectName(u"label_TabsUnits")
        self.label_TabsUnits.setFont(font1)

        self.formLayout_Tabs.setWidget(0, QFormLayout.LabelRole, self.label_TabsUnits)

        self.comboBox_Tabs_Units = QComboBox(self.grid_Tabs)
        self.comboBox_Tabs_Units.addItem("")
        self.comboBox_Tabs_Units.addItem("")
        self.comboBox_Tabs_Units.setObjectName(u"comboBox_Tabs_Units")
        self.comboBox_Tabs_Units.setEnabled(True)

        self.formLayout_Tabs.setWidget(0, QFormLayout.FieldRole, self.comboBox_Tabs_Units)

        self.label_Tabs_MaxCutDepth = QLabel(self.grid_Tabs)
        self.label_Tabs_MaxCutDepth.setObjectName(u"label_Tabs_MaxCutDepth")
        self.label_Tabs_MaxCutDepth.setFont(font1)

        self.formLayout_Tabs.setWidget(1, QFormLayout.LabelRole, self.label_Tabs_MaxCutDepth)

        self.doubleSpinBox_Tabs_MaxCutDepth = QDoubleSpinBox(self.grid_Tabs)
        self.doubleSpinBox_Tabs_MaxCutDepth.setObjectName(u"doubleSpinBox_Tabs_MaxCutDepth")
        self.doubleSpinBox_Tabs_MaxCutDepth.setEnabled(True)
        self.doubleSpinBox_Tabs_MaxCutDepth.setDecimals(3)

        self.formLayout_Tabs.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_Tabs_MaxCutDepth)


        self.verticalLayout_4.addLayout(self.formLayout_Tabs)


        self.verticalLayoutTabsContent.addWidget(self.grid_Tabs)

        self.tabsview_manager = PyCutTabsTableViewManager(self.centralwidget)
        self.tabsview_manager.setObjectName(u"tabsview_manager")
        self.tabsview_manager.setMinimumSize(QSize(0, 100))

        self.verticalLayoutTabsContent.addWidget(self.tabsview_manager)


        self.verticalLayoutLeft.addLayout(self.verticalLayoutTabsContent)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayoutLeft.addItem(self.verticalSpacer)

        self.verticalLayoutLeft.setStretch(3, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayoutLeft)

        self.centralArea = QWidget(self.centralwidget)
        self.centralArea.setObjectName(u"centralArea")
        self.centralArea.setMinimumSize(QSize(400, 0))
        self.centralArea.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.centralArea)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.splitter = QSplitter(self.centralArea)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(2)
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
        self.verticalLayout_5 = QVBoxLayout(self.simulator)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
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

        self.verticalLayoutRight = QVBoxLayout()
        self.verticalLayoutRight.setObjectName(u"verticalLayoutRight")
        self.verticalLayoutMaterial = QVBoxLayout()
        self.verticalLayoutMaterial.setObjectName(u"verticalLayoutMaterial")
        self.verticalLayoutMaterial.setContentsMargins(-1, -1, -1, 20)
        self.labelMaterial = QLabel(self.centralwidget)
        self.labelMaterial.setObjectName(u"labelMaterial")
        self.labelMaterial.setFont(font)
        self.labelMaterial.setStyleSheet(u"background-color: rgb(200, 200, 200);")

        self.verticalLayoutMaterial.addWidget(self.labelMaterial)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.widget_display_material = QWidget(self.centralwidget)
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
        self.label_Material_Units = QLabel(self.centralwidget)
        self.label_Material_Units.setObjectName(u"label_Material_Units")
        self.label_Material_Units.setFont(font1)

        self.formLayout_Material.setWidget(0, QFormLayout.LabelRole, self.label_Material_Units)

        self.comboBox_Material_Units = QComboBox(self.centralwidget)
        self.comboBox_Material_Units.addItem("")
        self.comboBox_Material_Units.addItem("")
        self.comboBox_Material_Units.setObjectName(u"comboBox_Material_Units")

        self.formLayout_Material.setWidget(0, QFormLayout.FieldRole, self.comboBox_Material_Units)

        self.label_Material_Thickness = QLabel(self.centralwidget)
        self.label_Material_Thickness.setObjectName(u"label_Material_Thickness")
        self.label_Material_Thickness.setFont(font1)

        self.formLayout_Material.setWidget(1, QFormLayout.LabelRole, self.label_Material_Thickness)

        self.doubleSpinBox_Material_Thickness = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_Material_Thickness.setObjectName(u"doubleSpinBox_Material_Thickness")
        self.doubleSpinBox_Material_Thickness.setMaximum(100.000000000000000)
        self.doubleSpinBox_Material_Thickness.setValue(50.000000000000000)

        self.formLayout_Material.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_Material_Thickness)

        self.label_Material_ZOrigin = QLabel(self.centralwidget)
        self.label_Material_ZOrigin.setObjectName(u"label_Material_ZOrigin")
        self.label_Material_ZOrigin.setFont(font1)

        self.formLayout_Material.setWidget(2, QFormLayout.LabelRole, self.label_Material_ZOrigin)

        self.comboBox_Material_ZOrigin = QComboBox(self.centralwidget)
        self.comboBox_Material_ZOrigin.addItem("")
        self.comboBox_Material_ZOrigin.addItem("")
        self.comboBox_Material_ZOrigin.setObjectName(u"comboBox_Material_ZOrigin")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_Material_ZOrigin.sizePolicy().hasHeightForWidth())
        self.comboBox_Material_ZOrigin.setSizePolicy(sizePolicy)

        self.formLayout_Material.setWidget(2, QFormLayout.FieldRole, self.comboBox_Material_ZOrigin)

        self.label_Material_Clearance = QLabel(self.centralwidget)
        self.label_Material_Clearance.setObjectName(u"label_Material_Clearance")
        self.label_Material_Clearance.setFont(font1)
        self.label_Material_Clearance.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_Material.setWidget(3, QFormLayout.LabelRole, self.label_Material_Clearance)

        self.doubleSpinBox_Material_Clearance = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_Material_Clearance.setObjectName(u"doubleSpinBox_Material_Clearance")
        self.doubleSpinBox_Material_Clearance.setMaximum(100.000000000000000)
        self.doubleSpinBox_Material_Clearance.setValue(20.000000000000000)

        self.formLayout_Material.setWidget(3, QFormLayout.FieldRole, self.doubleSpinBox_Material_Clearance)


        self.verticalLayoutMaterial.addLayout(self.formLayout_Material)


        self.verticalLayoutRight.addLayout(self.verticalLayoutMaterial)

        self.verticalLayoutCurveToLineConversion = QVBoxLayout()
        self.verticalLayoutCurveToLineConversion.setObjectName(u"verticalLayoutCurveToLineConversion")
        self.verticalLayoutCurveToLineConversion.setContentsMargins(-1, -1, -1, 20)
        self.labelCurveToLineConversion = QLabel(self.centralwidget)
        self.labelCurveToLineConversion.setObjectName(u"labelCurveToLineConversion")
        self.labelCurveToLineConversion.setFont(font)
        self.labelCurveToLineConversion.setStyleSheet(u"background-color: rgb(196, 196, 196);")

        self.verticalLayoutCurveToLineConversion.addWidget(self.labelCurveToLineConversion)

        self.formLayoutCurveToLineConversion = QFormLayout()
        self.formLayoutCurveToLineConversion.setObjectName(u"formLayoutCurveToLineConversion")
        self.formLayoutCurveToLineConversion.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayoutCurveToLineConversion.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.formLayoutCurveToLineConversion.setVerticalSpacing(6)
        self.label_CurveToLineConversion_MinimumSegments = QLabel(self.centralwidget)
        self.label_CurveToLineConversion_MinimumSegments.setObjectName(u"label_CurveToLineConversion_MinimumSegments")
        self.label_CurveToLineConversion_MinimumSegments.setFont(font1)

        self.formLayoutCurveToLineConversion.setWidget(0, QFormLayout.LabelRole, self.label_CurveToLineConversion_MinimumSegments)

        self.doubleSpinBox_CurveToLineConversion_MinimumSegments = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_CurveToLineConversion_MinimumSegments.setObjectName(u"doubleSpinBox_CurveToLineConversion_MinimumSegments")
        self.doubleSpinBox_CurveToLineConversion_MinimumSegments.setEnabled(False)

        self.formLayoutCurveToLineConversion.setWidget(0, QFormLayout.FieldRole, self.doubleSpinBox_CurveToLineConversion_MinimumSegments)

        self.label_CurveToLineConversion_MinimumSegmentsLength = QLabel(self.centralwidget)
        self.label_CurveToLineConversion_MinimumSegmentsLength.setObjectName(u"label_CurveToLineConversion_MinimumSegmentsLength")
        self.label_CurveToLineConversion_MinimumSegmentsLength.setFont(font1)

        self.formLayoutCurveToLineConversion.setWidget(1, QFormLayout.LabelRole, self.label_CurveToLineConversion_MinimumSegmentsLength)

        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setObjectName(u"doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength")
        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setMaximum(1.000000000000000)
        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setSingleStep(0.010000000000000)
        self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength.setValue(0.010000000000000)

        self.formLayoutCurveToLineConversion.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_CurveToLineConversion_MinimumSegmentsLength)


        self.verticalLayoutCurveToLineConversion.addLayout(self.formLayoutCurveToLineConversion)


        self.verticalLayoutRight.addLayout(self.verticalLayoutCurveToLineConversion)

        self.verticalLayoutGCodeConversion = QVBoxLayout()
        self.verticalLayoutGCodeConversion.setObjectName(u"verticalLayoutGCodeConversion")
        self.label_GCcodeConversion = QLabel(self.centralwidget)
        self.label_GCcodeConversion.setObjectName(u"label_GCcodeConversion")
        self.label_GCcodeConversion.setFont(font)
        self.label_GCcodeConversion.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutGCodeConversion.addWidget(self.label_GCcodeConversion)

        self.gridLayout_GCodeConversion = QGridLayout()
        self.gridLayout_GCodeConversion.setObjectName(u"gridLayout_GCodeConversion")
        self.label_GCodeConversion_GCodeUnits = QLabel(self.centralwidget)
        self.label_GCodeConversion_GCodeUnits.setObjectName(u"label_GCodeConversion_GCodeUnits")
        self.label_GCodeConversion_GCodeUnits.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_GCodeUnits, 0, 0, 1, 1)

        self.comboBox_GCodeConversion_Units = QComboBox(self.centralwidget)
        self.comboBox_GCodeConversion_Units.addItem("")
        self.comboBox_GCodeConversion_Units.addItem("")
        self.comboBox_GCodeConversion_Units.setObjectName(u"comboBox_GCodeConversion_Units")

        self.gridLayout_GCodeConversion.addWidget(self.comboBox_GCodeConversion_Units, 0, 1, 1, 1)

        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial = QPushButton(self.centralwidget)
        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setObjectName(u"pushButton_GCodeConversion_ZeroLowerLeftOfMaterial")
        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial, 1, 0, 1, 2)

        self.checkBox_GCodeConversion_ZeroLowerLeftOfMaterial_AsDefault = QCheckBox(self.centralwidget)
        self.checkBox_GCodeConversion_ZeroLowerLeftOfMaterial_AsDefault.setObjectName(u"checkBox_GCodeConversion_ZeroLowerLeftOfMaterial_AsDefault")

        self.gridLayout_GCodeConversion.addWidget(self.checkBox_GCodeConversion_ZeroLowerLeftOfMaterial_AsDefault, 1, 2, 1, 1)

        self.pushButton_GCodeConversion_ZeroLowerLeft = QPushButton(self.centralwidget)
        self.pushButton_GCodeConversion_ZeroLowerLeft.setObjectName(u"pushButton_GCodeConversion_ZeroLowerLeft")
        self.pushButton_GCodeConversion_ZeroLowerLeft.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.pushButton_GCodeConversion_ZeroLowerLeft, 2, 0, 1, 2)

        self.checkBox_GCodeConversion_ZeroLowerLeft_AsDefault = QCheckBox(self.centralwidget)
        self.checkBox_GCodeConversion_ZeroLowerLeft_AsDefault.setObjectName(u"checkBox_GCodeConversion_ZeroLowerLeft_AsDefault")

        self.gridLayout_GCodeConversion.addWidget(self.checkBox_GCodeConversion_ZeroLowerLeft_AsDefault, 2, 2, 1, 1)

        self.pushButton_GCodeConversion_ZeroCenter = QPushButton(self.centralwidget)
        self.pushButton_GCodeConversion_ZeroCenter.setObjectName(u"pushButton_GCodeConversion_ZeroCenter")
        self.pushButton_GCodeConversion_ZeroCenter.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.pushButton_GCodeConversion_ZeroCenter, 3, 0, 1, 2)

        self.checkBox_GCodeConversion_ZeroCenter_AsDefault = QCheckBox(self.centralwidget)
        self.checkBox_GCodeConversion_ZeroCenter_AsDefault.setObjectName(u"checkBox_GCodeConversion_ZeroCenter_AsDefault")

        self.gridLayout_GCodeConversion.addWidget(self.checkBox_GCodeConversion_ZeroCenter_AsDefault, 3, 2, 1, 1)

        self.label_GCodeConversion_XOffset = QLabel(self.centralwidget)
        self.label_GCodeConversion_XOffset.setObjectName(u"label_GCodeConversion_XOffset")
        self.label_GCodeConversion_XOffset.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_XOffset, 4, 0, 1, 1)

        self.label_GCodeConversion_XOffset_UnitsDescr = QLabel(self.centralwidget)
        self.label_GCodeConversion_XOffset_UnitsDescr.setObjectName(u"label_GCodeConversion_XOffset_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_XOffset_UnitsDescr, 4, 1, 1, 1)

        self.doubleSpinBox_GCodeConversion_XOffset = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_GCodeConversion_XOffset.setObjectName(u"doubleSpinBox_GCodeConversion_XOffset")
        self.doubleSpinBox_GCodeConversion_XOffset.setMinimum(-100.000000000000000)
        self.doubleSpinBox_GCodeConversion_XOffset.setMaximum(100.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_XOffset, 4, 2, 1, 1)

        self.label_GCodeConversion_YOffset = QLabel(self.centralwidget)
        self.label_GCodeConversion_YOffset.setObjectName(u"label_GCodeConversion_YOffset")
        self.label_GCodeConversion_YOffset.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_YOffset, 5, 0, 1, 1)

        self.label_GCodeConversion_YOffset_UnitsDescr = QLabel(self.centralwidget)
        self.label_GCodeConversion_YOffset_UnitsDescr.setObjectName(u"label_GCodeConversion_YOffset_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_YOffset_UnitsDescr, 5, 1, 1, 1)

        self.doubleSpinBox_GCodeConversion_YOffset = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_GCodeConversion_YOffset.setObjectName(u"doubleSpinBox_GCodeConversion_YOffset")
        self.doubleSpinBox_GCodeConversion_YOffset.setMinimum(-100.000000000000000)
        self.doubleSpinBox_GCodeConversion_YOffset.setMaximum(100.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_YOffset, 5, 2, 1, 1)

        self.label_GCodeConversion_MinX = QLabel(self.centralwidget)
        self.label_GCodeConversion_MinX.setObjectName(u"label_GCodeConversion_MinX")
        self.label_GCodeConversion_MinX.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinX, 6, 0, 1, 1)

        self.label_GCodeConversion_MinX_UnitsDescr = QLabel(self.centralwidget)
        self.label_GCodeConversion_MinX_UnitsDescr.setObjectName(u"label_GCodeConversion_MinX_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinX_UnitsDescr, 6, 1, 1, 1)

        self.doubleSpinBox_GCodeConversion_MinX = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_GCodeConversion_MinX.setObjectName(u"doubleSpinBox_GCodeConversion_MinX")
        self.doubleSpinBox_GCodeConversion_MinX.setEnabled(False)
        self.doubleSpinBox_GCodeConversion_MinX.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MinX.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_MinX, 6, 2, 1, 1)

        self.label_GCodeConversion_MaxX = QLabel(self.centralwidget)
        self.label_GCodeConversion_MaxX.setObjectName(u"label_GCodeConversion_MaxX")
        self.label_GCodeConversion_MaxX.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxX, 7, 0, 1, 1)

        self.doubleSpinBox_GCodeConversion_MaxX = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_GCodeConversion_MaxX.setObjectName(u"doubleSpinBox_GCodeConversion_MaxX")
        self.doubleSpinBox_GCodeConversion_MaxX.setEnabled(False)
        self.doubleSpinBox_GCodeConversion_MaxX.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MaxX.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_MaxX, 7, 2, 1, 1)

        self.label_GCodeConversion_MaxX_UnitsDescr = QLabel(self.centralwidget)
        self.label_GCodeConversion_MaxX_UnitsDescr.setObjectName(u"label_GCodeConversion_MaxX_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxX_UnitsDescr, 7, 1, 1, 1)

        self.label_GCodeConversion_MinY = QLabel(self.centralwidget)
        self.label_GCodeConversion_MinY.setObjectName(u"label_GCodeConversion_MinY")
        self.label_GCodeConversion_MinY.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinY, 8, 0, 1, 1)

        self.label_GCodeConversion_MinY_UnitsDescr = QLabel(self.centralwidget)
        self.label_GCodeConversion_MinY_UnitsDescr.setObjectName(u"label_GCodeConversion_MinY_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinY_UnitsDescr, 8, 1, 1, 1)

        self.doubleSpinBox_GCodeConversion_MinY = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_GCodeConversion_MinY.setObjectName(u"doubleSpinBox_GCodeConversion_MinY")
        self.doubleSpinBox_GCodeConversion_MinY.setEnabled(False)
        self.doubleSpinBox_GCodeConversion_MinY.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MinY.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_MinY, 8, 2, 1, 1)

        self.label_GCodeConversion_MaxY = QLabel(self.centralwidget)
        self.label_GCodeConversion_MaxY.setObjectName(u"label_GCodeConversion_MaxY")
        self.label_GCodeConversion_MaxY.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxY, 9, 0, 1, 1)

        self.label_GCodeConversion_MaxY_UnitsDescr = QLabel(self.centralwidget)
        self.label_GCodeConversion_MaxY_UnitsDescr.setObjectName(u"label_GCodeConversion_MaxY_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxY_UnitsDescr, 9, 1, 1, 1)

        self.doubleSpinBox_GCodeConversion_MaxY = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_GCodeConversion_MaxY.setObjectName(u"doubleSpinBox_GCodeConversion_MaxY")
        self.doubleSpinBox_GCodeConversion_MaxY.setEnabled(False)
        self.doubleSpinBox_GCodeConversion_MaxY.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MaxY.setMaximum(1000.000000000000000)
        self.doubleSpinBox_GCodeConversion_MaxY.setValue(0.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.doubleSpinBox_GCodeConversion_MaxY, 9, 2, 1, 1)


        self.verticalLayoutGCodeConversion.addLayout(self.gridLayout_GCodeConversion)


        self.verticalLayoutRight.addLayout(self.verticalLayoutGCodeConversion)

        self.verticalLayoutGCodeGeneration = QVBoxLayout()
        self.verticalLayoutGCodeGeneration.setObjectName(u"verticalLayoutGCodeGeneration")
        self.labelGCodeGeneration = QLabel(self.centralwidget)
        self.labelGCodeGeneration.setObjectName(u"labelGCodeGeneration")
        self.labelGCodeGeneration.setFont(font)
        self.labelGCodeGeneration.setStyleSheet(u"background-color: rgb(188, 188, 188);")

        self.verticalLayoutGCodeGeneration.addWidget(self.labelGCodeGeneration)

        self.formLayout_GCodeGeneration = QFormLayout()
        self.formLayout_GCodeGeneration.setObjectName(u"formLayout_GCodeGeneration")
        self.formLayout_GCodeGeneration.setFormAlignment(Qt.AlignCenter)
        self.label_GCodeGeneration_ReturnToZeroAtEnd = QLabel(self.centralwidget)
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setObjectName(u"label_GCodeGeneration_ReturnToZeroAtEnd")
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setFont(font1)
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_GCodeGeneration.setWidget(0, QFormLayout.LabelRole, self.label_GCodeGeneration_ReturnToZeroAtEnd)

        self.checkBox_GCodeGeneration_ReturnToZeroAtEnd = QCheckBox(self.centralwidget)
        self.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setObjectName(u"checkBox_GCodeGeneration_ReturnToZeroAtEnd")

        self.formLayout_GCodeGeneration.setWidget(0, QFormLayout.FieldRole, self.checkBox_GCodeGeneration_ReturnToZeroAtEnd)

        self.label_GCodeGenerationSpindleAutomatic = QLabel(self.centralwidget)
        self.label_GCodeGenerationSpindleAutomatic.setObjectName(u"label_GCodeGenerationSpindleAutomatic")
        self.label_GCodeGenerationSpindleAutomatic.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(1, QFormLayout.LabelRole, self.label_GCodeGenerationSpindleAutomatic)

        self.checkBox_GCodeGeneration_SpindleAutomatic = QCheckBox(self.centralwidget)
        self.checkBox_GCodeGeneration_SpindleAutomatic.setObjectName(u"checkBox_GCodeGeneration_SpindleAutomatic")
        self.checkBox_GCodeGeneration_SpindleAutomatic.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(1, QFormLayout.FieldRole, self.checkBox_GCodeGeneration_SpindleAutomatic)

        self.label_GCodeGenerationSpindleSpeed = QLabel(self.centralwidget)
        self.label_GCodeGenerationSpindleSpeed.setObjectName(u"label_GCodeGenerationSpindleSpeed")
        self.label_GCodeGenerationSpindleSpeed.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(2, QFormLayout.LabelRole, self.label_GCodeGenerationSpindleSpeed)

        self.spinBox_GCodeGeneration_SpindleSpeed = QSpinBox(self.centralwidget)
        self.spinBox_GCodeGeneration_SpindleSpeed.setObjectName(u"spinBox_GCodeGeneration_SpindleSpeed")
        self.spinBox_GCodeGeneration_SpindleSpeed.setMaximum(50000)

        self.formLayout_GCodeGeneration.setWidget(2, QFormLayout.FieldRole, self.spinBox_GCodeGeneration_SpindleSpeed)


        self.verticalLayoutGCodeGeneration.addLayout(self.formLayout_GCodeGeneration)


        self.verticalLayoutRight.addLayout(self.verticalLayoutGCodeGeneration)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayoutRight.addItem(self.verticalSpacer_2)

        self.verticalLayoutRight.setStretch(4, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayoutRight)

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
        mainwindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuJobs.menuAction())
        self.menuFile.addAction(self.actionOpenSvg)
        self.menuFile.addSeparator()
        self.menuJobs.addAction(self.actionNewJob)
        self.menuJobs.addAction(self.actionOpenJob)
        self.menuJobs.addAction(self.actionSaveJobAs)
        self.menuJobs.addAction(self.actionSaveJob)

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
        self.label_SvgSettings.setText(QCoreApplication.translate("mainwindow", u"  Svg Settings", None))
        self.label_PxPerInch.setText(QCoreApplication.translate("mainwindow", u"px per inch", None))
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
        self.label_Tabs.setText(QCoreApplication.translate("mainwindow", u" Tabs", None))
        self.label_TabsUnits.setText(QCoreApplication.translate("mainwindow", u"Units", None))
        self.comboBox_Tabs_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.comboBox_Tabs_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.label_Tabs_MaxCutDepth.setText(QCoreApplication.translate("mainwindow", u"Max Cut Depth", None))
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
        self.labelCurveToLineConversion.setText(QCoreApplication.translate("mainwindow", u" Curve To Line Conversion", None))
        self.label_CurveToLineConversion_MinimumSegments.setText(QCoreApplication.translate("mainwindow", u"Minimum Segments", None))
        self.label_CurveToLineConversion_MinimumSegmentsLength.setText(QCoreApplication.translate("mainwindow", u"Minimum Segments Length                ", None))
        self.label_GCcodeConversion.setText(QCoreApplication.translate("mainwindow", u" GCode Conversion", None))
        self.label_GCodeConversion_GCodeUnits.setText(QCoreApplication.translate("mainwindow", u"Gcode Units", None))
        self.comboBox_GCodeConversion_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.comboBox_GCodeConversion_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.pushButton_GCodeConversion_ZeroLowerLeftOfMaterial.setText(QCoreApplication.translate("mainwindow", u"Zero lower left (Material)", None))
        self.checkBox_GCodeConversion_ZeroLowerLeftOfMaterial_AsDefault.setText(QCoreApplication.translate("mainwindow", u"as Default", None))
        self.pushButton_GCodeConversion_ZeroLowerLeft.setText(QCoreApplication.translate("mainwindow", u"Zero lower left (Op)", None))
        self.checkBox_GCodeConversion_ZeroLowerLeft_AsDefault.setText(QCoreApplication.translate("mainwindow", u"as Default", None))
        self.pushButton_GCodeConversion_ZeroCenter.setText(QCoreApplication.translate("mainwindow", u"Zero center (Op)", None))
        self.checkBox_GCodeConversion_ZeroCenter_AsDefault.setText(QCoreApplication.translate("mainwindow", u"as Default", None))
        self.label_GCodeConversion_XOffset.setText(QCoreApplication.translate("mainwindow", u"X Offset", None))
        self.label_GCodeConversion_XOffset_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_YOffset.setText(QCoreApplication.translate("mainwindow", u"Y Offset", None))
        self.label_GCodeConversion_YOffset_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MinX.setText(QCoreApplication.translate("mainwindow", u"Min X", None))
        self.label_GCodeConversion_MinX_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MaxX.setText(QCoreApplication.translate("mainwindow", u"Max X", None))
        self.label_GCodeConversion_MaxX_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MinY.setText(QCoreApplication.translate("mainwindow", u"Min Y", None))
        self.label_GCodeConversion_MinY_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MaxY.setText(QCoreApplication.translate("mainwindow", u"Max Y", None))
        self.label_GCodeConversion_MaxY_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.labelGCodeGeneration.setText(QCoreApplication.translate("mainwindow", u" GCode Generation", None))
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setText(QCoreApplication.translate("mainwindow", u"Return to 0,0 at end", None))
        self.checkBox_GCodeGeneration_ReturnToZeroAtEnd.setText("")
        self.label_GCodeGenerationSpindleAutomatic.setText(QCoreApplication.translate("mainwindow", u"Spindle automatic", None))
        self.checkBox_GCodeGeneration_SpindleAutomatic.setText("")
        self.label_GCodeGenerationSpindleSpeed.setText(QCoreApplication.translate("mainwindow", u"Spindle speed", None))
        self.menuFile.setTitle(QCoreApplication.translate("mainwindow", u"File", None))
        self.menuJobs.setTitle(QCoreApplication.translate("mainwindow", u"Jobs", None))
    # retranslateUi

