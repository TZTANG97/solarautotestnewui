# -*- coding: utf-8 -*-
"""固定PF=1 国家标准 → Dialog widgets 默认（与 IOT solar_standard_profiles 对齐）。

默认 thai = 现行台架；切换标准才改功率点/频率/采集时长，不碰 WT/德威创模式。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

# S4…S8 ↔ PF_4…PF_8（与 Dialog_thaifixedPF 一致）
_PF_POINT_FIELDS: Tuple[Tuple[str, str], ...] = (
    ("checkBox_S4", "textEdit_S1_DC1_PF_4"),
    ("checkBox_S5", "textEdit_S1_DC1_PF_5"),
    ("checkBox_S6", "textEdit_S1_DC1_PF_6"),
    ("checkBox_S7", "textEdit_S1_DC1_PF_7"),
    ("checkBox_S8", "textEdit_S1_DC1_PF_8"),
)


def _power_points(pcts: Sequence[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for i, (cb, pf) in enumerate(_PF_POINT_FIELDS):
        if i < len(pcts):
            out[cb] = True
            out[pf] = str(pcts[i])
        else:
            out[cb] = False
    return out


FIXEDPF_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "thai": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100", "75", "50", "30", "20")),
        "textEdit_S3_TIME_2": "10",
        "_fixedpfMinCos": "0.99",
    },
    "en50549": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "15",
        "_fixedpfMinCos": "0.99",
    },
    "de_vde": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100", "50")),
        "textEdit_S3_TIME_2": "12",
        "_fixedpfMinCos": "0.99",
    },
    "br_ord140": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "60",
        **_power_points(("100", "50")),
        "textEdit_S3_TIME_2": "10",
        "_fixedpfMinCos": "0.98",
    },
    "iec61727": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "10",
        "_fixedpfMinCos": "0.85",
    },
    "as_nzs": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "12",
        "_fixedpfMinCos": "0.95",
    },
    "it_cei": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100", "75", "50")),
        "textEdit_S3_TIME_2": "10",
        "_fixedpfMinCos": "0.99",
    },
    "uk_g99": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        **_power_points(("100",)),
        "textEdit_S3_TIME_2": "20",
        "_fixedpfMinCos": "0.95",
    },
}

FIXEDPF_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)


def list_fixedpf_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in FIXEDPF_STANDARD_OPTIONS]


def normalize_fixedpf_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    aliases = {"iec": "iec61727", "cn_gb": "en50549"}
    s = aliases.get(s, s)
    if s in FIXEDPF_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_fixedpf_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_fixedpf_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_fixedpf_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_fixedpf_standard_id(standard_id) or "thai"
    defaults = FIXEDPF_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_fixedpf_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_fixedpf_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_fixedpf_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
