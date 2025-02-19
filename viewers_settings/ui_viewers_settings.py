# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'viewers_settings.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QGridLayout,
    QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)

from colorpicker import ColorPicker

class Ui_ViewersSettingsDialog(object):
    def setupUi(self, ViewersSettingsDialog):
        if not ViewersSettingsDialog.objectName():
            ViewersSettingsDialog.setObjectName(u"ViewersSettingsDialog")
        ViewersSettingsDialog.resize(406, 517)
        ViewersSettingsDialog.setStyleSheet(u"/*QWidget {\n"
"	font-size: 9pt;\n"
"}*/\n"
"\n"
"QSpinBox, QDoubleSpinBox {\n"
"	padding-top: 1px;\n"
"	padding-bottom: 1px;\n"
"}\n"
"\n"
"QGroupBox {\n"
"	border: none;\n"
"	padding-top: 16;\n"
"	font-weight: bold;\n"
"}")
        ViewersSettingsDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(ViewersSettingsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(ViewersSettingsDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        font = QFont()
        font.setBold(True)
        self.tabWidget.setFont(font)
        self.TabSvgViewer = QWidget()
        self.TabSvgViewer.setObjectName(u"TabSvgViewer")
        self.verticalLayout_2 = QVBoxLayout(self.TabSvgViewer)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_Tabs = QHBoxLayout()
        self.horizontalLayout_Tabs.setObjectName(u"horizontalLayout_Tabs")
        self.Tabs = QLabel(self.TabSvgViewer)
        self.Tabs.setObjectName(u"Tabs")
        self.Tabs.setFont(font)

        self.horizontalLayout_Tabs.addWidget(self.Tabs)


        self.verticalLayout_2.addLayout(self.horizontalLayout_Tabs)

        self.gridLayout_Tabs = QGridLayout()
        self.gridLayout_Tabs.setObjectName(u"gridLayout_Tabs")
        self.gridLayout_Tabs.setContentsMargins(20, -1, -1, -1)
        self.label_Tabs_fill = QLabel(self.TabSvgViewer)
        self.label_Tabs_fill.setObjectName(u"label_Tabs_fill")
        self.label_Tabs_fill.setMinimumSize(QSize(150, 0))

        self.gridLayout_Tabs.addWidget(self.label_Tabs_fill, 0, 0, 1, 1)

        self.colorpicker_Tabs_fill = ColorPicker(self.TabSvgViewer)
        self.colorpicker_Tabs_fill.setObjectName(u"colorpicker_Tabs_fill")

        self.gridLayout_Tabs.addWidget(self.colorpicker_Tabs_fill, 0, 1, 1, 1)

        self.label_Tabs_fill_opacity = QLabel(self.TabSvgViewer)
        self.label_Tabs_fill_opacity.setObjectName(u"label_Tabs_fill_opacity")

        self.gridLayout_Tabs.addWidget(self.label_Tabs_fill_opacity, 1, 0, 1, 1)

        self.Tabs_fill_opacity = QDoubleSpinBox(self.TabSvgViewer)
        self.Tabs_fill_opacity.setObjectName(u"Tabs_fill_opacity")
        self.Tabs_fill_opacity.setMaximum(1.000000000000000)
        self.Tabs_fill_opacity.setSingleStep(0.100000000000000)

        self.gridLayout_Tabs.addWidget(self.Tabs_fill_opacity, 1, 1, 1, 1)

        self.label_Tabs_fill_opacity_disabled = QLabel(self.TabSvgViewer)
        self.label_Tabs_fill_opacity_disabled.setObjectName(u"label_Tabs_fill_opacity_disabled")

        self.gridLayout_Tabs.addWidget(self.label_Tabs_fill_opacity_disabled, 2, 0, 1, 1)

        self.Tabs_fill_opacity_disabled = QDoubleSpinBox(self.TabSvgViewer)
        self.Tabs_fill_opacity_disabled.setObjectName(u"Tabs_fill_opacity_disabled")
        self.Tabs_fill_opacity_disabled.setMaximum(1.000000000000000)
        self.Tabs_fill_opacity_disabled.setSingleStep(0.100000000000000)

        self.gridLayout_Tabs.addWidget(self.Tabs_fill_opacity_disabled, 2, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_Tabs)

        self.horizontalLayout_Toolpaths = QHBoxLayout()
        self.horizontalLayout_Toolpaths.setObjectName(u"horizontalLayout_Toolpaths")
        self.Toolpaths = QLabel(self.TabSvgViewer)
        self.Toolpaths.setObjectName(u"Toolpaths")
        self.Toolpaths.setFont(font)

        self.horizontalLayout_Toolpaths.addWidget(self.Toolpaths)


        self.verticalLayout_2.addLayout(self.horizontalLayout_Toolpaths)

        self.gridLayout_Toolpath = QGridLayout()
        self.gridLayout_Toolpath.setObjectName(u"gridLayout_Toolpath")
        self.gridLayout_Toolpath.setContentsMargins(20, -1, -1, -1)
        self.colorpicker_Toolpath_stroke = ColorPicker(self.TabSvgViewer)
        self.colorpicker_Toolpath_stroke.setObjectName(u"colorpicker_Toolpath_stroke")

        self.gridLayout_Toolpath.addWidget(self.colorpicker_Toolpath_stroke, 1, 1, 1, 1)

        self.label_fill_opacity = QLabel(self.TabSvgViewer)
        self.label_fill_opacity.setObjectName(u"label_fill_opacity")

        self.gridLayout_Toolpath.addWidget(self.label_fill_opacity, 2, 0, 1, 1)

        self.label_fill = QLabel(self.TabSvgViewer)
        self.label_fill.setObjectName(u"label_fill")
        self.label_fill.setMinimumSize(QSize(150, 0))

        self.gridLayout_Toolpath.addWidget(self.label_fill, 1, 0, 1, 1)

        self.Toolpath_stroke_width = QDoubleSpinBox(self.TabSvgViewer)
        self.Toolpath_stroke_width.setObjectName(u"Toolpath_stroke_width")

        self.gridLayout_Toolpath.addWidget(self.Toolpath_stroke_width, 2, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_Toolpath)

        self.horizontalLayout_GeometryPreview = QHBoxLayout()
        self.horizontalLayout_GeometryPreview.setObjectName(u"horizontalLayout_GeometryPreview")
        self.GeometryPreview = QLabel(self.TabSvgViewer)
        self.GeometryPreview.setObjectName(u"GeometryPreview")
        self.GeometryPreview.setFont(font)

        self.horizontalLayout_GeometryPreview.addWidget(self.GeometryPreview)


        self.verticalLayout_2.addLayout(self.horizontalLayout_GeometryPreview)

        self.gridLayout_GeometryPreview = QGridLayout()
        self.gridLayout_GeometryPreview.setObjectName(u"gridLayout_GeometryPreview")
        self.gridLayout_GeometryPreview.setContentsMargins(20, -1, -1, -1)
        self.GeometryPreview_stroke_opacity = QDoubleSpinBox(self.TabSvgViewer)
        self.GeometryPreview_stroke_opacity.setObjectName(u"GeometryPreview_stroke_opacity")
        self.GeometryPreview_stroke_opacity.setDecimals(2)
        self.GeometryPreview_stroke_opacity.setMaximum(1.000000000000000)
        self.GeometryPreview_stroke_opacity.setSingleStep(0.100000000000000)

        self.gridLayout_GeometryPreview.addWidget(self.GeometryPreview_stroke_opacity, 5, 1, 1, 1)

        self.GeometryPreview_fill_opacity = QDoubleSpinBox(self.TabSvgViewer)
        self.GeometryPreview_fill_opacity.setObjectName(u"GeometryPreview_fill_opacity")
        self.GeometryPreview_fill_opacity.setDecimals(2)
        self.GeometryPreview_fill_opacity.setMaximum(1.000000000000000)
        self.GeometryPreview_fill_opacity.setSingleStep(0.100000000000000)

        self.gridLayout_GeometryPreview.addWidget(self.GeometryPreview_fill_opacity, 2, 1, 1, 1)

        self.colorpicker_GeometryPreview_fill = ColorPicker(self.TabSvgViewer)
        self.colorpicker_GeometryPreview_fill.setObjectName(u"colorpicker_GeometryPreview_fill")

        self.gridLayout_GeometryPreview.addWidget(self.colorpicker_GeometryPreview_fill, 1, 1, 1, 1)

        self.label = QLabel(self.TabSvgViewer)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.gridLayout_GeometryPreview.addWidget(self.label, 0, 0, 1, 1)

        self.label_GeometryPreview_stroke = QLabel(self.TabSvgViewer)
        self.label_GeometryPreview_stroke.setObjectName(u"label_GeometryPreview_stroke")
        self.label_GeometryPreview_stroke.setMinimumSize(QSize(150, 0))

        self.gridLayout_GeometryPreview.addWidget(self.label_GeometryPreview_stroke, 4, 0, 1, 1)

        self.label_GeometryPreview_stroke_opacity = QLabel(self.TabSvgViewer)
        self.label_GeometryPreview_stroke_opacity.setObjectName(u"label_GeometryPreview_stroke_opacity")

        self.gridLayout_GeometryPreview.addWidget(self.label_GeometryPreview_stroke_opacity, 5, 0, 1, 1)

        self.label_2 = QLabel(self.TabSvgViewer)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.gridLayout_GeometryPreview.addWidget(self.label_2, 3, 0, 1, 1)

        self.label_GeometryPreview_fill = QLabel(self.TabSvgViewer)
        self.label_GeometryPreview_fill.setObjectName(u"label_GeometryPreview_fill")
        self.label_GeometryPreview_fill.setMinimumSize(QSize(150, 0))

        self.gridLayout_GeometryPreview.addWidget(self.label_GeometryPreview_fill, 1, 0, 1, 1)

        self.label_GeometryPreview_fill_opacity = QLabel(self.TabSvgViewer)
        self.label_GeometryPreview_fill_opacity.setObjectName(u"label_GeometryPreview_fill_opacity")

        self.gridLayout_GeometryPreview.addWidget(self.label_GeometryPreview_fill_opacity, 2, 0, 1, 1)

        self.colorpicker_GeometryPreview_stroke = ColorPicker(self.TabSvgViewer)
        self.colorpicker_GeometryPreview_stroke.setObjectName(u"colorpicker_GeometryPreview_stroke")

        self.gridLayout_GeometryPreview.addWidget(self.colorpicker_GeometryPreview_stroke, 4, 1, 1, 1)

        self.label_GeometryPreview_stroke_width = QLabel(self.TabSvgViewer)
        self.label_GeometryPreview_stroke_width.setObjectName(u"label_GeometryPreview_stroke_width")

        self.gridLayout_GeometryPreview.addWidget(self.label_GeometryPreview_stroke_width, 6, 0, 1, 1)

        self.GeometryPreview_stroke_width = QDoubleSpinBox(self.TabSvgViewer)
        self.GeometryPreview_stroke_width.setObjectName(u"GeometryPreview_stroke_width")

        self.gridLayout_GeometryPreview.addWidget(self.GeometryPreview_stroke_width, 6, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_GeometryPreview)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.TabSvgViewer, "")
        self.TabGCodeViewer = QWidget()
        self.TabGCodeViewer.setObjectName(u"TabGCodeViewer")
        self.verticalLayout_3 = QVBoxLayout(self.TabGCodeViewer)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_GCodeViewer_LineWidth = QHBoxLayout()
        self.horizontalLayout_GCodeViewer_LineWidth.setObjectName(u"horizontalLayout_GCodeViewer_LineWidth")
        self.horizontalLayout_GCodeViewer_LineWidth.setContentsMargins(-1, -1, -1, 0)
        self.label_GCODEVIEWER_linewidth = QLabel(self.TabGCodeViewer)
        self.label_GCODEVIEWER_linewidth.setObjectName(u"label_GCODEVIEWER_linewidth")
        self.label_GCODEVIEWER_linewidth.setMinimumSize(QSize(150, 0))

        self.horizontalLayout_GCodeViewer_LineWidth.addWidget(self.label_GCODEVIEWER_linewidth)

        self.GCODEVIEWER_linewidth = QDoubleSpinBox(self.TabGCodeViewer)
        self.GCODEVIEWER_linewidth.setObjectName(u"GCODEVIEWER_linewidth")
        self.GCODEVIEWER_linewidth.setDecimals(1)
        self.GCODEVIEWER_linewidth.setSingleStep(0.100000000000000)

        self.horizontalLayout_GCodeViewer_LineWidth.addWidget(self.GCODEVIEWER_linewidth)


        self.verticalLayout_3.addLayout(self.horizontalLayout_GCodeViewer_LineWidth)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.TabGCodeViewer, "")
        self.TabGCodeSimulator = QWidget()
        self.TabGCodeSimulator.setObjectName(u"TabGCodeSimulator")
        self.verticalLayout_5 = QVBoxLayout(self.TabGCodeSimulator)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.TabGCodeSimulator)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.radioButton_GCODE_SIMULATOR_FB_1 = QRadioButton(self.TabGCodeSimulator)
        self.radioButton_GCODE_SIMULATOR_FB_1.setObjectName(u"radioButton_GCODE_SIMULATOR_FB_1")

        self.horizontalLayout.addWidget(self.radioButton_GCODE_SIMULATOR_FB_1)

        self.radioButton_GCODE_SIMULATOR_FB_2 = QRadioButton(self.TabGCodeSimulator)
        self.radioButton_GCODE_SIMULATOR_FB_2.setObjectName(u"radioButton_GCODE_SIMULATOR_FB_2")
        self.radioButton_GCODE_SIMULATOR_FB_2.setChecked(True)

        self.horizontalLayout.addWidget(self.radioButton_GCODE_SIMULATOR_FB_2)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_3)

        self.tabWidget.addTab(self.TabGCodeSimulator, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout_Buttons = QHBoxLayout()
        self.horizontalLayout_Buttons.setObjectName(u"horizontalLayout_Buttons")
        self.cmdDefaults = QPushButton(ViewersSettingsDialog)
        self.cmdDefaults.setObjectName(u"cmdDefaults")
        self.cmdDefaults.setAutoDefault(False)

        self.horizontalLayout_Buttons.addWidget(self.cmdDefaults)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_Buttons.addItem(self.horizontalSpacer)

        self.cmdOK = QPushButton(ViewersSettingsDialog)
        self.cmdOK.setObjectName(u"cmdOK")
        self.cmdOK.setAutoDefault(False)

        self.horizontalLayout_Buttons.addWidget(self.cmdOK)

        self.cmdCancel = QPushButton(ViewersSettingsDialog)
        self.cmdCancel.setObjectName(u"cmdCancel")
        self.cmdCancel.setAutoDefault(False)

        self.horizontalLayout_Buttons.addWidget(self.cmdCancel)


        self.verticalLayout.addLayout(self.horizontalLayout_Buttons)


        self.retranslateUi(ViewersSettingsDialog)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ViewersSettingsDialog)
    # setupUi

    def retranslateUi(self, ViewersSettingsDialog):
        ViewersSettingsDialog.setWindowTitle(QCoreApplication.translate("ViewersSettingsDialog", u"Viewers Settings", None))
        self.Tabs.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Tabs", None))
        self.label_Tabs_fill.setText(QCoreApplication.translate("ViewersSettingsDialog", u"fill", None))
        self.label_Tabs_fill_opacity.setText(QCoreApplication.translate("ViewersSettingsDialog", u"fill-opacity", None))
        self.label_Tabs_fill_opacity_disabled.setText(QCoreApplication.translate("ViewersSettingsDialog", u"fill-opacity [disabled]", None))
        self.Toolpaths.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Toolpaths", None))
        self.label_fill_opacity.setText(QCoreApplication.translate("ViewersSettingsDialog", u"stroke-width", None))
        self.label_fill.setText(QCoreApplication.translate("ViewersSettingsDialog", u"stroke", None))
        self.GeometryPreview.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Geometry Preview", None))
        self.label.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Polygons", None))
        self.label_GeometryPreview_stroke.setText(QCoreApplication.translate("ViewersSettingsDialog", u"stroke", None))
        self.label_GeometryPreview_stroke_opacity.setText(QCoreApplication.translate("ViewersSettingsDialog", u"stroke-opacity", None))
        self.label_2.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Lines", None))
        self.label_GeometryPreview_fill.setText(QCoreApplication.translate("ViewersSettingsDialog", u"fill", None))
        self.label_GeometryPreview_fill_opacity.setText(QCoreApplication.translate("ViewersSettingsDialog", u"fill-opacity", None))
        self.label_GeometryPreview_stroke_width.setText(QCoreApplication.translate("ViewersSettingsDialog", u"stroke-width", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.TabSvgViewer), QCoreApplication.translate("ViewersSettingsDialog", u"Svg Viewer", None))
        self.label_GCODEVIEWER_linewidth.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Line Width", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.TabGCodeViewer), QCoreApplication.translate("ViewersSettingsDialog", u"GCode Viewer", None))
        self.label_3.setText(QCoreApplication.translate("ViewersSettingsDialog", u"OpenGL FrameBuffer Size", None))
        self.radioButton_GCODE_SIMULATOR_FB_1.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Standard", None))
        self.radioButton_GCODE_SIMULATOR_FB_2.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Double", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.TabGCodeSimulator), QCoreApplication.translate("ViewersSettingsDialog", u"GCode Simulator", None))
        self.cmdDefaults.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Set to defaults", None))
        self.cmdOK.setText(QCoreApplication.translate("ViewersSettingsDialog", u"OK", None))
        self.cmdCancel.setText(QCoreApplication.translate("ViewersSettingsDialog", u"Cancel", None))
    # retranslateUi

