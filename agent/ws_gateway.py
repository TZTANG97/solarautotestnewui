# -*- coding: utf-8 -*-
"""
工控机 WebSocket 在线：发 on → 进入「添加设备」Python 端 ID 列表；
应答 equdata / getequdata，供验证连通。
"""
from __future__ import annotations

import json
import logging
import socket
import threading
import time
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger("solar.agent.ws")

try:
    import websocket  # websocket-client
except ImportError:  # pragma: no cover
    websocket = None  # type: ignore


def iot_base_to_ws_url(iot_base: str) -> str:
    """https://host/nss → wss://host/nss/ ；http → ws。"""
    raw = (iot_base or "").strip().rstrip("/")
    if not raw:
        return ""
    u = urlparse(raw if "://" in raw else f"https://{raw}")
    scheme = "wss" if u.scheme in ("https", "wss") else "ws"
    path = u.path or "/nss"
    if not path.endswith("/"):
        path += "/"
    netloc = u.netloc or u.path
    if u.scheme and u.netloc:
        netloc = u.netloc
        path = u.path or "/nss"
        if not path.endswith("/"):
            path += "/"
    return f"{scheme}://{netloc}{path}"


# 与 IOT app/services/solar_equipment_naming 台架角色对齐（equdata 仅报台架 + 已连接真机）
_SOLAR_BENCH = ("SolarBench", "光伏工控台架", "BENCH")


def _solar_codes_for_role(
    equ_num: str, role_tag: str, machine_id: str, host_name: str = ""
) -> tuple[str, str, str]:
    """型号 / 序列号 SAT-{ROLE}-主机-短码 / 设备ID {型号}Style…"""
    import re

    hx = re.sub(r"[^0-9a-fA-F]", "", (machine_id or "").lower())
    short8 = (hx[:8] or "LOCAL000").upper()
    short12 = (hx[:12] or (short8 + "0000")[:12]).upper()
    host = re.sub(r"[^A-Za-z0-9_-]+", "-", (host_name or "PC").strip()).strip("-_")[:24] or "PC"
    equ_seq = f"SAT-{role_tag}-{host}-{short8}"[:64]
    equ_id = f"{equ_num}Style{short12}"[:255]
    return equ_num, equ_seq, equ_id


def _stable_inst_equ_id(pythonid: str, resource: str) -> str:
    import hashlib

    digest = hashlib.sha1(f"{pythonid}|{resource}".encode("utf-8")).hexdigest()[:16].upper()
    return f"SolarInst{digest}"


