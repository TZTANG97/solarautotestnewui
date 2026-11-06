# -*- coding: utf-8 -*-
"""
从 Dialog_thaiguodianyashanbian.py 生成电压闪变 IOT 字段 schema（不依赖 Qt 运行时）。

输出：
  - utils/iot_flicker_schema_data.json  （软件侧）
  - 可选拷贝到 IOT（见 --iot-out）

Usage:
  uv run python code_example/gen_flicker_iot_schema.py
  uv run python code_example/gen_flicker_iot_schema.py --iot-out E:/IOT/iot/app/services/solar_test_schemas/flicker_fields.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOG = ROOT / "Dialog_thaiguodianyashanbian.py"
OUT_SW = ROOT / "utils" / "iot_flicker_schema_data.json"
OVERLOAD_SW = ROOT / "utils" / "iot_overload_schema_data.json"

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
    "checkBox_S2": "启用步骤2 闪变",
    "comboBox_S2_WT": "WT 单相/三相",
    "comboBox_S2_WT3000_Setting": "WT ELEMENT",
    "comboBox_S2_PER_FLICK_COUNT": "每组闪变次数",
    "textEdit_S2_TIME": "首次闪变间隔",
    "comboBox_S2_TIME": "首次闪变间隔单位",
    "checkBox_S2_DEW": "启用德威创闪变",
    "checkBox_DEW_FlickerStandard": "闪变标准",
    "comboBox_DEW_WeightingType": "加权类型",
    "comboBox_DEW_MaxRefreshRate": "最大刷新率 (ms)",
    "textEdit_DEW_NominalVoltage": "额定电压(V)",
    "textEdit_DEW_ShortFlickerTime": "短时闪变(min)",
    "textEdit_DEW_LongFlickerTime": "长时闪变(min)",
    "textEdit_DEW_S2_TIME": "德威创首次间隔",
    "comboBox_DEW_S2_TIME": "德威创首次间隔单位",
    "comboBox_DEW_S2_PER_FLICK_COUNT": "德威创每组次数",
    "textEdit_DEW_ShortCircuitPower": "短路容量(MVA)",
    "checkBox_DEW_RollingCalc": "滚动计算",
    "checkBox_S3": "启用步骤3 DC 开关循环",
    "textEdit_S3_TIME": "持续时间",
    "comboBox_S3_TIME": "持续时间单位",
    "textEdit_S3_TIME_2": "闪变间隔",
    "comboBox_S3_TIME_2": "闪变间隔单位",
    "textEdit_S3_CYCLE_TIME": "循环次数",
    "checkBox_S4": "启用步骤4 判定结果",
    "comboBox_S4_WT3000_1": "判定结束条件",
    "comboBox_S4_WT3000_2": "是否保存图片",
    "comboBox_S4_WT3000_3": "图片保存位置",
    "checkBox_S4_DEW": "启用德威创判定/导出",
    "checkBox_S5": "启用步骤5 关机",
    "comboBox_S5_AC": "关机 AC",
    "checkBox_S5_DC1": "关机 DC1",
    "comboBox_S5_DC1": "关机 DC1 动作",
    "checkBox_S5_DC2": "关机 DC2",
    "comboBox_S5_DC2": "关机 DC2 动作",
    "checkBox_S5_DC3": "关机 DC3",
    "comboBox_S5_DC3": "关机 DC3 动作",
    "checkBox_S5_DC4": "关机 DC4",
    "comboBox_S5_DC4": "关机 DC4 动作",
    "radio_wt3000": "WT3000闪变",
    "radio_dewetron": "德威创",
    "radio_wt": "功率分析仪",
}

GROUP_RULES = [
    ("step1_ac", "① AC 电源", ("S1_AC", "checkBox_S1")),
    ("step1_dc", "① DC 电源", ("S1_DC",)),
    ("step1_time", "① 时序", ("S1_ACWait", "S1_TIME", "textEdit_S1_TIME", "comboBox_S1_TIME")),
    ("step2_wt", "② 闪变 / 功率分析仪", ("S2", "radio_S2", "radio_wt", "radio_wt3000")),
    ("step2_dew", "② 德威创", ("DEW", "radio_dewetron", "checkBox_S2_DEW")),
    ("step3_cycle", "③ DC 开关循环", ("S3",)),
    ("step4_judge", "④ 判定结果", ("S4",)),
    ("step5_off", "⑤ 关机设置", ("S5",)),
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

    for m in re.finditer(r'\.setObjectName\(\s*["\']([^"\']+)["\']\s*\)', src):
        name = m.group(1)
        if name.startswith(("pushButton_", "label_", "groupBox_", "step_indicator_")):
            continue
        if name in ("Dialog_thaiguodianyashanbian",):
            continue
        fields.setdefault(
            name,
            {
                "name": name,
                "label": LABELS.get(name, name),
                "type": _infer_type(name),
                "group": _group_for(name),
                "default": None,
                "options": [],
            },
        )

    for m in re.finditer(r'(\w+)\.addItems\(\s*\[([^\]]+)\]\s*\)', src):
        var, items_raw = m.group(1), m.group(2)
        opts = re.findall(r'["\']([^"\']+)["\']', items_raw)
        key = None
        if var in fields:
            key = var
        else:
            for n in fields:
                if n == var or n.endswith(var):
                    key = n
                    break
            if key is None and var.startswith("comboBox_"):
                key = var
                fields.setdefault(
                    key,
                    {
                        "name": key,
                        "label": LABELS.get(key, key),
                        "type": "select",
                        "group": _group_for(key),
                        "default": None,
                        "options": [],
                    },
                )
        if key and opts:
            fields[key]["options"] = opts
            fields[key]["type"] = "select"
            if fields[key]["default"] is None:
                fields[key]["default"] = opts[0]

    for m in re.finditer(r'(\w+)\.setText\(\s*["\']([^"\']*)["\']\s*\)', src):
        var, val = m.group(1), m.group(2)
        if var in fields:
            fields[var]["default"] = val
        elif var.startswith("textEdit_"):
            fields.setdefault(
                var,
                {
                    "name": var,
                    "label": LABELS.get(var, var),
                    "type": "text",
                    "group": _group_for(var),
                    "default": val,
                    "options": [],
                },
            )
            fields[var]["default"] = val

    for m in re.finditer(r'\(\s*["\'](textEdit_[^"\']+)["\']\s*,\s*["\']([^"\']*)["\']\s*\)', src):
        name, val = m.group(1), m.group(2)
        fields.setdefault(
            name,
            {
                "name": name,
                "label": LABELS.get(name, name),
                "type": "text",
                "group": _group_for(name),
                "default": val,
                "options": [],
            },
        )
        fields[name]["default"] = val

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

    # 线上表单统一用 radio_wt / radio_dewetron；桌面闪变 Dialog 为 radio_wt3000
    if "radio_wt3000" in cleaned and "radio_wt" not in cleaned:
        cleaned["radio_wt"] = {
            "name": "radio_wt",
            "label": LABELS["radio_wt"],
            "type": "radio",
            "group": "step2_wt",
            "default": True,
            "options": [],
            "uiHint": "analyzer_mode",
        }
    if "radio_dewetron" in cleaned:
        cleaned["radio_dewetron"]["uiHint"] = "analyzer_mode"
        cleaned["radio_dewetron"]["group"] = "step2_dew"
        if cleaned["radio_dewetron"].get("default") is None:
            cleaned["radio_dewetron"]["default"] = False
    if "radio_wt" in cleaned and cleaned["radio_wt"].get("default") is None:
        cleaned["radio_wt"]["default"] = True

    groups = [{"id": gid, "title": title} for gid, title, _ in GROUP_RULES]
    groups.append({"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"})
    groups.append({"id": "other", "title": "其它"})

    return {
        "testType": "flicker",
        "title": "电压闪变",
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
    """闪变 Dialog 未内嵌 WT3000 测量页；复用过载 schema 的 WT/德威创可填字段。"""
    if not OVERLOAD_SW.is_file():
        return schema
    ov = json.loads(OVERLOAD_SW.read_text(encoding="utf-8"))
    have = {f["name"] for f in schema.get("fields") or []}
    extra = []
    for f in ov.get("fields") or []:
        name = f.get("name") or ""
        group = f.get("group") or ""
        if name in have:
            continue
        if group in ("step2_wt_cfg", "step2_dew") or name.startswith(
            ("checkBox_Set", "comboBox_Sigm", "comboBox_Unit", "comboBox_Wiring",
             "comboBox_Replace", "comboBox_Project", "comboBox_Auto", "textEdit_Stop",
             "textEdit_Save", "textEdit_File", "checkBox_AutoName", "radio_S2_WT",
             "spinBox_DEW", "dew_export")
        ):
            # 避免覆盖闪变自有 DEW 闪变参数
            if name.startswith(("checkBox_DEW_Flicker", "comboBox_DEW_Weight", "textEdit_DEW_",
                                "comboBox_DEW_S2", "checkBox_DEW_Rolling", "checkBox_S2_DEW")):
                continue
            extra.append(dict(f))
            have.add(name)
    schema["fields"] = sorted(
        list(schema.get("fields") or []) + extra,
        key=lambda x: (x.get("group") or "", x["name"]),
    )
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
