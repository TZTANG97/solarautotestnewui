# -*- coding: utf-8 -*-
"""功率百分比缩放后，短路端电压必须仍是 0V。"""

from utils.dc_iv_curve import sas_iv_table


def test_percent_scale_keeps_short_circuit_at_zero_volts():
    """147 的 80% 档：旧算法把短路端算成约 476V，电流比例本身是对的。"""
    isc = 19.541
    imp = 19.23 * isc / 19.859
    full_i, full_v = sas_iv_table(650.0, imp, 726.9, isc)
    scaled_i, scaled_v = sas_iv_table(650.0, imp * 0.8, 726.9, isc * 0.8)

    assert full_i[0] == "19.541"
    assert full_v[0] == "0.000"
    assert scaled_i[0] == "15.633"
    assert scaled_v[0] == "0.000"
    assert abs(float(scaled_v[1]) - float(full_v[1])) < 0.05
