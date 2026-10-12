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


def test_au_it_uk_and_all_eight_distinct():
    from utils.iot_flicker_standard import FLICKER_STANDARD_DEFAULTS

    au = apply_flicker_standard_to_widgets({}, "as_nzs", force=True)
    it = apply_flicker_standard_to_widgets({}, "it_cei", force=True)
    uk = apply_flicker_standard_to_widgets({}, "uk_g99", force=True)
    assert au["comboBox_S2_WT"] == "单相"
    assert it["comboBox_S2_PER_FLICK_COUNT"] == "3"
    assert it["textEdit_S3_TIME"] == "8"
    assert flicker_cycle_seconds("uk_g99", uk) == 7200
    ids = sorted(FLICKER_STANDARD_DEFAULTS)
    assert len(ids) == 8
    rows = [apply_flicker_standard_to_widgets({}, sid, force=True) for sid in ids]
    for i, a in enumerate(rows):
        for b in rows[i + 1 :]:
            assert a != b


def test_list_flicker_standard_options_desktop_catalog():
    from utils.iot_flicker_standard import list_flicker_standard_options

    opts = list_flicker_standard_options()
    assert len(opts) == 8
    assert opts[0]["id"] == "thai"
    assert "现行" in opts[0]["label"]
    ids = [o["id"] for o in opts]
    assert ids == [
        "thai",
        "de_vde",
        "br_ord140",
        "en50549",
        "as_nzs",
        "it_cei",
        "uk_g99",
        "iec61727",
    ]


def test_apply_flicker_standard_to_ui_meta_only():
    """无 Qt 控件时仍可挂 _solar_standard / 周期（handoff 兼容）。"""
    from utils.iot_flicker_standard import apply_flicker_standard_to_ui

    class _Stub:
        pass

    ui = _Stub()
    sid = apply_flicker_standard_to_ui(ui, "uk_g99", apply_defaults=True)
    assert sid == "uk_g99"
    assert ui._solar_standard == "uk_g99"
    assert int(ui._flicker_cycle_sec) == 7200


def test_force_false_keeps_user_value():
    w = apply_flicker_standard_to_widgets(
        {"textEdit_S2_TIME": "99", "solarStandard": "en50549"},
        "en50549",
        force=False,
    )
    assert w["textEdit_S2_TIME"] == "99"
    assert w["comboBox_S2_PER_FLICK_COUNT"] == "1"
