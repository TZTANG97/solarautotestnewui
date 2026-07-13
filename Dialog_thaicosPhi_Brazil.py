# -*- coding: utf-8 -*-
# 巴西CosPhi项目配置 - 现代化布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)

# ── 共享样式常量 ──
_INPUT_STYLE = (
    "QTextEdit { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; "
    "padding: 4px; font-size: 11px; color: #1e293b; }"
    "QTextEdit:focus { border: 1px solid #8b5cf6; }"
)
_COMBO_STYLE = (
    "QComboBox { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; "
    "padding: 4px 8px; font-size: 11px; color: #1e293b; }"
    "QComboBox:focus { border: 1px solid #8b5cf6; }"
    "QComboBox::drop-down { border: none; width: 20px; }"
)
_LABEL_STYLE = "font-size: 11px; color: #475569; background: transparent; border: none;"
_GROUPBOX_STYLE = (
    "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; "
    "font-weight: bold; font-size: 12px; color: #1e293b; }"
    "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }"
)
_CHECKBOX_STYLE = (
    "QCheckBox { font-size: 11px; color: #334155; spacing: 6px; }"
    "QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; "
    "border: 1px solid #cbd5e1; background: white; }"
    "QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
)
_PUSHBTN_PURPLE = (
    "QPushButton { background-color: #8b5cf6; color: white; border: none; border-radius: 4px; "
    "padding: 6px 14px; font-size: 12px; font-weight: bold; }"
    "QPushButton:hover { background-color: #7c3aed; }"
)
_PUSHBTN_BLUE = (
    "QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 4px; "
    "padding: 6px 14px; font-size: 12px; }"
    "QPushButton:hover { background-color: #2563eb; }"
)
_PUSHBTN_GREEN = (
    "QPushButton { background-color: #10b981; color: white; border: none; border-radius: 4px; "
    "padding: 6px 14px; font-size: 12px; }"
    "QPushButton:hover { background-color: #059669; }"
)


def _make_input(text=""):
    """创建统一样式的 QTextEdit 输入框。"""
    te = QtWidgets.QTextEdit()
    te.setFixedHeight(28)
    te.setStyleSheet(_INPUT_STYLE)
    if text:
        te.setPlainText(text)
    return te


def _make_combo(items=None):
    """创建统一样式的 QComboBox。"""
    cb = QtWidgets.QComboBox()
    cb.setFixedHeight(28)
    cb.setStyleSheet(_COMBO_STYLE)
    if items:
        cb.addItems(items)
    return cb


def _make_label(text):
    """创建统一样式的 QLabel。"""
    lbl = QtWidgets.QLabel(text)
    lbl.setStyleSheet(_LABEL_STYLE)
    return lbl


def _make_title_label(text):
    """创建组标题标签。"""
    lbl = QtWidgets.QLabel(text)
    lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b; background: transparent; border: none;")
    return lbl


