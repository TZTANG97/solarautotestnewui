# -*- coding: utf-8 -*-
"""Oxygen :STORE 工具与跳脱值检测单测（STORE 默认关闭）。"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from devices.dewetron_data_collector import DewetronDataCollector
from utils.dewetron_oxygen_store import (
    build_oxygen_store_path,
    format_abs_time_for_csv,
    oxygen_store_path_candidates,
    parse_store_file_name_response,
    parse_store_state_response,
    scpi_store_file_name,
    store_state_is_active,
    trip_wall_clock_from_gather_start,
)
from utils.dewetron_trip_monitor import (
    extract_trip_values,
    format_trip_value_log,
)


class FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)


class FakeController:
    def __init__(self, channels=None):
        self.connected = True
        self.channels = channels or [
            "U1_tRMS@AC",
            "I1_tRMS@AC",
            "I2_tRMS@AC",
            "I3_tRMS@AC",
            "F_fund@AC",
        ]
        self.state = "Stopped"
        self.store_state = "Stopped"
        self.store_file = None
        self.numeric_items = ""
        self.values = []
        self.sent = []

    def query_command(self, command, timeout_ms=30000):
        if command == ":CHANNELLIST:NAMES?":
            return ",".join(
                f'"{i}","{ch}"' for i, ch in enumerate(self.channels, start=1)
            )
        if command == ":ACQUISITION:STATE?":
            return self.state
        if command == ":NUM:NORM:ITEMs?":
            return self.numeric_items
        if command == ":RATE?":
            return "100ms"
        if command == ":STORE:STATE?":
            return f":STOR:STAT {self.store_state}"
        if command == ":STORE:WAVEFORM:MODE?":
            return getattr(self, "waveform_mode", "Continuous")
        if command == ":STORE:SAFTer?":
            return "OFF,0"
        if command == ":STORE:FILE:NAME?":
            if self.store_state == "Stopped" or not self.store_file:
                return ":STOR:FILE NONE"
            return f':STOR:FILE "{self.store_file}"'
        if command == ":SYSTEM:ERROR:ALL?":
            return '0,"No error"'
        if command == ":NUM:NORM:VALue?":
            if not self.values:
                return None
            return self.values.pop(0)
        return None

    def send_command(self, command, *args, **kwargs):
        self.sent.append(command)
        if command.startswith(":NUM:NORM:ITEMs "):
            self.numeric_items = command.split(" ", 1)[1]
        if command.startswith(":STORE:FILE:NAME "):
            if '"' in command:
                self.store_file = command.split('"', 2)[1]
        if command in (
            ":STORE:WAVEFORM:CONTINUOUS",
            ":STORE:WAVEFORM:MODE Continuous",
            ":STORE:SAFTer OFF",
            ":STORE:SAFTer OFF,0",
            ":STORE:RACQuisition OFF",
        ):
            self.waveform_mode = "Continuous"
            return True
        if command == ":STORE:START":
            if self.store_file:
                self.store_state = "Started"
        if command == ":STORE:STOP":
            self.store_state = "Stopped"
        return True

    def stop_acquisition(self):
        self.sent.append(":ACQUISITION:STOP")
        self.state = "Stopped"
        return True


def test_build_oxygen_store_path_beside_csv(tmp_path):
    csv_path = str(tmp_path / "voltage-frequency-protection_20260921_141738.csv")
    path = build_oxygen_store_path(csv_path)
    assert path.endswith("voltage-frequency-protection_20260921_141738_oxygen")
    assert "\\" in path or path.startswith(str(tmp_path))
    cmd = scpi_store_file_name(path)
    assert cmd.startswith(':STORE:FILE:NAME "')
    # 官方示例用正斜杠绝对路径
    assert "/" in cmd
    assert "\\" not in cmd.split('"', 2)[1]


def test_parse_store_responses_match_docs():
    assert parse_store_file_name_response(':STOR:FILE "D:\\DATA\\Testrun_1.dmd"') == (
        r"D:\DATA\Testrun_1.dmd"
    )
    assert parse_store_file_name_response(":STOR:FILE NONE") is None
    assert parse_store_state_response(":STOR:STAT Stopped") == "Stopped"
    assert parse_store_state_response("Started") == "Started"
    assert store_state_is_active("Started")
    assert store_state_is_active("Armed")
    assert not store_state_is_active("Stopped")
    assert not store_state_is_active("Stopping")


def test_candidates_prefer_csv_absolute_path(tmp_path):
    csv_path = str(tmp_path / "ovuf_demo.csv")
    cands = oxygen_store_path_candidates(csv_path)
    assert cands[0].replace("\\", "/").endswith("ovuf_demo_oxygen")
    assert "/" in cands[0]
    assert cands[-1] == "ovuf_demo_oxygen"


def test_format_abs_time_for_csv_excel_friendly():
    assert (
        format_abs_time_for_csv("2017-08-28T13:17:26.9715+00:00")
        == "2017/08/28 13:17:26.9715"
    )
    assert format_abs_time_for_csv("2025-12-17T16:58:07.6") == "2025/12/17 16:58:07.6"
    assert format_abs_time_for_csv("2025/12/17 16:58:07") == "2025/12/17 16:58:07"


def test_format_trip_value_log_shows_uf():
    line = format_trip_value_log(
        wall_clock="14:21:08",
        elapsed_s=45.2,
        reason="I_mean 10.100A -> 0.050A",
        trip_values={"u_v": 253.1, "f_hz": 50.2, "i_mean": 0.05},
    )
    assert "14:21:08" in line
    assert "U=253.100V" in line
    assert "F=50.200Hz" in line
    assert "跳脱值" in line


def test_extract_trip_values_from_sample():
    names = ["U1_tRMS", "U2_tRMS", "U3_tRMS", "I1_tRMS", "F_fund"]
    vals = [253.0, 252.0, 254.0, 0.1, 50.25]
    tv = extract_trip_values(vals, names)
    assert abs(tv["u_v"] - 253.0) < 1e-6
    assert abs(tv["f_hz"] - 50.25) < 1e-6


def test_trip_wall_clock_from_gather_start():
    wall, unix = trip_wall_clock_from_gather_start(1_000_000.0, 12.5)
    assert len(wall.split(":")) == 3
    assert abs(unix - (1_000_000.0 + 12.5)) < 1e-6


def test_collector_does_not_start_oxygen_store_by_default(tmp_path):
    ctrl = FakeController()
    ui_lines = []
    collector = DewetronDataCollector(
        ctrl, FakeLogger(), db_path=str(tmp_path / "store.sqlite")
    )
    collector.set_ui_notify(ui_lines.append)
    csv_path = str(tmp_path / "ovuf.csv")
    assert collector.prepare(
        ["U1_tRMS", "I1_tRMS", "I2_tRMS", "I3_tRMS"],
        "100",
        "voltage-frequency-protection",
        csv_path,
    ).success
    assert collector.begin_run()
    with patch("devices.dewetron_data_collector.time.sleep"):
        assert collector.start_gathering()
        ctrl.state = "Started"
        assert collector.on_acquisition_started()
    assert ":STORE:START" not in ctrl.sent
    assert not collector._oxygen_store_active
    collector.stop_gathering()
    collector.stop()


def test_collector_starts_oxygen_store_when_keep_dmd(tmp_path):
    ctrl = FakeController()
    ui_lines = []
    collector = DewetronDataCollector(
        ctrl, FakeLogger(), db_path=str(tmp_path / "keep_dmd.sqlite")
    )
    collector.set_ui_notify(ui_lines.append)
    csv_path = str(tmp_path / "keep.csv")
    assert collector.prepare(
        ["U1_tRMS", "I1_tRMS", "I2_tRMS", "I3_tRMS"],
        "100",
        "voltage-frequency-protection",
        csv_path,
        keep_oxygen_dmd=True,
    ).success
    assert collector.begin_run()
    with patch("devices.dewetron_data_collector.time.sleep"):
        assert collector.start_gathering()
        ctrl.state = "Started"
        assert collector.on_acquisition_started()
    assert any(c == ":STORE:START" for c in ctrl.sent)
    assert any(c == ":STORE:WAVEFORM:CONTINUOUS" for c in ctrl.sent)
    assert any(c == ":STORE:WAVEFORM:MODE Continuous" for c in ctrl.sent)
    assert any(c == ":STORE:SAFTer OFF" for c in ctrl.sent)
    assert collector._oxygen_store_active
    # 路径应优先落在 CSV 同目录，而不是仅文件名
    assert "/" in (ctrl.store_file or "") or "\\" in (ctrl.store_file or "")
    with patch("devices.dewetron_data_collector.time.sleep"), patch(
        "utils.dewetron_oxygen_store.preserve_oxygen_dmd_beside_csv",
        return_value=(True, str(tmp_path / "keep_oxygen.dmd")),
    ):
        collector.stop_gathering()
    assert any("已保留原始 .dmd" in line for line in ui_lines)
    # stop 后再调 stop() 不应重复发 STORE:STOP
    stop_count = sum(1 for c in ctrl.sent if c == ":STORE:STOP")
    collector.stop()
    assert sum(1 for c in ctrl.sent if c == ":STORE:STOP") == stop_count


def test_preserve_oxygen_dmd_beside_csv(tmp_path):
    from utils.dewetron_oxygen_store import preserve_oxygen_dmd_beside_csv

    src_dir = tmp_path / "oxygen_src"
    src_dir.mkdir()
    src = src_dir / "run_oxygen.dmd"
    src.write_bytes(b"oxygen")
    csv_path = str(tmp_path / "out" / "run.csv")
    ok, msg = preserve_oxygen_dmd_beside_csv(str(src.with_suffix("")), csv_path)
    assert ok
    assert Path(msg).is_file()
    assert Path(msg).read_bytes() == b"oxygen"


def test_trip_writes_value_log_without_png_or_marker(tmp_path):
    ctrl = FakeController()
    ui_lines = []
    collector = DewetronDataCollector(
        ctrl, FakeLogger(), db_path=str(tmp_path / "trip.sqlite")
    )
    collector.set_ui_notify(ui_lines.append)
    collector._trip_screenshot_enabled = True
    collector._trip_render_period_png = False
    collector._trip_capture_oxygen = False
    collector._trip_startup_ignore_s = 0.0
    collector._trip_arm_hold_s = 0.0
    csv_path = str(tmp_path / "trip.csv")
    assert collector.prepare(
        ["U1_tRMS", "I1_tRMS", "I2_tRMS", "I3_tRMS", "F_fund"],
        "100",
        "voltage-frequency-protection",
        csv_path,
    ).success
    assert collector._trip_monitor is not None
    assert collector.begin_run()
    collector._gather_start_time = 1_000_000.0
    with patch("devices.dewetron_data_collector.time.sleep"):
        for _ in range(6):
            collector._maybe_trip_screenshot([253.0, 10.0, 10.0, 10.0, 50.1])
        collector._maybe_trip_screenshot([253.0, 0.0, 0.0, 0.0, 50.1])
        collector._maybe_trip_screenshot([253.0, 0.0, 0.0, 0.0, 50.1])
    assert collector._trip_event_count >= 1
    assert any("[DEWETRON][跳脱]" in x and "U=" in x for x in ui_lines)
    assert not any(c.startswith(":MARKER:ADD") for c in ctrl.sent)
    assert list(Path(tmp_path).glob("*trip_period*.png")) == []
    tv = collector._trip_events[0]["trip_values"]
    assert abs(tv["u_v"] - 253.0) < 1e-6
    assert abs(tv["f_hz"] - 50.1) < 1e-6
    collector.stop()
