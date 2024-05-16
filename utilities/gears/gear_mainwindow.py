# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gear_mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSpinBox, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_mainwindow(object):
    def setupUi(self, mainwindow):
        if not mainwindow.objectName():
            mainwindow.setObjectName(u"mainwindow")
        mainwindow.resize(1146, 734)
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
        self.actionOpenGCode = QAction(mainwindow)
        self.actionOpenGCode.setObjectName(u"actionOpenGCode")
        self.centralwidget = QWidget(mainwindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.scrollArea_GearProperties = QScrollArea(self.centralwidget)
        self.scrollArea_GearProperties.setObjectName(u"scrollArea_GearProperties")
        self.scrollArea_GearProperties.setMinimumSize(QSize(320, 0))
        self.scrollArea_GearProperties.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 318, 714))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, -1, 9, -1)
        self.label_GearSvg = QLabel(self.scrollAreaWidgetContents)
        self.label_GearSvg.setObjectName(u"label_GearSvg")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label_GearSvg.setFont(font)
        self.label_GearSvg.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayout_2.addWidget(self.label_GearSvg)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(4, -1, -1, -1)
        self.label_svg_width = QLabel(self.scrollAreaWidgetContents)
        self.label_svg_width.setObjectName(u"label_svg_width")
        self.label_svg_width.setMinimumSize(QSize(160, 0))
        font1 = QFont()
        font1.setBold(True)
        self.label_svg_width.setFont(font1)

        self.horizontalLayout_11.addWidget(self.label_svg_width)

        self.svg_width = QSpinBox(self.scrollAreaWidgetContents)
        self.svg_width.setObjectName(u"svg_width")
        self.svg_width.setEnabled(True)

        self.horizontalLayout_11.addWidget(self.svg_width)


        self.verticalLayout_2.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(4, -1, -1, -1)
        self.label_svg_height = QLabel(self.scrollAreaWidgetContents)
        self.label_svg_height.setObjectName(u"label_svg_height")
        self.label_svg_height.setMinimumSize(QSize(160, 0))
        self.label_svg_height.setFont(font1)

        self.horizontalLayout_12.addWidget(self.label_svg_height)

        self.svg_height = QSpinBox(self.scrollAreaWidgetContents)
        self.svg_height.setObjectName(u"svg_height")
        self.svg_height.setEnabled(True)

        self.horizontalLayout_12.addWidget(self.svg_height)


        self.verticalLayout_2.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(4, -1, -1, -1)
        self.label_viewbox_x = QLabel(self.scrollAreaWidgetContents)
        self.label_viewbox_x.setObjectName(u"label_viewbox_x")
        self.label_viewbox_x.setMinimumSize(QSize(160, 0))
        self.label_viewbox_x.setFont(font1)

        self.horizontalLayout_13.addWidget(self.label_viewbox_x)

        self.viewbox_x = QSpinBox(self.scrollAreaWidgetContents)
        self.viewbox_x.setObjectName(u"viewbox_x")
        self.viewbox_x.setEnabled(True)

        self.horizontalLayout_13.addWidget(self.viewbox_x)


        self.verticalLayout_2.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(4, -1, -1, -1)
        self.label_viewbox_y = QLabel(self.scrollAreaWidgetContents)
        self.label_viewbox_y.setObjectName(u"label_viewbox_y")
        self.label_viewbox_y.setMinimumSize(QSize(160, 0))
        self.label_viewbox_y.setFont(font1)

        self.horizontalLayout_14.addWidget(self.label_viewbox_y)

        self.viewbox_y = QSpinBox(self.scrollAreaWidgetContents)
        self.viewbox_y.setObjectName(u"viewbox_y")
        self.viewbox_y.setEnabled(True)

        self.horizontalLayout_14.addWidget(self.viewbox_y)


        self.verticalLayout_2.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_L2 = QHBoxLayout()
        self.horizontalLayout_L2.setObjectName(u"horizontalLayout_L2")

        self.verticalLayout_2.addLayout(self.horizontalLayout_L2)

        self.label_GearBasics = QLabel(self.scrollAreaWidgetContents)
        self.label_GearBasics.setObjectName(u"label_GearBasics")
        self.label_GearBasics.setFont(font)
        self.label_GearBasics.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayout_2.addWidget(self.label_GearBasics)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(4, -1, -1, -1)
        self.label_modul = QLabel(self.scrollAreaWidgetContents)
        self.label_modul.setObjectName(u"label_modul")
        self.label_modul.setMinimumSize(QSize(160, 0))
        self.label_modul.setFont(font1)

        self.horizontalLayout_21.addWidget(self.label_modul)

        self.modul = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.modul.setObjectName(u"modul")
        self.modul.setEnabled(True)
        self.modul.setDecimals(1)
        self.modul.setMinimum(0.100000000000000)
        self.modul.setMaximum(10.000000000000000)
        self.modul.setValue(1.000000000000000)

        self.horizontalLayout_21.addWidget(self.modul)


        self.verticalLayout_2.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(4, -1, -1, -1)
        self.label_nb_teeths = QLabel(self.scrollAreaWidgetContents)
        self.label_nb_teeths.setObjectName(u"label_nb_teeths")
        self.label_nb_teeths.setMinimumSize(QSize(160, 0))
        self.label_nb_teeths.setFont(font1)

        self.horizontalLayout_22.addWidget(self.label_nb_teeths)

        self.nb_teeths = QSpinBox(self.scrollAreaWidgetContents)
        self.nb_teeths.setObjectName(u"nb_teeths")
        self.nb_teeths.setEnabled(True)
        self.nb_teeths.setMaximum(200)
        self.nb_teeths.setValue(40)

        self.horizontalLayout_22.addWidget(self.nb_teeths)


        self.verticalLayout_2.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.horizontalLayout_23.setContentsMargins(4, -1, -1, -1)
        self.label_gear_diameter = QLabel(self.scrollAreaWidgetContents)
        self.label_gear_diameter.setObjectName(u"label_gear_diameter")
        self.label_gear_diameter.setMinimumSize(QSize(160, 0))
        self.label_gear_diameter.setFont(font1)

        self.horizontalLayout_23.addWidget(self.label_gear_diameter)

        self.gear_diameter = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.gear_diameter.setObjectName(u"gear_diameter")
        self.gear_diameter.setEnabled(False)
        self.gear_diameter.setDecimals(1)
        self.gear_diameter.setMaximum(200.000000000000000)
        self.gear_diameter.setSingleStep(0.100000000000000)
        self.gear_diameter.setValue(40.000000000000000)

        self.horizontalLayout_23.addWidget(self.gear_diameter)


        self.verticalLayout_2.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalLayout_24.setContentsMargins(4, -1, -1, -1)
        self.label_reinforcment_radius = QLabel(self.scrollAreaWidgetContents)
        self.label_reinforcment_radius.setObjectName(u"label_reinforcment_radius")
        self.label_reinforcment_radius.setMinimumSize(QSize(160, 0))
        self.label_reinforcment_radius.setFont(font1)

        self.horizontalLayout_24.addWidget(self.label_reinforcment_radius)

        self.reinforcment_radius = QSpinBox(self.scrollAreaWidgetContents)
        self.reinforcment_radius.setObjectName(u"reinforcment_radius")
        self.reinforcment_radius.setMinimum(12)
        self.reinforcment_radius.setValue(15)

        self.horizontalLayout_24.addWidget(self.reinforcment_radius)


        self.verticalLayout_2.addLayout(self.horizontalLayout_24)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.label_GearSize = QLabel(self.scrollAreaWidgetContents)
        self.label_GearSize.setObjectName(u"label_GearSize")
        self.label_GearSize.setFont(font)
        self.label_GearSize.setStyleSheet(u"background-color: rgb(196, 196, 196);")

        self.verticalLayout_2.addWidget(self.label_GearSize)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(4, -1, -1, -1)
        self.label_foot_height = QLabel(self.scrollAreaWidgetContents)
        self.label_foot_height.setObjectName(u"label_foot_height")
        self.label_foot_height.setMinimumSize(QSize(160, 0))
        self.label_foot_height.setFont(font1)

        self.horizontalLayout_31.addWidget(self.label_foot_height)

        self.foot_height = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.foot_height.setObjectName(u"foot_height")
        self.foot_height.setEnabled(True)
        self.foot_height.setMaximum(10.000000000000000)
        self.foot_height.setSingleStep(0.100000000000000)
        self.foot_height.setValue(1.250000000000000)

        self.horizontalLayout_31.addWidget(self.foot_height)

        self.button_foot_height_reset = QPushButton(self.scrollAreaWidgetContents)
        self.button_foot_height_reset.setObjectName(u"button_foot_height_reset")
        self.button_foot_height_reset.setMaximumSize(QSize(24, 16777215))

        self.horizontalLayout_31.addWidget(self.button_foot_height_reset)


        self.verticalLayout_2.addLayout(self.horizontalLayout_31)

        self.horizontalLayout_32 = QHBoxLayout()
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.horizontalLayout_32.setContentsMargins(4, -1, -1, -1)
        self.label_head_height = QLabel(self.scrollAreaWidgetContents)
        self.label_head_height.setObjectName(u"label_head_height")
        self.label_head_height.setMinimumSize(QSize(160, 0))
        self.label_head_height.setFont(font1)

        self.horizontalLayout_32.addWidget(self.label_head_height)

        self.head_height = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.head_height.setObjectName(u"head_height")
        self.head_height.setMaximum(10.000000000000000)
        self.head_height.setSingleStep(0.100000000000000)
        self.head_height.setValue(1.000000000000000)

        self.horizontalLayout_32.addWidget(self.head_height)

        self.button_head_height_reset = QPushButton(self.scrollAreaWidgetContents)
        self.button_head_height_reset.setObjectName(u"button_head_height_reset")
        self.button_head_height_reset.setMaximumSize(QSize(24, 16777215))

        self.horizontalLayout_32.addWidget(self.button_head_height_reset)


        self.verticalLayout_2.addLayout(self.horizontalLayout_32)

        self.label_GearTeethsShape = QLabel(self.scrollAreaWidgetContents)
        self.label_GearTeethsShape.setObjectName(u"label_GearTeethsShape")
        self.label_GearTeethsShape.setEnabled(True)
        self.label_GearTeethsShape.setFont(font)
        self.label_GearTeethsShape.setStyleSheet(u"background-color: rgb(198, 198, 198);")

        self.verticalLayout_2.addWidget(self.label_GearTeethsShape)

        self.horizontalLayout_43 = QHBoxLayout()
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.horizontalLayout_43.setContentsMargins(4, -1, -1, -1)
        self.label_ratio_teeth_gap_base = QLabel(self.scrollAreaWidgetContents)
        self.label_ratio_teeth_gap_base.setObjectName(u"label_ratio_teeth_gap_base")
        self.label_ratio_teeth_gap_base.setMinimumSize(QSize(160, 0))
        self.label_ratio_teeth_gap_base.setFont(font1)

        self.horizontalLayout_43.addWidget(self.label_ratio_teeth_gap_base)

        self.ratio_teeth_gap_base = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.ratio_teeth_gap_base.setObjectName(u"ratio_teeth_gap_base")
        self.ratio_teeth_gap_base.setMaximum(5.000000000000000)
        self.ratio_teeth_gap_base.setSingleStep(0.050000000000000)
        self.ratio_teeth_gap_base.setValue(0.600000000000000)

        self.horizontalLayout_43.addWidget(self.ratio_teeth_gap_base)

        self.button_ratio_teeth_gap_base_reset = QPushButton(self.scrollAreaWidgetContents)
        self.button_ratio_teeth_gap_base_reset.setObjectName(u"button_ratio_teeth_gap_base_reset")
        self.button_ratio_teeth_gap_base_reset.setMaximumSize(QSize(24, 16777215))

        self.horizontalLayout_43.addWidget(self.button_ratio_teeth_gap_base_reset)


        self.verticalLayout_2.addLayout(self.horizontalLayout_43)

        self.horizontalLayout_41 = QHBoxLayout()
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.horizontalLayout_41.setContentsMargins(4, -1, -1, -1)
        self.label_curvature = QLabel(self.scrollAreaWidgetContents)
        self.label_curvature.setObjectName(u"label_curvature")
        self.label_curvature.setMinimumSize(QSize(160, 0))
        self.label_curvature.setFont(font1)

        self.horizontalLayout_41.addWidget(self.label_curvature)

        self.curvature = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.curvature.setObjectName(u"curvature")
        self.curvature.setEnabled(True)
        self.curvature.setDecimals(3)
        self.curvature.setMaximum(50.000000000000000)
        self.curvature.setSingleStep(0.100000000000000)
        self.curvature.setValue(5.000000000000000)

        self.horizontalLayout_41.addWidget(self.curvature)

        self.button_curvature_reset = QPushButton(self.scrollAreaWidgetContents)
        self.button_curvature_reset.setObjectName(u"button_curvature_reset")
        self.button_curvature_reset.setMaximumSize(QSize(24, 16777215))

        self.horizontalLayout_41.addWidget(self.button_curvature_reset)


        self.verticalLayout_2.addLayout(self.horizontalLayout_41)

        self.horizontalLayout_42 = QHBoxLayout()
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.horizontalLayout_42.setContentsMargins(4, -1, -1, -1)
        self.label_ratio_teeth_head_base = QLabel(self.scrollAreaWidgetContents)
        self.label_ratio_teeth_head_base.setObjectName(u"label_ratio_teeth_head_base")
        self.label_ratio_teeth_head_base.setMinimumSize(QSize(160, 0))
        self.label_ratio_teeth_head_base.setFont(font1)

        self.horizontalLayout_42.addWidget(self.label_ratio_teeth_head_base)

        self.ratio_teeth_head_base = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.ratio_teeth_head_base.setObjectName(u"ratio_teeth_head_base")
        self.ratio_teeth_head_base.setMaximum(1.000000000000000)
        self.ratio_teeth_head_base.setSingleStep(0.010000000000000)
        self.ratio_teeth_head_base.setValue(0.400000000000000)

        self.horizontalLayout_42.addWidget(self.ratio_teeth_head_base)

        self.button_ratio_teeth_head_base_reset = QPushButton(self.scrollAreaWidgetContents)
        self.button_ratio_teeth_head_base_reset.setObjectName(u"button_ratio_teeth_head_base_reset")
        self.button_ratio_teeth_head_base_reset.setMaximumSize(QSize(24, 16777215))

        self.horizontalLayout_42.addWidget(self.button_ratio_teeth_head_base_reset)


        self.verticalLayout_2.addLayout(self.horizontalLayout_42)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.verticalLayout_2.setStretch(19, 1)
        self.scrollArea_GearProperties.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_2.addWidget(self.scrollArea_GearProperties)

        self.centralArea = QWidget(self.centralwidget)
        self.centralArea.setObjectName(u"centralArea")
        self.centralArea.setMinimumSize(QSize(400, 0))
        self.centralArea.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(self.centralArea)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 0, 0, 0)
        self.generate_svg = QPushButton(self.centralArea)
        self.generate_svg.setObjectName(u"generate_svg")

        self.verticalLayout.addWidget(self.generate_svg)

        self.tabWidget = QTabWidget(self.centralArea)
        self.tabWidget.setObjectName(u"tabWidget")
        self.svgwidget_1_gear = QWidget()
        self.svgwidget_1_gear.setObjectName(u"svgwidget_1_gear")
        self.verticalLayout_3 = QVBoxLayout(self.svgwidget_1_gear)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.svgwidget_1_gear_layout = QVBoxLayout()
        self.svgwidget_1_gear_layout.setObjectName(u"svgwidget_1_gear_layout")

        self.verticalLayout_3.addLayout(self.svgwidget_1_gear_layout)

        self.tabWidget.addTab(self.svgwidget_1_gear, "")
        self.svgwidget_2_gears_static = QWidget()
        self.svgwidget_2_gears_static.setObjectName(u"svgwidget_2_gears_static")
        self.verticalLayout_5 = QVBoxLayout(self.svgwidget_2_gears_static)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.svgwidget_2_gears_static_layout = QVBoxLayout()
        self.svgwidget_2_gears_static_layout.setObjectName(u"svgwidget_2_gears_static_layout")

        self.verticalLayout_5.addLayout(self.svgwidget_2_gears_static_layout)

        self.tabWidget.addTab(self.svgwidget_2_gears_static, "")
        self.svgwidget_2_gears_animated = QWidget()
        self.svgwidget_2_gears_animated.setObjectName(u"svgwidget_2_gears_animated")
        self.verticalLayout_6 = QVBoxLayout(self.svgwidget_2_gears_animated)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.svgwidget_2_gears_animated_layout = QVBoxLayout()
        self.svgwidget_2_gears_animated_layout.setObjectName(u"svgwidget_2_gears_animated_layout")

        self.verticalLayout_6.addLayout(self.svgwidget_2_gears_animated_layout)

        self.tabWidget.addTab(self.svgwidget_2_gears_animated, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.save_svg = QPushButton(self.centralArea)
        self.save_svg.setObjectName(u"save_svg")

        self.verticalLayout.addWidget(self.save_svg)


        self.horizontalLayout_2.addWidget(self.centralArea)

        self.horizontalLayout_2.setStretch(1, 1)
        mainwindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(mainwindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(mainwindow)
    # setupUi

    def retranslateUi(self, mainwindow):
        mainwindow.setWindowTitle(QCoreApplication.translate("mainwindow", u"main", None))
        self.actionOpenSvg.setText(QCoreApplication.translate("mainwindow", u"Load SVG", None))
        self.actionNewJob.setText(QCoreApplication.translate("mainwindow", u"New Job", None))
        self.actionOpenJob.setText(QCoreApplication.translate("mainwindow", u"Open Job...", None))
        self.actionSaveJobAs.setText(QCoreApplication.translate("mainwindow", u"Save Job As...", None))
        self.actionSaveJob.setText(QCoreApplication.translate("mainwindow", u"Save Job", None))
        self.actionTutorial.setText(QCoreApplication.translate("mainwindow", u"Tutorial", None))
        self.actionAboutQt.setText(QCoreApplication.translate("mainwindow", u"About &Qt", None))
        self.actionAboutPyCut.setText(QCoreApplication.translate("mainwindow", u"About PyCut", None))
        self.actionSettings.setText(QCoreApplication.translate("mainwindow", u"Viewers Settings...", None))
        self.actionOpenGCode.setText(QCoreApplication.translate("mainwindow", u"Load GCode", None))
        self.label_GearSvg.setText(QCoreApplication.translate("mainwindow", u"Svg", None))
        self.label_svg_width.setText(QCoreApplication.translate("mainwindow", u"width", None))
        self.label_svg_height.setText(QCoreApplication.translate("mainwindow", u"height", None))
        self.label_viewbox_x.setText(QCoreApplication.translate("mainwindow", u"viewbox : x", None))
        self.label_viewbox_y.setText(QCoreApplication.translate("mainwindow", u"viewbox : y", None))
        self.label_GearBasics.setText(QCoreApplication.translate("mainwindow", u"Basics", None))
        self.label_modul.setText(QCoreApplication.translate("mainwindow", u"module", None))
        self.label_nb_teeths.setText(QCoreApplication.translate("mainwindow", u"nb teeths", None))
        self.label_gear_diameter.setText(QCoreApplication.translate("mainwindow", u"gear diameter", None))
        self.label_reinforcment_radius.setText(QCoreApplication.translate("mainwindow", u"reinforcment radius", None))
        self.label_GearSize.setText(QCoreApplication.translate("mainwindow", u"Sizes", None))
        self.label_foot_height.setText(QCoreApplication.translate("mainwindow", u"foot height", None))
        self.button_foot_height_reset.setText(QCoreApplication.translate("mainwindow", u"...", None))
        self.label_head_height.setText(QCoreApplication.translate("mainwindow", u"head height", None))
        self.button_head_height_reset.setText(QCoreApplication.translate("mainwindow", u"...", None))
        self.label_GearTeethsShape.setText(QCoreApplication.translate("mainwindow", u"Teeths Shape", None))
        self.label_ratio_teeth_gap_base.setText(QCoreApplication.translate("mainwindow", u"ratio teeth gap/base", None))
        self.button_ratio_teeth_gap_base_reset.setText(QCoreApplication.translate("mainwindow", u"....", None))
        self.label_curvature.setText(QCoreApplication.translate("mainwindow", u"curvature", None))
        self.button_curvature_reset.setText(QCoreApplication.translate("mainwindow", u"...", None))
        self.label_ratio_teeth_head_base.setText(QCoreApplication.translate("mainwindow", u"ratio teeth head/base", None))
        self.button_ratio_teeth_head_base_reset.setText(QCoreApplication.translate("mainwindow", u"...", None))
        self.generate_svg.setText(QCoreApplication.translate("mainwindow", u"Generate SVG", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.svgwidget_1_gear), QCoreApplication.translate("mainwindow", u"Gear", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.svgwidget_2_gears_static), QCoreApplication.translate("mainwindow", u"2 Gears", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.svgwidget_2_gears_animated), QCoreApplication.translate("mainwindow", u"Animation", None))
        self.save_svg.setText(QCoreApplication.translate("mainwindow", u"Save SVG", None))
    # retranslateUi

