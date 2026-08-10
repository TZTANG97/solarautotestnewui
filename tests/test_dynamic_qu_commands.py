# -*- coding: utf-8 -*-
from utils.dynamic_qu_commands import (
    DEFAULT_FILE_NAME,
    default_dc_iv_resolver,
    parse_voltage_ladder,
)


def test_parse_voltage_ladder():
    assert parse_voltage_ladder("100,103, 105") == [100.0, 103.0, 105.0]
    assert parse_voltage_ladder("100% 85%") == [100.0, 85.0]
    assert parse_voltage_ladder("") == []


def test_default_dc_iv_and_filename():
    code, cmds = default_dc_iv_resolver("400", "10", "450", "12", "100", 0)
    assert code == "ok"
    assert cmds[0] == "OUTP:MODE TABLE"
    assert cmds[-1] == "IVCurve:SELect 1"
    assert DEFAULT_FILE_NAME == "QU_dyn_curve"
