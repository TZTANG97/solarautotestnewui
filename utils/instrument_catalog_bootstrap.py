# -*- coding: utf-8 -*-
"""
在「发令进程」拉 IOT 设备命令库并写入各 *_catalog_sync 覆盖表。

Agent 子进程与 SCPITestWave 桌面进程都可能发 SCPI；两边都要调一次。
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _load_agent_cfg(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[1]
    cfg_path = root / "config" / "solar_agent.json"
    if not cfg_path.is_file():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        logger.debug("读取 solar_agent.json 失败", exc_info=True)
        return {}


def build_client_from_cfg(cfg: Optional[Dict[str, Any]] = None, *, repo_root: Optional[Path] = None):
    data = dict(cfg or _load_agent_cfg(repo_root))
    base = str(data.get("iot_base") or data.get("iotBase") or "").strip().rstrip("/")
    token = str(data.get("agent_token") or data.get("agentToken") or "").strip()
    if not base or not token:
        return None
    pythonid = str(data.get("pythonid") or data.get("pythonId") or "").strip() or None
    try:
        from agent.client import IotSolarClient

        return IotSolarClient(base, token, pythonid=pythonid)
    except Exception:
        logger.debug("构建 IotSolarClient 失败", exc_info=True)
        return None


def apply_all_instrument_catalogs(client: Any) -> Dict[str, Any]:
    """用已有 client 拉四类目录；返回摘要。"""
    summary: Dict[str, Any] = {}
    try:
        from utils.wt_measure_catalog_sync import apply_wt_measure_catalog_from_client

        summary["wt"] = apply_wt_measure_catalog_from_client(client)
    except Exception:
        logger.debug("WT 命令库同步失败", exc_info=True)
        summary["wt"] = {}
    try:
        from utils.ac_source_catalog_sync import apply_ac_source_catalog_from_client

        ac_n = 0
        for fam in ("61800", "AC_GENERIC"):
            ac_n += apply_ac_source_catalog_from_client(client, family=fam)
        summary["ac"] = ac_n
    except Exception:
        logger.debug("AC 命令库同步失败", exc_info=True)
        summary["ac"] = 0
    try:
        from utils.dc_source_catalog_sync import (
            DC_CATALOG_BRANDS,
            apply_dc_source_catalog_from_client,
        )

        dc_loaded = {}
        for firm in DC_CATALOG_BRANDS:
            n = apply_dc_source_catalog_from_client(client, firm)
            if n:
                dc_loaded[firm] = n
        summary["dc"] = dc_loaded
    except Exception:
        logger.debug("DC 命令库同步失败", exc_info=True)
        summary["dc"] = {}
    try:
        from utils.dew_catalog_sync import apply_dew_catalog_from_client

        summary["dew"] = apply_dew_catalog_from_client(client)
    except Exception:
        logger.debug("DEW 命令库同步失败", exc_info=True)
        summary["dew"] = 0
    return summary


def refresh_command_list_dc() -> Dict[str, list]:
    """现读 get_dc_mode_preamble，供 SCPITestWave 全局刷新。"""
    from utils.dc_source_catalog_sync import get_dc_mode_preamble

    return {
        "Chroma": get_dc_mode_preamble("Chroma"),
        "Keysight": get_dc_mode_preamble("Keysight"),
        "Itech": get_dc_mode_preamble("Itech"),
        "Bluesight": get_dc_mode_preamble("Bluesight"),
    }


def bootstrap_instrument_catalogs(
    client: Any = None, *, repo_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    拉库写入覆盖表；若能拿到 SCPITestWave.command_list_DC 则同步刷新。
    client 为空时从 solar_agent.json 建。
    """
    c = client or build_client_from_cfg(repo_root=repo_root)
    if c is None:
        logger.info("无 Agent 配置，跳过设备命令库拉库")
        return {}
    summary = apply_all_instrument_catalogs(c)
    try:
        refreshed = refresh_command_list_dc()
        import SCPITestWave as sw

        if hasattr(sw, "command_list_DC"):
            sw.command_list_DC = refreshed
            summary["command_list_DC"] = "refreshed"
    except Exception:
        logger.debug("刷新 SCPITestWave.command_list_DC 跳过", exc_info=True)
    logger.info("设备命令库 bootstrap %s", summary)
    return summary
