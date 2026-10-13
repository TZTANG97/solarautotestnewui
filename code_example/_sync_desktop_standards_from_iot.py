# -*- coding: utf-8 -*-
"""从 IOT solar_standard_profiles 同步桌面 iot_*_standard.py，并补 Dialog/handoff（缺啥补啥）。

在 solarautotestnewui 根执行：
  uv run python code_example/_sync_desktop_standards_from_iot.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DESK = Path(__file__).resolve().parents[1]
IOT = Path("E:/IOT/iot")
sys.path.insert(0, str(IOT))

# 避免拉取 sqlalchemy：直接 exec profiles 源文件
from typing import Any, Dict, List, Optional  # noqa: E402

_ns: Dict[str, Any] = {
    "__name__": "ssp",
    "Any": Any,
    "Dict": Dict,
    "List": List,
    "Optional": Optional,
}
_src = (IOT / "app" / "services" / "solar_standard_profiles.py").read_text(encoding="utf-8")
exec(compile(_src, "ssp.py", "exec"), _ns)
SOLAR_STANDARD_PROFILES = _ns["SOLAR_STANDARD_PROFILES"]
WIDGET_STANDARD_KEY = _ns.get("WIDGET_STANDARD_KEY", "solarStandard")


def defaults_for_standard(test_type: str, *, standard_id: str = "") -> Dict[str, Any]:
    """轻量版：不走 normalize_test_type / sqlalchemy。"""
    prof = SOLAR_STANDARD_PROFILES.get(test_type) or {}
    dm = prof.get("defaults_by_standard") or {}
    sid = str(standard_id or prof.get("default") or "thai").strip().lower()
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    sid = aliases.get(sid, sid)
    raw = dict(dm.get(sid) or {})
    # 与 IOT defaults_for_standard 白名单一致：保留公开控件 + 已登记 meta 前缀
    out: Dict[str, Any] = {}
    for k, v in raw.items():
        sk = str(k)
        if not sk.startswith("_"):
            out[sk] = v
            continue
        if any(
            sk.startswith(p)
            for p in (
                "_flicker",
                "_harmonic",
                "_dccomponent",
                "_fixedpf",
                "_overload",
                "_reconnect",
                "_ovuf",
                "_guopin",
                "_qianpin",
                "_vad",
                "_voltprotect",
                "_antibackflow",
                "_freqadapt",
                "_rocof",
                "_immun",
                "_rapidvolt",
                "_lvrt",
                "_phasejump",
                "_staticmppt",
                "_dynamicmppt",
                "_reactiveqcap",
                "_fixedq",
                "_reactiveqin",
                "_reactiveqacc",
                "_activep",
                "_staticqu",
                "_dynamicqu",
                "_testpu",
                "_staticcosphi",
                "_dynamiccosphi",
                "_cosphibrazil",
            )
        ):
            out[sk] = v
    return out

OPTIONS = (
    ("thai", "泰国 PEA/MEA（现行）"),
    ("de_vde", "德国 VDE"),
    ("br_ord140", "巴西 Ordinance 140"),
    ("en50549", "欧洲 EN 50549"),
    ("as_nzs", "澳洲 AS/NZS"),
    ("it_cei", "意大利 CEI"),
    ("uk_g99", "英国 G99/G98"),
    ("iec61727", "IEC 61727"),
)

# test_type -> Dialog path (relative to dialogs/)
DIALOGS = {
    "voltageadaptability": "Dialog_thaivoltageadaptability.py",
    "voltprotect10min": "Dialog_thaivoltprotect10min.py",
    "antibackflow": "Dialog_thaantibackflow.py",
    "qianpinshengzai": "Dialog_thaiqianpinshengzai.py",
    "guopinjiangzai": "Dialog_thaiguopinjiangzai.py",
    "frequencyadaptability": "Dialog_thaifrequencyadaptability.py",
    "rocof": "Dialog_thairocof.py",
    "guoqianpin_immun": "Dialog_thaiguoqianpin_immun.py",
    "rapidvolt": "Dialog_thairapidvolt.py",
    "lvrt": "Dialog_thailvrt.py",
    "phasejump": "Dialog_thaiphasejump.py",
    "staticmppt": "Dialog_thaistaticmppttest.py",
    "dynamicmppt": "Dialog_thaidynamicmppt.py",
    "reactiveqcap": "Dialog_thaireactiveQcap.py",
    "fixedq": "Dialog_thaifixedQ.py",
    "reactiveqin": "Dialog_thaireactiveQin.py",
    "reactiveqacc": "Dialog_thaireactiveQacc.py",
    "activep": "Dialog_thaiactiveP.py",
    "staticqu": "Dialog_thaistaticQU.py",
    "dynamicqu": "Dialog_thaidynamicQU.py",
    "testpu": "Dialog_thaitestPU.py",
    "staticcosphi": "Dialog_thaistaticcosPhi.py",
    "dynamiccosphi": "Dialog_thaidynamiccosPhi.py",
    "cosphibrazil": "Dialog_thaicosPhi_Brazil.py",
}


def _mod_name(tt: str) -> str:
    return f"iot_{tt}_standard"


def _fn_prefix(tt: str) -> str:
    return tt  # list_X_standard_options


# 已有手写 helper 的模块禁止被本脚本覆盖
PROTECTED_MODULES = {
    "flicker",
    "harmonic",
    "dccomponent",
    "fixedpf",
}


def write_standard_module(tt: str, *, force: bool = False) -> Path | None:
    path = DESK / "utils" / f"{_mod_name(tt)}.py"
    if tt in PROTECTED_MODULES and path.exists() and not force:
        print("skip protected", path.name)
        return None
    defaults = {sid: defaults_for_standard(tt, standard_id=sid) for sid, _ in OPTIONS}
    # drop empty
    defaults = {k: v for k, v in defaults.items() if v}
    const = f"{tt.upper()}_STANDARD_DEFAULTS"
    opt = f"{tt.upper()}_STANDARD_OPTIONS"
    lines = [
        "# -*- coding: utf-8 -*-",
        f'"""{tt} 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""',
        "from __future__ import annotations",
        "",
        "from typing import Any, Dict, List, Optional",
        "",
        f"{const}: Dict[str, Dict[str, Any]] = {{",
    ]
    for sid, _lab in OPTIONS:
        d = defaults.get(sid) or {}
        lines.append(f'    "{sid}": {{')
        for k, v in d.items():
            lines.append(f"        {k!r}: {v!r},")
        lines.append("    },")
    lines.append("}")
    lines.append("")
    lines.append(f"{opt} = (")
    for sid, lab in OPTIONS:
        lines.append(f'    {{"id": "{sid}", "label": "{lab}"}},')
    lines.append(")")
    lines.append("")
    pref = tt
    lines.append(
        f"""
def list_{pref}_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in {opt}]


def normalize_{pref}_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {{"iec": "iec61727", "cn_gb": "en50549"}}
    s = aliases.get(s, s)
    if s in {const}:
        return s
    return ""


def resolve_{pref}_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {{}}
    w = widgets if isinstance(widgets, dict) else {{}}
    for src in (p, w):
        sid = normalize_{pref}_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_{pref}_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {{}})
    sid = normalize_{pref}_standard_id(standard_id) or "thai"
    defaults = {const}.get(sid) or {{}}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_{pref}_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_{pref}_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_{pref}_standard_to_widgets({{}}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
""".strip()
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


COMBO_SNIPPET = '''
        stdLabel = QtWidgets.QLabel("国家标准")
        stdLabel.setStyleSheet(
            "font-size: 12px; color: #475569; background: transparent; border: none;"
        )
        topLayout.addWidget(stdLabel)
        self.comboBox_SolarStandard = QtWidgets.QComboBox()
        self.comboBox_SolarStandard.setObjectName("comboBox_SolarStandard")
        self.comboBox_SolarStandard.setFixedWidth(168)
        self.comboBox_SolarStandard.setStyleSheet(
            "QComboBox { font-size: 12px; padding: 2px 6px; background: white; }"
        )
        try:
            from utils.{mod} import list_{pref}_standard_options

            for opt in list_{pref}_standard_options():
                self.comboBox_SolarStandard.addItem(str(opt["label"]), str(opt["id"]))
        except Exception:
            self.comboBox_SolarStandard.addItem("泰国 PEA/MEA（现行）", "thai")
        self.comboBox_SolarStandard.setCurrentIndex(0)
        self._solar_standard = "thai"
        self.comboBox_SolarStandard.currentIndexChanged.connect(self._on_solar_standard_changed)
        topLayout.addWidget(self.comboBox_SolarStandard)

'''

METHODS = '''
    def set_solar_standard(self, standard_id, *, apply_defaults=False):
        try:
            from utils.{mod} import apply_{pref}_standard_to_ui

            apply_{pref}_standard_to_ui(
                self,
                standard_id,
                force=True,
                apply_defaults=bool(apply_defaults),
            )
        except Exception:
            self._solar_standard = str(standard_id or "thai").strip() or "thai"

    def _on_solar_standard_changed(self, index):
        sid = self.comboBox_SolarStandard.itemData(index)
        if sid is None:
            sid = "thai"
        self.set_solar_standard(str(sid), apply_defaults=True)

'''


def patch_dialog(tt: str, dialog_file: str) -> str:
    path = DESK / "dialogs" / dialog_file
    if not path.exists():
        return f"missing dialog {dialog_file}"
    text = path.read_text(encoding="utf-8")
    # 时序基类子类：靠 SOLAR_STANDARD_TT，不在此硬插 combo
    if "SOLAR_STANDARD_TT" in text and f'SOLAR_STANDARD_TT = "{tt}"' in text:
        return "dialog timing-tt ok"
    if "_BaseTimingProfileDialogUi" in text and "SOLAR_STANDARD_TT" not in text:
        # 尝试给子类加上 TT
        m0 = re.search(r"(class Ui_Dialog_\w+\(_BaseTimingProfileDialogUi\):\s*\n)", text)
        if m0 and f'SOLAR_STANDARD_TT = "{tt}"' not in text:
            text = text[: m0.end()] + f'    SOLAR_STANDARD_TT = "{tt}"\n' + text[m0.end() :]
            path.write_text(text, encoding="utf-8")
            return "dialog timing-tt patched"
    if "comboBox_SolarStandard" in text and f"iot_{tt}_standard" in text:
        return "dialog ok"
    if "comboBox_SolarStandard" in text:
        return "dialog has combo but other module"
    mod = _mod_name(tt)
    pref = tt
    snip = COMBO_SNIPPET.replace("{mod}", mod).replace("{pref}", pref)
    # insert before first topLayout.addStretch() after ResetCount if possible
    m = re.search(
        r"(topLayout\.addWidget\(self\.pushButton_ResetCount\)\s*\n)(\s*topLayout\.addStretch\(\))",
        text,
    )
    if not m:
        m = re.search(r"(\n\s*)(topLayout\.addStretch\(\))", text)
        if not m:
            return "no stretch anchor"
        text = text[: m.start(2)] + snip + text[m.start(2) :]
    else:
        text = text[: m.end(1)] + snip + m.group(2) + text[m.end(2) :]
    meth = METHODS.replace("{mod}", mod).replace("{pref}", pref)
    if "def set_solar_standard" not in text:
        # before first def _switch_step or after setupUi end
        m2 = re.search(r"\n    def _switch_step\(", text)
        if m2:
            text = text[: m2.start()] + "\n" + meth + text[m2.start() :]
        else:
            text += "\n" + meth
    path.write_text(text, encoding="utf-8")
    return "dialog patched"


def patch_handoff(tts: list[str]) -> str:
    path = DESK / "utils" / "iot_ui_handoff.py"
    text = path.read_text(encoding="utf-8")
    changed = False
    # ensure sid vars
    for tt in tts:
        var = f"{tt}_sid"
        if f"{var} = \"\"" not in text and f"{var} =" not in text.split("ovuf_sid", 1)[-1][:800]:
            # insert after guopinjiangzai_sid or reconnect
            if f"{var} = \"\"" not in text:
                anchor = 'guopinjiangzai_sid = ""'
                if anchor in text and f"{tt}_sid" not in text:
                    text = text.replace(
                        anchor,
                        anchor + f"\n            {tt}_sid = \"\"",
                        1,
                    )
                    changed = True
                elif 'ovuf_sid = ""' in text and f"{tt}_sid" not in text:
                    text = text.replace(
                        'ovuf_sid = ""',
                        'ovuf_sid = ""\n            ' + f'{tt}_sid = ""',
                        1,
                    )
                    changed = True
        branch = f'elif (handler.get("key") or "") == "{tt}":'
        if branch not in text:
            # insert before widgets_for_ui assignment after last elif for standards
            marker = "            widgets_for_ui = {"
            block = f'''
            elif (handler.get("key") or "") == "{tt}":
                try:
                    from utils.iot_{tt}_standard import (
                        apply_{tt}_standard_to_widgets,
                        resolve_{tt}_standard_id,
                    )

                    {tt}_sid = resolve_{tt}_standard_id(
                        params=params if isinstance(params, dict) else {{}},
                        widgets=widgets if isinstance(widgets, dict) else {{}},
                    )
                    widgets = apply_{tt}_standard_to_widgets(
                        widgets if isinstance(widgets, dict) else {{}},
                        {tt}_sid,
                        force=False,
                    )
                    self._log(f"{tt}标准 solarStandard={{{tt}_sid}}")
                except Exception as exc:
                    self._log(f"{tt}标准默认合并跳过: {{exc}}")
'''
            text = text.replace(marker, block + "\n" + marker, 1)
            changed = True
        # mount dialog
        mount = f'elif (handler.get("key") or "") == "{tt}" and real_ui is not None:'
        if mount not in text:
            marker2 = "            # 德威创导出字段：不在标准控件树里，单独写入面板"
            block2 = f'''
            elif (handler.get("key") or "") == "{tt}" and real_ui is not None:
                try:
                    sid = {tt}_sid or "thai"
                    if hasattr(real_ui, "set_solar_standard"):
                        real_ui.set_solar_standard(sid, apply_defaults=False)
                    else:
                        setattr(real_ui, "_solar_standard", sid)
                except Exception as exc:
                    self._log(f"{tt}标准挂载 Dialog 跳过: {{exc}}")
'''
            if marker2 in text:
                text = text.replace(marker2, block2 + "\n" + marker2, 1)
                changed = True
        # ensure in radio_wt3000 list
        if f'"{tt}",' not in text.split("radio_wt3000", 1)[0][-500:]:
            pass  # many already listed
    if changed:
        path.write_text(text, encoding="utf-8")
        return "handoff patched"
    return "handoff unchanged"


def main() -> None:
    # sync modules for all profiles that have defaults
    done = []
    for tt, prof in SOLAR_STANDARD_PROFILES.items():
        if not (prof.get("defaults_by_standard") or {}):
            continue
        p = write_standard_module(tt)
        done.append(tt)
        if p is not None:
            print("module", p.name)
        dlg = DIALOGS.get(tt)
        if dlg:
            print(" ", patch_dialog(tt, dlg))
    print(patch_handoff(done))
    print("synced", len(done), "types")


if __name__ == "__main__":
    main()
