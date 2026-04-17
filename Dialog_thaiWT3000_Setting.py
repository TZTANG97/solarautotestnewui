# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_Dialog_thai_WT3000_Setting(object):
    def setupUi(self, Dialog_thai_WT3000_Setting):
        Dialog_thai_WT3000_Setting.setObjectName("Dialog_thai_WT3000_Setting")
        Dialog_thai_WT3000_Setting.resize(360, 180)
        self.pushButton_Confirm = QtWidgets.QPushButton(Dialog_thai_WT3000_Setting)
        self.pushButton_Confirm.setGeometry(QtCore.QRect(240, 120, 90, 31))
        self.pushButton_Confirm.setObjectName("pushButton_Confirm")
        self.label = QtWidgets.QLabel(Dialog_thai_WT3000_Setting)
        self.label.setGeometry(QtCore.QRect(20, 30, 90, 21))
        self.label.setObjectName("label")
        self.comboBox_BaudRate = QtWidgets.QComboBox(Dialog_thai_WT3000_Setting)
        self.comboBox_BaudRate.setGeometry(QtCore.QRect(120, 30, 120, 21))
        self.comboBox_BaudRate.setObjectName("comboBox_BaudRate")
        self.comboBox_BaudRate.addItem("9600")
        self.comboBox_BaudRate.addItem("19200")
        self.comboBox_BaudRate.addItem("38400")
        self.comboBox_BaudRate.addItem("57600")
        self.comboBox_BaudRate.addItem("115200")

        self.retranslateUi(Dialog_thai_WT3000_Setting)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thai_WT3000_Setting)

    def retranslateUi(self, Dialog_thai_WT3000_Setting):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thai_WT3000_Setting.setWindowTitle(_translate("Dialog_thai_WT3000_Setting", "WT3000参数设置"))
        self.pushButton_Confirm.setText(_translate("Dialog_thai_WT3000_Setting", "确认"))
        self.label.setText(_translate("Dialog_thai_WT3000_Setting", "波特率"))
