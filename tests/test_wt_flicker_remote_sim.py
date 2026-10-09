# -*- coding: utf-8 -*-
"""模拟 WT3000E / WT5000 闪变 REMOTE→START 全流程。"""
from __future__ import annotations

import pytest

from utils.wt_flicker_scpi import (
    _remote_reply_is_off,
    _remote_reply_is_on,
    ensure_remote,
    verify_after_flicker_start,
    write_flicker_command,
)


@pytest.mark.parametrize(
    "reply,expect_on",
    [
        ("1", True),
        ("ON", True),
        (":COMM:REM 1", True),
        (":COMM:REM 1\n", True),
        (":COMMunicate:REMote ON", True),
        ("COMM:REM 1", True),
        ("0", False),
        ("OFF", False),
        (":COMM:REM 0", False),
        (":COMMunicate:REMote OFF", False),
    ],
)
def test_parse_yokogawa_remote_replies(reply, expect_on):
    assert _remote_reply_is_on(reply) is expect_on
    assert _remote_reply_is_off(reply) is (not expect_on)


class _SimHandle:
    """模拟横河网口：REMote? 返回带头格式；START 后 STATUS 可能超时。"""

    def __init__(self, *, remote_reply=":COMM:REM 1", status_timeout_after_start=True):
        self.remote_reply = remote_reply
        self.status_timeout_after_start = status_timeout_after_start
        self.writes = []
        self.remote = 0
        self.started = False

    def write(self, cmd: str):
        c = str(cmd or "").strip().upper().replace(" ", "")
        self.writes.append(str(cmd))
        if "COMMUNICATE:REMOTEON" in c or "COMMUNICATE:REMOTE1" in c or c.endswith(":REMOTEON"):
            self.remote = 1
        if "COMMUNICATE:REMOTEOFF" in c or "COMMUNICATE:REMOTE0" in c:
            self.remote = 0
        if c.startswith("FLICKER:START"):
            if self.remote == 1:
                self.started = True
            else:
                self.started = False

    def query(self, cmd: str):
        u = str(cmd or "").strip().upper()
        if "REMOTE?" in u.replace(" ", "") or "REM?" in u.replace(" ", ""):
            # 按仪器当前态拼带头回复（对齐现场日志）
            if self.remote_reply is not None and ":COMM" in self.remote_reply.upper():
                return ":COMM:REM 1" if self.remote == 1 else ":COMM:REM 0"
            return "1" if self.remote == 1 else "0"
        if "STATUS:ERROR?" in u.replace(" ", "") or "STAT:ERR?" in u.replace(" ", ""):
            if self.started and self.status_timeout_after_start:
                raise RuntimeError(
                    "VI_ERROR_TMO (-1073807339): Timeout expired before operation completed."
                )
            return '0,"No error"'
        raise RuntimeError(f"unexpected query {cmd}")


class _SimCtrl:
    def __init__(self, handle: _SimHandle):
        self.connected = True
        self.handle = handle


def test_wt5000_header_reply_must_not_abort():
    """现场：查询=:COMM:REM 1 却被误判 OFF 而中止。"""
    h = _SimHandle(remote_reply=":COMM:REM 1")
    ctrl = _SimCtrl(h)
    # 先写 ON
    h.remote = 1
    ok, msg = ensure_remote(ctrl=ctrl, retries=1)
    assert ok is True, msg
    assert "确认" in msg or "ON" in msg.upper()


def test_full_flicker_start_flow_wt5000_style():
    h = _SimHandle(remote_reply=":COMM:REM 1", status_timeout_after_start=True)
    ctrl = _SimCtrl(h)

    ok_r, msg_r = ensure_remote(ctrl=ctrl, retries=2)
    assert ok_r is True, msg_r
    assert h.remote == 1

    ok_i, msg_i = write_flicker_command(
        "FLICKER:INITIALIZE",
        ctrl=ctrl,
        check_error=True,
        ensure_remote_first=True,
    )
    assert ok_i is True, msg_i

    ok_s, msg_s = write_flicker_command(
        "FLICKER:START",
        ctrl=ctrl,
        check_error=True,
        ensure_remote_first=True,
        require_remote_on=True,
    )
    assert ok_s is True, msg_s
    assert h.started is True
    assert "已写" in msg_s

    vok, vmsg = verify_after_flicker_start(ctrl=ctrl)
    assert vok is True, vmsg


def test_start_aborts_only_when_remote_truly_off():
    h = _SimHandle()
    # 强制写 REMOTE 命令也被仪器忽略（保持 0）
    class _StuckOff(_SimHandle):
        def write(self, cmd: str):
            self.writes.append(str(cmd))
            # 故意不置 remote=1
            c = str(cmd or "").strip().upper().replace(" ", "")
            if c.startswith("FLICKER:START"):
                self.started = False

    h = _StuckOff()
    ctrl = _SimCtrl(h)
    ok, msg = write_flicker_command(
        "FLICKER:START",
        ctrl=ctrl,
        check_error=False,
        ensure_remote_first=True,
        require_remote_on=True,
    )
    assert ok is False
    assert "Network" in msg or "REMOTE" in msg
    assert h.started is False


def test_wt3000_plain_one_still_ok():
    h = _SimHandle(remote_reply="1")
    # 覆写 query 走纯数字
    def _q(cmd: str):
        u = str(cmd or "").upper()
        if "REM" in u:
            return "1" if h.remote == 1 else "0"
        return '0,"No error"'

    h.query = _q  # type: ignore[method-assign]
    ctrl = _SimCtrl(h)
    ok, msg = ensure_remote(ctrl=ctrl, retries=1)
    assert ok is True, msg


def test_initialize_ignores_status_85_remote_lock_message():
    """现场：INITIALIZE 后 85 远程锁定提示被误杀试验。"""
    queue = [
        '85,"In remote control mode, all keys are locked except LOCAL(UTILITY) key"',
        '0,"No error"',
    ]

    class _H(_SimHandle):
        def query(self, cmd: str):
            u = str(cmd or "").strip().upper().replace(" ", "")
            if "REMOTE?" in u or "REM?" in u:
                return ":COMM:REM 1" if self.remote == 1 else ":COMM:REM 0"
            if "STATUS:ERROR?" in u or "STAT:ERR?" in u:
                if queue:
                    return queue.pop(0)
                return '0,"No error"'
            raise RuntimeError(cmd)

    h = _H()
    h.remote = 1
    ctrl = _SimCtrl(h)
    ok, msg = write_flicker_command(
        "FLICKER:INITIALIZE",
        ctrl=ctrl,
        check_error=True,
        ensure_remote_first=False,
    )
    assert ok is True, msg
    assert "忽略" in msg or "已写" in msg
