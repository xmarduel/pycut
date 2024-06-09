# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
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
        self.actionNewProject = QAction(mainwindow)
        self.actionNewProject.setObjectName(u"actionNewProject")
        self.actionOpenProject = QAction(mainwindow)
        self.actionOpenProject.setObjectName(u"actionOpenProject")
        self.actionSaveProjectAs = QAction(mainwindow)
        self.actionSaveProjectAs.setObjectName(u"actionSaveProjectAs")
        self.actionSaveProject = QAction(mainwindow)
        self.actionSaveProject.setObjectName(u"actionSaveProject")
        self.actionTutorial = QAction(mainwindow)
        self.actionTutorial.setObjectName(u"actionTutorial")
        self.actionAboutQt = QAction(mainwindow)
        self.actionAboutQt.setObjectName(u"actionAboutQt")
        self.actionAboutPyCut = QAction(mainwindow)
        self.actionAboutPyCut.setObjectName(u"actionAboutPyCut")
        self.actionSettings = QAction(mainwindow)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionOpenGCode = QAction(mainwindow)
        self.actionOpenGCode.setObjectName(u"actionOpenGCode")
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
        self.verticalLayout_2.setSpacing(22)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, -1, 9, -1)
        self.verticalLayoutSettingsContent = QVBoxLayout()
        self.verticalLayoutSettingsContent.setSpacing(6)
        self.verticalLayoutSettingsContent.setObjectName(u"verticalLayoutSettingsContent")
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

        self.PxPerInch = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.PxPerInch.setObjectName(u"PxPerInch")
        self.PxPerInch.setEnabled(False)
        self.PxPerInch.setMaximum(999.990000000000009)
        self.PxPerInch.setValue(1.000000000000000)

        self.horizontalLayout.addWidget(self.PxPerInch)


        self.verticalLayoutSettingsContent.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(8, -1, -1, -1)
        self.label_SvgModelWidth = QLabel(self.scrollAreaWidgetContents)
        self.label_SvgModelWidth.setObjectName(u"label_SvgModelWidth")
        self.label_SvgModelWidth.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_SvgModelWidth)

        self.SvgModelWidth = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.SvgModelWidth.setObjectName(u"SvgModelWidth")
        self.SvgModelWidth.setEnabled(False)
        self.SvgModelWidth.setMaximum(999.990000000000009)

        self.horizontalLayout_4.addWidget(self.SvgModelWidth)


        self.verticalLayoutSettingsContent.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(8, -1, -1, -1)
        self.label_SvgModelHeight = QLabel(self.scrollAreaWidgetContents)
        self.label_SvgModelHeight.setObjectName(u"label_SvgModelHeight")
        self.label_SvgModelHeight.setFont(font1)

        self.horizontalLayout_3.addWidget(self.label_SvgModelHeight)

        self.SvgModelHeight = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.SvgModelHeight.setObjectName(u"SvgModelHeight")
        self.SvgModelHeight.setEnabled(False)
        self.SvgModelHeight.setMaximum(999.990000000000009)

        self.horizontalLayout_3.addWidget(self.SvgModelHeight)


        self.verticalLayoutSettingsContent.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addLayout(self.verticalLayoutSettingsContent)

        self.verticalLayoutToolContent = QVBoxLayout()
        self.verticalLayoutToolContent.setSpacing(6)
        self.verticalLayoutToolContent.setObjectName(u"verticalLayoutToolContent")
        self.label_Tool = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool.setObjectName(u"label_Tool")
        self.label_Tool.setFont(font)
        self.label_Tool.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayoutToolContent.addWidget(self.label_Tool)

        self.gridLayout_Tool = QGridLayout()
        self.gridLayout_Tool.setObjectName(u"gridLayout_Tool")
        self.gridLayout_Tool.setContentsMargins(8, -1, -1, -1)
        self.label_Tool_Diameter_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Diameter_UnitsDescr.setObjectName(u"label_Tool_Diameter_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Diameter_UnitsDescr, 1, 1, 1, 1)

        self.label_Tool_Cut_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Cut_UnitsDescr.setObjectName(u"label_Tool_Cut_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Cut_UnitsDescr, 7, 1, 1, 1)

        self.Tool_Plunge = QSpinBox(self.scrollAreaWidgetContents)
        self.Tool_Plunge.setObjectName(u"Tool_Plunge")
        self.Tool_Plunge.setMaximum(1000)
        self.Tool_Plunge.setValue(100)

        self.gridLayout_Tool.addWidget(self.Tool_Plunge, 6, 2, 1, 1)

        self.Tool_Cut = QSpinBox(self.scrollAreaWidgetContents)
        self.Tool_Cut.setObjectName(u"Tool_Cut")
        self.Tool_Cut.setMaximum(1000)
        self.Tool_Cut.setValue(200)

        self.gridLayout_Tool.addWidget(self.Tool_Cut, 7, 2, 1, 1)

        self.label_Tool_Cut = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Cut.setObjectName(u"label_Tool_Cut")
        self.label_Tool_Cut.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Cut, 7, 0, 1, 1)

        self.label_Tool_PassDepth_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_PassDepth_UnitsDescr.setObjectName(u"label_Tool_PassDepth_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_PassDepth_UnitsDescr, 3, 1, 1, 1)

        self.label_Tool_PassDepth = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_PassDepth.setObjectName(u"label_Tool_PassDepth")
        self.label_Tool_PassDepth.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_PassDepth, 3, 0, 1, 1)

        self.label_Tool_Angle = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Angle.setObjectName(u"label_Tool_Angle")
        self.label_Tool_Angle.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Angle, 2, 0, 1, 1)

        self.label_Tool_Diameter = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Diameter.setObjectName(u"label_Tool_Diameter")
        self.label_Tool_Diameter.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Diameter, 1, 0, 1, 1)

        self.label_Tool_Plunge = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Plunge.setObjectName(u"label_Tool_Plunge")
        self.label_Tool_Plunge.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Plunge, 6, 0, 1, 1)

        self.label_Tool_Angle_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Angle_UnitsDescr.setObjectName(u"label_Tool_Angle_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Angle_UnitsDescr, 2, 1, 1, 1)

        self.label_Tool_Plunge_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Plunge_UnitsDescr.setObjectName(u"label_Tool_Plunge_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Plunge_UnitsDescr, 6, 1, 1, 1)

        self.Tool_PassDepth = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.Tool_PassDepth.setObjectName(u"Tool_PassDepth")
        self.Tool_PassDepth.setDecimals(3)
        self.Tool_PassDepth.setMaximum(30.000000000000000)
        self.Tool_PassDepth.setSingleStep(0.500000000000000)
        self.Tool_PassDepth.setValue(0.200000000000000)

        self.gridLayout_Tool.addWidget(self.Tool_PassDepth, 3, 2, 1, 1)

        self.Tool_Rapid = QSpinBox(self.scrollAreaWidgetContents)
        self.Tool_Rapid.setObjectName(u"Tool_Rapid")
        self.Tool_Rapid.setMaximum(1000)
        self.Tool_Rapid.setValue(500)

        self.gridLayout_Tool.addWidget(self.Tool_Rapid, 5, 2, 1, 1)

        self.Tool_Overlap = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.Tool_Overlap.setObjectName(u"Tool_Overlap")
        self.Tool_Overlap.setDecimals(3)
        self.Tool_Overlap.setMaximum(1.000000000000000)
        self.Tool_Overlap.setSingleStep(0.010000000000000)
        self.Tool_Overlap.setValue(0.400000000000000)

        self.gridLayout_Tool.addWidget(self.Tool_Overlap, 4, 2, 1, 1)

        self.Tool_Units = QComboBox(self.scrollAreaWidgetContents)
        self.Tool_Units.addItem("")
        self.Tool_Units.addItem("")
        self.Tool_Units.setObjectName(u"Tool_Units")

        self.gridLayout_Tool.addWidget(self.Tool_Units, 0, 1, 1, 1)

        self.label_Tool_Units = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Units.setObjectName(u"label_Tool_Units")
        self.label_Tool_Units.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Units, 0, 0, 1, 1)

        self.label_Tool_Rapid_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Rapid_UnitsDescr.setObjectName(u"label_Tool_Rapid_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Rapid_UnitsDescr, 5, 1, 1, 1)

        self.label_Tool_Overlap_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Overlap_UnitsDescr.setObjectName(u"label_Tool_Overlap_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_Overlap_UnitsDescr, 4, 1, 1, 1)

        self.label_Tool_Rapid = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Rapid.setObjectName(u"label_Tool_Rapid")
        self.label_Tool_Rapid.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Rapid, 5, 0, 1, 1)

        self.Tool_Angle = QSpinBox(self.scrollAreaWidgetContents)
        self.Tool_Angle.setObjectName(u"Tool_Angle")
        self.Tool_Angle.setMaximum(180)
        self.Tool_Angle.setValue(180)

        self.gridLayout_Tool.addWidget(self.Tool_Angle, 2, 2, 1, 1)

        self.label_Tool_Overlap = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_Overlap.setObjectName(u"label_Tool_Overlap")
        self.label_Tool_Overlap.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_Overlap, 4, 0, 1, 1)

        self.Tool_Diameter = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.Tool_Diameter.setObjectName(u"Tool_Diameter")
        self.Tool_Diameter.setDecimals(3)
        self.Tool_Diameter.setMaximum(32.000000000000000)
        self.Tool_Diameter.setSingleStep(0.100000000000000)
        self.Tool_Diameter.setValue(1.000000000000000)

        self.gridLayout_Tool.addWidget(self.Tool_Diameter, 1, 2, 1, 1)

        self.label_Tool_HelixPitch = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_HelixPitch.setObjectName(u"label_Tool_HelixPitch")
        self.label_Tool_HelixPitch.setFont(font1)

        self.gridLayout_Tool.addWidget(self.label_Tool_HelixPitch, 8, 0, 1, 1)

        self.label_Tool_HelixPitch_UnitsDescr = QLabel(self.scrollAreaWidgetContents)
        self.label_Tool_HelixPitch_UnitsDescr.setObjectName(u"label_Tool_HelixPitch_UnitsDescr")

        self.gridLayout_Tool.addWidget(self.label_Tool_HelixPitch_UnitsDescr, 8, 1, 1, 1)

        self.Tool_HelixPitch = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.Tool_HelixPitch.setObjectName(u"Tool_HelixPitch")
        self.Tool_HelixPitch.setSingleStep(0.100000000000000)
        self.Tool_HelixPitch.setValue(1.000000000000000)

        self.gridLayout_Tool.addWidget(self.Tool_HelixPitch, 8, 2, 1, 1)


        self.verticalLayoutToolContent.addLayout(self.gridLayout_Tool)


        self.verticalLayout_2.addLayout(self.verticalLayoutToolContent)

        self.verticalLayoutCurveToLineConversion = QVBoxLayout()
        self.verticalLayoutCurveToLineConversion.setSpacing(6)
        self.verticalLayoutCurveToLineConversion.setObjectName(u"verticalLayoutCurveToLineConversion")
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
        self.label_CurveToLineConversion_MinimumNbSegments.setMinimumSize(QSize(189, 0))
        self.label_CurveToLineConversion_MinimumNbSegments.setFont(font1)

        self.formLayoutCurveToLineConversion.setWidget(0, QFormLayout.LabelRole, self.label_CurveToLineConversion_MinimumNbSegments)

        self.CurveToLineConversion_MinimumNbSegments = QSpinBox(self.scrollAreaWidgetContents)
        self.CurveToLineConversion_MinimumNbSegments.setObjectName(u"CurveToLineConversion_MinimumNbSegments")
        self.CurveToLineConversion_MinimumNbSegments.setEnabled(True)
        self.CurveToLineConversion_MinimumNbSegments.setMinimum(1)
        self.CurveToLineConversion_MinimumNbSegments.setValue(5)

        self.formLayoutCurveToLineConversion.setWidget(0, QFormLayout.FieldRole, self.CurveToLineConversion_MinimumNbSegments)

        self.label_CurveToLineConversion_MinimumSegmentsLength = QLabel(self.scrollAreaWidgetContents)
        self.label_CurveToLineConversion_MinimumSegmentsLength.setObjectName(u"label_CurveToLineConversion_MinimumSegmentsLength")
        self.label_CurveToLineConversion_MinimumSegmentsLength.setFont(font1)

        self.formLayoutCurveToLineConversion.setWidget(1, QFormLayout.LabelRole, self.label_CurveToLineConversion_MinimumSegmentsLength)

        self.CurveToLineConversion_MinimumSegmentsLength = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.CurveToLineConversion_MinimumSegmentsLength.setObjectName(u"CurveToLineConversion_MinimumSegmentsLength")
        self.CurveToLineConversion_MinimumSegmentsLength.setMaximum(1.000000000000000)
        self.CurveToLineConversion_MinimumSegmentsLength.setSingleStep(0.010000000000000)
        self.CurveToLineConversion_MinimumSegmentsLength.setValue(0.010000000000000)

        self.formLayoutCurveToLineConversion.setWidget(1, QFormLayout.FieldRole, self.CurveToLineConversion_MinimumSegmentsLength)


        self.verticalLayoutCurveToLineConversion.addLayout(self.formLayoutCurveToLineConversion)


        self.verticalLayout_2.addLayout(self.verticalLayoutCurveToLineConversion)

        self.verticalLayoutTabsContent = QVBoxLayout()
        self.verticalLayoutTabsContent.setSpacing(6)
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

        self.Tabs_Units = QComboBox(self.tabsGlobals)
        self.Tabs_Units.addItem("")
        self.Tabs_Units.addItem("")
        self.Tabs_Units.setObjectName(u"Tabs_Units")
        self.Tabs_Units.setEnabled(True)

        self.formLayout_Tabs.setWidget(0, QFormLayout.FieldRole, self.Tabs_Units)

        self.label_Tabs_Height = QLabel(self.tabsGlobals)
        self.label_Tabs_Height.setObjectName(u"label_Tabs_Height")
        self.label_Tabs_Height.setFont(font1)

        self.formLayout_Tabs.setWidget(1, QFormLayout.LabelRole, self.label_Tabs_Height)

        self.Tabs_Height = QDoubleSpinBox(self.tabsGlobals)
        self.Tabs_Height.setObjectName(u"Tabs_Height")
        self.Tabs_Height.setEnabled(True)
        self.Tabs_Height.setDecimals(3)

        self.formLayout_Tabs.setWidget(1, QFormLayout.FieldRole, self.Tabs_Height)

        self.label = QLabel(self.tabsGlobals)
        self.label.setObjectName(u"label")

        self.formLayout_Tabs.setWidget(2, QFormLayout.LabelRole, self.label)

        self.Tabs_hideAllTabs = QCheckBox(self.tabsGlobals)
        self.Tabs_hideAllTabs.setObjectName(u"Tabs_hideAllTabs")
        self.Tabs_hideAllTabs.setFont(font1)

        self.formLayout_Tabs.setWidget(2, QFormLayout.FieldRole, self.Tabs_hideAllTabs)

        self.Tabs_hideDisabledTabs = QCheckBox(self.tabsGlobals)
        self.Tabs_hideDisabledTabs.setObjectName(u"Tabs_hideDisabledTabs")
        self.Tabs_hideDisabledTabs.setFont(font1)

        self.formLayout_Tabs.setWidget(3, QFormLayout.FieldRole, self.Tabs_hideDisabledTabs)


        self.verticalLayout_4.addLayout(self.formLayout_Tabs)


        self.verticalLayoutTabsContent.addWidget(self.tabsGlobals)

        self.tabsview_manager = PyCutTabsTableViewManager(self.scrollAreaWidgetContents)
        self.tabsview_manager.setObjectName(u"tabsview_manager")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabsview_manager.sizePolicy().hasHeightForWidth())
        self.tabsview_manager.setSizePolicy(sizePolicy)
        self.tabsview_manager.setMinimumSize(QSize(0, 180))

        self.verticalLayoutTabsContent.addWidget(self.tabsview_manager)

        self.verticalLayoutTabsContent.setStretch(2, 1)

        self.verticalLayout_2.addLayout(self.verticalLayoutTabsContent)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.verticalLayout_2.setStretch(4, 1)
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
        self.simulator_webgl = QWidget()
        self.simulator_webgl.setObjectName(u"simulator_webgl")
        self.horizontalLayout_5 = QHBoxLayout(self.simulator_webgl)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.tabWidget.addTab(self.simulator_webgl, "")
        self.simulator_python = QWidget()
        self.simulator_python.setObjectName(u"simulator_python")
        self.horizontalLayout_5b = QHBoxLayout(self.simulator_python)
        self.horizontalLayout_5b.setObjectName(u"horizontalLayout_5b")
        self.tabWidget.addTab(self.simulator_python, "")
        self.splitter.addWidget(self.tabWidget)
        self.operationsview_manager = PyCutOperationsTableViewManager(self.splitter)
        self.operationsview_manager.setObjectName(u"operationsview_manager")
        self.operationsview_manager.setMinimumSize(QSize(0, 200))
        self.operationsview_manager.setMaximumSize(QSize(16777215, 400))
        self.splitter.addWidget(self.operationsview_manager)

        self.verticalLayout.addWidget(self.splitter)

        self.SaveGcode = QPushButton(self.centralArea)
        self.SaveGcode.setObjectName(u"SaveGcode")

        self.verticalLayout.addWidget(self.SaveGcode)


        self.horizontalLayout_2.addWidget(self.centralArea)

        self.scrollArea_right = QScrollArea(self.centralwidget)
        self.scrollArea_right.setObjectName(u"scrollArea_right")
        self.scrollArea_right.setMinimumSize(QSize(200, 0))
        self.scrollArea_right.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 300, 998))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_5.setSpacing(22)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayoutMaterial = QVBoxLayout()
        self.verticalLayoutMaterial.setSpacing(6)
        self.verticalLayoutMaterial.setObjectName(u"verticalLayoutMaterial")
        self.labelMaterial = QLabel(self.scrollAreaWidgetContents_2)
        self.labelMaterial.setObjectName(u"labelMaterial")
        self.labelMaterial.setFont(font)
        self.labelMaterial.setStyleSheet(u"background-color: rgb(200, 200, 200);")

        self.verticalLayoutMaterial.addWidget(self.labelMaterial)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.widget_display_material = QWidget(self.scrollAreaWidgetContents_2)
        self.widget_display_material.setObjectName(u"widget_display_material")
        self.widget_display_material.setMinimumSize(QSize(200, 150))
        self.widget_display_material.setMaximumSize(QSize(200, 150))

        self.horizontalLayout_6.addWidget(self.widget_display_material)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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

        self.Material_Units = QComboBox(self.scrollAreaWidgetContents_2)
        self.Material_Units.addItem("")
        self.Material_Units.addItem("")
        self.Material_Units.setObjectName(u"Material_Units")

        self.formLayout_Material.setWidget(0, QFormLayout.FieldRole, self.Material_Units)

        self.label_Material_Thickness = QLabel(self.scrollAreaWidgetContents_2)
        self.label_Material_Thickness.setObjectName(u"label_Material_Thickness")
        self.label_Material_Thickness.setFont(font1)

        self.formLayout_Material.setWidget(1, QFormLayout.LabelRole, self.label_Material_Thickness)

        self.Material_Thickness = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.Material_Thickness.setObjectName(u"Material_Thickness")
        self.Material_Thickness.setMaximum(100.000000000000000)
        self.Material_Thickness.setValue(50.000000000000000)

        self.formLayout_Material.setWidget(1, QFormLayout.FieldRole, self.Material_Thickness)

        self.label_Material_ZOrigin = QLabel(self.scrollAreaWidgetContents_2)
        self.label_Material_ZOrigin.setObjectName(u"label_Material_ZOrigin")
        self.label_Material_ZOrigin.setFont(font1)

        self.formLayout_Material.setWidget(2, QFormLayout.LabelRole, self.label_Material_ZOrigin)

        self.Material_ZOrigin = QComboBox(self.scrollAreaWidgetContents_2)
        self.Material_ZOrigin.addItem("")
        self.Material_ZOrigin.addItem("")
        self.Material_ZOrigin.setObjectName(u"Material_ZOrigin")
        sizePolicy.setHeightForWidth(self.Material_ZOrigin.sizePolicy().hasHeightForWidth())
        self.Material_ZOrigin.setSizePolicy(sizePolicy)

        self.formLayout_Material.setWidget(2, QFormLayout.FieldRole, self.Material_ZOrigin)

        self.label_Material_Clearance = QLabel(self.scrollAreaWidgetContents_2)
        self.label_Material_Clearance.setObjectName(u"label_Material_Clearance")
        self.label_Material_Clearance.setFont(font1)
        self.label_Material_Clearance.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.formLayout_Material.setWidget(3, QFormLayout.LabelRole, self.label_Material_Clearance)

        self.Material_Clearance = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.Material_Clearance.setObjectName(u"Material_Clearance")
        self.Material_Clearance.setMaximum(100.000000000000000)
        self.Material_Clearance.setValue(20.000000000000000)

        self.formLayout_Material.setWidget(3, QFormLayout.FieldRole, self.Material_Clearance)


        self.verticalLayoutMaterial.addLayout(self.formLayout_Material)


        self.verticalLayout_5.addLayout(self.verticalLayoutMaterial)

        self.verticalLayoutGCodeConversion = QVBoxLayout()
        self.verticalLayoutGCodeConversion.setSpacing(3)
        self.verticalLayoutGCodeConversion.setObjectName(u"verticalLayoutGCodeConversion")
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

        self.GCodeConversion_MinY = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_MinY.setObjectName(u"GCodeConversion_MinY")
        self.GCodeConversion_MinY.setEnabled(False)
        self.GCodeConversion_MinY.setMinimum(-1000.000000000000000)
        self.GCodeConversion_MinY.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_MinY, 10, 2, 1, 1)

        self.label_GCodeConversion_GCodeUnits = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_GCodeUnits.setObjectName(u"label_GCodeConversion_GCodeUnits")
        self.label_GCodeConversion_GCodeUnits.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_GCodeUnits, 0, 0, 1, 1)

        self.GCodeConversion_MaxX = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_MaxX.setObjectName(u"GCodeConversion_MaxX")
        self.GCodeConversion_MaxX.setEnabled(False)
        self.GCodeConversion_MaxX.setMinimum(-1000.000000000000000)
        self.GCodeConversion_MaxX.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_MaxX, 9, 2, 1, 1)

        self.label_GCodeConversion_MaxY = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MaxY.setObjectName(u"label_GCodeConversion_MaxY")
        self.label_GCodeConversion_MaxY.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MaxY, 11, 0, 1, 1)

        self.label_GCodeConversion_MinX_UnitsDescr = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MinX_UnitsDescr.setObjectName(u"label_GCodeConversion_MinX_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinX_UnitsDescr, 8, 1, 1, 1)

        self.GCodeConversion_FlipXY = QCheckBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_FlipXY.setObjectName(u"GCodeConversion_FlipXY")
        self.GCodeConversion_FlipXY.setEnabled(True)
        font2 = QFont()
        font2.setBold(True)
        font2.setKerning(False)
        self.GCodeConversion_FlipXY.setFont(font2)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_FlipXY, 5, 0, 1, 2)

        self.GCodeConversion_MinX = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_MinX.setObjectName(u"GCodeConversion_MinX")
        self.GCodeConversion_MinX.setEnabled(False)
        self.GCodeConversion_MinX.setMinimum(-1000.000000000000000)
        self.GCodeConversion_MinX.setMaximum(1000.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_MinX, 8, 2, 1, 1)

        self.GCodeConversion_MaxY = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_MaxY.setObjectName(u"GCodeConversion_MaxY")
        self.GCodeConversion_MaxY.setEnabled(False)
        self.GCodeConversion_MaxY.setMinimum(-1000.000000000000000)
        self.GCodeConversion_MaxY.setMaximum(1000.000000000000000)
        self.GCodeConversion_MaxY.setValue(0.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_MaxY, 11, 2, 1, 1)

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

        self.GCodeConversion_YOffset = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_YOffset.setObjectName(u"GCodeConversion_YOffset")
        self.GCodeConversion_YOffset.setKeyboardTracking(False)
        self.GCodeConversion_YOffset.setMinimum(-200.000000000000000)
        self.GCodeConversion_YOffset.setMaximum(200.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_YOffset, 7, 2, 1, 1)

        self.label_GCodeConversion_MinY_UnitsDescr = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MinY_UnitsDescr.setObjectName(u"label_GCodeConversion_MinY_UnitsDescr")

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinY_UnitsDescr, 10, 1, 1, 1)

        self.GCodeConversion_XOffset = QDoubleSpinBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_XOffset.setObjectName(u"GCodeConversion_XOffset")
        self.GCodeConversion_XOffset.setKeyboardTracking(False)
        self.GCodeConversion_XOffset.setDecimals(1)
        self.GCodeConversion_XOffset.setMinimum(-200.000000000000000)
        self.GCodeConversion_XOffset.setMaximum(200.000000000000000)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_XOffset, 6, 2, 1, 1)

        self.label_GCodeConversion_MinY = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_MinY.setObjectName(u"label_GCodeConversion_MinY")
        self.label_GCodeConversion_MinY.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_MinY, 10, 0, 1, 1)

        self.label_GCodeConversion_XOffset = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeConversion_XOffset.setObjectName(u"label_GCodeConversion_XOffset")
        self.label_GCodeConversion_XOffset.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.label_GCodeConversion_XOffset, 6, 0, 1, 1)

        self.GCodeConversion_Units = QComboBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_Units.addItem("")
        self.GCodeConversion_Units.addItem("")
        self.GCodeConversion_Units.setObjectName(u"GCodeConversion_Units")

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_Units, 0, 1, 1, 1)

        self.GCodeConversion_ZeroTopLeftOfMaterial = QPushButton(self.scrollAreaWidgetContents_2)
        self.buttonGroup_GCodeConversion = QButtonGroup(mainwindow)
        self.buttonGroup_GCodeConversion.setObjectName(u"buttonGroup_GCodeConversion")
        self.buttonGroup_GCodeConversion.addButton(self.GCodeConversion_ZeroTopLeftOfMaterial)
        self.GCodeConversion_ZeroTopLeftOfMaterial.setObjectName(u"GCodeConversion_ZeroTopLeftOfMaterial")
        self.GCodeConversion_ZeroTopLeftOfMaterial.setFont(font1)
        icon = QIcon()
        iconThemeName = u":/images/tango/22x22/actions/view-refresh.png"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.GCodeConversion_ZeroTopLeftOfMaterial.setIcon(icon)
        self.GCodeConversion_ZeroTopLeftOfMaterial.setCheckable(True)
        self.GCodeConversion_ZeroTopLeftOfMaterial.setChecked(True)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_ZeroTopLeftOfMaterial, 1, 0, 1, 3)

        self.GCodeConversion_ZeroLowerLeftOfMaterial = QPushButton(self.scrollAreaWidgetContents_2)
        self.buttonGroup_GCodeConversion.addButton(self.GCodeConversion_ZeroLowerLeftOfMaterial)
        self.GCodeConversion_ZeroLowerLeftOfMaterial.setObjectName(u"GCodeConversion_ZeroLowerLeftOfMaterial")
        self.GCodeConversion_ZeroLowerLeftOfMaterial.setFont(font1)
        self.GCodeConversion_ZeroLowerLeftOfMaterial.setIcon(icon)
        self.GCodeConversion_ZeroLowerLeftOfMaterial.setCheckable(True)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_ZeroLowerLeftOfMaterial, 2, 0, 1, 3)

        self.GCodeConversion_ZeroLowerLeftOfOp = QPushButton(self.scrollAreaWidgetContents_2)
        self.buttonGroup_GCodeConversion.addButton(self.GCodeConversion_ZeroLowerLeftOfOp)
        self.GCodeConversion_ZeroLowerLeftOfOp.setObjectName(u"GCodeConversion_ZeroLowerLeftOfOp")
        self.GCodeConversion_ZeroLowerLeftOfOp.setFont(font1)
        self.GCodeConversion_ZeroLowerLeftOfOp.setIcon(icon)
        self.GCodeConversion_ZeroLowerLeftOfOp.setCheckable(True)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_ZeroLowerLeftOfOp, 3, 0, 1, 3)

        self.GCodeConversion_ZeroCenterOfOp = QPushButton(self.scrollAreaWidgetContents_2)
        self.buttonGroup_GCodeConversion.addButton(self.GCodeConversion_ZeroCenterOfOp)
        self.GCodeConversion_ZeroCenterOfOp.setObjectName(u"GCodeConversion_ZeroCenterOfOp")
        self.GCodeConversion_ZeroCenterOfOp.setFont(font1)
        self.GCodeConversion_ZeroCenterOfOp.setIcon(icon)
        self.GCodeConversion_ZeroCenterOfOp.setCheckable(True)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_ZeroCenterOfOp, 4, 0, 1, 3)

        self.GCodeConversion_UseOffset = QCheckBox(self.scrollAreaWidgetContents_2)
        self.GCodeConversion_UseOffset.setObjectName(u"GCodeConversion_UseOffset")
        self.GCodeConversion_UseOffset.setFont(font1)

        self.gridLayout_GCodeConversion.addWidget(self.GCodeConversion_UseOffset, 5, 2, 1, 1)


        self.verticalLayoutGCodeConversion.addLayout(self.gridLayout_GCodeConversion)


        self.verticalLayout_5.addLayout(self.verticalLayoutGCodeConversion)

        self.verticalLayoutGCodeGeneration = QVBoxLayout()
        self.verticalLayoutGCodeGeneration.setSpacing(6)
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

        self.GCodeGeneration_ReturnToZeroAtEnd = QCheckBox(self.scrollAreaWidgetContents_2)
        self.GCodeGeneration_ReturnToZeroAtEnd.setObjectName(u"GCodeGeneration_ReturnToZeroAtEnd")

        self.formLayout_GCodeGeneration.setWidget(0, QFormLayout.FieldRole, self.GCodeGeneration_ReturnToZeroAtEnd)

        self.label_GCodeGeneration_SpindleControl = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeGeneration_SpindleControl.setObjectName(u"label_GCodeGeneration_SpindleControl")
        self.label_GCodeGeneration_SpindleControl.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(1, QFormLayout.LabelRole, self.label_GCodeGeneration_SpindleControl)

        self.GCodeGeneration_SpindleControl = QCheckBox(self.scrollAreaWidgetContents_2)
        self.GCodeGeneration_SpindleControl.setObjectName(u"GCodeGeneration_SpindleControl")
        self.GCodeGeneration_SpindleControl.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(1, QFormLayout.FieldRole, self.GCodeGeneration_SpindleControl)

        self.label_GCodeGeneration_SpindleSpeed = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeGeneration_SpindleSpeed.setObjectName(u"label_GCodeGeneration_SpindleSpeed")
        self.label_GCodeGeneration_SpindleSpeed.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(2, QFormLayout.LabelRole, self.label_GCodeGeneration_SpindleSpeed)

        self.GCodeGeneration_SpindleSpeed = QSpinBox(self.scrollAreaWidgetContents_2)
        self.GCodeGeneration_SpindleSpeed.setObjectName(u"GCodeGeneration_SpindleSpeed")
        self.GCodeGeneration_SpindleSpeed.setMaximum(25000)
        self.GCodeGeneration_SpindleSpeed.setSingleStep(50)

        self.formLayout_GCodeGeneration.setWidget(2, QFormLayout.FieldRole, self.GCodeGeneration_SpindleSpeed)

        self.label_GCodeGeneration_ProgramEnd = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeGeneration_ProgramEnd.setObjectName(u"label_GCodeGeneration_ProgramEnd")
        self.label_GCodeGeneration_ProgramEnd.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(3, QFormLayout.LabelRole, self.label_GCodeGeneration_ProgramEnd)

        self.GCodeGeneration_ProgramEnd = QCheckBox(self.scrollAreaWidgetContents_2)
        self.GCodeGeneration_ProgramEnd.setObjectName(u"GCodeGeneration_ProgramEnd")
        self.GCodeGeneration_ProgramEnd.setFont(font1)

        self.formLayout_GCodeGeneration.setWidget(3, QFormLayout.FieldRole, self.GCodeGeneration_ProgramEnd)


        self.verticalLayoutGCodeGeneration.addLayout(self.formLayout_GCodeGeneration)


        self.verticalLayout_5.addLayout(self.verticalLayoutGCodeGeneration)

        self.verticalLayoutGCodeStatistics = QVBoxLayout()
        self.verticalLayoutGCodeStatistics.setSpacing(6)
        self.verticalLayoutGCodeStatistics.setObjectName(u"verticalLayoutGCodeStatistics")
        self.labelGCodeStatistics = QLabel(self.scrollAreaWidgetContents_2)
        self.labelGCodeStatistics.setObjectName(u"labelGCodeStatistics")
        self.labelGCodeStatistics.setFont(font)
        self.labelGCodeStatistics.setStyleSheet(u"background-color: rgb(188, 188, 188);")

        self.verticalLayoutGCodeStatistics.addWidget(self.labelGCodeStatistics)

        self.formLayout_GCodeStatistics = QFormLayout()
        self.formLayout_GCodeStatistics.setObjectName(u"formLayout_GCodeStatistics")
        self.formLayout_GCodeStatistics.setFormAlignment(Qt.AlignCenter)
        self.label_GCodeStatistics_RunTime = QLabel(self.scrollAreaWidgetContents_2)
        self.label_GCodeStatistics_RunTime.setObjectName(u"label_GCodeStatistics_RunTime")
        self.label_GCodeStatistics_RunTime.setMinimumSize(QSize(120, 0))
        self.label_GCodeStatistics_RunTime.setFont(font1)
        self.label_GCodeStatistics_RunTime.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.formLayout_GCodeStatistics.setWidget(0, QFormLayout.LabelRole, self.label_GCodeStatistics_RunTime)

        self.GCodeStatistics_RunTime = QLabel(self.scrollAreaWidgetContents_2)
        self.GCodeStatistics_RunTime.setObjectName(u"GCodeStatistics_RunTime")

        self.formLayout_GCodeStatistics.setWidget(0, QFormLayout.FieldRole, self.GCodeStatistics_RunTime)


        self.verticalLayoutGCodeStatistics.addLayout(self.formLayout_GCodeStatistics)


        self.verticalLayout_5.addLayout(self.verticalLayoutGCodeStatistics)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)

        self.verticalLayout_5.setStretch(4, 1)
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
        self.menuSvg = QMenu(self.menubar)
        self.menuSvg.setObjectName(u"menuSvg")
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOpen_Recent_Jobs = QMenu(self.menuFile)
        self.menuOpen_Recent_Jobs.setObjectName(u"menuOpen_Recent_Jobs")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuGCode = QMenu(self.menubar)
        self.menuGCode.setObjectName(u"menuGCode")
        mainwindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSvg.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuGCode.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuSvg.addAction(self.actionOpenSvg)
        self.menuSvg.addSeparator()
        self.menuFile.addAction(self.actionNewProject)
        self.menuFile.addAction(self.menuOpen_Recent_Jobs.menuAction())
        self.menuFile.addAction(self.actionOpenProject)
        self.menuFile.addAction(self.actionSaveProjectAs)
        self.menuFile.addAction(self.actionSaveProject)
        self.menuHelp.addAction(self.actionTutorial)
        self.menuHelp.addAction(self.actionAboutQt)
        self.menuHelp.addAction(self.actionAboutPyCut)
        self.menuSettings.addAction(self.actionSettings)
        self.menuGCode.addAction(self.actionOpenGCode)

        self.retranslateUi(mainwindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(mainwindow)
    # setupUi

    def retranslateUi(self, mainwindow):
        mainwindow.setWindowTitle(QCoreApplication.translate("mainwindow", u"main", None))
        self.actionOpenSvg.setText(QCoreApplication.translate("mainwindow", u"Load SVG", None))
        self.actionNewProject.setText(QCoreApplication.translate("mainwindow", u"New Project", None))
#if QT_CONFIG(tooltip)
        self.actionNewProject.setToolTip(QCoreApplication.translate("mainwindow", u"New Project", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenProject.setText(QCoreApplication.translate("mainwindow", u"Open Project...", None))
#if QT_CONFIG(tooltip)
        self.actionOpenProject.setToolTip(QCoreApplication.translate("mainwindow", u"Open Project", None))
#endif // QT_CONFIG(tooltip)
        self.actionSaveProjectAs.setText(QCoreApplication.translate("mainwindow", u"Save Project As...", None))
#if QT_CONFIG(tooltip)
        self.actionSaveProjectAs.setToolTip(QCoreApplication.translate("mainwindow", u"Save Project As", None))
#endif // QT_CONFIG(tooltip)
        self.actionSaveProject.setText(QCoreApplication.translate("mainwindow", u"Save Project", None))
#if QT_CONFIG(tooltip)
        self.actionSaveProject.setToolTip(QCoreApplication.translate("mainwindow", u"Save Project", None))
#endif // QT_CONFIG(tooltip)
        self.actionTutorial.setText(QCoreApplication.translate("mainwindow", u"Tutorial", None))
        self.actionAboutQt.setText(QCoreApplication.translate("mainwindow", u"About &Qt", None))
        self.actionAboutPyCut.setText(QCoreApplication.translate("mainwindow", u"About PyCut", None))
        self.actionSettings.setText(QCoreApplication.translate("mainwindow", u"Viewers Settings...", None))
        self.actionOpenGCode.setText(QCoreApplication.translate("mainwindow", u"Load GCode", None))
        self.label_SvgSettings.setText(QCoreApplication.translate("mainwindow", u" Svg Settings", None))
        self.label_PxPerInch.setText(QCoreApplication.translate("mainwindow", u"user units scale factor", None))
        self.label_SvgModelWidth.setText(QCoreApplication.translate("mainwindow", u"width", None))
        self.SvgModelWidth.setSuffix(QCoreApplication.translate("mainwindow", u"mm", None))
        self.label_SvgModelHeight.setText(QCoreApplication.translate("mainwindow", u"height", None))
        self.SvgModelHeight.setSuffix(QCoreApplication.translate("mainwindow", u"mm", None))
        self.label_Tool.setText(QCoreApplication.translate("mainwindow", u" Tool (shared for all operations)", None))
        self.label_Tool_Diameter_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Cut_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
#if QT_CONFIG(tooltip)
        self.Tool_Plunge.setToolTip(QCoreApplication.translate("mainwindow", u"The speed the tool plunges downwards into the material", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.Tool_Cut.setToolTip(QCoreApplication.translate("mainwindow", u"The speed the tool moves horizontally during cutting", None))
#endif // QT_CONFIG(tooltip)
        self.label_Tool_Cut.setText(QCoreApplication.translate("mainwindow", u"Cut", None))
        self.label_Tool_PassDepth_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_PassDepth.setText(QCoreApplication.translate("mainwindow", u"Pass Depth", None))
        self.label_Tool_Angle.setText(QCoreApplication.translate("mainwindow", u"Cutter Angle", None))
        self.label_Tool_Diameter.setText(QCoreApplication.translate("mainwindow", u"Cutter Diameter", None))
        self.label_Tool_Plunge.setText(QCoreApplication.translate("mainwindow", u"Plunge", None))
        self.label_Tool_Angle_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Plunge_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
#if QT_CONFIG(tooltip)
        self.Tool_Rapid.setToolTip(QCoreApplication.translate("mainwindow", u"The speed the tool moves while not cutting", None))
#endif // QT_CONFIG(tooltip)
        self.Tool_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.Tool_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.label_Tool_Units.setText(QCoreApplication.translate("mainwindow", u"Units", None))
        self.label_Tool_Rapid_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Overlap_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_Tool_Rapid.setText(QCoreApplication.translate("mainwindow", u"Rapid", None))
        self.label_Tool_Overlap.setText(QCoreApplication.translate("mainwindow", u"Overlap", None))
        self.label_Tool_HelixPitch.setText(QCoreApplication.translate("mainwindow", u"Helix Pitch ", None))
        self.label_Tool_HelixPitch_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.labelCurveToLineConversion.setText(QCoreApplication.translate("mainwindow", u" Curve To Line Conversion", None))
        self.label_CurveToLineConversion_MinimumNbSegments.setText(QCoreApplication.translate("mainwindow", u"Minimum Segments", None))
        self.label_CurveToLineConversion_MinimumSegmentsLength.setText(QCoreApplication.translate("mainwindow", u"Minimum Segments Length", None))
        self.label_Tabs.setText(QCoreApplication.translate("mainwindow", u" Tabs", None))
        self.label_TabsUnits.setText(QCoreApplication.translate("mainwindow", u"Units", None))
        self.Tabs_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.Tabs_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.label_Tabs_Height.setText(QCoreApplication.translate("mainwindow", u"Height", None))
        self.label.setText("")
        self.Tabs_hideAllTabs.setText(QCoreApplication.translate("mainwindow", u"Hide all Tabs", None))
        self.Tabs_hideDisabledTabs.setText(QCoreApplication.translate("mainwindow", u"Hide disabled Tabs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.svg), QCoreApplication.translate("mainwindow", u"SVG", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.viewer), QCoreApplication.translate("mainwindow", u"GCode Viewer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.simulator_webgl), QCoreApplication.translate("mainwindow", u"GCode Simulator", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.simulator_python), QCoreApplication.translate("mainwindow", u"GCode Simulator", None))
        self.SaveGcode.setText(QCoreApplication.translate("mainwindow", u"Save Gcode", None))
        self.labelMaterial.setText(QCoreApplication.translate("mainwindow", u" Material", None))
        self.label_Material_Units.setText(QCoreApplication.translate("mainwindow", u"Units", None))
        self.Material_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.Material_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.label_Material_Thickness.setText(QCoreApplication.translate("mainwindow", u"Thickness", None))
        self.label_Material_ZOrigin.setText(QCoreApplication.translate("mainwindow", u"Z Origin", None))
        self.Material_ZOrigin.setItemText(0, QCoreApplication.translate("mainwindow", u"Top", None))
        self.Material_ZOrigin.setItemText(1, QCoreApplication.translate("mainwindow", u"Bottom", None))

        self.label_Material_Clearance.setText(QCoreApplication.translate("mainwindow", u"Cleareance                                     ", None))
        self.label_GCcodeConversion.setText(QCoreApplication.translate("mainwindow", u" GCode Conversion", None))
        self.label_GCodeConversion_YOffset_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_YOffset.setText(QCoreApplication.translate("mainwindow", u"Y Offset", None))
        self.label_GCodeConversion_GCodeUnits.setText(QCoreApplication.translate("mainwindow", u"Gcode Units", None))
        self.label_GCodeConversion_MaxY.setText(QCoreApplication.translate("mainwindow", u"Max Y", None))
        self.label_GCodeConversion_MinX_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.GCodeConversion_FlipXY.setText(QCoreApplication.translate("mainwindow", u"Flip X/Y", None))
        self.label_GCodeConversion_MinX.setText(QCoreApplication.translate("mainwindow", u"Min X", None))
        self.label_GCodeConversion_MaxX.setText(QCoreApplication.translate("mainwindow", u"Max X", None))
        self.label_GCodeConversion_XOffset_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MaxY_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MaxX_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MinY_UnitsDescr.setText(QCoreApplication.translate("mainwindow", u"__units__", None))
        self.label_GCodeConversion_MinY.setText(QCoreApplication.translate("mainwindow", u"Min Y", None))
        self.label_GCodeConversion_XOffset.setText(QCoreApplication.translate("mainwindow", u"X Offset", None))
        self.GCodeConversion_Units.setItemText(0, QCoreApplication.translate("mainwindow", u"inch", None))
        self.GCodeConversion_Units.setItemText(1, QCoreApplication.translate("mainwindow", u"mm", None))

        self.GCodeConversion_ZeroTopLeftOfMaterial.setText(QCoreApplication.translate("mainwindow", u"Zero top left Material       ", None))
        self.GCodeConversion_ZeroLowerLeftOfMaterial.setText(QCoreApplication.translate("mainwindow", u"Zero lower left (Material)", None))
        self.GCodeConversion_ZeroLowerLeftOfOp.setText(QCoreApplication.translate("mainwindow", u"Zero lower left (Op)         ", None))
        self.GCodeConversion_ZeroCenterOfOp.setText(QCoreApplication.translate("mainwindow", u"Zero center (Op)               ", None))
        self.GCodeConversion_UseOffset.setText(QCoreApplication.translate("mainwindow", u"Use Offset", None))
        self.labelGCodeGeneration.setText(QCoreApplication.translate("mainwindow", u" GCode Generation", None))
        self.label_GCodeGeneration_ReturnToZeroAtEnd.setText(QCoreApplication.translate("mainwindow", u"Return to 0,0 at end", None))
        self.GCodeGeneration_ReturnToZeroAtEnd.setText("")
        self.label_GCodeGeneration_SpindleControl.setText(QCoreApplication.translate("mainwindow", u"Spindle automatic", None))
        self.GCodeGeneration_SpindleControl.setText(QCoreApplication.translate("mainwindow", u"[M3/M5]", None))
        self.label_GCodeGeneration_SpindleSpeed.setText(QCoreApplication.translate("mainwindow", u"Spindle speed", None))
        self.label_GCodeGeneration_ProgramEnd.setText(QCoreApplication.translate("mainwindow", u"Program End", None))
        self.GCodeGeneration_ProgramEnd.setText(QCoreApplication.translate("mainwindow", u"[M2]", None))
        self.labelGCodeStatistics.setText(QCoreApplication.translate("mainwindow", u" GCode Statistics", None))
        self.label_GCodeStatistics_RunTime.setText(QCoreApplication.translate("mainwindow", u"Run Time", None))
        self.GCodeStatistics_RunTime.setText("")
        self.menuSvg.setTitle(QCoreApplication.translate("mainwindow", u"SVG", None))
        self.menuFile.setTitle(QCoreApplication.translate("mainwindow", u"File", None))
        self.menuOpen_Recent_Jobs.setTitle(QCoreApplication.translate("mainwindow", u"Open Recent Jobs", None))
        self.menuHelp.setTitle(QCoreApplication.translate("mainwindow", u"Help", None))
        self.menuSettings.setTitle(QCoreApplication.translate("mainwindow", u"Settings", None))
        self.menuGCode.setTitle(QCoreApplication.translate("mainwindow", u"GCode", None))
    # retranslateUi

