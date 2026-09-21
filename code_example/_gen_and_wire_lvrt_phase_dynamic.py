# -*- coding: utf-8 -*-
"""生成并接入：低电压穿越 / 相角突变 / 动态MPPT（时序共用基座）。"""
from __future__ import annotations

import json
from pathlib import Path

SOLAR = Path(r"E:/solarautotestnewui")
IOT = Path(r"E:/IOT/iot")
OVERLOAD_SW = SOLAR / "utils" / "iot_overload_schema_data.json"
IOT_OVERLOAD = IOT / "app/services/solar_test_schemas/overload_fields.json"

_LVRT_DEFAULT = [
    {
        "enabled": True,
        "label": "LVRT 0.20 p.u.",
        "t_pre": 1,
        "t_pre_unit": "秒",
        "t_dwell": 0.15,
        "t_dwell_unit": "秒",
        "t_post": 3,
        "t_post_unit": "秒",
        "u_pu": 0.2,
        "repeats": 1,
    }
]
_PHASE_DEFAULT = [
    {
        "enabled": True,
        "label": "相角 +10°",
        "t_pre": 1,
        "t_pre_unit": "秒",
        "t_dwell": 0.5,
        "t_dwell_unit": "秒",
        "t_post": 2,
        "t_post_unit": "秒",
        "phase_deg": 10,
        "repeats": 1,
    },
    {
        "enabled": False,
        "label": "相角 -10°",
        "t_pre": 1,
        "t_pre_unit": "秒",
        "t_dwell": 0.5,
        "t_dwell_unit": "秒",
        "t_post": 2,
        "t_post_unit": "秒",
        "phase_deg": -10,
        "repeats": 1,
    },
]


def _field(name, label, typ, group, default=None, options=None):
    return {
        "name": name,
        "label": label,
        "type": typ,
        "group": group,
        "default": default,
        "options": options or [],
    }


def _base_fields() -> list:
    fields = [
        _field("checkBox_S1", "启用步骤1 AC/DC", "checkbox", "step1_ac", True),
        _field("comboBox_S1_AC", "交流输出", "select", "step1_ac", "开启", ["开启", "关闭"]),
        _field("textEdit_S1_AC_VOLT", "交流电压1", "text", "step1_ac", "230"),
        _field("textEdit_S1_AC_VOLT_2", "交流电压2", "text", "step1_ac", "230"),
        _field("textEdit_S1_AC_VOLT_3", "交流电压3", "text", "step1_ac", "230"),
        _field("textEdit_S1_AC_FR", "频率(Hz)", "text", "step1_ac", "50"),
        _field("comboBox_S1_AC_2", "相制", "select", "step1_ac", "三相", ["单相", "三相"]),
        _field("textEdit_S1_ACWaitTIME", "交流输出等待", "text", "step1_ac", "3"),
        _field("comboBox_S1_ACWaitTIME", "等待单位", "select", "step1_ac", "秒", ["秒", "分钟", "毫秒"]),
        _field("textEdit_S1_TIME", "启机等待", "text", "step1_ac", "5"),
        _field("comboBox_S1_TIME", "启机单位", "select", "step1_ac", "分钟", ["分钟", "秒", "毫秒"]),
    ]
    for i in range(1, 5):
        fields.append(_field(f"checkBox_S1_DC{i}", f"直流电源{i}", "checkbox", "step1_dc", True))
        fields.append(
            _field(f"comboBox_S1_DC{i}", f"DC{i}开关", "select", "step1_dc", "开启", ["开启", "关闭"])
        )
        for suf, lab, d in (
            ("VOLT", "Vmp", "650"),
            ("CURR", "Imp", "12"),
            ("Voc", "Voc", "720"),
            ("Isc", "Isc", "13"),
            ("PF", "功率(%)", "100"),
        ):
            fields.append(_field(f"textEdit_S1_DC{i}_{suf}", f"DC{i} {lab}", "text", "step1_dc", d))

    fields += [
        _field("checkBox_S2", "启用步骤2 功率分析仪", "checkbox", "step2_wt", True),
        _field("radio_wt", "功率分析仪", "radio", "step2_wt", True),
        _field("radio_dewetron", "德威创", "radio", "step2_wt", False),
        _field("radio_S2_WT3000", "WT3000", "radio", "step2_wt", True),
        _field("radio_S2_WT1800", "WT1800", "radio", "step2_wt", False),
        _field("radio_S2_WT1806E", "WT1806E", "radio", "step2_wt", False),
        _field("radio_S2_WT5000", "WT5000", "radio", "step2_wt", False),
        _field("checkBox_S_End", "启用关机", "checkbox", "step4_off", True),
        _field("comboBox_S_End_AC", "关机 AC", "select", "step4_off", "关闭", ["关闭", "开启"]),
    ]
    for i in range(1, 5):
        fields.append(_field(f"checkBox_S_End_DC{i}", f"关机 DC{i}", "checkbox", "step4_off", True))
        fields.append(
            _field(
                f"comboBox_S_End_DC{i}",
                f"关机 DC{i}开关",
                "select",
                "step4_off",
                "关闭",
                ["关闭", "开启"],
            )
        )
    return fields


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


