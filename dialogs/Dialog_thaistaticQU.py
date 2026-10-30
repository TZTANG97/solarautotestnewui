# -*- coding: utf-8 -*-
# 静态QU项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.dewetron_autotest_panel import AnalyzerModeSection
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)


class Ui_Dialog_thaiStaticQU(object):
    def setupUi(self, Dialog_thaiStaticQU):
        Dialog_thaiStaticQU.setObjectName("Dialog_thaiStaticQU")
        Dialog_thaiStaticQU.resize(1597, 828)
        Dialog_thaiStaticQU.setMinimumSize(QtCore.QSize(1400, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaiStaticQU.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaiStaticQU)
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
            from utils.iot_staticqu_standard import list_staticqu_standard_options

            for opt in list_staticqu_standard_options():
                self.comboBox_SolarStandard.addItem(str(opt["label"]), str(opt["id"]))
        except Exception:
            self.comboBox_SolarStandard.addItem("泰国 PEA/MEA（现行）", "thai")
        self.comboBox_SolarStandard.setCurrentIndex(0)
        self._solar_standard = "thai"
        self.comboBox_SolarStandard.currentIndexChanged.connect(self._on_solar_standard_changed)
        topLayout.addWidget(self.comboBox_SolarStandard)

        topLayout.addStretch()

        self._step_labels = []
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ 电压阶梯", "④ QU测试2", "⑤ QU测试3", "⑥ QU测试4", "⑦ 判定结果", "⑧ 关机设置"]
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
        self._build_step1()
        self._build_step2()
        self._build_step3()
        self._build_step4()
        self._build_step5()
        self._build_step6()
        self._build_step7()
        self._build_step8()

        # 默认显示第一页
        self._switch_step(0)

        # DC 联动
        self._connect_dc_linkage()

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaiStaticQU)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaiStaticQU)


    def set_solar_standard(self, standard_id, *, apply_defaults=False):
        try:
            from utils.iot_staticqu_standard import apply_staticqu_standard_to_ui

            apply_staticqu_standard_to_ui(
                self,
                standard_id,
                force=True,
                apply_defaults=bool(apply_defaults),
            )
        except Exception:
            self._solar_standard = str(standard_id or "thai").strip() or "thai"

    def _on_solar_standard_changed(self, index):
        sid = self.comboBox_SolarStandard.itemData(index)
        if sid is None:
            sid = "thai"
        self.set_solar_standard(str(sid), apply_defaults=True)


    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 10px; font-size: 11px; font-weight: bold; color: #7c3aed;
                        border-bottom: 3px solid #8b5cf6; border-radius: 0;
                        background-color: #f3e8ff;
                    }
                """)
            else:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 10px; font-size: 11px; color: #64748b;
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
    # Step 1: AC/DC 电源 + 时序设置
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
        g0Layout = QtWidgets.QGridLayout(self.groupBox)
        g0Layout.setSpacing(8)
        g0Layout.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        g0Layout.addWidget(self.checkBox_S1, 0, 0, 1, 2)

        self.label_3 = QtWidgets.QLabel("交流电源")
        self.label_3.setObjectName("label_3")
        g0Layout.addWidget(self.label_3, 0, 2)
        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(100)
        g0Layout.addWidget(self.comboBox_S1_AC, 0, 3)

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        g0Layout.addWidget(self.label_4, 0, 4)
        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(80, 31)
        g0Layout.addWidget(self.textEdit_S1_AC_VOLT, 0, 5)
        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        g0Layout.addWidget(self.label_5, 0, 6)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        g0Layout.addWidget(self.label_113, 0, 7)
        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(80, 31)
        g0Layout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 8)
        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        g0Layout.addWidget(self.label_107, 0, 9)

        # Row 1
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(100)
        g0Layout.addWidget(self.comboBox_S1_AC_2, 1, 3)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        g0Layout.addWidget(self.label_123, 1, 4)
        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(80, 31)
        g0Layout.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 5)
        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        g0Layout.addWidget(self.label_102, 1, 6)

        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        g0Layout.addWidget(self.label_19, 1, 7)
        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(80, 31)
        g0Layout.addWidget(self.textEdit_S1_AC_FR, 1, 8)
        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        g0Layout.addWidget(self.label_18, 1, 9)

        layout.addWidget(self.groupBox)

        # ── DC 电源组 (4 channels) ──
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流电源设置")
        self.groupBox_2.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        g2Layout = QtWidgets.QGridLayout(self.groupBox_2)
        g2Layout.setSpacing(6)
        g2Layout.setContentsMargins(12, 20, 12, 12)

        # Header：单位写在表头（避免 V/A/% 挤到右侧空白列）
        headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
        header_labels = ["label_13", "label_120", "label_108", "label_118", "label_109", "label_119", "label_129"]
        for c, (h, hname) in enumerate(zip(headers, header_labels)):
            lbl = QtWidgets.QLabel(h)
            lbl.setObjectName(hname)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g2Layout.addWidget(lbl, 0, c)

        # DC channels config
        dc_channels = [
            (1, "checkBox_S1_DC1", "直流电源1", "comboBox_S1_DC1",
             "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF",
             "label_14", "label_53", "label_59", "label_52", "label_104"),
            (2, "checkBox_S1_DC2", "直流电源2", "comboBox_S1_DC2",
             "textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF",
             "label_17", "label_57", "label_51", "label_128", "label_116"),
            (3, "checkBox_S1_DC3", "直流电源3", "comboBox_S1_DC3",
             "textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF",
             "label_54", "label_58", "label_119", "label_105", "label_100"),
            (4, "checkBox_S1_DC4", "直流电源4", "comboBox_S1_DC4",
             "textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF",
             "label_54", "label_125", "label_111", "label_114", "label_100"),
        ]

        for r, (ch, cb_name, cb_text, combo_name,
                v_name, c_name, voc_name, isc_name, pf_name,
                lbl_v, lbl_c, lbl_voc, lbl_isc, lbl_pf) in enumerate(dc_channels, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g2Layout.addWidget(cb, r, 0)
            setattr(self, cb_name, cb)

            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["开启", "关闭"])
            combo.setFixedWidth(90)
            g2Layout.addWidget(combo, r, 1)
            setattr(self, combo_name, combo)

            for c, name in enumerate([v_name, c_name, voc_name, isc_name, pf_name], start=2):
                te = QtWidgets.QTextEdit()
                te.setObjectName(name)
                te.setFixedSize(80, 28)
                if hasattr(te, "setTabChangesFocus"):
                    te.setTabChangesFocus(True)
                g2Layout.addWidget(te, r, c)
                setattr(self, name, te)

        # 兼容旧 Open/Save 可能引用的单位 label objectName（不占布局）
        for lbl_name, unit in (
            ("label_110", "V"), ("label_56", "A"), ("label_55", "%"),
            ("label_15", "V"), ("label_112", "%"),
            ("label_127", "V"), ("label_124", "A"), ("label_115", "%"),
            ("label_126", "V"), ("label_117", "%"),
        ):
            if not hasattr(self, lbl_name):
                _lbl = QtWidgets.QLabel(unit)
                _lbl.setObjectName(lbl_name)
                _lbl.hide()
                setattr(self, lbl_name, _lbl)

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
        self.textEdit_S1_ACWaitTIME.setText("5")
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
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 3: QU 趋势1
    # ══════════════════════════════════════════════

    def _build_step3(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 电压 LIST：与 WT 文件名列表、Cos 功率阶梯同一写法（逗号分隔）
        # 无功不填：机侧 Q(U) 随电压变化，由 WT 实测
        # 先升到 115% 再降到 85%（经 100%），适合 Q(U) 连续扫
        _DEFAULT_U_LIST = (
            "100,103,105,106,107,108,110,112,115,"
            "112,110,108,107,106,105,103,100,"
            "97,94,93,90,87,85"
        )
        ladder_grp = QtWidgets.QGroupBox("Q(U) 电压 list（静态设定精度 / 连续录 1 条 QU_curve）")
        ladder_grp.setStyleSheet(
            "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; "
            "padding-top: 8px; font-weight: bold; }"
        )
        ladder_layout = QtWidgets.QGridLayout(ladder_grp)
        ladder_layout.setSpacing(8)
        ladder_layout.setContentsMargins(12, 20, 12, 12)

        ladder_layout.addWidget(QtWidgets.QLabel("Un基准(V)："), 0, 0)
        self.textEdit_VoltageLadder_Un = QtWidgets.QTextEdit()
        self.textEdit_VoltageLadder_Un.setObjectName("textEdit_VoltageLadder_Un")
        self.textEdit_VoltageLadder_Un.setFixedSize(80, 28)
        self.textEdit_VoltageLadder_Un.setText("230")
        ladder_layout.addWidget(self.textEdit_VoltageLadder_Un, 0, 1)
        ladder_layout.addWidget(QtWidgets.QLabel("频率(Hz)："), 0, 2)
        self.textEdit_VoltageLadder_FR = QtWidgets.QTextEdit()
        self.textEdit_VoltageLadder_FR.setObjectName("textEdit_VoltageLadder_FR")
        self.textEdit_VoltageLadder_FR.setFixedSize(80, 28)
        self.textEdit_VoltageLadder_FR.setText("50")
        ladder_layout.addWidget(self.textEdit_VoltageLadder_FR, 0, 3)

        ladder_layout.addWidget(QtWidgets.QLabel("电压Un%(list)："), 1, 0)
        from components.comma_segment_edit import CommaSegmentEdit
        self.textEdit_VoltageLadder = CommaSegmentEdit(value_header="电压 Un%", unit="%")
        self.textEdit_VoltageLadder.setObjectName("textEdit_VoltageLadder")
        self.textEdit_VoltageLadder.setPlaceholderText("Un%")
        self.textEdit_VoltageLadder.setText(_DEFAULT_U_LIST)
        self.textEdit_VoltageLadder.setPlaceholderText(
            "先升再降取滞环，如 100…115…85；连续录 1 条 QU_curve"
        )
        ladder_layout.addWidget(self.textEdit_VoltageLadder, 1, 1, 1, 3)

        ladder_layout.addWidget(QtWidgets.QLabel("每点驻留："), 2, 0)
        self.textEdit_VoltageLadder_TIME = QtWidgets.QTextEdit()
        self.textEdit_VoltageLadder_TIME.setObjectName("textEdit_VoltageLadder_TIME")
        self.textEdit_VoltageLadder_TIME.setFixedSize(80, 28)
        self.textEdit_VoltageLadder_TIME.setText("1")
        self.textEdit_VoltageLadder_TIME.setToolTip("每个 Un% 保持时间；WT 全程连续录，不停表")
        ladder_layout.addWidget(self.textEdit_VoltageLadder_TIME, 2, 1)
        self.comboBox_VoltageLadder_TIME = QtWidgets.QComboBox()
        self.comboBox_VoltageLadder_TIME.setObjectName("comboBox_VoltageLadder_TIME")
        self.comboBox_VoltageLadder_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_VoltageLadder_TIME.setCurrentText("分钟")
        self.comboBox_VoltageLadder_TIME.setFixedWidth(80)
        ladder_layout.addWidget(self.comboBox_VoltageLadder_TIME, 2, 2)
        tip = QtWidgets.QLabel(
            "静态设定精度：先升后降取滞环，WT 连续录 1 条 QU_curve（分析时可按电压段取稳态）。"
            "动态响应曲线用菜单「动态QU」→ QU_dyn_curve。Pn=100% 由步骤① DC 保持。"
        )
        tip.setStyleSheet("color: #64748b; font-weight: normal; font-size: 11px;")
        tip.setWordWrap(True)
        ladder_layout.addWidget(tip, 3, 0, 1, 4)
        layout.addWidget(ladder_grp)

        legacy_tip = QtWidgets.QLabel("下方为旧「等步长」模式：仅当上方电压 list 为空时才使用")
        legacy_tip.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(legacy_tip)

        self._build_qu_trend_page(
            layout, "groupBox_3", "QU 趋势1 设置（等步长备用）",
            "checkBox_S3", "step3", False,
            "label_20", "交流电源",
            "label_133", "V", "textEdit_S3_AC_VOLT", "230",
            "label_22", "交流电压趋势",
            "comboBox_S3_AC_Trend", ["下降", "上升"],
            "label_36", "电压变动区间",
            "textEdit_S3_AC_Range_S", "1",
            "label", "~",
            "textEdit_S3_AC_Range_E", "0.91",
            "label_60", "电压变动幅度",
            "textEdit_S3_AC_Step", "0.01",
            "label_61", "电压变动点数",
            "textEdit_S3_AC_Range_Point", "10",
            "label_37", "频率",
            "textEdit_S3_AC_FR", "50",
            "label_34", "Hz",
            "label_23", "数据采集",
            "textEdit_S3_TIME", "2",
            "comboBox_S3_TIME", ["分钟", "秒", "毫秒"],
        )

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 4: QU 趋势2
    # ══════════════════════════════════════════════
    def _build_step4(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._build_qu_trend_page(
            layout, "groupBox_6", "QU 趋势2 设置",
            "checkBox_S4", "step4", False,
            "label_21", "交流电源",
            "label_134", "V", "textEdit_S4_AC_VOLT", "230",
            "label_24", "交流电压趋势",
            "comboBox_S4_AC_Trend", ["上升", "下降"],
            "label_39", "电压变动区间",
            "textEdit_S4_AC_Range_S", "0.9",
            "label_2", "~",
            "textEdit_S4_AC_Range_E", "0.99",
            "label_62", "电压变动幅度",
            "textEdit_S4_AC_Step", "0.01",
            "label_63", "电压变动点数",
            "textEdit_S4_AC_Range_Point", "10",
            "label_38", "频率",
            "textEdit_S4_AC_FR", "50",
            "label_35", "Hz",
            "label_25", "数据采集",
            "textEdit_S4_TIME", "2",
            "comboBox_S4_TIME", ["分钟", "秒", "毫秒"],
        )

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 5: QU 趋势3
    # ══════════════════════════════════════════════
    def _build_step5(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._build_qu_trend_page(
            layout, "groupBox_7", "QU 趋势3 设置",
            "checkBox_S5", "step5", False,
            "label_27", "交流电源",
            "label_135", "V", "textEdit_S5_AC_VOLT", "230",
            "label_26", "交流电压趋势",
            "comboBox_S5_AC_Trend", ["上升", "下降"],
            "label_42", "电压变动区间",
            "textEdit_S5_AC_Range_S", "1",
            "label_6", "~",
            "textEdit_S5_AC_Range_E", "1.09",
            "label_64", "电压变动幅度",
            "textEdit_S5_AC_Step", "0.01",
            "label_65", "电压变动点数",
            "textEdit_S5_AC_Range_Point", "10",
            "label_41", "频率",
            "textEdit_S5_AC_FR", "50",
            "label_40", "Hz",
            "label_28", "数据采集",
            "textEdit_S5_TIME", "2",
            "comboBox_S5_TIME", ["分钟", "秒", "毫秒"],
        )

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 6: QU 趋势4
    # ══════════════════════════════════════════════
    def _build_step6(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._build_qu_trend_page(
            layout, "groupBox_8", "QU 趋势4 设置",
            "checkBox_S6", "step6", False,
            "label_30", "交流电源",
            "label_136", "V", "textEdit_S6_AC_VOLT", "230",
            "label_29", "交流电压趋势",
            "comboBox_S6_AC_Trend", ["下降", "上升"],
            "label_45", "电压变动区间",
            "textEdit_S6_AC_Range_S", "1.1",
            "label_7", "~",
            "textEdit_S6_AC_Range_E", "1",
            "label_66", "电压变动幅度",
            "textEdit_S6_AC_Step", "0.01",
            "label_67", "电压变动点数",
            "textEdit_S6_AC_Range_Point", "11",
            "label_44", "频率",
            "textEdit_S6_AC_FR", "50",
            "label_43", "Hz",
            "label_31", "数据采集",
            "textEdit_S6_TIME", "2",
            "comboBox_S6_TIME", ["分钟", "秒", "毫秒"],
        )

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 7: QU 趋势5
    # ══════════════════════════════════════════════
    def _build_step7(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._build_qu_trend_page(
            layout, "groupBox_9", "QU 趋势5 设置",
            "checkBox_S7", "step7", False,
            "label_46", "交流电源",
            "label_137", "V", "textEdit_S7_AC_VOLT", "230",
            "label_47", "交流电压趋势",
            "comboBox_S7_AC_Trend", ["上升", "下降"],
            "label_48", "电压变动区间",
            "textEdit_S7_AC_Range_S", "1",
            "label_9", "~",
            "textEdit_S7_AC_Range_E", "1.05",
            "label_49", "电压变动幅度",
            "textEdit_S7_AC_Step", "0.01",
            "label_50", "电压变动点数",
            "textEdit_S7_AC_Range_Point", "10",
            "label_68", "频率",
            "textEdit_S7_AC_FR", "50",
            "label_69", "Hz",
            "label_70", "数据采集",
            "textEdit_S7_TIME", "2",
            "comboBox_S7_TIME", ["分钟", "秒", "毫秒"],
        )

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 8: 关机设置
    # ══════════════════════════════════════════════
    def _build_step8(self):
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

        # AC power shutdown
        self.label_8 = QtWidgets.QLabel("交流电源")
        self.label_8.setObjectName("label_8")
        g11Layout.addWidget(self.label_8, 0, 1)
        self.comboBox_S_End_AC = QtWidgets.QComboBox()
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItems(["关闭", "开启"])
        self.comboBox_S_End_AC.setCurrentText("关闭")
        self.comboBox_S_End_AC.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_AC, 0, 2)

        # DC1 shutdown（可与 step1 解耦：原载/通用直流源可只在关机关输出）
        self.checkBox_S_End_DC1 = QtWidgets.QCheckBox("直流电源1")
        self.checkBox_S_End_DC1.setChecked(True)
        self.checkBox_S_End_DC1.setObjectName("checkBox_S_End_DC1")
        g11Layout.addWidget(self.checkBox_S_End_DC1, 1, 0)
        self.comboBox_S_End_DC1 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC1.setObjectName("comboBox_S_End_DC1")
        self.comboBox_S_End_DC1.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC1.setCurrentText("关闭")
        self.comboBox_S_End_DC1.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC1, 1, 1)

        # DC2 shutdown
        self.checkBox_S_End_DC2 = QtWidgets.QCheckBox("直流电源2")
        self.checkBox_S_End_DC2.setChecked(False)
        self.checkBox_S_End_DC2.setObjectName("checkBox_S_End_DC2")
        g11Layout.addWidget(self.checkBox_S_End_DC2, 1, 2)
        self.comboBox_S_End_DC2 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC2.setObjectName("comboBox_S_End_DC2")
        self.comboBox_S_End_DC2.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC2.setCurrentText("关闭")
        self.comboBox_S_End_DC2.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC2, 1, 3)

        # DC3 shutdown
        self.checkBox_S_End_DC3 = QtWidgets.QCheckBox("直流电源3")
        self.checkBox_S_End_DC3.setChecked(False)
        self.checkBox_S_End_DC3.setObjectName("checkBox_S_End_DC3")
        g11Layout.addWidget(self.checkBox_S_End_DC3, 2, 0)
        self.comboBox_S_End_DC3 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC3.setObjectName("comboBox_S_End_DC3")
        self.comboBox_S_End_DC3.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC3.setCurrentText("关闭")
        self.comboBox_S_End_DC3.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC3, 2, 1)

        # DC4 shutdown
        self.checkBox_S_End_DC4 = QtWidgets.QCheckBox("直流电源4")
        self.checkBox_S_End_DC4.setChecked(False)
        self.checkBox_S_End_DC4.setObjectName("checkBox_S_End_DC4")
        g11Layout.addWidget(self.checkBox_S_End_DC4, 2, 2)
        self.comboBox_S_End_DC4 = QtWidgets.QComboBox()
        self.comboBox_S_End_DC4.setObjectName("comboBox_S_End_DC4")
        self.comboBox_S_End_DC4.addItems(["关闭", "开启"])
        self.comboBox_S_End_DC4.setCurrentText("关闭")
        self.comboBox_S_End_DC4.setFixedWidth(120)
        g11Layout.addWidget(self.comboBox_S_End_DC4, 2, 3)

        tip_end = QtWidgets.QLabel(
            "提示：① 可不勾 DC（原载/通用直流源手动供电）；此处仍可勾选通道，"
            "结束时先关 DC 再关 AC。仅勾实际已连接的通道。"
        )
        tip_end.setWordWrap(True)
        tip_end.setStyleSheet("color: #64748b; font-size: 11px; font-weight: normal;")
        g11Layout.addWidget(tip_end, 3, 0, 1, 4)

        layout.addWidget(self.groupBox_11)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # QU 趋势页面构建辅助方法
    # ══════════════════════════════════════════════
    def _build_qu_trend_page(self, layout, gb_name, gb_title,
                              cb_name, cb_text, cb_checked,
                              ac_label_name, ac_label_text,
                              volt_unit_name, volt_unit_text, volt_edit_name, volt_default,
                              trend_label_name, trend_label_text,
                              trend_combo_name, trend_combo_items,
                              range_label_name, range_label_text,
                              range_s_name, range_s_default,
                              tilde_name, tilde_text,
                              range_e_name, range_e_default,
                              step_label_name, step_label_text,
                              step_edit_name, step_default,
                              point_label_name, point_label_text,
                              point_edit_name, point_default,
                              fr_label_name, fr_label_text,
                              fr_edit_name, fr_default,
                              hz_label_name, hz_label_text,
                             采_label_name, 采_label_text,
                              time_edit_name, time_default,
                              time_combo_name, time_combo_items):
        """Build a QU trend settings page (steps 3-7)."""
        groupBox = QtWidgets.QGroupBox()
        groupBox.setObjectName(gb_name)
        groupBox.setTitle(gb_title)
        groupBox.setStyleSheet("QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }")
        gLayout = QtWidgets.QGridLayout(groupBox)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        # Row 0: checkbox + 交流电源 + V + voltage + 交流电压趋势 + trend combo
        cb = QtWidgets.QCheckBox(cb_text)
        cb.setChecked(cb_checked)
        cb.setObjectName(cb_name)
        gLayout.addWidget(cb, 0, 0)
        setattr(self, cb_name, cb)

        lbl_ac = QtWidgets.QLabel(ac_label_text)
        lbl_ac.setObjectName(ac_label_name)
        gLayout.addWidget(lbl_ac, 0, 1)
        setattr(self, ac_label_name, lbl_ac)

        lbl_v = QtWidgets.QLabel(volt_unit_text)
        lbl_v.setObjectName(volt_unit_name)
        gLayout.addWidget(lbl_v, 0, 2)
        setattr(self, volt_unit_name, lbl_v)

        te_volt = QtWidgets.QTextEdit()
        te_volt.setObjectName(volt_edit_name)
        te_volt.setFixedSize(80, 31)
        te_volt.setText(volt_default)
        gLayout.addWidget(te_volt, 0, 3)
        setattr(self, volt_edit_name, te_volt)

        lbl_trend = QtWidgets.QLabel(trend_label_text)
        lbl_trend.setObjectName(trend_label_name)
        gLayout.addWidget(lbl_trend, 0, 4)
        setattr(self, trend_label_name, lbl_trend)

        combo_trend = QtWidgets.QComboBox()
        combo_trend.setObjectName(trend_combo_name)
        combo_trend.addItems(trend_combo_items)
        combo_trend.setFixedWidth(100)
        gLayout.addWidget(combo_trend, 0, 5)
        setattr(self, trend_combo_name, combo_trend)

        # Row 1: 电压变动区间 + range_s ~ range_e + 电压变动幅度 + step + 电压变动点数 + point
        lbl_range = QtWidgets.QLabel(range_label_text)
        lbl_range.setObjectName(range_label_name)
        gLayout.addWidget(lbl_range, 1, 0, 1, 2)
        setattr(self, range_label_name, lbl_range)

        te_rs = QtWidgets.QTextEdit()
        te_rs.setObjectName(range_s_name)
        te_rs.setFixedSize(80, 31)
        te_rs.setText(range_s_default)
        gLayout.addWidget(te_rs, 1, 2)
        setattr(self, range_s_name, te_rs)

        lbl_tilde = QtWidgets.QLabel(tilde_text)
        lbl_tilde.setObjectName(tilde_name)
        font_tilde = QtGui.QFont()
        font_tilde.setFamily("Arial")
        font_tilde.setPointSize(18)
        font_tilde.setBold(True)
        lbl_tilde.setFont(font_tilde)
        lbl_tilde.setAlignment(QtCore.Qt.AlignCenter)
        gLayout.addWidget(lbl_tilde, 1, 3)
        setattr(self, tilde_name, lbl_tilde)

        te_re = QtWidgets.QTextEdit()
        te_re.setObjectName(range_e_name)
        te_re.setFixedSize(80, 31)
        te_re.setText(range_e_default)
        gLayout.addWidget(te_re, 1, 4)
        setattr(self, range_e_name, te_re)

        lbl_step = QtWidgets.QLabel(step_label_text)
        lbl_step.setObjectName(step_label_name)
        gLayout.addWidget(lbl_step, 1, 5, 1, 2)
        setattr(self, step_label_name, lbl_step)

        te_step = QtWidgets.QTextEdit()
        te_step.setObjectName(step_edit_name)
        te_step.setFixedSize(80, 31)
        te_step.setText(step_default)
        gLayout.addWidget(te_step, 1, 7)
        setattr(self, step_edit_name, te_step)

        lbl_point = QtWidgets.QLabel(point_label_text)
        lbl_point.setObjectName(point_label_name)
        gLayout.addWidget(lbl_point, 1, 8)
        setattr(self, point_label_name, lbl_point)

        te_point = QtWidgets.QTextEdit()
        te_point.setObjectName(point_edit_name)
        te_point.setFixedSize(80, 31)
        te_point.setText(point_default)
        gLayout.addWidget(te_point, 1, 9)
        setattr(self, point_edit_name, te_point)

        # Row 2: 频率 + FR + Hz + 数据采集 + TIME + TIME_combo
        lbl_fr = QtWidgets.QLabel(fr_label_text)
        lbl_fr.setObjectName(fr_label_name)
        gLayout.addWidget(lbl_fr, 2, 0)
        setattr(self, fr_label_name, lbl_fr)

        te_fr = QtWidgets.QTextEdit()
        te_fr.setObjectName(fr_edit_name)
        te_fr.setFixedSize(80, 31)
        te_fr.setText(fr_default)
        gLayout.addWidget(te_fr, 2, 1)
        setattr(self, fr_edit_name, te_fr)

        lbl_hz = QtWidgets.QLabel(hz_label_text)
        lbl_hz.setObjectName(hz_label_name)
        gLayout.addWidget(lbl_hz, 2, 2)
        setattr(self, hz_label_name, lbl_hz)

        lbl_采 = QtWidgets.QLabel(采_label_text)
        lbl_采.setObjectName(采_label_name)
        gLayout.addWidget(lbl_采, 2, 3)
        setattr(self, 采_label_name, lbl_采)

        te_time = QtWidgets.QTextEdit()
        te_time.setObjectName(time_edit_name)
        te_time.setFixedSize(80, 31)
        te_time.setText(time_default)
        gLayout.addWidget(te_time, 2, 4)
        setattr(self, time_edit_name, te_time)

        combo_time = QtWidgets.QComboBox()
        combo_time.setObjectName(time_combo_name)
        combo_time.addItems(time_combo_items)
        combo_time.setFixedWidth(120)
        gLayout.addWidget(combo_time, 2, 5)
        setattr(self, time_combo_name, combo_time)

        layout.addWidget(groupBox)
        layout.addStretch()

    def _connect_dc_linkage(self):
        """关机步骤 DC：仅随 step_last 启用，不再强制依赖 step1 勾选。

        原载/通用直流源常在①不勾 DC（避免 STC），但仍需在⑧关输出。
        """
        end_dcs = [self.checkBox_S_End_DC1, self.checkBox_S_End_DC2,
                   self.checkBox_S_End_DC3, self.checkBox_S_End_DC4]
        end_combos = [self.comboBox_S_End_DC1, self.comboBox_S_End_DC2,
                      self.comboBox_S_End_DC3, self.comboBox_S_End_DC4]

        def _update_end_dc(_checked=None):
            step_on = self.checkBox_S_End.isChecked()
            for i in range(4):
                end_dcs[i].setEnabled(step_on)
                end_combos[i].setEnabled(step_on)
                # 不因 step1 取消勾选而强制改 checked，保留用户关机意图

        self.checkBox_S_End.toggled.connect(_update_end_dc)
        _update_end_dc()

    def retranslateUi(self, Dialog_thaiStaticQU):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaiStaticQU.setWindowTitle(_translate("Dialog_thaiStaticQU", "静态QU项目配置"))
        self.pushButton_Send.setText(_translate("Dialog_thaiStaticQU", "提交"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaiStaticQU", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaiStaticQU", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaiStaticQU", "读取设定"))
