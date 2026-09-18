"""启动路径不得在 UI 线程长时间 wait_for_claim。"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ensure_configured_and_start_has_no_sync_claim_wait():
    src = (ROOT / "agent" / "bootstrap.py").read_text(encoding="utf-8")
    # 截取 ensure_configured_and_start 函数体
    start = src.find("def ensure_configured_and_start")
    assert start > 0
    end = src.find("\n_claim_bg_started", start)
    body = src[start:end if end > 0 else start + 2500]
    assert "wait_for_claim(" not in body
    assert "_start_claim_background" in body
    assert "timeout=8" in body or "timeout=8.0" in body


def test_handoff_uses_background_auto_connect_signal():
    src = (ROOT / "utils" / "iot_ui_handoff.py").read_text(encoding="utf-8")
    assert "_auto_connect_finished" in src
    assert "prepare_auto_connect" in src
    assert "设备已就绪，跳过自动扫连" in src
    assert "iot-handoff-autoconnect" in src
