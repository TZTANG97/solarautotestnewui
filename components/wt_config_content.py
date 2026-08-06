# -*- coding: utf-8 -*-
"""
功率分析仪配置内容构建器
为各测试项目的 step2 提供嵌入式 WT 配置 UI，替代独立弹窗。
所有 widget objectName 保持不变，确保 SCPITestWave.py 和 Open_Save 兼容。
"""

from PyQt5 import QtWidgets

# ── 样式常量（与 Dialog_thaiWT3000E.py 一致）──────────────────────────────
_COMBO_STYLE = (
    "QComboBox { border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px 8px; "
    "font-size: 12px; background: white; min-height: 24px; }"
    "QComboBox::drop-down { border: none; width: 20px; }"
    "QComboBox::down-arrow { image: none; border-left: 5px solid transparent; "
    "border-right: 5px solid transparent; border-top: 6px solid #64748b; margin-right: 6px; }"
    "QComboBox QAbstractItemView { border: 1px solid #cbd5e1; selection-background-color: #ede9fe; "
    "selection-color: #1e1b4b; }"
)
_TEXTEDIT_STYLE = (
    "QTextEdit { border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px; "
    "font-size: 12px; background: white; }"
)
_GROUPBOX_STYLE = (
    "QGroupBox { border: 1px solid #e2e8f0; border-radius: 6px; padding-top: 8px; "
    "font-weight: bold; font-size: 13px; margin-top: 6px; }"
    "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }"
)
_LABEL_STYLE = "font-size: 12px; color: #475569;"
_CHECKBOX_STYLE = (
    "QCheckBox { spacing: 6px; font-size: 12px; }"
    "QCheckBox::indicator { width: 16px; height: 16px; border: 2px solid #cbd5e1; border-radius: 3px; }"
    "QCheckBox::indicator:checked { background-color: #8b5cf6; border-color: #8b5cf6; }"
)


def _make_cb(parent, name, text, checked=False):
    """创建 QCheckBox 并 setattr 到 parent。"""
    cb = QtWidgets.QCheckBox(text)
    cb.setChecked(checked)
    cb.setObjectName(name)
    cb.setStyleSheet(_CHECKBOX_STYLE)
    setattr(parent, name, cb)
    return cb


def _make_combo(parent, name, items, width=120):
    """创建 QComboBox 并 setattr 到 parent。"""
    combo = QtWidgets.QComboBox()
    combo.setObjectName(name)
    combo.addItems(items)
    combo.setFixedWidth(width)
    combo.setStyleSheet(_COMBO_STYLE)
    setattr(parent, name, combo)
    return combo


def _make_te(parent, name, html_text="", max_h=36):
    """创建 QTextEdit 并 setattr 到 parent。"""
    te = QtWidgets.QTextEdit()
    te.setObjectName(name)
    te.setStyleSheet(_TEXTEDIT_STYLE)
    te.setMaximumHeight(max_h)
    if html_text:
        te.setHtml(html_text)
    setattr(parent, name, te)
    return te


def _make_lbl(text):
    """创建 QLabel。"""
    lbl = QtWidgets.QLabel(text)
    lbl.setStyleSheet(_LABEL_STYLE)
    return lbl


