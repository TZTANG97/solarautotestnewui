# -*- coding: utf-8 -*-
"""台架本地开测 → IOT 登记。"""
from __future__ import annotations

from types import SimpleNamespace

from utils.iot_local_run import (
    adopt_cloud_job,
    bench_is_running,
    current_local_job_id,
    handoff_has_awaiting_job,
    notify_local_run_finished,
    notify_local_run_started,
)


def test_active_awaiting_skips_local_register(monkeypatch):
    """云端仍在等本局结束时，禁止再登记 local_ui（否则会秒成功云单并双开）。"""
    import utils.iot_local_run as mod

    fake_sw = SimpleNamespace(
        _iot_ui_handoff_svc=SimpleNamespace(_awaiting={"job_id": 42}, _job_ctx=None)
    )
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake_sw)
    assert handoff_has_awaiting_job() is True

    called = []
    released = []
    monkeypatch.setattr(mod, "_do_start", lambda *_a, **_k: called.append(1))
    monkeypatch.setattr(
        mod, "release_previous_cloud_job_for_new_round", lambda: released.append(42) or 42
    )
    notify_local_run_started("过载能力测试")
    assert released == []
    assert called == []


def test_handoff_job_ctx_skips_during_start_test(monkeypatch):
    """start_test 调用瞬间 _awaiting 还没写，靠 _job_ctx 防重复登记。"""
    import utils.iot_local_run as mod

    fake_sw = SimpleNamespace(
        _iot_ui_handoff_svc=SimpleNamespace(_awaiting=None, _job_ctx={"job_id": 7})
    )
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake_sw)
    assert handoff_has_awaiting_job() is True
    called = []
    monkeypatch.setattr(mod, "_do_start", lambda *_a, **_k: called.append(1))
    notify_local_run_started("过载能力测试")
    assert called == []


def test_handoff_no_awaiting_allows_start(monkeypatch):
    import utils.iot_local_run as mod

    fake_sw = SimpleNamespace(
        _iot_ui_handoff_svc=SimpleNamespace(_awaiting=None, _job_ctx=None)
    )
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake_sw)
    assert handoff_has_awaiting_job() is False

    called = []

    def _capture(name, widgets=None, *args, **kwargs):
        called.append(name)

    monkeypatch.setattr(mod, "_do_start", _capture)

    class _ImmediateThread:
        def __init__(self, target=None, args=(), kwargs=None, daemon=None, name=None):
            self._target = target
            self._args = args or ()
            self._kwargs = kwargs or {}

        def start(self):
            if self._target:
                self._target(*self._args, **self._kwargs)

    monkeypatch.setattr(mod.threading, "Thread", _ImmediateThread)
    notify_local_run_started("过载能力测试")
    assert called == ["过载能力测试"]


def test_notify_finished_noop_without_job(monkeypatch):
    import utils.iot_local_run as mod

    with mod._lock:
        mod._state["job_id"] = None
        mod._state["exper_id"] = None
    called = []

    def _boom(*_a, **_k):
        called.append(1)

    monkeypatch.setattr(mod, "_do_done", _boom)
    monkeypatch.setattr(mod, "_job_id_from_status_json", lambda: None)
    notify_local_run_finished(aborted=False)
    assert called == []
    assert current_local_job_id() is None


def test_notify_finished_falls_back_to_status_json(monkeypatch):
    import utils.iot_local_run as mod

    with mod._lock:
        mod._state["job_id"] = None
        mod._state["exper_id"] = None
    called = []

    def _capture(job_id, aborted):
        called.append((job_id, aborted))

    class _ImmediateThread:
        def __init__(self, target=None, args=(), kwargs=None, daemon=None, name=None):
            self._target = target
            self._args = args or ()

        def start(self):
            if self._target:
                self._target(*self._args)

    monkeypatch.setattr(mod, "_do_done", _capture)
    monkeypatch.setattr(mod, "_job_id_from_status_json", lambda: 26)
    monkeypatch.setattr(mod.threading, "Thread", _ImmediateThread)
    notify_local_run_finished(aborted=False)
    assert called == [(26, False)]
    assert current_local_job_id() == 26


