# -*- coding: utf-8 -*-
"""DEWETRON continuous vs split acquisition boundaries."""

from __future__ import annotations

from dewetron_autotest import DEWETRON_START_COMMAND, DEWETRON_STOP_COMMAND, make_wait_row
from utils.dewetron_recording import (
    apply_dewetron_recording_boundaries,
    ensure_dewetron_acq_boundaries,
    is_measure_wait_row,
    resolve_dewetron_save_paths,
    trim_leading_all_nan_samples,
)


def test_ensure_acq_boundaries_fills_missing_start_stop():
    body = [["AC", "write", "VOLT 230", "", "", "", "", "", "", ""]]
    rows = ensure_dewetron_acq_boundaries(body)
    assert rows[0][2] == DEWETRON_START_COMMAND
    assert rows[-1][2] == DEWETRON_STOP_COMMAND
    assert len(rows) == 3


def test_ensure_acq_boundaries_keeps_existing():
    body = [
        ["DEWETRON", "write", DEWETRON_START_COMMAND, "", "", "", "", "", "", ""],
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["DEWETRON", "write", DEWETRON_STOP_COMMAND, "", "", "", "", "", "", ""],
    ]
    rows = ensure_dewetron_acq_boundaries(body)
    assert len(rows) == 3
    assert rows[0][2] == DEWETRON_START_COMMAND
    assert rows[-1][2] == DEWETRON_STOP_COMMAND


def test_continuous_wraps_whole_segment():
    body = [["AC", "write", "VOLT 230", "", "", "", "", "", "", ""]]
    rows = apply_dewetron_recording_boundaries(body, continuous=True)
    assert rows[0][2] == DEWETRON_START_COMMAND
    assert rows[-1][2] == DEWETRON_STOP_COMMAND
    assert len(rows) == 3


def test_continuous_starts_after_startup_wait_not_at_head():
    """缺 ASYNC_START 时也不能把 START 插到启机前（否则启机阶段狂采）。"""
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["DC1", "write", "SAS:MODE TABL", "", "", "", "", "", "", ""],
        ["DC1", "write", "OUTP ON", "", "", "", "", "", "", ""],
        # 启机等待 10s（query *IDN? col9）
        ["AC", "query", "*IDN?", "", "", "", "", "", "", 100],
        ["DC1", "write", "SAS:TABL:ACT 1", "", "", "", "", "", "", ""],
        # 测量驻留
        ["AC", "query", "*IDN?", "", "", "", "", "", "", 50],
    ]
    rows = apply_dewetron_recording_boundaries(body, continuous=True)
    starts = [i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND]
    assert len(starts) == 1
    assert rows[0][2] == "OUTP ON"
    # START 在启机等待之后、测量之前
    assert starts[0] == 4
    assert rows[3][2] == "*IDN?"
    assert rows[4][2] == DEWETRON_START_COMMAND


def test_continuous_keeps_existing_start_from_async_marker():
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["DEWETRON", "write", DEWETRON_START_COMMAND, "", "", "", "", "", "", ""],
        ["AC", "wait", "", "", "", "", "", "", "", 50],
        ["DEWETRON", "write", DEWETRON_STOP_COMMAND, "", "", "", "", "", "", ""],
    ]
    rows = apply_dewetron_recording_boundaries(body, continuous=True)
    starts = [r for r in rows if r[2] == DEWETRON_START_COMMAND]
    assert len(starts) == 1
    assert rows[0][2] == "OUTP ON"
    assert rows[1][2] == DEWETRON_START_COMMAND


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


def test_resolve_save_paths_continuous_and_split(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    cont = resolve_dewetron_save_paths(
        test_type="reconnection",
        continuous=True,
        file_names=["Reconn_BR"],
        stamp="20260905_120000",
        base_dir=str(tmp_path / "dew"),
    )
    assert len(cont) == 1
    assert "Reconn_BR_20260905_120000.csv" in cont[0].replace("\\", "/")

    split = resolve_dewetron_save_paths(
        test_type="reconnection",
        continuous=False,
        file_names=["Reconn_S3", "Reconn_S4"],
        stamp="20260905_120000",
        base_dir=str(tmp_path / "dew"),
    )
    assert len(split) == 2
    assert "Reconn_S3_20260905_120000_01.csv" in split[0].replace("\\", "/")

    # 分开录：文件名少于段数时按 segment_count 补齐，避免多轮覆盖同一文件
    padded = resolve_dewetron_save_paths(
        test_type="reconnection",
        continuous=False,
        file_names=["Reconn_S3"],
        stamp="20260905_120000",
        base_dir=str(tmp_path / "dew"),
        segment_count=3,
    )
    assert len(padded) == 3
    assert len(set(padded)) == 3

    empty_split = resolve_dewetron_save_paths(
        test_type="reconnection",
        continuous=False,
        file_names=[],
        stamp="20260905_120000",
        base_dir=str(tmp_path / "dew"),
        segment_count=2,
    )
    assert len(empty_split) == 2
    assert empty_split[0] != empty_split[1]


def test_ensure_dewetron_path_at_does_not_reuse(tmp_path, monkeypatch):
    from utils.dewetron_recording import ensure_dewetron_path_at

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    base = str(tmp_path / "dew")
    paths, p0 = ensure_dewetron_path_at(
        [], 0, test_type="ovuf", base_dir=base, stamp="20260905_120000"
    )
    assert p0.endswith("_01.csv")
    paths2, p1 = ensure_dewetron_path_at(
        paths, 1, test_type="ovuf", base_dir=base, stamp="20260905_120000"
    )
    assert p1 != p0
    assert len(paths2) >= 2


def test_trim_leading_all_nan_and_rebase_time():
    rows = [
        (0.0, [float("nan"), float("nan")]),
        (0.1, [float("nan"), float("nan")]),
        (0.409, [230.1, 0.16]),
        (0.509, [230.2, 0.17]),
    ]
    got = trim_leading_all_nan_samples(rows, rebase_time=True)
    assert len(got) == 2
    assert abs(got[0][0] - 0.0) < 1e-9
    assert abs(got[1][0] - 0.1) < 1e-9
    assert got[0][1][0] == 230.1


def test_trim_keeps_partial_nan_rows():
    rows = [
        (0.0, [230.0, float("nan")]),
        (0.1, [231.0, 1.0]),
    ]
    got = trim_leading_all_nan_samples(rows, rebase_time=True)
    assert len(got) == 2
    assert got[0][1][0] == 230.0


def test_trim_no_drop_keeps_absolute_time():
    rows = [
        (1.0, [12.5]),
        (2.0, [13.0]),
    ]
    got = trim_leading_all_nan_samples(rows, rebase_time=True)
    assert abs(got[0][0] - 1.0) < 1e-9
    assert abs(got[1][0] - 2.0) < 1e-9
