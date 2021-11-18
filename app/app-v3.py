# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'app-v2.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.comboOrigin = QtWidgets.QComboBox(self.centralwidget)
        self.comboOrigin.setGeometry(QtCore.QRect(20, 70, 161, 31))
        self.comboOrigin.setObjectName("comboOrigin")
        self.comboOrigin.addItem("")
        self.comboOrigin.addItem("")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(20, 10, 301, 31))
        self.textEdit.setObjectName("textEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(690, 10, 91, 28))
        self.pushButton.setObjectName("pushButton")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 110, 761, 421))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(200, 80, 121, 17))
        self.checkBox.setObjectName("checkBox")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setEnabled(True)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 50, 201, 21))
        self.plainTextEdit.setMouseTracking(False)
        self.plainTextEdit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.plainTextEdit.setLineWidth(0)
        self.plainTextEdit.setObjectName("plainTextEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.comboOrigin.setItemText(0, _translate("MainWindow", "ALTITUDE 100"))
        self.comboOrigin.setItemText(1, _translate("MainWindow", "ANNEESSENS"))
        self.textEdit.setHtml(
            _translate(
                "MainWindow",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:7.8pt; text-decoration: underline;">Welcome to the Proximus Dataset Visualizer</span></p></body></html>',
            )
        )
        self.pushButton.setText(_translate("MainWindow", "Exit"))
        self.checkBox.setText(_translate("MainWindow", "Aggregate Demand"))
        self.plainTextEdit.setPlainText(
            _translate("MainWindow", "Origin Neighborhood for demand:")
        )

