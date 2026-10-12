# -*- coding: utf-8 -*-
"""谐波电流国家标准 → Dialog widgets 默认（与 IOT solar_standard_profiles 对齐）。

默认 thai = 现行台架；切换标准才改功率点/频率/阶次等，不碰 WT/德威创模式。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

# 谐波功率点卡片：step 勾选 ↔ 功率% 文本框（与 Dialog_thaixiebodianliu 一致）
_HARM_POINT_FIELDS: Tuple[Tuple[str, str], ...] = (
    ("checkBox_S3", "textEdit_S1_DC1_PF_2"),
    ("checkBox_S3_2", "textEdit_S1_DC1_PF_3"),
    ("checkBox_S3_3", "textEdit_S1_DC1_PF_4"),
    ("checkBox_S3_4", "textEdit_S1_DC1_PF_5"),
    ("checkBox_S3_5", "textEdit_S1_DC1_PF_6"),
    ("checkBox_S3_10", "textEdit_S1_DC1_PF_10"),
    ("checkBox_S3_6", "textEdit_S1_DC1_PF_9"),
    ("checkBox_S3_7", "textEdit_S1_DC1_PF_7"),
    ("checkBox_S3_9", "textEdit_S1_DC1_PF_11"),
    ("checkBox_S3_8", "textEdit_S1_DC1_PF_8"),
    ("checkBox_S3_11", "textEdit_S1_DC1_PF_12"),
)


def _power_points(pcts: Sequence[str]) -> Dict[str, Any]:
    """前 N 个功率点开启并写入 %；其余关闭。"""
    out: Dict[str, Any] = {}
    for i, (cb, pf) in enumerate(_HARM_POINT_FIELDS):
        if i < len(pcts):
            out[cb] = True
            out[pf] = str(pcts[i])
        else:
            out[cb] = False
    return out


_BASE_50_3P = {
    "comboBox_S1_AC_2": "三相",
    "textEdit_S1_AC_FR": "50",
    "checkBox_DEW_HarmonicEnabled": True,
    "textEdit_S3_TIME_2": "10",
}

HARMONIC_STANDARD_DEFAULTS: Dict[str, Dict[str, Any]] = {
    # 现行台架：100/50/33 三点、40 阶
    "thai": {
        **_BASE_50_3P,
        **_power_points(("100", "50", "33")),
        "spinBox_DEW_MaxHarmonicOrder": 40,
        "spinBox_DEW_THDOrder": 40,
        "_harmonicThdLimit": "5",
    },
    # EN：额定功率单点、50 阶窗口
    "en50549": {
        **_BASE_50_3P,
        **_power_points(("100",)),
        "spinBox_DEW_MaxHarmonicOrder": 50,
        "spinBox_DEW_THDOrder": 50,
        "textEdit_S3_TIME_2": "15",
        "_harmonicThdLimit": "5",
    },
    # 德：额定单点、稍长稳定
    "de_vde": {
        **_BASE_50_3P,
        **_power_points(("100",)),
        "spinBox_DEW_MaxHarmonicOrder": 40,
        "spinBox_DEW_THDOrder": 40,
        "textEdit_S3_TIME_2": "20",
        "_harmonicThdLimit": "5",
    },
    # 巴：60Hz、100/50
    "br_ord140": {
        "comboBox_S1_AC_2": "三相",
        "textEdit_S1_AC_FR": "60",
        "checkBox_DEW_HarmonicEnabled": True,
        **_power_points(("100", "50")),
        "spinBox_DEW_MaxHarmonicOrder": 40,
        "spinBox_DEW_THDOrder": 40,
        "textEdit_S3_TIME_2": "10",
        "_harmonicThdLimit": "5",
    },
    # IEC 61727：THD50<5%、单相可验收差、额定点
    "iec61727": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        "checkBox_DEW_HarmonicEnabled": True,
        **_power_points(("100",)),
        "spinBox_DEW_MaxHarmonicOrder": 40,
        "spinBox_DEW_THDOrder": 40,
        "textEdit_S3_TIME_2": "10",
        "_harmonicThdLimit": "5",
    },
    # 澳：单相、额定
    "as_nzs": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        "checkBox_DEW_HarmonicEnabled": True,
        **_power_points(("100",)),
        "spinBox_DEW_MaxHarmonicOrder": 40,
        "spinBox_DEW_THDOrder": 40,
        "textEdit_S3_TIME_2": "12",
        "_harmonicThdLimit": "5",
    },
    # 意：100/66/33 三功率点（对齐 CEI 报告习惯）
    "it_cei": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        "checkBox_DEW_HarmonicEnabled": True,
        **_power_points(("100", "66", "33")),
        "spinBox_DEW_MaxHarmonicOrder": 40,
        "spinBox_DEW_THDOrder": 40,
        "textEdit_S3_TIME_2": "10",
        "_harmonicThdLimit": "5",
    },
    # 英：单相、额定、稍长稳定
    "uk_g99": {
        "comboBox_S1_AC_2": "单相",
        "textEdit_S1_AC_FR": "50",
        "checkBox_DEW_HarmonicEnabled": True,
        **_power_points(("100",)),
        "spinBox_DEW_MaxHarmonicOrder": 40,
        "spinBox_DEW_THDOrder": 40,
        "textEdit_S3_TIME_2": "15",
        "_harmonicThdLimit": "5",
    },
}

HARMONIC_STANDARD_OPTIONS = (
    {"id": "thai", "label": "泰国 PEA/MEA（现行）"},
    {"id": "de_vde", "label": "德国 VDE"},
    {"id": "br_ord140", "label": "巴西 Ordinance 140"},
    {"id": "en50549", "label": "欧洲 EN 50549"},
    {"id": "as_nzs", "label": "澳洲 AS/NZS"},
    {"id": "it_cei", "label": "意大利 CEI"},
    {"id": "uk_g99", "label": "英国 G99/G98"},
    {"id": "iec61727", "label": "IEC 61727"},
)


def list_harmonic_standard_options() -> List[Dict[str, str]]:
    return [dict(x) for x in HARMONIC_STANDARD_OPTIONS]


def normalize_harmonic_standard_id(raw: Optional[str]) -> str:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "")
    if s in HARMONIC_STANDARD_DEFAULTS:
        return s
    return ""


def resolve_harmonic_standard_id(
    *,
    params: Optional[Dict[str, Any]] = None,
    widgets: Optional[Dict[str, Any]] = None,
) -> str:
    p = params if isinstance(params, dict) else {}
    w = widgets if isinstance(widgets, dict) else {}
    for src in (p, w):
        sid = normalize_harmonic_standard_id(
            src.get("solarStandard") or src.get("solar_standard") or src.get("standard")
        )
        if sid:
            return sid
    return "thai"


def apply_harmonic_standard_to_widgets(
    widgets: Optional[Dict[str, Any]],
    standard_id: str,
    *,
    force: bool = False,
) -> Dict[str, Any]:
    out = dict(widgets or {})
    sid = normalize_harmonic_standard_id(standard_id) or "thai"
    defaults = HARMONIC_STANDARD_DEFAULTS.get(sid) or {}
    out["solarStandard"] = sid
    for k, v in defaults.items():
        if force:
            out[k] = v
            continue
        cur = out.get(k)
        if cur is None or cur == "":
            out[k] = v
    return out


def apply_harmonic_standard_to_ui(
    ui: Any,
    standard_id: str,
    *,
    force: bool = True,
    apply_defaults: bool = True,
) -> str:
    from utils.iot_standard_widgets import apply_defaults_dict_to_ui, sync_standard_combo

    sid = normalize_harmonic_standard_id(standard_id) or "thai"
    setattr(ui, "_solar_standard", sid)
    sync_standard_combo(ui, sid)
    if not apply_defaults:
        return sid
    defaults = apply_harmonic_standard_to_widgets({}, sid, force=True)
    apply_defaults_dict_to_ui(ui, defaults, force=force)
    return sid
