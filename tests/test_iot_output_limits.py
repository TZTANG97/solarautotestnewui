# -*- coding: utf-8 -*-
"""iot_output_limits / iot_brand_limit_read unit tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.iot_brand_limit_read import (
    infer_ac_brand,
    infer_dc_brand,
    normalize_brand,
    read_ac_output_limits,
    read_chroma_scpi_limits,
    read_dc_output_limits,
)
from utils.iot_output_limits import (
    check_output_limits_gate,
    compare_limits,
    evaluate_controllers_output_limits_gate,
    format_limit_fail_reason,
    load_expected_limits,
    map_per_dc_factor_to_brands,
    read_limits_from_controllers,
)


def _base_expected(**overrides):
    data = {
        "ac": {"volt_max": None, "curr_max": None, "pow_max": None},
        "dc1": {"volt_max": None, "curr_max": None, "pow_max": None},
        "dc2": {"volt_max": None, "curr_max": None, "pow_max": None},
        "dc3": {"volt_max": None, "curr_max": None, "pow_max": None},
        "dc4": {"volt_max": None, "curr_max": None, "pow_max": None},
        "enforce": True,
    }
    data.update(overrides)
    return data


def test_null_expected_ok():
    expected = _base_expected()
    actual = {
        "ac": {"_unread": True, "detail": "未实现读回"},
        "dc1": {"volt_max": 999},
    }
    ok, reasons = compare_limits(expected, actual)
    assert ok is True
    assert reasons == []
    gate_ok, gate_reason = check_output_limits_gate(expected=expected, actual=actual)
    assert gate_ok is True
    assert gate_reason == ""


def test_enforce_false_ok_even_if_mismatch():
    expected = _base_expected(
        enforce=False,
        ac={"volt_max": 300, "curr_max": None, "pow_max": None},
    )
    actual = {"ac": {"volt_max": 400, "curr_max": 10, "pow_max": 1000}}
    ok, reasons = compare_limits(expected, actual)
    assert ok is True
    assert any("超限" in r for r in reasons)
    gate_ok, gate_reason = check_output_limits_gate(expected=expected, actual=actual)
    assert gate_ok is True
    assert gate_reason == ""


def test_mismatch_not_ok_chinese_reason():
    expected = _base_expected(
        ac={"volt_max": 300, "curr_max": None, "pow_max": None},
    )
    actual = {"ac": {"volt_max": 350}}
    ok, reasons = compare_limits(expected, actual)
    assert ok is False
    assert any("交流电源电压上限超限" in r for r in reasons)
    assert any("禁止开跑" in r for r in reasons)
    text = format_limit_fail_reason(reasons)
    assert "超限" in text
    assert "禁止开跑" in text
    gate_ok, gate_reason = check_output_limits_gate(expected=expected, actual=actual)
    assert gate_ok is False
    assert "超限" in gate_reason


def test_unread_when_expected_set_and_enforce():
    expected = _base_expected(
        dc1={"volt_max": 1000, "curr_max": None, "pow_max": None},
    )
    actual = {"dc1": {"_unread": True, "detail": "未实现读回"}}
    ok, reasons = compare_limits(expected, actual)
    assert ok is False
    assert any("直流电源1电压上限未能读回，禁止开跑" in r for r in reasons)
    gate_ok, gate_reason = check_output_limits_gate(expected=expected, actual=actual)
    assert gate_ok is False
    assert "未能读回" in gate_reason
    assert "禁止开跑" in gate_reason


def test_format_limit_fail_reason():
    assert format_limit_fail_reason([]) == "输出上限检查未通过"
    assert format_limit_fail_reason(["仅一条"]) == "仅一条"
    joined = format_limit_fail_reason(["A", "B"])
    assert joined.startswith("1.A")
    assert "2.B" in joined


def test_load_expected_limits_starter(tmp_path):
    starter = ROOT / "config" / "iot_output_limits.json"
    data = load_expected_limits(starter)
    assert "_note" in data
    assert data.get("enforce") is True
    assert "ac" in data
    assert "保护" in str(data.get("_note") or "") or "OVP" in str(data.get("_note") or "")

    missing = tmp_path / "no_such_limits.json"
    ok, reason = check_output_limits_gate(path=missing)
    assert ok is True
    assert reason == ""


def test_read_limits_best_effort_unread_and_attrs():
    unread = read_limits_from_controllers(ac_controller=object(), dc_controllers={})
    assert unread["ac"].get("_unread") is True
    assert "未实现读回" in str(unread["ac"].get("detail", ""))

    class _WithMethod:
        def query_output_limits(self, brand=None):
            return {"volt_max": 220, "curr_max": 5, "pow_max": 1000}

    class _WithAttrs:
        volt_max = 600
        curr_max = 20
        pow_max = 5000

    got = read_limits_from_controllers(
        ac_controller=_WithMethod(),
        dc_controllers={"dc1": _WithAttrs()},
    )
    assert got["ac"]["volt_max"] == 220
    assert got["dc1"]["curr_max"] == 20
    assert got["dc2"].get("_unread") is True


def test_normalize_and_infer_brand():
    assert normalize_brand("chroma_ip") == "chroma"
    assert normalize_brand("爱科") == "itech"
    assert normalize_brand("Bluesight") == "bluesight"
    ac = SimpleNamespace(_itech=object(), _idn="", handle=None, client=None, connected=True)
    assert infer_ac_brand(ac) == "itech"
    dc = SimpleNamespace(client=object(), handle=None, connected=True, brand=None)
    assert infer_dc_brand(dc) == "bluesight"
    assert infer_dc_brand(dc, "Chroma") == "chroma"


def test_unknown_brand_unread():
    ctrl = SimpleNamespace(
        connected=True,
        handle=object(),
        client=None,
        _itech=None,
        _idn="",
        brand="unknown_xyz",
    )
    got = read_ac_output_limits(ctrl, brand="unknown_xyz")
    assert got.get("_unread") is True
    assert "未识别" in str(got.get("detail") or "") or "不支持" in str(got.get("detail") or "")


def test_itech_modbus_regs_pending_unread():
    client = SimpleNamespace()
    ctrl = SimpleNamespace(
        connected=True,
        handle=object(),
        client=client,
        _itech=SimpleNamespace(AC_client=client),
        _idn="",
    )
    got = read_ac_output_limits(ctrl, brand="itech")
    assert got.get("_unread") is True
    assert "寄存器" in str(got.get("detail") or "")


def test_bluesight_regs_pending_unread():
    ctrl = SimpleNamespace(connected=True, handle=None, client=object(), brand="bluesight")
    got = read_dc_output_limits(ctrl, brand="bluesight")
    assert got.get("_unread") is True
    assert "寄存器" in str(got.get("detail") or "")


def test_chroma_scpi_read_success():
    class _Handle:
        def __init__(self):
            self.queries = []

        def query(self, cmd):
            self.queries.append(cmd)
            if cmd == "SYST:ERR?":
                return '0,"No error"'
            if "VOLT:PROT:HIGH?" in cmd or cmd.endswith("VOLT:PROT?"):
                return "300.0"
            if "CURR:PROT:HIGH?" in cmd or cmd.endswith("CURR:PROT?"):
                return "10.5"
            if "POW" in cmd:
                return "ERR"
            raise RuntimeError("nope")

    handle = _Handle()
    scpi_map = {
        "volt_max": ("SOUR:VOLT:PROT:HIGH?",),
        "curr_max": ("SOUR:CURR:PROT:HIGH?",),
        "pow_max": ("SOUR:POW:PROT:HIGH?",),
    }
    got = read_chroma_scpi_limits(handle, scpi_map)
    assert got.get("_unread") is not True
    assert got["volt_max"] == 300.0
    assert got["curr_max"] == 10.5
    assert "pow_max" not in got or got.get("_unread")


def test_evaluate_gate_with_fake_controllers():
    expected = _base_expected(
        ac={"volt_max": 300, "curr_max": None, "pow_max": None},
        dc1={"volt_max": 1000, "curr_max": None, "pow_max": None},
    )

    class _AcOk:
        connected = True

        def query_output_limits(self, brand=None):
            return {"volt_max": 280, "curr_max": 5}

    class _DcOver:
        connected = True

        def query_output_limits(self, brand=None):
            return {"volt_max": 1200}

    ok, reason = evaluate_controllers_output_limits_gate(
        ac_controller=_AcOk(),
        dc_controllers={"dc1": _DcOver()},
        expected=expected,
    )
    assert ok is False
    assert "直流电源1" in reason
    assert "超限" in reason

    class _DcOk:
        connected = True

        def query_output_limits(self, brand=None):
            return {"volt_max": 900}

    ok2, reason2 = evaluate_controllers_output_limits_gate(
        ac_controller=_AcOk(),
        dc_controllers={"dc1": _DcOk()},
        expected=expected,
    )
    assert ok2 is True
    assert reason2 == ""


def test_map_per_dc_factor_to_brands():
    got = map_per_dc_factor_to_brands({"0": "Chroma", "1": "Bluesight", "dc3": "Itech"})
    assert got["dc1"] == "Chroma"
    assert got["dc2"] == "Bluesight"
    assert got["dc3"] == "Itech"
