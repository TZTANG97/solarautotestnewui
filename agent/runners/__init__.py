# -*- coding: utf-8 -*-
"""按 testType 分发执行器。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from agent.runners.overload import OverloadRunner


def get_runner(
    test_type: str,
    *,
    dry_run: bool = True,
    execution_mode: str = "",
    repo_root: Optional[Path] = None,
):
    tt = (test_type or "").strip().lower()
    mode = (execution_mode or "").strip()
    if not mode:
        mode = "dry_run" if dry_run else "live"
    root = repo_root or Path(__file__).resolve().parent.parent
    if tt in ("overload", "过载能力测试", "overloads"):
        return OverloadRunner(execution_mode=mode, repo_root=root)
    raise ValueError(f"不支持的 testType: {test_type}")
