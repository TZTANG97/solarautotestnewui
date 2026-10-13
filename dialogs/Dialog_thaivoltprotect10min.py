# -*- coding: utf-8 -*-
# 10min过压保护项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.dewetron_autotest_panel import AnalyzerModeSection
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)


class Ui_Dialog_thaivoltprotect10min(object):
    def setupUi(self, Dialog_thaivoltprotect10min):
        Dialog_thaivoltprotect10min.setObjectName("Dialog_thaivoltprotect10min")
        Dialog_thaivoltprotect10min.resize(1300, 850)
        Dialog_thaivoltprotect10min.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaivoltprotect10min.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaivoltprotect10min)
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

        # 按钮组
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

        # 分隔线
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        sep.setStyleSheet("color: #cbd5e1; border: none; max-width: 1px;")
        topLayout.addWidget(sep)

        # 项目设置标题 + 计数器
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

        stdLabel = QtWidgets.QLabel("国家标准")
        stdLabel.setStyleSheet(
            "font-size: 12px; color: #475569; background: transparent; border: none;"
        )
        topLayout.addWidget(stdLabel)
        self.comboBox_SolarStandard = QtWidgets.QComboBox()
        self.comboBox_SolarStandard.setObjectName("comboBox_SolarStandard")
        self.comboBox_SolarStandard.setFixedWidth(168)
        self.comboBox_SolarStandard.setStyleSheet(
            "QComboBox { font-size: 12px; padding: 2px 6px; background: white; }"
        )
        try:
            from utils.iot_voltprotect10min_standard import list_voltprotect10min_standard_options

            for opt in list_voltprotect10min_standard_options():
                self.comboBox_SolarStandard.addItem(str(opt["label"]), str(opt["id"]))
        except Exception:
            self.comboBox_SolarStandard.addItem("泰国 PEA/MEA（现行）", "thai")
        self.comboBox_SolarStandard.setCurrentIndex(0)
        self._solar_standard = "thai"
        self.comboBox_SolarStandard.currentIndexChanged.connect(self._on_solar_standard_changed)
        topLayout.addWidget(self.comboBox_SolarStandard)

        topLayout.addStretch()

        # 横向步骤指示器
        self._step_labels = []
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ 过压保护", "④ 保护后恢复", "⑤ 关机设置"]
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

        # ══════════════════════════════════════
        # QStackedWidget（内容区）
        # ══════════════════════════════════════
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setStyleSheet("background-color: white;")
        mainLayout.addWidget(self.stackedWidget, 1)

        # ── 构建各步骤页面 ──
        self._build_step1()
        self._build_step2()
        self._build_step3()
        self._build_step4()
        self._build_step5()

        # ── DC 联动（step1 → 关机步骤） ──
        self._connect_dc_linkage()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaivoltprotect10min)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaivoltprotect10min)

    def set_solar_standard(self, standard_id, *, apply_defaults=False):
        try:
            from utils.iot_voltprotect10min_standard import apply_voltprotect10min_standard_to_ui

            apply_voltprotect10min_standard_to_ui(
                self,
                standard_id,
                force=True,
                apply_defaults=bool(apply_defaults),
            )
        except Exception:
            self._solar_standard = str(standard_id or "thai").strip() or "thai"

    def _on_solar_standard_changed(self, index):
        sid = self.comboBox_SolarStandard.itemData(index)
        if sid is None:
            sid = "thai"
        self.set_solar_standard(str(sid), apply_defaults=True)

    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 12px; font-size: 12px; font-weight: bold; color: #7c3aed;
                        border-bottom: 3px solid #8b5cf6; border-radius: 0;
                        background-color: #f3e8ff;
                    }
                """)
            else:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 12px; font-size: 12px; color: #64748b;
                        border-bottom: 3px solid transparent; border-radius: 0;
                        background: transparent;
                    }
                    QLabel:hover { background-color: #f1f5f9; }
                """)

    def _make_radio(self, name, text, parent=None, checked=False):
        """创建 QRadioButton，不调用 setParent（Dialog 不是 QWidget）。"""
        rb = QtWidgets.QRadioButton(text)
        rb.setObjectName(name)
        if parent is not None:
            setattr(self, name, rb)
        if checked:
            rb.setChecked(True)
        return rb

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
    # Step 1: AC + DC 电源设置 + 时序
    # ══════════════════════════════════════════════
    def _build_step1(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── AC 电源组 ──
        self.groupBox_6 = QtWidgets.QGroupBox()
        self.groupBox_6.setObjectName("groupBox_6")
        self.groupBox_6.setTitle("交流电源设置")
        self.groupBox_6.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g6Layout = QtWidgets.QGridLayout(self.groupBox_6)
        g6Layout.setSpacing(8)
        g6Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        g6Layout.addWidget(self.checkBox_S1, 0, 0, 1, 2)

        self.label_3 = QtWidgets.QLabel("交流电源")
        self.label_3.setObjectName("label_3")
        g6Layout.addWidget(self.label_3, 0, 2)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(120)
        g6Layout.addWidget(self.comboBox_S1_AC, 0, 3)

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        g6Layout.addWidget(self.label_4, 0, 4)

        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(100, 31)
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT, 0, 5)

        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        g6Layout.addWidget(self.label_5, 0, 6)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        g6Layout.addWidget(self.label_113, 0, 7)

        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(100, 31)
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 8)

        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        g6Layout.addWidget(self.label_107, 0, 9)

        # Row 2
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        g6Layout.addWidget(self.comboBox_S1_AC_2, 1, 3)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        g6Layout.addWidget(self.label_123, 1, 4)

        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(100, 31)
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 5)

        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        g6Layout.addWidget(self.label_102, 1, 6)

        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        g6Layout.addWidget(self.label_19, 1, 7)

        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(100, 31)
        g6Layout.addWidget(self.textEdit_S1_AC_FR, 1, 8)

        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        g6Layout.addWidget(self.label_18, 1, 9)

        layout.addWidget(self.groupBox_6)

        # ── DC 电源组 (4 channels) ──
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流电源设置")
        self.groupBox_2.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g2Layout = QtWidgets.QGridLayout(self.groupBox_2)
        g2Layout.setSpacing(6)
        g2Layout.setContentsMargins(12, 20, 12, 12)

        # Header：与静态 QU 一致，单位写在表头，每列一个输入框
        # 旧版把单位拆成独立列（12 列）却只放了 5 个输入，导致 Isc/功率列空白无法填写
        dc_headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
        for c, h in enumerate(dc_headers):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g2Layout.addWidget(lbl, 0, c)

        # DC channels: (row, cb, text, combo, VOLT, CURR, Voc, Isc, PF)
        dc_channels = [
            (1, "checkBox_S1_DC1", "直流电源1", "comboBox_S1_DC1",
             "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"),
            (2, "checkBox_S1_DC2", "直流电源2", "comboBox_S1_DC2",
             "textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"),
            (3, "checkBox_S1_DC3", "直流电源3", "comboBox_S1_DC3",
             "textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"),
            (4, "checkBox_S1_DC4", "直流电源4", "comboBox_S1_DC4",
             "textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"),
        ]

        for row, cb_name, cb_text, combo_name, volt_n, curr_n, voc_n, isc_n, pf_n in dc_channels:
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g2Layout.addWidget(cb, row, 0)
            setattr(self, cb_name, cb)

            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["开启", "关闭"])
            combo.setFixedWidth(100)
            g2Layout.addWidget(combo, row, 1)
            setattr(self, combo_name, combo)

            for c, name in enumerate([volt_n, curr_n, voc_n, isc_n, pf_n], start=2):
                te = QtWidgets.QTextEdit()
                te.setObjectName(name)
                te.setFixedSize(90, 28)
                te.setTabChangesFocus(True)
                g2Layout.addWidget(te, row, c)
                setattr(self, name, te)

        # 兼容旧 Open/Save 可能引用的 label objectName（不占布局）
        for lbl_name in (
            "label_13", "label_14", "label_15", "label_17", "label_118", "label_108",
            "label_109", "label_110", "label_106", "label_128", "label_104", "label_57",
            "label_120", "label_54", "label_119", "label_122", "label_53", "label_51",
            "label_56", "label_59", "label_124", "label_129", "label_112", "label_55",
            "label_125", "label_58", "label_127", "label_130", "label_126", "label_101",
            "label_105", "label_121", "label_116", "label_117", "label_115", "label_100",
            "label_103", "label_111", "label_114",
        ):
            if not hasattr(self, lbl_name):
                lbl = QtWidgets.QLabel("")
                lbl.setObjectName(lbl_name)
                setattr(self, lbl_name, lbl)

        layout.addWidget(self.groupBox_2)

        # ── 时序组 ──
        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("时序设置")
        self.groupBox_4.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g4Layout = QtWidgets.QGridLayout(self.groupBox_4)
        g4Layout.setSpacing(8)
        g4Layout.setContentsMargins(12, 20, 12, 12)

        self.label_131 = QtWidgets.QLabel("等待时间:")
        self.label_131.setObjectName("label_131")
        g4Layout.addWidget(self.label_131, 0, 0)
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(100, 31)
        self.textEdit_S1_ACWaitTIME.setText("3")
        g4Layout.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(120)
        g4Layout.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        self.label_132 = QtWidgets.QLabel("启机时间:")
        self.label_132.setObjectName("label_132")
        g4Layout.addWidget(self.label_132, 0, 3)
        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(100, 31)
        self.textEdit_S1_TIME.setText("5")
        g4Layout.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(120)
        g4Layout.addWidget(self.comboBox_S1_TIME, 0, 5)

        layout.addWidget(self.groupBox_4)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 2: 功率分析仪设置（radio + stackedWidget 内嵌）
    # ══════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_5 = QtWidgets.QGroupBox()
        self.groupBox_5.setObjectName("groupBox_5")
        self.groupBox_5.setTitle("功率分析仪设置")
        self.groupBox_5.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g5Layout = QtWidgets.QGridLayout(self.groupBox_5)
        g5Layout.setSpacing(10)
        g5Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        g5Layout.addWidget(self.checkBox_S2, 0, 0)

        # Radio buttons
        self.radioButton_S2_WT3000 = self._make_radio("radio_S2_WT3000", "WT3000", parent=self, checked=True)
        self.radioButton_S2_WT1800 = self._make_radio("radio_S2_WT1800", "WT1800", parent=self)
        self.radioButton_S2_WT1806E = self._make_radio("radio_S2_WT1806E", "WT1806E", parent=self)
        self.radioButton_S2_WT5000 = self._make_radio("radio_S2_WT5000", "WT5000", parent=self)

        radio_group = QtWidgets.QButtonGroup(None)
        radio_group.addButton(self.radioButton_S2_WT3000, 0)
        radio_group.addButton(self.radioButton_S2_WT1800, 1)
        radio_group.addButton(self.radioButton_S2_WT1806E, 2)
        radio_group.addButton(self.radioButton_S2_WT5000, 3)
        self._radio_group = radio_group  # 保持引用，防止垃圾回收

        # Radio 行布局
        radio_layout = QtWidgets.QHBoxLayout()
        for rb in [self.radioButton_S2_WT3000, self.radioButton_S2_WT1800,
                   self.radioButton_S2_WT1806E, self.radioButton_S2_WT5000]:
            radio_layout.addWidget(rb)
        radio_layout.addStretch()
        g5Layout.addLayout(radio_layout, 0, 1, 1, 3)

        # QStackedWidget
        self._wtStacked = QtWidgets.QStackedWidget()
        self._wtStacked.addWidget(build_wt3000_content(self))   # index 0
        self._wtStacked.addWidget(build_wt1800_content(self))   # index 1
        self._wtStacked.addWidget(build_wt1806e_content(self))  # index 2
        self._wtStacked.addWidget(build_wt5000_content(self))   # index 3
        g5Layout.addWidget(self._wtStacked, 1, 0, 1, 4)

        # Radio 切换联动
        def _on_radio_toggled(btn, checked):
            if checked:
                self._wtStacked.setCurrentIndex(radio_group.id(btn))
        radio_group.buttonToggled.connect(_on_radio_toggled)

        self._integrate_analyzer_mode(layout, self.groupBox_5)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 3: 过压保护
    # ══════════════════════════════════════════════

    def _build_step3(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_3 = QtWidgets.QGroupBox()
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setTitle("过压保护设置")
        self.groupBox_3.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g3Layout = QtWidgets.QGridLayout(self.groupBox_3)
        g3Layout.setSpacing(8)
        g3Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setChecked(True)
        self.checkBox_S3.setObjectName("checkBox_S3")
        g3Layout.addWidget(self.checkBox_S3, 0, 0)

        # Row 1: AC voltages
        self.label_20 = QtWidgets.QLabel("交流电源")
        self.label_20.setObjectName("label_20")
        g3Layout.addWidget(self.label_20, 1, 0)

        self.label_22 = QtWidgets.QLabel("交流电压L1")
        self.label_22.setObjectName("label_22")
        g3Layout.addWidget(self.label_22, 1, 1)

        self.textEdit_S3_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S3_AC_VOLT.setObjectName("textEdit_S3_AC_VOLT")
        self.textEdit_S3_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S3_AC_VOLT.setText("230")
        g3Layout.addWidget(self.textEdit_S3_AC_VOLT, 1, 2)

        self.label_21 = QtWidgets.QLabel("V/%")
        self.label_21.setObjectName("label_21")
        g3Layout.addWidget(self.label_21, 1, 3)

        self.label_29 = QtWidgets.QLabel("交流电压L2")
        self.label_29.setObjectName("label_29")
        g3Layout.addWidget(self.label_29, 1, 4)

        self.textEdit_S3_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S3_AC_VOLT_2.setObjectName("textEdit_S3_AC_VOLT_2")
        self.textEdit_S3_AC_VOLT_2.setFixedSize(100, 31)
        self.textEdit_S3_AC_VOLT_2.setText("230")
        g3Layout.addWidget(self.textEdit_S3_AC_VOLT_2, 1, 5)

        self.label_28 = QtWidgets.QLabel("V/%")
        self.label_28.setObjectName("label_28")
        g3Layout.addWidget(self.label_28, 1, 6)

        self.label_31 = QtWidgets.QLabel("交流电压L3")
        self.label_31.setObjectName("label_31")
        g3Layout.addWidget(self.label_31, 1, 7)

        self.textEdit_S3_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S3_AC_VOLT_3.setObjectName("textEdit_S3_AC_VOLT_3")
        self.textEdit_S3_AC_VOLT_3.setFixedSize(100, 31)
        self.textEdit_S3_AC_VOLT_3.setText("230")
        g3Layout.addWidget(self.textEdit_S3_AC_VOLT_3, 1, 8)

        self.label_30 = QtWidgets.QLabel("V/%")
        self.label_30.setObjectName("label_30")
        g3Layout.addWidget(self.label_30, 1, 9)

        tip3 = QtWidgets.QLabel("可填绝对电压(如257.6)或百分比(如112%)；% 相对①交流电压作 Un")
        tip3.setStyleSheet("color: #64748b; font-size: 11px;")
        tip3.setWordWrap(True)
        g3Layout.addWidget(tip3, 2, 0, 1, 10)

        # Row 3: Data collection time
        self.label_23 = QtWidgets.QLabel("数据采集")
        self.label_23.setObjectName("label_23")
        g3Layout.addWidget(self.label_23, 3, 0)

        self.textEdit_S3_TIME = QtWidgets.QTextEdit()
        self.textEdit_S3_TIME.setObjectName("textEdit_S3_TIME")
        self.textEdit_S3_TIME.setFixedSize(100, 31)
        self.textEdit_S3_TIME.setText("10")
        g3Layout.addWidget(self.textEdit_S3_TIME, 3, 1)

        self.comboBox_S3_TIME = QtWidgets.QComboBox()
        self.comboBox_S3_TIME.setObjectName("comboBox_S3_TIME")
        self.comboBox_S3_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S3_TIME.setFixedWidth(120)
        g3Layout.addWidget(self.comboBox_S3_TIME, 3, 2)

        layout.addWidget(self.groupBox_3)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 4: 保护后恢复
    # ══════════════════════════════════════════════
    def _build_step4(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("保护后恢复设置")
        self.groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(self.groupBox)
        gLayout.setSpacing(8)
        gLayout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S4 = QtWidgets.QCheckBox("step4")
        self.checkBox_S4.setChecked(True)
        self.checkBox_S4.setObjectName("checkBox_S4")
        gLayout.addWidget(self.checkBox_S4, 0, 0)

        # Row 1: AC voltages
        self.label_26 = QtWidgets.QLabel("交流电源")
        self.label_26.setObjectName("label_26")
        gLayout.addWidget(self.label_26, 1, 0)

        self.label_24 = QtWidgets.QLabel("交流电压L1")
        self.label_24.setObjectName("label_24")
        gLayout.addWidget(self.label_24, 1, 1)

        self.textEdit_S4_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S4_AC_VOLT.setObjectName("textEdit_S4_AC_VOLT")
        self.textEdit_S4_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S4_AC_VOLT.setText("230")
        gLayout.addWidget(self.textEdit_S4_AC_VOLT, 1, 2)

        self.label_27 = QtWidgets.QLabel("V/%")
        self.label_27.setObjectName("label_27")
        gLayout.addWidget(self.label_27, 1, 3)

        self.label_33 = QtWidgets.QLabel("交流电压L2")
        self.label_33.setObjectName("label_33")
        gLayout.addWidget(self.label_33, 1, 4)

        self.textEdit_S4_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S4_AC_VOLT_2.setObjectName("textEdit_S4_AC_VOLT_2")
        self.textEdit_S4_AC_VOLT_2.setFixedSize(100, 31)
        self.textEdit_S4_AC_VOLT_2.setText("230")
        gLayout.addWidget(self.textEdit_S4_AC_VOLT_2, 1, 5)

        self.label_32 = QtWidgets.QLabel("V/%")
        self.label_32.setObjectName("label_32")
        gLayout.addWidget(self.label_32, 1, 6)

        self.label_35 = QtWidgets.QLabel("交流电压L3")
        self.label_35.setObjectName("label_35")
        gLayout.addWidget(self.label_35, 1, 7)

        self.textEdit_S4_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S4_AC_VOLT_3.setObjectName("textEdit_S4_AC_VOLT_3")
        self.textEdit_S4_AC_VOLT_3.setFixedSize(100, 31)
        self.textEdit_S4_AC_VOLT_3.setText("230")
        gLayout.addWidget(self.textEdit_S4_AC_VOLT_3, 1, 8)

        self.label_34 = QtWidgets.QLabel("V/%")
        self.label_34.setObjectName("label_34")
        gLayout.addWidget(self.label_34, 1, 9)

        tip4 = QtWidgets.QLabel("可填绝对电压(如230)或百分比(如100%)；% 相对①交流电压作 Un")
        tip4.setStyleSheet("color: #64748b; font-size: 11px;")
        tip4.setWordWrap(True)
        gLayout.addWidget(tip4, 2, 0, 1, 10)

        # Row 3: Data collection time
        self.label_25 = QtWidgets.QLabel("数据采集")
        self.label_25.setObjectName("label_25")
        gLayout.addWidget(self.label_25, 3, 0)

        self.textEdit_S4_TIME = QtWidgets.QTextEdit()
        self.textEdit_S4_TIME.setObjectName("textEdit_S4_TIME")
        self.textEdit_S4_TIME.setFixedSize(100, 31)
        self.textEdit_S4_TIME.setText("3")
        gLayout.addWidget(self.textEdit_S4_TIME, 3, 1)

        self.comboBox_S4_TIME = QtWidgets.QComboBox()
        self.comboBox_S4_TIME.setObjectName("comboBox_S4_TIME")
        self.comboBox_S4_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S4_TIME.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S4_TIME, 3, 2)

        layout.addWidget(self.groupBox)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 5: 关机设置
    # ══════════════════════════════════════════════
    def _build_step5(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_11 = QtWidgets.QGroupBox()
        self.groupBox_11.setObjectName("groupBox_11")
        self.groupBox_11.setTitle("关机设置")
        self.groupBox_11.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g11Layout = QtWidgets.QGridLayout(self.groupBox_11)
        g11Layout.setSpacing(10)
        g11Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S_End = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_End.setChecked(True)
        self.checkBox_S_End.setObjectName("checkBox_S_End")
        g11Layout.addWidget(self.checkBox_S_End, 0, 0)

        self.label_8 = QtWidgets.QLabel("交流电源")
        self.label_8.setObjectName("label_8")
        g11Layout.addWidget(self.label_8, 0, 1)

        self.comboBox_S_End_AC = QtWidgets.QComboBox()
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItems(["关闭", "开启"])
        self.comboBox_S_End_AC.setToolTip(
            "关闭=本轮结束关交流输出；开启=保持输出（追加中间轮选开启，最后一轮再选关闭）"
        )
        self.comboBox_S_End_AC.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_AC, 0, 2)

        # DC channels row
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
            g11Layout.addWidget(cb, 1, col)
            setattr(self, cb_name, cb)

            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["关闭", "开启"])
            combo.setFixedWidth(120)
            g11Layout.addWidget(combo, 1, col + 1)
            setattr(self, combo_name, combo)

        layout.addWidget(self.groupBox_11)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _connect_dc_linkage(self):
        """连接 step1 DC 复选框与关机步骤 DC 复选框的联动。"""
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]
        end_dcs = [self.checkBox_S_End_DC1, self.checkBox_S_End_DC2,
                   self.checkBox_S_End_DC3, self.checkBox_S_End_DC4]

        def _update_end_dc(_checked=None):
            step_end_on = self.checkBox_S_End.isChecked()
            for i in range(4):
                should_enable = step_end_on and step1_dcs[i].isChecked()
                end_dcs[i].setEnabled(should_enable)
                end_dcs[i].setChecked(should_enable)

        self.checkBox_S_End.toggled.connect(_update_end_dc)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_end_dc)
        _update_end_dc()  # 初始化状态

    def retranslateUi(self, Dialog_thaivoltprotect10min):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaivoltprotect10min.setWindowTitle(_translate("Dialog_thaivoltprotect10min", "10min过压保护项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaivoltprotect10min", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaivoltprotect10min", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaivoltprotect10min", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaivoltprotect10min", "提交"))
