# -*- coding: utf-8 -*-
from utils.iot_dccomponent_standard import (
    DCCOMPONENT_STANDARD_DEFAULTS,
    apply_dccomponent_standard_to_widgets,
    list_dccomponent_standard_options,
    resolve_dccomponent_standard_id,
)


def test_resolve_and_options():
    assert resolve_dccomponent_standard_id(widgets={"solarStandard": "en50549"}) == "en50549"
    assert resolve_dccomponent_standard_id(widgets={}) == "thai"
    ids = {o["id"] for o in list_dccomponent_standard_options()}
    assert ids == set(DCCOMPONENT_STANDARD_DEFAULTS)


def test_defaults_pairwise_distinct():
    sids = sorted(DCCOMPONENT_STANDARD_DEFAULTS)
    for i, a in enumerate(sids):
        for b in sids[i + 1 :]:
            assert DCCOMPONENT_STANDARD_DEFAULTS[a] != DCCOMPONENT_STANDARD_DEFAULTS[b], f"{a} vs {b}"


def test_apply_force_and_fill_empty():
    thai = apply_dccomponent_standard_to_widgets({}, "thai", force=True)
    assert thai["checkBox_S3"] is True
    assert thai["textEdit_S3_DC_PF"] == "100"
    assert thai["checkBox_S4"] is True
    assert thai["textEdit_S4_DC_PF"] == "66"

    kept = apply_dccomponent_standard_to_widgets(
        {"textEdit_S3_TIME_2": "99", "solarStandard": "en50549"},
        "en50549",
        force=False,
    )
    assert kept["textEdit_S3_TIME_2"] == "99"
    assert kept["checkBox_S4"] is False

    forced = apply_dccomponent_standard_to_widgets(
        {"textEdit_S3_TIME_2": "99"},
        "en50549",
        force=True,
    )
    assert forced["textEdit_S3_TIME_2"] == "10"
    assert forced["textEdit_S1_AC_FR"] == "50"
