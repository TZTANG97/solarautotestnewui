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


def prepare_jobs_from_cloud_instruments(
    instruments: Sequence[Dict[str, Any]],
) -> List[Tuple[str, dict, Any]]:
    """IOT 开测下发的 instruments → 连接计划（可在后台线程跑）。"""
    from utils.device_discovery import FoundDevice, connect_plan, parse_host_port

    jobs: List[Tuple[str, dict, Any]] = []
    for item in instruments or []:
        if not isinstance(item, dict):
            continue
        slot = str(item.get("slot") or "").strip().lower()
        resource = str(item.get("resource") or item.get("addr") or "").strip()
        if not slot or not resource or resource.lower().startswith("pending:"):
            continue
        host = str(item.get("host") or "").strip()
        port = item.get("port")
        try:
            port_i = int(port) if port is not None and str(port).strip() != "" else None
        except (TypeError, ValueError):
            port_i = None
        if not host or port_i is None:
            h2, p2 = parse_host_port(resource)
            host = host or (h2 or "")
            port_i = port_i if port_i is not None else p2
        brand = str(item.get("brand") or "").strip()
        # 界面占位文案不要当成真实品牌
        if "/" in brand or "chroma /" in brand.lower():
            brand = ""
        kind = str(item.get("kind") or "").strip().lower()
        if not kind or kind == "unknown":
            kind = "dc" if slot.startswith("dc") else slot
        proto = ""
        bl = brand.lower()
        if bl == "bluesight" or (bl == "itech" and slot.startswith("dc")):
            proto = "modbus"
        elif slot == "ac" and (bl == "itech" or (port_i == 502 and bl != "chroma")):
            # :502 是 Modbus（Itech）。误走 Chroma SCPI 会在错误端口上等超时，桌面像卡住
            proto = "modbus"
            if not bl:
                brand = "itech"
        dev = FoundDevice(
            resource=resource,
            host=host or "",
            port=port_i,
            protocol=proto,
            kind_hint=kind,
            brand_hint=brand,
            idn="",
            source="cloud_config",
            extra={"from_cloud": True},
        )
        plan = connect_plan(slot, dev)
        if str(plan.get("target") or "") == "unknown":
            continue
        jobs.append((slot, plan, dev))
    return jobs


def prepare_auto_connect_jobs(
    *,
    visa_rm=None,
    status_json_path: Optional[str] = None,
    scan_lan: bool = False,
) -> Tuple[List[Tuple[str, dict, Any]], List[FoundDevice]]:
    """仅发现+建议槽位（可在后台线程跑）；不触碰 Qt。"""
    from utils.device_finder_connect import build_connect_jobs

    devices = discover_for_auto_connect(
        visa_rm=visa_rm,
        status_json_path=status_json_path,
        scan_lan=scan_lan,
    )
    pairs = suggest_auto_jobs(devices)
    return build_connect_jobs(pairs), devices


def apply_prepared_connect_jobs(
    jobs: Sequence[Tuple[str, dict, Any]],
    *,
    apply_plan: Callable[[str, dict, Any], None],
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """在主线程执行连接计划。"""
    _log = log or (lambda m: None)
    connected: List[str] = []
    errors: List[str] = []
    for slot, plan, dev in jobs or []:
        try:
            apply_plan(slot, plan, dev)
            remember_slot_for_resource(getattr(dev, "resource", "") or "", slot)
            connected.append(f"{slot}:{getattr(dev, 'resource', '')}")
            _log(f"自动连接 {slot} -> {getattr(dev, 'resource', '')}")
        except Exception as exc:
            errors.append(f"{slot}: {exc}")
            _log(f"自动连接失败 {slot}: {exc}")
    return {
        "found": len(jobs or []),
        "attempted": len(jobs or []),
        "connected": connected,
        "errors": errors,
        "skipped_ambiguous": 0,
    }


def auto_connect_best_effort(
    *,
    apply_plan: Callable[[str, dict, Any], None],
    visa_rm=None,
    status_json_path: Optional[str] = None,
    scan_lan: bool = False,
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    _log = log or (lambda m: None)
    jobs, devices = prepare_auto_connect_jobs(
        visa_rm=visa_rm,
        status_json_path=status_json_path,
        scan_lan=scan_lan,
    )
    summary = apply_prepared_connect_jobs(jobs, apply_plan=apply_plan, log=_log)
    summary["found"] = len(devices)
    summary["skipped_ambiguous"] = max(0, len(devices) - len(jobs))
    return summary