# ═══════════════════════════════════════════════════════════════════════════
# WT3000E 配置内容
# ═══════════════════════════════════════════════════════════════════════════
def build_wt3000_content(parent):
    """构建 WT3000E 配置内容（不含顶部按钮栏），返回 QScrollArea。"""
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet(
        "QScrollArea { border: none; background-color: white; }"
        "QScrollBar:vertical { background: #f1f5f9; width: 10px; }"
        "QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 5px; min-height: 30px; }"
        "QScrollBar::handle:vertical:hover { background: #94a3b8; }"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
    )
    cw = QtWidgets.QWidget()
    cw.setStyleSheet("background-color: white;")
    cl = QtWidgets.QVBoxLayout(cw)
    cl.setContentsMargins(16, 16, 16, 16)
    cl.setSpacing(12)

    # ── 基本设置 ──
    basicGrp = QtWidgets.QGroupBox("基本设置")
    basicGrp.setStyleSheet(_GROUPBOX_STYLE)
    bl = QtWidgets.QHBoxLayout(basicGrp)
    bl.setSpacing(12)
    bl.setContentsMargins(12, 12, 12, 12)

    # 接线方式
    wireGrp = QtWidgets.QGroupBox("接线方式")
    wireGrp.setObjectName("groupBox_3")
    wg = QtWidgets.QGridLayout(wireGrp)
    wg.setSpacing(6)
    wg.setContentsMargins(8, 16, 8, 8)

    for r, (lbl_text, c1_items, c2_items) in enumerate([
        ("SigmaA:", ["---", "1P3W", "3P3W", "3P4W", "3V3A"], ["Element1", "Element2", "Element3", "Element4"]),
        ("SigmaB:", ["---", "1P3W", "3P3W", "3P4W", "3V3A"], ["Element1", "Element2", "Element3", "Element4"]),
    ]):
        wg.addWidget(_make_lbl(lbl_text), r, 0)
        _make_combo(parent, f"comboBox_SigmA{'1' if r==0 else '2'}" if r==0 else f"comboBox_SigmB{'1' if r==0 else '2'}", c1_items)
        # 修正：SigmaA 用 SigmA1/A2，SigmaB 用 SigmB1/B2
    # 手动构建 SigmaA 行
    wg.addWidget(_make_lbl("SigmaA:"), 0, 0)
    _make_combo(parent, "comboBox_SigmA1", ["---", "1P3W", "3P3W", "3P4W", "3V3A"])
    wg.addWidget(parent.comboBox_SigmA1, 0, 1)
    _make_combo(parent, "comboBox_SigmA2", ["Element1", "Element2", "Element3", "Element4"])
    wg.addWidget(parent.comboBox_SigmA2, 0, 2)

    wg.addWidget(_make_lbl("SigmaB:"), 1, 0)
    _make_combo(parent, "comboBox_SigmB1", ["---", "1P3W", "3P3W", "3P4W", "3V3A"])
    wg.addWidget(parent.comboBox_SigmB1, 1, 1)
    _make_combo(parent, "comboBox_SigmB2", ["Element1", "Element2", "Element3", "Element4"])
    wg.addWidget(parent.comboBox_SigmB2, 1, 2)

    wg.addWidget(_make_lbl("单元独立设置:"), 2, 0)
    _make_combo(parent, "comboBox_UnitSet", ["OFF", "ON"])
    wg.addWidget(parent.comboBox_UnitSet, 2, 1)

    wg.addWidget(_make_lbl("接线补偿:"), 3, 0)
    _make_combo(parent, "comboBox_WiringCom", ["OFF", "U_I", "I_U"])
    wg.addWidget(parent.comboBox_WiringCom, 3, 1)

    # groupBox_12 (backward compat)
    g12 = QtWidgets.QGroupBox(wireGrp)
    g12.setObjectName("groupBox_12")
    g12.setMinimumHeight(0)
    g12.setMaximumHeight(0)

    bl.addWidget(wireGrp)

    # 更新率 + 项目数
    rightCol = QtWidgets.QVBoxLayout()
    rightCol.setSpacing(8)

    urGrp = QtWidgets.QGroupBox("")
    urGrp.setObjectName("groupBox_11")
    urLay = QtWidgets.QVBoxLayout(urGrp)
    urLay.setSpacing(4)
    urLay.setContentsMargins(8, 8, 8, 8)
    urLay.addWidget(_make_lbl("更新率:"))
    _make_combo(parent, "comboBox_ReplaceRate", ["50ms", "100ms", "250ms", "500ms", "1s", "2s", "5s", "10s", "20s"])
    urLay.addWidget(parent.comboBox_ReplaceRate)
    rightCol.addWidget(urGrp)

    projGrp = QtWidgets.QGroupBox("")
    projGrp.setObjectName("groupBox_13")
    pjLay = QtWidgets.QVBoxLayout(projGrp)
    pjLay.setSpacing(4)
    pjLay.setContentsMargins(8, 8, 8, 8)
    pjLay.addWidget(_make_lbl("项目数:"))
    _make_combo(parent, "comboBox_ProjectNum", ["12", "24", "48", "200"])
    pjLay.addWidget(parent.comboBox_ProjectNum)
    rightCol.addWidget(projGrp)

    bl.addLayout(rightCol)
    cl.addWidget(basicGrp)

    # ── 保存设置 ──
    saveGrp = QtWidgets.QGroupBox("保存设置")
    saveGrp.setStyleSheet(_GROUPBOX_STYLE)
    sg = QtWidgets.QGridLayout(saveGrp)
    sg.setSpacing(8)
    sg.setContentsMargins(12, 12, 12, 12)

    # 自动保存 + 停机时间
    g6 = QtWidgets.QGroupBox("")
    g6.setObjectName("groupBox_6")
    g6l = QtWidgets.QGridLayout(g6)
    g6l.setSpacing(4)
    g6l.setContentsMargins(8, 8, 8, 8)
    g6l.addWidget(_make_lbl("自动保存:"), 0, 0)
    _make_combo(parent, "comboBox_AutoSave", ["OFF", "自动保存", "手动保存"])
    # 旧独立弹窗默认「自动保存」且曾被禁用；内嵌后需可改，并默认开启以免测量不落盘
    parent.comboBox_AutoSave.setCurrentIndex(1)
    g6l.addWidget(parent.comboBox_AutoSave, 0, 1)
    g6l.addWidget(_make_lbl("停机时间:"), 1, 0)
    _make_te(parent, "textEdit_StopTime", '<p align="center"><span style="font-size:9pt;">00:05:00</span></p>')
    g6l.addWidget(parent.textEdit_StopTime, 1, 1)
    sg.addWidget(g6, 0, 0)

    # 保存路径
    g15 = QtWidgets.QGroupBox("")
    g15.setObjectName("groupBox_15")
    g15l = QtWidgets.QVBoxLayout(g15)
    g15l.setSpacing(4)
    g15l.setContentsMargins(8, 8, 8, 8)
    pr = QtWidgets.QHBoxLayout()
    pr.addWidget(_make_lbl("保存路径:"))
    _make_te(parent, "textEdit_SavePath", '<p><span style="font-size:9pt;">D:\\EnergyTest\\wt_file_save_path</span></p>')
    pr.addWidget(parent.textEdit_SavePath)
    g15l.addLayout(pr)
    cb_auto = QtWidgets.QCheckBox("自动命名")
    cb_auto.setObjectName("checkBox_AutoName")
    cb_auto.setEnabled(False)
    cb_auto.setCheckable(False)
    cb_auto.setChecked(False)
    cb_auto.setStyleSheet(_CHECKBOX_STYLE)
    setattr(parent, "checkBox_AutoName", cb_auto)
    g15l.addWidget(cb_auto)
    sg.addWidget(g15, 0, 1)

    # 文件名列表
    g7 = QtWidgets.QGroupBox("")
    g7.setObjectName("groupBox_7")
    g7l = QtWidgets.QVBoxLayout(g7)
    g7l.setSpacing(4)
    g7l.setContentsMargins(8, 8, 8, 8)
    g7l.addWidget(_make_lbl("文件名列表:"))
    _make_te(parent, "textEdit_FileNameList",
             '<p><span style="font-size:9pt;">100%_ambient,100%_+55,100%_-10,66%_ambient,66%_+55,66%_-10,33%_ambient,33%_+55,33%_-10,100%_ambient</span></p>',
             max_h=120)
    g7l.addWidget(parent.textEdit_FileNameList)
    sg.addWidget(g7, 0, 2)

    cl.addWidget(saveGrp)

    # ── 测量项目 - 基本量 ──
    bmGrp = QtWidgets.QGroupBox("测量项目 - 基本量")
    bmGrp.setStyleSheet(_GROUPBOX_STYLE)
    bm = QtWidgets.QGridLayout(bmGrp)
    bm.setSpacing(6)
    bm.setContentsMargins(12, 12, 12, 12)

    # Element
    bm.addWidget(_make_lbl("Element:"), 0, 0)
    for i in range(1, 5):
        _make_cb(parent, f"checkBox_SetElement{i}", f"Element{i}")
        bm.addWidget(getattr(parent, f"checkBox_SetElement{i}"), 0, i)

    # Sigma
    bm.addWidget(_make_lbl("Sigma:"), 1, 0)
    for name in ["checkBox_SetSigma", "checkBox_SetSigmaA", "checkBox_SetSigmaB"]:
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 1, ["checkBox_SetSigma", "checkBox_SetSigmaA", "checkBox_SetSigmaB"].index(name) + 1)

    # U
    bm.addWidget(_make_lbl("电压 U:"), 2, 0)
    for i, name in enumerate(["checkBox_SetU", "checkBox_SetUrange", "checkBox_SetCfU"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 2, i + 1)

    # I
    bm.addWidget(_make_lbl("电流 I:"), 3, 0)
    for i, name in enumerate(["checkBox_SetI", "checkBox_SetIrange", "checkBox_SetCfI"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 3, i + 1)

    # Peak
    bm.addWidget(_make_lbl("峰值:"), 4, 0)
    for i, name in enumerate(["checkBox_SetUppeak", "checkBox_SetUmpeak", "checkBox_SetIppeak", "checkBox_SetImpeak"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 4, i + 1)

    # Power
    bm.addWidget(_make_lbl("功率:"), 5, 0)
    for i, name in enumerate(["checkBox_SetP", "checkBox_SetS", "checkBox_SetQ", "checkBox_SetLambda", "checkBox_SetPhi", "checkBox_SetPc"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 5, i + 1)

    # Freq
    bm.addWidget(_make_lbl("频率:"), 6, 0)
    for i, name in enumerate(["checkBox_SetFreqU", "checkBox_SetFreqI"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 6, i + 1)

    cl.addWidget(bmGrp)

    # ── 测量项目 - 功率/能量/效率 ──
    peGrp = QtWidgets.QGroupBox("测量项目 - 功率/能量/效率")
    peGrp.setStyleSheet(_GROUPBOX_STYLE)
    pe = QtWidgets.QGridLayout(peGrp)
    pe.setSpacing(6)
    pe.setContentsMargins(12, 12, 12, 12)

    pe.addWidget(_make_lbl("时间:"), 0, 0)
    _make_cb(parent, "checkBox_SetTime", "Time")
    pe.addWidget(parent.checkBox_SetTime, 0, 1)

    pe.addWidget(_make_lbl("有功功率:"), 1, 0)
    for i, name in enumerate(["checkBox_SetWP", "checkBox_SetWPPlus", "checkBox_SetWPMinus"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 1, i + 1)

    pe.addWidget(_make_lbl("无功功率:"), 2, 0)
    for i, name in enumerate(["checkBox_Setq", "checkBox_SetqPlus", "checkBox_SetqMinus"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 2, i + 1)

    pe.addWidget(_make_lbl("视在功率/电能:"), 3, 0)
    for i, name in enumerate(["checkBox_SetWS", "checkBox_SetWQ"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 3, i + 1)

    pe.addWidget(_make_lbl("效率:"), 4, 0)
    for i in range(1, 5):
        _make_cb(parent, f"checkBox_SetEta{i}", f"Eta{i}")
        pe.addWidget(getattr(parent, f"checkBox_SetEta{i}"), 4, i)

    cl.addWidget(peGrp)

    # ── 测量项目 - 谐波量 ──
    harmGrp = QtWidgets.QGroupBox("测量项目 - 谐波量")
    harmGrp.setStyleSheet(_GROUPBOX_STYLE)
    hm = QtWidgets.QGridLayout(harmGrp)
    hm.setSpacing(6)
    hm.setContentsMargins(12, 12, 12, 12)

    harm_items = [
        ("Uk/Ik/Pk:", ["checkBox_SetUk", "checkBox_SetIk", "checkBox_SetPk"]),
        ("Sk/Qk/PFk:", ["checkBox_SetSk", "checkBox_SetQk", "checkBox_SetPFk"]),
        ("Phik/PhiUk/PhiIk:", ["checkBox_SetPhik", "checkBox_SetPhiUk", "checkBox_SetPhiIk"]),
        ("Uhdfk/Ihdfk/Phdfk:", ["checkBox_SetUhdfk", "checkBox_SetIhdfk", "checkBox_SetPhdfk"]),
        ("Zk/Rsk/Rpk:", ["checkBox_SetZk", "checkBox_SetRsk", "checkBox_SetRpk"]),
        ("Xsk/Xpk:", ["checkBox_SetXsk", "checkBox_SetXpk"]),
    ]
    for r, (lbl_text, names) in enumerate(harm_items):
        hm.addWidget(_make_lbl(lbl_text), r, 0)
        for c, name in enumerate(names):
            _make_cb(parent, name, name.replace("checkBox_Set", ""))
            hm.addWidget(getattr(parent, name), r, c + 1)

    # Start / Stop
    hm.addWidget(_make_lbl("开始:"), 7, 0)
    _make_te(parent, "textEdit_SetStart", max_h=32)
    getattr(parent, "textEdit_SetStart").setMaximumWidth(100)
    hm.addWidget(getattr(parent, "textEdit_SetStart"), 7, 1)
    hm.addWidget(_make_lbl("结束:"), 7, 2)
    _make_te(parent, "textEdit_SetStop", max_h=32)
    getattr(parent, "textEdit_SetStop").setMaximumWidth(100)
    hm.addWidget(getattr(parent, "textEdit_SetStop"), 7, 3)

    cl.addWidget(harmGrp)

    # ── 测量项目 - THD 及其他 ──
    thdGrp = QtWidgets.QGroupBox("测量项目 - THD 及其他")
    thdGrp.setStyleSheet(_GROUPBOX_STYLE)
    td = QtWidgets.QGridLayout(thdGrp)
    td.setSpacing(6)
    td.setContentsMargins(12, 12, 12, 12)

    thd_items = [
        ("THD:", ["checkBox_SetUthd", "checkBox_SetIthd", "checkBox_SetPthd"]),
        ("THF:", ["checkBox_SetUthf", "checkBox_SetIthf"]),
        ("TIF:", ["checkBox_SetUtif", "checkBox_SetItif"]),
        ("HVF/HCF:", ["checkBox_Sethvf", "checkBox_Sethcf"]),
        ("相位差:", ["checkBox_SetPhiUi_Uj", "checkBox_SetPhiUi_Uk", "checkBox_SetPhiUi_Ii", "checkBox_SetPhiUi_Ij", "checkBox_SetPhiUi_Ik"]),
        ("电机:", ["checkBox_SetSpeed", "checkBox_SetTorque", "checkBox_SetSyncSp", "checkBox_SetSlip", "checkBox_SetPm"]),
        ("DeltaF:", ["checkBox_SetDeltaF1", "checkBox_SetDeltaF2", "checkBox_SetDeltaF3", "checkBox_SetDeltaF4"]),
    ]
    for r, (lbl_text, names) in enumerate(thd_items):
        td.addWidget(_make_lbl(lbl_text), r, 0)
        for c, name in enumerate(names):
            _make_cb(parent, name, name.replace("checkBox_Set", ""))
            td.addWidget(getattr(parent, name), r, c + 1)

    cl.addWidget(thdGrp)

    # ── F Function ──
    fGrp = QtWidgets.QGroupBox("F Function 选择")
    fGrp.setStyleSheet(_GROUPBOX_STYLE)
    fg = QtWidgets.QGridLayout(fGrp)
    fg.setSpacing(4)
    fg.setContentsMargins(12, 12, 12, 12)

    for i in range(1, 21):
        name = f"checkBox_SetF{i:02d}"
        _make_cb(parent, name, f"F{i:02d}")
        fg.addWidget(getattr(parent, name), (i - 1) // 5, (i - 1) % 5)

    cl.addWidget(fGrp)
    cl.addStretch()

    scroll.setWidget(cw)
    return scroll


# ═══════════════════════════════════════════════════════════════════════════
# WT1800 配置内容
# ═══════════════════════════════════════════════════════════════════════════
def build_wt1800_content(parent):
    """构建 WT1800 配置内容（不含顶部按钮栏），返回 QScrollArea。"""
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet(
        "QScrollArea { border: none; background-color: white; }"
        "QScrollBar:vertical { background: #f1f5f9; width: 10px; }"
        "QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 5px; min-height: 30px; }"
        "QScrollBar::handle:vertical:hover { background: #94a3b8; }"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
    )
    cw = QtWidgets.QWidget()
    cw.setStyleSheet("background-color: white;")
    cl = QtWidgets.QVBoxLayout(cw)
    cl.setContentsMargins(16, 16, 16, 16)
    cl.setSpacing(12)

    # ── 基本设置 ──
    basicGrp = QtWidgets.QGroupBox("基本设置")
    basicGrp.setStyleSheet(_GROUPBOX_STYLE)
    bl = QtWidgets.QHBoxLayout(basicGrp)
    bl.setSpacing(12)
    bl.setContentsMargins(12, 12, 12, 12)

    # 接线方式 (3 rows: SigmaA, SigmaB, SigmaC)
    wireGrp = QtWidgets.QGroupBox("接线方式")
    wireGrp.setObjectName("groupBox_3")
    wg = QtWidgets.QGridLayout(wireGrp)
    wg.setSpacing(6)
    wg.setContentsMargins(8, 16, 8, 8)

    for r, (prefix, lbl_text) in enumerate([("A", "SigmaA:"), ("B", "SigmaB:"), ("C", "SigmaC:")]):
        wg.addWidget(_make_lbl(lbl_text), r, 0)
        _make_combo(parent, f"comboBox_Sigm{prefix}1", ["---", "1P3W", "3P3W", "3P4W", "3V3A"])
        wg.addWidget(getattr(parent, f"comboBox_Sigm{prefix}1"), r, 1)
        _make_combo(parent, f"comboBox_Sigm{prefix}2", ["Element1", "Element2", "Element3", "Element4", "Element5", "Element6"])
        wg.addWidget(getattr(parent, f"comboBox_Sigm{prefix}2"), r, 2)

    wg.addWidget(_make_lbl("单元独立设置:"), 3, 0)
    _make_combo(parent, "comboBox_UnitSet", ["OFF", "ON"])
    wg.addWidget(parent.comboBox_UnitSet, 3, 1)

    # groupBox_12 (backward compat)
    g12 = QtWidgets.QGroupBox(wireGrp)
    g12.setObjectName("groupBox_12")
    g12.setMinimumHeight(0)
    g12.setMaximumHeight(0)

    bl.addWidget(wireGrp)

    # 更新率 + 项目数
    rightCol = QtWidgets.QVBoxLayout()
    rightCol.setSpacing(8)

    urGrp = QtWidgets.QGroupBox("")
    urGrp.setObjectName("groupBox_11")
    urLay = QtWidgets.QVBoxLayout(urGrp)
    urLay.setSpacing(4)
    urLay.setContentsMargins(8, 8, 8, 8)
    urLay.addWidget(_make_lbl("更新率:"))
    _make_combo(parent, "comboBox_ReplaceRate", ["50ms", "100ms", "250ms", "500ms", "1s", "2s", "5s", "10s", "20s"])
    urLay.addWidget(parent.comboBox_ReplaceRate)
    rightCol.addWidget(urGrp)

    projGrp = QtWidgets.QGroupBox("")
    projGrp.setObjectName("groupBox_13")
    pjLay = QtWidgets.QVBoxLayout(projGrp)
    pjLay.setSpacing(4)
    pjLay.setContentsMargins(8, 8, 8, 8)
    pjLay.addWidget(_make_lbl("项目数:"))
    _make_combo(parent, "comboBox_ProjectNum", ["12", "24", "48", "200"])
    pjLay.addWidget(parent.comboBox_ProjectNum)
    rightCol.addWidget(projGrp)

    bl.addLayout(rightCol)
    cl.addWidget(basicGrp)

    # ── 保存设置 ──
    saveGrp = QtWidgets.QGroupBox("保存设置")
    saveGrp.setStyleSheet(_GROUPBOX_STYLE)
    sg = QtWidgets.QGridLayout(saveGrp)
    sg.setSpacing(8)
    sg.setContentsMargins(12, 12, 12, 12)

    g6 = QtWidgets.QGroupBox("")
    g6.setObjectName("groupBox_6")
    g6l = QtWidgets.QGridLayout(g6)
    g6l.setSpacing(4)
    g6l.setContentsMargins(8, 8, 8, 8)
    g6l.addWidget(_make_lbl("自动保存:"), 0, 0)
    _make_combo(parent, "comboBox_AutoSave", ["OFF", "自动保存", "手动保存"])
    # 旧独立弹窗默认「自动保存」且曾被禁用；内嵌后需可改，并默认开启以免测量不落盘
    parent.comboBox_AutoSave.setCurrentIndex(1)
    g6l.addWidget(parent.comboBox_AutoSave, 0, 1)
    g6l.addWidget(_make_lbl("停机时间:"), 1, 0)
    _make_te(parent, "textEdit_StopTime", '<p align="center"><span style="font-size:9pt;">00:05:00</span></p>')
    g6l.addWidget(parent.textEdit_StopTime, 1, 1)
    sg.addWidget(g6, 0, 0)

    g15 = QtWidgets.QGroupBox("")
    g15.setObjectName("groupBox_15")
    g15l = QtWidgets.QVBoxLayout(g15)
    g15l.setSpacing(4)
    g15l.setContentsMargins(8, 8, 8, 8)
    pr = QtWidgets.QHBoxLayout()
    pr.addWidget(_make_lbl("保存路径:"))
    _make_te(parent, "textEdit_SavePath", '<p><span style="font-size:9pt;">D:\\EnergyTest\\wt_file_save_path</span></p>')
    pr.addWidget(parent.textEdit_SavePath)
    g15l.addLayout(pr)
    cb_auto = QtWidgets.QCheckBox("自动命名")
    cb_auto.setObjectName("checkBox_AutoName")
    cb_auto.setEnabled(False)
    cb_auto.setCheckable(False)
    cb_auto.setChecked(False)
    cb_auto.setStyleSheet(_CHECKBOX_STYLE)
    setattr(parent, "checkBox_AutoName", cb_auto)
    g15l.addWidget(cb_auto)
    sg.addWidget(g15, 0, 1)

    g7 = QtWidgets.QGroupBox("")
    g7.setObjectName("groupBox_7")
    g7l = QtWidgets.QVBoxLayout(g7)
    g7l.setSpacing(4)
    g7l.setContentsMargins(8, 8, 8, 8)
    g7l.addWidget(_make_lbl("文件名列表:"))
    _make_te(parent, "textEdit_FileNameList",
             '<p><span style="font-size:9pt;">100%_ambient,100%_+55,100%_-10,66%_ambient,66%_+55,66%_-10,33%_ambient,33%_+55,33%_-10,100%_ambient</span></p>',
             max_h=120)
    g7l.addWidget(parent.textEdit_FileNameList)
    sg.addWidget(g7, 0, 2)

    cl.addWidget(saveGrp)

    # ── 测量项目 - 基本量 ──
    bmGrp = QtWidgets.QGroupBox("测量项目 - 基本量")
    bmGrp.setStyleSheet(_GROUPBOX_STYLE)
    bm = QtWidgets.QGridLayout(bmGrp)
    bm.setSpacing(6)
    bm.setContentsMargins(12, 12, 12, 12)

    # Element (6 for WT1800)
    bm.addWidget(_make_lbl("Element:"), 0, 0)
    for i in range(1, 7):
        _make_cb(parent, f"checkBox_SetElement{i}", f"Element{i}")
        bm.addWidget(getattr(parent, f"checkBox_SetElement{i}"), 0, i)

    # Sigma (A, B, C)
    bm.addWidget(_make_lbl("Sigma:"), 1, 0)
    for i, name in enumerate(["checkBox_SetSigma", "checkBox_SetSigmaA", "checkBox_SetSigmaB", "checkBox_SetSigmaC"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 1, i + 1)

    # U
    bm.addWidget(_make_lbl("电压 U:"), 2, 0)
    for i, name in enumerate(["checkBox_SetUrms", "checkBox_SetUmn", "checkBox_SetUdc", "checkBox_SetUrmn", "checkBox_SetUac", "checkBox_SetUrange", "checkBox_SetCfU"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 2, i + 1)

    # I
    bm.addWidget(_make_lbl("电流 I:"), 3, 0)
    for i, name in enumerate(["checkBox_SetIrms", "checkBox_SetImn", "checkBox_SetIdc", "checkBox_SetIrmn", "checkBox_SetIac", "checkBox_SetIrange", "checkBox_SetCfI"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 3, i + 1)

    # Peak
    bm.addWidget(_make_lbl("峰值:"), 4, 0)
    for i, name in enumerate(["checkBox_SetUppeak", "checkBox_SetUmpeak", "checkBox_SetIppeak", "checkBox_SetImpeak", "checkBox_SetPppeak", "checkBox_SetPmpeak"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 4, i + 1)

    # Power
    bm.addWidget(_make_lbl("功率:"), 5, 0)
    for i, name in enumerate(["checkBox_SetP", "checkBox_SetS", "checkBox_SetQ", "checkBox_SetPF", "checkBox_SetPhi", "checkBox_SetPc"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 5, i + 1)

    # Freq
    bm.addWidget(_make_lbl("频率:"), 6, 0)
    for i, name in enumerate(["checkBox_SetFreqU", "checkBox_SetFreqI"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 6, i + 1)

    cl.addWidget(bmGrp)

    # ── 测量项目 - 功率/能量/效率 ──
    peGrp = QtWidgets.QGroupBox("测量项目 - 功率/能量/效率")
    peGrp.setStyleSheet(_GROUPBOX_STYLE)
    pe = QtWidgets.QGridLayout(peGrp)
    pe.setSpacing(6)
    pe.setContentsMargins(12, 12, 12, 12)

    pe.addWidget(_make_lbl("时间:"), 0, 0)
    _make_cb(parent, "checkBox_SetTime", "Time")
    pe.addWidget(parent.checkBox_SetTime, 0, 1)

    pe.addWidget(_make_lbl("有功功率:"), 1, 0)
    for i, name in enumerate(["checkBox_SetWP", "checkBox_SetWPPlus", "checkBox_SetWPMinus"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 1, i + 1)

    pe.addWidget(_make_lbl("无功功率:"), 2, 0)
    for i, name in enumerate(["checkBox_Setq", "checkBox_SetqPlus", "checkBox_SetqMinus"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 2, i + 1)

    pe.addWidget(_make_lbl("视在功率/电能:"), 3, 0)
    for i, name in enumerate(["checkBox_SetWS", "checkBox_SetWQ"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 3, i + 1)

    pe.addWidget(_make_lbl("效率:"), 4, 0)
    for i in range(1, 5):
        _make_cb(parent, f"checkBox_SetEta{i}", f"Eta{i}")
        pe.addWidget(getattr(parent, f"checkBox_SetEta{i}"), 4, i)

    pe.addWidget(_make_lbl("Event:"), 5, 0)
    for i in range(1, 9):
        _make_cb(parent, f"checkBox_SetEvent{i}", f"Event{i}")
        pe.addWidget(getattr(parent, f"checkBox_SetEvent{i}"), 5, i)

    cl.addWidget(peGrp)

    # ── 测量项目 - 谐波量 ──
    harmGrp = QtWidgets.QGroupBox("测量项目 - 谐波量")
    harmGrp.setStyleSheet(_GROUPBOX_STYLE)
    hm = QtWidgets.QGridLayout(harmGrp)
    hm.setSpacing(6)
    hm.setContentsMargins(12, 12, 12, 12)

    harm_items = [
        ("Uk/Ik/Pk:", ["checkBox_SetUk", "checkBox_SetIk", "checkBox_SetPk"]),
        ("Sk/Qk/PFk:", ["checkBox_SetSk", "checkBox_SetQk", "checkBox_SetPFk"]),
        ("Phik/PhiUk/PhiIk:", ["checkBox_SetPhik", "checkBox_SetPhiUk", "checkBox_SetPhiIk"]),
        ("Uhdfk/Ihdfk/Phdfk:", ["checkBox_SetUhdfk", "checkBox_SetIhdfk", "checkBox_SetPhdfk"]),
        ("Zk/Rsk/Rpk:", ["checkBox_SetZk", "checkBox_SetRsk", "checkBox_SetRpk"]),
        ("Xsk/Xpk:", ["checkBox_SetXsk", "checkBox_SetXpk"]),
    ]
    for r, (lbl_text, names) in enumerate(harm_items):
        hm.addWidget(_make_lbl(lbl_text), r, 0)
        for c, name in enumerate(names):
            _make_cb(parent, name, name.replace("checkBox_Set", ""))
            hm.addWidget(getattr(parent, name), r, c + 1)

    # Start / Stop
    hm.addWidget(_make_lbl("开始:"), 7, 0)
    _make_te(parent, "textEdit_SetStart", max_h=32)
    getattr(parent, "textEdit_SetStart").setMaximumWidth(100)
    hm.addWidget(getattr(parent, "textEdit_SetStart"), 7, 1)
    hm.addWidget(_make_lbl("结束:"), 7, 2)
    _make_te(parent, "textEdit_SetStop", max_h=32)
    getattr(parent, "textEdit_SetStop").setMaximumWidth(100)
    hm.addWidget(getattr(parent, "textEdit_SetStop"), 7, 3)

    cl.addWidget(harmGrp)

    # ── 测量项目 - THD 及其他 ──
    thdGrp = QtWidgets.QGroupBox("测量项目 - THD 及其他")
    thdGrp.setStyleSheet(_GROUPBOX_STYLE)
    td = QtWidgets.QGridLayout(thdGrp)
    td.setSpacing(6)
    td.setContentsMargins(12, 12, 12, 12)

    thd_items = [
        ("THD:", ["checkBox_SetUthd", "checkBox_SetIthd", "checkBox_SetPthd"]),
        ("THF:", ["checkBox_SetUthf", "checkBox_SetIthf"]),
        ("TIF:", ["checkBox_SetUtif", "checkBox_SetItif"]),
        ("HVF/HCF:", ["checkBox_Sethvf", "checkBox_Sethcf"]),
        ("相位差:", ["checkBox_SetPhiUi_Uj", "checkBox_SetPhiUi_Uk", "checkBox_SetPhiUi_Ii", "checkBox_SetPhiUi_Ij", "checkBox_SetPhiUi_Ik"]),
        ("电机:", ["checkBox_SetSpeed", "checkBox_SetTorque", "checkBox_SetSyncSp", "checkBox_SetSlip", "checkBox_SetPm", "checkBox_SetEaU", "checkBox_SetEaI"]),
        ("DeltaU:", ["checkBox_SetDeltaU1", "checkBox_SetDeltaU2", "checkBox_SetDeltaU3", "checkBox_SetDeltaUSigma"]),
        ("DeltaI:", ["checkBox_SetDeltaI"]),
        ("DeltaP:", ["checkBox_SetDeltaP1", "checkBox_SetDeltaP2", "checkBox_SetDeltaP3", "checkBox_SetDeltaPSigma"]),
        ("PLL:", ["checkBox_SetFreqPLL1", "checkBox_SetFreqPLL2"]),
        ("K-factor:", ["checkBox_SetK_factor"]),
    ]
    for r, (lbl_text, names) in enumerate(thd_items):
        td.addWidget(_make_lbl(lbl_text), r, 0)
        for c, name in enumerate(names):
            _make_cb(parent, name, name.replace("checkBox_Set", ""))
            td.addWidget(getattr(parent, name), r, c + 1)

    cl.addWidget(thdGrp)

    # ── F Function ──
    fGrp = QtWidgets.QGroupBox("F Function 选择")
    fGrp.setStyleSheet(_GROUPBOX_STYLE)
    fg = QtWidgets.QGridLayout(fGrp)
    fg.setSpacing(4)
    fg.setContentsMargins(12, 12, 12, 12)

    for i in range(1, 21):
        name = f"checkBox_SetF{i:02d}"
        _make_cb(parent, name, f"F{i:02d}")
        fg.addWidget(getattr(parent, name), (i - 1) // 5, (i - 1) % 5)

    cl.addWidget(fGrp)
    cl.addStretch()

    scroll.setWidget(cw)
    return scroll


# ═══════════════════════════════════════════════════════════════════════════
# WT1806E 配置内容（与 WT1800 结构相同，差异：无 FreqPLL2, 无 EaU/EaI）
# ═══════════════════════════════════════════════════════════════════════════
def build_wt1806e_content(parent):
    """构建 WT1806E 配置内容，返回 QScrollArea。"""
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet(
        "QScrollArea { border: none; background-color: white; }"
        "QScrollBar:vertical { background: #f1f5f9; width: 10px; }"
        "QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 5px; min-height: 30px; }"
        "QScrollBar::handle:vertical:hover { background: #94a3b8; }"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
    )
    cw = QtWidgets.QWidget()
    cw.setStyleSheet("background-color: white;")
    cl = QtWidgets.QVBoxLayout(cw)
    cl.setContentsMargins(16, 16, 16, 16)
    cl.setSpacing(12)

    # ── 基本设置 ──
    basicGrp = QtWidgets.QGroupBox("基本设置")
    basicGrp.setStyleSheet(_GROUPBOX_STYLE)
    bl = QtWidgets.QHBoxLayout(basicGrp)
    bl.setSpacing(12)
    bl.setContentsMargins(12, 12, 12, 12)

    wireGrp = QtWidgets.QGroupBox("接线方式")
    wireGrp.setObjectName("groupBox_3")
    wg = QtWidgets.QGridLayout(wireGrp)
    wg.setSpacing(6)
    wg.setContentsMargins(8, 16, 8, 8)

    for r, (prefix, lbl_text) in enumerate([("A", "SigmaA:"), ("B", "SigmaB:"), ("C", "SigmaC:")]):
        wg.addWidget(_make_lbl(lbl_text), r, 0)
        _make_combo(parent, f"comboBox_Sigm{prefix}1", ["---", "1P3W", "3P3W", "3P4W", "3V3A"])
        wg.addWidget(getattr(parent, f"comboBox_Sigm{prefix}1"), r, 1)
        _make_combo(parent, f"comboBox_Sigm{prefix}2", ["Element1", "Element2", "Element3", "Element4", "Element5", "Element6"])
        wg.addWidget(getattr(parent, f"comboBox_Sigm{prefix}2"), r, 2)

    wg.addWidget(_make_lbl("单元独立设置:"), 3, 0)
    _make_combo(parent, "comboBox_UnitSet", ["OFF", "ON"])
    wg.addWidget(parent.comboBox_UnitSet, 3, 1)

    g12 = QtWidgets.QGroupBox(wireGrp)
    g12.setObjectName("groupBox_12")
    g12.setMinimumHeight(0)
    g12.setMaximumHeight(0)

    bl.addWidget(wireGrp)

    rightCol = QtWidgets.QVBoxLayout()
    rightCol.setSpacing(8)

    urGrp = QtWidgets.QGroupBox("")
    urGrp.setObjectName("groupBox_11")
    urLay = QtWidgets.QVBoxLayout(urGrp)
    urLay.setSpacing(4)
    urLay.setContentsMargins(8, 8, 8, 8)
    urLay.addWidget(_make_lbl("更新率:"))
    _make_combo(parent, "comboBox_ReplaceRate", ["50ms", "100ms", "250ms", "500ms", "1s", "2s", "5s", "10s", "20s"])
    urLay.addWidget(parent.comboBox_ReplaceRate)
    rightCol.addWidget(urGrp)

    projGrp = QtWidgets.QGroupBox("")
    projGrp.setObjectName("groupBox_13")
    pjLay = QtWidgets.QVBoxLayout(projGrp)
    pjLay.setSpacing(4)
    pjLay.setContentsMargins(8, 8, 8, 8)
    pjLay.addWidget(_make_lbl("项目数:"))
    _make_combo(parent, "comboBox_ProjectNum", ["12", "24", "48", "200"])
    pjLay.addWidget(parent.comboBox_ProjectNum)
    rightCol.addWidget(projGrp)

    bl.addLayout(rightCol)
    cl.addWidget(basicGrp)

    # ── 保存设置（同 WT1800）──
    saveGrp = QtWidgets.QGroupBox("保存设置")
    saveGrp.setStyleSheet(_GROUPBOX_STYLE)
    sg = QtWidgets.QGridLayout(saveGrp)
    sg.setSpacing(8)
    sg.setContentsMargins(12, 12, 12, 12)

    g6 = QtWidgets.QGroupBox("")
    g6.setObjectName("groupBox_6")
    g6l = QtWidgets.QGridLayout(g6)
    g6l.setSpacing(4)
    g6l.setContentsMargins(8, 8, 8, 8)
    g6l.addWidget(_make_lbl("自动保存:"), 0, 0)
    _make_combo(parent, "comboBox_AutoSave", ["OFF", "自动保存", "手动保存"])
    # 旧独立弹窗默认「自动保存」且曾被禁用；内嵌后需可改，并默认开启以免测量不落盘
    parent.comboBox_AutoSave.setCurrentIndex(1)
    g6l.addWidget(parent.comboBox_AutoSave, 0, 1)
    g6l.addWidget(_make_lbl("停机时间:"), 1, 0)
    _make_te(parent, "textEdit_StopTime", '<p align="center"><span style="font-size:9pt;">00:05:00</span></p>')
    g6l.addWidget(parent.textEdit_StopTime, 1, 1)
    sg.addWidget(g6, 0, 0)

    g15 = QtWidgets.QGroupBox("")
    g15.setObjectName("groupBox_15")
    g15l = QtWidgets.QVBoxLayout(g15)
    g15l.setSpacing(4)
    g15l.setContentsMargins(8, 8, 8, 8)
    pr = QtWidgets.QHBoxLayout()
    pr.addWidget(_make_lbl("保存路径:"))
    _make_te(parent, "textEdit_SavePath", '<p><span style="font-size:9pt;">D:\\EnergyTest\\wt_file_save_path</span></p>')
    pr.addWidget(parent.textEdit_SavePath)
    g15l.addLayout(pr)
    cb_auto = QtWidgets.QCheckBox("自动命名")
    cb_auto.setObjectName("checkBox_AutoName")
    cb_auto.setEnabled(False)
    cb_auto.setCheckable(False)
    cb_auto.setChecked(False)
    cb_auto.setStyleSheet(_CHECKBOX_STYLE)
    setattr(parent, "checkBox_AutoName", cb_auto)
    g15l.addWidget(cb_auto)
    sg.addWidget(g15, 0, 1)

    g7 = QtWidgets.QGroupBox("")
    g7.setObjectName("groupBox_7")
    g7l = QtWidgets.QVBoxLayout(g7)
    g7l.setSpacing(4)
    g7l.setContentsMargins(8, 8, 8, 8)
    g7l.addWidget(_make_lbl("文件名列表:"))
    _make_te(parent, "textEdit_FileNameList",
             '<p><span style="font-size:9pt;">100%_ambient,100%_+55,100%_-10,66%_ambient,66%_+55,66%_-10,33%_ambient,33%_+55,33%_-10,100%_ambient</span></p>',
             max_h=120)
    g7l.addWidget(parent.textEdit_FileNameList)
    sg.addWidget(g7, 0, 2)

    cl.addWidget(saveGrp)

    # ── 测量项目（同 WT1800 结构）──
    bmGrp = QtWidgets.QGroupBox("测量项目 - 基本量")
    bmGrp.setStyleSheet(_GROUPBOX_STYLE)
    bm = QtWidgets.QGridLayout(bmGrp)
    bm.setSpacing(6)
    bm.setContentsMargins(12, 12, 12, 12)

    bm.addWidget(_make_lbl("Element:"), 0, 0)
    for i in range(1, 7):
        _make_cb(parent, f"checkBox_SetElement{i}", f"Element{i}")
        bm.addWidget(getattr(parent, f"checkBox_SetElement{i}"), 0, i)

    bm.addWidget(_make_lbl("Sigma:"), 1, 0)
    for i, name in enumerate(["checkBox_SetSigma", "checkBox_SetSigmaA", "checkBox_SetSigmaB", "checkBox_SetSigmaC"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 1, i + 1)

    bm.addWidget(_make_lbl("电压 U:"), 2, 0)
    for i, name in enumerate(["checkBox_SetUrms", "checkBox_SetUmn", "checkBox_SetUdc", "checkBox_SetUrmn", "checkBox_SetUac", "checkBox_SetUrange", "checkBox_SetCfU"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 2, i + 1)

    bm.addWidget(_make_lbl("电流 I:"), 3, 0)
    for i, name in enumerate(["checkBox_SetIrms", "checkBox_SetImn", "checkBox_SetIdc", "checkBox_SetIrmn", "checkBox_SetIac", "checkBox_SetIrange", "checkBox_SetCfI"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 3, i + 1)

    bm.addWidget(_make_lbl("峰值:"), 4, 0)
    for i, name in enumerate(["checkBox_SetUppeak", "checkBox_SetUmpeak", "checkBox_SetIppeak", "checkBox_SetImpeak", "checkBox_SetPppeak", "checkBox_SetPmpeak"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 4, i + 1)

    bm.addWidget(_make_lbl("功率:"), 5, 0)
    for i, name in enumerate(["checkBox_SetP", "checkBox_SetS", "checkBox_SetQ", "checkBox_SetPF", "checkBox_SetPhi", "checkBox_SetPc"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 5, i + 1)

    bm.addWidget(_make_lbl("频率:"), 6, 0)
    for i, name in enumerate(["checkBox_SetFreqU", "checkBox_SetFreqI"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 6, i + 1)

    cl.addWidget(bmGrp)

    # ── 测量项目 - 功率/能量/效率 ──
    peGrp = QtWidgets.QGroupBox("测量项目 - 功率/能量/效率")
    peGrp.setStyleSheet(_GROUPBOX_STYLE)
    pe = QtWidgets.QGridLayout(peGrp)
    pe.setSpacing(6)
    pe.setContentsMargins(12, 12, 12, 12)

    pe.addWidget(_make_lbl("时间:"), 0, 0)
    _make_cb(parent, "checkBox_SetTime", "Time")
    pe.addWidget(parent.checkBox_SetTime, 0, 1)

    pe.addWidget(_make_lbl("有功功率:"), 1, 0)
    for i, name in enumerate(["checkBox_SetWP", "checkBox_SetWPPlus", "checkBox_SetWPMinus"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 1, i + 1)

    pe.addWidget(_make_lbl("无功功率:"), 2, 0)
    for i, name in enumerate(["checkBox_Setq", "checkBox_SetqPlus", "checkBox_SetqMinus"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 2, i + 1)

    pe.addWidget(_make_lbl("视在功率/电能:"), 3, 0)
    for i, name in enumerate(["checkBox_SetWS", "checkBox_SetWQ"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 3, i + 1)

    pe.addWidget(_make_lbl("效率:"), 4, 0)
    for i in range(1, 5):
        _make_cb(parent, f"checkBox_SetEta{i}", f"Eta{i}")
        pe.addWidget(getattr(parent, f"checkBox_SetEta{i}"), 4, i)

    pe.addWidget(_make_lbl("Event:"), 5, 0)
    for i in range(1, 9):
        _make_cb(parent, f"checkBox_SetEvent{i}", f"Event{i}")
        pe.addWidget(getattr(parent, f"checkBox_SetEvent{i}"), 5, i)

    cl.addWidget(peGrp)

    # ── 测量项目 - 谐波量 ──
    harmGrp = QtWidgets.QGroupBox("测量项目 - 谐波量")
    harmGrp.setStyleSheet(_GROUPBOX_STYLE)
    hm = QtWidgets.QGridLayout(harmGrp)
    hm.setSpacing(6)
    hm.setContentsMargins(12, 12, 12, 12)

    harm_items = [
        ("Uk/Ik/Pk:", ["checkBox_SetUk", "checkBox_SetIk", "checkBox_SetPk"]),
        ("Sk/Qk/PFk:", ["checkBox_SetSk", "checkBox_SetQk", "checkBox_SetPFk"]),
        ("Phik/PhiUk/PhiIk:", ["checkBox_SetPhik", "checkBox_SetPhiUk", "checkBox_SetPhiIk"]),
        ("Uhdfk/Ihdfk/Phdfk:", ["checkBox_SetUhdfk", "checkBox_SetIhdfk", "checkBox_SetPhdfk"]),
        ("Zk/Rsk/Rpk:", ["checkBox_SetZk", "checkBox_SetRsk", "checkBox_SetRpk"]),
        ("Xsk/Xpk:", ["checkBox_SetXsk", "checkBox_SetXpk"]),
    ]
    for r, (lbl_text, names) in enumerate(harm_items):
        hm.addWidget(_make_lbl(lbl_text), r, 0)
        for c, name in enumerate(names):
            _make_cb(parent, name, name.replace("checkBox_Set", ""))
            hm.addWidget(getattr(parent, name), r, c + 1)

    # Start / Stop
    hm.addWidget(_make_lbl("开始:"), 7, 0)
    _make_te(parent, "textEdit_SetStart", max_h=32)
    getattr(parent, "textEdit_SetStart").setMaximumWidth(100)
    hm.addWidget(getattr(parent, "textEdit_SetStart"), 7, 1)
    hm.addWidget(_make_lbl("结束:"), 7, 2)
    _make_te(parent, "textEdit_SetStop", max_h=32)
    getattr(parent, "textEdit_SetStop").setMaximumWidth(100)
    hm.addWidget(getattr(parent, "textEdit_SetStop"), 7, 3)

    cl.addWidget(harmGrp)

    # ── 测量项目 - THD 及其他 ──
    thdGrp = QtWidgets.QGroupBox("测量项目 - THD 及其他")
    thdGrp.setStyleSheet(_GROUPBOX_STYLE)
    td = QtWidgets.QGridLayout(thdGrp)
    td.setSpacing(6)
    td.setContentsMargins(12, 12, 12, 12)

    thd_items = [
        ("THD:", ["checkBox_SetUthd", "checkBox_SetIthd", "checkBox_SetPthd"]),
        ("THF:", ["checkBox_SetUthf", "checkBox_SetIthf"]),
        ("TIF:", ["checkBox_SetUtif", "checkBox_SetItif"]),
        ("HVF/HCF:", ["checkBox_Sethvf", "checkBox_Sethcf"]),
        ("相位差:", ["checkBox_SetPhiUi_Uj", "checkBox_SetPhiUi_Uk", "checkBox_SetPhiUi_Ii", "checkBox_SetPhiUi_Ij", "checkBox_SetPhiUi_Ik"]),
        ("电机:", ["checkBox_SetSpeed", "checkBox_SetTorque", "checkBox_SetSyncSp", "checkBox_SetSlip", "checkBox_SetPm"]),
        ("DeltaU:", ["checkBox_SetDeltaU1", "checkBox_SetDeltaU2", "checkBox_SetDeltaU3", "checkBox_SetDeltaUSigma"]),
        ("DeltaI:", ["checkBox_SetDeltaI"]),
        ("DeltaP:", ["checkBox_SetDeltaP1", "checkBox_SetDeltaP2", "checkBox_SetDeltaP3", "checkBox_SetDeltaPSigma"]),
        ("PLL:", ["checkBox_SetFreqPLL1"]),
        ("K-factor:", ["checkBox_SetK_factor"]),
    ]
    for r, (lbl_text, names) in enumerate(thd_items):
        td.addWidget(_make_lbl(lbl_text), r, 0)
        for c, name in enumerate(names):
            _make_cb(parent, name, name.replace("checkBox_Set", ""))
            td.addWidget(getattr(parent, name), r, c + 1)

    cl.addWidget(thdGrp)

    # ── F Function ──
    fGrp = QtWidgets.QGroupBox("F Function 选择")
    fGrp.setStyleSheet(_GROUPBOX_STYLE)
    fg = QtWidgets.QGridLayout(fGrp)
    fg.setSpacing(4)
    fg.setContentsMargins(12, 12, 12, 12)

    for i in range(1, 21):
        name = f"checkBox_SetF{i:02d}"
        _make_cb(parent, name, f"F{i:02d}")
        fg.addWidget(getattr(parent, name), (i - 1) // 5, (i - 1) % 5)

    cl.addWidget(fGrp)
    cl.addStretch()

    scroll.setWidget(cw)
    return scroll


# ═══════════════════════════════════════════════════════════════════════════
# WT5000 配置内容
# ═══════════════════════════════════════════════════════════════════════════
def build_wt5000_content(parent):
    """构建 WT5000 配置内容（不含顶部按钮栏），返回 QScrollArea。"""
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet(
        "QScrollArea { border: none; background-color: white; }"
        "QScrollBar:vertical { background: #f1f5f9; width: 10px; }"
        "QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 5px; min-height: 30px; }"
        "QScrollBar::handle:vertical:hover { background: #94a3b8; }"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
    )
    cw = QtWidgets.QWidget()
    cw.setStyleSheet("background-color: white;")
    cl = QtWidgets.QVBoxLayout(cw)
    cl.setContentsMargins(16, 16, 16, 16)
    cl.setSpacing(12)

    # ── 基本设置 ──
    basicGrp = QtWidgets.QGroupBox("基本设置")
    basicGrp.setStyleSheet(_GROUPBOX_STYLE)
    bl = QtWidgets.QHBoxLayout(basicGrp)
    bl.setSpacing(12)
    bl.setContentsMargins(12, 12, 12, 12)

    wireGrp = QtWidgets.QGroupBox("接线方式")
    wireGrp.setObjectName("groupBox_3")
    wg = QtWidgets.QGridLayout(wireGrp)
    wg.setSpacing(6)
    wg.setContentsMargins(8, 16, 8, 8)

    for r, (prefix, lbl_text) in enumerate([("A", "SigmaA:"), ("B", "SigmaB:")]):
        wg.addWidget(_make_lbl(lbl_text), r, 0)
        _make_combo(parent, f"comboBox_Sigm{prefix}1", ["---", "1P3W", "3P3W", "3P4W", "3V3A"])
        wg.addWidget(getattr(parent, f"comboBox_Sigm{prefix}1"), r, 1)
        _make_combo(parent, f"comboBox_Sigm{prefix}2", ["Element1", "Element2", "Element3", "Element4"])
        wg.addWidget(getattr(parent, f"comboBox_Sigm{prefix}2"), r, 2)

    g12 = QtWidgets.QGroupBox(wireGrp)
    g12.setObjectName("groupBox_12")
    g12.setMinimumHeight(0)
    g12.setMaximumHeight(0)

    bl.addWidget(wireGrp)

    rightCol = QtWidgets.QVBoxLayout()
    rightCol.setSpacing(8)

    urGrp = QtWidgets.QGroupBox("")
    urGrp.setObjectName("groupBox_11")
    urLay = QtWidgets.QVBoxLayout(urGrp)
    urLay.setSpacing(4)
    urLay.setContentsMargins(8, 8, 8, 8)
    urLay.addWidget(_make_lbl("更新率:"))
    _make_combo(parent, "comboBox_ReplaceRate", ["50ms", "100ms", "250ms", "500ms", "1s", "2s", "5s", "10s", "20s"])
    urLay.addWidget(parent.comboBox_ReplaceRate)
    rightCol.addWidget(urGrp)

    projGrp = QtWidgets.QGroupBox("")
    projGrp.setObjectName("groupBox_13")
    pjLay = QtWidgets.QVBoxLayout(projGrp)
    pjLay.setSpacing(4)
    pjLay.setContentsMargins(8, 8, 8, 8)
    pjLay.addWidget(_make_lbl("项目数:"))
    _make_combo(parent, "comboBox_ProjectNum", ["12", "24", "48", "200"])
    pjLay.addWidget(parent.comboBox_ProjectNum)
    rightCol.addWidget(projGrp)

    bl.addLayout(rightCol)
    cl.addWidget(basicGrp)

    # ── 保存设置 ──
    saveGrp = QtWidgets.QGroupBox("保存设置")
    saveGrp.setStyleSheet(_GROUPBOX_STYLE)
    sg = QtWidgets.QGridLayout(saveGrp)
    sg.setSpacing(8)
    sg.setContentsMargins(12, 12, 12, 12)

    g6 = QtWidgets.QGroupBox("")
    g6.setObjectName("groupBox_6")
    g6l = QtWidgets.QGridLayout(g6)
    g6l.setSpacing(4)
    g6l.setContentsMargins(8, 8, 8, 8)
    g6l.addWidget(_make_lbl("自动保存:"), 0, 0)
    _make_combo(parent, "comboBox_AutoSave", ["OFF", "自动保存", "手动保存"])
    # 旧独立弹窗默认「自动保存」且曾被禁用；内嵌后需可改，并默认开启以免测量不落盘
    parent.comboBox_AutoSave.setCurrentIndex(1)
    g6l.addWidget(parent.comboBox_AutoSave, 0, 1)
    g6l.addWidget(_make_lbl("停机时间:"), 1, 0)
    _make_te(parent, "textEdit_StopTime", '<p align="center"><span style="font-size:9pt;">00:05:00</span></p>')
    g6l.addWidget(parent.textEdit_StopTime, 1, 1)
    sg.addWidget(g6, 0, 0)

    g15 = QtWidgets.QGroupBox("")
    g15.setObjectName("groupBox_15")
    g15l = QtWidgets.QVBoxLayout(g15)
    g15l.setSpacing(4)
    g15l.setContentsMargins(8, 8, 8, 8)
    pr = QtWidgets.QHBoxLayout()
    pr.addWidget(_make_lbl("保存路径:"))
    _make_te(parent, "textEdit_SavePath", '<p><span style="font-size:9pt;">D:\\EnergyTest\\wt_file_save_path</span></p>')
    pr.addWidget(parent.textEdit_SavePath)
    g15l.addLayout(pr)
    cb_auto = QtWidgets.QCheckBox("自动命名")
    cb_auto.setObjectName("checkBox_AutoName")
    cb_auto.setEnabled(False)
    cb_auto.setCheckable(False)
    cb_auto.setChecked(False)
    cb_auto.setStyleSheet(_CHECKBOX_STYLE)
    setattr(parent, "checkBox_AutoName", cb_auto)
    g15l.addWidget(cb_auto)
    sg.addWidget(g15, 0, 1)

    g7 = QtWidgets.QGroupBox("")
    g7.setObjectName("groupBox_7")
    g7l = QtWidgets.QVBoxLayout(g7)
    g7l.setSpacing(4)
    g7l.setContentsMargins(8, 8, 8, 8)
    g7l.addWidget(_make_lbl("文件名列表:"))
    _make_te(parent, "textEdit_FileNameList",
             '<p><span style="font-size:9pt;">100%_ambient,100%_+55,100%_-10,66%_ambient,66%_+55,66%_-10,33%_ambient,33%_+55,33%_-10,100%_ambient</span></p>',
             max_h=120)
    g7l.addWidget(parent.textEdit_FileNameList)
    sg.addWidget(g7, 0, 2)

    cl.addWidget(saveGrp)

    # ── 测量项目 - 基本量 ──
    bmGrp = QtWidgets.QGroupBox("测量项目 - 基本量")
    bmGrp.setStyleSheet(_GROUPBOX_STYLE)
    bm = QtWidgets.QGridLayout(bmGrp)
    bm.setSpacing(6)
    bm.setContentsMargins(12, 12, 12, 12)

    bm.addWidget(_make_lbl("Element:"), 0, 0)
    for i in range(1, 5):
        _make_cb(parent, f"checkBox_SetElement{i}", f"Element{i}")
        bm.addWidget(getattr(parent, f"checkBox_SetElement{i}"), 0, i)

    bm.addWidget(_make_lbl("Sigma:"), 1, 0)
    for i, name in enumerate(["checkBox_SetSigma", "checkBox_SetSigmaA", "checkBox_SetSigmaB"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 1, i + 1)

    bm.addWidget(_make_lbl("电压 U:"), 2, 0)
    for i, name in enumerate(["checkBox_SetUrms", "checkBox_SetUmn", "checkBox_SetUdc", "checkBox_SetUrmn", "checkBox_SetUac", "checkBox_SetRngU", "checkBox_SetCfU"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 2, i + 1)

    bm.addWidget(_make_lbl("电流 I:"), 3, 0)
    for i, name in enumerate(["checkBox_SetIrms", "checkBox_SetImn", "checkBox_SetIdc", "checkBox_SetIrmn", "checkBox_SetIac", "checkBox_SetRngI", "checkBox_SetCfI"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 3, i + 1)

    bm.addWidget(_make_lbl("峰值:"), 4, 0)
    for i, name in enumerate(["checkBox_SetUppeak", "checkBox_SetUmpeak", "checkBox_SetIppeak", "checkBox_SetImpeak", "checkBox_SetPppeak", "checkBox_SetPmpeak"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 4, i + 1)

    bm.addWidget(_make_lbl("功率:"), 5, 0)
    for i, name in enumerate(["checkBox_SetP", "checkBox_SetS", "checkBox_SetQ", "checkBox_SetPF", "checkBox_SetPhi", "checkBox_SetPc"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 5, i + 1)

    # 基波 (WT5000 独有)
    bm.addWidget(_make_lbl("基波:"), 6, 0)
    for i, name in enumerate(["checkBox_SetUfnd", "checkBox_SetIfnd", "checkBox_SetPfnd", "checkBox_SetSfnd", "checkBox_SetQfnd", "checkBox_SetLambdafnd", "checkBox_SetPhifnd"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 6, i + 1)

    bm.addWidget(_make_lbl("频率:"), 7, 0)
    for i, name in enumerate(["checkBox_SetFreqU", "checkBox_SetFreqI", "checkBox_SetFreq2U", "checkBox_SetFreq2I"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        bm.addWidget(getattr(parent, name), 7, i + 1)

    # Start / Stop
    bm.addWidget(_make_lbl("开始:"), 8, 0)
    _make_te(parent, "textEdit_SetStart", max_h=32)
    getattr(parent, "textEdit_SetStart").setMaximumWidth(100)
    bm.addWidget(getattr(parent, "textEdit_SetStart"), 8, 1)
    bm.addWidget(_make_lbl("结束:"), 8, 2)
    _make_te(parent, "textEdit_SetStop", max_h=32)
    getattr(parent, "textEdit_SetStop").setMaximumWidth(100)
    bm.addWidget(getattr(parent, "textEdit_SetStop"), 8, 3)

    cl.addWidget(bmGrp)

    # ── 测量项目 - 功率/能量/效率 ──
    peGrp = QtWidgets.QGroupBox("测量项目 - 功率/能量/效率")
    peGrp.setStyleSheet(_GROUPBOX_STYLE)
    pe = QtWidgets.QGridLayout(peGrp)
    pe.setSpacing(6)
    pe.setContentsMargins(12, 12, 12, 12)

    pe.addWidget(_make_lbl("时间:"), 0, 0)
    _make_cb(parent, "checkBox_SetTime", "Time")
    pe.addWidget(parent.checkBox_SetTime, 0, 1)

    pe.addWidget(_make_lbl("有功功率:"), 1, 0)
    for i, name in enumerate(["checkBox_SetWP", "checkBox_SetWPPlus", "checkBox_SetWPMinus"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 1, i + 1)

    pe.addWidget(_make_lbl("无功功率:"), 2, 0)
    for i, name in enumerate(["checkBox_Setq", "checkBox_SetqPlus", "checkBox_SetqMinus"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 2, i + 1)

    pe.addWidget(_make_lbl("视在功率/电能:"), 3, 0)
    for i, name in enumerate(["checkBox_SetWS", "checkBox_SetWQ"]):
        _make_cb(parent, name, name.replace("checkBox_Set", ""))
        pe.addWidget(getattr(parent, name), 3, i + 1)

    pe.addWidget(_make_lbl("效率:"), 4, 0)
    for i in range(1, 5):
        _make_cb(parent, f"checkBox_SetEta{i}", f"Eta{i}")
        pe.addWidget(getattr(parent, f"checkBox_SetEta{i}"), 4, i)

    pe.addWidget(_make_lbl("Event:"), 5, 0)
    for i in range(1, 9):
        _make_cb(parent, f"checkBox_SetEvent{i}", f"Event{i}")
        pe.addWidget(getattr(parent, f"checkBox_SetEvent{i}"), 5, i)

    cl.addWidget(peGrp)

    # ── 测量项目 - 谐波量 ──
    harmGrp = QtWidgets.QGroupBox("测量项目 - 谐波量")
    harmGrp.setStyleSheet(_GROUPBOX_STYLE)
    hm = QtWidgets.QGridLayout(harmGrp)
    hm.setSpacing(6)
    hm.setContentsMargins(12, 12, 12, 12)

    harm_items = [
        ("Uk/Ik/Pk:", ["checkBox_SetUk", "checkBox_SetIk", "checkBox_SetPk"]),
        ("Sk/Qk/PFk:", ["checkBox_SetSk", "checkBox_SetQk", "checkBox_SetPFk"]),
        ("Phik/PhiUk/PhiIk:", ["checkBox_SetPhik", "checkBox_SetPhiUk", "checkBox_SetPhiIk"]),
        ("Uhdfk/Ihdfk/Phdfk:", ["checkBox_SetUhdfk", "checkBox_SetIhdfk", "checkBox_SetPhdfk"]),
        ("Zk/Rsk/Xsk:", ["checkBox_SetZk", "checkBox_SetRsk", "checkBox_SetXsk"]),
        ("Rpk/Xpk:", ["checkBox_SetRpk", "checkBox_SetXpk"]),
    ]
    for r, (lbl_text, names) in enumerate(harm_items):
        hm.addWidget(_make_lbl(lbl_text), r, 0)
        for c, name in enumerate(names):
            _make_cb(parent, name, name.replace("checkBox_Set", ""))
            hm.addWidget(getattr(parent, name), r, c + 1)

    cl.addWidget(harmGrp)

    # ── 测量项目 - THD 及其他 ──
    thdGrp = QtWidgets.QGroupBox("测量项目 - THD 及其他")
    thdGrp.setStyleSheet(_GROUPBOX_STYLE)
    td = QtWidgets.QGridLayout(thdGrp)
    td.setSpacing(6)
    td.setContentsMargins(12, 12, 12, 12)

    thd_items = [
        ("THD:", ["checkBox_SetUthd", "checkBox_SetIthd", "checkBox_SetPthd"]),
        ("THF:", ["checkBox_SetUthf", "checkBox_SetIthf"]),
        ("TIF:", ["checkBox_SetUtif", "checkBox_SetItif"]),
        ("HVF/HCF:", ["checkBox_Sethvf", "checkBox_Sethcf"]),
        ("K-factor:", ["checkBox_SetK_factor"]),
        ("相位差:", ["checkBox_SetPhiUi_Uj", "checkBox_SetPhiUi_Uk", "checkBox_SetPhiUi_Ii", "checkBox_SetPhiUi_Ij", "checkBox_SetPhiUi_Ik"]),
        ("电机:", ["checkBox_SetSpeed", "checkBox_SetTorque", "checkBox_SetSyncSp", "checkBox_SetSlip", "checkBox_SetPm"]),
        ("DeltaU:", ["checkBox_SetDeltaU1", "checkBox_SetDeltaU2", "checkBox_SetDeltaU3", "checkBox_SetDeltaUSigma"]),
        ("DeltaI:", ["checkBox_SetDeltaI"]),
        ("DeltaP:", ["checkBox_SetDeltaP1", "checkBox_SetDeltaP2", "checkBox_SetDeltaP3", "checkBox_SetDeltaPSigma"]),
        ("PLL:", ["checkBox_SetFreqPLL1", "checkBox_SetFreqPLL2"]),
        ("时间戳:", ["checkBox_SetTSDate", "checkBox_SetTSTime", "checkBox_SetTSSubsec"]),
    ]
    for r, (lbl_text, names) in enumerate(thd_items):
        td.addWidget(_make_lbl(lbl_text), r, 0)
        for c, name in enumerate(names):
            _make_cb(parent, name, name.replace("checkBox_Set", ""))
            td.addWidget(getattr(parent, name), r, c + 1)

    cl.addWidget(thdGrp)

    # ── F Function ──
    fGrp = QtWidgets.QGroupBox("F Function 选择")
    fGrp.setStyleSheet(_GROUPBOX_STYLE)
    fg = QtWidgets.QGridLayout(fGrp)
    fg.setSpacing(4)
    fg.setContentsMargins(12, 12, 12, 12)

    for i in range(1, 21):
        name = f"checkBox_SetF{i:02d}"
        _make_cb(parent, name, f"F{i:02d}")
        fg.addWidget(getattr(parent, name), (i - 1) // 5, (i - 1) % 5)

    cl.addWidget(fGrp)
    cl.addStretch()

    scroll.setWidget(cw)
    return scroll
