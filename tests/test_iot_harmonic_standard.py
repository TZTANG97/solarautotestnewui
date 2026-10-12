# -*- coding: utf-8 -*-
from utils.iot_harmonic_standard import (
    HARMONIC_STANDARD_DEFAULTS,
    apply_harmonic_standard_to_ui,
    apply_harmonic_standard_to_widgets,
    list_harmonic_standard_options,
    resolve_harmonic_standard_id,
)


def test_harmonic_catalog_and_defaults_diverge():
    opts = list_harmonic_standard_options()
    assert len(opts) == 8
    assert opts[0]["id"] == "thai"
    assert resolve_harmonic_standard_id(widgets={"solarStandard": "en50549"}) == "en50549"

    thai = apply_harmonic_standard_to_widgets({}, "thai", force=True)
    eu = apply_harmonic_standard_to_widgets({}, "en50549", force=True)
    br = apply_harmonic_standard_to_widgets({}, "br_ord140", force=True)
    it = apply_harmonic_standard_to_widgets({}, "it_cei", force=True)
    assert thai["checkBox_S3_2"] is True
    assert eu["checkBox_S3_2"] is False
    assert eu["spinBox_DEW_MaxHarmonicOrder"] == 50
    assert br["textEdit_S1_AC_FR"] == "60"
    assert it["textEdit_S1_DC1_PF_3"] == "66"

    ids = sorted(HARMONIC_STANDARD_DEFAULTS)
    assert len(ids) == 8
    rows = [apply_harmonic_standard_to_widgets({}, sid, force=True) for sid in ids]
    for i, a in enumerate(rows):
        for b in rows[i + 1 :]:
            assert a != b


def test_apply_harmonic_standard_to_ui_meta():
    class _Stub:
        pass

    ui = _Stub()
    sid = apply_harmonic_standard_to_ui(ui, "it_cei", apply_defaults=True)
    assert sid == "it_cei"
    assert ui._solar_standard == "it_cei"
