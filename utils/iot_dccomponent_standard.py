# -*- coding: utf-8 -*-
"""直流分量国家标准 → Dialog widgets 默认（与 IOT solar_standard_profiles 对齐）。

默认 thai = 现行台架；切换标准才改功率点/频率/采集时长，不碰 WT/德威创模式。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

# S3=100% / S4=66% / S5=33% / S6=可选（与 Dialog_thaizhiliufenliang 一致）
_DC_POINT_FIELDS: Tuple[Tuple[str, str], ...] = (
    ("checkBox_S3", "textEdit_S3_DC_PF"),
    ("checkBox_S4", "textEdit_S4_DC_PF"),
    ("checkBox_S5", "textEdit_S5_DC_PF"),
    ("checkBox_S6", "textEdit_S6_DC_PF"),
)


def _power_points(pcts: Sequence[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for i, (cb, pf) in enumerate(_DC_POINT_FIELDS):
        if i < len(pcts):
            out[cb] = True
            out[pf] = str(pcts[i])
        else:
            out[cb] = False
    return out


DCCOMPONENT_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100", "66", "33")),
        "textEdit_S3_TIME_2": "5",
        "_dccomponentIdcLimitPct": "0.5",
    },
    "en50549": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "10",
        "_dccomponentIdcLimitPct": "0.5",
    },
    "de_vde": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "8",
        "_dccomponentIdcLimitPct": "0.5",
    },
    "br_ord140": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "60",
        **_power_points(("100", "50")),
        "textEdit_S3_TIME_2": "5",
        "_dccomponentIdcLimitPct": "0.5",
    },
    "iec61727": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "5",
        "_dccomponentIdcLimitPct": "0.5",
    },
    "as_nzs": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "6",
        "_dccomponentIdcLimitPct": "1.0",
    },
    "it_cei": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100", "66", "33")),
        "textEdit_S3_TIME_2": "5",
        "_dccomponentIdcLimitPct": "0.5",
    },
    "uk_g99": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "12",
        "_dccomponentIdcLimitPct": "0.5",
    },
}

DCCOMPONENT_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)


def list_dccomponent_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in DCCOMPONENT_STANDARD_OPTIONS]


def normalize_dccomponent_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in DCCOMPONENT_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_dccomponent_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_dccomponent_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_dccomponent_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_dccomponent_standard_id(standard_id) or "thai"
    defaults = DCCOMPONENT_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_dccomponent_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_dccomponent_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_dccomponent_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
