# -*- coding: utf-8 -*-
"""reactiveqcap 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

REACTIVEQCAP_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,70,50,20',
        'textEdit_S3_TIME_2': '60',
        '_reactiveqcapLadder': '100,70,50,20',
        '_reactiveqcapDwell': '60',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,75,50,25',
        'textEdit_S3_TIME_2': '30',
        '_reactiveqcapLadder': '100,75,50,25',
        '_reactiveqcapDwell': '30',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'textEdit_PowerLadder': '100,50,20',
        'textEdit_S3_TIME_2': '45',
        '_reactiveqcapLadder': '100,50,20',
        '_reactiveqcapDwell': '45',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,66,33',
        'textEdit_S3_TIME_2': '40',
        '_reactiveqcapLadder': '100,66,33',
        '_reactiveqcapDwell': '40',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,50,0',
        'textEdit_S3_TIME_2': '50',
        '_reactiveqcapLadder': '100,50,0',
        '_reactiveqcapDwell': '50',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,80,40,20',
        'textEdit_S3_TIME_2': '35',
        '_reactiveqcapLadder': '100,80,40,20',
        '_reactiveqcapDwell': '35',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,50',
        'textEdit_S3_TIME_2': '55',
        '_reactiveqcapLadder': '100,50',
        '_reactiveqcapDwell': '55',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,50,10',
        'textEdit_S3_TIME_2': '20',
        '_reactiveqcapLadder': '100,50,10',
        '_reactiveqcapDwell': '20',
    },
}

REACTIVEQCAP_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_reactiveqcap_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in REACTIVEQCAP_STANDARD_OPTIONS]


def normalize_reactiveqcap_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in REACTIVEQCAP_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_reactiveqcap_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_reactiveqcap_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def ensure_reactiveqcap_capability_widgets(widgets: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """开测前保证能力工况可生成命令：总开关开、至少一种极限 cosφ。"""
    out = dict(widgets or {})
    out["checkBox_S3"] = True
    cos_keys = ("checkBox_cos_pos09", "checkBox_cos_neg09", "checkBox_cos_1")
    if not any(bool(out.get(k)) for k in cos_keys):
        out["checkBox_cos_pos09"] = True
        out["checkBox_cos_neg09"] = True
        out["checkBox_cos_1"] = False
    return out


def apply_reactiveqcap_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_reactiveqcap_standard_id(standard_id) or "thai"
    defaults = REACTIVEQCAP_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return ensure_reactiveqcap_capability_widgets(out)


def apply_reactiveqcap_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_reactiveqcap_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_reactiveqcap_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
