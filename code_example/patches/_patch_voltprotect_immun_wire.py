# -*- coding: utf-8 -*-
"""一次性：同时接入 10min过压保护 + 巴西过欠频稳定性。"""
from __future__ import annotations

from pathlib import Path

IOT = Path(r"E:/IOT/iot")
SOLAR = Path(r"E:/solarautotestnewui")


def _repl(path: Path, old: str, new: str, *, label: str) -> None:
    t = path.read_text(encoding="utf-8")
    if old not in t:
        raise SystemExit(f"missing in {path.name}: {label}\n---\n{old[:140]!r}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    print(f"ok {path.name} ({label})")


def patch_schema_init() -> None:
    p = IOT / "app/services/solar_test_schemas/__init__.py"
    t = p.read_text(encoding="utf-8")
    if "voltprotect10min_fields.json" in t and "guoqianpin_immun_fields.json" in t:
        print("schema init already")
        return
    old = '''        "qianpinshengzai": "qianpinshengzai_fields.json",
        "qianpin": "qianpinshengzai_fields.json",
        "uf_raise": "qianpinshengzai_fields.json",
        "欠频升载": "qianpinshengzai_fields.json",
    }
'''
    new = '''        "qianpinshengzai": "qianpinshengzai_fields.json",
        "qianpin": "qianpinshengzai_fields.json",
        "uf_raise": "qianpinshengzai_fields.json",
        "欠频升载": "qianpinshengzai_fields.json",
        "voltprotect10min": "voltprotect10min_fields.json",
        "voltprotect": "voltprotect10min_fields.json",
        "10min过压保护": "voltprotect10min_fields.json",
        "过压保护10min": "voltprotect10min_fields.json",
        "guoqianpin_immun": "guoqianpin_immun_fields.json",
        "guoqianpinimmun": "guoqianpin_immun_fields.json",
        "brazil_ovuf": "guoqianpin_immun_fields.json",
        "巴西过欠频稳定性": "guoqianpin_immun_fields.json",
        "过欠频稳定性": "guoqianpin_immun_fields.json",
    }
'''
    if old not in t:
        raise SystemExit("schema qianpin tail missing")
    t = t.replace(old, new, 1)
    t = t.replace(
        'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai"]',
        'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai", "qianpinshengzai", "voltprotect10min", "guoqianpin_immun"]',
        1,
    )
    p.write_text(t, encoding="utf-8")
    print("ok schema init")


def patch_catalog() -> None:
    p = IOT / "app/services/solar_blockly_catalog.py"
    t = p.read_text(encoding="utf-8")
    if '"voltprotect10min":' in t and '"guoqianpin_immun":' in t:
        print("catalog already")
        return
    marker = '''                "blockly_name": "solar_qianpinshengzai_s4",
                "com_name": "欠频升载步骤4 关机",
                "colour": 190,
            },
        ),
    },
}
'''
    insert = '''                "blockly_name": "solar_qianpinshengzai_s4",
                "com_name": "欠频升载步骤4 关机",
                "colour": 190,
            },
        ),
    },
    "voltprotect10min": {
        "com_name": "10min过压保护半自动",
        "blockly_name": "solar_voltprotect10min",
        "label": "10min过压保护",
        "colour": 200,
        "aliases": (
            "voltprotect10min",
            "voltprotect",
            "10min过压保护",
            "过压保护10min",
            "10min过压保护半自动",
        ),
        "steps": (
            {
                "blockly_name": "solar_voltprotect10min_s1",
                "com_name": "10min过压保护步骤1 AC/DC",
                "colour": 200,
            },
            {
                "blockly_name": "solar_voltprotect10min_s2",
                "com_name": "10min过压保护步骤2 分析仪",
                "colour": 210,
            },
            {
                "blockly_name": "solar_voltprotect10min_s3",
                "com_name": "10min过压保护步骤3 保护与恢复",
                "colour": 220,
            },
            {
                "blockly_name": "solar_voltprotect10min_s4",
                "com_name": "10min过压保护步骤4 关机",
                "colour": 230,
            },
        ),
    },
    "guoqianpin_immun": {
        "com_name": "巴西过欠频稳定性半自动",
        "blockly_name": "solar_guoqianpin_immun",
        "label": "巴西过欠频稳定性",
        "colour": 240,
        "aliases": (
            "guoqianpin_immun",
            "guoqianpinimmun",
            "brazil_ovuf",
            "巴西过欠频稳定性",
            "过欠频稳定性",
            "巴西过欠频稳定性半自动",
        ),
        "steps": (
            {
                "blockly_name": "solar_guoqianpin_immun_s1",
                "com_name": "巴西过欠频稳定性步骤1 AC/DC",
                "colour": 240,
            },
            {
                "blockly_name": "solar_guoqianpin_immun_s2",
                "com_name": "巴西过欠频稳定性步骤2 分析仪",
                "colour": 250,
            },
            {
                "blockly_name": "solar_guoqianpin_immun_s3",
                "com_name": "巴西过欠频稳定性步骤3 频率扫描",
                "colour": 260,
            },
            {
                "blockly_name": "solar_guoqianpin_immun_s4",
                "com_name": "巴西过欠频稳定性步骤4 关机",
                "colour": 270,
            },
        ),
    },
}
'''
    if marker not in t:
        raise SystemExit("catalog qianpin tail missing")
    p.write_text(t.replace(marker, insert, 1), encoding="utf-8")
    print("ok catalog")


def patch_detail() -> None:
    p = IOT / "app/services/solar_blockly_detail.py"
    t = p.read_text(encoding="utf-8")
    if "solar_voltprotect10min_s1" in t and "solar_guoqianpin_immun_s1" in t:
        print("detail already")
        return
    old = '''    "solar_qianpinshengzai_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
    new = '''    "solar_qianpinshengzai_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
    # ── 10min过压保护 ──
    "solar_voltprotect10min_s1": (
        "checkBox_S1",
        "comboBox_S1_AC",
        "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT",
        "textEdit_S1_AC_VOLT_2",
        "textEdit_S1_AC_VOLT_3",
        "textEdit_S1_AC_FR",
        "checkBox_S1_DC1",
        "comboBox_S1_DC1",
        "textEdit_S1_ACWaitTIME",
        "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME",
        "comboBox_S1_TIME",
    ),
    "solar_voltprotect10min_s2": (
        "checkBox_S2",
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "comboBox_DEW_MaxRefreshRate",
    ),
    "solar_voltprotect10min_s3": (
        "checkBox_S3",
        "textEdit_S3_AC_VOLT",
        "textEdit_S3_AC_VOLT_2",
        "textEdit_S3_AC_VOLT_3",
        "textEdit_S3_TIME",
        "comboBox_S3_TIME",
        "checkBox_S4",
        "textEdit_S4_AC_VOLT",
        "textEdit_S4_AC_VOLT_2",
        "textEdit_S4_AC_VOLT_3",
        "textEdit_S4_TIME",
        "comboBox_S4_TIME",
    ),
    "solar_voltprotect10min_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
    # ── 巴西过欠频稳定性 ──
    "solar_guoqianpin_immun_s1": (
        "checkBox_S1",
        "comboBox_S1_AC",
        "comboBox_S1_AC_2",
        "textEdit_S1_AC_VOLT",
        "textEdit_S1_AC_VOLT_2",
        "textEdit_S1_AC_VOLT_3",
        "textEdit_S1_AC_FR",
        "checkBox_S1_DC1",
        "comboBox_S1_DC1",
        "textEdit_S1_ACWaitTIME",
        "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME",
        "comboBox_S1_TIME",
    ),
    "solar_guoqianpin_immun_s2": (
        "checkBox_S2",
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "comboBox_DEW_MaxRefreshRate",
    ),
    "solar_guoqianpin_immun_s3": (
        "checkBox_S3",
        "textEdit_S3_AC_FR_Start",
        "textEdit_S3_AC_FR_End",
        "checkBox_S4",
        "textEdit_S4_AC_FR_Start",
        "textEdit_S4_AC_FR_End",
        "checkBox_S5",
        "textEdit_S5_AC_FR_Start",
        "textEdit_S5_AC_FR_End",
        "checkBox_S6",
        "checkBox_S7",
        "checkBox_S8",
        "checkBox_S9",
        "checkBox_S10",
        "checkBox_S11",
    ),
    "solar_guoqianpin_immun_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
    if old not in t:
        raise SystemExit("detail qianpin_s4 missing")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("ok detail")


def patch_experiment() -> None:
    _repl(
        IOT / "app/services/solar_experiment_service.py",
        '''            "guopinjiangzai",
            "qianpinshengzai",
        ):''',
        '''            "guopinjiangzai",
            "qianpinshengzai",
            "voltprotect10min",
            "guoqianpin_immun",
        ):''',
        label="experiment parsed",
    )


def patch_frontend() -> None:
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  qianpinshengzai: '欠频升载',
  qianpin: '欠频升载',
  uf_raise: '欠频升载',
  欠频升载: '欠频升载',
}
""",
        """  qianpinshengzai: '欠频升载',
  qianpin: '欠频升载',
  uf_raise: '欠频升载',
  欠频升载: '欠频升载',
  voltprotect10min: '10min过压保护',
  voltprotect: '10min过压保护',
  '10min过压保护': '10min过压保护',
  过压保护10min: '10min过压保护',
  guoqianpin_immun: '巴西过欠频稳定性',
  guoqianpinimmun: '巴西过欠频稳定性',
  brazil_ovuf: '巴西过欠频稳定性',
  巴西过欠频稳定性: '巴西过欠频稳定性',
  过欠频稳定性: '巴西过欠频稳定性',
}
""",
        label="labels map",
    )
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  { value: 'qianpinshengzai', label: '欠频升载' },
] as const
""",
        """  { value: 'qianpinshengzai', label: '欠频升载' },
  { value: 'voltprotect10min', label: '10min过压保护' },
  { value: 'guoqianpin_immun', label: '巴西过欠频稳定性' },
] as const
""",
        label="labels options",
    )
    _repl(
        IOT / "frontend/src/utils/solarBlockly.ts",
        """  { type: 'solar_qianpinshengzai', message0: '欠频升载半自动%1', arg: 'solar_qianpinshengzai', colour: 160 },
] as const
""",
        """  { type: 'solar_qianpinshengzai', message0: '欠频升载半自动%1', arg: 'solar_qianpinshengzai', colour: 160 },
  { type: 'solar_voltprotect10min_s1', message0: '10min过压保护步骤1 AC/DC%1', arg: 'solar_voltprotect10min_s1', colour: 200 },
  { type: 'solar_voltprotect10min_s2', message0: '10min过压保护步骤2 分析仪%1', arg: 'solar_voltprotect10min_s2', colour: 210 },
  { type: 'solar_voltprotect10min_s3', message0: '10min过压保护步骤3 保护与恢复%1', arg: 'solar_voltprotect10min_s3', colour: 220 },
  { type: 'solar_voltprotect10min_s4', message0: '10min过压保护步骤4 关机%1', arg: 'solar_voltprotect10min_s4', colour: 230 },
  { type: 'solar_voltprotect10min', message0: '10min过压保护半自动%1', arg: 'solar_voltprotect10min', colour: 200 },
  { type: 'solar_guoqianpin_immun_s1', message0: '巴西过欠频稳定性步骤1 AC/DC%1', arg: 'solar_guoqianpin_immun_s1', colour: 240 },
  { type: 'solar_guoqianpin_immun_s2', message0: '巴西过欠频稳定性步骤2 分析仪%1', arg: 'solar_guoqianpin_immun_s2', colour: 250 },
  { type: 'solar_guoqianpin_immun_s3', message0: '巴西过欠频稳定性步骤3 频率扫描%1', arg: 'solar_guoqianpin_immun_s3', colour: 260 },
  { type: 'solar_guoqianpin_immun_s4', message0: '巴西过欠频稳定性步骤4 关机%1', arg: 'solar_guoqianpin_immun_s4', colour: 270 },
  { type: 'solar_guoqianpin_immun', message0: '巴西过欠频稳定性半自动%1', arg: 'solar_guoqianpin_immun', colour: 240 },
] as const
""",
        label="blockly",
    )
    _repl(
        IOT / "frontend/src/views/solar/SolarOrderCreate.vue",
        """    | 'guopinjiangzai'
    | 'qianpinshengzai',
""",
        """    | 'guopinjiangzai'
    | 'qianpinshengzai'
    | 'voltprotect10min'
    | 'guoqianpin_immun',
""",
        label="order create",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  'guopinjiangzai',
  'qianpinshengzai',
])
""",
        """  'guopinjiangzai',
  'qianpinshengzai',
  'voltprotect10min',
  'guoqianpin_immun',
])
""",
        label="params types",
    )
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  if (
    blob.includes('solar_qianpinshengzai') ||
    blob.includes('qianpinshengzai') ||
    blob.includes('欠频升载') ||
    blob.includes('solar_qianpin')
  ) {
    return 'qianpinshengzai'
  }
""",
        """  if (
    blob.includes('solar_voltprotect10min') ||
    blob.includes('voltprotect10min') ||
    blob.includes('10min过压保护') ||
    blob.includes('过压保护10min')
  ) {
    return 'voltprotect10min'
  }
  if (
    blob.includes('solar_guoqianpin_immun') ||
    blob.includes('guoqianpin_immun') ||
    blob.includes('巴西过欠频稳定性') ||
    blob.includes('过欠频稳定性') ||
    blob.includes('brazil_ovuf')
  ) {
    return 'guoqianpin_immun'
  }
  if (
    blob.includes('solar_qianpinshengzai') ||
    blob.includes('qianpinshengzai') ||
    blob.includes('欠频升载') ||
    blob.includes('solar_qianpin')
  ) {
    return 'qianpinshengzai'
  }
""",
        label="detect pair",
    )

    p = IOT / "frontend/src/views/solar/SolarJobList.vue"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            '<el-option label="欠频升载" value="qianpinshengzai" />\n          </el-select>',
            '<el-option label="欠频升载" value="qianpinshengzai" />\n            <el-option label="10min过压保护" value="voltprotect10min" />\n            <el-option label="巴西过欠频稳定性" value="guoqianpin_immun" />\n          </el-select>',
        ),
        (
            '<el-option label="欠频升载自动开跑" value="qianpinshengzai_autostart" />\n          </el-select>',
            '<el-option label="欠频升载自动开跑" value="qianpinshengzai_autostart" />\n            <el-option label="10min过压保护默认（只追加）" value="voltprotect10min_default" />\n            <el-option label="10min过压保护自动开跑" value="voltprotect10min_autostart" />\n            <el-option label="巴西过欠频稳定性默认（只追加）" value="guoqianpin_immun_default" />\n            <el-option label="巴西过欠频稳定性自动开跑" value="guoqianpin_immun_autostart" />\n          </el-select>',
        ),
        (
            "  qianpinshengzai_default: { widgets: {}, auto_append: true, auto_start: false },\n  qianpinshengzai_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
            "  qianpinshengzai_default: { widgets: {}, auto_append: true, auto_start: false },\n  qianpinshengzai_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  voltprotect10min_default: { widgets: {}, auto_append: true, auto_start: false },\n  voltprotect10min_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  guoqianpin_immun_default: { widgets: {}, auto_append: true, auto_start: false },\n  guoqianpin_immun_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
        ),
        (
            """  } else if (form.templateId.startsWith('qianpinshengzai')) {
    form.testType = 'qianpinshengzai'
  } else if (
    (form.testType === 'antibackflow' ||
      form.testType === 'flicker' ||
      form.testType === 'harmonic' ||
      form.testType === 'fixedpf' ||
      form.testType === 'dccomponent' ||
      form.testType === 'reconnect' ||
      form.testType === 'ovuf' ||
      form.testType === 'guopinjiangzai' ||
      form.testType === 'qianpinshengzai') &&
    form.templateId.startsWith('overload')
  ) {
""",
            """  } else if (form.templateId.startsWith('qianpinshengzai')) {
    form.testType = 'qianpinshengzai'
  } else if (form.templateId.startsWith('voltprotect10min')) {
    form.testType = 'voltprotect10min'
  } else if (form.templateId.startsWith('guoqianpin_immun')) {
    form.testType = 'guoqianpin_immun'
  } else if (
    (form.testType === 'antibackflow' ||
      form.testType === 'flicker' ||
      form.testType === 'harmonic' ||
      form.testType === 'fixedpf' ||
      form.testType === 'dccomponent' ||
      form.testType === 'reconnect' ||
      form.testType === 'ovuf' ||
      form.testType === 'guopinjiangzai' ||
      form.testType === 'qianpinshengzai' ||
      form.testType === 'voltprotect10min' ||
      form.testType === 'guoqianpin_immun') &&
    form.templateId.startsWith('overload')
  ) {
""",
        ),
        (
            """    } else if (tt === 'qianpinshengzai' && !form.templateId.startsWith('qianpinshengzai')) {
      form.templateId = 'qianpinshengzai_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
      tt === 'overload' &&
      (form.templateId.startsWith('antibackflow') ||
        form.templateId.startsWith('flicker') ||
        form.templateId.startsWith('harmonic') ||
        form.templateId.startsWith('fixedpf') ||
        form.templateId.startsWith('dccomponent') ||
        form.templateId.startsWith('reconnect') ||
        form.templateId.startsWith('ovuf') ||
        form.templateId.startsWith('guopinjiangzai') ||
        form.templateId.startsWith('qianpinshengzai'))
    ) {
""",
            """    } else if (tt === 'qianpinshengzai' && !form.templateId.startsWith('qianpinshengzai')) {
      form.templateId = 'qianpinshengzai_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'voltprotect10min' && !form.templateId.startsWith('voltprotect10min')) {
      form.templateId = 'voltprotect10min_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'guoqianpin_immun' && !form.templateId.startsWith('guoqianpin_immun')) {
      form.templateId = 'guoqianpin_immun_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (
      tt === 'overload' &&
      (form.templateId.startsWith('antibackflow') ||
        form.templateId.startsWith('flicker') ||
        form.templateId.startsWith('harmonic') ||
        form.templateId.startsWith('fixedpf') ||
        form.templateId.startsWith('dccomponent') ||
        form.templateId.startsWith('reconnect') ||
        form.templateId.startsWith('ovuf') ||
        form.templateId.startsWith('guopinjiangzai') ||
        form.templateId.startsWith('qianpinshengzai') ||
        form.templateId.startsWith('voltprotect10min') ||
        form.templateId.startsWith('guoqianpin_immun'))
    ) {
""",
        ),
        (
            """                        : tt === 'qianpinshengzai'
                          ? '欠频升载联调'
                          : '过载联调'
""",
            """                        : tt === 'qianpinshengzai'
                          ? '欠频升载联调'
                          : tt === 'voltprotect10min'
                            ? '10min过压保护联调'
                            : tt === 'guoqianpin_immun'
                              ? '巴西过欠频稳定性联调'
                              : '过载联调'
""",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"joblist missing #{i}: {old[:100]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok job list")


