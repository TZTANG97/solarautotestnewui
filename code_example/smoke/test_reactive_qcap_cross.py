# -*- coding: utf-8 -*-
"""无功能力范围交叉冒烟：三相 Chroma + 连续录/分开录 + DC 按 P 缩放 + 文件名链路。"""
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


def _fill_chroma_profile(ui, *, record_mode="continuous", ladder="10,50,100", dwell="1", unit="分钟"):
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
    ui.textEdit_PowerLadder.setPlainText(ladder)
    ui.textEdit_S3_TIME_2.setPlainText(dwell)
    ui.comboBox_S3_TIME_2.setCurrentText(unit)
    from utils.wt_recording_mode import mode_to_combo_index

    ui.comboBox_S3_record_mode.setCurrentIndex(mode_to_combo_index(record_mode))
    ui.checkBox_cos_pos09.setChecked(True)
    ui.checkBox_cos_neg09.setChecked(True)
    ui.checkBox_cos_1.setChecked(False)

    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")
    ui.checkBox_S_END_DC1.setChecked(True)
    ui.comboBox_S_END_DC1.setCurrentText("关闭")


def test_cross_three_phase_continuous_async(qapp):
    from dialogs.Dialog_thaireactiveQcap import Ui_Dialog_thaireactiveQcap
    from utils.reactive_qcap_commands import build_reactive_qcap_plan

    ui = Ui_Dialog_thaireactiveQcap()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_chroma_profile(ui, record_mode="continuous", ladder="10,50,100", dwell="1", unit="分钟")

    plan = build_reactive_qcap_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1, "textEdit_FileNameList": "QCap_BR"},
        str_add_flag="0",
    )
    assert plan["ok"], plan.get("error")
    assert not plan["dc_errors"]
    assert plan["power_levels"] == [10.0, 50.0, 100.0]
    assert plan["cos_labels"] == ["cos0.9", "cos-0.9"]
    assert plan["wt_continuous"] is True
    assert plan["wt_rounds"] == 1
    assert plan["file_names"] == ["QCap_BR"]
    assert plan["wt_type"] == "WT1806E"

    writes = [str(r[2]) for r in plan["commands"] if r[0] == "AC" and r[1] == "write"]
    assert "INST:PHAS THREE" in writes
    assert "INST:EDIT EACH" in writes
    assert "OUTP ON" in writes

    dc_writes = [str(r[2]) for r in plan["commands"] if r[0] == "DC1" and r[1] == "write"]
    assert any("IVC:IT" in w for w in dc_writes)
    # step1 启机 + step3 首点各写一次 MODE TABLE；后续 P 档只缩放 IVC
    assert dc_writes.count("OUTP:MODE TABLE") >= 1
    ivc_it = [w for w in dc_writes if w.startswith("IVC:IT")]
    assert len(ivc_it) >= 3  # 10% / 50% / 100% 三档 Imp 缩放

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
    assert len(slot9) >= 6  # 3 power × 2 cos
    assert all(v == 600 for v in slot9[-6:])  # 1 min → 600 × 0.1s

    assert ("AC", "write", "OUTP OFF") in [(r[0], r[1], r[2]) for r in plan["commands"]]


def test_cross_split_mode_numeric_col6(qapp):
    from dialogs.Dialog_thaireactiveQcap import Ui_Dialog_thaireactiveQcap
    from utils.reactive_qcap_commands import build_reactive_qcap_plan

    ui = Ui_Dialog_thaireactiveQcap()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_chroma_profile(ui, record_mode="split", ladder="20,40", dwell="30", unit="秒")

    plan = build_reactive_qcap_plan(ui, wt_config_dict={"mock": 1}, str_add_flag="0")
    assert plan["ok"], plan.get("error")
    assert plan["wt_continuous"] is False
    assert plan["wt_rounds"] == 4
    assert plan["file_names"] == [
        "QCap_P20_cos0.9",
        "QCap_P20_cos-0.9",
        "QCap_P40_cos0.9",
        "QCap_P40_cos-0.9",
    ]

    col6 = [
        int(r[6])
        for r in plan["commands"]
        if len(r) > 6 and str(r[6]).strip().lstrip("-").isdigit()
    ]
    assert len(col6) == 4
    assert all(v == 300 for v in col6)  # 30s

    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert "ASYNC_START" not in markers
    assert "WAIT_END" not in markers


def test_cross_default_ui_ladder_and_filenames(qapp):
    from dialogs.Dialog_thaireactiveQcap import Ui_Dialog_thaireactiveQcap
    from utils.reactive_qcap_commands import build_reactive_qcap_plan
    from utils.wt_recording_mode import qcap_recommended_filenames, combo_index_to_mode

    ui = Ui_Dialog_thaireactiveQcap()
    dialog = QDialog()
    ui.setupUi(dialog)

    ladder = ui.textEdit_PowerLadder.toPlainText()
    assert "10" in ladder and "100" in ladder
    assert ui.checkBox_cos_pos09.isChecked()
    assert ui.checkBox_cos_neg09.isChecked()
    assert ui.comboBox_S3_TIME_2.currentText() == "分钟"

    mode = combo_index_to_mode(ui.comboBox_S3_record_mode.currentIndex())
    powers = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    cos_labels = ["cos0.9", "cos-0.9"]
    if mode == "continuous":
        assert qcap_recommended_filenames(powers, cos_labels, mode) == ["QCap_BR"]
    else:
        names = qcap_recommended_filenames(powers, cos_labels, mode)
        assert len(names) == 20
        assert names[0] == "QCap_P10_cos0.9"
        assert names[-1] == "QCap_P100_cos-0.9"

    ui.checkBox_S2.setChecked(False)
    ui.checkBox_S_END.setChecked(False)
    plan = build_reactive_qcap_plan(ui, wt_config_dict={}, str_add_flag="0")
    assert plan["ok"]
    assert len(plan["power_levels"]) == 10


def test_cross_dc_empty_iv_no_crash(qapp):
    """IV 参数留空时 plan 仍生成，但 dc_errors 提示（Send 层会拦截不下发）。"""
    from dialogs.Dialog_thaireactiveQcap import Ui_Dialog_thaireactiveQcap
    from utils.reactive_qcap_commands import build_reactive_qcap_plan

    ui = Ui_Dialog_thaireactiveQcap()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_chroma_profile(ui, record_mode="continuous", ladder="50", dwell="10", unit="秒")
    ui.textEdit_S1_DC1_VOLT.setPlainText("")
    ui.textEdit_S1_DC1_CURR.setPlainText("")
    ui.textEdit_S1_DC1_Voc.setPlainText("")
    ui.textEdit_S1_DC1_Isc.setPlainText("")

    plan = build_reactive_qcap_plan(ui, wt_config_dict={}, str_add_flag="0")
    assert plan["ok"]
    assert plan["dc_errors"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
