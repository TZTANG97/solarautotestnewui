# -*- coding: utf-8 -*-
"""是德长 SAS 命令日志摘要，避免整表打进 UI。"""
from __future__ import annotations

from utils.dc_cmd_log import format_dc_cmd_for_log


def test_format_dc_cmd_for_log_truncates_sas_tabl():
    long_cmd = "SAS:TABL1:VOLT " + ",".join(f"{i * 0.1:.3f}" for i in range(1024))
    out = format_dc_cmd_for_log(long_cmd)
    assert "SAS:TABL1:VOLT" in out
    assert "1024 pts" in out
    assert str(len(long_cmd)) in out
    assert len(out) < 200
    assert long_cmd not in out


def test_format_dc_cmd_for_log_keeps_short():
    assert format_dc_cmd_for_log("OUTP ON") == "OUTP ON"
