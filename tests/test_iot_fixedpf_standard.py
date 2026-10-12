# -*- coding: utf-8 -*-
from utils.iot_fixedpf_standard import (
    FIXEDPF_STANDARD_DEFAULTS,
    apply_fixedpf_standard_to_widgets,
    list_fixedpf_standard_options,
    resolve_fixedpf_standard_id,
)


def test_resolve_and_options():
    assert resolve_fixedpf_standard_id(widgets={"solarStandard": "en50549"}) == "en50549"
    assert resolve_fixedpf_standard_id(widgets={}) == "thai"
    ids = {o["id"] for o in list_fixedpf_standard_options()}
    assert ids == set(FIXEDPF_STANDARD_DEFAULTS)


def test_defaults_pairwise_distinct():
    sids = sorted(FIXEDPF_STANDARD_DEFAULTS)
    for i, a in enumerate(sids):
        for b in sids[i + 1 :]:
            assert FIXEDPF_STANDARD_DEFAULTS[a] != FIXEDPF_STANDARD_DEFAULTS[b], f"{a} vs {b}"


def test_apply_force_and_fill_empty():
    thai = apply_fixedpf_standard_to_widgets({}, "thai", force=True)
    assert thai["checkBox_S4"] is True
    assert thai["textEdit_S1_DC1_PF_4"] == "100"
    assert thai["checkBox_S5"] is True
    assert thai["textEdit_S1_DC1_PF_5"] == "75"

    kept = apply_fixedpf_standard_to_widgets(
        {"textEdit_S3_TIME_2": "99", "solarStandard": "en50549"},
        "en50549",
        force=False,
    )
    assert kept["textEdit_S3_TIME_2"] == "99"
    assert kept["checkBox_S5"] is False

    forced = apply_fixedpf_standard_to_widgets(
        {"textEdit_S3_TIME_2": "99"},
        "uk_g99",
        force=True,
    )
    assert forced["textEdit_S3_TIME_2"] == "20"
    assert forced["comboBox_S1_AC_2"] == "单相"
