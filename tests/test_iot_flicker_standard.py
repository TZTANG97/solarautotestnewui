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


def test_force_false_keeps_user_value():
    w = apply_flicker_standard_to_widgets(
        {"textEdit_S2_TIME": "99", "solarStandard": "en50549"},
        "en50549",
        force=False,
    )
    assert w["textEdit_S2_TIME"] == "99"
    assert w["comboBox_S2_PER_FLICK_COUNT"] == "1"
