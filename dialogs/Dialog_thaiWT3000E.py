# -*- coding: utf-8 -*-
"""
WT3000E Parameter Configuration Dialog - Modern UI
All widget objectNames are preserved for backward compatibility with SCPITestWave.py.
"""

from PyQt5 import QtCore, QtGui, QtWidgets


# ── Shared style constants ──────────────────────────────────────────────────
_COMBO_STYLE = (
    "QComboBox { border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px 8px; "
    "font-size: 12px; background: white; min-height: 24px; }"
    "QComboBox::drop-down { border: none; width: 20px; }"
    "QComboBox::down-arrow { image: none; border-left: 5px solid transparent; "
    "border-right: 5px solid transparent; border-top: 6px solid #64748b; margin-right: 6px; }"
    "QComboBox QAbstractItemView { border: 1px solid #cbd5e1; selection-background-color: #ede9fe; "
    "selection-color: #1e1b4b; }"
)

_TEXTEDIT_STYLE = (
    "QTextEdit { border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px; "
    "font-size: 12px; background: white; }"
)

_GROUPBOX_STYLE = (
    "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; "
    "font-weight: bold; font-size: 13px; margin-top: 6px; }"
    "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }"
)

_LABEL_STYLE = "font-size: 12px; color: #475569;"

_CHECKBOX_STYLE = (
    "QCheckBox { spacing: 6px; font-size: 12px; }"
    "QCheckBox::indicator { width: 16px; height: 16px; border: 2px solid #cbd5e1; border-radius: 3px; }"
    "QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
)

_GRID_STYLE = "QGridLayout { spacing: 6px; }"


