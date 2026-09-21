# -*- coding: utf-8 -*-
"""生成并接入：ROCOF保护 + 快速电压变化。"""
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


def _parse_common(src: str, *, group_fn, labels: dict, extras=None) -> dict:
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
        if name in fields:
            fields[name].update({k: v for k, v in base.items() if v not in (None, [], "")})
        else:
            fields[name] = base

    for m in re.finditer(
        r"self\.(checkBox_\w+|comboBox_\w+|textEdit_\w+|lineEdit_\w+|spinBox_\w+|doubleSpinBox_\w+|radioButton_\w+|radio_\w+)\s*=",
        src,
    ):
        _ensure(m.group(1))

    for m in re.finditer(
        r"self\.(comboBox_\w+)\.addItems\(\[(.*?)\]\)",
        src,
        flags=re.S,
    ):
        name = m.group(1)
        opts = re.findall(r'["\']([^"\']+)["\']', m.group(2))
        if name in fields and opts:
            fields[name]["options"] = opts
            fields[name]["type"] = "select"

    for m in re.finditer(
        r"self\.(checkBox_\w+)\.setChecked\((True|False)\)",
        src,
    ):
        if m.group(1) in fields:
            fields[m.group(1)]["default"] = m.group(2) == "True"

    for m in re.finditer(
        r'self\.(textEdit_\w+)\.set(?:Plain)?Text\(\s*["\'](.*?)["\']\s*\)',
        src,
        flags=re.S,
    ):
        if m.group(1) in fields:
            fields[m.group(1)]["default"] = m.group(2).replace("\\n", "\n")

    if extras:
        extras(_ensure)

    out = {}
    for name, f in fields.items():
        if name.startswith("radioButton_S2_"):
            alias = "radio_" + name[len("radioButton_") :]
            f = dict(f)
            f["name"] = alias
            name = alias
        out[name] = f
    return out


