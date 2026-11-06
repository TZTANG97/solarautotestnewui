# -*- coding: utf-8 -*-
"""防逆流（UNE 217001）交叉冒烟：多 DC 厂家 × 多 WT/录波模式 × 单三相。"""
from __future__ import annotations

import os
import sys

import pytest
from PyQt5.QtWidgets import QApplication, QDialog

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _fake_chroma_iv(vmp, imp, voc, isc, pf, dc_num):
    return "ok", [
        "OUTP:MODE TABLE",
        "IVC:VOLT %s" % vmp,
        "IVC:CURR %s" % imp,
    ]


def _fake_itech_iv(vmp, imp, voc, isc, pf, dc_num):
    return "ok", [
        "SOL 0",
        "SOL:USER VMP %s" % vmp,
        "SOL:USER IMP %s" % imp,
        "SOL 1",
    ]


def _fake_bluesight_iv(vmp, imp, voc, isc, pf, dc_num):
    return "ok", [
        "BLUESIGHT:STC V=%s I=%s VOC=%s ISC=%s PF=%s" % (vmp, imp, voc, isc, pf),
    ]


def _make_ui(qapp, *, phase="三相", wt="WT3000", record="continuous", only_51=True):
    from dialogs.Dialog_thaantibackflow import Ui_Dialog_thaantibackflow
    from utils.wt_recording_mode import mode_to_combo_index

    ui = Ui_Dialog_thaantibackflow()
    dialog = QDialog()
    ui.setupUi(dialog)

    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText(phase)
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("3")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.textEdit_S1_TIME.setPlainText("30")
    ui.comboBox_S1_TIME.setCurrentText("秒")

    for ch in range(1, 5):
        getattr(ui, "checkBox_S1_DC%d" % ch).setChecked(False)
        getattr(ui, "checkBox_S3_DC%d" % ch).setChecked(False)
    ui.checkBox_S1_DC1.setChecked(True)
    ui.comboBox_S1_DC1.setCurrentText("开启")
    ui.textEdit_S1_DC1_VOLT.setPlainText("400")
    ui.textEdit_S1_DC1_CURR.setPlainText("10")
    ui.textEdit_S1_DC1_Voc.setPlainText("450")
    ui.textEdit_S1_DC1_Isc.setPlainText("12")
    ui.textEdit_S1_DC1_PF.setPlainText("100")
    ui.checkBox_S3_DC1.setChecked(True)

    ui.checkBox_S2.setChecked(True)
    wt_map = {
        "WT3000": ui.radioButton_S2_WT3000,
        "WT1800": ui.radioButton_S2_WT1800,
        "WT1806E": ui.radioButton_S2_WT1806E,
        "WT5000": ui.radioButton_S2_WT5000,
    }
    wt_map[wt].setChecked(True)

    ui.checkBox_S3.setChecked(True)
    ui.textEdit_PowerLadder.setPlainText("100,0")
    ui.textEdit_S3_TIME_2.setPlainText("2")
    ui.comboBox_S3_TIME_2.setCurrentText("秒")
    ui.textEdit_OpWait.setPlainText("1")
    ui.comboBox_OpWait.setCurrentText("秒")
    ui.comboBox_S3_record_mode.setCurrentIndex(mode_to_combo_index(record))

    ui.checkBox_S5_1.setChecked(True)
    ui.checkBox_S5_2.setChecked(not only_51)
    ui.checkBox_S5_3.setChecked(not only_51)
    ui.checkBox_S5_4.setChecked(not only_51)

    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")
    ui.checkBox_S_END_DC1.setChecked(True)
    ui.comboBox_S_END_DC1.setCurrentText("关闭")
    return ui, dialog


