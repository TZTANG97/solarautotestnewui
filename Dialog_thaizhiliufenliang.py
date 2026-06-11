# -*- coding: utf-8 -*-
# 直流分量项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_thaizhiliufenliang(object):
    def setupUi(self, Dialog_thaizhiliufenliang):
        Dialog_thaizhiliufenliang.setObjectName("Dialog_thaizhiliufenliang")
        Dialog_thaizhiliufenliang.resize(1300, 850)
        Dialog_thaizhiliufenliang.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaizhiliufenliang.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaizhiliufenliang)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ 直流分量1", "④ 直流分量2", "⑤ 直流分量3", "⑥ 判定结果", "⑦ 关机设置"]
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
        self._build_step6()
        self._build_step7()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaizhiliufenliang)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaizhiliufenliang)

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
        self.label_3.setStyleSheet("font-weight: bold; color: #475569; background: transparent;")
        g6Layout.addWidget(self.label_3, 0, 2)

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        g6Layout.addWidget(self.label_4, 0, 3)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(120)
        g6Layout.addWidget(self.comboBox_S1_AC, 0, 4)

        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(80, 31)
        self.textEdit_S1_AC_VOLT.setText("220")
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT, 0, 5)

        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        g6Layout.addWidget(self.label_5, 0, 6)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        g6Layout.addWidget(self.label_113, 0, 7)

        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(80, 31)
        self.textEdit_S1_AC_VOLT_2.setText("220")
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 8)

        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        g6Layout.addWidget(self.label_107, 0, 9)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        g6Layout.addWidget(self.label_123, 0, 10)

        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(80, 31)
        self.textEdit_S1_AC_VOLT_3.setText("220")
        g6Layout.addWidget(self.textEdit_S1_AC_VOLT_3, 0, 11)

        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        g6Layout.addWidget(self.label_102, 0, 12)

        # Row 1
        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        g6Layout.addWidget(self.label_19, 1, 2)

        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        g6Layout.addWidget(self.comboBox_S1_AC_2, 1, 4)

        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        g6Layout.addWidget(self.label_18, 1, 6)

        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(80, 31)
        self.textEdit_S1_AC_FR.setText("50")
        g6Layout.addWidget(self.textEdit_S1_AC_FR, 1, 8)

        layout.addWidget(self.groupBox_6)

        # ── DC 电源组 (4 channels) ──
        # Grid layout: Col 0=checkbox, 1=combo, 2=Vmp_name, 3=Vmp_edit, 4=V_unit,
        #   5=Imp_name, 6=Imp_edit, 7=A_unit, 8=Voc_name, 9=Voc_edit, 10=V_unit,
        #   11=Isc_name, 12=Isc_edit, 13=A_unit, 14=PF_name, 15=PF_edit, 16=%_unit
        self.groupBox_7 = QtWidgets.QGroupBox()
        self.groupBox_7.setObjectName("groupBox_7")
        self.groupBox_7.setTitle("直流电源设置")
        self.groupBox_7.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g7Layout = QtWidgets.QGridLayout(self.groupBox_7)
        g7Layout.setSpacing(6)
        g7Layout.setContentsMargins(12, 20, 12, 12)

        # Header row
        hdr = ["通道", "开关", "Vmp", "", "V", "Imp", "", "A", "Voc", "", "V", "Isc", "", "A", "功率", "", "%"]
        for c, h in enumerate(hdr):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569; background: transparent; font-size: 11px;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g7Layout.addWidget(lbl, 0, c)

        # ── DC channel data ──
        # Each tuple: (cb_name, cb_text, combo_name, te_names[5],
        #   vmp_lbl, vmp_unit, imp_lbl, imp_unit, voc_lbl, voc_unit, isc_lbl, isc_unit, pf_lbl, pf_unit)
        dc_channels = [
            {
                "cb": ("checkBox_S1_DC1", "直流电源1"),
                "combo": ("comboBox_S1_DC1", ["开启", "关闭"]),
                "tes": ["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc",
                        "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"],
                "vmp": ("label_13", "Vmp"),  "vmp_u": ("label_109", "V"),
                "imp": ("label_120", "Imp"), "imp_u": ("label_118", "A"),
                "voc": ("label_108", "Voc"), "voc_u": ("label_111", "V"),
                "isc": ("label_59", "Isc"),  "isc_u": ("label_128", "A"),
                "pf":  ("label_104", "功率"), "pf_u": ("label_57", "%"),
            },
            {
                "cb": ("checkBox_S1_DC2", "直流电源2"),
                "combo": ("comboBox_S1_DC2", ["开启", "关闭"]),
                "tes": ["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc",
                        "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"],
                "vmp": ("label_14", "Vmp"),  "vmp_u": ("label_119", "V"),
                "imp": ("label_125", "Imp"), "imp_u": ("label_54", "A"),
                "voc": ("label_110", "Voc"), "voc_u": ("label_64", "V"),
                "isc": ("label_106", "Isc"), "isc_u": ("label_124", "A"),
                "pf":  ("label_129", "功率"), "pf_u": ("label_112", "%"),
            },
            {
                "cb": ("checkBox_S1_DC3", "直流电源3"),
                "combo": ("comboBox_S1_DC3", ["开启", "关闭"]),
                "tes": ["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc",
                        "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"],
                "vmp": ("label_17", "Vmp"),  "vmp_u": ("label_15", "V"),
                "imp": ("label_63", "Imp"),  "imp_u": ("label_58", "A"),
                "voc": ("label_122", "Voc"), "voc_u": ("label_127", "V"),
                "isc": ("label_101", "Isc"), "isc_u": ("label_114", "A"),
                "pf":  ("label_116", "功率"), "pf_u": ("label_117", "%"),
            },
            {
                "cb": ("checkBox_S1_DC4", "直流电源4"),
                "combo": ("comboBox_S1_DC4", ["开启", "关闭"]),
                "tes": ["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc",
                        "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"],
                "vmp": ("label_65", "Vmp"),  "vmp_u": ("label_37", "V"),
                "imp": ("label_66", "Imp"),  "imp_u": ("label_67", "A"),
                "voc": ("label_130", "Voc"), "voc_u": ("label_35", "V"),
                "isc": ("label_105", "Isc"), "isc_u": ("label_103", "A"),
                "pf":  ("label_100", "功率"), "pf_u": ("label_115", "%"),
            },
        ]

        for r, ch in enumerate(dc_channels, start=1):
            # Checkbox
            cb_name, cb_text = ch["cb"]
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g7Layout.addWidget(cb, r, 0)
            setattr(self, cb_name, cb)

            # ComboBox
            combo_name, combo_items = ch["combo"]
            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(combo_items)
            combo.setFixedWidth(90)
            g7Layout.addWidget(combo, r, 1)
            setattr(self, combo_name, combo)

            # 5 parameters: Vmp, Imp, Voc, Isc, PF
            params = [
                (2, 3, 4, "vmp", "tes", 0),   # Vmp
                (5, 6, 7, "imp", None, 1),     # Imp
                (8, 9, 10, "voc", None, 2),    # Voc
                (11, 12, 13, "isc", None, 3),  # Isc
                (14, 15, 16, "pf", None, 4),   # PF
            ]
            for name_col, edit_col, unit_col, key, tes_key, te_idx in params:
                # Name label
                lbl_name, lbl_text = ch[key]
                lbl = QtWidgets.QLabel(lbl_text)
                lbl.setObjectName(lbl_name)
                lbl.setStyleSheet("font-size: 11px; color: #475569; background: transparent;")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                g7Layout.addWidget(lbl, r, name_col)
                setattr(self, lbl_name, lbl)

                # Text edit
                te_name = ch["tes"][te_idx]
                te = QtWidgets.QTextEdit()
                te.setObjectName(te_name)
                te.setFixedSize(70, 28)
                g7Layout.addWidget(te, r, edit_col)
                setattr(self, te_name, te)

                # Unit label
                unit_key = key + "_u"
                u_name, u_text = ch[unit_key]
                ulbl = QtWidgets.QLabel(u_text)
                ulbl.setObjectName(u_name)
                ulbl.setStyleSheet("font-size: 11px; color: #64748b; background: transparent;")
                ulbl.setAlignment(QtCore.Qt.AlignCenter)
                g7Layout.addWidget(ulbl, r, unit_col)
                setattr(self, u_name, ulbl)

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
        self.textEdit_S1_ACWaitTIME.setText("3")
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
    # Step 2: 功率分析仪设置
    # ══════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_3 = QtWidgets.QGroupBox()
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setTitle("功率分析仪设置")
        self.groupBox_3.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g3Layout = QtWidgets.QGridLayout(self.groupBox_3)
        g3Layout.setSpacing(10)
        g3Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        g3Layout.addWidget(self.checkBox_S2, 0, 0, 1, 2)

        # WT3000
        self.checkBox_S2_WT3000 = QtWidgets.QCheckBox("WT3000")
        self.checkBox_S2_WT3000.setChecked(True)
        self.checkBox_S2_WT3000.setObjectName("checkBox_S2_WT3000")
        g3Layout.addWidget(self.checkBox_S2_WT3000, 1, 0)

        self.pushButton_S2_WT_3000_CONFIG = QtWidgets.QPushButton("WT_3000_config")
        self.pushButton_S2_WT_3000_CONFIG.setObjectName("pushButton_S2_WT_3000_CONFIG")
        self.pushButton_S2_WT_3000_CONFIG.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        g3Layout.addWidget(self.pushButton_S2_WT_3000_CONFIG, 1, 1)

        # WT1800
        self.checkBox_S2_WT1800 = QtWidgets.QCheckBox("WT1800")
        self.checkBox_S2_WT1800.setChecked(True)
        self.checkBox_S2_WT1800.setObjectName("checkBox_S2_WT1800")
        g3Layout.addWidget(self.checkBox_S2_WT1800, 1, 2)

        self.pushButton_S2_WT_1800_CONFIG = QtWidgets.QPushButton("WT_1800_config")
        self.pushButton_S2_WT_1800_CONFIG.setObjectName("pushButton_S2_WT_1800_CONFIG")
        self.pushButton_S2_WT_1800_CONFIG.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        g3Layout.addWidget(self.pushButton_S2_WT_1800_CONFIG, 1, 3)

        # WT1806E
        self.checkBox_S2_WT1806E = QtWidgets.QCheckBox("WT1806E")
        self.checkBox_S2_WT1806E.setChecked(True)
        self.checkBox_S2_WT1806E.setObjectName("checkBox_S2_WT1806E")
        g3Layout.addWidget(self.checkBox_S2_WT1806E, 1, 4)

        self.pushButton_S2_WT_1806E_CONFIG = QtWidgets.QPushButton("WT_1806E_config")
        self.pushButton_S2_WT_1806E_CONFIG.setObjectName("pushButton_S2_WT_1806E_CONFIG")
        self.pushButton_S2_WT_1806E_CONFIG.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        g3Layout.addWidget(self.pushButton_S2_WT_1806E_CONFIG, 1, 5)

        # WT5000
        self.checkBox_S2_WT5000 = QtWidgets.QCheckBox("WT5000")
        self.checkBox_S2_WT5000.setChecked(True)
        self.checkBox_S2_WT5000.setObjectName("checkBox_S2_WT5000")
        g3Layout.addWidget(self.checkBox_S2_WT5000, 1, 6)

        self.pushButton_S2_WT_5000_CONFIG = QtWidgets.QPushButton("WT_5000_config")
        self.pushButton_S2_WT_5000_CONFIG.setObjectName("pushButton_S2_WT_5000_CONFIG")
        self.pushButton_S2_WT_5000_CONFIG.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        g3Layout.addWidget(self.pushButton_S2_WT_5000_CONFIG, 1, 7)

        layout.addWidget(self.groupBox_3)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 3: 直流功率设置
    # ══════════════════════════════════════════════
    def _build_step3(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流功率设置")
        self.groupBox_2.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g2Layout = QtWidgets.QGridLayout(self.groupBox_2)
        g2Layout.setSpacing(8)
        g2Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setChecked(True)
        self.checkBox_S3.setObjectName("checkBox_S3")
        g2Layout.addWidget(self.checkBox_S3, 0, 0, 1, 2)

        # DC power checkboxes
        dc3_cfg = [
            ("checkBox_S3_DC1", "直流电源1"),
            ("checkBox_S3_DC2", "直流电源2"),
            ("checkBox_S3_DC3", "直流电源3"),
            ("checkBox_S3_DC4", "直流电源4"),
        ]
        for c, (cb_name, cb_text) in enumerate(dc3_cfg):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g2Layout.addWidget(cb, 1, c)
            setattr(self, cb_name, cb)

        # Power factor
        self.label_76 = QtWidgets.QLabel("功率")
        self.label_76.setObjectName("label_76")
        g2Layout.addWidget(self.label_76, 2, 0)
        self.textEdit_S3_DC_PF = QtWidgets.QTextEdit()
        self.textEdit_S3_DC_PF.setObjectName("textEdit_S3_DC_PF")
        self.textEdit_S3_DC_PF.setFixedSize(100, 31)
        self.textEdit_S3_DC_PF.setText("100")
        g2Layout.addWidget(self.textEdit_S3_DC_PF, 2, 1)
        self.label_47 = QtWidgets.QLabel("%")
        self.label_47.setObjectName("label_47")
        g2Layout.addWidget(self.label_47, 2, 2)

        # Time settings
        self.label_25 = QtWidgets.QLabel("数据采集")
        self.label_25.setObjectName("label_25")
        g2Layout.addWidget(self.label_25, 3, 0)
        self.textEdit_S3_TIME_2 = QtWidgets.QTextEdit()
        self.textEdit_S3_TIME_2.setObjectName("textEdit_S3_TIME_2")
        self.textEdit_S3_TIME_2.setFixedSize(100, 31)
        self.textEdit_S3_TIME_2.setText("5")
        g2Layout.addWidget(self.textEdit_S3_TIME_2, 3, 1)
        self.comboBox_S3_TIME_2 = QtWidgets.QComboBox()
        self.comboBox_S3_TIME_2.setObjectName("comboBox_S3_TIME_2")
        self.comboBox_S3_TIME_2.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S3_TIME_2.setFixedWidth(120)
        g2Layout.addWidget(self.comboBox_S3_TIME_2, 3, 2)

        self.label_26 = QtWidgets.QLabel("等待时间:")
        self.label_26.setObjectName("label_26")
        g2Layout.addWidget(self.label_26, 3, 3)
        self.textEdit_S3_TIME_3 = QtWidgets.QTextEdit()
        self.textEdit_S3_TIME_3.setObjectName("textEdit_S3_TIME_3")
        self.textEdit_S3_TIME_3.setFixedSize(100, 31)
        self.textEdit_S3_TIME_3.setText("1")
        g2Layout.addWidget(self.textEdit_S3_TIME_3, 3, 4)
        self.comboBox_S3_TIME_3 = QtWidgets.QComboBox()
        self.comboBox_S3_TIME_3.setObjectName("comboBox_S3_TIME_3")
        self.comboBox_S3_TIME_3.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S3_TIME_3.setFixedWidth(120)
        g2Layout.addWidget(self.comboBox_S3_TIME_3, 3, 5)

        layout.addWidget(self.groupBox_2)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 4: 直流功率设置
    # ══════════════════════════════════════════════
    def _build_step4(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("直流功率设置")
        self.groupBox_4.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g4Layout = QtWidgets.QGridLayout(self.groupBox_4)
        g4Layout.setSpacing(10)
        g4Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S4 = QtWidgets.QCheckBox("step4")
        self.checkBox_S4.setChecked(True)
        self.checkBox_S4.setObjectName("checkBox_S4")
        g4Layout.addWidget(self.checkBox_S4, 0, 0, 1, 2)

        dc4_cfg = [
            ("checkBox_S4_DC1", "直流电源1"),
            ("checkBox_S4_DC2", "直流电源2"),
            ("checkBox_S4_DC3", "直流电源3"),
            ("checkBox_S4_DC4", "直流电源4"),
        ]
        for c, (cb_name, cb_text) in enumerate(dc4_cfg):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g4Layout.addWidget(cb, 1, c)
            setattr(self, cb_name, cb)

        self.label_77 = QtWidgets.QLabel("功率")
        self.label_77.setObjectName("label_77")
        g4Layout.addWidget(self.label_77, 2, 0)
        self.textEdit_S4_DC_PF = QtWidgets.QTextEdit()
        self.textEdit_S4_DC_PF.setObjectName("textEdit_S4_DC_PF")
        self.textEdit_S4_DC_PF.setFixedSize(100, 31)
        self.textEdit_S4_DC_PF.setText("100")
        g4Layout.addWidget(self.textEdit_S4_DC_PF, 2, 1)
        self.label_49 = QtWidgets.QLabel("%")
        self.label_49.setObjectName("label_49")
        g4Layout.addWidget(self.label_49, 2, 2)

        layout.addWidget(self.groupBox_4)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 5: 直流功率设置
    # ══════════════════════════════════════════════
    def _build_step5(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_8 = QtWidgets.QGroupBox()
        self.groupBox_8.setObjectName("groupBox_8")
        self.groupBox_8.setTitle("直流功率设置")
        self.groupBox_8.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g8Layout = QtWidgets.QGridLayout(self.groupBox_8)
        g8Layout.setSpacing(10)
        g8Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S5 = QtWidgets.QCheckBox("step5")
        self.checkBox_S5.setChecked(True)
        self.checkBox_S5.setObjectName("checkBox_S5")
        g8Layout.addWidget(self.checkBox_S5, 0, 0, 1, 2)

        dc5_cfg = [
            ("checkBox_S5_DC1", "直流电源1"),
            ("checkBox_S5_DC2", "直流电源2"),
            ("checkBox_S5_DC3", "直流电源3"),
            ("checkBox_S5_DC4", "直流电源4"),
        ]
        for c, (cb_name, cb_text) in enumerate(dc5_cfg):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g8Layout.addWidget(cb, 1, c)
            setattr(self, cb_name, cb)

        self.label_78 = QtWidgets.QLabel("功率")
        self.label_78.setObjectName("label_78")
        g8Layout.addWidget(self.label_78, 2, 0)
        self.textEdit_S5_DC_PF = QtWidgets.QTextEdit()
        self.textEdit_S5_DC_PF.setObjectName("textEdit_S5_DC_PF")
        self.textEdit_S5_DC_PF.setFixedSize(100, 31)
        self.textEdit_S5_DC_PF.setText("100")
        g8Layout.addWidget(self.textEdit_S5_DC_PF, 2, 1)
        self.label_50 = QtWidgets.QLabel("%")
        self.label_50.setObjectName("label_50")
        g8Layout.addWidget(self.label_50, 2, 2)

        layout.addWidget(self.groupBox_8)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 6: 直流功率设置
    # ══════════════════════════════════════════════
    def _build_step6(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_9 = QtWidgets.QGroupBox()
        self.groupBox_9.setObjectName("groupBox_9")
        self.groupBox_9.setTitle("直流功率设置")
        self.groupBox_9.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g9Layout = QtWidgets.QGridLayout(self.groupBox_9)
        g9Layout.setSpacing(10)
        g9Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S6 = QtWidgets.QCheckBox("step6")
        self.checkBox_S6.setChecked(True)
        self.checkBox_S6.setObjectName("checkBox_S6")
        g9Layout.addWidget(self.checkBox_S6, 0, 0, 1, 2)

        dc6_cfg = [
            ("checkBox_S6_DC1", "直流电源1"),
            ("checkBox_S6_DC2", "直流电源2"),
            ("checkBox_S6_DC3", "直流电源3"),
            ("checkBox_S6_DC4", "直流电源4"),
        ]
        for c, (cb_name, cb_text) in enumerate(dc6_cfg):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g9Layout.addWidget(cb, 1, c)
            setattr(self, cb_name, cb)

        self.label_79 = QtWidgets.QLabel("功率")
        self.label_79.setObjectName("label_79")
        g9Layout.addWidget(self.label_79, 2, 0)
        self.textEdit_S6_DC_PF = QtWidgets.QTextEdit()
        self.textEdit_S6_DC_PF.setObjectName("textEdit_S6_DC_PF")
        self.textEdit_S6_DC_PF.setFixedSize(100, 31)
        self.textEdit_S6_DC_PF.setText("100")
        g9Layout.addWidget(self.textEdit_S6_DC_PF, 2, 1)
        self.label_51 = QtWidgets.QLabel("%")
        self.label_51.setObjectName("label_51")
        g9Layout.addWidget(self.label_51, 2, 2)

        layout.addWidget(self.groupBox_9)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 7: 关机设置
    # ══════════════════════════════════════════════
    def _build_step7(self):
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

        self.checkBox_S7 = QtWidgets.QCheckBox("step7")
        self.checkBox_S7.setChecked(True)
        self.checkBox_S7.setObjectName("checkBox_S7")
        gLayout.addWidget(self.checkBox_S7, 0, 0)

        self.label_8 = QtWidgets.QLabel("交流电源")
        self.label_8.setObjectName("label_8")
        gLayout.addWidget(self.label_8, 0, 1)

        self.comboBox_S7_AC = QtWidgets.QComboBox()
        self.comboBox_S7_AC.setObjectName("comboBox_S7_AC")
        self.comboBox_S7_AC.addItems(["关闭", "开启"])
        self.comboBox_S7_AC.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S7_AC, 0, 2)

        dc7_cfg = [
            ("checkBox_S7_DC1", "直流电源1", "comboBox_S7_DC1"),
            ("checkBox_S7_DC2", "直流电源2", "comboBox_S7_DC2"),
            ("checkBox_S7_DC3", "直流电源3", "comboBox_S7_DC3"),
            ("checkBox_S7_DC4", "直流电源4", "comboBox_S7_DC4"),
        ]
        for c, (cb_name, cb_text, combo_name) in enumerate(dc7_cfg):
            col = c * 2
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

    def retranslateUi(self, Dialog_thaizhiliufenliang):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaizhiliufenliang.setWindowTitle(_translate("Dialog_thaizhiliufenliang", "直流分量项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaizhiliufenliang", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaizhiliufenliang", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaizhiliufenliang", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaizhiliufenliang", "提交"))
