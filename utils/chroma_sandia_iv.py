# -*- coding: utf-8 -*-
"""Chroma Soft Panel Sandia → Vmp/Imp/Voc/Isc。

对齐 Soft Panel Sandia 页（Irr/TC/Pmax/FF/Beta）+ Initial Setup 的 Vmp，
自算四点后回填桌面/IOT，开测仍走现有 IVC 下发。

金标（Soft Panel 截图）：
  Vmp=650, Pmax=7000, FF=0.85, Beta=-0.38, Irr=IrrRef=1000, TC=TCRef=50
  → Imp≈10.768, Voc≈726.9, Isc≈11.120, Pmp≈6999.2
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional

# Soft Panel 形状：Voc=Vmp/FF^a、Isc=Imp/FF^b（由 Soft Panel 截图金标反演）
_VOC_FF_EXP = 0.68802
_ISC_FF_EXP = 0.198
# 辐照对 Voc 的弱对数修正（Irr=IrrRef 时为 0）
_VOC_IRR_LN_COEF = 0.06
# 电流温度系数 %/°C（Soft Panel Sandia 页未单独给出时的默认）
_DEFAULT_ALPHA_PCT_PER_C = 0.04


def clamp_ff(ff: float) -> float:
    f = float(ff)
    return max(0.25, min(0.95, f))


def parse_power_percent(raw: Any, default: float = 100.0) -> float:
    """功率档：80 / 80% / 0.8 → 80。空则 default。"""
    if raw is None or str(raw).strip() == "":
        return float(default)
    vs = str(raw).strip()
    if vs.endswith("%"):
        vs = vs[:-1].strip()
    p = float(vs)
    if 0 < p <= 1:
        p *= 100.0
    if p <= 0:
        raise ValueError("power level percent must be > 0")
    return p


def calc_sandia_iv(
    *,
    vmp: float,
    pmax_w: float,
    ff: float,
    beta_pct_per_c: float = -0.38,
    irr_wm2: float = 1000.0,
    irr_ref_wm2: float = 1000.0,
    tc_c: float = 25.0,
    tc_ref_c: float = 25.0,
    alpha_pct_per_c: float = _DEFAULT_ALPHA_PCT_PER_C,
    power_pct: float = 100.0,
) -> Dict[str, float]:
    """由 Soft Panel Sandia 输入计算 Vmp/Imp/Voc/Isc/Pmp。

    power_pct 是 Power Level（功率%）。先把 Pmax 乘上这个百分比再算 Imp，
    Isc 跟着变，Voc/Vmp 不变。与工控机 DCGetIVValueFunction 只缩放电流一致。
    """
    vmp_f = float(vmp)
    pmax_f = float(pmax_w)
    if vmp_f <= 0:
        raise ValueError("Vmp must be > 0")
    if pmax_f <= 0:
        raise ValueError("Pmax must be > 0")
    pct = parse_power_percent(power_pct, 100.0)
    pmax_f = pmax_f * (pct / 100.0)
    irr = float(irr_wm2)
    irr_ref = float(irr_ref_wm2)
    if irr <= 0 or irr_ref <= 0:
        raise ValueError("Irr / IrrRef must be > 0")

    ff_f = clamp_ff(ff)
    # Soft Panel：Imp 三位小数半向下（金标 7000/650 → 10.768，Pmp=6999.2）
    imp = math.floor(pmax_f / vmp_f * 1000.0 - 0.5 + 1e-12) / 1000.0
    if imp <= 0:
        raise ValueError("computed Imp must be > 0")

    pmp = vmp_f * imp
    voc_shape = vmp_f / (ff_f**_VOC_FF_EXP)
    isc_shape = imp / (ff_f**_ISC_FF_EXP)

    g_ratio = irr / irr_ref
    isc = isc_shape * g_ratio
    voc = voc_shape
    if abs(g_ratio - 1.0) > 1e-12:
        voc = voc_shape * (1.0 + _VOC_IRR_LN_COEF * math.log(g_ratio))

    d_t = float(tc_c) - float(tc_ref_c)
    voc *= 1.0 + float(beta_pct_per_c) / 100.0 * d_t
    isc *= 1.0 + float(alpha_pct_per_c) / 100.0 * d_t

    # 辐照变化时功率随 Irr 近似同比（Vmp 保持用户输入）
    if abs(g_ratio - 1.0) > 1e-12:
        imp = imp * g_ratio
        pmp = vmp_f * imp

    if voc <= vmp_f:
        raise ValueError("computed Voc must be > Vmp（请检查 FF/温度）")
    if isc <= imp:
        raise ValueError("computed Isc must be > Imp（请检查 FF/辐照）")

    return {
        "vmp": round(vmp_f, 3),
        "imp": round(imp, 3),
        "voc": round(voc, 3),
        "isc": round(isc, 3),
        "pmp": round(pmp, 3),
        "ff": round(ff_f, 4),
        "beta_pct_per_c": float(beta_pct_per_c),
        "irr_wm2": round(irr, 3),
        "irr_ref_wm2": round(irr_ref, 3),
        "tc_c": float(tc_c),
        "tc_ref_c": float(tc_ref_c),
        "power_pct": round(pct, 3),
    }


def sandia_inputs_from_mapping(data: Optional[Dict[str, Any]]) -> Dict[str, float]:
    """从 prefs / widgets 字典取 Sandia 输入（缺省对齐 Soft Panel）。"""
    d = data or {}

    def _f(*keys: str, default: float) -> float:
        for k in keys:
            if k not in d or d[k] is None or str(d[k]).strip() == "":
                continue
            try:
                return float(str(d[k]).strip().replace(",", ""))
            except (TypeError, ValueError):
                continue
        return float(default)

    return {
        "vmp": _f("vmp", "sandia_vmp", "textEdit_Vmp", default=650.0),
        "pmax_w": _f("pmax_w", "sandia_pmax", "pmax", default=7000.0),
        "ff": _f("ff", "sandia_ff", default=0.85),
        "beta_pct_per_c": _f("beta_pct_per_c", "sandia_beta", "beta", default=-0.38),
        "irr_wm2": _f("irr_wm2", "sandia_irr", "irr", default=1000.0),
        "irr_ref_wm2": _f("irr_ref_wm2", "sandia_irr_ref", default=1000.0),
        # Soft Panel 截图常用 TC=Pref TC=50；缺省与 Irr 同为台架常用点
        "tc_c": _f("tc_c", "sandia_tc", "tc", default=50.0),
        "tc_ref_c": _f("tc_ref_c", "sandia_tc_ref", default=50.0),
        "power_pct": parse_power_percent(
            next(
                (
                    d[k]
                    for k in ("power_pct", "sandia_power_pct", "textEdit_PF")
                    if k in d and d[k] is not None and str(d[k]).strip() != ""
                ),
                None,
            ),
            100.0,
        ),
    }
