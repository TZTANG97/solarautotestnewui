# -*- coding: utf-8 -*-
"""frequencyadaptability 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

FREQUENCYADAPTABILITY_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_freq_start_guopin': '50',
        'textEdit_S3_freq_end_guopin': '51.5',
        'textEdit_S3_test_duration_guopin': '30',
        'textEdit_S12_freq_start_qianpin': '50',
        'textEdit_S12_freq_end_qianpin': '47.5',
        'textEdit_S12_test_duration_qianpin': '30',
        '_freqadaptOfEnd': '51.5',
        '_freqadaptUfEnd': '47.5',
        '_freqadaptDwell': '30',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_freq_start_guopin': '50',
        'textEdit_S3_freq_end_guopin': '51.5',
        'textEdit_S3_test_duration_guopin': '20',
        'textEdit_S12_freq_start_qianpin': '50',
        'textEdit_S12_freq_end_qianpin': '47.5',
        'textEdit_S12_test_duration_qianpin': '20',
        '_freqadaptOfEnd': '51.5',
        '_freqadaptUfEnd': '47.5',
        '_freqadaptDwell': '20',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'textEdit_S3_freq_start_guopin': '60',
        'textEdit_S3_freq_end_guopin': '62.0',
        'textEdit_S3_test_duration_guopin': '30',
        'textEdit_S12_freq_start_qianpin': '60',
        'textEdit_S12_freq_end_qianpin': '57.0',
        'textEdit_S12_test_duration_qianpin': '30',
        '_freqadaptOfEnd': '62.0',
        '_freqadaptUfEnd': '57.0',
        '_freqadaptDwell': '30',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_freq_start_guopin': '50',
        'textEdit_S3_freq_end_guopin': '51.5',
        'textEdit_S3_test_duration_guopin': '25',
        'textEdit_S12_freq_start_qianpin': '50',
        'textEdit_S12_freq_end_qianpin': '47.5',
        'textEdit_S12_test_duration_qianpin': '25',
        '_freqadaptOfEnd': '51.5',
        '_freqadaptUfEnd': '47.5',
        '_freqadaptDwell': '25',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_freq_start_guopin': '50',
        'textEdit_S3_freq_end_guopin': '52.0',
        'textEdit_S3_test_duration_guopin': '40',
        'textEdit_S12_freq_start_qianpin': '50',
        'textEdit_S12_freq_end_qianpin': '47.0',
        'textEdit_S12_test_duration_qianpin': '40',
        '_freqadaptOfEnd': '52.0',
        '_freqadaptUfEnd': '47.0',
        '_freqadaptDwell': '40',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_freq_start_guopin': '50',
        'textEdit_S3_freq_end_guopin': '51.5',
        'textEdit_S3_test_duration_guopin': '35',
        'textEdit_S12_freq_start_qianpin': '50',
        'textEdit_S12_freq_end_qianpin': '47.5',
        'textEdit_S12_test_duration_qianpin': '35',
        '_freqadaptOfEnd': '51.5',
        '_freqadaptUfEnd': '47.5',
        '_freqadaptDwell': '35',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_freq_start_guopin': '50',
        'textEdit_S3_freq_end_guopin': '52.0',
        'textEdit_S3_test_duration_guopin': '45',
        'textEdit_S12_freq_start_qianpin': '50',
        'textEdit_S12_freq_end_qianpin': '47.0',
        'textEdit_S12_test_duration_qianpin': '45',
        '_freqadaptOfEnd': '52.0',
        '_freqadaptUfEnd': '47.0',
        '_freqadaptDwell': '45',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'textEdit_S3_freq_start_guopin': '50',
        'textEdit_S3_freq_end_guopin': '51.0',
        'textEdit_S3_test_duration_guopin': '15',
        'textEdit_S12_freq_start_qianpin': '50',
        'textEdit_S12_freq_end_qianpin': '49.0',
        'textEdit_S12_test_duration_qianpin': '15',
        '_freqadaptOfEnd': '51.0',
        '_freqadaptUfEnd': '49.0',
        '_freqadaptDwell': '15',
    },
}

FREQUENCYADAPTABILITY_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_frequencyadaptability_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in FREQUENCYADAPTABILITY_STANDARD_OPTIONS]


def normalize_frequencyadaptability_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in FREQUENCYADAPTABILITY_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_frequencyadaptability_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_frequencyadaptability_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_frequencyadaptability_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_frequencyadaptability_standard_id(standard_id) or "thai"
    defaults = FREQUENCYADAPTABILITY_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_frequencyadaptability_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_frequencyadaptability_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_frequencyadaptability_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
