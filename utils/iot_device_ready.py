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
    from utils.dc_channels import channel_numbers

    slots = []
    for n in channel_numbers():
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
        tail = slot[2:]
        if not tail.isdigit():
            reasons.append("%s 槽位无效" % slot)
            continue
        idx = int(tail) - 1
        label = tail
        ctrl = controllers.get(slot) or controllers.get(slot.upper())
        if not _ctrl_connected(ctrl):
            reasons.append("直流电源%s未连接" % label)
            continue
        brand = str(factors.get(str(idx)) or factors.get(idx) or "").strip()
        if brand not in KNOWN_DC_BRANDS:
            cur = brand or "空"
            reasons.append("直流电源%s厂家未识别（当前=%s）；请先连接并识别厂家，禁止致茂IVC混用" % (label, cur))
    return (len(reasons) == 0, reasons)

def _widget_checked(owner, name):
    if owner is None:
        return False
    widget = getattr(owner, name, None)
    if widget is None:
        return False
    try:
        return bool(widget.isChecked())
    except Exception:
        return False


def analyzer_slot_required(ui_obj):
    """本试验要哪台分析仪：dew / wt / ''。

    checkBox_S2 是功率分析仪和德威创共用的步骤开关，不代表一定用 WT。
    面板或单选已是德威创时，只认 dew，避免 S2 勾着却去报「功率分析仪未连接」。
    """
    if ui_obj is None:
        return ""
    section = getattr(ui_obj, "analyzerModeSection", None)
    if section is not None:
        try:
            if hasattr(section, "is_dewetron_mode") and bool(section.is_dewetron_mode()):
                return "dew"
        except Exception:
            pass
        try:
            mode = str(section.current_mode() or "").strip().lower()
        except Exception:
            mode = ""
        if mode in ("dewetron", "dew"):
            return "dew"
    if any(
        _widget_checked(ui_obj, name)
        for name in (
            "radio_dewetron",
            "radioButton_DEWETRON",
            "radio_S2_DEWETRON",
            "radioButton_S2_DEWETRON",
        )
    ):
        return "dew"
    if section is not None:
        try:
            mode = str(section.current_mode() or "").strip().lower()
        except Exception:
            mode = ""
        if mode in ("wt", "wt3000", "power_analyzer"):
            return "wt"
    if any(
        _widget_checked(ui_obj, name)
        for name in (
            "radio_wt3000",
            "radio_wt",
            "radioButton_WT3000",
            "radioButton_WT",
            "radio_S2_WT3000",
            "radioButton_S2_WT3000",
        )
    ):
        return "wt"
    if _widget_checked(ui_obj, "checkBox_S2"):
        return "wt"
    return ""


def format_ready_fail_reason(reasons):
    items = [str(r).strip() for r in reasons if str(r).strip()]
    if not items:
        return "设备未就绪"
    if len(items) == 1:
        return items[0]
    return "；".join("%d.%s" % (i + 1, t) for i, t in enumerate(items))
