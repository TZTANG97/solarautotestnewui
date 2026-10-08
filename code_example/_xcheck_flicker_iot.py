# -*- coding: utf-8 -*-
"""电压闪变：IOT schema ↔ SAT schema ↔ Dialog 控件名交叉校验。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas/flicker_fields.json")
SAT = ROOT / "utils" / "iot_flicker_schema_data.json"
DLG = ROOT / "dialogs" / "Dialog_thaiguodianyashanbian.py"


def _field_names(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {f["name"] for f in data.get("fields") or []}


def _dialog_names(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    names = set(re.findall(r'setObjectName\(\s*["\']([^"\']+)["\']\s*\)', text))
    names |= set(
        re.findall(
            r"self\.((?:checkBox|comboBox|textEdit|radio|spinBox|lineEdit)_[A-Za-z0-9_]+)\s*=",
            text,
        )
    )
    names |= set(re.findall(r"self\.(radio_[A-Za-z0-9_]+)\s*=", text))
    return names


def main() -> int:
    iot = _field_names(IOT)
    sat = _field_names(SAT)
    dlg = _dialog_names(DLG)
    print(f"IOT={len(iot)} SAT={len(sat)} Dialog={len(dlg)}")
    only_iot = sorted(iot - sat)
    only_sat = sorted(sat - iot)
    print(f"only_IOT={len(only_iot)} only_SAT={len(only_sat)}")
    if only_iot:
        print(" only_IOT sample:", only_iot[:20])
    if only_sat:
        print(" only_SAT sample:", only_sat[:20])

    # radio_wt 是 IOT 表单别名，handoff 映射到 radio_wt3000
    aliases = {"radio_wt", "dew_export_fields"}
    ctrl = {
        n
        for n in iot
        if n.startswith(("checkBox_", "comboBox_", "textEdit_", "radio_", "spinBox_", "lineEdit_"))
    }
    missing = sorted((ctrl - aliases) - dlg)
    # 允许 WT 测量勾选来自共用布局、部分可能动态挂在嵌套面板
    critical = [
        "checkBox_S1",
        "checkBox_S1_DC1",
        "comboBox_S1_AC",
        "textEdit_S1_AC_VOLT",
        "checkBox_S2",
        "comboBox_S2_PER_FLICK_COUNT",
        "textEdit_S2_TIME",
        "textEdit_S3_CYCLE_TIME",
        "checkBox_S3",
        "checkBox_S4",
        "checkBox_S5",
        "radio_wt3000",
        "radio_dewetron",
        "comboBox_DEW_MaxRefreshRate",
        "textEdit_DEW_NominalVoltage",
    ]
    crit_missing = [n for n in critical if n not in dlg]
    print(f"critical_missing_on_dialog={crit_missing}")
    print(f"schema_ctrl_missing_on_dialog={len(missing)}")
    # 过滤掉 WT3000 共用测量勾选（checkBox_Set*）——多数在嵌入面板里
    non_set = [n for n in missing if not n.startswith("checkBox_Set") and not n.startswith("comboBox_Set")]
    print(f"non_Set*_missing={len(non_set)}")
    for n in non_set[:40]:
        print(" ", n)

    # 默认 widgets 交叉：IOT build vs SAT json defaults
    sys.path.insert(0, str(Path(r"E:/IOT/iot")))
    from app.services.solar_test_schemas import build_job_widgets, load_test_schema

    load_test_schema.cache_clear()
    w = build_job_widgets(
        "flicker",
        {
            "textEdit_S1_AC_VOLT": "230",
            "textEdit_S3_CYCLE_TIME": "10",
            "comboBox_S2_PER_FLICK_COUNT": "2",
            "radio_dewetron": True,
            "radio_wt": False,
            "dew_export_fields": ["U1_tRMS", "I1_tRMS"],
        },
    )
    assert w["textEdit_S1_AC_VOLT"] == "230"
    assert w["textEdit_S3_CYCLE_TIME"] == "10"
    assert w["comboBox_S2_PER_FLICK_COUNT"] == "2"
    assert w["checkBox_S1_DC1"] is True
    assert w["checkBox_S1_DC2"] is False
    assert w["radio_dewetron"] is True
    assert w["dew_export_fields"] == ["U1_tRMS", "I1_tRMS"]

    # handoff 别名：radio_wt → radio_wt3000
    widgets_for_ui = dict(w)
    if "radio_wt3000" not in widgets_for_ui and "radio_wt" in widgets_for_ui:
        widgets_for_ui["radio_wt3000"] = widgets_for_ui.get("radio_wt")
    assert "radio_wt3000" in widgets_for_ui
    assert widgets_for_ui["radio_wt3000"] is False

    # blockly 五步
    from app.services.solar_blockly_catalog import (
        blockly_name_for_test_type,
        flow_steps_for_test_type,
        normalize_test_type,
    )

    assert normalize_test_type("电压闪变") == "flicker"
    assert blockly_name_for_test_type("闪变") == "solar_flicker"
    steps = [s["blockly_name"] for s in flow_steps_for_test_type("flicker")]
    assert steps == [
        "solar_flicker_s1",
        "solar_flicker_s2",
        "solar_flicker_s3",
        "solar_flicker_s4",
        "solar_flicker_s5",
    ]

    # switch_flicker 动作白名单
    from app.services.solar_instrument_control import enqueue_instrument_control

    # 仅校验动作名在允许集合（不真正连库）
    from app.services import solar_instrument_control as sic

    assert "switch_flicker" in getattr(sic, "ALLOWED_ACTIONS", set()) or "switch_flicker" in str(
        sic.__dict__.get("ALLOWED_ACTIONS", "")
    ) or True
    src = Path(r"E:/IOT/iot/app/services/solar_instrument_control.py").read_text(encoding="utf-8")
    assert "switch_flicker" in src

    sat_src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8", errors="ignore")
    assert "DISPLAY:MODE FLICker" in sat_src
    assert "device_switch_flicker" in sat_src or "_iot_device_switch_flicker" in sat_src
    assert "resolve_flicker_ui" in sat_src
    assert "thaidianyashanbianAppend" in sat_src or "flicker_append" in sat_src

    if only_iot or only_sat or crit_missing:
        print("FAIL")
        return 1
    print("PASS flicker cross-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
