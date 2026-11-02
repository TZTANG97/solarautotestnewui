# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

import pytest

from utils import iot_bench_prefs as prefs


@pytest.fixture()
def tmp_prefs(monkeypatch, tmp_path: Path):
    path = tmp_path / "iot_bench_prefs.json"
    monkeypatch.setattr(prefs, "prefs_path", lambda: path)
    return path


def test_save_and_merge_test_params(tmp_prefs):
    prefs.save_test_params(
        "flicker",
        widgets={"textEdit_S1_AC_VOLT": "230"},
        auto_append=True,
    )
    got = prefs.load_local()
    assert got["testParamsByType"]["flicker"]["widgets"]["textEdit_S1_AC_VOLT"] == "230"
    assert tmp_prefs.is_file()

    prefs.save_instruments([{"kind": "ac", "slot": "ac", "host": "10.0.0.1"}])
    got2 = prefs.load_local()
    assert got2["instruments"][0]["host"] == "10.0.0.1"
    assert "flicker" in got2["testParamsByType"]


def test_merge_widgets_respects_flag(tmp_prefs):
    prefs.save_test_params("flicker", widgets={"a": "1", "b": "2"})
    prefs.set_use_saved_test_params(True)
    merged = prefs.merge_widgets_with_memory("flicker", {"a": "cloud"}, {"useSavedTestParams": True})
    assert merged["a"] == "cloud"
    assert merged["b"] == "2"

    prefs.set_use_saved_test_params(False)
    merged2 = prefs.merge_widgets_with_memory("flicker", {"a": "cloud"}, {})
    assert merged2 == {"a": "cloud"}

    prefs.set_use_saved_test_params(True)
    merged3 = prefs.merge_widgets_with_memory(
        "flicker", {"a": "cloud"}, {"useSavedTestParams": False}
    )
    assert merged3 == {"a": "cloud"}


def test_merge_keeps_connected_three_phase_over_form_default(tmp_prefs):
    prefs.save_instruments(
        [
            {
                "kind": "ac",
                "slot": "ac",
                "widgets": {"comboBox_Phase": "三相"},
            }
        ]
    )
    merged = prefs.merge_widgets_with_memory(
        "flicker",
        {"comboBox_S1_AC_2": "单相", "textEdit_S1_AC_VOLT": "230"},
        {"useSavedTestParams": True},
    )
    assert merged["comboBox_S1_AC_2"] == "三相"
    assert merged["textEdit_S1_AC_VOLT"] == "230"

    explicit = prefs.apply_connected_ac_phase({"comboBox_S1_AC_2": "三相"})
    assert explicit["comboBox_S1_AC_2"] == "三相"


def test_loads_prefs_roundtrip(tmp_prefs):
    body = prefs.empty_prefs()
    body["instruments"] = [{"slot": "wt"}]
    prefs.save_local(body)
    raw = json.loads(tmp_prefs.read_text(encoding="utf-8"))
    assert raw["instruments"][0]["slot"] == "wt"


def test_persist_prefs_all_experiment_types(tmp_prefs, monkeypatch):
    """闪变/谐波/过载等：persist_current_project_prefs 按 handler.key 落盘。"""
    from utils import iot_ui_handoff as handoff

    samples = {
        "电压闪变": ("flicker", {"textEdit_S1_AC_VOLT": "230"}),
        "谐波电流": ("harmonic", {"textEdit_S1_AC_VOLT": "220"}),
        "过载能力测试": ("overload", {"textEdit_S1_AC_VOLT": "240"}),
        "固定PF=1": ("fixedpf", {"textEdit_S1_AC_VOLT": "230"}),
        "直流分量": ("dccomponent", {"textEdit_S1_AC_VOLT": "230"}),
    }

    class _Svc:
        def _resolve_handler(self, name: str):
            row = samples.get(name)
            if not row:
                return None
            key, widgets = row
            return {
                "key": key,
                "resolve_ui": lambda w=widgets: type("UI", (), {"_w": w})(),
            }

    monkeypatch.setattr(
        handoff,
        "collect_widget_values",
        lambda ui: dict(getattr(ui, "_w", {}) or {}),
    )
    svc = _Svc()
    for project, (key, widgets) in samples.items():
        n = handoff.persist_current_project_prefs(project, handoff_svc=svc)
        assert n == len(widgets), project
        got = prefs.load_local()["testParamsByType"][key]["widgets"]
        assert got["textEdit_S1_AC_VOLT"] == widgets["textEdit_S1_AC_VOLT"]
