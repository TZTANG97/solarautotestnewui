# -*- coding: utf-8 -*-
"""设备发现：上次地址优先，可选局域网扫描，按 *IDN?/端口分类。不负责真正连接。"""
from __future__ import annotations

import json
import os
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# 常见仪器端口（去掉 23，减少误报和耗时）
SCPI_PORTS = (2101, 5025, 5024)
DEW_PORT = 10001
ITECH_PORTS = (8080, 502)
MODBUS_PORTS = (502, 8080)
ALL_PROBE_PORTS = tuple(sorted(set(SCPI_PORTS + ITECH_PORTS + (DEW_PORT,))))
NO_IDN_PORTS = frozenset(MODBUS_PORTS)

SLOT_CHOICES = (
    ("", "未指定"),
    ("ac", "交流电源"),
    ("dc1", "直流电源1"),
    ("dc2", "直流电源2"),
    ("dc3", "直流电源3"),
    ("dc4", "直流电源4"),
    ("scope", "示波器"),
    ("wt", "功率分析仪"),
    ("dew", "德威创"),
)

KIND_LABELS = {
    "ac": "交流源",
    "dc": "直流源",
    "scope": "示波器",
    "wt": "功率分析仪",
    "dew": "德威创",
    "modbus": "Modbus(爱科/蓝电)",
    "unknown": "未识别",
}

# 输入框只记 IP，扫描时要拼回常用端口
_IP_PORT_KEYS = (
    ("ac.ip", "ac.port", 8080),
    ("chroma.ac.ip", "chroma.ac.port", 2101),
    ("dc.ip", "dc.port", 502),
    ("itech.dc.ip", "itech.dc.port", 502),
    ("dewetron.ip", "dewetron.port", 10001),
    ("wt.ip", "wt.port", 5025),
)

_FINDER_HISTORY_KEY = "device.finder.resource"


@dataclass
class FoundDevice:
    resource: str
    host: str = ""
    port: Optional[int] = None
    idn: str = ""
    kind_hint: str = "unknown"
    brand_hint: str = ""
    source: str = ""
    protocol: str = ""
    extra: dict = field(default_factory=dict)

    def display_idn(self) -> str:
        text = (self.idn or "").strip()
        if len(text) > 80:
            return text[:77] + "..."
        if text:
            return text
        if self.protocol == "modbus":
            return "Modbus 口无 *IDN?，请人手指定交流或直流槽位"
        return "—"

    def kind_label(self) -> str:
        if self.extra.get("offline"):
            return "离线"
        return KIND_LABELS.get(self.kind_hint, self.kind_hint or "未识别")


def classify_idn(idn: str) -> Tuple[str, str]:
    """根据 *IDN? 返回 (kind_hint, brand_hint)。槽位仍须人手指定。"""
    u = (idn or "").upper()
    if not u.strip():
        return "unknown", ""
    if "DEWETRON" in u or "OXYGEN" in u:
        return "dew", "dewetron"
    scope_keys = (
        "DL850",
        "DLM",
        "OSCILLOSCOPE",
        "TEKTRONIX",
        "KEYSIGHT,DSO",
        "KEYSIGHT,MSO",
        "KEYSIGHT,MSOX",
        "RIGOL,DS",
        "RIGOL,MSO",
        "SIGLENT,SDS",
        "LECROY",
        "YOKOGAWA,DL",
        "YOKOGAWA,DLM",
    )
    if any(k in u for k in scope_keys):
        return "scope", "scope"
    if "YOKOGAWA" in u and any(k in u for k in ("WT180", "WT300", "WT500", "WT160", "WT200")):
        return "wt", "yokogawa"
    if "YOKOGAWA" in u and "WT" in u:
        return "wt", "yokogawa"
    if "ITECH" in u or "I TECH" in u or ",IT" in u:
        if any(k in u for k in ("AC SOURCE", "IT76", "IT78", "IT73")):
            return "ac", "itech"
        if any(k in u for k in ("SOLAR", "IT6", "IT8")):
            return "dc", "itech"
        return "unknown", "itech"
    if "CHROMA" in u:
        if any(k in u for k in ("618", "61511", "61512", "616", "AC SOURCE", "61800")):
            return "ac", "chroma"
        return "dc", "chroma"
    if "BLUESIGHT" in u or "蓝电" in u or "LANDAIAN" in u:
        return "dc", "bluesight"
    if "KEYSIGHT" in u or "AGILENT" in u:
        if any(k in u for k in ("AC", "681", "N67")):
            return "ac", "keysight"
        return "unknown", "keysight"
    return "unknown", ""


