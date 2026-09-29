# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Dialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(678, 283)
        self.comboBox_WT3000 = QtWidgets.QComboBox(Dialog)
        self.comboBox_WT3000.setGeometry(QtCore.QRect(193, 40, 281, 41))
        self.comboBox_WT3000.setObjectName("comboBox_WT3000")
        self.pushButton_ConnectEQUWT3000 = QtWidgets.QPushButton(Dialog)
        self.pushButton_ConnectEQUWT3000.setGeometry(QtCore.QRect(493, 40, 81, 41))
        self.pushButton_ConnectEQUWT3000.setObjectName("pushButton_ConnectEQUWT3000")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(80, 50, 101, 20))
        self.label_10.setObjectName("label_10")
        self.pushButton_StopTest = QtWidgets.QPushButton(Dialog)
        self.pushButton_StopTest.setGeometry(QtCore.QRect(209, 140, 93, 41))
        self.pushButton_StopTest.setObjectName("pushButton_StopTest")
        self.pushButton_StartTest = QtWidgets.QPushButton(Dialog)
        self.pushButton_StartTest.setGeometry(QtCore.QRect(80, 140, 93, 41))
        self.pushButton_StartTest.setObjectName("pushButton_StartTest")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton_ConnectEQUWT3000.setText(_translate("Dialog", "连接设备"))
        self.label_10.setText(_translate("Dialog", "WT3000接口  :"))
        self.pushButton_StopTest.setText(_translate("Dialog", "结束采集"))
        self.pushButton_StartTest.setText(_translate("Dialog", "开始采集"))