def build_solar_equs(
    *,
    pythonid: str,
    machine_id: str = "",
    host_name: str = "",
    instruments: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    equdata_return.equs：
    - 始终含工控台架 SolarBench
    - 另附软件已连接的真仪器（品牌/型号/地址），不再虚构未连接的 SolarAC/DC 卡
    """
    host = host_name or socket.gethostname()
    mid = machine_id or ""
    pid = (pythonid or "").strip()
    out: List[Dict[str, Any]] = []

    equ_num, label, role_tag = _SOLAR_BENCH
    _n, equ_seq, equ_id = _solar_codes_for_role(equ_num, role_tag, mid, host)
    out.append(
        {
            "equ_id": equ_id,
            "equ_firm": "SolarAutoTest",
            "equ_num": equ_num,
            "equ_seq": equ_seq,
            "equ_name": f"{label}-{host}",
            "equ_type": "1",
            "status": "on",
            "pythonid": pid,
        }
    )

    kind_fallback = {
        "ac": "AC源",
        "dc": "DC源",
        "wt": "功率分析仪",
        "scope": "示波器",
        "dew": "德威创",
    }
    for item in instruments or []:
        if not isinstance(item, dict):
            continue
        if not item.get("connected"):
            continue
        resource = str(item.get("resource") or "").strip()
        if not resource or resource.lower().startswith("pending:"):
            continue
        brand = str(item.get("brand") or "").strip() or "未知厂商"
        model = str(item.get("model") or "").strip()
        kind = str(item.get("kind") or "unknown").strip().lower()
        if not model:
            model = kind_fallback.get(kind, kind.upper() or "Instrument")
        serial = str(item.get("serial") or "").strip() or resource[:64]
        name = f"{brand} {model}".strip()
        out.append(
            {
                "equ_id": _stable_inst_equ_id(pid, resource),
                "equ_firm": brand,
                "equ_num": model[:255],
                "equ_seq": serial[:255],
                "equ_name": name[:255],
                "equ_type": "1",
                "status": "on" if item.get("online", True) else "off",
                "pythonid": pid,
                "resource": resource,
                "slot": str(item.get("slot") or "").strip().lower(),
                "kind": kind,
            }
        )
    return out


class SolarWsPresence:
    """后台线程维持 WS；进程内单例。"""

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._ws = None
        self.iot_base = ""
        self.pythonid = ""
        self.machine_id = ""
        self.host_name = ""
        self._on_token: Optional[Callable[[], None]] = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(
        self,
        *,
        iot_base: str,
        pythonid: str,
        machine_id: str = "",
        host_name: str = "",
    ) -> bool:
        if websocket is None:
            logger.error("未安装 websocket-client，无法上线到「添加设备」")
            return False
        pid = (pythonid or "").strip()
        if not pid or not iot_base:
            return False
        if self.running and self.pythonid == pid and self.iot_base == iot_base:
            return True
        self.stop()
        self.iot_base = iot_base.rstrip("/")
        self.pythonid = pid
        self.machine_id = machine_id or ""
        self.host_name = host_name or socket.gethostname()
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="solar-ws-presence", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop.set()
        try:
            if self._ws is not None:
                self._ws.close()
        except Exception:
            pass
        self._ws = None
        t = self._thread
        if t and t.is_alive():
            t.join(timeout=3.0)
        self._thread = None

    def _run(self) -> None:
        url = iot_base_to_ws_url(self.iot_base)
        if not url:
            logger.error("无法从 iot_base 推导 WebSocket 地址: %s", self.iot_base)
            return
        logger.info("WS 上线 pythonid=%s url=%s", self.pythonid, url)
        while not self._stop.is_set():
            try:
                self._connect_once(url)
            except Exception as exc:
                logger.warning("WS 连接异常: %s", exc)
            if self._stop.wait(5.0):
                break

    def _connect_once(self, url: str) -> None:
        assert websocket is not None

        def on_open(ws) -> None:
            payload = {"type": "on", "pythonid": self.pythonid}
            ws.send(json.dumps(payload, ensure_ascii=False))
            logger.info("已发送 on pythonid=%s", self.pythonid)

        def on_message(ws, message) -> None:
            if isinstance(message, bytes):
                message = message.decode("utf-8", errors="replace")
            text = (message or "").strip()
            if text == "ping":
                return
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                return
            if not isinstance(data, dict):
                return
            msg_type = str(data.get("type") or "").strip().lower()
            client_id = str(data.get("clientid") or "").strip()
            if msg_type == "response":
                return
            if msg_type in ("equdata", "getequdata") and client_id:
                ret_type = "equdata_return" if msg_type == "equdata" else "getequdata_return"
                instruments: List[Dict[str, Any]] = []
                try:
                    from agent.instruments_snapshot import collect_instruments_snapshot

                    instruments = collect_instruments_snapshot(force=True, min_interval_sec=0)
                except Exception as exc:
                    logger.debug("equdata 采集仪器失败: %s", exc)
                reply = {
                    "type": ret_type,
                    "pythonid": self.pythonid,
                    "clientid": client_id,
                    "equs": build_solar_equs(
                        pythonid=self.pythonid,
                        machine_id=self.machine_id,
                        host_name=self.host_name,
                        instruments=instruments,
                    ),
                }
                ws.send(json.dumps(reply, ensure_ascii=False))
                logger.info(
                    "已应答 %s clientid=%s equs=%s",
                    ret_type,
                    client_id,
                    len(reply["equs"]),
                )

        def on_error(_ws, err) -> None:
            logger.debug("WS error: %s", err)

        def on_close(_ws, status, msg) -> None:
            logger.info("WS 关闭 status=%s msg=%s", status, msg)

        self._ws = websocket.WebSocketApp(
            url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        # ping 由本机定时发纯文本（与 test_device_client 一致）
        def ping_loop() -> None:
            while not self._stop.is_set() and self._ws is not None:
                time.sleep(15)
                try:
                    if self._ws and self._ws.sock and self._ws.sock.connected:
                        self._ws.send("ping")
                except Exception:
                    break

        threading.Thread(target=ping_loop, name="solar-ws-ping", daemon=True).start()
        self._ws.run_forever(ping_interval=0, ping_timeout=None)


_presence = SolarWsPresence()


def start_presence(*, iot_base: str, pythonid: str, machine_id: str = "", host_name: str = "") -> bool:
    return _presence.start(
        iot_base=iot_base, pythonid=pythonid, machine_id=machine_id, host_name=host_name
    )


def stop_presence() -> None:
    _presence.stop()


def presence_running() -> bool:
    return _presence.running
