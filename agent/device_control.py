# -*- coding: utf-8 -*-
"""云端 control_instrument → 本机 inbox → 等桌面执行结果。"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run_control_via_desktop(
    action_payload: Dict[str, Any],
    *,
    timeout_sec: float = 25.0,
) -> Dict[str, Any]:
    """Agent 侧：写 device_cmds pending，阻塞等待桌面 results。"""
    from utils.iot_device_cmd_inbox import wait_result, write_pending

    request_id = str(
        action_payload.get("requestId") or action_payload.get("request_id") or ""
    ).strip()
    if not request_id:
        return {"ok": False, "message": "缺少 requestId"}

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
        "已写入仪器控制命令 requestId=%s action=%s",
        request_id,
        action_payload.get("action"),
    )
    result = wait_result(root, request_id, timeout_sec=timeout_sec)
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
