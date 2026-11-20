# -*- coding: utf-8 -*-
"""DEWETRON continuous vs split acquisition boundaries."""

from __future__ import annotations

from dewetron_autotest import DEWETRON_START_COMMAND, DEWETRON_STOP_COMMAND, make_wait_row
from utils.dewetron_recording import (
    apply_dewetron_recording_boundaries,
    apply_recording_lead,
    dewetron_row_project,
    ensure_dewetron_acq_boundaries,
    is_measure_wait_row,
    is_project_gap_wait,
    is_record_lead_wait,
    make_acq_start_row,
    make_acq_stop_row,
    resolve_dewetron_save_paths,
    stamp_dewetron_project,
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


def test_continuous_fallback_starts_after_ovuf_boot_not_after_outp():
    """没有扫点标记时，也不能在 OUTP ON 后、启机结束前开录。"""
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", 30],
        ["AC", "query", "*IDN?", "", "", "", "", "", 2, 10],
        ["AC", "wait", "OVUF_BOOT", "", "", "", "", "", "", 3000],
        ["AC", "write", "VOLT 220", "", "", "", "", "", "", ""],
        ["AC", "query", "*IDN?", "", "", "", "", "", "", 15],
    ]
    rows = apply_dewetron_recording_boundaries(body, continuous=True)
    start = next(i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND)
    boot = next(i for i, r in enumerate(rows) if r[2] == "OVUF_BOOT")
    assert start == boot + 1
    assert rows[-1][2] == DEWETRON_STOP_COMMAND


def test_split_keeps_sweep_window_and_does_not_record_boot():
    """过欠压已标好扫段时，分开录不能再把启机等待包成一对 START/STOP。"""
    boot = ["AC", "wait", "OVUF_BOOT", "", "", "", "", "", "", 600]
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        boot,
        ["AC", "write", "VOLT 230", "", "", "", "", "", "", ""],
        ["DEWETRON", "write", DEWETRON_START_COMMAND, "", "", "", "", "", "", ""],
        ["AC", "wait", "IDN_NOP", "", "", "", "", "", "", 50],
        ["AC", "write", "VOLT 200", "", "", "", "", "", "", ""],
        ["AC", "wait", "IDN_NOP", "", "", "", "", "", "", 50],
        ["DEWETRON", "write", DEWETRON_STOP_COMMAND, "", "", "", "", "", "", ""],
        ["AC", "write", "VOLT 230", "", "", "", "", "", "", ""],
    ]
    rows = apply_dewetron_recording_boundaries(body, continuous=False)
    starts = [i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND]
    stops = [i for i, r in enumerate(rows) if r[2] == DEWETRON_STOP_COMMAND]
    assert starts == [3]
    assert stops == [7]
    assert rows[1][2] == "OVUF_BOOT"
    assert rows[starts[0] - 1][2] == "VOLT 230"
    assert rows[stops[0] + 1][2] == "VOLT 230"
    assert rows[stops[0] - 2][2] == "VOLT 200"


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


def test_two_second_dwell_is_still_a_recording():
    """测量驻留正好 2 秒时仍要开录。不能因为和跨项缝一样长就跳过。"""
    dwell = make_wait_row(20)
    assert is_measure_wait_row(dwell)
    assert not is_project_gap_wait(dwell)
    rows = apply_dewetron_recording_boundaries([dwell], continuous=False)
    starts = [r for r in rows if r[2] == DEWETRON_START_COMMAND]
    stops = [r for r in rows if r[2] == DEWETRON_STOP_COMMAND]
    assert len(starts) == 1
    assert len(stops) == 1
    assert rows[1][9] == 20