def _groups(profile_title: str) -> list:
    return [
        {"id": "step1_ac", "title": "① AC 电源"},
        {"id": "step1_dc", "title": "① DC 电源"},
        {"id": "step2_wt", "title": "② 功率分析仪"},
        {"id": "step2_dew", "title": "② 德威创"},
        {"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"},
        {"id": "step3_profile", "title": f"③ {profile_title}"},
        {"id": "step4_off", "title": "④ 关机设置"},
        {"id": "other", "title": "其它"},
    ]


def gen_lvrt() -> dict:
    fields = _base_fields()
    fields.append(_field("checkBox_S3", "启用时序工况", "checkbox", "step3_profile", True))
    for i in range(1, 5):
        fields.append(_field(f"checkBox_S3_DC{i}", f"工况 DC{i}", "checkbox", "step3_profile", True))
    fields.append(
        _field(
            "TIMING_PROFILE_JSON",
            "时序工况 JSON",
            "text",
            "step3_profile",
            json.dumps(_LVRT_DEFAULT, ensure_ascii=False),
        )
    )
    schema = {
        "testType": "lvrt",
        "title": "低电压穿越",
        "version": 1,
        "groups": _groups("LVRT 电压阶跃时序"),
        "fields": fields,
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def gen_phasejump() -> dict:
    fields = _base_fields()
    fields.append(_field("checkBox_S3", "启用时序工况", "checkbox", "step3_profile", True))
    for i in range(1, 5):
        fields.append(_field(f"checkBox_S3_DC{i}", f"工况 DC{i}", "checkbox", "step3_profile", True))
    fields.append(
        _field(
            "TIMING_PROFILE_JSON",
            "时序工况 JSON",
            "text",
            "step3_profile",
            json.dumps(_PHASE_DEFAULT, ensure_ascii=False),
        )
    )
    schema = {
        "testType": "phasejump",
        "title": "相角突变",
        "version": 1,
        "groups": _groups("相角突变时序"),
        "fields": fields,
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def gen_dynamicmppt() -> dict:
    fields = _base_fields()
    fields.append(_field("checkBox_S3", "启用动态MPPT", "checkbox", "step3_profile", True))
    for i in range(1, 5):
        fields.append(
            _field(f"checkBox_S3_DC{i}", f"工况 DC{i}", "checkbox", "step3_profile", i == 1)
        )
    fields += [
        _field("textEdit_S3_initial_setup_s", "初始稳定(s)", "text", "step3_profile", "300"),
        _field("textEdit_S3_vmp", "STC Vmp", "text", "step3_profile", "100"),
        _field("textEdit_S3_pmpp", "STC Pmpp", "text", "step3_profile", "600"),
        _field("comboBox_S3_ff", "填充因子", "select", "step3_profile", "c-Si", ["c-Si", "a-Si", "Thin Film"]),
        _field("textEdit_S3_wt_filename", "录波文件名", "text", "step3_profile", "DynamicMPPT_BR"),
        _field("EN50530_BUNDLE_JSON", "EN50530 工况包 JSON", "text", "step3_profile", ""),
    ]
    schema = {
        "testType": "dynamicmppt",
        "title": "动态MPPT",
        "version": 1,
        "groups": _groups("EN50530 动态MPPT"),
        "fields": fields,
        "jobFlags": {"auto_append": True, "auto_start": True, "wait_finish": True},
    }
    return _merge_wt(schema)


def write_schemas() -> None:
    for schema, sw_name, iot_name in (
        (gen_lvrt(), "iot_lvrt_schema_data.json", "lvrt_fields.json"),
        (gen_phasejump(), "iot_phasejump_schema_data.json", "phasejump_fields.json"),
        (gen_dynamicmppt(), "iot_dynamicmppt_schema_data.json", "dynamicmppt_fields.json"),
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
    if "lvrt_fields.json" not in t:
        old = '''        "快速电压变化": "rapidvolt_fields.json",
    }
'''
        new = '''        "快速电压变化": "rapidvolt_fields.json",
        "lvrt": "lvrt_fields.json",
        "lowvoltage_ride_through": "lvrt_fields.json",
        "低电压穿越": "lvrt_fields.json",
        "phasejump": "phasejump_fields.json",
        "phase_jump": "phasejump_fields.json",
        "相角突变": "phasejump_fields.json",
        "dynamicmppt": "dynamicmppt_fields.json",
        "dynamic_mppt": "dynamicmppt_fields.json",
        "动态mppt": "dynamicmppt_fields.json",
    }
'''
        t = t.replace(old, new, 1)
        t = t.replace(
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun", "staticmppt", "frequencyadaptability", "voltageadaptability", "rocof", "rapidvolt"]',
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun", "staticmppt", "frequencyadaptability", "voltageadaptability", "rocof", "rapidvolt", "lvrt", "phasejump", "dynamicmppt"]',
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok schema init")
    else:
        print("schema init already")

    p = IOT / "app/services/solar_blockly_catalog.py"
    t = p.read_text(encoding="utf-8")
    if '"lvrt":' not in t:
        marker = '''            {"blockly_name": "solar_rapidvolt_s4", "com_name": "快速电压变化步骤4 关机", "colour": 150},
        ),
    },
}
'''
        insert = '''            {"blockly_name": "solar_rapidvolt_s4", "com_name": "快速电压变化步骤4 关机", "colour": 150},
        ),
    },
    "lvrt": {
        "com_name": "低电压穿越半自动",
        "blockly_name": "solar_lvrt",
        "label": "低电压穿越",
        "colour": 160,
        "aliases": ("lvrt", "lowvoltage_ride_through", "低电压穿越", "LVRT", "低电压穿越半自动"),
        "steps": (
            {"blockly_name": "solar_lvrt_s1", "com_name": "LVRT步骤1 AC/DC", "colour": 160},
            {"blockly_name": "solar_lvrt_s2", "com_name": "LVRT步骤2 分析仪", "colour": 170},
            {"blockly_name": "solar_lvrt_s3", "com_name": "LVRT步骤3 时序", "colour": 180},
            {"blockly_name": "solar_lvrt_s4", "com_name": "LVRT步骤4 关机", "colour": 190},
        ),
    },
    "phasejump": {
        "com_name": "相角突变半自动",
        "blockly_name": "solar_phasejump",
        "label": "相角突变",
        "colour": 200,
        "aliases": ("phasejump", "phase_jump", "相角突变", "相角突变半自动"),
        "steps": (
            {"blockly_name": "solar_phasejump_s1", "com_name": "相角突变步骤1 AC/DC", "colour": 200},
            {"blockly_name": "solar_phasejump_s2", "com_name": "相角突变步骤2 分析仪", "colour": 210},
            {"blockly_name": "solar_phasejump_s3", "com_name": "相角突变步骤3 时序", "colour": 220},
            {"blockly_name": "solar_phasejump_s4", "com_name": "相角突变步骤4 关机", "colour": 230},
        ),
    },
    "dynamicmppt": {
        "com_name": "动态MPPT半自动",
        "blockly_name": "solar_dynamicmppt",
        "label": "动态MPPT",
        "colour": 240,
        "aliases": ("dynamicmppt", "dynamic_mppt", "动态MPPT", "动态mppt", "动态MPPT半自动"),
        "steps": (
            {"blockly_name": "solar_dynamicmppt_s1", "com_name": "动态MPPT步骤1 AC/DC", "colour": 240},
            {"blockly_name": "solar_dynamicmppt_s2", "com_name": "动态MPPT步骤2 分析仪", "colour": 250},
            {"blockly_name": "solar_dynamicmppt_s3", "com_name": "动态MPPT步骤3 工况", "colour": 260},
            {"blockly_name": "solar_dynamicmppt_s4", "com_name": "动态MPPT步骤4 关机", "colour": 270},
        ),
    },
}
'''
        if marker not in t:
            raise SystemExit("catalog rapidvolt tail missing")
        p.write_text(t.replace(marker, insert, 1), encoding="utf-8")
        print("ok catalog")
    else:
        print("catalog already")

    p = IOT / "app/services/solar_blockly_detail.py"
    t = p.read_text(encoding="utf-8")
    if "solar_lvrt_s1" not in t:
        old = '''    "solar_rapidvolt_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
        new = '''    "solar_rapidvolt_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
    # ── 低电压穿越 ──
    "solar_lvrt_s1": (
        "checkBox_S1", "comboBox_S1_AC", "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT", "textEdit_S1_AC_VOLT_2", "textEdit_S1_AC_VOLT_3",
        "textEdit_S1_AC_FR", "checkBox_S1_DC1",
        "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME", "comboBox_S1_TIME",
    ),
    "solar_lvrt_s2": (
        "checkBox_S2", "radio_wt", "radio_dewetron",
        "radio_S2_WT3000", "radio_S2_WT1800", "radio_S2_WT1806E", "radio_S2_WT5000",
    ),
    "solar_lvrt_s3": (
        "checkBox_S3", "checkBox_S3_DC1", "TIMING_PROFILE_JSON",
    ),
    "solar_lvrt_s4": ("checkBox_S_End", "comboBox_S_End_AC"),
    # ── 相角突变 ──
    "solar_phasejump_s1": (
        "checkBox_S1", "comboBox_S1_AC", "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT", "textEdit_S1_AC_FR", "checkBox_S1_DC1",
        "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME", "comboBox_S1_TIME",
    ),
    "solar_phasejump_s2": (
        "checkBox_S2", "radio_wt", "radio_dewetron",
        "radio_S2_WT3000", "radio_S2_WT1800", "radio_S2_WT1806E", "radio_S2_WT5000",
    ),
    "solar_phasejump_s3": (
        "checkBox_S3", "checkBox_S3_DC1", "TIMING_PROFILE_JSON",
    ),
    "solar_phasejump_s4": ("checkBox_S_End", "comboBox_S_End_AC"),
    # ── 动态MPPT ──
    "solar_dynamicmppt_s1": (
        "checkBox_S1", "comboBox_S1_AC", "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT", "textEdit_S1_AC_FR", "checkBox_S1_DC1",
        "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME", "comboBox_S1_TIME",
    ),
    "solar_dynamicmppt_s2": (
        "checkBox_S2", "radio_wt", "radio_dewetron",
        "radio_S2_WT3000", "radio_S2_WT1800", "radio_S2_WT1806E", "radio_S2_WT5000",
    ),
    "solar_dynamicmppt_s3": (
        "checkBox_S3", "checkBox_S3_DC1",
        "textEdit_S3_vmp", "textEdit_S3_pmpp", "comboBox_S3_ff",
        "EN50530_BUNDLE_JSON",
    ),
    "solar_dynamicmppt_s4": ("checkBox_S_End", "comboBox_S_End_AC"),
}
'''
        if old not in t:
            raise SystemExit("detail rapidvolt_s4 missing")
        p.write_text(t.replace(old, new, 1), encoding="utf-8")
        print("ok detail")
    else:
        print("detail already")

    _repl(
        IOT / "app/services/solar_experiment_service.py",
        '''            "rocof",
            "rapidvolt",
        ):''',
        '''            "rocof",
            "rapidvolt",
            "lvrt",
            "phasejump",
            "dynamicmppt",
        ):''',
        label="experiment",
    )

    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  快速电压变化: '快速电压变化',
}
""",
        """  快速电压变化: '快速电压变化',
  lvrt: '低电压穿越',
  lowvoltage_ride_through: '低电压穿越',
  低电压穿越: '低电压穿越',
  phasejump: '相角突变',
  phase_jump: '相角突变',
  相角突变: '相角突变',
  dynamicmppt: '动态MPPT',
  dynamic_mppt: '动态MPPT',
  动态MPPT: '动态MPPT',
  动态mppt: '动态MPPT',
}
""",
        label="labels map",
    )
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  { value: 'rapidvolt', label: '快速电压变化' },
] as const
""",
        """  { value: 'rapidvolt', label: '快速电压变化' },
  { value: 'lvrt', label: '低电压穿越' },
  { value: 'phasejump', label: '相角突变' },
  { value: 'dynamicmppt', label: '动态MPPT' },
] as const
""",
        label="labels options",
    )
    _repl(
        IOT / "frontend/src/utils/solarBlockly.ts",
        """  { type: 'solar_rapidvolt', message0: '快速电压变化半自动%1', arg: 'solar_rapidvolt', colour: 120 },
] as const
""",
        """  { type: 'solar_rapidvolt', message0: '快速电压变化半自动%1', arg: 'solar_rapidvolt', colour: 120 },
  { type: 'solar_lvrt_s1', message0: 'LVRT步骤1 AC/DC%1', arg: 'solar_lvrt_s1', colour: 160 },
  { type: 'solar_lvrt_s2', message0: 'LVRT步骤2 分析仪%1', arg: 'solar_lvrt_s2', colour: 170 },
  { type: 'solar_lvrt_s3', message0: 'LVRT步骤3 时序%1', arg: 'solar_lvrt_s3', colour: 180 },
  { type: 'solar_lvrt_s4', message0: 'LVRT步骤4 关机%1', arg: 'solar_lvrt_s4', colour: 190 },
  { type: 'solar_lvrt', message0: '低电压穿越半自动%1', arg: 'solar_lvrt', colour: 160 },
  { type: 'solar_phasejump_s1', message0: '相角突变步骤1 AC/DC%1', arg: 'solar_phasejump_s1', colour: 200 },
  { type: 'solar_phasejump_s2', message0: '相角突变步骤2 分析仪%1', arg: 'solar_phasejump_s2', colour: 210 },
  { type: 'solar_phasejump_s3', message0: '相角突变步骤3 时序%1', arg: 'solar_phasejump_s3', colour: 220 },
  { type: 'solar_phasejump_s4', message0: '相角突变步骤4 关机%1', arg: 'solar_phasejump_s4', colour: 230 },
  { type: 'solar_phasejump', message0: '相角突变半自动%1', arg: 'solar_phasejump', colour: 200 },
  { type: 'solar_dynamicmppt_s1', message0: '动态MPPT步骤1 AC/DC%1', arg: 'solar_dynamicmppt_s1', colour: 240 },
  { type: 'solar_dynamicmppt_s2', message0: '动态MPPT步骤2 分析仪%1', arg: 'solar_dynamicmppt_s2', colour: 250 },
  { type: 'solar_dynamicmppt_s3', message0: '动态MPPT步骤3 工况%1', arg: 'solar_dynamicmppt_s3', colour: 260 },
  { type: 'solar_dynamicmppt_s4', message0: '动态MPPT步骤4 关机%1', arg: 'solar_dynamicmppt_s4', colour: 270 },
  { type: 'solar_dynamicmppt', message0: '动态MPPT半自动%1', arg: 'solar_dynamicmppt', colour: 240 },
] as const
""",
        label="blockly",
    )
    _repl(
        IOT / "frontend/src/views/solar/SolarOrderCreate.vue",
        """    | 'rocof'
    | 'rapidvolt',
""",
        """    | 'rocof'
    | 'rapidvolt'
    | 'lvrt'
    | 'phasejump'
    | 'dynamicmppt',
""",
        label="order create",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  'rocof',
  'rapidvolt',
])
""",
        """  'rocof',
  'rapidvolt',
  'lvrt',
  'phasejump',
  'dynamicmppt',
])
""",
        label="params types",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  if (
    blob.includes('solar_rapidvolt') ||
    blob.includes('rapidvolt') ||
    blob.includes('快速电压变化') ||
    blob.includes('rvc')
  ) {
    return 'rapidvolt'
  }
""",
        """  if (
    blob.includes('solar_rapidvolt') ||
    blob.includes('rapidvolt') ||
    blob.includes('快速电压变化') ||
    blob.includes('rvc')
  ) {
    return 'rapidvolt'
  }
  if (
    blob.includes('solar_lvrt') ||
    blob.includes('lvrt') ||
    blob.includes('低电压穿越')
  ) {
    return 'lvrt'
  }
  if (
    blob.includes('solar_phasejump') ||
    blob.includes('phasejump') ||
    blob.includes('phase_jump') ||
    blob.includes('相角突变')
  ) {
    return 'phasejump'
  }
  if (
    blob.includes('solar_dynamicmppt') ||
    blob.includes('dynamicmppt') ||
    blob.includes('动态MPPT') ||
    blob.includes('动态mppt')
  ) {
    return 'dynamicmppt'
  }
""",
        label="detect",
    )

    p = IOT / "frontend/src/views/solar/SolarJobList.vue"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            '<el-option label="快速电压变化" value="rapidvolt" />\n          </el-select>',
            '<el-option label="快速电压变化" value="rapidvolt" />\n            <el-option label="低电压穿越" value="lvrt" />\n            <el-option label="相角突变" value="phasejump" />\n            <el-option label="动态MPPT" value="dynamicmppt" />\n          </el-select>',
        ),
        (
            '<el-option label="快速电压变化自动开跑" value="rapidvolt_autostart" />\n          </el-select>',
            '<el-option label="快速电压变化自动开跑" value="rapidvolt_autostart" />\n            <el-option label="LVRT默认（只追加）" value="lvrt_default" />\n            <el-option label="LVRT自动开跑" value="lvrt_autostart" />\n            <el-option label="相角突变默认（只追加）" value="phasejump_default" />\n            <el-option label="相角突变自动开跑" value="phasejump_autostart" />\n            <el-option label="动态MPPT默认（只追加）" value="dynamicmppt_default" />\n            <el-option label="动态MPPT自动开跑" value="dynamicmppt_autostart" />\n          </el-select>',
        ),
        (
            "  rapidvolt_default: { widgets: {}, auto_append: true, auto_start: false },\n  rapidvolt_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
            "  rapidvolt_default: { widgets: {}, auto_append: true, auto_start: false },\n  rapidvolt_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  lvrt_default: { widgets: {}, auto_append: true, auto_start: false },\n  lvrt_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  phasejump_default: { widgets: {}, auto_append: true, auto_start: false },\n  phasejump_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  dynamicmppt_default: { widgets: {}, auto_append: true, auto_start: false },\n  dynamicmppt_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
        ),
        (
            """  } else if (form.templateId.startsWith('rapidvolt')) {
    form.testType = 'rapidvolt'
  } else if (
""",
            """  } else if (form.templateId.startsWith('rapidvolt')) {
    form.testType = 'rapidvolt'
  } else if (form.templateId.startsWith('lvrt')) {
    form.testType = 'lvrt'
  } else if (form.templateId.startsWith('phasejump')) {
    form.testType = 'phasejump'
  } else if (form.templateId.startsWith('dynamicmppt')) {
    form.testType = 'dynamicmppt'
  } else if (
""",
        ),
        (
            """      form.testType === 'rocof' ||
      form.testType === 'rapidvolt') &&
""",
            """      form.testType === 'rocof' ||
      form.testType === 'rapidvolt' ||
      form.testType === 'lvrt' ||
      form.testType === 'phasejump' ||
      form.testType === 'dynamicmppt') &&
""",
        ),
        (
            """    } else if (tt === 'rapidvolt' && !form.templateId.startsWith('rapidvolt')) {
      form.templateId = 'rapidvolt_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
            """    } else if (tt === 'rapidvolt' && !form.templateId.startsWith('rapidvolt')) {
      form.templateId = 'rapidvolt_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'lvrt' && !form.templateId.startsWith('lvrt')) {
      form.templateId = 'lvrt_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'phasejump' && !form.templateId.startsWith('phasejump')) {
      form.templateId = 'phasejump_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'dynamicmppt' && !form.templateId.startsWith('dynamicmppt')) {
      form.templateId = 'dynamicmppt_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
""",
        ),
        (
            """        form.templateId.startsWith('rocof') ||
        form.templateId.startsWith('rapidvolt'))
""",
            """        form.templateId.startsWith('rocof') ||
        form.templateId.startsWith('rapidvolt') ||
        form.templateId.startsWith('lvrt') ||
        form.templateId.startsWith('phasejump') ||
        form.templateId.startsWith('dynamicmppt'))
""",
        ),
        (
            """                                      : tt === 'rapidvolt'
                                        ? '快速电压变化联调'
                                        : '过载联调'
""",
            """                                      : tt === 'rapidvolt'
                                        ? '快速电压变化联调'
                                        : tt === 'lvrt'
                                          ? 'LVRT联调'
                                          : tt === 'phasejump'
                                            ? '相角突变联调'
                                            : tt === 'dynamicmppt'
                                              ? '动态MPPT联调'
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
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载/欠频升载/10min过压保护/巴西过欠频稳定性/静态MPPT/频率适应性/电压适应性已完成 → **ROCOF + 快速电压变化已接入（待联调）**",
            "过载…电压适应性/ROCOF/快速电压变化已完成 → **LVRT + 相角突变 + 动态MPPT已接入（待联调；Auto_Test主队列收口）**",
        ),
        (
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载** / **10min过压保护** / **巴西过欠频稳定性** / **静态MPPT** / **频率适应性** / **电压适应性** / **ROCOF保护** / **快速电压变化**（`auto_append` / `auto_start`）  ",
            "5. IOT 下发上述试验及 **低电压穿越** / **相角突变** / **动态MPPT**（`auto_append` / `auto_start`）  ",
        ),
        (
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`、10min过压保护 `voltprotect10min`、巴西过欠频稳定性 `guoqianpin_immun`、静态MPPT `staticmppt`、频率适应性 `frequencyadaptability`、电压适应性 `voltageadaptability`、ROCOF `rocof`、快速电压变化 `rapidvolt`  ",
            "- 类型：…、电压适应性 `voltageadaptability`、ROCOF `rocof`、快速电压变化 `rapidvolt`、低电压穿越 `lvrt`、相角突变 `phasejump`、动态MPPT `dynamicmppt`  ",
        ),
        (
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 / 10min过压保护 / 巴西过欠频稳定性 / 静态MPPT / 频率适应性 / 电压适应性 / ROCOF / 快速电压变化 参数 → 创建实验",
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填对应试验参数（含 LVRT / 相角突变 / 动态MPPT）→ 创建实验",
        ),
        (
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai` / `voltprotect10min` / `guoqianpin_immun` / `staticmppt` / `frequencyadaptability` / `voltageadaptability` / `rocof` / `rapidvolt`）。",
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持至 `lvrt` / `phasejump` / `dynamicmppt`，覆盖 Auto_Test 主队列）。",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"docs #{i} missing: {old[:80]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok docs")

    for tt, title, key_field in (
        ("lvrt", "低电压穿越", "TIMING_PROFILE_JSON"),
        ("phasejump", "相角突变", "TIMING_PROFILE_JSON"),
        ("dynamicmppt", "动态MPPT", "EN50530_BUNDLE_JSON"),
    ):
        alias = {"lvrt": "低电压穿越", "phasejump": "相角突变", "dynamicmppt": "动态MPPT"}[tt]
        (IOT / f"tests/test_solar_{tt}_schema.py").write_text(
            f'''# -*- coding: utf-8 -*-
"""{title} schema / Blockly 接入冒烟。"""
from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_{tt}_supported_and_aliases():
    assert "{tt}" in list_supported_test_types()
    assert normalize_test_type("{alias}") == "{tt}"
    load_test_schema.cache_clear()
    assert load_test_schema("{alias}")["testType"] == "{tt}"


def test_{tt}_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("{tt}")
    assert schema["testType"] == "{tt}"
    names = {{f["name"] for f in schema["fields"]}}
    assert "{key_field}" in names
    assert isinstance(build_job_widgets("{tt}", None), dict)


def test_{tt}_blockly_steps():
    steps = flow_steps_for_test_type("{tt}")
    assert [s["blockly_name"] for s in steps] == [
        "solar_{tt}_s1",
        "solar_{tt}_s2",
        "solar_{tt}_s3",
        "solar_{tt}_s4",
    ]
    assert "{key_field}" in field_names_for_step("solar_{tt}_s3")
    assert detail_fields_for("{tt}", "solar_{tt}_s3", widgets=build_job_widgets("{tt}", None))
''',
            encoding="utf-8",
        )
    print("ok tests")

    p = SOLAR / "utils/iot_ui_handoff.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_lvrt_ui" not in t:
        reps = [
            (
                '''        "快速电压变化": ("快速电压变化", "rapidvolt"),
    }
