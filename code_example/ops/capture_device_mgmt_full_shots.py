# -*- coding: utf-8 -*-
"""Capture full device-management pages (brand + 串口/IP) for process PDF."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UTOO = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\media")
DC_BRANDS = ["Chroma", "Bluesight", "爱科(Itech)", "是德(Keysight)"]
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
    UTOO.mkdir(parents=True, exist_ok=True)
    pix.save(str(UTOO / path.name), "PNG")
    print(f"saved {path.name} ({pix.width()}x{pix.height()})")


def _shell(title: str) -> tuple[QWidget, QVBoxLayout]:
    w = QWidget()
    w.setWindowTitle(title)
    w.resize(1180, 980)
    w.setStyleSheet("background:#f8fafc;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(16, 12, 16, 12)
    lay.setSpacing(8)
    head = QLabel(title)
    head.setStyleSheet("font-size:16px;font-weight:700;color:#0f172a;")
    tip = QLabel("主界面左侧 → 设备管理")
    tip.setStyleSheet("font-size:12px;color:#64748b;")
    lay.addWidget(head)
    lay.addWidget(tip)
    return w, lay


def _empty_log() -> QTextEdit:
    log = QTextEdit()
    log.setReadOnly(True)
    log.setStyleSheet(_LOG_QSS)
    log.setMinimumHeight(72)
    return log


def _output_row(*buttons: QPushButton) -> QWidget:
    out = QWidget()
    ol = QHBoxLayout(out)
    ol.setContentsMargins(0, 0, 0, 0)
    ol.setSpacing(10)
    for button in buttons:
        ol.addWidget(button)
    ol.addStretch(1)
    return out


def build_ac_chroma(comm_mode: str = "串口") -> QWidget:
    """致茂交流：方式=串口或 IP，后面仍是相位、电压、输出、下发。"""
    timeline = TimelineWidget()
    mode = QComboBox()
    mode.addItems(["串口", "IP"])
    mode.setCurrentText(comm_mode)
    mode.setStyleSheet(_INPUT_QSS)
    mode.setFixedWidth(88)
    serial = QComboBox()
    serial.addItems(["ASRL3::INSTR", "USB0::…::INSTR", "TCPIP0::192.168.1.10::INSTR"])
    serial.setStyleSheet(_INPUT_QSS)
    serial.setMinimumWidth(280)
    ip = QLineEdit()
    ip.setPlaceholderText("如 192.168.1.100")
    ip.setStyleSheet(_INPUT_QSS)
    ip.setMinimumWidth(180)
    port = QLineEdit()
    port.setPlaceholderText("留空自动")
    port.setStyleSheet(_INPUT_QSS)
    port.setMinimumWidth(100)
    use_ip = comm_mode == "IP"
    serial.setVisible(not use_ip)
    iface = QLabel("接口")
    iface.setStyleSheet(_LABEL_QSS)
    iface.setVisible(not use_ip)
    ip_lab = QLabel("IP")
    ip_lab.setStyleSheet(_LABEL_QSS)
    port_lab = QLabel("端口")
    port_lab.setStyleSheet(_LABEL_QSS)
    ip_lab.setVisible(use_ip)
    port_lab.setVisible(use_ip)
    ip.setVisible(use_ip)
    port.setVisible(use_ip)
    btn = QPushButton("连接设备")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    btn.setFixedWidth(120)
    row = QWidget()
    hl = QHBoxLayout(row)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.setSpacing(8)
    way = QLabel("方式")
    way.setStyleSheet(_LABEL_QSS)
    hl.addWidget(way)
    hl.addWidget(mode)
    hl.addWidget(iface)
    hl.addWidget(serial, 1)
    hl.addWidget(ip_lab)
    hl.addWidget(ip)
    hl.addWidget(port_lab)
    hl.addWidget(port)
    hl.addWidget(btn)
    timeline.addStep("设备连接", row)

    phase = QComboBox()
    phase.addItems(["单相", "三相"])
    phase.setStyleSheet(_INPUT_QSS)
    timeline.addStep("相位选择（单相/三相）", phase)

    volt = QTextEdit()
    volt.setPlainText("220")
    volt.setStyleSheet(_INPUT_QSS)
    volt.setMaximumHeight(36)
    freq = QTextEdit()
    freq.setPlainText("50")
    freq.setStyleSheet(_INPUT_QSS)
    freq.setMaximumHeight(36)
    timeline.addStep("电压/频率设置", param_row([("电压", volt, "V"), ("频率", freq, "Hz")]))

    on = QPushButton("打开交流电源输出")
    off = QPushButton("关闭交流电源输出")
    apply_button_style(on, ButtonStyle.SUCCESS)
    apply_button_style(off, ButtonStyle.DANGER)
    timeline.addStep("输出控制", _output_row(on, off))

    send = QPushButton("单条命令发送")
    apply_button_style(send, ButtonStyle.PRIMARY)
    timeline.addStep("下发参数（已连接可反复下发）", _output_row(send))
    timeline.addStep("操作日志", _empty_log(), stretch=True)
    timeline.finalize()
    return timeline


def build_ac_itech() -> QWidget:
    timeline = TimelineWidget()
    ip = QLineEdit()
    ip.setPlaceholderText("如 192.168.1.100")
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
    timeline.addStep("设备连接", connect)

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
    timeline.addStep("电压/频率设置", param_row([("电压:", volt, "V"), ("频率:", freq, "Hz")]))

    on = QPushButton("打开交流电源输出")
    off = QPushButton("关闭交流电源输出")
    apply_button_style(on, ButtonStyle.SUCCESS)
    apply_button_style(off, ButtonStyle.DANGER)
    timeline.addStep("输出控制", _output_row(on, off))

    send = QPushButton("单条命令发送")
    apply_button_style(send, ButtonStyle.PRIMARY)
    timeline.addStep("单条命令测试", _output_row(send))
    timeline.addStep("操作日志", _empty_log(), stretch=True)
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


def _iv_row(vmp: str = "220", voc: str = "220", imp: str = "", isc: str = "") -> QWidget:
    from PyQt5.QtWidgets import QGridLayout

    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setSpacing(6)
    fields = (("Vmp:", vmp, 0, 0), ("Voc:", voc, 0, 2), ("Imp:", imp, 1, 0), ("Isc:", isc, 1, 2))
    for label, value, row, col in fields:
        lab = QLabel(label)
        lab.setStyleSheet(_LABEL_QSS)
        edit = QTextEdit()
        edit.setPlainText(value)
        edit.setStyleSheet(_INPUT_QSS)
        edit.setMaximumHeight(36)
        grid.addWidget(lab, row, col)
        grid.addWidget(edit, row, col + 1)
    return box


def build_dc_chroma() -> QWidget:
    """致茂直流：接口下拉，没有「方式」。是德停在第四项时用的就是这一页。"""
    w, lay = _shell("设备管理 · 直流电源1")
    crumb = BreadcrumbWidget(DC_BRANDS)
    timeline = TimelineWidget()

    serial = QComboBox()
    serial.setEditable(True)
    serial.addItems(["ASRL4::INSTR", "USB0::…::INSTR", "TCPIP0::192.168.1.20::INSTR"])
    serial.setStyleSheet(_INPUT_QSS)
    serial.setMinimumWidth(280)
    btn = QPushButton("连接设备")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    row = QWidget()
    hl = QHBoxLayout(row)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.setSpacing(8)
    iface = QLabel("接口")
    iface.setStyleSheet(_LABEL_QSS)
    hl.addWidget(iface)
    hl.addWidget(serial, 1)
    hl.addWidget(btn)
    timeline.addStep("设备连接", row)
    timeline.addStep("参数设置（IV 四点）", _iv_row())

    power = QTextEdit()
    power.setPlainText("100")
    power.setStyleSheet(_INPUT_QSS)
    power.setMaximumHeight(36)
    timeline.addStep("功率设置（功率%）", param_row([("功率%:", power, "%")]))

    on = QPushButton("打开直流电源1输出")
    off = QPushButton("关闭直流电源1输出")
    apply_button_style(on, ButtonStyle.SUCCESS)
    apply_button_style(off, ButtonStyle.DANGER)
    timeline.addStep("输出控制", _output_row(on, off))

    which = QComboBox()
    which.addItems(["DC1", "DC2", "DC3", "DC4"])
    which.setStyleSheet(_INPUT_QSS)
    send = QPushButton("直流源设置")
    apply_button_style(send, ButtonStyle.PRIMARY)
    timeline.addStep("下发 IV 曲线（已连接可反复下发）", _output_row(which, send))

    query = QLineEdit()
    query.setPlaceholderText("输入SCPI…")
    query.setStyleSheet(_INPUT_QSS)
    query_btn = QPushButton("单条命令发送query")
    timeline.addStep("单条命令查询", _output_row(query, query_btn))
    timeline.addStep("操作日志", _empty_log(), stretch=True)
    timeline.finalize()
    lay.addWidget(crumb)
    lay.addWidget(timeline, 1)
    return w


def build_dc_itech() -> QWidget:
    """爱科直流是独立一页：串口/IP 切换，再填 IV，按钮是「下发 IV 参数」。"""
    w, lay = _shell("设备管理 · 直流电源1")
    crumb = BreadcrumbWidget(DC_BRANDS)
    crumb.setIndex(2)
    timeline = TimelineWidget()

    mode = QComboBox()
    mode.addItems(["串口", "IP"])
    mode.setCurrentText("IP")
    mode.setStyleSheet(_INPUT_QSS)
    mode.setFixedWidth(100)
    ip = QLineEdit()
    ip.setPlaceholderText("如 192.168.1.100")
    ip.setStyleSheet(_INPUT_QSS)
    port = QLineEdit()
    port.setPlaceholderText("502")
    port.setStyleSheet(_INPUT_QSS)
    btn = QPushButton("连接")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    btn.setFixedWidth(120)
    row = QWidget()
    hl = QHBoxLayout(row)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.setSpacing(8)
    hl.addWidget(mode)
    hl.addWidget(QLabel("IP:"))
    hl.addWidget(ip)
    hl.addWidget(QLabel("端口:"))
    hl.addWidget(port)
    hl.addWidget(btn)
    hl.addStretch(1)
    timeline.addStep("设备连接", row)
    timeline.addStep("参数设置（IV 四点）", _iv_row(voc="220"))

    send = QPushButton("下发 IV 参数（已连接可反复下发）")
    apply_button_style(send, ButtonStyle.PRIMARY)
    timeline.addStep("下发 IV 参数", _output_row(send))

    on = QPushButton("打开输出")
    off = QPushButton("关闭输出")
    apply_button_style(on, ButtonStyle.SUCCESS)
    apply_button_style(off, ButtonStyle.DANGER)
    timeline.addStep("输出控制", _output_row(on, off))
    timeline.addStep("操作日志", _empty_log(), stretch=True)
    timeline.finalize()
    lay.addWidget(crumb)
    lay.addWidget(timeline, 1)
    return w


def build_dc_bluesight(mode: str = "SAS") -> QWidget:
    """Full Bluesight DC page: IP + 模式 + SAS/原始负载参数 + 输出."""
    from PyQt5.QtCore import QLocale
    from PyQt5.QtWidgets import QDoubleSpinBox, QGridLayout

    w, lay = _shell(f"设备管理 · 直流电源（蓝电 Bluesight · {mode}）")
    crumb = BreadcrumbWidget(DC_BRANDS)
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
        "1) 顶栏选第二项「Bluesight」\n"
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


def build_dc_keysight() -> QWidget:
    """是德与致茂共用同一套填写，面包屑必须停在第四项。"""
    w = build_dc_chroma()
    w.setWindowTitle("设备管理 · 直流电源1")
    title = w.findChild(QLabel)
    if title is not None:
        title.setText("设备管理 · 直流电源1")
    crumb = w.findChild(BreadcrumbWidget)
    if crumb is not None:
        crumb.setIndex(3)
    return w


def build_dl850() -> QWidget:
    w, lay = _shell("设备管理 · DL850 示波器")
    timeline = TimelineWidget()
    serial = QComboBox()
    serial.setEditable(True)
    serial.addItems(["USB0::…::INSTR", "TCPIP0::192.168.1.30::INSTR", "ASRL5::INSTR"])
    serial.setStyleSheet(_INPUT_QSS)
    btn = QPushButton("连接设备")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    row = QWidget()
    hl = QHBoxLayout(row)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.setSpacing(8)
    iface = QLabel("接口")
    iface.setStyleSheet(_LABEL_QSS)
    hl.addWidget(iface)
    hl.addWidget(serial, 1)
    hl.addWidget(btn)
    timeline.addStep("设备连接", row)

    start = QPushButton("START")
    stop = QPushButton("STOP")
    save = QPushButton("Save Picture")
    apply_button_style(start, ButtonStyle.SUCCESS)
    apply_button_style(stop, ButtonStyle.DANGER)
    timeline.addStep("采集控制", _output_row(start, stop, save))

    query = QTextEdit()
    query.setPlainText("220")
    query.setStyleSheet(_INPUT_QSS)
    query.setMaximumHeight(36)
    query_btn = QPushButton("单条命令发送query")
    timeline.addStep("命令查询", _output_row(query, query_btn))

    write = QTextEdit()
    write.setPlainText("220")
    write.setStyleSheet(_INPUT_QSS)
    write.setMaximumHeight(36)
    write_btn = QPushButton("单条命令发送write")
    timeline.addStep("命令发送", _output_row(write, write_btn))
    timeline.addStep("操作日志", _empty_log(), stretch=True)
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
        ("D17_dc_itech.png", build_dc_itech()),
        ("D16_dc_keysight.png", build_dc_keysight()),
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