def patch_docs() -> None:
    p = IOT / "docs/IOT-Solar自动化试验线上版方案.md"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载已完成 → **欠频升载已接入（待联调）**",
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频/过频降载/欠频升载已完成 → **10min过压保护 + 巴西过欠频稳定性已接入（待联调）**",
        ),
        (
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载**（`auto_append` / `auto_start`）  ",
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载** / **欠频升载** / **10min过压保护** / **巴西过欠频稳定性**（`auto_append` / `auto_start`）  ",
        ),
        (
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`  ",
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`、欠频升载 `qianpinshengzai`、10min过压保护 `voltprotect10min`、巴西过欠频稳定性 `guoqianpin_immun`  ",
        ),
        (
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 参数 → 创建实验",
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 / 欠频升载 / 10min过压保护 / 巴西过欠频稳定性 参数 → 创建实验",
        ),
        (
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai`）。",
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai` / `qianpinshengzai` / `voltprotect10min` / `guoqianpin_immun`）。",
        ),
    ]
    for old, new in reps:
        if old not in t:
            raise SystemExit(f"docs missing: {old[:80]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok docs")


def write_tests() -> None:
    (IOT / "tests/test_solar_voltprotect10min_schema.py").write_text(
        '''# -*- coding: utf-8 -*-
"""10min过压保护 schema / Blockly 接入冒烟。"""
from __future__ import annotations

from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_voltprotect10min_supported_and_aliases():
    assert "voltprotect10min" in list_supported_test_types()
    assert normalize_test_type("10min过压保护") == "voltprotect10min"
    assert normalize_test_type("voltprotect") == "voltprotect10min"


def test_voltprotect10min_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("voltprotect10min")
    assert schema["testType"] == "voltprotect10min"
    by_name = {f["name"]: f for f in schema["fields"]}
    for need in (
        "checkBox_S1",
        "radio_dewetron",
        "radio_wt",
        "dew_export_fields",
        "checkBox_S3",
        "textEdit_S3_AC_VOLT",
        "checkBox_S4",
        "textEdit_S4_AC_VOLT",
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ):
        assert need in by_name, need
    assert schema["wtLayout"]["dew"].get("powerGroupTreeNodes")


def test_voltprotect10min_blockly_steps():
    steps = flow_steps_for_test_type("voltprotect10min")
    assert len(steps) == 4
    names = [s["blockly_name"] for s in steps]
    assert names == [
        "solar_voltprotect10min_s1",
        "solar_voltprotect10min_s2",
        "solar_voltprotect10min_s3",
        "solar_voltprotect10min_s4",
    ]
    assert "textEdit_S3_AC_VOLT" in field_names_for_step("solar_voltprotect10min_s3")
    defaults = build_job_widgets("voltprotect10min", None)
    assert detail_fields_for("voltprotect10min", "solar_voltprotect10min_s3", widgets=defaults)
''',
        encoding="utf-8",
    )
    (IOT / "tests/test_solar_guoqianpin_immun_schema.py").write_text(
        '''# -*- coding: utf-8 -*-
"""巴西过欠频稳定性 schema / Blockly 接入冒烟。"""
from __future__ import annotations

from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_guoqianpin_immun_supported_and_aliases():
    assert "guoqianpin_immun" in list_supported_test_types()
    assert normalize_test_type("巴西过欠频稳定性") == "guoqianpin_immun"
    assert normalize_test_type("brazil_ovuf") == "guoqianpin_immun"


def test_guoqianpin_immun_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("guoqianpin_immun")
    assert schema["testType"] == "guoqianpin_immun"
    by_name = {f["name"]: f for f in schema["fields"]}
    for need in (
        "checkBox_S1",
        "radio_dewetron",
        "radio_wt",
        "dew_export_fields",
        "checkBox_S3",
        "textEdit_S3_AC_FR_Start",
        "textEdit_S3_AC_FR_End",
        "checkBox_S11",
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ):
        assert need in by_name, need
    assert schema["wtLayout"]["dew"].get("powerGroupTreeNodes")


def test_guoqianpin_immun_blockly_steps():
    steps = flow_steps_for_test_type("guoqianpin_immun")
    assert len(steps) == 4
    names = [s["blockly_name"] for s in steps]
    assert names == [
        "solar_guoqianpin_immun_s1",
        "solar_guoqianpin_immun_s2",
        "solar_guoqianpin_immun_s3",
        "solar_guoqianpin_immun_s4",
    ]
    assert "textEdit_S3_AC_FR_Start" in field_names_for_step("solar_guoqianpin_immun_s3")
    defaults = build_job_widgets("guoqianpin_immun", None)
    assert detail_fields_for("guoqianpin_immun", "solar_guoqianpin_immun_s3", widgets=defaults)
''',
        encoding="utf-8",
    )
    print("ok tests")