def test_project_gap_is_not_a_recording_segment():
    """只有明确的 PROJECT_GAP 不算录波；后面的 2 秒测量和长驻留各自成段。"""
    gap = ["AC", "wait", "PROJECT_GAP", "", "", "", "", "", "", 20]
    short = make_wait_row(20)
    long = make_wait_row(1800)
    body = [
        gap,
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        short,
        ["DC1", "write", "IVC:IT 1", "", "", "", "", "", "", ""],
        long,
    ]
    assert is_project_gap_wait(gap)
    assert not is_measure_wait_row(gap)
    rows = apply_dewetron_recording_boundaries(body, continuous=False)
    starts = [i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND]
    assert len(starts) == 2
    assert rows[0][2] == "PROJECT_GAP"
    assert rows[starts[0] - 1][2] == "OUTP ON"
    assert rows[starts[0] + 1][9] == 20
    assert rows[starts[1] + 1][9] == 1800

    ovuf = stamp_dewetron_project(
        [make_acq_start_row(), make_wait_row(600), make_acq_stop_row()],
        "过欠压_过欠频",
    )
    pf = stamp_dewetron_project(
        [make_acq_start_row(), make_wait_row(600), make_acq_stop_row()],
        "固定PF=1",
    )
    assert dewetron_row_project(ovuf[0]) == "过欠压_过欠频"
    assert dewetron_row_project(pf[0]) == "固定PF=1"
    assert dewetron_row_project(ovuf[1]) == ""

    stamped = stamp_dewetron_project(rows, "过欠压_过欠频")
    owners = [dewetron_row_project(r) for r in stamped if r[0] == "DEWETRON"]
    assert owners
    assert set(owners) == {"过欠压_过欠频"}


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

    # 同一秒追加的两个项目各用各的试验名，过欠压不会写成 fixed-pf
    ovuf_paths = resolve_dewetron_save_paths(
        test_type="voltage-frequency-protection",
        continuous=True,
        file_names=[],
        stamp="20261119_222525",
        base_dir=str(tmp_path / "dew"),
    )
    pf_paths = resolve_dewetron_save_paths(
        test_type="fixed-pf",
        continuous=False,
        file_names=["FixedPF_P80", "FixedPF_P100"],
        stamp="20261119_222525",
        base_dir=str(tmp_path / "dew"),
        segment_count=2,
    )
    assert "voltage-frequency-protection_20261119_222525.csv" in ovuf_paths[0].replace("\\", "/")
    assert "FixedPF_P80_20261119_222525_01.csv" in pf_paths[0].replace("\\", "/")
    assert "fixed-pf" not in ovuf_paths[0]
    assert set(ovuf_paths).isdisjoint(pf_paths)


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


def _rows_after_boot(body, lead_s):
    bounded = apply_dewetron_recording_boundaries(body, continuous=True)
    return apply_recording_lead(bounded, lead_s)


def test_zero_lead_keeps_start_immediately_after_boot():
    """提前 0 秒时，开录仍紧跟整段启机，和过欠压现在的窗口一致。"""
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["AC", "wait", "OVUF_BOOT", "", "", "", "", "", "", 1200],
        ["AC", "write", "VOLT 207", "", "", "", "", "", "", ""],
        ["AC", "wait", "IDN_NOP", "", "", "", "", "", "", 300],
    ]
    rows, note = _rows_after_boot(body, 0)
    start = next(i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND)
    boot = next(i for i, r in enumerate(rows) if r[2] == "OVUF_BOOT")
    assert note == ""
    assert start == boot + 1
    assert rows[boot][9] == 1200
    assert not any(is_record_lead_wait(r) for r in rows)


def test_lead_is_carved_from_the_end_of_startup():
    """提前 30 秒：启机少 30 秒，开录后先录这 30 秒并网，再进入试验动作。"""
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["AC", "query", "*IDN?", "", "", "", "", "", "", 1000],
        ["AC", "write", "VOLT 207", "", "", "", "", "", "", ""],
        ["AC", "wait", "IDN_NOP", "", "", "", "", "", "", 300],
    ]
    rows, note = _rows_after_boot(body, 30)
    start = next(i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND)
    boot = next(i for i, r in enumerate(rows) if r[2] == "*IDN?")
    assert "提前 30s 开录" in note
    assert rows[boot][9] == 700
    assert start == boot + 1
    assert is_record_lead_wait(rows[start + 1])
    assert rows[start + 1][9] == 300
    assert rows[start + 2][2] == "VOLT 207"
    assert rows[boot][9] + rows[start + 1][9] == 1000
    assert not is_measure_wait_row(rows[start + 1])
    assert not is_project_gap_wait(rows[start + 1])


def test_lead_longer_than_startup_is_clamped_to_startup():
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["AC", "wait", "OVUF_BOOT", "", "", "", "", "", "", 100],
        ["AC", "write", "VOLT 207", "", "", "", "", "", "", ""],
    ]
    rows, note = _rows_after_boot(body, 30)
    boot = next(i for i, r in enumerate(rows) if r[2] == "OVUF_BOOT")
    start = next(i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND)
    assert "超过启机" in note
    assert rows[boot][9] == 0
    assert start == boot + 1
    assert rows[start + 1][9] == 100
    assert rows[0][2] == "OUTP ON"


