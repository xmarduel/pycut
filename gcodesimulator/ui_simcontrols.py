# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'simcontrols.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_SimulationControls(object):
    def setupUi(self, SimulationControls):
        if not SimulationControls.objectName():
            SimulationControls.setObjectName(u"SimulationControls")
        SimulationControls.setProperty(u"modal", False)
        SimulationControls.resize(674, 51)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SimulationControls.sizePolicy().hasHeightForWidth())
        SimulationControls.setSizePolicy(sizePolicy)
        SimulationControls.setStyleSheet(u"/*QWidget {\n"
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
        self.verticalLayout = QVBoxLayout(SimulationControls)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSlider_Position = QSlider(SimulationControls)
        self.horizontalSlider_Position.setObjectName(u"horizontalSlider_Position")
        self.horizontalSlider_Position.setOrientation(Qt.Horizontal)

        self.horizontalLayout.addWidget(self.horizontalSlider_Position)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_Rewind = QPushButton(SimulationControls)
        self.pushButton_Rewind.setObjectName(u"pushButton_Rewind")
        icon = QIcon()
        icon.addFile(u"pics/media-skip-backward.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_Rewind.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.pushButton_Rewind)

        self.pushButton_StepBackward = QPushButton(SimulationControls)
        self.pushButton_StepBackward.setObjectName(u"pushButton_StepBackward")
        icon1 = QIcon()
        icon1.addFile(u"pics/media-seek-backward.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_StepBackward.setIcon(icon1)
        self.pushButton_StepBackward.setAutoRepeat(True)

        self.horizontalLayout_2.addWidget(self.pushButton_StepBackward)

        self.pushButton_RunBackward = QPushButton(SimulationControls)
        self.pushButton_RunBackward.setObjectName(u"pushButton_RunBackward")
        icon2 = QIcon()
        icon2.addFile(u"pics/media-playback-back.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_RunBackward.setIcon(icon2)

        self.horizontalLayout_2.addWidget(self.pushButton_RunBackward)

        self.pushButton_Pause = QPushButton(SimulationControls)
        self.pushButton_Pause.setObjectName(u"pushButton_Pause")
        icon3 = QIcon()
        icon3.addFile(u"pics/media-playback-pause.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_Pause.setIcon(icon3)

        self.horizontalLayout_2.addWidget(self.pushButton_Pause)

        self.pushButton_RunForward = QPushButton(SimulationControls)
        self.pushButton_RunForward.setObjectName(u"pushButton_RunForward")
        icon4 = QIcon()
        icon4.addFile(u"pics/media-playback-start.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_RunForward.setIcon(icon4)

        self.horizontalLayout_2.addWidget(self.pushButton_RunForward)

        self.pushButton_StepForward = QPushButton(SimulationControls)
        self.pushButton_StepForward.setObjectName(u"pushButton_StepForward")
        icon5 = QIcon()
        icon5.addFile(u"pics/media-seek-forward.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_StepForward.setIcon(icon5)
        self.pushButton_StepForward.setAutoRepeat(True)

        self.horizontalLayout_2.addWidget(self.pushButton_StepForward)

        self.pushButton_ToEnd = QPushButton(SimulationControls)
        self.pushButton_ToEnd.setObjectName(u"pushButton_ToEnd")
        icon6 = QIcon()
        icon6.addFile(u"pics/media-skip-forward.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_ToEnd.setIcon(icon6)

        self.horizontalLayout_2.addWidget(self.pushButton_ToEnd)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.spinBox_SpeedFactor = QSpinBox(SimulationControls)
        self.spinBox_SpeedFactor.setObjectName(u"spinBox_SpeedFactor")
        self.spinBox_SpeedFactor.setMinimum(1)
        self.spinBox_SpeedFactor.setMaximum(999)

        self.horizontalLayout_2.addWidget(self.spinBox_SpeedFactor)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.retranslateUi(SimulationControls)

        QMetaObject.connectSlotsByName(SimulationControls)
    # setupUi

    def retranslateUi(self, SimulationControls):
        SimulationControls.setWindowTitle(QCoreApplication.translate("SimulationControls", u"Settings", None))
        self.pushButton_Rewind.setText(QCoreApplication.translate("SimulationControls", u"Rewind", None))
        self.pushButton_StepBackward.setText(QCoreApplication.translate("SimulationControls", u"Step", None))
        self.pushButton_RunBackward.setText(QCoreApplication.translate("SimulationControls", u"Back", None))
        self.pushButton_Pause.setText(QCoreApplication.translate("SimulationControls", u"Pause", None))
        self.pushButton_RunForward.setText(QCoreApplication.translate("SimulationControls", u"Run", None))
        self.pushButton_StepForward.setText(QCoreApplication.translate("SimulationControls", u"Step", None))
        self.pushButton_ToEnd.setText(QCoreApplication.translate("SimulationControls", u"To End", None))
#if QT_CONFIG(tooltip)
        self.spinBox_SpeedFactor.setToolTip(QCoreApplication.translate("SimulationControls", u"Speed factor", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

