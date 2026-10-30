# -*- coding: utf-8 -*-
"""网页测量项用 WT3000 的控件名。WT1800 / WT5000 上电压电流换了名字，下发时两边都写。"""
from __future__ import annotations

from typing import Any, Dict, Tuple

# 同一测量项在不同型号上的 objectName。位置不同不影响，按名字写。
_PAIRS: Tuple[Tuple[str, str], ...] = (
    ("checkBox_SetU", "checkBox_SetUrms"),
    ("checkBox_SetI", "checkBox_SetIrms"),
    ("checkBox_SetUrange", "checkBox_SetRngU"),
    ("checkBox_SetIrange", "checkBox_SetRngI"),
    ("checkBox_SetLambda", "checkBox_SetPF"),
)


def expand_wt_measure_checks(values: Dict[str, Any]) -> Dict[str, Any]:
    """把已给出的勾选复制到另一型号的同名项。两边都有且不一致时保持原值。"""
    if not isinstance(values, dict):
        return {}
    out = dict(values)
    for left, right in _PAIRS:
        has_left = left in out
        has_right = right in out
        if has_left and not has_right:
            out[right] = out[left]
        elif has_right and not has_left:
            out[left] = out[right]
    return out
