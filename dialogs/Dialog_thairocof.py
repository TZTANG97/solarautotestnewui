# -*- coding: utf-8 -*-
# ROCOF保护项目配置界面 - 现代化步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)
from components.dewetron_autotest_panel import AnalyzerModeSection


_STEP_TITLES = [
    "① AC/DC 电源",
    "② 功率分析仪",
    "③ ROCOF设置",
    "④ 备用",
    "⑤ 关机设置",
]

_GB_STYLE = (
    "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px;"
    " padding-top: 8px; font-weight: bold; }"
)


class Ui_Dialog_thairocof(object):
    """ROCOF保护项目配置对话框 - 现代化 UI 布局"""

    # ------------------------------------------------------------------ #
    #  setupUi
    # ------------------------------------------------------------------ #
    def setupUi(self, Dialog_thairocof):
        Dialog_thairocof.setObjectName(
            "Dialog_thairocof",
        )
        Dialog_thairocof.resize(1400, 900)
        Dialog_thairocof.setMinimumSize(
            QtCore.QSize(1200, 750),
        )
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(".\\ui_files\\logo.jpg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On,
        )
        Dialog_thairocof.setWindowIcon(icon)

        # === 主布局（上下结构） ===
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thairocof)
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
            from utils.iot_rocof_standard import list_rocof_standard_options

            for opt in list_rocof_standard_options():
                self.comboBox_SolarStandard.addItem(str(opt["label"]), str(opt["id"]))
        except Exception:
            self.comboBox_SolarStandard.addItem("泰国 PEA/MEA（现行）", "thai")
        self.comboBox_SolarStandard.setCurrentIndex(0)
        self._solar_standard = "thai"
        self.comboBox_SolarStandard.currentIndexChanged.connect(self._on_solar_standard_changed)
        topLayout.addWidget(self.comboBox_SolarStandard)

        topLayout.addStretch()

        self._step_labels = []
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ ROCOF设置", "④ 关机设置"]
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
        self._build_step_page_ac_dc()       # Page 0  ① AC/DC 电源
        self._build_step_page_wt()          # Page 1  ② 功率分析仪
        self._build_rocof_steps()          # Page 2  ③ ROCOF设置
        self._build_step_page_shutdown()    # Page 3  ④ 关机设置

        # 保持 _freq_adapt_band_rows 以兼容旧代码
        self._freq_adapt_band_rows = []
        for _i in range(9):
            self._freq_adapt_band_rows.append({
                "sn_guopin": 3 + _i,
                "sn_qianpin": 12 + _i,
            })

        # ── DC 联动（step1 → 关机步骤） ──
        self._connect_dc_linkage()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thairocof)
        QtCore.QMetaObject.connectSlotsByName(
            Dialog_thairocof,
        )

    # ------------------------------------------------------------------ #
    #  _switch_step
    # ------------------------------------------------------------------ #

    def set_solar_standard(self, standard_id, *, apply_defaults=False):
        try:
            from utils.iot_rocof_standard import apply_rocof_standard_to_ui

            apply_rocof_standard_to_ui(
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
        """切换步骤页面并更新指示器样式。"""
        self.stackedWidget.setCurrentIndex(index)
        for _i, _lbl in enumerate(self._step_labels):
            if _i == index:
                _lbl.setStyleSheet("""
                    QLabel {
                        padding: 3px 5px; font-size: 10px;
                        font-weight: bold; color: #7c3aed;
                        border-bottom: 2px solid #8b5cf6;
                        border-radius: 0;
                        background-color: #f3e8ff;
                    }
                """)
            else:
                _lbl.setStyleSheet("""
                    QLabel {
                        padding: 3px 5px; font-size: 10px;
                        color: #64748b;
                        border-bottom: 2px solid transparent;
                        border-radius: 0; background: transparent;
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

    # ================================================================ #
    #  Page 0:  AC / DC 电源 (Step 1)
    # ================================================================ #
    def _build_step_page_ac_dc(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── 交流电源组 (groupBox) ──
        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("交流电源设置")
        self.groupBox.setStyleSheet(_GB_STYLE)
        acG = QtWidgets.QGridLayout(self.groupBox)
        acG.setSpacing(8)
        acG.setContentsMargins(12, 20, 12, 12)

        # Row 0: checkBox_S1 + 交流电源
        self.checkBox_S1 = QtWidgets.QCheckBox("step1")
        self.checkBox_S1.setChecked(True)
        self.checkBox_S1.setObjectName("checkBox_S1")
        acG.addWidget(self.checkBox_S1, 0, 0)

        self.label_3 = QtWidgets.QLabel("交流电源")
        self.label_3.setObjectName("label_3")
        acG.addWidget(self.label_3, 0, 1)

        # 交流电压1
        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        acG.addWidget(self.label_4, 1, 0)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(100)
        acG.addWidget(self.comboBox_S1_AC, 1, 1)

        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(80, 28)
        acG.addWidget(self.textEdit_S1_AC_VOLT, 1, 2)

        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        acG.addWidget(self.label_5, 1, 3)

        # 交流电压2
        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        acG.addWidget(self.label_113, 1, 4)

        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(80, 28)
        acG.addWidget(self.textEdit_S1_AC_VOLT_2, 1, 5)

        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        acG.addWidget(self.label_107, 1, 6)

        # 交流电压3
        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        acG.addWidget(self.label_123, 2, 0)

        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(80, 28)
        acG.addWidget(self.textEdit_S1_AC_VOLT_3, 2, 1)

        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        acG.addWidget(self.label_102, 2, 2)

        # 频率
        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        acG.addWidget(self.label_19, 2, 4)

        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(80, 28)
        acG.addWidget(self.textEdit_S1_AC_FR, 2, 5)

        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        acG.addWidget(self.label_18, 2, 6)

        # 单相/三相
        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(100)
        acG.addWidget(self.comboBox_S1_AC_2, 3, 1)

        layout.addWidget(self.groupBox)

        # ── 直流电源组 (groupBox_2) ──
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流电源设置")
        self.groupBox_2.setStyleSheet(_GB_STYLE)
        dcG = QtWidgets.QGridLayout(self.groupBox_2)
        dcG.setSpacing(6)
        dcG.setContentsMargins(12, 20, 12, 12)

        # 表头
        _dc_headers = ["通道", "开关", "Vmp(V)", "Imp(A)", "Voc(V)", "Isc(A)", "功率(%)"]
        for _c, _h in enumerate(_dc_headers):
            _hlbl = QtWidgets.QLabel(_h)
            _hlbl.setStyleSheet("font-weight: bold; color: #475569;")
            _hlbl.setAlignment(QtCore.Qt.AlignCenter)
            dcG.addWidget(_hlbl, 0, _c)

        # DC1 ~ DC4
        _dc_rows = [
            (1, "checkBox_S1_DC1", "直流电源1", "comboBox_S1_DC1",
             "textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR",
             "textEdit_S1_DC1_Voc", "textEdit_S1_DC1_Isc",
             "textEdit_S1_DC1_PF"),
            (2, "checkBox_S1_DC2", "直流电源2", "comboBox_S1_DC2",
             "textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR",
             "textEdit_S1_DC2_Voc", "textEdit_S1_DC2_Isc",
             "textEdit_S1_DC2_PF"),
            (3, "checkBox_S1_DC3", "直流电源3", "comboBox_S1_DC3",
             "textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR",
             "textEdit_S1_DC3_Voc", "textEdit_S1_DC3_Isc",
             "textEdit_S1_DC3_PF"),
            (4, "checkBox_S1_DC4", "直流电源4", "comboBox_S1_DC4",
             "textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR",
             "textEdit_S1_DC4_Voc", "textEdit_S1_DC4_Isc",
             "textEdit_S1_DC4_PF"),
        ]
        for _r, (_n, _cbn, _cbt, _cmn,
                  _vn, _cn, _von, _in, _pn) in enumerate(_dc_rows, 1):
            _cb = QtWidgets.QCheckBox(_cbt)
            _cb.setChecked(True)
            _cb.setObjectName(_cbn)
            dcG.addWidget(_cb, _r, 0)
            setattr(self, _cbn, _cb)

            _cm = QtWidgets.QComboBox()
            _cm.setObjectName(_cmn)
            _cm.addItems(["开启", "关闭"])
            _cm.setFixedWidth(80)
            dcG.addWidget(_cm, _r, 1)
            setattr(self, _cmn, _cm)

            for _c, _name in enumerate(
                [_vn, _cn, _von, _in, _pn], 2,
            ):
                _te = QtWidgets.QTextEdit()
                _te.setObjectName(_name)
                _te.setFixedSize(70, 26)
                dcG.addWidget(_te, _r, _c)
                setattr(self, _name, _te)

        layout.addWidget(self.groupBox_2)

        # ── 时序设置组 (groupBox_4) ──
        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("时序设置")
        self.groupBox_4.setStyleSheet(_GB_STYLE)
        tG = QtWidgets.QGridLayout(self.groupBox_4)
        tG.setSpacing(8)
        tG.setContentsMargins(12, 20, 12, 12)

        self.label_131 = QtWidgets.QLabel("等待时间:")
        self.label_131.setObjectName("label_131")
        tG.addWidget(self.label_131, 0, 0)

        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(80, 28)
        self.textEdit_S1_ACWaitTIME.setText("3")
        tG.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)

        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(100)
        tG.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        self.label_132 = QtWidgets.QLabel("启机时间:")
        self.label_132.setObjectName("label_132")
        tG.addWidget(self.label_132, 0, 3)

        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(80, 28)
        self.textEdit_S1_TIME.setText("5")
        tG.addWidget(self.textEdit_S1_TIME, 0, 4)

        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(100)
        tG.addWidget(self.comboBox_S1_TIME, 0, 5)

        layout.addWidget(self.groupBox_4)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    # ================================================================ #
    #  Page 1:  功率分析仪 (Step 2) — radio + stackedWidget 内嵌
    # ================================================================ #
    def _build_step_page_wt(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_wt = QtWidgets.QGroupBox()
        self.groupBox_wt.setObjectName("groupBox_wt")
        self.groupBox_wt.setTitle("功率分析仪设置")
        self.groupBox_wt.setStyleSheet(_GB_STYLE)
        wG = QtWidgets.QGridLayout(self.groupBox_wt)
        wG.setSpacing(10)
        wG.setContentsMargins(16, 24, 16, 12)

        # step2 checkbox
        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        wG.addWidget(self.checkBox_S2, 0, 0)

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
        self._radio_group = radio_group

        # Radio 行布局
        radio_layout = QtWidgets.QHBoxLayout()
        for rb in [self.radioButton_S2_WT3000, self.radioButton_S2_WT1800,
                   self.radioButton_S2_WT1806E, self.radioButton_S2_WT5000]:
            radio_layout.addWidget(rb)
        radio_layout.addStretch()
        wG.addLayout(radio_layout, 0, 1, 1, 3)

        # QStackedWidget
        self._wtStacked = QtWidgets.QStackedWidget()
        self._wtStacked.addWidget(build_wt3000_content(self))   # index 0
        self._wtStacked.addWidget(build_wt1800_content(self))   # index 1
        self._wtStacked.addWidget(build_wt1806e_content(self))  # index 2
        self._wtStacked.addWidget(build_wt5000_content(self))   # index 3
        wG.addWidget(self._wtStacked, 1, 0, 1, 4)

        # Radio 切换联动
        def _on_radio_toggled(btn, checked):
            if checked:
                self._wtStacked.setCurrentIndex(radio_group.id(btn))
        radio_group.buttonToggled.connect(_on_radio_toggled)

        # 更新率
        self.checkBox_S2_update_rate = QtWidgets.QCheckBox()
        self.checkBox_S2_update_rate.setChecked(True)
        self.checkBox_S2_update_rate.setText("")
        self.checkBox_S2_update_rate.setObjectName("checkBox_S2_update_rate")
        wG.addWidget(self.checkBox_S2_update_rate, 2, 0)

        self.label_S2_update_rate = QtWidgets.QLabel("更新率")
        self.label_S2_update_rate.setObjectName("label_S2_update_rate")
        wG.addWidget(self.label_S2_update_rate, 2, 1)

        self.textEdit_S2_update_rate = QtWidgets.QTextEdit()
        self.textEdit_S2_update_rate.setObjectName("textEdit_S2_update_rate")
        self.textEdit_S2_update_rate.setFixedSize(80, 28)
        self.textEdit_S2_update_rate.setText("50")
        wG.addWidget(self.textEdit_S2_update_rate, 2, 2)

        self.comboBox_S2_update_rate = QtWidgets.QComboBox()
        self.comboBox_S2_update_rate.setObjectName("comboBox_S2_update_rate")
        self.comboBox_S2_update_rate.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S2_update_rate.setCurrentIndex(2)
        self.comboBox_S2_update_rate.setFixedWidth(100)
        wG.addWidget(self.comboBox_S2_update_rate, 2, 3)

        self._integrate_analyzer_mode(layout, self.groupBox_wt)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

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

    # ================================================================ #
    #  过频步骤合并（9个卡片 → 1个滚动页面）
    # ================================================================ #
    def _build_rocof_steps(self):
        """构建合并的ROCOF设置页面，9个卡片垂直排列，可滚动。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # 过频页总开关（勿与卡片 checkBox_S3 同名，避免 setattr 覆盖）
        self.checkBox_rocof_page = QtWidgets.QCheckBox("启用ROCOF设置")
        self.checkBox_rocof_page.setChecked(True)
        self.checkBox_rocof_page.setObjectName("checkBox_rocof_page")
        self.checkBox_rocof_page.setStyleSheet("font-size: 13px; font-weight: bold; padding: 4px;")
        layout.addWidget(self.checkBox_rocof_page)

        # QScrollArea 承载所有卡片
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 8, 0, 8)
        scroll_layout.setSpacing(8)

        guopin_cards = []
        for i in range(6):
            step_num = 3 + i
            card = self._build_rocof_card(step_num, "rocof", "ROCOF %d" % (i + 1))
            scroll_layout.addWidget(card)
            guopin_cards.append(card)

        def _on_guopin_page_toggled(checked, cards=guopin_cards):
            for c in cards:
                c.setEnabled(checked)

        self.checkBox_rocof_page.toggled.connect(_on_guopin_page_toggled)
        _on_guopin_page_toggled(self.checkBox_rocof_page.isChecked())

        # 默认：±2 Hz/s 与 ±1 Hz/s 各一组（其余空、未勾）
        _defaults = [
            (3, "50", "52", "2"),
            (4, "50", "48", "2"),
            (5, "50", "52", "1"),
            (6, "50", "48", "1"),
        ]
        for sn, a, b, rate in _defaults:
            getattr(self, "textEdit_S%d_freq_start_rocof" % sn).setPlainText(a)
            getattr(self, "textEdit_S%d_freq_end_rocof" % sn).setPlainText(b)
            getattr(self, "textEdit_S%d_rocof_hz_s_rocof" % sn).setPlainText(rate)
        for sn in range(7, 9):
            getattr(self, "checkBox_S%d" % sn).setChecked(False)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self.stackedWidget.addWidget(page)

    # ================================================================ #
    #  欠频步骤合并（9个卡片 → 1个滚动页面）
    # ================================================================ #
    def _build_spare_steps(self):
        """构建合并的备用页面，9个卡片垂直排列，可滚动。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # 欠频页总开关（勿与卡片 checkBox_S12 同名）
        self.checkBox_rocof_spare_page = QtWidgets.QCheckBox("启用备用")
        self.checkBox_rocof_spare_page.setChecked(True)
        self.checkBox_rocof_spare_page.setObjectName("checkBox_rocof_spare_page")
        self.checkBox_rocof_spare_page.setStyleSheet("font-size: 13px; font-weight: bold; padding: 4px;")
        layout.addWidget(self.checkBox_rocof_spare_page)

        # QScrollArea 承载所有卡片
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 8, 0, 8)
        scroll_layout.setSpacing(8)

        qianpin_cards = []
        for i in range(9):
            step_num = 12 + i
            card = self._build_rocof_card(step_num, "spare", "备用 %d" % (i + 1))
            scroll_layout.addWidget(card)
            qianpin_cards.append(card)

        def _on_qianpin_page_toggled(checked, cards=qianpin_cards):
            for c in cards:
                c.setEnabled(checked)

        self.checkBox_rocof_spare_page.toggled.connect(_on_qianpin_page_toggled)
        _on_qianpin_page_toggled(self.checkBox_rocof_spare_page.isChecked())

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self.stackedWidget.addWidget(page)

    def _build_rocof_card(self, step_num, side_tag, title):
        """构建单个ROCOF扫描配置卡片。"""
        card = QtWidgets.QWidget()
        card.setStyleSheet("background-color: white;")
        cardLayout = QtWidgets.QVBoxLayout(card)
        cardLayout.setContentsMargins(0, 0, 0, 0)
        cardLayout.setSpacing(0)

        grp = QtWidgets.QGroupBox()
        grp.setObjectName("groupBox_rocof_S%d" % step_num)
        grp.setTitle(title)
        grp.setStyleSheet(_GB_STYLE)
        gG = QtWidgets.QGridLayout(grp)
        gG.setSpacing(10)
        gG.setContentsMargins(16, 24, 16, 12)

        # step checkbox
        _cb = QtWidgets.QCheckBox("step%d" % step_num)
        _cb.setChecked(True)
        _cb.setObjectName("checkBox_S%d" % step_num)
        gG.addWidget(_cb, 0, 0)
        setattr(self, "checkBox_S%d" % step_num, _cb)

        # 更新率（对齐ROCOF df/dt：勾选则按全局更新率ROCOF扫频）
        _rate = QtWidgets.QCheckBox("更新率")
        _rate.setChecked(True)
        _rate.setObjectName("checkBox_S%d_RATE" % step_num)
        gG.addWidget(_rate, 0, 1)
        setattr(self, "checkBox_S%d_RATE" % step_num, _rate)

        # ── 频率区间 ──
        _lbl_range = QtWidgets.QLabel("频率区间")
        gG.addWidget(_lbl_range, 1, 0)

        _te_start = QtWidgets.QTextEdit()
        _te_start.setObjectName("textEdit_S%d_freq_start_%s" % (step_num, side_tag))
        _te_start.setFixedSize(80, 28)
        gG.addWidget(_te_start, 1, 1)
        setattr(self, "textEdit_S%d_freq_start_%s" % (step_num, side_tag), _te_start)

        _lbl_tilde = QtWidgets.QLabel("~")
        gG.addWidget(_lbl_tilde, 1, 2)

        _te_end = QtWidgets.QTextEdit()
        _te_end.setObjectName("textEdit_S%d_freq_end_%s" % (step_num, side_tag))
        _te_end.setFixedSize(80, 28)
        gG.addWidget(_te_end, 1, 3)
        setattr(self, "textEdit_S%d_freq_end_%s" % (step_num, side_tag), _te_end)

        _lbl_hz = QtWidgets.QLabel("Hz")
        gG.addWidget(_lbl_hz, 1, 4)

        # ── ROCOF 变化率 ──
        _lbl_rate = QtWidgets.QLabel("ROCOF")
        gG.addWidget(_lbl_rate, 2, 0)
        _te_rocof = QtWidgets.QTextEdit()
        _te_rocof.setObjectName("textEdit_S%d_rocof_hz_s_%s" % (step_num, side_tag))
        _te_rocof.setFixedSize(80, 28)
        gG.addWidget(_te_rocof, 2, 1)
        setattr(self, "textEdit_S%d_rocof_hz_s_%s" % (step_num, side_tag), _te_rocof)
        _lbl_rocof_unit = QtWidgets.QLabel("Hz/s")
        gG.addWidget(_lbl_rocof_unit, 2, 2)

        # ── 终点保持（扫完后驻留）──
        _lbl_tdur = QtWidgets.QLabel("终点保持：")
        gG.addWidget(_lbl_tdur, 3, 0)

        _te_dur = QtWidgets.QTextEdit()
        _te_dur.setObjectName("textEdit_S%d_test_duration_%s" % (step_num, side_tag))
        _te_dur.setFixedSize(80, 28)
        _te_dur.setPlainText("2")
        gG.addWidget(_te_dur, 3, 1)
        setattr(self, "textEdit_S%d_test_duration_%s" % (step_num, side_tag), _te_dur)

        _cmu = QtWidgets.QComboBox()
        _cmu.setObjectName("comboBox_S%d_test_time_unit_%s" % (step_num, side_tag))
        _cmu.addItems(["秒", "分钟", "小时"])
        _cmu.setFixedWidth(100)
        gG.addWidget(_cmu, 3, 2)
        setattr(self, "comboBox_S%d_test_time_unit_%s" % (step_num, side_tag), _cmu)

        # 联动：步骤复选框禁用时，禁用内部控件
        inner_widgets = [_rate, _te_start, _te_end, _te_rocof, _te_dur, _cmu,
                         _lbl_range, _lbl_tilde, _lbl_hz, _lbl_rate, _lbl_rocof_unit, _lbl_tdur]
        step_cb = _cb

        def _on_step_toggled(checked, widgets=inner_widgets, scb=step_cb):
            for w in widgets:
                w.setEnabled(checked)

        _cb.toggled.connect(_on_step_toggled)

        cardLayout.addWidget(grp)
        return card

    # ================================================================ #
    #  Page 20:  关机设置 (Step 21)
    # ================================================================ #
    def _build_step_page_shutdown(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_End = QtWidgets.QGroupBox()
        self.groupBox_End.setObjectName("groupBox_End")
        self.groupBox_End.setTitle("关机设置")
        self.groupBox_End.setStyleSheet(_GB_STYLE)
        eG = QtWidgets.QGridLayout(self.groupBox_End)
        eG.setSpacing(10)
        eG.setContentsMargins(16, 24, 16, 12)

        # step_last
        self.checkBox_S_End = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_End.setChecked(True)
        self.checkBox_S_End.setObjectName("checkBox_S_End")
        eG.addWidget(self.checkBox_S_End, 0, 0)

        # 交流电源
        self.label_End_AC_cap = QtWidgets.QLabel("交流电源")
        self.label_End_AC_cap.setObjectName("label_End_AC_cap")
        eG.addWidget(self.label_End_AC_cap, 0, 1)

        self.comboBox_S_End_AC = QtWidgets.QComboBox()
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItems(["关闭", "开启"])
        self.comboBox_S_End_AC.setCurrentIndex(0)
        self.comboBox_S_End_AC.setFixedWidth(100)
        eG.addWidget(self.comboBox_S_End_AC, 0, 2)

        # 直流电源 1-4
        _dc_end = [
            ("checkBox_S_End_DC1", "直流电源1", "comboBox_S_End_DC1"),
            ("checkBox_S_End_DC2", "直流电源2", "comboBox_S_End_DC2"),
            ("checkBox_S_End_DC3", "直流电源3", "comboBox_S_End_DC3"),
            ("checkBox_S_End_DC4", "直流电源4", "comboBox_S_End_DC4"),
        ]
        for _c, (_cbn, _cbt, _cmn) in enumerate(_dc_end):
            _col = 1 + _c * 2

            _cb = QtWidgets.QCheckBox(_cbt)
            _cb.setChecked(True)
            _cb.setObjectName(_cbn)
            eG.addWidget(_cb, 1, _col)
            setattr(self, _cbn, _cb)

            _cm = QtWidgets.QComboBox()
            _cm.setObjectName(_cmn)
            _cm.addItems(["关闭", "开启"])
            _cm.setCurrentIndex(0)
            _cm.setFixedWidth(100)
            eG.addWidget(_cm, 1, _col + 1)
            setattr(self, _cmn, _cm)

        layout.addWidget(self.groupBox_End)
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

    # ------------------------------------------------------------------ #
    #  retranslateUi
    # ------------------------------------------------------------------ #
    def retranslateUi(self, Dialog_thairocof):
        _translate = QtCore.QCoreApplication.translate

        Dialog_thairocof.setWindowTitle(
            _translate(
                "Dialog_thairocof",
                "ROCOF保护项目配置",
            ),
        )

        # 顶部按钮
        self.pushButton_TestAppend.setText(
            _translate("Dialog_thairocof", "测试追加"),
        )
        self.pushButton_ReadSettingFile.setText(
            _translate("Dialog_thairocof", "读取设定"),
        )
        self.pushButton_SaveSettingFile.setText(
            _translate("Dialog_thairocof", "保存设定"),
        )
        self.pushButton_Send.setText(
            _translate("Dialog_thairocof", "提交"),
        )

        # Step 1 -- AC/DC 电源
        self.label_3.setText(
            _translate("Dialog_thairocof", "交流电源"),
        )
        self.label_4.setText(
            _translate("Dialog_thairocof", "交流电压1"),
        )
        self.label_5.setText(
            _translate("Dialog_thairocof", "V"),
        )
        self.label_113.setText(
            _translate("Dialog_thairocof", "交流电压2"),
        )
        self.label_107.setText(
            _translate("Dialog_thairocof", "V"),
        )
        self.label_123.setText(
            _translate("Dialog_thairocof", "交流电压3"),
        )
        self.label_102.setText(
            _translate("Dialog_thairocof", "V"),
        )
        self.label_19.setText(
            _translate("Dialog_thairocof", "频率"),
        )
        self.label_18.setText(
            _translate("Dialog_thairocof", "Hz"),
        )
        self.label_131.setText(
            _translate("Dialog_thairocof", "等待时间:"),
        )
        self.label_132.setText(
            _translate("Dialog_thairocof", "启机时间:"),
        )

        # Step 2 -- 功率分析仪（radio 已在 _build_step_page_wt 中设置文本）

        # Step 3-20 -- 频率频段（已在合并卡片中设置文本）

        # Step 21 -- 关机设置
        self.checkBox_S_End.setText(
            _translate("Dialog_thairocof", "step_last"),
        )
        self.label_End_AC_cap.setText(
            _translate("Dialog_thairocof", "交流电源"),
        )
        self.checkBox_S_End_DC1.setText(
            _translate("Dialog_thairocof", "直流电源1"),
        )
        self.checkBox_S_End_DC2.setText(
            _translate("Dialog_thairocof", "直流电源2"),
        )
        self.checkBox_S_End_DC3.setText(
            _translate("Dialog_thairocof", "直流电源3"),
        )
        self.checkBox_S_End_DC4.setText(
            _translate("Dialog_thairocof", "直流电源4"),
        )
