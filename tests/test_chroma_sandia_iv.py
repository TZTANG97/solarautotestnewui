# -*- coding: utf-8 -*-
"""Chroma Soft Panel Sandia 金标（截图 Irr=1000 TC=50 Pmax=7000 FF=0.85 Beta=-0.38 Vmp=650）。"""
from __future__ import annotations

import math


def _near(a: float, b: float, *, rel: float = 0.005, abs_tol: float = 0.05) -> bool:
    return abs(a - b) <= max(abs_tol, abs(b) * rel)


def test_soft_panel_golden_screenshot():
    from utils.chroma_sandia_iv import calc_sandia_iv

    pts = calc_sandia_iv(
        vmp=650,
        pmax_w=7000,
        ff=0.85,
        beta_pct_per_c=-0.38,
        irr_wm2=1000,
        irr_ref_wm2=1000,
        tc_c=50,
        tc_ref_c=50,
    )
    assert pts["vmp"] == 650.0
    assert _near(pts["imp"], 10.768)
    assert _near(pts["voc"], 726.9)
    assert _near(pts["isc"], 11.120)
    assert _near(pts["pmp"], 6999.2)
    assert pts["voc"] > pts["vmp"]
    assert pts["isc"] > pts["imp"]


def test_imp_from_pmax_vmp():
    from utils.chroma_sandia_iv import calc_sandia_iv

    pts = calc_sandia_iv(vmp=650, pmax_w=7000, ff=0.85, tc_c=50, tc_ref_c=50)
    assert abs(pts["imp"] - 10.768) < 1e-9
    assert abs(pts["pmp"] - 650.0 * 10.768) < 1e-6


def test_temp_beta_shifts_voc():
    from utils.chroma_sandia_iv import calc_sandia_iv

    base = calc_sandia_iv(
        vmp=650, pmax_w=7000, ff=0.85, beta_pct_per_c=-0.38, tc_c=50, tc_ref_c=50
    )
    hot = calc_sandia_iv(
        vmp=650, pmax_w=7000, ff=0.85, beta_pct_per_c=-0.38, tc_c=75, tc_ref_c=50
    )
    # Beta 为负：升温 Voc 下降
    assert hot["voc"] < base["voc"]
    expected = base["voc"] * (1.0 + (-0.38) / 100.0 * 25.0)
    assert abs(hot["voc"] - round(expected, 3)) < 0.02


def test_irr_scales_current():
    from utils.chroma_sandia_iv import calc_sandia_iv

    base = calc_sandia_iv(
        vmp=650, pmax_w=7000, ff=0.85, irr_wm2=1000, irr_ref_wm2=1000, tc_c=50, tc_ref_c=50
    )
    half = calc_sandia_iv(
        vmp=650, pmax_w=7000, ff=0.85, irr_wm2=500, irr_ref_wm2=1000, tc_c=50, tc_ref_c=50
    )
    assert _near(half["imp"], base["imp"] * 0.5, abs_tol=0.02)
    assert _near(half["isc"], base["isc"] * 0.5, abs_tol=0.02)
    assert half["voc"] < base["voc"]  # 对数辐照修正


def test_sandia_inputs_from_mapping_defaults():
    from utils.chroma_sandia_iv import sandia_inputs_from_mapping

    d = sandia_inputs_from_mapping({})
    assert d["vmp"] == 650.0
    assert d["pmax_w"] == 7000.0
    assert math.isclose(d["ff"], 0.85)
    assert d["tc_c"] == 50.0
    assert d["tc_ref_c"] == 50.0


def test_power_level_scales_current_not_voltage():
    from utils.chroma_sandia_iv import calc_sandia_iv

    full = calc_sandia_iv(
        vmp=650, pmax_w=7000, ff=0.85, irr_wm2=1000, irr_ref_wm2=1000, tc_c=50, tc_ref_c=50
    )
    half = calc_sandia_iv(
        vmp=650,
        pmax_w=7000,
        ff=0.85,
        irr_wm2=1000,
        irr_ref_wm2=1000,
        tc_c=50,
        tc_ref_c=50,
        power_pct=50,
    )
    assert half["vmp"] == full["vmp"]
    assert abs(half["voc"] - full["voc"]) < 1e-9
    assert abs(half["imp"] - full["imp"] * 0.5) < 1e-9
    assert _near(half["isc"], full["isc"] * 0.5, abs_tol=0.002)
    assert half["power_pct"] == 50.0


def test_power_percent_accepts_percent_sign_and_fraction():
    from utils.chroma_sandia_iv import parse_power_percent, sandia_inputs_from_mapping

    assert parse_power_percent("80%") == 80.0
    assert parse_power_percent("0.8") == 80.0
    mapped = sandia_inputs_from_mapping({"power_pct": "50%"})
    assert mapped["power_pct"] == 50.0


def test_rejects_bad_vmp():
    from utils.chroma_sandia_iv import calc_sandia_iv

    try:
        calc_sandia_iv(vmp=0, pmax_w=7000, ff=0.85)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_resolve_power_prefers_dc_page_until_panel_edited():
    from utils.chroma_sandia_iv import resolve_power_percent

    assert resolve_power_percent("50", "100", panel_edited=False) == 50.0
    assert resolve_power_percent("50", "80", panel_edited=True) == 80.0
    assert resolve_power_percent("", "60%", panel_edited=False) == 60.0


class _Plain:
    def __init__(self, text: str):
        self._text = text

    def toPlainText(self):
        return self._text

    def setPlainText(self, text: str):
        self._text = text

    def isChecked(self):
        return True


def test_apply_remembered_dc_iv_fills_later_dialog(monkeypatch):
    import components.sandia_iv_panel as panel

    store = {
        "dc.sandia_fill": "1",
        "dc.vmp": "650",
        "dc.imp": "5.384",
        "dc.voc": "726.9",
        "dc.isc": "5.56",
        "dc.sandia_scaled": "1",
    }
    monkeypatch.setattr(panel, "last_value", lambda key, default="": store.get(key, default))
    ui = type("Ui", (), {})()
    ui.textEdit_S1_DC1_VOLT = _Plain("400")
    ui.textEdit_S1_DC1_CURR = _Plain("10")
    ui.textEdit_S1_DC1_Voc = _Plain("450")
    ui.textEdit_S1_DC1_Isc = _Plain("12")
    ui.textEdit_S1_DC1_PF = _Plain("40")
    ui.checkBox_S1_DC1 = _Plain("1")
    assert panel.apply_remembered_dc_iv(ui) is True
    assert ui.textEdit_S1_DC1_VOLT.toPlainText() == "650"
    assert ui.textEdit_S1_DC1_CURR.toPlainText() == "5.384"
    assert ui.textEdit_S1_DC1_PF.toPlainText() == "100"
