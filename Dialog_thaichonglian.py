# -*- coding: utf-8 -*-
# 重连项目配置 - 步骤条布局（手写现代风格）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.dewetron_autotest_panel import AnalyzerModeSection
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)


class Ui_Dialog_thaichonglian(object):
    def setupUi(self, Dialog_thaichonglian):
        Dialog_thaichonglian.setObjectName("Dialog_thaichonglian")
        Dialog_thaichonglian.resize(1300, 850)
        Dialog_thaichonglian.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaichonglian.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaichonglian)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ 重联测试1", "④ 重联测试2", "⑤ 重联测试3", "⑥ 重联测试4", "⑦ 重联测试5", "⑧ 关机设置"]
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
        self._build_step0()
        self._build_step1()
        self._build_step2()
        self._build_step3()
        self._build_step4()
        self._build_step5()
        self._build_step6()
        self._build_step7()

        # 默认显示第一页
        self._switch_step(0)

        # DC 联动
        self._connect_dc_linkage()

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaichonglian)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaichonglian)

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
        """创建 QRadioButton 并存储到 self。"""
        rb = QtWidgets.QRadioButton(text)
        rb.setObjectName(name)
        if parent is not None:
            setattr(self, name, rb)
        if checked:
            rb.setChecked(True)
        return rb

    def _build_reconnect_step(self, step_index, step_num, group_box_name, check_box_name):
        """构建重连步骤页面（AC 电压 + 频率 + 数据采集时间）"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        groupBox = QtWidgets.QGroupBox()
        groupBox.setObjectName(group_box_name)
        groupBox.setTitle(f"重连 {step_num} 设置")
        groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(groupBox)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        # 行 0: 标题行
        lbl_ac_source = QtWidgets.QLabel("交流电源")
        lbl_ac_source.setStyleSheet("font-weight: bold; color: #475569;")
        gLayout.addWidget(lbl_ac_source, 0, 0)

        lbl_ac_volt_title = QtWidgets.QLabel("交流电压")
        lbl_ac_volt_title.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_ac_volt_title.setAlignment(QtCore.Qt.AlignCenter)
        gLayout.addWidget(lbl_ac_volt_title, 0, 1)

        lbl_freq_title = QtWidgets.QLabel("频率")
        lbl_freq_title.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_freq_title.setAlignment(QtCore.Qt.AlignCenter)
        gLayout.addWidget(lbl_freq_title, 0, 2)

        lbl_data_title = QtWidgets.QLabel("数据采集")
        lbl_data_title.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_data_title.setAlignment(QtCore.Qt.AlignCenter)
        gLayout.addWidget(lbl_data_title, 0, 3)

        # 行 1: 内容行
        checkBox = QtWidgets.QCheckBox(f"step{step_num}")
        checkBox.setChecked(True)
        checkBox.setObjectName(check_box_name)
        gLayout.addWidget(checkBox, 1, 0)

        # AC_VOLT
        ac_volt_edit = QtWidgets.QTextEdit()
        ac_volt_edit.setObjectName(f"textEdit_S{step_num}_AC_VOLT")
        ac_volt_edit.setFixedSize(100, 31)
        ac_volt_edit.setText("230")
        gLayout.addWidget(ac_volt_edit, 1, 1)
        setattr(self, f"textEdit_S{step_num}_AC_VOLT", ac_volt_edit)
        lbl_v_unit = QtWidgets.QLabel("V")
        lbl_v_unit.setStyleSheet("color: #64748b;")
        gLayout.addWidget(lbl_v_unit, 1, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # AC_FR
        ac_fr_edit = QtWidgets.QTextEdit()
        ac_fr_edit.setObjectName(f"textEdit_S{step_num}_AC_FR")
        ac_fr_edit.setFixedSize(100, 31)
        ac_fr_edit.setText("50")
        gLayout.addWidget(ac_fr_edit, 1, 2)
        setattr(self, f"textEdit_S{step_num}_AC_FR", ac_fr_edit)
        lbl_hz_unit = QtWidgets.QLabel("Hz")
        lbl_hz_unit.setStyleSheet("color: #64748b;")
        gLayout.addWidget(lbl_hz_unit, 1, 2, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # TIME + combo
        time_edit = QtWidgets.QTextEdit()
        time_edit.setObjectName(f"textEdit_S{step_num}_TIME")
        time_edit.setFixedSize(100, 31)
        time_edit.setText("2.5")
        gLayout.addWidget(time_edit, 1, 3)
        setattr(self, f"textEdit_S{step_num}_TIME", time_edit)
        time_combo = QtWidgets.QComboBox()
        time_combo.setObjectName(f"comboBox_S{step_num}_TIME")
        time_combo.addItems(["秒", "毫秒", "分钟"])
        time_combo.setFixedWidth(100)
        gLayout.addWidget(time_combo, 1, 4)
        setattr(self, f"comboBox_S{step_num}_TIME", time_combo)

        layout.addWidget(groupBox)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 0: AC + DC 电源设置 + 时序
    # ══════════════════════════════════════════════
    def _build_step0(self):
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

        lbl_ac_src = QtWidgets.QLabel("交流电源")
        lbl_ac_src.setObjectName("label_3")
        lbl_ac_src.setStyleSheet("font-weight: bold; color: #475569;")
        gLayout.addWidget(lbl_ac_src, 0, 2)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(100)
        gLayout.addWidget(self.comboBox_S1_AC, 0, 3)

        lbl_v1 = QtWidgets.QLabel("V")
        lbl_v1.setObjectName("label_5")
        gLayout.addWidget(lbl_v1, 0, 4)

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        gLayout.addWidget(self.label_4, 0, 5)

        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(80, 31)
        self.textEdit_S1_AC_VOLT.setText("230")
        gLayout.addWidget(self.textEdit_S1_AC_VOLT, 0, 6)

        lbl_v2_unit = QtWidgets.QLabel("V")
        gLayout.addWidget(lbl_v2_unit, 0, 7)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        gLayout.addWidget(self.label_113, 0, 8)

        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(80, 31)
        self.textEdit_S1_AC_VOLT_2.setText("230")
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 9)

        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        gLayout.addWidget(self.label_107, 0, 10)

        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(100)
        gLayout.addWidget(self.comboBox_S1_AC_2, 1, 3)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        gLayout.addWidget(self.label_123, 1, 5)

        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(80, 31)
        self.textEdit_S1_AC_VOLT_3.setText("230")
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 6)

        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        gLayout.addWidget(self.label_102, 1, 7)

        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        gLayout.addWidget(self.label_19, 1, 8)

        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(80, 31)
        self.textEdit_S1_AC_FR.setText("50")
        gLayout.addWidget(self.textEdit_S1_AC_FR, 1, 9)

        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        gLayout.addWidget(self.label_18, 1, 10)

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
        headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
        for c, h in enumerate(headers):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g2Layout.addWidget(lbl, 0, c)

        # DC1
        r = 1
        self.checkBox_S1_DC1 = QtWidgets.QCheckBox("直流电源1")
        self.checkBox_S1_DC1.setChecked(True)
        self.checkBox_S1_DC1.setObjectName("checkBox_S1_DC1")
        g2Layout.addWidget(self.checkBox_S1_DC1, r, 0)
        self.comboBox_S1_DC1 = QtWidgets.QComboBox()
        self.comboBox_S1_DC1.setObjectName("comboBox_S1_DC1")
        self.comboBox_S1_DC1.addItems(["开启", "关闭"])
        self.comboBox_S1_DC1.setFixedWidth(100)
        g2Layout.addWidget(self.comboBox_S1_DC1, r, 1)
        for c, name in enumerate(["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            if hasattr(te, "setTabChangesFocus"):
                te.setTabChangesFocus(True)
            g2Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC2
        r = 2
        self.checkBox_S1_DC2 = QtWidgets.QCheckBox("直流电源2")
        self.checkBox_S1_DC2.setChecked(True)
        self.checkBox_S1_DC2.setObjectName("checkBox_S1_DC2")
        g2Layout.addWidget(self.checkBox_S1_DC2, r, 0)
        self.comboBox_S1_DC2 = QtWidgets.QComboBox()
        self.comboBox_S1_DC2.setObjectName("comboBox_S1_DC2")
        self.comboBox_S1_DC2.addItems(["开启", "关闭"])
        self.comboBox_S1_DC2.setFixedWidth(100)
        g2Layout.addWidget(self.comboBox_S1_DC2, r, 1)
        for c, name in enumerate(["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            if hasattr(te, "setTabChangesFocus"):
                te.setTabChangesFocus(True)
            g2Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC3
        r = 3
        self.checkBox_S1_DC3 = QtWidgets.QCheckBox("直流电源3")
        self.checkBox_S1_DC3.setChecked(True)
        self.checkBox_S1_DC3.setObjectName("checkBox_S1_DC3")
        g2Layout.addWidget(self.checkBox_S1_DC3, r, 0)
        self.comboBox_S1_DC3 = QtWidgets.QComboBox()
        self.comboBox_S1_DC3.setObjectName("comboBox_S1_DC3")
        self.comboBox_S1_DC3.addItems(["开启", "关闭"])
        self.comboBox_S1_DC3.setFixedWidth(100)
        g2Layout.addWidget(self.comboBox_S1_DC3, r, 1)
        for c, name in enumerate(["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            if hasattr(te, "setTabChangesFocus"):
                te.setTabChangesFocus(True)
            g2Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC4
        r = 4
        self.checkBox_S1_DC4 = QtWidgets.QCheckBox("直流电源4")
        self.checkBox_S1_DC4.setChecked(True)
        self.checkBox_S1_DC4.setObjectName("checkBox_S1_DC4")
        g2Layout.addWidget(self.checkBox_S1_DC4, r, 0)
        self.comboBox_S1_DC4 = QtWidgets.QComboBox()
        self.comboBox_S1_DC4.setObjectName("comboBox_S1_DC4")
        self.comboBox_S1_DC4.addItems(["开启", "关闭"])
        self.comboBox_S1_DC4.setFixedWidth(100)
        g2Layout.addWidget(self.comboBox_S1_DC4, r, 1)
        for c, name in enumerate(["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            if hasattr(te, "setTabChangesFocus"):
                te.setTabChangesFocus(True)
            g2Layout.addWidget(te, r, c)
            setattr(self, name, te)

        layout.addWidget(self.groupBox_2)

        # ── 时序组 ──
        groupBoxTiming = QtWidgets.QGroupBox()
        groupBoxTiming.setObjectName("groupBox_4")
        groupBoxTiming.setTitle("时序设置")
        groupBoxTiming.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gTimingLayout = QtWidgets.QGridLayout(groupBoxTiming)
        gTimingLayout.setSpacing(8)
        gTimingLayout.setContentsMargins(12, 20, 12, 12)

        self.label_131 = QtWidgets.QLabel("等待时间:")
        self.label_131.setObjectName("label_131")
        gTimingLayout.addWidget(self.label_131, 0, 0)
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(100, 31)
        self.textEdit_S1_ACWaitTIME.setText("3")
        gTimingLayout.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(120)
        gTimingLayout.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        self.label_132 = QtWidgets.QLabel("启机时间:")
        self.label_132.setObjectName("label_132")
        gTimingLayout.addWidget(self.label_132, 0, 3)
        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(100, 31)
        self.textEdit_S1_TIME.setText("5")
        gTimingLayout.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(120)
        gTimingLayout.addWidget(self.comboBox_S1_TIME, 0, 5)

        layout.addWidget(groupBoxTiming)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 1: 功率分析仪设置（radio + stackedWidget 内嵌）
    # ══════════════════════════════════════════════
    def _build_step1(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_5 = QtWidgets.QGroupBox()
        self.groupBox_5.setObjectName("groupBox_5")
        self.groupBox_5.setTitle("功率分析仪配置")
        self.groupBox_5.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g5Layout = QtWidgets.QGridLayout(self.groupBox_5)
        g5Layout.setSpacing(10)
        g5Layout.setContentsMargins(16, 24, 16, 12)

        # 步骤启用复选框
        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        g5Layout.addWidget(self.checkBox_S2, 0, 0)

        # Radio buttons（单选，默认 WT3000）
        self.radioButton_S2_WT3000 = self._make_radio("radio_S2_WT3000", "WT3000", parent=self, checked=True)
        self.radioButton_S2_WT1800 = self._make_radio("radio_S2_WT1800", "WT1800", parent=self)
        self.radioButton_S2_WT1806E = self._make_radio("radio_S2_WT1806E", "WT1806E", parent=self)
        self.radioButton_S2_WT5000 = self._make_radio("radio_S2_WT5000", "WT5000", parent=self)

        self._wt_radio_group = QtWidgets.QButtonGroup(None)
        self._wt_radio_group.addButton(self.radioButton_S2_WT3000, 0)
        self._wt_radio_group.addButton(self.radioButton_S2_WT1800, 1)
        self._wt_radio_group.addButton(self.radioButton_S2_WT1806E, 2)
        self._wt_radio_group.addButton(self.radioButton_S2_WT5000, 3)

        radio_layout = QtWidgets.QHBoxLayout()
        radio_layout.setSpacing(24)
        radio_layout.setContentsMargins(8, 0, 0, 0)
        for rb in [self.radioButton_S2_WT3000, self.radioButton_S2_WT1800,
                   self.radioButton_S2_WT1806E, self.radioButton_S2_WT5000]:
            radio_layout.addWidget(rb)
        radio_layout.addStretch()
        g5Layout.addLayout(radio_layout, 0, 1, 1, 3)

        # QStackedWidget 承载 4 个 WT 配置页面
        self._wtStacked = QtWidgets.QStackedWidget()
        self._wtStacked.addWidget(build_wt3000_content(self))   # index 0
        self._wtStacked.addWidget(build_wt1800_content(self))   # index 1
        self._wtStacked.addWidget(build_wt1806e_content(self))  # index 2
        self._wtStacked.addWidget(build_wt5000_content(self))   # index 3
        g5Layout.addWidget(self._wtStacked, 1, 0, 1, 4)

        # Radio 切换联动
        def _on_wt_radio_toggled(btn, checked):
            if checked:
                btn_id = self._wt_radio_group.id(btn)
                self._wtStacked.setCurrentIndex(btn_id)

        self._wt_radio_group.buttonToggled.connect(_on_wt_radio_toggled)

        self._integrate_analyzer_mode(layout, self.groupBox_5)

        # Scroll so DEWETRON / WT content is never clipped on smaller screens.
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setWidget(page)
        self.stackedWidget.addWidget(scroll)

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
        self.comboBox_analyzer_recording_mode = getattr(
            self.analyzerModeSection, "comboBox_analyzer_recording_mode", None
        )
        self.get_checked_export_fields = self.dewetronPanel.get_checked_export_fields
        self.refresh_export_field_tree = self.dewetronPanel.refresh_export_field_tree
        self.set_checked_export_fields = self.dewetronPanel.set_checked_export_fields
        self.get_checked_fields = self.get_checked_export_fields
        self.refresh_checked_fields = self.refresh_export_field_tree
        self.set_checked_fields = self.set_checked_export_fields
        layout.addWidget(self.analyzerModeSection)

    # ══════════════════════════════════════════════
    # Step 2: 重连 1 (AC_VOLT, AC_FR, TIME)
    # ══════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_3 = QtWidgets.QGroupBox()
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setTitle("重连 1 设置")
        self.groupBox_3.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g3Layout = QtWidgets.QGridLayout(self.groupBox_3)
        g3Layout.setSpacing(10)
        g3Layout.setContentsMargins(16, 24, 16, 12)

        # 行 0: 标题
        lbl_ac_src = QtWidgets.QLabel("交流电源")
        lbl_ac_src.setStyleSheet("font-weight: bold; color: #475569;")
        g3Layout.addWidget(lbl_ac_src, 0, 0)

        lbl_ac_volt = QtWidgets.QLabel("交流电压")
        lbl_ac_volt.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_ac_volt.setAlignment(QtCore.Qt.AlignCenter)
        g3Layout.addWidget(lbl_ac_volt, 0, 1)

        lbl_freq = QtWidgets.QLabel("频率")
        lbl_freq.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_freq.setAlignment(QtCore.Qt.AlignCenter)
        g3Layout.addWidget(lbl_freq, 0, 2)

        lbl_data = QtWidgets.QLabel("数据采集")
        lbl_data.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_data.setAlignment(QtCore.Qt.AlignCenter)
        g3Layout.addWidget(lbl_data, 0, 3)

        # 行 1: 内容
        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setChecked(True)
        self.checkBox_S3.setObjectName("checkBox_S3")
        g3Layout.addWidget(self.checkBox_S3, 1, 0)

        self.textEdit_S3_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S3_AC_VOLT.setObjectName("textEdit_S3_AC_VOLT")
        self.textEdit_S3_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S3_AC_VOLT.setText("230")
        g3Layout.addWidget(self.textEdit_S3_AC_VOLT, 1, 1)

        self.textEdit_S3_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S3_AC_FR.setObjectName("textEdit_S3_AC_FR")
        self.textEdit_S3_AC_FR.setFixedSize(100, 31)
        self.textEdit_S3_AC_FR.setText("50")
        g3Layout.addWidget(self.textEdit_S3_AC_FR, 1, 2)

        self.textEdit_S3_TIME = QtWidgets.QTextEdit()
        self.textEdit_S3_TIME.setObjectName("textEdit_S3_TIME")
        self.textEdit_S3_TIME.setFixedSize(100, 31)
        self.textEdit_S3_TIME.setText("2.5")
        g3Layout.addWidget(self.textEdit_S3_TIME, 1, 3)
        self.comboBox_S3_TIME = QtWidgets.QComboBox()
        self.comboBox_S3_TIME.setObjectName("comboBox_S3_TIME")
        self.comboBox_S3_TIME.addItems(["秒", "毫秒", "分钟"])
        self.comboBox_S3_TIME.setFixedWidth(100)
        g3Layout.addWidget(self.comboBox_S3_TIME, 1, 4)

        layout.addWidget(self.groupBox_3)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 3: 重连 2
    # ══════════════════════════════════════════════
    def _build_step3(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_6 = QtWidgets.QGroupBox()
        self.groupBox_6.setObjectName("groupBox_6")
        self.groupBox_6.setTitle("重连 2 设置")
        self.groupBox_6.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g6Layout = QtWidgets.QGridLayout(self.groupBox_6)
        g6Layout.setSpacing(10)
        g6Layout.setContentsMargins(16, 24, 16, 12)

        lbl_ac_src = QtWidgets.QLabel("交流电源")
        lbl_ac_src.setStyleSheet("font-weight: bold; color: #475569;")
        g6Layout.addWidget(lbl_ac_src, 0, 0)

        lbl_ac_volt = QtWidgets.QLabel("交流电压")
        lbl_ac_volt.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_ac_volt.setAlignment(QtCore.Qt.AlignCenter)
        g6Layout.addWidget(lbl_ac_volt, 0, 1)

        lbl_freq = QtWidgets.QLabel("频率")
        lbl_freq.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_freq.setAlignment(QtCore.Qt.AlignCenter)
        g6Layout.addWidget(lbl_freq, 0, 2)

        lbl_data = QtWidgets.QLabel("数据采集")
        lbl_data.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_data.setAlignment(QtCore.Qt.AlignCenter)
        g6Layout.addWidget(lbl_data, 0, 3)

        self.checkBox_S4 = QtWidgets.QCheckBox("step4")
        self.checkBox_S4.setChecked(True)
        self.checkBox_S4.setObjectName("checkBox_S4")
        g6Layout.addWidget(self.checkBox_S4, 1, 0)

        self.textEdit_S4_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S4_AC_VOLT.setObjectName("textEdit_S4_AC_VOLT")
        self.textEdit_S4_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S4_AC_VOLT.setText("230")
        g6Layout.addWidget(self.textEdit_S4_AC_VOLT, 1, 1)

        self.textEdit_S4_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S4_AC_FR.setObjectName("textEdit_S4_AC_FR")
        self.textEdit_S4_AC_FR.setFixedSize(100, 31)
        self.textEdit_S4_AC_FR.setText("50")
        g6Layout.addWidget(self.textEdit_S4_AC_FR, 1, 2)

        self.textEdit_S4_TIME = QtWidgets.QTextEdit()
        self.textEdit_S4_TIME.setObjectName("textEdit_S4_TIME")
        self.textEdit_S4_TIME.setFixedSize(100, 31)
        self.textEdit_S4_TIME.setText("2.5")
        g6Layout.addWidget(self.textEdit_S4_TIME, 1, 3)
        self.comboBox_S4_TIME = QtWidgets.QComboBox()
        self.comboBox_S4_TIME.setObjectName("comboBox_S4_TIME")
        self.comboBox_S4_TIME.addItems(["秒", "毫秒", "分钟"])
        self.comboBox_S4_TIME.setFixedWidth(100)
        g6Layout.addWidget(self.comboBox_S4_TIME, 1, 4)

        layout.addWidget(self.groupBox_6)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 4: 重连 3
    # ══════════════════════════════════════════════
    def _build_step4(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_7 = QtWidgets.QGroupBox()
        self.groupBox_7.setObjectName("groupBox_7")
        self.groupBox_7.setTitle("重连 3 设置")
        self.groupBox_7.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g7Layout = QtWidgets.QGridLayout(self.groupBox_7)
        g7Layout.setSpacing(10)
        g7Layout.setContentsMargins(16, 24, 16, 12)

        lbl_ac_src = QtWidgets.QLabel("交流电源")
        lbl_ac_src.setStyleSheet("font-weight: bold; color: #475569;")
        g7Layout.addWidget(lbl_ac_src, 0, 0)

        lbl_ac_volt = QtWidgets.QLabel("交流电压")
        lbl_ac_volt.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_ac_volt.setAlignment(QtCore.Qt.AlignCenter)
        g7Layout.addWidget(lbl_ac_volt, 0, 1)

        lbl_freq = QtWidgets.QLabel("频率")
        lbl_freq.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_freq.setAlignment(QtCore.Qt.AlignCenter)
        g7Layout.addWidget(lbl_freq, 0, 2)

        lbl_data = QtWidgets.QLabel("数据采集")
        lbl_data.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_data.setAlignment(QtCore.Qt.AlignCenter)
        g7Layout.addWidget(lbl_data, 0, 3)

        self.checkBox_S5 = QtWidgets.QCheckBox("step5")
        self.checkBox_S5.setChecked(True)
        self.checkBox_S5.setObjectName("checkBox_S5")
        g7Layout.addWidget(self.checkBox_S5, 1, 0)

        self.textEdit_S5_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S5_AC_VOLT.setObjectName("textEdit_S5_AC_VOLT")
        self.textEdit_S5_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S5_AC_VOLT.setText("230")
        g7Layout.addWidget(self.textEdit_S5_AC_VOLT, 1, 1)

        self.textEdit_S5_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S5_AC_FR.setObjectName("textEdit_S5_AC_FR")
        self.textEdit_S5_AC_FR.setFixedSize(100, 31)
        self.textEdit_S5_AC_FR.setText("50")
        g7Layout.addWidget(self.textEdit_S5_AC_FR, 1, 2)

        self.textEdit_S5_TIME = QtWidgets.QTextEdit()
        self.textEdit_S5_TIME.setObjectName("textEdit_S5_TIME")
        self.textEdit_S5_TIME.setFixedSize(100, 31)
        self.textEdit_S5_TIME.setText("2.5")
        g7Layout.addWidget(self.textEdit_S5_TIME, 1, 3)
        self.comboBox_S5_TIME = QtWidgets.QComboBox()
        self.comboBox_S5_TIME.setObjectName("comboBox_S5_TIME")
        self.comboBox_S5_TIME.addItems(["秒", "毫秒", "分钟"])
        self.comboBox_S5_TIME.setFixedWidth(100)
        g7Layout.addWidget(self.comboBox_S5_TIME, 1, 4)

        layout.addWidget(self.groupBox_7)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 5: 重连 4
    # ══════════════════════════════════════════════
    def _build_step5(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_8 = QtWidgets.QGroupBox()
        self.groupBox_8.setObjectName("groupBox_8")
        self.groupBox_8.setTitle("重连 4 设置")
        self.groupBox_8.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g8Layout = QtWidgets.QGridLayout(self.groupBox_8)
        g8Layout.setSpacing(10)
        g8Layout.setContentsMargins(16, 24, 16, 12)

        lbl_ac_src = QtWidgets.QLabel("交流电源")
        lbl_ac_src.setStyleSheet("font-weight: bold; color: #475569;")
        g8Layout.addWidget(lbl_ac_src, 0, 0)

        lbl_ac_volt = QtWidgets.QLabel("交流电压")
        lbl_ac_volt.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_ac_volt.setAlignment(QtCore.Qt.AlignCenter)
        g8Layout.addWidget(lbl_ac_volt, 0, 1)

        lbl_freq = QtWidgets.QLabel("频率")
        lbl_freq.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_freq.setAlignment(QtCore.Qt.AlignCenter)
        g8Layout.addWidget(lbl_freq, 0, 2)

        lbl_data = QtWidgets.QLabel("数据采集")
        lbl_data.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_data.setAlignment(QtCore.Qt.AlignCenter)
        g8Layout.addWidget(lbl_data, 0, 3)

        self.checkBox_S6 = QtWidgets.QCheckBox("step6")
        self.checkBox_S6.setChecked(True)
        self.checkBox_S6.setObjectName("checkBox_S6")
        g8Layout.addWidget(self.checkBox_S6, 1, 0)

        self.textEdit_S6_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S6_AC_VOLT.setObjectName("textEdit_S6_AC_VOLT")
        self.textEdit_S6_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S6_AC_VOLT.setText("230")
        g8Layout.addWidget(self.textEdit_S6_AC_VOLT, 1, 1)

        self.textEdit_S6_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S6_AC_FR.setObjectName("textEdit_S6_AC_FR")
        self.textEdit_S6_AC_FR.setFixedSize(100, 31)
        self.textEdit_S6_AC_FR.setText("50")
        g8Layout.addWidget(self.textEdit_S6_AC_FR, 1, 2)

        self.textEdit_S6_TIME = QtWidgets.QTextEdit()
        self.textEdit_S6_TIME.setObjectName("textEdit_S6_TIME")
        self.textEdit_S6_TIME.setFixedSize(100, 31)
        self.textEdit_S6_TIME.setText("2.5")
        g8Layout.addWidget(self.textEdit_S6_TIME, 1, 3)
        self.comboBox_S6_TIME = QtWidgets.QComboBox()
        self.comboBox_S6_TIME.setObjectName("comboBox_S6_TIME")
        self.comboBox_S6_TIME.addItems(["秒", "毫秒", "分钟"])
        self.comboBox_S6_TIME.setFixedWidth(100)
        g8Layout.addWidget(self.comboBox_S6_TIME, 1, 4)

        layout.addWidget(self.groupBox_8)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 6: 重连 5
    # ══════════════════════════════════════════════
    def _build_step6(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_10 = QtWidgets.QGroupBox()
        self.groupBox_10.setObjectName("groupBox_10")
        self.groupBox_10.setTitle("重连 5 设置")
        self.groupBox_10.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g10Layout = QtWidgets.QGridLayout(self.groupBox_10)
        g10Layout.setSpacing(10)
        g10Layout.setContentsMargins(16, 24, 16, 12)

        lbl_ac_src = QtWidgets.QLabel("交流电源")
        lbl_ac_src.setStyleSheet("font-weight: bold; color: #475569;")
        g10Layout.addWidget(lbl_ac_src, 0, 0)

        lbl_ac_volt = QtWidgets.QLabel("交流电压")
        lbl_ac_volt.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_ac_volt.setAlignment(QtCore.Qt.AlignCenter)
        g10Layout.addWidget(lbl_ac_volt, 0, 1)

        lbl_freq = QtWidgets.QLabel("频率")
        lbl_freq.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_freq.setAlignment(QtCore.Qt.AlignCenter)
        g10Layout.addWidget(lbl_freq, 0, 2)

        lbl_data = QtWidgets.QLabel("数据采集")
        lbl_data.setStyleSheet("font-weight: bold; color: #475569;")
        lbl_data.setAlignment(QtCore.Qt.AlignCenter)
        g10Layout.addWidget(lbl_data, 0, 3)

        self.checkBox_S7 = QtWidgets.QCheckBox("step7")
        self.checkBox_S7.setChecked(True)
        self.checkBox_S7.setObjectName("checkBox_S7")
        g10Layout.addWidget(self.checkBox_S7, 1, 0)

        self.textEdit_S7_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S7_AC_VOLT.setObjectName("textEdit_S7_AC_VOLT")
        self.textEdit_S7_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S7_AC_VOLT.setText("230")
        g10Layout.addWidget(self.textEdit_S7_AC_VOLT, 1, 1)

        self.textEdit_S7_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S7_AC_FR.setObjectName("textEdit_S7_AC_FR")
        self.textEdit_S7_AC_FR.setFixedSize(100, 31)
        self.textEdit_S7_AC_FR.setText("50")
        g10Layout.addWidget(self.textEdit_S7_AC_FR, 1, 2)

        self.textEdit_S7_TIME = QtWidgets.QTextEdit()
        self.textEdit_S7_TIME.setObjectName("textEdit_S7_TIME")
        self.textEdit_S7_TIME.setFixedSize(100, 31)
        self.textEdit_S7_TIME.setText("2.5")
        g10Layout.addWidget(self.textEdit_S7_TIME, 1, 3)
        self.comboBox_S7_TIME = QtWidgets.QComboBox()
        self.comboBox_S7_TIME.setObjectName("comboBox_S7_TIME")
        self.comboBox_S7_TIME.addItems(["秒", "毫秒", "分钟"])
        self.comboBox_S7_TIME.setFixedWidth(100)
        g10Layout.addWidget(self.comboBox_S7_TIME, 1, 4)

        layout.addWidget(self.groupBox_10)
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

        self.groupBox_11 = QtWidgets.QGroupBox()
        self.groupBox_11.setObjectName("groupBox_11")
        self.groupBox_11.setTitle("关机设置")
        self.groupBox_11.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g11Layout = QtWidgets.QGridLayout(self.groupBox_11)
        g11Layout.setSpacing(10)
        g11Layout.setContentsMargins(16, 24, 16, 12)

        # Row 0: step_last + AC
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

        # Row 1: DC1-4
        self.checkBox_S_End_DC1 = QtWidgets.QCheckBox("直流电源1")
        self.checkBox_S_End_DC1.setChecked(True)
        self.checkBox_S_End_DC1.setObjectName("checkBox_S_End_DC1")
        g11Layout.addWidget(self.checkBox_S_End_DC1, 1, 0)

        self.label_dc1 = QtWidgets.QLabel("直流电源1")
        self.label_dc1.setVisible(False)
        g11Layout.addWidget(self.label_dc1, 1, 0)

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

        # 关机步骤 DC 联动
        end_dcs = [self.checkBox_S_End_DC1, self.checkBox_S_End_DC2,
                   self.checkBox_S_End_DC3, self.checkBox_S_End_DC4]
        end_combos = [self.comboBox_S_End_DC1, self.comboBox_S_End_DC2,
                      self.comboBox_S_End_DC3, self.comboBox_S_End_DC4]

        def _update_end_dc(_checked=None):
            step_on = self.checkBox_S_End.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                end_dcs[i].setEnabled(should_enable)
                end_dcs[i].setChecked(should_enable)
                end_combos[i].setEnabled(should_enable)

        self.checkBox_S_End.toggled.connect(_update_end_dc)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_end_dc)
        _update_end_dc()

    def retranslateUi(self, Dialog_thaichonglian):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaichonglian.setWindowTitle(_translate("Dialog_thaichonglian", "重连项目配置"))
