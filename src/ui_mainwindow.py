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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpinBox, QStatusBar,
    QVBoxLayout, QWidget)

from src.viewer import (ImageViewer, PreviewViewer)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(621, 636)
        self.actionOpen_Folder = QAction(MainWindow)
        self.actionOpen_Folder.setObjectName(u"actionOpen_Folder")
        self.actionCrop_All = QAction(MainWindow)
        self.actionCrop_All.setObjectName(u"actionCrop_All")
        self.actionClose_Folder = QAction(MainWindow)
        self.actionClose_Folder.setObjectName(u"actionClose_Folder")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionClear_all_quadrilaterals = QAction(MainWindow)
        self.actionClear_all_quadrilaterals.setObjectName(u"actionClear_all_quadrilaterals")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.imagesLabel = QLabel(self.centralwidget)
        self.imagesLabel.setObjectName(u"imagesLabel")

        self.verticalLayout.addWidget(self.imagesLabel)

        self.imagesListWidget = QListWidget(self.centralwidget)
        self.imagesListWidget.setObjectName(u"imagesListWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imagesListWidget.sizePolicy().hasHeightForWidth())
        self.imagesListWidget.setSizePolicy(sizePolicy)
        self.imagesListWidget.setMinimumSize(QSize(256, 0))
        self.imagesListWidget.setMaximumSize(QSize(256, 16777215))

        self.verticalLayout.addWidget(self.imagesListWidget)

        self.quadrilateralsLabel = QLabel(self.centralwidget)
        self.quadrilateralsLabel.setObjectName(u"quadrilateralsLabel")

        self.verticalLayout.addWidget(self.quadrilateralsLabel)

        self.quadsListWidget = QListWidget(self.centralwidget)
        self.quadsListWidget.setObjectName(u"quadsListWidget")
        sizePolicy.setHeightForWidth(self.quadsListWidget.sizePolicy().hasHeightForWidth())
        self.quadsListWidget.setSizePolicy(sizePolicy)
        self.quadsListWidget.setMinimumSize(QSize(256, 0))
        self.quadsListWidget.setMaximumSize(QSize(256, 16777215))

        self.verticalLayout.addWidget(self.quadsListWidget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.deleteSelectedQuadButton = QPushButton(self.centralwidget)
        self.deleteSelectedQuadButton.setObjectName(u"deleteSelectedQuadButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.deleteSelectedQuadButton.sizePolicy().hasHeightForWidth())
        self.deleteSelectedQuadButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.deleteSelectedQuadButton)

        self.deleteAllQuadsButton = QPushButton(self.centralwidget)
        self.deleteAllQuadsButton.setObjectName(u"deleteAllQuadsButton")
        sizePolicy1.setHeightForWidth(self.deleteAllQuadsButton.sizePolicy().hasHeightForWidth())
        self.deleteAllQuadsButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.deleteAllQuadsButton)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.cropGroupBox = QGroupBox(self.centralwidget)
        self.cropGroupBox.setObjectName(u"cropGroupBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cropGroupBox.sizePolicy().hasHeightForWidth())
        self.cropGroupBox.setSizePolicy(sizePolicy2)
        self.cropGroupBox.setMinimumSize(QSize(256, 0))
        self.cropGroupBox.setMaximumSize(QSize(256, 16777215))
        self.gridLayout_2 = QGridLayout(self.cropGroupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, -1, 9, -1)
        self.cropAllButton = QPushButton(self.cropGroupBox)
        self.cropAllButton.setObjectName(u"cropAllButton")

        self.gridLayout_2.addWidget(self.cropAllButton, 2, 0, 1, 1)

        self.autoPatchSizeCheckbox = QCheckBox(self.cropGroupBox)
        self.autoPatchSizeCheckbox.setObjectName(u"autoPatchSizeCheckbox")
        self.autoPatchSizeCheckbox.setChecked(True)

        self.gridLayout_2.addWidget(self.autoPatchSizeCheckbox, 0, 0, 1, 1)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.patchWidthLabel = QLabel(self.cropGroupBox)
        self.patchWidthLabel.setObjectName(u"patchWidthLabel")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.patchWidthLabel)

        self.patchWidthSpinBox = QSpinBox(self.cropGroupBox)
        self.patchWidthSpinBox.setObjectName(u"patchWidthSpinBox")
        self.patchWidthSpinBox.setMinimum(1)
        self.patchWidthSpinBox.setMaximum(99999999)
        self.patchWidthSpinBox.setSingleStep(10)
        self.patchWidthSpinBox.setValue(100)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.patchWidthSpinBox)

        self.patchHeightLabel = QLabel(self.cropGroupBox)
        self.patchHeightLabel.setObjectName(u"patchHeightLabel")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.patchHeightLabel)

        self.patchHeightSpinBox = QSpinBox(self.cropGroupBox)
        self.patchHeightSpinBox.setObjectName(u"patchHeightSpinBox")
        self.patchHeightSpinBox.setMinimum(1)
        self.patchHeightSpinBox.setMaximum(99999999)
        self.patchHeightSpinBox.setSingleStep(10)
        self.patchHeightSpinBox.setValue(100)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.patchHeightSpinBox)


        self.gridLayout_2.addLayout(self.formLayout_2, 1, 0, 1, 1)


        self.verticalLayout.addWidget(self.cropGroupBox)


        self.gridLayout.addLayout(self.verticalLayout, 2, 0, 1, 1)

        self.previewGraphicsView = PreviewViewer(self.centralwidget)
        self.previewGraphicsView.setObjectName(u"previewGraphicsView")
        sizePolicy.setHeightForWidth(self.previewGraphicsView.sizePolicy().hasHeightForWidth())
        self.previewGraphicsView.setSizePolicy(sizePolicy)
        self.previewGraphicsView.setMinimumSize(QSize(256, 128))
        self.previewGraphicsView.setMaximumSize(QSize(256, 16777215))

        self.gridLayout.addWidget(self.previewGraphicsView, 4, 0, 1, 1)

        self.previewLabel = QLabel(self.centralwidget)
        self.previewLabel.setObjectName(u"previewLabel")
        self.previewLabel.setMinimumSize(QSize(256, 0))
        self.previewLabel.setMaximumSize(QSize(256, 16777215))

        self.gridLayout.addWidget(self.previewLabel, 3, 0, 1, 1)

        self.graphicsView = ImageViewer(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.gridLayout.addWidget(self.graphicsView, 0, 1, 5, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 621, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen_Folder)
        self.menuFile.addAction(self.actionClose_Folder)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen_Folder.setText(QCoreApplication.translate("MainWindow", u"Open Folder...", None))
        self.actionCrop_All.setText(QCoreApplication.translate("MainWindow", u"Crop All", None))
        self.actionClose_Folder.setText(QCoreApplication.translate("MainWindow", u"Close Folder", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionClear_all_quadrilaterals.setText(QCoreApplication.translate("MainWindow", u"Clear All Quadrilaterals", None))
        self.imagesLabel.setText(QCoreApplication.translate("MainWindow", u"Images", None))
        self.quadrilateralsLabel.setText(QCoreApplication.translate("MainWindow", u"Quadrilaterals", None))
        self.deleteSelectedQuadButton.setText(QCoreApplication.translate("MainWindow", u"Delete Selected", None))
        self.deleteAllQuadsButton.setText(QCoreApplication.translate("MainWindow", u"Delete All", None))
        self.cropGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Crop", None))
        self.cropAllButton.setText(QCoreApplication.translate("MainWindow", u"Crop All", None))
        self.autoPatchSizeCheckbox.setText(QCoreApplication.translate("MainWindow", u"Automatic patch size", None))
        self.patchWidthLabel.setText(QCoreApplication.translate("MainWindow", u"Patch Width (px)", None))
        self.patchHeightLabel.setText(QCoreApplication.translate("MainWindow", u"Patch Height (px)", None))
        self.previewLabel.setText(QCoreApplication.translate("MainWindow", u"Preview", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

