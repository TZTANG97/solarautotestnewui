# -*- coding: utf-8 -*-
"""reconnect 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

RECONNECT_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT': '230',
        'textEdit_S3_AC_FR': '50',
        'textEdit_S3_TIME': '2.5',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_FR': '50',
        'textEdit_S4_TIME': '2.5',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT': '230',
        'textEdit_S5_AC_FR': '50',
        'textEdit_S5_TIME': '2.5',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': True,
        'textEdit_S6_AC_VOLT': '230',
        'textEdit_S6_AC_FR': '50',
        'textEdit_S6_TIME': '2.5',
        'comboBox_S6_TIME': '秒',
        'checkBox_S7': True,
        'textEdit_S7_AC_VOLT': '230',
        'textEdit_S7_AC_FR': '50',
        'textEdit_S7_TIME': '2.5',
        'comboBox_S7_TIME': '秒',
        '_reconnectObserveSec': '2.5',
        '_reconnectPointCount': '5',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT': '230',
        'textEdit_S3_AC_FR': '50',
        'textEdit_S3_TIME': '60',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_FR': '50',
        'textEdit_S4_TIME': '60',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': False,
        'checkBox_S6': False,
        'checkBox_S7': False,
        '_reconnectObserveSec': '60',
        '_reconnectPointCount': '2',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT': '220',
        'textEdit_S3_AC_FR': '60',
        'textEdit_S3_TIME': '10',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT': '220',
        'textEdit_S4_AC_FR': '60',
        'textEdit_S4_TIME': '10',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT': '220',
        'textEdit_S5_AC_FR': '60',
        'textEdit_S5_TIME': '10',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': False,
        'checkBox_S7': False,
        '_reconnectObserveSec': '10',
        '_reconnectPointCount': '3',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT': '230',
        'textEdit_S3_AC_FR': '50',
        'textEdit_S3_TIME': '20',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_FR': '50',
        'textEdit_S4_TIME': '20',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT': '230',
        'textEdit_S5_AC_FR': '50',
        'textEdit_S5_TIME': '20',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': False,
        'checkBox_S7': False,
        '_reconnectObserveSec': '20',
        '_reconnectPointCount': '3',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT': '230',
        'textEdit_S3_AC_FR': '50',
        'textEdit_S3_TIME': '60',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': False,
        'checkBox_S5': False,
        'checkBox_S6': False,
        'checkBox_S7': False,
        '_reconnectObserveSec': '60',
        '_reconnectPointCount': '1',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT': '230',
        'textEdit_S3_AC_FR': '50',
        'textEdit_S3_TIME': '30',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_FR': '50',
        'textEdit_S4_TIME': '30',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT': '230',
        'textEdit_S5_AC_FR': '50',
        'textEdit_S5_TIME': '30',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': False,
        'checkBox_S7': False,
        '_reconnectObserveSec': '30',
        '_reconnectPointCount': '3',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT': '230',
        'textEdit_S3_AC_FR': '50',
        'textEdit_S3_TIME': '20',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': False,
        'checkBox_S5': False,
        'checkBox_S6': False,
        'checkBox_S7': False,
        '_reconnectObserveSec': '20',
        '_reconnectPointCount': '1',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT': '230',
        'textEdit_S3_AC_FR': '50',
        'textEdit_S3_TIME': '15',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': False,
        'checkBox_S5': False,
        'checkBox_S6': False,
        'checkBox_S7': False,
        '_reconnectObserveSec': '15',
        '_reconnectPointCount': '1',
    },
}

RECONNECT_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_reconnect_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in RECONNECT_STANDARD_OPTIONS]


def normalize_reconnect_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in RECONNECT_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_reconnect_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_reconnect_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_reconnect_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_reconnect_standard_id(standard_id) or "thai"
    defaults = RECONNECT_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_reconnect_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_reconnect_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_reconnect_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
