# -*- coding: utf-8 -*-
"""DEWETRON :ACQUISITION:STATE? 解析与判定。"""
from __future__ import annotations

import re
from typing import Optional


def normalize_acq_state(raw: Optional[str]) -> str:
    """把 STATE? 回包归一成 started/stopped/stopping/armed/paused/空串。

    例: ``:ACQUISITION:STATE Started`` / ``Stopped`` / ``Stopping``。
    ``Stopping`` 不得误判成 ``stopped``（旧正则 ``Stopped$`` 虽不匹配 Stopping，
    但 ``started in stopping`` 类子串误判要避开）。
    """
    if raw is None:
        return ""
    text = str(raw).strip().strip('"')
    if not text:
        return ""
    low = text.casefold()
    for name in ("stopping", "started", "stopped", "paused", "armed"):
        if re.search(rf"\b{name}\b", low):
            return name
    # 无词界时 Stopped 优先，避免 Stopping/Started 子串互误
    if "stopped" in low:
        return "stopped"
    if "stopping" in low:
        return "stopping"
    if "started" in low:
        return "started"
    if "armed" in low:
        return "armed"
    if "paused" in low:
        return "paused"
    return low.split()[-1] if low.split() else ""


def acq_state_is_started(raw: Optional[str]) -> bool:
    return normalize_acq_state(raw) == "started"


def acq_state_is_idle(raw: Optional[str]) -> bool:
    """可再次 START 的空闲态：Stopped（含未知空串不当作 idle）。"""
    return normalize_acq_state(raw) == "stopped"
