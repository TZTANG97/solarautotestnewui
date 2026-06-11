# -*- coding: utf-8 -*-
"""
WT5000 parameter configuration dialog - Modern single-panel scrollable layout.
All widget objectNames are preserved for backward compatibility with SCPITestWave.py.
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_thai_WT5000(object):
    """WT5000 parameter configuration UI."""

    def setupUi(self, Dialog_thai_WT5000):
        Dialog_thai_WT5000.setObjectName("Dialog_thai_WT5000")
        Dialog_thai_WT5000.resize(1200, 900)
        Dialog_thai_WT5000.setMinimumSize(QtCore.QSize(900, 700))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_thai_WT5000.setWindowIcon(icon)

        # --- Global stylesheet ---
        _CHECKBOX_STYLE = (
            "QCheckBox { font-size: 12px; color: #334155; spacing: 6px; }"
            "QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; "
            "border: 1px solid #cbd5e1; background: #ffffff; }"
            "QCheckBox::indicator:checked { background: #3b82f6; border-color: #3b82f6; }"
            "QCheckBox::indicator:hover { border-color: #94a3b8; }"
        )
        _GROUP_STYLE = (
            "QGroupBox { font-size: 13px; font-weight: bold; color: #1e293b; "
            "border: 1px solid #e2e8f0; border-radius: 6px; margin-top: 12px; "
            "padding: 16px 12px 12px 12px; background: #f8fafc; }"
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; "
            "left: 12px; padding: 0 8px; background: white; border-radius: 3px; }"
        )
        _COMBO_STYLE = (
            "QComboBox { font-size: 12px; color: #334155; padding: 3px 8px; "
            "border: 1px solid #cbd5e1; border-radius: 4px; background: white; "
            "min-width: 80px; }"
            "QComboBox:hover { border-color: #94a3b8; }"
            "QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; "
            "width: 20px; border-left: 1px solid #e2e8f0; border-top-right-radius: 4px; "
            "border-bottom-right-radius: 4px; }"
        )
        _LABEL_STYLE = "QLabel { font-size: 12px; color: #475569; background: transparent; }"
        _TEXTEDIT_STYLE = (
            "QTextEdit { font-size: 12px; color: #334155; padding: 4px 6px; "
            "border: 1px solid #cbd5e1; border-radius: 4px; background: white; }"
            "QTextEdit:focus { border-color: #3b82f6; }"
        )

        # ================================================================
        # Main layout
        # ================================================================
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thai_WT5000)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ================================================================
        # Top bar (56 px)
        # ================================================================
        topBar = QtWidgets.QWidget()
        topBar.setFixedHeight(56)
        topBar.setStyleSheet(
            "QWidget { background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; }"
        )
        topLayout = QtWidgets.QHBoxLayout(topBar)
        topLayout.setContentsMargins(16, 0, 16, 0)
        topLayout.setSpacing(8)

        # -- pushButton_TestAppend (purple) --
        self.pushButton_TestAppend = QtWidgets.QPushButton("追加配置")
        self.pushButton_TestAppend.setObjectName("pushButton_TestAppend")
        self.pushButton_TestAppend.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_TestAppend.setStyleSheet(
            "QPushButton { background-color: #8b5cf6; color: white; border: none; "
            "border-radius: 4px; padding: 8px 16px; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background-color: #7c3aed; }"
            "QPushButton:pressed { background-color: #6d28d9; }"
        )

        # -- pushButton_ReadSettingFile (blue) --
        self.pushButton_ReadSettingFile = QtWidgets.QPushButton("读取配置")
        self.pushButton_ReadSettingFile.setObjectName("pushButton_ReadSettingFile")
        self.pushButton_ReadSettingFile.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_ReadSettingFile.setStyleSheet(
            "QPushButton { background-color: #3b82f6; color: white; border: none; "
            "border-radius: 4px; padding: 8px 16px; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background-color: #2563eb; }"
            "QPushButton:pressed { background-color: #1d4ed8; }"
        )

        # -- pushButton_SaveSettingFile (green) --
        self.pushButton_SaveSettingFile = QtWidgets.QPushButton("保存配置")
        self.pushButton_SaveSettingFile.setObjectName("pushButton_SaveSettingFile")
        self.pushButton_SaveSettingFile.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_SaveSettingFile.setStyleSheet(
            "QPushButton { background-color: #22c55e; color: white; border: none; "
            "border-radius: 4px; padding: 8px 16px; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background-color: #16a34a; }"
            "QPushButton:pressed { background-color: #15803d; }"
        )

        # Separator line
        sepLine = QtWidgets.QFrame()
        sepLine.setFrameShape(QtWidgets.QFrame.VLine)
        sepLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        sepLine.setStyleSheet("QFrame { color: #cbd5e1; }")

        # Title
        topTitle = QtWidgets.QLabel("WT5000 参数配置")
        topTitle.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #1e293b; background: transparent;"
        )

        # pushButton_Confirm (teal, right-aligned)
        self.pushButton_Confirm = QtWidgets.QPushButton("确认")
        self.pushButton_Confirm.setObjectName("pushButton_Confirm")
        self.pushButton_Confirm.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_Confirm.setFixedWidth(80)
        self.pushButton_Confirm.setStyleSheet(
            "QPushButton { background-color: #0d9488; color: white; border: none; "
            "border-radius: 4px; padding: 8px 16px; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background-color: #0f766e; }"
            "QPushButton:pressed { background-color: #115e59; }"
        )

        topLayout.addWidget(self.pushButton_TestAppend)
        topLayout.addWidget(self.pushButton_ReadSettingFile)
        topLayout.addWidget(self.pushButton_SaveSettingFile)
        topLayout.addWidget(sepLine)
        topLayout.addWidget(topTitle)
        topLayout.addStretch()
        topLayout.addWidget(self.pushButton_Confirm)
        mainLayout.addWidget(topBar)

        # ================================================================
        # Scrollable content area
        # ================================================================
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        scrollArea.setStyleSheet(
            "QScrollArea { border: none; background-color: white; }"
            "QScrollBar:vertical { background: #f1f5f9; width: 8px; border-radius: 4px; }"
            "QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 40px; }"
            "QScrollBar::handle:vertical:hover { background: #94a3b8; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }"
        )
        contentWidget = QtWidgets.QWidget()
        contentWidget.setStyleSheet("background-color: white;")
        contentLayout = QtWidgets.QVBoxLayout(contentWidget)
        contentLayout.setContentsMargins(20, 16, 20, 16)
        contentLayout.setSpacing(14)

        # ----------------------------------------------------------------
        # Section: 接线方式 (Wiring)
        # ----------------------------------------------------------------
        grpWiring = QtWidgets.QGroupBox("接线方式")
        grpWiring.setStyleSheet(_GROUP_STYLE)
        grpWiringLayout = QtWidgets.QGridLayout(grpWiring)
        grpWiringLayout.setSpacing(8)

        self.label_38 = QtWidgets.QLabel("SigmaA")
        self.label_38.setStyleSheet(_LABEL_STYLE)
        self.label_41 = QtWidgets.QLabel("SigmaB")
        self.label_41.setStyleSheet(_LABEL_STYLE)

        self.comboBox_SigmA1 = QtWidgets.QComboBox()
        self.comboBox_SigmA1.setObjectName("comboBox_SigmA1")
        self.comboBox_SigmA1.addItems(["---", "1P3W", "3P3W", "3P4W", "3V3A"])
        self.comboBox_SigmA1.setStyleSheet(_COMBO_STYLE)

        self.comboBox_SigmA2 = QtWidgets.QComboBox()
        self.comboBox_SigmA2.setObjectName("comboBox_SigmA2")
        self.comboBox_SigmA2.addItems(["Element1", "Element2", "Element3", "Element4"])
        self.comboBox_SigmA2.setStyleSheet(_COMBO_STYLE)

        self.comboBox_SigmB1 = QtWidgets.QComboBox()
        self.comboBox_SigmB1.setObjectName("comboBox_SigmB1")
        self.comboBox_SigmB1.addItems(["---", "1P3W", "3P3W", "3P4W", "3V3A"])
        self.comboBox_SigmB1.setStyleSheet(_COMBO_STYLE)

        self.comboBox_SigmB2 = QtWidgets.QComboBox()
        self.comboBox_SigmB2.setObjectName("comboBox_SigmB2")
        self.comboBox_SigmB2.addItems(["Element1", "Element2", "Element3", "Element4"])
        self.comboBox_SigmB2.setStyleSheet(_COMBO_STYLE)

        grpWiringLayout.addWidget(self.label_38, 0, 0)
        grpWiringLayout.addWidget(self.comboBox_SigmA1, 0, 1)
        grpWiringLayout.addWidget(self.comboBox_SigmA2, 0, 2)
        grpWiringLayout.addWidget(self.label_41, 1, 0)
        grpWiringLayout.addWidget(self.comboBox_SigmB1, 1, 1)
        grpWiringLayout.addWidget(self.comboBox_SigmB2, 1, 2)
        grpWiringLayout.setColumnStretch(3, 1)
        contentLayout.addWidget(grpWiring)

        # ----------------------------------------------------------------
        # Section: 基本设置 (Basic Settings)
        # ----------------------------------------------------------------
        grpBasic = QtWidgets.QGroupBox("基本设置")
        grpBasic.setStyleSheet(_GROUP_STYLE)
        grpBasicLayout = QtWidgets.QGridLayout(grpBasic)
        grpBasicLayout.setSpacing(8)

        # Row 0: 更新率 / 项目
        label_44 = QtWidgets.QLabel("更新率")
        label_44.setStyleSheet(_LABEL_STYLE)
        self.comboBox_ReplaceRate = QtWidgets.QComboBox()
        self.comboBox_ReplaceRate.setObjectName("comboBox_ReplaceRate")
        self.comboBox_ReplaceRate.addItems([
            "50ms", "100ms", "200ms", "500ms", "1s", "2s", "5s", "10s", "20s"
        ])
        self.comboBox_ReplaceRate.setStyleSheet(_COMBO_STYLE)

        label_73 = QtWidgets.QLabel("项目数")
        label_73.setStyleSheet(_LABEL_STYLE)
        self.comboBox_ProjectNum = QtWidgets.QComboBox()
        self.comboBox_ProjectNum.setObjectName("comboBox_ProjectNum")
        self.comboBox_ProjectNum.addItems(["12", "24", "48", "200", "900"])
        self.comboBox_ProjectNum.setStyleSheet(_COMBO_STYLE)

        grpBasicLayout.addWidget(label_44, 0, 0)
        grpBasicLayout.addWidget(self.comboBox_ReplaceRate, 0, 1)
        grpBasicLayout.addWidget(label_73, 0, 2)
        grpBasicLayout.addWidget(self.comboBox_ProjectNum, 0, 3)
        grpBasicLayout.setColumnStretch(4, 1)

        # Row 1: 自动保存 / 停止时间
        label_75 = QtWidgets.QLabel("自动保存")
        label_75.setStyleSheet(_LABEL_STYLE)
        self.comboBox_AutoSave = QtWidgets.QComboBox()
        self.comboBox_AutoSave.setObjectName("comboBox_AutoSave")
        self.comboBox_AutoSave.addItems(["OFF", "自动保存", "手动保存"])
        self.comboBox_AutoSave.setCurrentIndex(1)
        self.comboBox_AutoSave.setEnabled(False)
        self.comboBox_AutoSave.setStyleSheet(_COMBO_STYLE)

        label_89 = QtWidgets.QLabel("停止时间")
        label_89.setStyleSheet(_LABEL_STYLE)
        self.textEdit_StopTime = QtWidgets.QTextEdit()
        self.textEdit_StopTime.setObjectName("textEdit_StopTime")
        self.textEdit_StopTime.setPlaceholderText("")
        self.textEdit_StopTime.setHtml(
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">'
            '<span style=" font-size:9pt;">00:05:00</span></p>'
        )
        self.textEdit_StopTime.setMaximumHeight(32)
        self.textEdit_StopTime.setStyleSheet(_TEXTEDIT_STYLE)

        grpBasicLayout.addWidget(label_75, 1, 0)
        grpBasicLayout.addWidget(self.comboBox_AutoSave, 1, 1)
        grpBasicLayout.addWidget(label_89, 1, 2)
        grpBasicLayout.addWidget(self.textEdit_StopTime, 1, 3)
        contentLayout.addWidget(grpBasic)

        # ----------------------------------------------------------------
        # Section: 文件设置 (File Settings)
        # ----------------------------------------------------------------
        grpFile = QtWidgets.QGroupBox("文件设置")
        grpFile.setStyleSheet(_GROUP_STYLE)
        grpFileLayout = QtWidgets.QGridLayout(grpFile)
        grpFileLayout.setSpacing(8)

        label_39 = QtWidgets.QLabel("文件名")
        label_39.setStyleSheet(_LABEL_STYLE)
        self.textEdit_FileNameList = QtWidgets.QTextEdit()
        self.textEdit_FileNameList.setObjectName("textEdit_FileNameList")
        self.textEdit_FileNameList.setHtml(
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">'
            '<span style=" font-size:9pt;">'
            '100%_ambient,100%_+55,100%_-10,66%_ambient,66%_+55,66%_-10,33%_ambient,33%_+55,33%_-10,100%_ambient'
            '</span></p>'
        )
        self.textEdit_FileNameList.setStyleSheet(_TEXTEDIT_STYLE)

        label_136 = QtWidgets.QLabel("保存路径")
        label_136.setStyleSheet(_LABEL_STYLE)
        self.textEdit_SavePath = QtWidgets.QTextEdit()
        self.textEdit_SavePath.setObjectName("textEdit_SavePath")
        self.textEdit_SavePath.setHtml(
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">'
            '<span style=" font-size:9pt;">D:/xiebodianliu_test</span></p>'
        )
        self.textEdit_SavePath.setMaximumHeight(32)
        self.textEdit_SavePath.setStyleSheet(_TEXTEDIT_STYLE)

        self.checkBox_AutoName = QtWidgets.QCheckBox("自动命名")
        self.checkBox_AutoName.setObjectName("checkBox_AutoName")
        self.checkBox_AutoName.setEnabled(False)
        self.checkBox_AutoName.setCheckable(False)
        self.checkBox_AutoName.setChecked(False)
        self.checkBox_AutoName.setStyleSheet(_CHECKBOX_STYLE)

        grpFileLayout.addWidget(label_39, 0, 0)
        grpFileLayout.addWidget(self.textEdit_FileNameList, 0, 1, 1, 3)
        grpFileLayout.addWidget(label_136, 1, 0)
        grpFileLayout.addWidget(self.textEdit_SavePath, 1, 1)
        grpFileLayout.addWidget(self.checkBox_AutoName, 1, 2)
        grpFileLayout.setColumnStretch(3, 1)
        contentLayout.addWidget(grpFile)

        # ----------------------------------------------------------------
        # Section: 元件选择 (Element Selection)
        # ----------------------------------------------------------------
        grpElement = QtWidgets.QGroupBox("元件选择")
        grpElement.setStyleSheet(_GROUP_STYLE)
        grpElementLayout = QtWidgets.QGridLayout(grpElement)
        grpElementLayout.setSpacing(8)

        self.checkBox_SetElement1 = QtWidgets.QCheckBox("Element1")
        self.checkBox_SetElement1.setObjectName("checkBox_SetElement1")
        self.checkBox_SetElement1.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetElement2 = QtWidgets.QCheckBox("Element2")
        self.checkBox_SetElement2.setObjectName("checkBox_SetElement2")
        self.checkBox_SetElement2.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetElement3 = QtWidgets.QCheckBox("Element3")
        self.checkBox_SetElement3.setObjectName("checkBox_SetElement3")
        self.checkBox_SetElement3.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetElement4 = QtWidgets.QCheckBox("Element4")
        self.checkBox_SetElement4.setObjectName("checkBox_SetElement4")
        self.checkBox_SetElement4.setStyleSheet(_CHECKBOX_STYLE)

        for i, cb in enumerate([
            self.checkBox_SetElement1, self.checkBox_SetElement2,
            self.checkBox_SetElement3, self.checkBox_SetElement4
        ]):
            grpElementLayout.addWidget(cb, 0, i)
        grpElementLayout.setColumnStretch(4, 1)
        contentLayout.addWidget(grpElement)

        # ----------------------------------------------------------------
        # Section: Sigma 参数
        # ----------------------------------------------------------------
        grpSigma = QtWidgets.QGroupBox("Sigma 参数")
        grpSigma.setStyleSheet(_GROUP_STYLE)
        grpSigmaLayout = QtWidgets.QGridLayout(grpSigma)
        grpSigmaLayout.setSpacing(8)

        self.checkBox_SetSigma = QtWidgets.QCheckBox("∑")
        self.checkBox_SetSigma.setObjectName("checkBox_SetSigma")
        self.checkBox_SetSigma.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetSigmaA = QtWidgets.QCheckBox("SigmaA")
        self.checkBox_SetSigmaA.setObjectName("checkBox_SetSigmaA")
        self.checkBox_SetSigmaA.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetSigmaB = QtWidgets.QCheckBox("SigmaB")
        self.checkBox_SetSigmaB.setObjectName("checkBox_SetSigmaB")
        self.checkBox_SetSigmaB.setStyleSheet(_CHECKBOX_STYLE)

        for i, cb in enumerate([
            self.checkBox_SetSigma, self.checkBox_SetSigmaA, self.checkBox_SetSigmaB
        ]):
            grpSigmaLayout.addWidget(cb, 0, i)
        grpSigmaLayout.setColumnStretch(3, 1)
        contentLayout.addWidget(grpSigma)

        # ----------------------------------------------------------------
        # Section: 电压参数 (Voltage Parameters)
        # ----------------------------------------------------------------
        grpVoltage = QtWidgets.QGroupBox("电压参数")
        grpVoltage.setStyleSheet(_GROUP_STYLE)
        grpVoltageLayout = QtWidgets.QGridLayout(grpVoltage)
        grpVoltageLayout.setSpacing(8)

        self.checkBox_SetUrms = QtWidgets.QCheckBox("Urms")
        self.checkBox_SetUrms.setObjectName("checkBox_SetUrms")
        self.checkBox_SetUrms.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetUmn = QtWidgets.QCheckBox("Umn")
        self.checkBox_SetUmn.setObjectName("checkBox_SetUmn")
        self.checkBox_SetUmn.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetUdc = QtWidgets.QCheckBox("Udc")
        self.checkBox_SetUdc.setObjectName("checkBox_SetUdc")
        self.checkBox_SetUdc.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetUrmn = QtWidgets.QCheckBox("Urmn")
        self.checkBox_SetUrmn.setObjectName("checkBox_SetUrmn")
        self.checkBox_SetUrmn.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetUac = QtWidgets.QCheckBox("Uac")
        self.checkBox_SetUac.setObjectName("checkBox_SetUac")
        self.checkBox_SetUac.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetRngU = QtWidgets.QCheckBox("RngU")
        self.checkBox_SetRngU.setObjectName("checkBox_SetRngU")
        self.checkBox_SetRngU.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetCfU = QtWidgets.QCheckBox("CfU")
        self.checkBox_SetCfU.setObjectName("checkBox_SetCfU")
        self.checkBox_SetCfU.setStyleSheet(_CHECKBOX_STYLE)

        _vItems = [
            self.checkBox_SetUrms, self.checkBox_SetUmn, self.checkBox_SetUdc,
            self.checkBox_SetUrmn, self.checkBox_SetUac, self.checkBox_SetRngU,
            self.checkBox_SetCfU,
        ]
        cols = 7
        for i, cb in enumerate(_vItems):
            grpVoltageLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpVoltageLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpVoltage)

        # ----------------------------------------------------------------
        # Section: 电流参数 (Current Parameters)
        # ----------------------------------------------------------------
        grpCurrent = QtWidgets.QGroupBox("电流参数")
        grpCurrent.setStyleSheet(_GROUP_STYLE)
        grpCurrentLayout = QtWidgets.QGridLayout(grpCurrent)
        grpCurrentLayout.setSpacing(8)

        self.checkBox_SetIrms = QtWidgets.QCheckBox("Irms")
        self.checkBox_SetIrms.setObjectName("checkBox_SetIrms")
        self.checkBox_SetIrms.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetImn = QtWidgets.QCheckBox("Imn")
        self.checkBox_SetImn.setObjectName("checkBox_SetImn")
        self.checkBox_SetImn.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIdc = QtWidgets.QCheckBox("Idc")
        self.checkBox_SetIdc.setObjectName("checkBox_SetIdc")
        self.checkBox_SetIdc.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIrmn = QtWidgets.QCheckBox("Irmn")
        self.checkBox_SetIrmn.setObjectName("checkBox_SetIrmn")
        self.checkBox_SetIrmn.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIac = QtWidgets.QCheckBox("Iac")
        self.checkBox_SetIac.setObjectName("checkBox_SetIac")
        self.checkBox_SetIac.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetRngI = QtWidgets.QCheckBox("RngI")
        self.checkBox_SetRngI.setObjectName("checkBox_SetRngI")
        self.checkBox_SetRngI.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetCfI = QtWidgets.QCheckBox("CfI")
        self.checkBox_SetCfI.setObjectName("checkBox_SetCfI")
        self.checkBox_SetCfI.setStyleSheet(_CHECKBOX_STYLE)

        _iItems = [
            self.checkBox_SetIrms, self.checkBox_SetImn, self.checkBox_SetIdc,
            self.checkBox_SetIrmn, self.checkBox_SetIac, self.checkBox_SetRngI,
            self.checkBox_SetCfI,
        ]
        for i, cb in enumerate(_iItems):
            grpCurrentLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpCurrentLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpCurrent)

        # ----------------------------------------------------------------
        # Section: 峰值参数 (Peak Parameters)
        # ----------------------------------------------------------------
        grpPeak = QtWidgets.QGroupBox("峰值参数")
        grpPeak.setStyleSheet(_GROUP_STYLE)
        grpPeakLayout = QtWidgets.QGridLayout(grpPeak)
        grpPeakLayout.setSpacing(8)

        self.checkBox_SetUppeak = QtWidgets.QCheckBox("Uppeak")
        self.checkBox_SetUppeak.setObjectName("checkBox_SetUppeak")
        self.checkBox_SetUppeak.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetUmpeak = QtWidgets.QCheckBox("Umpeak")
        self.checkBox_SetUmpeak.setObjectName("checkBox_SetUmpeak")
        self.checkBox_SetUmpeak.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIppeak = QtWidgets.QCheckBox("Ippeak")
        self.checkBox_SetIppeak.setObjectName("checkBox_SetIppeak")
        self.checkBox_SetIppeak.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetImpeak = QtWidgets.QCheckBox("Impeak")
        self.checkBox_SetImpeak.setObjectName("checkBox_SetImpeak")
        self.checkBox_SetImpeak.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPppeak = QtWidgets.QCheckBox("Pppeak")
        self.checkBox_SetPppeak.setObjectName("checkBox_SetPppeak")
        self.checkBox_SetPppeak.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPmpeak = QtWidgets.QCheckBox("Pmpeak")
        self.checkBox_SetPmpeak.setObjectName("checkBox_SetPmpeak")
        self.checkBox_SetPmpeak.setStyleSheet(_CHECKBOX_STYLE)

        _pkItems = [
            self.checkBox_SetUppeak, self.checkBox_SetUmpeak,
            self.checkBox_SetIppeak, self.checkBox_SetImpeak,
            self.checkBox_SetPppeak, self.checkBox_SetPmpeak,
        ]
        for i, cb in enumerate(_pkItems):
            grpPeakLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpPeakLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpPeak)

        # ----------------------------------------------------------------
        # Section: 功率参数 (Power Parameters)
        # ----------------------------------------------------------------
        grpPower = QtWidgets.QGroupBox("功率参数")
        grpPower.setStyleSheet(_GROUP_STYLE)
        grpPowerLayout = QtWidgets.QGridLayout(grpPower)
        grpPowerLayout.setSpacing(8)

        self.checkBox_SetP = QtWidgets.QCheckBox("P")
        self.checkBox_SetP.setObjectName("checkBox_SetP")
        self.checkBox_SetP.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetS = QtWidgets.QCheckBox("S")
        self.checkBox_SetS.setObjectName("checkBox_SetS")
        self.checkBox_SetS.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetQ = QtWidgets.QCheckBox("Q")
        self.checkBox_SetQ.setObjectName("checkBox_SetQ")
        self.checkBox_SetQ.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPF = QtWidgets.QCheckBox("PF")
        self.checkBox_SetPF.setObjectName("checkBox_SetPF")
        self.checkBox_SetPF.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhi = QtWidgets.QCheckBox("Phi")
        self.checkBox_SetPhi.setObjectName("checkBox_SetPhi")
        self.checkBox_SetPhi.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPc = QtWidgets.QCheckBox("Pc")
        self.checkBox_SetPc.setObjectName("checkBox_SetPc")
        self.checkBox_SetPc.setStyleSheet(_CHECKBOX_STYLE)

        _pwItems = [
            self.checkBox_SetP, self.checkBox_SetS, self.checkBox_SetQ,
            self.checkBox_SetPF, self.checkBox_SetPhi, self.checkBox_SetPc,
        ]
        for i, cb in enumerate(_pwItems):
            grpPowerLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpPowerLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpPower)

        # ----------------------------------------------------------------
        # Section: 基波参数 (Fundamental Parameters)
        # ----------------------------------------------------------------
        grpFund = QtWidgets.QGroupBox("基波参数")
        grpFund.setStyleSheet(_GROUP_STYLE)
        grpFundLayout = QtWidgets.QGridLayout(grpFund)
        grpFundLayout.setSpacing(8)

        self.checkBox_SetUfnd = QtWidgets.QCheckBox("Ufnd")
        self.checkBox_SetUfnd.setObjectName("checkBox_SetUfnd")
        self.checkBox_SetUfnd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIfnd = QtWidgets.QCheckBox("Ifnd")
        self.checkBox_SetIfnd.setObjectName("checkBox_SetIfnd")
        self.checkBox_SetIfnd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPfnd = QtWidgets.QCheckBox("Pfnd")
        self.checkBox_SetPfnd.setObjectName("checkBox_SetPfnd")
        self.checkBox_SetPfnd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetSfnd = QtWidgets.QCheckBox("Sfnd")
        self.checkBox_SetSfnd.setObjectName("checkBox_SetSfnd")
        self.checkBox_SetSfnd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetQfnd = QtWidgets.QCheckBox("Qfnd")
        self.checkBox_SetQfnd.setObjectName("checkBox_SetQfnd")
        self.checkBox_SetQfnd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetLambdafnd = QtWidgets.QCheckBox("λfnd")
        self.checkBox_SetLambdafnd.setObjectName("checkBox_SetLambdafnd")
        self.checkBox_SetLambdafnd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhifnd = QtWidgets.QCheckBox("φfnd")
        self.checkBox_SetPhifnd.setObjectName("checkBox_SetPhifnd")
        self.checkBox_SetPhifnd.setStyleSheet(_CHECKBOX_STYLE)

        _fndItems = [
            self.checkBox_SetUfnd, self.checkBox_SetIfnd, self.checkBox_SetPfnd,
            self.checkBox_SetSfnd, self.checkBox_SetQfnd, self.checkBox_SetLambdafnd,
            self.checkBox_SetPhifnd,
        ]
        for i, cb in enumerate(_fndItems):
            grpFundLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpFundLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpFund)

        # ----------------------------------------------------------------
        # Section: 频率参数 (Frequency Parameters)
        # ----------------------------------------------------------------
        grpFreq = QtWidgets.QGroupBox("频率参数")
        grpFreq.setStyleSheet(_GROUP_STYLE)
        grpFreqLayout = QtWidgets.QGridLayout(grpFreq)
        grpFreqLayout.setSpacing(8)

        self.checkBox_SetFreqU = QtWidgets.QCheckBox("FreqU")
        self.checkBox_SetFreqU.setObjectName("checkBox_SetFreqU")
        self.checkBox_SetFreqU.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetFreqI = QtWidgets.QCheckBox("FreqI")
        self.checkBox_SetFreqI.setObjectName("checkBox_SetFreqI")
        self.checkBox_SetFreqI.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetFreq2U = QtWidgets.QCheckBox("Freq2U")
        self.checkBox_SetFreq2U.setObjectName("checkBox_SetFreq2U")
        self.checkBox_SetFreq2U.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetFreq2I = QtWidgets.QCheckBox("Freq2I")
        self.checkBox_SetFreq2I.setObjectName("checkBox_SetFreq2I")
        self.checkBox_SetFreq2I.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetFreqPLL1 = QtWidgets.QCheckBox("FreqPLL1")
        self.checkBox_SetFreqPLL1.setObjectName("checkBox_SetFreqPLL1")
        self.checkBox_SetFreqPLL1.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetFreqPLL2 = QtWidgets.QCheckBox("FreqPLL2")
        self.checkBox_SetFreqPLL2.setObjectName("checkBox_SetFreqPLL2")
        self.checkBox_SetFreqPLL2.setStyleSheet(_CHECKBOX_STYLE)

        _freqItems = [
            self.checkBox_SetFreqU, self.checkBox_SetFreqI,
            self.checkBox_SetFreq2U, self.checkBox_SetFreq2I,
            self.checkBox_SetFreqPLL1, self.checkBox_SetFreqPLL2,
        ]
        for i, cb in enumerate(_freqItems):
            grpFreqLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpFreqLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpFreq)

        # ----------------------------------------------------------------
        # Section: 时间/功率方向 (Time / Power Direction)
        # ----------------------------------------------------------------
        grpTimeDir = QtWidgets.QGroupBox("时间 / 功率方向")
        grpTimeDir.setStyleSheet(_GROUP_STYLE)
        grpTimeDirLayout = QtWidgets.QGridLayout(grpTimeDir)
        grpTimeDirLayout.setSpacing(8)

        self.checkBox_SetTime = QtWidgets.QCheckBox("Time")
        self.checkBox_SetTime.setObjectName("checkBox_SetTime")
        self.checkBox_SetTime.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetWP = QtWidgets.QCheckBox("WP")
        self.checkBox_SetWP.setObjectName("checkBox_SetWP")
        self.checkBox_SetWP.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetWPPlus = QtWidgets.QCheckBox("WPp")
        self.checkBox_SetWPPlus.setObjectName("checkBox_SetWPPlus")
        self.checkBox_SetWPPlus.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetWPMinus = QtWidgets.QCheckBox("WPm")
        self.checkBox_SetWPMinus.setObjectName("checkBox_SetWPMinus")
        self.checkBox_SetWPMinus.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_Setq = QtWidgets.QCheckBox("q")
        self.checkBox_Setq.setObjectName("checkBox_Setq")
        self.checkBox_Setq.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetqPlus = QtWidgets.QCheckBox("qp")
        self.checkBox_SetqPlus.setObjectName("checkBox_SetqPlus")
        self.checkBox_SetqPlus.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetqMinus = QtWidgets.QCheckBox("qm")
        self.checkBox_SetqMinus.setObjectName("checkBox_SetqMinus")
        self.checkBox_SetqMinus.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetWS = QtWidgets.QCheckBox("WS")
        self.checkBox_SetWS.setObjectName("checkBox_SetWS")
        self.checkBox_SetWS.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetWQ = QtWidgets.QCheckBox("WQ")
        self.checkBox_SetWQ.setObjectName("checkBox_SetWQ")
        self.checkBox_SetWQ.setStyleSheet(_CHECKBOX_STYLE)

        _tdItems = [
            self.checkBox_SetTime, self.checkBox_SetWP, self.checkBox_SetWPPlus,
            self.checkBox_SetWPMinus, self.checkBox_Setq, self.checkBox_SetqPlus,
            self.checkBox_SetqMinus, self.checkBox_SetWS, self.checkBox_SetWQ,
        ]
        for i, cb in enumerate(_tdItems):
            grpTimeDirLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpTimeDirLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpTimeDir)

        # ----------------------------------------------------------------
        # Section: 效率 (Efficiency)
        # ----------------------------------------------------------------
        grpEta = QtWidgets.QGroupBox("效率")
        grpEta.setStyleSheet(_GROUP_STYLE)
        grpEtaLayout = QtWidgets.QGridLayout(grpEta)
        grpEtaLayout.setSpacing(8)

        self.checkBox_SetEta1 = QtWidgets.QCheckBox("η1")
        self.checkBox_SetEta1.setObjectName("checkBox_SetEta1")
        self.checkBox_SetEta1.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEta2 = QtWidgets.QCheckBox("η2")
        self.checkBox_SetEta2.setObjectName("checkBox_SetEta2")
        self.checkBox_SetEta2.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEta3 = QtWidgets.QCheckBox("η3")
        self.checkBox_SetEta3.setObjectName("checkBox_SetEta3")
        self.checkBox_SetEta3.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEta4 = QtWidgets.QCheckBox("η4")
        self.checkBox_SetEta4.setObjectName("checkBox_SetEta4")
        self.checkBox_SetEta4.setStyleSheet(_CHECKBOX_STYLE)

        for i, cb in enumerate([
            self.checkBox_SetEta1, self.checkBox_SetEta2,
            self.checkBox_SetEta3, self.checkBox_SetEta4
        ]):
            grpEtaLayout.addWidget(cb, 0, i)
        grpEtaLayout.setColumnStretch(4, 1)
        contentLayout.addWidget(grpEta)

        # ----------------------------------------------------------------
        # Section: Event
        # ----------------------------------------------------------------
        grpEvent = QtWidgets.QGroupBox("Event")
        grpEvent.setStyleSheet(_GROUP_STYLE)
        grpEventLayout = QtWidgets.QGridLayout(grpEvent)
        grpEventLayout.setSpacing(8)

        self.checkBox_SetEvent1 = QtWidgets.QCheckBox("Event1")
        self.checkBox_SetEvent1.setObjectName("checkBox_SetEvent1")
        self.checkBox_SetEvent1.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEvent2 = QtWidgets.QCheckBox("Event2")
        self.checkBox_SetEvent2.setObjectName("checkBox_SetEvent2")
        self.checkBox_SetEvent2.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEvent3 = QtWidgets.QCheckBox("Event3")
        self.checkBox_SetEvent3.setObjectName("checkBox_SetEvent3")
        self.checkBox_SetEvent3.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEvent4 = QtWidgets.QCheckBox("Event4")
        self.checkBox_SetEvent4.setObjectName("checkBox_SetEvent4")
        self.checkBox_SetEvent4.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEvent5 = QtWidgets.QCheckBox("Event5")
        self.checkBox_SetEvent5.setObjectName("checkBox_SetEvent5")
        self.checkBox_SetEvent5.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEvent6 = QtWidgets.QCheckBox("Event6")
        self.checkBox_SetEvent6.setObjectName("checkBox_SetEvent6")
        self.checkBox_SetEvent6.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEvent7 = QtWidgets.QCheckBox("Event7")
        self.checkBox_SetEvent7.setObjectName("checkBox_SetEvent7")
        self.checkBox_SetEvent7.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetEvent8 = QtWidgets.QCheckBox("Event8")
        self.checkBox_SetEvent8.setObjectName("checkBox_SetEvent8")
        self.checkBox_SetEvent8.setStyleSheet(_CHECKBOX_STYLE)

        _evItems = [
            self.checkBox_SetEvent1, self.checkBox_SetEvent2,
            self.checkBox_SetEvent3, self.checkBox_SetEvent4,
            self.checkBox_SetEvent5, self.checkBox_SetEvent6,
            self.checkBox_SetEvent7, self.checkBox_SetEvent8,
        ]
        for i, cb in enumerate(_evItems):
            grpEventLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpEventLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpEvent)

        # ----------------------------------------------------------------
        # Section: 谐波基本量 (Harmonic Basic)
        # ----------------------------------------------------------------
        grpHarmBasic = QtWidgets.QGroupBox("谐波基本量")
        grpHarmBasic.setStyleSheet(_GROUP_STYLE)
        grpHarmBasicLayout = QtWidgets.QGridLayout(grpHarmBasic)
        grpHarmBasicLayout.setSpacing(8)

        label_90 = QtWidgets.QLabel("开始")
        label_90.setObjectName("label_90")
        label_90.setStyleSheet(_LABEL_STYLE)
        self.textEdit_SetStart = QtWidgets.QTextEdit()
        self.textEdit_SetStart.setObjectName("textEdit_SetStart")
        self.textEdit_SetStart.setPlaceholderText("")
        self.textEdit_SetStart.setMaximumHeight(32)
        self.textEdit_SetStart.setStyleSheet(_TEXTEDIT_STYLE)

        label_91 = QtWidgets.QLabel("结束")
        label_91.setObjectName("label_91")
        label_91.setStyleSheet(_LABEL_STYLE)
        self.textEdit_SetStop = QtWidgets.QTextEdit()
        self.textEdit_SetStop.setObjectName("textEdit_SetStop")
        self.textEdit_SetStop.setPlaceholderText("")
        self.textEdit_SetStop.setMaximumHeight(32)
        self.textEdit_SetStop.setStyleSheet(_TEXTEDIT_STYLE)

        grpHarmBasicLayout.addWidget(label_90, 0, 0)
        grpHarmBasicLayout.addWidget(self.textEdit_SetStart, 0, 1)
        grpHarmBasicLayout.addWidget(label_91, 0, 2)
        grpHarmBasicLayout.addWidget(self.textEdit_SetStop, 0, 3)
        grpHarmBasicLayout.setColumnStretch(4, 1)

        # Row 1: harmonic element checkboxes
        self.checkBox_SetUk = QtWidgets.QCheckBox("U(k)")
        self.checkBox_SetUk.setObjectName("checkBox_SetUk")
        self.checkBox_SetUk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIk = QtWidgets.QCheckBox("I(k)")
        self.checkBox_SetIk.setObjectName("checkBox_SetIk")
        self.checkBox_SetIk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPk = QtWidgets.QCheckBox("P(k)")
        self.checkBox_SetPk.setObjectName("checkBox_SetPk")
        self.checkBox_SetPk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetSk = QtWidgets.QCheckBox("S(k)")
        self.checkBox_SetSk.setObjectName("checkBox_SetSk")
        self.checkBox_SetSk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetQk = QtWidgets.QCheckBox("Q(k)")
        self.checkBox_SetQk.setObjectName("checkBox_SetQk")
        self.checkBox_SetQk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPFk = QtWidgets.QCheckBox("PF(k)")
        self.checkBox_SetPFk.setObjectName("checkBox_SetPFk")
        self.checkBox_SetPFk.setStyleSheet(_CHECKBOX_STYLE)

        _hbRow1 = [
            self.checkBox_SetUk, self.checkBox_SetIk, self.checkBox_SetPk,
            self.checkBox_SetSk, self.checkBox_SetQk, self.checkBox_SetPFk,
        ]
        for i, cb in enumerate(_hbRow1):
            grpHarmBasicLayout.addWidget(cb, 1, i)
        contentLayout.addWidget(grpHarmBasic)

        # ----------------------------------------------------------------
        # Section: 谐波相位 (Harmonic Phase)
        # ----------------------------------------------------------------
        grpHarmPhase = QtWidgets.QGroupBox("谐波相位")
        grpHarmPhase.setStyleSheet(_GROUP_STYLE)
        grpHarmPhaseLayout = QtWidgets.QGridLayout(grpHarmPhase)
        grpHarmPhaseLayout.setSpacing(8)

        self.checkBox_SetPhik = QtWidgets.QCheckBox("Phi(k)")
        self.checkBox_SetPhik.setObjectName("checkBox_SetPhik")
        self.checkBox_SetPhik.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhiUk = QtWidgets.QCheckBox("PhiU(k)")
        self.checkBox_SetPhiUk.setObjectName("checkBox_SetPhiUk")
        self.checkBox_SetPhiUk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhiIk = QtWidgets.QCheckBox("PhiI(k)")
        self.checkBox_SetPhiIk.setObjectName("checkBox_SetPhiIk")
        self.checkBox_SetPhiIk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetUhdfk = QtWidgets.QCheckBox("Uhdf(k)")
        self.checkBox_SetUhdfk.setObjectName("checkBox_SetUhdfk")
        self.checkBox_SetUhdfk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIhdfk = QtWidgets.QCheckBox("Ihdf(k)")
        self.checkBox_SetIhdfk.setObjectName("checkBox_SetIhdfk")
        self.checkBox_SetIhdfk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhdfk = QtWidgets.QCheckBox("Phdf(k)")
        self.checkBox_SetPhdfk.setObjectName("checkBox_SetPhdfk")
        self.checkBox_SetPhdfk.setStyleSheet(_CHECKBOX_STYLE)

        _hpItems = [
            self.checkBox_SetPhik, self.checkBox_SetPhiUk, self.checkBox_SetPhiIk,
            self.checkBox_SetUhdfk, self.checkBox_SetIhdfk, self.checkBox_SetPhdfk,
        ]
        for i, cb in enumerate(_hpItems):
            grpHarmPhaseLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpHarmPhaseLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpHarmPhase)

        # ----------------------------------------------------------------
        # Section: 谐波阻抗 (Harmonic Impedance)
        # ----------------------------------------------------------------
        grpHarmImp = QtWidgets.QGroupBox("谐波阻抗")
        grpHarmImp.setStyleSheet(_GROUP_STYLE)
        grpHarmImpLayout = QtWidgets.QGridLayout(grpHarmImp)
        grpHarmImpLayout.setSpacing(8)

        self.checkBox_SetZk = QtWidgets.QCheckBox("Z(k)")
        self.checkBox_SetZk.setObjectName("checkBox_SetZk")
        self.checkBox_SetZk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetRsk = QtWidgets.QCheckBox("Rs(k)")
        self.checkBox_SetRsk.setObjectName("checkBox_SetRsk")
        self.checkBox_SetRsk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetXsk = QtWidgets.QCheckBox("Xs(k)")
        self.checkBox_SetXsk.setObjectName("checkBox_SetXsk")
        self.checkBox_SetXsk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetRpk = QtWidgets.QCheckBox("Rp(k)")
        self.checkBox_SetRpk.setObjectName("checkBox_SetRpk")
        self.checkBox_SetRpk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetXpk = QtWidgets.QCheckBox("Xp(k)")
        self.checkBox_SetXpk.setObjectName("checkBox_SetXpk")
        self.checkBox_SetXpk.setStyleSheet(_CHECKBOX_STYLE)

        _hiItems = [
            self.checkBox_SetZk, self.checkBox_SetRsk, self.checkBox_SetXsk,
            self.checkBox_SetRpk, self.checkBox_SetXpk,
        ]
        for i, cb in enumerate(_hiItems):
            grpHarmImpLayout.addWidget(cb, 0, i)
        grpHarmImpLayout.setColumnStretch(5, 1)
        contentLayout.addWidget(grpHarmImp)

        # ----------------------------------------------------------------
        # Section: THD / TIF / K-factor
        # ----------------------------------------------------------------
        grpThdTif = QtWidgets.QGroupBox("THD / TIF / K-factor")
        grpThdTif.setStyleSheet(_GROUP_STYLE)
        grpThdTifLayout = QtWidgets.QGridLayout(grpThdTif)
        grpThdTifLayout.setSpacing(8)

        self.checkBox_SetUthd = QtWidgets.QCheckBox("Uthd")
        self.checkBox_SetUthd.setObjectName("checkBox_SetUthd")
        self.checkBox_SetUthd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIthd = QtWidgets.QCheckBox("Ithd")
        self.checkBox_SetIthd.setObjectName("checkBox_SetIthd")
        self.checkBox_SetIthd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPthd = QtWidgets.QCheckBox("Pthd")
        self.checkBox_SetPthd.setObjectName("checkBox_SetPthd")
        self.checkBox_SetPthd.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetUthf = QtWidgets.QCheckBox("Uthf")
        self.checkBox_SetUthf.setObjectName("checkBox_SetUthf")
        self.checkBox_SetUthf.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetIthf = QtWidgets.QCheckBox("Ithf")
        self.checkBox_SetIthf.setObjectName("checkBox_SetIthf")
        self.checkBox_SetIthf.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetUtif = QtWidgets.QCheckBox("Utif")
        self.checkBox_SetUtif.setObjectName("checkBox_SetUtif")
        self.checkBox_SetUtif.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetItif = QtWidgets.QCheckBox("Itif")
        self.checkBox_SetItif.setObjectName("checkBox_SetItif")
        self.checkBox_SetItif.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_Sethvf = QtWidgets.QCheckBox("hvf")
        self.checkBox_Sethvf.setObjectName("checkBox_Sethvf")
        self.checkBox_Sethvf.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_Sethcf = QtWidgets.QCheckBox("hcf")
        self.checkBox_Sethcf.setObjectName("checkBox_Sethcf")
        self.checkBox_Sethcf.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetK_factor = QtWidgets.QCheckBox("K-factor")
        self.checkBox_SetK_factor.setObjectName("checkBox_SetK_factor")
        self.checkBox_SetK_factor.setStyleSheet(_CHECKBOX_STYLE)

        _thdItems = [
            self.checkBox_SetUthd, self.checkBox_SetIthd, self.checkBox_SetPthd,
            self.checkBox_SetUthf, self.checkBox_SetIthf,
            self.checkBox_SetUtif, self.checkBox_SetItif,
            self.checkBox_Sethvf, self.checkBox_Sethcf,
            self.checkBox_SetK_factor,
        ]
        for i, cb in enumerate(_thdItems):
            grpThdTifLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpThdTifLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpThdTif)

        # ----------------------------------------------------------------
        # Section: 相位差 (Phase Differences)
        # ----------------------------------------------------------------
        grpPhaseDiff = QtWidgets.QGroupBox("相位差 (UI 相关)")
        grpPhaseDiff.setStyleSheet(_GROUP_STYLE)
        grpPhaseDiffLayout = QtWidgets.QGridLayout(grpPhaseDiff)
        grpPhaseDiffLayout.setSpacing(8)

        self.checkBox_SetPhiUi_Uj = QtWidgets.QCheckBox("φUi-Uj")
        self.checkBox_SetPhiUi_Uj.setObjectName("checkBox_SetPhiUi_Uj")
        self.checkBox_SetPhiUi_Uj.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhiUi_Uk = QtWidgets.QCheckBox("φUi-Uk")
        self.checkBox_SetPhiUi_Uk.setObjectName("checkBox_SetPhiUi_Uk")
        self.checkBox_SetPhiUi_Uk.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhiUi_Ii = QtWidgets.QCheckBox("φUi-Ii")
        self.checkBox_SetPhiUi_Ii.setObjectName("checkBox_SetPhiUi_Ii")
        self.checkBox_SetPhiUi_Ii.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhiUi_Ij = QtWidgets.QCheckBox("φUi-Ij")
        self.checkBox_SetPhiUi_Ij.setObjectName("checkBox_SetPhiUi_Ij")
        self.checkBox_SetPhiUi_Ij.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetPhiUi_Ik = QtWidgets.QCheckBox("φUi-Ik")
        self.checkBox_SetPhiUi_Ik.setObjectName("checkBox_SetPhiUi_Ik")
        self.checkBox_SetPhiUi_Ik.setStyleSheet(_CHECKBOX_STYLE)

        _pdItems = [
            self.checkBox_SetPhiUi_Uj, self.checkBox_SetPhiUi_Uk,
            self.checkBox_SetPhiUi_Ii, self.checkBox_SetPhiUi_Ij,
            self.checkBox_SetPhiUi_Ik,
        ]
        for i, cb in enumerate(_pdItems):
            grpPhaseDiffLayout.addWidget(cb, 0, i)
        grpPhaseDiffLayout.setColumnStretch(5, 1)
        contentLayout.addWidget(grpPhaseDiff)

        # ----------------------------------------------------------------
        # Section: 差值 (Delta Parameters)
        # ----------------------------------------------------------------
        grpDelta = QtWidgets.QGroupBox("差值")
        grpDelta.setStyleSheet(_GROUP_STYLE)
        grpDeltaLayout = QtWidgets.QGridLayout(grpDelta)
        grpDeltaLayout.setSpacing(8)

        self.checkBox_SetDeltaU1 = QtWidgets.QCheckBox("ΔU1")
        self.checkBox_SetDeltaU1.setObjectName("checkBox_SetDeltaU1")
        self.checkBox_SetDeltaU1.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetDeltaU2 = QtWidgets.QCheckBox("ΔU2")
        self.checkBox_SetDeltaU2.setObjectName("checkBox_SetDeltaU2")
        self.checkBox_SetDeltaU2.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetDeltaU3 = QtWidgets.QCheckBox("ΔU3")
        self.checkBox_SetDeltaU3.setObjectName("checkBox_SetDeltaU3")
        self.checkBox_SetDeltaU3.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetDeltaUSigma = QtWidgets.QCheckBox("ΔUΣ")
        self.checkBox_SetDeltaUSigma.setObjectName("checkBox_SetDeltaUSigma")
        self.checkBox_SetDeltaUSigma.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetDeltaI = QtWidgets.QCheckBox("ΔI")
        self.checkBox_SetDeltaI.setObjectName("checkBox_SetDeltaI")
        self.checkBox_SetDeltaI.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetDeltaP1 = QtWidgets.QCheckBox("ΔP1")
        self.checkBox_SetDeltaP1.setObjectName("checkBox_SetDeltaP1")
        self.checkBox_SetDeltaP1.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetDeltaP2 = QtWidgets.QCheckBox("ΔP2")
        self.checkBox_SetDeltaP2.setObjectName("checkBox_SetDeltaP2")
        self.checkBox_SetDeltaP2.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetDeltaP3 = QtWidgets.QCheckBox("ΔP3")
        self.checkBox_SetDeltaP3.setObjectName("checkBox_SetDeltaP3")
        self.checkBox_SetDeltaP3.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetDeltaPSigma = QtWidgets.QCheckBox("ΔPΣ")
        self.checkBox_SetDeltaPSigma.setObjectName("checkBox_SetDeltaPSigma")
        self.checkBox_SetDeltaPSigma.setStyleSheet(_CHECKBOX_STYLE)

        _dtItems = [
            self.checkBox_SetDeltaU1, self.checkBox_SetDeltaU2,
            self.checkBox_SetDeltaU3, self.checkBox_SetDeltaUSigma,
            self.checkBox_SetDeltaI,
            self.checkBox_SetDeltaP1, self.checkBox_SetDeltaP2,
            self.checkBox_SetDeltaP3, self.checkBox_SetDeltaPSigma,
        ]
        for i, cb in enumerate(_dtItems):
            grpDeltaLayout.addWidget(cb, i // cols, i % cols)
        for c in range(cols):
            grpDeltaLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpDelta)

        # ----------------------------------------------------------------
        # Section: 时间戳 (Timestamp)
        # ----------------------------------------------------------------
        grpTimestamp = QtWidgets.QGroupBox("时间戳")
        grpTimestamp.setStyleSheet(_GROUP_STYLE)
        grpTimestampLayout = QtWidgets.QGridLayout(grpTimestamp)
        grpTimestampLayout.setSpacing(8)

        self.checkBox_SetTSDate = QtWidgets.QCheckBox("TSDate")
        self.checkBox_SetTSDate.setObjectName("checkBox_SetTSDate")
        self.checkBox_SetTSDate.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetTSTime = QtWidgets.QCheckBox("TSTime")
        self.checkBox_SetTSTime.setObjectName("checkBox_SetTSTime")
        self.checkBox_SetTSTime.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetTSSubsec = QtWidgets.QCheckBox("TSSubsec")
        self.checkBox_SetTSSubsec.setObjectName("checkBox_SetTSSubsec")
        self.checkBox_SetTSSubsec.setStyleSheet(_CHECKBOX_STYLE)

        for i, cb in enumerate([
            self.checkBox_SetTSDate, self.checkBox_SetTSTime, self.checkBox_SetTSSubsec
        ]):
            grpTimestampLayout.addWidget(cb, 0, i)
        grpTimestampLayout.setColumnStretch(3, 1)
        contentLayout.addWidget(grpTimestamp)

        # ----------------------------------------------------------------
        # Section: 功能选择 F01-F20
        # ----------------------------------------------------------------
        grpFunc = QtWidgets.QGroupBox("功能选择 (F01 - F20)")
        grpFunc.setStyleSheet(_GROUP_STYLE)
        grpFuncLayout = QtWidgets.QGridLayout(grpFunc)
        grpFuncLayout.setSpacing(6)

        self.checkBox_SetF01 = QtWidgets.QCheckBox("F01")
        self.checkBox_SetF01.setObjectName("checkBox_SetF01")
        self.checkBox_SetF01.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF02 = QtWidgets.QCheckBox("F02")
        self.checkBox_SetF02.setObjectName("checkBox_SetF02")
        self.checkBox_SetF02.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF03 = QtWidgets.QCheckBox("F03")
        self.checkBox_SetF03.setObjectName("checkBox_SetF03")
        self.checkBox_SetF03.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF04 = QtWidgets.QCheckBox("F04")
        self.checkBox_SetF04.setObjectName("checkBox_SetF04")
        self.checkBox_SetF04.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF05 = QtWidgets.QCheckBox("F05")
        self.checkBox_SetF05.setObjectName("checkBox_SetF05")
        self.checkBox_SetF05.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF06 = QtWidgets.QCheckBox("F06")
        self.checkBox_SetF06.setObjectName("checkBox_SetF06")
        self.checkBox_SetF06.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF07 = QtWidgets.QCheckBox("F07")
        self.checkBox_SetF07.setObjectName("checkBox_SetF07")
        self.checkBox_SetF07.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF08 = QtWidgets.QCheckBox("F08")
        self.checkBox_SetF08.setObjectName("checkBox_SetF08")
        self.checkBox_SetF08.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF09 = QtWidgets.QCheckBox("F09")
        self.checkBox_SetF09.setObjectName("checkBox_SetF09")
        self.checkBox_SetF09.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF10 = QtWidgets.QCheckBox("F10")
        self.checkBox_SetF10.setObjectName("checkBox_SetF10")
        self.checkBox_SetF10.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF11 = QtWidgets.QCheckBox("F11")
        self.checkBox_SetF11.setObjectName("checkBox_SetF11")
        self.checkBox_SetF11.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF12 = QtWidgets.QCheckBox("F12")
        self.checkBox_SetF12.setObjectName("checkBox_SetF12")
        self.checkBox_SetF12.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF13 = QtWidgets.QCheckBox("F13")
        self.checkBox_SetF13.setObjectName("checkBox_SetF13")
        self.checkBox_SetF13.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF14 = QtWidgets.QCheckBox("F14")
        self.checkBox_SetF14.setObjectName("checkBox_SetF14")
        self.checkBox_SetF14.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF15 = QtWidgets.QCheckBox("F15")
        self.checkBox_SetF15.setObjectName("checkBox_SetF15")
        self.checkBox_SetF15.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF16 = QtWidgets.QCheckBox("F16")
        self.checkBox_SetF16.setObjectName("checkBox_SetF16")
        self.checkBox_SetF16.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF17 = QtWidgets.QCheckBox("F17")
        self.checkBox_SetF17.setObjectName("checkBox_SetF17")
        self.checkBox_SetF17.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF18 = QtWidgets.QCheckBox("F18")
        self.checkBox_SetF18.setObjectName("checkBox_SetF18")
        self.checkBox_SetF18.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF19 = QtWidgets.QCheckBox("F19")
        self.checkBox_SetF19.setObjectName("checkBox_SetF19")
        self.checkBox_SetF19.setStyleSheet(_CHECKBOX_STYLE)
        self.checkBox_SetF20 = QtWidgets.QCheckBox("F20")
        self.checkBox_SetF20.setObjectName("checkBox_SetF20")
        self.checkBox_SetF20.setStyleSheet(_CHECKBOX_STYLE)

        _funcItems = [
            self.checkBox_SetF01, self.checkBox_SetF02, self.checkBox_SetF03,
            self.checkBox_SetF04, self.checkBox_SetF05, self.checkBox_SetF06,
            self.checkBox_SetF07, self.checkBox_SetF08, self.checkBox_SetF09,
            self.checkBox_SetF10, self.checkBox_SetF11, self.checkBox_SetF12,
            self.checkBox_SetF13, self.checkBox_SetF14, self.checkBox_SetF15,
            self.checkBox_SetF16, self.checkBox_SetF17, self.checkBox_SetF18,
            self.checkBox_SetF19, self.checkBox_SetF20,
        ]
        funcCols = 10
        for i, cb in enumerate(_funcItems):
            grpFuncLayout.addWidget(cb, i // funcCols, i % funcCols)
        for c in range(funcCols):
            grpFuncLayout.setColumnStretch(c, 1)
        contentLayout.addWidget(grpFunc)

        # -- stretch at the bottom --
        contentLayout.addStretch(1)

        scrollArea.setWidget(contentWidget)
        mainLayout.addWidget(scrollArea, 1)

        # ================================================================
        # Log box (150 px)
        # ================================================================
        logWidget = QtWidgets.QWidget()
        # ================================================================
        # Hidden pushButton_Send (backward compatibility)
        # ================================================================
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thai_WT5000)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thai_WT5000)

    def retranslateUi(self, Dialog_thai_WT5000):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thai_WT5000.setWindowTitle(_translate("Dialog_thai_WT5000", "WT5000参数配置"))
        self.pushButton_Confirm.setText(_translate("Dialog_thai_WT5000", "确认"))
