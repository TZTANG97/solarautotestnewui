# -*- coding: utf-8 -*-
"""供桌面 UI 调用的本机互斥（与 Agent 共用锁文件）。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from agent.mutex import LocalMutex


def default_mutex_path(repo_root: Optional[Path] = None) -> Path:
    from agent.config import _repo_root

    root = Path(repo_root) if repo_root else _repo_root()
    return root / ".solar_agent_mutex"


def ui_try_acquire(meta: str = "manual_test", repo_root: Optional[Path] = None) -> bool:
    """本地手动开测前调用；失败表示 Agent 云任务占用中。"""
    m = LocalMutex(default_mutex_path(repo_root))
    m.clear_if_stale()
    return m.acquire("ui", meta=meta)


def ui_release(repo_root: Optional[Path] = None) -> None:
    LocalMutex(default_mutex_path(repo_root)).release("ui")


def ui_force_clear(repo_root: Optional[Path] = None) -> None:
    """软件退出时强制清锁，避免残留挡住 Agent 领云任务。"""
    LocalMutex(default_mutex_path(repo_root)).force_clear()


def ui_is_blocked_by_agent(repo_root: Optional[Path] = None) -> bool:
    m = LocalMutex(default_mutex_path(repo_root))
    return m.is_held_by_other("ui") == "agent"
