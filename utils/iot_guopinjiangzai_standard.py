# -*- coding: utf-8 -*-
"""guopinjiangzai 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

GUOPINJIANGZAI_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,50.25,50.7,51.15,50.7,50.25,50',
        'textEdit_FrequencyLadder_TIME': '60',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_guopinDwellSec': '60',
        '_guopinFList': '50,50.25,50.7,51.15,50.7,50.25,50',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,50.2,50.5,51.5,50.5,50.2,50',
        'textEdit_FrequencyLadder_TIME': '20',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_guopinDwellSec': '20',
        '_guopinFList': '50,50.2,50.5,51.5,50.5,50.2,50',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '220',
        'textEdit_FrequencyLadder': '60,60.1,60.5,61.0,61.5,61.0,60.5,60.1,60',
        'textEdit_FrequencyLadder_TIME': '30',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_guopinDwellSec': '30',
        '_guopinFList': '60,60.1,60.5,61.0,61.5,61.0,60.5,60.1,60',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,50.2,50.5,51.0,51.5,51.0,50.5,50.2,50',
        'textEdit_FrequencyLadder_TIME': '30',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_guopinDwellSec': '30',
        '_guopinFList': '50,50.2,50.5,51.0,51.5,51.0,50.5,50.2,50',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,50.5,51.0,51.5,52.0,51.5,51.0,50.5,50',
        'textEdit_FrequencyLadder_TIME': '45',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_guopinDwellSec': '45',
        '_guopinFList': '50,50.5,51.0,51.5,52.0,51.5,51.0,50.5,50',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,50.1,50.3,50.5,51.0,50.5,50.3,50.1,50',
        'textEdit_FrequencyLadder_TIME': '40',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_guopinDwellSec': '40',
        '_guopinFList': '50,50.1,50.3,50.5,51.0,50.5,50.3,50.1,50',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,50.5,51.0,52.0,51.0,50.5,50',
        'textEdit_FrequencyLadder_TIME': '55',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_guopinDwellSec': '55',
        '_guopinFList': '50,50.5,51.0,52.0,51.0,50.5,50',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_FrequencyLadder_VOLT': '230',
        'textEdit_FrequencyLadder': '50,50.5,51.0,50.5,50',
        'textEdit_FrequencyLadder_TIME': '15',
        'comboBox_FrequencyLadder_TIME': '秒',
        '_guopinDwellSec': '15',
        '_guopinFList': '50,50.5,51.0,50.5,50',
    },
}

GUOPINJIANGZAI_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_guopinjiangzai_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in GUOPINJIANGZAI_STANDARD_OPTIONS]


def normalize_guopinjiangzai_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in GUOPINJIANGZAI_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_guopinjiangzai_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_guopinjiangzai_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_guopinjiangzai_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_guopinjiangzai_standard_id(standard_id) or "thai"
    defaults = GUOPINJIANGZAI_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_guopinjiangzai_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_guopinjiangzai_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_guopinjiangzai_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
