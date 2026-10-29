# -*- coding: utf-8 -*-
"""闪变试验 WT SCPI：REMOTE 确认 + 写命令校验。

WT3004E/WT3000E 要点：
- 面板 MISC → Remote Ctrl → Device 必须选 Network，否则以太网命令不生效、REMOTE 灯不亮
- FLICKER:START 前必须 REMOTE ON；灯灭时面板会一直停在 Flicker:Reset
- START/INITIALIZE 后 STATus:ERRor? 常超时，超时不当硬失败
"""
from __future__ import annotations

import time
from typing import Any, Optional, Tuple

REMOTE_ON_CMDS = (
    ":COMMunicate:REMote ON",
    ":COMMunicate:REMote 1",
    "COMMunicate:REMote ON",
)
REMOTE_LOCK_CMDS = (
    ":COMMunicate:LOCKout ON",
    ":COMMunicate:LOCKout 1",
)
REMOTE_QUERY_CMDS = (
    ":COMMunicate:REMote?",
    "COMMunicate:REMote?",
)

REMOTE_PANEL_HINT = (
    "无法点亮 REMOTE。请在 WT 面板：MISC → Remote Ctrl（远程控制）→ Device 选 Network，"
    "然后软件断开功率分析仪再重连，确认 REMOTE 灯亮后再开闪变。"
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


def _remote_state_token(reply: str) -> Optional[str]:
    """从 REMote? 原文抽出状态 token：'1'/'0'/'ON'/'OFF'；无法识别返回 None。

    横河示例：``1`` / ``ON`` / ``:COMM:REM 1`` / ``:COMMunicate:REMote ON``
    """
    s = (reply or "").strip().upper().replace('"', "")
    if not s:
        return None
    # 先取逗号前一段
    head = s.split(",", 1)[0].strip()
    # 去掉常见头：:COMM:REM / :COMMUNICATE:REMOTE
    for prefix in (
        ":COMMUNICATE:REMOTE",
        "COMMUNICATE:REMOTE",
        ":COMM:REM",
        "COMM:REM",
        ":REMOTE",
        "REMOTE",
    ):
        if head.startswith(prefix):
            head = head[len(prefix) :].lstrip(" :=")
            break
    token = head.split()[-1].strip().lstrip("+") if head.split() else head.strip().lstrip("+")
    if token in ("1", "ON", "TRUE"):
        return "1"
    if token in ("0", "OFF", "FALSE"):
        return "0"
    try:
        n = int(token)
        if n == 1:
            return "1"
        if n == 0:
            return "0"
    except ValueError:
        pass
    return None


def _remote_reply_is_on(reply: str) -> bool:
    return _remote_state_token(reply) == "1"


def _remote_reply_is_off(reply: str) -> bool:
    return _remote_state_token(reply) == "0"


def query_remote_on(ctrl=None) -> Tuple[Optional[bool], str]:
    """查询 REMOTE 是否 ON。返回 (True/False/None, 原文)。None=查不到。"""
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return None, "WT 未连接"
    handle = c.handle
    last = ""
    for q in REMOTE_QUERY_CMDS:
        try:
            raw = str(handle.query(q) or "").strip()
            last = raw
            if _remote_reply_is_on(raw):
                return True, raw
            if _remote_reply_is_off(raw):
                return False, raw
            # 未知格式：不当 OFF，交给上层软通过
            return None, raw
        except Exception as exc:  # noqa: BLE001
            last = str(exc)
            if _is_query_timeout(exc):
                continue
    return None, last


def ensure_remote(ctrl=None, *, lockout: bool = True, retries: int = 3) -> Tuple[bool, str]:
    """强制进入远程模式并尽量确认 REMOTE 灯（查询 ON）。"""
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，无法切换 REMOTE"
    handle = c.handle
    last_write_exc: Optional[BaseException] = None
    last_query = ""

    for attempt in range(max(1, int(retries))):
        wrote = False
        for cmd in REMOTE_ON_CMDS:
            try:
                handle.write(cmd)
                wrote = True
                time.sleep(0.25)
                break
            except Exception as exc:  # noqa: BLE001
                last_write_exc = exc
        if not wrote:
            continue

        if lockout:
            for cmd in REMOTE_LOCK_CMDS:
                try:
                    handle.write(cmd)
                    time.sleep(0.1)
                    break
                except Exception:
                    pass

        on, raw = query_remote_on(c)
        last_query = raw
        # REMOTE/LOCK 后常留下 85 提示，先读走，避免 INITIALIZE 被误杀
        try:
            drain_status_errors(handle)
        except Exception:
            pass
        if on is True:
            return True, f"REMOTE 已确认 ON（{raw}，第{attempt + 1}次）"
        if on is False:
            # 明确 OFF：再试
            time.sleep(0.35)
            continue
        # 查不到：写成功也先当软通过，但带警告（部分固件无 REMote?）
        time.sleep(0.2)
        return True, (
            f"已写 REMOTE ON（未能查询确认：{raw}）。"
            f"请目视面板 REMOTE 灯是否亮；若不亮则 {REMOTE_PANEL_HINT}"
        )

    if last_write_exc is not None:
        return False, f"切换远程模式写失败: {last_write_exc}"
    return False, f"{REMOTE_PANEL_HINT}（查询={last_query or '无'}）"


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
    """读错误队列首条。query_ok=False 表示超时/读失败，不当仪器报错。"""
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


# 横河在 REMOTE/LOCK 后常见提示，不是命令失败
_BENIGN_STATUS_CODES = frozenset(
    {
        85,  # In remote control mode, all keys are locked except LOCAL...
    }
)


def _status_code(reply: str) -> Optional[int]:
    s = (reply or "").strip()
    if not s:
        return None
    head = s.split(",", 1)[0].strip().lstrip("+")
    try:
        return int(head)
    except ValueError:
        return None


def is_benign_status_error(reply: str) -> bool:
    code = _status_code(reply)
    if code in _BENIGN_STATUS_CODES:
        return True
    low = (reply or "").lower()
    return "in remote control mode" in low and "locked" in low


def is_status_error(reply: str) -> bool:
    s = (reply or "").strip()
    if not s:
        return False
    if "失败" in s or "超时" in s or "VI_ERROR_TMO" in s.upper():
        return False
    if is_benign_status_error(s):
        return False
    code = _status_code(s)
    if code is not None:
        return code != 0
    return "no error" not in s.lower()


def drain_status_errors(handle, *, max_n: int = 8) -> list:
    """读走错误队列直到 No error（含 85 提示），避免下一条命令被旧消息误杀。"""
    drained = []
    for _ in range(max(1, int(max_n))):
        err, ok = _query_status_error(handle)
        if not ok:
            break
        code = _status_code(err)
        if code == 0 or (err and "no error" in err.lower()):
            break
        if err:
            drained.append(err)
    return drained


def is_init_not_finished_error(reply: str) -> bool:
    """错误 821：初始化未完成就 START（WT5000/WT3000E 常见）。"""
    code = _status_code(reply)
    if code == 821:
        return True
    low = (reply or "").lower()
    return (
        "initialization is not finished" in low
        or "初始化未完成" in low
        or "flicker initialization" in low
    )


def write_flicker_command(
    command: str,
    *,
    ctrl=None,
    check_error: bool = True,
    ensure_remote_first: bool = False,
    require_remote_on: bool = False,
) -> Tuple[bool, str]:
    """写一条闪变相关 SCPI。失败返回 (False, message)。"""
    cmd = str(command or "").strip()
    if not cmd:
        return False, "空命令"
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，无法下发闪变命令（请先在仪器面板连接功率分析仪）"
    if ensure_remote_first:
        ok_r, msg_r = ensure_remote(c, lockout=True)
        if not ok_r:
            return False, msg_r
        if require_remote_on:
            on, raw = query_remote_on(c)
            if on is False:
                return False, f"{REMOTE_PANEL_HINT}（当前 REMote?={raw}）"
    handle = c.handle
    try:
        handle.write(cmd)
    except Exception as exc:
        return False, f"写失败 {cmd}: {exc}"

    if not check_error:
        return True, f"已写 {cmd}"

    cmd_u = cmd.upper().replace(" ", "")
    if cmd_u.startswith("FLICKER:START") or cmd_u.startswith("FLICKER:INITIALIZE"):
        time.sleep(0.8)

    err, query_ok = _query_status_error(handle)
    if not query_ok:
        return True, f"已写 {cmd}（错误队列暂不可读：{err}）"
    if is_benign_status_error(err):
        try:
            drain_status_errors(handle)
        except Exception:
            pass
        return True, f"已写 {cmd}（忽略提示: {err}）"
    if is_status_error(err):
        return False, f"{cmd} 后仪器报错: {err}"
    return True, f"已写 {cmd}"


def write_flicker_start(
    ctrl=None,
    *,
    retries: int = 8,
    retry_wait_sec: float = 5.0,
) -> Tuple[bool, str]:
    """FLICKER:START：若 821（初始化未完成）则等待重试，对齐旧版长时间等 INITIALIZE 的行为。"""
    c = ctrl if ctrl is not None else get_wt_controller()
    notes: list = []
    attempts = max(1, int(retries))
    wait_s = max(1.0, float(retry_wait_sec))
    for i in range(attempts):
        ok, msg = write_flicker_command(
            "FLICKER:START",
            ctrl=c,
            check_error=True,
            ensure_remote_first=True,
            require_remote_on=True,
        )
        if ok:
            if notes:
                return True, f"{msg}（曾遇初始化未完成，已重试 {i} 次）"
            return True, msg
        if is_init_not_finished_error(msg) or "821" in msg:
            try:
                if wt_connected(c):
                    drain_status_errors(c.handle)
            except Exception:
                pass
            notes.append(msg)
            if i + 1 >= attempts:
                break
            time.sleep(wait_s)
            continue
        return False, msg
    detail = notes[-1] if notes else "未知"
    return False, f"FLICKER:START 仍失败（初始化未完成，已重试 {attempts} 次）: {detail}"


def verify_after_flicker_start(ctrl=None) -> Tuple[bool, str]:
    """START 后确认：优先查 REMOTE 仍亮；STATUS 超时不当失败；821 不当最终成功。"""
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，FLICKER:START 无法确认"
    time.sleep(0.5)
    on, raw = query_remote_on(c)
    if on is False:
        return False, f"FLICKER:START 后 REMOTE 仍为 OFF（{raw}）。{REMOTE_PANEL_HINT}"
    err, query_ok = _query_status_error(c.handle)
    if not query_ok:
        rem = f"REMOTE={raw}" if raw else "REMOTE 未查询到"
        return True, f"FLICKER:START 已下发（{rem}；错误队列暂不可读，请看面板是否离开 Reset）"
    if is_init_not_finished_error(err):
        return False, f"FLICKER:START 后仪器报错: {err}"
    if is_benign_status_error(err):
        return True, f"FLICKER:START 已下发（忽略提示: {err}）"
    if is_status_error(err):
        return False, f"FLICKER:START 后仪器报错: {err}"
    rem = f"REMOTE ON（{raw}）" if on is True else "REMOTE 未确认"
    return True, f"FLICKER:START 已下发且无错误（{rem}）"


def should_hard_fail_flicker_cmd(command: str) -> bool:
    u = str(command or "").strip().upper()
    if not u.startswith("FLICKER:"):
        return False
    return True


def _parse_count_reply(raw: str) -> Optional[int]:
    """从 FLICKER:COUNT? 原文抽出整数。"""
    s = (raw or "").strip().replace('"', "")
    if not s:
        return None
    # 常见：12 / +12 / :FLIC:COUN 12
    head = s.split(",", 1)[0].strip()
    for prefix in (
        ":FLICKER:COUNT",
        "FLICKER:COUNT",
        ":FLIC:COUN",
        "FLIC:COUN",
        ":COUNT",
        "COUNT",
    ):
        if head.upper().startswith(prefix):
            head = head[len(prefix) :].lstrip(" :=")
            break
    token = head.split()[-1].strip().lstrip("+") if head.split() else head.strip().lstrip("+")
    try:
        return int(float(token))
    except (TypeError, ValueError):
        return None


def query_flicker_count(ctrl=None) -> Tuple[Optional[int], str]:
    """查询 Pst 观测组数。返回 (n/None, 原文)。"""
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return None, "WT 未连接"
    handle = c.handle
    last = ""
    for q in ("FLICKER:COUNT?", ":FLICker:COUNt?", "FLICker:COUNt?"):
        try:
            raw = str(handle.query(q) or "").strip()
            last = raw
            n = _parse_count_reply(raw)
            if n is not None:
                return n, raw
        except Exception as exc:  # noqa: BLE001
            last = str(exc)
            if _is_query_timeout(exc):
                continue
    return None, last


def ensure_flicker_count(expected: int, ctrl=None, *, retries: int = 2) -> Tuple[bool, str]:
    """写入并回读 FLICKER:COUNT，确认 Pst 组数（WT5000 上 INITIALIZE 后偶发掉回 1）。"""
    exp = int(expected)
    if exp < 1:
        return False, f"无效 FLICKER:COUNT={exp}"
    c = ctrl if ctrl is not None else get_wt_controller()
    if not wt_connected(c):
        return False, "WT 未连接，无法设置 FLICKER:COUNT"
    last = ""
    for attempt in range(max(1, int(retries))):
        ok, msg = write_flicker_command(
            f"FLICKER:COUNT {exp}",
            ctrl=c,
            check_error=False,
            ensure_remote_first=False,
        )
        last = msg
        if not ok:
            continue
        time.sleep(0.2)
        n, raw = query_flicker_count(c)
        if n == exp:
            return True, f"FLICKER:COUNT={exp} 已确认（{raw}，第{attempt + 1}次）"
        last = f"写后回读={n!r}（原文={raw}），期望 {exp}"
        time.sleep(0.25)
    return False, f"FLICKER:COUNT 未能确认成 {exp}：{last}"
