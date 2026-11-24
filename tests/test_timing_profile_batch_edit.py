# -*- coding: utf-8 -*-
"""TimingProfileTable: Ctrl/Shift multi-select batch-edits one column."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtCore, QtWidgets

from components.timing_profile_table import TimingProfileTable
from utils.lvrt_commands import pea_lvrt_template_profile
from utils.timing_profile import LVRT_SCHEMA


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_batch_edit_pre_time_on_selected_rows(qapp):
    rows = pea_lvrt_template_profile()[:3]
    w = TimingProfileTable(LVRT_SCHEMA, rows=rows)
    assert w.table.selectionMode() == QtWidgets.QAbstractItemView.ExtendedSelection

    # Select rows 0 and 2
    w.table.clearSelection()
    w.table.selectRow(0)
    w.table.selectRow(2)
    # ExtendedSelection with selectRow may replace; use selection model
    model = w.table.selectionModel()
    model.clearSelection()
    for r in (0, 1, 2):
        model.select(
            w.table.model().index(r, 0),
            QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows,
        )

    col = w._column_index["t_pre"]
    item = w.table.item(1, col)
    item.setText("5")
    # itemChanged → propagate
    profile = w.get_profile(validate=False, allow_empty=True)
    assert profile[0]["t_pre"] == "5"
    assert profile[1]["t_pre"] == "5"
    assert profile[2]["t_pre"] == "5"


def test_batch_edit_unit_combo(qapp):
    rows = pea_lvrt_template_profile()[:2]
    w = TimingProfileTable(LVRT_SCHEMA, rows=rows)
    model = w.table.selectionModel()
    model.clearSelection()
    for r in (0, 1):
        model.select(
            w.table.model().index(r, 0),
            QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows,
        )
    col = w._column_index["t_dwell_unit"]
    combo = w.table.cellWidget(0, col)
    assert isinstance(combo, QtWidgets.QComboBox)
    combo.setCurrentText("毫秒")
    profile = w.get_profile(validate=False, allow_empty=True)
    assert profile[0]["t_dwell_unit"] == "毫秒"
    assert profile[1]["t_dwell_unit"] == "毫秒"


def test_delete_removes_all_selected(qapp):
    rows = pea_lvrt_template_profile()[:4]
    w = TimingProfileTable(LVRT_SCHEMA, rows=rows)
    model = w.table.selectionModel()
    model.clearSelection()
    for r in (1, 3):
        model.select(
            w.table.model().index(r, 0),
            QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows,
        )
    w.remove_selected_row()
    assert w.table.rowCount() == 2
