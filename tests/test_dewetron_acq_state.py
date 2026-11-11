# -*- coding: utf-8 -*-
"""DEWETRON 采集 STATE 解析与延迟 Started 等待。"""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from devices.dewetron_data_collector import DewetronDataCollector
from tests.test_dewetron_runtime import FakeController, FakeLogger
from utils.dewetron_acq_state import (
    acq_state_is_idle,
    acq_state_is_started,
    normalize_acq_state,
)


@pytest.mark.parametrize(
    "raw,want",
    [
        (":ACQUISITION:STATE Started", "started"),
        ("Stopped", "stopped"),
        ("Stopping", "stopping"),
        (":ACQ:STAT Armed", "armed"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_acq_state(raw, want):
    assert normalize_acq_state(raw) == want
    if want == "started":
        assert acq_state_is_started(raw)
    if want == "stopped":
        assert acq_state_is_idle(raw)


def test_on_acquisition_started_accepts_delayed_state(tmp_path):
    controller = FakeController(channels=["U1_tRMS@AC"])
    collector = DewetronDataCollector(
        controller, FakeLogger(), db_path=str(tmp_path / "delay.sqlite")
    )
    assert collector.prepare(
        ["U1_tRMS"], "100", "flicker", str(tmp_path / "a.csv")
    ).success
    assert collector.begin_run()
    assert collector.start_gathering()

    controller.state = "Stopped"
    polls = {"n": 0}
    orig = controller.query_command

    def query(command, timeout_ms=30000):
        if command == ":ACQUISITION:STATE?":
            polls["n"] += 1
            if polls["n"] >= 3:
                controller.state = "Started"
        return orig(command, timeout_ms=timeout_ms)

    controller.query_command = query
    assert collector.on_acquisition_started(
        timeout_s=2.0, poll_s=0.05, retry_start=False
    )
    assert collector.is_gather.is_set()
    assert polls["n"] >= 3
    collector.stop()


def test_on_acquisition_started_retries_start_when_stuck_stopped(tmp_path):
    controller = FakeController(channels=["U1_tRMS@AC"])
    collector = DewetronDataCollector(
        controller, FakeLogger(), db_path=str(tmp_path / "retry.sqlite")
    )
    assert collector.prepare(
        ["U1_tRMS"], "100", "flicker", str(tmp_path / "b.csv")
    ).success
    assert collector.begin_run()
    assert collector.start_gathering()
    controller.state = "Stopped"

    def start():
        controller.sent.append(":ACQUISITION:START")
        controller.state = "Started"
        return True

    controller.start_acquisition = start
    assert collector.on_acquisition_started(timeout_s=0.6, poll_s=0.05)
    assert ":ACQUISITION:START" in controller.sent
    assert collector.is_gather.is_set()
    collector.stop()


def test_start_gathering_survives_empty_state_then_setup(tmp_path):
    """STATE? 暂时空不得直接判 NUMERIC/RATE 失败（1453 回归）。"""
    controller = FakeController(channels=["U1_tRMS@AC"])
    collector = DewetronDataCollector(
        controller, FakeLogger(), db_path=str(tmp_path / "empty_state.sqlite")
    )
    assert collector.prepare(
        ["U1_tRMS"], "100", "flicker", str(tmp_path / "c.csv")
    ).success
    assert collector.begin_batch("flicker", str(tmp_path / "c.csv"))

    polls = {"n": 0}
    orig = controller.query_command

    def query(command, timeout_ms=30000):
        if command == ":ACQUISITION:STATE?":
            polls["n"] += 1
            if polls["n"] <= 2:
                return None
            return "Stopped"
        return orig(command, timeout_ms=timeout_ms)

    controller.query_command = query
    assert collector.start_gathering()
    assert collector._ready_to_gather
    assert not collector._last_gather_error
    collector.stop()


def test_start_gathering_retries_numeric_after_first_fail(tmp_path):
    controller = FakeController(channels=["U1_tRMS@AC"])
    collector = DewetronDataCollector(
        controller, FakeLogger(), db_path=str(tmp_path / "num_retry.sqlite")
    )
    assert collector.prepare(
        ["U1_tRMS"], "100", "flicker", str(tmp_path / "d.csv")
    ).success
    assert collector.begin_batch("flicker", str(tmp_path / "d.csv"))
    fails = {"n": 0}
    orig_send = controller.send_command

    def send(command, *args, **kwargs):
        if str(command).startswith(":NUM:NORM:ITEMs "):
            fails["n"] += 1
            if fails["n"] == 1:
                return False
        return orig_send(command, *args, **kwargs)

    controller.send_command = send
    assert collector.start_gathering()
    assert fails["n"] >= 2
    collector.stop()
