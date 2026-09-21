# -*- coding: utf-8 -*-
"""一次性：接入过频降载 IOT + Solar handoff 全链路。"""
from __future__ import annotations

from pathlib import Path

IOT = Path(r"E:/IOT/iot")
SOLAR = Path(r"E:/solarautotestnewui")


def _repl(path: Path, old: str, new: str, *, label: str) -> None:
    t = path.read_text(encoding="utf-8")
    if old not in t:
        if "guopinjiangzai" in t and "solar_guopinjiangzai_s1" in t and "already" in label:
            print(f"skip {path.name} ({label})")
            return
        raise SystemExit(f"missing in {path}: {label}\n---\n{old[:120]!r}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    print(f"ok {path} ({label})")


def patch_iot_schema_init() -> None:
    p = IOT / "app/services/solar_test_schemas/__init__.py"
    t = p.read_text(encoding="utf-8")
    if '"guopinjiangzai"' in t and "guopinjiangzai_fields.json" in t:
        print("schema init already")
    else:
        old = '''        "过欠压_过欠频": "ovuf_fields.json",
        "过欠压过欠频": "ovuf_fields.json",
    }
'''
        new = '''        "过欠压_过欠频": "ovuf_fields.json",
        "过欠压过欠频": "ovuf_fields.json",
        "guopinjiangzai": "guopinjiangzai_fields.json",
        "guopin": "guopinjiangzai_fields.json",
        "of_reduce": "guopinjiangzai_fields.json",
        "过频降载": "guopinjiangzai_fields.json",
    }
'''
        if old not in t:
            raise SystemExit("schema mapping ovuf tail missing")
        t = t.replace(old, new, 1)
        t = t.replace(
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf"]',
            'return ["overload", "antibackflow", "flicker", "harmonic", "fixedpf", "dccomponent", "reconnect", "ovuf", "guopinjiangzai"]',
            1,
        )
        p.write_text(t, encoding="utf-8")
        print("ok schema init")


def patch_iot_catalog() -> None:
    p = IOT / "app/services/solar_blockly_catalog.py"
    t = p.read_text(encoding="utf-8")
    if '"guopinjiangzai":' in t and "solar_guopinjiangzai_s1" in t:
        print("catalog already")
        return
    # insert after ovuf block closing before final }
    marker = '                "blockly_name": "solar_ovuf_s4",\n                "com_name": "过欠压过欠频步骤4 关机",\n                "colour": 110,\n            },\n        ),\n    },\n}\n'
    insert = '''                "blockly_name": "solar_ovuf_s4",
                "com_name": "过欠压过欠频步骤4 关机",
                "colour": 110,
            },
        ),
    },
    "guopinjiangzai": {
        "com_name": "过频降载半自动",
        "blockly_name": "solar_guopinjiangzai",
        "label": "过频降载",
        "colour": 120,
        "aliases": (
            "guopinjiangzai",
            "guopin",
            "of_reduce",
            "过频降载",
            "过频降载半自动",
            "solar_guopin",
        ),
        "steps": (
            {
                "blockly_name": "solar_guopinjiangzai_s1",
                "com_name": "过频降载步骤1 AC/DC",
                "colour": 120,
            },
            {
                "blockly_name": "solar_guopinjiangzai_s2",
                "com_name": "过频降载步骤2 分析仪",
                "colour": 130,
            },
            {
                "blockly_name": "solar_guopinjiangzai_s3",
                "com_name": "过频降载步骤3 频率台阶",
                "colour": 140,
            },
            {
                "blockly_name": "solar_guopinjiangzai_s4",
                "com_name": "过频降载步骤4 关机",
                "colour": 150,
            },
        ),
    },
}
'''
    if marker not in t:
        raise SystemExit("catalog ovuf tail missing")
    p.write_text(t.replace(marker, insert, 1), encoding="utf-8")
    print("ok catalog")


def patch_iot_detail() -> None:
    p = IOT / "app/services/solar_blockly_detail.py"
    t = p.read_text(encoding="utf-8")
    if "solar_guopinjiangzai_s1" in t:
        print("detail already")
        return
    old = '''    "solar_ovuf_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
    new = '''    "solar_ovuf_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
    # ── 过频降载 ──
    "solar_guopinjiangzai_s1": (
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
    "solar_guopinjiangzai_s2": (
        "checkBox_S2",
        "radio_wt",
        "radio_dewetron",
        "radio_S2_WT3000",
        "radio_S2_WT1800",
        "radio_S2_WT1806E",
        "radio_S2_WT5000",
        "comboBox_DEW_MaxRefreshRate",
    ),
    "solar_guopinjiangzai_s3": (
        "checkBox_S3",
        "textEdit_FrequencyLadder_VOLT",
        "textEdit_FrequencyLadder",
        "textEdit_FrequencyLadder_TIME",
        "comboBox_FrequencyLadder_TIME",
    ),
    "solar_guopinjiangzai_s4": (
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ),
}
'''
    if old not in t:
        raise SystemExit("detail ovuf_s4 missing")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("ok detail")


def patch_iot_experiment() -> None:
    p = IOT / "app/services/solar_experiment_service.py"
    _repl(
        p,
        '''            "reconnect",
            "ovuf",
        ):''',
        '''            "reconnect",
            "ovuf",
            "guopinjiangzai",
        ):''',
        label="experiment parsed types",
    )


def patch_iot_frontend() -> None:
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  ovuf: '过欠压_过欠频',
  guoqianya_pin: '过欠压_过欠频',
  volt_freq: '过欠压_过欠频',
  '过欠压_过欠频': '过欠压_过欠频',
  过欠压过欠频: '过欠压_过欠频',
}
""",
        """  ovuf: '过欠压_过欠频',
  guoqianya_pin: '过欠压_过欠频',
  volt_freq: '过欠压_过欠频',
  '过欠压_过欠频': '过欠压_过欠频',
  过欠压过欠频: '过欠压_过欠频',
  guopinjiangzai: '过频降载',
  guopin: '过频降载',
  of_reduce: '过频降载',
  过频降载: '过频降载',
}
""",
        label="labels map",
    )
    _repl(
        IOT / "frontend/src/utils/solarLabels.ts",
        """  { value: 'ovuf', label: '过欠压_过欠频' },
] as const
""",
        """  { value: 'ovuf', label: '过欠压_过欠频' },
  { value: 'guopinjiangzai', label: '过频降载' },
] as const
""",
        label="labels options",
    )
    _repl(
        IOT / "frontend/src/utils/solarBlockly.ts",
        """  { type: 'solar_ovuf', message0: '过欠压_过欠频半自动%1', arg: 'solar_ovuf', colour: 80 },
] as const
""",
        """  { type: 'solar_ovuf', message0: '过欠压_过欠频半自动%1', arg: 'solar_ovuf', colour: 80 },
  { type: 'solar_guopinjiangzai_s1', message0: '过频降载步骤1 AC/DC%1', arg: 'solar_guopinjiangzai_s1', colour: 120 },
  { type: 'solar_guopinjiangzai_s2', message0: '过频降载步骤2 分析仪%1', arg: 'solar_guopinjiangzai_s2', colour: 130 },
  { type: 'solar_guopinjiangzai_s3', message0: '过频降载步骤3 频率台阶%1', arg: 'solar_guopinjiangzai_s3', colour: 140 },
  { type: 'solar_guopinjiangzai_s4', message0: '过频降载步骤4 关机%1', arg: 'solar_guopinjiangzai_s4', colour: 150 },
  { type: 'solar_guopinjiangzai', message0: '过频降载半自动%1', arg: 'solar_guopinjiangzai', colour: 120 },
] as const
""",
        label="blockly",
    )
    _repl(
        IOT / "frontend/src/views/solar/SolarOrderCreate.vue",
        """    | 'reconnect'
    | 'ovuf',
""",
        """    | 'reconnect'
    | 'ovuf'
    | 'guopinjiangzai',
""",
        label="order create",
    )
    # ExperimentStart: move guopin into params types; detect already exists
    _repl(
        IOT / "frontend/src/views/experiment/ExperimentStart.vue",
        """  'reconnect',
  'ovuf',
])
""",
        """  'reconnect',
  'ovuf',
  'guopinjiangzai',
])
""",
        label="params types",
    )
    # remove from unsupported hint map if present
    p = IOT / "frontend/src/views/experiment/ExperimentStart.vue"
    t = p.read_text(encoding="utf-8")
    t2 = t.replace(
        "  const map: Record<string, string> = {\n    guopinjiangzai: '过频降载',\n  }",
        "  const map: Record<string, string> = {}",
        1,
    )
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
        print("ok experiment start hint map")

    # JobList
    p = IOT / "frontend/src/views/solar/SolarJobList.vue"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            '<el-option label="过欠压_过欠频" value="ovuf" />\n          </el-select>',
            '<el-option label="过欠压_过欠频" value="ovuf" />\n            <el-option label="过频降载" value="guopinjiangzai" />\n          </el-select>',
        ),
        (
            '<el-option label="过欠压过欠频自动开跑" value="ovuf_autostart" />\n          </el-select>',
            '<el-option label="过欠压过欠频自动开跑" value="ovuf_autostart" />\n            <el-option label="过频降载默认（只追加）" value="guopinjiangzai_default" />\n            <el-option label="过频降载自动开跑" value="guopinjiangzai_autostart" />\n          </el-select>',
        ),
        (
            "  ovuf_default: { widgets: {}, auto_append: true, auto_start: false },\n  ovuf_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
            "  ovuf_default: { widgets: {}, auto_append: true, auto_start: false },\n  ovuf_autostart: { widgets: {}, auto_append: true, auto_start: true },\n  guopinjiangzai_default: { widgets: {}, auto_append: true, auto_start: false },\n  guopinjiangzai_autostart: { widgets: {}, auto_append: true, auto_start: true },\n}",
        ),
        (
            """  } else if (form.templateId.startsWith('ovuf')) {
    form.testType = 'ovuf'
  } else if (
    (form.testType === 'antibackflow' ||
      form.testType === 'flicker' ||
      form.testType === 'harmonic' ||
      form.testType === 'fixedpf' ||
      form.testType === 'dccomponent' ||
      form.testType === 'reconnect' ||
      form.testType === 'ovuf') &&
    form.templateId.startsWith('overload')
  ) {
""",
            """  } else if (form.templateId.startsWith('ovuf')) {
    form.testType = 'ovuf'
  } else if (form.templateId.startsWith('guopinjiangzai')) {
    form.testType = 'guopinjiangzai'
  } else if (
    (form.testType === 'antibackflow' ||
      form.testType === 'flicker' ||
      form.testType === 'harmonic' ||
      form.testType === 'fixedpf' ||
      form.testType === 'dccomponent' ||
      form.testType === 'reconnect' ||
      form.testType === 'ovuf' ||
      form.testType === 'guopinjiangzai') &&
    form.templateId.startsWith('overload')
  ) {
""",
        ),
        (
            """    } else if (tt === 'ovuf' && !form.templateId.startsWith('ovuf')) {
      form.templateId = 'ovuf_default'
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
        form.templateId.startsWith('ovuf'))
    ) {
""",
            """    } else if (tt === 'ovuf' && !form.templateId.startsWith('ovuf')) {
      form.templateId = 'ovuf_default'
      form.autoAppend = true
      form.autoStart = false
    } else if (tt === 'guopinjiangzai' && !form.templateId.startsWith('guopinjiangzai')) {
      form.templateId = 'guopinjiangzai_default'
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
        form.templateId.startsWith('guopinjiangzai'))
    ) {
""",
        ),
        (
            """                    : tt === 'ovuf'
                      ? '过欠压过欠频联调'
                      : '过载联调'
""",
            """                    : tt === 'ovuf'
                      ? '过欠压过欠频联调'
                      : tt === 'guopinjiangzai'
                        ? '过频降载联调'
                        : '过载联调'
""",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"joblist missing #{i}: {old[:80]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok job list")


def patch_iot_docs() -> None:
    p = IOT / "docs/IOT-Solar自动化试验线上版方案.md"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连已完成 → **过欠压_过欠频已接入（待联调）**",
            "过载/防逆流/闪变/谐波/固定PF/直流分量/重连/过欠压_过欠频已完成 → **过频降载已接入（待联调）**",
        ),
        (
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频**（`auto_append` / `auto_start`）  ",
            "5. IOT 下发 **过载** / **防逆流** / **电压闪变** / **谐波电流** / **固定PF=1** / **直流分量** / **重连** / **过欠压_过欠频** / **过频降载**（`auto_append` / `auto_start`）  ",
        ),
        (
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`  ",
            "- 类型：过载 `overload`、防逆流 `antibackflow`、电压闪变 `flicker`、谐波 `harmonic`、固定PF `fixedpf`、直流分量 `dccomponent`、重连 `reconnect`、过欠压_过欠频 `ovuf`、过频降载 `guopinjiangzai`  ",
        ),
        (
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 参数 → 创建实验",
            "2. 向导：选台架/类型 → 核对仪器槽位 → 填过载 / 防逆流 / 闪变 / 谐波 / 固定PF / 直流分量 / 重连 / 过欠压_过欠频 / 过频降载 参数 → 创建实验",
        ),
        (
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf`）。",
            "开测表单 schema：`app/services/solar_test_schemas/`（已支持 `overload` / `antibackflow` / `flicker` / `harmonic` / `fixedpf` / `dccomponent` / `reconnect` / `ovuf` / `guopinjiangzai`）。",
        ),
    ]
    for old, new in reps:
        if old not in t:
            raise SystemExit(f"docs missing: {old[:60]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok docs")


def write_iot_test() -> None:
    (IOT / "tests/test_solar_guopinjiangzai_schema.py").write_text(
        '''# -*- coding: utf-8 -*-
