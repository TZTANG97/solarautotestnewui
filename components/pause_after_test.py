# -*- coding: utf-8 -*-
"""试验设定顶栏：后续试验是否暂停（改逆变器后再继续）。"""
from __future__ import annotations

from typing import Any


def install_pause_after_checkbox(ui: Any) -> None:
    """在「测试追加」旁插入勾选框；追加完成后写入 QUEUE 标记行。"""
    if ui is None or getattr(ui, "checkBox_PauseAfterNext", None) is not None:
        return
    btn = getattr(ui, "pushButton_TestAppend", None)
    if btn is None:
        return
    try:
        if hasattr(btn, "isVisible") and not btn.isVisible() and btn.objectName() == "pushButton_TestAppend":
            # WT 设定页隐藏了追加按钮，不装
            if "WT" in type(ui).__name__ or "WT" in str(getattr(ui, "objectName", lambda: "")()):
                return
    except Exception:
        pass

    from PyQt5 import QtCore, QtWidgets

    cb = QtWidgets.QCheckBox("后续试验暂停")
    cb.setObjectName("checkBox_PauseAfterNext")
    cb.setChecked(False)
    cb.setToolTip(
        "勾选后：本试验全部命令跑完先停住，方便改逆变器/上位机；"
        "在主界面点「继续试验」再跑后面追加的项目。"
    )
    cb.setStyleSheet("QCheckBox { font-size: 12px; color: #1e293b; spacing: 6px; background: transparent; }")
    ui.checkBox_PauseAfterNext = cb

    parent = btn.parentWidget()
    layout = parent.layout() if parent is not None else None
    inserted = False
    if layout is not None:
        try:
            idx = layout.indexOf(btn)
            if idx >= 0:
                layout.insertWidget(idx + 1, cb)
                inserted = True
        except Exception:
            inserted = False
    if not inserted:
        try:
            btn.parentWidget().layout().addWidget(cb)
        except Exception:
            cb.setParent(parent or btn)

    def _schedule_marker() -> None:
        QtCore.QTimer.singleShot(0, lambda: _append_queue_marker(ui))

    try:
        btn.clicked.connect(_schedule_marker)
    except Exception:
        pass


def _append_queue_marker(ui: Any) -> None:
    try:
        import SCPITestWave as sw
    except Exception:
        return
    arr = getattr(sw, "strArrayTest", None)
    if not isinstance(arr, list) or not arr:
        return
    cb = getattr(ui, "checkBox_PauseAfterNext", None)
    pause = bool(cb.isChecked()) if cb is not None else False
    name = ""
    try:
        name = str(sw.ui.comboBox_PS.currentText() or "").strip()
    except Exception:
        name = ""
    try:
        from utils.append_mode import ensure_queue_end_marker

        ensure_queue_end_marker(sw.__dict__, name or "试验", pause_after=pause)
    except Exception:
        from utils.test_queue_markers import is_queue_end_row, make_queue_end_row

        row = make_queue_end_row(name, pause_after=pause)
        if is_queue_end_row(arr[-1]):
            arr[-1] = row
        else:
            arr.append(row)
    try:
        hint = "本试验结束后暂停，等人工改逆变器再继续" if pause else "本试验结束后直接进入下一项"
        sw.ui.textEdit_ReturnMessage.append(f"[{name or '试验'}] {hint}")
    except Exception:
        pass
