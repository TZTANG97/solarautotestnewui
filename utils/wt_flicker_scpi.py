# -*- coding: utf-8 -*-
"""闪变试验 WT SCPI 写命令校验。

WT3000E 在 FLICKER:INITIALIZE / START 后会短暂忙，STATus:ERRor? 常超时（VI_ERROR_TMO）。
超时 ≠ 仪器报错：不得把查询超时当成硬失败而中止试验。
"""
from __future__ import annotations

import time
from typing import Any, Optional, Tuple

# 闪变序列开头必须进远程，否则面板停在 Flicker:Reset、REMOTE 灯不亮、START 无效
REMOTE_ON_CMDS = (
    ":COMMunicate:REMote ON",
    "COMMunicate:REMote ON",
)


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


def ensure_remote(ctrl=None) -> Tuple[bool, str]:
    """强制进入远程模式（点亮 REMOTE）。以太网/串口尤其需要，否则闪变 START 常无反应。"""
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，无法切换 REMOTE"
    handle = c.handle
    last_exc: Optional[BaseException] = None
    for cmd in REMOTE_ON_CMDS:
        try:
            handle.write(cmd)
            time.sleep(0.15)
            return True, f"已切换远程模式（{cmd}）"
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    return False, f"切换远程模式失败: {last_exc}"


def _is_query_timeout(exc: BaseException) -> bool:
    s = str(exc or "")
    u = s.upper()
    return (
        "VI_ERROR_TMO" in u
        or "TIMEOUT" in u
        or "-1073807339" in s
        or "TIMED OUT" in u
    )


def _query_status_error(handle) -> Tuple[str, bool]:
    """读错误队列首条。

    返回 (reply, query_ok)：
    - query_ok=True：拿到合法回复（可能是 No error 或真实错误码）
    - query_ok=False：查询失败/超时，reply 为说明（不得当仪器报错）
    """
    last_exc: Optional[BaseException] = None
    for cmd in ("STATus:ERRor?", ":STATus:ERRor?"):
        try:
            raw = handle.query(cmd)
            return str(raw or "").strip(), True
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if _is_query_timeout(exc):
                return f"STATus:ERRor? 超时（仪器忙，可忽略）: {exc}", False
    return f"STATus:ERRor? 失败: {last_exc}", False


def is_status_error(reply: str) -> bool:
    s = (reply or "").strip()
    if not s:
        return False
    # 查询失败文案不是错误队列内容
    if "失败" in s or "超时" in s or "VI_ERROR_TMO" in s.upper():
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
    ensure_remote_first: bool = False,
) -> Tuple[bool, str]:
    """写一条闪变相关 SCPI。失败返回 (False, message)。"""
    cmd = str(command or "").strip()
    if not cmd:
        return False, "空命令"
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，无法下发闪变命令（请先在仪器面板连接功率分析仪）"
    if ensure_remote_first:
        ok_r, msg_r = ensure_remote(c)
        if not ok_r:
            return False, msg_r
    handle = c.handle
    try:
        handle.write(cmd)
    except Exception as exc:
        return False, f"写失败 {cmd}: {exc}"

    if not check_error:
        return True, f"已写 {cmd}"

    # START/INITIALIZE 后仪器常忙：短等再查；查不到（超时）不当失败
    cmd_u = cmd.upper().replace(" ", "")
    if cmd_u.startswith("FLICKER:START") or cmd_u.startswith("FLICKER:INITIALIZE"):
        time.sleep(0.8)

    err, query_ok = _query_status_error(handle)
    if not query_ok:
        return True, f"已写 {cmd}（错误队列暂不可读：{err}）"
    if is_status_error(err):
        return False, f"{cmd} 后仪器报错: {err}"
    return True, f"已写 {cmd}"


def verify_after_flicker_start(ctrl=None) -> Tuple[bool, str]:
    """FLICKER:START 后再确认一次错误队列。

    查询超时视为通过（WT3000E 进入测量后忙），只有明确错误码才失败。
    """
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，FLICKER:START 无法确认"
    time.sleep(0.5)
    err, query_ok = _query_status_error(c.handle)
    if not query_ok:
        return True, f"FLICKER:START 已下发（错误队列暂不可读，继续试验）: {err}"
    if is_status_error(err):
        return False, f"FLICKER:START 后仪器报错: {err}"
    return True, "FLICKER:START 已下发且无错误"


def should_hard_fail_flicker_cmd(command: str) -> bool:
    """关键闪变命令失败时应中止试验，避免空等 10h+。"""
    u = str(command or "").strip().upper()
    if not u.startswith("FLICKER:"):
        return False
    return True
