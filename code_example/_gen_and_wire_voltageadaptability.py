# -*- coding: utf-8 -*-
"""生成并接入：电压适应性。"""
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
        if name in fields:
            fields[name].update({k: v for k, v in base.items() if v not in (None, [], "")})
        else:
            fields[name] = base

    for m in re.finditer(
        r"self\.(checkBox_\w+|comboBox_\w+|textEdit_\w+|lineEdit_\w+|spinBox_\w+|doubleSpinBox_\w+|radioButton_\w+|radio_\w+)\s*=",
        src,
    ):
        _ensure(m.group(1))

    # combo options
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

    # checkbox defaults
    for m in re.finditer(
        r"self\.(checkBox_\w+)\.setChecked\((True|False)\)",
        src,
    ):
        if m.group(1) in fields:
            fields[m.group(1)]["default"] = m.group(2) == "True"

    # text defaults
    for m in re.finditer(
        r'self\.(textEdit_\w+)\.set(?:Plain)?Text\(\s*["\'](.*?)["\']\s*\)',
        src,
        flags=re.S,
    ):
        if m.group(1) in fields:
            fields[m.group(1)]["default"] = m.group(2).replace("\\n", "\n")

    if extras:
        extras(_ensure)

    # normalize radioButton_S2_* -> radio_S2_*
    out = {}
    for name, f in fields.items():
        if name.startswith("radioButton_S2_"):
            alias = "radio_" + name[len("radioButton_") :]
            f = dict(f)
            f["name"] = alias
            name = alias
        out[name] = f
    return out


