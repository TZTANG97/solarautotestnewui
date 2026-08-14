# -*- coding: utf-8 -*-
"""Unit tests for shared timing-profile schemas and new command builders."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from utils.timing_profile import (
    DYNAMIC_MPPT_SCHEMA,
    LVRT_SCHEMA,
    PHASE_JUMP_SCHEMA,
    TimingProfileValidationError,
    profile_from_json,
    profile_to_json,
    time_to_ticks,
    validate_profile,
)
from utils.lvrt_commands import append_lvrt_profile, build_lvrt_plan
from utils.phase_jump_commands import (
    build_phase_jump_plan,
    chroma_phase_difference_commands,
    normalize_ac_brand,
)
from utils.dynamic_mppt_commands import append_dynamic_mppt_profile
from utils.safe_shutdown import build_forced_shutdown_rows


def test_time_to_ticks_units():
    assert time_to_ticks(1, "秒") == 10
    assert time_to_ticks(100, "毫秒") == 1
    assert time_to_ticks(1, "分钟") == 600


def test_lvrt_profile_roundtrip_and_no_list():
    profile = [
        {
            "enabled": True,
            "label": "dip_0.2",
            "t_pre": 1,
            "t_pre_unit": "秒",
            "t_dwell": 0.2,
            "t_dwell_unit": "秒",
            "t_post": 1,
            "t_post_unit": "秒",
            "repeats": 1,
            "u_pu": 0.2,
        }
    ]
    validate_profile(profile, LVRT_SCHEMA)
    encoded = profile_to_json(profile, LVRT_SCHEMA)
    decoded = profile_from_json(encoded, LVRT_SCHEMA)
    assert decoded[0]["u_pu"] == 0.2

    rows = []
    append_lvrt_profile(rows, profile, phase_mode="三相", nominal_voltages=(230.0, 230.0, 230.0))
    joined = " | ".join(str(r[2]) for r in rows)
    assert "LIST" not in joined.upper()
    assert any("VOLT" in str(r[2]).upper() for r in rows)


def test_phase_jump_fail_closed_for_itech():
    with pytest.raises(TimingProfileValidationError):
        normalize_ac_brand("itech")
    p12, p13 = chroma_phase_difference_commands(30)
    assert p12.startswith("PHASe:P12")
    assert p13.startswith("PHASe:P13")


def _checkbox(checked=True):
    return SimpleNamespace(isChecked=lambda checked=checked: checked)


def _combo(text):
    return SimpleNamespace(currentText=lambda text=text: text)


def _text(value):
    return SimpleNamespace(toPlainText=lambda value=value: str(value), currentText=lambda value=value: str(value))


def test_phase_jump_plan_rejects_itech_ui():
    ui = SimpleNamespace(
        checkBox_S1=_checkbox(False),
        checkBox_S2=_checkbox(False),
        checkBox_S3=_checkbox(True),
        checkBox_S_End=_checkbox(False),
        comboBox_S1_Phase=_combo("三相"),
        textEdit_S1_V1=_text("230"),
        textEdit_S1_V2=_text("230"),
        textEdit_S1_V3=_text("230"),
        timingProfileTable=SimpleNamespace(
            get_profile=lambda: [
                {
                    "enabled": True,
                    "label": "jump30",
                    "t_pre": 0,
                    "t_pre_unit": "秒",
                    "t_dwell": 1,
                    "t_dwell_unit": "秒",
                    "t_post": 0,
                    "t_post_unit": "秒",
                    "repeats": 1,
                    "phase_deg": 30,
                }
            ]
        ),
        analyzerModeSection=SimpleNamespace(current_mode=lambda: "wt3000"),
    )
    for ch in range(1, 5):
        setattr(ui, f"checkBox_S1_DC{ch}", _checkbox(False))
        setattr(ui, f"checkBox_S3_DC{ch}", _checkbox(False))
        setattr(ui, f"checkBox_S_End_DC{ch}", _checkbox(False))
    plan = build_phase_jump_plan(ui, ac_brand="itech")
    assert plan["ok"] is False
    assert "爱科" in plan["error"] or "fail closed" in plan["error"]


def test_dynamic_mppt_schema_accepts_power_pct():
    rows = validate_profile(
        [
            {
                "enabled": True,
                "label": "p50",
                "t_pre": 0,
                "t_pre_unit": "秒",
                "t_dwell": 1,
                "t_dwell_unit": "秒",
                "t_post": 0,
                "t_post_unit": "秒",
                "repeats": 1,
                "p_pct": 50,
            }
        ],
        DYNAMIC_MPPT_SCHEMA,
    )
    assert rows[0]["p_pct"] == 50.0
    with pytest.raises(TimingProfileValidationError):
        validate_profile(
            [
                {
                    "enabled": True,
                    "label": "bad",
                    "t_pre": 0,
                    "t_pre_unit": "秒",
                    "t_dwell": 1,
                    "t_dwell_unit": "秒",
                    "t_post": 0,
                    "t_post_unit": "秒",
                    "repeats": 1,
                    "p_pct": 150,
                }
            ],
            DYNAMIC_MPPT_SCHEMA,
        )


def test_forced_shutdown_dc_before_ac_and_bluesight_settle():
    rows = build_forced_shutdown_rows(
        dc_channels=[1, 2],
        per_dc_factor={"0": "Bluesight", "1": "Chroma"},
    )
    devices = [r[0] for r in rows if r[1] == "write"]
    assert devices.index("DC1") < devices.index("AC")
    assert all(r[2] == "OUTP OFF" for r in rows if r[1] == "write")
    waits = [r[8] for r in rows if r[1] == "query" and r[8] not in ("", None)]
    assert any(int(w) >= 50 for w in waits)
