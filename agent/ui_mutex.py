# -*- coding: utf-8 -*-
"""供桌面 UI 调用的本机互斥（与 Agent 共用锁文件）。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from agent.mutex import LocalMutex


def default_mutex_path(repo_root: Optional[Path] = None) -> Path:
    root = repo_root or Path(__file__).resolve().parent.parent
    return root / ".solar_agent_mutex"


def ui_try_acquire(meta: str = "manual_test", repo_root: Optional[Path] = None) -> bool:
    """本地手动开测前调用；失败表示 Agent 云任务占用中。"""
    return LocalMutex(default_mutex_path(repo_root)).acquire("ui", meta=meta)


def ui_release(repo_root: Optional[Path] = None) -> None:
    LocalMutex(default_mutex_path(repo_root)).release("ui")


def ui_is_blocked_by_agent(repo_root: Optional[Path] = None) -> bool:
    m = LocalMutex(default_mutex_path(repo_root))
    return m.is_held_by_other("ui") == "agent"