def gen_voltageadaptability() -> dict:
    src = (SOLAR / "Dialog_thaivoltageadaptability.py").read_text(encoding="utf-8")
    labels = {
        "checkBox_S1": "启用步骤1 AC/DC",
        "checkBox_S2": "启用步骤2 功率分析仪",
        "checkBox_guoya_page": "启用过压设置",
        "checkBox_qianya_page": "启用欠压设置",
        "checkBox_S_End": "启用关机",
        "comboBox_S_End_AC": "关机 AC",
        "textEdit_VoltageLadder_guoya": "过压阶梯 (V@s)",
        "textEdit_VoltageLadder_qianya": "欠压阶梯 (V@s)",
        "checkBox_S2_split_ov_uv_files": "过/欠压分文件录波",
        "checkBox_S2_update_rate": "启用更新率",
        "textEdit_S2_update_rate": "更新率",
        "comboBox_S2_update_rate": "更新率单位",
        "radio_wt": "功率分析仪",
        "radio_dewetron": "德威创",
        "dew_export_fields": "导出字段选择",
    }

    def group_fn(name: str) -> str:
        if "S_End" in name:
            return "step5_off"
        if "qianya" in name:
            return "step4_uv"
        if "guoya" in name or "VoltageLadder_guoya" in name:
            return "step3_ov"
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
        ensure(
            "textEdit_VoltageLadder_guoya",
            label="过压阶梯 (V@s)",
            default="230-253@30\n253-230@30",
        )
        ensure("textEdit_VoltageLadder_qianya", label="欠压阶梯 (V@s)", default="")

    cleaned = _parse_common(
        src,
        dialog_name="Dialog_thaivoltageadaptability",
        group_fn=group_fn,
        labels=labels,
        extras=extras,
    )
    # analyzer alias
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
        {"id": "step3_ov", "title": "③ 过压设置"},
        {"id": "step4_uv", "title": "④ 欠压设置"},
        {"id": "step5_off", "title": "⑤ 关机设置"},
        {"id": "other", "title": "其它"},
    ]
    schema = {
        "testType": "voltageadaptability",
        "title": "电压适应性",
        "version": 1,
        "groups": groups,
        "fields": sorted(cleaned.values(), key=lambda x: (x["group"], x["name"])),
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def write_schemas() -> None:
    schema = gen_voltageadaptability()
    text = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
    sw = SOLAR / "utils" / "iot_voltageadaptability_schema_data.json"
    iot = IOT / "app/services/solar_test_schemas" / "voltageadaptability_fields.json"
    sw.write_text(text, encoding="utf-8")
    iot.write_text(text, encoding="utf-8")
    print(f"wrote {sw.name} / {iot.name} fields={len(schema['fields'])}")


def _repl(path: Path, old: str, new: str, *, label: str) -> None:
    t = path.read_text(encoding="utf-8")
    if old not in t:
        raise SystemExit(f"missing in {path.name}: {label}\n{old[:160]!r}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    print(f"ok {path.name} ({label})")


def wire() -> None:
    # schema init — lowercase-safe keys (tt.lower() before lookup)
    p = IOT / "app/services/solar_test_schemas/__init__.py"
    t = p.read_text(encoding="utf-8")
    if "voltageadaptability_fields.json" not in t:
        old = '''        "频率适应性": "frequencyadaptability_fields.json",
    }
'''
        new = '''        "频率适应性": "frequencyadaptability_fields.json",
        "voltageadaptability": "voltageadaptability_fields.json",
        "voltadapt": "voltageadaptability_fields.json",
        "voltage_adaptability": "voltageadaptability_fields.json",
        "电压适应性": "voltageadaptability_fields.json",
    }
'''
        t = t.replace(old, new, 1)
        t = t.replace(
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun", "staticmppt", "frequencyadaptability"]',
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun", "staticmppt", "frequencyadaptability", "voltageadaptability"]',
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok schema init")
    else:
        print("schema init already")

    # catalog
    p = IOT / "app/services/solar_blockly_catalog.py"
    t = p.read_text(encoding="utf-8")
    if '"voltageadaptability":' not in t:
        marker = '''            {"blockly_name": "solar_frequencyadaptability_s4", "com_name": "频率适应性步骤4 关机", "colour": 350},
        ),
    },
}
'''
        insert = '''            {"blockly_name": "solar_frequencyadaptability_s4", "com_name": "频率适应性步骤4 关机", "colour": 350},
        ),
    },
    "voltageadaptability": {
        "com_name": "电压适应性半自动",
        "blockly_name": "solar_voltageadaptability",
        "label": "电压适应性",
        "colour": 40,
        "aliases": (
            "voltageadaptability",
            "voltadapt",
            "voltage_adaptability",
            "电压适应性",
            "电压适应性半自动",
        ),
        "steps": (
            {"blockly_name": "solar_voltageadaptability_s1", "com_name": "电压适应性步骤1 AC/DC", "colour": 40},
            {"blockly_name": "solar_voltageadaptability_s2", "com_name": "电压适应性步骤2 分析仪", "colour": 50},
            {"blockly_name": "solar_voltageadaptability_s3", "com_name": "电压适应性步骤3 过欠压", "colour": 60},
            {"blockly_name": "solar_voltageadaptability_s4", "com_name": "电压适应性步骤4 关机", "colour": 70},
        ),
    },
}
'''
        if marker not in t:
            raise SystemExit("catalog frequencyadaptability tail missing")
        p.write_text(t.replace(marker, insert, 1), encoding="utf-8")
        print("ok catalog")
    else:
        print("catalog already")

    # detail
    p = IOT / "app/services/solar_blockly_detail.py"
    t = p.read_text(encoding="utf-8")
    if "solar_voltageadaptability_s1" not in t:
        old = '''    "solar_frequencyadaptability_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
        new = '''    "solar_frequencyadaptability_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
    # ── 电压适应性 ──
    "solar_voltageadaptability_s1": (
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
    "solar_voltageadaptability_s2": (
        "checkBox_S2",
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "checkBox_S2_split_ov_uv_files",
        "checkBox_S2_update_rate",
        "textEdit_S2_update_rate",
        "comboBox_S2_update_rate",
        "comboBox_DEW_MaxRefreshRate",
    ),
    "solar_voltageadaptability_s3": (
        "checkBox_guoya_page",
        "textEdit_VoltageLadder_guoya",
        "checkBox_qianya_page",
        "textEdit_VoltageLadder_qianya",
    ),
    "solar_voltageadaptability_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
        if old not in t:
            raise SystemExit("detail frequencyadaptability_s4 missing")
        p.write_text(t.replace(old, new, 1), encoding="utf-8")
        print("ok detail")
    else:
        print("detail already")

    _repl(
        IOT / "app/services/solar_experiment_service.py",
        '''            "staticmppt",
            "frequencyadaptability",
        ):''',
        '''            "staticmppt",
            "frequencyadaptability",
            "voltageadaptability",
        ):''',
        label="experiment",
    )

    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  频率适应性: '频率适应性',
}
""",
        """  频率适应性: '频率适应性',
  voltageadaptability: '电压适应性',
  voltadapt: '电压适应性',
  voltage_adaptability: '电压适应性',
  电压适应性: '电压适应性',
}
""",
        label="labels map",
    )
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  { value: 'frequencyadaptability', label: '频率适应性' },
] as const
""",
        """  { value: 'frequencyadaptability', label: '频率适应性' },
  { value: 'voltageadaptability', label: '电压适应性' },
] as const
""",
        label="labels options",
    )
    _repl(
        IOT / "frontend/src/utils/solarBlockly.ts",
        """  { type: 'solar_frequencyadaptability', message0: '频率适应性半自动%1', arg: 'solar_frequencyadaptability', colour: 320 },
] as const
""",
        """  { type: 'solar_frequencyadaptability', message0: '频率适应性半自动%1', arg: 'solar_frequencyadaptability', colour: 320 },
  { type: 'solar_voltageadaptability_s1', message0: '电压适应性步骤1 AC/DC%1', arg: 'solar_voltageadaptability_s1', colour: 40 },
  { type: 'solar_voltageadaptability_s2', message0: '电压适应性步骤2 分析仪%1', arg: 'solar_voltageadaptability_s2', colour: 50 },
  { type: 'solar_voltageadaptability_s3', message0: '电压适应性步骤3 过欠压%1', arg: 'solar_voltageadaptability_s3', colour: 60 },
  { type: 'solar_voltageadaptability_s4', message0: '电压适应性步骤4 关机%1', arg: 'solar_voltageadaptability_s4', colour: 70 },
  { type: 'solar_voltageadaptability', message0: '电压适应性半自动%1', arg: 'solar_voltageadaptability', colour: 40 },
] as const
""",
        label="blockly",
    )
    _repl(
        IOT / "frontend/src/views/solar/SolarOrderCreate.vue",
        """    | 'staticmppt'
    | 'frequencyadaptability',
""",
        """    | 'staticmppt'
    | 'frequencyadaptability'
    | 'voltageadaptability',
""",
        label="order create",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  'staticmppt',
  'frequencyadaptability',
])
""",
        """  'staticmppt',
  'frequencyadaptability',
  'voltageadaptability',
])
""",
        label="params types",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  if (
    blob.includes('solar_frequencyadaptability') ||
    blob.includes('frequencyadaptability') ||
    blob.includes('频率适应性') ||
    blob.includes('freqadapt')
  ) {
    return 'frequencyadaptability'
  }
""",
        """  if (
    blob.includes('solar_frequencyadaptability') ||
    blob.includes('frequencyadaptability') ||
    blob.includes('频率适应性') ||
    blob.includes('freqadapt')
  ) {
    return 'frequencyadaptability'
  }
  if (
    blob.includes('solar_voltageadaptability') ||
    blob.includes('voltageadaptability') ||
    blob.includes('电压适应性') ||
    blob.includes('voltadapt')
  ) {
    return 'voltageadaptability'
  }
""",
        label="detect",
    )

    p = IOT / "frontend/src/views/solar/SolarJobList.vue"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            '<el-option label="频率适应性" value="frequencyadaptability" />\n          </el-select>',
            '<el-option label="频率适应性" value="frequencyadaptability" />\n            <el-option label="电压适应性" value="voltageadaptability" />\n          </el-select>',
        ),
        (
            '<el-option label="频率适应性自动开跑" value="frequencyadaptability_autostart" />\n          </el-select>',
            '<el-option label="频率适应性自动开跑" value="frequencyadaptability_autostart" />\n            <el-option label="电压适应性默认（只追加）" value="voltageadaptability_default" />\n            <el-option label="电压适应性自动开跑" value="voltageadaptability_autostart" />\n          </el-select>',
        ),
        (
            "  frequencyadaptability_default: { widgets: {}, auto_append: true, auto_start: false },\n  frequencyadaptability_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
            "  frequencyadaptability_default: { widgets: {}, auto_append: true, auto_start: false },\n  frequencyadaptability_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  voltageadaptability_default: { widgets: {}, auto_append: true, auto_start: false },\n  voltageadaptability_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
        ),
        (
            """  } else if (form.templateId.startsWith('frequencyadaptability')) {
    form.testType = 'frequencyadaptability'
  } else if (
""",
            """  } else if (form.templateId.startsWith('frequencyadaptability')) {
    form.testType = 'frequencyadaptability'
  } else if (form.templateId.startsWith('voltageadaptability')) {
    form.testType = 'voltageadaptability'
  } else if (
""",
        ),
        (
            """      form.testType === 'staticmppt' ||
      form.testType === 'frequencyadaptability') &&
""",
            """      form.testType === 'staticmppt' ||
      form.testType === 'frequencyadaptability' ||
      form.testType === 'voltageadaptability') &&
""",
        ),
        (
            """    } else if (tt === 'frequencyadaptability' && !form.templateId.startsWith('frequencyadaptability')) {
      form.templateId = 'frequencyadaptability_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
            """    } else if (tt === 'frequencyadaptability' && !form.templateId.startsWith('frequencyadaptability')) {
      form.templateId = 'frequencyadaptability_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'voltageadaptability' && !form.templateId.startsWith('voltageadaptability')) {
      form.templateId = 'voltageadaptability_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
        ),
        (
            """        form.templateId.startsWith('staticmppt') ||
        form.templateId.startsWith('frequencyadaptability'))
""",
            """        form.templateId.startsWith('staticmppt') ||
        form.templateId.startsWith('frequencyadaptability') ||
        form.templateId.startsWith('voltageadaptability'))
""",
        ),
        (
            """                              : tt === 'frequencyadaptability'
                                  ? '频率适应性联调'
                                  : '过载联调'
""",
            """                              : tt === 'frequencyadaptability'
                                  ? '频率适应性联调'
                                  : tt === 'voltageadaptability'
                                    ? '电压适应性联调'
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

    # docs
    p = IOT / "docs/IOT-Solar自动化试验线上版方案.md"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载/欠频升载/10min过压保护/巴西过欠频稳定性已完成 → **静态MPPT + 频率适应性已接入（待联调）**",
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载/欠频升载/10min过压保护/巴西过欠频稳定性/静态MPPT/频率适应性已完成 → **电压适应性已接入（待联调）**",
        ),
        (
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载** / **10min过压保护** / **巴西过欠频稳定性** / **静态MPPT** / **频率适应性**（`auto_append` / `auto_start`）  ",
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载** / **10min过压保护** / **巴西过欠频稳定性** / **静态MPPT** / **频率适应性** / **电压适应性**（`auto_append` / `auto_start`）  ",
        ),
        (
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`、10min过压保护 `voltprotect10min`、巴西过欠频稳定性 `guoqianpin_immun`、静态MPPT `staticmppt`、频率适应性 `frequencyadaptability`  ",
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`、10min过压保护 `voltprotect10min`、巴西过欠频稳定性 `guoqianpin_immun`、静态MPPT `staticmppt`、频率适应性 `frequencyadaptability`、电压适应性 `voltageadaptability`  ",
        ),
        (
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 / 10min过压保护 / 巴西过欠频稳定性 / 静态MPPT / 频率适应性 参数 → 创建实验",
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 / 10min过压保护 / 巴西过欠频稳定性 / 静态MPPT / 频率适应性 / 电压适应性 参数 → 创建实验",
        ),
        (
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai` / `voltprotect10min` / `guoqianpin_immun` / `staticmppt` / `frequencyadaptability`）。",
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai` / `voltprotect10min` / `guoqianpin_immun` / `staticmppt` / `frequencyadaptability` / `voltageadaptability`）。",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"docs #{i} missing: {old[:80]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok docs")

    # tests
    (IOT / "tests/test_solar_voltageadaptability_schema.py").write_text(
        '''# -*- coding: utf-8 -*-
"""电压适应性 schema / Blockly 接入冒烟。"""
from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_voltageadaptability_supported_and_aliases():
    assert "voltageadaptability" in list_supported_test_types()
    assert normalize_test_type("电压适应性") == "voltageadaptability"
    assert normalize_test_type("voltadapt") == "voltageadaptability"
    load_test_schema.cache_clear()
    assert load_test_schema("电压适应性")["testType"] == "voltageadaptability"


def test_voltageadaptability_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("voltageadaptability")
    assert schema["testType"] == "voltageadaptability"
    names = {f["name"] for f in schema["fields"]}
    assert "checkBox_guoya_page" in names
    assert "textEdit_VoltageLadder_guoya" in names
    assert "checkBox_qianya_page" in names
    assert "checkBox_S2_split_ov_uv_files" in names
    widgets = build_job_widgets("voltageadaptability", None)
    assert isinstance(widgets, dict)


def test_voltageadaptability_blockly_steps():
    steps = flow_steps_for_test_type("voltageadaptability")
    assert [s["blockly_name"] for s in steps] == [
        "solar_voltageadaptability_s1",
        "solar_voltageadaptability_s2",
        "solar_voltageadaptability_s3",
        "solar_voltageadaptability_s4",
    ]
    assert "textEdit_VoltageLadder_guoya" in field_names_for_step("solar_voltageadaptability_s3")
    assert detail_fields_for(
        "voltageadaptability",
        "solar_voltageadaptability_s3",
        widgets=build_job_widgets("voltageadaptability", None),
    )
''',
        encoding="utf-8",
    )
    print("ok tests")

    # handoff
    p = SOLAR / "utils/iot_ui_handoff.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_voltageadaptability_ui" not in t:
        reps = [
            (
                '''        "频率适应性": ("频率适应性", "frequencyadaptability"),
    }
''',
                '''        "频率适应性": ("频率适应性", "frequencyadaptability"),
        "voltageadaptability": ("电压适应性", "voltageadaptability"),
        "voltadapt": ("电压适应性", "voltageadaptability"),
        "voltage_adaptability": ("电压适应性", "voltageadaptability"),
        "电压适应性": ("电压适应性", "voltageadaptability"),
    }
''',
            ),
            (
                """        resolve_frequencyadaptability_ui: Optional[Callable[[], Any]] = None,
        frequencyadaptability_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
                """        resolve_frequencyadaptability_ui: Optional[Callable[[], Any]] = None,
        frequencyadaptability_append: Optional[Callable[[], None]] = None,
        resolve_voltageadaptability_ui: Optional[Callable[[], Any]] = None,
        voltageadaptability_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
            ),
            (
                """        self.resolve_frequencyadaptability_ui = resolve_frequencyadaptability_ui
        self.frequencyadaptability_append = frequencyadaptability_append
        self.start_test = start_test
""",
                """        self.resolve_frequencyadaptability_ui = resolve_frequencyadaptability_ui
        self.frequencyadaptability_append = frequencyadaptability_append
        self.resolve_voltageadaptability_ui = resolve_voltageadaptability_ui
        self.voltageadaptability_append = voltageadaptability_append
        self.start_test = start_test
""",
            ),
            (
                '''        if handler_key == "frequencyadaptability":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_frequencyadaptability_ui,
                "append": self.frequencyadaptability_append,
                "label": "频率适应性",
            }
        return None
''',
                '''        if handler_key == "frequencyadaptability":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_frequencyadaptability_ui,
                "append": self.frequencyadaptability_append,
                "label": "频率适应性",
            }
        if handler_key == "voltageadaptability":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_voltageadaptability_ui,
                "append": self.voltageadaptability_append,
                "label": "电压适应性",
            }
        return None
''',
            ),
            (
                '''                "staticmppt",
                "frequencyadaptability",
            ) and isinstance(widgets_for_ui, dict):
''',
                '''                "staticmppt",
                "frequencyadaptability",
                "voltageadaptability",
            ) and isinstance(widgets_for_ui, dict):
''',
            ),
            (
                '''                    "staticmppt",
                    "frequencyadaptability",
                ) and isinstance(widgets, dict):
''',
                '''                    "staticmppt",
                    "frequencyadaptability",
                    "voltageadaptability",
                ) and isinstance(widgets, dict):
''',
            ),
            (
                """    resolve_frequencyadaptability_ui: Optional[Callable[[], Any]] = None,
    frequencyadaptability_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
                """    resolve_frequencyadaptability_ui: Optional[Callable[[], Any]] = None,
    frequencyadaptability_append: Optional[Callable[[], None]] = None,
    resolve_voltageadaptability_ui: Optional[Callable[[], Any]] = None,
    voltageadaptability_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
            ),
            (
                """        resolve_frequencyadaptability_ui=resolve_frequencyadaptability_ui,
        frequencyadaptability_append=frequencyadaptability_append,
        start_test=start_test,
""",
                """        resolve_frequencyadaptability_ui=resolve_frequencyadaptability_ui,
        frequencyadaptability_append=frequencyadaptability_append,
        resolve_voltageadaptability_ui=resolve_voltageadaptability_ui,
        voltageadaptability_append=voltageadaptability_append,
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
        '''        "frequencyadaptability",
        "freqadapt",
        "频率适应性",
    ):
''',
        '''        "frequencyadaptability",
        "freqadapt",
        "频率适应性",
        "voltageadaptability",
        "voltadapt",
        "voltage_adaptability",
        "电压适应性",
    ):
''',
        label="runner",
    )

    p = SOLAR / "SCPITestWave.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_voltageadaptability_ui" not in t:
        old = '''                def _resolve_frequencyadaptability_ui():
                    return globals().get("uiThaiFrequencyAdaptability")

                def _iot_get_run_status():
'''
        new = '''                def _resolve_frequencyadaptability_ui():
                    return globals().get("uiThaiFrequencyAdaptability")

                def _resolve_voltageadaptability_ui():
                    return globals().get("uiThaiVoltageAdaptability")

                def _iot_get_run_status():
'''
        t = t.replace(old, new, 1)
        old = """                    resolve_frequencyadaptability_ui=_resolve_frequencyadaptability_ui,
                    frequencyadaptability_append=thaifrequencyadaptabilityAppend,
                    start_test=RunProjectPush,
"""
        new = """                    resolve_frequencyadaptability_ui=_resolve_frequencyadaptability_ui,
                    frequencyadaptability_append=thaifrequencyadaptabilityAppend,
                    resolve_voltageadaptability_ui=_resolve_voltageadaptability_ui,
                    voltageadaptability_append=thaivoltageadaptabilityAppend,
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
    if 'get_runner("voltageadaptability"' not in t:
        old = '''    r20 = get_runner("frequencyadaptability", dry_run=True, execution_mode="handoff")
    r21 = get_runner("频率适应性", dry_run=True, execution_mode="handoff")
'''
        new = '''    r20 = get_runner("frequencyadaptability", dry_run=True, execution_mode="handoff")
    r21 = get_runner("频率适应性", dry_run=True, execution_mode="handoff")
    r22 = get_runner("voltageadaptability", dry_run=True, execution_mode="handoff")
    r23 = get_runner("电压适应性", dry_run=True, execution_mode="handoff")
'''
        t = t.replace(old, new, 1)
        t = t.replace(
            "assert r21 is not None",
            "assert r21 is not None\n    assert r22 is not None\n    assert r23 is not None",
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok runner test")
    else:
        print("runner test already")


def main() -> None:
    write_schemas()
    wire()
    print("voltageadaptability done")


if __name__ == "__main__":
    main()
