# -*- coding: utf-8 -*-
# PU项目配置 - 竖式步骤条布局（手写，非 pyuic5 生成）

from PyQt5 import QtCore, QtGui, QtWidgets

# 全局样式
_QSS_COMMON = """
QTextEdit {
    background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px;
    padding: 2px 4px; font-size: 12px; color: #1e293b;
}
QTextEdit:focus { border-color: #8b5cf6; }
QComboBox {
    background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px;
    padding: 4px 8px; font-size: 12px; color: #1e293b;
}
QComboBox:hover { border-color: #cbd5e1; }
QComboBox::drop-down { border: none; width: 20px; }
QCheckBox { font-size: 12px; color: #1e293b; spacing: 6px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 2px solid #cbd5e1; background: white; }
QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }
QLabel { font-size: 12px; color: #475569; }
QPushButton {
    background-color: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px;
    padding: 6px 12px; font-size: 12px; color: #1e293b;
}
QPushButton:hover { background-color: #e2e8f0; }
"""


class Ui_Dialog_thaitestPU(object):
    def setupUi(self, Dialog_thaitestPU):
        Dialog_thaitestPU.setObjectName("Dialog_thaitestPU")
        Dialog_thaitestPU.resize(1300, 850)
        Dialog_thaitestPU.setMinimumSize(QtCore.QSize(1200, 750))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\ui_files\\logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Dialog_thaitestPU.setWindowIcon(icon)
        Dialog_thaitestPU.setStyleSheet("QDialog { background-color: #f1f5f9; }")

        # ── 主布局 ──
        mainLayout = QtWidgets.QVBoxLayout(Dialog_thaitestPU)
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
        step_titles = ["① AC/DC 电源", "② 功率分析仪+PU", "③ 关机设置"]
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
        self._build_step_shutdown()

        # 默认显示第一页
        self._switch_step(0)

        # ── 隐藏提交按钮（保留 objectName 供兼容） ──
        self.pushButton_Send = QtWidgets.QPushButton()
        self.pushButton_Send.setObjectName("pushButton_Send")
        self.pushButton_Send.setVisible(False)

        self.retranslateUi(Dialog_thaitestPU)
        QtCore.QMetaObject.connectSlotsByName(Dialog_thaitestPU)

    # ══════════════════════════════════════════════
    # 步骤切换
    # ══════════════════════════════════════════════
    def _switch_step(self, index):
        self.stackedWidget.setCurrentIndex(index)
        for i, lbl in enumerate(self._step_labels):
            if i == index:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 8px; font-size: 10px; font-weight: bold; color: #7c3aed;
                        border-bottom: 3px solid #8b5cf6; border-radius: 0;
                        background-color: #f3e8ff;
                    }
                """)
            else:
                lbl.setStyleSheet("""
                    QLabel {
                        padding: 6px 8px; font-size: 10px; color: #64748b;
                        border-bottom: 3px solid transparent; border-radius: 0;
                        background: transparent;
                    }
                    QLabel:hover { background-color: #f1f5f9; }
                """)

    def _group_box_style(self):
        return "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; font-weight: bold; }"

    # ══════════════════════════════════════════════
    # Step 1: AC/DC 电源设置 + 时序
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
        self.groupBox.setStyleSheet(self._group_box_style())
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

        self.label_4 = QtWidgets.QLabel("交流电压1")
        self.label_4.setObjectName("label_4")
        gLayout.addWidget(self.label_4, 0, 3)
        self.textEdit_S1_AC_VOLT = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT.setObjectName("textEdit_S1_AC_VOLT")
        self.textEdit_S1_AC_VOLT.setFixedSize(100, 31)
        gLayout.addWidget(self.textEdit_S1_AC_VOLT, 0, 4)
        self.label_5 = QtWidgets.QLabel("V")
        self.label_5.setObjectName("label_5")
        gLayout.addWidget(self.label_5, 0, 5)

        self.label_113 = QtWidgets.QLabel("交流电压2")
        self.label_113.setObjectName("label_113")
        gLayout.addWidget(self.label_113, 0, 6)
        self.textEdit_S1_AC_VOLT_2 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_2.setAcceptDrops(True)
        self.textEdit_S1_AC_VOLT_2.setUndoRedoEnabled(True)
        self.textEdit_S1_AC_VOLT_2.setReadOnly(False)
        self.textEdit_S1_AC_VOLT_2.setObjectName("textEdit_S1_AC_VOLT_2")
        self.textEdit_S1_AC_VOLT_2.setFixedSize(100, 31)
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_2, 0, 7)
        self.label_107 = QtWidgets.QLabel("V")
        self.label_107.setObjectName("label_107")
        gLayout.addWidget(self.label_107, 0, 8)

        self.label_123 = QtWidgets.QLabel("交流电压3")
        self.label_123.setObjectName("label_123")
        gLayout.addWidget(self.label_123, 0, 9)
        self.textEdit_S1_AC_VOLT_3 = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_VOLT_3.setReadOnly(False)
        self.textEdit_S1_AC_VOLT_3.setObjectName("textEdit_S1_AC_VOLT_3")
        self.textEdit_S1_AC_VOLT_3.setFixedSize(100, 31)
        gLayout.addWidget(self.textEdit_S1_AC_VOLT_3, 0, 10)
        self.label_102 = QtWidgets.QLabel("V")
        self.label_102.setObjectName("label_102")
        gLayout.addWidget(self.label_102, 0, 11)

        self.label_19 = QtWidgets.QLabel("频率")
        self.label_19.setObjectName("label_19")
        gLayout.addWidget(self.label_19, 0, 12)
        self.textEdit_S1_AC_FR = QtWidgets.QTextEdit()
        self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
        self.textEdit_S1_AC_FR.setFixedSize(100, 31)
        gLayout.addWidget(self.textEdit_S1_AC_FR, 0, 13)
        self.label_18 = QtWidgets.QLabel("Hz")
        self.label_18.setObjectName("label_18")
        gLayout.addWidget(self.label_18, 0, 14)

        self.comboBox_S1_AC = QtWidgets.QComboBox()
        self.comboBox_S1_AC.setObjectName("comboBox_S1_AC")
        self.comboBox_S1_AC.addItems(["开启", "关闭"])
        self.comboBox_S1_AC.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S1_AC, 1, 3, 1, 2)

        self.comboBox_S1_AC_2 = QtWidgets.QComboBox()
        self.comboBox_S1_AC_2.setObjectName("comboBox_S1_AC_2")
        self.comboBox_S1_AC_2.addItems(["单相", "三相"])
        self.comboBox_S1_AC_2.setFixedWidth(120)
        gLayout.addWidget(self.comboBox_S1_AC_2, 1, 6, 1, 2)

        layout.addWidget(self.groupBox)

        # ── DC 电源组 (4 channels) ──
        self.groupBox_2 = QtWidgets.QGroupBox()
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("直流电源设置")
        self.groupBox_2.setStyleSheet(self._group_box_style())
        g2 = QtWidgets.QGridLayout(self.groupBox_2)
        g2.setSpacing(6)
        g2.setContentsMargins(12, 20, 12, 12)

        # Header
        headers = ["通道", "开关", "Vmp", "Imp", "Voc", "Isc", "功率"]
        for c, h in enumerate(headers):
            lbl = QtWidgets.QLabel(h)
            lbl.setStyleSheet("font-weight: bold; color: #475569;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            g2.addWidget(lbl, 0, c)

        dc_cfg = [
            ("checkBox_S1_DC1", "直流电源1", "comboBox_S1_DC1",
             ["textEdit_S1_DC1_VOLT", "textEdit_S1_DC1_CURR", "textEdit_S1_DC1_Voc",
              "textEdit_S1_DC1_Isc", "textEdit_S1_DC1_PF"]),
            ("checkBox_S1_DC2", "直流电源2", "comboBox_S1_DC2",
             ["textEdit_S1_DC2_VOLT", "textEdit_S1_DC2_CURR", "textEdit_S1_DC2_Voc",
              "textEdit_S1_DC2_Isc", "textEdit_S1_DC2_PF"]),
            ("checkBox_S1_DC3", "直流电源3", "comboBox_S1_DC3",
             ["textEdit_S1_DC3_VOLT", "textEdit_S1_DC3_CURR", "textEdit_S1_DC3_Voc",
              "textEdit_S1_DC3_Isc", "textEdit_S1_DC3_PF"]),
            ("checkBox_S1_DC4", "直流电源4", "comboBox_S1_DC4",
             ["textEdit_S1_DC4_VOLT", "textEdit_S1_DC4_CURR", "textEdit_S1_DC4_Voc",
              "textEdit_S1_DC4_Isc", "textEdit_S1_DC4_PF"]),
        ]
        for r, (cb_name, cb_text, combo_name, te_names) in enumerate(dc_cfg, start=1):
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g2.addWidget(cb, r, 0)
            setattr(self, cb_name, cb)
            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["开启", "关闭"])
            combo.setFixedWidth(100)
            g2.addWidget(combo, r, 1)
            setattr(self, combo_name, combo)
            for c, te_name in enumerate(te_names, start=2):
                te = QtWidgets.QTextEdit()
                te.setObjectName(te_name)
                te.setFixedSize(80, 28)
                g2.addWidget(te, r, c)
                setattr(self, te_name, te)

        layout.addWidget(self.groupBox_2)

        # ── 时序组 ──
        self.groupBox_4 = QtWidgets.QGroupBox()
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("时序设置")
        self.groupBox_4.setStyleSheet(self._group_box_style())
        g4 = QtWidgets.QGridLayout(self.groupBox_4)
        g4.setSpacing(8)
        g4.setContentsMargins(12, 20, 12, 12)

        self.label_131 = QtWidgets.QLabel("等待时间:")
        self.label_131.setObjectName("label_131")
        g4.addWidget(self.label_131, 0, 0)
        self.textEdit_S1_ACWaitTIME = QtWidgets.QTextEdit()
        self.textEdit_S1_ACWaitTIME.setObjectName("textEdit_S1_ACWaitTIME")
        self.textEdit_S1_ACWaitTIME.setFixedSize(100, 31)
        g4.addWidget(self.textEdit_S1_ACWaitTIME, 0, 1)
        self.comboBox_S1_ACWaitTIME = QtWidgets.QComboBox()
        self.comboBox_S1_ACWaitTIME.setObjectName("comboBox_S1_ACWaitTIME")
        self.comboBox_S1_ACWaitTIME.addItems(["秒", "分钟", "毫秒"])
        self.comboBox_S1_ACWaitTIME.setFixedWidth(120)
        g4.addWidget(self.comboBox_S1_ACWaitTIME, 0, 2)

        self.label_132 = QtWidgets.QLabel("启机时间:")
        self.label_132.setObjectName("label_132")
        g4.addWidget(self.label_132, 0, 3)
        self.textEdit_S1_TIME = QtWidgets.QTextEdit()
        self.textEdit_S1_TIME.setObjectName("textEdit_S1_TIME")
        self.textEdit_S1_TIME.setFixedSize(100, 31)
        g4.addWidget(self.textEdit_S1_TIME, 0, 4)
        self.comboBox_S1_TIME = QtWidgets.QComboBox()
        self.comboBox_S1_TIME.setObjectName("comboBox_S1_TIME")
        self.comboBox_S1_TIME.addItems(["分钟", "秒", "毫秒"])
        self.comboBox_S1_TIME.setFixedWidth(120)
        g4.addWidget(self.comboBox_S1_TIME, 0, 5)

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
        self.groupBox_5.setStyleSheet(self._group_box_style())
        g5 = QtWidgets.QGridLayout(self.groupBox_5)
        g5.setSpacing(10)
        g5.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S2 = QtWidgets.QCheckBox("step2")
        self.checkBox_S2.setChecked(True)
        self.checkBox_S2.setObjectName("checkBox_S2")
        g5.addWidget(self.checkBox_S2, 0, 0, 1, 2)

        self.checkBox_S2_WT3000 = QtWidgets.QCheckBox("WT3000")
        self.checkBox_S2_WT3000.setChecked(True)
        self.checkBox_S2_WT3000.setObjectName("checkBox_S2_WT3000")
        g5.addWidget(self.checkBox_S2_WT3000, 0, 2)
        self.pushButton_S2_WT_3000_CONFIG = QtWidgets.QPushButton("WT_3000_config")
        self.pushButton_S2_WT_3000_CONFIG.setObjectName("pushButton_S2_WT_3000_CONFIG")
        g5.addWidget(self.pushButton_S2_WT_3000_CONFIG, 0, 3)

        self.checkBox_S2_WT1800 = QtWidgets.QCheckBox("WT1800")
        self.checkBox_S2_WT1800.setChecked(True)
        self.checkBox_S2_WT1800.setObjectName("checkBox_S2_WT1800")
        g5.addWidget(self.checkBox_S2_WT1800, 0, 4)
        self.pushButton_S2_WT_1800_CONFIG = QtWidgets.QPushButton("WT_1800_config")
        self.pushButton_S2_WT_1800_CONFIG.setObjectName("pushButton_S2_WT_1800_CONFIG")
        g5.addWidget(self.pushButton_S2_WT_1800_CONFIG, 0, 5)

        self.checkBox_S2_WT1806E = QtWidgets.QCheckBox("WT1806E")
        self.checkBox_S2_WT1806E.setChecked(True)
        self.checkBox_S2_WT1806E.setObjectName("checkBox_S2_WT1806E")
        g5.addWidget(self.checkBox_S2_WT1806E, 1, 2)
        self.pushButton_S2_WT_1806E_CONFIG = QtWidgets.QPushButton("WT_1806E_config")
        self.pushButton_S2_WT_1806E_CONFIG.setObjectName("pushButton_S2_WT_1806E_CONFIG")
        g5.addWidget(self.pushButton_S2_WT_1806E_CONFIG, 1, 3)

        self.checkBox_S2_WT5000 = QtWidgets.QCheckBox("WT5000")
        self.checkBox_S2_WT5000.setChecked(True)
        self.checkBox_S2_WT5000.setObjectName("checkBox_S2_WT5000")
        g5.addWidget(self.checkBox_S2_WT5000, 1, 4)
        self.pushButton_S2_WT_5000_CONFIG = QtWidgets.QPushButton("WT_5000_config")
        self.pushButton_S2_WT_5000_CONFIG.setObjectName("pushButton_S2_WT_5000_CONFIG")
        g5.addWidget(self.pushButton_S2_WT_5000_CONFIG, 1, 5)

        layout.addWidget(self.groupBox_5)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # PU 步骤（3-22）：固定交流电压 + 数据采集时间
    # ══════════════════════════════════════════════
    def _build_pu_step(self, n):
        """
        构建 PU n 的页面。n = 3..22 对应 step3..step22。
        每页包含：checkBox_SN、交流电压输入、数据采集时间输入。
        """
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        groupBox = QtWidgets.QGroupBox()
        groupBox.setObjectName(f"groupBox_PU{n}")
        groupBox.setTitle(f"PU {n - 2} 设置")
        groupBox.setStyleSheet(self._group_box_style())
        gLayout = QtWidgets.QGridLayout(groupBox)
        gLayout.setSpacing(10)
        gLayout.setContentsMargins(16, 24, 16, 12)

        # checkbox
        checkBox = QtWidgets.QCheckBox(f"step{n}")
        checkBox.setChecked(True)
        checkBox.setObjectName(f"checkBox_S{n}")
        gLayout.addWidget(checkBox, 0, 0)
        setattr(self, f"checkBox_S{n}", checkBox)

        # 交流电压
        lbl_volt = QtWidgets.QLabel("交流电压")
        lbl_volt.setObjectName(f"label_{n * 10 + 1}")
        gLayout.addWidget(lbl_volt, 0, 1)
        textEdit_ac_volt = QtWidgets.QTextEdit()
        textEdit_ac_volt.setObjectName(f"textEdit_S{n}_AC_VOLT")
        textEdit_ac_volt.setFixedSize(100, 31)
        gLayout.addWidget(textEdit_ac_volt, 0, 2)
        setattr(self, f"textEdit_S{n}_AC_VOLT", textEdit_ac_volt)
        lbl_v = QtWidgets.QLabel("V")
        lbl_v.setObjectName(f"label_{n * 10 + 2}")
        gLayout.addWidget(lbl_v, 0, 3)

        # 数据采集时间
        lbl_time = QtWidgets.QLabel("数据采集")
        lbl_time.setObjectName(f"label_{n * 10 + 3}")
        gLayout.addWidget(lbl_time, 1, 1)
        textEdit_time = QtWidgets.QTextEdit()
        textEdit_time.setObjectName(f"textEdit_S{n}_TIME")
        textEdit_time.setFixedSize(100, 31)
        gLayout.addWidget(textEdit_time, 1, 2)
        setattr(self, f"textEdit_S{n}_TIME", textEdit_time)
        comboBox_time = QtWidgets.QComboBox()
        comboBox_time.setObjectName(f"comboBox_S{n}_TIME")
        comboBox_time.addItems(["秒", "毫秒", "分钟"])
        comboBox_time.setFixedWidth(120)
        gLayout.addWidget(comboBox_time, 1, 3)
        setattr(self, f"comboBox_S{n}_TIME", comboBox_time)

        layout.addWidget(groupBox)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    # ══════════════════════════════════════════════
    # Step last: 关机设置
    # ══════════════════════════════════════════════
    def _build_step_shutdown(self):
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.groupBox_11 = QtWidgets.QGroupBox()
        self.groupBox_11.setObjectName("groupBox_11")
        self.groupBox_11.setTitle("关机设置")
        self.groupBox_11.setStyleSheet(self._group_box_style())
        g11 = QtWidgets.QGridLayout(self.groupBox_11)
        g11.setSpacing(10)
        g11.setContentsMargins(16, 24, 16, 12)

        self.checkBox_S_End = QtWidgets.QCheckBox("step_last")
        self.checkBox_S_End.setChecked(True)
        self.checkBox_S_End.setObjectName("checkBox_S_End")
        g11.addWidget(self.checkBox_S_End, 0, 0, 1, 2)

        self.label_8 = QtWidgets.QLabel("交流电源")
        self.label_8.setObjectName("label_8")
        g11.addWidget(self.label_8, 0, 2)
        self.comboBox_S_End_AC = QtWidgets.QComboBox()
        self.comboBox_S_End_AC.setObjectName("comboBox_S_End_AC")
        self.comboBox_S_End_AC.addItems(["关闭", "开启"])
        self.comboBox_S_End_AC.setFixedWidth(120)
        g11.addWidget(self.comboBox_S_End_AC, 0, 3)

        # DC 电源 1-4
        dc_end_cfg = [
            ("checkBox_S_End_DC1", "直流电源1", "comboBox_S_End_DC1"),
            ("checkBox_S_End_DC2", "直流电源2", "comboBox_S_End_DC2"),
            ("checkBox_S_End_DC3", "直流电源3", "comboBox_S_End_DC3"),
            ("checkBox_S_End_DC4", "直流电源4", "comboBox_S_End_DC4"),
        ]
        for c, (cb_name, cb_text, combo_name) in enumerate(dc_end_cfg):
            col = c * 2
            cb = QtWidgets.QCheckBox(cb_text)
            cb.setChecked(True)
            cb.setObjectName(cb_name)
            g11.addWidget(cb, 1, col)
            setattr(self, cb_name, cb)
            combo = QtWidgets.QComboBox()
            combo.setObjectName(combo_name)
            combo.addItems(["关闭", "开启"])
            combo.setFixedWidth(120)
            g11.addWidget(combo, 1, col + 1)
            setattr(self, combo_name, combo)

        layout.addWidget(self.groupBox_11)
        layout.addStretch()
        self.stackedWidget.addWidget(page)

    def retranslateUi(self, Dialog_thaitestPU):
        _translate = QtCore.QCoreApplication.translate
        Dialog_thaitestPU.setWindowTitle(
            _translate("Dialog_thaitestPU", "PU项目配置")
        )
        self.pushButton_TestAppend.setText(
            _translate("Dialog_thaitestPU", "测试追加")
        )
        self.pushButton_SaveSettingFile.setText(
            _translate("Dialog_thaitestPU", "保存设定")
        )
        self.pushButton_ReadSettingFile.setText(
            _translate("Dialog_thaitestPU", "读取设定")
        )
        self.pushButton_Send.setText(
            _translate("Dialog_thaitestPU", "提交")
        )