''',
                '''        "快速电压变化": ("快速电压变化", "rapidvolt"),
        "lvrt": ("低电压穿越", "lvrt"),
        "lowvoltage_ride_through": ("低电压穿越", "lvrt"),
        "低电压穿越": ("低电压穿越", "lvrt"),
        "phasejump": ("相角突变", "phasejump"),
        "phase_jump": ("相角突变", "phasejump"),
        "相角突变": ("相角突变", "phasejump"),
        "dynamicmppt": ("动态MPPT", "dynamicmppt"),
        "dynamic_mppt": ("动态MPPT", "dynamicmppt"),
        "动态MPPT": ("动态MPPT", "dynamicmppt"),
        "动态mppt": ("动态MPPT", "dynamicmppt"),
    }
''',
            ),
            (
                """        resolve_rapidvolt_ui: Optional[Callable[[], Any]] = None,
        rapidvolt_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
                """        resolve_rapidvolt_ui: Optional[Callable[[], Any]] = None,
        rapidvolt_append: Optional[Callable[[], None]] = None,
        resolve_lvrt_ui: Optional[Callable[[], Any]] = None,
        lvrt_append: Optional[Callable[[], None]] = None,
        resolve_phasejump_ui: Optional[Callable[[], Any]] = None,
        phasejump_append: Optional[Callable[[], None]] = None,
        resolve_dynamicmppt_ui: Optional[Callable[[], Any]] = None,
        dynamicmppt_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
            ),
            (
                """        self.resolve_rapidvolt_ui = resolve_rapidvolt_ui
        self.rapidvolt_append = rapidvolt_append
        self.start_test = start_test
""",
                """        self.resolve_rapidvolt_ui = resolve_rapidvolt_ui
        self.rapidvolt_append = rapidvolt_append
        self.resolve_lvrt_ui = resolve_lvrt_ui
        self.lvrt_append = lvrt_append
        self.resolve_phasejump_ui = resolve_phasejump_ui
        self.phasejump_append = phasejump_append
        self.resolve_dynamicmppt_ui = resolve_dynamicmppt_ui
        self.dynamicmppt_append = dynamicmppt_append
        self.start_test = start_test
""",
            ),
            (
                '''        if handler_key == "rapidvolt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_rapidvolt_ui,
                "append": self.rapidvolt_append,
                "label": "快速电压变化",
            }
        return None
