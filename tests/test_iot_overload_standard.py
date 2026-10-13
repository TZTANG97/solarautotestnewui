# -*- coding: utf-8 -*-
from utils.iot_overload_standard import (
    OVERLOAD_STANDARD_DEFAULTS,
    apply_overload_standard_to_widgets,
    list_overload_standard_options,
    resolve_overload_standard_id,
)


def test_resolve_and_options():
    assert resolve_overload_standard_id(widgets={"solarStandard": "en50549"}) == "en50549"
    assert resolve_overload_standard_id(widgets={}) == "thai"
    ids = {o["id"] for o in list_overload_standard_options()}
    assert ids == set(OVERLOAD_STANDARD_DEFAULTS)


def test_defaults_pairwise_distinct():
    sids = sorted(OVERLOAD_STANDARD_DEFAULTS)
    for i, a in enumerate(sids):
        for b in sids[i + 1 :]:
            assert OVERLOAD_STANDARD_DEFAULTS[a] != OVERLOAD_STANDARD_DEFAULTS[b], f"{a} vs {b}"


def test_apply_force_and_fill_empty():
    thai = apply_overload_standard_to_widgets({}, "thai", force=True)
    assert thai["textEdit_S3_TIME_2"] == "90"
    assert thai["comboBox_S1_AC_2"] == "单相"
    assert thai["_overloadHoldMin"] == "90"

    kept = apply_overload_standard_to_widgets(
        {"textEdit_S3_TIME_2": "99", "solarStandard": "en50549"},
        "en50549",
        force=False,
    )
    assert kept["textEdit_S3_TIME_2"] == "99"
    assert kept["comboBox_S1_AC_2"] == "三相"

    forced = apply_overload_standard_to_widgets(
        {"textEdit_S3_TIME_2": "99"},
        "uk_g99",
        force=True,
    )
    assert forced["textEdit_S3_TIME_2"] == "120"
    assert forced["comboBox_S1_AC_2"] == "单相"


def test_apply_overload_standard_to_ui_meta():
    from utils.iot_overload_standard import apply_overload_standard_to_ui

    class _Ui:
        pass

    ui = _Ui()
    sid = apply_overload_standard_to_ui(ui, "it_cei", apply_defaults=True)
    assert sid == "it_cei"
    assert getattr(ui, "_solar_standard") == "it_cei"
