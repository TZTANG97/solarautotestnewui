# -*- coding: utf-8 -*-
"""批量接入 Auto_Test 剩余功率/无功族 11 项。"""
from __future__ import annotations

import json
import re
from pathlib import Path

SOLAR = Path(r"E:/solarautotestnewui")
IOT = Path(r"E:/IOT/iot")
OVERLOAD_SW = SOLAR / "utils" / "iot_overload_schema_data.json"
IOT_OVERLOAD = IOT / "app/services/solar_test_schemas/overload_fields.json"

# tt / title / dialog / ui_global / append_fn / aliases / detail_s3 / colour
SPECS = [
    {
        "tt": "reactiveqcap",
        "title": "无功能力范围",
        "dialog": "Dialog_thaireactiveQcap.py",
        "ui": "uiThaiReactiveQCap",
        "append": "thaireactiveQcapAppend",
        "aliases": ("reactiveqcap", "reactiveQcap", "reactive_qcap", "无功能力范围", "无功控制范围"),
        "s3": ("checkBox_S3", "textEdit_PowerLadder", "comboBox_S3_record_mode"),
        "colour": 15,
    },
    {
        "tt": "fixedq",
        "title": "定无功",
        "dialog": "Dialog_thaifixedQ.py",
        "ui": "uiThaiFixedQ",
        "append": "thaifixedQAppend",
        "aliases": ("fixedq", "fixedQ", "fixed_q", "定无功", "固无功"),
        "s3": ("checkBox_S3", "textEdit_QLadder", "textEdit_PowerLadder"),
        "colour": 25,
    },
    {
        "tt": "reactiveqin",
        "title": "无功注入",
        "dialog": "Dialog_thaireactiveQin.py",
        "ui": "uiThaiReactiveQin",
        "append": "thaireactiveQinAppend",
        "aliases": ("reactiveqin", "reactiveQin", "reactive_qin", "无功注入"),
        "s3": ("checkBox_S3", "textEdit_PowerLadder", "textEdit_QLadder"),
        "colour": 35,
    },
    {
        "tt": "reactiveqacc",
        "title": "无功精度",
        "dialog": "Dialog_thaireactiveQacc.py",
        "ui": "uiThaiReactiveQacc",
        "append": "thaireactiveQaccAppend",
        "aliases": ("reactiveqacc", "reactiveQacc", "reactive_qacc", "无功精度"),
        "s3": ("checkBox_S3", "textEdit_PowerLadder", "textEdit_QLadder"),
        "colour": 45,
    },
    {
        "tt": "activep",
        "title": "有功调度",
        "dialog": "Dialog_thaiactiveP.py",
        "ui": "uiThaiActiveP",
        "append": "thaiactivePAppend",
        "aliases": ("activep", "activeP", "active_p", "有功调度", "有功控制"),
        "s3": ("checkBox_S3", "textEdit_PowerLadder"),
        "colour": 55,
    },
    {
        "tt": "staticqu",
        "title": "静态QU",
        "dialog": "Dialog_thaistaticQU.py",
        "ui": "uiThaiStaticQU",
        "append": "thaistaticQUAppend",
        "aliases": ("staticqu", "staticQU", "static_qu", "静态QU", "静态qu"),
        "s3": ("textEdit_VoltageLadder", "textEdit_VoltageLadder_Un", "textEdit_VoltageLadder_FR"),
        "colour": 65,
    },
    {
        "tt": "dynamicqu",
        "title": "动态QU",
        "dialog": "Dialog_thaidynamicQU.py",
        "ui": "uiThaiDynamicQU",
        "append": "thaidynamicQUAppend",
        "aliases": ("dynamicqu", "dynamicQU", "dynamic_qu", "动态QU", "动态qu"),
        "s3": ("textEdit_VoltageLadder", "textEdit_VoltageLadder_Un", "textEdit_VoltageLadder_FR"),
        "colour": 75,
    },
    {
        "tt": "testpu",
        "title": "Test_PU",
        "dialog": "Dialog_thaitestPU.py",
        "ui": "uiThaiTestPU",
        "append": "thaitestPUAppend",
        "aliases": ("testpu", "testPU", "test_pu", "Test_PU", "test_PU"),
        "s3": ("checkBox_S_PU", "textEdit_VoltageLadder", "textEdit_VoltageLadder_Un"),
        "colour": 85,
    },
    {
        "tt": "staticcosphi",
        "title": "静态Cos(φ)",
        "dialog": "Dialog_thaistaticcosPhi.py",
        "ui": "uiThaiStaticCosPhi",
        "append": "thaistaticcosPhiAppend",
        "aliases": (
            "staticcosphi",
            "staticcosPhi",
            "static_cosphi",
            "静态Cos(φ)",
            "静态cos(φ)",
            "静态CosPhi",
        ),
        "s3": ("textEdit_PowerLadder", "textEdit_S3_TIME_2", "comboBox_S3_TIME_2"),
        "colour": 95,
    },
    {
        "tt": "dynamiccosphi",
        "title": "动态Cos(φ)",
        "dialog": "Dialog_thaidynamiccosPhi.py",
        "ui": "uiThaiDynamicCosPhi",
        "append": "thaidynamiccosPhiAppend",
        "aliases": (
            "dynamiccosphi",
            "dynamiccosPhi",
            "dynamic_cosphi",
            "动态Cos(φ)",
            "动态cos(φ)",
            "动态CosPhi",
        ),
        "s3": ("textEdit_PowerLadder", "textEdit_S3_TIME_2", "comboBox_S3_TIME_2"),
        "colour": 105,
    },
    {
        "tt": "cosphibrazil",
        "title": "Cos(φ)_Brazil",
        "dialog": "Dialog_thaicosPhi_Brazil.py",
        "ui": "uiThaiCosPhiBrazil",
        "append": "thaicosPhiBrazilAppend",
        "aliases": (
            "cosphibrazil",
            "cosPhiBrazil",
            "cos_phi_brazil",
            "Cos(φ)_Brazil",
            "cos(φ)_brazil",
            "巴西CosPhi",
        ),
        "s3": ("textEdit_S3_TIME_2", "checkBox_S9_AC_Check", "textEdit_S9_AC_Volt"),
        "colour": 115,
    },
]


