# -*- coding: utf-8 -*-
"""antibackflow 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

ANTIBACKFLOW_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'textEdit_PowerLadder': '100,70,20,0',
        'comboBox_S3_TIME_2': '分钟',
        'textEdit_S3_TIME_2': '2',
        'textEdit_DcPowerPct': '100',
        'textEdit_OpWait': '30',
        'checkBox_S5_1': True,
        'checkBox_S5_2': True,
        'checkBox_S5_3': True,
        'checkBox_S5_4': True,
        '_antibackflowHoldMin': '2',
        '_antibackflowPowerLadder': '100,70,20,0',
        '_antibackflowScenarioMask': 'steady+load_cut+energy_step+comm_loss',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'textEdit_PowerLadder': '100,60,30,0',
        'comboBox_S3_TIME_2': '分钟',
        'textEdit_S3_TIME_2': '2',
        'textEdit_DcPowerPct': '100',
        'textEdit_OpWait': '40',
        'checkBox_S5_1': True,
        'checkBox_S5_2': True,
        'checkBox_S5_3': True,
        'checkBox_S5_4': True,
        '_antibackflowHoldMin': '2',
        '_antibackflowPowerLadder': '100,60,30,0',
        '_antibackflowScenarioMask': 'steady+load_cut+energy_step+comm_loss',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'textEdit_S1_AC_VOLT': '220',
        'textEdit_S1_AC_VOLT_2': '220',
        'textEdit_S1_AC_VOLT_3': '220',
        'textEdit_PowerLadder': '100,80,40,0',
        'comboBox_S3_TIME_2': '分钟',
        'textEdit_S3_TIME_2': '3',
        'textEdit_DcPowerPct': '100',
        'textEdit_OpWait': '35',
        'checkBox_S5_1': True,
        'checkBox_S5_2': True,
        'checkBox_S5_3': True,
        'checkBox_S5_4': True,
        '_antibackflowHoldMin': '3',
        '_antibackflowPowerLadder': '100,80,40,0',
        '_antibackflowScenarioMask': 'steady+load_cut+energy_step+comm_loss',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'textEdit_PowerLadder': '100,50,10,0',
        'comboBox_S3_TIME_2': '分钟',
        'textEdit_S3_TIME_2': '3',
        'textEdit_DcPowerPct': '100',
        'textEdit_OpWait': '45',
        'checkBox_S5_1': True,
        'checkBox_S5_2': True,
        'checkBox_S5_3': True,
        'checkBox_S5_4': False,
        '_antibackflowHoldMin': '3',
        '_antibackflowPowerLadder': '100,50,10,0',
        '_antibackflowScenarioMask': 'steady+load_cut+energy_step',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'textEdit_PowerLadder': '100,66,33,0',
        'comboBox_S3_TIME_2': '分钟',
        'textEdit_S3_TIME_2': '4',
        'textEdit_DcPowerPct': '100',
        'textEdit_OpWait': '50',
        'checkBox_S5_1': True,
        'checkBox_S5_2': True,
        'checkBox_S5_3': False,
        'checkBox_S5_4': True,
        '_antibackflowHoldMin': '4',
        '_antibackflowPowerLadder': '100,66,33,0',
        '_antibackflowScenarioMask': 'steady+load_cut+comm_loss',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'textEdit_PowerLadder': '100,75,25,0',
        'comboBox_S3_TIME_2': '分钟',
        'textEdit_S3_TIME_2': '5',
        'textEdit_DcPowerPct': '100',
        'textEdit_OpWait': '55',
        'checkBox_S5_1': True,
        'checkBox_S5_2': True,
        'checkBox_S5_3': True,
        'checkBox_S5_4': False,
        '_antibackflowHoldMin': '5',
        '_antibackflowPowerLadder': '100,75,25,0',
        '_antibackflowScenarioMask': 'steady+load_cut+energy_step',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'textEdit_PowerLadder': '100,50,25,0',
        'comboBox_S3_TIME_2': '分钟',
        'textEdit_S3_TIME_2': '6',
        'textEdit_DcPowerPct': '100',
        'textEdit_OpWait': '60',
        'checkBox_S5_1': True,
        'checkBox_S5_2': True,
        'checkBox_S5_3': False,
        'checkBox_S5_4': False,
        '_antibackflowHoldMin': '6',
        '_antibackflowPowerLadder': '100,50,25,0',
        '_antibackflowScenarioMask': 'steady+load_cut',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S1_AC_VOLT': '230',
        'textEdit_S1_AC_VOLT_2': '230',
        'textEdit_S1_AC_VOLT_3': '230',
        'textEdit_PowerLadder': '100,50,0',
        'comboBox_S3_TIME_2': '分钟',
        'textEdit_S3_TIME_2': '1',
        'textEdit_DcPowerPct': '100',
        'textEdit_OpWait': '20',
        'checkBox_S5_1': True,
        'checkBox_S5_2': True,
        'checkBox_S5_3': False,
        'checkBox_S5_4': False,
        '_antibackflowHoldMin': '1',
        '_antibackflowPowerLadder': '100,50,0',
        '_antibackflowScenarioMask': 'steady+load_cut',
    },
}

ANTIBACKFLOW_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_antibackflow_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in ANTIBACKFLOW_STANDARD_OPTIONS]


def normalize_antibackflow_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in ANTIBACKFLOW_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_antibackflow_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_antibackflow_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_antibackflow_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_antibackflow_standard_id(standard_id) or "thai"
    defaults = ANTIBACKFLOW_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_antibackflow_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_antibackflow_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_antibackflow_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
