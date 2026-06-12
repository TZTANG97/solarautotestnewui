# -*- coding: utf-8 -*-
# 电压闪变项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_thaiguodianyashanbian(object):
    def setupUi(self, Dialog_thaiguodianyashanbian):
        Dialog_thaiguodianyashanbian.setObjectName("Dialog_thaiguodianyashanbian")
        Dialog_thaiguodianyashanbian.resize(1300, 850)
        Dialog_thaiguodianyashanbian.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaiguodianyashanbian.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaiguodianyashanbian)
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

        topLayout.addStretch()

        # 横向步骤指示器
        self._step_labels = []
        step_titles = ["① AC/DC 电源", "② WT3000 闪变", "③ DC 开关循环", "④ 判定结果", "⑤ 关机设置"]
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

        # ── 连接步骤复选框联动 ──
        self._connect_step_toggles()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaiguodianyashanbian)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaiguodianyashanbian)

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

    def _connect_step_toggles(self):
        """连接步骤复选框与子控件的联动"""
        # Step 1: AC/DC 电源
        s1_children = [
            self.comboBox_S1_AC, self.textEdit_S1_AC_VOLT, self.textEdit_S1_AC_VOLT_2,
            self.textEdit_S1_AC_VOLT_3, self.textEdit_S1_AC_FR, self.comboBox_S1_AC_2,
            self.checkBox_S1_DC1, self.comboBox_S1_DC1, self.textEdit_S1_DC1_VOLT,
            self.textEdit_S1_DC1_CURR, self.textEdit_S1_DC1_Voc, self.textEdit_S1_DC1_Isc,
            self.textEdit_S1_DC1_PF, self.checkBox_S1_DC2, self.comboBox_S1_DC2,
            self.textEdit_S1_DC2_VOLT, self.textEdit_S1_DC2_CURR, self.textEdit_S1_DC2_Voc,
            self.textEdit_S1_DC2_Isc, self.textEdit_S1_DC2_PF, self.checkBox_S1_DC3,
            self.comboBox_S1_DC3, self.textEdit_S1_DC3_VOLT, self.textEdit_S1_DC3_CURR,
            self.textEdit_S1_DC3_Voc, self.textEdit_S1_DC3_Isc, self.textEdit_S1_DC3_PF,
            self.checkBox_S1_DC4, self.comboBox_S1_DC4, self.textEdit_S1_DC4_VOLT,
            self.textEdit_S1_DC4_CURR, self.textEdit_S1_DC4_Voc, self.textEdit_S1_DC4_Isc,
            self.textEdit_S1_DC4_PF, self.textEdit_S1_ACWaitTIME, self.comboBox_S1_ACWaitTIME,
            self.textEdit_S1_TIME, self.comboBox_S1_TIME,
        ]

        def _on_s1_toggled(checked):
            for w in s1_children:
                w.setEnabled(checked)

        self.checkBox_S1.toggled.connect(_on_s1_toggled)
        _on_s1_toggled(self.checkBox_S1.isChecked())

        # Step 2: WT3000 闪变
        s2_children = [
            self.comboBox_S2_WT, self.comboBox_S2_WT3000_Setting,
            self.comboBox_S2_PER_FLICK_COUNT, self.textEdit_S2_TIME, self.comboBox_S2_TIME,
        ]

        def _on_s2_toggled(checked):
            for w in s2_children:
                w.setEnabled(checked)

        self.checkBox_S2.toggled.connect(_on_s2_toggled)
        _on_s2_toggled(self.checkBox_S2.isChecked())

        # Step 3: DC 开关循环
        s3_children = [
            self.checkBox_S3_DC1, self.comboBox_S3_DC1, self.checkBox_S3_DC2,
            self.comboBox_S3_DC2, self.checkBox_S3_DC3, self.comboBox_S3_DC3,
            self.checkBox_S3_DC4, self.comboBox_S3_DC4, self.checkBox_S3_DC1_2,
            self.comboBox_S3_DC1_2, self.checkBox_S3_DC2_2, self.comboBox_S3_DC2_2,
            self.checkBox_S3_DC3_2, self.comboBox_S3_DC3_2, self.checkBox_S3_DC4_2,
            self.comboBox_S3_DC4_2, self.textEdit_S3_TIME, self.comboBox_S3_TIME,
            self.textEdit_S3_TIME_2, self.comboBox_S3_TIME_2, self.textEdit_S3_CYCLE_TIME,
        ]

        def _on_s3_toggled(checked):
            for w in s3_children:
                w.setEnabled(checked)

        self.checkBox_S3.toggled.connect(_on_s3_toggled)
        _on_s3_toggled(self.checkBox_S3.isChecked())

        # Step 4: 判定结果
        s4_children = [
            self.comboBox_S4_WT3000_1, self.comboBox_S4_WT3000_2, self.comboBox_S4_WT3000_3,
        ]

        def _on_s4_toggled(checked):
            for w in s4_children:
                w.setEnabled(checked)

        self.checkBox_S4.toggled.connect(_on_s4_toggled)
        _on_s4_toggled(self.checkBox_S4.isChecked())

        # Step 5: 关机设置
        s5_children = [
            self.comboBox_S5_AC, self.checkBox_S5_DC1, self.comboBox_S5_DC1,
            self.checkBox_S5_DC2, self.comboBox_S5_DC2, self.checkBox_S5_DC3,
            self.comboBox_S5_DC3, self.checkBox_S5_DC4, self.comboBox_S5_DC4,
        ]

        def _on_s5_toggled(checked):
            for w in s5_children:
                w.setEnabled(checked)

        self.checkBox_S5.toggled.connect(_on_s5_toggled)
        _on_s5_toggled(self.checkBox_S5.isChecked())

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

        g6Layout.addWidget(QtWidgets.QLabel("交流电压1:"), 0, 2)
        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(120)
        g6Layout.addWidget(self.comboBox_S1_AC, 0, 3)

        g6Layout.addWidget(QtWidgets.QLabel("V"), 0, 4)
        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(100, 31)
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT, 0, 5)

        g6Layout.addWidget(QtWidgets.QLabel("交流电压2:"), 0, 6)
        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(100, 31)
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 7)

        g6Layout.addWidget(QtWidgets.QLabel("V"), 0, 8)

        g6Layout.addWidget(QtWidgets.QLabel("交流电压3:"), 1, 2)
        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(100, 31)
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 3)

        g6Layout.addWidget(QtWidgets.QLabel("V"), 1, 4)

        g6Layout.addWidget(QtWidgets.QLabel("频率:"), 1, 6)
        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(100, 31)
        g6Layout.addWidget(self.textEdit_S1_AC_FR, 1, 7)
        g6Layout.addWidget(QtWidgets.QLabel("Hz"), 1, 8)

        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        g6Layout.addWidget(self.comboBox_S1_AC_2, 1, 3)

        layout.addWidget(self.groupBox_6)

        # ── DC 电源组 (4 channels) ──
        self.groupBox_7 = QtWidgets.QGroupBox()
        self.groupBox_7.setObjectName("groupBox_7")
        self.groupBox_7.setTitle("直流电源设置")
        self.groupBox_7.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g7Layout = QtWidgets.QGridLayout(self.groupBox_7)
        g7Layout.setSpacing(6)
        g7Layout.setContentsMargins(12, 20, 12, 12)

        # Header
        headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]
        for c, h in enumerate(headers):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g7Layout.addWidget(lbl, 0, c)

        # DC1
        r = 1
        self.checkBox_S1_DC1 = QtWidgets.QCheckBox("直流电源1")
        self.checkBox_S1_DC1.setChecked(True)
        self.checkBox_S1_DC1.setObjectName("checkBox_S1_DC1")
        g7Layout.addWidget(self.checkBox_S1_DC1, r, 0)
        self.comboBox_S1_DC1 = QtWidgets.QComboBox()
        self.comboBox_S1_DC1.setObjectName("comboBox_S1_DC1")
        self.comboBox_S1_DC1.addItems(["开启", "关闭"])
        self.comboBox_S1_DC1.setFixedWidth(100)
        g7Layout.addWidget(self.comboBox_S1_DC1, r, 1)
        for c, name in enumerate(["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            g7Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC2
        r = 2
        self.checkBox_S1_DC2 = QtWidgets.QCheckBox("直流电源2")
        self.checkBox_S1_DC2.setChecked(True)
        self.checkBox_S1_DC2.setObjectName("checkBox_S1_DC2")
        g7Layout.addWidget(self.checkBox_S1_DC2, r, 0)
        self.comboBox_S1_DC2 = QtWidgets.QComboBox()
        self.comboBox_S1_DC2.setObjectName("comboBox_S1_DC2")
        self.comboBox_S1_DC2.addItems(["开启", "关闭"])
        self.comboBox_S1_DC2.setFixedWidth(100)
        g7Layout.addWidget(self.comboBox_S1_DC2, r, 1)
        for c, name in enumerate(["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            g7Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC3
        r = 3
        self.checkBox_S1_DC3 = QtWidgets.QCheckBox("直流电源3")
        self.checkBox_S1_DC3.setChecked(True)
        self.checkBox_S1_DC3.setObjectName("checkBox_S1_DC3")
        g7Layout.addWidget(self.checkBox_S1_DC3, r, 0)
        self.comboBox_S1_DC3 = QtWidgets.QComboBox()
        self.comboBox_S1_DC3.setObjectName("comboBox_S1_DC3")
        self.comboBox_S1_DC3.addItems(["开启", "关闭"])
        self.comboBox_S1_DC3.setFixedWidth(100)
        g7Layout.addWidget(self.comboBox_S1_DC3, r, 1)
        for c, name in enumerate(["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            g7Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC4
        r = 4
        self.checkBox_S1_DC4 = QtWidgets.QCheckBox("直流电源4")
        self.checkBox_S1_DC4.setChecked(True)
        self.checkBox_S1_DC4.setObjectName("checkBox_S1_DC4")
        g7Layout.addWidget(self.checkBox_S1_DC4, r, 0)
        self.comboBox_S1_DC4 = QtWidgets.QComboBox()
        self.comboBox_S1_DC4.setObjectName("comboBox_S1_DC4")
        self.comboBox_S1_DC4.addItems(["开启", "关闭"])
        self.comboBox_S1_DC4.setFixedWidth(100)
        g7Layout.addWidget(self.comboBox_S1_DC4, r, 1)
        for c, name in enumerate(["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            g7Layout.addWidget(te, r, c)
            setattr(self, name, te)

        layout.addWidget(self.groupBox_7)

        # ── 时序组 ──
        self.groupBox_5 = QtWidgets.QGroupBox()
        self.groupBox_5.setObjectName("groupBox_5")
        self.groupBox_5.setTitle("时序设置")
        self.groupBox_5.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g5Layout = QtWidgets.QGridLayout(self.groupBox_5)
        g5Layout.setSpacing(8)
        g5Layout.setContentsMargins(12, 20, 12, 12)

        self.label_131 = QtWidgets.QLabel("等待时间:")
        self.label_131.setObjectName("label_131")
        g5Layout.addWidget(self.label_131, 0, 0)
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(100, 31)
        self.textEdit_S1_ACWaitTIME.setText("5")
        g5Layout.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(120)
        g5Layout.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        self.label_132 = QtWidgets.QLabel("启机时间:")
        self.label_132.setObjectName("label_132")
        g5Layout.addWidget(self.label_132, 0, 3)
        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(100, 31)
        self.textEdit_S1_TIME.setText("5")
        g5Layout.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(120)
        g5Layout.addWidget(self.comboBox_S1_TIME, 0, 5)

        layout.addWidget(self.groupBox_5)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 2: WT3000 闪变设置
    # ══════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_3 = QtWidgets.QGroupBox()
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setTitle("WT3000 闪变测量设置")
        self.groupBox_3.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g3Layout = QtWidgets.QGridLayout(self.groupBox_3)
        g3Layout.setSpacing(10)
        g3Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        g3Layout.addWidget(self.checkBox_S2, 0, 0)

        self.label_6 = QtWidgets.QLabel("WT3000")
        self.label_6.setObjectName("label_6")
        g3Layout.addWidget(self.label_6, 0, 1)

        self.comboBox_S2_WT = QtWidgets.QComboBox()
        self.comboBox_S2_WT.setObjectName("comboBox_S2_WT")
        self.comboBox_S2_WT.addItems(["单相", "三相"])
        self.comboBox_S2_WT.setFixedWidth(120)
        g3Layout.addWidget(self.comboBox_S2_WT, 0, 2)

        self.comboBox_S2_WT3000_Setting = QtWidgets.QComboBox()
        self.comboBox_S2_WT3000_Setting.setObjectName("comboBox_S2_WT3000_Setting")
        self.comboBox_S2_WT3000_Setting.addItems(["ELEMENT1", "ELEMENT2", "ELEMENT3"])
        self.comboBox_S2_WT3000_Setting.setFixedWidth(120)
        g3Layout.addWidget(self.comboBox_S2_WT3000_Setting, 0, 3)

        self.label_31 = QtWidgets.QLabel("每组闪变")
        self.label_31.setObjectName("label_31")
        g3Layout.addWidget(self.label_31, 0, 4)

        self.comboBox_S2_PER_FLICK_COUNT = QtWidgets.QComboBox()
        self.comboBox_S2_PER_FLICK_COUNT.setObjectName("comboBox_S2_PER_FLICK_COUNT")
        self.comboBox_S2_PER_FLICK_COUNT.addItems(["3", "1", "2"])
        self.comboBox_S2_PER_FLICK_COUNT.setFixedWidth(120)
        g3Layout.addWidget(self.comboBox_S2_PER_FLICK_COUNT, 0, 5)

        self.label_32 = QtWidgets.QLabel("次")
        self.label_32.setObjectName("label_32")
        g3Layout.addWidget(self.label_32, 0, 6)

        self.label_30 = QtWidgets.QLabel("首次闪变间隔:")
        self.label_30.setObjectName("label_30")
        g3Layout.addWidget(self.label_30, 1, 1)

        self.textEdit_S2_TIME = QtWidgets.QTextEdit()
        self.textEdit_S2_TIME.setObjectName("textEdit_S2_TIME")
        self.textEdit_S2_TIME.setFixedSize(100, 31)
        self.textEdit_S2_TIME.setText("4")
        g3Layout.addWidget(self.textEdit_S2_TIME, 1, 2)

        self.comboBox_S2_TIME = QtWidgets.QComboBox()
        self.comboBox_S2_TIME.setObjectName("comboBox_S2_TIME")
        self.comboBox_S2_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S2_TIME.setFixedWidth(120)
        g3Layout.addWidget(self.comboBox_S2_TIME, 1, 3)

        layout.addWidget(self.groupBox_3)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 3: DC 开关循环
    # ══════════════════════════════════════════════
    def _build_step3(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("DC 开关循环设置")
        self.groupBox_2.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g2Layout = QtWidgets.QGridLayout(self.groupBox_2)
        g2Layout.setSpacing(8)
        g2Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setChecked(True)
        self.checkBox_S3.setObjectName("checkBox_S3")
        g2Layout.addWidget(self.checkBox_S3, 0, 0)

        # 第一次状态
        g2Layout.addWidget(QtWidgets.QLabel("第一次状态:"), 1, 0)
        dc1_cfg = [
            ("checkBox_S3_DC1", "直流电源1", "comboBox_S3_DC1", ["关闭", "开启"]),
            ("checkBox_S3_DC2", "直流电源2", "comboBox_S3_DC2", ["关闭", "开启"]),
            ("checkBox_S3_DC3", "直流电源3", "comboBox_S3_DC3", ["关闭", "开启"]),
            ("checkBox_S3_DC4", "直流电源4", "comboBox_S3_DC4", ["关闭", "开启"]),
        ]
        for c, (cb_name, cb_text, combo_name, items) in enumerate(dc1_cfg):
            col = 1 + c * 2
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g2Layout.addWidget(cb, 1, col)
            setattr(self, cb_name, cb)
            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(items)
            combo.setFixedWidth(120)
            g2Layout.addWidget(combo, 1, col + 1)
            setattr(self, combo_name, combo)

        # 第二次状态
        g2Layout.addWidget(QtWidgets.QLabel("第二次状态:"), 2, 0)
        dc2_cfg = [
            ("checkBox_S3_DC1_2", "直流电源1", "comboBox_S3_DC1_2", ["开启", "关闭"]),
            ("checkBox_S3_DC2_2", "直流电源2", "comboBox_S3_DC2_2", ["开启", "关闭"]),
            ("checkBox_S3_DC3_2", "直流电源3", "comboBox_S3_DC3_2", ["开启", "关闭"]),
            ("checkBox_S3_DC4_2", "直流电源4", "comboBox_S3_DC4_2", ["开启", "关闭"]),
        ]
        for c, (cb_name, cb_text, combo_name, items) in enumerate(dc2_cfg):
            col = 1 + c * 2
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g2Layout.addWidget(cb, 2, col)
            setattr(self, cb_name, cb)
            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(items)
            combo.setFixedWidth(120)
            g2Layout.addWidget(combo, 2, col + 1)
            setattr(self, combo_name, combo)

        # 时间设置
        g2Layout.addWidget(QtWidgets.QLabel("持续时间:"), 3, 0)
        self.textEdit_S3_TIME = QtWidgets.QTextEdit()
        self.textEdit_S3_TIME.setObjectName("textEdit_S3_TIME")
        self.textEdit_S3_TIME.setFixedSize(100, 31)
        self.textEdit_S3_TIME.setText("15")
        g2Layout.addWidget(self.textEdit_S3_TIME, 3, 1)
        self.comboBox_S3_TIME = QtWidgets.QComboBox()
        self.comboBox_S3_TIME.setObjectName("comboBox_S3_TIME")
        self.comboBox_S3_TIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S3_TIME.setFixedWidth(120)
        g2Layout.addWidget(self.comboBox_S3_TIME, 3, 2)

        g2Layout.addWidget(QtWidgets.QLabel("闪变间隔:"), 3, 3)
        self.textEdit_S3_TIME_2 = QtWidgets.QTextEdit()
        self.textEdit_S3_TIME_2.setObjectName("textEdit_S3_TIME_2")
        self.textEdit_S3_TIME_2.setFixedSize(100, 31)
        self.textEdit_S3_TIME_2.setText("3")
        g2Layout.addWidget(self.textEdit_S3_TIME_2, 3, 4)
        self.comboBox_S3_TIME_2 = QtWidgets.QComboBox()
        self.comboBox_S3_TIME_2.setObjectName("comboBox_S3_TIME_2")
        self.comboBox_S3_TIME_2.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S3_TIME_2.setFixedWidth(120)
        g2Layout.addWidget(self.comboBox_S3_TIME_2, 3, 5)

        g2Layout.addWidget(QtWidgets.QLabel("循环次数:"), 3, 6)
        self.textEdit_S3_CYCLE_TIME = QtWidgets.QTextEdit()
        self.textEdit_S3_CYCLE_TIME.setObjectName("textEdit_S3_CYCLE_TIME")
        self.textEdit_S3_CYCLE_TIME.setFixedSize(100, 31)
        self.textEdit_S3_CYCLE_TIME.setText("12")
        g2Layout.addWidget(self.textEdit_S3_CYCLE_TIME, 3, 7)

        layout.addWidget(self.groupBox_2)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 4: 判定结果
    # ══════════════════════════════════════════════
    def _build_step4(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("WT3000 判定设置")
        self.groupBox_4.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g4Layout = QtWidgets.QGridLayout(self.groupBox_4)
        g4Layout.setSpacing(10)
        g4Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S4 = QtWidgets.QCheckBox("step4")
        self.checkBox_S4.setChecked(True)
        self.checkBox_S4.setObjectName("checkBox_S4")
        g4Layout.addWidget(self.checkBox_S4, 0, 0)

        self.label_7 = QtWidgets.QLabel("WT3000")
        self.label_7.setObjectName("label_7")
        g4Layout.addWidget(self.label_7, 0, 1)

        self.comboBox_S4_WT3000_1 = QtWidgets.QComboBox()
        self.comboBox_S4_WT3000_1.setObjectName("comboBox_S4_WT3000_1")
        self.comboBox_S4_WT3000_1.addItems(["判断是结束", "判断未结束"])
        self.comboBox_S4_WT3000_1.setFixedWidth(120)
        g4Layout.addWidget(self.comboBox_S4_WT3000_1, 0, 2)

        self.comboBox_S4_WT3000_2 = QtWidgets.QComboBox()
        self.comboBox_S4_WT3000_2.setObjectName("comboBox_S4_WT3000_2")
        self.comboBox_S4_WT3000_2.addItems(["保存图片", "不保存图片"])
        self.comboBox_S4_WT3000_2.setFixedWidth(120)
        g4Layout.addWidget(self.comboBox_S4_WT3000_2, 0, 3)

        self.comboBox_S4_WT3000_3 = QtWidgets.QComboBox()
        self.comboBox_S4_WT3000_3.setObjectName("comboBox_S4_WT3000_3")
        self.comboBox_S4_WT3000_3.addItems(["保存至本地", "不保存图片"])
        self.comboBox_S4_WT3000_3.setFixedWidth(120)
        g4Layout.addWidget(self.comboBox_S4_WT3000_3, 0, 4)

        layout.addWidget(self.groupBox_4)
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

        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("关机设置")
        self.groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(self.groupBox)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S5 = QtWidgets.QCheckBox("step5")
        self.checkBox_S5.setChecked(True)
        self.checkBox_S5.setObjectName("checkBox_S5")
        gLayout.addWidget(self.checkBox_S5, 0, 0)

        self.label_8 = QtWidgets.QLabel("交流电源")
        self.label_8.setObjectName("label_8")
        gLayout.addWidget(self.label_8, 0, 1)

        self.comboBox_S5_AC = QtWidgets.QComboBox()
        self.comboBox_S5_AC.setObjectName("comboBox_S5_AC")
        self.comboBox_S5_AC.addItems(["关闭", "开启"])
        self.comboBox_S5_AC.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S5_AC, 0, 2)

        dc5_cfg = [
            ("checkBox_S5_DC1", "直流电源1", "comboBox_S5_DC1"),
            ("checkBox_S5_DC2", "直流电源2", "comboBox_S5_DC2"),
            ("checkBox_S5_DC3", "直流电源3", "comboBox_S5_DC3"),
            ("checkBox_S5_DC4", "直流电源4", "comboBox_S5_DC4"),
        ]
        for c, (cb_name, cb_text, combo_name) in enumerate(dc5_cfg):
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

        layout.addWidget(self.groupBox)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def retranslateUi(self, Dialog_thaiguodianyashanbian):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaiguodianyashanbian.setWindowTitle(_translate("Dialog_thaiguodianyashanbian", "电压闪变项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaiguodianyashanbian", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaiguodianyashanbian", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaiguodianyashanbian", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaiguodianyashanbian", "提交"))
