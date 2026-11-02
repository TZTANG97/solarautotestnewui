# -*- coding: utf-8 -*-
"""功率分析仪比例系数。电压 VT、电流 CT，1 表示不缩放。

连接页可下发到仪器并试读 U/I/P/频率，交流源、直流源通电后直接核对，
不必再开 WT 上位机。
"""
from __future__ import annotations

from PyQt5 import QtCore, QtWidgets

from utils.wt_channel_scale import SCALE_ELEMENTS, scale_object_name


def add_wt_scale_group(parent, layout, element_count: int) -> QtWidgets.QGroupBox:
    """插入比例系数。连接页用 7 个元素，覆盖 WT3000 / 1800 / 1806 / 5000。"""
    count = max(1, min(int(element_count or 1), len(SCALE_ELEMENTS)))
    group = QtWidgets.QGroupBox("比例系数")
    group.setToolTip(
        "在这里填写一次即可。SCPI 开测按手册下发 :INPUT:SCALING:VT/CT:ELEMENTn。1 表示不缩放。"
        "数值写入 config_files/wt_scale.ini，下次打开还是这次填的。"
    )
    grid = QtWidgets.QGridLayout(group)
    grid.setSpacing(6)
    grid.setContentsMargins(8, 12, 8, 8)
    grid.addWidget(QtWidgets.QLabel("电压 VT"), 0, 1)
    grid.addWidget(QtWidgets.QLabel("电流 CT"), 0, 3)
    for index, element in enumerate(SCALE_ELEMENTS[:count]):
        row = index + 1
        grid.addWidget(QtWidgets.QLabel(f"E{element}"), row, 0)
        for column, kind in ((1, "vt"), (3, "ct")):
            edit = QtWidgets.QLineEdit("1")
            name = scale_object_name(kind, element)
            edit.setObjectName(name)
            edit.setFixedWidth(72)
            edit.setPlaceholderText("1")
            edit.setToolTip(f"元素 {element} 的 {kind.upper()} 比例系数，1 表示不缩放")
            setattr(parent, name, edit)
            grid.addWidget(edit, row, column)
    layout.addWidget(group)
    return group