def classify_port(port: Optional[int]) -> Tuple[str, str, str]:
    """无 IDN 时按端口给弱提示 (kind, brand, protocol)。"""
    if port == DEW_PORT:
        return "dew", "dewetron", "dew_socket"
    if port in (2101,):
        return "ac", "chroma", "scpi_tcp"
    if port in (5025, 5024):
        return "wt", "yokogawa", "scpi_tcp"
    if port == 8080:
        return "modbus", "itech", "modbus"
    if port == 502:
        return "modbus", "", "modbus"
    return "unknown", "", "tcp"


def parse_host_port(resource: str) -> Tuple[str, Optional[int]]:
    text = (resource or "").strip()
    if not text:
        return "", None
    upper = text.upper()
    if upper.startswith("TCPIP"):
        parts = text.split("::")
        host = parts[1] if len(parts) >= 2 else ""
        port = None
        if len(parts) >= 3 and parts[2].isdigit():
            port = int(parts[2])
        return host, port
    if upper.startswith(("ASRL", "USB", "GPIB", "COM")):
        return "", None
    if ":" in text:
        host, _, rest = text.partition(":")
        if rest.isdigit():
            return host.strip(), int(rest)
    if _looks_ipv4(text):
        return text, None
    return "", None


def _looks_ipv4(text: str) -> bool:
    parts = text.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def is_valid_finder_resource(resource: str) -> bool:
    """可用于「上次」列表的地址：完整 IPv4[:port] 或 VISA 资源串。"""
    text = (resource or "").strip()
    if not text:
        return False
    upper = text.upper()
    if upper.startswith(("TCPIP", "ASRL", "USB", "GPIB", "COM")):
        return True
    host, port = parse_host_port(text)
    if host and _looks_ipv4(host):
        if port is None:
            return True
        return 1 <= int(port) <= 65535
    return False


def validate_assignments(rows: Sequence[Tuple[bool, str, FoundDevice]]) -> Optional[str]:
    """rows: (checked, slot_id, device)。勾选必须人手指定槽位，槽位不可重复。"""
    used = {}
    any_checked = False
    for checked, slot, dev in rows:
        if not checked:
            continue
        any_checked = True
        if not slot:
            return "勾选的设备必须人手指定槽位（同型号多台不会自动占槽）。"
        if slot in used:
            return f"槽位重复：{dict(SLOT_CHOICES).get(slot, slot)} 被多台勾选。"
        used[slot] = dev.resource
    if not any_checked:
        return "请先勾选要连接的设备。"
    return None


def devices_from_status_json(status_json_path: Optional[str] = None) -> List[FoundDevice]:
    """从 status.json 恢复「上次槽位 + 资源」，USB/网口直流都能带上槽位。"""
    path = (status_json_path or "").strip()
    if not path or not os.path.isfile(path):
        return []
    name_to_slot = {label: slot for slot, label in SLOT_CHOICES if slot}
    # status.json 历史命名与 SLOT_CHOICES 中文不完全一致
    name_to_slot.update(
        {
            "DL850": "scope",
            "示波器": "scope",
            "WT3000": "wt",
            "功率分析仪": "wt",
            "DEWETRON": "dew",
            "德威创": "dew",
        }
    )
    slot_to_kind = {
        "ac": "ac",
        "dc1": "dc",
        "dc2": "dc",
        "dc3": "dc",
        "dc4": "dc",
        "scope": "scope",
        "wt": "wt",
        "dew": "dew",
    }
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    out: List[FoundDevice] = []
    for row in data.get("devices") or []:
        if not isinstance(row, dict):
            continue
        res = str(row.get("resource") or "").strip()
        name = str(row.get("name") or "").strip()
        if not res or not is_valid_finder_resource(res):
            continue
        slot = name_to_slot.get(name) or ""
        host, port = parse_host_port(res)
        kind = slot_to_kind.get(slot, "unknown")
        proto = "visa"
        upper = res.upper()
        if host and port:
            _k, _b, proto = classify_port(port)
            if kind == "unknown":
                kind = _k
        elif not upper.startswith(("USB", "GPIB", "ASRL", "COM", "TCPIP")):
            proto = "scpi_tcp"
        out.append(
            FoundDevice(
                resource=res,
                host=host or "",
                port=port,
                kind_hint=kind,
                brand_hint="",
                source="status",
                protocol=proto,
                extra={"last_slot": slot} if slot else {},
            )
        )
    return out


