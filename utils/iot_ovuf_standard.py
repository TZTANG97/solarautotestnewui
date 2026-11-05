# -*- coding: utf-8 -*-
"""ovuf 国家标准 → Dialog widgets（与 IOT solar_standard_profiles 对齐）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

OVUF_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT_Start': '230',
        'textEdit_S3_AC_VOLT_End': '230',
        'textEdit_S3_AC_FR_Start': '50',
        'textEdit_S3_AC_FR_End': '50',
        'textEdit_S3_Step_Size': '5',
        'textEdit_S3_TIME': '3',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT_Start': '230',
        'textEdit_S4_AC_VOLT_End': '230',
        'textEdit_S4_AC_FR_Start': '50',
        'textEdit_S4_AC_FR_End': '50',
        'textEdit_S4_Step_Size': '5',
        'textEdit_S4_TIME': '3',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT_Start': '230',
        'textEdit_S5_AC_VOLT_End': '230',
        'textEdit_S5_AC_FR_Start': '50',
        'textEdit_S5_AC_FR_End': '50',
        'textEdit_S5_Step_Size': '5',
        'textEdit_S5_TIME': '3',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': True,
        'textEdit_S6_AC_VOLT_Start': '230',
        'textEdit_S6_AC_VOLT_End': '230',
        'textEdit_S6_AC_FR_Start': '50',
        'textEdit_S6_AC_FR_End': '50',
        'textEdit_S6_Step_Size': '5',
        'textEdit_S6_TIME': '3',
        'comboBox_S6_TIME': '秒',
        '_ovufDwellSec': '3',
        '_ovufScanMask': 'ov+uv+of+uf',
    },
    "de_vde": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT_Start': '230',
        'textEdit_S3_AC_VOLT_End': '264',
        'textEdit_S3_AC_FR_Start': '50',
        'textEdit_S3_AC_FR_End': '50',
        'textEdit_S3_Step_Size': '2',
        'textEdit_S3_TIME': '4',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT_Start': '230',
        'textEdit_S4_AC_VOLT_End': '184',
        'textEdit_S4_AC_FR_Start': '50',
        'textEdit_S4_AC_FR_End': '50',
        'textEdit_S4_Step_Size': '2',
        'textEdit_S4_TIME': '4',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT_Start': '230',
        'textEdit_S5_AC_VOLT_End': '230',
        'textEdit_S5_AC_FR_Start': '50',
        'textEdit_S5_AC_FR_End': '51.5',
        'textEdit_S5_Step_Size': '0.2',
        'textEdit_S5_TIME': '4',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': True,
        'textEdit_S6_AC_VOLT_Start': '230',
        'textEdit_S6_AC_VOLT_End': '230',
        'textEdit_S6_AC_FR_Start': '50',
        'textEdit_S6_AC_FR_End': '47.5',
        'textEdit_S6_Step_Size': '0.2',
        'textEdit_S6_TIME': '4',
        'comboBox_S6_TIME': '秒',
        '_ovufDwellSec': '4',
        '_ovufScanMask': 'ov+uv+of+uf',
    },
    "br_ord140": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '60',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT_Start': '220',
        'textEdit_S3_AC_VOLT_End': '242',
        'textEdit_S3_AC_FR_Start': '60',
        'textEdit_S3_AC_FR_End': '60',
        'textEdit_S3_Step_Size': '1',
        'textEdit_S3_TIME': '3',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT_Start': '220',
        'textEdit_S4_AC_VOLT_End': '176',
        'textEdit_S4_AC_FR_Start': '60',
        'textEdit_S4_AC_FR_End': '60',
        'textEdit_S4_Step_Size': '1',
        'textEdit_S4_TIME': '3',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT_Start': '220',
        'textEdit_S5_AC_VOLT_End': '220',
        'textEdit_S5_AC_FR_Start': '60',
        'textEdit_S5_AC_FR_End': '62',
        'textEdit_S5_Step_Size': '0.1',
        'textEdit_S5_TIME': '3',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': True,
        'textEdit_S6_AC_VOLT_Start': '220',
        'textEdit_S6_AC_VOLT_End': '220',
        'textEdit_S6_AC_FR_Start': '60',
        'textEdit_S6_AC_FR_End': '57',
        'textEdit_S6_Step_Size': '0.1',
        'textEdit_S6_TIME': '3',
        'comboBox_S6_TIME': '秒',
        '_ovufDwellSec': '3',
        '_ovufScanMask': 'ov+uv+of+uf',
    },
    "en50549": {
        'comboBox_S1_AC_2': '三相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT_Start': '230',
        'textEdit_S3_AC_VOLT_End': '253',
        'textEdit_S3_AC_FR_Start': '50',
        'textEdit_S3_AC_FR_End': '50',
        'textEdit_S3_Step_Size': '1',
        'textEdit_S3_TIME': '5',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT_Start': '230',
        'textEdit_S4_AC_VOLT_End': '184',
        'textEdit_S4_AC_FR_Start': '50',
        'textEdit_S4_AC_FR_End': '50',
        'textEdit_S4_Step_Size': '1',
        'textEdit_S4_TIME': '5',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT_Start': '230',
        'textEdit_S5_AC_VOLT_End': '230',
        'textEdit_S5_AC_FR_Start': '50',
        'textEdit_S5_AC_FR_End': '51.5',
        'textEdit_S5_Step_Size': '0.1',
        'textEdit_S5_TIME': '5',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': True,
        'textEdit_S6_AC_VOLT_Start': '230',
        'textEdit_S6_AC_VOLT_End': '230',
        'textEdit_S6_AC_FR_Start': '50',
        'textEdit_S6_AC_FR_End': '47.5',
        'textEdit_S6_Step_Size': '0.1',
        'textEdit_S6_TIME': '5',
        'comboBox_S6_TIME': '秒',
        '_ovufDwellSec': '5',
        '_ovufScanMask': 'ov+uv+of+uf',
    },
    "as_nzs": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT_Start': '230',
        'textEdit_S3_AC_VOLT_End': '253',
        'textEdit_S3_AC_FR_Start': '50',
        'textEdit_S3_AC_FR_End': '50',
        'textEdit_S3_Step_Size': '1',
        'textEdit_S3_TIME': '6',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT_Start': '230',
        'textEdit_S4_AC_VOLT_End': '180',
        'textEdit_S4_AC_FR_Start': '50',
        'textEdit_S4_AC_FR_End': '50',
        'textEdit_S4_Step_Size': '1',
        'textEdit_S4_TIME': '6',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': False,
        'checkBox_S6': False,
        '_ovufDwellSec': '6',
        '_ovufScanMask': 'ov+uv',
    },
    "it_cei": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT_Start': '230',
        'textEdit_S3_AC_VOLT_End': '253',
        'textEdit_S3_AC_FR_Start': '50',
        'textEdit_S3_AC_FR_End': '50',
        'textEdit_S3_Step_Size': '1',
        'textEdit_S3_TIME': '8',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT_Start': '230',
        'textEdit_S4_AC_VOLT_End': '184',
        'textEdit_S4_AC_FR_Start': '50',
        'textEdit_S4_AC_FR_End': '50',
        'textEdit_S4_Step_Size': '1',
        'textEdit_S4_TIME': '8',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT_Start': '230',
        'textEdit_S5_AC_VOLT_End': '230',
        'textEdit_S5_AC_FR_Start': '50',
        'textEdit_S5_AC_FR_End': '51.5',
        'textEdit_S5_Step_Size': '0.1',
        'textEdit_S5_TIME': '8',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': True,
        'textEdit_S6_AC_VOLT_Start': '230',
        'textEdit_S6_AC_VOLT_End': '230',
        'textEdit_S6_AC_FR_Start': '50',
        'textEdit_S6_AC_FR_End': '47.5',
        'textEdit_S6_Step_Size': '0.1',
        'textEdit_S6_TIME': '8',
        'comboBox_S6_TIME': '秒',
        '_ovufDwellSec': '8',
        '_ovufScanMask': 'ov+uv+of+uf',
    },
    "uk_g99": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT_Start': '230',
        'textEdit_S3_AC_VOLT_End': '253',
        'textEdit_S3_AC_FR_Start': '50',
        'textEdit_S3_AC_FR_End': '50',
        'textEdit_S3_Step_Size': '1',
        'textEdit_S3_TIME': '10',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT_Start': '230',
        'textEdit_S4_AC_VOLT_End': '184',
        'textEdit_S4_AC_FR_Start': '50',
        'textEdit_S4_AC_FR_End': '50',
        'textEdit_S4_Step_Size': '1',
        'textEdit_S4_TIME': '10',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': False,
        'checkBox_S6': False,
        '_ovufDwellSec': '10',
        '_ovufScanMask': 'ov+uv',
    },
    "iec61727": {
        'comboBox_S1_AC_2': '单相',
        'textEdit_S1_AC_FR': '50',
        'checkBox_S3': True,
        'textEdit_S3_AC_VOLT_Start': '230',
        'textEdit_S3_AC_VOLT_End': '253',
        'textEdit_S3_AC_FR_Start': '50',
        'textEdit_S3_AC_FR_End': '50',
        'textEdit_S3_Step_Size': '1',
        'textEdit_S3_TIME': '2',
        'comboBox_S3_TIME': '秒',
        'checkBox_S4': True,
        'textEdit_S4_AC_VOLT_Start': '230',
        'textEdit_S4_AC_VOLT_End': '184',
        'textEdit_S4_AC_FR_Start': '50',
        'textEdit_S4_AC_FR_End': '50',
        'textEdit_S4_Step_Size': '1',
        'textEdit_S4_TIME': '2',
        'comboBox_S4_TIME': '秒',
        'checkBox_S5': True,
        'textEdit_S5_AC_VOLT_Start': '230',
        'textEdit_S5_AC_VOLT_End': '230',
        'textEdit_S5_AC_FR_Start': '50',
        'textEdit_S5_AC_FR_End': '51',
        'textEdit_S5_Step_Size': '0.1',
        'textEdit_S5_TIME': '2',
        'comboBox_S5_TIME': '秒',
        'checkBox_S6': True,
        'textEdit_S6_AC_VOLT_Start': '230',
        'textEdit_S6_AC_VOLT_End': '230',
        'textEdit_S6_AC_FR_Start': '50',
        'textEdit_S6_AC_FR_End': '49',
        'textEdit_S6_Step_Size': '0.1',
        'textEdit_S6_TIME': '2',
        'comboBox_S6_TIME': '秒',
        '_ovufDwellSec': '2',
        '_ovufScanMask': 'ov+uv+of+uf',
    },
}

OVUF_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)

def list_ovuf_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in OVUF_STANDARD_OPTIONS]


def normalize_ovuf_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in OVUF_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_ovuf_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_ovuf_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_ovuf_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_ovuf_standard_id(standard_id) or "thai"
    defaults = OVUF_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    # 元数据 _ovufDwellSec → 可见「段间并网等待」控件（handoff/表单可改）
    dwell = out.get("_ovufDwellSec")
    if dwell not in (None, ""):
        if force or out.get("textEdit_ovuf_grid_wait") in (None, ""):
            out["textEdit_ovuf_grid_wait"] = str(dwell)
        if force or out.get("comboBox_ovuf_grid_wait") in (None, ""):
            out["comboBox_ovuf_grid_wait"] = "秒"
    # 防呆：段间等待常见 1~30「秒」；若单位误成「分钟」会把 2 秒拖成 2 分钟，
    # Soft Panel/段间空等会被当成「采集时长没生效」。
    try:
        gw = float(str(out.get("textEdit_ovuf_grid_wait") or "").strip() or "0")
    except (TypeError, ValueError):
        gw = 0.0
    unit = str(out.get("comboBox_ovuf_grid_wait") or "").strip()
    if gw > 0 and gw <= 30 and unit in ("分钟", "分", "min", "minute", "minutes"):
        out["comboBox_ovuf_grid_wait"] = "秒"
    return out


def apply_ovuf_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_ovuf_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_ovuf_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    dwell = defaults.get("_ovufDwellSec")
    if dwell not in (None, ""):
        setattr(ui, "_ovufDwellSec", str(dwell))
    return sid
