# -*- coding: utf-8 -*-
"""陈旧互斥锁应自动清理，避免关软件后 Agent 永不领任务。"""
from __future__ import annotations

import json
import os
from pathlib import Path

from agent.mutex import LocalMutex


def test_clear_if_stale_dead_pid(tmp_path: Path):
    lock = tmp_path / ".solar_agent_mutex"
    lock.write_text(
        json.dumps(
            {
                "owner": "ui",
                "pid": 1,  # 通常不存在的 pid；若碰巧存活则换一个
                "meta": "stale",
                "at": "2020-01-01 00:00:00",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    # 找一个确定不存在的 pid
    dead = 1
    while True:
        try:
            import psutil

            if not psutil.pid_exists(dead):
                break
        except Exception:
            break
        dead += 1
        if dead > 50_000:
            break
    lock.write_text(
        json.dumps(
            {"owner": "ui", "pid": dead, "meta": "stale", "at": "2020-01-01 00:00:00"},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    m = LocalMutex(lock)
    assert m.clear_if_stale() is True
    assert not lock.is_file()
    assert m.is_held_by_other("agent") is None


def test_alive_pid_not_cleared(tmp_path: Path):
    lock = tmp_path / ".solar_agent_mutex"
    lock.write_text(
        json.dumps(
            {
                "owner": "ui",
                "pid": os.getpid(),
                "meta": "live",
                "at": "2099-01-01 00:00:00",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    m = LocalMutex(lock)
    assert m.clear_if_stale() is False
    assert m.is_held_by_other("agent") == "ui"


def test_force_clear(tmp_path: Path):
    lock = tmp_path / ".solar_agent_mutex"
    m = LocalMutex(lock)
    assert m.acquire("ui", meta="x")
    m.force_clear()
    assert not lock.is_file()
