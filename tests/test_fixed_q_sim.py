# -*- coding: utf-8 -*-
"""定无功离屏模拟：Dialog + 命令计划 + Open/Save + 主程序接线。"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from Dialog_thaifixedQ import Ui_Dialog_thaifixedQ
from utils.fixed_q_commands import build_fixed_q_plan
from utils.Open_Save_ThaiFixedQ import FILE_TAG, HEADERS, _apply_csv_value, _widget_to_csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = PROJECT_ROOT / "SCPITestWave.py"


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def fixedq_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaifixedQ()
    ui.setupUi(dialog)
    yield ui, dialog
    dialog.close()
    dialog.deleteLater()


def _fill_step1_single(ui):
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


def _fill_ladder(ui, power="50,100", q="-50,0,50", dwell="3", unit="秒"):
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_PowerLadder.setPlainText(power)
    ui.textEdit_QLadder.setPlainText(q)
    ui.textEdit_S3_TIME_2.setPlainText(dwell)
    ui.comboBox_S3_TIME_2.setCurrentText(unit)
    ui.checkBox_S3_DC1.setChecked(True)
    for ch in range(2, 5):
        getattr(ui, "checkBox_S3_DC%d" % ch).setChecked(False)


def test_dialog_defaults(fixedq_ui):
    ui, _ = fixedq_ui
    assert ui.stackedWidget.count() == 4
    assert ui._wtStacked.count() == 4
    assert "50" in ui.textEdit_PowerLadder.toPlainText()
    assert "-100" in ui.textEdit_QLadder.toPlainText()
    assert hasattr(ui, "analyzerModeSection")


def test_power_times_q_numeric_col6(fixedq_ui):
    ui, _ = fixedq_ui
    _fill_step1_single(ui)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _fill_ladder(ui)
    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")

    plan = build_fixed_q_plan(ui, wt_config_dict={"k": 1}, str_add_flag="0")
    assert plan["ok"]
    assert plan["file_names"] == [
        "Qset_P50_Qm50",
        "Qset_P50_Q0",
        "Qset_P50_Q50",
        "Qset_P100_Qm50",
        "Qset_P100_Q0",
        "Qset_P100_Q50",
    ]
    assert plan["wt_rounds"] == 6
    col6 = [r for r in plan["commands"] if r and r[1] == "query" and r[6] not in ("", None)]
    assert len(col6) == 6


def test_empty_q_ladder_errors(fixedq_ui):
    ui, _ = fixedq_ui
    _fill_step1_single(ui)
    _fill_ladder(ui, q="")
    plan = build_fixed_q_plan(ui, str_add_flag="0")
    assert not plan["ok"]
    assert "Q 设定点" in plan["error"]


def test_csv_roundtrip_fields(fixedq_ui, tmp_path):
    ui, _ = fixedq_ui
    ui.textEdit_QLadder.setPlainText("-25,0,25")
    values = [FILE_TAG]
    for name in HEADERS[1:]:
        if name.startswith("checkBox_S2_WT"):
            values.append("1" if name.endswith("3000") else "0")
        else:
            values.append(_widget_to_csv(ui, name))
    assert values[HEADERS.index("textEdit_QLadder")] == "-25,0,25"
    ui2_dialog = QtWidgets.QDialog()
    ui2 = Ui_Dialog_thaifixedQ()
    ui2.setupUi(ui2_dialog)
    for name, val in zip(HEADERS, values):
        if name == "Style":
            continue
        if name.startswith("checkBox_S2_WT") and val == "1":
            ui2.radioButton_S2_WT3000.setChecked(True)
        else:
            _apply_csv_value(ui2, name, val)
    assert ui2.textEdit_QLadder.toPlainText() == "-25,0,25"
    ui2_dialog.deleteLater()


def test_main_wiring_mentions_fixedq():
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "thaifixedQAppend" in src
    assert "thaifixedQSend" in src
    assert "定无功" in src
    assert "fixedQ_append_count" in src
    assert "OpenFileDialogThaiFixedQ" in src
    assert "('功率与无功', '定无功', '定无功')" in src
