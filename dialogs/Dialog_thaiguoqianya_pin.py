# -*- coding: utf-8 -*-
# 过欠压_过欠频项目配置 - 横向步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.dewetron_autotest_panel import AnalyzerModeSection
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)


class Ui_Dialog_thaiguoqianya_pin(object):
    def setupUi(self, Dialog_thaiguoqianya_pin):
        Dialog_thaiguoqianya_pin.setObjectName("Dialog_thaiguoqianya_pin")
        Dialog_thaiguoqianya_pin.resize(1362, 1049)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog_thaiguoqianya_pin.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaiguoqianya_pin)
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

        # 国家标准（默认泰国=现行；切换才改扫描范围/频率，不碰 WT/德威创）
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
            from utils.iot_ovuf_standard import list_ovuf_standard_options

            for opt in list_ovuf_standard_options():
                self.comboBox_SolarStandard.addItem(str(opt["label"]), str(opt["id"]))
        except Exception:
            self.comboBox_SolarStandard.addItem("泰国 PEA/MEA（现行）", "thai")
        self.comboBox_SolarStandard.setCurrentIndex(0)
        self._solar_standard = "thai"
        self.comboBox_SolarStandard.currentIndexChanged.connect(self._on_solar_standard_changed)
        topLayout.addWidget(self.comboBox_SolarStandard)

        topLayout.addStretch()

        self._step_labels = []
        step_titles = [
            "① AC/DC 电源",
            "② 功率分析仪",
            "③ 过压扫描",
            "④ 欠压扫描",
            "⑤ 过频扫描",
            "⑥ 欠频扫描",
            "⑦ 测试相位",
            "⑧ 关机设置",
        ]
        # 步骤多时顶部可横向滚动，避免 Soft Panel 窄屏裁掉后面几步
        step_scroll = QtWidgets.QScrollArea()
        step_scroll.setObjectName("ovuf_step_scroll")
        step_scroll.setWidgetResizable(True)
        step_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        step_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        step_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        step_scroll.setFixedHeight(44)
        step_scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:horizontal { height: 8px; }"
        )
        step_bar = QtWidgets.QWidget()
        step_bar.setStyleSheet("background: transparent;")
        step_layout = QtWidgets.QHBoxLayout(step_bar)
        step_layout.setContentsMargins(0, 0, 0, 0)
        step_layout.setSpacing(4)
        for i, title in enumerate(step_titles):
            lbl = QtWidgets.QLabel(title)
            lbl.setObjectName(f"step_indicator_{i}")
            lbl.setCursor(QtCore.Qt.PointingHandCursor)
            lbl.setStyleSheet("""
                QLabel {
                    padding: 6px 10px; font-size: 12px; color: #334155;
                    border-bottom: 3px solid transparent; border-radius: 0;
                    background: transparent;
                }
                QLabel:hover { background-color: #f1f5f9; }
            """)
            lbl.mousePressEvent = lambda event, idx=i: self._switch_step(idx)
            step_layout.addWidget(lbl)
            self._step_labels.append(lbl)
        step_layout.addStretch()
        step_scroll.setWidget(step_bar)
        topLayout.addWidget(step_scroll, 1)

        mainLayout.addWidget(topBar)

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setStyleSheet("background-color: white;")
        mainLayout.addWidget(self.stackedWidget, 1)

        # ── 构建各步骤页面（顺序与顶部步骤条一致）──
        self._build_step1()
        self._build_step2()
        self._build_step3()
        self._build_step4()
        self._build_step5()
        self._build_step6()
        self._build_step7()
        self._build_step8()

        # ── DC 联动（step1 → 关机步骤） ──
        self._connect_dc_linkage()

        # 录波方式切换 → 按工况自动填充 WT 文件名列表
        self._wire_recording_mode()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaiguoqianya_pin)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaiguoqianya_pin)

    def set_solar_standard(self, standard_id, *, apply_defaults=False):
        """外部（IOT handoff）同步标准；默认不重写已填控件。"""
        try:
            from utils.iot_ovuf_standard import apply_ovuf_standard_to_ui

            apply_ovuf_standard_to_ui(
                self,
                standard_id,
                force=True,
                apply_defaults=bool(apply_defaults),
            )
        except Exception:
            self._solar_standard = str(standard_id or "thai").strip() or "thai"

    def _on_solar_standard_changed(self, index):
        """用户切换国家标准：回填扫描范围/频率等（不改 WT/德威创模式）。"""
        sid = self.comboBox_SolarStandard.itemData(index)
        if sid is None:
            sid = "thai"
        self.set_solar_standard(str(sid), apply_defaults=True)

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


    # ══════════════════════════════════════
    # 步骤切换
    # ══════════════════════════════════════
    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 10px; font-size: 11px; font-weight: bold; color: #7c3aed;
                        border-bottom: 3px solid #8b5cf6; border-radius: 0;
                        background-color: #f3e8ff;
                    }
                """)
            else:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 10px; font-size: 11px; color: #64748b;
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

    # ══════════════════════════════════════
    # Step 1: AC/DC 电源
    # ══════════════════════════════════════
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
        self.groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g1Layout = QtWidgets.QGridLayout(self.groupBox)
        g1Layout.setSpacing(8)
        g1Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        g1Layout.addWidget(self.checkBox_S1, 0, 0)

        g1Layout.addWidget(self._make_label("交流电源"), 0, 1)
        g1Layout.addWidget(self._make_label("交流电压1"), 0, 2)
        g1Layout.addWidget(self._make_label("交流电压2"), 0, 4)
        g1Layout.addWidget(self._make_label("交流电压3"), 0, 6)
        g1Layout.addWidget(self._make_label("频率"), 0, 8)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        g1Layout.addWidget(self.comboBox_S1_AC, 1, 1)

        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setMaximumHeight(31)
        self.textEdit_S1_AC_VOLT.setHtml("230")
        g1Layout.addWidget(self.textEdit_S1_AC_VOLT, 1, 2)
        g1Layout.addWidget(self._make_label("V"), 1, 3)

        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        g1Layout.addWidget(self.comboBox_S1_AC_2, 1, 4)

        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setMaximumHeight(31)
        self.textEdit_S1_AC_VOLT_2.setHtml("230")
        g1Layout.addWidget(self.textEdit_S1_AC_VOLT_2, 1, 5)

        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setMaximumHeight(31)
        self.textEdit_S1_AC_VOLT_3.setHtml("230")
        g1Layout.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 6)
        g1Layout.addWidget(self._make_label("V"), 1, 7)

        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setMaximumHeight(31)
        self.textEdit_S1_AC_FR.setHtml("50")
        g1Layout.addWidget(self.textEdit_S1_AC_FR, 1, 8)
        g1Layout.addWidget(self._make_label("Hz"), 1, 9)

        layout.addWidget(self.groupBox)

        # ── DC 电源组 ──
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流电源设置")
        self.groupBox_2.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g2Layout = QtWidgets.QGridLayout(self.groupBox_2)
        g2Layout.setSpacing(6)
        g2Layout.setContentsMargins(12, 20, 12, 12)

        headers = ["", "电源", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
        for c, h in enumerate(headers):
            g2Layout.addWidget(self._make_label(h), 0, c)

        dc_data = [
            ("checkBox_S1_DC1", "comboBox_S1_DC1", "直流电源1",
             "textEdit_S1_DC1_VOLT", "220", "textEdit_S1_DC1_CURR", "10",
             "textEdit_S1_DC1_Voc", "220", "textEdit_S1_DC1_Isc", "10",
             "textEdit_S1_DC1_PF", "100"),
            ("checkBox_S1_DC2", "comboBox_S1_DC2", "直流电源2",
             "textEdit_S1_DC2_VOLT", "220", "textEdit_S1_DC2_CURR", "10",
             "textEdit_S1_DC2_Voc", "220", "textEdit_S1_DC2_Isc", "10",
             "textEdit_S1_DC2_PF", "100"),
            ("checkBox_S1_DC3", "comboBox_S1_DC3", "直流电源3",
             "textEdit_S1_DC3_VOLT", "220", "textEdit_S1_DC3_CURR", "10",
             "textEdit_S1_DC3_Voc", "220", "textEdit_S1_DC3_Isc", "10",
             "textEdit_S1_DC3_PF", "100"),
            ("checkBox_S1_DC4", "comboBox_S1_DC4", "直流电源4",
             "textEdit_S1_DC4_VOLT", "220", "textEdit_S1_DC4_CURR", "10",
             "textEdit_S1_DC4_Voc", "220", "textEdit_S1_DC4_Isc", "10",
             "textEdit_S1_DC4_PF", "100"),
        ]
        for r, (cb_name, cmb_name, cmb_label,
                te_volt, volt_val, te_curr, curr_val,
                te_voc, voc_val, te_isc, isc_val,
                te_pf, pf_val) in enumerate(dc_data, start=1):
            cb = QtWidgets.QCheckBox(cmb_label)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            setattr(self, cb_name, cb)
            g2Layout.addWidget(cb, r, 0)

            cmb = QtWidgets.QComboBox()
            cmb.setObjectName(cmb_name)
            cmb.addItems(["开启", "关闭"])
            setattr(self, cmb_name, cmb)
            g2Layout.addWidget(cmb, r, 1)

            for col, (attr, val) in enumerate([
                (te_volt, volt_val), (te_curr, curr_val),
                (te_voc, voc_val), (te_isc, isc_val), (te_pf, pf_val)
            ], start=2):
                te = QtWidgets.QTextEdit()
                te.setObjectName(attr)
                te.setMaximumHeight(28)
                te.setHtml(str(val))
                setattr(self, attr, te)
                g2Layout.addWidget(te, r, col)

        layout.addWidget(self.groupBox_2)

        # ── 时间设置组 ──
        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("时间设置")
        self.groupBox_4.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g4Layout = QtWidgets.QGridLayout(self.groupBox_4)
        g4Layout.setSpacing(8)
        g4Layout.setContentsMargins(12, 20, 12, 12)

        g4Layout.addWidget(self._make_label("等待时间:"), 0, 0)
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setMaximumHeight(31)
        self.textEdit_S1_ACWaitTIME.setHtml("3")
        g4Layout.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        g4Layout.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        g4Layout.addWidget(self._make_label("启机时间:"), 1, 0)
        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setMaximumHeight(31)
        self.textEdit_S1_TIME.setHtml("5")
        g4Layout.addWidget(self.textEdit_S1_TIME, 1, 1)
        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        g4Layout.addWidget(self.comboBox_S1_TIME, 1, 2)

        g4Layout.addWidget(self._make_label("段间并网等待(回压回频后):"), 2, 0)
        self.textEdit_ovuf_grid_wait = QtWidgets.QTextEdit()
        self.textEdit_ovuf_grid_wait.setObjectName("textEdit_ovuf_grid_wait")
        self.textEdit_ovuf_grid_wait.setMaximumHeight(31)
        self.textEdit_ovuf_grid_wait.setHtml("5")
        self.textEdit_ovuf_grid_wait.setToolTip(
            "过压/欠压/过频扫完后先回到启机 230V/50Hz，再按此时间等待并网，然后才进下一段。"
            "单位请用「秒」；误选「分钟」会导致段间空等很久、试验看似扫完仍在等。"
        )
        g4Layout.addWidget(self.textEdit_ovuf_grid_wait, 2, 1)
        self.comboBox_ovuf_grid_wait = QtWidgets.QComboBox()
        self.comboBox_ovuf_grid_wait.setObjectName("comboBox_ovuf_grid_wait")
        self.comboBox_ovuf_grid_wait.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_ovuf_grid_wait.setCurrentIndex(0)  # 默认秒
        g4Layout.addWidget(self.comboBox_ovuf_grid_wait, 2, 2)

        layout.addWidget(self.groupBox_4)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════
    # Step 2: 功率分析仪（radio + stackedWidget 内嵌）
    # ══════════════════════════════════════
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

    # ══════════════════════════════════════
    # 步骤 3-8 的扫描范围构建辅助方法
    # ══════════════════════════════════════

    def _build_sweep_page(self, page_index, groupbox_objname, checkbox_objname,
                          groupbox_title, checkbox_text,
                          volt_start_obj, volt_start_val,
                          volt_end_obj, volt_end_val,
                          fr_start_obj, fr_start_val,
                          fr_end_obj, fr_end_val,
                          step_size_obj, step_size_val,
                          time_obj, time_val,
                          time_combo_obj, time_combo_items,
                          step_no, scan_kind):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        gb = QtWidgets.QGroupBox()
        gb.setObjectName(groupbox_objname)
        gb.setTitle(groupbox_title)
        gb.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(gb)
        gLayout.setSpacing(8)
        gLayout.setContentsMargins(12, 20, 12, 12)

        cb = QtWidgets.QCheckBox(checkbox_text)
        cb.setChecked(True)
        cb.setObjectName(checkbox_objname)
        setattr(self, checkbox_objname, cb)
        gLayout.addWidget(cb, 0, 0)

        # 电压/频率区间、步长、驻留仍保留控件，供旧 CSV 和 IOT 文本键写入。
        # 界面上不再摆这一组：第 3～6 步改由下方列表逐段填写。
        legacy = []
        lab_v = self._make_label("交流电压变动区间")
        lab_f = self._make_label("频率变动区间")
        gLayout.addWidget(lab_v, 1, 0, 1, 2)
        gLayout.addWidget(lab_f, 2, 0, 1, 2)
        legacy.extend((lab_v, lab_f))

        te_vs = QtWidgets.QTextEdit()
        te_vs.setObjectName(volt_start_obj)
        te_vs.setMaximumHeight(31)
        # plain：与 IOT handoff setPlainText 一致，避免 HTML 残留导致回读/显示错位
        te_vs.setPlainText(str(volt_start_val))
        setattr(self, volt_start_obj, te_vs)
        gLayout.addWidget(te_vs, 1, 2)
        lab_tilde_v = self._make_label("~")
        gLayout.addWidget(lab_tilde_v, 1, 3)
        legacy.append(lab_tilde_v)
        te_ve = QtWidgets.QTextEdit()
        te_ve.setObjectName(volt_end_obj)
        te_ve.setMaximumHeight(31)
        te_ve.setPlainText(str(volt_end_val))
        setattr(self, volt_end_obj, te_ve)
        gLayout.addWidget(te_ve, 1, 4)
        lab_v_unit = self._make_label("V")
        gLayout.addWidget(lab_v_unit, 1, 5)
        legacy.append(lab_v_unit)

        te_fs = QtWidgets.QTextEdit()
        te_fs.setObjectName(fr_start_obj)
        te_fs.setMaximumHeight(31)
        te_fs.setPlainText(str(fr_start_val))
        setattr(self, fr_start_obj, te_fs)
        gLayout.addWidget(te_fs, 2, 2)
        lab_tilde_f = self._make_label("~")
        gLayout.addWidget(lab_tilde_f, 2, 3)
        legacy.append(lab_tilde_f)
        te_fe = QtWidgets.QTextEdit()
        te_fe.setObjectName(fr_end_obj)
        te_fe.setMaximumHeight(31)
        te_fe.setPlainText(str(fr_end_val))
        setattr(self, fr_end_obj, te_fe)
        gLayout.addWidget(te_fe, 2, 4)
        lab_hz = self._make_label("Hz")
        gLayout.addWidget(lab_hz, 2, 5)
        legacy.append(lab_hz)

        lab_step = self._make_label("步长")
        gLayout.addWidget(lab_step, 3, 0)
        legacy.append(lab_step)
        te_ss = QtWidgets.QTextEdit()
        te_ss.setObjectName(step_size_obj)
        te_ss.setMaximumHeight(31)
        te_ss.setPlainText(str(step_size_val))
        setattr(self, step_size_obj, te_ss)
        gLayout.addWidget(te_ss, 3, 2)
        lab_step_unit = self._make_label("V|Hz")
        gLayout.addWidget(lab_step_unit, 3, 3)
        legacy.append(lab_step_unit)

        # 每点驻留：扫到该电压/频率点后保持多久；Soft Panel 停表总时长 =
        # 区间÷步长×驻留 + 开销，由 Append/ASYNC 自动填，勿与停表混淆。
        lab_dwell = self._make_label("每点驻留")
        gLayout.addWidget(lab_dwell, 4, 0)
        legacy.append(lab_dwell)
        te_time = QtWidgets.QTextEdit()
        te_time.setObjectName(time_obj)
        te_time.setMaximumHeight(31)
        te_time.setPlainText(str(time_val))
        setattr(self, time_obj, te_time)
        gLayout.addWidget(te_time, 4, 2)
        cmb_time = QtWidgets.QComboBox()
        cmb_time.setObjectName(time_combo_obj)
        cmb_time.addItems(time_combo_items)
        setattr(self, time_combo_obj, cmb_time)
        gLayout.addWidget(cmb_time, 4, 3)
        legacy.extend((te_vs, te_ve, te_fs, te_fe, te_ss, te_time, cmb_time))
        for widget in legacy:
            widget.hide()

        layout.addWidget(gb)
        self._mount_scan_list(layout, step_no, scan_kind)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _mount_scan_list(self, layout, step_no, scan_kind):
        """过压/欠压/过频/欠频各自一张可增删表。每一行是一段扫描。"""
        from components.ovuf_condition_list import OvufConditionList

        kind = "F" if str(scan_kind).upper() == "F" else "V"
        if kind == "F":
            tip = (
                "每一行是一段扫描，点「添加行 / 删除行」可以做多段，按从上到下执行。"
                "本页按频率区间和步长改整机频率，每点驻留是扫到每个点后停留的时间。"
                "电压区间起止相同时，这一段电压保持在起点。"
                "哪几相改电压，在过压、欠压表里勾 L1/L2/L3。"
            )
            default_value = "50"
        else:
            tip = (
                "每一行是一段扫描，点「添加行 / 删除行」可以做多段，按从上到下执行。"
                "本页按电压区间和步长改电压，每点驻留是扫到每个点后停留的时间。"
                "三相：勾选的相跟该段电压，没勾的相保持步骤①额定。"
                "例如只勾 L1、L2，这两相变化，L3 保持 230V（或步骤①该相额定）。"
                "频率区间起止相同时，这一段频率保持在起点。"
            )
            default_value = "230"
        widget = OvufConditionList(
            locked_kind=kind,
            tip_text=tip,
            default_value=default_value,
            show_template=False,
            show_phases=(kind == "V"),
            scan_range=True,
            object_name="ovufScanListS%d" % int(step_no),
        )
        setattr(self, "ovufScanListS%d" % int(step_no), widget)
        self._bind_scan_list_and_legacy(widget, int(step_no))
        widget.set_rows([self._legacy_scan_row(int(step_no))])
        layout.addWidget(widget, 1)

    def _legacy_scan_row(self, step_no):
        kind = "F" if int(step_no) in (5, 6) else "V"

        def _text(name, default):
            widget = getattr(self, name, None)
            if widget is None:
                return default
            if hasattr(widget, "toPlainText"):
                text = widget.toPlainText().strip()
                return text or default
            if hasattr(widget, "currentText"):
                text = str(widget.currentText() or "").strip()
                return text or default
            return default

        return {
            "enabled": True,
            "kind": kind,
            "volt_start": _text("textEdit_S%d_AC_VOLT_Start" % step_no, "230"),
            "volt_end": _text("textEdit_S%d_AC_VOLT_End" % step_no, "230"),
            "freq_start": _text("textEdit_S%d_AC_FR_Start" % step_no, "50"),
            "freq_end": _text("textEdit_S%d_AC_FR_End" % step_no, "50"),
            "step": _text("textEdit_S%d_Step_Size" % step_no, "5"),
            "l1": True,
            "l2": True,
            "l3": True,
            "dwell": _text("textEdit_S%d_TIME" % step_no, "3"),
            "unit": _text("comboBox_S%d_TIME" % step_no, "秒"),
        }

    def _bind_scan_list_and_legacy(self, widget, step_no):
        """只有一行时，旧文本键和这一行互相同步，IOT/旧 CSV 仍能改到这段扫描。"""

        def _pull(*_args):
            if getattr(widget, "_scan_pushing", False):
                return
            if widget.table.rowCount() > 1:
                return
            row = self._legacy_scan_row(step_no)
            existing = widget.get_rows(include_disabled=True)
            if existing:
                row["enabled"] = existing[0].get("enabled", True)
                row["l1"] = existing[0].get("l1", True)
                row["l2"] = existing[0].get("l2", True)
                row["l3"] = existing[0].get("l3", True)
            widget._scan_pulling = True
            try:
                widget.set_rows([row])
            finally:
                widget._scan_pulling = False

        names = (
            "textEdit_S%d_AC_VOLT_Start" % step_no,
            "textEdit_S%d_AC_VOLT_End" % step_no,
            "textEdit_S%d_AC_FR_Start" % step_no,
            "textEdit_S%d_AC_FR_End" % step_no,
            "textEdit_S%d_Step_Size" % step_no,
            "textEdit_S%d_TIME" % step_no,
            "comboBox_S%d_TIME" % step_no,
        )
        for name in names:
            editor = getattr(self, name, None)
            if editor is None:
                continue
            if hasattr(editor, "textChanged"):
                editor.textChanged.connect(_pull)
            elif hasattr(editor, "currentTextChanged"):
                editor.currentTextChanged.connect(_pull)

        def _push(*_args):
            if getattr(widget, "_scan_pulling", False):
                return
            rows = widget.get_rows(include_disabled=True)
            if len(rows) != 1:
                return
            row = rows[0]
            widget._scan_pushing = True
            try:
                mapping = (
                    ("textEdit_S%d_AC_VOLT_Start" % step_no, row.get("volt_start", "")),
                    ("textEdit_S%d_AC_VOLT_End" % step_no, row.get("volt_end", "")),
                    ("textEdit_S%d_AC_FR_Start" % step_no, row.get("freq_start", "")),
                    ("textEdit_S%d_AC_FR_End" % step_no, row.get("freq_end", "")),
                    ("textEdit_S%d_Step_Size" % step_no, row.get("step", "")),
                    ("textEdit_S%d_TIME" % step_no, row.get("dwell", "")),
                )
                for name, value in mapping:
                    editor = getattr(self, name, None)
                    if editor is not None and hasattr(editor, "setPlainText"):
                        if editor.toPlainText() != str(value):
                            editor.setPlainText(str(value))
                unit = getattr(self, "comboBox_S%d_TIME" % step_no, None)
                if unit is not None and hasattr(unit, "setCurrentText"):
                    unit.setCurrentText(str(row.get("unit") or "秒"))
            finally:
                widget._scan_pushing = False

        widget.rows_changed.connect(_push)

    # ══════════════════════════════════════
    # Step 3: 过压扫描（起止+步长）
    # ══════════════════════════════════════
    def _build_step3(self):
        self._build_sweep_page(
            2, "groupBox_3", "checkBox_S3", "过压扫描", "启用",
            "textEdit_S3_AC_VOLT_Start", 230,
            "textEdit_S3_AC_VOLT_End", 230,
            "textEdit_S3_AC_FR_Start", 50,
            "textEdit_S3_AC_FR_End", 50,
            "textEdit_S3_Step_Size", 5,
            "textEdit_S3_TIME", 3,
            "comboBox_S3_TIME", ["秒", "毫秒", "分钟"],
            3, "V",
        )

    # ══════════════════════════════════════
    # Step 4: 欠压扫描
    # ══════════════════════════════════════
    def _build_step4(self):
        self._build_sweep_page(
            3, "groupBox_6", "checkBox_S4", "欠压扫描", "启用",
            "textEdit_S4_AC_VOLT_Start", 230,
            "textEdit_S4_AC_VOLT_End", 230,
            "textEdit_S4_AC_FR_Start", 50,
            "textEdit_S4_AC_FR_End", 50,
            "textEdit_S4_Step_Size", 5,
            "textEdit_S4_TIME", 3,
            "comboBox_S4_TIME", ["秒", "毫秒", "分钟"],
            4, "V",
        )

    # ══════════════════════════════════════
    # Step 6: 过频扫描
    # ══════════════════════════════════════
    def _build_step5(self):
        self._build_sweep_page(
            4, "groupBox_7", "checkBox_S5", "过频扫描", "启用",
            "textEdit_S5_AC_VOLT_Start", 230,
            "textEdit_S5_AC_VOLT_End", 230,
            "textEdit_S5_AC_FR_Start", 50,
            "textEdit_S5_AC_FR_End", 50,
            "textEdit_S5_Step_Size", 5,
            "textEdit_S5_TIME", 3,
            "comboBox_S5_TIME", ["秒", "毫秒", "分钟"],
            5, "F",
        )

    # ══════════════════════════════════════
    # Step 7: 欠频扫描
    # ══════════════════════════════════════
    def _build_step6(self):
        self._build_sweep_page(
            5, "groupBox_13", "checkBox_S6", "欠频扫描", "启用",
            "textEdit_S6_AC_VOLT_Start", 230,
            "textEdit_S6_AC_VOLT_End", 230,
            "textEdit_S6_AC_FR_Start", 50,
            "textEdit_S6_AC_FR_End", 50,
            "textEdit_S6_Step_Size", 5,
            "textEdit_S6_TIME", 3,
            "comboBox_S6_TIME", ["秒", "毫秒", "分钟"],
            6, "F",
        )

    # ══════════════════════════════════════
    # Step 8: 测试相位
    # ══════════════════════════════════════
    def _build_step7(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── 测试项目与相位配置 ──
        self.groupBox_9 = QtWidgets.QGroupBox()
        self.groupBox_9.setObjectName("groupBox_9")
        self.groupBox_9.setTitle("测试相位")
        self.groupBox_9.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g9Layout = QtWidgets.QGridLayout(self.groupBox_9)
        g9Layout.setSpacing(8)
        g9Layout.setContentsMargins(12, 20, 12, 12)

        self.comboBox_Test_Project = QtWidgets.QComboBox(self.groupBox_9)
        self.comboBox_Test_Project.setObjectName("comboBox_Test_Project")
        self.comboBox_Test_Project.addItems(["过欠压", "过欠频"])
        self.comboBox_Test_Project.hide()

        g9Layout.addWidget(self._make_label("测试相"), 0, 0)
        self.checkBox_AC_Test_L1 = QtWidgets.QCheckBox("L1")
        self.checkBox_AC_Test_L1.setChecked(True)
        self.checkBox_AC_Test_L1.setObjectName("checkBox_AC_Test_L1")
        g9Layout.addWidget(self.checkBox_AC_Test_L1, 0, 1)
        self.checkBox_AC_Test_L2 = QtWidgets.QCheckBox("L2")
        self.checkBox_AC_Test_L2.setChecked(True)
        self.checkBox_AC_Test_L2.setObjectName("checkBox_AC_Test_L2")
        g9Layout.addWidget(self.checkBox_AC_Test_L2, 0, 2)
        self.checkBox_AC_Test_L3 = QtWidgets.QCheckBox("L3")
        self.checkBox_AC_Test_L3.setChecked(True)
        self.checkBox_AC_Test_L3.setObjectName("checkBox_AC_Test_L3")
        g9Layout.addWidget(self.checkBox_AC_Test_L3, 0, 3)

        phase_hint = QtWidgets.QLabel(
            "三相时：全选 L1/L2/L3 = 三相同压扫段（旧行为）。"
            "只勾部分相 = 勾选相跟扫点电压，未勾选相保持步骤①额定"
            "（可用于 PEA 等单相/两相电压故障穿越工况）。过欠频仍整机改频率。"
        )
        phase_hint.setWordWrap(True)
        phase_hint.setStyleSheet("color: #64748b; font-size: 12px; font-weight: normal;")
        g9Layout.addWidget(phase_hint, 1, 0, 1, 4)

        layout.addWidget(self.groupBox_9)

        # ── 过频扫描参数 ──
        self.groupBox_14 = QtWidgets.QGroupBox()
        self.groupBox_14.setObjectName("groupBox_14")
        self.groupBox_14.setTitle("过频扫描参数")
        self.groupBox_14.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g14Layout = QtWidgets.QGridLayout(self.groupBox_14)
        g14Layout.setSpacing(8)
        g14Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S7 = QtWidgets.QCheckBox("启用附加过频")
        self.checkBox_S7.setChecked(False)
        self.checkBox_S7.setObjectName("checkBox_S7")
        g14Layout.addWidget(self.checkBox_S7, 0, 0)

        g14Layout.addWidget(self._make_label("交流电压变动区间"), 1, 0, 1, 2)
        g14Layout.addWidget(self._make_label("频率变动区间"), 2, 0, 1, 2)

        self.textEdit_S7_AC_VOLT_Start = QtWidgets.QTextEdit()
        self.textEdit_S7_AC_VOLT_Start.setObjectName("textEdit_S7_AC_VOLT_Start")
        self.textEdit_S7_AC_VOLT_Start.setMaximumHeight(31)
        self.textEdit_S7_AC_VOLT_Start.setHtml("230")
        g14Layout.addWidget(self.textEdit_S7_AC_VOLT_Start, 1, 2)
        g14Layout.addWidget(self._make_label("~"), 1, 3)
        self.textEdit_S7_AC_VOLT_End = QtWidgets.QTextEdit()
        self.textEdit_S7_AC_VOLT_End.setObjectName("textEdit_S7_AC_VOLT_End")
        self.textEdit_S7_AC_VOLT_End.setMaximumHeight(31)
        self.textEdit_S7_AC_VOLT_End.setHtml("230")
        g14Layout.addWidget(self.textEdit_S7_AC_VOLT_End, 1, 4)
        g14Layout.addWidget(self._make_label("V"), 1, 5)

        self.textEdit_S7_AC_FR_Start = QtWidgets.QTextEdit()
        self.textEdit_S7_AC_FR_Start.setObjectName("textEdit_S7_AC_FR_Start")
        self.textEdit_S7_AC_FR_Start.setMaximumHeight(31)
        self.textEdit_S7_AC_FR_Start.setHtml("50")
        g14Layout.addWidget(self.textEdit_S7_AC_FR_Start, 2, 2)
        g14Layout.addWidget(self._make_label("~"), 2, 3)
        self.textEdit_S7_AC_FR_End = QtWidgets.QTextEdit()
        self.textEdit_S7_AC_FR_End.setObjectName("textEdit_S7_AC_FR_End")
        self.textEdit_S7_AC_FR_End.setMaximumHeight(31)
        self.textEdit_S7_AC_FR_End.setHtml("50")
        g14Layout.addWidget(self.textEdit_S7_AC_FR_End, 2, 4)
        g14Layout.addWidget(self._make_label("Hz"), 2, 5)

        g14Layout.addWidget(self._make_label("步长"), 3, 0)
        self.textEdit_S7_Step_Size = QtWidgets.QTextEdit()
        self.textEdit_S7_Step_Size.setObjectName("textEdit_S7_Step_Size")
        self.textEdit_S7_Step_Size.setMaximumHeight(31)
        self.textEdit_S7_Step_Size.setHtml("5")
        g14Layout.addWidget(self.textEdit_S7_Step_Size, 3, 2)
        g14Layout.addWidget(self._make_label("V|Hz"), 3, 3)

        g14Layout.addWidget(self._make_label("每点驻留"), 4, 0)
        self.textEdit_S7_TIME = QtWidgets.QTextEdit()
        self.textEdit_S7_TIME.setObjectName("textEdit_S7_TIME")
        self.textEdit_S7_TIME.setMaximumHeight(31)
        self.textEdit_S7_TIME.setHtml("3")
        g14Layout.addWidget(self.textEdit_S7_TIME, 4, 2)
        self.comboBox_S7_TIME = QtWidgets.QComboBox()
        self.comboBox_S7_TIME.setObjectName("comboBox_S7_TIME")
        self.comboBox_S7_TIME.addItems(["秒", "毫秒", "分钟"])
        g14Layout.addWidget(self.comboBox_S7_TIME, 4, 3)

        layout.addWidget(self.groupBox_14)

        # ── 欠频扫描参数 ──
        self.groupBox_15 = QtWidgets.QGroupBox()
        self.groupBox_15.setObjectName("groupBox_15")
        self.groupBox_15.setTitle("欠频扫描参数")
        self.groupBox_15.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g15Layout = QtWidgets.QGridLayout(self.groupBox_15)
        g15Layout.setSpacing(8)
        g15Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S8 = QtWidgets.QCheckBox("启用附加欠频")
        self.checkBox_S8.setChecked(False)
        self.checkBox_S8.setObjectName("checkBox_S8")
        g15Layout.addWidget(self.checkBox_S8, 0, 0)

        g15Layout.addWidget(self._make_label("交流电压变动区间"), 1, 0, 1, 2)
        g15Layout.addWidget(self._make_label("频率变动区间"), 2, 0, 1, 2)

        self.textEdit_S8_AC_VOLT_Start = QtWidgets.QTextEdit()
        self.textEdit_S8_AC_VOLT_Start.setObjectName("textEdit_S8_AC_VOLT_Start")
        self.textEdit_S8_AC_VOLT_Start.setMaximumHeight(31)
        self.textEdit_S8_AC_VOLT_Start.setHtml("230")
        g15Layout.addWidget(self.textEdit_S8_AC_VOLT_Start, 1, 2)
        g15Layout.addWidget(self._make_label("~"), 1, 3)
        self.textEdit_S8_AC_VOLT_End = QtWidgets.QTextEdit()
        self.textEdit_S8_AC_VOLT_End.setObjectName("textEdit_S8_AC_VOLT_End")
        self.textEdit_S8_AC_VOLT_End.setMaximumHeight(31)
        self.textEdit_S8_AC_VOLT_End.setHtml("230")
        g15Layout.addWidget(self.textEdit_S8_AC_VOLT_End, 1, 4)
        g15Layout.addWidget(self._make_label("V"), 1, 5)

        self.textEdit_S8_AC_FR_Start = QtWidgets.QTextEdit()
        self.textEdit_S8_AC_FR_Start.setObjectName("textEdit_S8_AC_FR_Start")
        self.textEdit_S8_AC_FR_Start.setMaximumHeight(31)
        self.textEdit_S8_AC_FR_Start.setHtml("50")
        g15Layout.addWidget(self.textEdit_S8_AC_FR_Start, 2, 2)
        g15Layout.addWidget(self._make_label("~"), 2, 3)
        self.textEdit_S8_AC_FR_End = QtWidgets.QTextEdit()
        self.textEdit_S8_AC_FR_End.setObjectName("textEdit_S8_AC_FR_End")
        self.textEdit_S8_AC_FR_End.setMaximumHeight(31)
        self.textEdit_S8_AC_FR_End.setHtml("50")
        g15Layout.addWidget(self.textEdit_S8_AC_FR_End, 2, 4)
        g15Layout.addWidget(self._make_label("Hz"), 2, 5)

        g15Layout.addWidget(self._make_label("步长"), 3, 0)
        self.textEdit_S8_Step_Size = QtWidgets.QTextEdit()
        self.textEdit_S8_Step_Size.setObjectName("textEdit_S8_Step_Size")
        self.textEdit_S8_Step_Size.setMaximumHeight(31)
        self.textEdit_S8_Step_Size.setHtml("5")
        g15Layout.addWidget(self.textEdit_S8_Step_Size, 3, 2)
        g15Layout.addWidget(self._make_label("V|Hz"), 3, 3)

        g15Layout.addWidget(self._make_label("每点驻留"), 4, 0)
        self.textEdit_S8_TIME = QtWidgets.QTextEdit()
        self.textEdit_S8_TIME.setObjectName("textEdit_S8_TIME")
        self.textEdit_S8_TIME.setMaximumHeight(31)
        self.textEdit_S8_TIME.setHtml("3")
        g15Layout.addWidget(self.textEdit_S8_TIME, 4, 2)
        self.comboBox_S8_TIME = QtWidgets.QComboBox()
        self.comboBox_S8_TIME.setObjectName("comboBox_S8_TIME")
        self.comboBox_S8_TIME.addItems(["秒", "毫秒", "分钟"])
        g15Layout.addWidget(self.comboBox_S8_TIME, 4, 3)

        layout.addWidget(self.groupBox_15)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════
    # Step 9: 关机设置
    # ══════════════════════════════════════
    def _build_step8(self):
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
        g11Layout.setSpacing(8)
        g11Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S_End = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_End.setChecked(True)
        self.checkBox_S_End.setObjectName("checkBox_S_End")
        g11Layout.addWidget(self.checkBox_S_End, 0, 0)

        # 第一行：交流电源 + AC 开关
        g11Layout.addWidget(self._make_label("交流电源"), 1, 0)
        self.comboBox_S_End_AC = QtWidgets.QComboBox()
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItems(["关闭", "开启"])
        g11Layout.addWidget(self.comboBox_S_End_AC, 1, 1)

        # DC 电源行
        dc_end_items = [
            ("checkBox_S_End_DC1", "直流电源1", "comboBox_S_End_DC1"),
            ("checkBox_S_End_DC2", "直流电源2", "comboBox_S_End_DC2"),
            ("checkBox_S_End_DC3", "直流电源3", "comboBox_S_End_DC3"),
            ("checkBox_S_End_DC4", "直流电源4", "comboBox_S_End_DC4"),
        ]
        for c, (cb_name, cb_label, cmb_name) in enumerate(dc_end_items):
            cb = QtWidgets.QCheckBox(cb_label)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            setattr(self, cb_name, cb)
            g11Layout.addWidget(cb, 2, c * 2)
            cmb = QtWidgets.QComboBox()
            cmb.setObjectName(cmb_name)
            cmb.addItems(["关闭", "开启"])
            setattr(self, cmb_name, cmb)
            g11Layout.addWidget(cmb, 2, c * 2 + 1)

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

    def _wire_recording_mode(self):
        """切换录波方式 / 勾选步骤 / 测试项目时，自动生成文件名列表。"""
        from utils.wt_recording_mode import apply_filename_list_to_wt_pages
        from utils.matrix_recording_commands import get_record_mode
        from utils.ovuf_recording import recommended_ovuf_names
        from components.wt_recording_mode_row import WtRecordingModeRow, install_on_wt_filename_group

        def _recommended_names():
            return recommended_ovuf_names(self, get_record_mode(self))

        def _fill_wt_names(names=None):
            if names is None:
                names = _recommended_names()
            apply_filename_list_to_wt_pages(self._wtStacked, names)

        def _sync_wt_rows(mode):
            for page_idx in range(self._wtStacked.count()):
                page = self._wtStacked.widget(page_idx)
                if page is None:
                    continue
                row = page.findChild(WtRecordingModeRow)
                if row is None:
                    continue
                row.blockSignals(True)
                row.set_mode(mode)
                row.blockSignals(False)

        def _on_mode(mode):
            _sync_wt_rows(mode)
            _fill_wt_names()

        for page_idx in range(self._wtStacked.count()):
            page = self._wtStacked.widget(page_idx)
            row = install_on_wt_filename_group(page, _recommended_names)
            if row is not None:
                row.names_filled.connect(_fill_wt_names)
                row.mode_changed.connect(_on_mode)

        shared = getattr(getattr(self, "analyzerModeSection", None), "recordingModeRow", None)
        if shared is not None:
            shared.mode_changed.connect(_on_mode)
        self.comboBox_Test_Project.currentIndexChanged.connect(lambda *_: _fill_wt_names())
        for step_no in (3, 4, 5, 6, 7, 8):
            cb = getattr(self, "checkBox_S%d" % step_no, None)
            if cb is not None:
                cb.toggled.connect(lambda *_: _fill_wt_names())
            for suffix in (
                "AC_VOLT_Start",
                "AC_VOLT_End",
                "AC_FR_Start",
                "AC_FR_End",
                "Step_Size",
            ):
                te = getattr(self, "textEdit_S%d_%s" % (step_no, suffix), None)
                if te is not None:
                    te.textChanged.connect(lambda *_: _fill_wt_names())

        _fill_wt_names()

    # ══════════════════════════════════════
    # 辅助方法
    # ══════════════════════════════════════
    def _make_label(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet("font-size: 12px; color: #475569; background: transparent; border: none;")
        return lbl

    def retranslateUi(self, Dialog_thaiguoqianya_pin):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaiguoqianya_pin.setWindowTitle(_translate("Dialog_thaiguoqianya_pin", "过欠压_过欠频项目配置"))
