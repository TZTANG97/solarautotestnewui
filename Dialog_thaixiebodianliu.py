# -*- coding: utf-8 -*-
# 谐波电流项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_thaixiebodianliu(object):
    def setupUi(self, Dialog_thaixiebodianliu):
        Dialog_thaixiebodianliu.setObjectName("Dialog_thaixiebodianliu")
        Dialog_thaixiebodianliu.resize(1300, 850)
        Dialog_thaixiebodianliu.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaixiebodianliu.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaixiebodianliu)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ 谐波2次", "④ 谐波3次", "⑤ 谐波4次", "⑥ 谐波5次", "⑦ 谐波6次", "⑧ 谐波7次", "⑨ 谐波8次", "⑩ 谐波9次", "⑪ 谐波10次", "⑫ 谐波11次", "⑬ 关机设置"]
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
        self._build_step1()   # AC/DC 电源
        self._build_step2()   # 功率分析仪
        self._build_harmonic_page(   # ③ 谐波 2次
            step_cb="checkBox_S3", step_text="step3",
            dc1_cb="checkBox_S1_DC1_2", dc2_cb="checkBox_S1_DC2_2",
            dc3_cb="checkBox_S1_DC3_2", dc4_cb="checkBox_S1_DC4_2",
            pf_te="textEdit_S1_DC1_PF_2", pwr_lbl="label_76", pct_lbl="label_47",
            include_timing=True,
        )
        self._build_harmonic_page(   # ④ 谐波 3次
            step_cb="checkBox_S3_2", step_text="step4",
            dc1_cb="checkBox_S1_DC1_3", dc2_cb="checkBox_S1_DC2_3",
            dc3_cb="checkBox_S1_DC3_3", dc4_cb="checkBox_S1_DC4_3",
            pf_te="textEdit_S1_DC1_PF_3", pwr_lbl="label_77", pct_lbl="label_49",
        )
        self._build_harmonic_page(   # ⑤ 谐波 4次
            step_cb="checkBox_S3_3", step_text="step5",
            dc1_cb="checkBox_S1_DC1_4", dc2_cb="checkBox_S1_DC2_4",
            dc3_cb="checkBox_S1_DC3_4", dc4_cb="checkBox_S1_DC4_4",
            pf_te="textEdit_S1_DC1_PF_4", pwr_lbl="label_78", pct_lbl="label_50",
        )
        self._build_harmonic_page(   # ⑥ 谐波 5次
            step_cb="checkBox_S3_4", step_text="step6",
            dc1_cb="checkBox_S1_DC1_5", dc2_cb="checkBox_S1_DC2_5",
            dc3_cb="checkBox_S1_DC3_5", dc4_cb="checkBox_S1_DC4_5",
            pf_te="textEdit_S1_DC1_PF_5", pwr_lbl="label_79", pct_lbl="label_51",
        )
        self._build_harmonic_page(   # ⑦ 谐波 6次
            step_cb="checkBox_S3_5", step_text="step7",
            dc1_cb="checkBox_S1_DC1_6", dc2_cb="checkBox_S1_DC2_6",
            dc3_cb="checkBox_S1_DC3_6", dc4_cb="checkBox_S1_DC4_6",
            pf_te="textEdit_S1_DC1_PF_6", pwr_lbl="label_80", pct_lbl="label_52",
        )
        self._build_harmonic_page(   # ⑧ 谐波 7次
            step_cb="checkBox_S3_10", step_text="step8",
            dc1_cb="checkBox_S1_DC1_10", dc2_cb="checkBox_S1_DC2_11",
            dc3_cb="checkBox_S1_DC3_10", dc4_cb="checkBox_S1_DC4_7",
            pf_te="textEdit_S1_DC1_PF_10", pwr_lbl="label_82", pct_lbl="label_61",
        )
        self._build_harmonic_page(   # ⑨ 谐波 8次
            step_cb="checkBox_S3_6", step_text="step9",
            dc1_cb="checkBox_S1_DC1_11", dc2_cb="checkBox_S1_DC2_8",
            dc3_cb="checkBox_S1_DC3_11", dc4_cb="checkBox_S1_DC3_15",
            pf_te="textEdit_S1_DC1_PF_9", pwr_lbl="label_81", pct_lbl="label_55",
        )
        self._build_harmonic_page(   # ⑩ 谐波 9次
            step_cb="checkBox_S3_7", step_text="step10",
            dc1_cb="checkBox_S1_DC1_7", dc2_cb="checkBox_S1_DC2_9",
            dc3_cb="checkBox_S1_DC3_8", dc4_cb="checkBox_S1_DC3_14",
            pf_te="textEdit_S1_DC1_PF_7", pwr_lbl="label_83", pct_lbl="label_53",
        )
        self._build_harmonic_page(   # ⑪ 谐波 10次
            step_cb="checkBox_S3_9", step_text="step11",
            dc1_cb="checkBox_S1_DC1_9", dc2_cb="checkBox_S1_DC2_10",
            dc3_cb="checkBox_S1_DC3_9", dc4_cb="checkBox_S1_DC3_16",
            pf_te="textEdit_S1_DC1_PF_11", pwr_lbl="label_84", pct_lbl="label_56",
        )
        self._build_harmonic_page(   # ⑫ 谐波 11次
            step_cb="checkBox_S3_8", step_text="step12",
            dc1_cb="checkBox_S1_DC1_8", dc2_cb="checkBox_S1_DC2_7",
            dc3_cb="checkBox_S1_DC3_7", dc4_cb="checkBox_S1_DC3_17",
            pf_te="textEdit_S1_DC1_PF_8", pwr_lbl="label_85", pct_lbl="label_60",
        )
        self._build_step13()  # ⑬ 关机设置（含 step13 谐波 12次 + step14 关机）

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaixiebodianliu)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaixiebodianliu)

    # ══════════════════════════════════════════════
    # 步骤切换
    # ══════════════════════════════════════════════
    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 8px; font-size: 11px; font-weight: bold; color: #7c3aed;
                        border-bottom: 3px solid #8b5cf6; border-radius: 0;
                        background-color: #f3e8ff;
                    }
                """)
            else:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 8px; font-size: 11px; color: #64748b;
                        border-bottom: 3px solid transparent; border-radius: 0;
                        background: transparent;
                    }
                    QLabel:hover { background-color: #f1f5f9; }
                """)

    # ══════════════════════════════════════════════
    # 通用样式常量
    # ══════════════════════════════════════════════
    _GRP_STYLE = "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }"
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
    _HEADER_STYLE = "font-weight: bold; color: #475569; font-size: 12px;"

    def _make_input(self, name, parent=None, default="", width=80, height=28):
        """创建统一样式的 QTextEdit 输入框。"""
        te = QtWidgets.QTextEdit()
        te.setObjectName(name)
        te.setFixedSize(width, height)
        te.setStyleSheet(self._INPUT_STYLE)
        if default:
            te.setText(default)
        if parent is not None:
            setattr(self, name, te)
        return te

    def _make_combo(self, name, items, parent=None, width=100):
        """创建统一样式的 QComboBox。"""
        cb = QtWidgets.QComboBox()
        cb.setObjectName(name)
        cb.addItems(items)
        cb.setFixedWidth(width)
        cb.setStyleSheet(self._COMBO_STYLE)
        if parent is not None:
            setattr(self, name, cb)
        return cb

    def _make_checkbox(self, name, text, checked=True, parent=None):
        """创建统一样式的 QCheckBox。"""
        cb = QtWidgets.QCheckBox(text)
        cb.setChecked(checked)
        cb.setObjectName(name)
        cb.setStyleSheet(self._CB_STYLE)
        if parent is not None:
            setattr(self, name, cb)
        return cb

    def _make_label(self, text, style=None):
        """创建统一标签。"""
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(style or self._LABEL_STYLE)
        return lbl

    # ══════════════════════════════════════════════
    # Step 1: AC/DC 电源 + 时序
    # ══════════════════════════════════════════════
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

        self.checkBox_S1 = self._make_checkbox("checkBox_S1", "step1")
        acGrid.addWidget(self.checkBox_S1, 0, 0)

        acGrid.addWidget(self._make_label("交流电源", self._HEADER_STYLE), 0, 1)
        self.comboBox_S1_AC = self._make_combo("comboBox_S1_AC", ["开启", "关闭"])
        acGrid.addWidget(self.comboBox_S1_AC, 0, 2)

        acGrid.addWidget(self._make_label("交流电压1:"), 0, 3)
        self.textEdit_S1_AC_VOLT = self._make_input("textEdit_S1_AC_VOLT", default="230")
        acGrid.addWidget(self.textEdit_S1_AC_VOLT, 0, 4)
        acGrid.addWidget(self._make_label("V"), 0, 5)

        acGrid.addWidget(self._make_label("交流电压2:"), 0, 6)
        self.textEdit_S1_AC_VOLT_2 = self._make_input("textEdit_S1_AC_VOLT_2", default="230")
        acGrid.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 7)
        acGrid.addWidget(self._make_label("V"), 0, 8)

        acGrid.addWidget(self._make_label("交流电压3:"), 1, 1)
        self.textEdit_S1_AC_VOLT_3 = self._make_input("textEdit_S1_AC_VOLT_3", default="230")
        acGrid.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 2)
        acGrid.addWidget(self._make_label("V"), 1, 3)

        self.comboBox_S1_AC_2 = self._make_combo("comboBox_S1_AC_2", ["单相", "三相"])
        acGrid.addWidget(self.comboBox_S1_AC_2, 1, 4)

        acGrid.addWidget(self._make_label("频率:"), 1, 5)
        self.textEdit_S1_AC_FR = self._make_input("textEdit_S1_AC_FR", default="50")
        acGrid.addWidget(self.textEdit_S1_AC_FR, 1, 6)
        acGrid.addWidget(self._make_label("Hz"), 1, 7)

        layout.addWidget(grp_ac)

        # ── DC 电源组 (4 channels) ──
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
        self.checkBox_S1_DC1 = self._make_checkbox("checkBox_S1_DC1", "直流电源1")
        dcGrid.addWidget(self.checkBox_S1_DC1, 1, 0)
        self.comboBox_S1_DC1 = self._make_combo("comboBox_S1_DC1", ["开启", "关闭"])
        dcGrid.addWidget(self.comboBox_S1_DC1, 1, 1)
        for c, n in enumerate(["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc",
                               "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"], start=2):
            te = self._make_input(n, parent=True, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100"))
            )
            dcGrid.addWidget(te, 1, c)

        # DC2
        self.checkBox_S1_DC2 = self._make_checkbox("checkBox_S1_DC2", "直流电源2")
        dcGrid.addWidget(self.checkBox_S1_DC2, 2, 0)
        self.comboBox_S1_DC2 = self._make_combo("comboBox_S1_DC2", ["开启", "关闭"])
        dcGrid.addWidget(self.comboBox_S1_DC2, 2, 1)
        for c, n in enumerate(["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc",
                               "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"], start=2):
            te = self._make_input(n, parent=True, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100"))
            )
            dcGrid.addWidget(te, 2, c)

        # DC3
        self.checkBox_S1_DC3 = self._make_checkbox("checkBox_S1_DC3", "直流电源3")
        dcGrid.addWidget(self.checkBox_S1_DC3, 3, 0)
        self.comboBox_S1_DC3 = self._make_combo("comboBox_S1_DC3", ["开启", "关闭"])
        dcGrid.addWidget(self.comboBox_S1_DC3, 3, 1)
        for c, n in enumerate(["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc",
                               "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"], start=2):
            te = self._make_input(n, parent=True, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100"))
            )
            dcGrid.addWidget(te, 3, c)

        # DC4
        self.checkBox_S1_DC4 = self._make_checkbox("checkBox_S1_DC4", "直流电源4")
        dcGrid.addWidget(self.checkBox_S1_DC4, 4, 0)
        self.comboBox_S1_DC4 = self._make_combo("comboBox_S1_DC4", ["开启", "关闭"])
        dcGrid.addWidget(self.comboBox_S1_DC4, 4, 1)
        for c, n in enumerate(["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc",
                               "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"], start=2):
            te = self._make_input(n, parent=True, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100"))
            )
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
        self.textEdit_S1_ACWaitTIME = self._make_input("textEdit_S1_ACWaitTIME", default="3")
        tGrid.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = self._make_combo("comboBox_S1_ACWaitTIME", ["秒", "分钟", "毫秒"])
        tGrid.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        tGrid.addWidget(self._make_label("启机时间:"), 0, 3)
        self.textEdit_S1_TIME = self._make_input("textEdit_S1_TIME", default="5")
        tGrid.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = self._make_combo("comboBox_S1_TIME", ["分钟", "秒", "毫秒"])
        tGrid.addWidget(self.comboBox_S1_TIME, 0, 5)

        # 积分测试
        self.checkBox_S1_Integral = self._make_checkbox("checkBox_S1_Integral", "积分测试")
        tGrid.addWidget(self.checkBox_S1_Integral, 1, 0)
        self.comboBox_S1_Integral = self._make_combo("comboBox_S1_Integral", ["关闭", "开启"])
        tGrid.addWidget(self.comboBox_S1_Integral, 1, 1)

        layout.addWidget(grp_time)
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

        grp = QtWidgets.QGroupBox()
        grp.setTitle("功率分析仪配置")
        grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = self._make_checkbox("checkBox_S2", "step2")
        gLayout.addWidget(self.checkBox_S2, 0, 0)

        # WT 选择行
        wt_cfg = [
            ("checkBox_S2_WT3000", "WT3000", "pushButton_S2_WT_3000_CONFIG", "WT_3000_config"),
            ("checkBox_S2_WT1800", "WT1800", "pushButton_S2_WT_1800_CONFIG", "WT_1800_config"),
            ("checkBox_S2_WT1806E", "WT1806E", "pushButton_S2_WT_1806E_CONFIG", "WT_1806E_config"),
            ("checkBox_S2_WT5000", "WT5000", "pushButton_S2_WT_5000_CONFIG", "WT_5000_config"),
        ]
        for c, (cb_name, cb_text, btn_name, btn_text) in enumerate(wt_cfg):
            col = c * 3
            cb = self._make_checkbox(cb_name, cb_text)
            gLayout.addWidget(cb, 1, col)
            btn = QtWidgets.QPushButton(btn_text)
            btn.setObjectName(btn_name)
            btn.setStyleSheet("""
                QPushButton { background-color: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe;
                              border-radius: 4px; padding: 6px 12px; font-size: 11px; }
                QPushButton:hover { background-color: #c7d2fe; }
            """)
            setattr(self, btn_name, btn)
            gLayout.addWidget(btn, 1, col + 1)

        layout.addWidget(grp)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # 谐波步骤页（通用构建器）
    # ══════════════════════════════════════════════
    def _build_harmonic_page(self, step_cb, step_text,
                             dc1_cb, dc2_cb, dc3_cb, dc4_cb,
                             pf_te, pwr_lbl, pct_lbl,
                             include_timing=False):
        """构建单个谐波步骤页面。所有 objectName 严格保持不变。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp = QtWidgets.QGroupBox()
        grp.setTitle("谐波功率设置")
        grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        # 步骤启用复选框
        step_widget = self._make_checkbox(step_cb, step_text)
        gLayout.addWidget(step_widget, 0, 0)

        # DC 通道行
        row_data = [
            (dc1_cb, "直流电源1"),
            (dc2_cb, "直流电源2"),
            (dc3_cb, "直流电源3"),
            (dc4_cb, "直流电源4"),
        ]
        for c, (name, text) in enumerate(row_data):
            cb = self._make_checkbox(name, text)
            gLayout.addWidget(cb, 1, c * 2)
            lbl = self._make_label("功率")
            lbl.setObjectName(pwr_lbl if c == 0 else f"_pwr_{name}")
            if c == 0:
                lbl.setObjectName(pwr_lbl)
            gLayout.addWidget(lbl, 1, c * 2 + 1)

        # PF 输入
        pf_widget = self._make_input(pf_te, default="100")
        gLayout.addWidget(pf_widget, 2, 0)
        pct = self._make_label("%")
        pct.setObjectName(pct_lbl)
        gLayout.addWidget(pct, 2, 1)

        layout.addWidget(grp)

        # 数据采集时序（仅第一个谐波页包含）
        if include_timing:
            grp_t = QtWidgets.QGroupBox()
            grp_t.setTitle("数据采集设置")
            grp_t.setStyleSheet(self._GRP_STYLE)
            tg = QtWidgets.QGridLayout(grp_t)
            tg.setSpacing(8)
            tg.setContentsMargins(12, 20, 12, 12)

            tg.addWidget(self._make_label("数据采集:"), 0, 0)
            self.textEdit_S3_TIME_2 = self._make_input("textEdit_S3_TIME_2", default="10")
            tg.addWidget(self.textEdit_S3_TIME_2, 0, 1)
            self.comboBox_S3_TIME_2 = self._make_combo("comboBox_S3_TIME_2", ["分钟", "秒", "毫秒"])
            tg.addWidget(self.comboBox_S3_TIME_2, 0, 2)

            tg.addWidget(self._make_label("等待时间:"), 0, 3)
            self.textEdit_S3_TIME_3 = self._make_input("textEdit_S3_TIME_3", default="1")
            tg.addWidget(self.textEdit_S3_TIME_3, 0, 4)
            self.comboBox_S3_TIME_3 = self._make_combo("comboBox_S3_TIME_3", ["秒", "分钟", "毫秒"])
            tg.addWidget(self.comboBox_S3_TIME_3, 0, 5)

            layout.addWidget(grp_t)

        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 13: 关机设置（含 step13 谐波 12次 + step14 关机）
    # ══════════════════════════════════════════════
    def _build_step13(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── 谐波 12次设置（step13 = checkBox_S3_11） ──
        grp_h = QtWidgets.QGroupBox()
        grp_h.setTitle("谐波 12次功率设置")
        grp_h.setStyleSheet(self._GRP_STYLE)
        hg = QtWidgets.QGridLayout(grp_h)
        hg.setSpacing(10)
        hg.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S3_11 = self._make_checkbox("checkBox_S3_11", "step13")
        hg.addWidget(self.checkBox_S3_11, 0, 0)

        for c, (name, text) in enumerate([
            ("checkBox_S1_DC1_12", "直流电源1"),
            ("checkBox_S1_DC2_12", "直流电源2"),
            ("checkBox_S1_DC3_12", "直流电源3"),
            ("checkBox_S1_DC3_13", "直流电源4"),
        ]):
            cb = self._make_checkbox(name, text)
            hg.addWidget(cb, 1, c * 2)

        self.textEdit_S1_DC1_PF_12 = self._make_input("textEdit_S1_DC1_PF_12", default="100")
        hg.addWidget(self.textEdit_S1_DC1_PF_12, 2, 0)
        lbl_pwr = self._make_label("功率")
        lbl_pwr.setObjectName("label_86")
        hg.addWidget(lbl_pwr, 2, 1)
        lbl_pct = self._make_label("%")
        lbl_pct.setObjectName("label_62")
        hg.addWidget(lbl_pct, 2, 2)

        layout.addWidget(grp_h)

        # ── 关机设置（step14 = checkBox_S5） ──
        grp_s = QtWidgets.QGroupBox()
        grp_s.setObjectName("groupBox_shutdown")
        grp_s.setTitle("关机设置")
        grp_s.setStyleSheet(self._GRP_STYLE)
        sg = QtWidgets.QGridLayout(grp_s)
        sg.setSpacing(10)
        sg.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S5 = self._make_checkbox("checkBox_S5", "step14")
        sg.addWidget(self.checkBox_S5, 0, 0)

        # 交流电源关机
        sg.addWidget(self._make_label("交流电源"), 0, 1)
        self.comboBox_S5_AC = self._make_combo("comboBox_S5_AC", ["关闭", "开启"])
        sg.addWidget(self.comboBox_S5_AC, 0, 2)

        # DC 电源关机
        dc_shutdown = [
            ("checkBox_S5_DC1", "直流电源1", "comboBox_S5_DC1"),
            ("checkBox_S5_DC2", "直流电源2", "comboBox_S5_DC2"),
            ("checkBox_S5_DC3", "直流电源3", "comboBox_S5_DC3"),
            ("checkBox_S5_DC4", "直流电源4", "comboBox_S5_DC4"),
        ]
        for c, (cb_name, cb_text, combo_name) in enumerate(dc_shutdown):
            col = 1 + c * 2
            cb = self._make_checkbox(cb_name, cb_text)
            sg.addWidget(cb, 1, col)
            combo = self._make_combo(combo_name, ["关闭", "开启"])
            sg.addWidget(combo, 1, col + 1)

        layout.addWidget(grp_s)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    def retranslateUi(self, Dialog_thaixiebodianliu):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaixiebodianliu.setWindowTitle(_translate("Dialog_thaixiebodianliu", "谐波电流项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaixiebodianliu", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaixiebodianliu", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaixiebodianliu", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaixiebodianliu", "提交"))
