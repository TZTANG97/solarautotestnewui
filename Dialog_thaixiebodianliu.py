# -*- coding: utf-8 -*-
# 谐波电流项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets
from components.timeline import TimelineWidget
from components.wt_config_content import build_wt3000_content, build_wt1800_content, build_wt1806e_content, build_wt5000_content

# 12 个谐波步骤的 widget objectName 规格（保持原有命名不变）
_HARMONIC_SPECS = [
    {"title": "谐波 1次",  "step_cb": "checkBox_S3",    "step_text": "step3",  "dc1_cb": "checkBox_S1_DC1_2",  "dc2_cb": "checkBox_S1_DC2_2",  "dc3_cb": "checkBox_S1_DC3_2",  "dc4_cb": "checkBox_S1_DC4_2",  "pf_te": "textEdit_S1_DC1_PF_2",  "pwr_lbl": "label_76", "pct_lbl": "label_47"},
    {"title": "谐波 2次",  "step_cb": "checkBox_S3_2",  "step_text": "step4",  "dc1_cb": "checkBox_S1_DC1_3",  "dc2_cb": "checkBox_S1_DC2_3",  "dc3_cb": "checkBox_S1_DC3_3",  "dc4_cb": "checkBox_S1_DC4_3",  "pf_te": "textEdit_S1_DC1_PF_3",  "pwr_lbl": "label_77", "pct_lbl": "label_49"},
    {"title": "谐波 3次",  "step_cb": "checkBox_S3_3",  "step_text": "step5",  "dc1_cb": "checkBox_S1_DC1_4",  "dc2_cb": "checkBox_S1_DC2_4",  "dc3_cb": "checkBox_S1_DC3_4",  "dc4_cb": "checkBox_S1_DC4_4",  "pf_te": "textEdit_S1_DC1_PF_4",  "pwr_lbl": "label_78", "pct_lbl": "label_50"},
    {"title": "谐波 4次",  "step_cb": "checkBox_S3_4",  "step_text": "step6",  "dc1_cb": "checkBox_S1_DC1_5",  "dc2_cb": "checkBox_S1_DC2_5",  "dc3_cb": "checkBox_S1_DC3_5",  "dc4_cb": "checkBox_S1_DC4_5",  "pf_te": "textEdit_S1_DC1_PF_5",  "pwr_lbl": "label_79", "pct_lbl": "label_51"},
    {"title": "谐波 5次",  "step_cb": "checkBox_S3_5",  "step_text": "step7",  "dc1_cb": "checkBox_S1_DC1_6",  "dc2_cb": "checkBox_S1_DC2_6",  "dc3_cb": "checkBox_S1_DC3_6",  "dc4_cb": "checkBox_S1_DC4_6",  "pf_te": "textEdit_S1_DC1_PF_6",  "pwr_lbl": "label_80", "pct_lbl": "label_52"},
    {"title": "谐波 6次",  "step_cb": "checkBox_S3_10", "step_text": "step8",  "dc1_cb": "checkBox_S1_DC1_10", "dc2_cb": "checkBox_S1_DC2_11", "dc3_cb": "checkBox_S1_DC3_10", "dc4_cb": "checkBox_S1_DC4_7",  "pf_te": "textEdit_S1_DC1_PF_10", "pwr_lbl": "label_82", "pct_lbl": "label_61"},
    {"title": "谐波 7次",  "step_cb": "checkBox_S3_6",  "step_text": "step9",  "dc1_cb": "checkBox_S1_DC1_11", "dc2_cb": "checkBox_S1_DC2_8",  "dc3_cb": "checkBox_S1_DC3_11", "dc4_cb": "checkBox_S1_DC3_15", "pf_te": "textEdit_S1_DC1_PF_9",  "pwr_lbl": "label_81", "pct_lbl": "label_55"},
    {"title": "谐波 8次",  "step_cb": "checkBox_S3_7",  "step_text": "step10", "dc1_cb": "checkBox_S1_DC1_7",  "dc2_cb": "checkBox_S1_DC2_9",  "dc3_cb": "checkBox_S1_DC3_8",  "dc4_cb": "checkBox_S1_DC3_14", "pf_te": "textEdit_S1_DC1_PF_7",  "pwr_lbl": "label_83", "pct_lbl": "label_53"},
    {"title": "谐波 9次",  "step_cb": "checkBox_S3_9",  "step_text": "step11", "dc1_cb": "checkBox_S1_DC1_9",  "dc2_cb": "checkBox_S1_DC2_10", "dc3_cb": "checkBox_S1_DC3_9",  "dc4_cb": "checkBox_S1_DC3_16", "pf_te": "textEdit_S1_DC1_PF_11", "pwr_lbl": "label_84", "pct_lbl": "label_56"},
    {"title": "谐波 10次", "step_cb": "checkBox_S3_8",  "step_text": "step12", "dc1_cb": "checkBox_S1_DC1_8",  "dc2_cb": "checkBox_S1_DC2_7",  "dc3_cb": "checkBox_S1_DC3_7",  "dc4_cb": "checkBox_S1_DC3_17", "pf_te": "textEdit_S1_DC1_PF_8",  "pwr_lbl": "label_85", "pct_lbl": "label_60"},
    {"title": "谐波 11次", "step_cb": "checkBox_S3_11", "step_text": "step13", "dc1_cb": "checkBox_S1_DC1_12", "dc2_cb": "checkBox_S1_DC2_12", "dc3_cb": "checkBox_S1_DC3_12", "dc4_cb": "checkBox_S1_DC3_13", "pf_te": "textEdit_S1_DC1_PF_12", "pwr_lbl": "label_86", "pct_lbl": "label_62"},
]