def _infer_type(name: str) -> str:
    if name.startswith("checkBox_"):
        return "checkbox"
    if name.startswith("comboBox_"):
        return "select"
    if name.startswith(("textEdit_", "lineEdit_")):
        return "text"
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


def _group_fn(name: str) -> str:
    if "S_End" in name or "S_END" in name:
        return "step4_off"
    if any(
        k in name
        for k in (
            "Ladder",
            "PowerLadder",
            "QLadder",
            "VoltageLadder",
            "S3",
            "S_PU",
            "S9",
            "cos",
            "Cos",
            "QU",
            "PU",
        )
    ):
        return "step3_test"
    if "DEW" in name or "dewetron" in name:
        return "step2_dew"
    if name.startswith(("checkBox_S2", "radio_S2", "radio_wt", "radio_wt3000", "textEdit_S2", "comboBox_S2")):
        return "step2_wt"
    if "S1" in name:
        return "step1_dc" if "DC" in name else "step1_ac"
    return "other"


def _parse_dialog(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    fields: dict[str, dict] = {}

    def ensure(name: str, **overrides):
        if not name or "%" in name:
            return
        base = {
            "name": name,
            "label": name,
            "type": _infer_type(name),
            "group": _group_fn(name),
            "default": None,
            "options": [],
        }
        base.update(overrides)
        if name in fields:
            fields[name].update({k: v for k, v in base.items() if v not in (None, [], "")})
        else:
            fields[name] = base

    for m in re.finditer(
        r"self\.(checkBox_\w+|comboBox_\w+|textEdit_\w+|lineEdit_\w+|radioButton_\w+|radio_\w+)\s*=",
        src,
    ):
        ensure(m.group(1))
    for m in re.finditer(r'setattr\(\s*self\s*,\s*["\']([^"\']+)["\']', src):
        ensure(m.group(1))
    for m in re.finditer(r"self\.(comboBox_\w+)\.addItems\(\[(.*?)\]\)", src, flags=re.S):
        opts = re.findall(r'["\']([^"\']+)["\']', m.group(2))
        if m.group(1) in fields and opts:
            fields[m.group(1)]["options"] = opts
            fields[m.group(1)]["type"] = "select"
    for m in re.finditer(r"self\.(checkBox_\w+)\.setChecked\((True|False)\)", src):
        if m.group(1) in fields:
            fields[m.group(1)]["default"] = m.group(2) == "True"

    ensure("radio_wt", label="功率分析仪", type="radio", default=True, group="step2_wt")
    ensure("radio_dewetron", label="德威创", type="radio", default=False, group="step2_wt")

    out = {}
    for name, f in fields.items():
        if name.startswith("radioButton_S2_"):
            alias = "radio_" + name[len("radioButton_") :]
            f = dict(f)
            f["name"] = alias
            name = alias
        out[name] = f
    if "radio_wt3000" in out and "radio_wt" not in out:
        out["radio_wt"] = dict(out["radio_wt3000"])
        out["radio_wt"]["name"] = "radio_wt"
        out["radio_wt"]["label"] = "功率分析仪"
    return out


def gen_schema(spec: dict) -> dict:
    cleaned = _parse_dialog(SOLAR / spec["dialog"])
    groups = [
        {"id": "step1_ac", "title": "① AC 电源"},
        {"id": "step1_dc", "title": "① DC 电源"},
        {"id": "step2_wt", "title": "② 功率分析仪"},
        {"id": "step2_dew", "title": "② 德威创"},
        {"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"},
        {"id": "step3_test", "title": "③ 试验参数"},
        {"id": "step4_off", "title": "④ 关机设置"},
        {"id": "other", "title": "其它"},
    ]
    schema = {
        "testType": spec["tt"],
        "title": spec["title"],
        "version": 1,
        "groups": groups,
        "fields": sorted(cleaned.values(), key=lambda x: (x["group"], x["name"])),
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def write_schemas() -> None:
    for spec in SPECS:
        schema = gen_schema(spec)
        text = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
        (SOLAR / "utils" / f"iot_{spec['tt']}_schema_data.json").write_text(text, encoding="utf-8")
        (IOT / "app/services/solar_test_schemas" / f"{spec['tt']}_fields.json").write_text(
            text, encoding="utf-8"
        )
        print(f"wrote {spec['tt']} fields={len(schema['fields'])}")


def _repl(path: Path, old: str, new: str, *, label: str) -> None:
    t = path.read_text(encoding="utf-8")
    if old not in t:
        raise SystemExit(f"missing in {path.name}: {label}\n{old[:160]!r}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    print(f"ok {path.name} ({label})")


def _insert_before(path: Path, marker: str, insert: str, *, label: str) -> None:
    t = path.read_text(encoding="utf-8")
    if insert.strip()[:40] in t:
        print(f"skip {path.name} ({label})")
        return
    if marker not in t:
        raise SystemExit(f"marker missing in {path.name}: {label}\n{marker[:120]!r}")
    path.write_text(t.replace(marker, insert + marker, 1), encoding="utf-8")
    print(f"ok {path.name} ({label})")


def wire() -> None:
    tts = [s["tt"] for s in SPECS]

    # schema init mapping + list
    p = IOT / "app/services/solar_test_schemas/__init__.py"
    t = p.read_text(encoding="utf-8")
    if f"{SPECS[0]['tt']}_fields.json" not in t:
        lines = []
        for s in SPECS:
            for a in s["aliases"]:
                # schema lookup uses .lower(); keep lowered forms for mixed Latin
                key = a.lower() if any(c.isascii() and c.isalpha() for c in a) else a
                # always also store original if different
                for k in dict.fromkeys([a, key]):
                    lines.append(f'        "{k}": "{s["tt"]}_fields.json",')
        block = "\n".join(lines) + "\n"
        t = t.replace(
            '        "动态mppt": "dynamicmppt_fields.json",\n    }\n',
            '        "动态mppt": "dynamicmppt_fields.json",\n' + block + "    }\n",
            1,
        )
        old_list = (
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", '
            '"dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", '
            '"voltprotect10min", "guoqianpin_immun", "staticmppt", "frequencyadaptability", '
            '"voltageadaptability", "rocof", "rapidvolt", "lvrt", "phasejump", "dynamicmppt"]'
        )
        new_list = old_list[:-1] + ", " + ", ".join(f'"{x}"' for x in tts) + "]"
        if old_list not in t:
            raise SystemExit("list_supported missing")
        t = t.replace(old_list, new_list, 1)
        p.write_text(t, encoding="utf-8")
        print("ok schema init")
    else:
        print("schema init already")

    # catalog
    p = IOT / "app/services/solar_blockly_catalog.py"
    t = p.read_text(encoding="utf-8")
    if f'"{SPECS[0]["tt"]}":' not in t:
        chunks = []
        for s in SPECS:
            c = s["colour"]
            aliases = ",\n            ".join(f'"{a}"' for a in s["aliases"])
            chunks.append(
                f'''    "{s["tt"]}": {{
        "com_name": "{s["title"]}半自动",
        "blockly_name": "solar_{s["tt"]}",
        "label": "{s["title"]}",
        "colour": {c},
        "aliases": (
            {aliases},
            "{s["title"]}半自动",
        ),
        "steps": (
            {{"blockly_name": "solar_{s["tt"]}_s1", "com_name": "{s["title"]}步骤1 AC/DC", "colour": {c}}},
            {{"blockly_name": "solar_{s["tt"]}_s2", "com_name": "{s["title"]}步骤2 分析仪", "colour": {c + 5}}},
            {{"blockly_name": "solar_{s["tt"]}_s3", "com_name": "{s["title"]}步骤3 参数", "colour": {c + 10}}},
            {{"blockly_name": "solar_{s["tt"]}_s4", "com_name": "{s["title"]}步骤4 关机", "colour": {c + 15}}},
        ),
    }},'''
            )
        insert = "\n".join(chunks) + "\n"
        marker = "\n}\n\n\ndef normalize_test_type"
        # catalog ends SOLAR_TEST_SPECS before normalize - find last entry closing
        if '"dynamicmppt":' not in t:
            raise SystemExit("catalog dynamicmppt missing")
        # insert before final closing of SOLAR_TEST_SPECS dict
        idx = t.rfind("\n}\n\n\ndef normalize_test_type")
        if idx < 0:
            idx = t.rfind("\n}\n\ndef normalize_test_type")
        if idx < 0:
            raise SystemExit("catalog normalize marker missing")
        # find the closing of dynamicmppt which is the last before }
        # simpler: replace the closing `,\n}\n\ndef normalize` after dynamicmppt block
        m = re.search(
            r'("dynamicmppt": \{.*?\n    \},\n)(\})',
            t,
            flags=re.S,
        )
        if not m:
            raise SystemExit("catalog dynamicmppt block missing")
        t = t[: m.end(1)] + insert + t[m.start(2) :]
        p.write_text(t, encoding="utf-8")
        print("ok catalog")
    else:
        print("catalog already")

    # detail
    p = IOT / "app/services/solar_blockly_detail.py"
    t = p.read_text(encoding="utf-8")
    if f'solar_{SPECS[0]["tt"]}_s1' not in t:
        chunks = []
        for s in SPECS:
            s3 = ",\n        ".join(f'"{x}"' for x in s["s3"])
            chunks.append(
                f'''    # ── {s["title"]} ──
    "solar_{s["tt"]}_s1": (
        "checkBox_S1", "comboBox_S1_AC", "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT", "textEdit_S1_AC_FR", "checkBox_S1_DC1",
        "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME", "comboBox_S1_TIME",
    ),
    "solar_{s["tt"]}_s2": (
        "checkBox_S2", "radio_wt", "radio_dewetron",
        "radio_S2_WT3000", "radio_S2_WT1800", "radio_S2_WT1806E", "radio_S2_WT5000",
    ),
    "solar_{s["tt"]}_s3": (
        {s3},
    ),
    "solar_{s["tt"]}_s4": (
        "checkBox_S_End", "comboBox_S_End_AC", "checkBox_S_END", "comboBox_S_END_AC",
    ),'''
            )
        insert = "\n".join(chunks) + "\n"
        old = '''    "solar_dynamicmppt_s4": ("checkBox_S_End", "comboBox_S_End_AC"),
}
'''
        if old not in t:
            raise SystemExit("detail dynamicmppt_s4 missing")
        t = t.replace(old, old.replace("}\n", insert + "}\n"), 1)
        p.write_text(t, encoding="utf-8")
        print("ok detail")
    else:
        print("detail already")

    # experiment service
    _repl(
        IOT / "app/services/solar_experiment_service.py",
        '''            "lvrt",
            "phasejump",
            "dynamicmppt",
        ):''',
        '''            "lvrt",
            "phasejump",
            "dynamicmppt",
            '''
        + ",\n            ".join(f'"{x}"' for x in tts)
        + """,
        ):""",
        label="experiment",
    )

    # labels map
    label_lines = []
    for s in SPECS:
        for a in s["aliases"]:
            label_lines.append(f"  {a}: '{s['title']}',")
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  动态mppt: '动态MPPT',
}
""",
        """  动态mppt: '动态MPPT',
"""
        + "\n".join(label_lines)
        + "\n}\n",
        label="labels map",
    )
    opt_lines = "\n".join(f"  {{ value: '{s['tt']}', label: '{s['title']}' }}," for s in SPECS)
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  { value: 'dynamicmppt', label: '动态MPPT' },
] as const
""",
        """  { value: 'dynamicmppt', label: '动态MPPT' },
"""
        + opt_lines
        + "\n] as const\n",
        label="labels options",
    )

    # blockly
    blk = []
    for s in SPECS:
        c = s["colour"]
        blk.append(
            f"  {{ type: 'solar_{s['tt']}_s1', message0: '{s['title']}步骤1 AC/DC%1', arg: 'solar_{s['tt']}_s1', colour: {c} }},"
        )
        blk.append(
            f"  {{ type: 'solar_{s['tt']}_s2', message0: '{s['title']}步骤2 分析仪%1', arg: 'solar_{s['tt']}_s2', colour: {c + 5} }},"
        )
        blk.append(
            f"  {{ type: 'solar_{s['tt']}_s3', message0: '{s['title']}步骤3 参数%1', arg: 'solar_{s['tt']}_s3', colour: {c + 10} }},"
        )
        blk.append(
            f"  {{ type: 'solar_{s['tt']}_s4', message0: '{s['title']}步骤4 关机%1', arg: 'solar_{s['tt']}_s4', colour: {c + 15} }},"
        )
        blk.append(
            f"  {{ type: 'solar_{s['tt']}', message0: '{s['title']}半自动%1', arg: 'solar_{s['tt']}', colour: {c} }},"
        )
    _repl(
        IOT / "frontend/src/utils/solarBlockly.ts",
        """  { type: 'solar_dynamicmppt', message0: '动态MPPT半自动%1', arg: 'solar_dynamicmppt', colour: 240 },
] as const
""",
        """  { type: 'solar_dynamicmppt', message0: '动态MPPT半自动%1', arg: 'solar_dynamicmppt', colour: 240 },
"""
        + "\n".join(blk)
        + "\n] as const\n",
        label="blockly",
    )

    # order create
    oc = "\n".join(f"    | '{s['tt']}'" for s in SPECS)
    _repl(
        IOT / "frontend/src/views/solar/SolarOrderCreate.vue",
        """    | 'lvrt'
    | 'phasejump'
    | 'dynamicmppt',
""",
        """    | 'lvrt'
    | 'phasejump'
    | 'dynamicmppt'
"""
        + oc
        + ",\n",
        label="order create",
    )

    # experiment start types
    es = "\n".join(f"  '{s['tt']}'," for s in SPECS)
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  'lvrt',
  'phasejump',
  'dynamicmppt',
])
""",
        """  'lvrt',
  'phasejump',
  'dynamicmppt',
