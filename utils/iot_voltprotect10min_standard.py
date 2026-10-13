# -*- coding: utf-8 -*-
"""voltprotect10min 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

VOLTPROTECT10MIN_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'comboBox_S3_TIME': '分钟',
        'textEdit_S3_TIME': '10',
        'textEdit_S3_AC_VOLT': '230',
        'textEdit_S3_AC_VOLT_2': '230',
        'textEdit_S3_AC_VOLT_3': '230',
        'comboBox_S4_TIME': '分钟',
        'textEdit_S4_TIME': '3',
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_VOLT_2': '230',
        'textEdit_S4_AC_VOLT_3': '230',
        '_voltprotectAvgMin': '10',
        '_voltprotectOvVolt': '230',
        '_voltprotectNominalV': '230',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'comboBox_S3_TIME': '分钟',
        'textEdit_S3_TIME': '10',
        'textEdit_S3_AC_VOLT': '264',
        'textEdit_S3_AC_VOLT_2': '264',
        'textEdit_S3_AC_VOLT_3': '264',
        'comboBox_S4_TIME': '分钟',
        'textEdit_S4_TIME': '4',
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_VOLT_2': '230',
        'textEdit_S4_AC_VOLT_3': '230',
        '_voltprotectAvgMin': '10',
        '_voltprotectOvVolt': '264',
        '_voltprotectNominalV': '230',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'textEdit_S1_AC_VOLT': '220',
        'textEdit_S1_AC_VOLT_2': '220',
        'textEdit_S1_AC_VOLT_3': '220',
        'comboBox_S3_TIME': '分钟',
        'textEdit_S3_TIME': '10',
        'textEdit_S3_AC_VOLT': '242',
        'textEdit_S3_AC_VOLT_2': '242',
        'textEdit_S3_AC_VOLT_3': '242',
        'comboBox_S4_TIME': '分钟',
        'textEdit_S4_TIME': '3',
        'textEdit_S4_AC_VOLT': '220',
        'textEdit_S4_AC_VOLT_2': '220',
        'textEdit_S4_AC_VOLT_3': '220',
        '_voltprotectAvgMin': '10',
        '_voltprotectOvVolt': '242',
        '_voltprotectNominalV': '220',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'comboBox_S3_TIME': '分钟',
        'textEdit_S3_TIME': '10',
        'textEdit_S3_AC_VOLT': '253',
        'textEdit_S3_AC_VOLT_2': '253',
        'textEdit_S3_AC_VOLT_3': '253',
        'comboBox_S4_TIME': '分钟',
        'textEdit_S4_TIME': '5',
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_VOLT_2': '230',
        'textEdit_S4_AC_VOLT_3': '230',
        '_voltprotectAvgMin': '10',
        '_voltprotectOvVolt': '253',
        '_voltprotectNominalV': '230',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'comboBox_S3_TIME': '分钟',
        'textEdit_S3_TIME': '10',
        'textEdit_S3_AC_VOLT': '258',
        'textEdit_S3_AC_VOLT_2': '258',
        'textEdit_S3_AC_VOLT_3': '258',
        'comboBox_S4_TIME': '分钟',
        'textEdit_S4_TIME': '6',
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_VOLT_2': '230',
        'textEdit_S4_AC_VOLT_3': '230',
        '_voltprotectAvgMin': '10',
        '_voltprotectOvVolt': '258',
        '_voltprotectNominalV': '230',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'comboBox_S3_TIME': '分钟',
        'textEdit_S3_TIME': '10',
        'textEdit_S3_AC_VOLT': '255',
        'textEdit_S3_AC_VOLT_2': '255',
        'textEdit_S3_AC_VOLT_3': '255',
        'comboBox_S4_TIME': '分钟',
        'textEdit_S4_TIME': '8',
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_VOLT_2': '230',
        'textEdit_S4_AC_VOLT_3': '230',
        '_voltprotectAvgMin': '10',
        '_voltprotectOvVolt': '255',
        '_voltprotectNominalV': '230',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'comboBox_S3_TIME': '分钟',
        'textEdit_S3_TIME': '12',
        'textEdit_S3_AC_VOLT': '253',
        'textEdit_S3_AC_VOLT_2': '253',
        'textEdit_S3_AC_VOLT_3': '253',
        'comboBox_S4_TIME': '分钟',
        'textEdit_S4_TIME': '10',
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_VOLT_2': '230',
        'textEdit_S4_AC_VOLT_3': '230',
        '_voltprotectAvgMin': '12',
        '_voltprotectOvVolt': '253',
        '_voltprotectNominalV': '230',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'comboBox_S3_TIME': '分钟',
        'textEdit_S3_TIME': '8',
        'textEdit_S3_AC_VOLT': '253',
        'textEdit_S3_AC_VOLT_2': '253',
        'textEdit_S3_AC_VOLT_3': '253',
        'comboBox_S4_TIME': '分钟',
        'textEdit_S4_TIME': '2',
        'textEdit_S4_AC_VOLT': '230',
        'textEdit_S4_AC_VOLT_2': '230',
        'textEdit_S4_AC_VOLT_3': '230',
        '_voltprotectAvgMin': '8',
        '_voltprotectOvVolt': '253',
        '_voltprotectNominalV': '230',
    },
}

VOLTPROTECT10MIN_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_voltprotect10min_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in VOLTPROTECT10MIN_STANDARD_OPTIONS]


def normalize_voltprotect10min_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in VOLTPROTECT10MIN_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_voltprotect10min_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_voltprotect10min_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_voltprotect10min_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_voltprotect10min_standard_id(standard_id) or "thai"
    defaults = VOLTPROTECT10MIN_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_voltprotect10min_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_voltprotect10min_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_voltprotect10min_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
