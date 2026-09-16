# -*- coding: utf-8 -*-
"""iot_output_limits unit tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.iot_output_limits import (
    check_output_limits_gate,
    compare_limits,
    format_limit_fail_reason,
    load_expected_limits,
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

    # 缺失配置路径 → 门禁放行
    missing = tmp_path / "no_such_limits.json"
    ok, reason = check_output_limits_gate(path=missing)
    assert ok is True
    assert reason == ""


def test_read_limits_best_effort_unread_and_attrs():
    unread = read_limits_from_controllers(ac_controller=object(), dc_controllers={})
    assert unread["ac"].get("_unread") is True
    assert "未实现读回" in str(unread["ac"].get("detail", ""))

    class _WithMethod:
        def query_output_limits(self):
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
