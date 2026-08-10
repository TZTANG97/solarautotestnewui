# -*- coding: utf-8 -*-
"""快速电压变化冒烟。"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from Dialog_thairapidvolt import Ui_Dialog_thairapidvolt
from utils.rapid_volt_commands import build_rapid_volt_plan


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_dialog_and_plan(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thairapidvolt()
    ui.setupUi(dialog)
    assert ui.stackedWidget.count() == 4
    assert hasattr(ui, "checkBox_rapidvolt_page")
    assert ui.textEdit_S3_volt_start_rvc.toPlainText() == "230"
    assert ui.textEdit_S3_volt_end_rvc.toPlainText() == "207"

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

    for sn in range(3, 9):
        getattr(ui, "checkBox_S%d" % sn).setChecked(False)
    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S_End.setChecked(False)

    plan = build_rapid_volt_plan(ui, wt_config_dict={"k": 1})
    assert plan["ok"] is True, plan.get("error")
    assert plan["file_names"] == ["RapidVolt_change"]
    assert plan["wt_continuous"] is True
    volts = [r[2] for r in plan["commands"] if str(r[2]).startswith("VOLT")]
    assert "VOLT 230" in volts
    assert "VOLT 207" in volts
    # 阶跃后回起点 → 至少两次 230
    assert volts.count("VOLT 230") >= 2
    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1
    dialog.close()
