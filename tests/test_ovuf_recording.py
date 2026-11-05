# -*- coding: utf-8 -*-
"""过欠压_过欠频：录波方式切换自动生成文件名 + 连续录/分开录触发。"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from Dialog_thaiguoqianya_pin import Ui_Dialog_thaiguoqianya_pin
from components.wt_recording_mode_row import WtRecordingModeRow
from utils.matrix_recording_commands import get_record_mode
from utils.ovuf_recording import (
    append_ovuf_segment_recovery,
    apply_ovuf_recording_mode,
    build_ovuf_sweep_points,
    enabled_ovuf_segments,
    ovuf_sweep_project,
    recommended_ovuf_names,
)
from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def ovuf_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaiguoqianya_pin()
    ui.setupUi(dialog)
    ui._dialog = dialog
    return ui


def test_step_kind_does_not_follow_the_project_combo():
    assert ovuf_sweep_project(3) == "过欠压"
    assert ovuf_sweep_project(4) == "过欠压"
    assert ovuf_sweep_project(5) == "过欠频"
    assert ovuf_sweep_project(6) == "过欠频"
    assert ovuf_sweep_project(7) == "过欠频"
    assert ovuf_sweep_project(8) == "过欠频"


def test_ovuf_has_recording_mode_on_filename_list(ovuf_ui):
    page = ovuf_ui._wtStacked.widget(0)
    gb = page.findChild(QtWidgets.QGroupBox, "groupBox_7")
    rows = gb.findChildren(WtRecordingModeRow)
    assert len(rows) == 1
    combo = page.findChild(QtWidgets.QComboBox, "comboBox_recording_mode")
    assert combo is not None
    assert combo.count() == 2


def test_ovuf_recommended_filenames_continuous_and_split(ovuf_ui):
    # 3/4 扫电压，5/6 扫频率；附加段默认关闭。两边都有时连续录用 OVUF_BR。
    assert recommended_ovuf_names(ovuf_ui, MODE_CONTINUOUS) == ["OVUF_BR"]
    split = recommended_ovuf_names(ovuf_ui, MODE_SPLIT)
    assert split == [
        "OVUF_S3_V230_230",
        "OVUF_S4_V230_230",
        "OVUF_S5_F50_50",
        "OVUF_S6_F50_50",
    ]

    ovuf_ui.comboBox_Test_Project.setCurrentText("过欠频")
    assert recommended_ovuf_names(ovuf_ui, MODE_SPLIT)[0].startswith("OVUF_S3_V")
    assert recommended_ovuf_names(ovuf_ui, MODE_SPLIT)[2].startswith("OVUF_S5_F")


def test_ovuf_mode_change_auto_fills_filename_list(ovuf_ui):
    page = ovuf_ui._wtStacked.widget(0)
    te = page.findChild(QtWidgets.QTextEdit, "textEdit_FileNameList")
    combo = page.findChild(QtWidgets.QComboBox, "comboBox_recording_mode")
    assert te is not None and combo is not None

    shared = ovuf_ui.analyzerModeSection.comboBox_analyzer_recording_mode
    shared.setCurrentIndex(0)  # continuous
    assert "OVUF_BR" in te.toPlainText().replace(" ", "")

    shared.setCurrentIndex(1)  # split
    text = te.toPlainText().replace(" ", "")
    assert "OVUF_S3_V230_230" in text
    assert "OVUF_S5_F50_50" in text
    assert "OVUF_S7_" not in text


def test_ovuf_sweep_points_and_segments(ovuf_ui):
    assert build_ovuf_sweep_points(230, 253, 5) == [230.0, 235.0, 240.0, 245.0, 250.0, 253.0]
    ovuf_ui.checkBox_S4.setChecked(False)
    ovuf_ui.checkBox_S5.setChecked(False)
    ovuf_ui.checkBox_S6.setChecked(False)
    ovuf_ui.checkBox_S7.setChecked(False)
    ovuf_ui.checkBox_S8.setChecked(False)
    ovuf_ui.textEdit_S3_AC_VOLT_End.setPlainText("240")
    ovuf_ui.textEdit_S3_Step_Size.setPlainText("10")
    segs = enabled_ovuf_segments(ovuf_ui)
    assert len(segs) == 1
    assert segs[0]["step"] == 3
    assert segs[0]["points"] == [230.0, 240.0]
    assert recommended_ovuf_names(ovuf_ui, MODE_SPLIT) == ["OVUF_S3_V230_240"]


def test_ovuf_apply_recording_continuous_vs_split(ovuf_ui):
    cmds = []
    for i, volt in enumerate(("230", "240", "230", "220")):
        cmds.append(["AC", "write", "VOLT " + volt, "", "", "", "", "", "", ""])
        row = ["AC", "query", "*IDN?", "", "", "", "", "", "", ""]
        if i == 0:
            row[6] = 30
        else:
            row[9] = 30
        cmds.append(row)

    for s in (5, 6, 7, 8):
        getattr(ovuf_ui, "checkBox_S%d" % s).setChecked(False)
    ovuf_ui.textEdit_S3_AC_VOLT_End.setPlainText("240")
    ovuf_ui.textEdit_S3_Step_Size.setPlainText("10")
    ovuf_ui.textEdit_S4_AC_VOLT_Start.setPlainText("230")
    ovuf_ui.textEdit_S4_AC_VOLT_End.setPlainText("220")
    ovuf_ui.textEdit_S4_Step_Size.setPlainText("10")

    cont = [list(r) for r in cmds]
    n = apply_ovuf_recording_mode(cont, ovuf_ui, continuous=True, wt_on=True)
    assert n == 1
    assert any(r[6] == "ASYNC_START" for r in cont)
    assert any(r[6] == "WAIT_END" for r in cont)

    split = [list(r) for r in cmds]
    n2 = apply_ovuf_recording_mode(split, ovuf_ui, continuous=False, wt_on=True)
    assert n2 == 2
    col6_nums = [
        r[6]
        for r in split
        if r[6] not in ("", None, "ASYNC_START", "WAIT_END")
    ]
    assert len(col6_nums) == 2


def test_ovuf_segment_recovery_full_setpoint_and_forced_wait(ovuf_ui, monkeypatch):
    """过频→欠频前：完整回压回频 + 不可跳过的并网等待行。"""
    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: False
    )
    ovuf_ui.checkBox_S5.setChecked(True)
    ovuf_ui.checkBox_S6.setChecked(True)
    ovuf_ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_FR.setPlainText("50")
    ovuf_ui.textEdit_ovuf_grid_wait.setPlainText("5")
    ovuf_ui.comboBox_ovuf_grid_wait.setCurrentText("秒")

    cmds = []
    wait = append_ovuf_segment_recovery(
        cmds, None, ovuf_ui, "三相", after_step=5, dwell_01s=50
    )
    assert wait == 50
    cmds_txt = [str(r[2]) for r in cmds if r and r[1] == "write"]
    assert any("EDIT ALL" in c for c in cmds_txt)
    assert any(c.startswith("VOLT") for c in cmds_txt)
    assert any(c.startswith("FREQ 50") for c in cmds_txt)
    wait_rows = [r for r in cmds if r[1] == "wait" and r[2] == "OVUF_GRID_RECOVERY"]
    assert len(wait_rows) == 1
    assert wait_rows[0][9] == 50

    # 末段：仍回额定，但不再插并网等待
    tail = []
    assert append_ovuf_segment_recovery(tail, None, ovuf_ui, "三相", after_step=6) == 0
    tail_txt = [str(r[2]) for r in tail if r and r[1] == "write"]
    assert any(c.startswith("FREQ 50") for c in tail_txt)
    assert any(c.startswith("VOLT") for c in tail_txt)
    assert not any(r[1] == "wait" for r in tail)
