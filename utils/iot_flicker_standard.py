# -*- coding: utf-8 -*-
"""闪变国家标准 → Dialog widgets 默认（与 IOT solar_standard_profiles 对齐）。

桌面 handoff / Send 认 solarStandard：闪变 8 套标准均已拉开可验收工况默认。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

# 与 IOT app/services/solar_standard_profiles.py 保持同步
_FLICKER_DEW_230_50 = {
    "comboBox_DEW_WeightingType": "230V / 50Hz",
    "textEdit_DEW_NominalVoltage": "230",
}

FLICKER_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        **_FLICKER_DEW_230_50,
        "checkBox_DEW_FlickerStandard": True,
        "textEdit_S2_TIME": "4",
        "comboBox_S2_TIME": "分钟",
        "comboBox_S2_PER_FLICK_COUNT": "3",
        "textEdit_DEW_S2_TIME": "5",
        "comboBox_DEW_S2_TIME": "分钟",
        "comboBox_DEW_S2_PER_FLICK_COUNT": "3",
        "textEdit_DEW_ShortFlickerTime": "10",
        "textEdit_DEW_LongFlickerTime": "120",
        "textEdit_S3_TIME": "15",
        "textEdit_S3_TIME_2": "2",
        "textEdit_S3_CYCLE_TIME": "12",
        "comboBox_S2_WT": "单相",
        "_flickerCycleSec": "600",
    },
    "en50549": {
        **_FLICKER_DEW_230_50,
        "checkBox_DEW_FlickerStandard": True,
        "textEdit_S2_TIME": "10",
        "comboBox_S2_TIME": "分钟",
        "comboBox_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_S2_TIME": "10",
        "comboBox_DEW_S2_TIME": "分钟",
        "comboBox_DEW_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_ShortFlickerTime": "10",
        "textEdit_DEW_LongFlickerTime": "120",
        "textEdit_S3_TIME": "10",
        "textEdit_S3_TIME_2": "5",
        "textEdit_S3_CYCLE_TIME": "10",
        "comboBox_S2_WT": "三相",
        "_flickerCycleSec": "600",
        "_flickerPstLimit": "1.0",
        "_flickerPltLimit": "0.65",
    },
    "de_vde": {
        **_FLICKER_DEW_230_50,
        "checkBox_DEW_FlickerStandard": True,
        "textEdit_S1_AC_FR": "50",
        "textEdit_S2_TIME": "12",
        "comboBox_S2_TIME": "分钟",
        "comboBox_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_S2_TIME": "12",
        "comboBox_DEW_S2_TIME": "分钟",
        "comboBox_DEW_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_ShortFlickerTime": "10",
        "textEdit_DEW_LongFlickerTime": "120",
        "textEdit_S3_TIME": "20",
        "textEdit_S3_TIME_2": "1",
        "textEdit_S3_CYCLE_TIME": "12",
        "comboBox_S2_WT": "三相",
        "_flickerCycleSec": "720",
        "_flickerPstLimit": "1.0",
        "_flickerPltLimit": "0.65",
    },
    "br_ord140": {
        "comboBox_DEW_WeightingType": "230V / 60Hz",
        "textEdit_DEW_NominalVoltage": "220",
        "checkBox_DEW_FlickerStandard": True,
        "textEdit_S1_AC_FR": "60",
        "textEdit_S2_TIME": "10",
        "comboBox_S2_TIME": "分钟",
        "comboBox_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_S2_TIME": "10",
        "comboBox_DEW_S2_TIME": "分钟",
        "comboBox_DEW_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_ShortFlickerTime": "10",
        "textEdit_DEW_LongFlickerTime": "120",
        "textEdit_S3_TIME": "10",
        "textEdit_S3_TIME_2": "3",
        "textEdit_S3_CYCLE_TIME": "10",
        "comboBox_S2_WT": "三相",
        "_flickerCycleSec": "600",
        "_flickerPstLimit": "1.0",
        "_flickerPltLimit": "0.65",
    },
    "iec61727": {
        **_FLICKER_DEW_230_50,
        "checkBox_DEW_FlickerStandard": True,
        "textEdit_S1_AC_FR": "50",
        "textEdit_S2_TIME": "10",
        "comboBox_S2_TIME": "分钟",
        "comboBox_S2_PER_FLICK_COUNT": "2",
        "textEdit_DEW_S2_TIME": "10",
        "comboBox_DEW_S2_TIME": "分钟",
        "comboBox_DEW_S2_PER_FLICK_COUNT": "2",
        "textEdit_DEW_ShortFlickerTime": "10",
        "textEdit_DEW_LongFlickerTime": "120",
        "textEdit_S3_TIME": "10",
        "textEdit_S3_TIME_2": "2",
        "textEdit_S3_CYCLE_TIME": "10",
        "comboBox_S2_WT": "单相",
        "_flickerCycleSec": "600",
        "_flickerPstLimit": "1.0",
        "_flickerPltLimit": "0.65",
    },
    "as_nzs": {
        **_FLICKER_DEW_230_50,
        "checkBox_DEW_FlickerStandard": True,
        "textEdit_S1_AC_FR": "50",
        "textEdit_S2_TIME": "10",
        "comboBox_S2_TIME": "分钟",
        "comboBox_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_S2_TIME": "10",
        "comboBox_DEW_S2_TIME": "分钟",
        "comboBox_DEW_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_ShortFlickerTime": "10",
        "textEdit_DEW_LongFlickerTime": "120",
        "textEdit_S3_TIME": "10",
        "textEdit_S3_TIME_2": "4",
        "textEdit_S3_CYCLE_TIME": "10",
        "comboBox_S2_WT": "单相",
        "_flickerCycleSec": "600",
        "_flickerPstLimit": "1.0",
        "_flickerPltLimit": "0.65",
    },
    "it_cei": {
        **_FLICKER_DEW_230_50,
        "checkBox_DEW_FlickerStandard": True,
        "textEdit_S1_AC_FR": "50",
        "textEdit_S2_TIME": "10",
        "comboBox_S2_TIME": "分钟",
        "comboBox_S2_PER_FLICK_COUNT": "3",
        "textEdit_DEW_S2_TIME": "10",
        "comboBox_DEW_S2_TIME": "分钟",
        "comboBox_DEW_S2_PER_FLICK_COUNT": "3",
        "textEdit_DEW_ShortFlickerTime": "10",
        "textEdit_DEW_LongFlickerTime": "120",
        "textEdit_S3_TIME": "8",
        "textEdit_S3_TIME_2": "4",
        "textEdit_S3_CYCLE_TIME": "12",
        "comboBox_S2_WT": "单相",
        "_flickerCycleSec": "600",
        "_flickerPstLimit": "1.0",
        "_flickerPltLimit": "0.65",
    },
    "uk_g99": {
        **_FLICKER_DEW_230_50,
        "checkBox_DEW_FlickerStandard": True,
        "textEdit_S1_AC_FR": "50",
        "textEdit_S2_TIME": "10",
        "comboBox_S2_TIME": "分钟",
        "comboBox_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_S2_TIME": "10",
        "comboBox_DEW_S2_TIME": "分钟",
        "comboBox_DEW_S2_PER_FLICK_COUNT": "1",
        "textEdit_DEW_ShortFlickerTime": "10",
        "textEdit_DEW_LongFlickerTime": "120",
        "textEdit_S3_TIME": "15",
        "textEdit_S3_TIME_2": "2",
        "textEdit_S3_CYCLE_TIME": "12",
        "comboBox_S2_WT": "单相",
        "_flickerCycleSec": "7200",
        "_flickerPstLimit": "1.0",
        "_flickerPltLimit": "0.65",
    },
}


def normalize_flicker_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    if s in FLICKER_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_flicker_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_flicker_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def flicker_cycle_seconds(standard_id: str, widgets: Optional[Dict[str, Any]] = None) -> int:
    w = widgets if isinstance(widgets, dict) else {}
    raw = w.get("_flickerCycleSec")
    if raw not in (None, ""):
        try:
            return max(60, int(float(raw)))
        except (TypeError, ValueError):
            pass
    sid = normalize_flicker_standard_id(standard_id) or "thai"
    d = FLICKER_STANDARD_DEFAULTS.get(sid) or {}
    try:
        return max(60, int(float(d.get("_flickerCycleSec") or 600)))
    except (TypeError, ValueError):
        return 600


def apply_flicker_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    """把标准默认合并进 widgets；force 时覆盖同名键（空/_ 元数据除外的标准键）。"""
    out = dict(widgets or {})
    sid = normalize_flicker_standard_id(standard_id) or "thai"
    defaults = FLICKER_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out
