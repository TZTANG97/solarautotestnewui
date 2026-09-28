# -*- coding: utf-8 -*-
"""IOT handoff auto connect from last resources."""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from utils.device_discovery import (
    FoundDevice,
    devices_from_last_resources,
    devices_from_status_json,
    enrich_device,
    last_known_resources,
    list_visa_resources,
    load_success_device_map,
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
    success = load_success_device_map()
    online = [d for d in devices if not (d.extra or {}).get("offline")]
    by_kind: Dict[str, List[FoundDevice]] = {}
    for d in online:
        kind = (d.kind_hint or "unknown").lower()
        by_kind.setdefault(kind, []).append(d)

    used_slots = set()
    jobs: List[Tuple[str, FoundDevice]] = []

    def _slot_for(dev: FoundDevice) -> str:
        res = getattr(dev, "resource", "") or ""
        slot = slot_map.get(res) or ""
        if not slot and getattr(dev, "host", None) and getattr(dev, "port", None):
            slot = slot_map.get(f"{dev.host}:{dev.port}") or ""
        if not slot:
            slot = str((dev.extra or {}).get("last_slot") or "").strip().lower()
        if not slot:
            snap = success.get(res) or {}
            if not snap and getattr(dev, "host", None) and getattr(dev, "port", None):
                snap = success.get(f"{dev.host}:{dev.port}") or {}
            slot = str(snap.get("slot") or "").strip().lower()
        return slot

    for d in online:
        slot = _slot_for(d)
        if slot and slot not in used_slots:
            jobs.append((slot, d))
            used_slots.add(slot)

    claimed = {id(d) for _, d in jobs}
    for kind, group in by_kind.items():
        remain = [d for d in group if id(d) not in claimed]
        if not remain:
            continue
        if kind == "dc":
            # 多台直流无记忆槽位时不强行占槽，避免 USB/网口错位
            if len(remain) == 1:
                free = next(
                    (f"dc{i}" for i in range(1, 5) if f"dc{i}" not in used_slots),
                    None,
                )
                if free:
                    jobs.append((free, remain[0]))
                    used_slots.add(free)
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
    # status.json 带槽位，优先补进列表（USB 直流手动连接后靠它恢复）
    try:
        for d in devices_from_status_json(status_json_path):
            if not any(x.resource == d.resource for x in base):
                base.append(d)
            else:
                for i, x in enumerate(base):
                    if x.resource != d.resource:
                        continue
                    extra = dict(x.extra or {})
                    if d.extra.get("last_slot") and not extra.get("last_slot"):
                        extra["last_slot"] = d.extra["last_slot"]
                    kind = x.kind_hint if x.kind_hint not in ("", "unknown") else d.kind_hint
                    base[i] = FoundDevice(
                        resource=x.resource,
                        host=x.host or d.host,
                        port=x.port if x.port is not None else d.port,
                        idn=x.idn,
                        kind_hint=kind,
                        brand_hint=x.brand_hint or d.brand_hint,
                        source=x.source or d.source,
                        protocol=x.protocol or d.protocol,
                        extra=extra,
                    )
                    break
    except Exception:
        pass

    live_set = set()
    if visa_rm is not None:
        try:
            live_set = set(list_visa_resources(visa_rm, include_serial=True))
        except Exception:
            live_set = set()
        known = {d.resource for d in base}
        success = load_success_device_map()
        for res in live_set:
            if res in known:
                continue
            # 只并入「以前连过」的 USB/GPIB，避免把无关 USB 仪表误挂到直流槽
            if res not in success and res not in set(last):
                continue
            base.append(
                FoundDevice(
                    resource=res,
                    source="VISA",
                    protocol="visa",
                    kind_hint=str((success.get(res) or {}).get("kind_hint") or "unknown"),
                    brand_hint=str((success.get(res) or {}).get("brand_hint") or ""),
                    extra={
                        "last_slot": str((success.get(res) or {}).get("slot") or ""),
                    },
                )
            )

    out: List[FoundDevice] = []
    for d in base:
        upper = (d.resource or "").upper()
        known_kind = (d.kind_hint or "").lower() not in ("", "unknown")
        # USB/GPIB：已有槽位/类型时不要先 *IDN? 占住会话，否则随后正式连接常失败
        if upper.startswith(("USB", "GPIB")) and (
            known_kind or (d.extra or {}).get("last_slot")
        ):
            if live_set and d.resource not in live_set:
                extra = dict(d.extra or {})
                extra["offline"] = True
                extra["detail"] = "VISA 列表中未找到该 USB/GPIB 资源"
                out.append(
                    FoundDevice(
                        resource=d.resource,
                        host=d.host,
                        port=d.port,
                        idn=f"未响应：{extra['detail']}",
                        kind_hint="unknown",
                        brand_hint=d.brand_hint,
                        source=d.source or "上次",
                        protocol=d.protocol,
                        extra=extra,
                    )
                )
            else:
                out.append(d)
            continue
        try:
            enriched = enrich_device(d, rm=visa_rm)
            if (
                (enriched.kind_hint or "").lower() in ("", "unknown")
                and known_kind
            ):
                enriched = FoundDevice(
                    resource=enriched.resource,
                    host=enriched.host or d.host,
                    port=enriched.port if enriched.port is not None else d.port,
                    idn=enriched.idn or d.idn,
                    kind_hint=d.kind_hint,
                    brand_hint=enriched.brand_hint or d.brand_hint,
                    source=enriched.source or d.source,
                    protocol=enriched.protocol or d.protocol,
                    extra=dict(d.extra or {}, **(enriched.extra or {})),
                )
            out.append(enriched)
        except Exception:
            out.append(d)
    return out


def explain_ac_brand_port_mismatch(
    *,
    brand: str = "",
    port: Optional[int] = None,
) -> str:
    """AC 品牌与端口明显冲突时返回中文说明，否则空串。

    502 = 爱科 Modbus；Chroma 网口 SCPI 常见 2101。网页若选「致茂网口」却留着 502，
    桌面连不上时只会得到含糊的「会话未建立」。
    """
    bl = str(brand or "").strip().lower()
    if port is None:
        return ""
    try:
        port_i = int(port)
    except (TypeError, ValueError):
        return ""
    chroma_net = bl in ("chroma_ip", "chroma")
    if chroma_net and port_i == 502:
        return (
            "品牌与端口不匹配：502 是爱科(Itech)（Modbus）；"
            "致茂 Chroma 网口请用 2101，或把品牌改成「爱科(Itech)」"
        )
    if bl == "itech" and port_i == 2101:
        return (
            "品牌与端口不匹配：2101 通常是致茂 Chroma SCPI；"
            "爱科(Itech) 请用 502，或把品牌改成「致茂 Chroma（网口）」"
        )
    return ""


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
        elif slot == "ac" and (bl == "itech" or port_i == 502):
            # :502 一律走爱科 Modbus。误走 Chroma SCPI 会在错误端口上等超时。
            # 若网页仍标 chroma/chroma_ip，外层应先用 explain_ac_brand_port_mismatch 拦住。
            proto = "modbus"
            if bl in ("", "chroma", "chroma_ip"):
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
    session_ok: Optional[Callable[[str], bool]] = None,
) -> Dict[str, Any]:
    """在主线程执行连接计划。

    ``session_ok`` 为真才算连上。连接函数失败时往往只打日志、不抛异常，
    不能把「没报错」当成已连接。
    """
    _log = log or (lambda m: None)
    connected: List[str] = []
    errors: List[str] = []
    for slot, plan, dev in jobs or []:
        try:
            apply_plan(slot, plan, dev)
            if session_ok is not None and not session_ok(slot):
                target = str((plan or {}).get("target") or "")
                host = str(getattr(dev, "host", "") or "")
                port = getattr(dev, "port", None)
                where = f"{host}:{port}" if host and port is not None else str(
                    getattr(dev, "resource", "") or ""
                )
                hint = f"{target}@{where}" if target else where
                errors.append(f"{slot}: 桌面连接失败（会话未建立；{hint}）")
                _log(f"自动连接失败 {slot}: 会话未建立 {hint}")
                continue
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