class Ui_Dialog_thaixiebodianliu(object):
    def setupUi(self, Dialog_thaixiebodianliu):
        Dialog_thaixiebodianliu.setObjectName("Dialog_thaixiebodianliu")
        Dialog_thaixiebodianliu.resize(1300, 850)
        Dialog_thaixiebodianliu.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaixiebodianliu.setWindowIcon(icon)

        # ── 主布局（上下结构） ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaixiebodianliu)
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

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        sep.setStyleSheet("color: #cbd5e1; border: none; max-width: 1px;")
        topLayout.addWidget(sep)

        # ── 模式切换（WT3000谐波 / 德威创模式） ──
        self._radio_group = QtWidgets.QButtonGroup(None)
        self._radio_group.setExclusive(True)

        self.radio_wt3000 = QtWidgets.QRadioButton("WT3000谐波")
        self.radio_wt3000.setChecked(True)
        self.radio_wt3000.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b; background: transparent;")
        self._radio_group.addButton(self.radio_wt3000, 0)
        topLayout.addWidget(self.radio_wt3000)

        self.radio_dewetron = QtWidgets.QRadioButton("德威创模式")
        self.radio_dewetron.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b; background: transparent;")
        self._radio_group.addButton(self.radio_dewetron, 1)
        topLayout.addWidget(self.radio_dewetron)

        topLayout.addStretch()

        self._step_labels = []
        step_titles = ["① AC/DC 电源", "② 功率分析仪", "③ 谐波设置", "④ 关机设置"]
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
        self._build_step1()           # AC/DC 电源
        self._build_step2()           # 功率分析仪
        self._build_step3_harmonics() # 谐波设置（timeline + card）
        self._build_step13()          # 关机设置

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaixiebodianliu)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaixiebodianliu)

    # ══════════════════════════════════════════════
    # 步骤切换
    # ══════════════════════════════════════════════
    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 8px; font-size: 11px; font-weight: bold; color: #7c3aed;
                        border-bottom: 3px solid #8b5cf6; border-radius: 0;
                        background-color: #f3e8ff;
                    }
                """)
            else:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 8px; font-size: 11px; color: #64748b;
                        border-bottom: 3px solid transparent; border-radius: 0;
                        background: transparent;
                    }
                    QLabel:hover { background-color: #f1f5f9; }
                """)

    # ══════════════════════════════════════════════
    # 通用样式常量
    # ══════════════════════════════════════════════
    _GRP_STYLE = "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }"
    _INPUT_STYLE = (
        "QTextEdit { border: 1px solid #d1d5db; border-radius: 4px; padding: 2px 4px; "
        "font-size: 12px; background-color: #f9fafb; }"
    )
    _COMBO_STYLE = (
        "QComboBox { border: 1px solid #d1d5db; border-radius: 4px; padding: 4px 8px; "
        "font-size: 12px; background-color: #f9fafb; min-width: 90px; }"
    )
    _CB_STYLE = "QCheckBox { font-size: 12px; spacing: 6px; }"
    _LABEL_STYLE = "font-size: 12px; color: #475569;"
    _HEADER_STYLE = "font-weight: bold; color: #475569; font-size: 12px;"

    def _make_input(self, name, parent=None, default="", width=80, height=28):
        """创建统一样式的 QTextEdit 输入框。"""
        te = QtWidgets.QTextEdit()
        te.setObjectName(name)
        te.setFixedSize(width, height)
        te.setStyleSheet(self._INPUT_STYLE)
        if default:
            te.setText(default)
        if parent is not None:
            setattr(self, name, te)
        return te

    def _make_combo(self, name, items, parent=None, width=100):
        """创建统一样式的 QComboBox。"""
        cb = QtWidgets.QComboBox()
        cb.setObjectName(name)
        cb.addItems(items)
        cb.setFixedWidth(width)
        cb.setStyleSheet(self._COMBO_STYLE)
        if parent is not None:
            setattr(self, name, cb)
        return cb

    def _make_checkbox(self, name, text, checked=True, parent=None):
        """创建统一样式的 QCheckBox。"""
        cb = QtWidgets.QCheckBox(text)
        cb.setChecked(checked)
        cb.setObjectName(name)
        cb.setStyleSheet(self._CB_STYLE)
        if parent is not None:
            setattr(self, name, cb)
        return cb

    def _make_label(self, text, style=None):
        """创建统一标签。"""
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(style or self._LABEL_STYLE)
        return lbl

    def _make_radio(self, name, text, parent=None, checked=False):
        """创建统一样式的 QRadioButton。"""
        rb = QtWidgets.QRadioButton(text)
        rb.setObjectName(name)
        rb.setStyleSheet(
            "QRadioButton { spacing: 8px; font-size: 13px; font-weight: bold; padding: 4px 8px; }"
            "QRadioButton::indicator { width: 16px; height: 16px; border: 2px solid #cbd5e1; border-radius: 10px; }"
            "QRadioButton::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
        )
        if parent is not None:
            setattr(self, name, rb)
        if checked:
            rb.setChecked(True)
        return rb

    # ══════════════════════════════════════════════
    # Step 1: AC/DC 电源 + 时序
    # ══════════════════════════════════════════════
    def _build_step1(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── AC 电源组 ──
        grp_ac = QtWidgets.QGroupBox()
        grp_ac.setObjectName("groupBox_2")
        grp_ac.setTitle("交流电源设置")
        grp_ac.setStyleSheet(self._GRP_STYLE)
        acGrid = QtWidgets.QGridLayout(grp_ac)
        acGrid.setSpacing(8)
        acGrid.setContentsMargins(12, 20, 12, 12)

        self.checkBox_S1 = self._make_checkbox("checkBox_S1", "step1")
        acGrid.addWidget(self.checkBox_S1, 0, 0)

        acGrid.addWidget(self._make_label("交流电源", self._HEADER_STYLE), 0, 1)
        self.comboBox_S1_AC = self._make_combo("comboBox_S1_AC", ["开启", "关闭"])
        acGrid.addWidget(self.comboBox_S1_AC, 0, 2)

        acGrid.addWidget(self._make_label("交流电压1:"), 0, 3)
        self.textEdit_S1_AC_VOLT = self._make_input("textEdit_S1_AC_VOLT", default="230")
        acGrid.addWidget(self.textEdit_S1_AC_VOLT, 0, 4)
        acGrid.addWidget(self._make_label("V"), 0, 5)

        acGrid.addWidget(self._make_label("交流电压2:"), 0, 6)
        self.textEdit_S1_AC_VOLT_2 = self._make_input("textEdit_S1_AC_VOLT_2", default="230")
        acGrid.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 7)
        acGrid.addWidget(self._make_label("V"), 0, 8)

        acGrid.addWidget(self._make_label("交流电压3:"), 1, 1)
        self.textEdit_S1_AC_VOLT_3 = self._make_input("textEdit_S1_AC_VOLT_3", default="230")
        acGrid.addWidget(self.textEdit_S1_AC_VOLT_3, 1, 2)
        acGrid.addWidget(self._make_label("V"), 1, 3)

        self.comboBox_S1_AC_2 = self._make_combo("comboBox_S1_AC_2", ["单相", "三相"])
        acGrid.addWidget(self.comboBox_S1_AC_2, 1, 4)

        acGrid.addWidget(self._make_label("频率:"), 1, 5)
        self.textEdit_S1_AC_FR = self._make_input("textEdit_S1_AC_FR", default="50")
        acGrid.addWidget(self.textEdit_S1_AC_FR, 1, 6)
        acGrid.addWidget(self._make_label("Hz"), 1, 7)

        layout.addWidget(grp_ac)

        # ── DC 电源组 (4 channels) ──
        grp_dc = QtWidgets.QGroupBox()
        grp_dc.setObjectName("groupBox_6")
        grp_dc.setTitle("直流电源设置")
        grp_dc.setStyleSheet(self._GRP_STYLE)
        dcGrid = QtWidgets.QGridLayout(grp_dc)
        dcGrid.setSpacing(6)
        dcGrid.setContentsMargins(12, 20, 12, 12)

        # 表头
        dc_headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]
        for c, h in enumerate(dc_headers):
            lbl = self._make_label(h, self._HEADER_STYLE)
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            dcGrid.addWidget(lbl, 0, c)

        # DC1
        self.checkBox_S1_DC1 = self._make_checkbox("checkBox_S1_DC1", "直流电源1")
        dcGrid.addWidget(self.checkBox_S1_DC1, 1, 0)
        self.comboBox_S1_DC1 = self._make_combo("comboBox_S1_DC1", ["开启", "关闭"])
        dcGrid.addWidget(self.comboBox_S1_DC1, 1, 1)
        for c, n in enumerate(["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc",
                               "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"], start=2):
            te = self._make_input(n, parent=True, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100"))
            )
            dcGrid.addWidget(te, 1, c)

        # DC2
        self.checkBox_S1_DC2 = self._make_checkbox("checkBox_S1_DC2", "直流电源2")
        dcGrid.addWidget(self.checkBox_S1_DC2, 2, 0)
        self.comboBox_S1_DC2 = self._make_combo("comboBox_S1_DC2", ["开启", "关闭"])
        dcGrid.addWidget(self.comboBox_S1_DC2, 2, 1)
        for c, n in enumerate(["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc",
                               "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"], start=2):
            te = self._make_input(n, parent=True, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100"))
            )
            dcGrid.addWidget(te, 2, c)

        # DC3
        self.checkBox_S1_DC3 = self._make_checkbox("checkBox_S1_DC3", "直流电源3")
        dcGrid.addWidget(self.checkBox_S1_DC3, 3, 0)
        self.comboBox_S1_DC3 = self._make_combo("comboBox_S1_DC3", ["开启", "关闭"])
        dcGrid.addWidget(self.comboBox_S1_DC3, 3, 1)
        for c, n in enumerate(["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc",
                               "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"], start=2):
            te = self._make_input(n, parent=True, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100"))
            )
            dcGrid.addWidget(te, 3, c)

        # DC4
        self.checkBox_S1_DC4 = self._make_checkbox("checkBox_S1_DC4", "直流电源4")
        dcGrid.addWidget(self.checkBox_S1_DC4, 4, 0)
        self.comboBox_S1_DC4 = self._make_combo("comboBox_S1_DC4", ["开启", "关闭"])
        dcGrid.addWidget(self.comboBox_S1_DC4, 4, 1)
        for c, n in enumerate(["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc",
                               "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"], start=2):
            te = self._make_input(n, parent=True, default="220" if c == 2 else ("10" if c in (3, 5) else ("220" if c == 4 else "100"))
            )
            dcGrid.addWidget(te, 4, c)

        layout.addWidget(grp_dc)

        # ── 时序组 ──
        grp_time = QtWidgets.QGroupBox()
        grp_time.setObjectName("groupBox_5")
        grp_time.setTitle("时序设置")
        grp_time.setStyleSheet(self._GRP_STYLE)
        tGrid = QtWidgets.QGridLayout(grp_time)
        tGrid.setSpacing(8)
        tGrid.setContentsMargins(12, 20, 12, 12)

        tGrid.addWidget(self._make_label("等待时间:"), 0, 0)
        self.textEdit_S1_ACWaitTIME = self._make_input("textEdit_S1_ACWaitTIME", default="3")
        tGrid.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = self._make_combo("comboBox_S1_ACWaitTIME", ["秒", "分钟", "毫秒"])
        tGrid.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        tGrid.addWidget(self._make_label("启机时间:"), 0, 3)
        self.textEdit_S1_TIME = self._make_input("textEdit_S1_TIME", default="5")
        tGrid.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = self._make_combo("comboBox_S1_TIME", ["分钟", "秒", "毫秒"])
        tGrid.addWidget(self.comboBox_S1_TIME, 0, 5)

        # 积分测试
        self.checkBox_S1_Integral = self._make_checkbox("checkBox_S1_Integral", "积分测试")
        tGrid.addWidget(self.checkBox_S1_Integral, 1, 0)
        self.comboBox_S1_Integral = self._make_combo("comboBox_S1_Integral", ["关闭", "开启"])
        tGrid.addWidget(self.comboBox_S1_Integral, 1, 1)

        layout.addWidget(grp_time)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 2: 功率分析仪（WT3000 / DEWETRON 双模式）
    # ══════════════════════════════════════════════
    def _build_step2(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── 步骤2 启用复选框 ──
        self.checkBox_S2 = self._make_checkbox("checkBox_S2", "step2", parent=self)
        layout.addWidget(self.checkBox_S2)

        # ── QStackedWidget：页面0=WT，页面1=DEWETRON ──
        self._step2Stacked = QtWidgets.QStackedWidget()

        # ── 页面 0: WT3000/WT1800/WT1806E/WT5000 ──
        wt_page = QtWidgets.QWidget()
        wt_page.setStyleSheet("background-color: white;")
        wt_layout = QtWidgets.QVBoxLayout(wt_page)
        wt_layout.setContentsMargins(0, 0, 0, 0)

        wt_grp = QtWidgets.QGroupBox()
        wt_grp.setTitle("功率分析仪配置")
        wt_grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(wt_grp)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

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
        gLayout.addLayout(radio_layout, 0, 1, 1, 3)

        # QStackedWidget 承载 4 个 WT 配置页面
        self._wtStacked = QtWidgets.QStackedWidget()
        page0 = build_wt3000_content(self)
        self._wtStacked.addWidget(page0)   # index 0
        page1 = build_wt1800_content(self)
        self._wtStacked.addWidget(page1)   # index 1
        page2 = build_wt1806e_content(self)
        self._wtStacked.addWidget(page2)   # index 2
        page3 = build_wt5000_content(self)
        self._wtStacked.addWidget(page3)   # index 3

        gLayout.addWidget(self._wtStacked, 1, 0, 1, 4)

        # WT Radio 切换联动
        def _on_wt_radio_toggled(btn, checked):
            if checked:
                btn_id = self._wt_radio_group.id(btn)
                self._wtStacked.setCurrentIndex(btn_id)

        self._wt_radio_group.buttonToggled.connect(_on_wt_radio_toggled)

        wt_layout.addWidget(wt_grp)
        self._step2Stacked.addWidget(wt_page)   # index 0

        # ── 页面 1: DEWETRON 谐波配置 ──
        dew_page = QtWidgets.QWidget()
        dew_page.setStyleSheet("background-color: white;")
        dew_layout = QtWidgets.QVBoxLayout(dew_page)
        dew_layout.setContentsMargins(16, 16, 16, 16)
        dew_layout.setSpacing(12)

        # ── Group 1: DEWETRON 谐波测量配置 ──
        dew_group = QtWidgets.QGroupBox()
        dew_group.setTitle("DEWETRON 谐波测量配置")
        dew_group.setStyleSheet(self._GRP_STYLE)
        formLayout = QtWidgets.QFormLayout(dew_group)
        formLayout.setSpacing(10)
        formLayout.setContentsMargins(16, 24, 16, 12)

        # 谐波/简谐波 开关
        self.checkBox_DEW_HarmonicEnabled = QtWidgets.QCheckBox("谐波/简谐波")
        self.checkBox_DEW_HarmonicEnabled.setChecked(True)
        self.checkBox_DEW_HarmonicEnabled.setObjectName("checkBox_DEW_HarmonicEnabled")
        formLayout.addRow(self.checkBox_DEW_HarmonicEnabled)

        # 最大谐波次数
        self.spinBox_DEW_MaxHarmonicOrder = QtWidgets.QSpinBox()
        self.spinBox_DEW_MaxHarmonicOrder.setObjectName("spinBox_DEW_MaxHarmonicOrder")
        self.spinBox_DEW_MaxHarmonicOrder.setRange(1, 100)
        self.spinBox_DEW_MaxHarmonicOrder.setValue(50)
        self.spinBox_DEW_MaxHarmonicOrder.setFixedWidth(120)
        formLayout.addRow("最大谐波次数:", self.spinBox_DEW_MaxHarmonicOrder)

        # THD计算谐波次数
        self.spinBox_DEW_THDOrder = QtWidgets.QSpinBox()
        self.spinBox_DEW_THDOrder.setObjectName("spinBox_DEW_THDOrder")
        self.spinBox_DEW_THDOrder.setRange(1, 100)
        self.spinBox_DEW_THDOrder.setValue(40)
        self.spinBox_DEW_THDOrder.setFixedWidth(120)
        formLayout.addRow("THD计算谐波次数:", self.spinBox_DEW_THDOrder)

        # Grouping type
        self.comboBox_DEW_GroupingType = QtWidgets.QComboBox()
        self.comboBox_DEW_GroupingType.setObjectName("comboBox_DEW_GroupingType")
        self.comboBox_DEW_GroupingType.addItems(["无", "类型1-IEC61000-4-7-5.6(9)", "类型1-IEC61000-4-7-5.1(8)"])
        self.comboBox_DEW_GroupingType.setFixedWidth(250)
        formLayout.addRow("Grouping type:", self.comboBox_DEW_GroupingType)

        # 最大刷新率
        self.comboBox_DEW_MaxRefreshRate = QtWidgets.QComboBox()
        self.comboBox_DEW_MaxRefreshRate.setObjectName("comboBox_DEW_MaxRefreshRate")
        self.comboBox_DEW_MaxRefreshRate.addItems(["Default", "100", "50", "20", "10", "5", "2", "1", "SYNC to HARMONIC"])
        self.comboBox_DEW_MaxRefreshRate.setCurrentText("SYNC to HARMONIC")
        self.comboBox_DEW_MaxRefreshRate.setFixedWidth(200)
        formLayout.addRow("最大刷新率:", self.comboBox_DEW_MaxRefreshRate)

        dew_layout.addWidget(dew_group)

        # ── Group 2: 文件设置 ──
        file_group = QtWidgets.QGroupBox()
        file_group.setTitle("文件设置")
        file_group.setStyleSheet(self._GRP_STYLE)
        fileFormLayout = QtWidgets.QFormLayout(file_group)
        fileFormLayout.setSpacing(10)
        fileFormLayout.setContentsMargins(16, 24, 16, 12)

        # 启用多文件存储
        self.checkBox_DEW_MultiFileStorage = QtWidgets.QCheckBox("启用多文件存储")
        self.checkBox_DEW_MultiFileStorage.setChecked(True)
        self.checkBox_DEW_MultiFileStorage.setObjectName("checkBox_DEW_MultiFileStorage")
        fileFormLayout.addRow(self.checkBox_DEW_MultiFileStorage)

        # 按时间分割文件
        self.checkBox_DEW_SplitByTime = QtWidgets.QCheckBox("按时间分割文件")
        self.checkBox_DEW_SplitByTime.setChecked(True)
        self.checkBox_DEW_SplitByTime.setObjectName("checkBox_DEW_SplitByTime")
        fileFormLayout.addRow(self.checkBox_DEW_SplitByTime)

        self.spinBox_DEW_SplitTime = QtWidgets.QSpinBox()
        self.spinBox_DEW_SplitTime.setObjectName("spinBox_DEW_SplitTime")
        self.spinBox_DEW_SplitTime.setRange(1, 3600)
        self.spinBox_DEW_SplitTime.setValue(305)
        self.spinBox_DEW_SplitTime.setFixedWidth(120)
        _split_time_container = QtWidgets.QWidget()
        _st_h = QtWidgets.QHBoxLayout(_split_time_container)
        _st_h.setContentsMargins(0, 0, 0, 0)
        _st_h.setSpacing(4)
        _st_h.addWidget(self.spinBox_DEW_SplitTime)
        _st_h.addWidget(QtWidgets.QLabel("秒"))
        _st_h.addStretch()
        fileFormLayout.addRow("文件分割时间:", _split_time_container)

        # 创建子文件夹
        self.checkBox_DEW_CreateSubfolder = QtWidgets.QCheckBox("创建子文件夹")
        self.checkBox_DEW_CreateSubfolder.setChecked(False)
        self.checkBox_DEW_CreateSubfolder.setObjectName("checkBox_DEW_CreateSubfolder")
        fileFormLayout.addRow(self.checkBox_DEW_CreateSubfolder)

        # 多文件存储联动：关闭时禁用子项
        def _on_multi_file_toggled(checked):
            self.checkBox_DEW_SplitByTime.setEnabled(checked)
            self.spinBox_DEW_SplitTime.setEnabled(checked and self.checkBox_DEW_SplitByTime.isChecked())
            self.checkBox_DEW_CreateSubfolder.setEnabled(checked)
        self.checkBox_DEW_MultiFileStorage.toggled.connect(_on_multi_file_toggled)

        # 按时间分割联动：启用时才允许设置时间
        def _on_split_by_time_toggled(checked):
            self.spinBox_DEW_SplitTime.setEnabled(checked)
        self.checkBox_DEW_SplitByTime.toggled.connect(_on_split_by_time_toggled)

        _on_multi_file_toggled(self.checkBox_DEW_MultiFileStorage.isChecked())

        dew_layout.addWidget(file_group)

        # ── Group 3: DMD文件保存 ──
        path_group = QtWidgets.QGroupBox()
        path_group.setTitle("DMD文件保存")
        path_group.setStyleSheet(self._GRP_STYLE)
        pathFormLayout = QtWidgets.QFormLayout(path_group)
        pathFormLayout.setSpacing(10)
        pathFormLayout.setContentsMargins(16, 24, 16, 12)

        # DMD文件保存路径（通过 SCPI :STORE:FILE:NAME 设置）
        self.lineEdit_DEW_StoreFileName = QtWidgets.QLineEdit()
        self.lineEdit_DEW_StoreFileName.setObjectName("lineEdit_DEW_StoreFileName")
        self.lineEdit_DEW_StoreFileName.setPlaceholderText("如: D:/data/harmonic_test")
        self.lineEdit_DEW_StoreFileName.setFixedWidth(300)
        pathFormLayout.addRow("DMD文件保存:", self.lineEdit_DEW_StoreFileName)

        dew_layout.addWidget(path_group)

        # ── 应用按钮 ──
        self.pushButton_DEW_Apply = QtWidgets.QPushButton("应用")
        self.pushButton_DEW_Apply.setObjectName("pushButton_DEW_Apply")
        self.pushButton_DEW_Apply.setStyleSheet("""
            QPushButton { background-color: #8b5cf6; color: white; border: none; border-radius: 4px;
                          padding: 6px 14px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        dew_layout.addWidget(self.pushButton_DEW_Apply)

        dew_layout.addStretch()
        self._step2Stacked.addWidget(dew_page)   # index 1

        layout.addWidget(self._step2Stacked)

        # ── 顶部模式切换联动 ──
        def _on_mode_changed(btn, checked):
            if checked:
                idx = self._radio_group.id(btn)
                self._step2Stacked.setCurrentIndex(idx)
                self._mode = 'dewetron' if idx == 1 else 'wt3000'

        self._radio_group.buttonToggled.connect(_on_mode_changed)

        # ── 步骤启用复选框联动 ──
        s2_children = [self._step2Stacked]
        def _on_s2_toggled(checked):
            for w in s2_children:
                w.setEnabled(checked)
        self.checkBox_S2.toggled.connect(_on_s2_toggled)
        _on_s2_toggled(self.checkBox_S2.isChecked())

        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # 谐波卡片构建器
    # ══════════════════════════════════════════════
    def _build_harmonic_card(self, spec):
        """构建单个谐波卡片（QGroupBox），用于 timeline 布局。"""
        grp = QtWidgets.QGroupBox()
        grp.setTitle(spec["title"])
        grp.setStyleSheet(self._GRP_STYLE)
        gLayout = QtWidgets.QGridLayout(grp)
        gLayout.setSpacing(8)
        gLayout.setContentsMargins(12, 20, 12, 12)

        # 步骤启用复选框
        step_widget = self._make_checkbox(spec["step_cb"], spec["step_text"], parent=self)
        gLayout.addWidget(step_widget, 0, 0)

        # DC 通道行
        dc_cbs = []
        row_data = [
            (spec["dc1_cb"], "直流电源1"),
            (spec["dc2_cb"], "直流电源2"),
            (spec["dc3_cb"], "直流电源3"),
            (spec["dc4_cb"], "直流电源4"),
        ]
        for c, (name, text) in enumerate(row_data):
            cb = self._make_checkbox(name, text, parent=self)
            dc_cbs.append(cb)
            gLayout.addWidget(cb, 1, c * 2)
            lbl = self._make_label("功率")
            lbl.setObjectName(spec["pwr_lbl"] if c == 0 else f"_pwr_{name}")
            gLayout.addWidget(lbl, 1, c * 2 + 1)

        # PF 输入
        pf_widget = self._make_input(spec["pf_te"], parent=self, default="100")
        gLayout.addWidget(pf_widget, 2, 0)
        pct = self._make_label("%")
        pct.setObjectName(spec["pct_lbl"])
        gLayout.addWidget(pct, 2, 1)

        # 步骤启用 + step1 DC 联动：DC 复选框需同时满足步骤启用且 step1 DC 已勾选
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        def _update_dc_enabled():
            step_on = step_widget.isChecked()
            for i, dc_cb in enumerate(dc_cbs):
                should_enable = step_on and step1_dcs[i].isChecked()
                dc_cb.setEnabled(should_enable)
                dc_cb.setChecked(should_enable)

        def _on_step_toggled(checked):
            _update_dc_enabled()
            pf_widget.setEnabled(checked)
            pct.setEnabled(checked)

        step_widget.toggled.connect(_on_step_toggled)
        for dc_idx, s1dc in enumerate(step1_dcs):
            s1dc.toggled.connect(_update_dc_enabled)
        # 初始化状态
        _on_step_toggled(step_widget.isChecked())

        return grp

    def _build_timing_card(self):
        """构建数据采集设置卡片。"""
        grp = QtWidgets.QGroupBox()
        grp.setTitle("数据采集设置")
        grp.setStyleSheet(self._GRP_STYLE)
        tg = QtWidgets.QGridLayout(grp)
        tg.setSpacing(8)
        tg.setContentsMargins(12, 20, 12, 12)

        tg.addWidget(self._make_label("数据采集:"), 0, 0)
        self.textEdit_S3_TIME_2 = self._make_input("textEdit_S3_TIME_2", parent=self, default="10")
        tg.addWidget(self.textEdit_S3_TIME_2, 0, 1)
        self.comboBox_S3_TIME_2 = self._make_combo("comboBox_S3_TIME_2", ["分钟", "秒", "毫秒"], parent=self)
        tg.addWidget(self.comboBox_S3_TIME_2, 0, 2)

        tg.addWidget(self._make_label("等待时间:"), 0, 3)
        self.textEdit_S3_TIME_3 = self._make_input("textEdit_S3_TIME_3", parent=self, default="1")
        tg.addWidget(self.textEdit_S3_TIME_3, 0, 4)
        self.comboBox_S3_TIME_3 = self._make_combo("comboBox_S3_TIME_3", ["秒", "分钟", "毫秒"], parent=self)
        tg.addWidget(self.comboBox_S3_TIME_3, 0, 5)

        return grp

    # ══════════════════════════════════════════════
    # 谐波设置合并页（timeline + card 布局）
    # ══════════════════════════════════════════════
    def _build_step3_harmonics(self):
        """将 12 个谐波步骤合并为单页，用 timeline + card 展示。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        outer_layout = QtWidgets.QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")

        timeline = TimelineWidget()

        # 数据采集设置卡片
        timing_card = self._build_timing_card()
        timeline.addStep("数据采集设置", timing_card)

        # 12 个谐波卡片
        for spec in _HARMONIC_SPECS:
            card = self._build_harmonic_card(spec)
            timeline.addStep(spec["title"], card)

        timeline.finalize()
        scroll.setWidget(timeline)
        outer_layout.addWidget(scroll)

        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step 4: 关机设置
    # ══════════════════════════════════════════════
    def _build_step13(self):
        """关机设置页面（谐波 12次已移入 timeline 合并页）。"""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp_s = QtWidgets.QGroupBox()
        grp_s.setObjectName("groupBox_shutdown")
        grp_s.setTitle("关机设置")
        grp_s.setStyleSheet(self._GRP_STYLE)
        sg = QtWidgets.QGridLayout(grp_s)
        sg.setSpacing(10)
        sg.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S5 = self._make_checkbox("checkBox_S5", "step14")
        sg.addWidget(self.checkBox_S5, 0, 0)

        # 交流电源关机
        sg.addWidget(self._make_label("交流电源"), 0, 1)
        self.comboBox_S5_AC = self._make_combo("comboBox_S5_AC", ["关闭", "开启"])
        sg.addWidget(self.comboBox_S5_AC, 0, 2)

        # DC 电源关机
        shutdown_widgets = [self.comboBox_S5_AC]
        s5_dc = []
        dc_shutdown = [
            ("checkBox_S5_DC1", "直流电源1", "comboBox_S5_DC1"),
            ("checkBox_S5_DC2", "直流电源2", "comboBox_S5_DC2"),
            ("checkBox_S5_DC3", "直流电源3", "comboBox_S5_DC3"),
            ("checkBox_S5_DC4", "直流电源4", "comboBox_S5_DC4"),
        ]
        for c, (cb_name, cb_text, combo_name) in enumerate(dc_shutdown):
            col = 1 + c * 2
            cb = self._make_checkbox(cb_name, cb_text, parent=self)
            s5_dc.append(cb)
            shutdown_widgets.append(cb)
            sg.addWidget(cb, 1, col)
            combo = self._make_combo(combo_name, ["关闭", "开启"], parent=self)
            shutdown_widgets.append(combo)
            sg.addWidget(combo, 1, col + 1)

        # 步骤启用 + step1 DC 联动
        step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                     self.checkBox_S1_DC3, self.checkBox_S1_DC4]

        def _update_s5_dc():
            step_on = self.checkBox_S5.isChecked()
            for i in range(4):
                should_enable = step_on and step1_dcs[i].isChecked()
                s5_dc[i].setEnabled(should_enable)
                s5_dc[i].setChecked(should_enable)

        def _on_step_toggled(checked):
            _update_s5_dc()
            for w in [self.comboBox_S5_AC]:
                w.setEnabled(checked)

        self.checkBox_S5.toggled.connect(_on_step_toggled)
        for s1dc in step1_dcs:
            s1dc.toggled.connect(_update_s5_dc)
        _on_step_toggled(self.checkBox_S5.isChecked())

        layout.addWidget(grp_s)
        layout.addStretch()

        self.stackedWidget.addWidget(page)

    def retranslateUi(self, Dialog_thaixiebodianliu):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaixiebodianliu.setWindowTitle(_translate("Dialog_thaixiebodianliu", "谐波电流项目配置"))
        self.pushButton_TestAppend.setText(_translate("Dialog_thaixiebodianliu", "测试追加"))
        self.pushButton_SaveSettingFile.setText(_translate("Dialog_thaixiebodianliu", "保存设定"))
        self.pushButton_ReadSettingFile.setText(_translate("Dialog_thaixiebodianliu", "读取设定"))
        self.pushButton_Send.setText(_translate("Dialog_thaixiebodianliu", "提交"))
