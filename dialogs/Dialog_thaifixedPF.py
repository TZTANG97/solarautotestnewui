# -*- coding: utf-8 -*-
# 固定PF=1项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.dewetron_autotest_panel import AnalyzerModeSection
from components.timeline import TimelineWidget
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content,
)


class Ui_Dialog_thaifixedPF(object):
    _GRP_STYLE = "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }"
    _HEADER_STYLE = "font-weight: bold; color: #475569; font-size: 12px;"
    _INPUT_STYLE = (
        "QTextEdit { border: 1px solid #d1d5db; border-radius: 4px; padding: 2px 4px; "
        "font-size: 12px; background-color: #f9fafb; }"
    )
    _COMBO_STYLE = (
        "QComboBox { border: 1px solid #d1d5db; border-radius: 4px; padding: 4px 8px; "
        "font-size: 12px; background-color: #f9fafb; min-width: 90px; }"
    )
    _CB_STYLE = "QCheckBox { font-size: 12px; spacing: 6px; }"
    _LABEL_STYLE = "font-size: 12px; color: #475569;"

    def setupUi(self, Dialog_thaifixedPF):
        Dialog_thaifixedPF.setObjectName("Dialog_thaifixedPF")
        Dialog_thaifixedPF.resize(1300, 850)
        Dialog_thaifixedPF.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaifixedPF.setWindowIcon(icon)
        self._dialog = Dialog_thaifixedPF

        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaifixedPF)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # ══════════════════════════════════════
        # 顶部工具栏
        # ══════════════════════════════════════
        topBar = QtWidgets.QWidget()
        topBar.setFixedHeight(56)
        topBar.setStyleSheet("QWidget { background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; }")
        topLayout = QtWidgets.QHBoxLayout(topBar)
        topLayout.setContentsMargins(12, 0, 12, 0)
        topLayout.setSpacing(8)

        self.pushButton_TestAppend = QtWidgets.QPushButton("测试追加")
        self.pushButton_TestAppend.setObjectName("pushButton_TestAppend")
        self.pushButton_TestAppend.setStyleSheet(
            "QPushButton { background-color: #8b5cf6; color: white; border: none; border-radius: 4px; padding: 6px 14px; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background-color: #7c3aed; }")
        topLayout.addWidget(self.pushButton_TestAppend)

        self.pushButton_ReadSettingFile = QtWidgets.QPushButton("读取设定")
        self.pushButton_ReadSettingFile.setObjectName("pushButton_ReadSettingFile")
        self.pushButton_ReadSettingFile.setStyleSheet(
            "QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 4px; padding: 6px 14px; font-size: 12px; }"
            "QPushButton:hover { background-color: #2563eb; }")
        topLayout.addWidget(self.pushButton_ReadSettingFile)

        self.pushButton_SaveSettingFile = QtWidgets.QPushButton("保存设定")
        self.pushButton_SaveSettingFile.setObjectName("pushButton_SaveSettingFile")
        self.pushButton_SaveSettingFile.setStyleSheet(
            "QPushButton { background-color: #10b981; color: white; border: none; border-radius: 4px; padding: 6px 14px; font-size: 12px; }"
            "QPushButton:hover { background-color: #059669; }")
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
            "font-size: 12px; font-weight: bold; color: #8b5cf6; background-color: #ede9fe; border-radius: 10px; padding: 2px 8px; border: none;")
        self.label_append_count.setAlignment(QtCore.Qt.AlignCenter)
        topLayout.addWidget(self.label_append_count)

        self.pushButton_ResetCount = QtWidgets.QPushButton("重置")
        self.pushButton_ResetCount.setObjectName("pushButton_ResetCount")
        self.pushButton_ResetCount.setStyleSheet(
            "QPushButton { background-color: #ef4444; color: white; border: none; border-radius: 4px; padding: 4px 10px; font-size: 11px; }"
            "QPushButton:hover { background-color: #dc2626; }")
        topLayout.addWidget(self.pushButton_ResetCount)

        topLayout.addStretch()

        # 步骤指示器
        self._step_labels = []
        step_titles = [
            "① AC/DC电源", "② 功率分析仪",
            "③ 测量步骤", "④ 关机设置",
        ]
        for i, title in enumerate(step_titles):
            lbl = QtWidgets.QLabel(title)
            lbl.setObjectName(f"step_indicator_{i}")
            lbl.setCursor(QtCore.Qt.PointingHandCursor)
            lbl.setStyleSheet(
                "QLabel { padding: 6px 8px; font-size: 11px; color: #64748b; border-bottom: 3px solid transparent; border-radius: 0; background: transparent; }"
                "QLabel:hover { background-color: #f1f5f9; }")
            lbl.mousePressEvent = lambda event, idx=i: self._switch_step(idx)
            topLayout.addWidget(lbl)
            self._step_labels.append(lbl)

        mainLayout.addWidget(topBar)

        # QStackedWidget
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setStyleSheet("background-color: white;")
        mainLayout.addWidget(self.stackedWidget, 1)

        self._build_step1()
        self._build_step2()
        self._build_measure_steps()
        self._build_step_end()

        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self._wire_recording_mode()
        self._switch_step(0)
        self.retranslateUi(Dialog_thaifixedPF)

    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        active = ("QLabel { padding: 6px 8px; font-size: 11px; font-weight: bold; color: #7c3aed; "
                  "border-bottom: 3px solid #8b5cf6; border-radius: 0; "
                  "background-color: #f3e8ff; }")
        normal = ("QLabel { padding: 6px 8px; font-size: 11px; color: #64748b; "
                  "border-bottom: 3px solid transparent; border-radius: 0; "
                  "background: transparent; }"
                  "QLabel:hover { background-color: #f1f5f9; }")
        for i, lbl in enumerate(self._step_labels):
            lbl.setStyleSheet(active if i == index else normal)

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
            "pushButton_DEW_TestApply",
            "pushButton_DEW_RefreshFields",
            "pushButton_DEW_DataViewer",
            "comboBox_DEW_MaxRefreshRate",
            "spinBox_DEW_DecimalPlaces",
            "checkBox_DEW_RealtimeWaveform",
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

    # ════════════════════════════════════════════════
    # Step1: AC/DC 电源 + 时序
    # ════════════════════════════════════════════════
    def _build_step1(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── AC 电源组 ──
        grp_ac = QtWidgets.QGroupBox()
        grp_ac.setObjectName("groupBox_2")
        grp_ac.setTitle("交流电源设置")
        grp_ac.setStyleSheet(self._GRP_STYLE)
        acGrid = QtWidgets.QGridLayout(grp_ac)
        acGrid.setSpacing(8)
        acGrid.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = self._make_checkbox("checkBox_S1", "step1", checked=True, parent=self._dialog)
        acGrid.addWidget(self.checkBox_S1, 0, 0)

        acGrid.addWidget(self._make_label("交流电源", self._HEADER_STYLE), 0, 1)
        self.comboBox_S1_AC = self._make_combo("comboBox_S1_AC", ["开启", "关闭"], parent=self._dialog)
        acGrid.addWidget(self.comboBox_S1_AC, 0, 2)

        acGrid.addWidget(self._make_label("交流电压1:"), 0, 3)
        self.textEdit_S1_AC_VOLT = self._make_input("textEdit_S1_AC_VOLT", default="230", parent=self._dialog)
        acGrid.addWidget(self.textEdit_S1_AC_VOLT, 0, 4)
        acGrid.addWidget(self._make_label("V"), 0, 5)

        acGrid.addWidget(self._make_label("交流电压2:"), 0, 6)
        self.textEdit_S1_AC_VOLT_2 = self._make_input("textEdit_S1_AC_VOLT_2", default="230", parent=self._dialog)
        acGrid.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 7)
        acGrid.addWidget(self._make_label("V"), 0, 8)

        acGrid.addWidget(self._make_label("交流电压3:"), 1, 1)
        self.textEdit_S1_AC_VOLT_3 = self._make_input("textEdit_S1_AC_VOLT_3", default="230", parent=self._dialog)
        acGrid.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 2)
        acGrid.addWidget(self._make_label("V"), 1, 3)

        self.comboBox_S1_AC_2 = self._make_combo("comboBox_S1_AC_2", ["单相", "三相"], parent=self._dialog)
        acGrid.addWidget(self.comboBox_S1_AC_2, 1, 4)

        acGrid.addWidget(self._make_label("频率:"), 1, 5)
        self.textEdit_S1_AC_FR = self._make_input("textEdit_S1_AC_FR", default="50", parent=self._dialog)
        acGrid.addWidget(self.textEdit_S1_AC_FR, 1, 6)
        acGrid.addWidget(self._make_label("Hz"), 1, 7)

        layout.addWidget(grp_ac)

        # ── DC 电源组 (4 channels, table layout) ──
        grp_dc = QtWidgets.QGroupBox()
        grp_dc.setObjectName("groupBox_6")
        grp_dc.setTitle("直流电源设置")
        grp_dc.setStyleSheet(self._GRP_STYLE)
        dcGrid = QtWidgets.QGridLayout(grp_dc)
        dcGrid.setSpacing(6)
        dcGrid.setContentsMargins(12, 20, 12, 12)

        # 表头
        dc_headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
        for c, h in enumerate(dc_headers):
            lbl = self._make_label(h, self._HEADER_STYLE)
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            dcGrid.addWidget(lbl, 0, c)

        # DC1
        self.checkBox_S1_DC1 = self._make_checkbox("checkBox_S1_DC1", "直流电源1", parent=self._dialog)
        dcGrid.addWidget(self.checkBox_S1_DC1, 1, 0)
        self.comboBox_S1_DC1 = self._make_combo("comboBox_S1_DC1", ["开启", "关闭"], parent=self._dialog)
        dcGrid.addWidget(self.comboBox_S1_DC1, 1, 1)
        for c, n in enumerate(["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc",
                               "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"], start=2):
            te = self._make_input(n, parent=self._dialog, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100")))
            dcGrid.addWidget(te, 1, c)

        # DC2
        self.checkBox_S1_DC2 = self._make_checkbox("checkBox_S1_DC2", "直流电源2", parent=self._dialog)
        dcGrid.addWidget(self.checkBox_S1_DC2, 2, 0)
        self.comboBox_S1_DC2 = self._make_combo("comboBox_S1_DC2", ["开启", "关闭"], parent=self._dialog)
        dcGrid.addWidget(self.comboBox_S1_DC2, 2, 1)
        for c, n in enumerate(["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc",
                               "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"], start=2):
            te = self._make_input(n, parent=self._dialog, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100")))
            dcGrid.addWidget(te, 2, c)

        # DC3
        self.checkBox_S1_DC3 = self._make_checkbox("checkBox_S1_DC3", "直流电源3", parent=self._dialog)
        dcGrid.addWidget(self.checkBox_S1_DC3, 3, 0)
        self.comboBox_S1_DC3 = self._make_combo("comboBox_S1_DC3", ["开启", "关闭"], parent=self._dialog)
        dcGrid.addWidget(self.comboBox_S1_DC3, 3, 1)
        for c, n in enumerate(["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc",
                               "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"], start=2):
            te = self._make_input(n, parent=self._dialog, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100")))
            dcGrid.addWidget(te, 3, c)

        # DC4
        self.checkBox_S1_DC4 = self._make_checkbox("checkBox_S1_DC4", "直流电源4", parent=self._dialog)
        dcGrid.addWidget(self.checkBox_S1_DC4, 4, 0)
        self.comboBox_S1_DC4 = self._make_combo("comboBox_S1_DC4", ["开启", "关闭"], parent=self._dialog)
        dcGrid.addWidget(self.comboBox_S1_DC4, 4, 1)
        for c, n in enumerate(["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc",
                               "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"], start=2):
            te = self._make_input(n, parent=self._dialog, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100")))
            dcGrid.addWidget(te, 4, c)

        layout.addWidget(grp_dc)

        # ── 时序组 ──
        grp_time = QtWidgets.QGroupBox()
        grp_time.setObjectName("groupBox_5")
        grp_time.setTitle("时序设置")
        grp_time.setStyleSheet(self._GRP_STYLE)
        tGrid = QtWidgets.QGridLayout(grp_time)
        tGrid.setSpacing(8)
        tGrid.setContentsMargins(12, 20, 12, 12)

        tGrid.addWidget(self._make_label("等待时间:"), 0, 0)
        self.textEdit_S1_ACWaitTIME = self._make_input("textEdit_S1_ACWaitTIME", default="3", parent=self._dialog)
        tGrid.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = self._make_combo("comboBox_S1_ACWaitTIME", ["秒", "分钟", "毫秒"], parent=self._dialog)
        tGrid.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        tGrid.addWidget(self._make_label("启机时间:"), 0, 3)
        self.textEdit_S1_TIME = self._make_input("textEdit_S1_TIME", default="5", parent=self._dialog)
        tGrid.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = self._make_combo("comboBox_S1_TIME", ["分钟", "秒", "毫秒"], parent=self._dialog)
        tGrid.addWidget(self.comboBox_S1_TIME, 0, 5)

        # 积分测试
        self.checkBox_S1_Integral = self._make_checkbox("checkBox_S1_Integral", "积分测试", parent=self._dialog)
        tGrid.addWidget(self.checkBox_S1_Integral, 1, 0)
        self.comboBox_S1_Integral = self._make_combo("comboBox_S1_Integral", ["关闭", "开启"], parent=self._dialog)
        tGrid.addWidget(self.comboBox_S1_Integral, 1, 1)

        layout.addWidget(grp_time)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    # ════════════════════════════════════════════════
    # Step2: 功率分析仪
    # ════════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp = QtWidgets.QGroupBox()
        grp.setTitle("功率分析仪配置")
        grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = self._make_checkbox("checkBox_S2", "启用步骤", parent=self._dialog)
        gLayout.addWidget(self.checkBox_S2, 0, 0)

        self.radioButton_S2_WT3000 = self._make_radio("radio_S2_WT3000", "WT3000", parent=self._dialog, checked=True)
        self.radioButton_S2_WT1800 = self._make_radio("radio_S2_WT1800", "WT1800", parent=self._dialog)
        self.radioButton_S2_WT1806E = self._make_radio("radio_S2_WT1806E", "WT1806E", parent=self._dialog)
        self.radioButton_S2_WT5000 = self._make_radio("radio_S2_WT5000", "WT5000", parent=self._dialog)
        radio_group = QtWidgets.QButtonGroup(None)
        radio_group.addButton(self.radioButton_S2_WT3000, 0)
        radio_group.addButton(self.radioButton_S2_WT1800, 1)
        radio_group.addButton(self.radioButton_S2_WT1806E, 2)
        radio_group.addButton(self.radioButton_S2_WT5000, 3)
        self._radio_group = radio_group

        radio_layout = QtWidgets.QHBoxLayout()
        radio_layout.setSpacing(24)
        radio_layout.setContentsMargins(8, 0, 0, 0)
        for rb in [self.radioButton_S2_WT3000, self.radioButton_S2_WT1800,
                   self.radioButton_S2_WT1806E, self.radioButton_S2_WT5000]:
            radio_layout.addWidget(rb)
        radio_layout.addStretch()
        gLayout.addLayout(radio_layout, 0, 1, 1, 3)

        self._wtStacked = QtWidgets.QStackedWidget()
        self._wtStacked.addWidget(build_wt3000_content(self))
        self._wtStacked.addWidget(build_wt1800_content(self))
        self._wtStacked.addWidget(build_wt1806e_content(self))
        self._wtStacked.addWidget(build_wt5000_content(self))
        gLayout.addWidget(self._wtStacked, 1, 0, 1, 4)

        def _on_radio_toggled(btn, checked):
            if checked:
                self._wtStacked.setCurrentIndex(radio_group.id(btn))

        radio_group.buttonToggled.connect(_on_radio_toggled)

        self._integrate_analyzer_mode(layout, grp)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _build_timing_card(self):
        """数据采集 + 录波方式（与谐波/无功族一致）。"""
        from utils.wt_recording_mode import MODE_LABELS, MODE_CONTINUOUS, MODE_SPLIT

        grp = QtWidgets.QGroupBox()
        grp.setTitle("数据采集设置")
        grp.setStyleSheet(self._GRP_STYLE)
        tg = QtWidgets.QGridLayout(grp)
        tg.setSpacing(8)
        tg.setContentsMargins(12, 20, 12, 12)

        tg.addWidget(self._make_label("数据采集:"), 0, 0)
        self.textEdit_S3_TIME_2 = self._make_input("textEdit_S3_TIME_2", parent=self._dialog, default="10")
        tg.addWidget(self.textEdit_S3_TIME_2, 0, 1)
        self.comboBox_S3_TIME_2 = self._make_combo(
            "comboBox_S3_TIME_2", ["分钟", "秒", "毫秒"], parent=self._dialog
        )
        tg.addWidget(self.comboBox_S3_TIME_2, 0, 2)

        tg.addWidget(self._make_label("等待时间:"), 0, 3)
        self.textEdit_S3_TIME_3 = self._make_input("textEdit_S3_TIME_3", parent=self._dialog, default="1")
        tg.addWidget(self.textEdit_S3_TIME_3, 0, 4)
        self.comboBox_S3_TIME_3 = self._make_combo(
            "comboBox_S3_TIME_3", ["秒", "分钟", "毫秒"], parent=self._dialog
        )
        tg.addWidget(self.comboBox_S3_TIME_3, 0, 5)

        tg.addWidget(self._make_label("录波方式:"), 1, 0)
        self.comboBox_S3_record_mode = QtWidgets.QComboBox()
        self.comboBox_S3_record_mode.setObjectName("comboBox_S3_record_mode")
        self.comboBox_S3_record_mode.addItem(MODE_LABELS[MODE_CONTINUOUS], MODE_CONTINUOUS)
        self.comboBox_S3_record_mode.addItem(MODE_LABELS[MODE_SPLIT], MODE_SPLIT)
        self.comboBox_S3_record_mode.setMinimumWidth(220)
        tg.addWidget(self.comboBox_S3_record_mode, 1, 1, 1, 2)
        self.pushButton_S3_fill_filenames = QtWidgets.QPushButton("填充推荐文件名")
        self.pushButton_S3_fill_filenames.setObjectName("pushButton_S3_fill_filenames")
        tg.addWidget(self.pushButton_S3_fill_filenames, 1, 3, 1, 2)

        tip = QtWidgets.QLabel(
            "一条线连续录：五个功率点录成单个文件；分开录：每个功率点单独存盘。"
            "文件名填在功率分析仪页的「文件名列表」。"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #64748b; font-weight: normal; font-size: 11px;")
        tg.addWidget(tip, 2, 0, 1, 6)
        return grp

    # ════════════════════════════════════════════════
    # 测量步骤（数据采集 + Step4-8 合并为 timeline）
    # ════════════════════════════════════════════════
    def _build_measure_steps(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        outer_layout = QtWidgets.QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")

        timeline = TimelineWidget()
        timeline.addStep("数据采集设置", self._build_timing_card())

        _pf_defaults = {4: "100", 5: "75", 6: "50", 7: "30", 8: "20"}
        for step_num in range(4, 9):
            card = self._build_single_measure_step(step_num, _pf_defaults[step_num])
            timeline.addStep(f"测量步骤{step_num - 3}", card)

        timeline.finalize()
        scroll.setWidget(timeline)
        outer_layout.addWidget(scroll)

        self.stackedWidget.addWidget(page)

    def _build_single_measure_step(self, step_num, pf_default="100"):
        """单个功率点卡片：DC 通道 + 功率%，无 json 宏。"""
        grp = QtWidgets.QGroupBox()
        grp.setTitle(f"测量步骤{step_num - 3}")
        grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(8)
        gLayout.setContentsMargins(12, 20, 12, 12)

        cb = self._make_checkbox(
            f"checkBox_S{step_num}", f"启用步骤{step_num - 3}", parent=self._dialog
        )
        cb.setChecked(True)
        gLayout.addWidget(cb, 0, 0)

        dc_cbs = []
        for j in range(4):
            dc_cb = self._make_checkbox(
                f"checkBox_S1_DC{j+1}_{step_num}", f"直流电源{j+1}", parent=self._dialog
            )
            dc_cbs.append(dc_cb)
            gLayout.addWidget(dc_cb, 1, j * 2)
            gLayout.addWidget(self._make_label("功率"), 1, j * 2 + 1)

        pf_widget = self._make_input(
            f"textEdit_S1_DC1_PF_{step_num}", pf_default, parent=self._dialog
        )
        gLayout.addWidget(pf_widget, 2, 0)
        pct = self._make_label("%")
        gLayout.addWidget(pct, 2, 1)

        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        def _update_dc(_checked=None):
            step_on = cb.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                dc_cbs[i].setEnabled(should_enable)
                dc_cbs[i].setChecked(should_enable)
            pf_widget.setEnabled(step_on)
            pct.setEnabled(step_on)

        cb.toggled.connect(_update_dc)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_dc)
        _update_dc()
        return grp

    # ════════════════════════════════════════════════
    # StepEnd: 结束关机设置（竖式卡片布局）
    # ════════════════════════════════════════════════
    def _build_step_end(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp_s = QtWidgets.QGroupBox()
        grp_s.setObjectName("groupBox_shutdown")
        grp_s.setTitle("关机设置")
        grp_s.setStyleSheet(self._GRP_STYLE)
        sg = QtWidgets.QGridLayout(grp_s)
        sg.setSpacing(10)
        sg.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S14 = self._make_checkbox("checkBox_S14", "step14", parent=self._dialog)
        self.checkBox_S14.setChecked(True)
        sg.addWidget(self.checkBox_S14, 0, 0)

        sg.addWidget(self._make_label("交流电源"), 0, 1)
        self.comboBox_S5_AC = self._make_combo("comboBox_S5_AC", ["关闭", "开启"], parent=self._dialog)
        sg.addWidget(self.comboBox_S5_AC, 0, 2)

        self._s5_dc_cbs = []
        dc_shutdown = [
            ("checkBox_S5_DC1", "直流电源1", "comboBox_S5_DC1"),
            ("checkBox_S5_DC2", "直流电源2", "comboBox_S5_DC2"),
            ("checkBox_S5_DC3", "直流电源3", "comboBox_S5_DC3"),
            ("checkBox_S5_DC4", "直流电源4", "comboBox_S5_DC4"),
        ]
        for c, (cb_name, cb_text, combo_name) in enumerate(dc_shutdown):
            col = 1 + c * 2
            cb = self._make_checkbox(cb_name, cb_text, parent=self._dialog)
            self._s5_dc_cbs.append(cb)
            sg.addWidget(cb, 1, col)
            combo = self._make_combo(combo_name, ["关闭", "开启"], parent=self._dialog)
            sg.addWidget(combo, 1, col + 1)

        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        def _update_s5_dc():
            step_on = self.checkBox_S14.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                self._s5_dc_cbs[i].setEnabled(should_enable)
                self._s5_dc_cbs[i].setChecked(should_enable)
            self.comboBox_S5_AC.setEnabled(step_on)

        self.checkBox_S14.toggled.connect(_update_s5_dc)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_s5_dc)
        _update_s5_dc()

        layout.addWidget(grp_s)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _wire_recording_mode(self):
        from utils.wt_recording_mode import (
            apply_filename_list_to_wt_pages,
            combo_index_to_mode,
        )
        from components.wt_recording_mode_row import install_on_wt_filename_group

        def _recommended_names():
            from utils.wt_recording_mode import fixed_pf_recommended_filenames

            mode = combo_index_to_mode(self.comboBox_S3_record_mode.currentIndex())
            percents = []
            for s in range(4, 9):
                if getattr(self, f"checkBox_S{s}").isChecked():
                    raw = getattr(self, f"textEdit_S1_DC1_PF_{s}").toPlainText().strip()
                    try:
                        percents.append(float(raw))
                    except ValueError:
                        percents.append(s)
            return fixed_pf_recommended_filenames(percents, mode)

        def _fill_wt_names(names=None):
            if names is None:
                names = _recommended_names()
            apply_filename_list_to_wt_pages(self._wtStacked, names)

        self.pushButton_S3_fill_filenames.clicked.connect(lambda: _fill_wt_names())
        self.comboBox_S3_record_mode.currentIndexChanged.connect(lambda _i: _fill_wt_names())
        for s in range(4, 9):
            getattr(self, f"checkBox_S{s}").toggled.connect(lambda _c: _fill_wt_names())

        for page_idx in range(self._wtStacked.count()):
            page = self._wtStacked.widget(page_idx)
            row = install_on_wt_filename_group(page, _recommended_names)
            if row is not None:
                row.names_filled.connect(_fill_wt_names)

        _fill_wt_names()

    # ════════════════════════════════════════════════
    # 辅助方法
    # ════════════════════════════════════════════════
    def _make_checkbox(self, name, text, checked=True, parent=None):
        cb = QtWidgets.QCheckBox(text)
        cb.setChecked(checked)
        cb.setObjectName(name)
        cb.setStyleSheet(self._CB_STYLE)
        if parent is not None:
            setattr(self, name, cb)
        return cb

    def _make_radio(self, name, text, parent=None, checked=False):
        rb = QtWidgets.QRadioButton(text)
        rb.setObjectName(name)
        if parent:
            rb.setParent(parent)
            setattr(self, name, rb)
        if checked:
            rb.setChecked(True)
        return rb

    def _make_label(self, text, style=None):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(style or self._LABEL_STYLE)
        return lbl

    def _make_combo(self, name, items, parent=None, width=100):
        cb = QtWidgets.QComboBox()
        cb.setObjectName(name)
        cb.addItems(items)
        cb.setFixedWidth(width)
        cb.setStyleSheet(self._COMBO_STYLE)
        if parent is not None:
            setattr(self, name, cb)
        return cb

    def _make_input(self, name, default="", parent=None, width=80, height=28):
        te = QtWidgets.QTextEdit()
        te.setObjectName(name)
        te.setFixedSize(width, height)
        te.setStyleSheet(self._INPUT_STYLE)
        if default:
            te.setText(default)
        if parent is not None:
            setattr(self, name, te)
        return te

    def retranslateUi(self, Dialog_thaifixedPF):
        Dialog_thaifixedPF.setWindowTitle("固定PF_1项目配置")
        self.pushButton_Send.setVisible(False)
