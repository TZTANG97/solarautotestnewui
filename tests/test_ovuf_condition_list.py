# -*- coding: utf-8 -*-
"""过欠压：恢复 8 步扫段；工况列表组件仍可单测（已不挂 Dialog）。"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from components.ovuf_condition_list import OvufConditionList, pea_vfrt_template_rows
from dialogs.Dialog_thaiguoqianya_pin import Ui_Dialog_thaiguoqianya_pin
from utils.ovuf_recording import (
    append_ovuf_condition_sequence,
    enabled_ovuf_segments,
    read_ovuf_condition_rows,
)


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


def test_dialog_restored_eight_steps_no_condition_list(ovuf_ui):
    assert len(ovuf_ui._step_labels) == 8
    assert ovuf_ui.stackedWidget.count() == 8
    assert not hasattr(ovuf_ui, "ovufConditionList")
    assert ovuf_ui.checkBox_S3 is not None
    assert ovuf_ui.textEdit_S3_Step_Size is not None
    # ③ 过压 = stacked index 2
    ovuf_ui._switch_step(2)
    assert ovuf_ui.stackedWidget.currentIndex() == 2


def test_no_list_uses_legacy_segments(ovuf_ui):
    assert read_ovuf_condition_rows(ovuf_ui) == []
    segs = enabled_ovuf_segments(ovuf_ui)
    assert segs  # default S3–S6 checked
    assert all(not s.get("from_list") for s in segs)


def test_pea_template_rows_include_ab_fault():
    rows = pea_vfrt_template_rows(460)
    assert any(r["l1"] and r["l2"] and not r["l3"] for r in rows)
    assert any(r["l1"] and r["l2"] and r["l3"] for r in rows)
    assert any(abs(float(r["value"]) - 414.0) < 0.2 for r in rows)


def test_append_ab_then_three_phase_recovery(monkeypatch, ovuf_ui):
    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: False
    )
    ovuf_ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_FR.setPlainText("50")
    rows = [
        {
            "enabled": True,
            "kind": "V",
            "value": "207",
            "l1": True,
            "l2": True,
            "l3": False,
            "dwell": "1",
            "unit": "秒",
        },
        {
            "enabled": True,
            "kind": "V",
            "value": "115",
            "l1": True,
            "l2": True,
            "l3": True,
            "dwell": "1",
            "unit": "秒",
        },
    ]
    cmds: list = []
    batches: list = []
    sec = append_ovuf_condition_sequence(cmds, batches, ovuf_ui, "三相", rows)
    assert sec > 0
    assert len(batches) == 2
    writes = [str(r[2]) for r in cmds if r and r[1] == "write"]
    assert "INST:EDIT EACH" in writes
    assert "VOLT 207" in writes and "VOLT 230" in writes
    assert "VOLT 115" in writes


def test_widget_get_set_rows(qapp):
    w = OvufConditionList()
    w.set_rows(
        [
            {
                "enabled": True,
                "kind": "F",
                "value": "51.5",
                "l1": False,
                "l2": False,
                "l3": False,
                "dwell": "2",
                "unit": "秒",
            }
        ]
    )
    got = w.get_rows()
    assert len(got) == 1
    assert got[0]["kind"] == "F"
    assert got[0]["value"] == "51.5"
