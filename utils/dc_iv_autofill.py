# -*- coding: utf-8 -*-
"""IV helpers kept for optional tools/tests. UI defaults to manual entry (no autofill)."""
from __future__ import annotations

import math
from typing import Any, Dict, Tuple

DEFAULT_FF = 0.80


def parse_percent(v) -> float:
    """解析功率百分比：80 / 80% / 0.8 → 80。"""
    if v is None:
        raise ValueError("percent is None")
    vs = str(v).strip()
    if vs.endswith("%"):
        vs = vs[:-1].strip()
    p = float(vs)
    if 0 < p <= 1:
        p *= 100.0
    return p


def clamp_ff(ff: float) -> float:
    f = float(ff) if ff else DEFAULT_FF
    return max(0.25, min(0.95, f))


def calc_iv_from_voc_ff_power(
    voc: float,
    ff: float,
    power_w: float,
    percent: float = 100.0,
) -> Dict[str, float]:
    """由 Voc / FF / 额定功率W / 功率% 计算 Vmp、Voc、Imp、Isc（工具用，不接 UI）。"""
    voc_f = float(voc)
    if voc_f <= 0:
        raise ValueError("Voc must be > 0")
    pw = float(power_w)
    if pw <= 0:
        raise ValueError("power_w must be > 0")
    pct = parse_percent(percent)
    if pct <= 0:
        raise ValueError("percent must be > 0")
    ff_f = clamp_ff(ff)
    pmp = pw * (pct / 100.0)
    isc = pmp / (voc_f * ff_f)
    vmp = voc_f * math.sqrt(ff_f)
    if vmp <= 0:
        raise ValueError("Vmp computed <= 0")
    imp = pmp / vmp
    return {
        "vmp": round(vmp, 3),
        "voc": round(voc_f, 3),
        "imp": round(imp, 3),
        "isc": round(isc, 3),
        "pmp": round(pmp, 3),
        "ff": round(ff_f, 4),
        "percent": round(pct, 3),
    }


def derive_voc_isc(
    vmp: float, imp: float, *, ff: float = DEFAULT_FF
) -> Tuple[float, float]:
    f = clamp_ff(ff)
    return round(float(vmp) / f, 3), round(float(imp) / f, 3)


def derive_imp_from_power_w(power_w: float, vmp: float) -> float:
    if float(vmp) <= 0:
        raise ValueError("vmp must be > 0")
    return round(float(power_w) / float(vmp), 3)


def wire_dc_iv_autofill(*_args: Any, **_kwargs: Any) -> None:
    """No-op: UI 默认手动填写 IV，不再自动推算。"""
    return
