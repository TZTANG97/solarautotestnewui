# -*- coding: utf-8 -*-
"""台架本地开测 → IOT 登记。"""
from __future__ import annotations

from types import SimpleNamespace

from utils.iot_local_run import (
    current_local_job_id,
    handoff_has_awaiting_job,
    notify_local_run_finished,
    notify_local_run_started,
)


def test_handoff_awaiting_skips_when_job_present(monkeypatch):
    import utils.iot_local_run as mod

    fake_sw = SimpleNamespace(
        _iot_ui_handoff_svc=SimpleNamespace(_awaiting={"job_id": 42}, _job_ctx=None)
    )
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake_sw)
    assert handoff_has_awaiting_job() is True

    called = []

    def _boom(*_a, **_k):
        called.append(1)

    monkeypatch.setattr(mod, "_do_start", _boom)
    notify_local_run_started("过载能力测试")
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

    def _capture(name, widgets=None):
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
