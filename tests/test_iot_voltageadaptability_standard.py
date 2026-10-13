# -*- coding: utf-8 -*-
from utils.iot_voltageadaptability_standard import (
    VOLTAGEADAPTABILITY_STANDARD_DEFAULTS,
    apply_voltageadaptability_standard_to_ui,
    apply_voltageadaptability_standard_to_widgets,
    list_voltageadaptability_standard_options,
    resolve_voltageadaptability_standard_id,
)


def test_resolve_and_options():
    assert (
        resolve_voltageadaptability_standard_id(widgets={"solarStandard": "en50549"})
        == "en50549"
    )
    assert resolve_voltageadaptability_standard_id(widgets={}) == "thai"
    ids = {o["id"] for o in list_voltageadaptability_standard_options()}
    assert ids == set(VOLTAGEADAPTABILITY_STANDARD_DEFAULTS)


def test_defaults_pairwise_distinct():
    sids = sorted(VOLTAGEADAPTABILITY_STANDARD_DEFAULTS)
    for i, a in enumerate(sids):
        for b in sids[i + 1 :]:
            assert (
                VOLTAGEADAPTABILITY_STANDARD_DEFAULTS[a]
                != VOLTAGEADAPTABILITY_STANDARD_DEFAULTS[b]
            ), f"{a} vs {b}"


def test_apply_force_and_fill_empty():
    thai = apply_voltageadaptability_standard_to_widgets({}, "thai", force=True)
    assert "253" in thai["textEdit_VoltageLadder_guoya"]
    assert thai["comboBox_S1_AC_2"] == "单相"

    forced = apply_voltageadaptability_standard_to_widgets({}, "br_ord140", force=True)
    assert forced["textEdit_S1_AC_FR"] == "60"
    assert "220" in forced["textEdit_VoltageLadder_guoya"]


def test_apply_ui_meta():
    class _Stub:
        pass

    ui = _Stub()
    sid = apply_voltageadaptability_standard_to_ui(ui, "de_vde", apply_defaults=True)
    assert sid == "de_vde"
    assert ui._solar_standard == "de_vde"
