# -*- coding: utf-8 -*-
"""reactiveqacc 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

REACTIVEQACC_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,70,50,20',
        'textEdit_S3_TIME_2': '60',
        '_reactiveqaccLadder': '100,70,50,20',
        '_reactiveqaccDwell': '60',
        'textEdit_QLadder': '100,50,0,-50,-100',
        '_reactiveqaccQLadder': '100,50,0,-50,-100',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,75,50,25',
        'textEdit_S3_TIME_2': '30',
        '_reactiveqaccLadder': '100,75,50,25',
        '_reactiveqaccDwell': '30',
        'textEdit_QLadder': '100,50,0,-50,-100',
        '_reactiveqaccQLadder': '100,50,0,-50,-100',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'textEdit_PowerLadder': '100,50,20',
        'textEdit_S3_TIME_2': '45',
        '_reactiveqaccLadder': '100,50,20',
        '_reactiveqaccDwell': '45',
        'textEdit_QLadder': '100,0,-100',
        '_reactiveqaccQLadder': '100,0,-100',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,66,33',
        'textEdit_S3_TIME_2': '40',
        '_reactiveqaccLadder': '100,66,33',
        '_reactiveqaccDwell': '40',
        'textEdit_QLadder': '100,50,0,-50,-100',
        '_reactiveqaccQLadder': '100,50,0,-50,-100',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,50,0',
        'textEdit_S3_TIME_2': '50',
        '_reactiveqaccLadder': '100,50,0',
        '_reactiveqaccDwell': '50',
        'textEdit_QLadder': '100,0,-100',
        '_reactiveqaccQLadder': '100,0,-100',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,80,40,20',
        'textEdit_S3_TIME_2': '35',
        '_reactiveqaccLadder': '100,80,40,20',
        '_reactiveqaccDwell': '35',
        'textEdit_QLadder': '100,66,0,-66,-100',
        '_reactiveqaccQLadder': '100,66,0,-66,-100',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,50',
        'textEdit_S3_TIME_2': '55',
        '_reactiveqaccLadder': '100,50',
        '_reactiveqaccDwell': '55',
        'textEdit_QLadder': '100,50,0,-50,-100',
        '_reactiveqaccQLadder': '100,50,0,-50,-100',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_PowerLadder': '100,50,10',
        'textEdit_S3_TIME_2': '20',
        '_reactiveqaccLadder': '100,50,10',
        '_reactiveqaccDwell': '20',
        'textEdit_QLadder': '100,0,-100',
        '_reactiveqaccQLadder': '100,0,-100',
    },
}

REACTIVEQACC_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_reactiveqacc_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in REACTIVEQACC_STANDARD_OPTIONS]


def normalize_reactiveqacc_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in REACTIVEQACC_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_reactiveqacc_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_reactiveqacc_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_reactiveqacc_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_reactiveqacc_standard_id(standard_id) or "thai"
    defaults = REACTIVEQACC_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_reactiveqacc_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_reactiveqacc_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_reactiveqacc_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
