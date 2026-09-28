# -*- coding: utf-8 -*-
"""主界面「继续试验」：人工暂停 / 中途暂停时显示。"""
from __future__ import annotations

from typing import Any


def sync_continue_test_button(ui: Any, *, paused: bool) -> None:
    """暂停时显示并可点；运行中隐藏。"""
    btn = getattr(ui, "pushButton_ConTest", None) if ui is not None else None
    if btn is None:
        return
    show = bool(paused)
    try:
        btn.setVisible(show)
        btn.setEnabled(show)
    except Exception:
        pass
