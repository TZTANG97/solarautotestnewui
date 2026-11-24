# -*- coding: utf-8 -*-
import sys
from unittest.mock import MagicMock

sys.modules.setdefault("PyQt5", MagicMock())
sys.modules.setdefault("PyQt5.QtWidgets", MagicMock())

from devices.ac_controller import (
    _chroma_three_phase_command_list,
    _generic_scpi_three_phase_command_list,
    _is_chroma_61800_idn,
    _resolve_three_phase_volts,
    ACController,
)
from utils.voltage_adaptability_commands import append_chroma_three_phase_setpoints, _empty_row


def test_is_chroma_61800_idn():
    assert _is_chroma_61800_idn("Chroma,61800-100,0,1.0")
    assert _is_chroma_61800_idn("Chroma ATE,61830,00001,1.0")
    assert _is_chroma_61800_idn("Chroma ATE,61845,00001,1.0")
    assert not _is_chroma_61800_idn("Chroma,62050H,0,1.0")
    assert not _is_chroma_61800_idn("ITECH,IT7322,0,1.0")
    assert not _is_chroma_61800_idn("")


def test_resolve_chroma_61800_reads_main_module(monkeypatch):
    import types
    from utils.ac_scpi_commands import resolve_chroma_61800

    class _FakeAC:
        connected = True

        def is_chroma_61800(self):
            return True

    fake_main = types.SimpleNamespace(ac_controller=_FakeAC())
    monkeypatch.setitem(sys.modules, "__main__", fake_main)
    monkeypatch.delitem(sys.modules, "SCPITestWave", raising=False)
    assert resolve_chroma_61800() is True


def test_generic_scpi_three_phase_uses_edit_all_not_balance():
    cmds = _generic_scpi_three_phase_command_list("230", "50")
    assert cmds == [
        "INST:PHAS THREE",
        "INST:EDIT ALL",
        "VOLT 230",
        "FREQ 50",
    ]
    assert "PHAS:THREE SAMEFREQ" not in cmds


def test_apply_setpoints_generic_three_phase_no_chroma_cmds():
    class _Log:
        def info(self, *a, **k):
            pass

        def warning(self, *a, **k):
            pass

        def error(self, *a, **k):
            pass

    ac = ACController(_Log(), lambda *a, **k: None, lambda: "t")
    ac._store_idn("Keysight,AC6800,0,1.0")
    cmds = []
    class _H:
        def write(self, c):
            cmds.append(c)
    ac._set_handle(_H())
    ac.apply_setpoints("230", "50", "三相")
    assert "INST:EDIT ALL" in cmds
    assert "VOLT:AC" not in "".join(cmds)


def test_resolve_fills_empty_phase1_from_phase2():
    a, b, c = _resolve_three_phase_volts("", "230", "230")
    assert a == "230" and b == "230" and c == "230"


def test_chroma_commands_samerefreq_volt_ac_all_phases():
    cmds = _chroma_three_phase_command_list("", "230", "230", "50")
    assert cmds[0] == "CONF:COUP AC"
    assert "PHAS:THREE SAMEFREQ" in cmds
    assert cmds.count("VOLT:AC 230") == 4
    assert "INST:EDIT ALL" in cmds
    assert "INST:NSEL 1" in cmds
    assert "PHAS:THREE BALANCE" not in cmds


def test_chroma_commands_independ_when_voltages_differ():
    cmds = _chroma_three_phase_command_list("220", "230", "240", "50")
    assert "PHAS:THREE INDEPEND" in cmds
    assert "VOLT:AC 220" in cmds
    assert "VOLT:AC 240" in cmds


def test_append_chroma_rows_phase1_not_zero():
    rows = []
    append_chroma_three_phase_setpoints(rows, "", "230", "", "50")
    writes = [r[2] for r in rows if r[1] == "write" and str(r[2]).startswith("VOLT")]
    assert writes == ["VOLT:AC 230", "VOLT:AC 230", "VOLT:AC 230", "VOLT:AC 230"]
    assert any(r[2] == "INST:EDIT ALL" for r in rows)
    assert any(r[2] == "PHAS:THREE SAMEFREQ" for r in rows)
