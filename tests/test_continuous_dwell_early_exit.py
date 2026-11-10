# -*- coding: utf-8 -*-
"""连续录 col9 驻留：录波结束 / 请求停表 / 截止时刻应立刻跳过。"""

from __future__ import annotations

import sys
import time
from types import SimpleNamespace

import pytest


@pytest.fixture
def sw_module():
    import SCPITestWave as sw

    if not hasattr(sw, "logger"):
        class _L:
            def info(self, *a, **k):
                pass

            def error(self, *a, **k):
                pass

            def warning(self, *a, **k):
                pass

        sw.logger = _L()
    sw._wt_async_session_active = False
    sw._wt_async_stop_requested = False
    sw._wt_async_deadline_ts = 0.0
    sw.test_status = ""
    sw.strTestStatusFlag = ""
    return sw


def test_wait_command_dwell_skips_when_async_measure_done(sw_module, monkeypatch):
    sw = sw_module
    sw._wt_async_session_active = True
    sw.test_status = "0"
    slept = []
    monkeypatch.setattr(time, "sleep", lambda s: slept.append(s))
    sw._wait_command_dwell_01s(26, 600, log_tag="query,col9")
    assert slept == []
    assert sw.test_status == "0"


def test_wait_command_dwell_full_when_not_in_async_session(sw_module, monkeypatch):
    sw = sw_module
    sw._wt_async_session_active = False
    sw.test_status = "0"
    slept = []
    monkeypatch.setattr(time, "sleep", lambda s: slept.append(s))
    sw._wait_command_dwell_01s(3, 5, log_tag="write,col9")
    assert slept == [0.1, 0.1, 0.1, 0.1, 0.1]


def test_wait_command_dwell_exits_midway_when_measure_ends(sw_module, monkeypatch):
    sw = sw_module
    sw._wt_async_session_active = True
    sw.test_status = "1"
    ticks = {"n": 0}

    def _fake_sleep(_sec):
        ticks["n"] += 1
        if ticks["n"] >= 3:
            sw.test_status = "0"

    monkeypatch.setattr(time, "sleep", _fake_sleep)
    sw._wait_command_dwell_01s(10, 100, log_tag="query,col9")
    assert ticks["n"] == 3
    assert sw.test_status == "0"


def test_wait_command_dwell_skips_when_stop_requested(sw_module, monkeypatch):
    sw = sw_module
    sw._wt_async_session_active = True
    sw.test_status = "1"
    sw._wt_async_stop_requested = True
    slept = []
    monkeypatch.setattr(time, "sleep", lambda s: slept.append(s))
    sw._wait_command_dwell_01s(8, 200, log_tag="query,col9")
    assert slept == []


def test_wait_command_dwell_skips_when_deadline_passed(sw_module, monkeypatch):
    sw = sw_module
    sw._wt_async_session_active = True
    sw.test_status = "1"
    sw._wt_async_deadline_ts = time.time() - 1.0
    slept = []
    monkeypatch.setattr(time, "sleep", lambda s: slept.append(s))
    sw._wait_command_dwell_01s(9, 200, log_tag="query,col9")
    assert slept == []
    assert sw._wt_async_stop_requested is True


def test_wait_end_requests_measure_stop(sw_module, monkeypatch):
    sw = sw_module
    sw.test_status = "1"
    sw.strTestStatusFlag = ""
    sw._wt_async_session_active = True
    sw._wt_async_stop_requested = False
    scpi_stops = []

    fake = SimpleNamespace(request_stop=lambda reason="": scpi_stops.append(reason))
    monkeypatch.setitem(sys.modules, "utils.wt_scpi_session", fake)
    # ``from utils import wt_scpi_session`` 走 package 属性
    import utils as utils_pkg

    monkeypatch.setattr(utils_pkg, "wt_scpi_session", fake, raising=False)

    def _fake_sleep(_sec):
        sw.test_status = "0"

    monkeypatch.setattr(time, "sleep", _fake_sleep)
    sw._wt_wait_measure_end(35, wait_timeout_sec=2)
    assert sw._wt_async_stop_requested is True
    assert sw._wt_async_session_active is False
    assert scpi_stops  # SCPI 路径也必须收到停表
