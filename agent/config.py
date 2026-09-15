# -*- coding: utf-8 -*-
"""Agent 配置加载。"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


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
    agent_version: str = "0.1.0"

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


def load_config(path: Optional[str] = None) -> AgentConfig:
    """
    优先级：显式 path > 环境变量 SOLAR_AGENT_CONFIG > config/solar_agent.json
    令牌可用环境变量 SOLAR_AGENT_TOKEN 覆盖。
    """
    cfg_path = path or os.environ.get("SOLAR_AGENT_CONFIG") or ""
    if not cfg_path:
        cfg_path = str(_repo_root() / "config" / "solar_agent.json")
    p = Path(cfg_path)
    raw: Dict[str, Any] = {}
    if p.is_file():
        raw = json.loads(p.read_text(encoding="utf-8"))
    elif not path and not os.environ.get("SOLAR_AGENT_TOKEN"):
        example = _repo_root() / "config" / "solar_agent.example.json"
        raise FileNotFoundError(
            f"未找到配置 {p}。请复制 {example} 为 solar_agent.json 并填写 agent_token。"
        )

    token = (os.environ.get("SOLAR_AGENT_TOKEN") or raw.get("agent_token") or "").strip()
    base = (
        os.environ.get("SOLAR_IOT_BASE")
        or raw.get("iot_base")
        or "http://127.0.0.1:18082/nss"
    ).rstrip("/")
    dry = raw.get("dry_run", True)
    if os.environ.get("SOLAR_AGENT_DRY_RUN", "").strip() != "":
        dry = os.environ.get("SOLAR_AGENT_DRY_RUN", "1").strip() not in ("0", "false", "False")

    return AgentConfig(
        iot_base=base,
        agent_token=token,
        poll_interval_sec=float(raw.get("poll_interval_sec") or 15),
        heartbeat_interval_sec=float(raw.get("heartbeat_interval_sec") or 15),
        dry_run=bool(dry),
        execution_mode=str(raw.get("execution_mode") or ""),
        mutex_path=str(raw.get("mutex_path") or ""),
        agent_version=str(raw.get("agent_version") or "0.1.0"),
    )
