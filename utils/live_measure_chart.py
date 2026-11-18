# -*- coding: utf-8 -*-
"""实时测量曲线分组：按量纲分栏，避免 U/I/P/λ/F 挤在同一纵轴。"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

# Soft Panel / Oxygen 习惯：同类量一栏，各自量程
_GROUP_ORDER = (
    ("电压 U", ("U", "URMS", "UPPEAK", "UMPEAK", "CFU", "UK", "UTHD", "UTHF", "UTIF", "UFND", "HVF")),
    ("电流 I", ("I", "IRMS", "IPPEAK", "IMPEAK", "CFI", "IK", "ITHD", "ITHF", "ITIF", "IFND", "HCF")),
    ("功率 P/S/Q", ("P", "S", "Q", "PC", "PK", "SK", "QK", "WP", "WS", "WQ", "PFND", "PTHD")),
    ("功率因数 / 相位", ("LAMBDA", "PHI", "PF", "PFK", "LAMBDAFND")),
    ("频率", ("FU", "FI", "FREQ", "F")),
    ("其它", ()),
)

_COLORS = (
    "#2563eb",
    "#dc2626",
    "#059669",
    "#d97706",
    "#7c3aed",
    "#0891b2",
    "#be123c",
    "#4d7c0f",
)


def series_color(index: int) -> str:
    return _COLORS[index % len(_COLORS)]


def item_root(name: str) -> str:
    """取通道根名：U,1,TOTAL → U；AI 1/U1 → U1；P_t@POWER/0 → P_T。"""
    text = str(name or "").strip()
    if not text:
        return ""
    # 德威创/CEI：量名在 @ 前；AI 通道：取最后一节
    if "@" in text:
        text = text.split("@", 1)[0].strip()
    elif "/" in text:
        text = text.rsplit("/", 1)[-1]
    head = text.split(",", 1)[0].strip()
    return head.upper()


def short_label(name: str) -> str:
    """图例短名：U,1,TOTAL → U1；U,SIGMA,TOTAL → UΣ；P_t@POWER/0 → P_t。"""
    text = str(name or "").strip()
    if "@" in text:
        return text.split("@", 1)[0].strip()
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        return text
    root = parts[0]
    if len(parts) == 1:
        if "/" in root:
            return root.rsplit("/", 1)[-1]
        return root
    target = "Σ" if parts[1].upper().startswith("SIGM") else parts[1]
    order = ""
    if len(parts) > 2 and parts[2].upper() not in ("TOTAL", "DC"):
        order = f"/{parts[2]}"
    return f"{root}{target}{order}"


def _match_group(root: str) -> str:
    upper = root.upper().replace(" ", "")
    # PF / cosφ 先于纯 P，避免 PF 进功率栏
    if upper.startswith("PF") or "LAMBDA" in upper or upper.startswith("PHI") or "COS" in upper:
        return "功率因数 / 相位"
    for title, prefixes in _GROUP_ORDER:
        if not prefixes:
            continue
        for prefix in prefixes:
            if upper == prefix or upper.startswith(prefix):
                return title
    # 德威创常见：U1/I1/P_t/Q_fund/F…
    if upper[:1] == "U" or "VOLT" in upper:
        return "电压 U"
    if upper[:1] == "I" or "CURR" in upper:
        return "电流 I"
    if upper[:1] in ("P", "S", "Q") or "POWER" in upper or "WATT" in upper:
        return "功率 P/S/Q"
    if upper[:1] == "F" or "FREQ" in upper or "HZ" in upper:
        return "频率"
    return "其它"


def group_series(names: Sequence[str]) -> List[Tuple[str, List[str]]]:
    """按量纲分组，保持勾选出现顺序。空组丢掉。"""
    buckets: Dict[str, List[str]] = {title: [] for title, _ in _GROUP_ORDER}
    for name in names:
        buckets[_match_group(item_root(name))].append(name)
    out: List[Tuple[str, List[str]]] = []
    for title, _ in _GROUP_ORDER:
        rows = buckets.get(title) or []
        if rows:
            out.append((title, rows))
    return out


def y_range(values: Sequence[float], *, pad_ratio: float = 0.08) -> Tuple[float, float]:
    finite = [value for value in values if value == value]
    if not finite:
        return 0.0, 1.0
    low = min(finite)
    high = max(finite)
    if high == low:
        span = abs(low) * 0.05 if low else 1.0
        return low - span, high + span
    pad = (high - low) * pad_ratio
    return low - pad, high + pad
