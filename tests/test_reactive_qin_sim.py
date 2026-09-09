# -*- coding: utf-8 -*-
"""无功注入离屏模拟。"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from Dialog_thaireactiveQin import Ui_Dialog_thaireactiveQin
from utils.reactive_qin_commands import build_reactive_qin_plan

MAIN_PATH = Path(__file__).resolve().parents[1] / "SCPITestWave.py"


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def qin_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaireactiveQin()
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
    ui.textEdit_PowerLadder.setPlainText("20,50")
    ui.textEdit_QLadder.setPlainText("-100,100")
    ui.textEdit_S3_TIME_2.setPlainText("3")
    ui.comboBox_S3_TIME_2.setCurrentText("秒")
    from utils.wt_recording_mode import mode_to_combo_index

    ui.comboBox_S3_record_mode.setCurrentIndex(mode_to_combo_index("split"))
    ui.checkBox_S3_DC1.setChecked(True)
    for ch in range(2, 5):
        getattr(ui, "checkBox_S3_DC%d" % ch).setChecked(False)
    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")


def test_dialog_defaults(qin_ui):
    ui, _ = qin_ui
    assert ui.stackedWidget.count() == 4
    assert "20" in ui.textEdit_PowerLadder.toPlainText()
    assert ui.textEdit_QLadder.toPlainText().replace(" ", "") == "-100,-50,50,100"
    assert hasattr(ui, "comboBox_S3_record_mode")
    assert hasattr(ui, "analyzerModeSection")


def test_qin_plan_filenames(qin_ui):
    ui, _ = qin_ui
    _fill(ui)
    plan = build_reactive_qin_plan(ui, wt_config_dict={}, str_add_flag="0")
    assert plan["ok"]
    assert plan["file_names"] == [
        "Qin_P20_Qm100",
        "Qin_P20_Q100",
        "Qin_P50_Qm100",
        "Qin_P50_Q100",
    ]
    assert plan["wt_rounds"] == 4


def test_main_wiring():
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "thaireactiveQinAppend" in src
    assert "thaireactiveQinSend" in src
    assert "无功注入" in src
    assert "('功率与无功', '无功注入', '无功注入')" in src
