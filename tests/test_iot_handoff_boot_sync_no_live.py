# -*- coding: utf-8 -*-
"""开测交接 Soft Panel 同步不得立刻下真机（否则与试验队列 S1 重复发 AC/DC）。"""

from pathlib import Path


def test_handoff_boot_sync_calls_use_apply_to_device_false():
    text = Path("utils/iot_ui_handoff.py").read_text(encoding="utf-8")
    assert text.count("apply_to_device=False") >= 2
    assert "真机交由试验队列" in text or "仅界面" in text