def gen_rocof() -> dict:
    src = (SOLAR / "Dialog_thairocof.py").read_text(encoding="utf-8")
    labels = {
        "checkBox_S1": "启用步骤1 AC/DC",
        "checkBox_S2": "启用步骤2 功率分析仪",
        "checkBox_rocof_page": "启用ROCOF设置",
        "checkBox_S_End": "启用关机",
        "comboBox_S_End_AC": "关机 AC",
        "radio_wt": "功率分析仪",
        "radio_dewetron": "德威创",
    }

    def group_fn(name: str) -> str:
        if "S_End" in name:
            return "step4_off"
        if "rocof" in name or re.match(r".*_S[3-8]_", name) or re.match(
            r"^(?:checkBox|textEdit|comboBox)_S[3-8]", name
        ):
            return "step3_rocof"
        if "DEW" in name or "dewetron" in name:
            return "step2_dew"
        if name.startswith(
            ("checkBox_S2", "radio_S2", "radio_wt", "radio_wt3000", "textEdit_S2", "comboBox_S2")
        ):
            return "step2_wt"
        if "S1" in name:
            return "step1_dc" if "DC" in name else "step1_ac"
        return "other"

    def extras(ensure):
        ensure("radio_wt", label="功率分析仪", type="radio", default=True)
        ensure("radio_dewetron", label="德威创", type="radio", default=False)
        for i in range(3, 9):
            ensure(f"checkBox_S{i}", label=f"启用ROCOF{i-2}", default=(i <= 6))
            ensure(f"checkBox_S{i}_RATE", label=f"ROCOF{i-2} 更新率", default=True)
            ensure(f"textEdit_S{i}_freq_start_rocof", label=f"ROCOF{i-2} 起点(Hz)")
            ensure(f"textEdit_S{i}_freq_end_rocof", label=f"ROCOF{i-2} 终点(Hz)")
            ensure(f"textEdit_S{i}_rocof_hz_s_rocof", label=f"ROCOF{i-2} (Hz/s)")
            ensure(f"textEdit_S{i}_test_duration_rocof", label=f"ROCOF{i-2} 时长")
            ensure(
                f"comboBox_S{i}_test_time_unit_rocof",
                label=f"ROCOF{i-2} 单位",
                type="select",
                options=["秒", "毫秒", "分钟"],
                default="秒",
            )

    cleaned = _parse_common(src, group_fn=group_fn, labels=labels, extras=extras)
    if "radio_wt3000" in cleaned and "radio_wt" not in cleaned:
        cleaned["radio_wt"] = dict(cleaned["radio_wt3000"])
        cleaned["radio_wt"]["name"] = "radio_wt"
        cleaned["radio_wt"]["label"] = "功率分析仪"

    groups = [
        {"id": "step1_ac", "title": "① AC 电源"},
        {"id": "step1_dc", "title": "① DC 电源"},
        {"id": "step2_wt", "title": "② 功率分析仪"},
        {"id": "step2_dew", "title": "② 德威创"},
        {"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"},
        {"id": "step3_rocof", "title": "③ ROCOF设置"},
        {"id": "step4_off", "title": "④ 关机设置"},
        {"id": "other", "title": "其它"},
    ]
    schema = {
        "testType": "rocof",
        "title": "ROCOF保护",
        "version": 1,
        "groups": groups,
        "fields": sorted(cleaned.values(), key=lambda x: (x["group"], x["name"])),
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def gen_rapidvolt() -> dict:
    src = (SOLAR / "Dialog_thairapidvolt.py").read_text(encoding="utf-8")
    labels = {
        "checkBox_S1": "启用步骤1 AC/DC",
        "checkBox_S2": "启用步骤2 功率分析仪",
        "checkBox_rapidvolt_page": "启用快速电压变化",
        "checkBox_S_End": "启用关机",
        "comboBox_S_End_AC": "关机 AC",
        "radio_wt": "功率分析仪",
        "radio_dewetron": "德威创",
    }

    def group_fn(name: str) -> str:
        if "S_End" in name:
            return "step4_off"
        if "rapidvolt" in name or "rvc" in name or re.match(
            r".*_S[3-8]_", name
        ) or re.match(r"^(?:checkBox|textEdit|comboBox)_S[3-8]", name):
            return "step3_rvc"
        if "DEW" in name or "dewetron" in name:
            return "step2_dew"
        if name.startswith(
            ("checkBox_S2", "radio_S2", "radio_wt", "radio_wt3000", "textEdit_S2", "comboBox_S2")
        ):
            return "step2_wt"
        if "S1" in name:
            return "step1_dc" if "DC" in name else "step1_ac"
        return "other"

    def extras(ensure):
        ensure("radio_wt", label="功率分析仪", type="radio", default=True)
        ensure("radio_dewetron", label="德威创", type="radio", default=False)
        for i in range(3, 9):
            ensure(f"checkBox_S{i}", label=f"启用阶跃{i-2}", default=(i <= 6))
            ensure(f"checkBox_S{i}_return_rvc", label=f"阶跃{i-2} 回起点", default=True)
            ensure(f"textEdit_S{i}_volt_start_rvc", label=f"阶跃{i-2} 起点(V)")
            ensure(f"textEdit_S{i}_volt_end_rvc", label=f"阶跃{i-2} 终点(V)")
            ensure(f"textEdit_S{i}_pre_hold_rvc", label=f"阶跃{i-2} 起点保持", default="1")
            ensure(
                f"comboBox_S{i}_pre_hold_unit_rvc",
                label=f"阶跃{i-2} 起点单位",
                type="select",
                options=["秒", "分钟", "小时"],
                default="秒",
            )
            ensure(f"textEdit_S{i}_post_hold_rvc", label=f"阶跃{i-2} 终点保持", default="3")
            ensure(
                f"comboBox_S{i}_post_hold_unit_rvc",
                label=f"阶跃{i-2} 终点单位",
                type="select",
                options=["秒", "分钟", "小时"],
                default="秒",
            )

    cleaned = _parse_common(src, group_fn=group_fn, labels=labels, extras=extras)
    if "radio_wt3000" in cleaned and "radio_wt" not in cleaned:
        cleaned["radio_wt"] = dict(cleaned["radio_wt3000"])
        cleaned["radio_wt"]["name"] = "radio_wt"
        cleaned["radio_wt"]["label"] = "功率分析仪"

    groups = [
        {"id": "step1_ac", "title": "① AC 电源"},
        {"id": "step1_dc", "title": "① DC 电源"},
        {"id": "step2_wt", "title": "② 功率分析仪"},
        {"id": "step2_dew", "title": "② 德威创"},
        {"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"},
        {"id": "step3_rvc", "title": "③ 快速电压变化"},
        {"id": "step4_off", "title": "④ 关机设置"},
        {"id": "other", "title": "其它"},
    ]
    schema = {
        "testType": "rapidvolt",
        "title": "快速电压变化",
        "version": 1,
        "groups": groups,
        "fields": sorted(cleaned.values(), key=lambda x: (x["group"], x["name"])),
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def write_schemas() -> None:
    for schema, sw_name, iot_name in (
        (gen_rocof(), "iot_rocof_schema_data.json", "rocof_fields.json"),
        (gen_rapidvolt(), "iot_rapidvolt_schema_data.json", "rapidvolt_fields.json"),
    ):
        text = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
        (SOLAR / "utils" / sw_name).write_text(text, encoding="utf-8")
        (IOT / "app/services/solar_test_schemas" / iot_name).write_text(text, encoding="utf-8")
        print(f"wrote {sw_name} / {iot_name} fields={len(schema['fields'])}")


def _repl(path: Path, old: str, new: str, *, label: str) -> None:
    t = path.read_text(encoding="utf-8")
    if old not in t:
        raise SystemExit(f"missing in {path.name}: {label}\n{old[:160]!r}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    print(f"ok {path.name} ({label})")


def wire() -> None:
    p = IOT / "app/services/solar_test_schemas/__init__.py"
    t = p.read_text(encoding="utf-8")
    if "rocof_fields.json" not in t:
        old = '''        "电压适应性": "voltageadaptability_fields.json",
    }
'''
        new = '''        "电压适应性": "voltageadaptability_fields.json",
        "rocof": "rocof_fields.json",
        "rocofprotect": "rocof_fields.json",
        "rocof_protect": "rocof_fields.json",
        "rocof保护": "rocof_fields.json",
        "rapidvolt": "rapidvolt_fields.json",
        "rapid_volt": "rapidvolt_fields.json",
        "rvc": "rapidvolt_fields.json",
        "快速电压变化": "rapidvolt_fields.json",
    }
'''
        t = t.replace(old, new, 1)
        t = t.replace(
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun", "staticmppt", "frequencyadaptability", "voltageadaptability"]',
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun", "staticmppt", "frequencyadaptability", "voltageadaptability", "rocof", "rapidvolt"]',
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok schema init")
    else:
        print("schema init already")

    p = IOT / "app/services/solar_blockly_catalog.py"
    t = p.read_text(encoding="utf-8")
    if '"rocof":' not in t:
        marker = '''            {"blockly_name": "solar_voltageadaptability_s4", "com_name": "电压适应性步骤4 关机", "colour": 70},
        ),
    },
}
'''
        insert = '''            {"blockly_name": "solar_voltageadaptability_s4", "com_name": "电压适应性步骤4 关机", "colour": 70},
        ),
    },
    "rocof": {
        "com_name": "ROCOF保护半自动",
        "blockly_name": "solar_rocof",
        "label": "ROCOF保护",
        "colour": 80,
        "aliases": (
            "rocof",
            "rocofprotect",
            "rocof_protect",
            "ROCOF保护",
            "rocof保护",
            "ROCOF保护半自动",
        ),
        "steps": (
            {"blockly_name": "solar_rocof_s1", "com_name": "ROCOF步骤1 AC/DC", "colour": 80},
            {"blockly_name": "solar_rocof_s2", "com_name": "ROCOF步骤2 分析仪", "colour": 90},
            {"blockly_name": "solar_rocof_s3", "com_name": "ROCOF步骤3 设置", "colour": 100},
            {"blockly_name": "solar_rocof_s4", "com_name": "ROCOF步骤4 关机", "colour": 110},
        ),
    },
    "rapidvolt": {
        "com_name": "快速电压变化半自动",
        "blockly_name": "solar_rapidvolt",
        "label": "快速电压变化",
        "colour": 120,
        "aliases": (
            "rapidvolt",
            "rapid_volt",
            "rvc",
            "快速电压变化",
            "快速电压变化半自动",
        ),
        "steps": (
            {"blockly_name": "solar_rapidvolt_s1", "com_name": "快速电压变化步骤1 AC/DC", "colour": 120},
            {"blockly_name": "solar_rapidvolt_s2", "com_name": "快速电压变化步骤2 分析仪", "colour": 130},
            {"blockly_name": "solar_rapidvolt_s3", "com_name": "快速电压变化步骤3 阶跃", "colour": 140},
            {"blockly_name": "solar_rapidvolt_s4", "com_name": "快速电压变化步骤4 关机", "colour": 150},
        ),
    },
}
'''
        if marker not in t:
            raise SystemExit("catalog voltageadaptability tail missing")
        p.write_text(t.replace(marker, insert, 1), encoding="utf-8")
        print("ok catalog")
    else:
        print("catalog already")

    p = IOT / "app/services/solar_blockly_detail.py"
    t = p.read_text(encoding="utf-8")
    if "solar_rocof_s1" not in t:
        old = '''    "solar_voltageadaptability_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
        new = '''    "solar_voltageadaptability_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
    # ── ROCOF保护 ──
    "solar_rocof_s1": (
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
    "solar_rocof_s2": (
        "checkBox_S2",
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "comboBox_DEW_MaxRefreshRate",
    ),
    "solar_rocof_s3": (
        "checkBox_rocof_page",
        "checkBox_S3",
        "textEdit_S3_freq_start_rocof",
        "textEdit_S3_freq_end_rocof",
        "textEdit_S3_rocof_hz_s_rocof",
        "checkBox_S4",
        "textEdit_S4_freq_start_rocof",
        "textEdit_S4_freq_end_rocof",
        "textEdit_S4_rocof_hz_s_rocof",
    ),
    "solar_rocof_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
    # ── 快速电压变化 ──
    "solar_rapidvolt_s1": (
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
    "solar_rapidvolt_s2": (
        "checkBox_S2",
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "comboBox_DEW_MaxRefreshRate",
    ),
    "solar_rapidvolt_s3": (
        "checkBox_rapidvolt_page",
        "checkBox_S3",
        "textEdit_S3_volt_start_rvc",
        "textEdit_S3_volt_end_rvc",
        "checkBox_S4",
        "textEdit_S4_volt_start_rvc",
        "textEdit_S4_volt_end_rvc",
    ),
    "solar_rapidvolt_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
        if old not in t:
            raise SystemExit("detail voltageadaptability_s4 missing")
        p.write_text(t.replace(old, new, 1), encoding="utf-8")
        print("ok detail")
    else:
        print("detail already")

    _repl(
        IOT / "app/services/solar_experiment_service.py",
        '''            "frequencyadaptability",
            "voltageadaptability",
        ):''',
        '''            "frequencyadaptability",
            "voltageadaptability",
            "rocof",
            "rapidvolt",
        ):''',
        label="experiment",
    )

    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  电压适应性: '电压适应性',
}
""",
        """  电压适应性: '电压适应性',
  rocof: 'ROCOF保护',
  rocofprotect: 'ROCOF保护',
  rocof_protect: 'ROCOF保护',
  ROCOF保护: 'ROCOF保护',
  rocof保护: 'ROCOF保护',
  rapidvolt: '快速电压变化',
  rapid_volt: '快速电压变化',
  rvc: '快速电压变化',
  快速电压变化: '快速电压变化',
}
""",
        label="labels map",
    )
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  { value: 'voltageadaptability', label: '电压适应性' },
] as const
""",
        """  { value: 'voltageadaptability', label: '电压适应性' },
  { value: 'rocof', label: 'ROCOF保护' },
  { value: 'rapidvolt', label: '快速电压变化' },
] as const
""",
        label="labels options",
    )
    _repl(
        IOT / "frontend/src/utils/solarBlockly.ts",
        """  { type: 'solar_voltageadaptability', message0: '电压适应性半自动%1', arg: 'solar_voltageadaptability', colour: 40 },
] as const
""",
        """  { type: 'solar_voltageadaptability', message0: '电压适应性半自动%1', arg: 'solar_voltageadaptability', colour: 40 },
  { type: 'solar_rocof_s1', message0: 'ROCOF步骤1 AC/DC%1', arg: 'solar_rocof_s1', colour: 80 },
  { type: 'solar_rocof_s2', message0: 'ROCOF步骤2 分析仪%1', arg: 'solar_rocof_s2', colour: 90 },
  { type: 'solar_rocof_s3', message0: 'ROCOF步骤3 设置%1', arg: 'solar_rocof_s3', colour: 100 },
  { type: 'solar_rocof_s4', message0: 'ROCOF步骤4 关机%1', arg: 'solar_rocof_s4', colour: 110 },
  { type: 'solar_rocof', message0: 'ROCOF保护半自动%1', arg: 'solar_rocof', colour: 80 },
  { type: 'solar_rapidvolt_s1', message0: '快速电压变化步骤1 AC/DC%1', arg: 'solar_rapidvolt_s1', colour: 120 },
  { type: 'solar_rapidvolt_s2', message0: '快速电压变化步骤2 分析仪%1', arg: 'solar_rapidvolt_s2', colour: 130 },
  { type: 'solar_rapidvolt_s3', message0: '快速电压变化步骤3 阶跃%1', arg: 'solar_rapidvolt_s3', colour: 140 },
  { type: 'solar_rapidvolt_s4', message0: '快速电压变化步骤4 关机%1', arg: 'solar_rapidvolt_s4', colour: 150 },
  { type: 'solar_rapidvolt', message0: '快速电压变化半自动%1', arg: 'solar_rapidvolt', colour: 120 },
] as const
""",
        label="blockly",
    )
    _repl(
        IOT / "frontend/src/views/solar/SolarOrderCreate.vue",
        """    | 'frequencyadaptability'
    | 'voltageadaptability',
""",
        """    | 'frequencyadaptability'
    | 'voltageadaptability'
    | 'rocof'
    | 'rapidvolt',
""",
        label="order create",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  'frequencyadaptability',
  'voltageadaptability',
])
""",
        """  'frequencyadaptability',
  'voltageadaptability',
  'rocof',
  'rapidvolt',
])
""",
        label="params types",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  if (
    blob.includes('solar_voltageadaptability') ||
    blob.includes('voltageadaptability') ||
    blob.includes('电压适应性') ||
    blob.includes('voltadapt')
  ) {
    return 'voltageadaptability'
  }
""",
        """  if (
    blob.includes('solar_voltageadaptability') ||
    blob.includes('voltageadaptability') ||
    blob.includes('电压适应性') ||
    blob.includes('voltadapt')
  ) {
    return 'voltageadaptability'
  }
  if (
    blob.includes('solar_rocof') ||
    blob.includes('rocof') ||
    blob.includes('ROCOF保护') ||
    blob.includes('rocof保护')
  ) {
    return 'rocof'
  }
  if (
    blob.includes('solar_rapidvolt') ||
    blob.includes('rapidvolt') ||
    blob.includes('快速电压变化') ||
    blob.includes('rvc')
  ) {
    return 'rapidvolt'
  }
""",
        label="detect",
    )

    p = IOT / "frontend/src/views/solar/SolarJobList.vue"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            '<el-option label="电压适应性" value="voltageadaptability" />\n          </el-select>',
            '<el-option label="电压适应性" value="voltageadaptability" />\n            <el-option label="ROCOF保护" value="rocof" />\n            <el-option label="快速电压变化" value="rapidvolt" />\n          </el-select>',
        ),
        (
            '<el-option label="电压适应性自动开跑" value="voltageadaptability_autostart" />\n          </el-select>',
            '<el-option label="电压适应性自动开跑" value="voltageadaptability_autostart" />\n            <el-option label="ROCOF默认（只追加）" value="rocof_default" />\n            <el-option label="ROCOF自动开跑" value="rocof_autostart" />\n            <el-option label="快速电压变化默认（只追加）" value="rapidvolt_default" />\n            <el-option label="快速电压变化自动开跑" value="rapidvolt_autostart" />\n          </el-select>',
        ),
        (
            "  voltageadaptability_default: { widgets: {}, auto_append: true, auto_start: false },\n  voltageadaptability_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
            "  voltageadaptability_default: { widgets: {}, auto_append: true, auto_start: false },\n  voltageadaptability_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  rocof_default: { widgets: {}, auto_append: true, auto_start: false },\n  rocof_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  rapidvolt_default: { widgets: {}, auto_append: true, auto_start: false },\n  rapidvolt_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
        ),
        (
            """  } else if (form.templateId.startsWith('voltageadaptability')) {
    form.testType = 'voltageadaptability'
  } else if (
""",
            """  } else if (form.templateId.startsWith('voltageadaptability')) {
    form.testType = 'voltageadaptability'
  } else if (form.templateId.startsWith('rocof')) {
    form.testType = 'rocof'
  } else if (form.templateId.startsWith('rapidvolt')) {
    form.testType = 'rapidvolt'
  } else if (
""",
        ),
        (
            """      form.testType === 'frequencyadaptability' ||
      form.testType === 'voltageadaptability') &&
""",
            """      form.testType === 'frequencyadaptability' ||
      form.testType === 'voltageadaptability' ||
      form.testType === 'rocof' ||
      form.testType === 'rapidvolt') &&
""",
        ),
        (
            """    } else if (tt === 'voltageadaptability' && !form.templateId.startsWith('voltageadaptability')) {
      form.templateId = 'voltageadaptability_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
            """    } else if (tt === 'voltageadaptability' && !form.templateId.startsWith('voltageadaptability')) {
      form.templateId = 'voltageadaptability_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'rocof' && !form.templateId.startsWith('rocof')) {
      form.templateId = 'rocof_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'rapidvolt' && !form.templateId.startsWith('rapidvolt')) {
      form.templateId = 'rapidvolt_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
        ),
        (
            """        form.templateId.startsWith('frequencyadaptability') ||
        form.templateId.startsWith('voltageadaptability'))
""",
            """        form.templateId.startsWith('frequencyadaptability') ||
        form.templateId.startsWith('voltageadaptability') ||
        form.templateId.startsWith('rocof') ||
        form.templateId.startsWith('rapidvolt'))
""",
        ),
        (
            """                                  : tt === 'voltageadaptability'
                                    ? '电压适应性联调'
                                    : '过载联调'
""",
            """                                  : tt === 'voltageadaptability'
                                    ? '电压适应性联调'
                                    : tt === 'rocof'
                                      ? 'ROCOF联调'
                                      : tt === 'rapidvolt'
                                        ? '快速电压变化联调'
                                        : '过载联调'
""",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"joblist #{i} missing: {old[:100]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok job list")

    p = IOT / "docs/IOT-Solar自动化试验线上版方案.md"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载/欠频升载/10min过压保护/巴西过欠频稳定性/静态MPPT/频率适应性已完成 → **电压适应性已接入（待联调）**",
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载/欠频升载/10min过压保护/巴西过欠频稳定性/静态MPPT/频率适应性/电压适应性已完成 → **ROCOF + 快速电压变化已接入（待联调）**",
        ),
        (
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载** / **10min过压保护** / **巴西过欠频稳定性** / **静态MPPT** / **频率适应性** / **电压适应性**（`auto_append` / `auto_start`）  ",
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载** / **10min过压保护** / **巴西过欠频稳定性** / **静态MPPT** / **频率适应性** / **电压适应性** / **ROCOF保护** / **快速电压变化**（`auto_append` / `auto_start`）  ",
        ),
        (
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`、10min过压保护 `voltprotect10min`、巴西过欠频稳定性 `guoqianpin_immun`、静态MPPT `staticmppt`、频率适应性 `frequencyadaptability`、电压适应性 `voltageadaptability`  ",
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`、10min过压保护 `voltprotect10min`、巴西过欠频稳定性 `guoqianpin_immun`、静态MPPT `staticmppt`、频率适应性 `frequencyadaptability`、电压适应性 `voltageadaptability`、ROCOF `rocof`、快速电压变化 `rapidvolt`  ",
        ),
        (
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 / 10min过压保护 / 巴西过欠频稳定性 / 静态MPPT / 频率适应性 / 电压适应性 参数 → 创建实验",
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 / 10min过压保护 / 巴西过欠频稳定性 / 静态MPPT / 频率适应性 / 电压适应性 / ROCOF / 快速电压变化 参数 → 创建实验",
        ),
        (
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai` / `voltprotect10min` / `guoqianpin_immun` / `staticmppt` / `frequencyadaptability` / `voltageadaptability`）。",
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai` / `voltprotect10min` / `guoqianpin_immun` / `staticmppt` / `frequencyadaptability` / `voltageadaptability` / `rocof` / `rapidvolt`）。",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"docs #{i} missing: {old[:80]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok docs")

    (IOT / "tests/test_solar_rocof_schema.py").write_text(
        '''# -*- coding: utf-8 -*-
"""ROCOF保护 schema / Blockly 接入冒烟。"""
from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_rocof_supported_and_aliases():
    assert "rocof" in list_supported_test_types()
    assert normalize_test_type("ROCOF保护") == "rocof"
    assert normalize_test_type("rocofprotect") == "rocof"
    load_test_schema.cache_clear()
    assert load_test_schema("ROCOF保护")["testType"] == "rocof"


def test_rocof_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("rocof")
    assert schema["testType"] == "rocof"
    names = {f["name"] for f in schema["fields"]}
    assert "checkBox_rocof_page" in names
    assert "textEdit_S3_rocof_hz_s_rocof" in names
    assert isinstance(build_job_widgets("rocof", None), dict)


def test_rocof_blockly_steps():
    steps = flow_steps_for_test_type("rocof")
    assert [s["blockly_name"] for s in steps] == [
        "solar_rocof_s1",
        "solar_rocof_s2",
        "solar_rocof_s3",
        "solar_rocof_s4",
    ]
    assert "textEdit_S3_rocof_hz_s_rocof" in field_names_for_step("solar_rocof_s3")
    assert detail_fields_for("rocof", "solar_rocof_s3", widgets=build_job_widgets("rocof", None))
''',
        encoding="utf-8",
    )
    (IOT / "tests/test_solar_rapidvolt_schema.py").write_text(
        '''# -*- coding: utf-8 -*-
"""快速电压变化 schema / Blockly 接入冒烟。"""
from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_rapidvolt_supported_and_aliases():
    assert "rapidvolt" in list_supported_test_types()
    assert normalize_test_type("快速电压变化") == "rapidvolt"
    assert normalize_test_type("rvc") == "rapidvolt"
    load_test_schema.cache_clear()
    assert load_test_schema("快速电压变化")["testType"] == "rapidvolt"


def test_rapidvolt_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("rapidvolt")
    assert schema["testType"] == "rapidvolt"
    names = {f["name"] for f in schema["fields"]}
    assert "checkBox_rapidvolt_page" in names
    assert "textEdit_S3_volt_start_rvc" in names
    assert isinstance(build_job_widgets("rapidvolt", None), dict)


def test_rapidvolt_blockly_steps():
    steps = flow_steps_for_test_type("rapidvolt")
    assert [s["blockly_name"] for s in steps] == [
        "solar_rapidvolt_s1",
        "solar_rapidvolt_s2",
        "solar_rapidvolt_s3",
        "solar_rapidvolt_s4",
    ]
    assert "textEdit_S3_volt_start_rvc" in field_names_for_step("solar_rapidvolt_s3")
    assert detail_fields_for(
        "rapidvolt", "solar_rapidvolt_s3", widgets=build_job_widgets("rapidvolt", None)
    )
''',
        encoding="utf-8",
    )
    print("ok tests")

    p = SOLAR / "utils/iot_ui_handoff.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_rocof_ui" not in t:
        reps = [
            (
                '''        "电压适应性": ("电压适应性", "voltageadaptability"),
    }
''',
                '''        "电压适应性": ("电压适应性", "voltageadaptability"),
        "rocof": ("ROCOF保护", "rocof"),
        "rocofprotect": ("ROCOF保护", "rocof"),
        "rocof_protect": ("ROCOF保护", "rocof"),
        "ROCOF保护": ("ROCOF保护", "rocof"),
        "rocof保护": ("ROCOF保护", "rocof"),
        "rapidvolt": ("快速电压变化", "rapidvolt"),
        "rapid_volt": ("快速电压变化", "rapidvolt"),
        "rvc": ("快速电压变化", "rapidvolt"),
        "快速电压变化": ("快速电压变化", "rapidvolt"),
    }
''',
            ),
            (
                """        resolve_voltageadaptability_ui: Optional[Callable[[], Any]] = None,
        voltageadaptability_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
                """        resolve_voltageadaptability_ui: Optional[Callable[[], Any]] = None,
        voltageadaptability_append: Optional[Callable[[], None]] = None,
        resolve_rocof_ui: Optional[Callable[[], Any]] = None,
        rocof_append: Optional[Callable[[], None]] = None,
        resolve_rapidvolt_ui: Optional[Callable[[], Any]] = None,
        rapidvolt_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
            ),
            (
                """        self.resolve_voltageadaptability_ui = resolve_voltageadaptability_ui
        self.voltageadaptability_append = voltageadaptability_append
        self.start_test = start_test
""",
                """        self.resolve_voltageadaptability_ui = resolve_voltageadaptability_ui
        self.voltageadaptability_append = voltageadaptability_append
        self.resolve_rocof_ui = resolve_rocof_ui
        self.rocof_append = rocof_append
        self.resolve_rapidvolt_ui = resolve_rapidvolt_ui
        self.rapidvolt_append = rapidvolt_append
        self.start_test = start_test
""",
            ),
            (
                '''        if handler_key == "voltageadaptability":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_voltageadaptability_ui,
                "append": self.voltageadaptability_append,
                "label": "电压适应性",
            }
        return None
''',
                '''        if handler_key == "voltageadaptability":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_voltageadaptability_ui,
                "append": self.voltageadaptability_append,
                "label": "电压适应性",
            }
        if handler_key == "rocof":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_rocof_ui,
                "append": self.rocof_append,
                "label": "ROCOF保护",
            }
        if handler_key == "rapidvolt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_rapidvolt_ui,
                "append": self.rapidvolt_append,
                "label": "快速电压变化",
            }
        return None
''',
            ),
            (
                '''                "frequencyadaptability",
                "voltageadaptability",
            ) and isinstance(widgets_for_ui, dict):
''',
                '''                "frequencyadaptability",
                "voltageadaptability",
                "rocof",
                "rapidvolt",
            ) and isinstance(widgets_for_ui, dict):
''',
            ),
            (
                '''                    "frequencyadaptability",
                    "voltageadaptability",
                ) and isinstance(widgets, dict):
''',
                '''                    "frequencyadaptability",
                    "voltageadaptability",
                    "rocof",
                    "rapidvolt",
                ) and isinstance(widgets, dict):
''',
            ),
            (
                """    resolve_voltageadaptability_ui: Optional[Callable[[], Any]] = None,
    voltageadaptability_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
                """    resolve_voltageadaptability_ui: Optional[Callable[[], Any]] = None,
    voltageadaptability_append: Optional[Callable[[], None]] = None,
    resolve_rocof_ui: Optional[Callable[[], Any]] = None,
    rocof_append: Optional[Callable[[], None]] = None,
    resolve_rapidvolt_ui: Optional[Callable[[], Any]] = None,
    rapidvolt_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
            ),
            (
                """        resolve_voltageadaptability_ui=resolve_voltageadaptability_ui,
        voltageadaptability_append=voltageadaptability_append,
        start_test=start_test,
""",
                """        resolve_voltageadaptability_ui=resolve_voltageadaptability_ui,
        voltageadaptability_append=voltageadaptability_append,
        resolve_rocof_ui=resolve_rocof_ui,
        rocof_append=rocof_append,
        resolve_rapidvolt_ui=resolve_rapidvolt_ui,
        rapidvolt_append=rapidvolt_append,
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
        '''        "voltageadaptability",
        "voltadapt",
        "voltage_adaptability",
        "电压适应性",
    ):
''',
        '''        "voltageadaptability",
        "voltadapt",
        "voltage_adaptability",
        "电压适应性",
        "rocof",
        "rocofprotect",
        "rocof_protect",
        "rocof保护",
        "rapidvolt",
        "rapid_volt",
        "rvc",
        "快速电压变化",
    ):
''',
        label="runner",
    )

    p = SOLAR / "SCPITestWave.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_rocof_ui" not in t:
        old = '''                def _resolve_voltageadaptability_ui():
                    return globals().get("uiThaiVoltageAdaptability")

                def _iot_get_run_status():
'''
        new = '''                def _resolve_voltageadaptability_ui():
                    return globals().get("uiThaiVoltageAdaptability")

                def _resolve_rocof_ui():
                    return globals().get("uiThaiROCOF")

                def _resolve_rapidvolt_ui():
                    return globals().get("uiThaiRapidVolt")

                def _iot_get_run_status():
'''
        t = t.replace(old, new, 1)
        old = """                    resolve_voltageadaptability_ui=_resolve_voltageadaptability_ui,
                    voltageadaptability_append=thaivoltageadaptabilityAppend,
                    start_test=RunProjectPush,
"""
        new = """                    resolve_voltageadaptability_ui=_resolve_voltageadaptability_ui,
                    voltageadaptability_append=thaivoltageadaptabilityAppend,
                    resolve_rocof_ui=_resolve_rocof_ui,
                    rocof_append=thairocofAppend,
                    resolve_rapidvolt_ui=_resolve_rapidvolt_ui,
                    rapidvolt_append=thairapidvoltAppend,
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
    if 'get_runner("rocof"' not in t:
        old = '''    r22 = get_runner("voltageadaptability", dry_run=True, execution_mode="handoff")
    r23 = get_runner("电压适应性", dry_run=True, execution_mode="handoff")
'''
        new = '''    r22 = get_runner("voltageadaptability", dry_run=True, execution_mode="handoff")
    r23 = get_runner("电压适应性", dry_run=True, execution_mode="handoff")
    r24 = get_runner("rocof", dry_run=True, execution_mode="handoff")
    r25 = get_runner("ROCOF保护", dry_run=True, execution_mode="handoff")
    r26 = get_runner("rapidvolt", dry_run=True, execution_mode="handoff")
    r27 = get_runner("快速电压变化", dry_run=True, execution_mode="handoff")
'''
        t = t.replace(old, new, 1)
        t = t.replace(
            "assert r23 is not None",
            "assert r23 is not None\n    assert r24 is not None\n    assert r25 is not None\n    assert r26 is not None\n    assert r27 is not None",
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok runner test")
    else:
        print("runner test already")


def main() -> None:
    write_schemas()
    wire()
    print("rocof + rapidvolt done")


if __name__ == "__main__":
    main()
