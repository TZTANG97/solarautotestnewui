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


def test_loads_prefs_roundtrip(tmp_prefs):
    body = prefs.empty_prefs()
    body["instruments"] = [{"slot": "wt"}]
    prefs.save_local(body)
    raw = json.loads(tmp_prefs.read_text(encoding="utf-8"))
    assert raw["instruments"][0]["slot"] == "wt"
