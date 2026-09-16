# -*- coding: utf-8 -*-
"""结束试验：未连 DC 静默关断 + RunProject/宏可中断。"""
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dc_close_supports_silent_if_disconnected():
    src = (ROOT / "devices" / "dc_controller.py").read_text(encoding="utf-8")
    assert "silent_if_disconnected" in src
    assert "if not silent_if_disconnected:" in src


def test_force_hardware_safe_off_uses_silent_dc_close():
    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    assert "silent_if_disconnected=True" in src
    assert "def _force_hardware_safe_off" in src


def test_runproject_breaks_on_end_at_loop_head():
    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    assert '试验已结束，跳过剩余命令' in src
    assert '试验已结束（等待设备 UI 后），跳过剩余命令' in src


def test_upper_wt_config_checks_end_flag():
    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    # Upper_WT_Config 段应在 wt_is_check 前后检查结束
    idx = src.find('elif strArrayTest[i][0] == "Upper_WT_Config":')
    assert idx > 0
    chunk = src[idx : idx + 1200]
    assert 'if strTestStatusFlag == "结束":' in chunk
    assert "wt_is_check()" in chunk


def test_macro_player_interruptible_wait():
    src = (ROOT / "RecPlayer" / "player" / "src" / "player.py").read_text(encoding="utf-8")
    assert "while self.is_playing and time.time() < deadline" in src


def test_macro_manager_stop_always_calls_stop_playback():
    src = (ROOT / "RecPlayer" / "player" / "macro_manager.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    stop_fn = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "MacroManager":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "stop":
                    stop_fn = item
                    break
    assert stop_fn is not None
    dump = ast.dump(stop_fn)
    assert "stop_playback" in dump
    # 不应再仅依赖 is_playback_active 才 stop
    assert "is_playback_active" not in dump


def test_immun_rate_unit_order_matches_ui_and_defaults_to_second():
    src = (ROOT / "Dialog_thaiguoqianpin_immun.py").read_text(encoding="utf-8")
    idx = src.find("comboBox_S2_RATE_TIME")
    assert idx > 0
    chunk = src[idx : idx + 500]
    assert 'addItems(["毫秒", "秒", "分钟"])' in chunk
    assert "setCurrentIndex(0)" in chunk
    # 默认 200ms；最短允许 100ms（非强制 1 秒）
    te_idx = src.find("textEdit_S2_RATE_TIME.setText")
    assert 'setText("200")' in src[te_idx : te_idx + 80]


def test_immun_send_allows_100ms_rate_floor():
    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    assert "系统最短 100ms" in src
    assert "100/200/500" in src


def test_abort_does_not_force_setting_status_done():
    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    idx = src.find("def _abort_wt_side_effects")
    chunk = src[idx : idx + 1800]
    assert "setting_status = \"1\"" not in chunk
    assert "messure_status = \"1\"" not in chunk


def test_end_push_reasserts_first_test_after_reset():
    src = (ROOT / "SCPITestWave.py").read_text(encoding="utf-8")
    idx = src.find("def EndProjectPush(")
    chunk = src[idx : idx + 1600]
    assert "reset_wt_automation_state()" in chunk
    assert 'first_test = "1"' in chunk
    assert "force=" in chunk or "silent_if_idle" in chunk
