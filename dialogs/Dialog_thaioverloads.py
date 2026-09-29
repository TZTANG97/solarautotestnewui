# -*- coding: utf-8 -*-
# 90min过载项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.dewetron_autotest_panel import AnalyzerModeSection
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content,
)


class Ui_Dialog_thaioverloads(object):
    def setupUi(self, Dialog_thaioverloads):
        Dialog_thaioverloads.setObjectName("Dialog_thaioverloads")
        Dialog_thaioverloads.resize(1300, 850)
        Dialog_thaioverloads.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaioverloads.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaioverloads)
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

        self.pushButton_ExportIotTemplate = QtWidgets.QPushButton("导出IOT模板")
        self.pushButton_ExportIotTemplate.setObjectName("pushButton_ExportIotTemplate")
        self.pushButton_ExportIotTemplate.setToolTip("把当前过载页控件导出为 iot_templates/overload_default.json，供云端任务模板使用")
        self.pushButton_ExportIotTemplate.setStyleSheet("""
            QPushButton { background-color: #0ea5e9; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; }
            QPushButton:hover { background-color: #0284c7; }
        """)
        topLayout.addWidget(self.pushButton_ExportIotTemplate)

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
        step_titles = ["① AC/DC 电源+时序", "② 功率分析仪", "③ 过载测试", "④ 关机设置"]
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
        self._wire_recording_mode()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaioverloads)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaioverloads)

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
        self.get_checked_export_fields = self.dewetronPanel.get_checked_export_fields
        self.refresh_export_field_tree = self.dewetronPanel.refresh_export_field_tree
        self.set_checked_export_fields = self.dewetronPanel.set_checked_export_fields
        self.get_checked_fields = self.get_checked_export_fields
        self.refresh_checked_fields = self.refresh_export_field_tree
        self.set_checked_fields = self.set_checked_export_fields
        layout.addWidget(self.analyzerModeSection)


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
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("交流电源设置")
        self.groupBox_2.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g2Layout = QtWidgets.QGridLayout(self.groupBox_2)
        g2Layout.setSpacing(8)
        g2Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        g2Layout.addWidget(self.checkBox_S1, 0, 0, 1, 2)

        self.label_3 = QtWidgets.QLabel("交流电源")
        self.label_3.setObjectName("label_3")
        g2Layout.addWidget(self.label_3, 0, 2)
        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(120)
        g2Layout.addWidget(self.comboBox_S1_AC, 0, 3)

        g2Layout.addWidget(QtWidgets.QLabel("相位"), 0, 4)
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        g2Layout.addWidget(self.comboBox_S1_AC_2, 0, 5)

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        g2Layout.addWidget(self.label_4, 1, 0)
        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(100, 31)
        self.textEdit_S1_AC_VOLT.setText("230")
        g2Layout.addWidget(self.textEdit_S1_AC_VOLT, 1, 1)
        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        g2Layout.addWidget(self.label_5, 1, 2)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        g2Layout.addWidget(self.label_113, 1, 3)
        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(100, 31)
        self.textEdit_S1_AC_VOLT_2.setText("230")
        g2Layout.addWidget(self.textEdit_S1_AC_VOLT_2, 1, 4)
        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        g2Layout.addWidget(self.label_107, 1, 5)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        g2Layout.addWidget(self.label_123, 2, 0)
        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(100, 31)
        self.textEdit_S1_AC_VOLT_3.setText("230")
        g2Layout.addWidget(self.textEdit_S1_AC_VOLT_3, 2, 1)
        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        g2Layout.addWidget(self.label_102, 2, 2)

        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        g2Layout.addWidget(self.label_19, 2, 3)
        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(100, 31)
        self.textEdit_S1_AC_FR.setText("50")
        g2Layout.addWidget(self.textEdit_S1_AC_FR, 2, 4)
        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        g2Layout.addWidget(self.label_18, 2, 5)

        layout.addWidget(self.groupBox_2)

        # ── DC 电源组 (4 channels) ──
        self.groupBox_6 = QtWidgets.QGroupBox()
        self.groupBox_6.setObjectName("groupBox_6")
        self.groupBox_6.setTitle("直流电源设置")
        self.groupBox_6.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g6Layout = QtWidgets.QGridLayout(self.groupBox_6)
        g6Layout.setSpacing(6)
        g6Layout.setContentsMargins(12, 20, 12, 12)

        # Header
        headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
        for c, h in enumerate(headers):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g6Layout.addWidget(lbl, 0, c)

        # DC1
        r = 1
        self.checkBox_S1_DC1 = QtWidgets.QCheckBox("直流电源1")
        self.checkBox_S1_DC1.setChecked(True)
        self.checkBox_S1_DC1.setObjectName("checkBox_S1_DC1")
        g6Layout.addWidget(self.checkBox_S1_DC1, r, 0)
        self.comboBox_S1_DC1 = QtWidgets.QComboBox()
        self.comboBox_S1_DC1.setObjectName("comboBox_S1_DC1")
        self.comboBox_S1_DC1.addItems(["开启", "关闭"])
        self.comboBox_S1_DC1.setFixedWidth(100)
        g6Layout.addWidget(self.comboBox_S1_DC1, r, 1)
        for c, (name, default) in enumerate([
            ("textEdit_S1_DC1_VOLT", "220"), ("textEdit_S1_DC1_CURR", "10"),
            ("textEdit_S1_DC1_Voc", "220"), ("textEdit_S1_DC1_Isc", "10"),
            ("textEdit_S1_DC1_PF", "100")
        ], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            te.setText(default)
            g6Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC2
        r = 2
        self.checkBox_S1_DC2 = QtWidgets.QCheckBox("直流电源2")
        self.checkBox_S1_DC2.setChecked(True)
        self.checkBox_S1_DC2.setObjectName("checkBox_S1_DC2")
        g6Layout.addWidget(self.checkBox_S1_DC2, r, 0)
        self.comboBox_S1_DC2 = QtWidgets.QComboBox()
        self.comboBox_S1_DC2.setObjectName("comboBox_S1_DC2")
        self.comboBox_S1_DC2.addItems(["开启", "关闭"])
        self.comboBox_S1_DC2.setFixedWidth(100)
        g6Layout.addWidget(self.comboBox_S1_DC2, r, 1)
        for c, (name, default) in enumerate([
            ("textEdit_S1_DC2_VOLT", "220"), ("textEdit_S1_DC2_CURR", "10"),
            ("textEdit_S1_DC2_Voc", "220"), ("textEdit_S1_DC2_Isc", "10"),
            ("textEdit_S1_DC2_PF", "100")
        ], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            te.setText(default)
            g6Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC3
        r = 3
        self.checkBox_S1_DC3 = QtWidgets.QCheckBox("直流电源3")
        self.checkBox_S1_DC3.setChecked(True)
        self.checkBox_S1_DC3.setObjectName("checkBox_S1_DC3")
        g6Layout.addWidget(self.checkBox_S1_DC3, r, 0)
        self.comboBox_S1_DC3 = QtWidgets.QComboBox()
        self.comboBox_S1_DC3.setObjectName("comboBox_S1_DC3")
        self.comboBox_S1_DC3.addItems(["开启", "关闭"])
        self.comboBox_S1_DC3.setFixedWidth(100)
        g6Layout.addWidget(self.comboBox_S1_DC3, r, 1)
        for c, (name, default) in enumerate([
            ("textEdit_S1_DC3_VOLT", "220"), ("textEdit_S1_DC3_CURR", "10"),
            ("textEdit_S1_DC3_Voc", "220"), ("textEdit_S1_DC3_Isc", "10"),
            ("textEdit_S1_DC3_PF", "100")
        ], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            te.setText(default)
            g6Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC4
        r = 4
        self.checkBox_S1_DC4 = QtWidgets.QCheckBox("直流电源4")
        self.checkBox_S1_DC4.setChecked(True)
        self.checkBox_S1_DC4.setObjectName("checkBox_S1_DC4")
        g6Layout.addWidget(self.checkBox_S1_DC4, r, 0)
        self.comboBox_S1_DC4 = QtWidgets.QComboBox()
        self.comboBox_S1_DC4.setObjectName("comboBox_S1_DC4")
        self.comboBox_S1_DC4.addItems(["开启", "关闭"])
        self.comboBox_S1_DC4.setFixedWidth(100)
        g6Layout.addWidget(self.comboBox_S1_DC4, r, 1)
        for c, (name, default) in enumerate([
            ("textEdit_S1_DC4_VOLT", "220"), ("textEdit_S1_DC4_CURR", "10"),
            ("textEdit_S1_DC4_Voc", "220"), ("textEdit_S1_DC4_Isc", "10"),
            ("textEdit_S1_DC4_PF", "100")
        ], start=2):
            te = QtWidgets.QTextEdit()
            te.setObjectName(name)
            te.setFixedSize(80, 28)
            te.setText(default)
            g6Layout.addWidget(te, r, c)
            setattr(self, name, te)

        layout.addWidget(self.groupBox_6)

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

        grp = QtWidgets.QGroupBox()
        grp.setTitle("功率分析仪配置")
        grp.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        gLayout.addWidget(self.checkBox_S2, 0, 0)

        # Radio buttons（单选，默认 WT3000）
        self.radioButton_S2_WT3000 = QtWidgets.QRadioButton("WT3000")
        self.radioButton_S2_WT3000.setObjectName("radio_S2_WT3000")
        self.radioButton_S2_WT3000.setChecked(True)
        self.radioButton_S2_WT1800 = QtWidgets.QRadioButton("WT1800")
        self.radioButton_S2_WT1800.setObjectName("radio_S2_WT1800")
        self.radioButton_S2_WT1806E = QtWidgets.QRadioButton("WT1806E")
        self.radioButton_S2_WT1806E.setObjectName("radio_S2_WT1806E")
        self.radioButton_S2_WT5000 = QtWidgets.QRadioButton("WT5000")
        self.radioButton_S2_WT5000.setObjectName("radio_S2_WT5000")

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

        # QStackedWidget 承载 4 个配置页面
        self._wtStacked = QtWidgets.QStackedWidget()
        self._wtStacked.addWidget(build_wt3000_content(self))   # index 0
        self._wtStacked.addWidget(build_wt1800_content(self))   # index 1
        self._wtStacked.addWidget(build_wt1806e_content(self))  # index 2
        self._wtStacked.addWidget(build_wt5000_content(self))   # index 3
        gLayout.addWidget(self._wtStacked, 1, 0, 1, 4)

        # Radio 切换联动
        def _on_radio_toggled(btn, checked):
            if checked:
                self._wtStacked.setCurrentIndex(radio_group.id(btn))

        radio_group.buttonToggled.connect(_on_radio_toggled)

        self._integrate_analyzer_mode(layout, grp)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 3: 数据采集
    # ══════════════════════════════════════════════

    def _build_step3(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("数据采集设置")
        self.groupBox_4.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g4Layout = QtWidgets.QGridLayout(self.groupBox_4)
        g4Layout.setSpacing(10)
        g4Layout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S3 = QtWidgets.QCheckBox("step3")
        self.checkBox_S3.setChecked(True)
        self.checkBox_S3.setObjectName("checkBox_S3")
        g4Layout.addWidget(self.checkBox_S3, 0, 0)

        self.label_25 = QtWidgets.QLabel("数据采集")
        self.label_25.setObjectName("label_25")
        g4Layout.addWidget(self.label_25, 0, 1)

        self.textEdit_S3_TIME_2 = QtWidgets.QTextEdit()
        self.textEdit_S3_TIME_2.setObjectName("textEdit_S3_TIME_2")
        self.textEdit_S3_TIME_2.setFixedSize(100, 31)
        self.textEdit_S3_TIME_2.setText("90")
        g4Layout.addWidget(self.textEdit_S3_TIME_2, 0, 2)

        self.comboBox_S3_TIME_2 = QtWidgets.QComboBox()
        self.comboBox_S3_TIME_2.setObjectName("comboBox_S3_TIME_2")
        self.comboBox_S3_TIME_2.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S3_TIME_2.setFixedWidth(120)
        g4Layout.addWidget(self.comboBox_S3_TIME_2, 0, 3)

        from utils.wt_recording_mode import MODE_LABELS, MODE_CONTINUOUS, MODE_SPLIT

        rec_label = QtWidgets.QLabel("录波方式")
        g4Layout.addWidget(rec_label, 1, 1)
        self.comboBox_S3_record_mode = QtWidgets.QComboBox()
        self.comboBox_S3_record_mode.setObjectName("comboBox_S3_record_mode")
        self.comboBox_S3_record_mode.addItem(MODE_LABELS[MODE_CONTINUOUS], MODE_CONTINUOUS)
        self.comboBox_S3_record_mode.addItem(MODE_LABELS[MODE_SPLIT], MODE_SPLIT)
        self.comboBox_S3_record_mode.setMinimumWidth(220)
        g4Layout.addWidget(self.comboBox_S3_record_mode, 1, 2, 1, 2)
        self.pushButton_S3_fill_filenames = QtWidgets.QPushButton("填充推荐文件名")
        self.pushButton_S3_fill_filenames.setObjectName("pushButton_S3_fill_filenames")
        g4Layout.addWidget(self.pushButton_S3_fill_filenames, 1, 4)

        tip = QtWidgets.QLabel(
            "一条线连续录：90 分钟录成单个文件；分开录：按采集时间触发一轮存盘。"
            "文件名填在功率分析仪页的「文件名列表」。"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #64748b; font-weight: normal; font-size: 11px;")
        g4Layout.addWidget(tip, 2, 0, 1, 6)

        layout.addWidget(self.groupBox_4)
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

        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("关机设置")
        self.groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(self.groupBox)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S5 = QtWidgets.QCheckBox("step14")
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
        s5_dc = []
        for c, (cb_name, cb_text, combo_name) in enumerate(dc5_cfg):
            col = 1 + c * 2
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            gLayout.addWidget(cb, 1, col)
            setattr(self, cb_name, cb)
            s5_dc.append(cb)
            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["关闭", "开启"])
            combo.setFixedWidth(120)
            gLayout.addWidget(combo, 1, col + 1)
            setattr(self, combo_name, combo)

        # step1 DC 联动关机 DC 复选框
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        def _update_s5_dc():
            step_on = self.checkBox_S5.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                s5_dc[i].setEnabled(should_enable)
                s5_dc[i].setChecked(should_enable)

        def _on_s5_toggled(checked):
            _update_s5_dc()
            self.comboBox_S5_AC.setEnabled(checked)

        self.checkBox_S5.toggled.connect(_on_s5_toggled)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_s5_dc)
        _on_s5_toggled(self.checkBox_S5.isChecked())

        layout.addWidget(self.groupBox)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def _wire_recording_mode(self):
        from utils.wt_recording_mode import (
            apply_filename_list_to_wt_pages,
            combo_index_to_mode,
            mode_to_combo_index,
            overload_recommended_filenames,
        )
        from components.wt_recording_mode_row import WtRecordingModeRow, install_on_wt_filename_group

        def _recommended_names():
            return overload_recommended_filenames(
                combo_index_to_mode(self.comboBox_S3_record_mode.currentIndex())
            )

        def _fill_wt_names(names=None):
            if names is None:
                names = _recommended_names()
            apply_filename_list_to_wt_pages(self._wtStacked, names)

        def _sync_wt_rows(mode):
            for page_idx in range(self._wtStacked.count()):
                page = self._wtStacked.widget(page_idx)
                if page is None:
                    continue
                row = page.findChild(WtRecordingModeRow)
                if row is None:
                    continue
                row.blockSignals(True)
                row.set_mode(mode)
                row.blockSignals(False)

        def _on_s3_mode(_index=None):
            mode = combo_index_to_mode(self.comboBox_S3_record_mode.currentIndex())
            _sync_wt_rows(mode)
            _fill_wt_names()

        self.pushButton_S3_fill_filenames.clicked.connect(lambda: _fill_wt_names())
        self.comboBox_S3_record_mode.currentIndexChanged.connect(_on_s3_mode)

        for page_idx in range(self._wtStacked.count()):
            page = self._wtStacked.widget(page_idx)
            row = install_on_wt_filename_group(page, _recommended_names)
            if row is not None:
                row.names_filled.connect(_fill_wt_names)

                def _on_wt_mode(mode, row_ref=row):
                    self.comboBox_S3_record_mode.blockSignals(True)
                    self.comboBox_S3_record_mode.setCurrentIndex(mode_to_combo_index(mode))
                    self.comboBox_S3_record_mode.blockSignals(False)
                    _sync_wt_rows(mode)
                    _fill_wt_names()

                row.mode_changed.connect(_on_wt_mode)

        _on_s3_mode()

    def retranslateUi(self, Dialog_thaioverloads):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaioverloads.setWindowTitle(_translate("Dialog_thaioverloads", "90min过载项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaioverloads", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaioverloads", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaioverloads", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaioverloads", "提交"))
