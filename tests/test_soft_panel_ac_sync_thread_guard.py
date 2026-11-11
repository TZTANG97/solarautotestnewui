# -*- coding: utf-8 -*-
"""VOLT/FREQ Soft Panel 回写不得在试验线程直接碰 QTextEdit。"""
from __future__ import annotations

import ast
from pathlib import Path


def _fn_body_source(path: Path, name: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            body = list(node.body)
            if body and isinstance(body[0], ast.Expr):
                val = body[0].value
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    body = body[1:]
            return "\n".join(ast.unparse(stmt) for stmt in body)
    raise AssertionError(f"missing {name}")


def test_sync_soft_panel_uses_bridge_not_direct_setplaintext():
    src = Path(__file__).resolve().parents[1] / "SCPITestWave.py"
    body = _fn_body_source(src, "_sync_soft_panel_ac_setpoint_from_scpi")
    assert "setPlainText" not in body
    assert "ac_setpoint.emit" in body or "_apply_soft_panel_ac_setpoint_ui" in body


def test_device_io_bridge_log_uses_queued_connection():
    text = (Path(__file__).resolve().parents[1] / "SCPITestWave.py").read_text(
        encoding="utf-8", errors="ignore"
    )
    assert "log_line.connect(_append_return_message_ui, Qt.QueuedConnection)" in text
    assert "ac_setpoint.connect(" in text
    assert "QueuedConnection" in text[text.find("ac_setpoint.connect") :][:200]
