# -*- coding: utf-8 -*-
"""rapidvolt 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

RAPIDVOLT_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_volt_start_rvc': '230',
        'textEdit_S3_volt_end_rvc': '207',
        'textEdit_S3_pre_hold_rvc': '1',
        'textEdit_S3_post_hold_rvc': '3',
        'textEdit_S4_volt_start_rvc': '230',
        'textEdit_S4_volt_end_rvc': '253',
        'textEdit_S4_pre_hold_rvc': '1',
        'textEdit_S4_post_hold_rvc': '3',
        '_rapidvoltLo': '207',
        '_rapidvoltHi': '253',
        '_rapidvoltHold': '3',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_volt_start_rvc': '230',
        'textEdit_S3_volt_end_rvc': '184',
        'textEdit_S3_pre_hold_rvc': '1',
        'textEdit_S3_post_hold_rvc': '2',
        'textEdit_S4_volt_start_rvc': '230',
        'textEdit_S4_volt_end_rvc': '264',
        'textEdit_S4_pre_hold_rvc': '1',
        'textEdit_S4_post_hold_rvc': '2',
        '_rapidvoltLo': '184',
        '_rapidvoltHi': '264',
        '_rapidvoltHold': '2',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'textEdit_S3_volt_start_rvc': '220',
        'textEdit_S3_volt_end_rvc': '198',
        'textEdit_S3_pre_hold_rvc': '1',
        'textEdit_S3_post_hold_rvc': '3',
        'textEdit_S4_volt_start_rvc': '220',
        'textEdit_S4_volt_end_rvc': '242',
        'textEdit_S4_pre_hold_rvc': '1',
        'textEdit_S4_post_hold_rvc': '3',
        '_rapidvoltLo': '198',
        '_rapidvoltHi': '242',
        '_rapidvoltHold': '3',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_volt_start_rvc': '230',
        'textEdit_S3_volt_end_rvc': '184',
        'textEdit_S3_pre_hold_rvc': '1',
        'textEdit_S3_post_hold_rvc': '3',
        'textEdit_S4_volt_start_rvc': '230',
        'textEdit_S4_volt_end_rvc': '253',
        'textEdit_S4_pre_hold_rvc': '1',
        'textEdit_S4_post_hold_rvc': '3',
        '_rapidvoltLo': '184',
        '_rapidvoltHi': '253',
        '_rapidvoltHold': '3',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_volt_start_rvc': '230',
        'textEdit_S3_volt_end_rvc': '180',
        'textEdit_S3_pre_hold_rvc': '1',
        'textEdit_S3_post_hold_rvc': '4',
        'textEdit_S4_volt_start_rvc': '230',
        'textEdit_S4_volt_end_rvc': '253',
        'textEdit_S4_pre_hold_rvc': '1',
        'textEdit_S4_post_hold_rvc': '4',
        '_rapidvoltLo': '180',
        '_rapidvoltHi': '253',
        '_rapidvoltHold': '4',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_volt_start_rvc': '230',
        'textEdit_S3_volt_end_rvc': '184',
        'textEdit_S3_pre_hold_rvc': '1',
        'textEdit_S3_post_hold_rvc': '2',
        'textEdit_S4_volt_start_rvc': '230',
        'textEdit_S4_volt_end_rvc': '253',
        'textEdit_S4_pre_hold_rvc': '1',
        'textEdit_S4_post_hold_rvc': '2',
        '_rapidvoltLo': '184',
        '_rapidvoltHi': '253',
        '_rapidvoltHold': '2',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_volt_start_rvc': '230',
        'textEdit_S3_volt_end_rvc': '184',
        'textEdit_S3_pre_hold_rvc': '1',
        'textEdit_S3_post_hold_rvc': '5',
        'textEdit_S4_volt_start_rvc': '230',
        'textEdit_S4_volt_end_rvc': '253',
        'textEdit_S4_pre_hold_rvc': '1',
        'textEdit_S4_post_hold_rvc': '5',
        '_rapidvoltLo': '184',
        '_rapidvoltHi': '253',
        '_rapidvoltHold': '5',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_volt_start_rvc': '230',
        'textEdit_S3_volt_end_rvc': '207',
        'textEdit_S3_pre_hold_rvc': '1',
        'textEdit_S3_post_hold_rvc': '1',
        'textEdit_S4_volt_start_rvc': '230',
        'textEdit_S4_volt_end_rvc': '253',
        'textEdit_S4_pre_hold_rvc': '1',
        'textEdit_S4_post_hold_rvc': '1',
        '_rapidvoltLo': '207',
        '_rapidvoltHi': '253',
        '_rapidvoltHold': '1',
    },
}

RAPIDVOLT_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_rapidvolt_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in RAPIDVOLT_STANDARD_OPTIONS]


def normalize_rapidvolt_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in RAPIDVOLT_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_rapidvolt_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_rapidvolt_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_rapidvolt_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_rapidvolt_standard_id(standard_id) or "thai"
    defaults = RAPIDVOLT_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_rapidvolt_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_rapidvolt_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_rapidvolt_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
