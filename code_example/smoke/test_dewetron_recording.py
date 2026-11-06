# -*- coding: utf-8 -*-
"""DEWETRON continuous vs split acquisition boundaries."""

from __future__ import annotations

from dewetron_autotest import DEWETRON_START_COMMAND, DEWETRON_STOP_COMMAND, make_wait_row
from utils.dewetron_recording import (
    apply_dewetron_recording_boundaries,
    is_measure_wait_row,
    resolve_dewetron_save_paths,
)


def test_continuous_wraps_whole_segment():
    body = [["AC", "write", "VOLT 230", "", "", "", "", "", "", ""]]
    rows = apply_dewetron_recording_boundaries(body, continuous=True)
    assert rows[0][2] == DEWETRON_START_COMMAND
    assert rows[-1][2] == DEWETRON_STOP_COMMAND
    assert len(rows) == 3


def test_split_wraps_each_measure_wait():
    body = [
        ["AC", "write", "VOLT 230", "", "", "", "", "", "", ""],
        make_wait_row(50),
        ["AC", "query", "*IDN?", "", "", "", "", "", 10, ""],
        make_wait_row(50),
    ]
    rows = apply_dewetron_recording_boundaries(body, continuous=False)
    starts = [r for r in rows if r[2] == DEWETRON_START_COMMAND]
    stops = [r for r in rows if r[2] == DEWETRON_STOP_COMMAND]
    assert len(starts) == 2
    assert len(stops) == 2
    assert is_measure_wait_row(make_wait_row(50))
    assert not is_measure_wait_row(make_wait_row(5))


def test_split_falls_back_without_measure_waits():
    body = [["AC", "write", "OUTP ON", "", "", "", "", "", "", ""]]
    rows = apply_dewetron_recording_boundaries(body, continuous=False)
    assert rows[0][2] == DEWETRON_START_COMMAND
    assert rows[-1][2] == DEWETRON_STOP_COMMAND


def test_resolve_save_paths_continuous_and_split():
    cont = resolve_dewetron_save_paths(
        test_type="reconnection",
        continuous=True,
        file_names=["Reconn_BR"],
        stamp="20260905_120000",
    )
    assert len(cont) == 1
    assert "Reconn_BR_20260905_120000.csv" in cont[0].replace("\\", "/")

    split = resolve_dewetron_save_paths(
        test_type="reconnection",
        continuous=False,
        file_names=["Reconn_S3", "Reconn_S4"],
        stamp="20260905_120000",
    )
    assert len(split) == 2
    assert split[0].endswith("Reconn_S3_20260905_120000_01.csv") or split[0].endswith(
        "Reconn_S3_20260905_120000_01.csv".replace("/", "\\")
    )
