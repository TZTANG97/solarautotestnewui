from pathlib import Path
src = r"""# -*- coding: utf-8 -*-
\"\"\"IOT handoff ready check.\"\"\"
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
KNOWN_DC_BRANDS = frozenset({"Chroma", "Keysight", "Itech", "Bluesight"})

def _ctrl_connected(ctrl):
    if ctrl is None:
        return False
    try:
        return bool(getattr(ctrl, "connected", False))
    except Exception:
        return False

def required_dc_slots_from_ui(ui_obj):
    if ui_obj is None:
        return []
    slots = []
    for n in (1, 2, 3, 4):
        names = ("checkBox_S1_DC%d" % n, "checkBox_DC%d" % n, "checkBox_S1_DC%d_Enable" % n)
        checked = False
        for name in names:
            w = getattr(ui_obj, name, None)
            if w is None:
                continue
            try:
                if bool(w.isChecked()):
                    checked = True
                    break
            except Exception:
                continue
        if checked:
            slots.append("dc%d" % n)
    return slots

def check_devices_ready(*, ac_controller=None, dc_controllers=None, per_dc_factor=None, required_dc_slots=None, require_ac=True):
    reasons = []
    if require_ac and not _ctrl_connected(ac_controller):
        reasons.append("\u4ea4\u6d41\u7535\u6e90\u672a\u8fde\u63a5")
    slots = [str(s).strip().lower() for s in (required_dc_slots or []) if str(s).strip()]
    factors = per_dc_factor or {}
    controllers = dc_controllers or {}
    for slot in slots:
        if not slot.startswith("dc") or len(slot) < 3:
            continue
        try:
            idx = int(slot[-1]) - 1
        except ValueError:
            reasons.append("%s \u69fd\u4f4d\u65e0\u6548" % slot)
            continue
        ctrl = controllers.get(slot) or controllers.get(slot.upper())
        if not _ctrl_connected(ctrl):
            reasons.append("\u76f4\u6d41\u7535\u6e90%s\u672a\u8fde\u63a5" % slot[-1])
            continue
        brand = str(factors.get(str(idx)) or factors.get(idx) or "").strip()
        if brand not in KNOWN_DC_BRANDS:
            cur = brand or "\u7a7a"
            reasons.append("\u76f4\u6d41\u7535\u6e90%s\u5382\u5bb6\u672a\u8bc6\u522b\uff08\u5f53\u524d=%s\uff09\uff1b\u8bf7\u5148\u8fde\u63a5\u5e76\u8bc6\u522b\u5382\u5bb6\uff0c\u7981\u6b62\u81f4\u8302IVC\u6df7\u7528" % (slot[-1], cur))
    return (len(reasons) == 0, reasons)

def format_ready_fail_reason(reasons):
    items = [str(r).strip() for r in reasons if str(r).strip()]
    if not items:
        return "\u8bbe\u5907\u672a\u5c31\u7eea"
    if len(items) == 1:
        return items[0]
    return "\uff1b".join("%d.%s" % (i + 1, t) for i, t in enumerate(items))
"""
# src contains literal backslash-u sequences; decode them
out = src.encode("utf-8").decode("unicode_escape")
# fix accidental decode of real escapes - the string used \\u in raw so unicode_escape works
Path(r"E:\solarautotestnewui\utils\iot_device_ready.py").write_text(out, encoding="utf-8")
# verify
t = Path(r"E:\solarautotestnewui\utils\iot_device_ready.py").read_text(encoding="utf-8")
assert "交流电源未连接" in t, t[t.find("reasons"):t.find("reasons")+80]
print("device_ready OK")