"""过频降载 schema / Blockly 接入冒烟。"""
from __future__ import annotations

from app.services.solar_blockly_catalog import flow_steps_for_test_type, normalize_test_type
from app.services.solar_blockly_detail import detail_fields_for, field_names_for_step
from app.services.solar_test_schemas import build_job_widgets, list_supported_test_types, load_test_schema


def test_guopinjiangzai_supported_and_aliases():
    assert "guopinjiangzai" in list_supported_test_types()
    assert normalize_test_type("过频降载") == "guopinjiangzai"
    assert normalize_test_type("guopin") == "guopinjiangzai"


def test_guopinjiangzai_schema_core_fields():
    load_test_schema.cache_clear()
    schema = load_test_schema("guopinjiangzai")
    assert schema["testType"] == "guopinjiangzai"
    by_name = {f["name"]: f for f in schema["fields"]}
    for need in (
        "checkBox_S1",
        "radio_dewetron",
        "radio_wt",
        "dew_export_fields",
        "checkBox_S3",
        "textEdit_FrequencyLadder",
        "textEdit_FrequencyLadder_VOLT",
        "textEdit_FrequencyLadder_TIME",
        "comboBox_FrequencyLadder_TIME",
        "checkBox_S_End",
        "comboBox_S_End_AC",
    ):
        assert need in by_name, need
    dew = schema["wtLayout"]["dew"]
    assert dew.get("powerGroupTreeNodes")


