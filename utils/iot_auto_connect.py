# -*- coding: utf-8 -*-
"""IOT handoff auto connect from last resources."""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from utils.device_discovery import (
    FoundDevice,
    enrich_device,
    last_known_resources,
    devices_from_last_resources,
)
from utils.device_finder_connect import build_connect_jobs

_SLOT_MAP_KEY = "device.finder.slot_map"


def load_slot_map() -> Dict[str, str]:
    try:
        from utils.ui_field_helpers import last_value

        raw = last_value(_SLOT_MAP_KEY, "") or ""
        if not raw.strip():
            return {}
        data = json.loads(raw)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items() if k and v}
    except Exception:
        pass
    return {}


def remember_slot_for_resource(resource: str, slot: str) -> None:
    res = (resource or "").strip()
    sl = (slot or "").strip().lower()
    if not res or not sl:
        return
    try:
        from utils.ui_field_helpers import remember_value

        m = load_slot_map()
        m[res] = sl
        remember_value(_SLOT_MAP_KEY, json.dumps(m, ensure_ascii=False))
    except Exception:
        pass


def _default_slot_for_kind(kind: str) -> Optional[str]:
    k = (kind or "").lower()
    return {"ac": "ac", "wt": "wt", "dew": "dew", "scope": "scope", "dc": "dc1"}.get(k)


def suggest_auto_jobs(devices: Sequence[FoundDevice]) -> List[Tuple[str, FoundDevice]]:
    slot_map = load_slot_map()
    online = [d for d in devices if not (d.extra or {}).get("offline")]
    by_kind: Dict[str, List[FoundDevice]] = {}
    for d in online:
        kind = (d.kind_hint or "unknown").lower()
        by_kind.setdefault(kind, []).append(d)

    used_slots = set()
    jobs: List[Tuple[str, FoundDevice]] = []

    for d in online:
        slot = slot_map.get(d.resource) or ""
        if not slot and d.host and d.port:
            slot = slot_map.get(f"{d.host}:{d.port}") or ""
        if slot and slot not in used_slots:
            jobs.append((slot, d))
            used_slots.add(slot)

    claimed = {id(d) for _, d in jobs}
    for kind, group in by_kind.items():
        remain = [d for d in group if id(d) not in claimed]
        if not remain:
            continue
        if kind == "dc":
            if len(remain) == 1 and "dc1" not in used_slots:
                jobs.append(("dc1", remain[0]))
                used_slots.add("dc1")
            continue
        if kind == "modbus":
            continue
        default = _default_slot_for_kind(kind)
        if default and default not in used_slots and len(remain) == 1:
            jobs.append((default, remain[0]))
            used_slots.add(default)
    return jobs


def discover_for_auto_connect(
    *,
    visa_rm=None,
    status_json_path: Optional[str] = None,
    scan_lan: bool = False,
) -> List[FoundDevice]:
    last = last_known_resources(status_json_path)
    base = devices_from_last_resources(last, source="上次")
    out: List[FoundDevice] = []
    for d in base:
        try:
            out.append(enrich_device(d, rm=visa_rm))
        except Exception:
            out.append(d)
    return out


def auto_connect_best_effort(
    *,
    apply_plan: Callable[[str, dict, Any], None],
    visa_rm=None,
    status_json_path: Optional[str] = None,
    scan_lan: bool = False,
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    _log = log or (lambda m: None)
    devices = discover_for_auto_connect(
        visa_rm=visa_rm,
        status_json_path=status_json_path,
        scan_lan=scan_lan,
    )
    pairs = suggest_auto_jobs(devices)
    jobs = build_connect_jobs(pairs)
    connected: List[str] = []
    errors: List[str] = []
    for slot, plan, dev in jobs:
        try:
            apply_plan(slot, plan, dev)
            remember_slot_for_resource(getattr(dev, "resource", "") or "", slot)
            connected.append(f"{slot}:{getattr(dev, 'resource', '')}")
            _log(f"自动连接 {slot} -> {getattr(dev, 'resource', '')}")
        except Exception as exc:
            errors.append(f"{slot}: {exc}")
            _log(f"自动连接失败 {slot}: {exc}")
    return {
        "found": len(devices),
        "attempted": len(jobs),
        "connected": connected,
        "errors": errors,
        "skipped_ambiguous": max(0, len(devices) - len(jobs)),
    }
