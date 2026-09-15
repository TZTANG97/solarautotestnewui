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


def build_solar_equs(*, pythonid: str, machine_id: str = "", host_name: str = "") -> List[Dict[str, Any]]:
    host = host_name or socket.gethostname()
    mid = (machine_id or "")[:16] or "local"
    return [
        {
            "equ_id": f"SOLAR-BENCH-{mid}",
            "equ_firm": "SolarAutoTest",
            "equ_num": "PV-Bench",
            "equ_seq": mid,
            "equ_name": f"光伏自动化台架-{host}",
            "status": "on",
            "pythonid": pythonid,
        }
    ]


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
                reply = {
                    "type": ret_type,
                    "pythonid": self.pythonid,
                    "clientid": client_id,
                    "equs": build_solar_equs(
                        pythonid=self.pythonid,
                        machine_id=self.machine_id,
                        host_name=self.host_name,
                    ),
                }
                ws.send(json.dumps(reply, ensure_ascii=False))
                logger.info("已应答 %s clientid=%s", ret_type, client_id)

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
