# -*- coding: utf-8 -*-
"""一次性：接入过欠压_过欠频 Solar handoff / Agent runner。"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _replace(path: Path, old: str, new: str, *, label: str) -> None:
    t = path.read_text(encoding="utf-8")
    if old not in t:
        if new[:40] in t or ("ovuf" in t and label.startswith("skip-ok")):
            print(f"skip {path.name} ({label})")
            return
        raise SystemExit(f"missing anchor in {path}: {label}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    print(f"ok {path.relative_to(ROOT)} ({label})")


def patch_handoff() -> None:
    p = ROOT / "utils/iot_ui_handoff.py"
    t = p.read_text(encoding="utf-8")
    if '"ovuf":' in t and "resolve_ovuf_ui" in t:
        print("handoff already has ovuf")
        return

    reps = [
        (
            '''        "reconnect": ("重连", "reconnect"),
        "chonglian": ("重连", "reconnect"),
        "reconn": ("重连", "reconnect"),
        "重连": ("重连", "reconnect"),
        "重联": ("重连", "reconnect"),
        "重连测试": ("重连", "reconnect"),
    }
''',
            '''        "reconnect": ("重连", "reconnect"),
        "chonglian": ("重连", "reconnect"),
        "reconn": ("重连", "reconnect"),
        "重连": ("重连", "reconnect"),
        "重联": ("重连", "reconnect"),
        "重连测试": ("重连", "reconnect"),
        "ovuf": ("过欠压_过欠频", "ovuf"),
        "guoqianya_pin": ("过欠压_过欠频", "ovuf"),
        "volt_freq": ("过欠压_过欠频", "ovuf"),
        "过欠压_过欠频": ("过欠压_过欠频", "ovuf"),
        "过欠压过欠频": ("过欠压_过欠频", "ovuf"),
    }
''',
        ),
        (
            """        resolve_reconnect_ui: Optional[Callable[[], Any]] = None,
        reconnect_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
            """        resolve_reconnect_ui: Optional[Callable[[], Any]] = None,
        reconnect_append: Optional[Callable[[], None]] = None,
        resolve_ovuf_ui: Optional[Callable[[], Any]] = None,
        ovuf_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
""",
        ),
        (
            """        self.resolve_reconnect_ui = resolve_reconnect_ui
        self.reconnect_append = reconnect_append
        self.start_test = start_test
""",
            """        self.resolve_reconnect_ui = resolve_reconnect_ui
        self.reconnect_append = reconnect_append
        self.resolve_ovuf_ui = resolve_ovuf_ui
        self.ovuf_append = ovuf_append
        self.start_test = start_test
""",
        ),
        (
            '''        if handler_key == "reconnect":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_reconnect_ui,
                "append": self.reconnect_append,
                "label": "重连",
            }
        return None
''',
            '''        if handler_key == "reconnect":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_reconnect_ui,
                "append": self.reconnect_append,
                "label": "重连",
            }
        if handler_key == "ovuf":
            return {
                "key": handler_key,
                "project_name": project_name,
                "resolve_ui": self.resolve_ovuf_ui,
                "append": self.ovuf_append,
                "label": "过欠压_过欠频",
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
            ) and isinstance(widgets_for_ui, dict):
                if "radio_wt3000" not in widgets_for_ui and "radio_wt" in widgets_for_ui:
                    widgets_for_ui = {**widgets_for_ui, "radio_wt3000": widgets_for_ui.get("radio_wt")}
''',
            '''            if (handler.get("key") or "") in (
                "flicker",
                "harmonic",
                "fixedpf",
                "dccomponent",
                "reconnect",
                "ovuf",
            ) and isinstance(widgets_for_ui, dict):
                if "radio_wt3000" not in widgets_for_ui and "radio_wt" in widgets_for_ui:
                    widgets_for_ui = {**widgets_for_ui, "radio_wt3000": widgets_for_ui.get("radio_wt")}
''',
        ),
        (
            '''                elif (handler.get("key") or "") in (
                    "flicker",
                    "harmonic",
                    "fixedpf",
                    "dccomponent",
                    "reconnect",
                ) and isinstance(widgets, dict):
''',
            '''                elif (handler.get("key") or "") in (
                    "flicker",
                    "harmonic",
                    "fixedpf",
                    "dccomponent",
                    "reconnect",
                    "ovuf",
                ) and isinstance(widgets, dict):
''',
        ),
        (
            """    resolve_reconnect_ui: Optional[Callable[[], Any]] = None,
    reconnect_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
            """    resolve_reconnect_ui: Optional[Callable[[], Any]] = None,
    reconnect_append: Optional[Callable[[], None]] = None,
    resolve_ovuf_ui: Optional[Callable[[], Any]] = None,
    ovuf_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
""",
        ),
        (
            """        resolve_reconnect_ui=resolve_reconnect_ui,
        reconnect_append=reconnect_append,
        start_test=start_test,
""",
            """        resolve_reconnect_ui=resolve_reconnect_ui,
        reconnect_append=reconnect_append,
        resolve_ovuf_ui=resolve_ovuf_ui,
        ovuf_append=ovuf_append,
        start_test=start_test,
""",
        ),
    ]
    for i, (old, new) in enumerate(reps):
        if old not in t:
            raise SystemExit(f"handoff missing anchor #{i}: {old[:80]!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok handoff")


def patch_runner() -> None:
    p = ROOT / "agent/runners/__init__.py"
    _replace(
        p,
        '''        "reconnect",
        "chonglian",
        "reconn",
        "重连",
        "重联",
        "重连测试",
    ):
''',
        '''        "reconnect",
        "chonglian",
        "reconn",
        "重连",
        "重联",
        "重连测试",
        "ovuf",
        "guoqianya_pin",
        "volt_freq",
        "过欠压_过欠频",
        "过欠压过欠频",
    ):
''',
        label="runner aliases",
    )


def patch_scpi() -> None:
    p = ROOT / "SCPITestWave.py"
    t = p.read_text(encoding="utf-8")
    if "resolve_ovuf_ui" in t:
        print("SCPI already has ovuf handoff")
        return
    old = '''                def _resolve_reconnect_ui():
                    return globals().get("uithaichonglian")

                def _iot_get_run_status():
'''
    new = '''                def _resolve_reconnect_ui():
                    return globals().get("uithaichonglian")

                def _resolve_ovuf_ui():
                    return globals().get("uiThaiGuoQianYa_Pin")

                def _iot_get_run_status():
'''
    if old not in t:
        raise SystemExit("SCPI resolve_reconnect missing")
    t = t.replace(old, new, 1)
    old = """                    resolve_reconnect_ui=_resolve_reconnect_ui,
                    reconnect_append=thaichonglianAppend,
                    start_test=RunProjectPush,
"""
    new = """                    resolve_reconnect_ui=_resolve_reconnect_ui,
                    reconnect_append=thaichonglianAppend,
                    resolve_ovuf_ui=_resolve_ovuf_ui,
                    ovuf_append=thaiguoqianya_pinAppend,
                    start_test=RunProjectPush,
"""
    if old not in t:
        raise SystemExit("SCPI start_iot handoff kwargs missing")
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("ok SCPITestWave")


def patch_gen_skip_pct() -> None:
    p = ROOT / "code_example/gen_ovuf_iot_schema.py"
    t = p.read_text(encoding="utf-8")
    needle = '        if name in ("Dialog_thaiguoqianya_pin",):\n            continue\n'
    insert = (
        '        if name in ("Dialog_thaiguoqianya_pin",):\n'
        "            continue\n"
        '        if "%" in name:\n'
        "            continue\n"
    )
    if '%" in name' in t or '"%" in name' in t:
        print("gen already skips %")
        return
    if needle not in t:
        raise SystemExit("gen dialog skip missing")
    p.write_text(t.replace(needle, insert, 1), encoding="utf-8")
    # also sync cleaned schema to utils
    src = Path(r"E:/IOT/iot/app/services/solar_test_schemas/ovuf_fields.json")
    dst = ROOT / "utils/iot_ovuf_schema_data.json"
    if src.is_file():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print("synced utils/iot_ovuf_schema_data.json")
    print("ok gen skip")


def patch_runner_test() -> None:
    p = ROOT / "tests/test_agent_runner_fixedpf.py"
    t = p.read_text(encoding="utf-8")
    if 'get_runner("ovuf"' in t:
        print("runner test already has ovuf")
        return
    old = '''    r6 = get_runner("reconnect", dry_run=True, execution_mode="handoff")
    r7 = get_runner("重连", dry_run=True, execution_mode="handoff")
'''
    # read full file to see assert pattern
    if old not in t:
        raise SystemExit("runner test reconnect lines missing")
    # append ovuf lines after reconnect
    new = '''    r6 = get_runner("reconnect", dry_run=True, execution_mode="handoff")
    r7 = get_runner("重连", dry_run=True, execution_mode="handoff")
    r8 = get_runner("ovuf", dry_run=True, execution_mode="handoff")
    r9 = get_runner("过欠压_过欠频", dry_run=True, execution_mode="handoff")
'''
    t = t.replace(old, new, 1)
    # also ensure asserts if present
    if "assert r6 is not None" in t and "assert r8 is not None" not in t:
        t = t.replace(
            "assert r7 is not None",
            "assert r7 is not None\n    assert r8 is not None\n    assert r9 is not None",
            1,
        )
    p.write_text(t, encoding="utf-8")
    print("ok runner test")


def main() -> None:
    patch_handoff()
    patch_runner()
    patch_scpi()
    patch_gen_skip_pct()
    patch_runner_test()
    print("Solar ovuf wire done")


if __name__ == "__main__":
    main()
