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
    # 手册里积分功率的命令名是 WH/WHP/WHM，菜单上才写成 WP/WP+/WP-。
    "checkBox_SetWP": "WH",
    "checkBox_SetWPPlus": "WHP",
    "checkBox_SetWPMinus": "WHM",
    "checkBox_Setq": "AH",
    "checkBox_SetqPlus": "AHP",
    "checkBox_SetqMinus": "AHM",
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
    # 波峰因数是测量值。量程才不是。
    "checkBox_SetCfU": "CFU",
    "checkBox_SetCfI": "CFI",
    # Fundamental (WT5000)
    "checkBox_SetUfnd": "UFND",
    "checkBox_SetIfnd": "IFND",
    "checkBox_SetPfnd": "PFND",
    "checkBox_SetSfnd": "SFND",
    "checkBox_SetQfnd": "QFND",
    "checkBox_SetLambdafnd": "LAMBDAFND",
    "checkBox_SetPhifnd": "PHIFND",
    "checkBox_SetFreq2U": "F2U",
    "checkBox_SetFreq2I": "F2I",
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
}

# 谐波阶次必须写成 UK,元素,阶次。括号形式 U(K) 仪器不回读。
# WT3000 的数值项没有单独的 UK，阶次写在 U/I/P 的第三个字段上（手册 6-44）。
_HARMONIC_BY_CHECKBOX: Dict[str, Tuple[str, str]] = {
    "checkBox_SetUk": ("U", "UK"),
    "checkBox_SetIk": ("I", "IK"),
    "checkBox_SetPk": ("P", "PK"),
    "checkBox_SetSk": ("S", "SK"),
    "checkBox_SetQk": ("Q", "QK"),
    "checkBox_SetPFk": ("LAMBDA", "LAMBDAK"),
    "checkBox_SetPhik": ("PHI", "PHIK"),
    "checkBox_SetPhiUk": ("PHIU", "PHIUK"),
    "checkBox_SetPhiIk": ("PHII", "PHIIK"),
    "checkBox_SetUhdfk": ("UHDF", "UHDFK"),
    "checkBox_SetIhdfk": ("IHDF", "IHDFK"),
    "checkBox_SetPhdfk": ("PHDF", "PHDFK"),
    "checkBox_SetZk": ("Z", "ZK"),
    "checkBox_SetRsk": ("RS", "RSK"),
    "checkBox_SetRpk": ("RP", "RPK"),
    "checkBox_SetXsk": ("XS", "XSK"),
    "checkBox_SetXpk": ("XP", "XPK"),
}

# 相位差是完整功能名，不能再拼成 PHIUiii,1。
# 值是 (WT3000 功能名, 其他机型功能名, 5000 是否只能跟 Σ)。
_PHASE_BY_CHECKBOX: Dict[str, Tuple[str, str, bool]] = {
    "checkBox_SetPhiUi_Uj": ("PHI_U1U2", "PHI_U1U2", True),
    "checkBox_SetPhiUi_Uk": ("PHI_U1U3", "PHI_U1U3", True),
    "checkBox_SetPhiUi_Ii": ("PHI_U1I1", "PHI_U1I1", False),
    "checkBox_SetPhiUi_Ij": ("PHI_U1I2", "PHI_U2I2", True),
    "checkBox_SetPhiUi_Ik": ("PHI_U1I3", "PHI_U3I3", True),
}

# WT5000 的 Δ 计算命令名。元素只能是 Σ。
_WT5000_DELTA_SINGLE = {
    "DELTAU1": "DU1",
    "DELTAU2": "DU2",
    "DELTAU3": "DU3",
    "DELTAUSIGMA": "DUS",
    "DELTAI": "DI",
    "DELTAP1": "DP1",
    "DELTAP2": "DP2",
    "DELTAP3": "DP3",
    "DELTAPSIGMA": "DPS",
}

_WT5000_SINGLE_ALIAS = {
    "DATE": "TSDATE",
    "CLOCK": "TSTIME",
    "SUBSEC": "TSSUBSEC",
    **{f"EVENT{i}": f"EV{i}" for i in range(1, 9)},
}

# WT3000 这些功能的阶次是必填，省略时仪器按 TOTAL 回读。
_WT3000_NEEDS_ORDER = {"U", "I", "P", "S", "Q", "LAMBDA", "PHI"}
_WT3000_FUNCTION_ALIAS = {
    "checkBox_SetU": "U",
    "checkBox_SetI": "I",
    "checkBox_SetUrms": "U",
    "checkBox_SetIrms": "I",
    "checkBox_SetUmn": "U",
    "checkBox_SetUdc": "U",
    "checkBox_SetUrmn": "U",
    "checkBox_SetUac": "U",
    "checkBox_SetImn": "I",
    "checkBox_SetIdc": "I",
    "checkBox_SetIrmn": "I",
    "checkBox_SetIac": "I",
}

