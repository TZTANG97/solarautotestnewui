# -*- coding: utf-8 -*-
"""工控机本机串口 / VISA 资源。只在台架上枚举，再随心跳/WS 交给云端供网页选择。

优先用 Windows 注册表（不依赖 pyserial），避免安装包漏打 serial 时整表空上报。
"""
from __future__ import annotations

import logging
import re
import time
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_cache: List[Dict[str, str]] = []
_cache_at: float = 0.0
_last_error: str = ""


def _add(out: List[Dict[str, str]], seen: set, *, kind: str, resource: str, label: str, com: str = "") -> None:
    key = (resource or "").strip().upper()
    if not key or key in seen:
        return
    seen.add(key)
    item = {"kind": kind, "resource": resource.strip(), "label": (label or resource).strip()}
    if com:
        item["com"] = com
    out.append(item)


def _com_to_asrl(com: str) -> Optional[str]:
    match = re.search(r"(\d+)$", (com or "").strip(), re.I)
    if not match:
        return None
    return f"ASRL{match.group(1)}::INSTR"


def _enumerate_winreg() -> Tuple[List[Dict[str, str]], Optional[str]]:
    """HARDWARE\\DEVICEMAP\\SERIALCOMM → COM 名（Windows 本机，无额外依赖）。"""
    out: List[Dict[str, str]] = []
    seen: set = set()
    try:
        import winreg  # type: ignore
    except ImportError:
        return out, "winreg unavailable"
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
    except OSError as exc:
        return out, f"SERIALCOMM open: {exc}"
    try:
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
            except OSError:
                break
            i += 1
            com = str(value or "").strip()
            if not com.upper().startswith("COM"):
                continue
            asrl = _com_to_asrl(com)
            if not asrl:
                continue
            label = f"{com} {name}".strip() if name else com
            _add(out, seen, kind="serial", resource=asrl, label=label, com=com)
    finally:
        try:
            winreg.CloseKey(key)
        except Exception:
            pass
    return out, None


def _enumerate_pyserial() -> Tuple[List[Dict[str, str]], Optional[str]]:
    out: List[Dict[str, str]] = []
    seen: set = set()
    try:
        from serial.tools import list_ports
    except ImportError:
        return out, "pyserial not installed"
    try:
        for port in list_ports.comports():
            dev = str(getattr(port, "device", "") or "").strip()
            desc = str(getattr(port, "description", "") or "").strip()
            asrl = _com_to_asrl(dev)
            if not asrl:
                continue
            label = f"{dev} {desc}".strip()
            _add(out, seen, kind="serial", resource=asrl, label=label, com=dev)
    except Exception as exc:
        return out, f"pyserial: {exc}"
    return out, None


def _merge(dst: List[Dict[str, str]], src: List[Dict[str, str]]) -> None:
    seen = {(x.get("resource") or "").upper() for x in dst}
    for item in src:
        key = (item.get("resource") or "").upper()
        if not key or key in seen:
            continue
        seen.add(key)
        dst.append(item)


def collect_local_endpoints(*, min_interval_sec: float = 15.0, force: bool = False) -> List[Dict[str, str]]:
    """枚举本机 COM，映射为桌面使用的 ASRL{n}::INSTR。不打开 VISA，避免心跳被资源管理器卡住。"""
    global _cache, _cache_at, _last_error
    now = time.time()
    if not force and _cache and (now - _cache_at) < float(min_interval_sec):
        return list(_cache)

    out: List[Dict[str, str]] = []
    errors: List[str] = []

    win_items, win_err = _enumerate_winreg()
    if win_err:
        errors.append(win_err)
    _merge(out, win_items)

    ser_items, ser_err = _enumerate_pyserial()
    if ser_err:
        errors.append(ser_err)
    _merge(out, ser_items)

    _last_error = "; ".join(errors) if errors and not out else ""
    if out:
        _cache = out
        _cache_at = now
        if errors:
            logger.debug("串口枚举部分失败但已有结果: %s", _last_error)
        return list(_cache)

    # 枚举失败时保留上一帧，避免网页闪成「尚未上报」
    if _cache:
        logger.warning("串口枚举为空/失败，保留上次 %s 个: %s", len(_cache), "; ".join(errors) or "none")
        _cache_at = now
        return list(_cache)

    _cache = []
    _cache_at = now
    if errors:
        logger.warning("串口枚举失败且无缓存: %s", "; ".join(errors))
    return []


def last_collect_error() -> str:
    return _last_error
