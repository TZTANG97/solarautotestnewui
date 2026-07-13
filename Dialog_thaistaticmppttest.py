# -*- coding: utf-8 -*-
# 静态MPPT项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_thaistaticmppttest(object):
    def setupUi(self, Dialog_thaistaticmppttest):
        Dialog_thaistaticmppttest.setObjectName("Dialog_thaistaticmppttest")
        Dialog_thaistaticmppttest.resize(1300, 850)
        Dialog_thaistaticmppttest.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaistaticmppttest.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaistaticmppttest)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ MPPT测试", "④ 关机设置"]
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

        # ── DC 联动（step1 → 关机步骤） ──
        self._connect_dc_linkage()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaistaticmppttest)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaistaticmppttest)

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
    # Step 1: AC/DC电源设置 + 直流源 + 时序
    # ══════════════════════════════════════════════
    def _build_step1(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        pageLayout = QtWidgets.QVBoxLayout(page)
        pageLayout.setContentsMargins(16, 16, 16, 16)
        pageLayout.setSpacing(12)

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

        self.label_3 = QtWidgets.QLabel("交流电源")
        self.label_3.setObjectName("label_3")
        gLayout.addWidget(self.label_3, 0, 2)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(100)
        gLayout.addWidget(self.comboBox_S1_AC, 0, 3)

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        gLayout.addWidget(self.label_4, 0, 4)

        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(80, 31)
        self.textEdit_S1_AC_VOLT.setText("230")
        gLayout.addWidget(self.textEdit_S1_AC_VOLT, 0, 5)

        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        gLayout.addWidget(self.label_5, 0, 6)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        gLayout.addWidget(self.label_113, 0, 7)

        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(80, 31)
        self.textEdit_S1_AC_VOLT_2.setText("230")
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 8)

        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        gLayout.addWidget(self.label_107, 0, 9)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        gLayout.addWidget(self.label_123, 1, 4)

        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(80, 31)
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
        self.textEdit_S1_AC_FR.setFixedSize(80, 31)
        self.textEdit_S1_AC_FR.setText("50")
        gLayout.addWidget(self.textEdit_S1_AC_FR, 1, 8)

        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        gLayout.addWidget(self.label_18, 1, 9)

        # 相位选择（单相/三相）放在第二行左侧
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(100)
        gLayout.addWidget(self.comboBox_S1_AC_2, 1, 3)

        # 直流源电压段数 + 直流源开关
        self.label_49 = QtWidgets.QLabel("直流源测试电压段")
        self.label_49.setObjectName("label_49")
        gLayout.addWidget(self.label_49, 2, 0)

        self.comboBox_S1_Vdc_Count = QtWidgets.QComboBox()
        self.comboBox_S1_Vdc_Count.setObjectName("comboBox_S1_Vdc_Count")
        self.comboBox_S1_Vdc_Count.addItems(["3", "1", "2", "4", "5", "6"])
        self.comboBox_S1_Vdc_Count.setFixedWidth(80)
        gLayout.addWidget(self.comboBox_S1_Vdc_Count, 2, 1)

        self.label_6 = QtWidgets.QLabel("直流源")
        self.label_6.setObjectName("label_6")
        gLayout.addWidget(self.label_6, 2, 2)

        self.comboBox_S1_DC_START = QtWidgets.QComboBox()
        self.comboBox_S1_DC_START.setObjectName("comboBox_S1_DC_START")
        self.comboBox_S1_DC_START.addItems(["开启", "关闭"])
        self.comboBox_S1_DC_START.setFixedWidth(80)
        gLayout.addWidget(self.comboBox_S1_DC_START, 2, 3)

        # 等待时间 / 启机时间
        self.label_131 = QtWidgets.QLabel("等待时间:")
        self.label_131.setObjectName("label_131")
        gLayout.addWidget(self.label_131, 2, 4)

        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(80, 31)
        self.textEdit_S1_ACWaitTIME.setText("3")
        gLayout.addWidget(self.textEdit_S1_ACWaitTIME, 2, 5)

        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(80)
        gLayout.addWidget(self.comboBox_S1_ACWaitTIME, 2, 6)

        self.label_132 = QtWidgets.QLabel("启机时间:")
        self.label_132.setObjectName("label_132")
        gLayout.addWidget(self.label_132, 2, 7)

        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(80, 31)
        self.textEdit_S1_TIME.setText("5")
        gLayout.addWidget(self.textEdit_S1_TIME, 2, 8)

        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(80)
        gLayout.addWidget(self.comboBox_S1_TIME, 2, 9)

        pageLayout.addWidget(self.groupBox)

        # ── 直流电源面板（DC1 ~ DC4，2x2 网格） ──
        dcGrid = QtWidgets.QGridLayout()
        dcGrid.setSpacing(10)

        dc_panels = [
            (0, 0, "groupBox_7", "直流电源1", "DC1", "label_29", "直流源1接口", "label_36", "直流源1配置文档"),
            (0, 1, "groupBox_8", "直流电源2", "DC2", "label_38", "直流源2接口", "label_37", "直流源2配置文档"),
            (1, 0, "groupBox_10", "直流电源3", "DC3", "label_42", "直流源3接口", "label_41", "直流源3配置文档"),
            (1, 1, "groupBox_9", "直流电源4", "DC4", "label_40", "直流源4接口", "label_39", "直流源4配置文档"),
        ]

        for row, col, grpName, grpTitle, dcPrefix, portLabelName, portLabelText, docLabelName, docLabelText in dc_panels:
            grp = QtWidgets.QGroupBox()
            grp.setObjectName(grpName)
            grp.setTitle(grpTitle)
            grp.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
            grpGrid = QtWidgets.QGridLayout(grp)
            grpGrid.setSpacing(6)
            grpGrid.setContentsMargins(10, 18, 10, 10)

            # 行0: 开关 checkbox + 接口
            cbName = f"checkBox_S1_{dcPrefix}"
            cb = QtWidgets.QCheckBox(grpTitle)
            cb.setChecked(True)
            cb.setObjectName(cbName)
            grpGrid.addWidget(cb, 0, 0)
            setattr(self, cbName, cb)

            portLbl = QtWidgets.QLabel(portLabelText)
            portLbl.setObjectName(portLabelName)
            grpGrid.addWidget(portLbl, 0, 1)

            portComboName = f"comboBox_S1_{dcPrefix}_PORT"
            portCombo = QtWidgets.QComboBox()
            portCombo.setObjectName(portComboName)
            portCombo.setFixedWidth(100)
            grpGrid.addWidget(portCombo, 0, 2)
            setattr(self, portComboName, portCombo)

            # 行1: 配置文档标签
            docLbl = QtWidgets.QLabel(docLabelText)
            docLbl.setObjectName(docLabelName)
            grpGrid.addWidget(docLbl, 1, 0, 1, 3)

            # 行2+: 电压段 (Vmin/Vnom/Vmax 左列, Vdc1/Vdc2/Vdc3 右列)
            voltages_left = [
                (f"checkBox_S1_{dcPrefix}_Vmin", "Vmin", True, f"textEdit_S1_{dcPrefix}_Vmin"),
                (f"checkBox_S1_{dcPrefix}_Vnom", "Vnom", True, f"textEdit_S1_{dcPrefix}_Vnom"),
                (f"checkBox_S1_{dcPrefix}_Vmax", "Vmax", True, f"textEdit_S1_{dcPrefix}_Vmax"),
            ]
            voltages_right = [
                (f"checkBox_S1_{dcPrefix}_Vdc1", "Vdc1", False, f"textEdit_S1_{dcPrefix}_Vdc1"),
                (f"checkBox_S1_{dcPrefix}_Vdc2", "Vdc2", False, f"textEdit_S1_{dcPrefix}_Vdc2"),
                (f"checkBox_S1_{dcPrefix}_Vdc3", "Vdc3", False, f"textEdit_S1_{dcPrefix}_Vdc3"),
            ]

            for i, (cbName, cbText, checked, teName) in enumerate(voltages_left):
                r = 2 + i
                vc = QtWidgets.QCheckBox(cbText)
                vc.setChecked(checked)
                vc.setObjectName(cbName)
                grpGrid.addWidget(vc, r, 0)
                setattr(self, cbName, vc)
                te = QtWidgets.QTextEdit()
                te.setObjectName(teName)
                te.setFixedSize(80, 28)
                grpGrid.addWidget(te, r, 1)
                setattr(self, teName, te)

            for i, (cbName, cbText, checked, teName) in enumerate(voltages_right):
                r = 2 + i
                vc = QtWidgets.QCheckBox(cbText)
                vc.setChecked(checked)
                vc.setObjectName(cbName)
                grpGrid.addWidget(vc, r, 2)
                setattr(self, cbName, vc)
                te = QtWidgets.QTextEdit()
                te.setObjectName(teName)
                te.setFixedSize(80, 28)
                grpGrid.addWidget(te, r, 3)
                setattr(self, teName, te)

            dcGrid.addWidget(grp, row, col)

        pageLayout.addLayout(dcGrid)
        pageLayout.addStretch()

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 2: 测试功率段
    # ══════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── 测试保存路径 ──
        self.groupBox_5 = QtWidgets.QGroupBox()
        self.groupBox_5.setObjectName("groupBox_5")
        self.groupBox_5.setTitle("测试功率段设置")
        self.groupBox_5.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g5Layout = QtWidgets.QGridLayout(self.groupBox_5)
        g5Layout.setSpacing(8)
        g5Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        g5Layout.addWidget(self.checkBox_S2, 0, 0)

        # 保存路径
        self.label_25 = QtWidgets.QLabel("测试保存路径")
        self.label_25.setObjectName("label_25")
        self.label_25.setStyleSheet("font-weight: bold; color: #475569;")
        g5Layout.addWidget(self.label_25, 1, 0, 1, 2)

        path_rows = [
            (2, "label_31", "Vmin", "textEdit_S2_Vmin_PATH"),
            (3, "label_34", "Vnom", "textEdit_S2_Vnom_PATH"),
            (4, "label_35", "Vmax", "textEdit_S2_Vmax_PATH"),
        ]
        path_rows_right = [
            (2, "label_44", "Vdc1", "textEdit_S2_Vdc1_PATH"),
            (3, "label_45", "Vdc2", "textEdit_S2_Vdc2_PATH"),
            (4, "label_43", "Vdc3", "textEdit_S2_Vdc3_PATH"),
        ]

        for r, lblName, lblText, teName in path_rows:
            lbl = QtWidgets.QLabel(lblText)
            lbl.setObjectName(lblName)
            g5Layout.addWidget(lbl, r, 0)
            te = QtWidgets.QTextEdit()
            te.setObjectName(teName)
            te.setFixedSize(120, 31)
            g5Layout.addWidget(te, r, 1)
            setattr(self, lblName, lbl)
            setattr(self, teName, te)

        for r, lblName, lblText, teName in path_rows_right:
            lbl = QtWidgets.QLabel(lblText)
            lbl.setObjectName(lblName)
            g5Layout.addWidget(lbl, r, 2)
            te = QtWidgets.QTextEdit()
            te.setObjectName(teName)
            te.setFixedSize(120, 31)
            g5Layout.addWidget(te, r, 3)
            setattr(self, lblName, lbl)
            setattr(self, teName, te)

        # 测试功率段
        self.label_24 = QtWidgets.QLabel("测试功率段")
        self.label_24.setObjectName("label_24")
        self.label_24.setStyleSheet("font-weight: bold; color: #475569;")
        g5Layout.addWidget(self.label_24, 5, 0, 1, 2)

        pn_checks = [
            (6, "checkBox_S2_Pn_100", "100%", True),
            (6, "checkBox_S2_Pn_75", "75%", True),
            (6, "checkBox_S2_Pn_50", "50%", True),
            (6, "checkBox_S2_Pn_30", "30%", True),
            (7, "checkBox_S2_Pn_25", "25%", True),
            (7, "checkBox_S2_Pn_20", "20%", True),
            (7, "checkBox_S2_Pn_10", "10%", True),
            (7, "checkBox_S2_Pn_5", "5%", True),
        ]
        for r, cbName, cbText, checked in pn_checks:
            cb = QtWidgets.QCheckBox(cbText)
            cb.setChecked(checked)
            cb.setObjectName(cbName)
            g5Layout.addWidget(cb, r, 0)
            setattr(self, cbName, cb)

        layout.addWidget(self.groupBox_5)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 3: MPPT测试时长
    # ══════════════════════════════════════════════
    def _build_step3(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_6 = QtWidgets.QGroupBox()
        self.groupBox_6.setObjectName("groupBox_6")
        self.groupBox_6.setTitle("MPPT测试时长设置")
        self.groupBox_6.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g6Layout = QtWidgets.QGridLayout(self.groupBox_6)
        g6Layout.setSpacing(10)
        g6Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setChecked(True)
        self.checkBox_S3.setObjectName("checkBox_S3")
        g6Layout.addWidget(self.checkBox_S3, 0, 0)

        # MPPT测试总时长
        self.label_26 = QtWidgets.QLabel("MPPT测试总时长")
        self.label_26.setObjectName("label_26")
        g6Layout.addWidget(self.label_26, 0, 1)

        self.textEdit_S3_TOTAL_H = QtWidgets.QTextEdit()
        self.textEdit_S3_TOTAL_H.setObjectName("textEdit_S3_TOTAL_H")
        self.textEdit_S3_TOTAL_H.setFixedSize(80, 31)
        self.textEdit_S3_TOTAL_H.setText("9")
        g6Layout.addWidget(self.textEdit_S3_TOTAL_H, 0, 2)

        self.label_27 = QtWidgets.QLabel("H")
        self.label_27.setObjectName("label_27")
        g6Layout.addWidget(self.label_27, 0, 3)

        self.textEdit_S3_TOTAL_M = QtWidgets.QTextEdit()
        self.textEdit_S3_TOTAL_M.setObjectName("textEdit_S3_TOTAL_M")
        self.textEdit_S3_TOTAL_M.setFixedSize(80, 31)
        self.textEdit_S3_TOTAL_M.setText("0")
        g6Layout.addWidget(self.textEdit_S3_TOTAL_M, 0, 4)

        self.label_32 = QtWidgets.QLabel("M")
        self.label_32.setObjectName("label_32")
        g6Layout.addWidget(self.label_32, 0, 5)

        # 单次测试时长
        self.label_28 = QtWidgets.QLabel("单次测试时长")
        self.label_28.setObjectName("label_28")
        g6Layout.addWidget(self.label_28, 1, 1)

        self.textEdit_S3_PER_H = QtWidgets.QTextEdit()
        self.textEdit_S3_PER_H.setObjectName("textEdit_S3_PER_H")
        self.textEdit_S3_PER_H.setFixedSize(80, 31)
        self.textEdit_S3_PER_H.setText("0")
        g6Layout.addWidget(self.textEdit_S3_PER_H, 1, 2)

        self.label_30 = QtWidgets.QLabel("H")
        self.label_30.setObjectName("label_30")
        g6Layout.addWidget(self.label_30, 1, 3)

        self.textEdit_S3_PER_M = QtWidgets.QTextEdit()
        self.textEdit_S3_PER_M.setObjectName("textEdit_S3_PER_M")
        self.textEdit_S3_PER_M.setFixedSize(80, 31)
        self.textEdit_S3_PER_M.setText("15")
        g6Layout.addWidget(self.textEdit_S3_PER_M, 1, 4)

        self.label_33 = QtWidgets.QLabel("M")
        self.label_33.setObjectName("label_33")
        g6Layout.addWidget(self.label_33, 1, 5)

        layout.addWidget(self.groupBox_6)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 4: 关机设置
    # ══════════════════════════════════════════════
    def _build_step4(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_11 = QtWidgets.QGroupBox()
        self.groupBox_11.setObjectName("groupBox_11")
        self.groupBox_11.setTitle("关机设置")
        self.groupBox_11.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(self.groupBox_11)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S_End = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_End.setChecked(True)
        self.checkBox_S_End.setObjectName("checkBox_S_End")
        gLayout.addWidget(self.checkBox_S_End, 0, 0)

        self.label_8 = QtWidgets.QLabel("交流电源")
        self.label_8.setObjectName("label_8")
        gLayout.addWidget(self.label_8, 0, 1)

        self.comboBox_S_End_AC = QtWidgets.QComboBox()
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItems(["关闭", "开启"])
        self.comboBox_S_End_AC.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S_End_AC, 0, 2)

        self.checkBox_S_End_DC = QtWidgets.QCheckBox("直流电源")
        self.checkBox_S_End_DC.setChecked(True)
        self.checkBox_S_End_DC.setObjectName("checkBox_S_End_DC")
        gLayout.addWidget(self.checkBox_S_End_DC, 0, 3)

        self.comboBox_S_End_DC = QtWidgets.QComboBox()
        self.comboBox_S_End_DC.setObjectName("comboBox_S_End_DC")
        self.comboBox_S_End_DC.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S_End_DC, 0, 4)

        layout.addWidget(self.groupBox_11)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _connect_dc_linkage(self):
        """连接 step1 DC 复选框与关机步骤 DC 复选框的联动。"""
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        def _update_end_dc(_checked=None):
            step_end_on = self.checkBox_S_End.isChecked()
            any_dc_on = any(dc.isChecked() for dc in step1_dcs)
            should_enable = step_end_on and any_dc_on
            self.checkBox_S_End_DC.setEnabled(should_enable)
            self.checkBox_S_End_DC.setChecked(should_enable)

        self.checkBox_S_End.toggled.connect(_update_end_dc)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_end_dc)
        _update_end_dc()  # 初始化状态

    def retranslateUi(self, Dialog_thaistaticmppttest):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaistaticmppttest.setWindowTitle(_translate("Dialog_thaistaticmppttest", "静态MPPT项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaistaticmppttest", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaistaticmppttest", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaistaticmppttest", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaistaticmppttest", "提交"))
