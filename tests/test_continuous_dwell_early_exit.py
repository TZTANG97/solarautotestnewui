# -*- coding: utf-8 -*-
"""连续录 col9 驻留：录波结束 / 请求停表 / 截止时刻应立刻跳过。"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
# 多根工作区：IOT 的 app/（有 __init__）会盖住本仓无 __init__ 的 app.bootstrap
def _keep_path(p: str) -> bool:
    norm = p.replace("\\", "/").lower()
    return "/iot/iot" not in norm and not norm.rstrip("/").endswith("/iot")


sys.path[:] = [p for p in sys.path if _keep_path(str(p))]
if str(_ROOT) in sys.path:
    sys.path.remove(str(_ROOT))
sys.path.insert(0, str(_ROOT))
for _mod in list(sys.modules):
    if _mod == "app" or _mod.startswith("app."):
        sys.modules.pop(_mod, None)


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
    sw._wt_measure_flow_entered = True
    sw._wt_async_stop_requested = False
    scpi_stops = []

    fake = SimpleNamespace(
        request_stop=lambda reason="": scpi_stops.append(reason),
        stop_and_export=lambda *a, **k: None,
    )
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


def test_wait_end_force_clears_when_measure_stuck(sw_module, monkeypatch):
    sw = sw_module
    sw.test_status = "1"
    sw.strTestStatusFlag = ""
    sw._wt_async_session_active = True
    sw._wt_measure_flow_entered = True
    sw.WT_auto_messure_status = "1"
    fake = SimpleNamespace(
        request_stop=lambda reason="": None,
        stop_and_export=lambda *a, **k: "x.csv",
    )
    monkeypatch.setitem(sys.modules, "utils.wt_scpi_session", fake)
    import utils as utils_pkg

    monkeypatch.setattr(utils_pkg, "wt_scpi_session", fake, raising=False)
    monkeypatch.setattr(sw, "_wt_emergency_stop_and_export", lambda reason="": "x.csv")
    monkeypatch.setattr(time, "sleep", lambda _s: None)
    # time.time 快进超过超时
    t0 = {"n": 0}

    def _fake_time():
        t0["n"] += 1
        return 1000.0 + t0["n"] * 3.0

    monkeypatch.setattr(time, "time", _fake_time)
    sw._wt_wait_measure_end(39, wait_timeout_sec=5)
    assert sw.test_status in ("", "0")
    assert sw._wt_async_session_active is False
    assert sw.WT_auto_messure_status == ""


def test_wait_end_skips_when_measure_never_started(sw_module, monkeypatch):
    sw = sw_module
    sw.test_status = "1"
    sw.strTestStatusFlag = ""
    sw._wt_async_session_active = True
    sw._wt_measure_flow_entered = False
    sw.WT_auto_messure_status = "1"
    called = {"n": 0}
    monkeypatch.setattr(
        sw, "_wt_request_async_measure_stop", lambda reason="": called.__setitem__("n", 1)
    )
    sw._wt_wait_measure_end(39, wait_timeout_sec=5)
    assert called["n"] == 0  # 从未启动则不必 request_stop 空等
    assert sw.test_status in ("", "0")
    assert sw._wt_async_session_active is False


def test_async_start_aborts_when_gates_not_ready(sw_module, monkeypatch):
    sw = sw_module
    sw.setting_status = ""
    sw.messure_status = ""
    sw.test_status = ""
    sw.WT_auto_messure_status = ""
    sw.now_save_file = 0
    sw.save_file_name = ""
    sw.strArrayTest = []
    sw.config_dict = {}
    sw.strTestStatusFlag = ""
    sw.ui = None
    sw._wt_async_start_measure(3)
    assert sw._wt_async_session_active is False
    assert sw.test_status in ("", "0")
