# -*- coding: utf-8 -*-
"""功率分析仪比例系数。电压 VT、电流 CT，1 表示不缩放。

连接页填写后，必须点「下发并保存」才会写入配置档并下发到仪器。
连接设备时不再自动改变比。
"""
from __future__ import annotations

from PyQt5 import QtCore, QtWidgets

from utils.wt_channel_scale import SCALE_ELEMENTS, scale_object_name


def add_wt_scale_group(parent, layout, element_count: int) -> QtWidgets.QGroupBox:
    """插入比例系数。连接页用 7 个元素，覆盖 WT3000 / 1800 / 1806 / 5000。"""
    count = max(1, min(int(element_count or 1), len(SCALE_ELEMENTS)))
    group = QtWidgets.QGroupBox("VT / CT 填写")
    group.setToolTip(
        "在这里填写一次即可。点「下发并保存」后按手册写 :INPUT:SCALING:VT/CT:ELEMENTn。"
        "1 表示不缩放。未点按钮不会改仪器、也不会写配置档。"
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
    """功率分析仪连接页上的比例系数。仅「下发并保存」会写档并改仪器。"""
    from utils.wt_channel_scale import load_saved_scales, save_saved_scales, scales_from_root
    from utils.wt_scale_probe import apply_scales, prepare_probe, read_probe

    panel = QtWidgets.QWidget()
    panel.setObjectName("widget_wt_scale")
    panel.setMinimumHeight(280)
    layout = QtWidgets.QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    tip = QtWidgets.QLabel(
        "改完 VT/CT 后必须点上方蓝色「下发并保存」才会写入配置档并下发到仪器。"
        "连接设备不会自动改变比。交流源、直流源通电后可再点「开始试读」核对。"
    )
    tip.setWordWrap(True)
    tip.setStyleSheet(
        "QLabel { color: #1e40af; background-color: #eff6ff; border: 1px solid #bfdbfe; "
        "border-radius: 6px; padding: 6px 10px; font-size: 12px; }"
    )
    layout.addWidget(tip)

    # 按钮挂到 host，由时间线「比例系数下发」单独一行展示（避免塞进竖向面板后被裁切看不见）
    apply_btn = QtWidgets.QPushButton("下发并保存")
    apply_btn.setObjectName("pushButton_wt_scale_apply")
    apply_btn.setMinimumHeight(36)
    apply_btn.setMinimumWidth(120)
    apply_btn.setCursor(QtCore.Qt.PointingHandCursor)
    apply_btn.setStyleSheet(
        "QPushButton { background:#2563eb; color:#fff; border:none; border-radius:8px; "
        "padding:8px 16px; font-size:13px; font-weight:600; }"
        "QPushButton:hover { background:#1d4ed8; }"
        "QPushButton:disabled { background:#94a3b8; }"
    )
    apply_btn.setToolTip("保存到 config_files/wt_scale.ini，并下发 :INPUT:SCALING… 到已连接的功率分析仪")
    probe_btn = QtWidgets.QPushButton("开始试读")
    probe_btn.setObjectName("pushButton_wt_scale_probe")
    probe_btn.setMinimumHeight(36)
    probe_btn.setToolTip("读取各元素 U/I/P/频率；不会自动下发变比，请先点「下发并保存」")
    once_btn = QtWidgets.QPushButton("读一次")
    once_btn.setObjectName("pushButton_wt_scale_once")
    once_btn.setMinimumHeight(36)
    once_btn.setToolTip("只读当前一帧，不持续刷新；不会自动下发变比")

    add_wt_scale_group(host, layout, len(SCALE_ELEMENTS))
    saved = load_saved_scales()
    for name, text in saved.items():
        edit = getattr(host, name, None)
        if edit is not None and hasattr(edit, "setText") and str(text).strip():
            edit.setText(str(text).strip())

    status = QtWidgets.QLabel("未下发。改完系数后点「下发并保存」。")
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

    # 挂到 host，便于时间线单独排一行（更醒目）
    setattr(host, "pushButton_wt_scale_apply", apply_btn)
    setattr(host, "pushButton_wt_scale_probe", probe_btn)
    setattr(host, "pushButton_wt_scale_once", once_btn)
    setattr(host, "widget_wt_scale", panel)

    state = {"items": [], "running": False, "applied": False}

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
        ctrl = _controller()
        if ctrl is None or not bool(getattr(ctrl, "connected", False)):
            status.setText("已保存到配置档。功率分析仪未连接，连上后再点一次「下发并保存」写入仪器。")
            state["applied"] = False
            QtWidgets.QMessageBox.information(
                panel,
                "比例系数",
                "数值已保存到本机配置档。\n请先连接功率分析仪，再点「下发并保存」写入仪器。",
            )
            return
        ok, message, _cmds = apply_scales(ctrl, _current_scales())
        status.setText(message)
        state["applied"] = bool(ok)
        if ok:
            QtWidgets.QMessageBox.information(panel, "比例系数", message)
        else:
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

    def _ensure_probe_items():
        ctrl = _controller()
        if ctrl is None or not bool(getattr(ctrl, "connected", False)):
            return False, "请先连接功率分析仪"
        ok, message, items = prepare_probe(ctrl)
        if not ok:
            return False, message
        state["items"] = items
        return True, message

    def _start_probe() -> None:
        # 试读不再偷偷下发变比，避免「连上就改仪器」
        ok, message = _ensure_probe_items()
        if not ok:
            status.setText(message)
            QtWidgets.QMessageBox.warning(panel, "试读", message)
            return
        hint = "" if state["applied"] else "（若刚改过系数，请先点「下发并保存」）"
        status.setText(f"{message}{hint}")
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
        if not state["items"]:
            ok, message = _ensure_probe_items()
            if not ok:
                status.setText(message)
                QtWidgets.QMessageBox.warning(panel, "试读", message)
                return
            status.setText(message)
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
    # 不再 editingFinished 自动写档；只有点「下发并保存」才保存/下发
    return panel
