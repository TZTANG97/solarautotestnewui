# -*- coding: utf-8 -*-
"""中途停机 / 结案：能从 LOCALAPPDATA dewetron_save 找到 reactive-qcap CSV。"""

from pathlib import Path

from utils.iot_data_analysis_bridge import _pick_input_dir, _prefer_keys_for_test
from utils.last_dew_export import hard_dewetron_save_dirs, last_dew_csv, remember_dew_export


def test_prefer_keys_include_reactive_hyphen():
    keys = _prefer_keys_for_test("reactive_qcap")
    assert "qcap" in keys
    assert "reactive-qcap" in keys


def test_pick_input_dir_finds_localappdata_dewetron(tmp_path, monkeypatch):
    dew = tmp_path / "SolarAutoTest" / "dewetron_save"
    dew.mkdir(parents=True)
    csv = dew / "reactive-qcap_20261111_203620.csv"
    csv.write_text(
        "Time [s],P_t\n0.0,1.0\n0.1,1.1\n0.2,1.2\n0.3,1.3\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(
        "utils.wt_save_path.default_dewetron_save_dir",
        lambda: str(tmp_path / "other_empty_dew"),
    )
    monkeypatch.setattr(
        "utils.wt_save_path.default_wt_save_path",
        lambda: str(tmp_path / "wt_save"),
    )
    # data_root 指错目录时，仍应硬扫 LOCALAPPDATA\\SolarAutoTest\\dewetron_save
    picked = _pick_input_dir(
        tmp_path / "repo", {"result_summary": {"testType": "reactive_qcap"}}
    )
    assert picked is not None
    assert Path(picked) == dew


def test_remember_sidecar_survives_cleared_memory(tmp_path, monkeypatch):
    dew = tmp_path / "SolarAutoTest" / "dewetron_save"
    dew.mkdir(parents=True)
    csv = dew / "reactive-qcap_20261111_204420.csv"
    csv.write_text("Time [s],P\n0,1\n1,2\n2,3\n", encoding="utf-8")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(
        "utils.wt_save_path.default_dewetron_save_dir",
        lambda: str(dew),
    )
    remember_dew_export(str(csv))
    # 模拟双份 utils：清掉内存后仍能从 sidecar 读到
    import utils.last_dew_export as mod

    mod._LAST_CSV = ""
    mod._LAST_DIR = ""
    assert last_dew_csv() == str(csv)
    picked = _pick_input_dir(tmp_path / "repo", {"result_summary": {"testType": "reactiveqcap"}})
    assert picked == dew


def test_pick_from_summary_last_dew_csv(tmp_path):
    dew = tmp_path / "dewetron_save"
    dew.mkdir()
    csv = dew / "reactive-qcap_x.csv"
    csv.write_text("t,p\n0,1\n1,2\n2,3\n", encoding="utf-8")
    picked = _pick_input_dir(
        tmp_path,
        {
            "result_summary": {
                "testType": "reactive_qcap",
                "last_dew_csv": str(csv),
            }
        },
    )
    assert picked == dew


def test_hard_dewetron_save_dirs_includes_localappdata(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    dirs = hard_dewetron_save_dirs()
    assert any("dewetron_save" in str(d).replace("\\", "/") for d in dirs)
