# -*- coding: utf-8 -*-
"""
工控机 WebSocket：上线 + 仪器控制/试连 + 试验 startexper 实时通道。

对齐箱子：IOT → send_to_python → 本机立刻执行 → 回包推前端。
桌面 Qt 仍走 inbox；本模块只写 pending / 等结果 / 上行 JSON。
"""
from __future__ import annotations

import json
import logging
import socket
import threading
import time
import uuid
from pathlib import Path
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


_SOLAR_BENCH = ("SolarBench", "光伏工控台架", "BENCH")

# 下行业务类型
TYPE_CONTROL = "control_instrument"
TYPE_PROBE = "probe_instruments"
TYPE_START = "startexper"
# 上行
TYPE_CONTROL_RETURN = "control_instrument_return"
TYPE_PROBE_RETURN = "probe_instruments_return"
TYPE_INSTRUMENT_STATUS = "instrument_status"
TYPE_START_RETURN = "startexper_return"


def _solar_codes_for_role(
    equ_num: str, role_tag: str, machine_id: str, host_name: str = ""
) -> tuple[str, str, str]:
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


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _status_json_path() -> str:
    return str(_repo_root() / "status.json")


def _collect_status_payload() -> Dict[str, Any]:
    instruments: List[Dict[str, Any]] = []
    local_resources: List[Dict[str, Any]] = []
    try:
        from agent.instruments_snapshot import collect_instruments_snapshot

        instruments = collect_instruments_snapshot(
            status_json_path=_status_json_path(), force=True, min_interval_sec=0
        )
    except Exception as exc:
        logger.debug("采集仪器快照失败: %s", exc)
    try:
        from agent.local_endpoints import collect_local_endpoints

        local_resources = collect_local_endpoints(force=True)
    except Exception as exc:
        logger.debug("采集串口失败: %s", exc)
    return {"instruments": instruments, "localResources": local_resources}


