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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(682, 436)
        self.actionOpen_Folder = QAction(MainWindow)
        self.actionOpen_Folder.setObjectName(u"actionOpen_Folder")
        self.actionCrop_All = QAction(MainWindow)
        self.actionCrop_All.setObjectName(u"actionCrop_All")
        self.actionClose_Folder = QAction(MainWindow)
        self.actionClose_Folder.setObjectName(u"actionClose_Folder")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionClear_all_annotations = QAction(MainWindow)
        self.actionClear_all_annotations.setObjectName(u"actionClear_all_annotations")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.imagesListWidget = QListWidget(self.centralwidget)
        self.imagesListWidget.setObjectName(u"imagesListWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imagesListWidget.sizePolicy().hasHeightForWidth())
        self.imagesListWidget.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.imagesListWidget)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.quadsListWidget = QListWidget(self.centralwidget)
        self.quadsListWidget.setObjectName(u"quadsListWidget")
        sizePolicy.setHeightForWidth(self.quadsListWidget.sizePolicy().hasHeightForWidth())
        self.quadsListWidget.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.quadsListWidget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.deleteQuadButton = QPushButton(self.centralwidget)
        self.deleteQuadButton.setObjectName(u"deleteQuadButton")

        self.horizontalLayout_2.addWidget(self.deleteQuadButton)

        self.horizontalSpacer = QSpacerItem(100, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 682, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuCrop = QMenu(self.menubar)
        self.menuCrop.setObjectName(u"menuCrop")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuCrop.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen_Folder)
        self.menuFile.addAction(self.actionClose_Folder)
        self.menuCrop.addAction(self.actionCrop_All)
        self.menuCrop.addAction(self.actionClear_all_annotations)
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
        self.actionClear_all_annotations.setText(QCoreApplication.translate("MainWindow", u"Clear All Annotations", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Images", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Quadrilaterals", None))
        self.deleteQuadButton.setText(QCoreApplication.translate("MainWindow", u"Delete Quadrilateral", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuCrop.setTitle(QCoreApplication.translate("MainWindow", u"Actions", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