def test_guopinjiangzai_blockly_steps():
    steps = flow_steps_for_test_type("guopinjiangzai")
    assert len(steps) == 4
    names = [s["blockly_name"] for s in steps]
    assert names == [
        "solar_guopinjiangzai_s1",
        "solar_guopinjiangzai_s2",
        "solar_guopinjiangzai_s3",
        "solar_guopinjiangzai_s4",
    ]
    assert "textEdit_FrequencyLadder" in field_names_for_step("solar_guopinjiangzai_s3")
    defaults = build_job_widgets("guopinjiangzai", None)
    fields = detail_fields_for("guopinjiangzai", "solar_guopinjiangzai_s3", widgets=defaults)
    assert fields
''',
        encoding="utf-8",
    )
    print("ok iot test")


def patch_solar_handoff() -> None:
    p = SOLAR / "utils/iot_ui_handoff.py"
    t = p.read_text(encoding="utf-8")
    if '"guopinjiangzai":' in t and "resolve_guopinjiangzai_ui" in t:
        print("handoff already")
        return
    reps = [
        (
            '''        "过欠压_过欠频": ("过欠压_过欠频", "ovuf"),
        "过欠压过欠频": ("过欠压_过欠频", "ovuf"),
    }
''',
            '''        "过欠压_过欠频": ("过欠压_过欠频", "ovuf"),
        "过欠压过欠频": ("过欠压_过欠频", "ovuf"),
        "guopinjiangzai": ("过频降载", "guopinjiangzai"),
        "guopin": ("过频降载", "guopinjiangzai"),
        "of_reduce": ("过频降载", "guopinjiangzai"),
        "过频降载": ("过频降载", "guopinjiangzai"),
    }
