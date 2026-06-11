# -*- coding: utf-8 -*-
# WT3000参数设置 - 现代化单面板布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_thai_WT3000_Setting(object):
    def setupUi(self, Dialog_thai_WT3000_Setting):
        Dialog_thai_WT3000_Setting.setObjectName("Dialog_thai_WT3000_Setting")
        Dialog_thai_WT3000_Setting.resize(510, 360)
        Dialog_thai_WT3000_Setting.setMinimumSize(QtCore.QSize(510, 360))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thai_WT3000_Setting.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thai_WT3000_Setting)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ── 波特率设置 ──
        contentWidget = QtWidgets.QWidget()
        contentLayout = QtWidgets.QFormLayout(contentWidget)
        contentLayout.setContentsMargins(20, 20, 20, 20)
        contentLayout.setSpacing(12)

        self.label = QtWidgets.QLabel("波特率:")
        self.label.setObjectName("label")
        contentLayout.addRow(self.label)

        self.comboBox_BaudRate = QtWidgets.QComboBox()
        self.comboBox_BaudRate.setObjectName("comboBox_BaudRate")
        self.comboBox_BaudRate.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.comboBox_BaudRate.setFixedWidth(120)
        contentLayout.addRow(self.comboBox_BaudRate)

        self.pushButton_Confirm = QtWidgets.QPushButton("确认")
        self.pushButton_Confirm.setObjectName("pushButton_Confirm")
        self.pushButton_Confirm.setFixedWidth(90)
        contentLayout.addRow(self.pushButton_Confirm)

        mainLayout.addWidget(contentWidget)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.pushButton_TestAppend = QtWidgets.QPushButton()
        self.pushButton_TestAppend.setObjectName("pushButton_TestAppend")
        self.pushButton_TestAppend.setVisible(False)

        self.pushButton_ReadSettingFile = QtWidgets.QPushButton()
        self.pushButton_ReadSettingFile.setObjectName("pushButton_ReadSettingFile")
        self.pushButton_ReadSettingFile.setVisible(False)

        self.pushButton_SaveSettingFile = QtWidgets.QPushButton()
        self.pushButton_SaveSettingFile.setObjectName("pushButton_SaveSettingFile")
        self.pushButton_SaveSettingFile.setVisible(False)

        self.retranslateUi(Dialog_thai_WT3000_Setting)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thai_WT3000_Setting)

    def retranslateUi(self, Dialog_thai_WT3000_Setting):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thai_WT3000_Setting.setWindowTitle(_translate("Dialog_thai_WT3000_Setting", "WT3000参数设置"))
        self.pushButton_Confirm.setText(_translate("Dialog_thai_WT3000_Setting", "确认"))
        self.label.setText(_translate("Dialog_thai_WT3000_Setting", "波特率:"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thai_WT3000_Setting", "测试追加"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thai_WT3000_Setting", "读取设定"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thai_WT3000_Setting", "保存设定"))
        self.pushButton_Send.setText(_translate("Dialog_thai_WT3000_Setting", "提交"))
