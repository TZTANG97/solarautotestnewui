# -*- coding: utf-8 -*-
"""采集台架仪器快照，随 Agent 心跳上报 IOT（不占 python_id）。

只上报 status.json 里「真正连通过」的仪（有 resource，且当前 connected
或曾有 last_connected）。软件输入框里随手填的 IP 不得冒充在线。
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_cache: List[Dict[str, Any]] = []
_cache_at: float = 0.0

# 首页 status.json 设备名 → (kind, slot)
_STATUS_NAME_MAP: Dict[str, Tuple[str, str]] = {
    "交流电源": ("ac", "ac"),
    "直流电源1": ("dc", "dc1"),
    "直流电源2": ("dc", "dc2"),
    "直流电源3": ("dc", "dc3"),
    "直流电源4": ("dc", "dc4"),
    "WT3000": ("wt", "wt"),
    "DL850": ("scope", "scope"),
    "DEWETRON": ("dew", "dew"),
}


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


def _parse_host_port(resource: str) -> Tuple[str, Optional[int]]:
    text = (resource or "").strip()
    if not text:
        return "", None
    try:
        from utils.device_discovery import parse_host_port

        host, port = parse_host_port(text)
        return (host or ""), port
    except Exception:
        if ":" in text:
            host, _, port_s = text.rpartition(":")
            host = host.strip()
            try:
                return host, int(port_s.strip())
            except ValueError:
                return host, None
        return text, None


def _load_status_devices(status_json_path: Optional[str]) -> List[Dict[str, Any]]:
    path = (status_json_path or "").strip()
    if not path:
        return []
    p = Path(path)
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    rows = data.get("devices") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict)]


def _status_row_to_item(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """仅：有地址，且当前已连接或曾经连成功过。"""
    name = str(row.get("name") or "").strip()
    resource = str(row.get("resource") or "").strip()
    if not resource or resource in ("未配置", "-"):
        return None
    # 残缺 IP（192.1 / 192.10）不上报
    host, _port = _parse_host_port(resource)
    if host and host.replace(".", "").isdigit():
        if len(host.split(".")) != 4:
            return None
    connected_now = bool(row.get("connected"))
    ever_connected = bool(str(row.get("last_connected") or "").strip()) or connected_now
    if not ever_connected:
        # 只有地址残留、从未成功连接 → 不上报（避免输入框 IP 冒充在线）
        return None

    kind, slot = _STATUS_NAME_MAP.get(name, ("unknown", ""))
    host, port = _parse_host_port(resource)
    brand = str(row.get("brand") or "").strip()
    model = str(row.get("model") or "").strip()
    idn = str(row.get("idn") or "").strip()
    if idn and (not brand or not model):
        b, m, _s = parse_scpi_idn(idn)
        brand = brand or b
        model = model or m
    if kind == "dew" and not brand:
        brand = "dewetron"

    item: Dict[str, Any] = {
        "kind": kind,
        "slot": slot,
        "resource": resource,
        "host": host,
        "port": port,
        "brand": brand,
        "model": model,
        "serial": "",
        "idn": idn,
        # 以软件真实连接态为准：未连成功绝不为 online
        "online": connected_now,
        "connected": connected_now,
        "source": "agent_status",
        "name": name,
    }
    widgets = row.get("widgets")
    if isinstance(widgets, dict) and widgets:
        item["widgets"] = dict(widgets)
    return item


def collect_instruments_snapshot(
    *,
    status_json_path: Optional[str] = None,
    min_interval_sec: float = 45.0,
    force: bool = False,
) -> List[Dict[str, Any]]:
    """
    只读 status.json 已连/曾连设备。
    禁止再用「输入框字段记忆 / 仅 TCP 通」冒充在线。
    """
    global _cache, _cache_at
    now = time.time()
    if not force and _cache and (now - _cache_at) < float(min_interval_sec):
        return list(_cache)

    out: List[Dict[str, Any]] = []
    try:
        for row in _load_status_devices(status_json_path):
            item = _status_row_to_item(row)
            if item:
                out.append(item)
    except Exception as exc:
        logger.debug("collect instruments failed: %s", exc)
        return list(_cache)

    _cache = out
    _cache_at = now
    return list(out)
