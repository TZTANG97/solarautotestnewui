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


def selected_targets(config: Mapping) -> List[str]:
    max_el = _style_max_elements(config)
    targets: List[str] = []
    for i in range(1, max_el + 1):
        if _is_checked(config, f"checkBox_SetElement{i}"):
            targets.append(str(i))
    if _is_checked(config, "checkBox_SetSigma"):
        targets.append("SIGMA")
    if _is_checked(config, "checkBox_SetSigmaA"):
        targets.append("SIGMAA")
    if _is_checked(config, "checkBox_SetSigmaB"):
        targets.append("SIGMAB")
    if _is_checked(config, "checkBox_SetSigmaC"):
        targets.append("SIGMAC")
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
    if not funcs and not singles:
        return list(fallback)

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

    # Element/sigma quantities first so ProjectNum caps do not drop U/I/P
    # when many F*/motor singles are also ticked.
    for target in ordered_targets:
        for func in funcs:
            _add(f"{func},{target}")

    for token in singles:
        _add(token)

    limit = max_item_slots(config)
    if len(items) > limit:
        items = items[:limit]
    return items if items else list(fallback)


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