@pytest.mark.parametrize(
    "brand,resolver,needle",
    [
        ("Chroma", _fake_chroma_iv, "IVC:"),
        ("Itech", _fake_itech_iv, "SOL:USER"),
        ("Bluesight", _fake_bluesight_iv, "BLUESIGHT:STC"),
    ],
)
@pytest.mark.parametrize("wt", ["WT3000", "WT1800", "WT1806E", "WT5000"])
def test_dc_brand_x_wt_continuous(qapp, brand, resolver, needle, wt):
    from utils.antibackflow_commands import build_antibackflow_plan

    ui, _ = _make_ui(qapp, wt=wt, record="continuous", only_51=True)
    plan = build_antibackflow_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1, "textEdit_FileNameList": "AntiBackflow_BR"},
        str_add_flag="0",
        dc_iv_resolver=resolver,
        per_dc_factor={"0": brand},
    )
    assert plan["ok"], plan.get("error")
    assert not plan["dc_errors"], plan["dc_errors"]
    assert plan["wt_type"] == wt
    assert plan["wt_continuous"] is True
    assert plan["file_names"] == ["AntiBackflow_BR"]
    assert plan["wt_rounds"] == 1

    joined = " ".join(
        str(r[2])
        for r in plan["commands"]
        if r and str(r[0]).startswith("DC") and r[1] == "write"
    )
    assert needle.upper() in joined.upper(), joined
    assert any(r and r[0] == "Upper_WT_Config" for r in plan["commands"])


@pytest.mark.parametrize("phase", ["单相", "三相"])
def test_phase_modes(qapp, phase):
    from utils.antibackflow_commands import build_antibackflow_plan

    ui, _ = _make_ui(qapp, phase=phase, only_51=True)
    plan = build_antibackflow_plan(
        ui,
        wt_config_dict={},
        str_add_flag="0",
        dc_iv_resolver=_fake_chroma_iv,
    )
    assert plan["ok"], plan.get("error")
    assert plan["file_names"] == ["AntiBackflow_BR"]


def test_split_record_filenames(qapp):
    from utils.antibackflow_commands import build_antibackflow_plan

    ui, _ = _make_ui(qapp, record="split", only_51=True)
    plan = build_antibackflow_plan(
        ui,
        wt_config_dict={},
        str_add_flag="0",
        dc_iv_resolver=_fake_chroma_iv,
    )
    assert plan["ok"], plan.get("error")
    assert plan["wt_continuous"] is False
    assert len(plan["file_names"]) == 2
    assert all(n.startswith("AntiBF_") for n in plan["file_names"])


def test_full_une_scenarios_have_operator_waits(qapp):
    from utils.antibackflow_commands import build_antibackflow_plan

    ui, _ = _make_ui(qapp, only_51=False)
    plan = build_antibackflow_plan(
        ui,
        wt_config_dict={},
        str_add_flag="0",
        dc_iv_resolver=_fake_chroma_iv,
    )
    assert plan["ok"], plan.get("error")
    assert plan["scenario_count"] >= 20
    # 人工等待：AC query *IDN? 且 slot 有等待
    op_waits = [
        r
        for r in plan["commands"]
        if r and r[0] == "AC" and r[1] == "query" and r[2] == "*IDN?" and r[9]
    ]
    assert len(op_waits) >= 6, len(op_waits)


def test_dewetron_project_registered():
    from dewetron_autotest import ELIGIBLE_PROJECT_NAMES, PROJECT_SPECS

    assert "防逆流测试" in PROJECT_SPECS
    assert "防逆流测试" in ELIGIBLE_PROJECT_NAMES
    assert PROJECT_SPECS["防逆流测试"].test_type == "anti-backflow"


def test_recommended_filenames(qapp):
    from utils.antibackflow_commands import antibackflow_recommended_filenames
    from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT

    ui, _ = _make_ui(qapp, only_51=True)
    assert antibackflow_recommended_filenames(ui, MODE_CONTINUOUS) == ["AntiBackflow_BR"]
    split = antibackflow_recommended_filenames(ui, MODE_SPLIT)
    assert len(split) == 2


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    # 精简直接跑，不依赖 pytest 收集
    for brand, resolver, needle in [
        ("Chroma", _fake_chroma_iv, "IVC:"),
        ("Itech", _fake_itech_iv, "SOL:USER"),
        ("Bluesight", _fake_bluesight_iv, "BLUESIGHT:STC"),
    ]:
        for wt in ["WT3000", "WT1800", "WT1806E", "WT5000"]:
            test_dc_brand_x_wt_continuous(app, brand, resolver, needle, wt)
            print("OK", brand, wt)
    test_phase_modes(app, "单相")
    test_phase_modes(app, "三相")
    test_split_record_filenames(app)
    test_full_une_scenarios_have_operator_waits(app)
    test_dewetron_project_registered()
    test_recommended_filenames(app)
    print("ALL CROSS OK")
