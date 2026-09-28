# -*- coding: utf-8 -*-
"""IV helpers + compact field heuristics (autofill wiring disabled)."""
from __future__ import annotations

import math


def test_calc_iv_from_voc_ff_power_100pct():
    from utils.dc_iv_autofill import calc_iv_from_voc_ff_power

    pts = calc_iv_from_voc_ff_power(voc=1000.0, ff=0.8, power_w=8000.0, percent=100)
    assert abs(pts["voc"] - 1000.0) < 1e-6
    assert abs(pts["pmp"] - 8000.0) < 1e-6
    assert abs(pts["isc"] - 8000.0 / (1000.0 * 0.8)) < 1e-6
    assert abs(pts["vmp"] - 1000.0 * math.sqrt(0.8)) < 1e-2
    assert abs(pts["imp"] - pts["pmp"] / pts["vmp"]) < 1e-2
    ff_chk = (pts["vmp"] * pts["imp"]) / (pts["voc"] * pts["isc"])
    assert abs(ff_chk - 0.8) < 1e-3


def test_wire_dc_iv_autofill_is_noop():
    from utils.dc_iv_autofill import wire_dc_iv_autofill

    # Must not raise / must not require Qt widgets
    assert wire_dc_iv_autofill(None, None, None, None) is None


def test_unit_percent_not_expand():
    from components.timeline import _is_unit_field, _should_expand_field
    from PyQt5.QtWidgets import QApplication, QLineEdit, QTextEdit
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    unit = QLineEdit("%")
    assert _is_unit_field("lineEdit_2", unit)
    assert not _should_expand_field("textEdit_Vmp", QTextEdit())
    assert not _should_expand_field("textEdit_PF", QTextEdit())
