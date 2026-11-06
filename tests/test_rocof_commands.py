# -*- coding: utf-8 -*-
"""ROCOF保护冒烟。"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thairocof import Ui_Dialog_thairocof
from utils.rocof_commands import build_rocof_plan, build_rocof_step_list


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_build_rocof_step_list_rate():
    steps, sweep = build_rocof_step_list("50", "52", 2.0, dt_s=0.05)
    assert steps[0] == "50"
    assert steps[-1] == "52"
    assert abs(sweep - 1.0) < 1e-6
    assert len(steps) > 5


def test_dialog_and_plan(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thairocof()
    ui.setupUi(dialog)
    assert ui.stackedWidget.count() == 4
    assert hasattr(ui, "checkBox_rocof_page")
    assert ui.textEdit_S3_rocof_hz_s_rocof.toPlainText() == "2"

    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("单相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("1")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.textEdit_S1_TIME.setPlainText("1")
    ui.comboBox_S1_TIME.setCurrentText("秒")
    for ch in range(1, 5):
        getattr(ui, "checkBox_S1_DC%d" % ch).setChecked(False)

    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    ui.checkBox_S2_update_rate.setChecked(True)
    ui.textEdit_S2_update_rate.setPlainText("50")
    ui.comboBox_S2_update_rate.setCurrentText("毫秒")

    # 只开一条 +2Hz/s
    for sn in range(3, 9):
        getattr(ui, "checkBox_S%d" % sn).setChecked(False)
    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S_End.setChecked(False)

    plan = build_rocof_plan(ui, wt_config_dict={"k": 1})
    assert plan["ok"] is True
    assert plan["file_names"] == ["ROCOF_protect"]
    assert plan["wt_continuous"] is True
    freqs = [r[2] for r in plan["commands"] if str(r[2]).startswith("FREQ")]
    assert "FREQ 50" in freqs
    assert "FREQ 52" in freqs
    assert len(freqs) > 3
    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1
    dialog.close()
