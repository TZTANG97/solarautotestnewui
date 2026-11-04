# -*- coding: utf-8 -*-
"""云端 S1_* widgets → Soft Panel AC/DC 键映射。"""

from __future__ import annotations

from utils.iot_boot_params_sync import (
    extract_ac_boot_from_widgets,
    extract_dc1_iv_from_widgets,
    normalize_phase_label,
    phase_combo_aliases,
)


def test_normalize_phase_three_single():
    assert normalize_phase_label("Three") == "三相"
    assert normalize_phase_label("Single") == "单相"
    assert normalize_phase_label("三相") == "三相"
    assert normalize_phase_label("单相") == "单相"
    assert normalize_phase_label("") == ""


def test_extract_ac_prefers_s1_and_soft_panel():
    ac = extract_ac_boot_from_widgets(
        {
            "comboBox_S1_AC_2": "Three",
            "textEdit_S1_AC_VOLT": "230",
            "textEdit_S1_AC_FR": "50",
        }
    )
    assert ac == {"phase": "三相", "volt": "230", "freq": "50"}

    ac2 = extract_ac_boot_from_widgets(
        {
            "comboBox_Phase": "单相",
            "textEdit_AC_VOLT": "220",
            "textEdit_AC_FR": "60",
            "comboBox_S1_AC_2": "Three",
        }
    )
    # Soft Panel 键优先
    assert ac2["phase"] == "单相"
    assert ac2["volt"] == "220"


def test_extract_dc1_from_s1_dialog_keys():
    dc = extract_dc1_iv_from_widgets(
        {
            "textEdit_S1_DC1_VOLT": "650",
            "textEdit_S1_DC1_CURR": "14.364",
            "textEdit_S1_DC1_Voc": "726.9",
            "textEdit_S1_DC1_Isc": "14.832",
            "textEdit_S1_DC1_PF": "100",
        }
    )
    assert dc["vmp"] == "650"
    assert dc["imp"] == "14.364"
    assert dc["voc"] == "726.9"
    assert dc["isc"] == "14.832"
    assert dc["pf"] == "100"


def test_extract_dc1_keeps_explicit_ff_and_mode():
    dc = extract_dc1_iv_from_widgets(
        {
            "textEdit_Vmp": "750",
            "textEdit_Imp": "13.33",
            "textEdit_Voc": "804",
            "textEdit_Isc": "14.29",
            "textEdit_PF": "100",
            "textEdit_FF": "0.85",
            "comboBox_DC_Mode": "SAS",
        }
    )
    assert dc["ff"] == "0.85"
    assert dc["mode"] == "sas"


def test_apply_bluesight_sas_from_iv_sets_mode_and_stc():
    from utils.iot_boot_params_sync import apply_bluesight_sas_from_iv

    class _Spin:
        def __init__(self, value):
            self.value = value

        def setValue(self, value):
            self.value = value

    class _Combo:
        def __init__(self):
            self.idx = 0

        def setCurrentIndex(self, idx):
            self.idx = idx

    ref = {
        "combo_mode": _Combo(),
        "sp_pmpp": _Spin(8.0),
        "sp_umpp": _Spin(650.0),
        "sp_ff": _Spin(0.8),
    }
    triple = apply_bluesight_sas_from_iv(
        ref,
        {
            "vmp": "750",
            "imp": "13.33",
            "voc": "804",
            "isc": "14.29",
            "pf": "100",
            "ff": "0.85",
            "mode": "SAS",
        },
    )
    assert triple is not None
    assert ref["combo_mode"].idx == 1
    assert abs(ref["sp_umpp"].value - 750) < 1e-6
    assert abs(ref["sp_pmpp"].value - 9.9975) < 1e-3
    assert abs(ref["sp_ff"].value - 0.85) < 1e-6


def test_apply_ac_boot_writes_itech_phase_not_only_chroma():
    from utils.iot_boot_params_sync import apply_ac_boot_to_panels

    class _Combo:
        def __init__(self):
            self.items = ["单相", "三相"]
            self.idx = 0

        def findText(self, text):
            return self.items.index(text) if text in self.items else -1

        def setCurrentIndex(self, idx):
            self.idx = idx

        def currentText(self):
            return self.items[self.idx]

    class _Text:
        def __init__(self, value):
            self.value = value

        def setPlainText(self, text):
            self.value = text

    chroma_phase, itech_phase = _Combo(), _Combo()
    chroma = type("C", (), {
        "comboBox_Phase": chroma_phase,
        "textEdit_AC_VOLT": _Text("220"),
        "textEdit_AC_FR": _Text("50"),
    })()
    itech = {
        "combo_phase": itech_phase,
        "textEdit_VOLT": _Text("220"),
        "textEdit_FR": _Text("50"),
    }
    apply_ac_boot_to_panels(
        {"phase": "三相", "volt": "230", "freq": "50"},
        chroma_ui=chroma,
        itech_ref=itech,
    )
    assert chroma_phase.currentText() == "三相"
    assert itech_phase.currentText() == "三相"
    assert itech["textEdit_VOLT"].value == "230"


def test_phase_combo_aliases():
    assert "三相" in phase_combo_aliases("Three")
    assert "单相" in phase_combo_aliases("Single")


def test_output_on_aliases_and_phase_fill():
    from utils.iot_boot_params_sync import (
        fill_missing_phase_volts,
        is_output_on,
        normalize_output_on,
        output_combo_aliases,
    )

    assert normalize_output_on("ON") is True
    assert normalize_output_on("开启") is True
    assert normalize_output_on("OFF") is False
    assert is_output_on("ON", default=False) is True
    assert is_output_on("关闭", default=True) is False
    assert "开启" in output_combo_aliases("ON")

    filled = fill_missing_phase_volts(
        {
            "textEdit_S1_AC_VOLT": "230",
            "textEdit_S4_AC_VOLT": "230",
        }
    )
    assert filled["textEdit_S1_AC_VOLT_2"] == "230"
    assert filled["textEdit_S1_AC_VOLT_3"] == "230"
    assert filled["textEdit_S4_AC_VOLT_2"] == "230"
    assert filled["comboBox_S1_AC"] == "开启"
