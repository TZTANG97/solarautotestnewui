# -*- coding: utf-8 -*-
"""iot_device_ready unit tests."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.iot_device_ready import (
    analyzer_slot_required,
    check_devices_ready,
    format_ready_fail_reason,
    required_dc_slots_from_ui,
)


class _Box:
    def __init__(self, checked: bool):
        self._checked = checked

    def isChecked(self):
        return self._checked


def test_required_dc_slots_from_ui():
    ui = SimpleNamespace(
        checkBox_S1_DC1=_Box(True),
        checkBox_S1_DC2=_Box(False),
        checkBox_DC3=_Box(True),
    )
    assert required_dc_slots_from_ui(ui) == ["dc1", "dc3"]
    assert required_dc_slots_from_ui(None) == []


def test_check_devices_ready_ok():
    ac = SimpleNamespace(connected=True)
    dc1 = SimpleNamespace(connected=True)
    ok, reasons = check_devices_ready(
        ac_controller=ac,
        dc_controllers={"dc1": dc1},
        per_dc_factor={"0": "Chroma"},
        required_dc_slots=["dc1"],
        require_ac=True,
    )
    assert ok is True
    assert reasons == []


def test_check_devices_ready_fail_messages():
    ok, reasons = check_devices_ready(
        ac_controller=None,
        dc_controllers={"dc1": SimpleNamespace(connected=False)},
        per_dc_factor={},
        required_dc_slots=["dc1"],
        require_ac=True,
    )
    assert ok is False
    assert any("交流电源未连接" in r for r in reasons)
    assert any("直流电源1未连接" in r for r in reasons)

    ok10, reasons10 = check_devices_ready(
        ac_controller=SimpleNamespace(connected=True),
        dc_controllers={"dc10": SimpleNamespace(connected=False)},
        per_dc_factor={},
        required_dc_slots=["dc10"],
        require_ac=False,
    )
    assert ok10 is False
    assert any("直流电源10未连接" in r for r in reasons10)

    ok2, reasons2 = check_devices_ready(
        ac_controller=SimpleNamespace(connected=True),
        dc_controllers={"dc1": SimpleNamespace(connected=True)},
        per_dc_factor={"0": ""},
        required_dc_slots=["dc1"],
    )
    assert ok2 is False
    assert any("厂家未识别" in r for r in reasons2)
    text = format_ready_fail_reason(reasons2)
    assert "厂家未识别" in text
    assert "禁止致茂IVC混用" in text


def test_analyzer_slot_dewetron_ignores_step_checkbox():
    """无功能力范围这类试验：S2 勾着且选了德威创，不能当成 WT。"""
    ui = SimpleNamespace(
        checkBox_S2=_Box(True),
        radio_dewetron=_Box(True),
        radio_wt=_Box(False),
        radio_wt3000=_Box(False),
        analyzerModeSection=SimpleNamespace(
            is_dewetron_mode=lambda: True,
            current_mode=lambda: "dewetron",
        ),
    )
    assert analyzer_slot_required(ui) == "dew"


def test_analyzer_slot_radio_dewetron_wins_over_stale_wt_mode():
    ui = SimpleNamespace(
        checkBox_S2=_Box(True),
        radio_dewetron=_Box(True),
        radio_wt=_Box(False),
        analyzerModeSection=SimpleNamespace(
            is_dewetron_mode=lambda: False,
            current_mode=lambda: "wt3000",
        ),
    )
    assert analyzer_slot_required(ui) == "dew"


def test_analyzer_slot_wt_when_power_analyzer_selected():
    ui = SimpleNamespace(
        checkBox_S2=_Box(True),
        radio_dewetron=_Box(False),
        radio_wt3000=_Box(True),
        analyzerModeSection=SimpleNamespace(
            is_dewetron_mode=lambda: False,
            current_mode=lambda: "wt3000",
        ),
    )
    assert analyzer_slot_required(ui) == "wt"
    only_step = SimpleNamespace(checkBox_S2=_Box(True))
    assert analyzer_slot_required(only_step) == "wt"
    assert analyzer_slot_required(SimpleNamespace(checkBox_S2=_Box(False))) == ""


def test_format_ready_fail_reason_join():
    assert format_ready_fail_reason([]) == "设备未就绪"
    assert format_ready_fail_reason(["仅一条"]) == "仅一条"
    joined = format_ready_fail_reason(["A", "B"])
    assert joined.startswith("1.A")
    assert "2.B" in joined