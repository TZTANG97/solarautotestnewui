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


def test_experiment_commands_do_not_rewrite_ac_config_page():
    src = Path(__file__).resolve().parents[1] / "SCPITestWave.py"
    sync_body = _fn_body_source(src, "_sync_soft_panel_ac_setpoint_from_scpi")
    apply_body = _fn_body_source(src, "_apply_soft_panel_ac_setpoint_ui")
    recover_body = _fn_body_source(src, "_recover_ac_nominal_before_stop")
    assert "setPlainText" not in sync_body
    assert "setPlainText" not in apply_body
    assert "ac_setpoint.emit" not in sync_body
    assert "textEdit_S1_AC_VOLT" not in recover_body
    assert "_get_active_ac_setpoints" in recover_body


def test_device_io_bridge_log_uses_queued_connection():
    text = (Path(__file__).resolve().parents[1] / "SCPITestWave.py").read_text(
        encoding="utf-8", errors="ignore"
    )
    assert "log_line.connect(_append_return_message_ui, Qt.QueuedConnection)" in text
    assert "ac_setpoint.connect(" in text
    assert "QueuedConnection" in text[text.find("ac_setpoint.connect") :][:200]
