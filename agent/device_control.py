# -*- coding: utf-8 -*-
"""云端 control_instrument → 本机 inbox → 等桌面执行结果。"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def control_timeout_sec(action_payload: Dict[str, Any], *, default: float = 25.0) -> float:
    """discover_lan / WT 连接可能远超普通 connect；与云端超时对齐。"""
    act = str(action_payload.get("action") or "").strip().lower()
    if act == "discover_lan":
        return 180.0
    if act == "connect":
        inst = action_payload.get("instrument") if isinstance(action_payload.get("instrument"), dict) else {}
        slot = str((inst or {}).get("slot") or "").strip().lower()
        kind = str((inst or {}).get("kind") or "").strip().lower()
        # WT VISA 多后端×多资源串试连，单次可能 >25s
        if slot == "wt" or kind == "wt":
            return 90.0
    return float(default)


def run_control_via_desktop(
    action_payload: Dict[str, Any],
    *,
    timeout_sec: Optional[float] = None,
) -> Dict[str, Any]:
    """Agent 侧：写 device_cmds pending，阻塞等待桌面 results。"""
    from utils.iot_device_cmd_inbox import wait_result, write_pending

    request_id = str(
        action_payload.get("requestId") or action_payload.get("request_id") or ""
    ).strip()
    if not request_id:
        return {"ok": False, "message": "缺少 requestId"}

    wait_sec = (
        float(timeout_sec)
        if timeout_sec is not None
        else control_timeout_sec(action_payload)
    )

    root = _repo_root()
    write_pending(
        root,
        request_id,
        {
            "action": action_payload.get("action"),
            "instrument": action_payload.get("instrument") or {},
            "widgets": action_payload.get("widgets") or {},
        },
    )
    logger.info(
        "已写入仪器控制命令 requestId=%s action=%s timeout=%.0fs",
        request_id,
        action_payload.get("action"),
        wait_sec,
    )
    result = wait_result(root, request_id, timeout_sec=wait_sec)
    if not result:
        return {
            "ok": False,
            "message": "等待桌面执行超时：请确认 SolarAutoTest 主界面已打开",
            "requestId": request_id,
        }
    result = dict(result)
    result["requestId"] = request_id
    result["action"] = str(action_payload.get("action") or "")
    return result
