# -*- coding: utf-8 -*-
# 固定PF=1项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.timeline import TimelineWidget


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
            "③ 测量步骤", "④ 测量设置", "⑤ 结束关机"
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
        self._build_step3_measure_settings()
        self._build_step_end()

        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

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
        dc_headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]
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
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp = QtWidgets.QGroupBox("功率分析仪配置")
        grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(grp)

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
        for rb in [self.radioButton_S2_WT3000, self.radioButton_S2_WT1800,
                   self.radioButton_S2_WT1806E, self.radioButton_S2_WT5000]:
            radio_layout.addWidget(rb)
        radio_layout.addStretch()
        gLayout.addLayout(radio_layout, 0, 1, 1, 3)

        # 执行json文件
        gLayout.addWidget(self._make_label("执行json文件:"), 1, 0)
        self.cB_wt_json = self._make_combo("cB_wt_json", [], parent=self._dialog, width=400)
        gLayout.addWidget(self.cB_wt_json, 1, 1, 1, 3)

        # WT数据保存路径
        gLayout.addWidget(self._make_label("WT数据保存路径:"), 2, 0)
        self.lE_wt_save_path = self._make_input("lE_wt_save_path", "", parent=self._dialog, width=400)
        gLayout.addWidget(self.lE_wt_save_path, 2, 1, 1, 3)

        layout.addWidget(grp)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ════════════════════════════════════════════════
    # Step3: 测量设置（共享时间参数）
    # ════════════════════════════════════════════════
    def _build_step3_measure_settings(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp = QtWidgets.QGroupBox()
        grp.setTitle("测量设置（共享时间参数）")
        grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(8)
        gLayout.setContentsMargins(12, 20, 12, 12)

        TIME_LABELS = ["等待时间", "保存改名延时", "开始测量延时", "结束测量延时"]
        for idx, label in enumerate(TIME_LABELS):
            row = idx
            gLayout.addWidget(self._make_label(f"{label}:"), row, 0)
            gLayout.addWidget(self._make_input(f"lE_S3_{idx+1}", "5", parent=self._dialog, width=400), row, 1)
            gLayout.addWidget(self._make_combo(f"cB_S3_unit_{idx+1}", ["秒", "分钟", "毫秒"], parent=self._dialog, width=400), row, 2)

        # 批量设置按钮
        self.btn_set_batch_time = QtWidgets.QPushButton("批量应用到所有测量步骤")
        self.btn_set_batch_time.setObjectName("btn_set_batch_time")
        self.btn_set_batch_time.setFixedHeight(36)
        self.btn_set_batch_time.setStyleSheet(
            "QPushButton { background-color: #f59e0b; color: white; border: none; border-radius: 6px; padding: 0 20px; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background-color: #d97706; }")
        gLayout.addWidget(self.btn_set_batch_time, len(TIME_LABELS), 0, 1, 3)

        layout.addWidget(grp)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ════════════════════════════════════════════════
    # 测量步骤（Step4-8 合并为 timeline + 卡片布局）
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

        for step_num in range(4, 9):
            card = self._build_single_measure_step(step_num)
            timeline.addStep(f"测量步骤{step_num - 3}", card)

        timeline.finalize()
        scroll.setWidget(timeline)
        outer_layout.addWidget(scroll)

        self.stackedWidget.addWidget(page)

    def _build_single_measure_step(self, step_num):
        """构建单个测量步骤的 QGroupBox 卡片"""
        grp = QtWidgets.QGroupBox()
        grp.setTitle(f"测量步骤{step_num - 3}")
        grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(8)
        gLayout.setContentsMargins(12, 20, 12, 12)

        # 步骤启用复选框
        cb = self._make_checkbox(f"checkBox_S{step_num}", f"启用步骤{step_num - 3}", parent=self._dialog)
        cb.setChecked(True)
        gLayout.addWidget(cb, 0, 0, 1, 4)

        # DC 通道
        gLayout.addWidget(self._make_label("DC通道:"), 1, 0)
        dc_cbs = []
        for j in range(4):
            dc_cb = self._make_checkbox(f"checkBox_S1_DC{j+1}_{step_num}", f"DC{j+1}", parent=self._dialog)
            dc_cb.setChecked(True)
            gLayout.addWidget(dc_cb, 1, j + 1)
            dc_cbs.append(dc_cb)

        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]
        def _update_dc(_checked=None):
            step_on = cb.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                dc_cbs[i].setEnabled(should_enable)
                dc_cbs[i].setChecked(should_enable)
        cb.toggled.connect(lambda checked: _update_dc(checked))
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_dc)
        _update_dc()

        # 功率
        gLayout.addWidget(self._make_label("功率:"), 2, 0)
        pf_row = QtWidgets.QHBoxLayout()
        pf_row.addWidget(self._make_input(f"textEdit_S1_DC1_PF_{step_num}", "100", parent=self._dialog))
        pf_row.addWidget(self._make_label("%"))
        pf_row.addStretch()
        gLayout.addLayout(pf_row, 2, 1, 1, 3)

        # 保存文件名 + 录制动作 json
        gLayout.addWidget(self._make_label("保存文件名:"), 3, 0)
        name_row = QtWidgets.QHBoxLayout()
        name_row.addWidget(self._make_input(f"lE_S{step_num}_filename", "", parent=self._dialog, width=400))
        name_row.addWidget(self._make_combo(f"cB_S{step_num}_json_1", [], parent=self._dialog, width=400))
        name_row.addStretch()
        gLayout.addLayout(name_row, 3, 1, 1, 3)

        # 开始测量 json
        gLayout.addWidget(self._make_label("开始测量:"), 4, 0)
        gLayout.addWidget(self._make_combo(f"cB_S{step_num}_json_2", [], parent=self._dialog, width=400), 4, 1, 1, 3)

        # 结束测量 json
        gLayout.addWidget(self._make_label("结束测量:"), 5, 0)
        gLayout.addWidget(self._make_combo(f"cB_S{step_num}_json_3", [], parent=self._dialog, width=400), 5, 1, 1, 3)

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

        # 启用复选框
        self.checkBox_S14 = self._make_checkbox("checkBox_S14", "启用结束步骤", parent=self._dialog)
        self.checkBox_S14.setChecked(True)
        sg.addWidget(self.checkBox_S14, 0, 0)
        self.checkBox_S14_2 = self._make_checkbox("checkBox_S14_2", "", parent=self._dialog)
        self.checkBox_S14_2.setChecked(True)
        sg.addWidget(self.checkBox_S14_2, 0, 1)

        # 交流电源
        sg.addWidget(self._make_label("交流电源:", self._HEADER_STYLE), 1, 0)
        self.comboBox_S5_AC = self._make_combo("comboBox_S5_AC", ["关闭", "开启"], parent=self._dialog)
        sg.addWidget(self.comboBox_S5_AC, 1, 1)

        # DC 电源 (4 channels)
        sg.addWidget(self._make_label("直流电源:", self._HEADER_STYLE), 2, 0)
        self._s5_dc_cbs = []
        dc_row = QtWidgets.QHBoxLayout()
        for j in range(4):
            cb = self._make_checkbox(f"checkBox_S5_DC{j+1}", f"DC{j+1}", parent=self._dialog)
            cb.setChecked(True)
            dc_row.addWidget(cb)
            self._s5_dc_cbs.append(cb)
        dc_row.addStretch()
        sg.addLayout(dc_row, 2, 1)

        # DC 开关
        sg.addWidget(self._make_label("DC开关:", self._HEADER_STYLE), 3, 0)
        dc_combo_row = QtWidgets.QHBoxLayout()
        for j in range(4):
            combo = self._make_combo(f"comboBox_S5_DC{j+1}", ["关闭", "开启"], parent=self._dialog)
            dc_combo_row.addWidget(combo)
        dc_combo_row.addStretch()
        sg.addLayout(dc_combo_row, 3, 1)

        # DC 联动 step1
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]
        def _update_s5_dc():
            step_on = self.checkBox_S14.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                self._s5_dc_cbs[i].setEnabled(should_enable)
                self._s5_dc_cbs[i].setChecked(should_enable)
        self.checkBox_S14.toggled.connect(_update_s5_dc)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_s5_dc)
        _update_s5_dc()

        # JSON 文件
        sg.addWidget(self._make_label("执行json文件:"), 4, 0)
        self.cB_S14_json_14 = self._make_combo("cB_S14_json_14", [], parent=self._dialog, width=400)
        sg.addWidget(self.cB_S14_json_14, 4, 1)

        # 等待时间
        sg.addWidget(self._make_label("等待时间:"), 5, 0)
        time_row = QtWidgets.QHBoxLayout()
        time_row.addWidget(self._make_input("lE_S14_1", "5", parent=self._dialog, width=400))
        time_row.addWidget(self._make_combo("cB_S14_unit_1", ["秒", "分钟", "毫秒"], parent=self._dialog, width=400))
        time_row.addStretch()
        sg.addLayout(time_row, 5, 1)

        layout.addWidget(grp_s)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

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
