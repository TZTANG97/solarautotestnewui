# -*- coding: utf-8 -*-
"""重连：录波方式下拉 + 连续录/分开录命令。"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thaichonglian import Ui_Dialog_thaichonglian
from components.wt_recording_mode_row import WtRecordingModeRow
from utils.reconnect_commands import (
    append_reconnect_measure,
    enabled_reconnect_steps,
    recommended_reconnect_names,
)
from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT, reconnect_recommended_filenames


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def reconn_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaichonglian()
    ui.setupUi(dialog)
    ui._dialog = dialog
    return ui


def test_reconn_has_recording_mode_on_filename_list(reconn_ui):
    page = reconn_ui._wtStacked.widget(0)
    gb = page.findChild(QtWidgets.QGroupBox, "groupBox_7")
    rows = gb.findChildren(WtRecordingModeRow)
    assert len(rows) == 1
    combo = page.findChild(QtWidgets.QComboBox, "comboBox_recording_mode")
    assert combo is not None
    assert combo.count() == 2


def test_reconn_recommended_filenames(reconn_ui):
    steps = enabled_reconnect_steps(reconn_ui)
    assert steps == [3, 4, 5, 6, 7]
    assert recommended_reconnect_names(reconn_ui, MODE_CONTINUOUS) == ["Reconn_BR"]
    assert reconnect_recommended_filenames(steps, MODE_SPLIT) == [
        "Reconn_S3",
        "Reconn_S4",
        "Reconn_S5",
        "Reconn_S6",
        "Reconn_S7",
    ]


def test_reconn_measure_continuous_vs_split():
    cmds = []
    append_reconnect_measure(
        cmds, [], dwell_01s=25, wt_continuous=True, wt_on=True,
        first_point=True, last_point=False,
    )
    assert cmds[0][6] == "ASYNC_START"
    assert cmds[1][9] == 25
    assert all(r[6] != "WAIT_END" for r in cmds)

    cmds2 = []
    append_reconnect_measure(
        cmds2, [], dwell_01s=25, wt_continuous=True, wt_on=True,
        first_point=False, last_point=True,
    )
    assert cmds2[-1][6] == "WAIT_END"

    split = []
    append_reconnect_measure(
        split, [], dwell_01s=25, wt_continuous=False, wt_on=True,
        first_point=True, last_point=True,
    )
    assert [r[7] for r in split if r[7] != ""] == [25]
    assert all(r[6] not in ("ASYNC_START", "WAIT_END") for r in split)