def patch_handoff() -> None:
    p = SOLAR / "utils/iot_ui_handoff.py"
    t = p.read_text(encoding="utf-8")
    if "voltprotect10min" in t and "resolve_guoqianpin_immun_ui" in t:
        print("handoff already")
        return
    reps = [
        (
            '''        "qianpinshengzai": ("欠频升载", "qianpinshengzai"),
        "qianpin": ("欠频升载", "qianpinshengzai"),
        "uf_raise": ("欠频升载", "qianpinshengzai"),
        "欠频升载": ("欠频升载", "qianpinshengzai"),
    }
''',
            '''        "qianpinshengzai": ("欠频升载", "qianpinshengzai"),
        "qianpin": ("欠频升载", "qianpinshengzai"),
        "uf_raise": ("欠频升载", "qianpinshengzai"),
        "欠频升载": ("欠频升载", "qianpinshengzai"),
        "voltprotect10min": ("10min过压保护", "voltprotect10min"),
        "voltprotect": ("10min过压保护", "voltprotect10min"),
        "10min过压保护": ("10min过压保护", "voltprotect10min"),
        "过压保护10min": ("10min过压保护", "voltprotect10min"),
        "guoqianpin_immun": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "guoqianpinimmun": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "brazil_ovuf": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "巴西过欠频稳定性": ("巴西过欠频稳定性", "guoqianpin_immun"),
        "过欠频稳定性": ("巴西过欠频稳定性", "guoqianpin_immun"),
    }
''',
        ),
        (
            """        resolve_qianpinshengzai_ui: Optional[Callable[[], Any]] = None,
        qianpinshengzai_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
            """        resolve_qianpinshengzai_ui: Optional[Callable[[], Any]] = None,
        qianpinshengzai_append: Optional[Callable[[], None]] = None,
        resolve_voltprotect10min_ui: Optional[Callable[[], Any]] = None,
        voltprotect10min_append: Optional[Callable[[], None]] = None,
        resolve_guoqianpin_immun_ui: Optional[Callable[[], Any]] = None,
        guoqianpin_immun_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
        ),
        (
            """        self.resolve_qianpinshengzai_ui = resolve_qianpinshengzai_ui
        self.qianpinshengzai_append = qianpinshengzai_append
        self.start_test = start_test
""",
            """        self.resolve_qianpinshengzai_ui = resolve_qianpinshengzai_ui
        self.qianpinshengzai_append = qianpinshengzai_append
        self.resolve_voltprotect10min_ui = resolve_voltprotect10min_ui
        self.voltprotect10min_append = voltprotect10min_append
        self.resolve_guoqianpin_immun_ui = resolve_guoqianpin_immun_ui
        self.guoqianpin_immun_append = guoqianpin_immun_append
        self.start_test = start_test
""",
        ),
        (
            '''        if handler_key == "qianpinshengzai":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_qianpinshengzai_ui,
                "append": self.qianpinshengzai_append,
                "label": "欠频升载",
            }
        return None
''',
            '''        if handler_key == "qianpinshengzai":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_qianpinshengzai_ui,
                "append": self.qianpinshengzai_append,
                "label": "欠频升载",
            }
        if handler_key == "voltprotect10min":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_voltprotect10min_ui,
                "append": self.voltprotect10min_append,
                "label": "10min过压保护",
            }
        if handler_key == "guoqianpin_immun":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_guoqianpin_immun_ui,
                "append": self.guoqianpin_immun_append,
                "label": "巴西过欠频稳定性",
            }
        return None
''',
        ),
        (
            '''                "guopinjiangzai",
                "qianpinshengzai",
            ) and isinstance(widgets_for_ui, dict):
''',
            '''                "guopinjiangzai",
                "qianpinshengzai",
                "voltprotect10min",
                "guoqianpin_immun",
            ) and isinstance(widgets_for_ui, dict):
''',
        ),
        (
            '''                    "guopinjiangzai",
                    "qianpinshengzai",
                ) and isinstance(widgets, dict):
''',
            '''                    "guopinjiangzai",
                    "qianpinshengzai",
                    "voltprotect10min",
                    "guoqianpin_immun",
                ) and isinstance(widgets, dict):
''',
        ),
        (
            """    resolve_qianpinshengzai_ui: Optional[Callable[[], Any]] = None,
    qianpinshengzai_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
            """    resolve_qianpinshengzai_ui: Optional[Callable[[], Any]] = None,
    qianpinshengzai_append: Optional[Callable[[], None]] = None,
    resolve_voltprotect10min_ui: Optional[Callable[[], Any]] = None,
    voltprotect10min_append: Optional[Callable[[], None]] = None,
    resolve_guoqianpin_immun_ui: Optional[Callable[[], Any]] = None,
    guoqianpin_immun_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
        ),
        (
            """        resolve_qianpinshengzai_ui=resolve_qianpinshengzai_ui,
        qianpinshengzai_append=qianpinshengzai_append,
        start_test=start_test,
""",
            """        resolve_qianpinshengzai_ui=resolve_qianpinshengzai_ui,
        qianpinshengzai_append=qianpinshengzai_append,
        resolve_voltprotect10min_ui=resolve_voltprotect10min_ui,
        voltprotect10min_append=voltprotect10min_append,
        resolve_guoqianpin_immun_ui=resolve_guoqianpin_immun_ui,
        guoqianpin_immun_append=guoqianpin_immun_append,
        start_test=start_test,
""",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"handoff missing #{i}: {old[:90]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok handoff")


def patch_runner() -> None:
    _repl(
        SOLAR / "agent/runners/__init__.py",
        '''        "qianpinshengzai",
        "qianpin",
        "uf_raise",
        "欠频升载",
    ):
''',
        '''        "qianpinshengzai",
        "qianpin",
        "uf_raise",
        "欠频升载",
        "voltprotect10min",
        "voltprotect",
        "10min过压保护",
        "过压保护10min",
        "guoqianpin_immun",
        "guoqianpinimmun",
        "brazil_ovuf",
        "巴西过欠频稳定性",
        "过欠频稳定性",
    ):
''',
        label="runner",
    )


def patch_scpi() -> None:
    p = SOLAR / "SCPITestWave.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_voltprotect10min_ui" in t and "resolve_guoqianpin_immun_ui" in t:
        print("SCPI already")
        return
    old = '''                def _resolve_qianpinshengzai_ui():
                    return globals().get("uiThaiQianPinShengZai")

                def _iot_get_run_status():
'''
    new = '''                def _resolve_qianpinshengzai_ui():
                    return globals().get("uiThaiQianPinShengZai")

                def _resolve_voltprotect10min_ui():
                    return globals().get("uiThaiVoltProtect10min")

                def _resolve_guoqianpin_immun_ui():
                    return globals().get("uiThaiGuoQianPin_Immun")

                def _iot_get_run_status():
'''
    if old not in t:
        raise SystemExit("SCPI resolve_qianpin missing")
    t = t.replace(old, new, 1)
    old = """                    resolve_qianpinshengzai_ui=_resolve_qianpinshengzai_ui,
                    qianpinshengzai_append=thaiqianpinshengzaiAppend,
                    start_test=RunProjectPush,
"""
    new = """                    resolve_qianpinshengzai_ui=_resolve_qianpinshengzai_ui,
                    qianpinshengzai_append=thaiqianpinshengzaiAppend,
                    resolve_voltprotect10min_ui=_resolve_voltprotect10min_ui,
                    voltprotect10min_append=thaivoltprotect10minAppend,
                    resolve_guoqianpin_immun_ui=_resolve_guoqianpin_immun_ui,
                    guoqianpin_immun_append=thaiguoqianpin_immunAppend,
                    start_test=RunProjectPush,
"""
    if old not in t:
        raise SystemExit("SCPI handoff kwargs missing")
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok SCPI")


def patch_runner_test() -> None:
    p = SOLAR / "tests/test_agent_runner_fixedpf.py"
    t = p.read_text(encoding="utf-8")
    if 'get_runner("voltprotect10min"' in t:
        print("runner test already")
        return
    old = '''    r12 = get_runner("qianpinshengzai", dry_run=True, execution_mode="handoff")
    r13 = get_runner("欠频升载", dry_run=True, execution_mode="handoff")
'''
    new = '''    r12 = get_runner("qianpinshengzai", dry_run=True, execution_mode="handoff")
    r13 = get_runner("欠频升载", dry_run=True, execution_mode="handoff")
    r14 = get_runner("voltprotect10min", dry_run=True, execution_mode="handoff")
    r15 = get_runner("10min过压保护", dry_run=True, execution_mode="handoff")
    r16 = get_runner("guoqianpin_immun", dry_run=True, execution_mode="handoff")
    r17 = get_runner("巴西过欠频稳定性", dry_run=True, execution_mode="handoff")
'''
    if old not in t:
        raise SystemExit("runner test qianpin lines missing")
    t = t.replace(old, new, 1)
    if "assert r13 is not None" in t and "assert r14 is not None" not in t:
        t = t.replace(
            "assert r13 is not None",
            "assert r13 is not None\n    assert r14 is not None\n    assert r15 is not None\n    assert r16 is not None\n    assert r17 is not None",
            1,
        )
    p.write_text(t, encoding="utf-8")
    print("ok runner test")


def main() -> None:
    patch_schema_init()
    patch_catalog()
    patch_detail()
    patch_experiment()
    patch_frontend()
    patch_docs()
    write_tests()
    patch_handoff()
    patch_runner()
    patch_scpi()
    patch_runner_test()
    print("voltprotect10min + guoqianpin_immun wire done")


if __name__ == "__main__":
    main()
