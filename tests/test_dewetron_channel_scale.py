# -*- coding: utf-8 -*-
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_CHANNEL = (
    '<Channel id="{cid}">'
    '<Property name="ShortId"><StringValue>"{name}"</StringValue></Property>'
    '<Property name="Neon/PhysicalScaleFactor"><DoubleValue>{factor}</DoubleValue></Property>'
    "</Channel>"
)


def _sample_xml():
    parts = [
        _CHANNEL.format(cid="1", name="AI 1/U1", factor="1"),
        _CHANNEL.format(cid="2", name="AI 1/I1", factor="1"),
        _CHANNEL.format(cid="3", name="AI 1/U2", factor="1.5"),
    ]
    return "".join(parts)


def test_format_and_apply_scale_factor_on_matching_channel_only():
    from utils.dewetron_channel_scale import (
        apply_physical_scale_factors,
        format_physical_scale_factor,
        read_physical_scale_factors,
    )

    assert format_physical_scale_factor("100.0") == "100"
    assert format_physical_scale_factor("0.50") == "0.5"
    assert format_physical_scale_factor("abc") is None
    assert format_physical_scale_factor("") is None

    xml = _sample_xml()
    updated = apply_physical_scale_factors(
        xml,
        {"AI 1/U1": "20", "AI 1/l1": "2.5", "AI 1/U2": "bad"},
    )
    found = read_physical_scale_factors(updated)
    assert found["AI 1/U1"] == "20"
    assert found["AI 1/l1"] == "2.5"
    assert found["AI 1/U2"] == "1.5"


def test_modify_xml_writes_scale_factor():
    from devices.dewetron_controller import DewetronController

    updated = DewetronController.modify_xml(
        _sample_xml(),
        wiring_type=None,
        channel_map={},
        channel_scale_factors={"AI 1/U1": "8"},
    )
    assert 'ShortId"><StringValue>"AI 1/U1"' in updated
    u1 = updated.split('ShortId"><StringValue>"AI 1/U2"')[0]
    assert "<DoubleValue>8</DoubleValue>" in u1
    assert u1.count("<DoubleValue>8</DoubleValue>") == 1


def test_setting_page_edits_roundtrip_scale_factors(monkeypatch, tmp_path):
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication, QDialog

    from dialogs.Dialog_DEWETRON_Setting import Ui_Dialog_DEWETRON_Setting

    monkeypatch.setenv("SOLARAUTOTEST_DEW_SCALE", str(tmp_path / "dew_scale.ini"))
    app = QApplication.instance() or QApplication([])
    assert app is not None
    dialog = QDialog()
    ui = Ui_Dialog_DEWETRON_Setting()
    ui.setupUi(dialog)
    factors = ui.channel_scale_factors()
    assert factors["AI 1/U1"] == "1"
    assert factors["AI 1/l1"] == "1"
    assert len(factors) == 8
    ui.set_channel_scale_factors({"AI 1/I1": "12", "AI 1/U3": "3"})
    again = ui.channel_scale_factors()
    assert again["AI 1/l1"] == "12"
    assert again["AI 1/U3"] == "3"
    assert again["AI 1/U1"] == "1"
    dialog.deleteLater()


def test_scales_worth_applying_skips_all_ones():
    from utils.dewetron_channel_scale import scales_worth_applying

    assert scales_worth_applying({}) == {}
    assert scales_worth_applying({"AI 1/U1": "1", "AI 1/l1": "1.0"}) == {}
    got = scales_worth_applying({"AI 1/U1": "1", "AI 1/l1": "1000"})
    assert got["AI 1/l1"] == "1000"
    assert got["AI 1/U1"] == "1"


def test_saved_dew_scales_roundtrip(monkeypatch, tmp_path):
    from utils.dewetron_channel_scale import load_saved_dew_scales, save_saved_dew_scales

    monkeypatch.setenv("SOLARAUTOTEST_DEW_SCALE", str(tmp_path / "dew_scale.ini"))
    save_saved_dew_scales({"AI 1/l1": "1000", "AI 1/l2": "1000", "AI 1/U1": "1"})
    loaded = load_saved_dew_scales()
    assert loaded["AI 1/l1"] == "1000"
    assert loaded["AI 1/l2"] == "1000"
    assert loaded["AI 1/U1"] == "1"


def test_merge_prefers_saved_over_device_ones(monkeypatch, tmp_path):
    from utils.dewetron_channel_scale import (
        merge_device_and_saved_scales,
        save_saved_dew_scales,
    )

    monkeypatch.setenv("SOLARAUTOTEST_DEW_SCALE", str(tmp_path / "dew_scale.ini"))
    save_saved_dew_scales({"AI 1/l1": "1000", "AI 1/U1": "230"})
    merged = merge_device_and_saved_scales(
        {"AI 1/l1": "1", "AI 1/U1": "1", "AI 1/l2": "5"}
    )
    assert merged["AI 1/l1"] == "1000"
    assert merged["AI 1/U1"] == "230"
    assert merged["AI 1/l2"] == "5"


def test_record_lead_roundtrip_keeps_scales(monkeypatch, tmp_path):
    from utils.dewetron_channel_scale import (
        load_saved_dew_scales,
        load_saved_record_lead_s,
        save_saved_dew_scales,
        save_saved_record_lead_s,
    )

    monkeypatch.setenv("SOLARAUTOTEST_DEW_SCALE", str(tmp_path / "dew_scale.ini"))
    save_saved_dew_scales({"AI 1/l1": "1000"})
    assert save_saved_record_lead_s(30) == 30
    assert load_saved_record_lead_s() == 30
    assert load_saved_dew_scales()["AI 1/l1"] == "1000"
    save_saved_dew_scales({"AI 1/l1": "500"})
    assert load_saved_record_lead_s() == 30
