# -*- coding: utf-8 -*-
"""ROCOF 保护（巴西）软件交叉冒烟：扫频 df/dt + 连续录 ASYNC/WAIT_END。"""
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


def _fill_rocof_profile(ui, *, with_end=False):
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

    for sn in range(3, 12):
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is not None:
            cb.setChecked(False)
    for sn in range(12, 21):
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is not None:
            cb.setChecked(False)
    ui.checkBox_rocof_page.setChecked(True)
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_S3_freq_start_rocof.setPlainText("50")
    ui.textEdit_S3_freq_end_rocof.setPlainText("52")
    ui.textEdit_S3_rocof_hz_s_rocof.setPlainText("2")

    ui.checkBox_S_End.setChecked(bool(with_end))
    if with_end:
        ui.comboBox_S_End_AC.setCurrentText("关闭")


def test_rocof_cross_rate_sweep_continuous(qapp):
    from Dialog_thairocof import Ui_Dialog_thairocof
    from utils.rocof_commands import build_rocof_plan

    ui = Ui_Dialog_thairocof()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_rocof_profile(ui, with_end=False)

    plan = build_rocof_plan(ui, wt_config_dict={"comboBox_AutoSave": 1})
    assert plan["ok"], plan.get("error")
    assert not plan["dc_errors"]
    assert plan["wt_continuous"] is True
    assert plan["wt_rounds"] == 1
    assert plan["file_names"] == ["ROCOF_protect"]

    freqs = [str(r[2]) for r in plan["commands"] if str(r[2]).startswith("FREQ")]
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

    band_01 = int(plan.get("band_duration_01s") or 0)
    assert band_01 >= 10  # 1s 扫频 + 保持


def test_rocof_step_list_matches_rate(qapp):
    from utils.rocof_commands import build_rocof_step_list

    steps, sweep = build_rocof_step_list("50", "52", 2.0, dt_s=0.05)
    assert steps[0] == "50"
    assert steps[-1] == "52"
    assert abs(sweep - 1.0) < 1e-6
    assert len(steps) > 5


def test_rocof_chroma_three_phase_startup(qapp):
    from Dialog_thairocof import Ui_Dialog_thairocof
    from utils.rocof_commands import build_rocof_plan

    ui = Ui_Dialog_thairocof()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_rocof_profile(ui, with_end=False)
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    for sn in range(4, 9):
        getattr(ui, "checkBox_S%d" % sn).setChecked(False)

    plan = build_rocof_plan(ui, wt_config_dict={"comboBox_AutoSave": 1}, chroma_61800=True)
    assert plan["ok"], plan.get("error")
    writes = [str(r[2]) for r in plan["commands"] if r[0] == "AC" and r[1] == "write"]
    assert "CONF:COUP AC" in writes
    assert "PHAS:THREE SAMEFREQ" in writes
    assert "VOLT:AC 230" in writes
    assert writes.count("INST:EDIT ALL") >= 1
    assert "VOLT 230" not in writes


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    test_rocof_cross_rate_sweep_continuous(app)
    test_rocof_step_list_matches_rate(app)
    print("ROCOF_CROSS_ALL_OK")
