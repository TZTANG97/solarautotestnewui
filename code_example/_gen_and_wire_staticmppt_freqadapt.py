# -*- coding: utf-8 -*-
"""生成并接入：静态MPPT测试 + 频率适应性。"""
from __future__ import annotations

import json
import re
from pathlib import Path

SOLAR = Path(r"E:/solarautotestnewui")
IOT = Path(r"E:/IOT/iot")
OVERLOAD_SW = SOLAR / "utils" / "iot_overload_schema_data.json"
IOT_OVERLOAD = IOT / "app/services/solar_test_schemas/overload_fields.json"


def _infer_type(name: str) -> str:
    if name.startswith("checkBox_"):
        return "checkbox"
    if name.startswith("comboBox_"):
        return "select"
    if name.startswith(("textEdit_", "lineEdit_")):
        return "text"
    if name.startswith(("spinBox_", "doubleSpinBox_")):
        return "number"
    if name.startswith(("radioButton_", "radio_")):
        return "radio"
    return "text"


def _merge_wt(schema: dict) -> dict:
    src = OVERLOAD_SW if OVERLOAD_SW.is_file() else IOT_OVERLOAD
    if not src.is_file():
        return schema
    ov = json.loads(src.read_text(encoding="utf-8"))
    have = {f["name"] for f in schema.get("fields") or []}
    extra = []
    for f in ov.get("fields") or []:
        name = f.get("name") or ""
        group = f.get("group") or ""
        if name in have:
            continue
        if group == "step2_wt_cfg" or name.startswith(
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


def _parse_common(src: str, *, dialog_name: str, group_fn, labels: dict, extras=None) -> dict:
    fields: dict[str, dict] = {}

    def _ensure(name: str, **overrides):
        if not name or "%" in name:
            return
        base = {
            "name": name,
            "label": labels.get(name, name),
            "type": _infer_type(name),
            "group": group_fn(name),
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
        if name == dialog_name:
            continue
        _ensure(name)

    for m in re.finditer(r'["\']((?:checkBox|textEdit|comboBox)_[^"\']+)["\']', src):
        _ensure(m.group(1))

    if extras:
        extras(_ensure)

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

    for m in re.finditer(r'(\w+)\.set(?:Html|Text|PlainText|CurrentText)\(\s*["\']([^"\']*)["\']\s*\)', src):
        var, val = m.group(1), m.group(2)
        if var in fields and fields[var].get("default") is None:
            fields[var]["default"] = val

    for m in re.finditer(r'(\w+)\.setChecked\(\s*(True|False)\s*\)', src):
        var, val = m.group(1), m.group(2) == "True"
        if var in fields:
            fields[var]["default"] = val
            fields[var]["type"] = "checkbox" if var.startswith("checkBox_") else "radio"

    keep = ("checkBox_", "comboBox_", "textEdit_", "lineEdit_", "spinBox_", "radioButton_", "radio_")
    cleaned = {k: v for k, v in fields.items() if k.startswith(keep)}
    if "radio_dewetron" in cleaned:
        cleaned["radio_dewetron"]["uiHint"] = "analyzer_mode"
        cleaned["radio_dewetron"]["group"] = "step2_dew"
        cleaned["radio_dewetron"].setdefault("default", False)
    if "radio_wt" in cleaned:
        cleaned["radio_wt"].setdefault("default", True)
    if "dew_export_fields" not in cleaned:
        cleaned["dew_export_fields"] = {
            "name": "dew_export_fields",
            "label": "导出字段选择",
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
        cleaned["comboBox_DEW_MaxRefreshRate"].setdefault("default", "Default")
        cleaned["comboBox_DEW_MaxRefreshRate"]["uiHint"] = "dew"
        cleaned["comboBox_DEW_MaxRefreshRate"]["group"] = "step2_dew"
    return cleaned


def gen_staticmppt() -> dict:
    src = (SOLAR / "Dialog_thaistaticmppttest.py").read_text(encoding="utf-8")
    labels = {
        "checkBox_S1": "启用步骤1 AC/DC",
        "checkBox_Analyzer": "启用分析仪步骤",
        "checkBox_S2": "启用测试功率段",
        "checkBox_S3": "启用MPPT时长",
        "textEdit_S3_TOTAL_H": "MPPT总时长(时)",
        "textEdit_S3_TOTAL_M": "MPPT总时长(分)",
        "textEdit_S3_PER_H": "单次时长(时)",
        "textEdit_S3_PER_M": "单次时长(分)",
        "checkBox_S_End": "启用关机",
        "comboBox_S_End_AC": "关机 AC",
        "radio_wt": "功率分析仪",
        "radio_dewetron": "德威创",
        "dew_export_fields": "导出字段选择",
    }

    def group_fn(name: str) -> str:
        if "S_End" in name:
            return "step5_off"
        if name.startswith(("checkBox_S3", "textEdit_S3", "comboBox_S3")) or "record_mode" in name:
            return "step4_mppt"
        if name.startswith(("checkBox_S2", "textEdit_S2", "comboBox_S2")):
            return "step3_power"
        if "Analyzer" in name or name.startswith(("radio_S2", "radio_wt", "radio_dewetron", "DEW", "comboBox_DEW", "checkBox_DEW", "spinBox_DEW")):
            return "step2_wt" if "DEW" not in name and "dewetron" not in name else "step2_dew"
        if "DEW" in name or "dewetron" in name:
            return "step2_dew"
        if "S1" in name or name.startswith(("radio_Mode",)):
            return "step1_ac" if "DC" not in name else "step1_dc"
        return "other"

    def extras(ensure):
        for pct in (100, 75, 50, 30, 25, 20, 10, 5):
            ensure(f"checkBox_S2_Pn_{pct}", label=f"功率段 {pct}%", default=(pct == 100))

    cleaned = _parse_common(
        src,
        dialog_name="Dialog_thaistaticmppttest",
        group_fn=group_fn,
        labels=labels,
        extras=extras,
    )
    # analyzer enable
    if "checkBox_Analyzer" in cleaned:
        cleaned["checkBox_Analyzer"]["group"] = "step2_wt"
    groups = [
        {"id": "step1_ac", "title": "① AC 电源"},
        {"id": "step1_dc", "title": "① DC 电源"},
        {"id": "step2_wt", "title": "② 功率分析仪"},
        {"id": "step2_dew", "title": "② 德威创"},
        {"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"},
        {"id": "step3_power", "title": "③ 测试功率段"},
        {"id": "step4_mppt", "title": "④ MPPT测试"},
        {"id": "step5_off", "title": "⑤ 关机设置"},
        {"id": "other", "title": "其它"},
    ]
    schema = {
        "testType": "staticmppt",
        "title": "静态MPPT测试",
        "version": 1,
        "groups": groups,
        "fields": sorted(cleaned.values(), key=lambda x: (x["group"], x["name"])),
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def gen_frequencyadaptability() -> dict:
    src = (SOLAR / "Dialog_thaifrequencyadaptability.py").read_text(encoding="utf-8")
    labels = {
        "checkBox_S1": "启用步骤1 AC/DC",
        "checkBox_S2": "启用步骤2 功率分析仪",
        "checkBox_guopin_page": "启用过频设置",
        "checkBox_qianpin_page": "启用欠频设置",
        "checkBox_S_End": "启用关机",
        "comboBox_S_End_AC": "关机 AC",
        "radio_wt": "功率分析仪",
        "radio_dewetron": "德威创",
        "dew_export_fields": "导出字段选择",
    }

    def group_fn(name: str) -> str:
        if "S_End" in name:
            return "step5_off"
        if "qianpin" in name or re.match(r".*_S(1[2-9]|20)_", name) or re.match(
            r"^(?:checkBox|textEdit|comboBox)_S(1[2-9]|20)", name
        ):
            return "step4_uf"
        if "guopin" in name or re.match(r".*_S([3-9]|1[01])_", name) or re.match(
            r"^(?:checkBox|textEdit|comboBox)_S([3-9]|1[01])", name
        ):
            return "step3_of"
        if "DEW" in name or "dewetron" in name:
            return "step2_dew"
        if name.startswith(("checkBox_S2", "radio_S2", "radio_wt", "radio_wt3000")):
            return "step2_wt"
        if "S1" in name:
            return "step1_dc" if "DC" in name else "step1_ac"
        return "other"

    def extras(ensure):
        # 过频 S3-S11 / 欠频 S12-S20
        for i in range(3, 12):
            ensure(f"checkBox_S{i}", label=f"启用过频{i-2}", default=(i == 3))
            ensure(f"checkBox_S{i}_RATE", label=f"过频{i-2} 更新率", default=True)
            ensure(f"textEdit_S{i}_freq_start_guopin", label=f"过频{i-2} 起点(Hz)")
            ensure(f"textEdit_S{i}_freq_end_guopin", label=f"过频{i-2} 终点(Hz)")
            ensure(f"textEdit_S{i}_test_duration_guopin", label=f"过频{i-2} 时长")
            ensure(
                f"comboBox_S{i}_test_time_unit_guopin",
                label=f"过频{i-2} 单位",
                type="select",
                options=["秒", "毫秒", "分钟"],
                default="秒",
            )
        for i in range(12, 21):
            ensure(f"checkBox_S{i}", label=f"启用欠频{i-11}", default=False)
            ensure(f"checkBox_S{i}_RATE", label=f"欠频{i-11} 更新率", default=True)
            ensure(f"textEdit_S{i}_freq_start_qianpin", label=f"欠频{i-11} 起点(Hz)")
            ensure(f"textEdit_S{i}_freq_end_qianpin", label=f"欠频{i-11} 终点(Hz)")
            ensure(f"textEdit_S{i}_test_duration_qianpin", label=f"欠频{i-11} 时长")
            ensure(
                f"comboBox_S{i}_test_time_unit_qianpin",
                label=f"欠频{i-11} 单位",
                type="select",
                options=["秒", "毫秒", "分钟"],
                default="秒",
            )

    cleaned = _parse_common(
        src,
        dialog_name="Dialog_thaifrequencyadaptability",
        group_fn=group_fn,
        labels=labels,
        extras=extras,
    )
    groups = [
        {"id": "step1_ac", "title": "① AC 电源"},
        {"id": "step1_dc", "title": "① DC 电源"},
        {"id": "step2_wt", "title": "② 功率分析仪"},
        {"id": "step2_dew", "title": "② 德威创"},
        {"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"},
        {"id": "step3_of", "title": "③ 过频设置"},
        {"id": "step4_uf", "title": "④ 欠频设置"},
        {"id": "step5_off", "title": "⑤ 关机设置"},
        {"id": "other", "title": "其它"},
    ]
    schema = {
        "testType": "frequencyadaptability",
        "title": "频率适应性",
        "version": 1,
        "groups": groups,
        "fields": sorted(cleaned.values(), key=lambda x: (x["group"], x["name"])),
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def write_schemas() -> None:
    for schema, sw_name, iot_name in (
        (gen_staticmppt(), "iot_staticmppt_schema_data.json", "staticmppt_fields.json"),
        (gen_frequencyadaptability(), "iot_frequencyadaptability_schema_data.json", "frequencyadaptability_fields.json"),
    ):
        sw = SOLAR / "utils" / sw_name
        iot = IOT / "app/services/solar_test_schemas" / iot_name
        text = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
        sw.write_text(text, encoding="utf-8")
        iot.write_text(text, encoding="utf-8")
        print(f"wrote {sw.name} / {iot.name} fields={len(schema['fields'])}")


def _repl(path: Path, old: str, new: str, *, label: str) -> None:
    t = path.read_text(encoding="utf-8")
    if old not in t:
        raise SystemExit(f"missing in {path.name}: {label}\n{old[:120]!r}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    print(f"ok {path.name} ({label})")


def wire() -> None:
    # schema init
    p = IOT / "app/services/solar_test_schemas/__init__.py"
    t = p.read_text(encoding="utf-8")
    if "staticmppt_fields.json" not in t:
        old = '''        "过欠频稳定性": "guoqianpin_immun_fields.json",
    }
'''
        new = '''        "过欠频稳定性": "guoqianpin_immun_fields.json",
        "staticmppt": "staticmppt_fields.json",
        "staticMPPTtest": "staticmppt_fields.json",
        "static_mppt": "staticmppt_fields.json",
        "静态MPPT测试": "staticmppt_fields.json",
        "静态MPPT": "staticmppt_fields.json",
        "frequencyadaptability": "frequencyadaptability_fields.json",
        "freqadapt": "frequencyadaptability_fields.json",
        "频率适应性": "frequencyadaptability_fields.json",
    }
'''
        t = t.replace(old, new, 1)
        t = t.replace(
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun"]',
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun", "staticmppt", "frequencyadaptability"]',
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok schema init")
    else:
        print("schema init already")

    # catalog
    p = IOT / "app/services/solar_blockly_catalog.py"
    t = p.read_text(encoding="utf-8")
    if '"staticmppt":' not in t:
        marker = '''                "blockly_name": "solar_guoqianpin_immun_s4",
                "com_name": "巴西过欠频稳定性步骤4 关机",
                "colour": 270,
            },
        ),
    },
}
'''
        insert = '''                "blockly_name": "solar_guoqianpin_immun_s4",
                "com_name": "巴西过欠频稳定性步骤4 关机",
                "colour": 270,
            },
        ),
    },
    "staticmppt": {
        "com_name": "静态MPPT半自动",
        "blockly_name": "solar_staticmppt",
        "label": "静态MPPT测试",
        "colour": 280,
        "aliases": (
            "staticmppt",
            "staticMPPTtest",
            "static_mppt",
            "静态MPPT测试",
            "静态MPPT",
            "静态MPPT半自动",
        ),
        "steps": (
            {"blockly_name": "solar_staticmppt_s1", "com_name": "静态MPPT步骤1 AC/DC", "colour": 280},
            {"blockly_name": "solar_staticmppt_s2", "com_name": "静态MPPT步骤2 分析仪", "colour": 290},
            {"blockly_name": "solar_staticmppt_s3", "com_name": "静态MPPT步骤3 功率与时长", "colour": 300},
            {"blockly_name": "solar_staticmppt_s4", "com_name": "静态MPPT步骤4 关机", "colour": 310},
        ),
    },
    "frequencyadaptability": {
        "com_name": "频率适应性半自动",
        "blockly_name": "solar_frequencyadaptability",
        "label": "频率适应性",
        "colour": 320,
        "aliases": (
            "frequencyadaptability",
            "freqadapt",
            "频率适应性",
            "频率适应性半自动",
        ),
        "steps": (
            {"blockly_name": "solar_frequencyadaptability_s1", "com_name": "频率适应性步骤1 AC/DC", "colour": 320},
            {"blockly_name": "solar_frequencyadaptability_s2", "com_name": "频率适应性步骤2 分析仪", "colour": 330},
            {"blockly_name": "solar_frequencyadaptability_s3", "com_name": "频率适应性步骤3 过欠频", "colour": 340},
            {"blockly_name": "solar_frequencyadaptability_s4", "com_name": "频率适应性步骤4 关机", "colour": 350},
        ),
    },
}
'''
        if marker not in t:
            raise SystemExit("catalog immun tail missing")
        p.write_text(t.replace(marker, insert, 1), encoding="utf-8")
        print("ok catalog")
    else:
        print("catalog already")

    # detail
    p = IOT / "app/services/solar_blockly_detail.py"
    t = p.read_text(encoding="utf-8")
    if "solar_staticmppt_s1" not in t:
        old = '''    "solar_guoqianpin_immun_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
        new = '''    "solar_guoqianpin_immun_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
    # ── 静态MPPT ──
    "solar_staticmppt_s1": (
        "checkBox_S1",
        "comboBox_S1_AC",
        "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT",
        "textEdit_S1_AC_VOLT_2",
        "textEdit_S1_AC_VOLT_3",
        "textEdit_S1_AC_FR",
        "comboBox_S1_Vdc_Count",
        "checkBox_S1_DC1",
        "textEdit_S1_ACWaitTIME",
        "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME",
        "comboBox_S1_TIME",
    ),
    "solar_staticmppt_s2": (
        "checkBox_Analyzer",
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "comboBox_DEW_MaxRefreshRate",
    ),
    "solar_staticmppt_s3": (
        "checkBox_S2",
        "checkBox_S2_Pn_100",
        "checkBox_S2_Pn_75",
        "checkBox_S2_Pn_50",
        "checkBox_S3",
        "textEdit_S3_TOTAL_H",
        "textEdit_S3_TOTAL_M",
        "textEdit_S3_PER_H",
        "textEdit_S3_PER_M",
    ),
    "solar_staticmppt_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
        "checkBox_S_End_DC",
    ),
    # ── 频率适应性 ──
    "solar_frequencyadaptability_s1": (
        "checkBox_S1",
        "comboBox_S1_AC",
        "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT",
        "textEdit_S1_AC_VOLT_2",
        "textEdit_S1_AC_VOLT_3",
        "textEdit_S1_AC_FR",
        "checkBox_S1_DC1",
        "textEdit_S1_ACWaitTIME",
        "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME",
        "comboBox_S1_TIME",
    ),
    "solar_frequencyadaptability_s2": (
        "checkBox_S2",
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "comboBox_DEW_MaxRefreshRate",
    ),
    "solar_frequencyadaptability_s3": (
        "checkBox_guopin_page",
        "checkBox_S3",
        "textEdit_S3_freq_start_guopin",
        "textEdit_S3_freq_end_guopin",
        "checkBox_qianpin_page",
        "checkBox_S12",
        "textEdit_S12_freq_start_qianpin",
        "textEdit_S12_freq_end_qianpin",
    ),
    "solar_frequencyadaptability_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
        if old not in t:
            raise SystemExit("detail immun_s4 missing")
        p.write_text(t.replace(old, new, 1), encoding="utf-8")
        print("ok detail")
    else:
        print("detail already")

    _repl(
        IOT / "app/services/solar_experiment_service.py",
        '''            "voltprotect10min",
            "guoqianpin_immun",
        ):''',
        '''            "voltprotect10min",
            "guoqianpin_immun",
            "staticmppt",
            "frequencyadaptability",
        ):''',
        label="experiment",
    )

    # frontend labels
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  过欠频稳定性: '巴西过欠频稳定性',
}
""",
        """  过欠频稳定性: '巴西过欠频稳定性',
  staticmppt: '静态MPPT测试',
  staticMPPTtest: '静态MPPT测试',
  static_mppt: '静态MPPT测试',
  静态MPPT测试: '静态MPPT测试',
  静态MPPT: '静态MPPT测试',
  frequencyadaptability: '频率适应性',
  freqadapt: '频率适应性',
  频率适应性: '频率适应性',
}
""",
        label="labels map",
    )
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  { value: 'guoqianpin_immun', label: '巴西过欠频稳定性' },
] as const
""",
        """  { value: 'guoqianpin_immun', label: '巴西过欠频稳定性' },
  { value: 'staticmppt', label: '静态MPPT测试' },
  { value: 'frequencyadaptability', label: '频率适应性' },
] as const
""",
        label="labels options",
    )
    _repl(
        IOT / "frontend/src/utils/solarBlockly.ts",
        """  { type: 'solar_guoqianpin_immun', message0: '巴西过欠频稳定性半自动%1', arg: 'solar_guoqianpin_immun', colour: 240 },
] as const
""",
        """  { type: 'solar_guoqianpin_immun', message0: '巴西过欠频稳定性半自动%1', arg: 'solar_guoqianpin_immun', colour: 240 },
  { type: 'solar_staticmppt_s1', message0: '静态MPPT步骤1 AC/DC%1', arg: 'solar_staticmppt_s1', colour: 280 },
  { type: 'solar_staticmppt_s2', message0: '静态MPPT步骤2 分析仪%1', arg: 'solar_staticmppt_s2', colour: 290 },
  { type: 'solar_staticmppt_s3', message0: '静态MPPT步骤3 功率与时长%1', arg: 'solar_staticmppt_s3', colour: 300 },
  { type: 'solar_staticmppt_s4', message0: '静态MPPT步骤4 关机%1', arg: 'solar_staticmppt_s4', colour: 310 },
  { type: 'solar_staticmppt', message0: '静态MPPT半自动%1', arg: 'solar_staticmppt', colour: 280 },
  { type: 'solar_frequencyadaptability_s1', message0: '频率适应性步骤1 AC/DC%1', arg: 'solar_frequencyadaptability_s1', colour: 320 },
  { type: 'solar_frequencyadaptability_s2', message0: '频率适应性步骤2 分析仪%1', arg: 'solar_frequencyadaptability_s2', colour: 330 },
  { type: 'solar_frequencyadaptability_s3', message0: '频率适应性步骤3 过欠频%1', arg: 'solar_frequencyadaptability_s3', colour: 340 },
  { type: 'solar_frequencyadaptability_s4', message0: '频率适应性步骤4 关机%1', arg: 'solar_frequencyadaptability_s4', colour: 350 },
  { type: 'solar_frequencyadaptability', message0: '频率适应性半自动%1', arg: 'solar_frequencyadaptability', colour: 320 },
] as const
""",
        label="blockly",
    )
    _repl(
        IOT / "frontend/src/views/solar/SolarOrderCreate.vue",
        """    | 'voltprotect10min'
    | 'guoqianpin_immun',
""",
        """    | 'voltprotect10min'
    | 'guoqianpin_immun'
    | 'staticmppt'
    | 'frequencyadaptability',
""",
        label="order create",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  'voltprotect10min',
  'guoqianpin_immun',
])
""",
        """  'voltprotect10min',
  'guoqianpin_immun',
  'staticmppt',
  'frequencyadaptability',
])
""",
        label="params types",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  if (
    blob.includes('solar_voltprotect10min') ||
    blob.includes('voltprotect10min') ||
    blob.includes('10min过压保护') ||
    blob.includes('过压保护10min')
  ) {
    return 'voltprotect10min'
  }
""",
        """  if (
    blob.includes('solar_staticmppt') ||
    blob.includes('staticmppt') ||
    blob.includes('静态MPPT')
  ) {
    return 'staticmppt'
  }
  if (
    blob.includes('solar_frequencyadaptability') ||
    blob.includes('frequencyadaptability') ||
    blob.includes('频率适应性') ||
    blob.includes('freqadapt')
  ) {
    return 'frequencyadaptability'
  }
  if (
    blob.includes('solar_voltprotect10min') ||
    blob.includes('voltprotect10min') ||
    blob.includes('10min过压保护') ||
    blob.includes('过压保护10min')
  ) {
    return 'voltprotect10min'
  }
""",
        label="detect",
    )

    # JobList - append after immun
    p = IOT / "frontend/src/views/solar/SolarJobList.vue"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            '<el-option label="巴西过欠频稳定性" value="guoqianpin_immun" />\n          </el-select>',
            '<el-option label="巴西过欠频稳定性" value="guoqianpin_immun" />\n            <el-option label="静态MPPT测试" value="staticmppt" />\n            <el-option label="频率适应性" value="frequencyadaptability" />\n          </el-select>',
        ),
        (
            '<el-option label="巴西过欠频稳定性自动开跑" value="guoqianpin_immun_autostart" />\n          </el-select>',
            '<el-option label="巴西过欠频稳定性自动开跑" value="guoqianpin_immun_autostart" />\n            <el-option label="静态MPPT默认（只追加）" value="staticmppt_default" />\n            <el-option label="静态MPPT自动开跑" value="staticmppt_autostart" />\n            <el-option label="频率适应性默认（只追加）" value="frequencyadaptability_default" />\n            <el-option label="频率适应性自动开跑" value="frequencyadaptability_autostart" />\n          </el-select>',
        ),
        (
            "  guoqianpin_immun_default: { widgets: {}, auto_append: true, auto_start: false },\n  guoqianpin_immun_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
            "  guoqianpin_immun_default: { widgets: {}, auto_append: true, auto_start: false },\n  guoqianpin_immun_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  staticmppt_default: { widgets: {}, auto_append: true, auto_start: false },\n  staticmppt_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  frequencyadaptability_default: { widgets: {}, auto_append: true, auto_start: false },\n  frequencyadaptability_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
        ),
        (
            """  } else if (form.templateId.startsWith('guoqianpin_immun')) {
    form.testType = 'guoqianpin_immun'
  } else if (
""",
            """  } else if (form.templateId.startsWith('guoqianpin_immun')) {
    form.testType = 'guoqianpin_immun'
  } else if (form.templateId.startsWith('staticmppt')) {
    form.testType = 'staticmppt'
  } else if (form.templateId.startsWith('frequencyadaptability')) {
    form.testType = 'frequencyadaptability'
  } else if (
""",
        ),
        (
            """      form.testType === 'voltprotect10min' ||
      form.testType === 'guoqianpin_immun') &&
""",
            """      form.testType === 'voltprotect10min' ||
      form.testType === 'guoqianpin_immun' ||
      form.testType === 'staticmppt' ||
      form.testType === 'frequencyadaptability') &&
""",
        ),
        (
            """    } else if (tt === 'guoqianpin_immun' && !form.templateId.startsWith('guoqianpin_immun')) {
      form.templateId = 'guoqianpin_immun_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
            """    } else if (tt === 'guoqianpin_immun' && !form.templateId.startsWith('guoqianpin_immun')) {
      form.templateId = 'guoqianpin_immun_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'staticmppt' && !form.templateId.startsWith('staticmppt')) {
      form.templateId = 'staticmppt_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'frequencyadaptability' && !form.templateId.startsWith('frequencyadaptability')) {
      form.templateId = 'frequencyadaptability_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
        ),
        (
            """        form.templateId.startsWith('voltprotect10min') ||
        form.templateId.startsWith('guoqianpin_immun'))
""",
            """        form.templateId.startsWith('voltprotect10min') ||
        form.templateId.startsWith('guoqianpin_immun') ||
        form.templateId.startsWith('staticmppt') ||
        form.templateId.startsWith('frequencyadaptability'))
""",
        ),
        (
            """                            : tt === 'guoqianpin_immun'
                              ? '巴西过欠频稳定性联调'
                              : '过载联调'
""",
            """                            : tt === 'guoqianpin_immun'
                              ? '巴西过欠频稳定性联调'
                              : tt === 'staticmppt'
                                ? '静态MPPT联调'
                                : tt === 'frequencyadaptability'
                                  ? '频率适应性联调'
                                  : '过载联调'
""",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"joblist #{i} missing: {old[:80]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok job list")

    # docs
    p = IOT / "docs/IOT-Solar自动化试验线上版方案.md"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载/欠频升载已完成 → **10min过压保护 + 巴西过欠频稳定性已接入（待联调）**",
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载/欠频升载/10min过压保护/巴西过欠频稳定性已完成 → **静态MPPT + 频率适应性已接入（待联调）**",
        ),
        (
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载** / **10min过压保护** / **巴西过欠频稳定性**（`auto_append` / `auto_start`）  ",
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载** / **10min过压保护** / **巴西过欠频稳定性** / **静态MPPT** / **频率适应性**（`auto_append` / `auto_start`）  ",
        ),
        (
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`、10min过压保护 `voltprotect10min`、巴西过欠频稳定性 `guoqianpin_immun`  ",
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`、10min过压保护 `voltprotect10min`、巴西过欠频稳定性 `guoqianpin_immun`、静态MPPT `staticmppt`、频率适应性 `frequencyadaptability`  ",
        ),
        (
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 / 10min过压保护 / 巴西过欠频稳定性 参数 → 创建实验",
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 / 10min过压保护 / 巴西过欠频稳定性 / 静态MPPT / 频率适应性 参数 → 创建实验",
        ),
        (
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai` / `voltprotect10min` / `guoqianpin_immun`）。",
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai` / `voltprotect10min` / `guoqianpin_immun` / `staticmppt` / `frequencyadaptability`）。",
        ),
    ]
    for old, new in reps:
        if old not in t:
            raise SystemExit(f"docs missing: {old[:70]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok docs")

    # tests
    (IOT / "tests/test_solar_staticmppt_schema.py").write_text(
        '''# -*- coding: utf-8 -*-
"""静态MPPT schema / Blockly 接入冒烟。"""
from __future__ import annotations

from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_staticmppt_supported_and_aliases():
    assert "staticmppt" in list_supported_test_types()
    assert normalize_test_type("静态MPPT测试") == "staticmppt"
    assert normalize_test_type("staticMPPTtest") == "staticmppt"


def test_staticmppt_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("staticmppt")
    assert schema["testType"] == "staticmppt"
    by_name = {f["name"]: f for f in schema["fields"]}
    for need in (
        "checkBox_S1",
        "checkBox_Analyzer",
        "radio_wt",
        "dew_export_fields",
        "checkBox_S2",
        "checkBox_S2_Pn_100",
        "checkBox_S3",
        "textEdit_S3_TOTAL_M",
        "checkBox_S_End",
    ):
        assert need in by_name, need
    assert schema["wtLayout"]["dew"].get("powerGroupTreeNodes")


def test_staticmppt_blockly_steps():
    steps = flow_steps_for_test_type("staticmppt")
    assert [s["blockly_name"] for s in steps] == [
        "solar_staticmppt_s1",
        "solar_staticmppt_s2",
        "solar_staticmppt_s3",
        "solar_staticmppt_s4",
    ]
    assert "checkBox_S2_Pn_100" in field_names_for_step("solar_staticmppt_s3")
    assert detail_fields_for("staticmppt", "solar_staticmppt_s3", widgets=build_job_widgets("staticmppt", None))
''',
        encoding="utf-8",
    )
    (IOT / "tests/test_solar_frequencyadaptability_schema.py").write_text(
        '''# -*- coding: utf-8 -*-
"""频率适应性 schema / Blockly 接入冒烟。"""
from __future__ import annotations

from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_frequencyadaptability_supported_and_aliases():
    assert "frequencyadaptability" in list_supported_test_types()
    assert normalize_test_type("频率适应性") == "frequencyadaptability"
    assert normalize_test_type("freqadapt") == "frequencyadaptability"


def test_frequencyadaptability_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("frequencyadaptability")
    assert schema["testType"] == "frequencyadaptability"
    by_name = {f["name"]: f for f in schema["fields"]}
    for need in (
        "checkBox_S1",
        "radio_wt",
        "dew_export_fields",
        "checkBox_guopin_page",
        "checkBox_qianpin_page",
        "textEdit_S3_freq_start_guopin",
        "textEdit_S12_freq_start_qianpin",
        "checkBox_S_End",
    ):
        assert need in by_name, need
    assert schema["wtLayout"]["dew"].get("powerGroupTreeNodes")


def test_frequencyadaptability_blockly_steps():
    steps = flow_steps_for_test_type("frequencyadaptability")
    assert [s["blockly_name"] for s in steps] == [
        "solar_frequencyadaptability_s1",
        "solar_frequencyadaptability_s2",
        "solar_frequencyadaptability_s3",
        "solar_frequencyadaptability_s4",
    ]
    assert "checkBox_guopin_page" in field_names_for_step("solar_frequencyadaptability_s3")
    assert detail_fields_for(
        "frequencyadaptability",
        "solar_frequencyadaptability_s3",
        widgets=build_job_widgets("frequencyadaptability", None),
    )
''',
        encoding="utf-8",
    )
    print("ok tests")

    # handoff
    p = SOLAR / "utils/iot_ui_handoff.py"
    t = p.read_text(encoding="utf-8")
    if "staticmppt" not in t or "resolve_staticmppt_ui" not in t:
        reps = [
            (
                '''        "过欠频稳定性": ("巴西过欠频稳定性", "guoqianpin_immun"),
    }
''',
                '''        "过欠频稳定性": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "staticmppt": ("静态MPPT测试", "staticmppt"),
        "staticMPPTtest": ("静态MPPT测试", "staticmppt"),
        "static_mppt": ("静态MPPT测试", "staticmppt"),
        "静态MPPT测试": ("静态MPPT测试", "staticmppt"),
        "静态MPPT": ("静态MPPT测试", "staticmppt"),
        "frequencyadaptability": ("频率适应性", "frequencyadaptability"),
        "freqadapt": ("频率适应性", "frequencyadaptability"),
        "频率适应性": ("频率适应性", "frequencyadaptability"),
    }
''',
            ),
            (
                """        resolve_guoqianpin_immun_ui: Optional[Callable[[], Any]] = None,
        guoqianpin_immun_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
                """        resolve_guoqianpin_immun_ui: Optional[Callable[[], Any]] = None,
        guoqianpin_immun_append: Optional[Callable[[], None]] = None,
        resolve_staticmppt_ui: Optional[Callable[[], Any]] = None,
        staticmppt_append: Optional[Callable[[], None]] = None,
        resolve_frequencyadaptability_ui: Optional[Callable[[], Any]] = None,
        frequencyadaptability_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
            ),
            (
                """        self.resolve_guoqianpin_immun_ui = resolve_guoqianpin_immun_ui
        self.guoqianpin_immun_append = guoqianpin_immun_append
        self.start_test = start_test
""",
                """        self.resolve_guoqianpin_immun_ui = resolve_guoqianpin_immun_ui
        self.guoqianpin_immun_append = guoqianpin_immun_append
        self.resolve_staticmppt_ui = resolve_staticmppt_ui
        self.staticmppt_append = staticmppt_append
        self.resolve_frequencyadaptability_ui = resolve_frequencyadaptability_ui
        self.frequencyadaptability_append = frequencyadaptability_append
        self.start_test = start_test
""",
            ),
            (
                '''        if handler_key == "guoqianpin_immun":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_guoqianpin_immun_ui,
                "append": self.guoqianpin_immun_append,
                "label": "巴西过欠频稳定性",
            }
        return None
''',
                '''        if handler_key == "guoqianpin_immun":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_guoqianpin_immun_ui,
                "append": self.guoqianpin_immun_append,
                "label": "巴西过欠频稳定性",
            }
        if handler_key == "staticmppt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_staticmppt_ui,
                "append": self.staticmppt_append,
                "label": "静态MPPT测试",
            }
        if handler_key == "frequencyadaptability":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_frequencyadaptability_ui,
                "append": self.frequencyadaptability_append,
                "label": "频率适应性",
            }
        return None
''',
            ),
            (
                '''                "voltprotect10min",
                "guoqianpin_immun",
            ) and isinstance(widgets_for_ui, dict):
''',
                '''                "voltprotect10min",
                "guoqianpin_immun",
                "staticmppt",
                "frequencyadaptability",
            ) and isinstance(widgets_for_ui, dict):
''',
            ),
            (
                '''                    "voltprotect10min",
                    "guoqianpin_immun",
                ) and isinstance(widgets, dict):
''',
                '''                    "voltprotect10min",
                    "guoqianpin_immun",
                    "staticmppt",
                    "frequencyadaptability",
                ) and isinstance(widgets, dict):
''',
            ),
            (
                """    resolve_guoqianpin_immun_ui: Optional[Callable[[], Any]] = None,
    guoqianpin_immun_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
                """    resolve_guoqianpin_immun_ui: Optional[Callable[[], Any]] = None,
    guoqianpin_immun_append: Optional[Callable[[], None]] = None,
    resolve_staticmppt_ui: Optional[Callable[[], Any]] = None,
    staticmppt_append: Optional[Callable[[], None]] = None,
    resolve_frequencyadaptability_ui: Optional[Callable[[], Any]] = None,
    frequencyadaptability_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
            ),
            (
                """        resolve_guoqianpin_immun_ui=resolve_guoqianpin_immun_ui,
        guoqianpin_immun_append=guoqianpin_immun_append,
        start_test=start_test,
""",
                """        resolve_guoqianpin_immun_ui=resolve_guoqianpin_immun_ui,
        guoqianpin_immun_append=guoqianpin_immun_append,
        resolve_staticmppt_ui=resolve_staticmppt_ui,
        staticmppt_append=staticmppt_append,
        resolve_frequencyadaptability_ui=resolve_frequencyadaptability_ui,
        frequencyadaptability_append=frequencyadaptability_append,
        start_test=start_test,
""",
            ),
        ]
        for i, (old, new) in enumerate(reps):
            if old not in t:
                raise SystemExit(f"handoff #{i} missing")
            t = t.replace(old, new, 1)
        p.write_text(t, encoding="utf-8")
        print("ok handoff")
    else:
        print("handoff already")

    _repl(
        SOLAR / "agent/runners/__init__.py",
        '''        "巴西过欠频稳定性",
        "过欠频稳定性",
    ):
''',
        '''        "巴西过欠频稳定性",
        "过欠频稳定性",
        "staticmppt",
        "staticMPPTtest",
        "static_mppt",
        "静态MPPT测试",
        "静态MPPT",
        "frequencyadaptability",
        "freqadapt",
        "频率适应性",
    ):
''',
        label="runner",
    )

    p = SOLAR / "SCPITestWave.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_staticmppt_ui" not in t:
        old = '''                def _resolve_guoqianpin_immun_ui():
                    return globals().get("uiThaiGuoQianPin_Immun")

                def _iot_get_run_status():
'''
        new = '''                def _resolve_guoqianpin_immun_ui():
                    return globals().get("uiThaiGuoQianPin_Immun")

                def _resolve_staticmppt_ui():
                    return globals().get("uiThaiStaticMPPTTest")

                def _resolve_frequencyadaptability_ui():
                    return globals().get("uiThaiFrequencyAdaptability")

                def _iot_get_run_status():
'''
        t = t.replace(old, new, 1)
        old = """                    resolve_guoqianpin_immun_ui=_resolve_guoqianpin_immun_ui,
                    guoqianpin_immun_append=thaiguoqianpin_immunAppend,
                    start_test=RunProjectPush,
"""
        new = """                    resolve_guoqianpin_immun_ui=_resolve_guoqianpin_immun_ui,
                    guoqianpin_immun_append=thaiguoqianpin_immunAppend,
                    resolve_staticmppt_ui=_resolve_staticmppt_ui,
                    staticmppt_append=thaistaticMPPTtestAppend,
                    resolve_frequencyadaptability_ui=_resolve_frequencyadaptability_ui,
                    frequencyadaptability_append=thaifrequencyadaptabilityAppend,
                    start_test=RunProjectPush,
"""
        if old not in t:
            raise SystemExit("SCPI kwargs missing")
        t = t.replace(old, new, 1)
        p.write_text(t, encoding="utf-8")
        print("ok SCPI")
    else:
        print("SCPI already")

    p = SOLAR / "tests/test_agent_runner_fixedpf.py"
    t = p.read_text(encoding="utf-8")
    if 'get_runner("staticmppt"' not in t:
        old = '''    r16 = get_runner("guoqianpin_immun", dry_run=True, execution_mode="handoff")
    r17 = get_runner("巴西过欠频稳定性", dry_run=True, execution_mode="handoff")
'''
        new = '''    r16 = get_runner("guoqianpin_immun", dry_run=True, execution_mode="handoff")
    r17 = get_runner("巴西过欠频稳定性", dry_run=True, execution_mode="handoff")
    r18 = get_runner("staticmppt", dry_run=True, execution_mode="handoff")
    r19 = get_runner("静态MPPT测试", dry_run=True, execution_mode="handoff")
    r20 = get_runner("frequencyadaptability", dry_run=True, execution_mode="handoff")
    r21 = get_runner("频率适应性", dry_run=True, execution_mode="handoff")
'''
        t = t.replace(old, new, 1)
        t = t.replace(
            "assert r17 is not None",
            "assert r17 is not None\n    assert r18 is not None\n    assert r19 is not None\n    assert r20 is not None\n    assert r21 is not None",
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok runner test")
    else:
        print("runner test already")


def main() -> None:
    write_schemas()
    wire()
    print("staticmppt + frequencyadaptability done")


if __name__ == "__main__":
    main()
