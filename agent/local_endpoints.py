# -*- coding: utf-8 -*-
"""工控机本机串口 / VISA 资源。只在台架上枚举，再随心跳交给云端供网页选择。"""
from __future__ import annotations

import re
import time
from typing import Dict, List

_cache: List[Dict[str, str]] = []
_cache_at: float = 0.0


def _add(out: List[Dict[str, str]], seen: set, *, kind: str, resource: str, label: str, com: str = "") -> None:
    key = (resource or "").strip().upper()
    if not key or key in seen:
        return
    seen.add(key)
    item = {"kind": kind, "resource": resource.strip(), "label": (label or resource).strip()}
    if com:
        item["com"] = com
    out.append(item)


def collect_local_endpoints(*, min_interval_sec: float = 15.0, force: bool = False) -> List[Dict[str, str]]:
    """枚举本机 COM，映射为桌面使用的 ASRL{n}::INSTR。不打开 VISA，避免心跳被资源管理器卡住。"""
    global _cache, _cache_at
    now = time.time()
    if not force and _cache and (now - _cache_at) < float(min_interval_sec):
        return list(_cache)

    out: List[Dict[str, str]] = []
    seen: set = set()
    try:
        from serial.tools import list_ports

        for port in list_ports.comports():
            dev = str(getattr(port, "device", "") or "").strip()
            desc = str(getattr(port, "description", "") or "").strip()
            match = re.search(r"(\d+)$", dev)
            if not match:
                continue
            asrl = f"ASRL{match.group(1)}::INSTR"
            label = f"{dev} {desc}".strip()
            _add(out, seen, kind="serial", resource=asrl, label=label, com=dev)
    except Exception:
        pass

    _cache = out
    _cache_at = now
    return list(out)
