# -*- coding: utf-8 -*-
"""WTViewerEfree（宏 Soft Panel）是否在跑：空闲时也要能上报网页「已连接」。

宏模式不建 wt3000_controller SCPI 会话，旧逻辑只看 controller.connected，
导致 Soft Panel 已连、试验未跑时网页仍灰。
"""
from __future__ import annotations

from typing import Callable, Optional


def wtviewer_window_alive(
    *,
    enum_windows: Optional[Callable[[], dict]] = None,
) -> bool:
    """主窗口标题含 WTViewerEfree / WTViewer 即视为 Soft Panel 会话在。"""
    titles: dict = {}
    if enum_windows is not None:
        try:
            titles = dict(enum_windows() or {})
        except Exception:
            titles = {}
    else:
        try:
            import win32gui

            def _cb(hwnd, out):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        text = win32gui.GetWindowText(hwnd) or ""
                        if text:
                            out[hwnd] = text
                except Exception:
                    pass
                return True

            win32gui.EnumWindows(_cb, titles)
        except Exception:
            return False

    for title in titles.values():
        t = str(title or "").strip()
        if not t:
            continue
        if t == "WTViewerEfree":
            return True
        # 排除「数值详细设置」等子窗
        if "WTViewer" in t and "数值" not in t:
            return True
    return False
