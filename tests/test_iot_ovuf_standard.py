# -*- coding: utf-8 -*-
from utils.iot_ovuf_standard import (
    OVUF_STANDARD_DEFAULTS,
    apply_ovuf_standard_to_ui,
    apply_ovuf_standard_to_widgets,
    list_ovuf_standard_options,
    resolve_ovuf_standard_id,
)


def test_resolve_and_options():
    assert resolve_ovuf_standard_id(widgets={"solarStandard": "en50549"}) == "en50549"
    assert resolve_ovuf_standard_id(widgets={"solarStandard": "iec"}) == "iec61727"
    assert resolve_ovuf_standard_id(widgets={"solarStandard": "cn_gb"}) == "en50549"
    assert resolve_ovuf_standard_id(widgets={}) == "thai"
    ids = {o["id"] for o in list_ovuf_standard_options()}
    assert ids == set(OVUF_STANDARD_DEFAULTS)


def test_defaults_pairwise_distinct():
    sids = sorted(OVUF_STANDARD_DEFAULTS)
    for i, a in enumerate(sids):
        for b in sids[i + 1 :]:
            assert OVUF_STANDARD_DEFAULTS[a] != OVUF_STANDARD_DEFAULTS[b], f"{a} vs {b}"


def test_apply_force_and_fill_empty():
    thai = apply_ovuf_standard_to_widgets({}, "thai", force=True)
    assert thai["checkBox_S3"] is True
    assert thai["textEdit_S3_AC_VOLT_End"] == "230"
    assert thai["_ovufDwellSec"] == "3"

    kept = apply_ovuf_standard_to_widgets(
        {"textEdit_S3_TIME": "99", "solarStandard": "en50549"},
        "en50549",
        force=False,
    )
    assert kept["textEdit_S3_TIME"] == "99"
    assert kept["comboBox_S1_AC_2"] == "三相"
    assert kept["textEdit_S3_AC_VOLT_End"] == "253"

    forced = apply_ovuf_standard_to_widgets(
        {"textEdit_S3_TIME": "99"},
        "uk_g99",
        force=True,
    )
    assert forced["textEdit_S3_TIME"] == "10"
    assert forced["checkBox_S5"] is False
    assert forced["comboBox_S1_AC_2"] == "单相"


def test_apply_ovuf_standard_to_ui_meta():
    class _Stub:
        pass

    ui = _Stub()
    sid = apply_ovuf_standard_to_ui(ui, "br_ord140", apply_defaults=True)
    assert sid == "br_ord140"
    assert ui._solar_standard == "br_ord140"
