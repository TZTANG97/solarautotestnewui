# -*- coding: utf-8 -*-
"""AC/DC/DEW 命令库运行时覆盖。"""
from __future__ import annotations

from utils.ac_scpi_commands import append_single_phase_setpoints
from utils.ac_source_catalog_sync import (
    clear_ac_source_overrides,
    get_ac_scpi_verb,
    set_ac_source_overrides,
)
from utils.dc_source_catalog_sync import (
    clear_dc_source_overrides,
    get_dc_mode_preamble,
    set_dc_source_overrides,
)
from utils.dew_catalog_sync import clear_dew_overrides, get_dew_acq_command, set_dew_overrides

_DEW_START_DEFAULT = "ACQUISITION:START"
_DEW_STOP_DEFAULT = "ACQUISITION:STOP"


def setup_function():
    clear_ac_source_overrides()
    clear_dc_source_overrides()
    clear_dew_overrides()


def teardown_function():
    clear_ac_source_overrides()
    clear_dc_source_overrides()
    clear_dew_overrides()


def test_ac_volt_verb_override_in_setpoints():
    set_ac_source_overrides({"VOLT": "VOLT:LIN"})
    assert get_ac_scpi_verb("VOLT", "VOLT") == "VOLT:LIN"
    rows = []
    append_single_phase_setpoints(rows, "230", "50", chroma_61800=False)
    volt_writes = [r[2] for r in rows if r[1] == "write" and "VOLT" in r[2]]
    assert any(w.startswith("VOLT:LIN ") for w in volt_writes)


def test_dc_mode_preamble_split_from_override():
    set_dc_source_overrides(
        "Chroma",
        {"dc_mode_preamble": "OUTP:MODE CURR\nIVCurve:SELect 2"},
    )
    pre = get_dc_mode_preamble("Chroma")
    assert pre == ["OUTP:MODE CURR", "IVCurve:SELect 2"]
    assert get_dc_mode_preamble("Itech") == ["SOL 0", "SOL 1"]


def test_dew_acq_start_stop_override():
    set_dew_overrides(
        {
            "dew_acq_start": ":ACQUISITION:START NOW",
            "dew_acq_stop": ":ACQUISITION:STOP",
        }
    )
    assert get_dew_acq_command("start", _DEW_START_DEFAULT) == ":ACQUISITION:START NOW"
    assert get_dew_acq_command("stop", _DEW_STOP_DEFAULT) == ":ACQUISITION:STOP"
    assert get_dew_acq_command("dew_acq_start", _DEW_START_DEFAULT) == ":ACQUISITION:START NOW"
