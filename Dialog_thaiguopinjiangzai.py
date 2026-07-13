# -*- coding: utf-8 -*-
# 过频降载项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)


class Ui_Dialog_thaiguopinjiangzai(object):
    def setupUi(self, Dialog_thaiguopinjiangzai):
        Dialog_thaiguopinjiangzai.setObjectName("Dialog_thaiguopinjiangzai")
        Dialog_thaiguopinjiangzai.resize(1395, 900)
        Dialog_thaiguopinjiangzai.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaiguopinjiangzai.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaiguopinjiangzai)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ 过频设置", "④ 关机设置"]
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
        self._build_step1()   # ① AC/DC 电源
        self._build_step2()   # ② 功率分析仪
        self._build_overfreq_steps()  # ③ 过频设置（15个卡片合并）
        self._build_step_last()  # ④ 关机设置

        # ── DC 联动（step1 → 关机步骤） ──
        self._connect_dc_linkage()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaiguopinjiangzai)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaiguopinjiangzai)

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

    # ══════════════════════════════════════════════
    # 过频步骤合并（15个卡片 → 1个滚动页面）
    # ══════════════════════════════════════════════
    def _build_overfreq_steps(self):
        """构建合并的过频设置页面，15个卡片垂直排列，可滚动。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # 步骤启用复选框
        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setChecked(True)
        self.checkBox_S3.setObjectName("checkBox_S3")
        self.checkBox_S3.setStyleSheet("font-size: 13px; font-weight: bold; padding: 4px;")
        layout.addWidget(self.checkBox_S3)

        # QScrollArea 承载所有卡片
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 8, 0, 8)
        scroll_layout.setSpacing(8)

        # 构建15个过频卡片
        for i in range(15):
            step_index = i + 3  # S3 ~ S17
            suffix = f"S{step_index}"
            title = f"过频 {i + 1}"
            card = self._build_overfreq_card(step_index, suffix, title)
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self.stackedWidget.addWidget(page)

    def _build_overfreq_card(self, step_index, suffix, title):
        """构建单个过频配置卡片。"""
        card = QtWidgets.QWidget()
        card.setStyleSheet("background-color: white;")
        cardLayout = QtWidgets.QVBoxLayout(card)
        cardLayout.setContentsMargins(0, 0, 0, 0)
        cardLayout.setSpacing(0)

        grp = QtWidgets.QGroupBox()
        grp.setObjectName(f"groupBox_{suffix}")
        grp.setTitle(title)
        grp.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        # Row 0: checkBox + 交流电压
        cb = QtWidgets.QCheckBox(f"step{step_index}")
        cb.setChecked(True)
        cb.setObjectName(f"checkBox_{suffix}")
        setattr(self, f"checkBox_{suffix}", cb)
        gLayout.addWidget(cb, 0, 0)

        lbl_ac = QtWidgets.QLabel("交流电压")
        lbl_ac.setObjectName(f"label_{suffix}_ac_title")
        gLayout.addWidget(lbl_ac, 0, 1)

        te_volt = QtWidgets.QTextEdit()
        te_volt.setObjectName(f"textEdit_{suffix}_AC_VOLT")
        te_volt.setFixedSize(100, 31)
        te_volt.setText("230")
        setattr(self, f"textEdit_{suffix}_AC_VOLT", te_volt)
        gLayout.addWidget(te_volt, 0, 2)

        lbl_v = QtWidgets.QLabel("V")
        lbl_v.setObjectName(f"label_{suffix}_V")
        gLayout.addWidget(lbl_v, 0, 3)

        # Row 0 右侧: 频率
        lbl_fr_title = QtWidgets.QLabel("频率")
        lbl_fr_title.setObjectName(f"label_{suffix}_fr_title")
        gLayout.addWidget(lbl_fr_title, 0, 4)

        te_fr = QtWidgets.QTextEdit()
        te_fr.setObjectName(f"textEdit_{suffix}_AC_FR")
        te_fr.setFixedSize(100, 31)
        te_fr.setText("50")
        setattr(self, f"textEdit_{suffix}_AC_FR", te_fr)
        gLayout.addWidget(te_fr, 0, 5)

        lbl_hz = QtWidgets.QLabel("Hz")
        lbl_hz.setObjectName(f"label_{suffix}_Hz")
        gLayout.addWidget(lbl_hz, 0, 6)

        # Row 1: 数据采集
        lbl_time_title = QtWidgets.QLabel("数据采集")
        lbl_time_title.setObjectName(f"label_{suffix}_time_title")
        gLayout.addWidget(lbl_time_title, 1, 1)

        te_time = QtWidgets.QTextEdit()
        te_time.setObjectName(f"textEdit_{suffix}_TIME")
        te_time.setFixedSize(100, 31)
        te_time.setText("2.5")
        setattr(self, f"textEdit_{suffix}_TIME", te_time)
        gLayout.addWidget(te_time, 1, 2)

        combo_time = QtWidgets.QComboBox()
        combo_time.setObjectName(f"comboBox_{suffix}_TIME")
        combo_time.addItems(["秒", "毫秒", "分钟"])
        combo_time.setFixedWidth(120)
        setattr(self, f"comboBox_{suffix}_TIME", combo_time)
        gLayout.addWidget(combo_time, 1, 3)

        # 联动：步骤复选框禁用时，禁用内部控件
        inner_widgets = [te_volt, te_fr, te_time, combo_time,
                         lbl_ac, lbl_v, lbl_fr_title, lbl_hz, lbl_time_title]
        step_cb = cb  # 局部引用

        def _on_step_toggled(checked, widgets=inner_widgets, scb=step_cb):
            for w in widgets:
                w.setEnabled(checked)

        cb.toggled.connect(_on_step_toggled)

        cardLayout.addWidget(grp)
        return card

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
        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("交流电源设置")
        self.groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(self.groupBox)
        gLayout.setSpacing(8)
        gLayout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        gLayout.addWidget(self.checkBox_S1, 0, 0, 1, 2)

        lbl_title = QtWidgets.QLabel("交流电源")
        lbl_title.setObjectName("label_3")
        gLayout.addWidget(lbl_title, 0, 2)

        # Row 0: AC switch + AC_VOLT1
        gLayout.addWidget(QtWidgets.QLabel("交流电压1"), 0, 3)
        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S1_AC, 0, 4)

        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S1_AC_VOLT.setText("230")
        gLayout.addWidget(self.textEdit_S1_AC_VOLT, 0, 5)
        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        gLayout.addWidget(self.label_5, 0, 6)

        # AC_VOLT2
        gLayout.addWidget(QtWidgets.QLabel("交流电压2"), 0, 7)
        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(100, 31)
        self.textEdit_S1_AC_VOLT_2.setText("230")
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 8)
        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        gLayout.addWidget(self.label_107, 0, 9)

        # Row 1: AC_2 type + AC_VOLT3 + FR
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S1_AC_2, 1, 4)

        gLayout.addWidget(QtWidgets.QLabel("交流电压3"), 1, 3)
        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(100, 31)
        self.textEdit_S1_AC_VOLT_3.setText("230")
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 5)
        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        gLayout.addWidget(self.label_102, 1, 6)

        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        gLayout.addWidget(self.label_19, 1, 7)
        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(100, 31)
        self.textEdit_S1_AC_FR.setText("50")
        gLayout.addWidget(self.textEdit_S1_AC_FR, 1, 8)
        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        gLayout.addWidget(self.label_18, 1, 9)

        layout.addWidget(self.groupBox)

        # ── DC 电源组 (4 channels) ──
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流电源设置")
        self.groupBox_2.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g2Layout = QtWidgets.QGridLayout(self.groupBox_2)
        g2Layout.setSpacing(6)
        g2Layout.setContentsMargins(12, 20, 12, 12)

        # Header
        headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]
        for c, h in enumerate(headers):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g2Layout.addWidget(lbl, 0, c)

        dc_channels = [
            ("1", "checkBox_S1_DC1", "直流电源1", "comboBox_S1_DC1",
             ["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"]),
            ("2", "checkBox_S1_DC2", "直流电源2", "comboBox_S1_DC2",
             ["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"]),
            ("3", "checkBox_S1_DC3", "直流电源3", "comboBox_S1_DC3",
             ["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"]),
            ("4", "checkBox_S1_DC4", "直流电源4", "comboBox_S1_DC4",
             ["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"]),
        ]
        for r, (ch_num, cb_name, cb_text, combo_name, te_names) in enumerate(dc_channels, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            setattr(self, cb_name, cb)
            g2Layout.addWidget(cb, r, 0)

            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["开启", "关闭"])
            combo.setFixedWidth(100)
            setattr(self, combo_name, combo)
            g2Layout.addWidget(combo, r, 1)

            for c, name in enumerate(te_names, start=2):
                te = QtWidgets.QTextEdit()
                te.setObjectName(name)
                te.setFixedSize(80, 28)
                setattr(self, name, te)
                g2Layout.addWidget(te, r, c)

        # DC row labels for units
        for r in range(1, 5):
            for c, unit in [(2, "V"), (3, "A"), (4, "V"), (5, "A"), (6, "%")]:
                lbl = QtWidgets.QLabel(unit)
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                lbl.setStyleSheet("color: #94a3b8; font-size: 10px;")
                g2Layout.addWidget(lbl, r + 4, c)

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

        layout.addWidget(self.groupBox_5)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step last: 关机设置
    # ══════════════════════════════════════════════
    def _build_step_last(self):
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

        # Row 0: AC
        self.label_8 = QtWidgets.QLabel("交流电源")
        self.label_8.setObjectName("label_8")
        g11Layout.addWidget(self.label_8, 0, 1)

        self.comboBox_S_End_AC = QtWidgets.QComboBox()
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItems(["关闭", "开启"])
        self.comboBox_S_End_AC.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_AC, 0, 2)

        # Row 1: DC1, DC2, DC3, DC4
        self.checkBox_S_End_DC1 = QtWidgets.QCheckBox("直流电源1")
        self.checkBox_S_End_DC1.setChecked(True)
        self.checkBox_S_End_DC1.setObjectName("checkBox_S_End_DC1")
        g11Layout.addWidget(self.checkBox_S_End_DC1, 1, 0)

        self.comboBox_S_End_DC1 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC1.setObjectName("comboBox_S_End_DC1")
        self.comboBox_S_End_DC1.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC1.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC1, 1, 1)

        self.checkBox_S_End_DC2 = QtWidgets.QCheckBox("直流电源2")
        self.checkBox_S_End_DC2.setChecked(True)
        self.checkBox_S_End_DC2.setObjectName("checkBox_S_End_DC2")
        g11Layout.addWidget(self.checkBox_S_End_DC2, 1, 2)

        self.comboBox_S_End_DC2 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC2.setObjectName("comboBox_S_End_DC2")
        self.comboBox_S_End_DC2.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC2.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC2, 1, 3)

        self.checkBox_S_End_DC3 = QtWidgets.QCheckBox("直流电源3")
        self.checkBox_S_End_DC3.setChecked(True)
        self.checkBox_S_End_DC3.setObjectName("checkBox_S_End_DC3")
        g11Layout.addWidget(self.checkBox_S_End_DC3, 1, 4)

        self.comboBox_S_End_DC3 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC3.setObjectName("comboBox_S_End_DC3")
        self.comboBox_S_End_DC3.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC3.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC3, 1, 5)

        self.checkBox_S_End_DC4 = QtWidgets.QCheckBox("直流电源4")
        self.checkBox_S_End_DC4.setChecked(True)
        self.checkBox_S_End_DC4.setObjectName("checkBox_S_End_DC4")
        g11Layout.addWidget(self.checkBox_S_End_DC4, 1, 6)

        self.comboBox_S_End_DC4 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC4.setObjectName("comboBox_S_End_DC4")
        self.comboBox_S_End_DC4.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC4.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC4, 1, 7)

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

    def retranslateUi(self, Dialog_thaiguopinjiangzai):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaiguopinjiangzai.setWindowTitle(_translate("Dialog_thaiguopinjiangzai", "过频降载项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaiguopinjiangzai", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaiguopinjiangzai", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaiguopinjiangzai", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaiguopinjiangzai", "提交"))
