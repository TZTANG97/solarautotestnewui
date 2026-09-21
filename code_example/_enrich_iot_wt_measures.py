# -*- coding: utf-8 -*-
"""从 wt_config_content 抽出全部测量勾选名，写入 IOT schema。"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WT_SRC = ROOT / "components" / "wt_config_content.py"
IOT_DIR = Path(r"E:/IOT/iot/app/services/solar_test_schemas")
SW_PATHS = [
    ROOT / "utils" / "iot_overload_schema_data.json",
    ROOT / "utils" / "iot_antibackflow_schema_data.json",
]


def extract_measure_names(src: str) -> list[str]:
    names = set()
    # "checkBox_SetXxx"
    for m in re.finditer(r"[\"'](checkBox_Set[A-Za-z0-9_]+)[\"']", src):
        names.add(m.group(1))
    # f"checkBox_SetElement{i}" style — expand 1..6 common
    for m in re.finditer(
        r'f[\"\'](checkBox_Set[A-Za-z0-9_]*)\{i\}[\"\']',
        src,
    ):
        base = m.group(1)
        for i in range(1, 7):
            names.add(f"{base}{i}")
    # checkBox_AutoName etc
    for m in re.finditer(r"[\"'](checkBox_AutoName|checkBox_[A-Za-z0-9_]+)[\"']", src):
        n = m.group(1)
        if n.startswith("checkBox_") and ("Set" in n or n == "checkBox_AutoName"):
            names.add(n)
    return sorted(names)


def main() -> int:
    src = WT_SRC.read_text(encoding="utf-8")
    names = extract_measure_names(src)
    print("measure names", len(names))

    measure_fields = [
        {
            "name": n,
            "label": n.replace("checkBox_Set", "").replace("checkBox_", ""),
            "type": "checkbox",
            "group": "step2_wt_cfg",
            "default": False,
            "options": [],
            "uiHint": "wt_measure",
        }
        for n in names
    ]

    targets = list(IOT_DIR.glob("*_fields.json")) + [p for p in SW_PATHS if p.is_file()]
    for path in targets:
        schema = json.loads(path.read_text(encoding="utf-8"))
        fields = list(schema.get("fields") or [])
        existing = {f["name"] for f in fields}
        added = 0
        for f in measure_fields:
            if f["name"] in existing:
                continue
            fields.append(f)
            existing.add(f["name"])
            added += 1
        # ensure groups
        gids = {g["id"] for g in schema.get("groups") or []}
        if "step2_wt_cfg" not in gids:
            groups = list(schema.get("groups") or [])
            idx = next((i for i, g in enumerate(groups) if g["id"] == "step2_wt"), len(groups))
            groups.insert(idx + 1, {"id": "step2_wt_cfg", "title": "② 功率分析仪 · 测量/存盘"})
            schema["groups"] = groups
        schema["fields"] = sorted(fields, key=lambda x: (x.get("group") or "", x["name"]))
        path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{path.name}: +{added} total={len(schema['fields'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
