# -*- coding: utf-8 -*-
"""qianpinshengzai 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

QIANPINSHENGZAI_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,49.75,49.5,49.25,49.0,49.25,49.5,49.75,50',
        'textEdit_FrequencyLadder_TIME': '60',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_qianpinDwellSec': '60',
        '_qianpinFList': '50,49.75,49.5,49.25,49.0,49.25,49.5,49.75,50',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,49.8,49.5,48.5,49.5,49.8,50',
        'textEdit_FrequencyLadder_TIME': '20',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_qianpinDwellSec': '20',
        '_qianpinFList': '50,49.8,49.5,48.5,49.5,49.8,50',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '220',
        'textEdit_FrequencyLadder': '60,59.9,59.5,59.0,58.5,59.0,59.5,59.9,60',
        'textEdit_FrequencyLadder_TIME': '30',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_qianpinDwellSec': '30',
        '_qianpinFList': '60,59.9,59.5,59.0,58.5,59.0,59.5,59.9,60',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,49.8,49.5,49.0,48.5,49.0,49.5,49.8,50',
        'textEdit_FrequencyLadder_TIME': '30',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_qianpinDwellSec': '30',
        '_qianpinFList': '50,49.8,49.5,49.0,48.5,49.0,49.5,49.8,50',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,49.5,49.0,48.5,48.0,48.5,49.0,49.5,50',
        'textEdit_FrequencyLadder_TIME': '45',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_qianpinDwellSec': '45',
        '_qianpinFList': '50,49.5,49.0,48.5,48.0,48.5,49.0,49.5,50',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,49.9,49.7,49.5,49.0,49.5,49.7,49.9,50',
        'textEdit_FrequencyLadder_TIME': '40',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_qianpinDwellSec': '40',
        '_qianpinFList': '50,49.9,49.7,49.5,49.0,49.5,49.7,49.9,50',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,49.5,49.0,48.0,49.0,49.5,50',
        'textEdit_FrequencyLadder_TIME': '55',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_qianpinDwellSec': '55',
        '_qianpinFList': '50,49.5,49.0,48.0,49.0,49.5,50',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,49.5,49.0,49.5,50',
        'textEdit_FrequencyLadder_TIME': '15',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_qianpinDwellSec': '15',
        '_qianpinFList': '50,49.5,49.0,49.5,50',
    },
}

QIANPINSHENGZAI_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_qianpinshengzai_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in QIANPINSHENGZAI_STANDARD_OPTIONS]


def normalize_qianpinshengzai_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in QIANPINSHENGZAI_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_qianpinshengzai_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_qianpinshengzai_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_qianpinshengzai_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_qianpinshengzai_standard_id(standard_id) or "thai"
    defaults = QIANPINSHENGZAI_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_qianpinshengzai_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_qianpinshengzai_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_qianpinshengzai_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