''',
                '''        if handler_key == "rapidvolt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_rapidvolt_ui,
                "append": self.rapidvolt_append,
                "label": "快速电压变化",
            }
        if handler_key == "lvrt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_lvrt_ui,
                "append": self.lvrt_append,
                "label": "低电压穿越",
            }
        if handler_key == "phasejump":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_phasejump_ui,
                "append": self.phasejump_append,
                "label": "相角突变",
            }
        if handler_key == "dynamicmppt":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_dynamicmppt_ui,
                "append": self.dynamicmppt_append,
                "label": "动态MPPT",
            }
        return None
''',
            ),
            (
                '''                "rocof",
                "rapidvolt",
            ) and isinstance(widgets_for_ui, dict):
''',
                '''                "rocof",
                "rapidvolt",
                "lvrt",
                "phasejump",
                "dynamicmppt",
            ) and isinstance(widgets_for_ui, dict):
''',
            ),
            (
                '''                    "rocof",
                    "rapidvolt",
                ) and isinstance(widgets, dict):
''',
                '''                    "rocof",
                    "rapidvolt",
                    "lvrt",
                    "phasejump",
                    "dynamicmppt",
                ) and isinstance(widgets, dict):
''',
            ),
            (
                """    resolve_rapidvolt_ui: Optional[Callable[[], Any]] = None,
    rapidvolt_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
                """    resolve_rapidvolt_ui: Optional[Callable[[], Any]] = None,
    rapidvolt_append: Optional[Callable[[], None]] = None,
    resolve_lvrt_ui: Optional[Callable[[], Any]] = None,
    lvrt_append: Optional[Callable[[], None]] = None,
    resolve_phasejump_ui: Optional[Callable[[], Any]] = None,
    phasejump_append: Optional[Callable[[], None]] = None,
    resolve_dynamicmppt_ui: Optional[Callable[[], Any]] = None,
    dynamicmppt_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
            ),
            (
                """        resolve_rapidvolt_ui=resolve_rapidvolt_ui,
        rapidvolt_append=rapidvolt_append,
        start_test=start_test,
""",
                """        resolve_rapidvolt_ui=resolve_rapidvolt_ui,
        rapidvolt_append=rapidvolt_append,
        resolve_lvrt_ui=resolve_lvrt_ui,
        lvrt_append=lvrt_append,
        resolve_phasejump_ui=resolve_phasejump_ui,
        phasejump_append=phasejump_append,
        resolve_dynamicmppt_ui=resolve_dynamicmppt_ui,
        dynamicmppt_append=dynamicmppt_append,
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
        '''        "rapidvolt",
        "rapid_volt",
        "rvc",
        "快速电压变化",
    ):
