# -*- coding: utf-8 -*-
"""是德 SAS:TABL 点数须远小于 1024，避免一次 viWrite 闪退。"""
from __future__ import annotations

import math


def _build_keysight_tabl_cmds(vmp, imp, voc, isc, pf=100.0, n: int = 128):
    """与 SCPITestWave.DCGetIVValueFunction Keysight 分支同公式（抽测用）。"""
    f_vmp = float(vmp)
    f_imp = float(imp) * (0.01 * float(pf))
    f_voc = float(voc)
    f_isc = float(isc) * (0.01 * float(pf))
    c2 = (f_vmp / f_voc - 1) / math.log(1 - f_imp / f_isc)
    c1 = (1 - f_imp / f_isc) * math.exp(-1 * f_vmp / (c2 * f_voc))
    den = float(n - 1) if n > 1 else 1.0
    curr = []
    volt = []
    for i in range(n):
        p = i / den
        i_pt = round((1 - p) * f_isc, 3)
        ratio = 1.0 - (i_pt / f_isc)
        inner = (ratio / c1) + 1.0
        if abs(inner) < 1e-15:
            inner = 1e-15
        v_pt = round(abs(math.log(abs(inner)) * c2 * f_voc), 3)
        curr.append(f"{i_pt:.3f}")
        volt.append(f"{v_pt:.3f}")
    return (
        "SAS:TABL1:VOLT " + ",".join(volt),
        "SAS:TABL1:CURR " + ",".join(curr),
    )


def test_keysight_128_points_under_2kb():
    volt, curr = _build_keysight_tabl_cmds(400, 8, 500, 10, n=128)
    assert volt.count(",") == 127
    assert curr.count(",") == 127
    assert len(volt) < 2048
    assert len(curr) < 2048


def test_keysight_1024_would_be_huge():
    volt, _curr = _build_keysight_tabl_cmds(400, 8, 500, 10, n=1024)
    assert len(volt) > 5000
