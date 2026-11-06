# -*- coding: utf-8 -*-
"""Capture full device-management pages (brand + 串口/IP) for process PDF."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.breadcrumb import BreadcrumbWidget
from components.buttons import ButtonStyle, apply_button_style
from components.timeline import (
    TimelineWidget,
    param_row,
    _BTN_QSS,
    _CONNECT_BTN_QSS,
    _INPUT_QSS,
    _LABEL_QSS,
    _LOG_QSS,
)

OUT = ROOT / "code_example" / "media" / "overload_flow_shots"


def grab(widget: QWidget, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pix = widget.grab()
    if pix.isNull():
        raise RuntimeError(f"empty grab {path}")
    if not pix.save(str(path), "PNG"):
        raise RuntimeError(f"save failed {path}")
    print(f"saved {path.name} ({pix.width()}x{pix.height()})")


def _shell(title: str) -> tuple[QWidget, QVBoxLayout]:
    w = QWidget()
    w.setWindowTitle(title)
    w.resize(1180, 860)
    w.setStyleSheet("background:#f8fafc;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(16, 12, 16, 12)
    lay.setSpacing(8)
    head = QLabel(title)
    head.setStyleSheet("font-size:16px;font-weight:700;color:#0f172a;")
    tip = QLabel("主界面 → 左侧设备页（与软件实际布局一致的操作示意截图）")
    tip.setStyleSheet("font-size:12px;color:#64748b;")
    lay.addWidget(head)
    lay.addWidget(tip)
    return w, lay


def build_ac_chroma(comm_mode: str = "串口") -> QWidget:
    """Chroma AC: 串口(SCPI资源) 或 IP(TCP SCPI)."""
    timeline = TimelineWidget()

    mode = QComboBox()
    mode.addItems(["串口", "IP"])
    mode.setCurrentText(comm_mode)
    mode.setStyleSheet(_INPUT_QSS)
    mode.setFixedWidth(90)

    serial = QComboBox()
    serial.addItems(
        [
            "ASRL3::INSTR",
            "USB0::0x0AAD::0x01D6::INSTR",
            "TCPIP0::192.168.1.10::INSTR",
        ]
    )
    serial.setStyleSheet(_INPUT_QSS)
    serial.setMinimumWidth(280)

    ip = QLineEdit("192.168.1.100")
    ip.setPlaceholderText("如 192.168.1.100")
    ip.setStyleSheet(_INPUT_QSS)
    ip.setMinimumWidth(160)
    port = QLineEdit("")
    port.setPlaceholderText("留空自动探测")
    port.setStyleSheet(_INPUT_QSS)
    port.setMinimumWidth(100)

    ip_lab = QLabel("IP:")
    ip_lab.setStyleSheet(_LABEL_QSS)
    port_lab = QLabel("端口:")
    port_lab.setStyleSheet(_LABEL_QSS)
    btn = QPushButton("连接设备")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    btn.setFixedWidth(120)

    use_ip = comm_mode == "IP"
    serial.setVisible(not use_ip)
    ip.setVisible(use_ip)
    port.setVisible(use_ip)
    ip_lab.setVisible(use_ip)
    port_lab.setVisible(use_ip)

    row = QWidget()
    hl = QHBoxLayout(row)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.setSpacing(8)
    hl.addWidget(QLabel("通信:"))
    hl.addWidget(mode)
    hl.addWidget(serial, 1)
    hl.addWidget(ip_lab)
    hl.addWidget(ip)
    hl.addWidget(port_lab)
    hl.addWidget(port)
    hl.addWidget(btn)
    timeline.addStep("设备连接（Chroma）", row)

    phase = QComboBox()
    phase.addItems(["单相", "三相"])
    phase.setStyleSheet(_INPUT_QSS)
    timeline.addStep("相位选择", param_row([("相位:", phase)]))

    volt = QTextEdit()
    volt.setPlainText("230")
    volt.setStyleSheet(_INPUT_QSS)
    volt.setMaximumHeight(36)
    freq = QTextEdit()
    freq.setPlainText("50")
    freq.setStyleSheet(_INPUT_QSS)
    freq.setMaximumHeight(36)
    timeline.addStep(
        "电压/频率设置",
        param_row([("电压:", volt, "V"), ("频率:", freq, "Hz")]),
    )

    on = QPushButton("打开交流电源输出")
    off = QPushButton("关闭交流电源输出")
    apply_button_style(on, ButtonStyle.SUCCESS)
    apply_button_style(off, ButtonStyle.DANGER)
    out = QWidget()
    ol = QHBoxLayout(out)
    ol.setContentsMargins(0, 0, 0, 0)
    ol.addWidget(on)
    ol.addWidget(off)
    ol.addStretch(1)
    timeline.addStep("输出控制", out)

    log = QTextEdit()
    log.setReadOnly(True)
    log.setStyleSheet(_LOG_QSS)
    if use_ip:
        log.setPlainText(
            "通信=IP → 走 TCP/SCPI（Chroma 网口）\n"
            "填写设备 IP；端口可留空由软件自动探测\n"
            "连接成功后设置电压/频率，再开输出"
        )
    else:
        log.setPlainText(
            "通信=串口 → 走 VISA/SCPI 资源名\n"
            "在下拉框选择 ASRL/USB/TCPIP0::…::INSTR\n"
            "连接成功后设置电压/频率，再开输出"
        )
    timeline.addStep("操作说明", log, stretch=True)
    timeline.finalize()
    return timeline


def build_ac_itech() -> QWidget:
    timeline = TimelineWidget()
    ip = QLineEdit("192.168.1.88")
    ip.setStyleSheet(_INPUT_QSS)
    port = QLineEdit("502")
    port.setStyleSheet(_INPUT_QSS)
    btn = QPushButton("连接")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    btn.setFixedWidth(120)
    connect = QWidget()
    cl = QHBoxLayout(connect)
    cl.setContentsMargins(0, 0, 0, 0)
    cl.addWidget(param_row([("IP:", ip), ("端口:", port)]), 1)
    cl.addWidget(btn)
    timeline.addStep("设备连接（爱科 Itech · Modbus TCP）", connect)

    phase = QComboBox()
    phase.addItems(["单相", "三相"])
    phase.setStyleSheet(_INPUT_QSS)
    timeline.addStep("相位选择", param_row([("相位:", phase)]))

    volt = QTextEdit()
    volt.setPlainText("220")
    volt.setStyleSheet(_INPUT_QSS)
    volt.setMaximumHeight(36)
    freq = QTextEdit()
    freq.setPlainText("50")
    freq.setStyleSheet(_INPUT_QSS)
    freq.setMaximumHeight(36)
    timeline.addStep(
        "电压/频率设置",
        param_row([("电压:", volt, "V"), ("频率:", freq, "Hz")]),
    )

    on = QPushButton("打开交流电源输出")
    off = QPushButton("关闭交流电源输出")
    apply_button_style(on, ButtonStyle.SUCCESS)
    apply_button_style(off, ButtonStyle.DANGER)
    out = QWidget()
    ol = QHBoxLayout(out)
    ol.setContentsMargins(0, 0, 0, 0)
    ol.addWidget(on)
    ol.addWidget(off)
    ol.addStretch(1)
    timeline.addStep("输出控制", out)

    log = QTextEdit()
    log.setReadOnly(True)
    log.setStyleSheet(_LOG_QSS)
    log.setPlainText(
        "爱科(Itech) 交流源：顶部选「爱科(Itech)」\n"
        "必须填 IP + 端口（默认 502，Modbus TCP）\n"
        "不要用串口下拉的 SCPI 资源名"
    )
    timeline.addStep("操作说明", log, stretch=True)
    timeline.finalize()
    return timeline


def build_ac_page(brand: str, chroma_mode: str = "串口") -> QWidget:
    w, lay = _shell(f"设备管理 · 交流电源（{brand}）")
    crumb = BreadcrumbWidget(["Chroma", "爱科(Itech)"])
    stack = QStackedWidget()
    stack.addWidget(build_ac_chroma(chroma_mode))
    stack.addWidget(build_ac_itech())
    if brand.startswith("爱科"):
        crumb.setIndex(1)
        stack.setCurrentIndex(1)
    else:
        stack.setCurrentIndex(0)
    lay.addWidget(crumb)
    lay.addWidget(stack, 1)
    return w


def build_dc_chroma() -> QWidget:
    w, lay = _shell("设备管理 · 直流电源（Chroma · SCPI）")
    crumb = BreadcrumbWidget(["Chroma", "蓝电(Bluesight)", "爱科(Itech)"])
    timeline = TimelineWidget()

    mode = QComboBox()
    mode.addItems(["串口", "IP"])
    mode.setCurrentText("串口")
    mode.setStyleSheet(_INPUT_QSS)
    serial = QComboBox()
    serial.addItems(["ASRL4::INSTR", "USB0::…::INSTR", "TCPIP0::192.168.1.20::INSTR"])
    serial.setStyleSheet(_INPUT_QSS)
    btn = QPushButton("连接设备")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    row = QWidget()
    hl = QHBoxLayout(row)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.addWidget(QLabel("通信:"))
    hl.addWidget(mode)
    hl.addWidget(serial, 1)
    hl.addWidget(btn)
    timeline.addStep("设备连接", row)

    for name, val in (("Vmp", "220"), ("Voc", "250"), ("Imp", "10"), ("Isc", "12")):
        te = QTextEdit()
        te.setPlainText(val)
        te.setStyleSheet(_INPUT_QSS)
        te.setMaximumHeight(34)
        timeline.addStep(f"参数 {name}", param_row([(f"{name}:", te)]))

    on = QPushButton("打开输出")
    off = QPushButton("关闭输出")
    apply_button_style(on, ButtonStyle.SUCCESS)
    apply_button_style(off, ButtonStyle.DANGER)
    out = QWidget()
    ol = QHBoxLayout(out)
    ol.setContentsMargins(0, 0, 0, 0)
    ol.addWidget(on)
    ol.addWidget(off)
    ol.addStretch(1)
    timeline.addStep("输出控制", out)

    log = QTextEdit()
    log.setReadOnly(True)
    log.setStyleSheet(_LOG_QSS)
    log.setPlainText(
        "Chroma 直流：通信选串口 → SCPI 资源名；选 IP → 填 IP（按厂家走 SCPI/Modbus）\n"
        "蓝电：顶部切「蓝电」→ 填 IP（Modbus）\n"
        "爱科直流：顶部切「爱科」→ 按页内提示连接"
    )
    timeline.addStep("操作说明", log, stretch=True)
    timeline.finalize()
    lay.addWidget(crumb)
    lay.addWidget(timeline, 1)
    return w


def build_dc_bluesight(mode: str = "SAS") -> QWidget:
    """Full Bluesight DC page: IP + 模式 + SAS/原始负载参数 + 输出."""
    from PyQt5.QtCore import QLocale
    from PyQt5.QtWidgets import QDoubleSpinBox, QGridLayout

    w, lay = _shell(f"设备管理 · 直流电源（蓝电 Bluesight · {mode}）")
    crumb = BreadcrumbWidget(["Chroma", "蓝电(Bluesight)", "爱科(Itech)"])
    crumb.setIndex(1)
    timeline = TimelineWidget()

    # 1) connect
    ip = QLineEdit("192.168.1.50")
    ip.setStyleSheet(_INPUT_QSS)
    port = QLineEdit("502")
    port.setStyleSheet(_INPUT_QSS)
    btn = QPushButton("连接")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    btn.setFixedWidth(120)
    connect = QWidget()
    cl = QHBoxLayout(connect)
    cl.setContentsMargins(0, 0, 0, 0)
    cl.addWidget(param_row([("IP:", ip), ("端口:", port)]), 1)
    cl.addWidget(btn)
    timeline.addStep("① 设备连接（只用 IP/Modbus，不要填串口 SCPI）", connect)

    # 2) mode
    combo_mode = QComboBox()
    combo_mode.addItems(["原始负载", "SAS", "电池模拟器"])
    combo_mode.setCurrentText(mode if mode in ("原始负载", "SAS", "电池模拟器") else "SAS")
    combo_mode.setStyleSheet(_INPUT_QSS)
    combo_mode.setMinimumWidth(140)
    btn_apply_mode = QPushButton("应用模式")
    apply_button_style(btn_apply_mode, ButtonStyle.PRIMARY)
    mode_content = QWidget()
    ml = QHBoxLayout(mode_content)
    ml.setContentsMargins(0, 0, 0, 0)
    ml.setSpacing(8)
    ml.addWidget(param_row([("工作模式:", combo_mode)]), 1)
    ml.addWidget(btn_apply_mode)
    timeline.addStep("② 模式选择（必须先应用模式）", mode_content)

    # 3) params
    stacked = QStackedWidget()

    # SAS
    sas = QWidget()
    sas.setStyleSheet("background: transparent;")
    sf = QGridLayout(sas)
    sf.setContentsMargins(0, 0, 0, 0)
    sf.setSpacing(6)
    sp_pmpp = QDoubleSpinBox()
    sp_pmpp.setDecimals(3)
    sp_pmpp.setRange(0.001, 1000.0)
    sp_pmpp.setValue(8.0)
    sp_pmpp.setLocale(QLocale.c())
    sp_pmpp.setStyleSheet(_INPUT_QSS)
    sf.addWidget(QLabel("Pmpp_stc (kW):"), 0, 0)
    sf.addWidget(sp_pmpp, 0, 1)
    sp_umpp = QDoubleSpinBox()
    sp_umpp.setDecimals(2)
    sp_umpp.setRange(0.0, 2000.0)
    sp_umpp.setValue(650.0)
    sp_umpp.setLocale(QLocale.c())
    sp_umpp.setStyleSheet(_INPUT_QSS)
    sf.addWidget(QLabel("Umpp_stc (V):"), 0, 2)
    sf.addWidget(sp_umpp, 0, 3)
    sp_ff = QDoubleSpinBox()
    sp_ff.setDecimals(2)
    sp_ff.setRange(0.25, 0.95)
    sp_ff.setValue(0.8)
    sp_ff.setLocale(QLocale.c())
    sp_ff.setStyleSheet(_INPUT_QSS)
    sf.addWidget(QLabel("填充因子:"), 1, 0)
    sf.addWidget(sp_ff, 1, 1)
    btn_curve = QPushButton("发送参数到设备（曲线）")
    apply_button_style(btn_curve, ButtonStyle.INFO)
    sf.addWidget(btn_curve, 1, 2, 1, 2)
    tip_sas = QLabel("SAS：先点「应用模式」→ 填 STC 曲线参数 →「发送参数到设备（曲线）」")
    tip_sas.setStyleSheet("color:#64748b;font-size:12px;")
    sf.addWidget(tip_sas, 2, 0, 1, 4)
    stacked.addWidget(sas)

    # 原始负载
    orig = QWidget()
    orig.setStyleSheet("background: transparent;")
    ol = QVBoxLayout(orig)
    ol.setContentsMargins(0, 0, 0, 0)
    ol.setSpacing(6)
    outmode_row = QHBoxLayout()
    outmode_row.addWidget(QLabel("输出模式:"))
    combo_out = QComboBox()
    combo_out.addItems(["恒压", "恒流", "恒功率", "恒阻"])
    combo_out.setStyleSheet(_INPUT_QSS)
    combo_out.setMinimumWidth(120)
    outmode_row.addWidget(combo_out)
    btn_send = QPushButton("发送参数")
    apply_button_style(btn_send, ButtonStyle.PRIMARY)
    outmode_row.addWidget(btn_send)
    outmode_row.addStretch(1)
    ol.addLayout(outmode_row)
    grid = QGridLayout()
    v = QDoubleSpinBox()
    v.setDecimals(3)
    v.setRange(0, 2000)
    v.setValue(400)
    v.setStyleSheet(_INPUT_QSS)
    r = QDoubleSpinBox()
    r.setDecimals(3)
    r.setRange(0, 1e6)
    r.setValue(0.1)
    r.setStyleSheet(_INPUT_QSS)
    grid.addWidget(QLabel("输出电压(V):"), 0, 0)
    grid.addWidget(v, 0, 1)
    grid.addWidget(QLabel("电源内阻(Ω):"), 1, 0)
    grid.addWidget(r, 1, 1)
    ol.addLayout(grid)
    tip_o = QLabel("原始负载：恒压/恒流/恒功率/恒阻 选一种 → 填对应量 →「发送参数」")
    tip_o.setStyleSheet("color:#64748b;font-size:12px;")
    ol.addWidget(tip_o)
    stacked.addWidget(orig)

    if mode == "原始负载":
        stacked.setCurrentIndex(1)
        combo_mode.setCurrentText("原始负载")
    else:
        stacked.setCurrentIndex(0)
        combo_mode.setCurrentText("SAS")
    timeline.addStep("③ 参数设置（随模式切换）", stacked, stretch=True)

    # 4) output
    on = QPushButton("打开输出")
    off = QPushButton("关闭输出")
    apply_button_style(on, ButtonStyle.SUCCESS)
    apply_button_style(off, ButtonStyle.DANGER)
    out = QWidget()
    ohl = QHBoxLayout(out)
    ohl.setContentsMargins(0, 0, 0, 0)
    ohl.addWidget(on)
    ohl.addWidget(off)
    ohl.addStretch(1)
    timeline.addStep("④ 输出控制", out)

    log = QTextEdit()
    log.setReadOnly(True)
    log.setStyleSheet(_LOG_QSS)
    log.setPlainText(
        "蓝电操作顺序（与软件一致）：\n"
        "1) 顶栏选「蓝电(Bluesight)」\n"
        "2) 填 IP + 端口(常见502) → 连接\n"
        "3) 工作模式：原始负载 / SAS / 电池模拟器 →「应用模式」\n"
        "4) SAS：填 Pmpp_stc / Umpp_stc / 填充因子 →「发送参数到设备（曲线）」\n"
        "   原始负载：选恒压/恒流/恒功率/恒阻 → 填对应参数 →「发送参数」\n"
        "5) 打开输出\n"
        "说明：台架试验常用 SAS（光伏曲线）；不要与 Chroma 的 Vmp/Imp 串口页混用。"
    )
    timeline.addStep("操作说明", log, stretch=True)
    timeline.finalize()
    lay.addWidget(crumb)
    lay.addWidget(timeline, 1)
    return w


def build_dl850() -> QWidget:
    w, lay = _shell("设备管理 · 示波器 DL850")
    timeline = TimelineWidget()
    serial = QComboBox()
    serial.addItems(["USB0::…::INSTR", "TCPIP0::192.168.1.30::INSTR", "ASRL5::INSTR"])
    serial.setStyleSheet(_INPUT_QSS)
    btn = QPushButton("连接设备")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    row = QWidget()
    hl = QHBoxLayout(row)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.addWidget(QLabel("VISA/SCPI 资源:"))
    hl.addWidget(serial, 1)
    hl.addWidget(btn)
    timeline.addStep("设备连接", row)

    start = QPushButton("START")
    stop = QPushButton("STOP")
    apply_button_style(start, ButtonStyle.SUCCESS)
    apply_button_style(stop, ButtonStyle.DANGER)
    out = QWidget()
    ol = QHBoxLayout(out)
    ol.setContentsMargins(0, 0, 0, 0)
    ol.addWidget(start)
    ol.addWidget(stop)
    ol.addStretch(1)
    timeline.addStep("采集控制", out)

    log = QTextEdit()
    log.setReadOnly(True)
    log.setStyleSheet(_LOG_QSS)
    log.setPlainText(
        "DL850：在设备列表选 VISA 资源后连接（多为 USB/LAN SCPI）\n"
        "连接成功可用 START/STOP 试采；需要时再发单条命令\n"
        "每个试验开跑前建议确认示波器已连接（若本试验用到录波/触发）"
    )
    timeline.addStep("操作说明", log, stretch=True)
    timeline.finalize()
    lay.addWidget(timeline, 1)
    return w


def main() -> int:
    app = QApplication(sys.argv)
    pages = [
        ("D10_ac_chroma_serial.png", build_ac_page("Chroma · 串口/SCPI", "串口")),
        ("D11_ac_chroma_ip.png", build_ac_page("Chroma · IP/SCPI", "IP")),
        ("D12_ac_itech_ip.png", build_ac_page("爱科(Itech) · IP/Modbus", "串口")),
        ("D13_dc_chroma.png", build_dc_chroma()),
        ("D14_dc_bluesight_sas.png", build_dc_bluesight("SAS")),
        ("D14b_dc_bluesight_orig.png", build_dc_bluesight("原始负载")),
        ("D15_dl850.png", build_dl850()),
    ]
    for name, w in pages:
        w.show()
        app.processEvents()
        QTimer.singleShot(80, lambda: None)
        app.processEvents()
        grab(w, OUT / name)
        w.close()
    print(f"DONE -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
