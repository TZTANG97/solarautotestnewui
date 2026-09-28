# -*- coding: utf-8 -*-
"""IOT Agent 启动不得再弹可见控制台。"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_agent_launch_prefers_python_not_uv_first():
    from agent import process_control as pc

    cmds = pc._agent_launch_commands()
    assert cmds, "应至少有一条启动命令"
    assert cmds[0][0].lower().endswith("python.exe") or cmds[0][0].lower().endswith(
        "pythonw.exe"
    )
    assert cmds[0][-2:] == ["-m", "agent"]
    assert any(c[0] == "uv" for c in cmds), "uv 仅作最后回退"


def test_hidden_popen_kwargs_hide_console_on_windows():
    from agent import process_control as pc

    kwargs = pc._hidden_popen_kwargs()
    assert kwargs["stdin"] is subprocess.DEVNULL
    # stdout 落到日志文件（或 DEVNULL 兜底），不再丢弃到空
    assert kwargs["stdout"] is not None
    if kwargs["stdout"] is not subprocess.DEVNULL:
        assert kwargs["stderr"] is subprocess.STDOUT
    if os.name == "nt":
        assert kwargs.get("creationflags", 0) & getattr(subprocess, "CREATE_NO_WINDOW", 0)
        assert "startupinfo" in kwargs
        assert getattr(kwargs["startupinfo"], "wShowWindow", None) == getattr(
            subprocess, "SW_HIDE", 0
        )


def test_start_agent_uses_hidden_kwargs(tmp_path, monkeypatch):
    from agent import process_control as pc

    cfg = tmp_path / "solar_agent.json"
    cfg.write_text('{"agent_token":"tok","iot_base":"https://example.com"}', encoding="utf-8")
    monkeypatch.setattr(pc, "config_file", lambda: cfg)
    monkeypatch.setattr(pc, "is_running", lambda: False)
    monkeypatch.setattr(pc, "pid_file", lambda: tmp_path / "agent.pid")
    monkeypatch.setattr(pc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(pc, "log_file", lambda: tmp_path / "agent.log")

    seen = {}

    class FakeProc:
        pid = 4242

    def fake_popen(cmd, **kwargs):
        seen["cmd"] = cmd
        seen["kwargs"] = kwargs
        return FakeProc()

    monkeypatch.setattr(pc.subprocess, "Popen", fake_popen)
    ok, msg = pc.start_agent(allow_without_token=False)
    assert ok, msg
    assert seen["cmd"][0] != "uv"
    assert "-m" in seen["cmd"] and "agent" in seen["cmd"]
    assert seen["kwargs"]["stdout"] is not None
    if os.name == "nt":
        assert seen["kwargs"].get("creationflags", 0) & getattr(
            subprocess, "CREATE_NO_WINDOW", 0
        )


def test_read_agent_comm_info_masks_token(tmp_path, monkeypatch):
    from agent import process_control as pc

    cfg = tmp_path / "solar_agent.json"
    cfg.write_text(
        '{"agent_token":"sat_abcdef1234567890","pythonid":"PY-9","iot_base":"http://x",'
        '"machine_id":"mid-1","execution_mode":"handoff","agent_version":"0.1.0"}',
        encoding="utf-8",
    )
    monkeypatch.setattr(pc, "config_file", lambda: cfg)
    monkeypatch.setattr(pc, "is_running", lambda: False)
    monkeypatch.setattr(pc, "log_file", lambda: tmp_path / "a.log")
    monkeypatch.setattr(pc, "status_text", lambda: "未运行")

    info = pc.read_agent_comm_info()
    assert info["pythonid"] == "PY-9"
    assert info["machine_id"] == "mid-1"
    assert info["iot_base"] == "http://x"
    assert "sat_abcd" in info["agent_token_masked"]
    assert "7890" in info["agent_token_masked"]
    assert "sat_abcdef1234567890" not in info["agent_token_masked"]


def test_tail_agent_log_missing(tmp_path, monkeypatch):
    from agent import process_control as pc

    monkeypatch.setattr(pc, "log_file", lambda: tmp_path / "missing.log")
    text = pc.tail_agent_log()
    assert "尚无" in text or "日志" in text


def test_stop_agent_cleans_orphans(tmp_path, monkeypatch):
    from agent import process_control as pc

    seen = []
    pid_path = tmp_path / "agent.pid"
    pid_path.write_text("7777\n", encoding="utf-8")

    def fake_tree(pid, *, timeout_sec=5.0):
        seen.append(pid)

    monkeypatch.setattr(pc, "pid_file", lambda: pid_path)
    monkeypatch.setattr(pc, "_pid_alive", lambda pid: pid in (7777, 8888))
    monkeypatch.setattr(pc, "_terminate_process_tree", fake_tree)
    monkeypatch.setattr(pc, "_iter_repo_agent_pids", lambda: [8888])

    ok, msg = pc.stop_agent()
    assert ok
    assert 7777 in seen
    assert 8888 in seen
    assert "残留" in msg


def test_stop_agent_for_app_exit_clears_pid_file(tmp_path, monkeypatch):
    from agent import process_control as pc

    pid_path = tmp_path / "agent.pid"
    pid_path.write_text("1\n", encoding="utf-8")
    monkeypatch.setattr(pc, "pid_file", lambda: pid_path)
    monkeypatch.setattr(pc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(pc, "_pid_alive", lambda _pid: False)
    monkeypatch.setattr(pc, "_iter_repo_agent_pids", lambda: [])

    ok, msg = pc.stop_agent_for_app_exit()
    assert ok
    assert "Agent" in msg
    assert not pid_path.is_file()


def test_stop_agent_terminates_process_tree(tmp_path, monkeypatch):
    from agent import process_control as pc

    seen = {}
    pid_path = tmp_path / "agent.pid"
    pid_path.write_text("7777\n", encoding="utf-8")

    def fake_tree(pid, *, timeout_sec=5.0):
        seen["pid"] = pid
        seen["timeout"] = timeout_sec

    monkeypatch.setattr(pc, "pid_file", lambda: pid_path)
    monkeypatch.setattr(pc, "_pid_alive", lambda pid: pid == 7777)
    monkeypatch.setattr(pc, "_terminate_process_tree", fake_tree)

    ok, msg = pc.stop_agent()
    assert ok
    assert seen["pid"] == 7777
    assert "7777" in msg
    assert not pid_path.is_file()
