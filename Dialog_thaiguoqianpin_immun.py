# -*- coding: utf-8 -*-
# 过欠频稳定性项目配置 - 横向步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_thaiguoqianpin_immun(object):
    def setupUi(self, Dialog_thaiguoqianpin_immun):
        Dialog_thaiguoqianpin_immun.setObjectName("Dialog_thaiguoqianpin_immun")
        Dialog_thaiguoqianpin_immun.resize(1300, 850)
        Dialog_thaiguoqianpin_immun.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaiguoqianpin_immun.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaiguoqianpin_immun)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ 频率扫描1", "④ 频率扫描2", "⑤ 频率扫描3", "⑥ 频率扫描4", "⑦ 频率扫描5", "⑧ 频率扫描6", "⑨ 频率扫描7", "⑩ 频率扫描8", "⑪ 频率扫描9", "⑫ 关机设置"]
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
        self._build_step3()   # 频率扫描1
        self._build_step4()   # 频率扫描2
        self._build_step5()   # 频率扫描3
        self._build_step6()   # 频率扫描4
        self._build_step7()   # 频率扫描5
        self._build_step8()   # 频率扫描6
        self._build_step9()   # 频率扫描7
        self._build_step10()  # 频率扫描8
        self._build_step11()  # 频率扫描9
        self._build_step12()  # 关机设置

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaiguoqianpin_immun)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaiguoqianpin_immun)

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
        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("交流电源设置")
        self.groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gAcLayout = QtWidgets.QGridLayout(self.groupBox)
        gAcLayout.setSpacing(8)
        gAcLayout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        gAcLayout.addWidget(self.checkBox_S1, 0, 0)

        self.label_3 = QtWidgets.QLabel("交流电源")
        self.label_3.setObjectName("label_3")
        gAcLayout.addWidget(self.label_3, 0, 1)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(120)
        gAcLayout.addWidget(self.comboBox_S1_AC, 0, 2)

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        gAcLayout.addWidget(self.label_4, 0, 3)

        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(100, 31)
        gAcLayout.addWidget(self.textEdit_S1_AC_VOLT, 0, 4)

        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        gAcLayout.addWidget(self.label_5, 0, 5)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        gAcLayout.addWidget(self.label_113, 0, 6)

        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(100, 31)
        gAcLayout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 7)

        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        gAcLayout.addWidget(self.label_107, 0, 8)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        gAcLayout.addWidget(self.label_123, 1, 0)

        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(100, 31)
        gAcLayout.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 1)

        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        gAcLayout.addWidget(self.label_102, 1, 2)

        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        gAcLayout.addWidget(self.label_19, 1, 3)

        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(100, 31)
        gAcLayout.addWidget(self.textEdit_S1_AC_FR, 1, 4)

        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        gAcLayout.addWidget(self.label_18, 1, 5)

        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        gAcLayout.addWidget(self.comboBox_S1_AC_2, 1, 6)

        layout.addWidget(self.groupBox)

        # ── DC 电源组 (4 channels) ──
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流电源设置")
        self.groupBox_2.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gDcLayout = QtWidgets.QGridLayout(self.groupBox_2)
        gDcLayout.setSpacing(6)
        gDcLayout.setContentsMargins(12, 20, 12, 12)

        # Header
        headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]
        for c, h in enumerate(headers):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            gDcLayout.addWidget(lbl, 0, c)

        # DC1
        r = 1
        self.checkBox_S1_DC1 = QtWidgets.QCheckBox("直流电源1")
        self.checkBox_S1_DC1.setChecked(True)
        self.checkBox_S1_DC1.setObjectName("checkBox_S1_DC1")
        gDcLayout.addWidget(self.checkBox_S1_DC1, r, 0)
        self.comboBox_S1_DC1 = QtWidgets.QComboBox()
        self.comboBox_S1_DC1.setObjectName("comboBox_S1_DC1")
        self.comboBox_S1_DC1.addItems(["开启", "关闭"])
        self.comboBox_S1_DC1.setFixedWidth(100)
        gDcLayout.addWidget(self.comboBox_S1_DC1, r, 1)
        for c, name in enumerate(["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            gDcLayout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC2
        r = 2
        self.checkBox_S1_DC2 = QtWidgets.QCheckBox("直流电源2")
        self.checkBox_S1_DC2.setChecked(True)
        self.checkBox_S1_DC2.setObjectName("checkBox_S1_DC2")
        gDcLayout.addWidget(self.checkBox_S1_DC2, r, 0)
        self.comboBox_S1_DC2 = QtWidgets.QComboBox()
        self.comboBox_S1_DC2.setObjectName("comboBox_S1_DC2")
        self.comboBox_S1_DC2.addItems(["开启", "关闭"])
        self.comboBox_S1_DC2.setFixedWidth(100)
        gDcLayout.addWidget(self.comboBox_S1_DC2, r, 1)
        for c, name in enumerate(["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            gDcLayout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC3
        r = 3
        self.checkBox_S1_DC3 = QtWidgets.QCheckBox("直流电源3")
        self.checkBox_S1_DC3.setChecked(True)
        self.checkBox_S1_DC3.setObjectName("checkBox_S1_DC3")
        gDcLayout.addWidget(self.checkBox_S1_DC3, r, 0)
        self.comboBox_S1_DC3 = QtWidgets.QComboBox()
        self.comboBox_S1_DC3.setObjectName("comboBox_S1_DC3")
        self.comboBox_S1_DC3.addItems(["开启", "关闭"])
        self.comboBox_S1_DC3.setFixedWidth(100)
        gDcLayout.addWidget(self.comboBox_S1_DC3, r, 1)
        for c, name in enumerate(["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            gDcLayout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC4
        r = 4
        self.checkBox_S1_DC4 = QtWidgets.QCheckBox("直流电源4")
        self.checkBox_S1_DC4.setChecked(True)
        self.checkBox_S1_DC4.setObjectName("checkBox_S1_DC4")
        gDcLayout.addWidget(self.checkBox_S1_DC4, r, 0)
        self.comboBox_S1_DC4 = QtWidgets.QComboBox()
        self.comboBox_S1_DC4.setObjectName("comboBox_S1_DC4")
        self.comboBox_S1_DC4.addItems(["开启", "关闭"])
        self.comboBox_S1_DC4.setFixedWidth(100)
        gDcLayout.addWidget(self.comboBox_S1_DC4, r, 1)
        for c, name in enumerate(["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            gDcLayout.addWidget(te, r, c)
            setattr(self, name, te)

        layout.addWidget(self.groupBox_2)

        # ── 时序组 ──
        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("时序设置")
        self.groupBox_4.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gTimeLayout = QtWidgets.QGridLayout(self.groupBox_4)
        gTimeLayout.setSpacing(8)
        gTimeLayout.setContentsMargins(12, 20, 12, 12)

        self.label_131 = QtWidgets.QLabel("等待时间:")
        self.label_131.setObjectName("label_131")
        gTimeLayout.addWidget(self.label_131, 0, 0)
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(100, 31)
        gTimeLayout.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(120)
        gTimeLayout.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        self.label_132 = QtWidgets.QLabel("启机时间:")
        self.label_132.setObjectName("label_132")
        gTimeLayout.addWidget(self.label_132, 0, 3)
        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(100, 31)
        gTimeLayout.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(120)
        gTimeLayout.addWidget(self.comboBox_S1_TIME, 0, 5)

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
        self.groupBox_5.setTitle("功率分析仪设置")
        self.groupBox_5.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g2Layout = QtWidgets.QGridLayout(self.groupBox_5)
        g2Layout.setSpacing(10)
        g2Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        g2Layout.addWidget(self.checkBox_S2, 0, 0)

        # WT 选择
        self.checkBox_S2_WT3000 = QtWidgets.QCheckBox("WT3000")
        self.checkBox_S2_WT3000.setChecked(True)
        self.checkBox_S2_WT3000.setObjectName("checkBox_S2_WT3000")
        g2Layout.addWidget(self.checkBox_S2_WT3000, 1, 0)

        self.pushButton_S2_WT_3000_CONFIG = QtWidgets.QPushButton("WT_3000_config")
        self.pushButton_S2_WT_3000_CONFIG.setObjectName("pushButton_S2_WT_3000_CONFIG")
        self.pushButton_S2_WT_3000_CONFIG.setFixedWidth(141)
        g2Layout.addWidget(self.pushButton_S2_WT_3000_CONFIG, 1, 1)

        self.checkBox_S2_WT1800 = QtWidgets.QCheckBox("WT1800")
        self.checkBox_S2_WT1800.setChecked(True)
        self.checkBox_S2_WT1800.setObjectName("checkBox_S2_WT1800")
        g2Layout.addWidget(self.checkBox_S2_WT1800, 1, 2)

        self.pushButton_S2_WT_1800_CONFIG = QtWidgets.QPushButton("WT_1800_config")
        self.pushButton_S2_WT_1800_CONFIG.setObjectName("pushButton_S2_WT_1800_CONFIG")
        self.pushButton_S2_WT_1800_CONFIG.setFixedWidth(141)
        g2Layout.addWidget(self.pushButton_S2_WT_1800_CONFIG, 1, 3)

        self.checkBox_S2_WT1806E = QtWidgets.QCheckBox("WT1806E")
        self.checkBox_S2_WT1806E.setChecked(True)
        self.checkBox_S2_WT1806E.setObjectName("checkBox_S2_WT1806E")
        g2Layout.addWidget(self.checkBox_S2_WT1806E, 1, 4)

        self.pushButton_S2_WT_1806E_CONFIG = QtWidgets.QPushButton("WT_1806E_config")
        self.pushButton_S2_WT_1806E_CONFIG.setObjectName("pushButton_S2_WT_1806E_CONFIG")
        self.pushButton_S2_WT_1806E_CONFIG.setFixedWidth(141)
        g2Layout.addWidget(self.pushButton_S2_WT_1806E_CONFIG, 1, 5)

        self.checkBox_S2_WT5000 = QtWidgets.QCheckBox("WT5000")
        self.checkBox_S2_WT5000.setChecked(True)
        self.checkBox_S2_WT5000.setObjectName("checkBox_S2_WT5000")
        g2Layout.addWidget(self.checkBox_S2_WT5000, 2, 0)

        self.pushButton_S2_WT_5000_CONFIG = QtWidgets.QPushButton("WT_5000_config")
        self.pushButton_S2_WT_5000_CONFIG.setObjectName("pushButton_S2_WT_5000_CONFIG")
        self.pushButton_S2_WT_5000_CONFIG.setFixedWidth(141)
        g2Layout.addWidget(self.pushButton_S2_WT_5000_CONFIG, 2, 1)

        # 更新率
        self.checkBox_RATE = QtWidgets.QCheckBox("更新率")
        self.checkBox_RATE.setChecked(True)
        self.checkBox_RATE.setObjectName("checkBox_RATE")
        g2Layout.addWidget(self.checkBox_RATE, 2, 2)

        self.textEdit_S2_RATE_TIME = QtWidgets.QTextEdit()
        self.textEdit_S2_RATE_TIME.setObjectName("textEdit_S2_RATE_TIME")
        self.textEdit_S2_RATE_TIME.setFixedSize(100, 31)
        g2Layout.addWidget(self.textEdit_S2_RATE_TIME, 2, 3)

        self.comboBox_S2_RATE_TIME = QtWidgets.QComboBox()
        self.comboBox_S2_RATE_TIME.setObjectName("comboBox_S2_RATE_TIME")
        self.comboBox_S2_RATE_TIME.addItems(["毫秒", "秒", "分钟"])
        self.comboBox_S2_RATE_TIME.setFixedWidth(120)
        g2Layout.addWidget(self.comboBox_S2_RATE_TIME, 2, 4)

        layout.addWidget(self.groupBox_5)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # 频率扫描步骤构建辅助方法
    # ══════════════════════════════════════════════
    def _build_freq_sweep_step(self, step_num, step_label, groupbox_name,
                               cb_name, rate_cb_name,
                               fr_start_name, fr_end_name, tilde_label_name,
                               time_cb_name, time_te_name,
                               freq_range_label_name, hz_label1_name,
                               tilde_display, hz_label2_name,
                               data_label_name, data_display):
        """构建一个频率扫描步骤页面"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        groupBox = QtWidgets.QGroupBox()
        groupBox.setObjectName(groupbox_name)
        groupBox.setTitle(f"频率扫描设置 - {step_label}")
        groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(groupBox)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        # Row 0: checkBox + 更新率
        cb = QtWidgets.QCheckBox(step_label)
        cb.setChecked(True)
        cb.setObjectName(cb_name)
        gLayout.addWidget(cb, 0, 0)
        setattr(self, cb_name, cb)

        rateCb = QtWidgets.QCheckBox("更新率")
        rateCb.setChecked(True)
        rateCb.setObjectName(rate_cb_name)
        gLayout.addWidget(rateCb, 0, 1)
        setattr(self, rate_cb_name, rateCb)

        # Row 1: 频率变动区间
        freqRangeLbl = QtWidgets.QLabel("频率变动区间")
        freqRangeLbl.setObjectName(freq_range_label_name)
        gLayout.addWidget(freqRangeLbl, 1, 0)

        frStartTe = QtWidgets.QTextEdit()
        frStartTe.setObjectName(fr_start_name)
        frStartTe.setFixedSize(100, 31)
        gLayout.addWidget(frStartTe, 1, 1)
        setattr(self, fr_start_name, frStartTe)

        hz1Lbl = QtWidgets.QLabel("Hz")
        hz1Lbl.setObjectName(hz_label1_name)
        gLayout.addWidget(hz1Lbl, 1, 2)

        tildeLbl = QtWidgets.QLabel(tilde_display)
        tildeLbl.setObjectName(tilde_label_name)
        gLayout.addWidget(tildeLbl, 1, 3)

        frEndTe = QtWidgets.QTextEdit()
        frEndTe.setObjectName(fr_end_name)
        frEndTe.setFixedSize(100, 31)
        gLayout.addWidget(frEndTe, 1, 4)
        setattr(self, fr_end_name, frEndTe)

        hz2Lbl = QtWidgets.QLabel("Hz")
        hz2Lbl.setObjectName(hz_label2_name)
        gLayout.addWidget(hz2Lbl, 1, 5)

        # Row 2: 数据采集时间
        dataLbl = QtWidgets.QLabel("数据采集")
        dataLbl.setObjectName(data_label_name)
        gLayout.addWidget(dataLbl, 2, 0)

        timeTe = QtWidgets.QTextEdit()
        timeTe.setObjectName(time_te_name)
        timeTe.setFixedSize(100, 31)
        gLayout.addWidget(timeTe, 2, 1)
        setattr(self, time_te_name, timeTe)

        timeCombo = QtWidgets.QComboBox()
        timeCombo.setObjectName(time_cb_name)
        timeCombo.addItems(["秒", "毫秒", "分钟"])
        timeCombo.setFixedWidth(120)
        gLayout.addWidget(timeCombo, 2, 2)
        setattr(self, time_cb_name, timeCombo)

        layout.addWidget(groupBox)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 3: 频率扫描1
    # ══════════════════════════════════════════════
    def _build_step3(self):
        self._build_freq_sweep_step(
            step_num=3, step_label="step3", groupbox_name="groupBox_3",
            cb_name="checkBox_S3", rate_cb_name="checkBox_S3_RATE",
            fr_start_name="textEdit_S3_AC_FR_Start", fr_end_name="textEdit_S3_AC_FR_End",
            tilde_label_name="label_7",
            time_cb_name="comboBox_S3_TIME", time_te_name="textEdit_S3_TIME",
            freq_range_label_name="label_37", hz_label1_name="label_34",
            tilde_display="~", hz_label2_name="label_78",
            data_label_name="label_23", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 4: 频率扫描2
    # ══════════════════════════════════════════════
    def _build_step4(self):
        self._build_freq_sweep_step(
            step_num=4, step_label="step4", groupbox_name="groupBox_6",
            cb_name="checkBox_S4", rate_cb_name="checkBox_S4_RATE",
            fr_start_name="textEdit_S4_AC_FR_Start", fr_end_name="textEdit_S4_AC_FR_End",
            tilde_label_name="label_20",
            time_cb_name="comboBox_S4_TIME", time_te_name="textEdit_S4_TIME",
            freq_range_label_name="label_38", hz_label1_name="label_35",
            tilde_display="~", hz_label2_name="label_94",
            data_label_name="label_26", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 5: 频率扫描3
    # ══════════════════════════════════════════════
    def _build_step5(self):
        self._build_freq_sweep_step(
            step_num=5, step_label="step5", groupbox_name="groupBox_7",
            cb_name="checkBox_S5", rate_cb_name="checkBox_S5_RATE",
            fr_start_name="textEdit_S5_AC_FR_Start", fr_end_name="textEdit_S5_AC_FR_End",
            tilde_label_name="label_31",
            time_cb_name="comboBox_S5_TIME", time_te_name="textEdit_S5_TIME",
            freq_range_label_name="label_39", hz_label1_name="label_36",
            tilde_display="~", hz_label2_name="label_98",
            data_label_name="label_29", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 6: 频率扫描4
    # ══════════════════════════════════════════════
    def _build_step6(self):
        self._build_freq_sweep_step(
            step_num=6, step_label="step6", groupbox_name="groupBox_13",
            cb_name="checkBox_S6", rate_cb_name="checkBox_S6_RATE",
            fr_start_name="textEdit_S6_AC_FR_Start", fr_end_name="textEdit_S6_AC_FR_End",
            tilde_label_name="label_10",
            time_cb_name="comboBox_S6_TIME", time_te_name="textEdit_S6_TIME",
            freq_range_label_name="label_73", hz_label1_name="label_72",
            tilde_display="~", hz_label2_name="label_82",
            data_label_name="label_75", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 7: 频率扫描5
    # ══════════════════════════════════════════════
    def _build_step7(self):
        self._build_freq_sweep_step(
            step_num=7, step_label="step7", groupbox_name="groupBox_14",
            cb_name="checkBox_S7", rate_cb_name="checkBox_S7_RATE",
            fr_start_name="textEdit_S7_AC_FR_Start", fr_end_name="textEdit_S7_AC_FR_End",
            tilde_label_name="label_12",
            time_cb_name="comboBox_S7_TIME", time_te_name="textEdit_S7_TIME",
            freq_range_label_name="label_86", hz_label1_name="label_85",
            tilde_display="~", hz_label2_name="label_90",
            data_label_name="label_88", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 8: 频率扫描6
    # ══════════════════════════════════════════════
    def _build_step8(self):
        self._build_freq_sweep_step(
            step_num=8, step_label="step8", groupbox_name="groupBox_15",
            cb_name="checkBox_S8", rate_cb_name="checkBox_S8_RATE",
            fr_start_name="textEdit_S8_AC_FR_Start", fr_end_name="textEdit_S8_AC_FR_End",
            tilde_label_name="label_33",
            time_cb_name="comboBox_S8_TIME", time_te_name="textEdit_S8_TIME",
            freq_range_label_name="label_136", hz_label1_name="label_135",
            tilde_display="~", hz_label2_name="label_140",
            data_label_name="label_138", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 9: 频率扫描7
    # ══════════════════════════════════════════════
    def _build_step9(self):
        self._build_freq_sweep_step(
            step_num=9, step_label="step9", groupbox_name="groupBox_17",
            cb_name="checkBox_S9", rate_cb_name="checkBox_S9_RATE",
            fr_start_name="textEdit_S9_AC_FR_Start", fr_end_name="textEdit_S9_AC_FR_End",
            tilde_label_name="label_11",
            time_cb_name="comboBox_S9_TIME", time_te_name="textEdit_S9_TIME",
            freq_range_label_name="label_76", hz_label1_name="label_74",
            tilde_display="~", hz_label2_name="label_87",
            data_label_name="label_77", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 10: 频率扫描8
    # ══════════════════════════════════════════════
    def _build_step10(self):
        self._build_freq_sweep_step(
            step_num=10, step_label="step10", groupbox_name="groupBox_18",
            cb_name="checkBox_S10", rate_cb_name="checkBox_S10_RATE",
            fr_start_name="textEdit_S10_AC_FR_Start", fr_end_name="textEdit_S10_AC_FR_End",
            tilde_label_name="label_16",
            time_cb_name="comboBox_S10_TIME", time_te_name="textEdit_S10_TIME",
            freq_range_label_name="label_134", hz_label1_name="label_97",
            tilde_display="~", hz_label2_name="label_148",
            data_label_name="label_147", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 11: 频率扫描9
    # ══════════════════════════════════════════════
    def _build_step11(self):
        self._build_freq_sweep_step(
            step_num=11, step_label="step11", groupbox_name="groupBox_16",
            cb_name="checkBox_S11", rate_cb_name="checkBox_S11_RATE",
            fr_start_name="textEdit_S11_AC_FR_Start", fr_end_name="textEdit_S11_AC_FR_End",
            tilde_label_name="label_40",
            time_cb_name="comboBox_S11_TIME", time_te_name="textEdit_S11_TIME",
            freq_range_label_name="label_139", hz_label1_name="label_137",
            tilde_display="~", hz_label2_name="label_144",
            data_label_name="label_143", data_display="数据采集"
        )

    # ══════════════════════════════════════════════
    # Step 12: 关机设置
    # ══════════════════════════════════════════════
    def _build_step12(self):
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
        self.comboBox_S_End_AC.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_AC, 0, 2)

        # Row 1: DC1 + DC2
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

        # Row 2: DC3 + DC4
        self.checkBox_S_End_DC3 = QtWidgets.QCheckBox("直流电源3")
        self.checkBox_S_End_DC3.setChecked(True)
        self.checkBox_S_End_DC3.setObjectName("checkBox_S_End_DC3")
        g11Layout.addWidget(self.checkBox_S_End_DC3, 2, 0)

        self.comboBox_S_End_DC3 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC3.setObjectName("comboBox_S_End_DC3")
        self.comboBox_S_End_DC3.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC3.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC3, 2, 1)

        self.checkBox_S_End_DC4 = QtWidgets.QCheckBox("直流电源4")
        self.checkBox_S_End_DC4.setChecked(True)
        self.checkBox_S_End_DC4.setObjectName("checkBox_S_End_DC4")
        g11Layout.addWidget(self.checkBox_S_End_DC4, 2, 2)

        self.comboBox_S_End_DC4 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC4.setObjectName("comboBox_S_End_DC4")
        self.comboBox_S_End_DC4.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC4.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC4, 2, 3)

        layout.addWidget(self.groupBox_11)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    def retranslateUi(self, Dialog_thaiguoqianpin_immun):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaiguoqianpin_immun.setWindowTitle(_translate("Dialog_thaiguoqianpin_immun", "过欠频稳定性项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaiguoqianpin_immun", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaiguoqianpin_immun", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaiguoqianpin_immun", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaiguoqianpin_immun", "提交"))
