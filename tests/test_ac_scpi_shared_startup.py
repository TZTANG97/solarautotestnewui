# -*- coding: utf-8 -*-
"""共用 AC 启机：爱科同压不得再走 EDIT EACH+NSEL。"""
from utils.ac_scpi_commands import (
    append_ac_startup_setpoints,
    append_legacy_three_phase_setpoints,
    append_volt_set,
)


def test_legacy_equal_volts_uses_edit_all():
    rows = []
    append_legacy_three_phase_setpoints(rows, "230", "230", "230", "50")
    cmds = [r[2] for r in rows]
    assert cmds == [
        "INST:PHAS THREE",
        "INST:EDIT ALL",
        "VOLT 230",
        "FREQ 50",
    ]
    assert "INST:EDIT EACH" not in cmds
    assert "INST:NSEL 1" not in cmds


def test_legacy_unequal_volts_ends_with_edit_all():
    rows = []
    append_legacy_three_phase_setpoints(rows, "230", "220", "210", "50")
    cmds = [r[2] for r in rows]
    assert cmds[0] == "INST:PHAS THREE"
    assert "INST:EDIT EACH" in cmds
    assert cmds[-1] == "INST:EDIT ALL"


def test_startup_setpoints_three_phase_non_chroma():
    rows = []
    append_ac_startup_setpoints(
        rows, "三相", "230", "230", "230", "50", chroma_61800=False
    )
    cmds = [r[2] for r in rows]
    assert "INST:EDIT ALL" in cmds
    assert "INST:EDIT EACH" not in cmds


def test_append_volt_set_three_phase_edit_all():
    rows = []
    append_volt_set(rows, "三相", "207", chroma_61800=False)
    assert [r[2] for r in rows] == ["INST:EDIT ALL", "VOLT 207"]
