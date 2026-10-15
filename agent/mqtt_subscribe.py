# -*- coding: utf-8 -*-
"""订阅 IOT 经 MQTT 下发的命令（/EquCommand/{pythonid}），对齐温箱。

WS 离线时 startexper 仍可到达 Agent。
"""
from __future__ import annotations

import json
import logging
import threading
from typing import Any, Callable, Dict, List, Optional

from agent.mqtt_publish import MqttPublishConfig, get_config, resolve_publish_topic

logger = logging.getLogger("solar.agent.mqtt.sub")

JobHandler = Callable[[Dict[str, Any]], None]

_lock = threading.Lock()
_pending: List[Dict[str, Any]] = []
_handler: Optional[JobHandler] = None
_thread: Optional[threading.Thread] = None
_stop = threading.Event()
_client = None
_pythonid = ""


def set_job_handler(handler: Optional[JobHandler]) -> None:
    global _handler
    _handler = handler


def pop_pending_job() -> Optional[Dict[str, Any]]:
    with _lock:
        if not _pending:
            return None
        return _pending.pop(0)


def _enqueue_job(job: Dict[str, Any]) -> None:
    if _handler:
        try:
            _handler(job)
            return
        except Exception as exc:
            logger.warning("MQTT startexper handler 失败: %s", exc)
    with _lock:
        jid = int(job.get("id") or 0)
        global _pending
        if jid:
            _pending = [x for x in _pending if int(x.get("id") or 0) != jid]
        _pending.append(job)


def _on_message(_client, _userdata, msg) -> None:
    try:
        text = msg.payload.decode("utf-8") if isinstance(msg.payload, (bytes, bytearray)) else str(msg.payload)
        data = json.loads(text)
    except Exception as exc:
        logger.warning("MQTT 命令解析失败: %s", exc)
        return
    if not isinstance(data, dict):
        return
    msg_type = str(data.get("type") or "").strip().lower()
    if msg_type not in ("startexper", "solar_startexper"):
        return
    from agent.job_normalize import normalize_startexper_job

    job = normalize_startexper_job(data)
    jid = int(job.get("id") or 0)
    if not jid:
        logger.warning(
            "MQTT startexper 缺少 solar_jobs.id experid=%s topic=%s，忽略",
            job.get("experid"),
            getattr(msg, "topic", ""),
        )
        return
    from agent.job_dedupe import remember_job

    if not remember_job(jid):
        logger.info("MQTT startexper 重复 id=%s，跳过", jid)
        return
    logger.info(
        "MQTT 收到 startexper id=%s experid=%s topic=%s",
        job.get("id"),
        job.get("experid"),
        getattr(msg, "topic", ""),
    )
    _enqueue_job(job)


def start_subscriber(*, pythonid: str, cfg: Optional[MqttPublishConfig] = None) -> bool:
    """后台线程订阅 /EquCommand/{pythonid}。"""
    global _thread, _client, _pythonid
    conf = cfg or get_config()
    pid = (pythonid or "").strip()
    if not conf.enable or not conf.host or not pid:
        return False
    if _thread and _thread.is_alive() and _pythonid == pid:
        return True
    stop_subscriber()
    _pythonid = pid
    _stop.clear()

    cmd_topic = f"/EquCommand/{pid}"
    # 兼容：也听上行同前缀（部分环境复用 EquMessage 下发）
    msg_topic = resolve_publish_topic(conf.topic_prefix, pid)

    def _run() -> None:
        global _client
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            logger.warning("未安装 paho-mqtt，无法订阅命令")
            return
        client_id = f"{conf.client_id}-sub-{pid[-12:]}"
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
        if conf.username:
            client.username_pw_set(conf.username, conf.password or None)
        if conf.use_ssl:
            import ssl

            client.tls_set(cert_reqs=ssl.CERT_NONE)
            client.tls_insecure_set(True)
        client.on_message = _on_message

        def _on_connect(c, _u, _f, rc, *_a):
            if rc != 0:
                logger.warning("MQTT 订阅连接失败 rc=%s", rc)
                return
            for t in (cmd_topic, msg_topic):
                c.subscribe(t, qos=int(conf.qos or 1))
            logger.info("MQTT 已订阅命令 topic=%s,%s", cmd_topic, msg_topic)

        client.on_connect = _on_connect
        try:
            client.connect(conf.host, int(conf.port or 1883), keepalive=60)
            _client = client
            client.loop_start()
            while not _stop.wait(1.0):
                pass
        except Exception as exc:
            logger.warning("MQTT 订阅异常: %s", exc)
        finally:
            try:
                client.loop_stop()
                client.disconnect()
            except Exception:
                pass
            _client = None

    _thread = threading.Thread(target=_run, name="solar-mqtt-sub", daemon=True)
    _thread.start()
    return True


def stop_subscriber() -> None:
    global _thread
    _stop.set()
    t = _thread
    if t and t.is_alive():
        t.join(timeout=3.0)
    _thread = None


def subscriber_running() -> bool:
    return bool(_thread and _thread.is_alive())
