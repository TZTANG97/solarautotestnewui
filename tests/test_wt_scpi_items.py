# -*- coding: utf-8 -*-
"""Full coverage tests for WT checkbox → SCPI NUMERIC mapping."""
from __future__ import annotations

import re
from pathlib import Path

from utils.wt_scpi_items import (
    all_known_checkbox_keys,
    items_from_wt_config,
    macro_column_name,
    max_item_slots,
    selected_functions,
    selected_singles,
    selected_targets,
)


def _open_save_checkbox_keys() -> set[str]:
    keys: set[str] = set()
    root = Path(__file__).resolve().parents[1] / "utils"
    for path in root.glob("Open_Save_ThaiWT*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        keys |= set(re.findall(r"checkBox_Set[A-Za-z0-9_]+", text))
    return keys


def test_all_open_save_checkboxes_are_classified():
    known = all_known_checkbox_keys()
    missing = sorted(_open_save_checkbox_keys() - known)
    assert missing == [], f"unmapped checkboxes: {missing}"


def test_default_fallback_when_nothing_checked():
    items = items_from_wt_config({"Style": "Thai_WT3000E_Config"})
    assert "URMS,1" in items and "P,SIGMA" in items and "FU,1" in items


def test_elements_and_basic_ui_expand():
    cfg = {
        "Style": "Thai_WT3000E_Config",
        "checkBox_SetElement1": "1",
        "checkBox_SetElement2": "1",
        "checkBox_SetElement3": "1",
        "checkBox_SetSigma": "1",
        "checkBox_SetU": "1",
        "checkBox_SetI": "1",
        "checkBox_SetP": "1",
        "checkBox_SetQ": "1",
        "checkBox_SetFreqU": "1",
        "comboBox_ProjectNum": 1,
    }
    assert selected_targets(cfg) == ["1", "2", "3", "SIGMA"]
    assert selected_functions(cfg) == ["URMS", "IRMS", "P", "Q", "FU"]
    items = items_from_wt_config(cfg)
    # 同一测量项先排元素再排总和，和宏 CSV 列顺序一致。
    assert items[:5] == ["URMS,1", "URMS,2", "URMS,3", "URMS,SIGMA", "IRMS,1"]
    assert "P,SIGMA" in items
    assert max_item_slots(cfg) == 24


def test_singles_and_harmonics_included():
    cfg = {
        "Style": "Thai_WT3000E_Config",
        "checkBox_SetElement1": "1",
        "checkBox_SetTime": "1",
        "checkBox_SetSpeed": "1",
        "checkBox_SetF01": "1",
        "checkBox_SetUk": "1",
        "checkBox_SetUthd": "1",
        "checkBox_SetEta1": "1",
        "comboBox_ProjectNum": 2,  # 48
    }
    singles = selected_singles(cfg)
    assert "TIME" in singles and "SPEED" in singles and "F1" in singles and "ETA1" in singles
    items = items_from_wt_config(cfg)
    assert "U(K),1" in items
    assert "UTHD,1" in items
    assert "TIME" in items
    assert "SPEED" in items
    assert "F1" in items
    assert "ETA1" in items


def test_wt1800_urms_checkbox_and_six_elements():
    cfg = {
        "Style": "Thai_WT1800_Config",
        "checkBox_SetElement1": "1",
        "checkBox_SetElement6": "1",
        "checkBox_SetSigmaA": "1",
        "checkBox_SetUrms": "1",
        "checkBox_SetPF": "1",
        "comboBox_ProjectNum": 0,
    }
    targets = selected_targets(cfg)
    assert "1" in targets and "6" in targets and "SIGMAA" in targets
    items = items_from_wt_config(cfg)
    assert "URMS,1" in items and "URMS,6" in items and "URMS,SIGMAA" in items
    assert "LAMBDA,1" in items
    assert len(items) <= 12


def test_project_num_caps_long_list():
    cfg = {
        "Style": "Thai_WT1800_Config",
        "checkBox_SetElement1": "1",
        "checkBox_SetElement2": "1",
        "checkBox_SetElement3": "1",
        "checkBox_SetElement4": "1",
        "checkBox_SetElement5": "1",
        "checkBox_SetElement6": "1",
        "checkBox_SetSigma": "1",
        "checkBox_SetUrms": "1",
        "checkBox_SetIrms": "1",
        "checkBox_SetP": "1",
        "checkBox_SetQ": "1",
        "checkBox_SetS": "1",
        "comboBox_ProjectNum": 0,
    }
    items = items_from_wt_config(cfg)
    assert "URMS,SIGMA" in items
    assert "P,SIGMA" in items
    assert "Q,SIGMA" in items
    assert len(items) > 12


def test_sigmaa_survives_twelve_slot_cap():
    """WT3000 的 SigmaA 就是 ΣA，元素名 SIGMA。项目数 12 也不能把它换成仪器不认的 SIGMAA。"""
    cfg = {
        "Style": "Thai_WT3000E_Config",
        "checkBox_SetElement1": "1",
        "checkBox_SetElement2": "1",
        "checkBox_SetElement3": "1",
        "checkBox_SetSigma": "1",
        "checkBox_SetSigmaA": "1",
        "checkBox_SetU": "1",
        "checkBox_SetI": "1",
        "checkBox_SetP": "1",
        "comboBox_ProjectNum": 0,
    }
    items = items_from_wt_config(cfg)
    assert "URMS,SIGMA" in items
    assert "IRMS,SIGMA" in items
    assert "P,SIGMA" in items
    assert "URMS,SIGMAA" not in items
    assert "P,SIGMAA" not in items
    assert macro_column_name("URMS,SIGMA", "Thai_WT3000E_Config") == "U-SIGMA"


def test_only_sigmaa_checkbox_writes_sigma_column():
    """只勾 SigmaA、不勾元素 1/2/3：CSV 表头必须有 U-SIGMA，不能被默认元素盖掉。"""
    cfg = {
        "Style": "Thai_WT3000E_Config",
        "checkBox_SetElement1": False,
        "checkBox_SetElement2": False,
        "checkBox_SetElement3": False,
        "checkBox_SetSigma": False,
        "checkBox_SetSigmaA": True,
        "checkBox_SetSigmaB": False,
        "checkBox_SetU": True,
        "checkBox_SetI": True,
        "checkBox_SetP": True,
        "checkBox_SetQ": True,
        "comboBox_ProjectNum": "12",
    }
    assert selected_targets(cfg) == ["SIGMA"]
    items = items_from_wt_config(cfg)
    assert items[:4] == ["URMS,SIGMA", "IRMS,SIGMA", "P,SIGMA", "Q,SIGMA"]
    assert all(not tok.endswith(",1") for tok in items)
    headers = ["Time [s]"] + [macro_column_name(tok, cfg["Style"]) for tok in items]
    assert "U-SIGMA" in headers
    assert "I-SIGMA" in headers
    assert "P-SIGMA" in headers
    assert "Q-SIGMA" in headers
    assert "U-1" not in headers
    assert "U-SIGMAA" not in headers


def test_only_sigmaa_without_measure_functions_still_has_u_sigma():
    cfg = {
        "Style": "Thai_WT3000E_Config",
        "checkBox_SetSigmaA": "1",
        "comboBox_ProjectNum": 0,
    }
    items = items_from_wt_config(cfg)
    assert "URMS,SIGMA" in items
    assert "P,SIGMA" in items
    assert "Q,SIGMA" in items
    assert "URMS,1" not in items
    assert "URMS,SIGMAA" not in items
    assert macro_column_name("URMS,SIGMA", cfg["Style"]) == "U-SIGMA"


def test_only_sigmaa_on_wt1800_stays_sigmaa():
    cfg = {
        "Style": "Thai_WT1800_Config",
        "checkBox_SetSigmaA": "1",
        "checkBox_SetUrms": "1",
    }
    items = items_from_wt_config(cfg)
    assert items == ["URMS,SIGMAA"]
    assert macro_column_name(items[0], cfg["Style"]) == "Urms-SIGMAA"


def test_only_sigmaa_web_radio_wt3000_without_style():
    cfg = {
        "radio_S2_WT3000": True,
        "checkBox_SetSigmaA": True,
        "checkBox_SetU": True,
    }
    items = items_from_wt_config(cfg)
    assert items == ["URMS,SIGMA"]
    assert macro_column_name(items[0], "Thai_WT3000E_Config") == "U-SIGMA"


def test_macro_column_names_match_viewer_csv():
    assert macro_column_name("URMS,SIGMAA", "Thai_WT3000E_Config") == "U-SIGMAA"
    assert macro_column_name("URMS,1", "Thai_WT1800_Config") == "Urms-1"
    assert macro_column_name("LAMBDA,1", "Thai_WT3000E_Config") == "PF-1"
    assert macro_column_name("FU,SIGMA", "WT3000") == "FreqU-SIGMA"
    assert macro_column_name("F1", "") == "F01"
    assert macro_column_name("ETA1", "Thai_WT1800_Config") == "η1"
    assert macro_column_name("WPPLUS", "") == "WP+"


def test_save_path_unrelated_still_maps():
    cfg = {
        "Style": "Thai_WT3000E_Config",
        "textEdit_SavePath": r"D:\EnergyTest\wt",
        "textEdit_FileNameList": "CaseA",
        "checkBox_SetElement1": "1",
        "checkBox_SetP": "1",
    }
    assert items_from_wt_config(cfg) == ["P,1"]


def test_mass_check_all_functions_respects_cap():
    """Tick every classified function/single once; still returns ≤ ProjectNum."""
    cfg = {"Style": "Thai_WT5000_Config", "comboBox_ProjectNum": 3}  # 200
    for i in range(1, 5):
        cfg[f"checkBox_SetElement{i}"] = "1"
    cfg["checkBox_SetSigma"] = "1"
    from utils.wt_scpi_items import _FUNCTION_BY_CHECKBOX, _SINGLE_BY_CHECKBOX

    for key in _FUNCTION_BY_CHECKBOX:
        cfg[key] = "1"
    for key in _SINGLE_BY_CHECKBOX:
        cfg[key] = "1"
    items = items_from_wt_config(cfg)
    assert 1 <= len(items) <= 200
    assert any(x.startswith("URMS,") for x in items)
    # Singles may be truncated when every function×element fills the slot budget
    assert any(x.startswith("P,") for x in items)
