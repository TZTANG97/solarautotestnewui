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
    append_ovuf_scan_list,
    enabled_ovuf_segments,
    read_ovuf_condition_rows,
    read_ovuf_scan_rows,
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


def test_dialog_keeps_eight_steps_and_empty_scan_lists(ovuf_ui):
    assert len(ovuf_ui._step_labels) == 8
    assert ovuf_ui.stackedWidget.count() == 8
    assert not hasattr(ovuf_ui, "ovufConditionList")
    assert ovuf_ui.checkBox_S3 is not None
    assert ovuf_ui.textEdit_S3_Step_Size is not None
    assert ovuf_ui.textEdit_S3_Step_Size.isHidden()
    for step, kind in ((3, "V"), (4, "V"), (5, "F"), (6, "F")):
        widget = getattr(ovuf_ui, "ovufScanListS%d" % step)
        rows = widget.get_rows(include_disabled=True)
        assert len(rows) == 1
        assert rows[0]["kind"] == kind
        assert rows[0]["step"] == "5"
        assert rows[0]["dwell"] == "3"
        assert rows[0]["volt_start"] == "230" and rows[0]["volt_end"] == "230"
        assert rows[0]["freq_start"] == "50" and rows[0]["freq_end"] == "50"
        assert widget._locked_kind == kind
        assert widget._scan_range is True
        assert widget.table.isColumnHidden(6) is (kind == "F")
    ovuf_ui._switch_step(2)
    assert ovuf_ui.stackedWidget.currentIndex() == 2


def test_default_scan_rows_match_old_ranges(ovuf_ui):
    assert read_ovuf_condition_rows(ovuf_ui) == []
    segs = enabled_ovuf_segments(ovuf_ui)
    assert [s["step"] for s in segs] == [3, 4, 5, 6]
    assert segs[0]["points"] == [230.0]
    assert segs[2]["points"] == [50.0]
    assert all(s.get("from_scan_list") for s in segs)


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


def test_overvolt_list_l1_l2_keeps_l3_at_rated(monkeypatch, ovuf_ui):
    """只勾 L1、L2：这两相跟设定电压，L3 保持步骤①额定。"""
    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: False
    )
    for step in (4, 5, 6, 7, 8):
        getattr(ovuf_ui, "checkBox_S%d" % step).setChecked(False)
    ovuf_ui.checkBox_S3.setChecked(True)
    ovuf_ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_FR.setPlainText("50")
    ovuf_ui.ovufScanListS3.set_rows(
        [
            {
                "enabled": True,
                "kind": "V",
                "value": "253",
                "l1": True,
                "l2": True,
                "l3": False,
                "dwell": "1",
                "unit": "秒",
            }
        ]
    )
    assert read_ovuf_condition_rows(ovuf_ui) == []
    segs = enabled_ovuf_segments(ovuf_ui)
    assert segs[0]["from_scan_list"] is True
    assert segs[0]["points"] == [253.0]
    cmds: list = []
    sec = append_ovuf_scan_list(
        cmds, [], ovuf_ui, "三相", 3, ovuf_ui.ovufScanListS3.get_rows()
    )
    assert sec > 0
    writes = [str(r[2]) for r in cmds if r and r[1] == "write"]
    assert "INST:EDIT EACH" in writes
    assert "VOLT 253" in writes
    assert "VOLT 230" in writes
    ovuf_ui.ovufScanListS3.clear_rows()
    assert read_ovuf_scan_rows(ovuf_ui, 3) == []


def test_freq_scan_list_changes_whole_machine_frequency(monkeypatch, ovuf_ui):
    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: False
    )
    ovuf_ui.textEdit_S1_AC_FR.setPlainText("50")
    ovuf_ui.ovufScanListS5.set_rows(
        [
            {
                "enabled": True,
                "kind": "F",
                "value": "51.5",
                "l1": True,
                "l2": False,
                "l3": False,
                "dwell": "1",
                "unit": "秒",
            }
        ]
    )
    cmds: list = []
    append_ovuf_scan_list(cmds, [], ovuf_ui, "三相", 5, read_ovuf_scan_rows(ovuf_ui, 5))
    writes = [str(r[2]) for r in cmds if r and r[1] == "write"]
    assert "FREQ 51.5" in writes
    ovuf_ui.ovufScanListS5.clear_rows()


def test_overvolt_list_runs_each_range(monkeypatch, ovuf_ui):
    """两段过压：各自按起止和步长扫，第一段只动 L1/L2。"""
    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: False
    )
    for step in (4, 5, 6, 7, 8):
        getattr(ovuf_ui, "checkBox_S%d" % step).setChecked(False)
    ovuf_ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_FR.setPlainText("50")
    ovuf_ui.ovufScanListS3.set_rows(
        [
            {
                "enabled": True,
                "kind": "V",
                "volt_start": "230",
                "volt_end": "240",
                "freq_start": "50",
                "freq_end": "50",
                "step": "10",
                "l1": True,
                "l2": True,
                "l3": False,
                "dwell": "1",
                "unit": "秒",
            },
            {
                "enabled": True,
                "kind": "V",
                "volt_start": "250",
                "volt_end": "253",
                "freq_start": "50",
                "freq_end": "50",
                "step": "5",
                "l1": True,
                "l2": True,
                "l3": True,
                "dwell": "2",
                "unit": "秒",
            },
        ]
    )
    segs = enabled_ovuf_segments(ovuf_ui)
    assert segs[0]["points"] == [230.0, 240.0, 250.0, 253.0]
    cmds: list = []
    append_ovuf_scan_list(cmds, [], ovuf_ui, "三相", 3, ovuf_ui.ovufScanListS3.get_rows())
    volts = [
        str(r[2])
        for r in cmds
        if r and r[1] == "write" and str(r[2]).startswith("VOLT ")
    ]
    assert "VOLT 230" in volts and "VOLT 240" in volts
    assert "VOLT 250" in volts and "VOLT 253" in volts
    assert "INST:EDIT EACH" in [str(r[2]) for r in cmds if r and r[1] == "write"]
    ovuf_ui.ovufScanListS3.clear_rows()


def test_cleared_scan_list_does_not_fall_back_to_old_range(monkeypatch, ovuf_ui):
    """删空列表后，不再用隐藏的旧起止生成扫点或命令。"""
    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: False
    )
    for step in (4, 5, 6, 7, 8):
        getattr(ovuf_ui, "checkBox_S%d" % step).setChecked(False)
    ovuf_ui.checkBox_S3.setChecked(True)
    ovuf_ui.textEdit_S3_AC_VOLT_End.setPlainText("253")
    ovuf_ui.ovufScanListS3.clear_rows()
    assert read_ovuf_scan_rows(ovuf_ui, 3) == []
    assert enabled_ovuf_segments(ovuf_ui) == []
    cmds: list = []
    assert append_ovuf_scan_list(cmds, [], ovuf_ui, "三相", 3, []) == 0
    assert cmds == []


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