''',
        ),
        (
            """        resolve_ovuf_ui: Optional[Callable[[], Any]] = None,
        ovuf_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
            """        resolve_ovuf_ui: Optional[Callable[[], Any]] = None,
        ovuf_append: Optional[Callable[[], None]] = None,
        resolve_guopinjiangzai_ui: Optional[Callable[[], Any]] = None,
        guopinjiangzai_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
        ),
        (
            """        self.resolve_ovuf_ui = resolve_ovuf_ui
        self.ovuf_append = ovuf_append
        self.start_test = start_test
""",
            """        self.resolve_ovuf_ui = resolve_ovuf_ui
        self.ovuf_append = ovuf_append
        self.resolve_guopinjiangzai_ui = resolve_guopinjiangzai_ui
        self.guopinjiangzai_append = guopinjiangzai_append
        self.start_test = start_test
""",
        ),
        (
            '''        if handler_key == "ovuf":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_ovuf_ui,
                "append": self.ovuf_append,
                "label": "过欠压_过欠频",
            }
        return None
''',
            '''        if handler_key == "ovuf":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_ovuf_ui,
                "append": self.ovuf_append,
                "label": "过欠压_过欠频",
            }
        if handler_key == "guopinjiangzai":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_guopinjiangzai_ui,
                "append": self.guopinjiangzai_append,
                "label": "过频降载",
            }
        return None
