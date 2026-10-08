# -*- coding: utf-8 -*-
"""闪变试验 WT SCPI 写命令校验：连接检查 + STATus:ERRor，避免静默失败后空等数小时。"""
from __future__ import annotations

from typing import Any, Optional, Tuple


def get_wt_controller():
    try:
        from utils.wt_scpi_session import _get_controller

        return _get_controller()
    except Exception:
        return None


def wt_connected(ctrl=None) -> bool:
    c = ctrl if ctrl is not None else get_wt_controller()
    if c is None:
        return False
    if not getattr(c, "connected", False):
        return False
    return getattr(c, "handle", None) is not None


def _query_status_error(handle) -> str:
    """读走错误队列首条；无错返回空串。"""
    try:
        raw = handle.query("STATus:ERRor?")
    except Exception:
        try:
            raw = handle.query(":STATus:ERRor?")
        except Exception as exc:
            return f"STATus:ERRor? 失败: {exc}"
    return str(raw or "").strip()


def is_status_error(reply: str) -> bool:
    s = (reply or "").strip()
    if not s:
        return False
    # 常见：0,"No error" 或 +0,"No error"
    head = s.split(",", 1)[0].strip().lstrip("+")
    try:
        return int(head) != 0
    except ValueError:
        return "no error" not in s.lower()


def write_flicker_command(
    command: str,
    *,
    ctrl=None,
    check_error: bool = True,
) -> Tuple[bool, str]:
    """写一条闪变相关 SCPI。失败返回 (False, message)。"""
    cmd = str(command or "").strip()
    if not cmd:
        return False, "空命令"
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，无法下发闪变命令（请先在仪器面板连接功率分析仪）"
    handle = c.handle
    try:
        handle.write(cmd)
    except Exception as exc:
        return False, f"写失败 {cmd}: {exc}"

    if not check_error:
        return True, f"已写 {cmd}"

    # DISPLAY / ELEMENT 等可能无错误队列；仍尝试读，避免残留错误遮住后续 START
    err = _query_status_error(handle)
    if is_status_error(err):
        return False, f"{cmd} 后仪器报错: {err}"
    return True, f"已写 {cmd}"


def verify_after_flicker_start(ctrl=None) -> Tuple[bool, str]:
    """FLICKER:START 后再确认一次错误队列。"""
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，FLICKER:START 无法确认"
    err = _query_status_error(c.handle)
    if is_status_error(err):
        return False, f"FLICKER:START 后仪器报错: {err}"
    return True, "FLICKER:START 已下发且无错误"


def should_hard_fail_flicker_cmd(command: str) -> bool:
    """关键闪变命令失败时应中止试验，避免空等 10h+。"""
    u = str(command or "").strip().upper()
    if not u.startswith("FLICKER:"):
        return False
    # 显示/ELEMENT 失败也尽量中止，否则面板无倒计时却继续跑
    return True
