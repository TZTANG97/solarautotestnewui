# -*- coding: utf-8 -*-
"""光伏 Agent → MQTT 上行（对齐温箱 /EquMessage 路径）。

进度/状态出站发布；Broker 由 IOT 订阅落库。无 Broker 配置时静默跳过。
"""
from __future__ import annotations

import json
import logging
import ssl
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger("solar.agent.mqtt")


@dataclass
class MqttPublishConfig:
    enable: bool = False
    host: str = ""
    port: int = 1883
    username: str = ""
    password: str = ""
    topic_prefix: str = "/EquMessage"
    qos: int = 1
    use_ssl: bool = False
    client_id: str = "solar_agent_pub"


def mqtt_config_from_dict(raw: Optional[Dict[str, Any]]) -> MqttPublishConfig:
    """从 solar_agent.json 的 mqtt 段或扁平字段解析。"""
    data = raw if isinstance(raw, dict) else {}
    nested = data.get("mqtt") if isinstance(data.get("mqtt"), dict) else {}
    src = {**data, **nested}

    def _b(key: str, default: bool = False) -> bool:
        if key in nested:
            return bool(nested.get(key))
        if key in data and key.startswith("mqtt"):
            return bool(data.get(key))
        return bool(nested.get(key, default)) if nested else default

    enable = nested.get("enable")
    if enable is None:
        enable = data.get("mqtt_enable")
    host = str(nested.get("host") or data.get("mqtt_host") or "").strip()
    port = int(nested.get("port") or data.get("mqtt_port") or 1883)
    if enable is None:
        enable = bool(host)
    return MqttPublishConfig(
        enable=bool(enable) and bool(host),
        host=host,
        port=port,
        username=str(nested.get("username") or data.get("mqtt_username") or "").strip(),
        password=str(nested.get("password") or data.get("mqtt_password") or ""),
        topic_prefix=str(
            nested.get("topic_prefix") or data.get("mqtt_topic_prefix") or "/EquMessage"
        ).strip()
        or "/EquMessage",
        qos=int(nested.get("qos") or data.get("mqtt_qos") or 1),
        use_ssl=bool(nested.get("use_ssl") or data.get("mqtt_use_ssl") or False),
        client_id=str(nested.get("client_id") or data.get("mqtt_client_id") or "solar_agent_pub"),
    )


def resolve_publish_topic(prefix: str, pythonid: str) -> str:
    base = (prefix or "/EquMessage").rstrip("/")
    pid = (pythonid or "").strip()
    return f"{base}/{pid}" if pid else base


def build_experdata_payload(
    *,
    pythonid: str,
    job_id: int,
    progress_percent: int,
    progress_text: str = "",
    current_step: str = "",
    exper_id: str = "",
    measures: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """协议字段名对齐数据通信原则；type 用 Solar 前缀，避免与温箱 TH/TS 串道。"""
    pct = max(0, min(100, int(progress_percent)))
    equ: Dict[str, Any] = {
        "equ_id": f"SOLAR-JOB-{job_id}",
        "progress_percent": pct,
        "progress_text": str(progress_text or "")[:255],
        "current_step": str(current_step or "")[:64],
        "experId": str(exper_id or ""),
        "channel": "solar",
    }
    if isinstance(measures, dict) and measures:
        equ["measures"] = dict(measures)
    payload: Dict[str, Any] = {
        "type": "SolarEquipment_experdata_return",
        "pythonid": (pythonid or "").strip(),
        "experid": str(job_id),
        "time": "1",
        "equs": [equ],
    }
    if isinstance(measures, dict) and measures:
        payload["measures"] = dict(measures)
    return payload


def build_exper_auto_end_payload(
    *,
    pythonid: str,
    job_id: int,
    status: str,
    fail_reason: str = "",
    result_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "type": "SolarEquipment_experautoend_return",
        "pythonid": (pythonid or "").strip(),
        "experid": str(job_id),
        "status": str(status or "FAIL"),
        "fail_reason": str(fail_reason or "")[:512],
        "result_summary": result_summary if isinstance(result_summary, dict) else {},
        "channel": "solar",
    }


def publish_json(cfg: MqttPublishConfig, *, pythonid: str, payload: Dict[str, Any]) -> bool:
    if not cfg.enable or not cfg.host:
        return False
    try:
        import paho.mqtt.publish as mqtt_publish
    except ImportError:
        logger.warning("未安装 paho-mqtt，跳过 MQTT 进度上报")
        return False

    topic = resolve_publish_topic(cfg.topic_prefix, pythonid)
    body = json.dumps(payload, ensure_ascii=False)
    auth = None
    if cfg.username:
        auth = {"username": cfg.username, "password": cfg.password or None}
    tls = None
    if cfg.use_ssl:
        tls = ssl.create_default_context()
        tls.check_hostname = False
        tls.verify_mode = ssl.CERT_NONE
    try:
        mqtt_publish.single(
            topic,
            payload=body,
            qos=int(cfg.qos or 1),
            hostname=cfg.host,
            port=int(cfg.port or 1883),
            client_id=f"{cfg.client_id}-{(pythonid or 'x')[:16]}",
            auth=auth,
            tls=tls,
        )
        logger.debug(
            "MQTT 已发 type=%s topic=%s pythonid=%s",
            payload.get("type"),
            topic,
            pythonid,
        )
        return True
    except Exception as exc:
        logger.warning("MQTT 发布失败 topic=%s: %s", topic, exc)
        return False


_cfg: Optional[MqttPublishConfig] = None


def configure(cfg: MqttPublishConfig) -> None:
    global _cfg
    _cfg = cfg
    if cfg.enable:
        logger.info(
            "MQTT 上行已启用 broker=%s:%s prefix=%s",
            cfg.host,
            cfg.port,
            cfg.topic_prefix,
        )


def get_config() -> MqttPublishConfig:
    return _cfg or MqttPublishConfig()


def publish_experdata(
    *,
    pythonid: str,
    job_id: int,
    progress_percent: int,
    progress_text: str = "",
    current_step: str = "",
    exper_id: str = "",
    measures: Optional[Dict[str, Any]] = None,
) -> bool:
    cfg = get_config()
    payload = build_experdata_payload(
        pythonid=pythonid,
        job_id=job_id,
        progress_percent=progress_percent,
        progress_text=progress_text,
        current_step=current_step,
        exper_id=exper_id,
        measures=measures,
    )
    return publish_json(cfg, pythonid=pythonid, payload=payload)


def publish_exper_auto_end(
    *,
    pythonid: str,
    job_id: int,
    status: str,
    fail_reason: str = "",
    result_summary: Optional[Dict[str, Any]] = None,
) -> bool:
    cfg = get_config()
    payload = build_exper_auto_end_payload(
        pythonid=pythonid,
        job_id=job_id,
        status=status,
        fail_reason=fail_reason,
        result_summary=result_summary,
    )
    return publish_json(cfg, pythonid=pythonid, payload=payload)
