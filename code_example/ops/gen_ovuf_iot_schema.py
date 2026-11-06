# -*- coding: utf-8 -*-
"""
从 Dialog_thaiguoqianya_pin.py 生成过欠压_过欠频 IOT 字段 schema。

输出：
  - utils/iot_ovuf_schema_data.json
  - 可选 --iot-out 写入 IOT ovuf_fields.json

Usage:
  uv run python code_example/gen_ovuf_iot_schema.py
  uv run python code_example/gen_ovuf_iot_schema.py --iot-out E:/IOT/iot/app/services/solar_test_schemas/ovuf_fields.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOG = ROOT / "Dialog_thaiguoqianya_pin.py"
OUT_SW = ROOT / "utils" / "iot_ovuf_schema_data.json"
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
    "checkBox_S2": "启用步骤2 功率分析仪",
    "radio_S2_WT3000": "WT3000",
    "radio_S2_WT1800": "WT1800",
    "radio_S2_WT1806E": "WT1806E",
    "radio_S2_WT5000": "WT5000",
    "comboBox_DEW_MaxRefreshRate": "最大刷新率 (ms)",
    "checkBox_DEW_RealtimeWaveform": "启用实时波形显示",
    "checkBox_S3": "启用过压扫描",
    "textEdit_S3_AC_VOLT_Start": "过压 电压起点(V)",
    "textEdit_S3_AC_VOLT_End": "过压 电压终点(V)",
    "textEdit_S3_AC_FR_Start": "过压 频率起点(Hz)",
    "textEdit_S3_AC_FR_End": "过压 频率终点(Hz)",
    "textEdit_S3_Step_Size": "过压 步长",
    "textEdit_S3_TIME": "过压 采集时长",
    "comboBox_S3_TIME": "过压 时长单位",
    "checkBox_S4": "启用欠压扫描",
    "textEdit_S4_AC_VOLT_Start": "欠压 电压起点(V)",
    "textEdit_S4_AC_VOLT_End": "欠压 电压终点(V)",
    "textEdit_S4_AC_FR_Start": "欠压 频率起点(Hz)",
    "textEdit_S4_AC_FR_End": "欠压 频率终点(Hz)",
    "textEdit_S4_Step_Size": "欠压 步长",
    "textEdit_S4_TIME": "欠压 采集时长",
    "comboBox_S4_TIME": "欠压 时长单位",
    "checkBox_S5": "启用过频扫描",
    "textEdit_S5_AC_VOLT_Start": "过频 电压起点(V)",
    "textEdit_S5_AC_VOLT_End": "过频 电压终点(V)",
    "textEdit_S5_AC_FR_Start": "过频 频率起点(Hz)",
    "textEdit_S5_AC_FR_End": "过频 频率终点(Hz)",
    "textEdit_S5_Step_Size": "过频 步长",
    "textEdit_S5_TIME": "过频 采集时长",
    "comboBox_S5_TIME": "过频 时长单位",
    "checkBox_S6": "启用欠频扫描",
    "textEdit_S6_AC_VOLT_Start": "欠频 电压起点(V)",
    "textEdit_S6_AC_VOLT_End": "欠频 电压终点(V)",
    "textEdit_S6_AC_FR_Start": "欠频 频率起点(Hz)",
    "textEdit_S6_AC_FR_End": "欠频 频率终点(Hz)",
    "textEdit_S6_Step_Size": "欠频 步长",
    "textEdit_S6_TIME": "欠频 采集时长",
    "comboBox_S6_TIME": "欠频 时长单位",
    "comboBox_Test_Project": "测试项目",
    "checkBox_AC_Test_L1": "测试相 L1",
    "checkBox_AC_Test_L2": "测试相 L2",
    "checkBox_AC_Test_L3": "测试相 L3",
    "checkBox_S7": "启用过频参数(页内)",
    "checkBox_S8": "启用欠频参数(页内)",
    "checkBox_S_End": "启用关机",
    "comboBox_S_End_AC": "关机 AC",
    "radio_wt3000": "WT3000模式",
    "radio_dewetron": "德威创",
    "radio_wt": "功率分析仪",
    "dew_export_fields": "导出字段选择",
}

GROUP_RULES = [
    ("step1_ac", "① AC 电源", ("S1_AC", "checkBox_S1")),
    ("step1_dc", "① DC 电源", ("S1_DC",)),
    ("step1_time", "① 时序", ("S1_ACWait", "textEdit_S1_TIME", "comboBox_S1_TIME")),
    ("step2_wt", "② 功率分析仪", ("S2", "radio_S2", "radio_wt", "radio_wt3000")),
    ("step2_dew", "② 德威创", ("DEW", "radio_dewetron")),
    ("step3_ov", "③ 过压扫描", ("S3",)),
    ("step4_uv", "④ 欠压扫描", ("S4",)),
    ("step5_of", "⑤ 过频扫描", ("S5",)),
    ("step6_uf", "⑥ 欠频扫描", ("S6",)),
    ("step7_phase", "⑦ 过欠频/相位", ("S7", "S8", "Test_Project", "AC_Test")),
    ("step8_off", "⑧ 关机设置", ("S_End",)),
]


def _group_for(name: str) -> str:
    if "S_End" in name:
        return "step8_off"
    if name.startswith(("checkBox_S8", "textEdit_S8", "comboBox_S8")) or name in (
        "comboBox_Test_Project",
        "checkBox_AC_Test_L1",
        "checkBox_AC_Test_L2",
        "checkBox_AC_Test_L3",
    ):
        return "step7_phase"
    if name.startswith(("checkBox_S7", "textEdit_S7", "comboBox_S7")):
        return "step7_phase"
    if name.startswith(("checkBox_S6", "textEdit_S6", "comboBox_S6")):
        return "step6_uf"
    if name.startswith(("checkBox_S5", "textEdit_S5", "comboBox_S5")):
        return "step5_of"
    if name.startswith(("checkBox_S4", "textEdit_S4", "comboBox_S4")):
        return "step4_uv"
    if name.startswith(("checkBox_S3", "textEdit_S3", "comboBox_S3")):
        return "step3_ov"
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
        if name in ("Dialog_thaiguoqianya_pin",):
            continue
        if "%" in name:
            continue
        _ensure(name)

    # _build_sweep_page 参数字符串里的控件名
    for m in re.finditer(r'["\']((?:checkBox|textEdit|comboBox)_[^"\']+)["\']', src):
        _ensure(m.group(1))

    for m in re.finditer(
        r'_make_(?:checkbox|combo|te|radio|input)\(\s*["\']([^"\']+)["\']',
        src,
    ):
        _ensure(m.group(1))

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

    # setHtml / setText 默认值
    for m in re.finditer(r'(\w+)\.set(?:Html|Text)\(\s*["\']([^"\']*)["\']\s*\)', src):
        var, val = m.group(1), m.group(2)
        if var in fields:
            fields[var]["default"] = val

    # _build_sweep_page 数字默认：textEdit..., 230 形式较难解析；补常用默认
    defaults = {
        "textEdit_S3_AC_VOLT_Start": "230",
        "textEdit_S3_AC_VOLT_End": "230",
        "textEdit_S3_AC_FR_Start": "50",
        "textEdit_S3_AC_FR_End": "50",
        "textEdit_S3_Step_Size": "5",
        "textEdit_S3_TIME": "3",
        "textEdit_S4_AC_VOLT_Start": "230",
        "textEdit_S4_AC_VOLT_End": "230",
        "textEdit_S4_AC_FR_Start": "50",
        "textEdit_S4_AC_FR_End": "50",
        "textEdit_S4_Step_Size": "5",
        "textEdit_S4_TIME": "3",
        "textEdit_S5_AC_VOLT_Start": "230",
        "textEdit_S5_AC_VOLT_End": "230",
        "textEdit_S5_AC_FR_Start": "50",
        "textEdit_S5_AC_FR_End": "50",
        "textEdit_S5_Step_Size": "5",
        "textEdit_S5_TIME": "3",
        "textEdit_S6_AC_VOLT_Start": "230",
        "textEdit_S6_AC_VOLT_End": "230",
        "textEdit_S6_AC_FR_Start": "50",
        "textEdit_S6_AC_FR_End": "50",
        "textEdit_S6_Step_Size": "5",
        "textEdit_S6_TIME": "3",
    }
    for k, v in defaults.items():
        if k in fields and fields[k].get("default") is None:
            fields[k]["default"] = v

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
        ]
        if cleaned["comboBox_DEW_MaxRefreshRate"].get("default") is None:
            cleaned["comboBox_DEW_MaxRefreshRate"]["default"] = "Default"
        cleaned["comboBox_DEW_MaxRefreshRate"]["uiHint"] = "dew"
        cleaned["comboBox_DEW_MaxRefreshRate"]["group"] = "step2_dew"

    groups = [{"id": gid, "title": title} for gid, title, _ in GROUP_RULES]
    groups.append({"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"})
    groups.append({"id": "other", "title": "其它"})

    return {
        "testType": "ovuf",
        "title": "过欠压_过欠频",
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