def test_lead_without_startup_does_not_move_start():
    body = [
        ["AC", "write", "VOLT 230", "", "", "", "", "", "", ""],
        ["AC", "wait", "IDN_NOP", "", "", "", "", "", "", 50],
    ]
    rows, note = _rows_after_boot(body, 10)
    start = next(i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND)
    assert note == "没有启机等待，提前录制未生效"
    assert rows[start + 1][9] == 50
    assert not any(is_record_lead_wait(r) for r in rows)


def test_split_lead_only_shifts_the_first_file():
    boot = ["AC", "wait", "OVUF_BOOT", "", "", "", "", "", "", 600]
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        boot,
        ["AC", "write", "VOLT 230", "", "", "", "", "", "", ""],
        ["DEWETRON", "write", DEWETRON_START_COMMAND, "", "", "", "", "", "", ""],
        ["AC", "wait", "IDN_NOP", "", "", "", "", "", "", 50],
        ["DEWETRON", "write", DEWETRON_STOP_COMMAND, "", "", "", "", "", "", ""],
        ["AC", "write", "VOLT 200", "", "", "", "", "", "", ""],
        ["DEWETRON", "write", DEWETRON_START_COMMAND, "", "", "", "", "", "", ""],
        ["AC", "wait", "IDN_NOP", "", "", "", "", "", "", 50],
        ["DEWETRON", "write", DEWETRON_STOP_COMMAND, "", "", "", "", "", "", ""],
    ]
    rows, note = apply_recording_lead(
        apply_dewetron_recording_boundaries(body, continuous=False),
        10,
    )
    starts = [i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND]
    assert len(starts) == 2
    assert "提前 10s 开录" in note
    assert rows[1][2] == "OVUF_BOOT"
    assert rows[1][9] == 500
    assert starts[0] == 2
    assert is_record_lead_wait(rows[3])
    assert rows[3][9] == 100
    assert rows[starts[1] - 1][2] == "VOLT 200"
    assert rows[starts[1] + 1][2] == "IDN_NOP"


def test_start_before_boot_moves_to_after_startup_even_without_lead():
    body = [
        ["DEWETRON", "write", DEWETRON_START_COMMAND, "", "", "", "", "", "", ""],
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["AC", "wait", "OVUF_BOOT", "", "", "", "", "", "", 800],
        ["AC", "write", "VOLT 220", "", "", "", "", "", "", ""],
        ["DEWETRON", "write", DEWETRON_STOP_COMMAND, "", "", "", "", "", "", ""],
    ]
    rows, note = apply_recording_lead(body, 0)
    start = next(i for i, r in enumerate(rows) if r[2] == DEWETRON_START_COMMAND)
    boot = next(i for i, r in enumerate(rows) if r[2] == "OVUF_BOOT")
    assert note == "开录已挪到启机结束之后"
    assert start == boot + 1
    assert rows[boot][9] == 800
    assert not any(is_record_lead_wait(r) for r in rows)


def test_recording_lead_is_not_applied_twice():
    body = [
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", ""],
        ["AC", "wait", "OVUF_BOOT", "", "", "", "", "", "", 600],
        ["AC", "write", "VOLT 230", "", "", "", "", "", "", ""],
    ]
    once, _note = _rows_after_boot(body, 20)
    twice, note = apply_recording_lead(once, 20)
    assert note == ""
    assert twice == once


def test_record_lead_round_trips_in_dewetron_config():
    from dewetron_autotest import parse_dewetron_config, serialize_dewetron_config
    from components.dewetron_autotest_panel import DewetronUiConfig

    config = DewetronUiConfig("20", 3, False, ["U1_tRMS"], record_lead_s=15)
    restored = parse_dewetron_config(serialize_dewetron_config(config))
    assert restored.record_lead_s == 15
    assert restored == config
    assert DewetronUiConfig("20", 3, False, ["U1_tRMS"]).record_lead_s == 0
    assert "提前录制秒数不能为负数" in DewetronUiConfig(
        record_lead_s=-1
    ).validation_errors(require_export_fields=False)
