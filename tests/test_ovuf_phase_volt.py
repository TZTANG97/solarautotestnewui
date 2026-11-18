# -*- coding: utf-8 -*-
"""过欠压分相扫压：全选同压，部分相独立改压。"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thaiguoqianya_pin import Ui_Dialog_thaiguoqianya_pin
from utils.ovuf_recording import (
    append_ovuf_segment_recovery,
    append_ovuf_sweep_volt,
    build_ovuf_phase_target_volts,
)


def test_all_selected_targets_same_as_step():
    assert build_ovuf_phase_target_volts("207", ["T", "T", "T"], ("230", "230", "230")) == (
        "207",
        "207",
        "207",
    )


def test_none_selected_falls_back_to_all_step():
    assert build_ovuf_phase_target_volts("207", ["", "", ""], ("230", "230", "230")) == (
        "207",
        "207",
        "207",
    )


def test_ab_fault_keeps_c_at_rated():
    # PEA Phase A-B：L1/L2 故障，L3 保持额定
    assert build_ovuf_phase_target_volts("207", ["T", "T", ""], ("230", "230", "230")) == (
        "207",
        "207",
        "230",
    )


def test_single_phase_l1_only():
    assert build_ovuf_phase_target_volts("115", ["T", "", ""], ("230", "231", "232")) == (
        "115",
        "231",
        "232",
    )


def test_append_all_selected_uses_edit_all_once():
    rows: list = []
    append_ovuf_sweep_volt(rows, "三相", "253", ["T", "T", "T"], ("230", "230", "230"), chroma_61800=False)
    cmds = [r[2] for r in rows]
    assert "INST:EDIT ALL" in cmds
    assert "INST:EDIT EACH" not in cmds
    assert any(str(c).startswith("VOLT ") for c in cmds)


def test_append_partial_phases_uses_edit_each():
    rows: list = []
    append_ovuf_sweep_volt(rows, "三相", "207", ["T", "T", ""], ("230", "230", "230"), chroma_61800=False)
    cmds = [r[2] for r in rows]
    assert "INST:EDIT EACH" in cmds
    assert "INST:NSEL 1" in cmds
    assert "INST:NSEL 2" in cmds
    assert "INST:NSEL 3" in cmds
    # 故障相 207，C 相额定 230
    assert "VOLT 207" in cmds
    assert "VOLT 230" in cmds


def test_append_partial_phases_chroma_uses_independ():
    rows: list = []
    append_ovuf_sweep_volt(
        rows, "三相", "207", ["T", "T", ""], ("230", "230", "230"), chroma_61800=True
    )
    cmds = [r[2] for r in rows]
    assert "CONF:COUP AC" in cmds
    assert "PHAS:THREE INDEPEND" in cmds
    assert "INST:EDIT EACH" in cmds
    assert "VOLT:AC 207" in cmds
    assert "VOLT:AC 230" in cmds
    assert "PHAS:THREE SAMEFREQ" not in cmds
    # 扫压不夹 FREQ，避免与段后恢复双 SAVE
    assert not any(str(c).startswith("FREQ") for c in cmds)


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def ovuf_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaiguoqianya_pin()
    ui.setupUi(dialog)
    ui._dialog = dialog  # keep parent alive for Qt widgets
    return ui


def test_partial_sweep_then_segment_recovery_legacy(ovuf_ui, monkeypatch):
    """PEA A-B 扫压后段恢复：先回额定压，短驻留，再回频；并网等待保留。"""
    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: False
    )
    for s in (4, 6, 7, 8):
        getattr(ovuf_ui, "checkBox_S%d" % s).setChecked(False)
    ovuf_ui.checkBox_S3.setChecked(True)
    ovuf_ui.checkBox_S5.setChecked(True)
    ovuf_ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_FR.setPlainText("50")

    cmds: list = []
    append_ovuf_sweep_volt(
        cmds, "三相", "207", ["T", "T", ""], ("230", "230", "230"), chroma_61800=False
    )
    sweep_n = len(cmds)
    wait = append_ovuf_segment_recovery(
        cmds, None, ovuf_ui, "三相", after_step=3, dwell_01s=50
    )
    assert wait == 50
    sweep_cmds = [r[2] for r in cmds[:sweep_n] if r and r[1] == "write"]
    assert "VOLT 207" in sweep_cmds and "VOLT 230" in sweep_cmds

    kinds = [(r[1], str(r[2])) for r in cmds[sweep_n:] if r]
    assert any(op == "write" and cmd.startswith("VOLT 230") for op, cmd in kinds)
    assert any(op == "wait" and cmd == "OVUF_VOLT_SETTLE" for op, cmd in kinds)
    assert any(op == "write" and cmd.startswith("FREQ 50") for op, cmd in kinds)
    assert any(op == "wait" and cmd == "OVUF_GRID_RECOVERY" for op, cmd in kinds)
    volt_i = next(
        i for i, (op, cmd) in enumerate(kinds) if op == "write" and cmd.startswith("VOLT")
    )
    settle_i = next(i for i, (op, cmd) in enumerate(kinds) if cmd == "OVUF_VOLT_SETTLE")
    freq_i = next(
        i for i, (op, cmd) in enumerate(kinds) if op == "write" and cmd.startswith("FREQ")
    )
    assert volt_i < settle_i < freq_i


def test_partial_sweep_then_segment_recovery_chroma(ovuf_ui, monkeypatch):
    """Chroma：分相扫压走 INDEPEND；段恢复回 SAMEFREQ 再 VOLT:AC，仍 settle→FREQ。"""
    monkeypatch.setattr(
        "utils.ac_scpi_commands.resolve_chroma_61800", lambda *a, **k: True
    )
    for s in (4, 6, 7, 8):
        getattr(ovuf_ui, "checkBox_S%d" % s).setChecked(False)
    ovuf_ui.checkBox_S3.setChecked(True)
    ovuf_ui.checkBox_S5.setChecked(True)
    ovuf_ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ovuf_ui.textEdit_S1_AC_FR.setPlainText("50")

    cmds: list = []
    append_ovuf_sweep_volt(
        cmds, "三相", "207", ["T", "T", ""], ("230", "230", "230"), chroma_61800=True
    )
    sweep_n = len(cmds)
    append_ovuf_segment_recovery(
        cmds, None, ovuf_ui, "三相", after_step=3, dwell_01s=50
    )

    sweep_cmds = [r[2] for r in cmds[:sweep_n] if r and r[1] == "write"]
    assert "PHAS:THREE INDEPEND" in sweep_cmds
    assert "VOLT:AC 207" in sweep_cmds

    rec_cmds = [r[2] for r in cmds[sweep_n:] if r and r[1] == "write"]
    assert "PHAS:THREE SAMEFREQ" in rec_cmds
    assert "VOLT:AC 230" in rec_cmds
    kinds = [(r[1], str(r[2])) for r in cmds[sweep_n:] if r]
    settle_i = next(i for i, (op, cmd) in enumerate(kinds) if cmd == "OVUF_VOLT_SETTLE")
    freq_i = next(
        i for i, (op, cmd) in enumerate(kinds) if op == "write" and cmd.startswith("FREQ")
    )
    assert settle_i < freq_i