_FUNCTION_PRIORITY: Tuple[str, ...] = (
    "U",
    "I",
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
    "WH",
    "WHP",
    "WHM",
    "AH",
    "AHP",
    "AHM",
    "WP",
    "WQ",
    "WS",
    "UFND",
    "IFND",
    "PFND",
    "SFND",
    "QFND",
    "LAMBDAFND",
    "PHIFND",
    "F2U",
    "F2I",
    "UTHD",
    "ITHD",
    "PTHD",
    "UTHF",
    "ITHF",
    "UTIF",
    "ITIF",
    "HVF",
    "HCF",
    "UK",
    "IK",
    "PK",
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
    return (
        set(_SKIP_CHECKBOXES)
        | set(_SINGLE_BY_CHECKBOX)
        | set(_FUNCTION_BY_CHECKBOX)
        | set(_HARMONIC_BY_CHECKBOX)
        | set(_PHASE_BY_CHECKBOX)
    )


def model_of(config: Optional[Mapping]) -> str:
    """3000 / 1800 / 1806 / 5000。认不出时按 1800 这一代（URMS、SIGMAA）。"""
    if not isinstance(config, Mapping):
        return ""
    style = str(config.get("Style") or "")
    for tag in ("5000", "1806", "1800", "3000"):
        if tag in style:
            return tag
    if _is_checked(config, "radio_S2_WT5000"):
        return "5000"
    if _is_checked(config, "radio_S2_WT1806E"):
        return "1806"
    if _is_checked(config, "radio_S2_WT1800"):
        return "1800"
    if _is_checked(config, "radio_S2_WT3000") or _is_checked(config, "radio_wt3000"):
        return "3000"
    return ""


def _is_wt3000(config: Mapping) -> bool:
    return model_of(config) == "3000"


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
    # WT3000 / WT5000 手册里 ΣA 的元素名是 SIGMA。1800/1806 仍用 SIGMAA。
    # WT5000 的 ΣC 是 SIGMC，不是 SIGMAC。
    model = model_of(config)
    sigma_a = "SIGMA" if model in ("3000", "5000") else "SIGMAA"
    sigma_c = "SIGMC" if model == "5000" else "SIGMAC"
    if _is_checked(config, "checkBox_SetSigma"):
        _append_target(targets, "SIGMA")
    if _is_checked(config, "checkBox_SetSigmaA"):
        _append_target(targets, sigma_a)
    if _is_checked(config, "checkBox_SetSigmaB"):
        _append_target(targets, "SIGMAB")
    if _is_checked(config, "checkBox_SetSigmaC"):
        _append_target(targets, sigma_c)
    if targets:
        return targets
    return list(_DEFAULT_ELEMENTS) + list(_DEFAULT_SIGMA)


def selected_functions(config: Mapping) -> List[str]:
    model = model_of(config)
    found: List[str] = []
    seen = set()
    for key, func in _FUNCTION_BY_CHECKBOX.items():
        if not _is_checked(config, key):
            continue
        if model == "3000":
            func = _WT3000_FUNCTION_ALIAS.get(key, func)
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


def _any_extra_checked(config: Mapping) -> bool:
    keys = list(_HARMONIC_BY_CHECKBOX) + list(_PHASE_BY_CHECKBOX)
    return any(_is_checked(config, key) for key in keys)


def harmonic_orders(config: Mapping) -> List[str]:
    """谐波阶次。空白时发 1，和手册示例 UK,1,1 一致。跨度超过 50 阶就截断。"""

    def _one(raw, default: int) -> int:
        text = str(raw if raw is not None else "").strip()
        if not text:
            return default
        try:
            return int(float(text))
        except ValueError:
            return default

    start = _one(config.get("textEdit_SetStart"), 1)
    stop = _one(config.get("textEdit_SetStop"), start)
    if start <= 0 and stop <= 0:
        return ["DC"]
    start = max(1, min(start, 500))
    stop = max(start, min(stop, 500))
    if stop - start > 50:
        stop = start + 50
    return [str(number) for number in range(start, stop + 1)]


def _fallback_for(config: Mapping, fallback: Sequence[str]) -> List[str]:
    if model_of(config) != "3000":
        return list(fallback)
    return [
        "U,1,TOTAL",
        "U,2,TOTAL",
        "U,3,TOTAL",
        "I,1,TOTAL",
        "I,2,TOTAL",
        "I,3,TOTAL",
        "P,1,TOTAL",
        "P,2,TOTAL",
        "P,3,TOTAL",
        "P,SIGMA,TOTAL",
        "Q,SIGMA,TOTAL",
        "LAMBDA,SIGMA,TOTAL",
        "FU,1",
    ]


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
    model = model_of(config)
    # 只勾总和、没勾 U/I/P 时，旧逻辑整表换成元素 1/2/3 的默认项。
    # 电压只剩元素 1，没有 SIGMA，CSV 里看不到 U-SIGMA。
    if not funcs and not singles and not _any_extra_checked(config):
        if not (_user_picked_sigma(config) and not _user_picked_element(config)):
            return _fallback_for(config, fallback)
        funcs = ["U", "I", "P", "Q"] if model == "3000" else ["URMS", "IRMS", "P", "Q"]

    targets = selected_targets(config)
    element_targets = [t for t in targets if str(t).isdigit()]
    sigma_targets = [t for t in targets if not str(t).isdigit()]
    ordered_targets = element_targets + sigma_targets
    if not element_targets:
        element_targets = list(_DEFAULT_ELEMENTS[:1])

    items: List[str] = []
    seen = set()

    def _add(token: str) -> None:
        if token in seen:
            return
        seen.add(token)
        items.append(token)

    # 按测量项分组、组内先元素再总和，和 WT 宏录制列顺序一致。
    for func in funcs:
        for target in ordered_targets:
            token = f"{func},{target}"
            if model == "3000" and func in _WT3000_NEEDS_ORDER:
                token = f"{token},TOTAL"
            _add(token)

    orders = harmonic_orders(config)
    for key, (on_3000, on_other) in _HARMONIC_BY_CHECKBOX.items():
        if not _is_checked(config, key):
            continue
        func = on_3000 if model == "3000" else on_other
        for target in element_targets:
            for order in orders:
                _add(f"{func},{target},{order}")

    for key, (on_3000, on_other, sigma_only_on_5000) in _PHASE_BY_CHECKBOX.items():
        if not _is_checked(config, key):
            continue
        func = on_3000 if model == "3000" else on_other
        if model == "5000" and sigma_only_on_5000:
            phase_targets = sigma_targets or ["SIGMA"]
        elif model == "3000":
            phase_targets = ordered_targets
        else:
            # 1800/1806 相位差按已选元素发完整功能名，不带仪器不认的 PHIUiii。
            phase_targets = element_targets
            if model != "5000" and key == "checkBox_SetPhiUi_Ij":
                func = "PHI_U1I2"
            if model != "5000" and key == "checkBox_SetPhiUi_Ik":
                func = "PHI_U1I3"
        for target in phase_targets:
            _add(f"{func},{target}")

    for token in singles:
        if model in ("1800", "1806") and token == "SYNCSP":
            # 手册电机项是 SYNC，不是界面上的 SyncSp。
            _add("SYNC")
            continue
        if model in ("5000", "1800", "1806") and token in _WT5000_DELTA_SINGLE:
            name = _WT5000_DELTA_SINGLE[token]
            for target in sigma_targets or ["SIGMA"]:
                _add(f"{name},{target}")
            continue
        if model == "5000" and token in _WT5000_SINGLE_ALIAS:
            _add(_WT5000_SINGLE_ALIAS[token])
            continue
        if model == "3000" and token.startswith("DELTAF") and token[6:].isdigit():
            _add("DELTA" + token[6:])
            continue
        _add(token)

    limit = 200
    if len(items) > limit:
        items = _fit_keep_sigma(items, limit)
    return items if items else list(fallback)


def _is_sigma_item(token: str) -> bool:
    if "," not in str(token):
        return False
    target = str(token).split(",", 1)[1].strip().upper().split(",", 1)[0]
    return target.startswith("SIGM")


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
# WT3000 发给仪器的是 U,SIGMA,TOTAL，表头仍是 U-SIGMA。
# 1800/1806 的 SigmaA 是 URMS,SIGMAA。5000 的 ΣA 是 SIGMA。
_MACRO_STEM_SHORT: Dict[str, str] = {
    "U": "U",
    "I": "I",
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
    "WH": "WP",
    "WHP": "WP+",
    "WHM": "WP-",
    "WPPLUS": "WP+",
    "WPMINUS": "WP-",
    "WQ": "q",
    "AH": "q",
    "AHP": "q+",
    "AHM": "q-",
    "WQPLUS": "q+",
    "WQMINUS": "q-",
    "WS": "WS",
    "UK": "U(k)",
    "IK": "I(k)",
    "PK": "P(k)",
    "U(K)": "U(k)",
    "I(K)": "I(k)",
    "P(K)": "P(k)",
    "PHI_U1U2": "PhiUi-Uj",
    "PHI_U1U3": "PhiUi-Uk",
    "PHI_U1I1": "PhiUi-Ii",
    "PHI_U1I2": "PhiUi-Ij",
    "PHI_U1I3": "PhiUi-Ik",
    "PHI_U2I2": "PhiUj-Ij",
    "PHI_U3I3": "PhiUj-Ik",
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
    """SCPI 令牌 → WTViewer 宏 CSV 列名。例如 U,SIGMA,TOTAL + WT3000 → U-SIGMA。"""
    raw = str(token or "").strip()
    if not raw:
        return raw
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    short = "3000" in str(style or "") or parts[0].upper() in ("U", "I")
    if len(parts) == 1:
        return _macro_stem(parts[0], short=short)
    name = f"{_macro_stem(parts[0], short=short)}-{parts[1]}"
    if len(parts) >= 3 and parts[2].upper() != "TOTAL":
        name = f"{name}-{parts[2]}"
    return name


def _known_function_names() -> Set[str]:
    names = set(_FUNCTION_BY_CHECKBOX.values())
    names |= set(_SINGLE_BY_CHECKBOX.values())
    names |= set(_WT3000_FUNCTION_ALIAS.values())
    names |= {part for pair in _HARMONIC_BY_CHECKBOX.values() for part in pair}
    names |= {part for triple in _PHASE_BY_CHECKBOX.values() for part in triple[:2]}
    names |= set(_WT5000_DELTA_SINGLE.values())
    names |= set(_WT5000_SINGLE_ALIAS.values())
    names.add("SYNC")
    return {str(name).upper() for name in names}


_KNOWN_FUNCTION_NAMES = _known_function_names()


def _function_echo_ok(sent: str, echoed: str) -> bool:
    """长名下发、短名回读也算接受。LAMBda→LAMB，UPPeak→UPP，SPEed→SPE，TORQue→TORQ。

    短名至少 3 个字符，并且不能是另一条完整功能名，避免 U 认成 URMS、PHI 认成 PHI_U1U2。
    """
    sent_u = str(sent or "").upper()
    echo_u = str(echoed or "").upper()
    if not sent_u or not echo_u:
        return False
    if sent_u == echo_u:
        return True
    if len(echo_u) < 3 or not sent_u.startswith(echo_u):
        return False
    if echo_u in _KNOWN_FUNCTION_NAMES and echo_u != sent_u:
        return False
    return True


def _element_echo_ok(sent: str, echoed: str) -> bool:
    sent_u = str(sent or "").upper()
    echo_u = str(echoed or "").upper()
    if sent_u == echo_u:
        return True
    if sent_u.isdigit() and echo_u in (f"ELEMENT{sent_u}", f"EL{sent_u}"):
        return True
    return False


def item_echo_matches(token: str, reply: str) -> bool:
    """ITEM? 回读必须对上功能名。仪器常在后面补 ,TOTAL，或把长名收成短名。

    不能用子串：U,1 会误中 FU,1。
    """
    payload = str(reply or "").upper().replace(" ", "")
    marker = "ITEM"
    idx = payload.rfind(marker)
    if idx >= 0:
        rest = payload[idx + len(marker) :]
        cursor = 0
        while cursor < len(rest) and rest[cursor].isdigit():
            cursor += 1
        payload = rest[cursor:]
    wanted = str(token or "").upper().replace(" ", "")
    if not wanted or not payload:
        return False
    if payload == wanted or payload.startswith(wanted + ","):
        return True
    wanted_parts = [part for part in wanted.split(",") if part]
    echo_parts = [part for part in payload.split(",") if part]
    if not wanted_parts or not echo_parts:
        return False
    if not _function_echo_ok(wanted_parts[0], echo_parts[0]):
        return False
    if echo_parts[-1] == "TOTAL" and (len(wanted_parts) < 2 or wanted_parts[-1] != "TOTAL"):
        echo_parts = echo_parts[:-1]
    if len(echo_parts) != len(wanted_parts):
        return False
    return all(_element_echo_ok(sent, echoed) for sent, echoed in zip(wanted_parts[1:], echo_parts[1:]))


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
