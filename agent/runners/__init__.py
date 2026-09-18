# -*- coding: utf-8 -*-
"""按 testType 分发执行器。

接入新试验时：在此注册 runner，并与 IOT 侧
app/services/solar_blockly_catalog.SOLAR_TEST_SPECS 的 test_type / write^solar_* 对齐。
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from agent.config import _repo_root
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
    # 必须与 UI handoff / config 同一安装根，勿用 runners/ 的 parent.parent（会落到 agent/）
    root = Path(repo_root) if repo_root else _repo_root()
    # 一期 handoff：过载 / 防逆流 共用 OverloadRunner（落盘 + 等 UI 结果）
    # 对应 Blockly：solar_overload / solar_antibackflow（start→块→stop）
    if tt in (
        "overload",
        "过载能力测试",
        "overloads",
        "antibackflow",
        "anti_backflow",
        "防逆流测试",
        "防逆流",
    ):
        return OverloadRunner(execution_mode=mode, repo_root=root)
    raise ValueError(f"不支持的 testType: {test_type}")
