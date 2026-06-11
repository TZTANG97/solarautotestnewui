# -*- coding: utf-8 -*-
# 静态CosPhi项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_thaistaticcosPhi(object):
    def setupUi(self, Dialog_thaistaticcosPhi):
        Dialog_thaistaticcosPhi.setObjectName("Dialog_thaistaticcosPhi")
        Dialog_thaistaticcosPhi.resize(1597, 828)
        Dialog_thaistaticcosPhi.setMinimumSize(QtCore.QSize(1400, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaistaticcosPhi.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaistaticcosPhi)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ cosPhi", "④ cosPhi", "⑤ cosPhi", "⑥ cosPhi", "⑦ cosPhi", "⑧ cosPhi", "⑨ cosPhi", "⑩ 判定结果", "⑪ 关机设置"]
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
        self._build_step1()    # AC/DC 电源
        self._build_step2()    # 功率分析仪
        self._build_cosPhi_steps()  # Steps 3-11 (cosPhi)
        self._build_step_last()  # 关机设置

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaistaticcosPhi)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaistaticcosPhi)

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
    # Step 1: AC/DC 电源设置
    # ══════════════════════════════════════════════
    def _build_step1(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── AC 电源组 ──
        grpAC = QtWidgets.QGroupBox()
        grpAC.setObjectName("groupBox_ac")
        grpAC.setTitle("交流电源设置")
        grpAC.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        acLayout = QtWidgets.QGridLayout(grpAC)
        acLayout.setSpacing(8)
        acLayout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        acLayout.addWidget(self.checkBox_S1, 0, 0, 1, 2)

        # Row 0: 交流电源开关 + 交流电压1
        lbl = QtWidgets.QLabel("交流电源:")
        lbl.setObjectName("label_3")
        acLayout.addWidget(lbl, 0, 2)
        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(100)
        acLayout.addWidget(self.comboBox_S1_AC, 0, 3)

        lbl = QtWidgets.QLabel("交流电压1:")
        lbl.setObjectName("label_4")
        acLayout.addWidget(lbl, 0, 4)
        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(80, 28)
        acLayout.addWidget(self.textEdit_S1_AC_VOLT, 0, 5)
        lbl = QtWidgets.QLabel("V")
        lbl.setObjectName("label_5")
        acLayout.addWidget(lbl, 0, 6)

        lbl = QtWidgets.QLabel("交流电压2:")
        lbl.setObjectName("label_69")
        acLayout.addWidget(lbl, 0, 7)
        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(80, 28)
        acLayout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 8)
        lbl = QtWidgets.QLabel("V")
        lbl.setObjectName("label_67")
        acLayout.addWidget(lbl, 0, 9)

        lbl = QtWidgets.QLabel("交流电压3:")
        lbl.setObjectName("label_68")
        acLayout.addWidget(lbl, 0, 10)
        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(80, 28)
        acLayout.addWidget(self.textEdit_S1_AC_VOLT_3, 0, 11)
        lbl = QtWidgets.QLabel("V")
        lbl.setObjectName("label_71")
        acLayout.addWidget(lbl, 0, 12)

        # Row 1: 相模式 + 频率
        lbl = QtWidgets.QLabel("相模式:")
        acLayout.addWidget(lbl, 1, 2)
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(100)
        acLayout.addWidget(self.comboBox_S1_AC_2, 1, 3)

        lbl = QtWidgets.QLabel("频率:")
        lbl.setObjectName("label_17")
        acLayout.addWidget(lbl, 1, 4)
        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(80, 28)
        acLayout.addWidget(self.textEdit_S1_AC_FR, 1, 5)
        lbl = QtWidgets.QLabel("Hz")
        lbl.setObjectName("label_18")
        acLayout.addWidget(lbl, 1, 6)

        layout.addWidget(grpAC)

        # ── DC 电源组 (4 channels) ──
        grpDC = QtWidgets.QGroupBox()
        grpDC.setObjectName("groupBox_dc")
        grpDC.setTitle("直流电源设置")
        grpDC.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        dcLayout = QtWidgets.QGridLayout(grpDC)
        dcLayout.setSpacing(6)
        dcLayout.setContentsMargins(12, 20, 12, 12)

        # Header
        dcHeaders = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]
        for c, h in enumerate(dcHeaders):
            hdrLbl = QtWidgets.QLabel(h)
            hdrLbl.setStyleSheet("font-weight: bold; color: #475569;")
            hdrLbl.setAlignment(QtCore.Qt.AlignCenter)
            dcLayout.addWidget(hdrLbl, 0, c)

        # DC channels data
        dc_channels = [
            ("checkBox_S1_DC1", "直流电源1", "comboBox_S1_DC1",
             ["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"]),
            ("checkBox_S1_DC2", "直流电源2", "comboBox_S1_DC2",
             ["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"]),
            ("checkBox_S1_DC3", "直流电源3", "comboBox_S1_DC3",
             ["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"]),
            ("checkBox_S1_DC4", "直流电源4", "comboBox_S1_DC4",
             ["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"]),
        ]
        for r, (cb_name, cb_text, combo_name, te_names) in enumerate(dc_channels, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            dcLayout.addWidget(cb, r, 0)
            setattr(self, cb_name, cb)

            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["开启", "关闭"])
            combo.setFixedWidth(100)
            dcLayout.addWidget(combo, r, 1)
            setattr(self, combo_name, combo)

            for c, te_name in enumerate(te_names, start=2):
                te = QtWidgets.QTextEdit()
                te.setObjectName(te_name)
                te.setFixedSize(80, 28)
                dcLayout.addWidget(te, r, c)
                setattr(self, te_name, te)

        layout.addWidget(grpDC)

        # ── 时序组 ──
        grpTime = QtWidgets.QGroupBox()
        grpTime.setObjectName("groupBox_time")
        grpTime.setTitle("时序设置")
        grpTime.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        timeLayout = QtWidgets.QGridLayout(grpTime)
        timeLayout.setSpacing(8)
        timeLayout.setContentsMargins(12, 20, 12, 12)

        lbl = QtWidgets.QLabel("等待时间:")
        lbl.setObjectName("label_65")
        timeLayout.addWidget(lbl, 0, 0)
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(80, 28)
        timeLayout.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(100)
        timeLayout.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        lbl = QtWidgets.QLabel("启机时间:")
        lbl.setObjectName("label_19")
        timeLayout.addWidget(lbl, 0, 3)
        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(80, 28)
        timeLayout.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(100)
        timeLayout.addWidget(self.comboBox_S1_TIME, 0, 5)

        layout.addWidget(grpTime)
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

        grpWT = QtWidgets.QGroupBox()
        grpWT.setObjectName("groupBox_wt")
        grpWT.setTitle("功率分析仪设置")
        grpWT.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        wtLayout = QtWidgets.QGridLayout(grpWT)
        wtLayout.setSpacing(10)
        wtLayout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        wtLayout.addWidget(self.checkBox_S2, 0, 0)

        # WT3000
        self.checkBox_S2_WT3000 = QtWidgets.QCheckBox("WT3000")
        self.checkBox_S2_WT3000.setChecked(True)
        self.checkBox_S2_WT3000.setObjectName("checkBox_S2_WT3000")
        wtLayout.addWidget(self.checkBox_S2_WT3000, 1, 0)
        self.pushButton_S2_WT_3000_CONFIG = QtWidgets.QPushButton("WT_3000_config")
        self.pushButton_S2_WT_3000_CONFIG.setObjectName("pushButton_S2_WT_3000_CONFIG")
        self.pushButton_S2_WT_3000_CONFIG.setStyleSheet("""
            QPushButton { background-color: #6366f1; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #4f46e5; }
        """)
        wtLayout.addWidget(self.pushButton_S2_WT_3000_CONFIG, 1, 1)

        # WT1800
        self.checkBox_S2_WT1800 = QtWidgets.QCheckBox("WT1800")
        self.checkBox_S2_WT1800.setChecked(True)
        self.checkBox_S2_WT1800.setObjectName("checkBox_S2_WT1800")
        wtLayout.addWidget(self.checkBox_S2_WT1800, 1, 2)
        self.pushButton_S2_WT_1800_CONFIG = QtWidgets.QPushButton("WT_1800_config")
        self.pushButton_S2_WT_1800_CONFIG.setObjectName("pushButton_S2_WT_1800_CONFIG")
        self.pushButton_S2_WT_1800_CONFIG.setStyleSheet("""
            QPushButton { background-color: #6366f1; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #4f46e5; }
        """)
        wtLayout.addWidget(self.pushButton_S2_WT_1800_CONFIG, 1, 3)

        # WT1806E
        self.checkBox_S2_WT1806E = QtWidgets.QCheckBox("WT1806E")
        self.checkBox_S2_WT1806E.setChecked(True)
        self.checkBox_S2_WT1806E.setObjectName("checkBox_S2_WT1806E")
        wtLayout.addWidget(self.checkBox_S2_WT1806E, 2, 0)
        self.pushButton_S2_WT_1806E_CONFIG = QtWidgets.QPushButton("WT_1806E_config")
        self.pushButton_S2_WT_1806E_CONFIG.setObjectName("pushButton_S2_WT_1806E_CONFIG")
        self.pushButton_S2_WT_1806E_CONFIG.setStyleSheet("""
            QPushButton { background-color: #6366f1; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #4f46e5; }
        """)
        wtLayout.addWidget(self.pushButton_S2_WT_1806E_CONFIG, 2, 1)

        # WT5000
        self.checkBox_S2_WT5000 = QtWidgets.QCheckBox("WT5000")
        self.checkBox_S2_WT5000.setChecked(True)
        self.checkBox_S2_WT5000.setObjectName("checkBox_S2_WT5000")
        wtLayout.addWidget(self.checkBox_S2_WT5000, 2, 2)
        self.pushButton_S2_WT_5000_CONFIG = QtWidgets.QPushButton("WT_5000_config")
        self.pushButton_S2_WT_5000_CONFIG.setObjectName("pushButton_S2_WT_5000_CONFIG")
        self.pushButton_S2_WT_5000_CONFIG.setStyleSheet("""
            QPushButton { background-color: #6366f1; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #4f46e5; }
        """)
        wtLayout.addWidget(self.pushButton_S2_WT_5000_CONFIG, 2, 3)

        layout.addWidget(grpWT)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Steps 3-11: cosPhi 正/负 设置（统一构建）
    # ══════════════════════════════════════════════
    def _build_cosPhi_steps(self):
        """构建 step3-step11 的 cosPhi 页面"""
        cosPhi_configs = [
            # (step_index, step_num, cb_name, title, dc_prefixes, pf_te_name, pf_label_name, pct_label_name)
            (2,  3,  "checkBox_S3",  "cosPhi 0.0 设置",  ["checkBox_S3_DC1",  "checkBox_S3_DC2",  "checkBox_S3_DC3",  "checkBox_S3_DC4"],
             "textEdit_S3_DC_PF",  "label_76", "label_47"),
            (3,  4,  "checkBox_S4",  "cosPhi 0.5 设置",  ["checkBox_S4_DC1",  "checkBox_S4_DC2",  "checkBox_S4_DC3",  "checkBox_S4_DC4"],
             "textEdit_S4_DC_PF",  "label_77", "label_49"),
            (4,  5,  "checkBox_S5",  "cosPhi 0.8 设置",  ["checkBox_S5_DC1",  "checkBox_S5_DC2",  "checkBox_S5_DC3",  "checkBox_S5_DC4"],
             "textEdit_S5_DC_PF",  "label_78", "label_50"),
            (5,  6,  "checkBox_S6",  "cosPhi 0.9 设置",  ["checkBox_S6_DC1",  "checkBox_S6_DC2",  "checkBox_S6_DC3",  "checkBox_S6_DC4"],
             "textEdit_S6_DC_PF",  "label_79", "label_51"),
            (6,  7,  "checkBox_S7",  "cosPhi 1.0 设置",  ["checkBox_S7_DC1",  "checkBox_S7_DC2",  "checkBox_S7_DC3",  "checkBox_S7_DC4"],
             "textEdit_S7_DC_PF",  "label_84", "label_52"),
            (7,  8,  "checkBox_S8",  "cosPhi -0.5 设置", ["checkBox_S8_DC1",  "checkBox_S8_DC2",  "checkBox_S8_DC3",  "checkBox_S8_DC4"],
             "textEdit_S8_DC_PF",  "label_86", "label_62"),
            (8,  9,  "checkBox_S9",  "cosPhi -0.8 设置", ["checkBox_S9_DC1",  "checkBox_S9_DC2",  "checkBox_S9_DC3",  "checkBox_S9_DC4"],
             "textEdit_S9_DC_PF",  "label_88", "label_61"),
            (9,  10, "checkBox_S10", "cosPhi -0.9 设置", ["checkBox_S10_DC1", "checkBox_S10_DC2", "checkBox_S10_DC3", "checkBox_S10_DC4"],
             "textEdit_S10_DC_PF", "label_85", "label_56"),
            (10, 11, "checkBox_S11", "cosPhi -1.0 设置", ["checkBox_S11_DC1", "checkBox_S11_DC2", "checkBox_S11_DC3", "checkBox_S11_DC4"],
             "textEdit_S11_DC_PF", "label_87", "label_53"),
        ]

        for page_idx, step_num, cb_name, title, dc_cb_names, pf_te_name, pf_lbl_name, pct_lbl_name in cosPhi_configs:
            page = QtWidgets.QWidget()
            page.setStyleSheet("background-color: white;")
            layout = QtWidgets.QVBoxLayout(page)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(12)

            grp = QtWidgets.QGroupBox()
            grp.setObjectName(f"groupBox_cosPhi_{step_num}")
            grp.setTitle(title)
            grp.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
            gLayout = QtWidgets.QGridLayout(grp)
            gLayout.setSpacing(10)
            gLayout.setContentsMargins(16, 24, 16, 12)

            # Step enable checkbox
            stepCb = QtWidgets.QCheckBox(f"step{step_num}")
            stepCb.setChecked(True)
            stepCb.setObjectName(cb_name)
            gLayout.addWidget(stepCb, 0, 0)
            setattr(self, cb_name, stepCb)

            # DC power percentage label + textEdit + %
            pfLbl = QtWidgets.QLabel("功率")
            pfLbl.setObjectName(pf_lbl_name)
            pfLbl.setStyleSheet("font-weight: bold; color: #475569;")
            gLayout.addWidget(pfLbl, 0, 1)
            setattr(self, pf_lbl_name, pfLbl)

            pfTe = QtWidgets.QTextEdit()
            pfTe.setObjectName(pf_te_name)
            pfTe.setFixedSize(80, 28)
            pfTe.setText("100")
            gLayout.addWidget(pfTe, 0, 2)
            setattr(self, pf_te_name, pfTe)

            pctLbl = QtWidgets.QLabel("%")
            pctLbl.setObjectName(pct_lbl_name)
            gLayout.addWidget(pctLbl, 0, 3)
            setattr(self, pct_lbl_name, pctLbl)

            # DC channel checkboxes
            for c, dcCbName in enumerate(dc_cb_names):
                dcCb = QtWidgets.QCheckBox("直流电源" + str(c + 1))
                dcCb.setChecked(True)
                dcCb.setObjectName(dcCbName)
                gLayout.addWidget(dcCb, 1, c)
                setattr(self, dcCbName, dcCb)

            layout.addWidget(grp)
            layout.addStretch()
            self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 12: 关机设置
    # ══════════════════════════════════════════════
    def _build_step_last(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp = QtWidgets.QGroupBox()
        grp.setObjectName("groupBox_end")
        grp.setTitle("关机设置")
        grp.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S_END = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_END.setChecked(True)
        self.checkBox_S_END.setObjectName("checkBox_S_END")
        gLayout.addWidget(self.checkBox_S_END, 0, 0)

        # AC shutdown
        lbl = QtWidgets.QLabel("交流电源")
        lbl.setObjectName("label_8")
        gLayout.addWidget(lbl, 0, 1)
        self.comboBox_S_END_AC = QtWidgets.QComboBox()
        self.comboBox_S_END_AC.setObjectName("comboBox_S_END_AC")
        self.comboBox_S_END_AC.addItems(["关闭", "开启"])
        self.comboBox_S_END_AC.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S_END_AC, 0, 2)

        # DC shutdown - checkboxes + combos
        dc_end_cfg = [
            ("checkBox_S_END_DC1", "直流电源1", "comboBox_S_END_DC1"),
            ("checkBox_S_END_DC2", "直流电源2", "comboBox_S_END_DC2"),
            ("checkBox_S_END_DC3", "直流电源3", "comboBox_S_END_DC3"),
            ("checkBox_S_END_DC4", "直流电源4", "comboBox_S_END_DC4"),
        ]
        for c, (cb_name, cb_text, combo_name) in enumerate(dc_end_cfg):
            col = 1 + c * 2
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            gLayout.addWidget(cb, 1, col)
            setattr(self, cb_name, cb)

            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["关闭", "开启"])
            combo.setFixedWidth(120)
            gLayout.addWidget(combo, 1, col + 1)
            setattr(self, combo_name, combo)

        layout.addWidget(grp)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def retranslateUi(self, Dialog_thaistaticcosPhi):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaistaticcosPhi.setWindowTitle(_translate("Dialog_thaistaticcosPhi", "静态CosPhi项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaistaticcosPhi", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaistaticcosPhi", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaistaticcosPhi", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaistaticcosPhi", "提交"))
