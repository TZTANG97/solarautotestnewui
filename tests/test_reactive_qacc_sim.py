# -*- coding: utf-8 -*-
"""无功精度离屏模拟。"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thaireactiveQacc import Ui_Dialog_thaireactiveQacc
from utils.reactive_qacc_commands import build_reactive_qacc_plan

MAIN_PATH = Path(__file__).resolve().parents[1] / "SCPITestWave.py"


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def qacc_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaireactiveQacc()
    ui.setupUi(dialog)
    yield ui, dialog
    dialog.close()
    dialog.deleteLater()


def _fill(ui):
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("单相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("1")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.textEdit_S1_TIME.setPlainText("2")
    ui.comboBox_S1_TIME.setCurrentText("秒")
    for ch in range(1, 5):
        getattr(ui, "checkBox_S1_DC%d" % ch).setChecked(False)
    ui.checkBox_S1_DC1.setChecked(True)
    ui.comboBox_S1_DC1.setCurrentText("开启")
    ui.textEdit_S1_DC1_VOLT.setPlainText("400")
    ui.textEdit_S1_DC1_CURR.setPlainText("10")
    ui.textEdit_S1_DC1_Voc.setPlainText("450")
    ui.textEdit_S1_DC1_Isc.setPlainText("12")
    ui.textEdit_S1_DC1_PF.setPlainText("100")
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_PowerLadder.setPlainText("100")
    ui.textEdit_QLadder.setPlainText("-50,0,50")
    ui.textEdit_S3_TIME_2.setPlainText("3")
    ui.comboBox_S3_TIME_2.setCurrentText("秒")
    from utils.wt_recording_mode import mode_to_combo_index

    ui.comboBox_S3_record_mode.setCurrentIndex(mode_to_combo_index("split"))
    ui.checkBox_S3_DC1.setChecked(True)
    for ch in range(2, 5):
        getattr(ui, "checkBox_S3_DC%d" % ch).setChecked(False)
    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")


def test_dialog_defaults(qacc_ui):
    ui, _ = qacc_ui
    assert ui.stackedWidget.count() == 4
    assert ui.textEdit_PowerLadder.toPlainText().strip() == "100"
    assert "-75" in ui.textEdit_QLadder.toPlainText()
    assert hasattr(ui, "analyzerModeSection")


def test_qacc_plan_filenames(qacc_ui):
    ui, _ = qacc_ui
    _fill(ui)
    plan = build_reactive_qacc_plan(ui, wt_config_dict={}, str_add_flag="0")
    assert plan["ok"]
    assert plan["file_names"] == [
        "Qacc_P100_Qm50",
        "Qacc_P100_Q0",
        "Qacc_P100_Q50",
    ]
    assert plan["wt_rounds"] == 3


def test_main_wiring():
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "thaireactiveQaccAppend" in src
    assert "thaireactiveQaccSend" in src
    assert "无功精度" in src
    assert "('功率与无功', '无功精度', '无功精度')" in src
