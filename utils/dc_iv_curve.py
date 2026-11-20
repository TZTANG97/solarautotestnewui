# -*- coding: utf-8 -*-
"""致茂 / 是德光伏模拟器 IV 表。电压用理想电流比例，避免百分比缩放后短路端电压被放大。"""

from __future__ import annotations

import math
from typing import List, Tuple


def sas_iv_table(vmp: float, imp: float, voc: float, isc: float, n_points: int = 128) -> Tuple[List[str], List[str]]:
    """返回 (电流点, 电压点)，各点已格式化为 3 位小数。

    电流仍按 (1 - k/(n-1)) * Isc 四舍五入到 0.001A。
    电压用理想比例 k/(n-1)，不用舍入后的电流。功率百分比把 Isc 乘完后
    常常落不到 0.001A；若再用舍入电流反推 1-I/Isc，高填充因子下 C1 极小，
    短路端会从 0V 被放大到几百伏。
    """
    n = int(n_points)
    if n < 2:
        raise ValueError("n_points")
    if min(vmp, imp, voc, isc) <= 0 or imp >= isc or vmp >= voc:
        raise ValueError("iv points")
    den = float(n - 1)
    c2 = (vmp / voc - 1.0) / math.log(1.0 - imp / isc)
    c1 = (1.0 - imp / isc) * math.exp(-vmp / (c2 * voc))
    currents: List[str] = []
    voltages: List[str] = []
    for k in range(n):
        frac = k / den
        cur = round((1.0 - frac) * isc, 3)
        inner = (frac / c1) + 1.0
        if abs(inner) < 1e-15:
            inner = 1e-15
        vol = round(abs(math.log(abs(inner)) * c2 * voc), 3)
        currents.append("%.3f" % cur)
        voltages.append("%.3f" % vol)
    return currents, voltages
