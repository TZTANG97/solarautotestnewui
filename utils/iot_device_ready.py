# -*- coding: utf-8 -*-
"""IOT handoff ready check."""
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
        reasons.append("交流电源未连接")
    slots = [str(s).strip().lower() for s in (required_dc_slots or []) if str(s).strip()]
    factors = per_dc_factor or {}
    controllers = dc_controllers or {}
    for slot in slots:
        if not slot.startswith("dc") or len(slot) < 3:
            continue
        try:
            idx = int(slot[-1]) - 1
        except ValueError:
            reasons.append("%s 槽位无效" % slot)
            continue
        ctrl = controllers.get(slot) or controllers.get(slot.upper())
        if not _ctrl_connected(ctrl):
            reasons.append("直流电源%s未连接" % slot[-1])
            continue
        brand = str(factors.get(str(idx)) or factors.get(idx) or "").strip()
        if brand not in KNOWN_DC_BRANDS:
            cur = brand or "空"
            reasons.append("直流电源%s厂家未识别（当前=%s）；请先连接并识别厂家，禁止致茂IVC混用" % (slot[-1], cur))
    return (len(reasons) == 0, reasons)

def format_ready_fail_reason(reasons):
    items = [str(r).strip() for r in reasons if str(r).strip()]
    if not items:
        return "设备未就绪"
    if len(items) == 1:
        return items[0]
    return "；".join("%d.%s" % (i + 1, t) for i, t in enumerate(items))
