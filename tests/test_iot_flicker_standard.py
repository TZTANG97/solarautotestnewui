# -*- coding: utf-8 -*-
from utils.iot_flicker_standard import (
    apply_flicker_standard_to_widgets,
    flicker_cycle_seconds,
    resolve_flicker_standard_id,
)


def test_resolve_and_thai_eu_differ():
    assert resolve_flicker_standard_id(widgets={"solarStandard": "en50549"}) == "en50549"
    thai = apply_flicker_standard_to_widgets({}, "thai", force=True)
    eu = apply_flicker_standard_to_widgets({}, "en50549", force=True)
    assert thai["comboBox_S2_PER_FLICK_COUNT"] == "3"
    assert eu["comboBox_S2_PER_FLICK_COUNT"] == "1"
    assert thai["comboBox_S2_WT"] == "单相"
    assert eu["comboBox_S2_WT"] == "三相"
    assert flicker_cycle_seconds("en50549", eu) == 600


def test_de_br_iec_defaults_diverge():
    de = apply_flicker_standard_to_widgets({}, "de_vde", force=True)
    br = apply_flicker_standard_to_widgets({}, "br_ord140", force=True)
    iec = apply_flicker_standard_to_widgets({}, "iec61727", force=True)
    assert de["textEdit_S2_TIME"] == "12"
    assert flicker_cycle_seconds("de_vde", de) == 720
    assert br["textEdit_S1_AC_FR"] == "60"
    assert br["comboBox_DEW_WeightingType"] == "230V / 60Hz"
    assert iec["comboBox_S2_PER_FLICK_COUNT"] == "2"
    assert resolve_flicker_standard_id(widgets={"solarStandard": "br_ord140"}) == "br_ord140"


def test_force_false_keeps_user_value():
    w = apply_flicker_standard_to_widgets(
        {"textEdit_S2_TIME": "99", "solarStandard": "en50549"},
        "en50549",
        force=False,
    )
    assert w["textEdit_S2_TIME"] == "99"
    assert w["comboBox_S2_PER_FLICK_COUNT"] == "1"
