# -*- coding: utf-8 -*-
"""Capture WT3000 / DEWETRON device-management screenshots for autotest-docs."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from Dialog_DEWETRON_Setting import Ui_Dialog_DEWETRON_Setting
from components.breadcrumb import BreadcrumbWidget
from components.buttons import ButtonStyle, apply_button_style
from components.timeline import TimelineWidget, _CONNECT_BTN_QSS, _INPUT_QSS, _LOG_QSS

OUT = ROOT / "code_example" / "media" / "overload_flow_shots"
UTOO = Path(r"E:\utoo\utoo-pydjango\utoo-web-front\public\autotest-docs\media")


def grab(widget: QWidget, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    QApplication.instance().processEvents()
    pix = widget.grab()
    if pix.isNull():
        raise RuntimeError(f"empty grab {path}")
    if not pix.save(str(path), "PNG"):
        raise RuntimeError(f"save failed {path}")
    print(f"saved {path.name} ({pix.width()}x{pix.height()})")
    if UTOO.exists():
        UTOO.mkdir(parents=True, exist_ok=True)
        dest = UTOO / path.name
        pix.save(str(dest), "PNG")
        print(f"  -> utoo {dest.name}")


def _shell(title: str, size=(1180, 900)) -> tuple[QWidget, QVBoxLayout]:
    w = QWidget()
    w.setWindowTitle(title)
    w.resize(*size)
    w.setStyleSheet("background:#f8fafc;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(16, 12, 16, 12)
    lay.setSpacing(8)
    head = QLabel(title)
    head.setStyleSheet("font-size:16px;font-weight:700;color:#0f172a;")
    tip = QLabel("主界面左侧设备页 · 与软件实际布局一致的操作示意")
    tip.setStyleSheet("font-size:12px;color:#64748b;")
    lay.addWidget(head)
    lay.addWidget(tip)
    return w, lay


def build_wt3000_device_page() -> QWidget:
    """Match SCPITestWave _WT3000_GRID: tips / IP / baud / connect / flicker."""
    w, lay = _shell("设备管理 · WT3000 功率分析仪", (1100, 780))
    crumb = BreadcrumbWidget(["首页", "设备管理", "WT3000"])
    timeline = TimelineWidget()

    tips = QLabel(
        "提示: 网口连接请填写IP地址，点击连接; "
        "串口连接请保持IP为空，从下拉框选择串口后点击连接"
    )
    tips.setWordWrap(True)
    tips.setStyleSheet(
        "QLabel { color: #1e40af; background-color: #eff6ff; border: 1px solid #bfdbfe; "
        "border-radius: 6px; padding: 8px 12px; font-size: 12px; }"
    )
    timeline.addStep("使用说明", tips)

    ip = QLineEdit("192.168.40.19")
    ip.setPlaceholderText("IP地址 (如 192.168.1.100)")
    ip.setStyleSheet(_INPUT_QSS)
    ip.setMinimumWidth(180)
    port = QLineEdit("5025")
    port.setPlaceholderText("端口 (默认5025)")
    port.setStyleSheet(_INPUT_QSS)
    port.setMinimumWidth(110)
    ip_row = QWidget()
    ih = QHBoxLayout(ip_row)
    ih.setContentsMargins(0, 0, 0, 0)
    ih.setSpacing(8)
    ih.addWidget(QLabel("IP:"))
    ih.addWidget(ip)
    ih.addWidget(QLabel("端口:"))
    ih.addWidget(port)
    ih.addStretch(1)
    timeline.addStep("IP地址（网口优先）", ip_row)

    baud = QComboBox()
    baud.addItems(["9600", "19200", "38400", "57600", "115200"])
    baud.setCurrentText("9600")
    baud.setStyleSheet(_INPUT_QSS)
    baud.setFixedWidth(140)
    baud_row = QWidget()
    bh = QHBoxLayout(baud_row)
    bh.setContentsMargins(0, 0, 0, 0)
    bh.addWidget(QLabel("波特率:"))
    bh.addWidget(baud)
    bh.addStretch(1)
    timeline.addStep("波特率设置（串口时用）", baud_row)

    combo = QComboBox()
    combo.addItems(
        [
            "TCPIP0::192.168.40.19::inst0::INSTR",
            "ASRL3::INSTR",
            "USB0::0x0B21::0x002E::INSTR",
        ]
    )
    combo.setStyleSheet(_INPUT_QSS)
    combo.setMinimumWidth(320)
    btn = QPushButton("连接设备")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    set_btn = QPushButton("设定WT3000")
    apply_button_style(set_btn, ButtonStyle.SUCCESS)
    set_btn.setFixedWidth(110)
    conn = QWidget()
    ch = QHBoxLayout(conn)
    ch.setContentsMargins(0, 0, 0, 0)
    ch.setSpacing(8)
    ch.addWidget(QLabel("接口:"))
    ch.addWidget(combo, 1)
    ch.addWidget(btn)
    ch.addWidget(set_btn)
    timeline.addStep("设备连接", conn)

    flicker = QPushButton("切换闪变页面")
    apply_button_style(flicker, ButtonStyle.PRIMARY)
    flicker.setFixedWidth(140)
    fr = QWidget()
    fh = QHBoxLayout(fr)
    fh.setContentsMargins(0, 0, 0, 0)
    fh.addWidget(flicker)
    fh.addStretch(1)
    timeline.addStep("测试命令（已连接后）", fr)

    log = QTextEdit()
    log.setReadOnly(True)
    log.setStyleSheet(_LOG_QSS)
    log.setPlainText(
        "WT3000 连接顺序：\n"
        "1) 左侧菜单进入「WT3000」设备页\n"
        "2) 网口：填 IP（常见 192.168.x.x）+ 端口（常见 5025）→「连接设备」\n"
        "3) 串口：IP 留空，在接口下拉框选串口资源 →「连接设备」；波特率按设备设定\n"
        "4) 连接成功后按钮变为「取消连接」；需要时可点「设定WT3000」改波特率\n"
        "说明：本页只管「连上仪器」。试验里的测量项目/保存路径在各自试验对话框的「功率分析仪」步骤配置，不是本页。"
    )
    timeline.addStep("操作说明", log, stretch=True)
    timeline.finalize()
    lay.addWidget(crumb)
    lay.addWidget(timeline, 1)
    return w


def build_wt3000_baud_dialog() -> QDialog:
    dlg = QDialog()
    dlg.setWindowTitle("WT3000参数设置")
    dlg.resize(420, 220)
    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(20, 16, 20, 16)
    tip = QLabel("设备管理页「设定WT3000」弹出：串口通信时核对波特率后点确认。")
    tip.setWordWrap(True)
    tip.setStyleSheet("color:#64748b;font-size:12px;")
    lay.addWidget(tip)
    row = QHBoxLayout()
    row.addWidget(QLabel("波特率:"))
    baud = QComboBox()
    baud.addItems(["9600", "19200", "38400", "57600", "115200"])
    baud.setCurrentText("9600")
    baud.setStyleSheet(_INPUT_QSS)
    baud.setFixedWidth(140)
    row.addWidget(baud)
    row.addStretch(1)
    lay.addLayout(row)
    ok = QPushButton("确认")
    apply_button_style(ok, ButtonStyle.PRIMARY)
    ok.setFixedWidth(90)
    lay.addWidget(ok, alignment=Qt.AlignLeft)
    lay.addStretch(1)
    return dlg


def build_dewetron_connect_shell() -> QWidget:
    """Device page: IP connect bar + embedded DEWETRON setting (wiring)."""
    w, lay = _shell("设备管理 · 德威创 DEWETRON", (1400, 960))
    crumb = BreadcrumbWidget(["首页", "设备管理", "德威创"])
    lay.addWidget(crumb)

    card = QWidget()
    card.setStyleSheet(
        "QWidget#dewCard { background:#fff; border:1px solid #e2e8f0; border-radius:10px; }"
    )
    card.setObjectName("dewCard")
    cl = QVBoxLayout(card)
    cl.setContentsMargins(14, 12, 14, 12)
    cl.setSpacing(10)

    title = QLabel("① 先连接设备（IP）")
    title.setStyleSheet("font-size:14px;font-weight:700;color:#0f172a;")
    cl.addWidget(title)

    row = QHBoxLayout()
    row.setSpacing(8)
    row.addWidget(QLabel("IP地址:"))
    ip = QLineEdit("192.168.40.21")
    ip.setStyleSheet(_INPUT_QSS)
    ip.setMinimumWidth(160)
    row.addWidget(ip)
    row.addWidget(QLabel("端口:"))
    port = QLineEdit("10001")
    port.setStyleSheet(_INPUT_QSS)
    port.setFixedWidth(90)
    row.addWidget(port)
    btn = QPushButton("连接设备")
    btn.setStyleSheet(_CONNECT_BTN_QSS)
    row.addWidget(btn)
    row.addStretch(1)
    cl.addLayout(row)

    note = QLabel(
        "电脑与德威创须同一网段；确认 OXYGEN 未占用远程连接（通常只允许 1 个客户端）。"
        "连接成功后再做下方接线与通道绑定。"
    )
    note.setWordWrap(True)
    note.setStyleSheet("color:#92400e;background:#fffbeb;border:1px solid #fde68a;border-radius:6px;padding:8px;font-size:12px;")
    cl.addWidget(note)

    sub = QLabel("② 接线类型、通道绑定与设备参数（连接成功后操作）")
    sub.setStyleSheet("font-size:14px;font-weight:700;color:#0f172a;margin-top:4px;")
    cl.addWidget(sub)

    dew = QWidget()
    ui = Ui_Dialog_DEWETRON_Setting()
    ui.setupUi(dew)
    # Pre-fill a typical 1P2W mapping for a clearer shot
    try:
        ui.lineEdit_deviceIP.setText("192.168.40.21")
        ui.lineEdit_port.setText("10001")
        # bind U1/I1 if slots exist
        slots = getattr(ui, "_slot_input_widgets", {})
        if "U1" in slots:
            slots["U1"].set_channel("AI 1/U1")
        if "I1" in slots:
            slots["I1"].set_channel("AI 1/l1")
        ui.textEdit_log.setPlainText(
            "[OK] DEWETRON 已连接 192.168.40.21:10001\n"
            "请选择接线类型 → 绑定通道 → 点「保存」应用配置"
        )
    except Exception as exc:
        print(f"prefill dew: {exc}")

    cl.addWidget(dew, 1)
    lay.addWidget(card, 1)
    return w


def build_dewetron_wiring_only(wiring_btn_attr: str, out_name: str) -> tuple[QWidget, str]:
    dlg = QDialog()
    dlg.setWindowTitle("DEWETRON 设置 · 接线图")
    dlg.resize(1380, 900)
    ui = Ui_Dialog_DEWETRON_Setting()
    ui.setupUi(dlg)
    btn = getattr(ui, wiring_btn_attr, None)
    if btn is not None:
        btn.click()
    QApplication.instance().processEvents()
    slots = getattr(ui, "_slot_input_widgets", {})
    # Fill first available U/I slots for demo
    u_slots = [k for k in slots if k.startswith("U")]
    i_slots = [k for k in slots if k.startswith("I")]
    for i, key in enumerate(u_slots[:3]):
        slots[key].set_channel(f"AI 1/U{i+1}")
    for i, key in enumerate(i_slots[:3]):
        slots[key].set_channel(f"AI 1/l{i+1}")
    ui.lineEdit_deviceIP.setText("192.168.40.21")
    ui.lineEdit_port.setText("10001")
    return dlg, out_name


def main() -> int:
    app = QApplication(sys.argv)
    OUT.mkdir(parents=True, exist_ok=True)

    wt = build_wt3000_device_page()
    wt.show()
    app.processEvents()
    QTimer.singleShot(80, lambda: None)
    app.processEvents()
    grab(wt, OUT / "D05_device_wt3000e.png")
    wt.close()

    baud_dlg = build_wt3000_baud_dialog()
    baud_dlg.show()
    app.processEvents()
    grab(baud_dlg, OUT / "D05b_wt3000_baud.png")
    baud_dlg.close()

    dew_full = build_dewetron_connect_shell()
    dew_full.show()
    app.processEvents()
    QTimer.singleShot(120, lambda: None)
    app.processEvents()
    grab(dew_full, OUT / "D03_device_dewetron.png")
    dew_full.close()

    for attr, name in (
        ("btn_wiring_1P2W", "D03b_dewetron_1p2w.png"),
        ("btn_wiring_3P4W", "D03c_dewetron_3p4w.png"),
    ):
        dlg, _ = build_dewetron_wiring_only(attr, name)
        dlg.show()
        app.processEvents()
        QTimer.singleShot(100, lambda: None)
        app.processEvents()
        grab(dlg, OUT / name)
        dlg.close()

    print(f"DONE -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
