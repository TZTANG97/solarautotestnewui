# -*- coding: utf-8 -*-
from utils.wt_flicker_scpi import (
    is_status_error,
    should_hard_fail_flicker_cmd,
    write_flicker_command,
)


def test_is_status_error():
    assert not is_status_error('0,"No error"')
    assert not is_status_error('+0,"No error"')
    assert is_status_error('-113,"Undefined header"')


def test_should_hard_fail():
    assert should_hard_fail_flicker_cmd("FLICKER:RESET")
    assert should_hard_fail_flicker_cmd("FLICKER:START")
    assert not should_hard_fail_flicker_cmd(":RATE 100ms")


def test_write_fails_when_disconnected():
    ok, msg = write_flicker_command("FLICKER:RESET", ctrl=None, check_error=False)
    assert not ok
    assert "未连接" in msg
