# -*- coding: utf-8 -*-
"""WTViewerEfree（宏 Soft Panel）是否在跑：空闲时也要能上报网页「已连接」。

宏模式不建 wt3000_controller SCPI 会话，旧逻辑只看 controller.connected，
导致 Soft Panel 已连、试验未跑时网页仍灰。

开跑录波时主窗可能短暂不可见 / 被子弹盖住，仅靠 IsWindowVisible 会抖成「未连接」
并经心跳清掉网页已连；因此：存在标题即算在，并做短时 sticky latch。
"""
from __future__ import annotations

import time
from typing import Callable, Optional

# Soft Panel 枚举偶发漏检时，短时仍报已连（断开时必须 clear_wtviewer_alive_latch）
_LATCH_SEC = 120.0
_last_alive_mono: float = 0.0


def clear_wtviewer_alive_latch() -> None:
    """用户点断开 / Soft Panel 确认退出时清掉 sticky。"""
    global _last_alive_mono
    _last_alive_mono = 0.0


def _title_looks_like_wtviewer(title: str) -> bool:
    t = str(title or "").strip()
    if not t:
        return False
    if t == "WTViewerEfree":
        return True
    # 排除「数值详细设置」等子窗
    if "WTViewer" in t and "数值" not in t:
        return True
    return False


def wtviewer_window_alive(
    *,
    enum_windows: Optional[Callable[[], dict]] = None,
    now_mono: Optional[float] = None,
    latch_sec: Optional[float] = None,
) -> bool:
    """主窗口标题含 WTViewerEfree / WTViewer 即视为 Soft Panel 会话在。"""
    global _last_alive_mono
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
                    # 开跑时主窗可能被遮挡/最小化：只要窗口还在就认
                    if not win32gui.IsWindow(hwnd):
                        return True
                    text = win32gui.GetWindowText(hwnd) or ""
                    if text:
                        out[hwnd] = text
                except Exception:
                    pass
                return True

            win32gui.EnumWindows(_cb, titles)
        except Exception:
            titles = {}

    found = any(_title_looks_like_wtviewer(t) for t in titles.values())
    ts = float(now_mono if now_mono is not None else time.monotonic())
    hold = float(_LATCH_SEC if latch_sec is None else latch_sec)
    if found:
        _last_alive_mono = ts
        return True
    if _last_alive_mono > 0 and hold > 0 and (ts - _last_alive_mono) < hold:
        return True
    return False