def last_known_resources(status_json_path: Optional[str] = None) -> List[str]:
    """本机上次连过的地址：字段记忆 + 发现历史 + status.json。裸 IP 会拼上记忆端口。

    只保留合法 IPv4[:port] / VISA 资源，丢掉半截输入（如 192.10）。
    """
    out: List[str] = []
    try:
        from utils.ui_field_helpers import last_value, load_history

        out.extend(load_history(_FINDER_HISTORY_KEY))
        for ip_key, port_key, default_port in _IP_PORT_KEYS:
            port_text = last_value(port_key, str(default_port)) or str(default_port)
            try:
                port_num = (
                    int(str(port_text).strip())
                    if str(port_text).strip().isdigit()
                    else int(default_port)
                )
            except ValueError:
                port_num = int(default_port)
            for item in load_history(ip_key):
                host, existing = parse_host_port(item)
                if host and existing and _looks_ipv4(host):
                    out.append(f"{host}:{existing}")
                elif host and _looks_ipv4(host):
                    out.append(f"{host}:{port_num}")
                elif item and is_valid_finder_resource(item):
                    out.append(item)
    except Exception:
        pass
    if status_json_path and os.path.isfile(status_json_path):
        try:
            with open(status_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for dev in data.get("devices") or []:
                res = str(dev.get("resource") or "").strip()
                if res:
                    out.append(res)
        except Exception:
            pass
    try:
        out.extend(load_success_device_map().keys())
    except Exception:
        pass
    seen = set()
    unique: List[str] = []
    for item in out:
        item = str(item).strip()
        if not item or item in seen:
            continue
        if not is_valid_finder_resource(item):
            continue
        seen.add(item)
        unique.append(item)
    return unique


def remember_found_resource(resource: str) -> None:
    text = (resource or "").strip()
    if not text or not is_valid_finder_resource(text):
        return
    try:
        from utils.ui_field_helpers import remember_value

        remember_value(_FINDER_HISTORY_KEY, text)
    except Exception:
        pass


_SUCCESS_MAP_KEY = "device.finder.success_map"


def load_success_device_map() -> Dict[str, dict]:
    """上次成功连接快照：resource → {idn, kind_hint, brand_hint, slot, ...}。"""
    try:
        from utils.ui_field_helpers import last_value

        raw = last_value(_SUCCESS_MAP_KEY, "") or ""
        if not raw.strip():
            return {}
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        out: Dict[str, dict] = {}
        for k, v in data.items():
            key = str(k).strip()
            if not key or not isinstance(v, dict):
                continue
            out[key] = dict(v)
        return out
    except Exception:
        return {}


def remember_successful_device(slot: str, dev: FoundDevice) -> None:
    """连接成功后记住识别信息与槽位，下次「上次」列表直接带出。"""
    res = (getattr(dev, "resource", "") or "").strip()
    if not res or not is_valid_finder_resource(res):
        return
    try:
        from utils.ui_field_helpers import remember_value

        m = load_success_device_map()
        entry = {
            "idn": str(getattr(dev, "idn", "") or ""),
            "kind_hint": str(getattr(dev, "kind_hint", "") or "unknown"),
            "brand_hint": str(getattr(dev, "brand_hint", "") or ""),
            "protocol": str(getattr(dev, "protocol", "") or ""),
            "slot": str(slot or "").strip().lower(),
            "host": str(getattr(dev, "host", "") or ""),
            "port": getattr(dev, "port", None),
        }
        m[res] = entry
        if getattr(dev, "host", None) and getattr(dev, "port", None):
            m[f"{dev.host}:{dev.port}"] = entry
        remember_value(_SUCCESS_MAP_KEY, json.dumps(m, ensure_ascii=False))
        remember_found_resource(res)
    except Exception:
        pass


def _windows_ipv4s() -> List[str]:
    """列出本机全部网卡 IPv4（不只默认路由那一块）。"""
    import subprocess

    ips: List[str] = []
    try:
        kwargs = {"stderr": subprocess.DEVNULL}
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        raw = subprocess.check_output(["ipconfig"], timeout=5, **kwargs)
        text = raw.decode("gbk", errors="replace")
        if "IPv4" not in text and "IP Address" not in text:
            text = raw.decode("utf-8", errors="replace")
        for line in text.splitlines():
            if "IPv4" not in line and "IP Address" not in line:
                continue
            if ":" not in line:
                continue
            candidate = line.split(":")[-1].strip()
            candidate = candidate.split("(")[0].strip()
            if _looks_ipv4(candidate):
                ips.append(candidate)
    except Exception:
        pass
    return ips


def local_ipv4_addrs() -> List[str]:
    ips: List[str] = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.append(info[4][0])
    except Exception:
        pass
    try:
        ips.extend(socket.gethostbyname_ex(socket.gethostname())[2])
    except Exception:
        pass
    ips.extend(_windows_ipv4s())
    out: List[str] = []
    seen = set()
    for ip in ips:
        if not _looks_ipv4(ip) or ip.startswith("127.") or ip.startswith("169.254."):
            continue
        if ip not in seen:
            seen.add(ip)
            out.append(ip)
    return out


def local_ipv4_prefixes(extra_hosts: Optional[Sequence[str]] = None) -> List[str]:
    prefixes = []
    seen = set()
    for ip in local_ipv4_addrs():
        prefix = ".".join(ip.split(".")[:3])
        if prefix not in seen:
            seen.add(prefix)
            prefixes.append(prefix)
    for host in extra_hosts or ():
        if not _looks_ipv4(str(host)):
            continue
        prefix = ".".join(str(host).split(".")[:3])
        if prefix.startswith("127.") or prefix.startswith("169.254"):
            continue
        if prefix not in seen:
            seen.add(prefix)
            prefixes.append(prefix)
    return prefixes


def local_ipv4_self() -> List[str]:
    return local_ipv4_addrs()


def tcp_open(host: str, port: int, timeout: float = 0.2) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        return sock.connect_ex((host, int(port))) == 0
    except Exception:
        return False
    finally:
        try:
            sock.close()
        except Exception:
            pass


def probe_scpi_idn(host: str, port: int, timeout: float = 0.6) -> str:
    if int(port) in NO_IDN_PORTS:
        return ""
    try:
        with socket.create_connection((host, int(port)), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(b"*IDN?\n")
            chunks = []
            try:
                chunks.append(sock.recv(512))
            except Exception:
                pass
            text = b"".join(chunks).decode("utf-8", errors="replace").strip()
            if not text:
                sock.sendall(b"*IDN?\r\n")
                chunks.append(sock.recv(512))
                text = b"".join(chunks).decode("utf-8", errors="replace").strip()
        return text.replace("\x00", "").splitlines()[0].strip() if text else ""
    except Exception:
        return ""


def _device_from_host_port(host: str, port: int, source: str) -> FoundDevice:
    port = int(port)
    idn = "" if port in NO_IDN_PORTS else probe_scpi_idn(host, port)
    kind, brand = classify_idn(idn)
    p_kind, p_brand, proto = classify_port(port)
    if kind == "unknown":
        kind, brand = p_kind, brand or p_brand
    elif not brand:
        brand = p_brand
    if port == DEW_PORT:
        proto = "dew_socket"
    elif port in ITECH_PORTS and kind in ("ac", "unknown") and brand in ("itech", ""):
        proto = "modbus"
    elif port in MODBUS_PORTS and kind in ("dc", "unknown"):
        proto = "modbus"
    elif proto == "tcp" and idn:
        proto = "scpi_tcp"
    resource = f"{host}:{port}"
    return FoundDevice(
        resource=resource,
        host=host,
        port=port,
        idn=idn,
        kind_hint=kind,
        brand_hint=brand,
        source=source,
        protocol=proto,
    )


def list_visa_resources(rm, include_serial: bool = False) -> List[str]:
    if rm is None:
        return []
    try:
        items = list(rm.list_resources())
    except Exception:
        return []
    out = []
    for item in items:
        text = str(item)
        upper = text.upper()
        if upper.startswith("ASRL") and not include_serial:
            continue
        if any(upper.startswith(p) for p in ("USB", "GPIB", "TCPIP", "ASRL")):
            out.append(text)
    return out


def probe_visa_idn(rm, resource: str, timeout_ms: int = 400) -> str:
    if rm is None:
        return ""
    upper = (resource or "").upper()
    # 串口 *IDN? 又慢又容易把已占用 COM 锁死，默认跳过
    if upper.startswith("ASRL"):
        return ""
    handle = None
    try:
        handle = rm.open_resource(resource)
        try:
            handle.timeout = timeout_ms
        except Exception:
            pass
        try:
            raw = handle.query("*IDN?")
        except Exception:
            handle.write("*IDN?")
            raw = handle.read()
        return str(raw).strip().splitlines()[0].strip()
    except Exception:
        return ""
    finally:
        if handle is not None:
            try:
                handle.close()
            except Exception:
                pass


def devices_from_last_resources(resources: Iterable[str], source: str = "上次") -> List[FoundDevice]:
    success = load_success_device_map()
    found: List[FoundDevice] = []
    for res in resources:
        res = str(res).strip()
        if not res or not is_valid_finder_resource(res):
            continue
        host, port = parse_host_port(res)
        kind, brand = "unknown", ""
        proto = "visa"
        idn = ""
        snap = success.get(res) or (
            success.get(f"{host}:{port}") if host and port else None
        )
        extra: dict = {}
        if isinstance(snap, dict):
            idn = str(snap.get("idn") or "")
            kind = str(snap.get("kind_hint") or kind)
            brand = str(snap.get("brand_hint") or brand)
            proto = str(snap.get("protocol") or proto)
            if snap.get("slot"):
                extra["last_slot"] = str(snap.get("slot") or "")
            if not host:
                host = str(snap.get("host") or "")
            if port is None and snap.get("port") is not None:
                try:
                    port = int(snap.get("port"))
                except (TypeError, ValueError):
                    port = None
        elif host and port:
            p_kind, p_brand, proto = classify_port(port)
            kind, brand = p_kind, p_brand
        elif host:
            proto = "scpi_tcp"
        found.append(
            FoundDevice(
                resource=res if not (host and port) else f"{host}:{port}",
                host=host,
                port=port,
                idn=idn,
                kind_hint=kind or "unknown",
                brand_hint=brand,
                source=source,
                protocol=proto,
                extra=extra,
            )
        )
    return found


def _offline_device(dev: FoundDevice, reason: str) -> FoundDevice:
    extra = dict(dev.extra)
    extra["offline"] = True
    extra["detail"] = reason
    return FoundDevice(
        resource=dev.resource,
        host=dev.host,
        port=dev.port,
        idn=f"未响应：{reason}",
        kind_hint="unknown",
        brand_hint=dev.brand_hint,
        source=dev.source or "上次",
        protocol=dev.protocol,
        extra=extra,
    )


def _best_open_on_host(host: str, source: str, timeout: float, preferred_port: Optional[int] = None) -> Optional[FoundDevice]:
    ports: List[int] = []
    if preferred_port:
        ports.append(int(preferred_port))
    for port in ALL_PROBE_PORTS:
        if port not in ports:
            ports.append(int(port))
    found: List[FoundDevice] = []
    for port in ports:
        if tcp_open(host, port, timeout=timeout):
            found.append(_device_from_host_port(host, port, source))
    if not found:
        return None

    def _score(dev: FoundDevice) -> int:
        score = 0
        if dev.idn:
            score += 10
        if dev.kind_hint in ("ac", "dc", "scope", "wt", "dew"):
            score += 5
        if dev.kind_hint == "modbus":
            score += 2
        if preferred_port and dev.port == preferred_port:
            score += 1
        return score

    return max(found, key=_score)


def enrich_device(dev: FoundDevice, rm=None, skip_resources: Optional[Sequence[str]] = None) -> FoundDevice:
    """对已有条目做端口/*IDN? 探测，补识别信息。不通的记为离线，不假装已识别。"""
    skip = set(skip_resources or ())
    if dev.resource in skip or (dev.host and dev.port and f"{dev.host}:{dev.port}" in skip):
        extra = dict(dev.extra)
        extra["skipped"] = "already_connected"
        return FoundDevice(
            resource=dev.resource,
            host=dev.host,
            port=dev.port,
            idn=dev.idn or "(已连接，跳过探测)",
            kind_hint=dev.kind_hint,
            brand_hint=dev.brand_hint,
            source=dev.source,
            protocol=dev.protocol,
            extra=extra,
        )
    last_timeout = 0.45
    if dev.host and dev.port:
        if not tcp_open(dev.host, int(dev.port), timeout=last_timeout):
            probed = _best_open_on_host(dev.host, dev.source or "上次", last_timeout, preferred_port=int(dev.port))
            if probed is None:
                return _offline_device(dev, f"端口 {dev.port} 未开放（关机、不同网段或端口不对）")
            probed.source = dev.source or probed.source
            return probed
        probed = _device_from_host_port(dev.host, int(dev.port), dev.source or "扫描")
        probed.source = dev.source or probed.source
        return probed
    if dev.host and not dev.port:
        probed = _best_open_on_host(dev.host, dev.source or "上次", last_timeout)
        if probed is None:
            return _offline_device(dev, "常用端口未开放（关机、不同网段或只记了 IP）")
        return probed
    if rm is not None and dev.resource:
        idn = probe_visa_idn(rm, dev.resource)
        kind, brand = classify_idn(idn)
        return FoundDevice(
            resource=dev.resource,
            host=dev.host,
            port=dev.port,
            idn=idn,
            kind_hint=kind,
            brand_hint=brand,
            source=dev.source or "VISA",
            protocol="visa",
        )
    return dev


def scan_lan(
    prefixes: Optional[Sequence[str]] = None,
    ports: Sequence[int] = ALL_PROBE_PORTS,
    timeout: float = 0.2,
    max_workers: int = 128,
    progress: Optional[Callable[[str], None]] = None,
    cancel_flag: Optional[Callable[[], bool]] = None,
    skip_hosts: Optional[Sequence[str]] = None,
    hosts: Optional[Sequence[str]] = None,
    extra_hosts: Optional[Sequence[str]] = None,
) -> List[FoundDevice]:
    skip_hosts = set(skip_hosts or ()) | set(local_ipv4_self())
    found: List[FoundDevice] = []
    seen = set()
    jobs = []
    if hosts:
        target_hosts = [h for h in hosts if h and h not in skip_hosts]
    else:
        prefixes = list(prefixes or local_ipv4_prefixes(extra_hosts=extra_hosts))
        target_hosts = []
        for prefix in prefixes:
            for last in range(1, 255):
                host = f"{prefix}.{last}"
                if host not in skip_hosts:
                    target_hosts.append(host)
    for host in extra_hosts or ():
        if host and host not in skip_hosts and host not in target_hosts:
            target_hosts.append(host)
    for host in target_hosts:
        for port in ports:
            jobs.append((host, port))
    total = len(jobs)
    if progress:
        nets = ",".join(f"{p}.0/24" for p in (prefixes or local_ipv4_prefixes(extra_hosts=extra_hosts)))
        progress(f"局域网扫描 {nets or '无网段'}，共 {total} 个端点…")
    done = 0
    open_eps = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {pool.submit(tcp_open, h, p, timeout): (h, p) for h, p in jobs}
        for fut in as_completed(futs):
            if cancel_flag and cancel_flag():
                break
            done += 1
            if done % 500 == 0 and progress:
                progress(f"局域网扫描 {done}/{total}")
            try:
                ok = fut.result()
            except Exception:
                ok = False
            if ok:
                open_eps.append(futs[fut])
    if progress:
        progress(f"识别 {len(open_eps)} 个开放端口…")
    idn_jobs = []
    for host, port in open_eps:
        if cancel_flag and cancel_flag():
            break
        key = (host, port)
        if key in seen:
            continue
        seen.add(key)
        idn_jobs.append((host, port))
    with ThreadPoolExecutor(max_workers=min(16, max(4, len(idn_jobs) or 1))) as pool:
        futs = {pool.submit(_device_from_host_port, h, p, "局域网"): (h, p) for h, p in idn_jobs}
        for fut in as_completed(futs):
            if cancel_flag and cancel_flag():
                break
            try:
                found.append(fut.result())
            except Exception:
                h, p = futs[fut]
                found.append(FoundDevice(resource=f"{h}:{p}", host=h, port=p, source="局域网"))
    return found


def merge_devices(*groups: Iterable[FoundDevice]) -> List[FoundDevice]:
    by_key: Dict[tuple, FoundDevice] = {}
    order: List[tuple] = []

    def _key(dev: FoundDevice) -> tuple:
        if dev.host and dev.port:
            return ("hp", dev.host, int(dev.port))
        if dev.host:
            return ("h", dev.host)
        return ("r", dev.resource)

    def _score(dev: FoundDevice) -> int:
        if dev.extra.get("offline"):
            return -10
        score = 0
        idn = (dev.idn or "").strip()
        if idn and not idn.startswith("未响应") and not idn.startswith("("):
            score += 10
        if dev.kind_hint in ("ac", "dc", "scope", "wt", "dew"):
            score += 5
        elif dev.kind_hint == "modbus":
            score += 2
        if dev.port:
            score += 1
        if dev.source == "局域网":
            score += 1
        return score

    def _richer(a: FoundDevice, b: FoundDevice) -> FoundDevice:
        return b if _score(b) > _score(a) else a

    host_only = {}
    for group in groups:
        for dev in group:
            key = _key(dev)
            if key[0] == "hp":
                host_only.pop(("h", key[1]), None)
            if key not in by_key:
                by_key[key] = dev
                order.append(key)
                if key[0] == "h":
                    host_only[key] = True
            else:
                by_key[key] = _richer(by_key[key], dev)

    # 裸 IP 已被同主机带端口条目覆盖时，丢掉裸 IP 行；在线结果优先于离线「上次」
    live_hosts = {
        d.host
        for d in by_key.values()
        if d.host and not d.extra.get("offline") and d.port
    }
    hp_hosts = {k[1] for k in by_key if k[0] == "hp"}
    filtered = []
    seen_keys = set()
    for key in order:
        if key[0] == "h" and key[1] in hp_hosts:
            continue
        if key in seen_keys or key not in by_key:
            continue
        dev = by_key[key]
        if dev.extra.get("offline") and dev.host in live_hosts:
            continue
        seen_keys.add(key)
        filtered.append(dev)
    return filtered


def run_discovery(
    visa_rm=None,
    last_resources: Optional[Sequence[str]] = None,
    scan_lan_enabled: bool = False,
    progress: Optional[Callable[[str], None]] = None,
    cancel_flag: Optional[Callable[[], bool]] = None,
    skip_resources: Optional[Sequence[str]] = None,
    include_serial: bool = False,
) -> List[FoundDevice]:
    last_resources = list(last_resources or [])
    last_devs = devices_from_last_resources(last_resources, source="上次")
    if progress:
        progress("探测上次地址与本机 VISA…")

    def _enrich(dev):
        return enrich_device(dev, rm=visa_rm, skip_resources=skip_resources)

    enriched_last: List[FoundDevice] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(_enrich, dev) for dev in last_devs]
        for fut in as_completed(futs):
            if cancel_flag and cancel_flag():
                break
            try:
                enriched_last.append(fut.result())
            except Exception:
                pass

    visa_raw = [
        FoundDevice(resource=res, source="VISA", protocol="visa")
        for res in list_visa_resources(visa_rm, include_serial=include_serial)
        if res not in set(last_resources)
    ]
    visa_devs: List[FoundDevice] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = [pool.submit(_enrich, dev) for dev in visa_raw]
        for fut in as_completed(futs):
            if cancel_flag and cancel_flag():
                break
            try:
                visa_devs.append(fut.result())
            except Exception:
                pass

    lan_devs: List[FoundDevice] = []
    prefixes: List[str] = []
    if scan_lan_enabled:
        last_hosts = [d.host for d in last_devs if d.host]
        prefixes = local_ipv4_prefixes(extra_hosts=last_hosts)
        if progress:
            nets = ",".join(f"{p}.0/24" for p in prefixes) or "无可用网段"
            progress(f"局域网将扫描：{nets}")
        lan_devs = scan_lan(
            prefixes=prefixes,
            progress=progress,
            cancel_flag=cancel_flag,
            extra_hosts=last_hosts,
        )
    devices = merge_devices(enriched_last, visa_devs, lan_devs)
    if progress and scan_lan_enabled:
        progress(summarize_discovery(devices, prefixes=prefixes, lan_raw=len(lan_devs)))
    return devices


def summarize_discovery(
    devices: Sequence[FoundDevice],
    prefixes: Optional[Sequence[str]] = None,
    lan_raw: Optional[int] = None,
) -> str:
    total = len(devices)
    offline = sum(1 for d in devices if d.extra.get("offline"))
    identified = sum(
        1
        for d in devices
        if not d.extra.get("offline") and d.kind_hint not in ("", "unknown")
    )
    lan = sum(1 for d in devices if d.source == "局域网")
    extra = ""
    if prefixes:
        extra += "扫描网段 " + ",".join(f"{p}.0/24" for p in prefixes) + "。"
    if lan_raw == 0 and prefixes:
        extra += "这些网段上常见仪器端口未开放（设备关机、网段不对或防火墙拦截）。"
    elif lan_raw is not None:
        extra += f"局域网原始命中 {lan_raw}。"
    return (
        f"扫描完成 {total} 台：识别 {identified}，离线/未响应 {offline}，局域网新发现 {lan}。"
        + extra
    )


def connect_plan(slot: str, dev: FoundDevice) -> Dict[str, object]:
    """把发现结果映射到现有连接路径（仍不自动占槽）。"""
    host = dev.host or ""
    port = dev.port
    if not host:
        host, port = parse_host_port(dev.resource)
    brand = (dev.brand_hint or "").lower()
    proto = dev.protocol or ""
    resource = dev.resource
    visa_like = resource.upper().startswith(("USB", "GPIB", "ASRL", "TCPIP"))
    if slot == "ac":
        if brand == "itech" or proto == "modbus":
            return {"target": "ac_itech", "host": host, "port": int(port or 502)}
        if visa_like and not host:
            return {"target": "ac_visa", "resource": resource}
        return {"target": "ac_chroma_ip", "host": host, "port": port}
    if slot in ("dc1", "dc2", "dc3", "dc4"):
        n = int(slot[-1])
        if brand == "itech" or (dev.port == 8080):
            return {
                "target": "dc_itech",
                "n": n,
                "device_type": "itech",
                "addr": host or resource,
                "host": host,
                "port": port,
            }
        is_bs = brand == "bluesight" or proto == "modbus"
        if is_bs:
            return {
                "target": "dc_modbus",
                "n": n,
                "device_type": "bluesight",
                "addr": f"{host}:{port or 502}",
                "host": host,
                "port": int(port or 502),
            }
        addr = resource if visa_like else (host or resource)
        return {"target": "dc_chroma", "n": n, "device_type": "chroma", "addr": addr}
    if slot == "scope":
        addr = resource if visa_like else (f"TCPIP0::{host}::INSTR" if host else resource)
        return {"target": "scope", "resource": addr}
    if slot == "wt":
        return {"target": "wt", "host": host, "port": int(port or 5025) if host else None, "resource": resource}
    if slot == "dew":
        return {
            "target": "dew",
            "host": host or resource.split(":")[0],
            "port": int(port or 10001),
        }
    return {"target": "unknown", "resource": resource}


def as_dicts(devices: Sequence[FoundDevice]) -> List[dict]:
    return [asdict(d) for d in devices]
