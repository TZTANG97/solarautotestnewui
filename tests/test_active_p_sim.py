# -*- coding: utf-8 -*-
"""有功调度离屏模拟。"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thaiactiveP import Ui_Dialog_thaiactiveP
from utils.active_p_commands import build_active_p_plan, default_dc_iv_resolver

MAIN_PATH = Path(__file__).resolve().parents[1] / "SCPITestWave.py"


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def activep_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaiactiveP()
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
    ui.textEdit_PowerLadder.setPlainText("100,50,0")
    ui.textEdit_DcPowerPct.setPlainText("100")
    ui.textEdit_S3_TIME_2.setPlainText("3")
    ui.comboBox_S3_TIME_2.setCurrentText("秒")
    from utils.wt_recording_mode import mode_to_combo_index

    ui.comboBox_S3_record_mode.setCurrentIndex(mode_to_combo_index("split"))
    ui.checkBox_S3_DC1.setChecked(True)
    for ch in range(2, 5):
        getattr(ui, "checkBox_S3_DC%d" % ch).setChecked(False)
    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")


def test_dialog_defaults(activep_ui):
    ui, _ = activep_ui
    assert ui.stackedWidget.count() == 4
    assert "100,80" in ui.textEdit_PowerLadder.toPlainText()
    assert ui.textEdit_DcPowerPct.toPlainText().strip() == "100"
    assert hasattr(ui, "analyzerModeSection")


def test_active_p_plan_filenames(activep_ui):
    ui, _ = activep_ui
    _fill(ui)
    plan = build_active_p_plan(ui, wt_config_dict={}, str_add_flag="0")
    assert plan["ok"]
    assert plan["dc_pct"] == 100.0
    assert plan["file_names"] == ["Pdisp_P100", "Pdisp_P50", "Pdisp_P0"]
    assert plan["wt_rounds"] == 3


def test_each_p_step_rewrites_dc_and_reselects(activep_ui):
    ui, _ = activep_ui
    _fill(ui)
    ui.textEdit_PowerLadder.setPlainText("100,50,0")
    ui.textEdit_DcPowerPct.setPlainText("100")
    ui.checkBox_S_END.setChecked(False)
    plan = build_active_p_plan(
        ui,
        wt_config_dict={},
        str_add_flag="0",
        dc_iv_resolver=default_dc_iv_resolver,
    )
    assert plan["ok"]
    assert plan["dc_errors"] == []
    dc_writes = [str(r[2]) for r in plan["commands"] if r[0] == "DC1" and r[1] == "write"]
    selects = [w for w in dc_writes if "SELect" in w]
    its = [w for w in dc_writes if w.startswith("IVC:IT")]
    # 启机 100% + 阶梯 100% + 50%；0% 不生成曲线
    assert len(selects) == 3
    assert len(its) == 3
    assert "10.000" in its[1] and "12.000" in its[1]
    assert "5.000" in its[2] and "6.000" in its[2]
    assert dc_writes[-1] == "OUTP OFF"


def test_headroom_scales_each_step(activep_ui):
    ui, _ = activep_ui
    _fill(ui)
    ui.textEdit_PowerLadder.setPlainText("100,50")
    ui.textEdit_DcPowerPct.setPlainText("80")
    ui.checkBox_S_END.setChecked(False)
    plan = build_active_p_plan(
        ui,
        wt_config_dict={},
        str_add_flag="0",
        dc_iv_resolver=default_dc_iv_resolver,
    )
    its = [
        str(r[2])
        for r in plan["commands"]
        if r[0] == "DC1" and str(r[2]).startswith("IVC:IT")
    ]
    # 阶梯第二档 50% × 头寸 80% = 40%
    assert "4.000" in its[-1] and "4.800" in its[-1]


def test_main_wiring():
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "thaiactivePAppend" in src
    assert "thaiactivePSend" in src
    assert "有功调度" in src
    assert "('功率与无功', '有功调度', '有功调度')" in src