"""
        + es
        + "\n])\n",
        label="params types",
    )

    detect_chunks = []
    for s in SPECS:
        conds = [f"blob.includes('solar_{s['tt']}')", f"blob.includes('{s['tt']}')"]
        for a in s["aliases"]:
            if a != s["tt"]:
                conds.append(f"blob.includes('{a}')")
        detect_chunks.append(
            "  if (\n    "
            + " ||\n    ".join(conds[:6])
            + f"\n  ) {{\n    return '{s['tt']}'\n  }}\n"
        )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  if (
    blob.includes('solar_dynamicmppt') ||
    blob.includes('dynamicmppt') ||
    blob.includes('动态MPPT') ||
    blob.includes('动态mppt')
  ) {
    return 'dynamicmppt'
  }
""",
        """  if (
    blob.includes('solar_dynamicmppt') ||
    blob.includes('dynamicmppt') ||
    blob.includes('动态MPPT') ||
    blob.includes('动态mppt')
  ) {
    return 'dynamicmppt'
  }
"""
        + "".join(detect_chunks),
        label="detect",
    )

    # JobList - multiple patches
    p = IOT / "frontend/src/views/solar/SolarJobList.vue"
    t = p.read_text(encoding="utf-8")
    if f'value="{SPECS[0]["tt"]}"' not in t:
        opts = "\n".join(
            f'            <el-option label="{s["title"]}" value="{s["tt"]}" />' for s in SPECS
        )
        t = t.replace(
            '<el-option label="动态MPPT" value="dynamicmppt" />\n          </el-select>',
            '<el-option label="动态MPPT" value="dynamicmppt" />\n'
            + opts
            + "\n          </el-select>",
            1,
        )
        tpls = []
        for s in SPECS:
            tpls.append(
                f'            <el-option label="{s["title"]}默认（只追加）" value="{s["tt"]}_default" />'
            )
            tpls.append(
                f'            <el-option label="{s["title"]}自动开跑" value="{s["tt"]}_autostart" />'
            )
        t = t.replace(
            '<el-option label="动态MPPT自动开跑" value="dynamicmppt_autostart" />\n          </el-select>',
            '<el-option label="动态MPPT自动开跑" value="dynamicmppt_autostart" />\n'
            + "\n".join(tpls)
            + "\n          </el-select>",
            1,
        )
        tmpl_obj = []
        for s in SPECS:
            tmpl_obj.append(
                f"  {s['tt']}_default: {{ widgets: {{}}, auto_append: true, auto_start: false }},"
            )
            tmpl_obj.append(
                f"  {s['tt']}_autostart: {{ widgets: {{}}, auto_append: true, auto_start: true }},"
            )
        t = t.replace(
            "  dynamicmppt_default: { widgets: {}, auto_append: true, auto_start: false },\n  dynamicmppt_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
            "  dynamicmppt_default: { widgets: {}, auto_append: true, auto_start: false },\n  dynamicmppt_autostart: { widgets: {}, auto_append: true, auto_start: true },\n"
            + "\n".join(tmpl_obj)
            + "\n}",
            1,
        )
        branches = []
        for s in SPECS:
            branches.append(
                f"  }} else if (form.templateId.startsWith('{s['tt']}')) {{\n    form.testType = '{s['tt']}'"
            )
        t = t.replace(
            "  } else if (form.templateId.startsWith('dynamicmppt')) {\n    form.testType = 'dynamicmppt'\n  } else if (",
            "  } else if (form.templateId.startsWith('dynamicmppt')) {\n    form.testType = 'dynamicmppt'\n"
            + "\n".join(branches)
            + "\n  } else if (",
            1,
        )
        type_ors = " ||\n      ".join(f"form.testType === '{s['tt']}'" for s in SPECS)
        t = t.replace(
            "      form.testType === 'dynamicmppt') &&\n",
            "      form.testType === 'dynamicmppt' ||\n      " + type_ors + ") &&\n",
            1,
        )
        syncs = []
        for s in SPECS:
            syncs.append(
                f"""    }} else if (tt === '{s["tt"]}' && !form.templateId.startsWith('{s["tt"]}')) {{
      form.templateId = '{s["tt"]}_default'
      form.autoAppend = true
      form.autoStart = false"""
            )
        t = t.replace(
            """    } else if (tt === 'dynamicmppt' && !form.templateId.startsWith('dynamicmppt')) {
      form.templateId = 'dynamicmppt_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
            """    } else if (tt === 'dynamicmppt' && !form.templateId.startsWith('dynamicmppt')) {
      form.templateId = 'dynamicmppt_default'
      form.autoAppend = true
      form.autoStart = false
"""
            + "\n".join(syncs)
            + "\n    } else if (\n",
            1,
        )
        starts = " ||\n        ".join(f"form.templateId.startsWith('{s['tt']}')" for s in SPECS)
        t = t.replace(
            "        form.templateId.startsWith('dynamicmppt'))\n",
            "        form.templateId.startsWith('dynamicmppt') ||\n        " + starts + ")\n",
            1,
        )
        # nested ternary for display name - append before final 过载联调
        nested = ""
        for s in SPECS:
            nested += f"                                          : tt === '{s['tt']}'\n                                            ? '{s['title']}联调'\n"
        t = t.replace(
            """                                            : tt === 'dynamicmppt'
                                              ? '动态MPPT联调'
                                              : '过载联调'
""",
            """                                            : tt === 'dynamicmppt'
                                              ? '动态MPPT联调'
"""
            + nested
            + "                                              : '过载联调'\n",
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok job list")
    else:
        print("job list already")

    # docs
    p = IOT / "docs/IOT-Solar自动化试验线上版方案.md"
    t = p.read_text(encoding="utf-8")
    t = t.replace(
        "过载…电压适应性/ROCOF/快速电压变化已完成 → **LVRT + 相角突变 + 动态MPPT已接入（待联调；Auto_Test主队列收口）**",
        "**Auto_Test 全队列已接入（含功率/无功族；待联调）**",
        1,
    )
    t = t.replace(
        "开测表单 schema：`app/services/solar_test_schemas/`（已支持至 `lvrt` / `phasejump` / `dynamicmppt`，覆盖 Auto_Test 主队列）。",
        "开测表单 schema：`app/services/solar_test_schemas/`（已覆盖 Auto_Test 全队列，含无功能力范围/定无功/无功注入/无功精度/有功调度/静态QU/动态QU/Test_PU/静态·动态 Cos(φ)/Cos(φ)_Brazil）。",
        1,
    )
    p.write_text(t, encoding="utf-8")
    print("ok docs")

    # tests - one combined smoke file
    cases = "\n".join(
        f'    ("{s["tt"]}", "{s["title"]}", "{s["s3"][0]}"),' for s in SPECS
    )
    (IOT / "tests/test_solar_power_family_schema.py").write_text(
        f'''# -*- coding: utf-8 -*-
"""功率/无功族 11 项 schema / Blockly 冒烟。"""
import pytest
from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import field_names_for_step
from app.services.solar_test_schemas import list_supported_test_types, load_test_schema

CASES = [
{cases}
]


@pytest.mark.parametrize("tt,title,key", CASES)
def test_power_family_supported(tt, title, key):
    assert tt in list_supported_test_types()
    assert normalize_test_type(title) == tt
    load_test_schema.cache_clear()
    schema = load_test_schema(tt)
    assert schema["testType"] == tt
    names = {{f["name"] for f in schema["fields"]}}
    assert key in names
    steps = flow_steps_for_test_type(tt)
    assert [s["blockly_name"] for s in steps] == [
        f"solar_{{tt}}_s1",
        f"solar_{{tt}}_s2",
        f"solar_{{tt}}_s3",
        f"solar_{{tt}}_s4",
    ]
    assert key in field_names_for_step(f"solar_{{tt}}_s3")
''',
        encoding="utf-8",
    )
    print("ok tests")

    # handoff
    p = SOLAR / "utils/iot_ui_handoff.py"
    t = p.read_text(encoding="utf-8")
    if f'resolve_{SPECS[0]["tt"]}_ui' not in t:
        type_map = []
        for s in SPECS:
            for a in s["aliases"]:
                type_map.append(f'        "{a}": ("{s["title"]}", "{s["tt"]}"),')
                low = a.lower()
                if low != a:
                    type_map.append(f'        "{low}": ("{s["title"]}", "{s["tt"]}"),')
        t = t.replace(
            '        "动态mppt": ("动态MPPT", "dynamicmppt"),\n    }\n',
            '        "动态mppt": ("动态MPPT", "dynamicmppt"),\n'
            + "\n".join(type_map)
            + "\n    }\n",
            1,
        )
        # ctor params - both class and factory
        param_lines = []
        assign_lines = []
        factory_params = []
        factory_pass = []
        handlers = []
        for s in SPECS:
            param_lines.append(
                f"        resolve_{s['tt']}_ui: Optional[Callable[[], Any]] = None,\n"
                f"        {s['tt']}_append: Optional[Callable[[], None]] = None,"
            )
            assign_lines.append(
                f"        self.resolve_{s['tt']}_ui = resolve_{s['tt']}_ui\n"
                f"        self.{s['tt']}_append = {s['tt']}_append"
            )
            factory_params.append(
                f"    resolve_{s['tt']}_ui: Optional[Callable[[], Any]] = None,\n"
                f"    {s['tt']}_append: Optional[Callable[[], None]] = None,"
            )
            factory_pass.append(
                f"        resolve_{s['tt']}_ui=resolve_{s['tt']}_ui,\n"
                f"        {s['tt']}_append={s['tt']}_append,"
            )
            handlers.append(
                f'''        if handler_key == "{s["tt"]}":
            return {{
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_{s["tt"]}_ui,
                "append": self.{s["tt"]}_append,
                "label": "{s["title"]}",
            }}'''
            )
        t = t.replace(
            """        resolve_dynamicmppt_ui: Optional[Callable[[], Any]] = None,
        dynamicmppt_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
            """        resolve_dynamicmppt_ui: Optional[Callable[[], Any]] = None,
        dynamicmppt_append: Optional[Callable[[], None]] = None,
"""
            + "\n".join(param_lines)
            + """
        start_test: Optional[Callable[[], None]] = None,
""",
            1,
        )
        t = t.replace(
            """        self.resolve_dynamicmppt_ui = resolve_dynamicmppt_ui
        self.dynamicmppt_append = dynamicmppt_append
        self.start_test = start_test
""",
            """        self.resolve_dynamicmppt_ui = resolve_dynamicmppt_ui
        self.dynamicmppt_append = dynamicmppt_append
"""
            + "\n".join(assign_lines)
            + """
        self.start_test = start_test
""",
            1,
        )
        t = t.replace(
            '''        if handler_key == "dynamicmppt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_dynamicmppt_ui,
                "append": self.dynamicmppt_append,
                "label": "动态MPPT",
            }
        return None
''',
            '''        if handler_key == "dynamicmppt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_dynamicmppt_ui,
                "append": self.dynamicmppt_append,
                "label": "动态MPPT",
            }
'''
            + "\n".join(handlers)
            + """
        return None
""",
            1,
        )
        widget_list = ",\n                ".join(f'"{x}"' for x in tts)
        t = t.replace(
            '''                "lvrt",
                "phasejump",
                "dynamicmppt",
            ) and isinstance(widgets_for_ui, dict):
''',
            '''                "lvrt",
                "phasejump",
                "dynamicmppt",
                '''
            + widget_list
            + """,
            ) and isinstance(widgets_for_ui, dict):
""",
            1,
        )
        t = t.replace(
            '''                    "lvrt",
                    "phasejump",
                    "dynamicmppt",
                ) and isinstance(widgets, dict):
''',
            '''                    "lvrt",
                    "phasejump",
                    "dynamicmppt",
                    '''
            + widget_list.replace("\n                ", "\n                    ")
            + """,
                ) and isinstance(widgets, dict):
""",
            1,
        )
        t = t.replace(
            """    resolve_dynamicmppt_ui: Optional[Callable[[], Any]] = None,
    dynamicmppt_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
            """    resolve_dynamicmppt_ui: Optional[Callable[[], Any]] = None,
    dynamicmppt_append: Optional[Callable[[], None]] = None,
"""
            + "\n".join(factory_params)
            + """
    start_test: Optional[Callable[[], None]] = None,
""",
            1,
        )
        t = t.replace(
            """        resolve_dynamicmppt_ui=resolve_dynamicmppt_ui,
        dynamicmppt_append=dynamicmppt_append,
        start_test=start_test,
""",
            """        resolve_dynamicmppt_ui=resolve_dynamicmppt_ui,
        dynamicmppt_append=dynamicmppt_append,
"""
            + "\n".join(factory_pass)
            + """
        start_test=start_test,
""",
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok handoff")
    else:
        print("handoff already")

    # runner
    runner_aliases = []
    for s in SPECS:
        for a in s["aliases"]:
            runner_aliases.append(f'        "{a.lower() if any(c.isascii() and c.isalpha() for c in a) else a}",')
            # also keep chinese originals that lower changes Latin parts
            low = a.lower()
            if low != a:
                runner_aliases.append(f'        "{low}",')
    # dedupe preserve order
    seen = set()
    uniq = []
    for line in runner_aliases:
        if line not in seen:
            seen.add(line)
            uniq.append(line)
    _repl(
        SOLAR / "agent/runners/__init__.py",
        '''        "dynamicmppt",
        "dynamic_mppt",
        "动态mppt",
    ):
''',
        '''        "dynamicmppt",
        "dynamic_mppt",
        "动态mppt",
'''
        + "\n".join(uniq)
        + """
    ):
