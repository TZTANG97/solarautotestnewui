# -*- coding: utf-8 -*-
"""跨 WS/MQTT 通道的 startexper 任务去重（同 id 短时不重复入队）。"""
from __future__ import annotations

import threading
import time
from typing import Dict

_lock = threading.Lock()
# job_id → 最近入队时间戳
_seen: Dict[int, float] = {}
_TTL_SEC = 120.0


def remember_job(job_id: int) -> bool:
    """
    记录即将处理的任务。
    返回 True 表示首次见到（应入队）；False 表示短时重复（应丢弃）。
    """
    try:
        jid = int(job_id or 0)
    except (TypeError, ValueError):
        return False
    if jid <= 0:
        return False
    now = time.time()
    with _lock:
        # 顺带清理过期
        dead = [k for k, ts in _seen.items() if now - ts > _TTL_SEC]
        for k in dead:
            _seen.pop(k, None)
        prev = _seen.get(jid)
        if prev is not None and now - prev < _TTL_SEC:
            return False
        _seen[jid] = now
        return True


def clear_for_tests() -> None:
    with _lock:
        _seen.clear()
