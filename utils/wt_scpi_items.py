# -*- coding: utf-8 -*-
"""Map WTViewer checkbox config → Yokogawa ``:NUMERIC:NORMAL:ITEM`` tokens.

Covers WT3000E / WT1800 / WT1806E / WT5000 embedded measurement ticks.
Instrument-rejected tokens are dropped later by ``WtScpiCollector._setup_numeric_items``.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

# ---------------------------------------------------------------------------
# Not measurement values (wiring / range UI only) — ignored for NUMERIC.
# ---------------------------------------------------------------------------
_SKIP_CHECKBOXES: Set[str] = {
    "checkBox_SetElement1",
    "checkBox_SetElement2",
    "checkBox_SetElement3",
    "checkBox_SetElement4",
    "checkBox_SetElement5",
    "checkBox_SetElement6",
    "checkBox_SetSigma",
    "checkBox_SetSigmaA",
    "checkBox_SetSigmaB",
    "checkBox_SetSigmaC",
    "checkBox_SetUrange",
    "checkBox_SetIrange",
    "checkBox_SetRngU",
    "checkBox_SetRngI",
    "checkBox_SetCfU",
    "checkBox_SetCfI",
}

# ---------------------------------------------------------------------------
# Single token (no ,Element / ,SIGMA suffix)
# ---------------------------------------------------------------------------
_SINGLE_BY_CHECKBOX: Dict[str, str] = {
    "checkBox_SetTime": "TIME",
    "checkBox_SetTSDate": "DATE",
    "checkBox_SetTSTime": "CLOCK",
    "checkBox_SetTSSubsec": "SUBSEC",
    "checkBox_SetSpeed": "SPEED",
    "checkBox_SetTorque": "TORQUE",
    "checkBox_SetSyncSp": "SYNCSP",
    "checkBox_SetSlip": "SLIP",
    "checkBox_SetPm": "PM",
    "checkBox_SetEaU": "EAU",
    "checkBox_SetEaI": "EAI",
    "checkBox_SetK_factor": "KFACTOR",
    "checkBox_SetFreqPLL1": "FUPLL1",
    "checkBox_SetFreqPLL2": "FUPLL2",
    "checkBox_SetEta1": "ETA1",
    "checkBox_SetEta2": "ETA2",
    "checkBox_SetEta3": "ETA3",
    "checkBox_SetEta4": "ETA4",
    "checkBox_SetEvent1": "EVENT1",
    "checkBox_SetEvent2": "EVENT2",
    "checkBox_SetEvent3": "EVENT3",
    "checkBox_SetEvent4": "EVENT4",
    "checkBox_SetEvent5": "EVENT5",
    "checkBox_SetEvent6": "EVENT6",
    "checkBox_SetEvent7": "EVENT7",
    "checkBox_SetEvent8": "EVENT8",
    "checkBox_SetDeltaI": "DELTAI",
    "checkBox_SetDeltaUSigma": "DELTAUSIGMA",
    "checkBox_SetDeltaPSigma": "DELTAPSIGMA",
    **{f"checkBox_SetF{i:02d}": f"F{i}" for i in range(1, 21)},
    **{f"checkBox_SetDeltaF{i}": f"DELTAF{i}" for i in range(1, 5)},
    **{f"checkBox_SetDeltaU{i}": f"DELTAU{i}" for i in range(1, 4)},
    **{f"checkBox_SetDeltaP{i}": f"DELTAP{i}" for i in range(1, 4)},
}

# ---------------------------------------------------------------------------
# Per-element / per-sigma function names
# ---------------------------------------------------------------------------
_FUNCTION_BY_CHECKBOX: Dict[str, str] = {
    # WT3000E shorts
    "checkBox_SetU": "URMS",
    "checkBox_SetI": "IRMS",
    "checkBox_SetP": "P",
    "checkBox_SetS": "S",
    "checkBox_SetQ": "Q",
    "checkBox_SetLambda": "LAMBDA",
    "checkBox_SetPhi": "PHI",
    "checkBox_SetPc": "PC",
    "checkBox_SetFreqU": "FU",
    "checkBox_SetFreqI": "FI",
    "checkBox_SetWP": "WP",
    "checkBox_SetWPPlus": "WPPLUS",
    "checkBox_SetWPMinus": "WPMINUS",
    "checkBox_Setq": "WQ",
    "checkBox_SetqPlus": "WQPLUS",
    "checkBox_SetqMinus": "WQMINUS",
    "checkBox_SetWS": "WS",
    "checkBox_SetWQ": "WQ",
    # RMS family (1800/1806/5000)
    "checkBox_SetUrms": "URMS",
    "checkBox_SetUmn": "UMN",
    "checkBox_SetUdc": "UDC",
    "checkBox_SetUrmn": "URMN",
    "checkBox_SetUac": "UAC",
    "checkBox_SetIrms": "IRMS",
    "checkBox_SetImn": "IMN",
    "checkBox_SetIdc": "IDC",
    "checkBox_SetIrmn": "IRMN",
    "checkBox_SetIac": "IAC",
    "checkBox_SetPF": "LAMBDA",
    "checkBox_SetUppeak": "UPPEAK",
    "checkBox_SetUmpeak": "UMPEAK",
    "checkBox_SetIppeak": "IPPEAK",
    "checkBox_SetImpeak": "IMPEAK",
    "checkBox_SetPppeak": "PPPEAK",
    "checkBox_SetPmpeak": "PMPEAK",
    # Fundamental (WT5000)
    "checkBox_SetUfnd": "UFND",
    "checkBox_SetIfnd": "IFND",
    "checkBox_SetPfnd": "PFND",
    "checkBox_SetSfnd": "SFND",
    "checkBox_SetQfnd": "QFND",
    "checkBox_SetLambdafnd": "LAMBDAFND",
    "checkBox_SetPhifnd": "PHIFND",
    "checkBox_SetFreq2U": "FU2",
    "checkBox_SetFreq2I": "FI2",
    # Distortion / quality
    "checkBox_SetUthd": "UTHD",
    "checkBox_SetIthd": "ITHD",
    "checkBox_SetPthd": "PTHD",
    "checkBox_SetUthf": "UTHF",
    "checkBox_SetIthf": "ITHF",
    "checkBox_SetUtif": "UTIF",
    "checkBox_SetItif": "ITIF",
    "checkBox_Sethvf": "HVF",
    "checkBox_Sethcf": "HCF",
    # Harmonic order list (best-effort tokens; may need HARMonics mode on instrument)
    "checkBox_SetUk": "U(K)",
    "checkBox_SetIk": "I(K)",
    "checkBox_SetPk": "P(K)",
    "checkBox_SetSk": "S(K)",
    "checkBox_SetQk": "Q(K)",
    "checkBox_SetPFk": "LAMBDA(K)",
    "checkBox_SetPhik": "PHI(K)",
    "checkBox_SetPhiUk": "PHIU(K)",
    "checkBox_SetPhiIk": "PHII(K)",
    "checkBox_SetUhdfk": "UHDF(K)",
    "checkBox_SetIhdfk": "IHDF(K)",
    "checkBox_SetPhdfk": "PHDF(K)",
    "checkBox_SetZk": "Z(K)",
    "checkBox_SetRsk": "RS(K)",
    "checkBox_SetRpk": "RP(K)",
    "checkBox_SetXsk": "XS(K)",
    "checkBox_SetXpk": "XP(K)",
    # Phase differences
    "checkBox_SetPhiUi_Uj": "PHIUIUJ",
    "checkBox_SetPhiUi_Uk": "PHIUIUK",
    "checkBox_SetPhiUi_Ii": "PHIUiii",
    "checkBox_SetPhiUi_Ij": "PHIUIJI",
    "checkBox_SetPhiUi_Ik": "PHIUIKI",
}

_FUNCTION_PRIORITY: Tuple[str, ...] = (
    "URMS",
    "IRMS",
    "P",
    "Q",
    "S",
    "LAMBDA",
    "PHI",
    "FU",
    "FI",
    "UDC",
    "IDC",
    "UAC",
    "IAC",
    "UMN",
    "IMN",
    "URMN",
    "IRMN",
    "UPPEAK",
    "UMPEAK",
    "IPPEAK",
    "IMPEAK",
    "PPPEAK",
    "PMPEAK",
    "PC",
    "WP",
    "WPPLUS",
    "WPMINUS",
    "WQ",
    "WQPLUS",
    "WQMINUS",
    "WS",
    "UFND",
    "IFND",
    "PFND",
    "SFND",
    "QFND",
    "LAMBDAFND",
    "PHIFND",
    "FU2",
    "FI2",
    "UTHD",
    "ITHD",
    "PTHD",
    "UTHF",
    "ITHF",
    "UTIF",
    "ITIF",
    "HVF",
    "HCF",
    "U(K)",
    "I(K)",
    "P(K)",
    "S(K)",
    "Q(K)",
    "LAMBDA(K)",
    "PHI(K)",
    "PHIU(K)",
    "PHII(K)",
    "UHDF(K)",
    "IHDF(K)",
    "PHDF(K)",
    "Z(K)",
    "RS(K)",
    "RP(K)",
    "XS(K)",
    "XP(K)",
    "PHIUIUJ",
    "PHIUIUK",
    "PHIUiii",
    "PHIUIJI",
    "PHIUIKI",
)

_PROJECT_NUM_BY_INDEX = (12, 24, 48, 200)
_DEFAULT_ELEMENTS = ("1", "2", "3")
_DEFAULT_SIGMA = ("SIGMA",)
_FALLBACK_ITEMS = (
    "URMS,1",
    "URMS,2",
    "URMS,3",
    "IRMS,1",
    "IRMS,2",
    "IRMS,3",
    "P,1",
    "P,2",
    "P,3",
    "P,SIGMA",
    "Q,SIGMA",
    "LAMBDA,SIGMA",
    "FU,1",
)


def _is_checked(config: Mapping, key: str) -> bool:
    val = config.get(key, "")
    if val is True or val == 1:
        return True
    text = str(val).strip()
    return text in ("1", "true", "True", "YES", "yes", "on", "ON")


def _style_max_elements(config: Mapping) -> int:
    style = str(config.get("Style") or "")
    if "1800" in style or "1806" in style:
        return 6
    return 4


def all_known_checkbox_keys() -> Set[str]:
    return set(_SKIP_CHECKBOXES) | set(_SINGLE_BY_CHECKBOX) | set(_FUNCTION_BY_CHECKBOX)


def _is_wt3000(config: Mapping) -> bool:
    """WT3000/WT3000E。网页字典可能没有 Style，只带型号单选。"""
    style = str(config.get("Style") or "")
    if "3000" in style:
        return True
    if any(tag in style for tag in ("1800", "1806", "5000")):
        return False
    if any(
        _is_checked(config, key)
        for key in ("radio_S2_WT1800", "radio_S2_WT1806E", "radio_S2_WT5000")
    ):
        return False
    return _is_checked(config, "radio_S2_WT3000") or _is_checked(config, "radio_wt3000")


def _append_target(targets: List[str], token: str) -> None:
    if token not in targets:
        targets.append(token)


def _user_picked_element(config: Mapping) -> bool:
    max_el = _style_max_elements(config)
    return any(
        _is_checked(config, f"checkBox_SetElement{i}") for i in range(1, max_el + 1)
    )


def _user_picked_sigma(config: Mapping) -> bool:
    return any(
        _is_checked(config, key)
        for key in (
            "checkBox_SetSigma",
            "checkBox_SetSigmaA",
            "checkBox_SetSigmaB",
            "checkBox_SetSigmaC",
        )
    )


def selected_targets(config: Mapping) -> List[str]:
    max_el = _style_max_elements(config)
    targets: List[str] = []
    for i in range(1, max_el + 1):
        if _is_checked(config, f"checkBox_SetElement{i}"):
            _append_target(targets, str(i))
    # WT3000 通信手册里 ΣA 的元素名是 SIGMA（存盘列 U-SIGMA），ΣB 是 SIGMB。
    # 没有 SIGMAA。勾 SigmaA 却发 SIGMAA 时，ITEM? 回读对不上，
    # WtScpiCollector._setup_numeric_items 会丢掉该列，CSV 里就没有 sigma。
    sigma_a = "SIGMA" if _is_wt3000(config) else "SIGMAA"
    if _is_checked(config, "checkBox_SetSigma"):
        _append_target(targets, "SIGMA")
    if _is_checked(config, "checkBox_SetSigmaA"):
        _append_target(targets, sigma_a)
    if _is_checked(config, "checkBox_SetSigmaB"):
        _append_target(targets, "SIGMAB")
    if _is_checked(config, "checkBox_SetSigmaC"):
        _append_target(targets, "SIGMAC")
    if targets:
        return targets
    return list(_DEFAULT_ELEMENTS) + list(_DEFAULT_SIGMA)


def selected_functions(config: Mapping) -> List[str]:
    found: List[str] = []
    seen = set()
    for key, func in _FUNCTION_BY_CHECKBOX.items():
        if not _is_checked(config, key):
            continue
        if func in seen:
            continue
        seen.add(func)
        found.append(func)
    if not found:
        return []

    def _rank(name: str) -> Tuple[int, str]:
        try:
            return (_FUNCTION_PRIORITY.index(name), name)
        except ValueError:
            return (len(_FUNCTION_PRIORITY), name)

    return sorted(found, key=_rank)


def selected_singles(config: Mapping) -> List[str]:
    out: List[str] = []
    seen = set()
    for key, token in _SINGLE_BY_CHECKBOX.items():
        if not _is_checked(config, key):
            continue
        if token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def max_item_slots(config: Mapping) -> int:
    idx = config.get("comboBox_ProjectNum", 1)
    try:
        i = int(idx)
    except (TypeError, ValueError):
        i = 1
    if 0 <= i < len(_PROJECT_NUM_BY_INDEX):
        return _PROJECT_NUM_BY_INDEX[i]
    return 48


def items_from_wt_config(
    config: Optional[Mapping],
    *,
    fallback: Sequence[str] = _FALLBACK_ITEMS,
) -> List[str]:
    """Build NUMERIC item list from Upper_WT_Config / params_dict."""
    if not isinstance(config, Mapping):
        return list(fallback)

    funcs = selected_functions(config)
    singles = selected_singles(config)
    # 只勾总和、没勾 U/I/P 时，旧逻辑整表换成元素 1/2/3 的默认项。
    # 电压只剩 URMS,1，没有 URMS,SIGMA，CSV 里看不到 U-SIGMA。
    if not funcs and not singles:
        if not (_user_picked_sigma(config) and not _user_picked_element(config)):
            return list(fallback)
        funcs = ["URMS", "IRMS", "P", "Q"]

    targets = selected_targets(config)
    element_targets = [t for t in targets if str(t).isdigit()]
    sigma_targets = [t for t in targets if not str(t).isdigit()]
    ordered_targets = element_targets + sigma_targets

    items: List[str] = []
    seen = set()

    def _add(token: str) -> None:
        if token in seen:
            return
        seen.add(token)
        items.append(token)

    # 按测量项分组、组内先元素再总和，和 WT 宏录制列顺序一致。
    # 旧顺序是每个元素先占满全部测量项，项目数一截，SIGMA/SIGMAA 整组被切掉。
    for func in funcs:
        for target in ordered_targets:
            _add(f"{func},{target}")

    for token in singles:
        _add(token)

    limit = 200
    if len(items) > limit:
        items = _fit_keep_sigma(items, limit)
    return items if items else list(fallback)


def _is_sigma_item(token: str) -> bool:
    if "," not in str(token):
        return False
    target = str(token).split(",", 1)[1].strip().upper()
    return target.startswith("SIGMA")


def _fit_keep_sigma(items: List[str], limit: int) -> List[str]:
    """超过 200 列时先留总和，再按原顺序留元素。项目数下拉不再把已勾的 SIGMA 整组切掉。"""
    if limit <= 0:
        return []
    sigma = [item for item in items if _is_sigma_item(item)]
    plain = [item for item in items if not _is_sigma_item(item)]
    chosen = set(sigma[:limit])
    for item in plain:
        if len(chosen) >= limit:
            break
        chosen.add(item)
    return [item for item in items if item in chosen]


# CSV 表头用宏录制的「名称-对象」。
# WT3000 勾 SigmaA 发给仪器的是 URMS,SIGMA，表头 U-SIGMA（与 wt_file_save_path 实录一致）。
# 1800/1806/5000 的 SigmaA 才是 URMS,SIGMAA。3000 短名 U-1；1800/1806/5000 用 Urms-1。
_MACRO_STEM_SHORT: Dict[str, str] = {
    "URMS": "U",
    "IRMS": "I",
    "P": "P",
    "S": "S",
    "Q": "Q",
    "LAMBDA": "PF",
    "PHI": "Phi",
    "FU": "FreqU",
    "FI": "FreqI",
    "PC": "Pc",
    "WP": "WP",
    "WPPLUS": "WP+",
    "WPMINUS": "WP-",
    "WQ": "q",
    "WQPLUS": "q+",
    "WQMINUS": "q-",
    "WS": "WS",
    "U(K)": "U(k)",
    "I(K)": "I(k)",
    "P(K)": "P(k)",
    "TIME": "Time",
    "ETA1": "η1",
    "ETA2": "η2",
    "ETA3": "η3",
    "ETA4": "η4",
}
_MACRO_STEM_LONG: Dict[str, str] = {
    **_MACRO_STEM_SHORT,
    "URMS": "Urms",
    "IRMS": "Irms",
    "UMN": "Umn",
    "UDC": "Udc",
    "URMN": "Urmn",
    "UAC": "Uac",
    "IMN": "Imn",
    "IDC": "Idc",
    "IRMN": "Irmn",
    "IAC": "Iac",
    "UPPEAK": "Uppeak",
    "UMPEAK": "Umpeak",
    "IPPEAK": "Ippeak",
    "IMPEAK": "Impeak",
    "UTHD": "Uthd",
    "ITHD": "Ithd",
    "UFND": "Ufnd",
    "IFND": "Ifnd",
    "PFND": "Pfnd",
}


def _macro_stem(func: str, *, short: bool) -> str:
    table = _MACRO_STEM_SHORT if short else _MACRO_STEM_LONG
    if func in table:
        return table[func]
    if func.startswith("F") and func[1:].isdigit():
        return f"F{int(func[1:]):02d}"
    return func


def macro_column_name(token: str, style: str = "") -> str:
    """SCPI 令牌 → WTViewer 宏 CSV 列名。例如 URMS,SIGMA + WT3000 → U-SIGMA。"""
    raw = str(token or "").strip()
    if not raw:
        return raw
    short = "3000" in str(style or "")
    if "," in raw:
        func, target = raw.split(",", 1)
        return f"{_macro_stem(func.strip(), short=short)}-{target.strip()}"
    return _macro_stem(raw, short=short)


def describe_mapping(config: Mapping) -> Dict[str, Any]:
    return {
        "functions": selected_functions(config),
        "singles": selected_singles(config),
        "targets": selected_targets(config),
        "items": items_from_wt_config(config),
        "max_slots": max_item_slots(config),
        "harmonic_start": str(config.get("textEdit_SetStart") or "").strip(),
        "harmonic_stop": str(config.get("textEdit_SetStop") or "").strip(),
    }
