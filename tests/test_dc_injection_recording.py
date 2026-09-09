# -*- coding: utf-8 -*-
"""直流分量：录波方式下拉 + 连续录/分开录命令。"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from Dialog_thaizhiliufenliang import Ui_Dialog_thaizhiliufenliang
from components.wt_recording_mode_row import WtRecordingModeRow
from utils.dc_injection_commands import append_dc_injection_measure, enabled_dc_injection_steps
from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT, dc_injection_recommended_filenames


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def dcinj_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaizhiliufenliang()
    ui.setupUi(dialog)
    ui._dialog = dialog
    return ui


def test_dcinj_has_recording_mode_on_filename_list(dcinj_ui):
    assert dcinj_ui.comboBox_S3_record_mode.count() == 2
    page = dcinj_ui._wtStacked.widget(0)
    gb = page.findChild(QtWidgets.QGroupBox, "groupBox_7")
    rows = gb.findChildren(WtRecordingModeRow)
    assert len(rows) == 1


def test_dcinj_recommended_filenames(dcinj_ui):
    steps = enabled_dc_injection_steps(dcinj_ui)
    assert [s for s, _p in steps] == [3, 4, 5]
    assert [p for _s, p in steps] == [100.0, 66.0, 33.0]
    assert dc_injection_recommended_filenames(steps, MODE_CONTINUOUS) == ["DCInj_BR"]
    split = dc_injection_recommended_filenames(steps, MODE_SPLIT)
    assert split == ["DCInj_S3_P100", "DCInj_S4_P66", "DCInj_S5_P33"]


def test_dcinj_measure_continuous_vs_split():
    cmds = []
    rows = []
    append_dc_injection_measure(
        cmds, rows, wait_01s=10, collect_01s=3000,
        wt_continuous=True, wt_on=True, include_wait=True,
        first_point=True, last_point=False,
    )
    assert cmds[0][6] == "ASYNC_START"
    assert cmds[1][9] == 10
    assert cmds[2][9] == 3000
    assert all(r[6] != "WAIT_END" for r in cmds)

    cmds2 = []
    rows2 = []
    append_dc_injection_measure(
        cmds2, rows2, wait_01s=10, collect_01s=3000,
        wt_continuous=True, wt_on=True, include_wait=True,
        first_point=False, last_point=True,
    )
    assert cmds2[-1][6] == "WAIT_END"

    split = []
    append_dc_injection_measure(
        split, [], wait_01s=10, collect_01s=3000,
        wt_continuous=False, wt_on=True, include_wait=True,
        first_point=True, last_point=True,
    )
    assert [r[7] for r in split if r[7] != ""] == [3000]
    assert all(r[6] not in ("ASYNC_START", "WAIT_END") for r in split)