""",
        label="runner",
    )

    # SCPI
    p = SOLAR / "SCPITestWave.py"
    t = p.read_text(encoding="utf-8")
    if f'resolve_{SPECS[0]["tt"]}_ui' not in t:
        defs = []
        kwargs = []
        for s in SPECS:
            defs.append(
                f'''                def _resolve_{s["tt"]}_ui():
                    return globals().get("{s["ui"]}")
'''
            )
            kwargs.append(
                f'                    resolve_{s["tt"]}_ui=_resolve_{s["tt"]}_ui,\n'
                f'                    {s["tt"]}_append={s["append"]},'
            )
        t = t.replace(
            '''                def _resolve_dynamicmppt_ui():
                    return globals().get("uiThaiDynamicMPPT")

                def _iot_get_run_status():
''',
            '''                def _resolve_dynamicmppt_ui():
                    return globals().get("uiThaiDynamicMPPT")

'''
            + "\n".join(defs)
            + """
                def _iot_get_run_status():
""",
            1,
        )
        t = t.replace(
            """                    resolve_dynamicmppt_ui=_resolve_dynamicmppt_ui,
                    dynamicmppt_append=thaidynamicmpptAppend,
                    start_test=RunProjectPush,
""",
            """                    resolve_dynamicmppt_ui=_resolve_dynamicmppt_ui,
                    dynamicmppt_append=thaidynamicmpptAppend,
