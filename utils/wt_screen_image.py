# -*- coding: utf-8 -*-
"""把功率分析仪当前画面读回工控机。

只发 IMAGE:EXEC 时，图留在仪器存储上；路径没配好就是空文件。
这里改问 :IMAGE:SEND?，空图不保存。
"""
from __future__ import annotations

import os
import time
from typing import Any, Optional, Tuple

from utils.screen_capture import load_usable_bytes, save_usable_image
from utils.wt_save_path import ensure_wt_save_dir

_SEND_QUERIES = (":IMAGE:SEND?", "IMAGE:SEND?")
_FORMAT_CMDS = (":IMAGE:FORMAT PNG", ":IMAGE:FORMAT BMP")


def save_wt_screen(ctrl: Any, save_path: str = "") -> Tuple[bool, str]:
    handle = getattr(ctrl, "handle", None) if ctrl is not None else None
    if handle is None:
        return False, "WT 未连接，无法截屏"
    path = (save_path or "").strip()
    if not path:
        folder = ensure_wt_save_dir()
        path = os.path.join(folder, f"wt_screen_{time.strftime('%Y%m%d_%H%M%S')}.png")
    raw, err = _read_screen_bytes(handle)
    if raw is None:
        return False, err or "没有读到画面数据"
    img, msg = load_usable_bytes(raw)
    if img is None:
        return False, msg
    return save_usable_image(img, path)


def _read_screen_bytes(handle: Any) -> Tuple[Optional[bytes], str]:
    old_timeout = getattr(handle, "timeout", None)
    try:
        if old_timeout is not None:
            handle.timeout = max(int(old_timeout or 0), 20000)
    except Exception:
        old_timeout = None
    last = "IMAGE:SEND? 无应答"
    try:
        for fmt in _FORMAT_CMDS:
            try:
                handle.write(fmt)
            except Exception:
                continue
            for query in _SEND_QUERIES:
                try:
                    raw = _query_bytes(handle, query)
                except Exception as exc:
                    last = str(exc)
                    continue
                if raw:
                    return raw, ""
                last = "IMAGE:SEND? 返回空"
        return None, last
    finally:
        if old_timeout is not None:
            try:
                handle.timeout = old_timeout
            except Exception:
                pass


def _query_bytes(handle: Any, query: str) -> bytes:
    if hasattr(handle, "query_binary_values"):
        try:
            data = handle.query_binary_values(query, datatype="B", container=bytes)
            return bytes(data or b"")
        except TypeError:
            data = handle.query_binary_values(query, datatype="B")
            return bytes(data or b"")
    if hasattr(handle, "write") and hasattr(handle, "read_raw"):
        handle.write(query)
        return bytes(handle.read_raw() or b"")
    if hasattr(handle, "query"):
        text = handle.query(query)
        if isinstance(text, bytes):
            return text
        return str(text or "").encode("latin1", errors="ignore")
    raise RuntimeError("WT 会话不能读二进制画面")