''',
        ),
        (
            '''            if (handler.get("key") or "") in (
                "flicker",
                "harmonic",
                "fixedpf",
                "dccomponent",
                "reconnect",
                "ovuf",
            ) and isinstance(widgets_for_ui, dict):
''',
            '''            if (handler.get("key") or "") in (
                "flicker",
                "harmonic",
                "fixedpf",
                "dccomponent",
                "reconnect",
                "ovuf",
                "guopinjiangzai",
            ) and isinstance(widgets_for_ui, dict):
''',
        ),
        (
            '''                elif (handler.get("key") or "") in (
                    "flicker",
                    "harmonic",
                    "fixedpf",
                    "dccomponent",
                    "reconnect",
                    "ovuf",
                ) and isinstance(widgets, dict):
''',
            '''                elif (handler.get("key") or "") in (
                    "flicker",
                    "harmonic",
                    "fixedpf",
                    "dccomponent",
                    "reconnect",
                    "ovuf",
                    "guopinjiangzai",
                ) and isinstance(widgets, dict):
''',
        ),
        (
            """    resolve_ovuf_ui: Optional[Callable[[], Any]] = None,
    ovuf_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
            """    resolve_ovuf_ui: Optional[Callable[[], Any]] = None,
    ovuf_append: Optional[Callable[[], None]] = None,
    resolve_guopinjiangzai_ui: Optional[Callable[[], Any]] = None,
    guopinjiangzai_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
        ),
        (
            """        resolve_ovuf_ui=resolve_ovuf_ui,
        ovuf_append=ovuf_append,
        start_test=start_test,
""",
            """        resolve_ovuf_ui=resolve_ovuf_ui,
        ovuf_append=ovuf_append,
        resolve_guopinjiangzai_ui=resolve_guopinjiangzai_ui,
        guopinjiangzai_append=guopinjiangzai_append,
        start_test=start_test,
""",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"handoff missing #{i}: {old[:80]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok handoff")


def patch_solar_runner() -> None:
    _repl(
        SOLAR / "agent/runners/__init__.py",
        '''        "ovuf",
        "guoqianya_pin",
        "volt_freq",
        "过欠压_过欠频",
        "过欠压过欠频",
    ):
