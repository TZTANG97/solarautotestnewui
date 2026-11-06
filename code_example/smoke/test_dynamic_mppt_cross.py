# -*- coding: utf-8 -*-
"""动态 MPPT：SoftPanel 全带宽语义交叉冒烟。"""
from __future__ import annotations

import os
import sys

import pytest
from PyQt5.QtWidgets import QApplication, QDialog

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

CHROMA_IV = [
    "OUTP:MODE TABLE",
    "IVC:IT 1,2,3,4,5,6",
    "IVC:VT 7,8,9,10,11,12",
    "IVCurve:SELect 1",
]


def _fake_chroma_iv(*_args, **_kwargs):
    return list(CHROMA_IV)


def _fake_itech_iv(vmp, imp, voc, isc, *_args, **_kwargs):
    return [
        "SOL:USER:VOC %s" % voc,
        "SOL:USER:IMP %s" % imp,
        "SOL:USER:VMP %s" % vmp,
        "SOL:USER:ISC %s" % isc,
    ]


def _fake_bluesight_iv(vmp, imp, *_args, **_kwargs):
    return ["BLUESIGHT:STC %s %s 0.8" % (float(vmp) * float(imp), vmp)]


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _fill_common(ui, *, dc2: bool = False):
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    for ch in range(1, 5):
        getattr(ui, "checkBox_S1_DC%d" % ch).setChecked(False)
        getattr(ui, "checkBox_S3_DC%d" % ch).setChecked(False)
    ui.checkBox_S1_DC1.setChecked(True)
    ui.comboBox_S1_DC1.setCurrentText("开启")
    ui.textEdit_S1_DC1_VOLT.setPlainText("650")
    ui.textEdit_S1_DC1_CURR.setPlainText("12")
    ui.textEdit_S1_DC1_Voc.setPlainText("720")
    ui.textEdit_S1_DC1_Isc.setPlainText("13")
    ui.textEdit_S1_DC1_PF.setPlainText("100")
    if dc2:
        ui.checkBox_S1_DC2.setChecked(True)
        ui.comboBox_S1_DC2.setCurrentText("开启")
        ui.textEdit_S1_DC2_VOLT.setPlainText("650")
        ui.textEdit_S1_DC2_CURR.setPlainText("12")
        ui.textEdit_S1_DC2_Voc.setPlainText("720")
        ui.textEdit_S1_DC2_Isc.setPlainText("13")
        ui.textEdit_S1_DC2_PF.setPlainText("100")
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT1806E.setChecked(True)
    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S3_DC1.setChecked(True)
    if dc2:
        ui.checkBox_S3_DC2.setChecked(True)
    ui.checkBox_S_End.setChecked(False)


def _short_bundle(**overrides):
    """Slope=700 → Ramp=1s on 300–1000 band; SoftPanel full-band path."""
    base = {
        "active_tab": "30_100",
        "stc": {
            "initial_setup_s": 1,
            "vmp": 100,
            "pmpp": 600,
            "ff": 0.8,
            "ff_label": "c-Si",
            "irr_stc_wm2": 1000,
        },
        "tabs": {
            "10_50": [],
            "30_100": [
                {
                    "enabled": True,
                    "repetitions": 1,
                    "slope_wm2_s": 700,
                    "dwell_up_s": 1,
                    "dwell_dn_s": 1,
                }
            ],
            "startup_shutdown": [],
        },
        "wt_filename": "DynamicMPPT_BR",
    }
    base.update(overrides)
    return base


def _make_ui(qapp, bundle=None, **fill_kw):
    from dialogs.Dialog_thaidynamicmppt import Ui_Dialog_thaidynamicmppt

    ui = Ui_Dialog_thaidynamicmppt()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_common(ui, **fill_kw)
    ui.en50530Panel.set_bundle_dict(bundle or _short_bundle())
    return ui, dialog


def test_softpanel_full_band_dn_then_up(qapp):
    from utils.en50530_dynamic_mppt import build_en50530_command_rows, validate_en50530_bundle

    bundle = validate_en50530_bundle(_short_bundle())
    irrs = []

    def iv(_ch, irr):
        irrs.append(float(irr))
        return ["IV"]

    build_en50530_command_rows(bundle, channels=[1], iv_for_channel_irr=iv)
    assert irrs[0] == pytest.approx(1000.0)
    assert min(irrs) == pytest.approx(300.0)
    assert max(irrs) == pytest.approx(1000.0)
    after = [v for v in irrs[1:] if abs(v - 1000.0) > 1e-6]
    assert after and after[0] < 1000.0