class Ui_Dialog_thaicosPhi_Brazil(object):
    def setupUi(self, Dialog_thaicosPhi_Brazil):
        Dialog_thaicosPhi_Brazil.setObjectName("Dialog_thaicosPhi_Brazil")
        Dialog_thaicosPhi_Brazil.resize(1599, 840)
        Dialog_thaicosPhi_Brazil.setMinimumSize(QtCore.QSize(1400, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_thaicosPhi_Brazil.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaicosPhi_Brazil)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ══════════════════════════════════════
        # 顶部工具栏（按钮 + 横向步骤条）
        # ══════════════════════════════════════
        topBar = QtWidgets.QWidget()
        topBar.setFixedHeight(56)
        topBar.setStyleSheet("QWidget { background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; }")
        topLayout = QtWidgets.QHBoxLayout(topBar)
        topLayout.setContentsMargins(12, 0, 12, 0)
        topLayout.setSpacing(8)

        self.pushButton_TestAppend = QtWidgets.QPushButton("测试追加")
        self.pushButton_TestAppend.setObjectName("pushButton_TestAppend")
        self.pushButton_TestAppend.setStyleSheet("""
            QPushButton { background-color: #8b5cf6; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        topLayout.addWidget(self.pushButton_TestAppend)

        self.pushButton_ReadSettingFile = QtWidgets.QPushButton("读取设定")
        self.pushButton_ReadSettingFile.setObjectName("pushButton_ReadSettingFile")
        self.pushButton_ReadSettingFile.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        topLayout.addWidget(self.pushButton_ReadSettingFile)

        self.pushButton_SaveSettingFile = QtWidgets.QPushButton("保存设定")
        self.pushButton_SaveSettingFile.setObjectName("pushButton_SaveSettingFile")
        self.pushButton_SaveSettingFile.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #059669; }
        """)
        topLayout.addWidget(self.pushButton_SaveSettingFile)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        sep.setStyleSheet("color: #cbd5e1; border: none; max-width: 1px;")
        topLayout.addWidget(sep)

        settingsTitle = QtWidgets.QLabel("项目设置")
        settingsTitle.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e293b; background: transparent; border: none;")
        topLayout.addWidget(settingsTitle)
        self.label_append_count = QtWidgets.QLabel("0")
        self.label_append_count.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #8b5cf6; background-color: #ede9fe; "
            "border-radius: 10px; padding: 2px 8px; border: none;"
        )
        self.label_append_count.setAlignment(QtCore.Qt.AlignCenter)
        topLayout.addWidget(self.label_append_count)

        self.pushButton_ResetCount = QtWidgets.QPushButton("重置")
        self.pushButton_ResetCount.setObjectName("pushButton_ResetCount")
        self.pushButton_ResetCount.setStyleSheet("""
            QPushButton { background-color: #ef4444; color: white; border: none; border-radius: 4px;
                          padding: 4px 10px; font-size: 11px; }
            QPushButton:hover { background-color: #dc2626; }
        """)
        topLayout.addWidget(self.pushButton_ResetCount)

        topLayout.addStretch()

        self._step_labels = []
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ cosPhi 设置", "④ 关机设置"]
        for i, title in enumerate(step_titles):
            lbl = QtWidgets.QLabel(title)
            lbl.setObjectName(f"step_indicator_{i}")
            lbl.setCursor(QtCore.Qt.PointingHandCursor)
            lbl.setStyleSheet("""
                QLabel {
                    padding: 6px 12px; font-size: 12px; color: #64748b;
                    border-bottom: 3px solid transparent; border-radius: 0;
                    background: transparent;
                }
                QLabel:hover { background-color: #f1f5f9; }
            """)
            lbl.mousePressEvent = lambda event, idx=i: self._switch_step(idx)
            topLayout.addWidget(lbl)
            self._step_labels.append(lbl)

        mainLayout.addWidget(topBar)

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setStyleSheet("background-color: white;")
        mainLayout.addWidget(self.stackedWidget, 1)

        # ── 构建各步骤页面 ──
        self._build_step1()
        self._build_step2()
        self._build_cosPhi_steps()
        self._build_step_last()

        # 默认显示第一页
        self._switch_step(0)

        # DC 联动
        self._connect_dc_linkage()

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaicosPhi_Brazil)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaicosPhi_Brazil)

    # ══════════════════════════════════════════════
    # 步骤切换
    # ══════════════════════════════════════════════
    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet(
                    "QLabel { padding: 6px 12px; font-size: 12px; font-weight: bold; color: #7c3aed; "
                    "border-bottom: 3px solid #8b5cf6; border-radius: 0; background-color: #f3e8ff; }"
                )
            else:
                lbl.setStyleSheet(
                    "QLabel { padding: 6px 12px; font-size: 12px; color: #64748b; "
                    "border-bottom: 3px solid transparent; border-radius: 0; background: transparent; }"
                    "QLabel:hover { background-color: #f1f5f9; }"
                )

    def _make_radio(self, name, text, parent=None, checked=False):
        """创建 QRadioButton 并存储到 self。"""
        rb = QtWidgets.QRadioButton(text)
        rb.setObjectName(name)
        if parent is not None:
            setattr(self, name, rb)
        if checked:
            rb.setChecked(True)
        return rb

    # ══════════════════════════════════════════════
    # Step 1: AC/DC 电源设置
    # ══════════════════════════════════════════════
    def _build_step1(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 主开关
        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setStyleSheet(
            "QCheckBox { font-size: 13px; font-weight: bold; color: #7c3aed; spacing: 6px; }"
            "QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; "
            "border: 1px solid #cbd5e1; background: white; }"
            "QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
        )
        layout.addWidget(self.checkBox_S1)

        # ── AC 电源组 ──
        acGroup = QtWidgets.QGroupBox("交流电源设置")
        acGroup.setStyleSheet(_GROUPBOX_STYLE)
        acLayout = QtWidgets.QGridLayout(acGroup)
        acLayout.setSpacing(8)
        acLayout.setContentsMargins(12, 20, 12, 12)

        row = 0
        acLayout.addWidget(_make_label("交流电源"), row, 0)
        self.comboBox_S1_AC = _make_combo(["开启", "关闭"])
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        acLayout.addWidget(self.comboBox_S1_AC, row, 1)
        acLayout.addWidget(_make_label("交流电压1"), row, 2)
        self.textEdit_S1_AC_VOLT = _make_input("220")
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        acLayout.addWidget(self.textEdit_S1_AC_VOLT, row, 3)
        acLayout.addWidget(_make_label("V"), row, 4)
        acLayout.addWidget(_make_label("交流电压2"), row, 5)
        self.comboBox_S1_AC_2 = _make_combo(["单相", "三相"])
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        acLayout.addWidget(self.comboBox_S1_AC_2, row, 6)
        self.textEdit_S1_AC_VOLT_2 = _make_input("220")
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        acLayout.addWidget(self.textEdit_S1_AC_VOLT_2, row, 7)
        acLayout.addWidget(_make_label("V"), row, 8)
        acLayout.addWidget(_make_label("交流电压3"), row, 9)
        self.textEdit_S1_AC_VOLT_3 = _make_input("220")
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        acLayout.addWidget(self.textEdit_S1_AC_VOLT_3, row, 10)
        acLayout.addWidget(_make_label("V"), row, 11)

        row = 1
        acLayout.addWidget(_make_label("频率"), row, 2)
        self.textEdit_S1_AC_FR = _make_input("50")
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        acLayout.addWidget(self.textEdit_S1_AC_FR, row, 3)
        acLayout.addWidget(_make_label("Hz"), row, 4)

        acLayout.setColumnStretch(12, 1)
        layout.addWidget(acGroup)

        # ── DC 电源组（4路，每路一行） ──
        dcGroup = QtWidgets.QGroupBox("直流电源设置")
        dcGroup.setStyleSheet(_GROUPBOX_STYLE)
        dcLayout = QtWidgets.QGridLayout(dcGroup)
        dcLayout.setSpacing(8)
        dcLayout.setContentsMargins(12, 20, 12, 12)

        # 表头
        headers = ["", "电源", "Vmp", "", "Voc", "", "Imp", "", "Isc", "", "功率", "", "开关"]
        for c, h in enumerate(headers):
            if h:
                dcLayout.addWidget(_make_title_label(h), 0, c)

        dc_data = [
            ("checkBox_S1_DC1", "直流电源1", "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_Voc",
             "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF", "comboBox_S1_DC1"),
            ("checkBox_S1_DC2", "直流电源2", "textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_Voc",
             "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF", "comboBox_S1_DC2"),
            ("checkBox_S1_DC3", "直流电源3", "textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_Voc",
             "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF", "comboBox_S1_DC3"),
            ("checkBox_S1_DC4", "直流电源4", "textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_Voc",
             "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF", "comboBox_S1_DC4"),
        ]
        for r, (cb_name, cb_text, volt, voc, curr, isc, pf, combo_name) in enumerate(dc_data, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setObjectName(cb_name)
            cb.setChecked(True)
            cb.setStyleSheet(_CHECKBOX_STYLE)
            dcLayout.addWidget(cb, r, 0, 1, 2)
            setattr(self, cb_name, cb)

            volt_te = _make_input("220")
            volt_te.setObjectName(volt)
            dcLayout.addWidget(volt_te, r, 2)
            dcLayout.addWidget(_make_label("V"), r, 3)
            setattr(self, volt, volt_te)

            voc_te = _make_input("220")
            voc_te.setObjectName(voc)
            dcLayout.addWidget(voc_te, r, 4)
            dcLayout.addWidget(_make_label("V"), r, 5)
            setattr(self, voc, voc_te)

            curr_te = _make_input("10")
            curr_te.setObjectName(curr)
            dcLayout.addWidget(curr_te, r, 6)
            dcLayout.addWidget(_make_label("A"), r, 7)
            setattr(self, curr, curr_te)

            isc_te = _make_input("10")
            isc_te.setObjectName(isc)
            dcLayout.addWidget(isc_te, r, 8)
            dcLayout.addWidget(_make_label("A"), r, 9)
            setattr(self, isc, isc_te)

            pf_te = _make_input("100")
            pf_te.setObjectName(pf)
            dcLayout.addWidget(pf_te, r, 10)
            dcLayout.addWidget(_make_label("%"), r, 11)
            setattr(self, pf, pf_te)

            combo = _make_combo(["开启", "关闭"])
            combo.setObjectName(combo_name)
            dcLayout.addWidget(combo, r, 12)
            setattr(self, combo_name, combo)

        layout.addWidget(dcGroup)

        # ── 时序设置 ──
        seqGroup = QtWidgets.QGroupBox("时序设置")
        seqGroup.setStyleSheet(_GROUPBOX_STYLE)
        seqLayout = QtWidgets.QGridLayout(seqGroup)
        seqLayout.setSpacing(8)
        seqLayout.setContentsMargins(12, 20, 12, 12)

        seqLayout.addWidget(_make_label("等待时间:"), 0, 0)
        self.textEdit_S1_ACWaitTIME = _make_input("3")
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        seqLayout.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = _make_combo(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        seqLayout.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        seqLayout.addWidget(_make_label("启机时间:"), 0, 3)
        self.textEdit_S1_TIME = _make_input("5")
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        seqLayout.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = _make_combo(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        seqLayout.addWidget(self.comboBox_S1_TIME, 0, 5)

        seqLayout.setColumnStretch(6, 1)
        layout.addWidget(seqGroup)

        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 2: 功率分析仪
    # ══════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 步骤启用复选框
        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setStyleSheet(
            "QCheckBox { font-size: 13px; font-weight: bold; color: #7c3aed; spacing: 6px; }"
            "QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; "
            "border: 1px solid #cbd5e1; background: white; }"
            "QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
        )
        layout.addWidget(self.checkBox_S2)

        # 功率分析仪配置组
        wtGroup = QtWidgets.QGroupBox("功率分析仪配置")
        wtGroup.setStyleSheet(_GROUPBOX_STYLE)
        wtLayout = QtWidgets.QGridLayout(wtGroup)
        wtLayout.setSpacing(12)
        wtLayout.setContentsMargins(12, 20, 12, 12)

        # Radio buttons（单选，默认 WT3000）
        self.radioButton_S2_WT3000 = self._make_radio("radio_S2_WT3000", "WT3000", parent=self, checked=True)
        self.radioButton_S2_WT1800 = self._make_radio("radio_S2_WT1800", "WT1800", parent=self)
        self.radioButton_S2_WT1806E = self._make_radio("radio_S2_WT1806E", "WT1806E", parent=self)
        self.radioButton_S2_WT5000 = self._make_radio("radio_S2_WT5000", "WT5000", parent=self)

        self._wt_radio_group = QtWidgets.QButtonGroup(None)
        self._wt_radio_group.addButton(self.radioButton_S2_WT3000, 0)
        self._wt_radio_group.addButton(self.radioButton_S2_WT1800, 1)
        self._wt_radio_group.addButton(self.radioButton_S2_WT1806E, 2)
        self._wt_radio_group.addButton(self.radioButton_S2_WT5000, 3)

        radio_layout = QtWidgets.QHBoxLayout()
        radio_layout.setSpacing(24)
        radio_layout.setContentsMargins(8, 0, 0, 0)
        for rb in [self.radioButton_S2_WT3000, self.radioButton_S2_WT1800,
                   self.radioButton_S2_WT1806E, self.radioButton_S2_WT5000]:
            radio_layout.addWidget(rb)
        radio_layout.addStretch()
        wtLayout.addLayout(radio_layout, 0, 0, 1, 3)

        # QStackedWidget 承载 4 个 WT 配置页面
        self._wtStacked = QtWidgets.QStackedWidget()
        self._wtStacked.addWidget(build_wt3000_content(self))   # index 0
        self._wtStacked.addWidget(build_wt1800_content(self))   # index 1
        self._wtStacked.addWidget(build_wt1806e_content(self))  # index 2
        self._wtStacked.addWidget(build_wt5000_content(self))   # index 3
        wtLayout.addWidget(self._wtStacked, 1, 0, 1, 4)

        # Radio 切换联动
        def _on_wt_radio_toggled(btn, checked):
            if checked:
                btn_id = self._wt_radio_group.id(btn)
                self._wtStacked.setCurrentIndex(btn_id)

        self._wt_radio_group.buttonToggled.connect(_on_wt_radio_toggled)

        # checkBox_S2 联动禁用 radio + stackedWidget 内容
        def _on_s2_toggled(checked):
            for rb in [self.radioButton_S2_WT3000, self.radioButton_S2_WT1800,
                       self.radioButton_S2_WT1806E, self.radioButton_S2_WT5000]:
                rb.setEnabled(checked)
            self._wtStacked.setEnabled(checked)

        self.checkBox_S2.toggled.connect(_on_s2_toggled)
        _on_s2_toggled(self.checkBox_S2.isChecked())

        layout.addWidget(wtGroup)

        # 数据采集设置
        dataGroup = QtWidgets.QGroupBox("数据采集设置")
        dataGroup.setStyleSheet(_GROUPBOX_STYLE)
        dataLayout = QtWidgets.QGridLayout(dataGroup)
        dataLayout.setSpacing(8)
        dataLayout.setContentsMargins(12, 20, 12, 12)

        dataLayout.addWidget(_make_label("数据采集"), 0, 0)
        self.textEdit_S3_TIME_2 = _make_input("5")
        self.textEdit_S3_TIME_2.setObjectName("textEdit_S3_TIME_2")
        dataLayout.addWidget(self.textEdit_S3_TIME_2, 0, 1)
        self.comboBox_S3_TIME_2 = _make_combo(["分钟", "秒", "毫秒"])
        self.comboBox_S3_TIME_2.setObjectName("comboBox_S3_TIME_2")
        dataLayout.addWidget(self.comboBox_S3_TIME_2, 0, 2)

        dataLayout.setColumnStretch(3, 1)
        layout.addWidget(dataGroup)

        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # 通用 DC 百分比步骤构建（Step 3-9）
    # ══════════════════════════════════════════════
    def _build_dc_percent_step(self, step_num, step_label, dc_pf_default, title_suffix,
                               has_dc4=False, has_ac_check=False):
        """构建一个 DC 百分比步骤页面。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 步骤开关
        cb_main = QtWidgets.QCheckBox(step_label)
        cb_main.setChecked(True)
        cb_main.setStyleSheet(
            "QCheckBox { font-size: 13px; font-weight: bold; color: #7c3aed; spacing: 6px; }"
            "QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; "
            "border: 1px solid #cbd5e1; background: white; }"
            "QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
        )
        setattr(self, f"checkBox_S{step_num}", cb_main)
        layout.addWidget(cb_main)

        # DC 组
        dcGroup = QtWidgets.QGroupBox(f"DC {title_suffix} - 直流电源设置")
        dcGroup.setStyleSheet(_GROUPBOX_STYLE)
        dcLayout = QtWidgets.QGridLayout(dcGroup)
        dcLayout.setSpacing(8)
        dcLayout.setContentsMargins(12, 20, 12, 12)

        # 表头
        dcLayout.addWidget(_make_title_label("电源"), 0, 0)
        dcLayout.addWidget(_make_title_label("功率"), 0, 1)
        dcLayout.addWidget(_make_title_label("%"), 0, 2)

        dc_rows = [
            (f"checkBox_S{step_num}_DC1", "直流电源1"),
            (f"checkBox_S{step_num}_DC2", "直流电源2"),
            (f"checkBox_S{step_num}_DC3", "直流电源3"),
        ]
        if has_dc4:
            dc_rows.append((f"checkBox_S{step_num}_DC4", "直流电源4"))

        for r, (cb_obj_name, cb_text) in enumerate(dc_rows, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setObjectName(cb_obj_name)
            cb.setChecked(True)
            cb.setStyleSheet(_CHECKBOX_STYLE)
            dcLayout.addWidget(cb, r, 0)
            setattr(self, cb_obj_name, cb)

            pf_te = _make_input(str(dc_pf_default))
            pf_te.setObjectName(f"textEdit_S{step_num}_DC_PF")
            dcLayout.addWidget(pf_te, r, 1)
            dcLayout.addWidget(_make_label("%"), r, 2)
            setattr(self, f"textEdit_S{step_num}_DC_PF", pf_te)

        dcLayout.setColumnStretch(3, 1)
        layout.addWidget(dcGroup)

        # AC 电压变更（仅 step 9）
        if has_ac_check:
            acGroup = QtWidgets.QGroupBox("交流电压变更")
            acGroup.setStyleSheet(_GROUPBOX_STYLE)
            acLayout = QtWidgets.QGridLayout(acGroup)
            acLayout.setSpacing(8)
            acLayout.setContentsMargins(12, 20, 12, 12)

            self.checkBox_S9_AC_Check = QtWidgets.QCheckBox("交流电压变更")
            self.checkBox_S9_AC_Check.setChecked(True)
            self.checkBox_S9_AC_Check.setObjectName("checkBox_S9_AC_Check")
            self.checkBox_S9_AC_Check.setStyleSheet(_CHECKBOX_STYLE)
            acLayout.addWidget(self.checkBox_S9_AC_Check, 0, 0)

            acLayout.addWidget(_make_label("电压"), 0, 1)
            self.textEdit_S9_AC_Volt = _make_input("217.8")
            self.textEdit_S9_AC_Volt.setObjectName("textEdit_S9_AC_Volt")
            acLayout.addWidget(self.textEdit_S9_AC_Volt, 0, 2)
            acLayout.addWidget(_make_label("V"), 0, 3)

            acLayout.setColumnStretch(4, 1)
            layout.addWidget(acGroup)

        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _build_cosPhi_steps(self):
        """构建合并的 cosPhi 设置页面，7 个 cosPhi 卡片平铺在滚动区域中。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 滚动区域承载所有 cosPhi 卡片
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(8)

        cosPhi_configs = [
            (3,  "step3", 10, "DC 10%",  True, False),
            (4,  "step4", 20, "DC 20%",  True, False),
            (5,  "step5", 30, "DC 30%",  True, False),
            (6,  "step6", 50, "DC 50%",  True, False),
            (7,  "step7", 75, "DC 75%",  True, False),
            (8,  "step8", 100, "DC 100%", True, False),
            (9,  "step9", 100, "AC 100%", True, True),
        ]

        for step_num, step_label, dc_pf, title, has_dc4, has_ac in cosPhi_configs:
            card = self._build_cosPhi_card(step_num, step_label, dc_pf, title, has_dc4, has_ac)
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self.stackedWidget.addWidget(page)

    def _build_cosPhi_card(self, step_num, step_label, dc_pf_default, title_suffix,
                           has_dc4=False, has_ac_check=False):
        """构建单个 cosPhi 卡片。"""
        card = QtWidgets.QWidget()
        card.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 步骤开关
        cb_main = QtWidgets.QCheckBox(step_label)
        cb_main.setChecked(True)
        cb_main.setStyleSheet(
            "QCheckBox { font-size: 13px; font-weight: bold; color: #7c3aed; spacing: 6px; }"
            "QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; "
            "border: 1px solid #cbd5e1; background: white; }"
            "QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
        )
        setattr(self, f"checkBox_S{step_num}", cb_main)
        layout.addWidget(cb_main)

        # DC 组
        dcGroup = QtWidgets.QGroupBox(f"DC {title_suffix} - 直流电源设置")
        dcGroup.setStyleSheet(_GROUPBOX_STYLE)
        dcLayout = QtWidgets.QGridLayout(dcGroup)
        dcLayout.setSpacing(8)
        dcLayout.setContentsMargins(12, 20, 12, 12)

        # 表头
        dcLayout.addWidget(_make_title_label("电源"), 0, 0)
        dcLayout.addWidget(_make_title_label("功率"), 0, 1)
        dcLayout.addWidget(_make_title_label("%"), 0, 2)

        dc_rows = [
            (f"checkBox_S{step_num}_DC1", "直流电源1"),
            (f"checkBox_S{step_num}_DC2", "直流电源2"),
            (f"checkBox_S{step_num}_DC3", "直流电源3"),
        ]
        if has_dc4:
            dc_rows.append((f"checkBox_S{step_num}_DC4", "直流电源4"))

        for r, (cb_obj_name, cb_text) in enumerate(dc_rows, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setObjectName(cb_obj_name)
            cb.setChecked(True)
            cb.setStyleSheet(_CHECKBOX_STYLE)
            dcLayout.addWidget(cb, r, 0)
            setattr(self, cb_obj_name, cb)

            pf_te = _make_input(str(dc_pf_default))
            pf_te.setObjectName(f"textEdit_S{step_num}_DC_PF")
            dcLayout.addWidget(pf_te, r, 1)
            dcLayout.addWidget(_make_label("%"), r, 2)
            setattr(self, f"textEdit_S{step_num}_DC_PF", pf_te)

        dcLayout.setColumnStretch(3, 1)
        layout.addWidget(dcGroup)

        # AC 电压变更（仅 step 9）
        if has_ac_check:
            acGroup = QtWidgets.QGroupBox("交流电压变更")
            acGroup.setStyleSheet(_GROUPBOX_STYLE)
            acLayout = QtWidgets.QGridLayout(acGroup)
            acLayout.setSpacing(8)
            acLayout.setContentsMargins(12, 20, 12, 12)

            self.checkBox_S9_AC_Check = QtWidgets.QCheckBox("交流电压变更")
            self.checkBox_S9_AC_Check.setChecked(True)
            self.checkBox_S9_AC_Check.setObjectName("checkBox_S9_AC_Check")
            self.checkBox_S9_AC_Check.setStyleSheet(_CHECKBOX_STYLE)
            acLayout.addWidget(self.checkBox_S9_AC_Check, 0, 0)

            acLayout.addWidget(_make_label("电压"), 0, 1)
            self.textEdit_S9_AC_Volt = _make_input("217.8")
            self.textEdit_S9_AC_Volt.setObjectName("textEdit_S9_AC_Volt")
            acLayout.addWidget(self.textEdit_S9_AC_Volt, 0, 2)
            acLayout.addWidget(_make_label("V"), 0, 3)

            acLayout.setColumnStretch(4, 1)
            layout.addWidget(acGroup)

        layout.addStretch()
        return card

    # ══════════════════════════════════════════════
    # Step 10: 关机设置
    # ══════════════════════════════════════════════
    def _build_step_last(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 步骤开关
        self.checkBox_S_END = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_END.setChecked(True)
        self.checkBox_S_END.setStyleSheet(
            "QCheckBox { font-size: 13px; font-weight: bold; color: #7c3aed; spacing: 6px; }"
            "QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; "
            "border: 1px solid #cbd5e1; background: white; }"
            "QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
        )
        layout.addWidget(self.checkBox_S_END)

        # 关机组
        endGroup = QtWidgets.QGroupBox("关机设置")
        endGroup.setStyleSheet(_GROUPBOX_STYLE)
        endLayout = QtWidgets.QGridLayout(endGroup)
        endLayout.setSpacing(10)
        endLayout.setContentsMargins(12, 20, 12, 12)

        # AC 电源
        endLayout.addWidget(_make_title_label("交流电源"), 0, 0)
        self.comboBox_S_END_AC = _make_combo(["关闭", "开启"])
        self.comboBox_S_END_AC.setObjectName("comboBox_S_END_AC")
        endLayout.addWidget(self.comboBox_S_END_AC, 0, 1)

        # DC 电源 1-4
        dc_end_data = [
            ("checkBox_S_END_DC1", "直流电源1", "comboBox_S_END_DC1"),
            ("checkBox_S_END_DC2", "直流电源2", "comboBox_S_END_DC2"),
            ("checkBox_S_END_DC3", "直流电源3", "comboBox_S_END_DC3"),
            ("checkBox_S_END_DC4", "直流电源4", "comboBox_S_END_DC4"),
        ]
        for r, (cb_name, cb_text, combo_name) in enumerate(dc_end_data, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setObjectName(cb_name)
            cb.setChecked(True)
            cb.setStyleSheet(_CHECKBOX_STYLE)
            endLayout.addWidget(cb, r, 0)
            setattr(self, cb_name, cb)

            combo = _make_combo(["关闭", "开启"])
            combo.setObjectName(combo_name)
            endLayout.addWidget(combo, r, 1)
            setattr(self, combo_name, combo)

        endLayout.setColumnStretch(2, 1)
        layout.addWidget(endGroup)

        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # 翻译
    # ══════════════════════════════════════════════
    def _connect_dc_linkage(self):
        """连接 step1 DC 复选框与 step4-9 及关机步骤 DC 复选框的联动。"""
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        # step4-9 DC 联动
        for step_num in [4, 5, 6, 7, 8, 9]:
            step_cb = getattr(self, f"checkBox_S{step_num}", None)
            if step_cb is None:
                continue
            step_dcs = []
            for dc_idx in range(1, 5):
                cb = getattr(self, f"checkBox_S{step_num}_DC{dc_idx}", None)
                if cb is not None:
                    step_dcs.append(cb)
            if not step_dcs:
                continue

            def _make_update_dcs(scb, sdcs, s1dcs):
                def _update(_checked=None):
                    step_on = scb.isChecked()
                    for i in range(len(sdcs)):
                        should_enable = step_on and s1dcs[i].isChecked()
                        sdcs[i].setEnabled(should_enable)
                        sdcs[i].setChecked(should_enable)
                return _update

            update_fn = _make_update_dcs(step_cb, step_dcs, step1_dcs)
            step_cb.toggled.connect(update_fn)
            for s1dc in step1_dcs:
                s1dc.toggled.connect(update_fn)
            update_fn()

        # 关机步骤 DC 联动
        end_dcs = [self.checkBox_S_END_DC1, self.checkBox_S_END_DC2,
                   self.checkBox_S_END_DC3, self.checkBox_S_END_DC4]
        end_combos = [self.comboBox_S_END_DC1, self.comboBox_S_END_DC2,
                      self.comboBox_S_END_DC3, self.comboBox_S_END_DC4]

        def _update_end_dc(_checked=None):
            step_on = self.checkBox_S_END.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                end_dcs[i].setEnabled(should_enable)
                end_dcs[i].setChecked(should_enable)
                end_combos[i].setEnabled(should_enable)

        self.checkBox_S_END.toggled.connect(_update_end_dc)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_end_dc)
        _update_end_dc()

    def retranslateUi(self, Dialog_thaicosPhi_Brazil):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaicosPhi_Brazil.setWindowTitle(
            _translate("Dialog_thaicosPhi_Brazil", "巴西CosPhi项目配置")
        )