def build_connection_scale_panel(host) -> QtWidgets.QWidget:
    """功率分析仪连接页上的比例系数。可下发、试读，离开输入框时写入配置档。"""
    from utils.wt_channel_scale import load_saved_scales, save_saved_scales, scales_from_root
    from utils.wt_scale_probe import apply_scales, prepare_probe, read_probe

    panel = QtWidgets.QWidget()
    panel.setObjectName("widget_wt_scale")
    panel.setMinimumHeight(360)
    layout = QtWidgets.QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    add_wt_scale_group(host, layout, len(SCALE_ELEMENTS))
    saved = load_saved_scales()
    for name, text in saved.items():
        edit = getattr(host, name, None)
        if edit is not None and hasattr(edit, "setText") and str(text).strip():
            edit.setText(str(text).strip())

    tip = QtWidgets.QLabel(
        "先连好功率分析仪，交流源、直流源通电后：点「下发到仪器」，再点「开始试读」。"
        "对照显示的电压电流调比例系数，调完再下发，不必打开 WT 上位机。"
    )
    tip.setWordWrap(True)
    tip.setStyleSheet(
        "QLabel { color: #1e40af; background-color: #eff6ff; border: 1px solid #bfdbfe; "
        "border-radius: 6px; padding: 6px 10px; font-size: 12px; }"
    )
    layout.addWidget(tip)

    row = QtWidgets.QHBoxLayout()
    row.setSpacing(8)
    apply_btn = QtWidgets.QPushButton("下发到仪器")
    apply_btn.setObjectName("pushButton_wt_scale_apply")
    apply_btn.setToolTip("把当前 VT/CT 按手册写成 :INPUT:SCALING…")
    probe_btn = QtWidgets.QPushButton("开始试读")
    probe_btn.setObjectName("pushButton_wt_scale_probe")
    probe_btn.setToolTip("读取各元素 U/I/P/频率，方便核对比例系数")
    once_btn = QtWidgets.QPushButton("读一次")
    once_btn.setObjectName("pushButton_wt_scale_once")
    once_btn.setToolTip("只读当前一帧，不持续刷新")
    row.addWidget(apply_btn)
    row.addWidget(probe_btn)
    row.addWidget(once_btn)
    row.addStretch(1)
    layout.addLayout(row)

    status = QtWidgets.QLabel("未试读")
    status.setObjectName("label_wt_scale_status")
    status.setWordWrap(True)
    layout.addWidget(status)

    live = QtWidgets.QLabel("试读结果会显示在这里")
    live.setObjectName("label_wt_scale_live")
    live.setWordWrap(True)
    live.setMinimumHeight(90)
    live.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    live.setStyleSheet(
        "QLabel { background: #0f172a; color: #e2e8f0; border-radius: 6px; "
        "padding: 8px 10px; font-family: Consolas, 'Courier New', monospace; font-size: 12px; }"
    )
    layout.addWidget(live)

    state = {"items": [], "running": False}

    def _persist() -> None:
        payload = {}
        for element in SCALE_ELEMENTS:
            for kind in ("vt", "ct"):
                name = scale_object_name(kind, element)
                edit = getattr(host, name, None)
                payload[name] = edit.text().strip() if edit is not None and hasattr(edit, "text") else "1"
        save_saved_scales(payload)

    def _controller():
        try:
            from utils.wt_scpi_session import _get_controller

            return _get_controller()
        except Exception:
            return None

    def _current_scales():
        live_map = scales_from_root(host)
        return live_map or load_saved_scales()

    def _on_apply() -> None:
        _persist()
        ok, message, _cmds = apply_scales(_controller(), _current_scales())
        status.setText(message)
        if not ok:
            QtWidgets.QMessageBox.warning(panel, "比例系数", message)

    def _refresh_once() -> bool:
        ok, message, measures = read_probe(_controller(), state["items"])
        if ok:
            live.setText(message)
            status.setText("试读中" if state["running"] else "已读一帧")
            return True
        status.setText(message)
        return False

    def _stop_probe() -> None:
        state["running"] = False
        probe_btn.setText("开始试读")
        timer.stop()

    def _start_probe() -> None:
        _persist()
        ctrl = _controller()
        ok_scale, scale_msg, _ = apply_scales(ctrl, _current_scales())
        if not ok_scale:
            status.setText(scale_msg)
            QtWidgets.QMessageBox.warning(panel, "比例系数", scale_msg)
            return
        ok, message, items = prepare_probe(ctrl)
        status.setText(f"{scale_msg}；{message}" if ok else message)
        if not ok:
            QtWidgets.QMessageBox.warning(panel, "试读", message)
            return
        state["items"] = items
        state["running"] = True
        probe_btn.setText("停止试读")
        _refresh_once()
        timer.start(500)

    def _toggle_probe() -> None:
        if state["running"]:
            _stop_probe()
            status.setText("已停止试读")
            return
        _start_probe()

    def _on_once() -> None:
        _persist()
        ctrl = _controller()
        if not state["items"]:
            ok_scale, scale_msg, _ = apply_scales(ctrl, _current_scales())
            if not ok_scale:
                status.setText(scale_msg)
                QtWidgets.QMessageBox.warning(panel, "比例系数", scale_msg)
                return
            ok, message, items = prepare_probe(ctrl)
            if not ok:
                status.setText(message)
                QtWidgets.QMessageBox.warning(panel, "试读", message)
                return
            state["items"] = items
            status.setText(f"{scale_msg}；{message}")
        _refresh_once()

    timer = QtCore.QTimer(panel)
    timer.setInterval(500)
    timer.timeout.connect(_refresh_once)

    apply_btn.clicked.connect(_on_apply)
    probe_btn.clicked.connect(_toggle_probe)
    once_btn.clicked.connect(_on_once)

    panel.persist_scales = _persist  # type: ignore[attr-defined]
    panel.apply_scales_now = _on_apply  # type: ignore[attr-defined]
    panel.stop_scale_probe = _stop_probe  # type: ignore[attr-defined]
    for element in SCALE_ELEMENTS:
        for kind in ("vt", "ct"):
            edit = getattr(host, scale_object_name(kind, element), None)
            if edit is not None and hasattr(edit, "editingFinished"):
                edit.editingFinished.connect(_persist)
    return panel
