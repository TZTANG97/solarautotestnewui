# -*- coding: utf-8 -*-
"""动态 Cosφ(P) 命令构建单元测试（无 UI）。"""

from utils.dynamic_cosphi_commands import (
    DEFAULT_FILE_NAME,
    default_dc_iv_resolver,
    parse_power_ladder,
)


def test_parse_power_ladder_comma_and_space():
    assert parse_power_ladder("20,40, 60，80") == [20.0, 40.0, 60.0, 80.0]
    assert parse_power_ladder("20% 40%") == [20.0, 40.0]
    assert parse_power_ladder("") == []
    assert parse_power_ladder("# comment\n50") == [50.0]


def test_default_dc_iv_resolver_chroma_chain():
    code, cmds = default_dc_iv_resolver("400", "10", "450", "12", "50", 0)
    assert code == "ok"
    assert cmds[0] == "OUTP:MODE TABLE"
    assert "IVC:IT" in cmds[1]
    assert "IVC:VT" in cmds[2]
    assert cmds[3] == "IVCurve:SELect 1"
    # 50% PF → Imp/Isc 减半
    assert "5.000" in cmds[1]
    assert "6.000" in cmds[1]


def test_default_dc_iv_resolver_errors():
    assert default_dc_iv_resolver("400", "12", "450", "10", "100", 0)[0] == "err1"
    assert default_dc_iv_resolver("400", "10", "450", "2000", "100", 0)[0] == "err2"


def test_default_file_name():
    assert DEFAULT_FILE_NAME == "CosPhiP_curve"
