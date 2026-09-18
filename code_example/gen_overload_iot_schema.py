# -*- coding: utf-8 -*-
"""
从 Dialog_thaioverloads.py 生成过载 IOT 字段 schema（不依赖 Qt 运行时）。

输出：
  - utils/iot_overload_schema_data.json  （软件侧）
  - 可选拷贝到 IOT（见 --iot-out）

Usage:
  uv run python code_example/gen_overload_iot_schema.py
  uv run python code_example/gen_overload_iot_schema.py --iot-out E:/IOT/iot/app/services/solar_test_schemas/overload_fields.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOG = ROOT / "Dialog_thaioverloads.py"
OUT_SW = ROOT / "utils" / "iot_overload_schema_data.json"

# objectName → 中文标签（手维，补全 UI 语义；未知则回退 objectName）
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
    "checkBox_S2": "启用步骤2 功率分析仪",
    "radio_S2_WT3000": "选用 WT3000",
    "radio_S2_WT1800": "选用 WT1800",
    "radio_S2_WT1806E": "选用 WT1806E",
    "radio_S2_WT5000": "选用 WT5000",
    "checkBox_S2_WT3000": "WT3000(旧勾选)",
    "checkBox_S2_WT1800": "WT1800(旧勾选)",
    "checkBox_S2_WT1806E": "WT1806E(旧勾选)",
    "checkBox_S2_WT5000": "WT5000(旧勾选)",
    "checkBox_S3": "启用步骤3 过载测试",
    "textEdit_S3_TIME_2": "过载保持时间",
    "comboBox_S3_TIME_2": "过载保持时间单位",
    "comboBox_S3_record_mode": "录波方式",
    "checkBox_S5": "启用步骤4 关机",
    "comboBox_S5_AC": "关机 AC",
    "checkBox_S5_DC1": "关机 DC1",
    "comboBox_S5_DC1": "关机 DC1 动作",
    "checkBox_S5_DC2": "关机 DC2",
    "comboBox_S5_DC2": "关机 DC2 动作",
    "checkBox_S5_DC3": "关机 DC3",
    "comboBox_S5_DC3": "关机 DC3 动作",
    "checkBox_S5_DC4": "关机 DC4",
    "comboBox_S5_DC4": "关机 DC4 动作",
}

GROUP_RULES = [
    ("step1_ac", "① AC 电源", ("S1_AC", "checkBox_S1")),
    ("step1_dc", "① DC 电源", ("S1_DC",)),
    ("step1_time", "① 时序", ("S1_ACWait", "S1_TIME", "textEdit_S1_TIME", "comboBox_S1_TIME")),
    ("step2_wt", "② 功率分析仪", ("S2",)),
    ("step3_ov", "③ 过载测试", ("S3",)),
    ("step4_off", "④ 关机设置", ("S5",)),
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
    if name.startswith("radioButton_"):
        return "radio"
    return "text"


def parse_dialog(src: str) -> dict:
    """从手写 Dialog 抽出 objectName + 默认值/选项。"""
    fields: dict[str, dict] = {}

    # setObjectName("xxx")
    for m in re.finditer(r'\.setObjectName\(\s*["\']([^"\']+)["\']\s*\)', src):
        name = m.group(1)
        if name.startswith(("pushButton_", "label_", "groupBox_", "step_indicator_")):
            continue
        if name in ("Dialog_thaioverloads",):
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

    # addItems([...])
    for m in re.finditer(
        r'(\w+)\.addItems\(\s*\[([^\]]+)\]\s*\)',
        src,
    ):
        var, items_raw = m.group(1), m.group(2)
        opts = re.findall(r'["\']([^"\']+)["\']', items_raw)
        # map var to objectName if same attribute
        key = None
        if var in fields:
            key = var
        else:
            # self.comboBox_xxx
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

    # setText("...")
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

    # tuple defaults ("textEdit_...", "220")
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

    # setChecked(True/False)
    for m in re.finditer(r'(\w+)\.setChecked\(\s*(True|False)\s*\)', src):
        var, val = m.group(1), m.group(2) == "True"
        if var in fields:
            fields[var]["default"] = val
            fields[var]["type"] = "checkbox"

    # filter: only interactive
    keep_prefix = (
        "checkBox_",
        "comboBox_",
        "textEdit_",
        "lineEdit_",
        "spinBox_",
        "radioButton_",
        "radio_",
    )
    cleaned = {
        k: v
        for k, v in fields.items()
        if k.startswith(keep_prefix)
    }

    groups = []
    for gid, title, _ in GROUP_RULES:
        groups.append({"id": gid, "title": title})
    groups.append({"id": "other", "title": "其它"})

    return {
        "testType": "overload",
        "title": "过载能力测试",
        "version": 1,
        "groups": groups,
        "fields": sorted(cleaned.values(), key=lambda x: (x["group"], x["name"])),
        "jobFlags": {
            "auto_append": True,
            "auto_start": True,
            "wait_finish": True,
        },
    }


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
