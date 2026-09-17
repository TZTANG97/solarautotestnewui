# -*- coding: utf-8 -*-
"""采集台架仪器快照，随 Agent 心跳上报 IOT（不占 python_id）。"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_cache: List[Dict[str, Any]] = []
_cache_at: float = 0.0


def parse_scpi_idn(idn: str) -> Tuple[str, str, str]:
    """*IDN? → (brand, model, serial)。"""
    text = (idn or "").strip()
    if not text or text.startswith("未响应"):
        return "", "", ""
    parts = [p.strip() for p in text.split(",")]
    brand = parts[0] if parts else ""
    model = parts[1] if len(parts) > 1 else ""
    serial = parts[2] if len(parts) > 2 else ""
    return brand[:64], model[:128], serial[:64]


def collect_instruments_snapshot(
    *,
    status_json_path: Optional[str] = None,
    min_interval_sec: float = 45.0,
    force: bool = False,
) -> List[Dict[str, Any]]:
    """
    轻量采集：优先上次资源 + 槽位映射，不做全网扫/VISA 深探（避免拖慢心跳）。
    """
    global _cache, _cache_at
    now = time.time()
    if not force and _cache and (now - _cache_at) < float(min_interval_sec):
        return list(_cache)

    out: List[Dict[str, Any]] = []
    try:
        from utils.iot_auto_connect import (
            discover_for_auto_connect,
            load_slot_map,
            suggest_auto_jobs,
        )

        devices = discover_for_auto_connect(
            visa_rm=None,
            status_json_path=status_json_path,
            scan_lan=False,
        )
        slot_map = load_slot_map()
        pairs = suggest_auto_jobs(devices)
        claimed = {id(d) for _, d in pairs}
        for slot, d in pairs:
            out.append(_dev_to_item(d, slot=slot, connected=True))
        for d in devices:
            if id(d) in claimed:
                continue
            slot = ""
            try:
                slot = slot_map.get(getattr(d, "resource", "") or "", "") or ""
            except Exception:
                slot = ""
            out.append(_dev_to_item(d, slot=slot, connected=False))
    except Exception as exc:
        logger.debug("collect instruments failed: %s", exc)
        return list(_cache)

    _cache = out
    _cache_at = now
    return list(out)


def _dev_to_item(d: Any, *, slot: str = "", connected: bool = False) -> Dict[str, Any]:
    extra = getattr(d, "extra", None) or {}
    offline = bool(extra.get("offline"))
    idn = getattr(d, "idn", "") or ""
    idn_brand, idn_model, idn_serial = parse_scpi_idn(idn)
    brand = (getattr(d, "brand_hint", "") or idn_brand or "").strip()
    model = (idn_model or "").strip()
    return {
        "kind": (getattr(d, "kind_hint", None) or "unknown"),
        "slot": (slot or "").strip().lower(),
        "resource": getattr(d, "resource", "") or "",
        "host": getattr(d, "host", "") or "",
        "port": getattr(d, "port", None),
        "brand": brand,
        "model": model,
        "serial": idn_serial,
        "idn": idn,
        "online": not offline,
        "connected": bool(connected) and not offline,
        "source": getattr(d, "source", "") or "agent_scan",
    }
