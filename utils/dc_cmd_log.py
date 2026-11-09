# -*- coding: utf-8 -*-
"""直流 SCPI 日志摘要：是德 SAS:TABL 长命令勿整段打进 UI。"""
from __future__ import annotations


def format_dc_cmd_for_log(cmd, limit: int = 96) -> str:
    s = str(cmd or "")
    u = s.upper()
    if "SAS:TABL" in u and len(s) > limit:
        pts = s.count(",") + 1
        head = s.split(",", 1)[0][:48]
        return f"{head},…[{pts} pts / {len(s)} bytes]"
    if len(s) > limit:
        return f"{s[:limit]}…({len(s)} bytes)"
    return s
