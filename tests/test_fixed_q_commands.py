# -*- coding: utf-8 -*-
"""定无功：P×Q 命令构建（无 UI）。"""

from utils.fixed_q_commands import (
    default_dc_iv_resolver,
    format_setpoint_tag,
    parse_ladder,
)


def test_parse_ladder_signed():
    assert parse_ladder("-100, -50,0, 50，100") == [-100.0, -50.0, 0.0, 50.0, 100.0]
    assert parse_ladder("10% 20%") == [10.0, 20.0]
    assert parse_ladder("") == []


def test_format_setpoint_tag():
    assert format_setpoint_tag(-50) == "m50"
    assert format_setpoint_tag(12.5) == "12p5"
    assert format_setpoint_tag(100) == "100"


def test_default_dc_iv_resolver_ok():
    code, cmds = default_dc_iv_resolver("400", "10", "450", "12", "50", 0)
    assert code == "ok"
    assert cmds[0] == "OUTP:MODE TABLE"
