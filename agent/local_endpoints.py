# -*- coding: utf-8 -*-
"""工控机本机串口 / VISA 资源。只在台架上枚举，再随心跳/WS 交给云端供网页选择。

优先用 Windows 注册表（不依赖 pyserial），避免安装包漏打 serial 时整表空上报。
"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_cache: List[Dict[str, str]] = []
_cache_at: float = 0.0
_last_error: str = ""
_last_warn_at: float = 0.0
_last_warn_msg: str = ""


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
        # 本机无串口时该键常不存在（WinError 2），属正常空结果，勿当故障刷屏
        winerr = getattr(exc, "winerror", None)
        errno = getattr(exc, "errno", None)
        if winerr == 2 or errno == 2:
            return out, None
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


_PLACEHOLDER_RESOURCES = {"未发现可连接设备", "未配置", "-"}


def scanned_resources_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config_files" / "scanned_resources.json"


def _usable_scanned_resource(text: str) -> bool:
    raw = (text or "").strip()
    if not raw or raw in _PLACEHOLDER_RESOURCES or raw.startswith("--"):
        return False
    upper = raw.upper()
    if upper.startswith(("TCPIP", "ASRL", "USB", "GPIB", "COM")):
        return True
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}(:\d+)?$", raw))


def _resource_to_endpoint(resource: str) -> Dict[str, str]:
    upper = resource.upper()
    if upper.startswith("USB"):
        return {"kind": "usb", "resource": resource, "label": resource}
    if upper.startswith("GPIB"):
        return {"kind": "gpib", "resource": resource, "label": resource}
    if upper.startswith("ASRL") or upper.startswith("COM"):
        com = ""
        match = re.search(r"ASRL(\d+)", upper)
        if match:
            com = f"COM{match.group(1)}"
        elif upper.startswith("COM"):
            com = resource.split("::", 1)[0]
        label = f"{com} {resource}".strip() if com and com.upper() not in upper else resource
        item = {"kind": "serial", "resource": resource, "label": label}
        if com:
            item["com"] = com
        return item
    if upper.startswith("TCPIP") or ":" in resource:
        return {"kind": "network", "resource": resource, "label": resource}
    return {"kind": "visa", "resource": resource, "label": resource}


def remember_scanned_resources(resources: Optional[List[str]]) -> None:
    """桌面 VISA/网口扫描结果落盘。空列表或占位文案不覆盖上一帧。"""
    items: List[Dict[str, str]] = []
    seen = set()
    for raw in resources or []:
        if isinstance(raw, dict):
            text = str(raw.get("resource") or "").strip()
        else:
            text = str(raw or "").strip()
        if not _usable_scanned_resource(text):
            continue
        key = text.upper()
        if key in seen:
            continue
        seen.add(key)
        items.append(_resource_to_endpoint(text))
    if not items:
        return
    text = json.dumps(items, ensure_ascii=False)
    path = scanned_resources_path()
    try:
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            return
    except Exception:
        pass
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except Exception as exc:
        logger.debug("写入扫描资源失败: %s", exc)


def load_scanned_resources() -> List[Dict[str, str]]:
    path = scanned_resources_path()
    try:
        if not path.is_file():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    out: List[Dict[str, str]] = []
    for raw in data:
        if isinstance(raw, dict):
            resource = str(raw.get("resource") or "").strip()
            if not _usable_scanned_resource(resource):
                continue
            item = _resource_to_endpoint(resource)
            label = str(raw.get("label") or "").strip()
            if label:
                item["label"] = label
            kind = str(raw.get("kind") or "").strip().lower()
            if kind in ("serial", "usb", "gpib", "visa", "network"):
                item["kind"] = kind
            com = str(raw.get("com") or "").strip()
            if com:
                item["com"] = com
            out.append(item)
        elif _usable_scanned_resource(str(raw or "")):
            out.append(_resource_to_endpoint(str(raw).strip()))
    return out


def _with_scanned(items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = list(items)
    _merge(out, load_scanned_resources())
    _merge(out, _endpoints_from_status_json())
    return out


def status_json_path() -> Path:
    return Path(__file__).resolve().parent.parent / "status.json"


def _endpoints_from_status_json() -> List[Dict[str, str]]:
    """把 status.json 里已配置/曾连接的网口·串口地址并进上报，避免网页「上报 0」却左侧已有交流源。"""
    path = status_json_path()
    try:
        if not path.is_file():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    rows = data.get("devices") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    out: List[Dict[str, str]] = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        resource = str(row.get("resource") or "").strip()
        if not _usable_scanned_resource(resource):
            continue
        # 残缺 IP 不上报
        if re.match(r"^\d{1,3}(\.\d{1,3}){0,2}$", resource):
            continue
        key = resource.upper()
        if key in seen:
            continue
        seen.add(key)
        item = _resource_to_endpoint(resource)
        name = str(row.get("name") or "").strip()
        if name:
            item["label"] = f"{name} · {item.get('label') or resource}"
        out.append(item)
    return out


def collect_local_endpoints(*, min_interval_sec: float = 15.0, force: bool = False) -> List[Dict[str, str]]:
    """枚举本机 COM，并带上桌面已扫描的 USB/网口与 status.json 已知地址。不在心跳里打开 VISA。"""
    global _cache, _cache_at, _last_error
    now = time.time()
    if not force and _cache and (now - _cache_at) < float(min_interval_sec):
        return _with_scanned(_cache)

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
    _merge(out, load_scanned_resources())
    _merge(out, _endpoints_from_status_json())

    _last_error = "; ".join(errors) if errors and not out else ""
    if out:
        _cache = out
        _cache_at = now
        if errors:
            logger.debug("串口枚举部分失败但已有结果: %s", _last_error)
        return list(_cache)

    def _warn_throttled(msg: str) -> None:
        global _last_warn_at, _last_warn_msg
        # 同类告警至少隔 5 分钟再打，避免 Agent 日志页被刷爆卡死
        if msg == _last_warn_msg and (now - _last_warn_at) < 300.0:
            return
        _last_warn_at = now
        _last_warn_msg = msg
        logger.warning("%s", msg)

    # 枚举失败时保留上一帧，避免网页闪成「尚未上报」
    if _cache:
        if errors:
            _warn_throttled(
                f"串口枚举为空/失败，保留上次 {len(_cache)} 个: {'; '.join(errors)}"
            )
        _cache_at = now
        return list(_cache)

    _cache = []
    _cache_at = now
    if errors:
        _warn_throttled(f"串口枚举失败且无缓存: {'; '.join(errors)}")
    return []


def last_collect_error() -> str:
    return _last_error
