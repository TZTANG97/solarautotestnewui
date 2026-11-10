# -*- coding: utf-8 -*-
"""SCPI prepare 失败必须回落 Soft Panel，不能 continue 空挂门闩。"""
from __future__ import annotations

from pathlib import Path


def test_upper_wt_config_scpi_fail_falls_back_to_macro():
    text = (Path(__file__).resolve().parents[1] / "SCPITestWave.py").read_text(
        encoding="utf-8", errors="ignore"
    )
    assert 'config_dict["wt_acquire_mode"] = "macro"' in text
    assert "已回落 Soft Panel 宏模式继续录波" in text
    assert "_scpi_ready" in text
    # 失败后不得无条件 continue 跳过 Soft Panel
    idx = text.find("SCPI prepare failed")
    assert idx > 0
    window = text[idx : idx + 1200]
    assert "已回落 Soft Panel" in window
    assert "wt_is_check" in text[text.find("_scpi_ready:") : text.find("_scpi_ready:") + 800]
