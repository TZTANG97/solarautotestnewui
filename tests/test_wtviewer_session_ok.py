# -*- coding: utf-8 -*-
"""空闲/开跑时 WT Soft Panel 也要判已连，供 status.json → 网页上报。"""
from __future__ import annotations

import ast
from pathlib import Path

from utils.wtviewer_session import (
    clear_wtviewer_alive_latch,
    wtviewer_window_alive,
)

ROOT = Path(__file__).resolve().parents[1]
SCPI = ROOT / "SCPITestWave.py"


def _fn_source(path: Path, name: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"missing {name}")


def test_wtviewer_alive_when_efree_title_present():
    clear_wtviewer_alive_latch()
    assert wtviewer_window_alive(
        enum_windows=lambda: {1: "WTViewerEfree", 2: "数值详细设置"},
        latch_sec=0,
    )


def test_wtviewer_alive_ignores_detail_only():
    clear_wtviewer_alive_latch()
    assert not wtviewer_window_alive(
        enum_windows=lambda: {1: "数值详细设置"},
        latch_sec=0,
    )


def test_wtviewer_alive_false_when_no_windows():
    clear_wtviewer_alive_latch()
    assert not wtviewer_window_alive(enum_windows=lambda: {}, latch_sec=0)


def test_wtviewer_alive_sticky_latch_after_brief_miss():
    clear_wtviewer_alive_latch()
    assert wtviewer_window_alive(
        enum_windows=lambda: {1: "WTViewerEfree"},
        now_mono=100.0,
        latch_sec=30.0,
    )
    # 开跑瞬间枚举漏检：仍应 sticky
    assert wtviewer_window_alive(
        enum_windows=lambda: {},
        now_mono=110.0,
        latch_sec=30.0,
    )
    clear_wtviewer_alive_latch()
    assert not wtviewer_window_alive(
        enum_windows=lambda: {},
        now_mono=111.0,
        latch_sec=30.0,
    )


def test_iot_slot_session_ok_covers_async_and_soft_panel():
    src = _fn_source(SCPI, "_iot_slot_session_ok")
    assert "_wt_async_session_active" in src
    assert 'test_status' in src
    assert "WT_auto_messure_status" in src
    assert "wtviewer_window_alive" in src


def test_disconnect_clears_wtviewer_latch():
    src = _fn_source(SCPI, "DisconnectEQUWT3000")
    assert "clear_wtviewer_alive_latch" in src
