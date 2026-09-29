# -*- coding: utf-8 -*-
"""充实 IOT 试验 schema：DC 默认只开1、补 WT 测量项/德威创字段。"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WT_SRC = ROOT / "components" / "wt_config_content.py"
DEW_SRC = ROOT / "components" / "dewetron_autotest_panel.py"

IOT_DIR = Path(r"E:/IOT/iot/app/services/solar_test_schemas")
SW_OVERLOAD = ROOT / "utils" / "iot_overload_schema_data.json"
SW_ANTI = ROOT / "utils" / "iot_antibackflow_schema_data.json"


def _parse_wt_fields() -> list[dict]:
    src = WT_SRC.read_text(encoding="utf-8")
    fields: dict[str, dict] = {}

    for m in re.finditer(
        r"_make_cb\(\s*parent\s*,\s*[\"']([^\"']+)[\"']\s*,\s*[\"']([^\"']*)[\"']\s*(?:,\s*(True|False))?",
        src,
    ):
        name, label, checked = m.group(1), m.group(2), m.group(3)
        fields[name] = {
            "name": name,
            "label": label or name,
            "type": "checkbox",
            "group": "step2_wt_cfg",
            "default": checked == "True" if checked else False,
            "options": [],
            "uiHint": "wt_measure",
        }

    for m in re.finditer(
        r"_make_combo\(\s*parent\s*,\s*[\"']([^\"']+)[\"']\s*,\s*\[([^\]]+)\]",
        src,
    ):
        name, items_raw = m.group(1), m.group(2)
        opts = re.findall(r"[\"']([^\"']+)[\"']", items_raw)
        fields[name] = {
            "name": name,
            "label": name.replace("comboBox_", "").replace("_", " "),
            "type": "select",
            "group": "step2_wt_cfg",
            "default": opts[0] if opts else None,
            "options": opts,
            "uiHint": "wt_cfg",
        }

    for m in re.finditer(
        r"_make_te\(\s*parent\s*,\s*[\"']([^\"']+)[\"']",
        src,
    ):
        name = m.group(1)
        label = "录波文件名列表" if "FileName" in name else (
            "停止时间" if "StopTime" in name else name
        )
        fields[name] = {
            "name": name,
            "label": label,
            "type": "text",
            "group": "step2_wt_cfg",
            "default": "",
            "options": [],
            "uiHint": "wt_cfg",
        }

    # Prefer first occurrence defaults already set; return sorted
    return sorted(fields.values(), key=lambda x: (x.get("uiHint") or "", x["name"]))


def _parse_dew_fields() -> list[dict]:
    src = DEW_SRC.read_text(encoding="utf-8")
    fields: dict[str, dict] = {}
    for m in re.finditer(r'\.setObjectName\(\s*[\"\']([^\"\']+)[\"\']\s*\)', src):
        name = m.group(1)
        if not name.startswith(("comboBox_DEW_", "spinBox_DEW_", "checkBox_DEW_", "radio_dewetron", "radio_wt")):
            continue
        if name.startswith("checkBox_"):
            typ, default = "checkbox", False
        elif name.startswith("comboBox_"):
            typ, default = "select", None
        elif name.startswith("spinBox_"):
            typ, default = "number", 3
        elif name.startswith("radio_"):
            typ, default = "radio", name == "radio_wt"
        else:
            typ, default = "text", ""
        fields[name] = {
            "name": name,
            "label": {
                "radio_wt": "使用功率分析仪(WT)",
                "radio_dewetron": "使用德威创",
                "comboBox_DEW_MaxRefreshRate": "德威创刷新率",
                "spinBox_DEW_DecimalPlaces": "德威创小数位",
                "checkBox_DEW_RealtimeWaveform": "德威创实时波形",
            }.get(name, name),
            "type": typ,
            "group": "step2_dew" if "DEW" in name or name == "radio_dewetron" else "step2_wt",
            "default": default,
            "options": [],
            "uiHint": "dew" if "DEW" in name or name == "radio_dewetron" else "analyzer_mode",
        }
    return list(fields.values())


def _patch_dc_defaults(fields: list[dict]) -> None:
    for f in fields:
        name = f.get("name") or ""
        if name in ("checkBox_S1_DC2", "checkBox_S1_DC3", "checkBox_S1_DC4"):
            f["default"] = False
        if name in ("comboBox_S1_DC2", "comboBox_S1_DC3", "comboBox_S1_DC4"):
            f["default"] = "关闭"
            f["type"] = "select"
            if not f.get("options"):
                f["options"] = ["开启", "关闭"]
        if name == "checkBox_S1_DC1":
            f["default"] = True
        if name == "comboBox_S1_DC1":
            f["default"] = "开启"
            f["type"] = "select"
            if not f.get("options"):
                f["options"] = ["开启", "关闭"]


def _ensure_wt_radios(fields: list[dict]) -> None:
    names = {f["name"] for f in fields}
    radios = [
        ("radio_S2_WT3000", "选用 WT3000", True),
        ("radio_S2_WT1800", "选用 WT1800", False),
        ("radio_S2_WT1806E", "选用 WT1806E", False),
        ("radio_S2_WT5000", "选用 WT5000", False),
        ("radio_dewetron", "使用德威创", False),
        ("radio_wt", "使用功率分析仪(WT)", True),
    ]
    for name, label, default in radios:
        if name in names:
            for f in fields:
                if f["name"] == name:
                    f["type"] = "radio"
                    f["group"] = "step2_wt"
                    if f.get("default") is None:
                        f["default"] = default
                    f["label"] = label
            continue
        fields.append(
            {
                "name": name,
                "label": label,
                "type": "radio",
                "group": "step2_wt",
                "default": default,
                "options": [],
                "uiHint": "analyzer_mode",
            }
        )


def _merge_schema(path: Path, wt_fields: list[dict], dew_fields: list[dict]) -> dict:
    schema = json.loads(path.read_text(encoding="utf-8"))
    fields = list(schema.get("fields") or [])
    _patch_dc_defaults(fields)
    _ensure_wt_radios(fields)

    existing = {f["name"] for f in fields}
    for f in wt_fields + dew_fields:
        if f["name"] in existing:
            continue
        fields.append(f)
        existing.add(f["name"])

    groups = list(schema.get("groups") or [])
    gids = {g["id"] for g in groups}
    for gid, title in (
        ("step2_wt_cfg", "② 功率分析仪 · 测量/存盘"),
        ("step2_dew", "② 德威创"),
    ):
        if gid not in gids:
            # insert after step2_wt if present
            idx = next((i for i, g in enumerate(groups) if g["id"] == "step2_wt"), len(groups) - 1)
            groups.insert(idx + 1, {"id": gid, "title": title})
            gids.add(gid)

    schema["fields"] = sorted(fields, key=lambda x: (x.get("group") or "", x["name"]))
    schema["groups"] = groups
    schema["version"] = int(schema.get("version") or 1) + 1
    return schema


def main() -> int:
    wt_fields = _parse_wt_fields()
    dew_fields = _parse_dew_fields()
    print(f"wt_fields={len(wt_fields)} dew_fields={len(dew_fields)}")

    targets = [
        (IOT_DIR / "overload_fields.json", SW_OVERLOAD),
        (IOT_DIR / "antibackflow_fields.json", SW_ANTI),
    ]
    for iot_path, sw_path in targets:
        if not iot_path.is_file():
            print("skip missing", iot_path)
            continue
        schema = _merge_schema(iot_path, wt_fields, dew_fields)
        text = json.dumps(schema, ensure_ascii=False, indent=2)
        iot_path.write_text(text + "\n", encoding="utf-8")
        sw_path.parent.mkdir(parents=True, exist_ok=True)
        sw_path.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {iot_path.name} fields={len(schema['fields'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