def test_cross_en50530_scpi_plan(qapp):
    from utils.dynamic_mppt_plan import build_dynamic_mppt_plan

    ui, _ = _make_ui(qapp)
    plan = build_dynamic_mppt_plan(
        ui,
        get_iv_fn=_fake_chroma_iv,
        per_dc_factor={"0": "Chroma"},
        command_list_dc={"Chroma": ["OUTP:MODE TABLE", "IVCurve:SELect 1"]},
        str_add_flag="0",
    )
    assert plan["ok"], plan.get("error")
    assert plan["band_duration_01s"] >= 50
    metas = plan.get("profile_metas") or []
    assert any(m.get("name") == "InitialSetup" for m in metas)
    assert any(m.get("irr_min") == 300.0 and m.get("irr_max") == 1000.0 for m in metas)
    assert float(ui.textEdit_S1_DC1_VOLT.toPlainText()) == pytest.approx(100.0)


def test_slope_change_resyncs_ramp(qapp):
    ui, _ = _make_ui(qapp)
    table = ui.en50530Panel._tables["30_100"]
    table.item(0, 2).setText("10")
    assert float(table.item(0, 3).text()) == pytest.approx(70.0)


def test_duration_from_softpanel_ramp(qapp):
    ui, _ = _make_ui(qapp)
    table = ui.en50530Panel._tables["30_100"]
    assert float(table.item(0, 3).text()) == pytest.approx(1.0)
    assert table.item(0, 7).text() == "4"


@pytest.mark.parametrize(
    "brand,get_iv,modes,needle",
    [
        ("Chroma", _fake_chroma_iv, {"Chroma": ["OUTP:MODE TABLE"]}, "IVC:"),
        ("Itech", _fake_itech_iv, {"Itech": ["SOL 0", "SOL 1"]}, "SOL:USER"),
        ("Bluesight", _fake_bluesight_iv, {"Bluesight": []}, "BLUESIGHT:STC"),
    ],
)
def test_brand_scpi_commands(qapp, brand, get_iv, modes, needle):
    from utils.dynamic_mppt_plan import build_dynamic_mppt_plan

    ui, _ = _make_ui(qapp)
    plan = build_dynamic_mppt_plan(
        ui,
        get_iv_fn=get_iv,
        per_dc_factor={"0": brand},
        command_list_dc=modes,
        str_add_flag="0",
    )
    assert plan["ok"], plan.get("error")
    joined = " ".join(
        str(r[2]) for r in plan["commands"] if r and str(r[0]).startswith("DC") and r[1] == "write"
    )
    assert needle.upper() in joined.upper()


def test_send_stoptime(qapp):
    from utils.dynamic_mppt_plan import build_dynamic_mppt_plan
    from utils.Open_Save_ThaiDynamicMPPT import apply_send_wt_metadata

    ui, _ = _make_ui(qapp)
    plan = build_dynamic_mppt_plan(
        ui,
        get_iv_fn=_fake_chroma_iv,
        per_dc_factor={"0": "Chroma"},
        command_list_dc={"Chroma": ["OUTP:MODE TABLE"]},
        wt_config_dict={"textEdit_FileNameList": "", "textEdit_StopTime": "00:00:10"},
        str_add_flag="0",
    )
    assert plan["ok"]
    assert apply_send_wt_metadata(plan) == "00:02:00"


def test_settings_csv_roundtrip(qapp, tmp_path):
    from utils.Open_Save_ThaiDynamicMPPT import load_settings_from_path, save_settings_to_path

    ui, _ = _make_ui(qapp)
    ui.en50530Panel.set_bundle_dict(
        _short_bundle(
            stc={
                "initial_setup_s": 12,
                "vmp": 88,
                "pmpp": 500,
                "ff": 0.75,
                "ff_label": "a-Si",
                "irr_stc_wm2": 1000,
            },
            wt_filename="DynMPPT_Roundtrip",
        )
    )
    path = tmp_path / "dynamic_mppt_settings.csv"
    save_settings_to_path(ui, path)
    ui.en50530Panel.set_bundle_dict(_short_bundle())
    load_settings_from_path(ui, path)
    b = ui.en50530Panel.get_bundle_dict()
    assert float(b["stc"]["vmp"]) == pytest.approx(88.0)
    assert b["wt_filename"] == "DynMPPT_Roundtrip"


def test_default_softpanel_preset(qapp):
    from dialogs.Dialog_thaidynamicmppt import Ui_Dialog_thaidynamicmppt
    from utils.en50530_dynamic_mppt import estimate_en50530_total_duration_s, validate_en50530_bundle

    ui = Ui_Dialog_thaidynamicmppt()
    dialog = QDialog()
    ui.setupUi(dialog)
    bundle = validate_en50530_bundle(ui.en50530Panel.get_bundle_dict())
    rows = bundle.enabled_rows_for_active_tab()
    assert [r["slope_wm2_s"] for r in rows] == [10, 14, 20, 30, 50, 100]
    assert rows[0]["ramp_up_s"] == pytest.approx(70.0)
    assert estimate_en50530_total_duration_s(bundle) > 3600


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
