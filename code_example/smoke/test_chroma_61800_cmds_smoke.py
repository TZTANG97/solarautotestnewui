# -*- coding: utf-8 -*-
"""Chroma 61800 命令序列冒烟（不连真机、不依赖 PyQt5 GUI）。"""

import os
import sys
from unittest.mock import MagicMock

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ac_controller 顶层 import PyQt5；无 GUI 环境用 mock
sys.modules.setdefault("PyQt5", MagicMock())
sys.modules.setdefault("PyQt5.QtWidgets", MagicMock())
sys.modules.setdefault("pyvisa", MagicMock())
sys.modules.setdefault("modbus_visa", MagicMock())
sys.modules.setdefault("scpi_to_modbustcp", MagicMock())

from devices.ac_controller import (
    ACController,
    _chroma_three_phase_command_list,
    _generic_scpi_three_phase_command_list,
    _is_chroma_61800_idn,
    _normalize_chroma_ac_write,
    _normalize_ac_volt_command,
)
from utils.voltage_adaptability_commands import append_chroma_three_phase_setpoints, _empty_row


def test_idn_gate():
    assert _is_chroma_61800_idn("Chroma,61800-100,0,1.0")
    assert not _is_chroma_61800_idn("ITECH,IT7322,0,1.0")


def test_chroma_three_phase_same_volt_sequence():
    cmds = _chroma_three_phase_command_list("230", "230", "230", "50")
    assert cmds[0] == "CONF:COUP AC"
    assert "PHAS:THREE SAMEFREQ" in cmds
    assert "PHAS:THREE BALANCE" not in cmds
    assert cmds.count("VOLT:AC 230") == 4
    assert "INST:EDIT ALL" in cmds
    assert "INST:NSEL 1" in cmds
    assert "INST:NSEL 2" in cmds
    assert "INST:NSEL 3" in cmds


def test_chroma_three_phase_independ_when_diff():
    cmds = _chroma_three_phase_command_list("220", "230", "240", "50")
    assert "PHAS:THREE INDEPEND" in cmds
    assert "VOLT:AC 220" in cmds
    assert "VOLT:AC 240" in cmds


def test_generic_not_chroma():
    g = _generic_scpi_three_phase_command_list("230", "50")
    assert "VOLT 230" in g
    assert "VOLT:AC" not in "".join(g)
    assert "CONF:COUP AC" not in g


def test_normalize_chroma_volt():
    assert _normalize_chroma_ac_write("VOLT 230.04") == "VOLT:AC 230"
    assert _normalize_chroma_ac_write("VOLT:AC 230.61") == "VOLT:AC 230.6"
    assert _normalize_ac_volt_command("VOLT 230.04") == "VOLT 230"


def test_append_chroma_rows():
    rows = []
    append_chroma_three_phase_setpoints(rows, "", "230", "", "50")
    writes = [r[2] for r in rows if r[1] == "write"]
    assert writes[0] == "CONF:COUP AC"
    assert "PHAS:THREE SAMEFREQ" in writes
    assert writes.count("VOLT:AC 230") == 4
    assert "INST:EDIT ALL" in writes
    assert "PHAS:THREE BALANCE" not in writes


def test_apply_setpoints_chroma_mock_handle():
    class _Log:
        def info(self, *a, **k):
            pass

        def warning(self, *a, **k):
            pass

        def error(self, *a, **k):
            pass

    class _H:
        def __init__(self):
            self.writes = []
            self.queries = []

        def write(self, c):
            self.writes.append(c)

        def query(self, q):
            self.queries.append(q)
            if q == "VOLT:AC?":
                return "230"
            if q == "OUTP?":
                return "1"
            return "0"

    ac = ACController(_Log(), lambda *a, **k: None, lambda: "t")
    h = _H()
    ac._set_handle(h)
    ac._store_idn("Chroma,61800-100,0,1.0")
    ac.apply_setpoints("230", "50", "三相")
    assert h.writes[0] == "CONF:COUP AC"
    assert "VOLT:AC 230" in h.writes
    assert "VOLT 230" not in h.writes
    assert any(q == "VOLT:AC?" for q in h.queries)


def main():
    test_idn_gate()
    test_chroma_three_phase_same_volt_sequence()
    test_chroma_three_phase_independ_when_diff()
    test_generic_not_chroma()
    test_normalize_chroma_volt()
    test_append_chroma_rows()
    test_apply_setpoints_chroma_mock_handle()
    print("ALL CHROMA 61800 CMD TESTS PASSED")


if __name__ == "__main__":
    main()