"""
            + "\n".join(kwargs)
            + """
                    start_test=RunProjectPush,
""",
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok SCPI")
    else:
        print("SCPI already")

    # runner test
    p = SOLAR / "tests/test_agent_runner_fixedpf.py"
    t = p.read_text(encoding="utf-8")
    if f'get_runner("{SPECS[0]["tt"]}"' not in t:
        adds = []
        asserts = []
        n = 34
        for s in SPECS:
            adds.append(
                f'    r{n} = get_runner("{s["tt"]}", dry_run=True, execution_mode="handoff")'
            )
            asserts.append(f"    assert r{n} is not None")
            n += 1
            adds.append(
                f'    r{n} = get_runner("{s["title"]}", dry_run=True, execution_mode="handoff")'
            )
            asserts.append(f"    assert r{n} is not None")
            n += 1
        t = t.replace(
            '''    r32 = get_runner("dynamicmppt", dry_run=True, execution_mode="handoff")
    r33 = get_runner("动态MPPT", dry_run=True, execution_mode="handoff")
''',
            '''    r32 = get_runner("dynamicmppt", dry_run=True, execution_mode="handoff")
    r33 = get_runner("动态MPPT", dry_run=True, execution_mode="handoff")
'''
            + "\n".join(adds)
            + "\n",
            1,
        )
        t = t.replace(
            "    assert r33 is not None",
            "    assert r33 is not None\n" + "\n".join(asserts),
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok runner test")
    else:
        print("runner test already")


def main() -> None:
    write_schemas()
    wire()
    print("power family 11 done")


if __name__ == "__main__":
    main()
