# -*- coding: utf-8 -*-
"""过欠压工况列表：分相多行 + 空列表回退旧扫段。"""

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
    recommended_ovuf_names,
)
from utils.wt_recording_mode import MODE_SPLIT


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


def test_dialog_has_four_visible_steps_and_condition_list(ovuf_ui):
    assert len(ovuf_ui._step_labels) == 4
    assert ovuf_ui.stackedWidget.count() == 4
    assert ovuf_ui.ovufConditionList is not None
    assert ovuf_ui.checkBox_S3 is not None  # legacy still present
    assert not ovuf_ui._legacy_host.isVisible()


def test_pea_template_rows_include_ab_fault():
    rows = pea_vfrt_template_rows(460)
    assert any(r["l1"] and r["l2"] and not r["l3"] for r in rows)
    assert any(r["l1"] and r["l2"] and r["l3"] for r in rows)
    assert any(abs(float(r["value"]) - 414.0) < 0.2 for r in rows)  # 0.9*460


def test_empty_list_falls_back_to_legacy_segments(ovuf_ui):
    ovuf_ui.ovufConditionList.clear_rows()
    assert read_ovuf_condition_rows(ovuf_ui) == []
    segs = enabled_ovuf_segments(ovuf_ui)
    assert segs  # default S3–S6 checked
    assert all(not s.get("from_list") for s in segs)


def test_list_rows_drive_segments_and_names(ovuf_ui):
    ovuf_ui.ovufConditionList.set_rows(
        [
            {
                "enabled": True,
                "kind": "V",
                "value": "413",
                "l1": True,
                "l2": True,
                "l3": False,
                "dwell": "120",
                "unit": "秒",
            },
            {
                "enabled": True,
                "kind": "V",
                "value": "230",
                "l1": True,
                "l2": True,
                "l3": True,
                "dwell": "10",
                "unit": "秒",
            },
        ]
    )
    segs = enabled_ovuf_segments(ovuf_ui)
    assert len(segs) == 2
    assert segs[0]["from_list"] and segs[0]["phase_tag"] == "L12"
    names = recommended_ovuf_names(ovuf_ui, MODE_SPLIT)
    assert names[0].startswith("OVUF_R01_V413_L12")
    assert "L123" in names[1]


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
    assert "INST:EDIT ALL" in writes
    assert "VOLT 115" in writes
    assert any(r[1] == "wait" and r[2] == "OVUF_COND_DWELL" for r in cmds)
    assert any(r[1] == "wait" and r[2] == "OVUF_VOLT_SETTLE" for r in cmds)
    assert any(r[1] == "wait" and r[2] == "OVUF_GRID_RECOVERY" for r in cmds)


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


def test_list_mode_recording_split_and_continuous(monkeypatch, ovuf_ui):
    """P0：工况列表 OVUF_COND_DWELL 能被录波改写认到，并计入 StopTime。"""
    from utils.ovuf_recording import (
        apply_ovuf_recording_mode,
        append_ovuf_condition_sequence,
        ovuf_split_collect_sec,
    )

    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: False
    )
    ovuf_ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_FR.setPlainText("50")
    rows = [
        {
            "enabled": True,
            "kind": "V",
            "value": "207",
            "l1": True,
            "l2": True,
            "l3": False,
            "dwell": "120",
            "unit": "秒",
        },
        {
            "enabled": True,
            "kind": "V",
            "value": "115",
            "l1": True,
            "l2": True,
            "l3": True,
            "dwell": "10",
            "unit": "秒",
        },
    ]
    ovuf_ui.ovufConditionList.set_rows(rows)

    cmds: list = []
    batches: list = []
    append_ovuf_condition_sequence(cmds, batches, ovuf_ui, "三相", rows)
    assert any(r[1] == "wait" and r[2] == "OVUF_COND_DWELL" for r in cmds)
    assert ovuf_split_collect_sec(cmds) >= 120

    cont = [list(r) for r in cmds]
    n = apply_ovuf_recording_mode(cont, ovuf_ui, continuous=True, wt_on=True)
    assert n == 1
    assert any(len(r) > 6 and r[6] == "ASYNC_START" for r in cont)
    assert any(len(r) > 6 and r[6] == "WAIT_END" for r in cont)

    split = [list(r) for r in cmds]
    n2 = apply_ovuf_recording_mode(split, ovuf_ui, continuous=False, wt_on=True)
    assert n2 == 2
    assert sum(1 for r in split if len(r) > 6 and r[6] == "ASYNC_START") == 2
    assert sum(1 for r in split if len(r) > 6 and r[6] == "WAIT_END") == 2


def test_freq_list_name_has_no_phase_tag(ovuf_ui):
    ovuf_ui.ovufConditionList.set_rows(
        [
            {
                "enabled": True,
                "kind": "F",
                "value": "51.5",
                "l1": True,
                "l2": False,
                "l3": False,
                "dwell": "3",
                "unit": "秒",
            }
        ]
    )
    names = recommended_ovuf_names(ovuf_ui, MODE_SPLIT)
    assert names == ["OVUF_R01_F51p5"]  # 小数点格式化为 p，无相标签
