# -*- coding: utf-8 -*-
"""开测时从各试验页抽出工况，避免多项追加只报上一份模板默认值。"""
from __future__ import annotations

from typing import Any, Dict, List


def _filled(value: Any) -> bool:
    text = str(value if value is not None else "").strip()
    return text not in ("", "false", "False", "None")


def _dc_on(widgets: Dict[str, Any], index: int) -> bool:
    flag = widgets.get(f"checkBox_S1_DC{index}")
    switch = str(widgets.get(f"comboBox_S1_DC{index}") or "").strip()
    return flag in (True, 1, "1", "true", "True") or switch == "开启"


def compact_start_condition(name: str, widgets: Dict[str, Any]) -> Dict[str, Any]:
    """只保留详情页要展示的交流/直流设定。"""
    w = widgets if isinstance(widgets, dict) else {}
    items: List[Dict[str, str]] = []

    def add(label: str, value: Any) -> None:
        if _filled(value):
            items.append({"label": label, "value": str(value).strip()})

    add("交流相数", w.get("comboBox_S1_AC_2"))
    add("交流电压", w.get("textEdit_S1_AC_VOLT"))
    add("交流电压2", w.get("textEdit_S1_AC_VOLT_2"))
    add("交流电压3", w.get("textEdit_S1_AC_VOLT_3"))
    add("频率", w.get("textEdit_S1_AC_FR") or w.get("textEdit_S1_AC_FREQ"))
    add("标准", w.get("solarStandard"))
    for index in range(1, 5):
        if not _dc_on(w, index):
            continue
        parts = []
        pairs = (
            ("Vmp", f"textEdit_S1_DC{index}_VOLT", "V"),
            ("Imp", f"textEdit_S1_DC{index}_CURR", "A"),
            ("Voc", f"textEdit_S1_DC{index}_Voc", "V"),
            ("Isc", f"textEdit_S1_DC{index}_Isc", "A"),
            ("功率", f"textEdit_S1_DC{index}_PF", "%"),
        )
        for title, key, unit in pairs:
            if _filled(w.get(key)):
                parts.append(f"{title} {w.get(key)}{unit}")
        if parts:
            items.append({"label": f"直流{index}", "value": " · ".join(parts)})
    return {"name": str(name or "").strip(), "items": items}
