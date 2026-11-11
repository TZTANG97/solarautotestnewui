# -*- coding: utf-8 -*-
# 电压闪变项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
import re as _re
from xml.etree import ElementTree as _ET

from components.dewetron_autotest_panel import (
    DEFAULT_RATE_OPTIONS,
    parse_power_group_tree,  # noqa: F401 — SCPITestWave / 谐波 Dialog 从此处导入
)


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

        # 防止字段树父子联动时递归触发 itemChanged
        self._block_tree_signals = False

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

        # 数据查看按钮（德威创模式专用，默认隐藏）
        self.pushButton_DEW_DataViewer = QtWidgets.QPushButton("数据查看")
        self.pushButton_DEW_DataViewer.setObjectName("pushButton_DEW_DataViewer")
        self.pushButton_DEW_DataViewer.setStyleSheet("""
            QPushButton { background-color: #f59e0b; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #d97706; }
        """)
        self.pushButton_DEW_DataViewer.hide()  # 默认隐藏，切换到德威创模式时显示
        topLayout.addWidget(self.pushButton_DEW_DataViewer)

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

        # ── 模式切换（WT3000闪变 / 德威创模式） ──
        self._radio_group = QtWidgets.QButtonGroup(None)
        self._radio_group.setExclusive(True)

        self.radio_wt3000 = QtWidgets.QRadioButton("WT3000闪变")
        self.radio_wt3000.setChecked(True)
        self.radio_wt3000.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b; background: transparent;")
        self._radio_group.addButton(self.radio_wt3000, 0)
        topLayout.addWidget(self.radio_wt3000)

        self.radio_dewetron = QtWidgets.QRadioButton("德威创模式")
        self.radio_dewetron.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b; background: transparent;")
        self._radio_group.addButton(self.radio_dewetron, 1)
        topLayout.addWidget(self.radio_dewetron)

        # 国家标准（默认泰国=现行台架；切换才改工况，不碰 WT/德威创模式）
        stdLabel = QtWidgets.QLabel("国家标准")
        stdLabel.setStyleSheet(
            "font-size: 12px; color: #475569; background: transparent; border: none;"
        )
        topLayout.addWidget(stdLabel)
        self.comboBox_SolarStandard = QtWidgets.QComboBox()
        self.comboBox_SolarStandard.setObjectName("comboBox_SolarStandard")
        self.comboBox_SolarStandard.setFixedWidth(168)
        self.comboBox_SolarStandard.setStyleSheet(
            "QComboBox { font-size: 12px; padding: 2px 6px; background: white; }"
        )
        try:
            from utils.iot_flicker_standard import list_flicker_standard_options

            for opt in list_flicker_standard_options():
                self.comboBox_SolarStandard.addItem(str(opt["label"]), str(opt["id"]))
        except Exception:
            self.comboBox_SolarStandard.addItem("泰国 PEA/MEA（现行）", "thai")
        self.comboBox_SolarStandard.setCurrentIndex(0)
        self._solar_standard = "thai"
        self._flicker_cycle_sec = 600
        self.comboBox_SolarStandard.currentIndexChanged.connect(self._on_solar_standard_changed)
        topLayout.addWidget(self.comboBox_SolarStandard)

        sep2 = QtWidgets.QFrame()
        sep2.setFrameShape(QtWidgets.QFrame.VLine)
        sep2.setStyleSheet("color: #cbd5e1; border: none; max-width: 1px;")
        topLayout.addWidget(sep2)

        # 横向步骤指示器
        self._step_labels = []
        step_titles = ["① AC/DC 电源", "② 闪变", "③ DC 开关循环", "④ 判定结果", "⑤ 关机设置"]
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

        # ── 连接模式切换信号 ──
        self._radio_group.buttonToggled.connect(self._on_mode_changed)

        # 默认显示第一页（WT3000 模式）
        self._mode = 'wt3000'
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

        # Step 2: DEWETRON 闪变
        s2_dew_children = [
            self.checkBox_DEW_FlickerStandard, self.comboBox_DEW_WeightingType,
            self.comboBox_DEW_MaxRefreshRate, self.textEdit_DEW_NominalVoltage,
            self.textEdit_DEW_ShortFlickerTime, self.textEdit_DEW_LongFlickerTime,
            self.textEdit_DEW_ShortCircuitPower, self.checkBox_DEW_RollingCalc,
            self.pushButton_DEW_TestApply,
        ]

        def _on_s2_dew_toggled(checked):
            for w in s2_dew_children:
                w.setEnabled(checked)

        self.checkBox_S2_DEW.toggled.connect(_on_s2_dew_toggled)
        _on_s2_dew_toggled(self.checkBox_S2_DEW.isChecked())

        # Step 3: DC 开关循环（DC 复选框联动 step1 DC）
        s3_dc_first = [self.checkBox_S3_DC1, self.checkBox_S3_DC2,
                       self.checkBox_S3_DC3, self.checkBox_S3_DC4]
        s3_dc_second = [self.checkBox_S3_DC1_2, self.checkBox_S3_DC2_2,
                        self.checkBox_S3_DC3_2, self.checkBox_S3_DC4_2]
        s3_non_dc = [
            self.comboBox_S3_DC1, self.comboBox_S3_DC2,
            self.comboBox_S3_DC3, self.comboBox_S3_DC4,
            self.comboBox_S3_DC1_2, self.comboBox_S3_DC2_2,
            self.comboBox_S3_DC3_2, self.comboBox_S3_DC4_2,
            self.textEdit_S3_TIME, self.comboBox_S3_TIME,
            self.textEdit_S3_TIME_2, self.comboBox_S3_TIME_2, self.textEdit_S3_CYCLE_TIME,
        ]
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        def _update_s3_dc():
            step_on = self.checkBox_S3.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                s3_dc_first[i].setEnabled(should_enable)
                s3_dc_first[i].setChecked(should_enable)
                s3_dc_second[i].setEnabled(should_enable)
                s3_dc_second[i].setChecked(should_enable)

        def _on_s3_toggled(checked):
            _update_s3_dc()
            for w in s3_non_dc:
                w.setEnabled(checked)

        self.checkBox_S3.toggled.connect(_on_s3_toggled)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_s3_dc)
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

        # Step 4: DEWETRON 导出设置
        s4_dew_children = [
            self.spinBox_DEW_DecimalPlaces, self.checkBox_DEW_RealtimeWaveform,
            self.checkBox_DEW_ExportAbsTime, self.checkBox_DEW_KeepOxygenDmd,
            self.treeWidget_DEW_ExportFields,
        ]

        def _on_s4_dew_toggled(checked):
            for w in s4_dew_children:
                w.setEnabled(checked)

        self.checkBox_S4_DEW.toggled.connect(_on_s4_dew_toggled)
        _on_s4_dew_toggled(self.checkBox_S4_DEW.isChecked())

        # Step 5: 关机设置（DC 复选框联动 step1 DC）
        s5_dc = [self.checkBox_S5_DC1, self.checkBox_S5_DC2,
                 self.checkBox_S5_DC3, self.checkBox_S5_DC4]
        s5_non_dc = [
            self.comboBox_S5_AC, self.comboBox_S5_DC1,
            self.comboBox_S5_DC2, self.comboBox_S5_DC3, self.comboBox_S5_DC4,
        ]

        def _update_s5_dc():
            step_on = self.checkBox_S5.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                s5_dc[i].setEnabled(should_enable)
                s5_dc[i].setChecked(should_enable)

        def _on_s5_toggled(checked):
            _update_s5_dc()
            for w in s5_non_dc:
                w.setEnabled(checked)

        self.checkBox_S5.toggled.connect(_on_s5_toggled)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_s5_dc)
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

        # 单相/三相：必须独占格子，不能与交流电压3同占 (1,3)
        g6Layout.addWidget(QtWidgets.QLabel("接线:"), 1, 0)
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        g6Layout.addWidget(self.comboBox_S1_AC_2, 1, 1)

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
        headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
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
            if hasattr(te, "setTabChangesFocus"):
                te.setTabChangesFocus(True)
            g7Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC2
        r = 2
        self.checkBox_S1_DC2 = QtWidgets.QCheckBox("直流电源2")
        self.checkBox_S1_DC2.setChecked(False)
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
            if hasattr(te, "setTabChangesFocus"):
                te.setTabChangesFocus(True)
            g7Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC3
        r = 3
        self.checkBox_S1_DC3 = QtWidgets.QCheckBox("直流电源3")
        self.checkBox_S1_DC3.setChecked(False)
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
            if hasattr(te, "setTabChangesFocus"):
                te.setTabChangesFocus(True)
            g7Layout.addWidget(te, r, c)
            setattr(self, name, te)

        # DC4
        r = 4
        self.checkBox_S1_DC4 = QtWidgets.QCheckBox("直流电源4")
        self.checkBox_S1_DC4.setChecked(False)
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
            if hasattr(te, "setTabChangesFocus"):
                te.setTabChangesFocus(True)
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
    # Step 2: 闪变设置（WT3000 / DEWETRON 双模式）
    # ══════════════════════════════════════════════
    def _build_step2(self):
        # step2 用 QStackedWidget 承载两种模式的配置页
        self._step2Stacked = QtWidgets.QStackedWidget()

        # ── 页面 0: WT3000 闪变 ──
        wt_page = QtWidgets.QWidget()
        wt_page.setStyleSheet("background-color: white;")
        wt_layout = QtWidgets.QVBoxLayout(wt_page)
        wt_layout.setContentsMargins(16, 16, 16, 16)
        wt_layout.setSpacing(12)

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

        wt_layout.addWidget(self.groupBox_3)
        wt_layout.addStretch()
        self._step2Stacked.addWidget(wt_page)

        # ── 页面 1: DEWETRON 闪变 ──
        dew_page = QtWidgets.QWidget()
        dew_page.setStyleSheet("background-color: white;")
        dew_layout = QtWidgets.QVBoxLayout(dew_page)
        dew_layout.setContentsMargins(16, 16, 16, 16)
        dew_layout.setSpacing(12)

        dew_group = QtWidgets.QGroupBox()
        dew_group.setTitle("DEWETRON 闪变测量配置")
        dew_group.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        formLayout = QtWidgets.QFormLayout(dew_group)
        formLayout.setSpacing(10)
        formLayout.setContentsMargins(16, 24, 16, 12)

        # step2 复选框（DEWETRON 模式也复用）
        self.checkBox_S2_DEW = QtWidgets.QCheckBox("step2")
        self.checkBox_S2_DEW.setChecked(True)
        self.checkBox_S2_DEW.setObjectName("checkBox_S2_DEW")
        formLayout.addRow(self.checkBox_S2_DEW)

        self.checkBox_DEW_FlickerStandard = QtWidgets.QCheckBox("闪变计算依照IEC61000-4-15: 2011")
        self.checkBox_DEW_FlickerStandard.setChecked(True)
        self.checkBox_DEW_FlickerStandard.setObjectName("checkBox_DEW_FlickerStandard")
        formLayout.addRow(self.checkBox_DEW_FlickerStandard)

        self.comboBox_DEW_WeightingType = QtWidgets.QComboBox()
        self.comboBox_DEW_WeightingType.setObjectName("comboBox_DEW_WeightingType")
        self.comboBox_DEW_WeightingType.addItems(["自动检测", "230V / 50Hz", "230V / 60Hz", "120V / 50Hz", "120V / 60Hz"])
        self.comboBox_DEW_WeightingType.setFixedWidth(200)
        formLayout.addRow("加权类型:", self.comboBox_DEW_WeightingType)

        self.comboBox_DEW_MaxRefreshRate = QtWidgets.QComboBox()
        self.comboBox_DEW_MaxRefreshRate.setObjectName("comboBox_DEW_MaxRefreshRate")
        # 与共用 Dewetron 面板一致：含 200/500/1000ms（原先闪变页只有 100）
        self.comboBox_DEW_MaxRefreshRate.addItems(list(DEFAULT_RATE_OPTIONS))
        self.comboBox_DEW_MaxRefreshRate.setCurrentText("Default")
        self.comboBox_DEW_MaxRefreshRate.setEditable(True)
        self.comboBox_DEW_MaxRefreshRate.setToolTip(
            "最大刷新率（ms）。可选 100/200/500/1000；也可直接输入数值。"
        )
        self.comboBox_DEW_MaxRefreshRate.setFixedWidth(200)
        formLayout.addRow("最大刷新率:", self.comboBox_DEW_MaxRefreshRate)

        self.textEdit_DEW_NominalVoltage = QtWidgets.QTextEdit()
        self.textEdit_DEW_NominalVoltage.setObjectName("textEdit_DEW_NominalVoltage")
        self.textEdit_DEW_NominalVoltage.setFixedSize(100, 31)
        self.textEdit_DEW_NominalVoltage.setText("230")
        formLayout.addRow("标称电压:", self._make_unit_row(self.textEdit_DEW_NominalVoltage, "V"))

        # 加权类型联动标称电压：自动检测时禁用，选具体类型时启用
        def _on_weighting_type_changed(text):
            self.textEdit_DEW_NominalVoltage.setEnabled(text != "自动检测")
        self.comboBox_DEW_WeightingType.currentTextChanged.connect(_on_weighting_type_changed)
        _on_weighting_type_changed(self.comboBox_DEW_WeightingType.currentText())

        self.textEdit_DEW_ShortFlickerTime = QtWidgets.QTextEdit()
        self.textEdit_DEW_ShortFlickerTime.setObjectName("textEdit_DEW_ShortFlickerTime")
        self.textEdit_DEW_ShortFlickerTime.setFixedSize(100, 31)
        self.textEdit_DEW_ShortFlickerTime.setText("10")
        formLayout.addRow("短时闪变计算时间:", self._make_unit_row(self.textEdit_DEW_ShortFlickerTime, "分钟"))

        self.textEdit_DEW_LongFlickerTime = QtWidgets.QTextEdit()
        self.textEdit_DEW_LongFlickerTime.setObjectName("textEdit_DEW_LongFlickerTime")
        self.textEdit_DEW_LongFlickerTime.setFixedSize(100, 31)
        self.textEdit_DEW_LongFlickerTime.setText("120")
        formLayout.addRow("长时闪变计算时间:", self._make_unit_row(self.textEdit_DEW_LongFlickerTime, "分钟"))

        # 首次闪变间隔（与 WT 模式的 S2 对应）
        self.textEdit_DEW_S2_TIME = QtWidgets.QTextEdit()
        self.textEdit_DEW_S2_TIME.setObjectName("textEdit_DEW_S2_TIME")
        self.textEdit_DEW_S2_TIME.setFixedSize(100, 31)
        self.textEdit_DEW_S2_TIME.setText("5")
        self.comboBox_DEW_S2_TIME = QtWidgets.QComboBox()
        self.comboBox_DEW_S2_TIME.setObjectName("comboBox_DEW_S2_TIME")
        self.comboBox_DEW_S2_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_DEW_S2_TIME.setFixedWidth(120)
        _s2_container = QtWidgets.QWidget()
        _s2_h = QtWidgets.QHBoxLayout(_s2_container)
        _s2_h.setContentsMargins(0, 0, 0, 0)
        _s2_h.setSpacing(4)
        _s2_h.addWidget(self.textEdit_DEW_S2_TIME)
        _s2_h.addWidget(self.comboBox_DEW_S2_TIME)
        _s2_h.addStretch()
        formLayout.addRow("首次闪变间隔:", _s2_container)

        # 每组闪变次数
        self.comboBox_DEW_S2_PER_FLICK_COUNT = QtWidgets.QComboBox()
        self.comboBox_DEW_S2_PER_FLICK_COUNT.setObjectName("comboBox_DEW_S2_PER_FLICK_COUNT")
        self.comboBox_DEW_S2_PER_FLICK_COUNT.addItems(["3", "1", "2"])
        self.comboBox_DEW_S2_PER_FLICK_COUNT.setFixedWidth(120)
        _flick_count_container = QtWidgets.QWidget()
        _fc_h = QtWidgets.QHBoxLayout(_flick_count_container)
        _fc_h.setContentsMargins(0, 0, 0, 0)
        _fc_h.setSpacing(4)
        _fc_h.addWidget(self.comboBox_DEW_S2_PER_FLICK_COUNT)
        _fc_h.addWidget(QtWidgets.QLabel("次"))
        _fc_h.addStretch()
        formLayout.addRow("每组闪变次数:", _flick_count_container)

        self.textEdit_DEW_ShortCircuitPower = QtWidgets.QTextEdit()
        self.textEdit_DEW_ShortCircuitPower.setObjectName("textEdit_DEW_ShortCircuitPower")
        self.textEdit_DEW_ShortCircuitPower.setFixedSize(100, 31)
        self.textEdit_DEW_ShortCircuitPower.setText("50")
        formLayout.addRow("短路视在功率:", self._make_unit_row(self.textEdit_DEW_ShortCircuitPower, "MVA"))

        self.checkBox_DEW_RollingCalc = QtWidgets.QCheckBox("打开滚动计算")
        self.checkBox_DEW_RollingCalc.setChecked(True)
        self.checkBox_DEW_RollingCalc.setObjectName("checkBox_DEW_RollingCalc")
        formLayout.addRow(self.checkBox_DEW_RollingCalc)

        # 测试生效按钮 — 自测用，读取设备XML并应用当前设置
        self.pushButton_DEW_TestApply = QtWidgets.QPushButton("测试生效")
        self.pushButton_DEW_TestApply.setMinimumSize(120, 36)
        self.pushButton_DEW_TestApply.setStyleSheet(
            "QPushButton { color: white; background-color: #059669; border: none; "
            "border-radius: 4px; padding: 6px 14px; font-size: 13px; }"
            "QPushButton:hover { background-color: #047857; }"
        )
        formLayout.addRow("", self.pushButton_DEW_TestApply)

        dew_layout.addWidget(dew_group)
        dew_layout.addStretch()
        self._step2Stacked.addWidget(dew_page)

        # 默认显示 WT3000 页面
        self._step2Stacked.setCurrentIndex(0)

        # 直接加入主 stackedWidget（index 1 = step2）
        self.stackedWidget.addWidget(self._step2Stacked)

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
            # 仅 DC1 默认勾选；2~4 由 step1 联动决定（避免未接 DC2~4 却写入命令）
            cb.setChecked(cb_name == "checkBox_S3_DC1")
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
            cb.setChecked(cb_name == "checkBox_S3_DC1_2")
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
        # 默认须满足：首次间隔+次数×持续+(次数-1)×间隔 ≤ 600s
        # 旧默认 4min+3×15s+2×3min=645s 会触发超限；改为 2min → 525s
        self.textEdit_S3_TIME_2.setText("2")
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
    # Step 4: 判定结果（WT3000 / DEWETRON 双模式）
    # ══════════════════════════════════════════════
    def _build_step4(self):
        self._step4Stacked = QtWidgets.QStackedWidget()

        # ── 页面 0: WT3000 判定设置 ──
        wt_page = QtWidgets.QWidget()
        wt_page.setStyleSheet("background-color: white;")
        wt_layout = QtWidgets.QVBoxLayout(wt_page)
        wt_layout.setContentsMargins(16, 16, 16, 16)
        wt_layout.setSpacing(12)

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
        self.comboBox_S4_WT3000_3.addItems(["保存至本地", "不保存图片", "保存至USB"])
        self.comboBox_S4_WT3000_3.setFixedWidth(120)
        g4Layout.addWidget(self.comboBox_S4_WT3000_3, 0, 4)

        wt_layout.addWidget(self.groupBox_4)
        wt_layout.addStretch()
        self._step4Stacked.addWidget(wt_page)

        # ── 页面 1: DEWETRON 导出设置 ──
        dew_page = QtWidgets.QWidget()
        dew_page.setStyleSheet("background-color: white;")
        dew_layout = QtWidgets.QVBoxLayout(dew_page)
        dew_layout.setContentsMargins(16, 16, 16, 16)
        dew_layout.setSpacing(12)

        dew_group = QtWidgets.QGroupBox()
        dew_group.setTitle("DEWETRON 导出设置")
        dew_group.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        dew_form = QtWidgets.QFormLayout(dew_group)
        dew_form.setSpacing(10)
        dew_form.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S4_DEW = QtWidgets.QCheckBox("step4")
        self.checkBox_S4_DEW.setChecked(True)
        self.checkBox_S4_DEW.setObjectName("checkBox_S4_DEW")
        dew_form.addRow(self.checkBox_S4_DEW)

        # 保留小数位数
        self.spinBox_DEW_DecimalPlaces = QtWidgets.QSpinBox()
        self.spinBox_DEW_DecimalPlaces.setRange(0, 6)
        self.spinBox_DEW_DecimalPlaces.setValue(3)
        self.spinBox_DEW_DecimalPlaces.setFixedWidth(80)
        self.spinBox_DEW_DecimalPlaces.setObjectName("spinBox_DEW_DecimalPlaces")
        dew_form.addRow("保留小数位数:", self.spinBox_DEW_DecimalPlaces)

        # 启用实时波形
        self.checkBox_DEW_RealtimeWaveform = QtWidgets.QCheckBox("启用实时波形显示")
        self.checkBox_DEW_RealtimeWaveform.setChecked(False)
        self.checkBox_DEW_RealtimeWaveform.setObjectName("checkBox_DEW_RealtimeWaveform")
        dew_form.addRow("实时波形:", self.checkBox_DEW_RealtimeWaveform)

        self.checkBox_DEW_ExportAbsTime = QtWidgets.QCheckBox(
            "CSV 增加绝对时间戳列（设备 ABS-TIME）"
        )
        self.checkBox_DEW_ExportAbsTime.setChecked(False)
        self.checkBox_DEW_ExportAbsTime.setObjectName("checkBox_DEW_ExportAbsTime")
        self.checkBox_DEW_ExportAbsTime.setToolTip(
            "导出时在 Time [s] 前增加 Abs Time 列，来自 Oxygen NUMERIC 的 ABS-TIME。"
        )
        dew_form.addRow("绝对时间:", self.checkBox_DEW_ExportAbsTime)

        self.checkBox_DEW_KeepOxygenDmd = QtWidgets.QCheckBox(
            "保留 Oxygen 原始 .dmd 录波到保存目录"
        )
        self.checkBox_DEW_KeepOxygenDmd.setChecked(False)
        self.checkBox_DEW_KeepOxygenDmd.setObjectName("checkBox_DEW_KeepOxygenDmd")
        self.checkBox_DEW_KeepOxygenDmd.setToolTip(
            "试验过程中启动 :STORE 录波；结束后把 .dmd 复制/保留到与 CSV 相同的保存目录。"
        )
        dew_form.addRow("原始录波:", self.checkBox_DEW_KeepOxygenDmd)

        # 字段选择树
        self.treeWidget_DEW_ExportFields = QtWidgets.QTreeWidget()
        self.treeWidget_DEW_ExportFields.setHeaderLabel("导出字段选择")
        self.treeWidget_DEW_ExportFields.setMinimumHeight(300)
        self.treeWidget_DEW_ExportFields.setObjectName("treeWidget_DEW_ExportFields")
        self.treeWidget_DEW_ExportFields.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px;
                font-size: 12px;
                color: #1e293b;
                outline: none;
            }
            QTreeWidget::item {
                padding: 3px 0px;
                margin: 1px 0px;
                border-radius: 3px;
            }
            QTreeWidget::item:selected {
                background-color: #ede9fe;
                color: #5b21b6;
            }
            QTreeWidget::item:hover:!selected {
                background-color: #f8fafc;
            }
            QTreeWidget::item:has-children {
                font-weight: bold;
                color: #334155;
            }
            QTreeWidget::branch {
                background: transparent;
            }
            QTreeWidget::branch:has-children:closed {
                border-image: none;
                image: none;
            }
            QTreeWidget::branch:has-children:open {
                border-image: none;
                image: none;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                padding: 6px 8px;
                font-weight: bold;
                color: #475569;
            }
        """)
        self.treeWidget_DEW_ExportFields.setHeaderHidden(True)
        self.treeWidget_DEW_ExportFields.setRootIsDecorated(True)
        self.treeWidget_DEW_ExportFields.setIndentation(20)
        self.treeWidget_DEW_ExportFields.setAlternatingRowColors(True)
        self._build_export_field_tree(tree_data=None)
        dew_form.addRow("字段选择:", self.treeWidget_DEW_ExportFields)

        dew_layout.addWidget(dew_group)
        dew_layout.addStretch()
        self._step4Stacked.addWidget(dew_page)

        # 默认显示 WT3000 页面
        self._step4Stacked.setCurrentIndex(0)

        self.stackedWidget.addWidget(self._step4Stacked)

    def _build_export_field_tree(self, tree_data=None, checked_fields=None):
        """构建 DEWETRON 导出字段选择树。

        Args:
            tree_data: parse_power_group_tree() 返回的嵌套字典。
                       None 时显示占位提示。
            checked_fields: 需要勾选的字段名集合。None 时全部勾选。
        """
        tree = self.treeWidget_DEW_ExportFields
        tree.clear()

        if not tree_data:
            item = QtWidgets.QTreeWidgetItem(tree, ["请先连接 DEWETRON 设备并切换到德威创模式"])
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
            item.setForeground(0, QtGui.QColor("#94a3b8"))
            return

        # 断开旧信号，避免构建过程中触发联动
        try:
            tree.itemChanged.disconnect(self._on_export_field_item_changed)
        except (TypeError, RuntimeError):
            pass

        check_set = set(checked_fields) if checked_fields is not None else None

        # 类别图标映射
        cat_icons = {
            'Voltage (U)': '⚡',
            'Current (I)': '〰',
            'Active Power (P)': 'P',
            'Reactive Power (Q)': 'Q',
            'Apparent Power (S)': 'S',
            'Power Factor (PF)': 'PF',
            'Energy (W)': 'W',
            'Frequency (F)': 'Hz',
        }

        for category, sub_cats in tree_data.items():
            # 类别节点：带图标 + 紫色背景
            cat_icon = cat_icons.get(category, '•')
            cat_item = QtWidgets.QTreeWidgetItem(tree, [f"  {category}"])
            cat_item.setFlags(cat_item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
            cat_item.setCheckState(0, QtCore.Qt.Checked)
            cat_item.setForeground(0, QtGui.QColor("#5b21b6"))
            cat_item.setBackground(0, QtGui.QColor("#f5f3ff"))
            font = cat_item.font(0)
            font.setBold(True)
            font.setPointSize(10)
            cat_item.setFont(0, font)
            cat_item.setData(0, QtCore.Qt.UserRole, cat_icon)

            for sub_name, channels in sub_cats.items():
                # 子类别节点：蓝色文字
                sub_item = QtWidgets.QTreeWidgetItem(cat_item, [f"    {sub_name}"])
                sub_item.setFlags(sub_item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
                sub_item.setCheckState(0, QtCore.Qt.Checked)
                sub_item.setForeground(0, QtGui.QColor("#1d4ed8"))
                font = sub_item.font(0)
                font.setBold(True)
                sub_item.setFont(0, font)
                sub_item.setData(0, QtCore.Qt.UserRole, f"  {len(channels)} ch")

                for ch_name in channels:
                    # 叶子节点：普通样式
                    ch_item = QtWidgets.QTreeWidgetItem(sub_item, [f"      {ch_name}"])
                    ch_item.setFlags(ch_item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
                    # 构建时直接设好勾选状态
                    if check_set is not None:
                        ch_item.setCheckState(0, QtCore.Qt.Checked if ch_name in check_set else QtCore.Qt.Unchecked)
                    else:
                        ch_item.setCheckState(0, QtCore.Qt.Checked)
                    ch_item.setForeground(0, QtGui.QColor("#475569"))

        tree.expandToDepth(1)
        tree.itemChanged.connect(self._on_export_field_item_changed)

    def refresh_export_field_tree(self, xml_string, checked_fields=None):
        """从设备 XML 动态刷新导出字段树。供 SCPITestWave.py 调用。

        Args:
            xml_string: 设备 XML
            checked_fields: 需要勾选的字段名集合。None 时全部勾选。
        """
        tree_data = parse_power_group_tree(xml_string)
        self._build_export_field_tree(tree_data, checked_fields)

    def get_checked_export_fields(self):
        """获取当前勾选的导出字段列表。

        Returns:
            list: 勾选的叶子节点字段名列表（如 ['U1_tRMS', 'I1_fundRMS', ...]）
        """
        tree = self.treeWidget_DEW_ExportFields
        checked_fields = []

        def _collect_checked(item):
            # 只收集叶子节点（无子节点的节点）
            if item.childCount() == 0:
                if item.checkState(0) == QtCore.Qt.Checked:
                    # 获取字段名（去掉缩进空格）
                    text = item.text(0).strip()
                    checked_fields.append(text)
            else:
                for i in range(item.childCount()):
                    _collect_checked(item.child(i))

        for i in range(tree.topLevelItemCount()):
            _collect_checked(tree.topLevelItem(i))

        return checked_fields

    def set_checked_export_fields(self, fields_list):
        """根据字段名列表勾选树节点。

        Args:
            fields_list: 勾选的叶子节点字段名列表（如 ['U1_tRMS', 'I1_fundRMS', ...]）
        """
        tree = self.treeWidget_DEW_ExportFields
        self._block_tree_signals = True
        try:
            # 先全部取消勾选
            for i in range(tree.topLevelItemCount()):
                cat = tree.topLevelItem(i)
                cat.setCheckState(0, QtCore.Qt.Unchecked)
                for j in range(cat.childCount()):
                    sub = cat.child(j)
                    sub.setCheckState(0, QtCore.Qt.Unchecked)
                    for k in range(sub.childCount()):
                        sub.child(k).setCheckState(0, QtCore.Qt.Unchecked)

            field_set = set(fields_list)
            # 勾选匹配的叶子节点
            for i in range(tree.topLevelItemCount()):
                cat = tree.topLevelItem(i)
                for j in range(cat.childCount()):
                    sub = cat.child(j)
                    for k in range(sub.childCount()):
                        leaf = sub.child(k)
                        leaf_text = leaf.text(0).strip()
                        if leaf_text in field_set:
                            leaf.setCheckState(0, QtCore.Qt.Checked)

            # 更新父节点状态（自底向上）
            for i in range(tree.topLevelItemCount()):
                cat = tree.topLevelItem(i)
                for j in range(cat.childCount()):
                    sub = cat.child(j)
                    sub_checked = sum(1 for k in range(sub.childCount())
                                      if sub.child(k).checkState(0) == QtCore.Qt.Checked)
                    sub_total = sub.childCount()
                    if sub_total > 0:
                        if sub_checked == 0:
                            sub.setCheckState(0, QtCore.Qt.Unchecked)
                        elif sub_checked == sub_total:
                            sub.setCheckState(0, QtCore.Qt.Checked)
                        else:
                            sub.setCheckState(0, QtCore.Qt.PartiallyChecked)
                cat_checked = sum(1 for j in range(cat.childCount())
                                  if cat.child(j).checkState(0) == QtCore.Qt.Checked)
                cat_total = cat.childCount()
                if cat_total > 0:
                    if cat_checked == 0:
                        cat.setCheckState(0, QtCore.Qt.Unchecked)
                    elif cat_checked == cat_total:
                        cat.setCheckState(0, QtCore.Qt.Checked)
                    else:
                        cat.setCheckState(0, QtCore.Qt.PartiallyChecked)
        finally:
            self._block_tree_signals = False

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
            cb.setChecked(cb_name == "checkBox_S5_DC1")
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

    @staticmethod
    def _make_unit_row(widget, unit_text):
        """创建带单位标签的行容器。"""
        container = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(4)
        h.addWidget(widget)
        lbl = QtWidgets.QLabel(unit_text)
        lbl.setStyleSheet("color: #64748b; background: transparent;")
        h.addWidget(lbl)
        h.addStretch()
        return container

    def set_solar_standard(self, standard_id, *, apply_defaults=False):
        """外部（IOT handoff）同步标准；默认不重写已填控件，避免冲掉下发 widgets。"""
        try:
            from utils.iot_flicker_standard import apply_flicker_standard_to_ui

            apply_flicker_standard_to_ui(
                self,
                standard_id,
                force=True,
                apply_defaults=bool(apply_defaults),
            )
        except Exception:
            sid = str(standard_id or "thai").strip() or "thai"
            self._solar_standard = sid

    def _on_solar_standard_changed(self, index):
        """用户手动切换国家标准：回填该标准默认工况（不改 WT/德威创模式）。"""
        sid = self.comboBox_SolarStandard.itemData(index)
        if sid is None:
            sid = "thai"
        # 泰国且首次等同现行控件默认：仍走 apply，保证与 profiles 一致
        self.set_solar_standard(str(sid), apply_defaults=True)

    def _on_mode_changed(self, button, checked):
        """模式切换回调（WT3000闪变 / 德威创模式）。切换 step2 和 step4 内容。"""
        if not checked:
            return
        if button == self.radio_wt3000:
            self._mode = 'wt3000'
            self._step2Stacked.setCurrentIndex(0)
            self._step4Stacked.setCurrentIndex(0)
            # WT 模式隐藏数据查看按钮
            if hasattr(self, 'pushButton_DEW_DataViewer'):
                self.pushButton_DEW_DataViewer.hide()
        elif button == self.radio_dewetron:
            self._mode = 'dewetron'
            self._step2Stacked.setCurrentIndex(1)
            self._step4Stacked.setCurrentIndex(1)
            # 德威创模式显示数据查看按钮
            if hasattr(self, 'pushButton_DEW_DataViewer'):
                self.pushButton_DEW_DataViewer.show()

    def _on_export_field_item_changed(self, item, column):
        """字段树复选框变化回调（不做任何联动，勾选啥就是啥）。"""
        pass

    def retranslateUi(self, Dialog_thaiguodianyashanbian):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaiguodianyashanbian.setWindowTitle(_translate("Dialog_thaiguodianyashanbian", "电压闪变项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaiguodianyashanbian", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaiguodianyashanbian", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaiguodianyashanbian", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaiguodianyashanbian", "提交"))
