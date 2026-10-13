# -*- coding: utf-8 -*-
from utils.iot_qianpinshengzai_standard import (
    QIANPINSHENGZAI_STANDARD_DEFAULTS,
    apply_qianpinshengzai_standard_to_ui,
    apply_qianpinshengzai_standard_to_widgets,
    list_qianpinshengzai_standard_options,
    resolve_qianpinshengzai_standard_id,
)


def test_resolve_and_options():
    assert resolve_qianpinshengzai_standard_id(widgets={"solarStandard": "en50549"}) == "en50549"
    assert resolve_qianpinshengzai_standard_id(widgets={}) == "thai"
    ids = {o["id"] for o in list_qianpinshengzai_standard_options()}
    assert ids == set(QIANPINSHENGZAI_STANDARD_DEFAULTS)


def test_defaults_pairwise_distinct():
    sids = sorted(QIANPINSHENGZAI_STANDARD_DEFAULTS)
    for i, a in enumerate(sids):
        for b in sids[i + 1 :]:
            assert (
                QIANPINSHENGZAI_STANDARD_DEFAULTS[a] != QIANPINSHENGZAI_STANDARD_DEFAULTS[b]
            ), f"{a} vs {b}"


def test_apply_force_and_fill_empty():
    thai = apply_qianpinshengzai_standard_to_widgets({}, "thai", force=True)
    assert thai["textEdit_FrequencyLadder_TIME"] == "60"
    assert "49.0" in thai["textEdit_FrequencyLadder"]
    assert thai["comboBox_S1_AC_2"] == "单相"

    kept = apply_qianpinshengzai_standard_to_widgets(
        {"textEdit_FrequencyLadder_TIME": "99", "solarStandard": "en50549"},
        "en50549",
        force=False,
    )
    assert kept["textEdit_FrequencyLadder_TIME"] == "99"
    assert kept["comboBox_S1_AC_2"] == "三相"
    assert "48.5" in kept["textEdit_FrequencyLadder"]

    forced = apply_qianpinshengzai_standard_to_widgets(
        {"textEdit_FrequencyLadder_TIME": "99"},
        "br_ord140",
        force=True,
    )
    assert forced["textEdit_FrequencyLadder_TIME"] == "30"
    assert forced["textEdit_S1_AC_FR"] == "60"
    assert forced["textEdit_FrequencyLadder_VOLT"] == "220"


def test_apply_qianpinshengzai_standard_to_ui_meta():
    class _Stub:
        pass

    ui = _Stub()
    sid = apply_qianpinshengzai_standard_to_ui(ui, "uk_g99", apply_defaults=True)
    assert sid == "uk_g99"
    assert ui._solar_standard == "uk_g99"
