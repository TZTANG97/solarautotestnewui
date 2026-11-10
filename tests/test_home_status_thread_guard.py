# -*- coding: utf-8 -*-
"""首页 deviceStatusBadge 刷新必须经 QueuedConnection，禁止后台线程直接 setStyleSheet。"""
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCPI = ROOT / "SCPITestWave.py"


def _fn_source(path: Path, name: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(f"missing {name}")


def test_reload_home_status_marshals_off_ui_thread():
    src = _fn_source(SCPI, "_reload_home_status")
    assert "currentThread" in src
    assert "app.thread()" in src
    assert "reload.emit" in src
    assert "_reload_home_status_ui" in src


def test_home_status_bridge_uses_queued_connection():
    text = SCPI.read_text(encoding="utf-8", errors="ignore")
    assert "class _HomeStatusBridge" in text
    assert "_reload_home_status_ui, Qt.QueuedConnection" in text
    # UI 写样式只应出现在 _reload_home_status_ui / 样式 helper，不在入口直接碰 badge
    entry = _fn_source(SCPI, "_reload_home_status")
    assert "setStyleSheet" not in entry
    assert "_home_dots" not in entry


def test_home_status_bridge_created_only_on_ui_thread():
    src = _fn_source(SCPI, "_ensure_home_status_bridge")
    assert "currentThread" in src
    assert "return None" in src
    text = SCPI.read_text(encoding="utf-8", errors="ignore")
    assert "_ensure_home_status_bridge()" in text
    # 启动段须预热，避免首次在 system_error_info 线程 new QObject
    assert text.count("_ensure_home_status_bridge()") >= 2


def test_save_device_status_does_not_touch_widgets_directly():
    src = _fn_source(SCPI, "_save_device_status")
    assert "setStyleSheet" not in src
    assert ".update()" not in src
    assert "_reload_home_status" in src


def test_badge_stylesheet_helper_is_scoped():
    src = _fn_source(SCPI, "_badge_stylesheet")
    assert "QLabel#deviceStatusBadge" in src
    assert "background-color: transparent" in src
    assert "font-weight: bold" in src