''',
        '''        "ovuf",
        "guoqianya_pin",
        "volt_freq",
        "过欠压_过欠频",
        "过欠压过欠频",
        "guopinjiangzai",
        "guopin",
        "of_reduce",
        "过频降载",
    ):
''',
        label="runner",
    )


def patch_solar_scpi() -> None:
    p = SOLAR / "SCPITestWave.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_guopinjiangzai_ui" in t:
        print("SCPI already")
        return
    old = '''                def _resolve_ovuf_ui():
                    return globals().get("uiThaiGuoQianYa_Pin")

                def _iot_get_run_status():
'''
    new = '''                def _resolve_ovuf_ui():
                    return globals().get("uiThaiGuoQianYa_Pin")

                def _resolve_guopinjiangzai_ui():
                    return globals().get("uiThaiGuoPinJiangZai")

                def _iot_get_run_status():
'''
    if old not in t:
        raise SystemExit("SCPI resolve_ovuf missing")
    t = t.replace(old, new, 1)
    old = """                    resolve_ovuf_ui=_resolve_ovuf_ui,
                    ovuf_append=thaiguoqianya_pinAppend,
                    start_test=RunProjectPush,
"""
    new = """                    resolve_ovuf_ui=_resolve_ovuf_ui,
                    ovuf_append=thaiguoqianya_pinAppend,
                    resolve_guopinjiangzai_ui=_resolve_guopinjiangzai_ui,
                    guopinjiangzai_append=thaiguopinjiangzaiAppend,
                    start_test=RunProjectPush,
"""
    if old not in t:
        raise SystemExit("SCPI handoff kwargs missing")
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok SCPI")


def patch_solar_runner_test() -> None:
    p = SOLAR / "tests/test_agent_runner_fixedpf.py"
    t = p.read_text(encoding="utf-8")
    if 'get_runner("guopinjiangzai"' in t:
        print("runner test already")
        return
    old = '''    r8 = get_runner("ovuf", dry_run=True, execution_mode="handoff")
    r9 = get_runner("过欠压_过欠频", dry_run=True, execution_mode="handoff")
'''
    new = '''    r8 = get_runner("ovuf", dry_run=True, execution_mode="handoff")
    r9 = get_runner("过欠压_过欠频", dry_run=True, execution_mode="handoff")
    r10 = get_runner("guopinjiangzai", dry_run=True, execution_mode="handoff")
    r11 = get_runner("过频降载", dry_run=True, execution_mode="handoff")
'''
    if old not in t:
        raise SystemExit("runner test ovuf lines missing")
    t = t.replace(old, new, 1)
    if "assert r9 is not None" in t and "assert r10 is not None" not in t:
        t = t.replace(
            "assert r9 is not None",
            "assert r9 is not None\n    assert r10 is not None\n    assert r11 is not None",
            1,
        )
    p.write_text(t, encoding="utf-8")
    print("ok runner test")


def main() -> None:
    patch_iot_schema_init()
    patch_iot_catalog()
    patch_iot_detail()
    patch_iot_experiment()
    patch_iot_frontend()
    patch_iot_docs()
    write_iot_test()
    patch_solar_handoff()
    patch_solar_runner()
    patch_solar_scpi()
    patch_solar_runner_test()
    print("guopinjiangzai wire done")


if __name__ == "__main__":
    main()
