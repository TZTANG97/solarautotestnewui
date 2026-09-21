# -*- coding: utf-8 -*-
"""云端试连：对本机地址做 TCP 通断 + 可选 *IDN?（不建立完整设备会话）。"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# 常见 Modbus 口：TCP 通即可视为可达（不发 *IDN?）
_MODBUS_PORTS = {502, 5025}


def _parse_host_port(resource: str):
    text = (resource or "").strip()
    if not text:
        return "", None
    try:
        from utils.device_discovery import parse_host_port

        host, port = parse_host_port(text)
        return (host or ""), port
    except Exception:
        if ":" in text and "://" not in text.lower():
            host, _, port_s = text.rpartition(":")
            try:
                return host.strip(), int(port_s.strip())
            except ValueError:
                return host.strip(), None
        return text, None


def probe_one_instrument(item: Dict[str, Any]) -> Dict[str, Any]:
    resource = str(item.get("resource") or "").strip()
    slot = str(item.get("slot") or "").strip().lower()
    kind = str(item.get("kind") or "").strip().lower()
    brand = str(item.get("brand") or "").strip()
    model = str(item.get("model") or "").strip()
    host = str(item.get("host") or "").strip()
    port = item.get("port")
    try:
        port_i = int(port) if port is not None and str(port).strip() != "" else None
    except (TypeError, ValueError):
        port_i = None
    if not host or port_i is None:
        h2, p2 = _parse_host_port(resource)
        host = host or (h2 or "")
        port_i = port_i if port_i is not None else p2

    base = {
        "resource": resource,
        "slot": slot,
        "kind": kind,
        "brand": brand,
        "model": model,
        "host": host,
        "port": port_i,
        "idn": "",
        "connected": False,
        "online": False,
        "error": "",
    }
    if not resource or resource.lower().startswith("pending:"):
        base["error"] = "地址无效或仍为 pending"
        return base
    if not host or port_i is None:
        base["error"] = "无法解析 host:port"
        return base

    try:
        from utils.device_discovery import probe_scpi_idn, tcp_open
    except Exception as exc:
        base["error"] = f"探测模块不可用: {exc}"
        return base

    if not tcp_open(host, int(port_i), timeout=0.8):
        base["error"] = f"TCP 不通 {host}:{port_i}"
        return base

    idn = ""
    if int(port_i) not in _MODBUS_PORTS:
        try:
            idn = probe_scpi_idn(host, int(port_i), timeout=0.8) or ""
        except Exception:
            idn = ""

    if idn:
        base["idn"] = idn
        try:
            from agent.instruments_snapshot import parse_scpi_idn

            b, m, _s = parse_scpi_idn(idn)
            base["brand"] = brand or b
            base["model"] = model or m
        except Exception:
            pass

    base["connected"] = True
    base["online"] = True
    base["error"] = ""
    return base


def probe_instruments(instruments: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in instruments or []:
        if not isinstance(item, dict):
            continue
        try:
            out.append(probe_one_instrument(item))
        except Exception as exc:
            logger.warning("probe failed: %s", exc)
            out.append(
                {
                    "resource": str(item.get("resource") or ""),
                    "slot": str(item.get("slot") or ""),
                    "kind": str(item.get("kind") or ""),
                    "connected": False,
                    "online": False,
                    "error": str(exc)[:255],
                    "idn": "",
                }
            )
    return out
