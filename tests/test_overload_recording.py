# -*- coding: utf-8 -*-
"""过载能力：录波方式下拉 + 连续录/分开录命令。"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thaioverloads import Ui_Dialog_thaioverloads
from components.wt_recording_mode_row import WtRecordingModeRow
from utils.overload_commands import build_overload_measure_rows
from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT, overload_recommended_filenames


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def overload_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaioverloads()
    ui.setupUi(dialog)
    ui._dialog = dialog
    return ui


def test_overload_has_recording_mode_on_filename_list(overload_ui):
    assert overload_ui.comboBox_S3_record_mode.count() == 2
    page = overload_ui._wtStacked.widget(0)
    gb = page.findChild(QtWidgets.QGroupBox, "groupBox_7")
    rows = gb.findChildren(WtRecordingModeRow)
    assert len(rows) == 1
    combo = page.findChild(QtWidgets.QComboBox, "comboBox_recording_mode")
    assert combo is not None
    assert combo.count() == 2


def test_overload_recommended_filenames():
    assert overload_recommended_filenames(MODE_CONTINUOUS) == ["Overload_BR"]
    assert overload_recommended_filenames(MODE_SPLIT) == ["Overload_90min"]


def test_overload_measure_rows_continuous_vs_split():
    collect = 54000
    cont = build_overload_measure_rows(collect, wt_continuous=True, wt_on=True)
    assert [r[6] for r in cont] == ["ASYNC_START", "", "WAIT_END"]
    assert cont[1][9] == collect
    split = build_overload_measure_rows(collect, wt_continuous=False, wt_on=True)
    assert len(split) == 1
    assert split[0][7] == collect
    assert split[0][6] == ""