def test_release_closes_awaiting_and_drops_status_job_id(monkeypatch, tmp_path):
    import json

    import utils.iot_local_run as mod

    closed = []

    class _Svc:
        _job_ctx = None
        _awaiting = {"job_id": 69}

        def finish_awaiting_as_new_round(self):
            closed.append(69)
            self._awaiting = None
            return 69

    fake_sw = SimpleNamespace(_iot_ui_handoff_svc=_Svc(), strTestStatusFlag="")
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake_sw)
    monkeypatch.setattr(mod, "_repo_root", lambda: tmp_path)
    # 仍显示进行中：不能强结（避免追加开测误杀上一单）
    (tmp_path / "status.json").write_text(
        json.dumps({"project": {"jobId": 69, "status": "进行中"}}, ensure_ascii=False),
        encoding="utf-8",
    )
    assert mod.release_previous_cloud_job_for_new_round() is None
    assert closed == []

    (tmp_path / "status.json").write_text(
        json.dumps({"project": {"jobId": 69, "status": "已结束"}}, ensure_ascii=False),
        encoding="utf-8",
    )
    assert mod.release_previous_cloud_job_for_new_round() == 69
    saved = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
    assert "jobId" not in saved["project"]
    assert closed == [69]

    fake_sw.strTestStatusFlag = "运行"
    assert mod.release_previous_cloud_job_for_new_round() is None


def test_fresh_start_drops_previous_job_and_its_stop(monkeypatch, tmp_path):
    import json

    import utils.iot_local_run as mod
    from agent.job_inbox import list_stop_requests, write_stop_request

    fake_sw = SimpleNamespace(strTestStatusFlag="", strArrayTest=[])
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake_sw)
    monkeypatch.setattr(mod, "_repo_root", lambda: tmp_path)
    (tmp_path / "status.json").write_text(
        json.dumps({"project": {"jobId": 80, "status": "进行中"}}, ensure_ascii=False),
        encoding="utf-8",
    )
    write_stop_request(tmp_path, 80, reason="台架本地中止")
    with mod._lock:
        mod._state["job_id"] = 80
    assert mod.detach_previous_job_for_fresh_start() == 80
    saved = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
    assert "jobId" not in saved["project"]
    assert list_stop_requests(tmp_path) == []
    assert mod.current_local_job_id() is None


def test_notify_started_skips_while_desktop_running(monkeypatch):
    """中途追加后再点开始：本机还在跑时不得新开 IOT 任务。"""
    import utils.iot_local_run as mod

    fake_sw = SimpleNamespace(
        _iot_ui_handoff_svc=SimpleNamespace(_awaiting=None, _job_ctx=None),
        strTestStatusFlag="运行",
    )
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake_sw)
    called = []
    monkeypatch.setattr(mod, "_do_start", lambda *_a, **_k: called.append(1))
    monkeypatch.setattr(mod, "release_previous_cloud_job_for_new_round", lambda: called.append("rel"))
    with mod._lock:
        mod._state["job_id"] = 75
    notify_local_run_started("Test_PU")
    assert called == []
    assert current_local_job_id() == 75


def test_adopt_cloud_job_drops_previous_local_id(monkeypatch):
    import utils.iot_local_run as mod

    written = {}

    def _persist(job_id, exper_id=None):
        written["job"] = job_id
        written["exper"] = exper_id

    monkeypatch.setattr(mod, "_persist_local_job_ids", _persist)
    with mod._lock:
        mod._state["job_id"] = 67
        mod._state["exper_id"] = 1
    adopt_cloud_job(69, 3)
    assert written == {"job": 69, "exper": 3}
    assert current_local_job_id() is None


def test_bench_running_if_either_signal_says_so(monkeypatch):
    """进度已是进行中、执行标志还没写成运行时，也算占用。"""
    fake_sw = SimpleNamespace(strTestStatusFlag="", strArrayTest=[])
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake_sw)
    assert bench_is_running("进行中") is True
    assert bench_is_running("人工等待") is True
    assert bench_is_running("待开始") is False
    fake_sw.strTestStatusFlag = "运行"
    assert bench_is_running("") is True
    assert bench_is_running("已结束") is True
