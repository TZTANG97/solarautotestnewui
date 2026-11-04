# -*- coding: utf-8 -*-
"""云端 Job widgets（S1_* / Soft Panel 键）→ 桌面交流/直流启机参数抽取。

Web/Blockly 写 comboBox_S1_AC_2=Three|Single、textEdit_S1_DC1_*；
桌面 Soft Panel 读 comboBox_Phase / textEdit_Vmp 等。交接与开输出前统一映射。
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def normalize_phase_label(raw: Any) -> str:
    """统一为桌面 Dialog/Soft Panel 用的「单相」「三相」；无法识别则空串。"""
    s = str(raw or "").strip()
    if not s:
        return ""
    low = s.lower()
    if s in ("单相",) or low in ("single", "1") or "单相" in s:
        return "单相"
    if s in ("三相",) or low in ("three", "3") or "三相" in s:
        return "三相"
    return ""


def _pick(widgets: Dict[str, Any], *keys: str) -> str:
    for k in keys:
        if k not in widgets:
            continue
        v = str(widgets.get(k) or "").strip()
        if v:
            return v
    return ""


def extract_ac_boot_from_widgets(widgets: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """从云端 widgets 抽 AC 启机：phase / volt / freq。"""
    w = widgets if isinstance(widgets, dict) else {}
    phase_raw = _pick(w, "comboBox_Phase", "comboBox_S1_AC_2")
    return {
        "phase": normalize_phase_label(phase_raw),
        "volt": _pick(w, "textEdit_AC_VOLT", "textEdit_S1_AC_VOLT"),
        "freq": _pick(w, "textEdit_AC_FR", "textEdit_S1_AC_FR"),
    }


def extract_dc1_iv_from_widgets(widgets: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """从云端 widgets 抽 DC1 IV：Vmp/Imp/Voc/Isc/PF%。"""
    w = widgets if isinstance(widgets, dict) else {}
    return {
        "vmp": _pick(w, "textEdit_Vmp", "textEdit_S1_DC1_VOLT"),
        "imp": _pick(w, "textEdit_Imp", "textEdit_S1_DC1_CURR"),
        "voc": _pick(w, "textEdit_Voc", "textEdit_S1_DC1_Voc"),
        "isc": _pick(w, "textEdit_Isc", "textEdit_S1_DC1_Isc"),
        "pf": _pick(w, "textEdit_PF", "textEdit_S1_DC1_PF"),
    }


def phase_combo_aliases(text: str) -> Tuple[str, ...]:
    """QComboBox.findText 候选（Three↔三相）。"""
    n = normalize_phase_label(text)
    if n == "单相":
        return ("单相", "Single", "1")
    if n == "三相":
        return ("三相", "Three", "3")
    t = str(text or "").strip()
    return (t,) if t else ()


def normalize_output_on(raw: Any) -> Optional[bool]:
    """交流/直流「开启|关闭」；Blockly/Web 常写 ON|OFF|true。无法识别则 None。"""
    s = str(raw or "").strip()
    if not s:
        return None
    low = s.lower()
    if s in ("开启", "开") or low in ("on", "true", "1", "open", "enable", "enabled"):
        return True
    if s in ("关闭", "关") or low in ("off", "false", "0", "close", "disable", "disabled"):
        return False
    return None


def is_output_on(raw: Any, *, default: bool = False) -> bool:
    """Send 路径：明确关闭才不开；ON/开启/true 都开。"""
    flag = normalize_output_on(raw)
    if flag is None:
        return default
    return flag


def output_combo_aliases(text: str) -> Tuple[str, ...]:
    """QComboBox.findText 候选（ON↔开启）。"""
    flag = normalize_output_on(text)
    if flag is True:
        return ("开启", "开", "ON", "On", "on", "true", "1")
    if flag is False:
        return ("关闭", "关", "OFF", "Off", "off", "false", "0")
    t = str(text or "").strip()
    return (t,) if t else ()


_PHASE_VOLT_GROUPS = (
    ("textEdit_S1_AC_VOLT", "textEdit_S1_AC_VOLT_2", "textEdit_S1_AC_VOLT_3"),
    ("textEdit_S3_AC_VOLT", "textEdit_S3_AC_VOLT_2", "textEdit_S3_AC_VOLT_3"),
    ("textEdit_S4_AC_VOLT", "textEdit_S4_AC_VOLT_2", "textEdit_S4_AC_VOLT_3"),
)

def fill_missing_phase_volts(widgets: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """L1 有值而 L2/L3 空时抄 L1，避免 Soft Panel / 启机只写下了 A 相。

    缺交流开关时默认「开启」，避免桌面残留「关闭」导致直流开了交流没开。
    """
    out = dict(widgets or {})
    for l1, l2, l3 in _PHASE_VOLT_GROUPS:
        src = str(out.get(l1) or "").strip()
        if not src:
            continue
        if not str(out.get(l2) or "").strip():
            out[l2] = src
        if not str(out.get(l3) or "").strip():
            out[l3] = src
    if normalize_output_on(out.get("comboBox_S1_AC")) is None:
        out["comboBox_S1_AC"] = "开启"
    return out


def _set_phase_combo(combo, phase: str) -> bool:
    if combo is None or not phase or not hasattr(combo, "findText"):
        return False
    for candidate in phase_combo_aliases(phase):
        try:
            idx = int(combo.findText(candidate))
        except Exception:
            continue
        if idx >= 0:
            combo.setCurrentIndex(idx)
            return True
    return False


def _set_plain(widget, text: str) -> None:
    if widget is None or not str(text or "").strip():
        return
    value = str(text).strip()
    if hasattr(widget, "setPlainText"):
        widget.setPlainText(value)
    elif hasattr(widget, "setText"):
        widget.setText(value)


def apply_bluesight_sas_from_iv(ref, iv: Optional[Dict[str, str]]):
    """把网页四点写到蓝点页：模式选 SAS，填 Pmpp(kW) / Umpp(V) / 填充因子。

    曲线缓存用 100% 基准，工况功率%由试验步骤再乘。参数不够时返回 None。
    """
    from utils.guochan_sim_matrix import bluesight_stc_from_iv

    if not isinstance(ref, dict):
        return None
    src = iv if isinstance(iv, dict) else {}
    triple = bluesight_stc_from_iv(
        src.get("vmp"),
        src.get("imp"),
        src.get("voc"),
        src.get("isc"),
        "100",
    )
    if not triple:
        return None
    pmpp, umpp, ff = triple
    combo = ref.get("combo_mode")
    if combo is not None and hasattr(combo, "setCurrentIndex"):
        combo.setCurrentIndex(1)
    for key, val in (("sp_pmpp", pmpp), ("sp_umpp", umpp), ("sp_ff", ff)):
        spin = ref.get(key)
        if spin is not None and hasattr(spin, "setValue"):
            spin.setValue(float(val))
    return (float(pmpp), float(umpp), float(ff))


def apply_ac_boot_to_panels(ac: Optional[Dict[str, str]], *, chroma_ui=None, itech_ref=None) -> None:
    """电压/频率/单相三相同时写致茂页和爱科页。

    爱科连接读的是 combo_phase / textEdit_VOLT，只写致茂 comboBox_Phase
    时，重连仍按爱科页上的「单相」下发，并回写成云端单相。
    """
    src = ac if isinstance(ac, dict) else {}
    phase = str(src.get("phase") or "")
    volt = str(src.get("volt") or "")
    freq = str(src.get("freq") or "")
    if chroma_ui is not None:
        _set_phase_combo(getattr(chroma_ui, "comboBox_Phase", None), phase)
        _set_plain(getattr(chroma_ui, "textEdit_AC_VOLT", None), volt)
        _set_plain(getattr(chroma_ui, "textEdit_AC_FR", None), freq)
    if isinstance(itech_ref, dict):
        _set_phase_combo(itech_ref.get("combo_phase"), phase)
        _set_plain(itech_ref.get("textEdit_VOLT"), volt)
        _set_plain(itech_ref.get("textEdit_FR"), freq)
