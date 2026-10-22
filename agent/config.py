# -*- coding: utf-8 -*-
"""Agent 配置加载。"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from agent.mqtt_publish import MqttPublishConfig, mqtt_config_from_dict


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


@dataclass
class AgentConfig:
    iot_base: str
    agent_token: str
    poll_interval_sec: float = 15.0
    heartbeat_interval_sec: float = 15.0
    dry_run: bool = True
    execution_mode: str = ""  # dry_run | handoff | live；空则跟 dry_run
    mutex_path: str = ""
    agent_version: str = "0.1.1"
    mqtt: MqttPublishConfig = field(default_factory=MqttPublishConfig)

    @property
    def mutex_file(self) -> Path:
        if self.mutex_path.strip():
            return Path(self.mutex_path)
        return _repo_root() / ".solar_agent_mutex"

    @property
    def resolved_execution_mode(self) -> str:
        mode = (self.execution_mode or "").strip().lower()
        if mode:
            return mode
        return "dry_run" if self.dry_run else "live"


def default_config_path() -> Path:
    return _repo_root() / "config" / "solar_agent.json"


def load_config(path: Optional[str] = None) -> AgentConfig:
    """
    优先级：显式 path > 环境变量 SOLAR_AGENT_CONFIG > config/solar_agent.json
    令牌可用环境变量 SOLAR_AGENT_TOKEN 覆盖。
    iot_base：环境变量 > 非本地的 solar_agent > iot_bootstrap 正式地址 > 其余。
    """
    cfg_path = path or os.environ.get("SOLAR_AGENT_CONFIG") or ""
    if not cfg_path:
        cfg_path = str(default_config_path())
    p = Path(cfg_path)
    raw: Dict[str, Any] = {}
    if p.is_file():
        raw = json.loads(p.read_text(encoding="utf-8"))
    elif not path and not os.environ.get("SOLAR_AGENT_TOKEN"):
        example = _repo_root() / "config" / "solar_agent.example.json"
        raise FileNotFoundError(
            f"未找到配置 {p}。请复制 {example} 为 solar_agent.json；打开软件会自动上线。"
        )

    token = (os.environ.get("SOLAR_AGENT_TOKEN") or raw.get("agent_token") or "").strip()

    def _local(u: str) -> bool:
        t = (u or "").lower()
        return (not t) or any(x in t for x in ("127.0.0.1", "localhost", "0.0.0.0", "请填写"))

    env_base = (os.environ.get("SOLAR_IOT_BASE") or "").strip().rstrip("/")
    agent_base = str(raw.get("iot_base") or "").strip().rstrip("/")
    boot = {}
    try:
        bp = _repo_root() / "config" / "iot_bootstrap.json"
        if bp.is_file():
            boot = json.loads(bp.read_text(encoding="utf-8"))
    except Exception:
        boot = {}
    boot_base = str(boot.get("iot_base") or "").strip().rstrip("/")

    if env_base and not _local(env_base):
        base = env_base
    elif boot_base and not _local(boot_base):
        base = boot_base
    elif agent_base and not _local(agent_base):
        base = agent_base
    else:
        base = env_base or boot_base or agent_base or "https://www.laidecloud.com/nss"
    base = base.rstrip("/")

    dry = raw.get("dry_run", True)
    if os.environ.get("SOLAR_AGENT_DRY_RUN", "").strip() != "":
        dry = os.environ.get("SOLAR_AGENT_DRY_RUN", "1").strip() not in ("0", "false", "False")

    exec_mode = str(raw.get("execution_mode") or "")
    env_mode = (os.environ.get("SOLAR_AGENT_EXECUTION_MODE") or "").strip()
    if env_mode:
        exec_mode = env_mode

    mqtt_cfg = mqtt_config_from_dict(raw)
    # 环境变量可覆盖 Broker（与温箱共用 EMQX）
    env_host = (os.environ.get("SOLAR_MQTT_HOST") or "").strip()
    if env_host:
        mqtt_cfg.host = env_host
        mqtt_cfg.enable = True
    if os.environ.get("SOLAR_MQTT_PORT", "").strip():
        mqtt_cfg.port = int(os.environ.get("SOLAR_MQTT_PORT") or mqtt_cfg.port)
    if os.environ.get("SOLAR_MQTT_USERNAME", "").strip() != "":
        mqtt_cfg.username = os.environ.get("SOLAR_MQTT_USERNAME") or ""
    if os.environ.get("SOLAR_MQTT_PASSWORD") is not None:
        mqtt_cfg.password = os.environ.get("SOLAR_MQTT_PASSWORD") or ""
    if os.environ.get("SOLAR_MQTT_ENABLE", "").strip() != "":
        mqtt_cfg.enable = os.environ.get("SOLAR_MQTT_ENABLE", "1").strip() not in (
            "0",
            "false",
            "False",
        )

    return AgentConfig(
        iot_base=base,
        agent_token=token,
        poll_interval_sec=float(raw.get("poll_interval_sec") or 15),
        heartbeat_interval_sec=float(raw.get("heartbeat_interval_sec") or 15),
        dry_run=bool(dry),
        execution_mode=str(exec_mode or ""),
        mutex_path=str(raw.get("mutex_path") or ""),
        agent_version=str(raw.get("agent_version") or "0.1.0"),
        mqtt=mqtt_cfg,
    )
