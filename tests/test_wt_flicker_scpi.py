# -*- coding: utf-8 -*-
from utils.wt_flicker_scpi import (
    REMOTE_ON_CMDS,
    ensure_remote,
    is_status_error,
    query_remote_on,
    should_hard_fail_flicker_cmd,
    verify_after_flicker_start,
    write_flicker_command,
)


def test_is_status_error():
    assert not is_status_error('0,"No error"')
    assert not is_status_error('+0,"No error"')
    assert is_status_error('-113,"Undefined header"')
    assert not is_status_error(
        "STATus:ERRor? 失败: VI_ERROR_TMO (-1073807339): Timeout expired"
    )
    assert not is_status_error("STATus:ERRor? 超时（仪器忙，可忽略）: VI_ERROR_TMO")
    # 远程锁定提示不是命令失败
    assert not is_status_error(
        '85,"In remote control mode, all keys are locked except LOCAL(UTILITY) key"'
    )


def test_should_hard_fail():
    assert should_hard_fail_flicker_cmd("FLICKER:RESET")
    assert should_hard_fail_flicker_cmd("FLICKER:START")
    assert not should_hard_fail_flicker_cmd(":RATE 100ms")


def test_write_fails_when_disconnected():
    ok, msg = write_flicker_command("FLICKER:RESET", ctrl=None, check_error=False)
    assert not ok
    assert "未连接" in msg


def test_ensure_remote_fails_when_disconnected():
    ok, msg = ensure_remote(ctrl=None)
    assert not ok
    assert "未连接" in msg


def test_remote_on_cmds():
    assert any("REMote ON" in c for c in REMOTE_ON_CMDS)


class _TimeoutHandle:
    def write(self, cmd):
        self.last = cmd

    def query(self, cmd):
        raise RuntimeError("VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.")


class _TimeoutCtrl:
    connected = True
    handle = _TimeoutHandle()


def test_start_timeout_on_status_error_is_ok():
    ok, msg = write_flicker_command(
        "FLICKER:START",
        ctrl=_TimeoutCtrl(),
        check_error=True,
        ensure_remote_first=False,
    )
    assert ok is True
    assert "已写" in msg


def test_verify_after_start_tolerates_timeout():
    ok, msg = verify_after_flicker_start(ctrl=_TimeoutCtrl())
    # REMOTE? 也超时 → on=None，仍可继续
    assert ok is True


def test_real_status_error_still_fails():
    class _ErrHandle:
        def write(self, cmd):
            pass

        def query(self, cmd):
            return '-113,"Undefined header"'

    class _ErrCtrl:
        connected = True
        handle = _ErrHandle()

    ok, msg = write_flicker_command(
        "FLICKER:START",
        ctrl=_ErrCtrl(),
        check_error=True,
        ensure_remote_first=False,
    )
    assert ok is False
    assert "报错" in msg


def test_ensure_remote_confirms_on():
    writes = []

    class _H:
        def write(self, cmd):
            writes.append(cmd)

        def query(self, cmd):
            if "REMote?" in cmd or "REMOTE?" in cmd.upper():
                return "1"
            raise RuntimeError("unexpected")

    class _C:
        connected = True
        handle = _H()

    ok, msg = ensure_remote(ctrl=_C(), retries=1)
    assert ok is True
    assert "确认" in msg or "ON" in msg.upper()
    assert any("REMote" in w for w in writes)


def test_ensure_remote_fails_when_stays_off():
    class _H:
        def write(self, cmd):
            pass

        def query(self, cmd):
            return "0"

    class _C:
        connected = True
        handle = _H()

    ok, msg = ensure_remote(ctrl=_C(), retries=2)
    assert ok is False
    assert "Network" in msg or "REMOTE" in msg


def test_start_requires_remote_on():
    class _H:
        def write(self, cmd):
            pass

        def query(self, cmd):
            if "REMote?" in cmd:
                return "0"
            return '0,"No error"'

    class _C:
        connected = True
        handle = _H()

    ok, msg = write_flicker_command(
        "FLICKER:START",
        ctrl=_C(),
        check_error=False,
        ensure_remote_first=True,
        require_remote_on=True,
    )
    assert ok is False
    assert "Network" in msg or "REMOTE" in msg


def test_query_remote_on_parses():
    class _H:
        def query(self, cmd):
            return "ON"

    class _C:
        connected = True
        handle = _H()

    on, raw = query_remote_on(ctrl=_C())
    assert on is True
    assert raw == "ON"