class Ui_Dialog_thai_WT3000E(object):
    """WT3000E parameter configuration UI with modern styling."""

    def setupUi(self, Dialog_thai_WT3000E):
        Dialog_thai_WT3000E.setObjectName("Dialog_thai_WT3000E")
        Dialog_thai_WT3000E.resize(1200, 900)
        Dialog_thai_WT3000E.setMinimumSize(QtCore.QSize(1000, 700))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_thai_WT3000E.setWindowIcon(icon)

        # ── Main layout ─────────────────────────────────────────────────────
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thai_WT3000E)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ── Top bar (56px) ──────────────────────────────────────────────────
        topBar = QtWidgets.QWidget()
        topBar.setFixedHeight(56)
        topBar.setStyleSheet(
            "QWidget { background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; }"
        )
        topLayout = QtWidgets.QHBoxLayout(topBar)
        topLayout.setContentsMargins(16, 8, 16, 8)
        topLayout.setSpacing(10)

        # -- pushButton_TestAppend (purple) --
        self.pushButton_TestAppend = QtWidgets.QPushButton(topBar)
        self.pushButton_TestAppend.setObjectName("pushButton_TestAppend")
        self.pushButton_TestAppend.setMinimumSize(130, 36)
        self.pushButton_TestAppend.setStyleSheet(
            "QPushButton { background-color: #8b5cf6; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; padding: 0 16px; }"
            "QPushButton:hover { background-color: #7c3aed; }"
            "QPushButton:pressed { background-color: #6d28d9; }"
        )
        topLayout.addWidget(self.pushButton_TestAppend)

        # -- pushButton_ReadSettingFile (blue) --
        self.pushButton_ReadSettingFile = QtWidgets.QPushButton(topBar)
        self.pushButton_ReadSettingFile.setObjectName("pushButton_ReadSettingFile")
        self.pushButton_ReadSettingFile.setMinimumSize(130, 36)
        self.pushButton_ReadSettingFile.setStyleSheet(
            "QPushButton { background-color: #3b82f6; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; padding: 0 16px; }"
            "QPushButton:hover { background-color: #2563eb; }"
            "QPushButton:pressed { background-color: #1d4ed8; }"
        )
        topLayout.addWidget(self.pushButton_ReadSettingFile)

        # -- pushButton_SaveSettingFile (green) --
        self.pushButton_SaveSettingFile = QtWidgets.QPushButton(topBar)
        self.pushButton_SaveSettingFile.setObjectName("pushButton_SaveSettingFile")
        self.pushButton_SaveSettingFile.setMinimumSize(130, 36)
        self.pushButton_SaveSettingFile.setStyleSheet(
            "QPushButton { background-color: #10b981; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; padding: 0 16px; }"
            "QPushButton:hover { background-color: #059669; }"
            "QPushButton:pressed { background-color: #047857; }"
        )
        topLayout.addWidget(self.pushButton_SaveSettingFile)

        # -- Separator line --
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("color: #cbd5e1;")
        separator.setFixedHeight(36)
        topLayout.addWidget(separator)

        # -- Title --
        titleLabel = QtWidgets.QLabel("WT3000 参数配置")
        titleLabel.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1e293b; background: transparent;"
        )
        topLayout.addWidget(titleLabel)

        topLayout.addStretch(1)

        # -- pushButton_Confirm (in top bar, right side) --
        self.pushButton_Confirm = QtWidgets.QPushButton(topBar)
        self.pushButton_Confirm.setObjectName("pushButton_Confirm")
        self.pushButton_Confirm.setMinimumSize(120, 36)
        self.pushButton_Confirm.setStyleSheet(
            "QPushButton { background-color: #0ea5e9; color: white; border: none; "
            "border-radius: 6px; font-size: 13px; font-weight: bold; padding: 0 20px; }"
            "QPushButton:hover { background-color: #0284c7; }"
            "QPushButton:pressed { background-color: #0369a1; }"
        )
        topLayout.addWidget(self.pushButton_Confirm)

        mainLayout.addWidget(topBar)

        # ── Scrollable content area ─────────────────────────────────────────
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet(
            "QScrollArea { border: none; background-color: white; }"
            "QScrollBar:vertical { background: #f1f5f9; width: 10px; }"
            "QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 5px; min-height: 30px; }"
            "QScrollBar::handle:vertical:hover { background: #94a3b8; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )
        contentWidget = QtWidgets.QWidget()
        contentWidget.setStyleSheet("background-color: white;")
        contentLayout = QtWidgets.QVBoxLayout(contentWidget)
        contentLayout.setContentsMargins(20, 20, 20, 20)
        contentLayout.setSpacing(16)

        # ══════════════════════════════════════════════════════════════════════
        # Section 1: Basic Settings (Wiring / Update Rate / Project)
        # ══════════════════════════════════════════════════════════════════════
        basicGroup = QtWidgets.QGroupBox("基本设置")
        basicGroup.setStyleSheet(_GROUPBOX_STYLE)
        basicLayout = QtWidgets.QHBoxLayout(basicGroup)
        basicLayout.setSpacing(16)
        basicLayout.setContentsMargins(12, 12, 12, 12)

        # -- groupBox_3: Wiring (接线方式) --
        self.groupBox_3 = QtWidgets.QGroupBox(basicGroup)
        self.groupBox_3.setObjectName("groupBox_3")
        wiringLayout = QtWidgets.QGridLayout(self.groupBox_3)
        wiringLayout.setSpacing(8)
        wiringLayout.setContentsMargins(12, 16, 12, 12)

        # SigmaA row
        self.label_38 = QtWidgets.QLabel(self.groupBox_3)
        self.label_38.setObjectName("label_38")
        self.label_38.setStyleSheet(_LABEL_STYLE)
        wiringLayout.addWidget(self.label_38, 0, 0)

        self.comboBox_SigmA1 = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_SigmA1.setObjectName("comboBox_SigmA1")
        self.comboBox_SigmA1.setStyleSheet(_COMBO_STYLE)
        for txt in ["---", "1P3W", "3P3W", "3P4W", "3V3A"]:
            self.comboBox_SigmA1.addItem(txt)
        wiringLayout.addWidget(self.comboBox_SigmA1, 0, 1)

        self.comboBox_SigmA2 = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_SigmA2.setObjectName("comboBox_SigmA2")
        self.comboBox_SigmA2.setStyleSheet(_COMBO_STYLE)
        for txt in ["Element1", "Element2", "Element3", "Element4"]:
            self.comboBox_SigmA2.addItem(txt)
        wiringLayout.addWidget(self.comboBox_SigmA2, 0, 2)

        # SigmaB row
        self.label_41 = QtWidgets.QLabel(self.groupBox_3)
        self.label_41.setObjectName("label_41")
        self.label_41.setStyleSheet(_LABEL_STYLE)
        wiringLayout.addWidget(self.label_41, 1, 0)

        self.comboBox_SigmB1 = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_SigmB1.setObjectName("comboBox_SigmB1")
        self.comboBox_SigmB1.setStyleSheet(_COMBO_STYLE)
        for txt in ["---", "1P3W", "3P3W", "3P4W", "3V3A"]:
            self.comboBox_SigmB1.addItem(txt)
        wiringLayout.addWidget(self.comboBox_SigmB1, 1, 1)

        self.comboBox_SigmB2 = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_SigmB2.setObjectName("comboBox_SigmB2")
        self.comboBox_SigmB2.setStyleSheet(_COMBO_STYLE)
        for txt in ["Element1", "Element2", "Element3", "Element4"]:
            self.comboBox_SigmB2.addItem(txt)
        wiringLayout.addWidget(self.comboBox_SigmB2, 1, 2)

        # UnitSet row
        self.label_43 = QtWidgets.QLabel(self.groupBox_3)
        self.label_43.setObjectName("label_43")
        self.label_43.setStyleSheet(_LABEL_STYLE)
        wiringLayout.addWidget(self.label_43, 2, 0)

        self.comboBox_UnitSet = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_UnitSet.setObjectName("comboBox_UnitSet")
        self.comboBox_UnitSet.setStyleSheet(_COMBO_STYLE)
        for txt in ["OFF", "ON"]:
            self.comboBox_UnitSet.addItem(txt)
        wiringLayout.addWidget(self.comboBox_UnitSet, 2, 1)

        # WiringComp row
        self.label_42 = QtWidgets.QLabel(self.groupBox_3)
        self.label_42.setObjectName("label_42")
        self.label_42.setStyleSheet(_LABEL_STYLE)
        wiringLayout.addWidget(self.label_42, 3, 0)

        self.comboBox_WiringCom = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_WiringCom.setObjectName("comboBox_WiringCom")
        self.comboBox_WiringCom.setStyleSheet(_COMBO_STYLE)
        for txt in ["OFF", "U_I", "I_U"]:
            self.comboBox_WiringCom.addItem(txt)
        wiringLayout.addWidget(self.comboBox_WiringCom, 3, 1)

        # groupBox_12 (nested, kept for backward compatibility)
        self.groupBox_12 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_12.setObjectName("groupBox_12")
        self.groupBox_12.setMinimumHeight(0)
        self.groupBox_12.setMaximumHeight(0)

        basicLayout.addWidget(self.groupBox_3)

        # -- Update Rate column --
        updateCol = QtWidgets.QVBoxLayout()
        updateCol.setSpacing(12)

        self.groupBox_11 = QtWidgets.QGroupBox(basicGroup)
        self.groupBox_11.setObjectName("groupBox_11")
        self.groupBox_11.setTitle("")
        urLayout = QtWidgets.QVBoxLayout(self.groupBox_11)
        urLayout.setSpacing(6)
        urLayout.setContentsMargins(12, 12, 12, 12)

        self.label_44 = QtWidgets.QLabel(self.groupBox_11)
        self.label_44.setObjectName("label_44")
        self.label_44.setStyleSheet(_LABEL_STYLE)
        urLayout.addWidget(self.label_44)

        self.comboBox_ReplaceRate = QtWidgets.QComboBox(self.groupBox_11)
        self.comboBox_ReplaceRate.setObjectName("comboBox_ReplaceRate")
        self.comboBox_ReplaceRate.setStyleSheet(_COMBO_STYLE)
        for txt in ["50ms", "100ms", "250ms", "500ms", "1s", "2s", "5s", "10s", "20s"]:
            self.comboBox_ReplaceRate.addItem(txt)
        urLayout.addWidget(self.comboBox_ReplaceRate)

        updateCol.addWidget(self.groupBox_11)

        # -- Project Number --
        self.groupBox_13 = QtWidgets.QGroupBox(basicGroup)
        self.groupBox_13.setObjectName("groupBox_13")
        self.groupBox_13.setTitle("")
        projLayout = QtWidgets.QVBoxLayout(self.groupBox_13)
        projLayout.setSpacing(6)
        projLayout.setContentsMargins(12, 12, 12, 12)

        self.label_73 = QtWidgets.QLabel(self.groupBox_13)
        self.label_73.setObjectName("label_73")
        self.label_73.setStyleSheet(_LABEL_STYLE)
        projLayout.addWidget(self.label_73)

        self.comboBox_ProjectNum = QtWidgets.QComboBox(self.groupBox_13)
        self.comboBox_ProjectNum.setObjectName("comboBox_ProjectNum")
        self.comboBox_ProjectNum.setStyleSheet(_COMBO_STYLE)
        for txt in ["12", "24", "48", "200"]:
            self.comboBox_ProjectNum.addItem(txt)
        projLayout.addWidget(self.comboBox_ProjectNum)

        updateCol.addWidget(self.groupBox_13)
        basicLayout.addLayout(updateCol)

        contentLayout.addWidget(basicGroup)

        # ══════════════════════════════════════════════════════════════════════
        # Section 2: Save Settings (Auto Save / Stop Time / Path / Filenames)
        # ══════════════════════════════════════════════════════════════════════
        saveGroup = QtWidgets.QGroupBox("保存设置")
        saveGroup.setStyleSheet(_GROUPBOX_STYLE)
        saveLayout = QtWidgets.QGridLayout(saveGroup)
        saveLayout.setSpacing(12)
        saveLayout.setContentsMargins(12, 12, 12, 12)

        # -- groupBox_6: Auto Save + Stop Time --
        self.groupBox_6 = QtWidgets.QGroupBox(saveGroup)
        self.groupBox_6.setObjectName("groupBox_6")
        self.groupBox_6.setTitle("")
        gs6Layout = QtWidgets.QGridLayout(self.groupBox_6)
        gs6Layout.setSpacing(6)
        gs6Layout.setContentsMargins(8, 8, 8, 8)

        self.label_75 = QtWidgets.QLabel(self.groupBox_6)
        self.label_75.setObjectName("label_75")
        self.label_75.setStyleSheet(_LABEL_STYLE)
        gs6Layout.addWidget(self.label_75, 0, 0)

        self.comboBox_AutoSave = QtWidgets.QComboBox(self.groupBox_6)
        self.comboBox_AutoSave.setEnabled(False)
        self.comboBox_AutoSave.setEditable(True)
        self.comboBox_AutoSave.setObjectName("comboBox_AutoSave")
        self.comboBox_AutoSave.setStyleSheet(_COMBO_STYLE)
        for txt in ["OFF", "自动保存", "手动保存"]:
            self.comboBox_AutoSave.addItem(txt)
        gs6Layout.addWidget(self.comboBox_AutoSave, 0, 1)

        self.label_89 = QtWidgets.QLabel(self.groupBox_6)
        self.label_89.setObjectName("label_89")
        self.label_89.setStyleSheet(_LABEL_STYLE)
        gs6Layout.addWidget(self.label_89, 1, 0)

        self.textEdit_StopTime = QtWidgets.QTextEdit(self.groupBox_6)
        self.textEdit_StopTime.setObjectName("textEdit_StopTime")
        self.textEdit_StopTime.setStyleSheet(_TEXTEDIT_STYLE)
        self.textEdit_StopTime.setPlaceholderText("")
        self.textEdit_StopTime.setMaximumHeight(36)
        self.textEdit_StopTime.setHtml(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
            '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
            '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
            'p, li { white-space: pre-wrap; }\n'
            '</style></head><body style=" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;">\n'
            '<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">'
            '<span style=" font-family:\'SimSun\'; font-size:9pt;">00:05:00</span></p></body></html>'
        )
        gs6Layout.addWidget(self.textEdit_StopTime, 1, 1)

        saveLayout.addWidget(self.groupBox_6, 0, 0)

        # -- groupBox_15: Save Path --
        self.groupBox_15 = QtWidgets.QGroupBox(saveGroup)
        self.groupBox_15.setObjectName("groupBox_15")
        self.groupBox_15.setTitle("")
        gs15Layout = QtWidgets.QVBoxLayout(self.groupBox_15)
        gs15Layout.setSpacing(6)
        gs15Layout.setContentsMargins(8, 8, 8, 8)

        pathRow = QtWidgets.QHBoxLayout()
        self.label_136 = QtWidgets.QLabel(self.groupBox_15)
        self.label_136.setObjectName("label_136")
        self.label_136.setStyleSheet(_LABEL_STYLE)
        pathRow.addWidget(self.label_136)

        self.textEdit_SavePath = QtWidgets.QTextEdit(self.groupBox_15)
        self.textEdit_SavePath.setObjectName("textEdit_SavePath")
        self.textEdit_SavePath.setStyleSheet(_TEXTEDIT_STYLE)
        self.textEdit_SavePath.setMaximumHeight(36)
        self.textEdit_SavePath.setHtml(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
            '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
            '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
            'p, li { white-space: pre-wrap; }\n'
            '</style></head><body style=" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;">\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">'
            '<span style=" font-family:\'SimSun\'; font-size:9pt;">D:\\xiebodianliu_test</span></p></body></html>'
        )
        pathRow.addWidget(self.textEdit_SavePath)
        gs15Layout.addLayout(pathRow)

        self.checkBox_AutoName = QtWidgets.QCheckBox(self.groupBox_15)
        self.checkBox_AutoName.setEnabled(False)
        self.checkBox_AutoName.setCheckable(False)
        self.checkBox_AutoName.setChecked(False)
        self.checkBox_AutoName.setObjectName("checkBox_AutoName")
        self.checkBox_AutoName.setStyleSheet(_CHECKBOX_STYLE)
        gs15Layout.addWidget(self.checkBox_AutoName)

        saveLayout.addWidget(self.groupBox_15, 0, 1)

        # -- groupBox_7: File Name List --
        self.groupBox_7 = QtWidgets.QGroupBox(saveGroup)
        self.groupBox_7.setObjectName("groupBox_7")
        self.groupBox_7.setTitle("")
        gs7Layout = QtWidgets.QVBoxLayout(self.groupBox_7)
        gs7Layout.setSpacing(4)
        gs7Layout.setContentsMargins(8, 8, 8, 8)

        self.label_39 = QtWidgets.QLabel(self.groupBox_7)
        self.label_39.setObjectName("label_39")
        self.label_39.setStyleSheet(_LABEL_STYLE)
        gs7Layout.addWidget(self.label_39)

        self.textEdit_FileNameList = QtWidgets.QTextEdit(self.groupBox_7)
        self.textEdit_FileNameList.setObjectName("textEdit_FileNameList")
        self.textEdit_FileNameList.setStyleSheet(_TEXTEDIT_STYLE)
        self.textEdit_FileNameList.setMaximumHeight(120)
        self.textEdit_FileNameList.setHtml(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
            '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
            '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
            'p, li { white-space: pre-wrap; }\n'
            '</style></head><body style=" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;">\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">'
            '<span style=" font-family:\'SimSun\'; font-size:9pt;">'
            '100%_ambient,100%_+55,100%_-10,66%_ambient,66%_+55,66%_-10,'
            '33%_ambient,33%_+55,33%_-10,100%_ambient'
            '</span></p></body></html>'
        )
        gs7Layout.addWidget(self.textEdit_FileNameList)

        saveLayout.addWidget(self.groupBox_7, 0, 2)

        contentLayout.addWidget(saveGroup)

        # ══════════════════════════════════════════════════════════════════════
        # Section 3: Basic Measurements (Element / Sigma / U / I / P / S / Q)
        # ══════════════════════════════════════════════════════════════════════
        basicMeasGroup = QtWidgets.QGroupBox("测量项目 - 基本量")
        basicMeasGroup.setStyleSheet(_GROUPBOX_STYLE)
        bmLayout = QtWidgets.QGridLayout(basicMeasGroup)
        bmLayout.setSpacing(8)
        bmLayout.setContentsMargins(12, 12, 12, 12)

        # Row 0: Element 1-4
        bmLayout.addWidget(self._make_label(basicMeasGroup, "Element"), 0, 0)
        self.checkBox_SetElement1 = self._make_checkbox(basicMeasGroup, "Element1", "checkBox_SetElement1")
        self.checkBox_SetElement2 = self._make_checkbox(basicMeasGroup, "Element2", "checkBox_SetElement2")
        self.checkBox_SetElement3 = self._make_checkbox(basicMeasGroup, "Element3", "checkBox_SetElement3")
        self.checkBox_SetElement4 = self._make_checkbox(basicMeasGroup, "Element4", "checkBox_SetElement4")
        bmLayout.addWidget(self.checkBox_SetElement1, 0, 1)
        bmLayout.addWidget(self.checkBox_SetElement2, 0, 2)
        bmLayout.addWidget(self.checkBox_SetElement3, 0, 3)
        bmLayout.addWidget(self.checkBox_SetElement4, 0, 4)

        # Row 1: Sigma / SigmaA / SigmaB
        bmLayout.addWidget(self._make_label(basicMeasGroup, "Sigma"), 1, 0)
        self.checkBox_SetSigma = self._make_checkbox(basicMeasGroup, "Σ", "checkBox_SetSigma")
        self.checkBox_SetSigmaA = self._make_checkbox(basicMeasGroup, "SigmaA", "checkBox_SetSigmaA")
        self.checkBox_SetSigmaB = self._make_checkbox(basicMeasGroup, "SigmaB", "checkBox_SetSigmaB")
        bmLayout.addWidget(self.checkBox_SetSigma, 1, 1)
        bmLayout.addWidget(self.checkBox_SetSigmaA, 1, 2)
        bmLayout.addWidget(self.checkBox_SetSigmaB, 1, 3)

        # Row 2: U / Urange / CfU
        bmLayout.addWidget(self._make_label(basicMeasGroup, "U"), 2, 0)
        self.checkBox_SetU = self._make_checkbox(basicMeasGroup, "U", "checkBox_SetU")
        self.checkBox_SetUrange = self._make_checkbox(basicMeasGroup, "Urange", "checkBox_SetUrange")
        self.checkBox_SetCfU = self._make_checkbox(basicMeasGroup, "CfU", "checkBox_SetCfU")
        bmLayout.addWidget(self.checkBox_SetU, 2, 1)
        bmLayout.addWidget(self.checkBox_SetUrange, 2, 2)
        bmLayout.addWidget(self.checkBox_SetCfU, 2, 3)

        # Row 3: I / Irange / CfI
        bmLayout.addWidget(self._make_label(basicMeasGroup, "I"), 3, 0)
        self.checkBox_SetI = self._make_checkbox(basicMeasGroup, "I", "checkBox_SetI")
        self.checkBox_SetIrange = self._make_checkbox(basicMeasGroup, "Irange", "checkBox_SetIrange")
        self.checkBox_SetCfI = self._make_checkbox(basicMeasGroup, "CfI", "checkBox_SetCfI")
        bmLayout.addWidget(self.checkBox_SetI, 3, 1)
        bmLayout.addWidget(self.checkBox_SetIrange, 3, 2)
        bmLayout.addWidget(self.checkBox_SetCfI, 3, 3)

        # Row 4: Uppeak / Umpeak / Ippeak / Impeak
        bmLayout.addWidget(self._make_label(basicMeasGroup, "Peak"), 4, 0)
        self.checkBox_SetUppeak = self._make_checkbox(basicMeasGroup, "Uppeak", "checkBox_SetUppeak")
        self.checkBox_SetUmpeak = self._make_checkbox(basicMeasGroup, "Umpeak", "checkBox_SetUmpeak")
        self.checkBox_SetIppeak = self._make_checkbox(basicMeasGroup, "Ippeak", "checkBox_SetIppeak")
        self.checkBox_SetImpeak = self._make_checkbox(basicMeasGroup, "Impeak", "checkBox_SetImpeak")
        bmLayout.addWidget(self.checkBox_SetUppeak, 4, 1)
        bmLayout.addWidget(self.checkBox_SetUmpeak, 4, 2)
        bmLayout.addWidget(self.checkBox_SetIppeak, 4, 3)
        bmLayout.addWidget(self.checkBox_SetImpeak, 4, 4)

        # Row 5: P / S / Q / Lambda / Phi / Pc
        bmLayout.addWidget(self._make_label(basicMeasGroup, "Power"), 5, 0)
        self.checkBox_SetP = self._make_checkbox(basicMeasGroup, "P", "checkBox_SetP")
        self.checkBox_SetS = self._make_checkbox(basicMeasGroup, "S", "checkBox_SetS")
        self.checkBox_SetQ = self._make_checkbox(basicMeasGroup, "Q", "checkBox_SetQ")
        self.checkBox_SetLambda = self._make_checkbox(basicMeasGroup, "λ", "checkBox_SetLambda")
        self.checkBox_SetPhi = self._make_checkbox(basicMeasGroup, "φ", "checkBox_SetPhi")
        self.checkBox_SetPc = self._make_checkbox(basicMeasGroup, "Pc", "checkBox_SetPc")
        bmLayout.addWidget(self.checkBox_SetP, 5, 1)
        bmLayout.addWidget(self.checkBox_SetS, 5, 2)
        bmLayout.addWidget(self.checkBox_SetQ, 5, 3)
        bmLayout.addWidget(self.checkBox_SetLambda, 5, 4)
        bmLayout.addWidget(self.checkBox_SetPhi, 5, 5)
        bmLayout.addWidget(self.checkBox_SetPc, 5, 6)

        # Row 6: FreqU / FreqI
        bmLayout.addWidget(self._make_label(basicMeasGroup, "Freq"), 6, 0)
        self.checkBox_SetFreqU = self._make_checkbox(basicMeasGroup, "FreqU", "checkBox_SetFreqU")
        self.checkBox_SetFreqI = self._make_checkbox(basicMeasGroup, "FreqI", "checkBox_SetFreqI")
        bmLayout.addWidget(self.checkBox_SetFreqU, 6, 1)
        bmLayout.addWidget(self.checkBox_SetFreqI, 6, 2)

        contentLayout.addWidget(basicMeasGroup)

        # ══════════════════════════════════════════════════════════════════════
        # Section 4: Power / Energy / Efficiency
        # ══════════════════════════════════════════════════════════════════════
        powerGroup = QtWidgets.QGroupBox("测量项目 - 功率/能量/效率")
        powerGroup.setStyleSheet(_GROUPBOX_STYLE)
        pwrLayout = QtWidgets.QGridLayout(powerGroup)
        pwrLayout.setSpacing(8)
        pwrLayout.setContentsMargins(12, 12, 12, 12)

        # Row 0: Time / WP / WP+ / WP-
        pwrLayout.addWidget(self._make_label(powerGroup, "Active Power"), 0, 0)
        self.checkBox_SetTime = self._make_checkbox(powerGroup, "Time", "checkBox_SetTime")
        self.checkBox_SetWP = self._make_checkbox(powerGroup, "WP", "checkBox_SetWP")
        self.checkBox_SetWPPlus = self._make_checkbox(powerGroup, "WP+", "checkBox_SetWPPlus")
        self.checkBox_SetWPMinus = self._make_checkbox(powerGroup, "WP-", "checkBox_SetWPMinus")
        pwrLayout.addWidget(self.checkBox_SetTime, 0, 1)
        pwrLayout.addWidget(self.checkBox_SetWP, 0, 2)
        pwrLayout.addWidget(self.checkBox_SetWPPlus, 0, 3)
        pwrLayout.addWidget(self.checkBox_SetWPMinus, 0, 4)

        # Row 1: q / q+ / q- / WS / WQ
        pwrLayout.addWidget(self._make_label(powerGroup, "Reactive/Energy"), 1, 0)
        self.checkBox_Setq = self._make_checkbox(powerGroup, "q", "checkBox_Setq")
        self.checkBox_SetqPlus = self._make_checkbox(powerGroup, "q+", "checkBox_SetqPlus")
        self.checkBox_SetqMinus = self._make_checkbox(powerGroup, "q-", "checkBox_SetqMinus")
        self.checkBox_SetWS = self._make_checkbox(powerGroup, "WS", "checkBox_SetWS")
        self.checkBox_SetWQ = self._make_checkbox(powerGroup, "WQ", "checkBox_SetWQ")
        pwrLayout.addWidget(self.checkBox_Setq, 1, 1)
        pwrLayout.addWidget(self.checkBox_SetqPlus, 1, 2)
        pwrLayout.addWidget(self.checkBox_SetqMinus, 1, 3)
        pwrLayout.addWidget(self.checkBox_SetWS, 1, 4)
        pwrLayout.addWidget(self.checkBox_SetWQ, 1, 5)

        # Row 2: Eta1-4
        pwrLayout.addWidget(self._make_label(powerGroup, "Efficiency"), 2, 0)
        self.checkBox_SetEta1 = self._make_checkbox(powerGroup, "η1", "checkBox_SetEta1")
        self.checkBox_SetEta2 = self._make_checkbox(powerGroup, "η2", "checkBox_SetEta2")
        self.checkBox_SetEta3 = self._make_checkbox(powerGroup, "η3", "checkBox_SetEta3")
        self.checkBox_SetEta4 = self._make_checkbox(powerGroup, "η4", "checkBox_SetEta4")
        pwrLayout.addWidget(self.checkBox_SetEta1, 2, 1)
        pwrLayout.addWidget(self.checkBox_SetEta2, 2, 2)
        pwrLayout.addWidget(self.checkBox_SetEta3, 2, 3)
        pwrLayout.addWidget(self.checkBox_SetEta4, 2, 4)

        contentLayout.addWidget(powerGroup)

        # ══════════════════════════════════════════════════════════════════════
        # Section 5: Harmonic Measurements (Element k)
        # ══════════════════════════════════════════════════════════════════════
        harmonicGroup = QtWidgets.QGroupBox("测量项目 - 谐波量")
        harmonicGroup.setStyleSheet(_GROUPBOX_STYLE)
        hmLayout = QtWidgets.QGridLayout(harmonicGroup)
        hmLayout.setSpacing(8)
        hmLayout.setContentsMargins(12, 12, 12, 12)

        # Start / Stop
        self.label_90 = QtWidgets.QLabel(harmonicGroup)
        self.label_90.setObjectName("label_90")
        self.label_90.setStyleSheet(_LABEL_STYLE)
        hmLayout.addWidget(self.label_90, 0, 0)

        self.textEdit_SetStart = QtWidgets.QTextEdit(harmonicGroup)
        self.textEdit_SetStart.setObjectName("textEdit_SetStart")
        self.textEdit_SetStart.setStyleSheet(_TEXTEDIT_STYLE)
        self.textEdit_SetStart.setPlaceholderText("")
        self.textEdit_SetStart.setMaximumHeight(32)
        self.textEdit_SetStart.setMaximumWidth(100)
        self.textEdit_SetStart.setHtml(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
            '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
            '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
            'p, li { white-space: pre-wrap; }\n'
            '</style></head><body style=" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;">\n'
            '<p align="center" style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; '
            'margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; '
            'font-family:\'SimSun\'; font-size:9pt;"><br /></p></body></html>'
        )
        hmLayout.addWidget(self.textEdit_SetStart, 0, 1)

        self.label_91 = QtWidgets.QLabel(harmonicGroup)
        self.label_91.setObjectName("label_91")
        self.label_91.setStyleSheet(_LABEL_STYLE)
        hmLayout.addWidget(self.label_91, 0, 2)

        self.textEdit_SetStop = QtWidgets.QTextEdit(harmonicGroup)
        self.textEdit_SetStop.setObjectName("textEdit_SetStop")
        self.textEdit_SetStop.setStyleSheet(_TEXTEDIT_STYLE)
        self.textEdit_SetStop.setPlaceholderText("")
        self.textEdit_SetStop.setMaximumHeight(32)
        self.textEdit_SetStop.setMaximumWidth(100)
        self.textEdit_SetStop.setHtml(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
            '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
            '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
            'p, li { white-space: pre-wrap; }\n'
            '</style></head><body style=" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;">\n'
            '<p align="center" style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; '
            'margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; '
            'font-family:\'SimSun\'; font-size:9pt;"><br /></p></body></html>'
        )
        hmLayout.addWidget(self.textEdit_SetStop, 0, 3)

        # Row 1: Uk / Ik / Pk / Sk / Qk / PFk
        hmLayout.addWidget(self._make_label(harmonicGroup, "Basic"), 1, 0)
        self.checkBox_SetUk = self._make_checkbox(harmonicGroup, "U(k)", "checkBox_SetUk")
        self.checkBox_SetIk = self._make_checkbox(harmonicGroup, "I(k)", "checkBox_SetIk")
        self.checkBox_SetPk = self._make_checkbox(harmonicGroup, "P(k)", "checkBox_SetPk")
        self.checkBox_SetSk = self._make_checkbox(harmonicGroup, "S(k)", "checkBox_SetSk")
        self.checkBox_SetQk = self._make_checkbox(harmonicGroup, "Q(k)", "checkBox_SetQk")
        self.checkBox_SetPFk = self._make_checkbox(harmonicGroup, "PF(k)", "checkBox_SetPFk")
        hmLayout.addWidget(self.checkBox_SetUk, 1, 1)
        hmLayout.addWidget(self.checkBox_SetIk, 1, 2)
        hmLayout.addWidget(self.checkBox_SetPk, 1, 3)
        hmLayout.addWidget(self.checkBox_SetSk, 1, 4)
        hmLayout.addWidget(self.checkBox_SetQk, 1, 5)
        hmLayout.addWidget(self.checkBox_SetPFk, 1, 6)

        # Row 2: Phik / PhiUk / PhiIk
        hmLayout.addWidget(self._make_label(harmonicGroup, "Phi"), 2, 0)
        self.checkBox_SetPhik = self._make_checkbox(harmonicGroup, "Phi(k)", "checkBox_SetPhik")
        self.checkBox_SetPhiUk = self._make_checkbox(harmonicGroup, "PhiU(k)", "checkBox_SetPhiUk")
        self.checkBox_SetPhiIk = self._make_checkbox(harmonicGroup, "PhiI(k)", "checkBox_SetPhiIk")
        hmLayout.addWidget(self.checkBox_SetPhik, 2, 1)
        hmLayout.addWidget(self.checkBox_SetPhiUk, 2, 2)
        hmLayout.addWidget(self.checkBox_SetPhiIk, 2, 3)

        # Row 3: Uhdfk / Ihdfk / Phdfk
        hmLayout.addWidget(self._make_label(harmonicGroup, "HDF"), 3, 0)
        self.checkBox_SetUhdfk = self._make_checkbox(harmonicGroup, "Uhdf(k)", "checkBox_SetUhdfk")
        self.checkBox_SetIhdfk = self._make_checkbox(harmonicGroup, "Ihdf(k)", "checkBox_SetIhdfk")
        self.checkBox_SetPhdfk = self._make_checkbox(harmonicGroup, "Phdf(k)", "checkBox_SetPhdfk")
        hmLayout.addWidget(self.checkBox_SetUhdfk, 3, 1)
        hmLayout.addWidget(self.checkBox_SetIhdfk, 3, 2)
        hmLayout.addWidget(self.checkBox_SetPhdfk, 3, 3)

        # Row 4: Zk / Rsk / Rpk / Xsk / Xpk
        hmLayout.addWidget(self._make_label(harmonicGroup, "Impedance"), 4, 0)
        self.checkBox_SetZk = self._make_checkbox(harmonicGroup, "Z(k)", "checkBox_SetZk")
        self.checkBox_SetRsk = self._make_checkbox(harmonicGroup, "Rs(k)", "checkBox_SetRsk")
        self.checkBox_SetRpk = self._make_checkbox(harmonicGroup, "Rp(k)", "checkBox_SetRpk")
        self.checkBox_SetXsk = self._make_checkbox(harmonicGroup, "Xs(k)", "checkBox_SetXsk")
        self.checkBox_SetXpk = self._make_checkbox(harmonicGroup, "Xp(k)", "checkBox_SetXpk")
        hmLayout.addWidget(self.checkBox_SetZk, 4, 1)
        hmLayout.addWidget(self.checkBox_SetRsk, 4, 2)
        hmLayout.addWidget(self.checkBox_SetRpk, 4, 3)
        hmLayout.addWidget(self.checkBox_SetXsk, 4, 4)
        hmLayout.addWidget(self.checkBox_SetXpk, 4, 5)

        contentLayout.addWidget(harmonicGroup)

        # ══════════════════════════════════════════════════════════════════════
        # Section 6: THD & Others
        # ══════════════════════════════════════════════════════════════════════
        thdGroup = QtWidgets.QGroupBox("测量项目 - THD 及其他")
        thdGroup.setStyleSheet(_GROUPBOX_STYLE)
        thdLayout = QtWidgets.QGridLayout(thdGroup)
        thdLayout.setSpacing(8)
        thdLayout.setContentsMargins(12, 12, 12, 12)

        # Row 0: Uthd / Ithd / Pthd / Uthf / Ithf
        thdLayout.addWidget(self._make_label(thdGroup, "THD/F"), 0, 0)
        self.checkBox_SetUthd = self._make_checkbox(thdGroup, "Uthd", "checkBox_SetUthd")
        self.checkBox_SetIthd = self._make_checkbox(thdGroup, "Ithd", "checkBox_SetIthd")
        self.checkBox_SetPthd = self._make_checkbox(thdGroup, "Pthd", "checkBox_SetPthd")
        self.checkBox_SetUthf = self._make_checkbox(thdGroup, "Uthf", "checkBox_SetUthf")
        self.checkBox_SetIthf = self._make_checkbox(thdGroup, "Ithf", "checkBox_SetIthf")
        thdLayout.addWidget(self.checkBox_SetUthd, 0, 1)
        thdLayout.addWidget(self.checkBox_SetIthd, 0, 2)
        thdLayout.addWidget(self.checkBox_SetPthd, 0, 3)
        thdLayout.addWidget(self.checkBox_SetUthf, 0, 4)
        thdLayout.addWidget(self.checkBox_SetIthf, 0, 5)

        # Row 1: Utif / Itif / hvf / hcf
        thdLayout.addWidget(self._make_label(thdGroup, "TIF/Factor"), 1, 0)
        self.checkBox_SetUtif = self._make_checkbox(thdGroup, "Utif", "checkBox_SetUtif")
        self.checkBox_SetItif = self._make_checkbox(thdGroup, "Itif", "checkBox_SetItif")
        self.checkBox_Sethvf = self._make_checkbox(thdGroup, "hvf", "checkBox_Sethvf")
        self.checkBox_Sethcf = self._make_checkbox(thdGroup, "hcf", "checkBox_Sethcf")
        thdLayout.addWidget(self.checkBox_SetUtif, 1, 1)
        thdLayout.addWidget(self.checkBox_SetItif, 1, 2)
        thdLayout.addWidget(self.checkBox_Sethvf, 1, 3)
        thdLayout.addWidget(self.checkBox_Sethcf, 1, 4)

        # Row 2: PhiUi-Uj / PhiUi-Uk / PhiUi-Ii / PhiUi-Ij / PhiUi-Ik
        thdLayout.addWidget(self._make_label(thdGroup, "Phase"), 2, 0)
        self.checkBox_SetPhiUi_Uj = self._make_checkbox(thdGroup, "φUi-Uj", "checkBox_SetPhiUi_Uj")
        self.checkBox_SetPhiUi_Uk = self._make_checkbox(thdGroup, "φUi-Uk", "checkBox_SetPhiUi_Uk")
        self.checkBox_SetPhiUi_Ii = self._make_checkbox(thdGroup, "φUi-Ii", "checkBox_SetPhiUi_Ii")
        self.checkBox_SetPhiUi_Ij = self._make_checkbox(thdGroup, "φUi-Ij", "checkBox_SetPhiUi_Ij")
        self.checkBox_SetPhiUi_Ik = self._make_checkbox(thdGroup, "φUi-Ik", "checkBox_SetPhiUi_Ik")
        thdLayout.addWidget(self.checkBox_SetPhiUi_Uj, 2, 1)
        thdLayout.addWidget(self.checkBox_SetPhiUi_Uk, 2, 2)
        thdLayout.addWidget(self.checkBox_SetPhiUi_Ii, 2, 3)
        thdLayout.addWidget(self.checkBox_SetPhiUi_Ij, 2, 4)
        thdLayout.addWidget(self.checkBox_SetPhiUi_Ik, 2, 5)

        # Row 3: Speed / Torque / SyncSp / Slip / Pm
        thdLayout.addWidget(self._make_label(thdGroup, "Motor"), 3, 0)
        self.checkBox_SetSpeed = self._make_checkbox(thdGroup, "Speed", "checkBox_SetSpeed")
        self.checkBox_SetTorque = self._make_checkbox(thdGroup, "Torque", "checkBox_SetTorque")
        self.checkBox_SetSyncSp = self._make_checkbox(thdGroup, "SyncSp", "checkBox_SetSyncSp")
        self.checkBox_SetSlip = self._make_checkbox(thdGroup, "Slip", "checkBox_SetSlip")
        self.checkBox_SetPm = self._make_checkbox(thdGroup, "Pm", "checkBox_SetPm")
        thdLayout.addWidget(self.checkBox_SetSpeed, 3, 1)
        thdLayout.addWidget(self.checkBox_SetTorque, 3, 2)
        thdLayout.addWidget(self.checkBox_SetSyncSp, 3, 3)
        thdLayout.addWidget(self.checkBox_SetSlip, 3, 4)
        thdLayout.addWidget(self.checkBox_SetPm, 3, 5)

        # Row 4: DeltaF1-4
        thdLayout.addWidget(self._make_label(thdGroup, "DeltaF"), 4, 0)
        self.checkBox_SetDeltaF1 = self._make_checkbox(thdGroup, "ΔF1", "checkBox_SetDeltaF1")
        self.checkBox_SetDeltaF2 = self._make_checkbox(thdGroup, "ΔF2", "checkBox_SetDeltaF2")
        self.checkBox_SetDeltaF3 = self._make_checkbox(thdGroup, "ΔF3", "checkBox_SetDeltaF3")
        self.checkBox_SetDeltaF4 = self._make_checkbox(thdGroup, "ΔF4", "checkBox_SetDeltaF4")
        thdLayout.addWidget(self.checkBox_SetDeltaF1, 4, 1)
        thdLayout.addWidget(self.checkBox_SetDeltaF2, 4, 2)
        thdLayout.addWidget(self.checkBox_SetDeltaF3, 4, 3)
        thdLayout.addWidget(self.checkBox_SetDeltaF4, 4, 4)

        contentLayout.addWidget(thdGroup)

        # ══════════════════════════════════════════════════════════════════════
        # Section 7: F Function (F01-F20)
        # ══════════════════════════════════════════════════════════════════════
        fGroup = QtWidgets.QGroupBox("F Function 选择")
        fGroup.setStyleSheet(_GROUPBOX_STYLE)
        fLayout = QtWidgets.QGridLayout(fGroup)
        fLayout.setSpacing(8)
        fLayout.setContentsMargins(12, 12, 12, 12)

        # Row 0: F01-F10
        fLabels0 = ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10"]
        fNames0 = [
            "checkBox_SetF01", "checkBox_SetF02", "checkBox_SetF03", "checkBox_SetF04",
            "checkBox_SetF05", "checkBox_SetF06", "checkBox_SetF07", "checkBox_SetF08",
            "checkBox_SetF09", "checkBox_SetF10",
        ]
        for col, (lbl, nm) in enumerate(zip(fLabels0, fNames0)):
            cb = self._make_checkbox(fGroup, lbl, nm)
            setattr(self, nm, cb)
            fLayout.addWidget(cb, 0, col)

        # Row 1: F11-F20
        fLabels1 = ["F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20"]
        fNames1 = [
            "checkBox_SetF11", "checkBox_SetF12", "checkBox_SetF13", "checkBox_SetF14",
            "checkBox_SetF15", "checkBox_SetF16", "checkBox_SetF17", "checkBox_SetF18",
            "checkBox_SetF19", "checkBox_SetF20",
        ]
        for col, (lbl, nm) in enumerate(zip(fLabels1, fNames1)):
            cb = self._make_checkbox(fGroup, lbl, nm)
            setattr(self, nm, cb)
            fLayout.addWidget(cb, 1, col)

        contentLayout.addWidget(fGroup)

        # ── End of scrollable content ───────────────────────────────────────
        contentLayout.addStretch(1)
        scrollArea.setWidget(contentWidget)
        mainLayout.addWidget(scrollArea, 1)

        # ── Hidden pushButton_Send (backward compatibility) ──────────────────
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        # ── Finalize ────────────────────────────────────────────────────────
        self.comboBox_AutoSave.setCurrentIndex(1)
        self.retranslateUi(Dialog_thai_WT3000E)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thai_WT3000E)

    # ── Helper methods ──────────────────────────────────────────────────────

    @staticmethod
    def _make_label(parent, text):
        """Create a styled QLabel for grid row headers."""
        lbl = QtWidgets.QLabel(text, parent)
        lbl.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #334155; padding-right: 8px;"
        )
        return lbl

    @staticmethod
    def _make_checkbox(parent, text, object_name):
        """Create a styled QCheckBox with the given objectName."""
        cb = QtWidgets.QCheckBox(text, parent)
        cb.setObjectName(object_name)
        cb.setChecked(False)
        cb.setStyleSheet(_CHECKBOX_STYLE)
        return cb

    def retranslateUi(self, Dialog_thai_WT3000E):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thai_WT3000E.setWindowTitle(
            _translate("Dialog_thai_WT3000E", "WT3000E参数配置")
        )
        self.pushButton_Confirm.setText(
            _translate("Dialog_thai_WT3000E", "确认")
        )
        self.pushButton_TestAppend.setText(
            _translate("Dialog_thai_WT3000E", "追加测试")
        )
        self.pushButton_ReadSettingFile.setText(
            _translate("Dialog_thai_WT3000E", "读取配置")
        )
        self.pushButton_SaveSettingFile.setText(
            _translate("Dialog_thai_WT3000E", "保存配置")
        )

        # ComboBox item texts
        for i, txt in enumerate(["50ms", "100ms", "250ms", "500ms", "1s", "2s", "5s", "10s", "20s"]):
            self.comboBox_ReplaceRate.setItemText(i, _translate("Dialog_thai_WT3000E", txt))

        self.label_44.setText(_translate("Dialog_thai_WT3000E", "更新率"))
        self.groupBox_3.setTitle(_translate("Dialog_thai_WT3000E", "接线方式"))
        self.label_38.setText(_translate("Dialog_thai_WT3000E", "SigmaA"))
        self.label_41.setText(_translate("Dialog_thai_WT3000E", "SigmaB"))
        self.label_42.setText(_translate("Dialog_thai_WT3000E", "接线补偿"))
        self.label_43.setText(_translate("Dialog_thai_WT3000E", "单元独立设置"))
        self.groupBox_12.setTitle(_translate("Dialog_thai_WT3000E", "更新率"))
        self.label_73.setText(_translate("Dialog_thai_WT3000E", "项目"))
        self.label_75.setText(_translate("Dialog_thai_WT3000E", "自动保存"))
        self.label_89.setText(_translate("Dialog_thai_WT3000E", "停止时间"))
        self.label_39.setText(_translate("Dialog_thai_WT3000E", "文件名"))
        self.label_136.setText(_translate("Dialog_thai_WT3000E", "保存路径"))
        self.checkBox_AutoName.setText(_translate("Dialog_thai_WT3000E", "自动命名"))
        self.label_90.setText(_translate("Dialog_thai_WT3000E", "开始"))
        self.label_91.setText(_translate("Dialog_thai_WT3000E", "结束"))

        # Measurement checkbox texts
        cb_texts = {
            "checkBox_SetF11": "F11", "checkBox_SetF12": "F12", "checkBox_SetF14": "F14",
            "checkBox_SetF13": "F13", "checkBox_SetF16": "F16", "checkBox_SetF15": "F15",
            "checkBox_SetF18": "F18", "checkBox_SetF17": "F17", "checkBox_SetF20": "F20",
            "checkBox_SetF19": "F19", "checkBox_SetF06": "F06", "checkBox_SetF02": "F02",
            "checkBox_SetF09": "F09", "checkBox_SetF08": "F08", "checkBox_SetF07": "F07",
            "checkBox_SetF10": "F10", "checkBox_SetF05": "F05", "checkBox_SetF04": "F04",
            "checkBox_SetF01": "F01", "checkBox_SetF03": "F03",
            "checkBox_SetWPPlus": "WP+", "checkBox_SetWQ": "WQ",
            "checkBox_SetEta1": "η1", "checkBox_SetWPMinus": "WP-",
            "checkBox_SetWP": "WP", "checkBox_SetqPlus": "q+", "checkBox_SetqMinus": "q-",
            "checkBox_SetEta2": "η2", "checkBox_SetEta3": "η3",
            "checkBox_SetEta4": "η4", "checkBox_SetTime": "Time",
            "checkBox_SetWS": "WS", "checkBox_Setq": "q", "checkBox_SetQ": "Q",
            "checkBox_SetUmpeak": "Umpeak", "checkBox_SetFreqU": "FreqU",
            "checkBox_SetIppeak": "Ippeak", "checkBox_SetI": "I",
            "checkBox_SetUppeak": "Uppeak", "checkBox_SetLambda": "λ",
            "checkBox_SetS": "S", "checkBox_SetIrange": "Irange", "checkBox_SetPc": "Pc",
            "checkBox_SetCfI": "CfI", "checkBox_SetFreqI": "FreqI",
            "checkBox_SetPhi": "φ", "checkBox_SetP": "P", "checkBox_SetImpeak": "Impeak",
            "checkBox_SetElement3": "Element3", "checkBox_SetElement4": "Element4",
            "checkBox_SetSigmaA": "SigmaA", "checkBox_SetSigma": "Σ",
            "checkBox_SetSigmaB": "SigmaB", "checkBox_SetU": "U",
            "checkBox_SetElement1": "Element1", "checkBox_SetElement2": "Element2",
            "checkBox_SetUrange": "Urange", "checkBox_SetCfU": "CfU",
            "checkBox_SetPk": "P(k)", "checkBox_SetUk": "U(k)",
            "checkBox_SetPhdfk": "Phdf(k)", "checkBox_SetPhik": "Phi(k)",
            "checkBox_SetQk": "Q(k)", "checkBox_SetPFk": "PF(k)",
            "checkBox_SetUhdfk": "Uhdf(k)", "checkBox_SetIk": "I(k)",
            "checkBox_SetPhiUk": "PhiU(k)", "checkBox_SetIhdfk": "Ihdf(k)",
            "checkBox_SetSk": "S(k)", "checkBox_SetPhiIk": "PhiI(k)",
            "checkBox_SetXsk": "Xs(k)", "checkBox_SetZk": "Z(k)",
            "checkBox_SetUthd": "Uthd", "checkBox_SetXpk": "Xp(k)",
            "checkBox_SetUthf": "Uthf", "checkBox_SetRsk": "Rs(k)",
            "checkBox_SetIthd": "Ithd", "checkBox_SetIthf": "Ithf",
            "checkBox_SetRpk": "Rp(k)", "checkBox_SetPthd": "Pthd",
            "checkBox_Sethvf": "hvf", "checkBox_SetUtif": "Utif",
            "checkBox_SetPhiUi_Uj": "φUi-Uj", "checkBox_SetPhiUi_Ij": "φUi-Ij",
            "checkBox_SetItif": "Itif", "checkBox_SetPhiUi_Uk": "φUi-Uk",
            "checkBox_SetPhiUi_Ik": "φUi-Ik", "checkBox_Sethcf": "hcf",
            "checkBox_SetPhiUi_Ii": "φUi-Ii", "checkBox_SetSyncSp": "SyncSp",
            "checkBox_SetSpeed": "Speed", "checkBox_SetDeltaF1": "ΔF1",
            "checkBox_SetPm": "Pm", "checkBox_SetDeltaF4": "ΔF4",
            "checkBox_SetTorque": "Torque", "checkBox_SetDeltaF2": "ΔF2",
            "checkBox_SetSlip": "Slip", "checkBox_SetDeltaF3": "ΔF3",
        }
        for obj_name, text in cb_texts.items():
            cb = getattr(self, obj_name, None)
            if cb:
                cb.setText(_translate("Dialog_thai_WT3000E", text))
