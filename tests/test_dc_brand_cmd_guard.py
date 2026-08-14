# -*- coding: utf-8 -*-
"""DC 品牌命令拦截（生成阶段）。"""
from __future__ import annotations

import pytest

from utils.dc_brand_cmd_guard import (
    resolve_dc_iv_with_bridge,
    validate_dc_cmds_for_brand,
)


@pytest.mark.parametrize(
    "factor,cmds,ok",
    [
        ("Bluesight", ["BLUESIGHT:STC 8 650 0.8"], True),
        ("Bluesight", ["OUTP:MODE TABLE", "IVC:IT 1,2"], False),
        ("Bluesight", ["SAS:MODE TABL", "SAS:TABL1:CURR 1,2"], False),
        ("Bluesight", ["SOL 0", "SOL:USER:VOC 450"], False),
        ("Itech", ["SOL:USER:VOC 450", "SOL:USER:VMP 400"], True),
        ("Itech", ["IVC:IT 1,2", "IVC:VT 1,2"], False),
        ("Itech", ["SAS:TABL1:CURR 1,2"], False),
        ("Itech", ["BLUESIGHT:STC 1 2 0.8"], False),
        ("Chroma", ["OUTP:MODE TABLE", "IVC:IT 1,2"], True),
        ("Chroma", ["SAS:MODE TABL", "SAS:TABL1:CURR 1,2"], False),
        ("Chroma", ["SOL:USER:VOC 450"], False),
        ("Chroma", ["BLUESIGHT:STC 1 2 0.8"], False),
        ("Keysight", ["SAS:MODE TABL", "SAS:TABL1:CURR 1,2"], True),
        ("Keysight", ["OUTP:MODE TABLE", "IVC:IT 1,2"], False),
        ("Keysight", ["SOL:USER:VOC 450"], False),
        ("Keysight", ["BLUESIGHT:STC 1 2 0.8"], False),
        ("keysight", ["SAS:TABL1:VOLT 1,2"], True),
        ("Chroma", ["OUTP OFF"], True),
        ("", ["IVC:IT 1,2"], False),  # 未识别禁止 IVC
        ("", ["BLUESIGHT:STC 1 2 0.8"], False),
        ("", ["OUTP OFF"], False),
        ("Unknown", ["OUTP OFF"], False),
    ],
)
def test_validate_dc_cmds_for_brand(factor, cmds, ok):
    passed, msg = validate_dc_cmds_for_brand(factor, cmds)
    assert passed is ok
    if not ok:
        assert msg


def test_bridge_blocks_chroma_when_bluesight_factor():
    def fake_get_iv(*_a):
        return ["IVC:IT 1,2", "IVC:VT 3,4"]

    code, cmds = resolve_dc_iv_with_bridge(
        "400",
        "10",
        "450",
        "12",
        "100",
        0,
        get_iv_fn=fake_get_iv,
        per_dc_factor={"0": "Bluesight"},
        command_list_dc={"Bluesight": [], "Chroma": ["OUTP:MODE TABLE", "IVCurve:SELect 1"]},
    )
    assert code == "err_brand"
    assert cmds is None


def test_bridge_itech_wraps_sol_prefix():
    def fake_get_iv(*_a):
        return [
            "SOL:USER:VOC 450",
            "SOL:USER:IMP 10",
            "SOL:USER:VMP 400",
            "SOL:USER:ISC 12",
        ]

    code, cmds = resolve_dc_iv_with_bridge(
        "400",
        "10",
        "450",
        "12",
        "100",
        0,
        get_iv_fn=fake_get_iv,
        per_dc_factor={"0": "Itech"},
        command_list_dc={"Itech": ["SOL 0", "SOL 1"]},
    )
    assert code == "ok"
    assert cmds is not None
    assert any(c.startswith("SOL:USER") for c in cmds)


@pytest.mark.parametrize(
    "factor,iv_cmds,mode_cmds,required",
    [
        (
            "Chroma",
            ["IVC:IT 1,2", "IVC:VT 3,4"],
            ["OUTP:MODE TABLE", "IVCurve:SELect 1"],
            {"OUTP:MODE TABLE", "IVCurve:SELect 1"},
        ),
        (
            "Keysight",
            ["SAS:TABL1:CURR 1,2", "SAS:TABL1:VOLT 3,4"],
            ["SAS:MODE TABL", "SAS:TABL:ACT 1"],
            {"SAS:MODE TABL", "SAS:TABL:ACT 1"},
        ),
        (
            "Bluesight",
            ["BLUESIGHT:STC 8 650 0.8"],
            [],
            {"BLUESIGHT:STC 8 650 0.8"},
        ),
    ],
)
def test_bridge_preserves_each_brand_path(factor, iv_cmds, mode_cmds, required):
    code, cmds = resolve_dc_iv_with_bridge(
        "400",
        "10",
        "450",
        "12",
        "100",
        0,
        get_iv_fn=lambda *_a: list(iv_cmds),
        per_dc_factor={"0": factor},
        command_list_dc={factor: list(mode_cmds)},
    )

    assert code == "ok"
    assert cmds is not None
    assert required.issubset(set(cmds))


def test_bridge_unknown_brand_fails_closed_even_for_generic_command():
    code, cmds = resolve_dc_iv_with_bridge(
        "400",
        "10",
        "450",
        "12",
        "100",
        0,
        get_iv_fn=lambda *_a: ["OUTP OFF"],
        per_dc_factor={"0": ""},
        command_list_dc={},
    )

    assert code == "err_brand"
    assert cmds is None
