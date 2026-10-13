# -*- coding: utf-8 -*-
"""phasejump 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

PHASEJUMP_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'TIMING_PROFILE_JSON': '[{"enabled": true, "label": "相角 +10°", "t_pre": 1, "t_pre_unit": "秒", "t_dwell": 0.5, "t_dwell_unit": "秒", "t_post": 2, "t_post_unit": "秒", "phase_deg": 10, "repeats": 1}]',
        '_phasejumpDeg': '10',
        '_phasejumpDwell': '0.5',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'TIMING_PROFILE_JSON': '[{"enabled": true, "label": "相角 +20°", "t_pre": 1, "t_pre_unit": "秒", "t_dwell": 0.5, "t_dwell_unit": "秒", "t_post": 2, "t_post_unit": "秒", "phase_deg": 20, "repeats": 1}]',
        '_phasejumpDeg': '20',
        '_phasejumpDwell': '0.5',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'TIMING_PROFILE_JSON': '[{"enabled": true, "label": "相角 +15°", "t_pre": 1, "t_pre_unit": "秒", "t_dwell": 0.5, "t_dwell_unit": "秒", "t_post": 2, "t_post_unit": "秒", "phase_deg": 15, "repeats": 1}]',
        '_phasejumpDeg': '15',
        '_phasejumpDwell': '0.5',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'TIMING_PROFILE_JSON': '[{"enabled": true, "label": "相角 +30°", "t_pre": 1, "t_pre_unit": "秒", "t_dwell": 0.5, "t_dwell_unit": "秒", "t_post": 2, "t_post_unit": "秒", "phase_deg": 30, "repeats": 1}]',
        '_phasejumpDeg': '30',
        '_phasejumpDwell': '0.5',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'TIMING_PROFILE_JSON': '[{"enabled": true, "label": "相角 +20°", "t_pre": 1, "t_pre_unit": "秒", "t_dwell": 0.6, "t_dwell_unit": "秒", "t_post": 2, "t_post_unit": "秒", "phase_deg": 20, "repeats": 1}]',
        '_phasejumpDeg': '20',
        '_phasejumpDwell': '0.6',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'TIMING_PROFILE_JSON': '[{"enabled": true, "label": "相角 +15°", "t_pre": 1, "t_pre_unit": "秒", "t_dwell": 0.4, "t_dwell_unit": "秒", "t_post": 2, "t_post_unit": "秒", "phase_deg": 15, "repeats": 1}]',
        '_phasejumpDeg': '15',
        '_phasejumpDwell': '0.4',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'TIMING_PROFILE_JSON': '[{"enabled": true, "label": "相角 +40°", "t_pre": 1, "t_pre_unit": "秒", "t_dwell": 0.5, "t_dwell_unit": "秒", "t_post": 2, "t_post_unit": "秒", "phase_deg": 40, "repeats": 1}]',
        '_phasejumpDeg': '40',
        '_phasejumpDwell': '0.5',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'TIMING_PROFILE_JSON': '[{"enabled": true, "label": "相角 +10°", "t_pre": 1, "t_pre_unit": "秒", "t_dwell": 0.3, "t_dwell_unit": "秒", "t_post": 2, "t_post_unit": "秒", "phase_deg": 10, "repeats": 1}]',
        '_phasejumpDeg': '10',
        '_phasejumpDwell': '0.3',
    },
}

PHASEJUMP_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_phasejump_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in PHASEJUMP_STANDARD_OPTIONS]


def normalize_phasejump_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in PHASEJUMP_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_phasejump_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_phasejump_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_phasejump_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_phasejump_standard_id(standard_id) or "thai"
    defaults = PHASEJUMP_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_phasejump_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_phasejump_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_phasejump_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
