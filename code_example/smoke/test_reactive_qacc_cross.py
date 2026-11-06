# -*- coding: utf-8 -*-
"""无功精度交叉冒烟：三相 Chroma + 连续录/分开录 + 文件名链路。"""
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


def _fill_chroma_profile(
    ui,
    *,
    record_mode="continuous",
    power="100",
    q="-50,0,50",
    dwell="1",
    unit="分钟",
):
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("5")
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
    ui.radioButton_S2_WT1806E.setChecked(True)

    ui.checkBox_S3.setChecked(True)
    ui.textEdit_PowerLadder.setPlainText(power)
    ui.textEdit_QLadder.setPlainText(q)
    ui.textEdit_S3_TIME_2.setPlainText(dwell)
    ui.comboBox_S3_TIME_2.setCurrentText(unit)
    from utils.wt_recording_mode import mode_to_combo_index

    ui.comboBox_S3_record_mode.setCurrentIndex(mode_to_combo_index(record_mode))

    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")
    ui.checkBox_S_END_DC1.setChecked(True)
    ui.comboBox_S_END_DC1.setCurrentText("关闭")


def test_cross_three_phase_continuous_async(qapp):
    from dialogs.Dialog_thaireactiveQacc import Ui_Dialog_thaireactiveQacc
    from utils.reactive_qacc_commands import build_reactive_qacc_plan

    ui = Ui_Dialog_thaireactiveQacc()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_chroma_profile(ui, record_mode="continuous", power="100", q="-50,0,50")

    plan = build_reactive_qacc_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1, "textEdit_FileNameList": "Qacc_BR"},
        str_add_flag="0",
    )
    assert plan["ok"], plan.get("error")
    assert not plan["dc_errors"]
    assert plan["power_levels"] == [100.0]
    assert plan["q_setpoints"] == [-50.0, 0.0, 50.0]
    assert plan["wt_continuous"] is True
    assert plan["wt_rounds"] == 1
    assert plan["file_names"] == ["Qacc_BR"]
    assert plan["wt_type"] == "WT1806E"

    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1
    assert sum(1 for m in markers if m.isdigit()) == 0

    slot9 = [
        int(r[9])
        for r in plan["commands"]
        if len(r) > 9 and str(r[9]).strip().lstrip("-").isdigit()
    ]
    assert len(slot9) >= 3
    assert all(v == 600 for v in slot9[-3:])


def test_cross_split_mode_numeric_col6(qapp):
    from dialogs.Dialog_thaireactiveQacc import Ui_Dialog_thaireactiveQacc
    from utils.reactive_qacc_commands import build_reactive_qacc_plan

    ui = Ui_Dialog_thaireactiveQacc()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_chroma_profile(ui, record_mode="split", power="100", q="-50,0", dwell="30", unit="秒")

    plan = build_reactive_qacc_plan(ui, wt_config_dict={"mock": 1}, str_add_flag="0")
    assert plan["ok"], plan.get("error")
    assert plan["wt_continuous"] is False
    assert plan["wt_rounds"] == 2
    assert plan["file_names"] == ["Qacc_P100_Qm50", "Qacc_P100_Q0"]

    col6 = [
        int(r[6])
        for r in plan["commands"]
        if len(r) > 6 and str(r[6]).strip().lstrip("-").isdigit()
    ]
    assert len(col6) == 2
    assert all(v == 300 for v in col6)


def test_cross_default_ui_ladder_and_filenames(qapp):
    from dialogs.Dialog_thaireactiveQacc import Ui_Dialog_thaireactiveQacc
    from utils.reactive_qacc_commands import build_reactive_qacc_plan
    from utils.wt_recording_mode import reactive_qacc_recommended_filenames, combo_index_to_mode

    ui = Ui_Dialog_thaireactiveQacc()
    dialog = QDialog()
    ui.setupUi(dialog)

    assert hasattr(ui, "comboBox_S3_record_mode")
    assert ui.textEdit_PowerLadder.toPlainText().strip() == "100"
    assert "-75" in ui.textEdit_QLadder.toPlainText()

    mode = combo_index_to_mode(ui.comboBox_S3_record_mode.currentIndex())
    powers = [100.0]
    q_points = [-100.0, -75.0, -50.0, -25.0, 0.0, 25.0, 50.0, 75.0, 100.0]
    if mode == "continuous":
        assert reactive_qacc_recommended_filenames(powers, q_points, mode) == ["Qacc_BR"]
    else:
        names = reactive_qacc_recommended_filenames(powers, q_points, mode)
        assert len(names) == 9
        assert names[0] == "Qacc_P100_Qm100"
        assert names[-1] == "Qacc_P100_Q100"

    ui.checkBox_S2.setChecked(False)
    ui.checkBox_S_END.setChecked(False)
    plan = build_reactive_qacc_plan(ui, wt_config_dict={}, str_add_flag="0")
    assert plan["ok"]
    assert plan["power_levels"] == [100.0]
    assert len(plan["q_setpoints"]) == 9


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
