# -*- coding: utf-8 -*-
# PU项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.dewetron_autotest_panel import AnalyzerModeSection
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)

# 全局样式
_QSS_COMMON = """
QTextEdit {
    background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px;
    padding: 2px 4px; font-size: 12px; color: #1e293b;
}
QTextEdit:focus { border-color: #8b5cf6; }
QComboBox {
    background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px;
    padding: 4px 8px; font-size: 12px; color: #1e293b;
}
QComboBox:hover { border-color: #cbd5e1; }
QComboBox::drop-down { border: none; width: 20px; }
QCheckBox { font-size: 12px; color: #1e293b; spacing: 6px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 2px solid #cbd5e1; background: white; }
QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }
QLabel { font-size: 12px; color: #475569; }
QPushButton {
    background-color: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px;
    padding: 6px 12px; font-size: 12px; color: #1e293b;
}
QPushButton:hover { background-color: #e2e8f0; }
"""


class Ui_Dialog_thaitestPU(object):
    def setupUi(self, Dialog_thaitestPU):
        Dialog_thaitestPU.setObjectName("Dialog_thaitestPU")
        Dialog_thaitestPU.resize(1300, 850)
        Dialog_thaitestPU.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaitestPU.setWindowIcon(icon)
        Dialog_thaitestPU.setStyleSheet("QDialog { background-color: #f1f5f9; }")

        # ── 主布局 ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaitestPU)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪+PU", "③ PU 测试", "④ 关机设置"]
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
        self._build_pu_steps()
        self._build_step_shutdown()

        # 默认显示第一页
        self._switch_step(0)

        # DC 联动
        self._connect_dc_linkage()

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaitestPU)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaitestPU)

    def _integrate_analyzer_mode(self, layout, wt_group):
        """Wrap the existing WT controls with the shared WT/DEWETRON selector."""
        self.analyzerModeSection = AnalyzerModeSection(wt_group, self.checkBox_S2)
        self.dewetronPanel = self.analyzerModeSection.dewetron_panel
        self.radio_wt3000 = self.analyzerModeSection.radio_wt
        self.radio_dewetron = self.analyzerModeSection.radio_dewetron
        self._mode = self.analyzerModeSection.current_mode()
        self.analyzerModeSection.mode_changed.connect(
            lambda mode: setattr(self, "_mode", mode)
        )
        for name in (
            "pushButton_DEW_TestApply", "pushButton_DEW_RefreshFields",
            "pushButton_DEW_DataViewer", "comboBox_DEW_MaxRefreshRate",
            "spinBox_DEW_DecimalPlaces", "checkBox_DEW_RealtimeWaveform",
            "treeWidget_DEW_ExportFields",
        ):
            setattr(self, name, getattr(self.dewetronPanel, name))
        self.get_checked_export_fields = self.dewetronPanel.get_checked_export_fields
        self.refresh_export_field_tree = self.dewetronPanel.refresh_export_field_tree
        self.set_checked_export_fields = self.dewetronPanel.set_checked_export_fields
        self.get_checked_fields = self.get_checked_export_fields
        self.refresh_checked_fields = self.refresh_export_field_tree
        self.set_checked_fields = self.set_checked_export_fields
        layout.addWidget(self.analyzerModeSection)


    # ══════════════════════════════════════════════
    # 步骤切换
    # ══════════════════════════════════════════════
    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 8px; font-size: 10px; font-weight: bold; color: #7c3aed;
                        border-bottom: 3px solid #8b5cf6; border-radius: 0;
                        background-color: #f3e8ff;
                    }
                """)
            else:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 8px; font-size: 10px; color: #64748b;
                        border-bottom: 3px solid transparent; border-radius: 0;
                        background: transparent;
                    }
                    QLabel:hover { background-color: #f1f5f9; }
                """)

    def _group_box_style(self):
        return "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }"

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
    # Step 1: AC/DC 电源设置 + 时序
    # ══════════════════════════════════════════════
    def _build_step1(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── AC 电源组 ──
        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("交流电源设置")
        self.groupBox.setStyleSheet(self._group_box_style())
        gLayout = QtWidgets.QGridLayout(self.groupBox)
        gLayout.setSpacing(8)
        gLayout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        gLayout.addWidget(self.checkBox_S1, 0, 0, 1, 2)

        self.label_3 = QtWidgets.QLabel("交流电源")
        self.label_3.setObjectName("label_3")
        gLayout.addWidget(self.label_3, 0, 2)

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        gLayout.addWidget(self.label_4, 0, 3)
        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(100, 31)
        gLayout.addWidget(self.textEdit_S1_AC_VOLT, 0, 4)
        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        gLayout.addWidget(self.label_5, 0, 5)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        gLayout.addWidget(self.label_113, 0, 6)
        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setAcceptDrops(True)
        self.textEdit_S1_AC_VOLT_2.setUndoRedoEnabled(True)
        self.textEdit_S1_AC_VOLT_2.setReadOnly(False)
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(100, 31)
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 7)
        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        gLayout.addWidget(self.label_107, 0, 8)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        gLayout.addWidget(self.label_123, 0, 9)
        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setReadOnly(False)
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(100, 31)
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_3, 0, 10)
        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        gLayout.addWidget(self.label_102, 0, 11)

        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        gLayout.addWidget(self.label_19, 0, 12)
        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(100, 31)
        gLayout.addWidget(self.textEdit_S1_AC_FR, 0, 13)
        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        gLayout.addWidget(self.label_18, 0, 14)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S1_AC, 1, 3, 1, 2)

        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S1_AC_2, 1, 6, 1, 2)

        layout.addWidget(self.groupBox)

        # ── DC 电源组 (4 channels) ──
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流电源设置")
        self.groupBox_2.setStyleSheet(self._group_box_style())
        g2 = QtWidgets.QGridLayout(self.groupBox_2)
        g2.setSpacing(6)
        g2.setContentsMargins(12, 20, 12, 12)

        # Header
        headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
        for c, h in enumerate(headers):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g2.addWidget(lbl, 0, c)

        dc_cfg = [
            ("checkBox_S1_DC1", "直流电源1", "comboBox_S1_DC1",
             ["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc",
              "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"]),
            ("checkBox_S1_DC2", "直流电源2", "comboBox_S1_DC2",
             ["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc",
              "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"]),
            ("checkBox_S1_DC3", "直流电源3", "comboBox_S1_DC3",
             ["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc",
              "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"]),
            ("checkBox_S1_DC4", "直流电源4", "comboBox_S1_DC4",
             ["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc",
              "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"]),
        ]
        for r, (cb_name, cb_text, combo_name, te_names) in enumerate(dc_cfg, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g2.addWidget(cb, r, 0)
            setattr(self, cb_name, cb)
            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["开启", "关闭"])
            combo.setFixedWidth(100)
            g2.addWidget(combo, r, 1)
            setattr(self, combo_name, combo)
            for c, te_name in enumerate(te_names, start=2):
                te = QtWidgets.QTextEdit()
                te.setObjectName(te_name)
                te.setFixedSize(80, 28)
                if hasattr(te, "setTabChangesFocus"):
                    te.setTabChangesFocus(True)
                g2.addWidget(te, r, c)
                setattr(self, te_name, te)

        layout.addWidget(self.groupBox_2)

        # ── 时序组 ──
        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("时序设置")
        self.groupBox_4.setStyleSheet(self._group_box_style())
        g4 = QtWidgets.QGridLayout(self.groupBox_4)
        g4.setSpacing(8)
        g4.setContentsMargins(12, 20, 12, 12)

        self.label_131 = QtWidgets.QLabel("等待时间:")
        self.label_131.setObjectName("label_131")
        g4.addWidget(self.label_131, 0, 0)
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(100, 31)
        self.textEdit_S1_ACWaitTIME.setText("5")
        g4.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(120)
        g4.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        self.label_132 = QtWidgets.QLabel("启机时间:")
        self.label_132.setObjectName("label_132")
        g4.addWidget(self.label_132, 0, 3)
        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(100, 31)
        self.textEdit_S1_TIME.setText("5")
        g4.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(120)
        g4.addWidget(self.comboBox_S1_TIME, 0, 5)

        layout.addWidget(self.groupBox_4)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 2: 功率分析仪设置
    # ══════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_5 = QtWidgets.QGroupBox()
        self.groupBox_5.setObjectName("groupBox_5")
        self.groupBox_5.setTitle("功率分析仪配置")
        self.groupBox_5.setStyleSheet(self._group_box_style())
        g5 = QtWidgets.QGridLayout(self.groupBox_5)
        g5.setSpacing(10)
        g5.setContentsMargins(16, 24, 16, 12)

        # 步骤启用复选框
        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        g5.addWidget(self.checkBox_S2, 0, 0)

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
        g5.addLayout(radio_layout, 0, 1, 1, 3)

        # QStackedWidget 承载 4 个 WT 配置页面
        self._wtStacked = QtWidgets.QStackedWidget()
        self._wtStacked.addWidget(build_wt3000_content(self))   # index 0
        self._wtStacked.addWidget(build_wt1800_content(self))   # index 1
        self._wtStacked.addWidget(build_wt1806e_content(self))  # index 2
        self._wtStacked.addWidget(build_wt5000_content(self))   # index 3
        g5.addWidget(self._wtStacked, 1, 0, 1, 4)

        # Radio 切换联动
        def _on_wt_radio_toggled(btn, checked):
            if checked:
                btn_id = self._wt_radio_group.id(btn)
                self._wtStacked.setCurrentIndex(btn_id)

        self._wt_radio_group.buttonToggled.connect(_on_wt_radio_toggled)

        self._integrate_analyzer_mode(layout, self.groupBox_5)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # PU 步骤（合并）：滚动列表平铺展示
    # ══════════════════════════════════════════════

    def _build_pu_steps(self):
        """构建合并的 PU 测试页面：优先电压 list 连续录；旧 20 卡为备用。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 步骤启用复选框
        self.checkBox_S_PU = QtWidgets.QCheckBox("PU 测试")
        self.checkBox_S_PU.setChecked(True)
        self.checkBox_S_PU.setObjectName("checkBox_S_PU")
        layout.addWidget(self.checkBox_S_PU)

        # P(U) 电压 LIST：与静态 QU 同写法，连续录 1 条 PU_curve（测有功 P）
        _DEFAULT_U_LIST = (
            "100,103,105,106,107,108,110,112,115,"
            "112,110,108,107,106,105,103,100,"
            "97,94,93,90,87,85"
        )
        ladder_grp = QtWidgets.QGroupBox("P(U) 电压 list（连续录 1 条 PU_curve）")
        ladder_grp.setStyleSheet(self._group_box_style())
        ladder_layout = QtWidgets.QGridLayout(ladder_grp)
        ladder_layout.setSpacing(8)
        ladder_layout.setContentsMargins(12, 20, 12, 12)

        ladder_layout.addWidget(QtWidgets.QLabel("Un基准(V)："), 0, 0)
        self.textEdit_VoltageLadder_Un = QtWidgets.QTextEdit()
        self.textEdit_VoltageLadder_Un.setObjectName("textEdit_VoltageLadder_Un")
        self.textEdit_VoltageLadder_Un.setFixedSize(80, 28)
        self.textEdit_VoltageLadder_Un.setText("230")
        ladder_layout.addWidget(self.textEdit_VoltageLadder_Un, 0, 1)
        ladder_layout.addWidget(QtWidgets.QLabel("频率(Hz)："), 0, 2)
        self.textEdit_VoltageLadder_FR = QtWidgets.QTextEdit()
        self.textEdit_VoltageLadder_FR.setObjectName("textEdit_VoltageLadder_FR")
        self.textEdit_VoltageLadder_FR.setFixedSize(80, 28)
        self.textEdit_VoltageLadder_FR.setText("50")
        ladder_layout.addWidget(self.textEdit_VoltageLadder_FR, 0, 3)

        ladder_layout.addWidget(QtWidgets.QLabel("电压Un%(list)："), 1, 0)
        self.textEdit_VoltageLadder = QtWidgets.QTextEdit()
        self.textEdit_VoltageLadder.setObjectName("textEdit_VoltageLadder")
        self.textEdit_VoltageLadder.setFixedHeight(28)
        self.textEdit_VoltageLadder.setText(_DEFAULT_U_LIST)
        self.textEdit_VoltageLadder.setPlaceholderText("先升再降，如 100…115…85；连续录 PU_curve")
        ladder_layout.addWidget(self.textEdit_VoltageLadder, 1, 1, 1, 3)

        ladder_layout.addWidget(QtWidgets.QLabel("每点驻留："), 2, 0)
        self.textEdit_VoltageLadder_TIME = QtWidgets.QTextEdit()
        self.textEdit_VoltageLadder_TIME.setObjectName("textEdit_VoltageLadder_TIME")
        self.textEdit_VoltageLadder_TIME.setFixedSize(80, 28)
        self.textEdit_VoltageLadder_TIME.setText("1")
        self.textEdit_VoltageLadder_TIME.setToolTip("每个 Un% 保持时间；WT 全程连续录，不停表")
        ladder_layout.addWidget(self.textEdit_VoltageLadder_TIME, 2, 1)
        self.comboBox_VoltageLadder_TIME = QtWidgets.QComboBox()
        self.comboBox_VoltageLadder_TIME.setObjectName("comboBox_VoltageLadder_TIME")
        self.comboBox_VoltageLadder_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_VoltageLadder_TIME.setCurrentText("分钟")
        self.comboBox_VoltageLadder_TIME.setFixedWidth(80)
        ladder_layout.addWidget(self.comboBox_VoltageLadder_TIME, 2, 2)
        tip = QtWidgets.QLabel(
            "只填电压 list（同静态QU）。逐点改网压，有功由机侧 P(U)/降载特性产生，WT 连续录一条曲线。"
            "Pn 工况由步骤① DC 保持。"
        )
        tip.setStyleSheet("color: #64748b; font-weight: normal; font-size: 11px;")
        tip.setWordWrap(True)
        ladder_layout.addWidget(tip, 3, 0, 1, 4)
        layout.addWidget(ladder_grp)

        legacy_tip = QtWidgets.QLabel("下方为旧「逐点卡片」模式：仅当上方电压 list 为空时才使用")
        legacy_tip.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(legacy_tip)

        # 滚动区域承载所有 PU 卡片
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(8)

        for n in range(3, 23):
            card = self._build_pu_card(n)
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # checkBox_S_PU 联动禁用 list + 滚动区域
        def _on_pu_toggled(checked):
            ladder_grp.setEnabled(checked)
            scroll.setEnabled(checked)

        self.checkBox_S_PU.toggled.connect(_on_pu_toggled)
        _on_pu_toggled(self.checkBox_S_PU.isChecked())

        self.stackedWidget.addWidget(page)

    def _build_pu_card(self, n):
        """构建单个 PU 卡片（n=3..22，对应 PU 1..20）。"""
        card = QtWidgets.QWidget()
        card.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        groupBox = QtWidgets.QGroupBox()
        groupBox.setObjectName(f"groupBox_PU{n}")
        groupBox.setTitle(f"PU {n - 2} 设置")
        groupBox.setStyleSheet(self._group_box_style())
        gLayout = QtWidgets.QGridLayout(groupBox)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        # checkbox
        checkBox = QtWidgets.QCheckBox(f"step{n}")
        checkBox.setChecked(True)
        checkBox.setObjectName(f"checkBox_S{n}")
        gLayout.addWidget(checkBox, 0, 0)
        setattr(self, f"checkBox_S{n}", checkBox)

        # 交流电压
        lbl_volt = QtWidgets.QLabel("交流电压")
        lbl_volt.setObjectName(f"label_{n * 10 + 1}")
        gLayout.addWidget(lbl_volt, 0, 1)
        textEdit_ac_volt = QtWidgets.QTextEdit()
        textEdit_ac_volt.setObjectName(f"textEdit_S{n}_AC_VOLT")
        textEdit_ac_volt.setFixedSize(100, 31)
        textEdit_ac_volt.setText("230")
        gLayout.addWidget(textEdit_ac_volt, 0, 2)
        setattr(self, f"textEdit_S{n}_AC_VOLT", textEdit_ac_volt)
        lbl_v = QtWidgets.QLabel("V")
        lbl_v.setObjectName(f"label_{n * 10 + 2}")
        gLayout.addWidget(lbl_v, 0, 3)

        # 数据采集时间
        lbl_time = QtWidgets.QLabel("数据采集")
        lbl_time.setObjectName(f"label_{n * 10 + 3}")
        gLayout.addWidget(lbl_time, 1, 1)
        textEdit_time = QtWidgets.QTextEdit()
        textEdit_time.setObjectName(f"textEdit_S{n}_TIME")
        textEdit_time.setFixedSize(100, 31)
        textEdit_time.setText("5")
        gLayout.addWidget(textEdit_time, 1, 2)
        setattr(self, f"textEdit_S{n}_TIME", textEdit_time)
        comboBox_time = QtWidgets.QComboBox()
        comboBox_time.setObjectName(f"comboBox_S{n}_TIME")
        comboBox_time.addItems(["秒", "毫秒", "分钟"])
        comboBox_time.setFixedWidth(120)
        gLayout.addWidget(comboBox_time, 1, 3)
        setattr(self, f"comboBox_S{n}_TIME", comboBox_time)

        layout.addWidget(groupBox)
        layout.addStretch()
        return card

        layout.addWidget(groupBox)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step last: 关机设置
    # ══════════════════════════════════════════════
    def _build_step_shutdown(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_11 = QtWidgets.QGroupBox()
        self.groupBox_11.setObjectName("groupBox_11")
        self.groupBox_11.setTitle("关机设置")
        self.groupBox_11.setStyleSheet(self._group_box_style())
        g11 = QtWidgets.QGridLayout(self.groupBox_11)
        g11.setSpacing(10)
        g11.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S_End = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_End.setChecked(True)
        self.checkBox_S_End.setObjectName("checkBox_S_End")
        g11.addWidget(self.checkBox_S_End, 0, 0, 1, 2)

        self.label_8 = QtWidgets.QLabel("交流电源")
        self.label_8.setObjectName("label_8")
        g11.addWidget(self.label_8, 0, 2)
        self.comboBox_S_End_AC = QtWidgets.QComboBox()
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItems(["关闭", "开启"])
        self.comboBox_S_End_AC.setCurrentText("关闭")
        self.comboBox_S_End_AC.setFixedWidth(120)
        g11.addWidget(self.comboBox_S_End_AC, 0, 3)

        # DC 电源 1-4
        dc_end_cfg = [
            ("checkBox_S_End_DC1", "直流电源1", "comboBox_S_End_DC1"),
            ("checkBox_S_End_DC2", "直流电源2", "comboBox_S_End_DC2"),
            ("checkBox_S_End_DC3", "直流电源3", "comboBox_S_End_DC3"),
            ("checkBox_S_End_DC4", "直流电源4", "comboBox_S_End_DC4"),
        ]
        for c, (cb_name, cb_text, combo_name) in enumerate(dc_end_cfg):
            col = c * 2
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g11.addWidget(cb, 1, col)
            setattr(self, cb_name, cb)
            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["关闭", "开启"])
            combo.setCurrentText("关闭")
            combo.setFixedWidth(120)
            g11.addWidget(combo, 1, col + 1)
            setattr(self, combo_name, combo)

        layout.addWidget(self.groupBox_11)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _connect_dc_linkage(self):
        """连接 step1 DC 复选框与关机步骤 DC 复选框的联动。"""
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        # 关机步骤 DC 联动
        end_dcs = [self.checkBox_S_End_DC1, self.checkBox_S_End_DC2,
                   self.checkBox_S_End_DC3, self.checkBox_S_End_DC4]
        end_combos = [self.comboBox_S_End_DC1, self.comboBox_S_End_DC2,
                      self.comboBox_S_End_DC3, self.comboBox_S_End_DC4]

        def _update_end_dc(_checked=None):
            step_on = self.checkBox_S_End.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                end_dcs[i].setEnabled(should_enable)
                end_dcs[i].setChecked(should_enable)
                end_combos[i].setEnabled(should_enable)

        self.checkBox_S_End.toggled.connect(_update_end_dc)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_end_dc)
        _update_end_dc()

    def retranslateUi(self, Dialog_thaitestPU):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaitestPU.setWindowTitle(
            _translate("Dialog_thaitestPU", "PU项目配置")
        )
        self.pushButton_TestAppend.setText(
            _translate("Dialog_thaitestPU", "测试追加")
        )
        self.pushButton_SaveSettingFile.setText(
            _translate("Dialog_thaitestPU", "保存设定")
        )
        self.pushButton_ReadSettingFile.setText(
            _translate("Dialog_thaitestPU", "读取设定")
        )
        self.pushButton_Send.setText(
            _translate("Dialog_thaitestPU", "提交")
        )