''',
        '''        "rapidvolt",
        "rapid_volt",
        "rvc",
        "快速电压变化",
        "lvrt",
        "lowvoltage_ride_through",
        "低电压穿越",
        "phasejump",
        "phase_jump",
        "相角突变",
        "dynamicmppt",
        "dynamic_mppt",
        "动态mppt",
    ):
''',
        label="runner",
    )

    p = SOLAR / "SCPITestWave.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_lvrt_ui" not in t:
        old = '''                def _resolve_rapidvolt_ui():
                    return globals().get("uiThaiRapidVolt")

                def _iot_get_run_status():
'''
        new = '''                def _resolve_rapidvolt_ui():
                    return globals().get("uiThaiRapidVolt")

                def _resolve_lvrt_ui():
                    return globals().get("uiThaiLVRT")

                def _resolve_phasejump_ui():
                    return globals().get("uiThaiPhaseJump")

                def _resolve_dynamicmppt_ui():
                    return globals().get("uiThaiDynamicMPPT")

                def _iot_get_run_status():
'''
        t = t.replace(old, new, 1)
        old = """                    resolve_rapidvolt_ui=_resolve_rapidvolt_ui,
                    rapidvolt_append=thairapidvoltAppend,
                    start_test=RunProjectPush,
"""
        new = """                    resolve_rapidvolt_ui=_resolve_rapidvolt_ui,
                    rapidvolt_append=thairapidvoltAppend,
                    resolve_lvrt_ui=_resolve_lvrt_ui,
                    lvrt_append=thailvrtAppend,
                    resolve_phasejump_ui=_resolve_phasejump_ui,
                    phasejump_append=thaiphasejumpAppend,
                    resolve_dynamicmppt_ui=_resolve_dynamicmppt_ui,
                    dynamicmppt_append=thaidynamicmpptAppend,
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
    if 'get_runner("lvrt"' not in t:
        old = '''    r26 = get_runner("rapidvolt", dry_run=True, execution_mode="handoff")
    r27 = get_runner("快速电压变化", dry_run=True, execution_mode="handoff")
'''
        new = '''    r26 = get_runner("rapidvolt", dry_run=True, execution_mode="handoff")
    r27 = get_runner("快速电压变化", dry_run=True, execution_mode="handoff")
    r28 = get_runner("lvrt", dry_run=True, execution_mode="handoff")
    r29 = get_runner("低电压穿越", dry_run=True, execution_mode="handoff")
    r30 = get_runner("phasejump", dry_run=True, execution_mode="handoff")
    r31 = get_runner("相角突变", dry_run=True, execution_mode="handoff")
    r32 = get_runner("dynamicmppt", dry_run=True, execution_mode="handoff")
    r33 = get_runner("动态MPPT", dry_run=True, execution_mode="handoff")
'''
        t = t.replace(old, new, 1)
        t = t.replace(
            "assert r27 is not None",
            "assert r27 is not None\n    assert r28 is not None\n    assert r29 is not None\n    assert r30 is not None\n    assert r31 is not None\n    assert r32 is not None\n    assert r33 is not None",
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok runner test")
    else:
        print("runner test already")


def main() -> None:
    write_schemas()
    wire()
    print("lvrt + phasejump + dynamicmppt done")


if __name__ == "__main__":
    main()
