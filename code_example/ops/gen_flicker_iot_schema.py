# -*- coding: utf-8 -*-
"""
从 Dialog_thaiguodianyashanbian.py 生成电压闪变 IOT 字段 schema（不依赖 Qt 运行时）。

输出：
  - utils/iot_flicker_schema_data.json  （软件侧）
  - 可选拷贝到 IOT（见 --iot-out）

Usage:
  uv run python code_example/ops/gen_flicker_iot_schema.py
  uv run python code_example/ops/gen_flicker_iot_schema.py --iot-out E:/IOT/iot/app/services/solar_test_schemas/flicker_fields.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIALOG = ROOT / "dialogs" / "Dialog_thaiguodianyashanbian.py"
OUT_SW = ROOT / "utils" / "iot_flicker_schema_data.json"

# 文案与 Dialog_thaiguodianyashanbian 上的 QLabel / 复选框原文一致
LABELS = {
    "checkBox_S1": "step1",
    "comboBox_S1_AC": "交流电压1",
    "comboBox_S1_AC_2": "接线",
    "textEdit_S1_AC_VOLT": "交流电压1(V)",
    "textEdit_S1_AC_VOLT_2": "交流电压2(V)",
    "textEdit_S1_AC_VOLT_3": "交流电压3(V)",
    "textEdit_S1_AC_FR": "频率(Hz)",
    "checkBox_S1_DC1": "直流电源1",
    "comboBox_S1_DC1": "直流电源1 开关",
    "textEdit_S1_DC1_VOLT": "直流电源1 Vmp(V)",
    "textEdit_S1_DC1_CURR": "直流电源1 Imp(A)",
    "textEdit_S1_DC1_Voc": "直流电源1 Voc(V)",
    "textEdit_S1_DC1_Isc": "直流电源1 Isc(A)",
    "textEdit_S1_DC1_PF": "直流电源1 功率(%)",
    "checkBox_S1_DC2": "直流电源2",
    "comboBox_S1_DC2": "直流电源2 开关",
    "textEdit_S1_DC2_VOLT": "直流电源2 Vmp(V)",
    "textEdit_S1_DC2_CURR": "直流电源2 Imp(A)",
    "textEdit_S1_DC2_Voc": "直流电源2 Voc(V)",
    "textEdit_S1_DC2_Isc": "直流电源2 Isc(A)",
    "textEdit_S1_DC2_PF": "直流电源2 功率(%)",
    "checkBox_S1_DC3": "直流电源3",
    "comboBox_S1_DC3": "直流电源3 开关",
    "textEdit_S1_DC3_VOLT": "直流电源3 Vmp(V)",
    "textEdit_S1_DC3_CURR": "直流电源3 Imp(A)",
    "textEdit_S1_DC3_Voc": "直流电源3 Voc(V)",
    "textEdit_S1_DC3_Isc": "直流电源3 Isc(A)",
    "textEdit_S1_DC3_PF": "直流电源3 功率(%)",
    "checkBox_S1_DC4": "直流电源4",
    "comboBox_S1_DC4": "直流电源4 开关",
    "textEdit_S1_DC4_VOLT": "直流电源4 Vmp(V)",
    "textEdit_S1_DC4_CURR": "直流电源4 Imp(A)",
    "textEdit_S1_DC4_Voc": "直流电源4 Voc(V)",
    "textEdit_S1_DC4_Isc": "直流电源4 Isc(A)",
    "textEdit_S1_DC4_PF": "直流电源4 功率(%)",
    "textEdit_S1_ACWaitTIME": "等待时间",
    "comboBox_S1_ACWaitTIME": "等待时间单位",
    "textEdit_S1_TIME": "启机时间",
    "comboBox_S1_TIME": "启机时间单位",
    "checkBox_S2": "step2",
    "comboBox_S2_WT": "WT3000",
    "comboBox_S2_WT3000_Setting": "ELEMENT",
    "comboBox_S2_PER_FLICK_COUNT": "每组闪变",
    "textEdit_S2_TIME": "首次闪变间隔",
    "comboBox_S2_TIME": "首次闪变间隔单位",
    "checkBox_S2_DEW": "step2",
    "checkBox_DEW_FlickerStandard": "闪变计算依照IEC61000-4-15: 2011",
    "comboBox_DEW_WeightingType": "加权类型",
    "comboBox_DEW_MaxRefreshRate": "最大刷新率",
    "textEdit_DEW_NominalVoltage": "标称电压",
    "textEdit_DEW_ShortFlickerTime": "短时闪变计算时间",
    "textEdit_DEW_LongFlickerTime": "长时闪变计算时间",
    "textEdit_DEW_S2_TIME": "首次闪变间隔",
    "comboBox_DEW_S2_TIME": "首次闪变间隔单位",
    "comboBox_DEW_S2_PER_FLICK_COUNT": "每组闪变次数",
    "textEdit_DEW_ShortCircuitPower": "短路视在功率",
    "checkBox_DEW_RollingCalc": "打开滚动计算",
    "spinBox_DEW_DecimalPlaces": "保留小数位数",
    "checkBox_DEW_RealtimeWaveform": "启用实时波形显示",
    "checkBox_DEW_ExportAbsTime": "CSV 增加绝对时间戳列（设备 ABS-TIME）",
    "checkBox_DEW_KeepOxygenDmd": "保留 Oxygen 原始 .dmd 录波到保存目录",
    "checkBox_S3": "step3",
    "textEdit_S3_TIME": "持续时间",
    "comboBox_S3_TIME": "持续时间单位",
    "textEdit_S3_TIME_2": "闪变间隔",
    "comboBox_S3_TIME_2": "闪变间隔单位",
    "textEdit_S3_CYCLE_TIME": "循环次数",
    "checkBox_S4": "step4",
    "comboBox_S4_WT3000_1": "判断是结束",
    "comboBox_S4_WT3000_2": "保存图片",
    "comboBox_S4_WT3000_3": "保存至本地",
    "checkBox_S4_DEW": "step4",
    "checkBox_S5": "step5",
    "comboBox_S5_AC": "交流电源",
    "checkBox_S5_DC1": "直流电源1",
    "comboBox_S5_DC1": "直流电源1 开关",
    "checkBox_S5_DC2": "直流电源2",
    "comboBox_S5_DC2": "直流电源2 开关",
    "checkBox_S5_DC3": "直流电源3",
    "comboBox_S5_DC3": "直流电源3 开关",
    "checkBox_S5_DC4": "直流电源4",
    "comboBox_S5_DC4": "直流电源4 开关",
    "radio_wt3000": "WT3000闪变",
    "radio_dewetron": "德威创模式",
    "radio_wt": "WT3000闪变",
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

    _apply_loop_fields(cleaned)

    groups = [{"id": gid, "title": title} for gid, title, _ in GROUP_RULES]
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


def _blank(name: str, *, typ: str, group: str, default, options=None) -> dict:
    return {
        "name": name,
        "label": LABELS.get(name, name),
        "type": typ,
        "group": group,
        "default": default,
        "options": list(options or []),
    }


def _apply_loop_fields(cleaned: dict) -> None:
    """Dialog 用循环 setObjectName(变量)，静态扫描扫不到第一次/第二次状态和关机直流。"""
    on_off = ["开启", "关闭"]
    off_on = ["关闭", "开启"]
    for i in range(1, 5):
        checked = i == 1
        cleaned[f"checkBox_S3_DC{i}"] = _blank(
            f"checkBox_S3_DC{i}", typ="checkbox", group="step3_cycle", default=checked
        )
        cleaned[f"checkBox_S3_DC{i}"]["label"] = f"第一次状态 直流电源{i}"
        cleaned[f"comboBox_S3_DC{i}"] = _blank(
            f"comboBox_S3_DC{i}",
            typ="select",
            group="step3_cycle",
            default="关闭",
            options=off_on,
        )
        cleaned[f"comboBox_S3_DC{i}"]["label"] = f"第一次状态 直流电源{i} 开关"
        cleaned[f"checkBox_S3_DC{i}_2"] = _blank(
            f"checkBox_S3_DC{i}_2", typ="checkbox", group="step3_cycle", default=checked
        )
        cleaned[f"checkBox_S3_DC{i}_2"]["label"] = f"第二次状态 直流电源{i}"
        cleaned[f"comboBox_S3_DC{i}_2"] = _blank(
            f"comboBox_S3_DC{i}_2",
            typ="select",
            group="step3_cycle",
            default="开启",
            options=on_off,
        )
        cleaned[f"comboBox_S3_DC{i}_2"]["label"] = f"第二次状态 直流电源{i} 开关"
        cleaned[f"checkBox_S5_DC{i}"] = _blank(
            f"checkBox_S5_DC{i}", typ="checkbox", group="step5_off", default=checked
        )
        cleaned[f"comboBox_S5_DC{i}"] = _blank(
            f"comboBox_S5_DC{i}",
            typ="select",
            group="step5_off",
            default="关闭",
            options=off_on,
        )
    if "spinBox_DEW_DecimalPlaces" in cleaned:
        cleaned["spinBox_DEW_DecimalPlaces"]["type"] = "number"
        cleaned["spinBox_DEW_DecimalPlaces"]["default"] = 3
    rate = cleaned.get("comboBox_DEW_MaxRefreshRate")
    if rate is not None and not rate.get("options"):
        rate["options"] = ["Default", "1000", "500", "200", "100", "50", "20", "10", "5", "2", "1"]
        rate["default"] = "Default"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iot-out", type=str, default="", help="额外写入 IOT 仓库路径")
    args = ap.parse_args(argv)
    schema = parse_dialog(DIALOG.read_text(encoding="utf-8"))
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