class SolarWsPresence:
    """后台线程维持 WS；进程内单例。支持业务下行与主动上行。"""

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._ws = None
        self._send_lock = threading.Lock()
        self.iot_base = ""
        self.pythonid = ""
        self.machine_id = ""
        self.host_name = ""
        self._on_token: Optional[Callable[[], None]] = None
        self._job_handler: Optional[Callable[[Dict[str, Any]], None]] = None
        self._pending_jobs: List[Dict[str, Any]] = []
        self._jobs_lock = threading.Lock()

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def set_job_handler(self, handler: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        self._job_handler = handler

    def pop_pending_job(self) -> Optional[Dict[str, Any]]:
        with self._jobs_lock:
            if not self._pending_jobs:
                return None
            return self._pending_jobs.pop(0)

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

    def send_json(self, payload: Dict[str, Any]) -> bool:
        """上行任意 JSON（进度/结案/仪器状态）。"""
        body = dict(payload or {})
        body.setdefault("pythonid", self.pythonid)
        text = json.dumps(body, ensure_ascii=False)
        with self._send_lock:
            ws = self._ws
            if ws is None:
                return False
            try:
                if ws.sock and ws.sock.connected:
                    ws.send(text)
                    return True
            except Exception as exc:
                logger.debug("WS 上行失败: %s", exc)
        return False

    def push_instrument_status(self, *, clientid: str = "", extra: Optional[Dict[str, Any]] = None) -> bool:
        snap = _collect_status_payload()
        payload: Dict[str, Any] = {
            "type": TYPE_INSTRUMENT_STATUS,
            "pythonid": self.pythonid,
            "clientid": clientid or "",
            "instruments": snap["instruments"],
            "localResources": snap["localResources"],
        }
        if extra:
            payload.update(extra)
        return self.send_json(payload)

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
            # 连上立刻推一帧真实会话，清掉网页假「已连接」
            threading.Thread(
                target=lambda: (time.sleep(0.3), self.push_instrument_status()),
                name="solar-ws-boot-status",
                daemon=True,
            ).start()

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
                self._reply_equdata(ws, msg_type, client_id)
                return
            if msg_type == TYPE_CONTROL:
                threading.Thread(
                    target=self._handle_control,
                    args=(data,),
                    name="solar-ws-ctrl",
                    daemon=True,
                ).start()
                return
            if msg_type == TYPE_PROBE:
                threading.Thread(
                    target=self._handle_probe,
                    args=(data,),
                    name="solar-ws-probe",
                    daemon=True,
                ).start()
                return
            if msg_type == TYPE_START:
                self._handle_startexper(data)
                return

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

    def _reply_equdata(self, ws, msg_type: str, client_id: str) -> None:
        ret_type = "equdata_return" if msg_type == "equdata" else "getequdata_return"
        snap = _collect_status_payload()
        reply = {
            "type": ret_type,
            "pythonid": self.pythonid,
            "clientid": client_id,
            "equs": build_solar_equs(
                pythonid=self.pythonid,
                machine_id=self.machine_id,
                host_name=self.host_name,
                instruments=snap["instruments"],
            ),
            "instruments": snap["instruments"],
            "localResources": snap["localResources"],
        }
        try:
            ws.send(json.dumps(reply, ensure_ascii=False))
            logger.info("已应答 %s clientid=%s equs=%s", ret_type, client_id, len(reply["equs"]))
        except Exception as exc:
            logger.warning("应答 equdata 失败: %s", exc)

    def _handle_control(self, data: Dict[str, Any]) -> None:
        client_id = str(data.get("clientid") or "").strip()
        request_id = str(data.get("requestId") or data.get("request_id") or "").strip()
        if not request_id:
            request_id = uuid.uuid4().hex[:16]
        try:
            from agent.device_control import run_control_via_desktop

            result = run_control_via_desktop(data, timeout_sec=25.0)
        except Exception as exc:
            logger.warning("WS 仪器控制失败: %s", exc)
            result = {"ok": False, "message": str(exc)[:500], "requestId": request_id}
        snap = _collect_status_payload()
        reply = {
            "type": TYPE_CONTROL_RETURN,
            "pythonid": self.pythonid,
            "clientid": client_id,
            "requestId": request_id,
            "action": str(data.get("action") or result.get("action") or ""),
            "ok": bool(result.get("ok")),
            "message": str(result.get("message") or "")[:500],
            "detail": result.get("detail") if isinstance(result.get("detail"), dict) else result,
            "instrument": data.get("instrument") if isinstance(data.get("instrument"), dict) else {},
            "instruments": snap["instruments"],
            "localResources": snap["localResources"],
        }
        self.send_json(reply)

    def _handle_probe(self, data: Dict[str, Any]) -> None:
        client_id = str(data.get("clientid") or "").strip()
        request_id = str(data.get("requestId") or data.get("request_id") or "").strip()
        instruments = data.get("instruments") or []
        try:
            from agent.instrument_probe import probe_instruments

            results = probe_instruments(instruments if isinstance(instruments, list) else [])
        except Exception as exc:
            results = [
                {
                    "resource": str((x or {}).get("resource") or ""),
                    "connected": False,
                    "error": str(exc)[:255],
                }
                for x in (instruments or [])
                if isinstance(x, dict)
            ]
        self.send_json(
            {
                "type": TYPE_PROBE_RETURN,
                "pythonid": self.pythonid,
                "clientid": client_id,
                "requestId": request_id,
                "results": results,
            }
        )

    def _handle_startexper(self, data: Dict[str, Any]) -> None:
        client_id = str(data.get("clientid") or "").strip()
        job = dict(data)
        # 保证有 id（solar_jobs 主键）
        if "id" not in job:
            try:
                job["id"] = int(job.get("experid") or 0)
            except (TypeError, ValueError):
                job["id"] = 0
        logger.info(
            "WS 收到 startexper id=%s experid=%s type=%s",
            job.get("id"),
            job.get("experid"),
            job.get("testType"),
        )
        self.send_json(
            {
                "type": TYPE_START_RETURN,
                "pythonid": self.pythonid,
                "clientid": client_id,
                "experid": str(job.get("experid") or ""),
                "id": job.get("id"),
                "status": "OK",
                "message": "已接收开测",
            }
        )
        if self._job_handler:
            try:
                self._job_handler(job)
                return
            except Exception as exc:
                logger.warning("startexper handler 失败: %s", exc)
        with self._jobs_lock:
            self._pending_jobs.append(job)


_presence = SolarWsPresence()


def start_presence(*, iot_base: str, pythonid: str, machine_id: str = "", host_name: str = "") -> bool:
    return _presence.start(
        iot_base=iot_base, pythonid=pythonid, machine_id=machine_id, host_name=host_name
    )


def stop_presence() -> None:
    _presence.stop()


def presence_running() -> bool:
    return _presence.running


def send_json(payload: Dict[str, Any]) -> bool:
    return _presence.send_json(payload)


def push_instrument_status(*, clientid: str = "", extra: Optional[Dict[str, Any]] = None) -> bool:
    return _presence.push_instrument_status(clientid=clientid, extra=extra)


def set_job_handler(handler: Optional[Callable[[Dict[str, Any]], None]]) -> None:
    _presence.set_job_handler(handler)


def pop_pending_job() -> Optional[Dict[str, Any]]:
    return _presence.pop_pending_job()
