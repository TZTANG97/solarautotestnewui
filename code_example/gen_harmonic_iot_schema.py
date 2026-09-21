# -*- coding: utf-8 -*-
"""
从 Dialog_thaixiebodianliu.py 生成谐波电流 IOT 字段 schema（不依赖 Qt 运行时）。

输出：
  - utils/iot_harmonic_schema_data.json
  - 可选 --iot-out 写入 IOT harmonic_fields.json

Usage:
  uv run python code_example/gen_harmonic_iot_schema.py
  uv run python code_example/gen_harmonic_iot_schema.py --iot-out E:/IOT/iot/app/services/solar_test_schemas/harmonic_fields.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOG = ROOT / "Dialog_thaixiebodianliu.py"
OUT_SW = ROOT / "utils" / "iot_harmonic_schema_data.json"
OVERLOAD_SW = ROOT / "utils" / "iot_overload_schema_data.json"
IOT_OVERLOAD = Path(r"E:/IOT/iot/app/services/solar_test_schemas/overload_fields.json")

LABELS = {
    "checkBox_S1": "启用步骤1 AC/DC",
    "comboBox_S1_AC": "AC 开关",
    "comboBox_S1_AC_2": "AC 单相/三相",
    "textEdit_S1_AC_VOLT": "A相电压(V)",
    "textEdit_S1_AC_VOLT_2": "B相电压(V)",
    "textEdit_S1_AC_VOLT_3": "C相电压(V)",
    "textEdit_S1_AC_FR": "AC 频率(Hz)",
    "checkBox_S1_DC1": "启用直流电源1",
    "comboBox_S1_DC1": "直流1 开关",
    "textEdit_S1_DC1_VOLT": "直流1 Vmp(V)",
    "textEdit_S1_DC1_CURR": "直流1 Imp(A)",
    "textEdit_S1_DC1_Voc": "直流1 Voc(V)",
    "textEdit_S1_DC1_Isc": "直流1 Isc(A)",
    "textEdit_S1_DC1_PF": "直流1 功率(%)",
    "checkBox_S1_DC2": "启用直流电源2",
    "comboBox_S1_DC2": "直流2 开关",
    "textEdit_S1_DC2_VOLT": "直流2 Vmp(V)",
    "textEdit_S1_DC2_CURR": "直流2 Imp(A)",
    "textEdit_S1_DC2_Voc": "直流2 Voc(V)",
    "textEdit_S1_DC2_Isc": "直流2 Isc(A)",
    "textEdit_S1_DC2_PF": "直流2 功率(%)",
    "checkBox_S1_DC3": "启用直流电源3",
    "comboBox_S1_DC3": "直流3 开关",
    "textEdit_S1_DC3_VOLT": "直流3 Vmp(V)",
    "textEdit_S1_DC3_CURR": "直流3 Imp(A)",
    "textEdit_S1_DC3_Voc": "直流3 Voc(V)",
    "textEdit_S1_DC3_Isc": "直流3 Isc(A)",
    "textEdit_S1_DC3_PF": "直流3 功率(%)",
    "checkBox_S1_DC4": "启用直流电源4",
    "comboBox_S1_DC4": "直流4 开关",
    "textEdit_S1_DC4_VOLT": "直流4 Vmp(V)",
    "textEdit_S1_DC4_CURR": "直流4 Imp(A)",
    "textEdit_S1_DC4_Voc": "直流4 Voc(V)",
    "textEdit_S1_DC4_Isc": "直流4 Isc(A)",
    "textEdit_S1_DC4_PF": "直流4 功率(%)",
    "textEdit_S1_ACWaitTIME": "等待时间",
    "comboBox_S1_ACWaitTIME": "等待时间单位",
    "textEdit_S1_TIME": "启机时间",
    "comboBox_S1_TIME": "启机时间单位",
    "checkBox_S1_Integral": "积分测试",
    "checkBox_S2": "启用步骤2 功率分析仪",
    "radio_S2_WT3000": "WT3000",
    "radio_S2_WT1800": "WT1800",
    "radio_S2_WT1806E": "WT1806E",
    "radio_S2_WT5000": "WT5000",
    "checkBox_DEW_HarmonicEnabled": "启用德威创谐波",
    "spinBox_DEW_MaxHarmonicOrder": "最大谐波阶次",
    "spinBox_DEW_THDOrder": "THD 阶次",
    "comboBox_DEW_GroupingType": "Grouping type",
    "comboBox_DEW_MaxRefreshRate": "最大刷新率 (ms)",
    "checkBox_DEW_MultiFileStorage": "多文件存储",
    "checkBox_DEW_SplitByTime": "按时间拆分",
    "spinBox_DEW_SplitTime": "拆分时间(s)",
    "checkBox_DEW_CreateSubfolder": "创建子目录",
    "spinBox_DEW_DecimalPlaces": "保留小数位数",
    "checkBox_DEW_RealtimeWaveform": "启用实时波形显示",
    "comboBox_S3_record_mode": "录波模式",
    "checkBox_S5": "启用关机",
    "comboBox_S5_AC": "关机 AC",
    "radio_wt3000": "WT3000谐波",
    "radio_dewetron": "德威创",
    "radio_wt": "功率分析仪",
    "dew_export_fields": "导出字段选择",
}

GROUP_RULES = [
    ("step1_ac", "① AC 电源", ("S1_AC", "checkBox_S1")),
    ("step1_dc", "① DC 电源", ("S1_DC",)),
    ("step1_time", "① 时序", ("S1_ACWait", "S1_TIME", "textEdit_S1_TIME", "comboBox_S1_TIME", "Integral")),
    ("step2_wt", "② 功率分析仪", ("S2", "radio_S2", "radio_wt", "radio_wt3000")),
    ("step2_dew", "② 德威创", ("DEW", "radio_dewetron")),
    ("step3_harm", "③ 谐波工况", ("S3", "S1_DC1_", "S1_DC2_", "S1_DC3_", "S1_DC4_", "PF_")),
    ("step4_off", "④ 关机设置", ("S5", "S_END")),
]


def _group_for(name: str) -> str:
    for gid, _title, keys in GROUP_RULES:
        if any(k in name for k in keys):
            return gid
    return "other"


def _infer_type(name: str) -> str:
    if name.startswith("checkBox_"):
        return "checkbox"
    if name.startswith("comboBox_"):
        return "select"
    if name.startswith("textEdit_") or name.startswith("lineEdit_"):
        return "text"
    if name.startswith("spinBox_") or name.startswith("doubleSpinBox_"):
        return "number"
    if name.startswith("radioButton_") or name.startswith("radio_"):
        return "radio"
    return "text"


def parse_dialog(src: str) -> dict:
    fields: dict[str, dict] = {}

    def _ensure(name: str, **overrides):
        if not name:
            return
        base = {
            "name": name,
            "label": LABELS.get(name, name),
            "type": _infer_type(name),
            "group": _group_for(name),
            "default": None,
            "options": [],
        }
        base.update(overrides)
        if name not in fields:
            fields[name] = base
        else:
            fields[name].update({k: v for k, v in overrides.items() if v is not None})

    for m in re.finditer(r'\.setObjectName\(\s*["\']([^"\']+)["\']\s*\)', src):
        name = m.group(1)
        if name.startswith(("pushButton_", "label_", "groupBox_", "step_indicator_", "treeWidget_")):
            continue
        if name in ("Dialog_thaixiebodianliu",):
            continue
        _ensure(name)

    # HARMONIC_STEPS 字典里的控件名
    for key in ("step_cb", "dc1_cb", "dc2_cb", "dc3_cb", "dc4_cb", "pf_te"):
        for m in re.finditer(rf'"{key}":\s*"([^"]+)"', src):
            _ensure(m.group(1))

    # _make_checkbox / _make_combo / _make_te / _make_radio / _make_input 的 name 参数
    for m in re.finditer(
        r'_make_(?:checkbox|combo|te|radio|input)\(\s*["\']([^"\']+)["\']',
        src,
    ):
        _ensure(m.group(1))

    # 模式切换 radio 无 setObjectName
    _ensure("radio_wt3000", type="radio", group="step2_wt", default=True)
    _ensure("radio_dewetron", type="radio", group="step2_dew", default=False, uiHint="analyzer_mode")
    _ensure("radio_wt", type="radio", group="step2_wt", default=True, uiHint="analyzer_mode")

    for m in re.finditer(r'(\w+)\.addItems\(\s*\[([^\]]+)\]\s*\)', src):
        var, items_raw = m.group(1), m.group(2)
        opts = re.findall(r'["\']([^"\']+)["\']', items_raw)
        key = var if var in fields else None
        if key is None and var.startswith("comboBox_"):
            key = var
            _ensure(key, type="select")
        if key and opts:
            fields[key]["options"] = opts
            fields[key]["type"] = "select"
            if fields[key]["default"] is None:
                fields[key]["default"] = opts[0]

    for m in re.finditer(r'(\w+)\.setCurrentText\(\s*["\']([^"\']*)["\']\s*\)', src):
        var, val = m.group(1), m.group(2)
        if var in fields:
            fields[var]["default"] = val

    for m in re.finditer(r'(\w+)\.setText\(\s*["\']([^"\']*)["\']\s*\)', src):
        var, val = m.group(1), m.group(2)
        if var in fields:
            fields[var]["default"] = val

    for m in re.finditer(r'(\w+)\.setValue\(\s*(-?\d+(?:\.\d+)?)\s*\)', src):
        var, val = m.group(1), m.group(2)
        if var in fields:
            fields[var]["default"] = float(val) if "." in val else int(val)
            fields[var]["type"] = "number"

    for m in re.finditer(r'(\w+)\.setChecked\(\s*(True|False)\s*\)', src):
        var, val = m.group(1), m.group(2) == "True"
        if var in fields:
            fields[var]["default"] = val
            fields[var]["type"] = "checkbox" if var.startswith("checkBox_") else "radio"

    keep_prefix = (
        "checkBox_",
        "comboBox_",
        "textEdit_",
        "lineEdit_",
        "spinBox_",
        "radioButton_",
        "radio_",
    )
    cleaned = {k: v for k, v in fields.items() if k.startswith(keep_prefix)}

    if "radio_dewetron" in cleaned:
        cleaned["radio_dewetron"]["uiHint"] = "analyzer_mode"
        cleaned["radio_dewetron"]["group"] = "step2_dew"
        if cleaned["radio_dewetron"].get("default") is None:
            cleaned["radio_dewetron"]["default"] = False
    if "radio_wt" in cleaned and cleaned["radio_wt"].get("default") is None:
        cleaned["radio_wt"]["default"] = True

    # 德威创导出字段虚拟控件（与过载/闪变一致）
    if "dew_export_fields" not in cleaned:
        cleaned["dew_export_fields"] = {
            "name": "dew_export_fields",
            "label": LABELS["dew_export_fields"],
            "type": "multi",
            "group": "step2_dew",
            "default": [
                "U1_tRMS",
                "U2_tRMS",
                "U3_tRMS",
                "I1_tRMS",
                "I2_tRMS",
                "I3_tRMS",
                "P1",
                "P2",
                "P3",
                "P_sum",
                "Q_sum",
                "S_sum",
                "Freq",
                "PF_sum",
            ],
            "options": [],
            "uiHint": "dew",
        }

    if "comboBox_DEW_MaxRefreshRate" in cleaned:
        cleaned["comboBox_DEW_MaxRefreshRate"]["options"] = [
            "Default",
            "100",
            "50",
            "20",
            "10",
            "5",
            "2",
            "1",
            "SYNC to HARMONIC",
        ]
        cleaned["comboBox_DEW_MaxRefreshRate"]["default"] = "SYNC to HARMONIC"
        cleaned["comboBox_DEW_MaxRefreshRate"]["uiHint"] = "dew"
        cleaned["comboBox_DEW_MaxRefreshRate"]["group"] = "step2_dew"

    for name in (
        "spinBox_DEW_DecimalPlaces",
        "checkBox_DEW_RealtimeWaveform",
        "checkBox_DEW_HarmonicEnabled",
        "spinBox_DEW_MaxHarmonicOrder",
        "spinBox_DEW_THDOrder",
        "comboBox_DEW_GroupingType",
        "checkBox_DEW_MultiFileStorage",
        "checkBox_DEW_SplitByTime",
        "spinBox_DEW_SplitTime",
        "checkBox_DEW_CreateSubfolder",
    ):
        if name in cleaned:
            cleaned[name]["group"] = "step2_dew"
            cleaned[name]["uiHint"] = "dew"

    # 谐波工况步默认勾选第一次
    if "checkBox_S3" in cleaned and cleaned["checkBox_S3"].get("default") is None:
        cleaned["checkBox_S3"]["default"] = True

    groups = [{"id": gid, "title": title} for gid, title, _ in GROUP_RULES]
    groups.append({"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"})
    groups.append({"id": "other", "title": "其它"})

    return {
        "testType": "harmonic",
        "title": "谐波电流",
        "version": 1,
        "groups": groups,
        "fields": sorted(cleaned.values(), key=lambda x: (x["group"], x["name"])),
        "jobFlags": {
            "auto_append": True,
            "auto_start": True,
            "wait_finish": True,
        },
    }


def _merge_wt_fields_from_overload(schema: dict) -> dict:
    src_path = OVERLOAD_SW if OVERLOAD_SW.is_file() else IOT_OVERLOAD
    if not src_path.is_file():
        return schema
    ov = json.loads(src_path.read_text(encoding="utf-8"))
    have = {f["name"] for f in schema.get("fields") or []}
    extra = []
    for f in ov.get("fields") or []:
        name = f.get("name") or ""
        group = f.get("group") or ""
        if name in have:
            continue
        if group in ("step2_wt_cfg",) or name.startswith(
            (
                "checkBox_Set",
                "comboBox_Sigm",
                "comboBox_Unit",
                "comboBox_Wiring",
                "comboBox_Replace",
                "comboBox_Project",
                "comboBox_Auto",
                "textEdit_Stop",
                "textEdit_Save",
                "textEdit_File",
                "checkBox_AutoName",
                "radio_S2_WT",
            )
        ):
            extra.append(dict(f))
            have.add(name)
    schema["fields"] = sorted(
        list(schema.get("fields") or []) + extra,
        key=lambda x: (x.get("group") or "", x["name"]),
    )
    # 复用过载 wtLayout（dew 树由 IOT load_test_schema 注入）
    if "wtLayout" in ov and "wtLayout" not in schema:
        schema["wtLayout"] = ov["wtLayout"]
    return schema


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iot-out", type=str, default="", help="额外写入 IOT 仓库路径")
    args = ap.parse_args(argv)
    schema = parse_dialog(DIALOG.read_text(encoding="utf-8"))
    schema = _merge_wt_fields_from_overload(schema)
    OUT_SW.parent.mkdir(parents=True, exist_ok=True)
    OUT_SW.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT_SW} fields={len(schema['fields'])}")
    if args.iot_out:
        p = Path(args.iot_out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
