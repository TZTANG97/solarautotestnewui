# -*- coding: utf-8 -*-
"""iot_device_ready unit tests."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.iot_device_ready import (
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


def test_format_ready_fail_reason_join():
    assert format_ready_fail_reason([]) == "设备未就绪"
    assert format_ready_fail_reason(["仅一条"]) == "仅一条"
    joined = format_ready_fail_reason(["A", "B"])
    assert joined.startswith("1.A")
    assert "2.B" in joined