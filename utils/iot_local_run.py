# -*- coding: utf-8 -*-
"""台架本地开测 → IOT 登记实验/任务。

Web 开测走 handoff（云端已建实验）；本地点「开始」原先不登记，
导致 IOT 实验管理无记录。本模块在 RunProjectPush / 结束时补登记。
云端 handoff 等待中（_awaiting）则跳过，避免重复建局。
"""
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_state: Dict[str, Any] = {"job_id": None, "exper_id": None}


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def handoff_has_awaiting_job() -> bool:
    """云端 handoff 正在处理或已占用当前试验局时返回 True。

    start_test() 调用时 _awaiting 尚未写入，但 _job_ctx 已在；
    两者任一存在都说明本局由云端任务登记，本地勿再创建实验。
    """
    try:
        import SCPITestWave as sw

        svc = getattr(sw, "_iot_ui_handoff_svc", None)
        if svc is None:
            return False
        if getattr(svc, "_job_ctx", None):
            return True
        aw = getattr(svc, "_awaiting", None)
        if not aw:
            return False
        try:
            return int(aw.get("job_id") or 0) > 0
        except (TypeError, ValueError):
            return True
    except Exception:
        return False


def current_local_job_id() -> Optional[int]:
    with _lock:
        jid = _state.get("job_id")
    try:
        return int(jid) if jid else None
    except (TypeError, ValueError):
        return None


def _build_client():
    from agent.client import IotSolarClient
    from agent.config import load_config

    cfg = load_config()
    if not cfg.agent_token or str(cfg.agent_token).startswith("请填写"):
        raise RuntimeError("无有效 agent_token，无法向 IOT 登记本地试验")
    pythonid = ""
    try:
        raw_path = _repo_root() / "config" / "solar_agent.json"
        if raw_path.is_file():
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            pythonid = str(raw.get("pythonid") or raw.get("pythonId") or "").strip()
    except Exception:
        pythonid = ""
    return IotSolarClient(cfg.iot_base, cfg.agent_token, pythonid=pythonid)


def _ui_log(msg: str) -> None:
    """后台线程只打日志，避免跨线程碰 Qt 控件。"""
    logger.info(msg)
    print(msg, flush=True)


def _do_start(test_name: str) -> None:
    try:
        client = _build_client()
        data = client.local_run_start(test_type=test_name, title=test_name)
        job_id = int(data.get("jobId") or data.get("id") or 0)
        exper_id = int(data.get("experimentId") or data.get("experid") or 0)
        if job_id <= 0:
            raise RuntimeError(f"IOT 未返回 jobId: {data!r}")
        with _lock:
            _state["job_id"] = job_id
            _state["exper_id"] = exper_id or None
        msg = (
            f"[IOT] 本地开测已登记实验 #{exper_id} / 任务 #{job_id}"
            if exper_id
            else f"[IOT] 本地开测已登记任务 #{job_id}"
        )
        logger.info(msg)
        _ui_log(msg)
    except Exception as exc:
        logger.info("本地开测 IOT 登记失败（试验仍继续）: %s", exc, exc_info=True)
        _ui_log(f"[IOT] 本地开测登记失败（试验仍继续）: {exc}")


def _do_done(job_id: int, aborted: bool) -> None:
    try:
        client = _build_client()
        status = "aborted" if aborted else "success"
        reason = "台架本地中止" if aborted else ""
        client.done(job_id, status=status, fail_reason=reason)
        logger.info("[IOT] 本地任务 #%s 已结案 status=%s", job_id, status)
        _ui_log(f"[IOT] 本地任务 #{job_id} 已结案（{status}）")
    except Exception as exc:
        logger.info("本地结案上报失败: %s", exc, exc_info=True)
        _ui_log(f"[IOT] 本地结案上报失败: {exc}")
    finally:
        with _lock:
            if _state.get("job_id") == job_id:
                _state["job_id"] = None
                _state["exper_id"] = None


def notify_local_run_started(test_name: str) -> None:
    """UI 线程调用：后台登记；handoff 占用时跳过。"""
    if handoff_has_awaiting_job():
        logger.info("[iot_local_run] handoff 任务进行中，跳过本地登记")
        return
    with _lock:
        if _state.get("job_id"):
            # 上一局未结案又开新测：仍报新 start，服务端会中止上一局 local_ui
            pass
    name = (test_name or "").strip() or "本地试验"
    threading.Thread(
        target=_do_start,
        args=(name,),
        daemon=True,
        name="iot-local-run-start",
    ).start()


def notify_local_run_finished(*, aborted: bool = False) -> None:
    """试验正常结束或中止时结案；无登记则静默。"""
    with _lock:
        jid = _state.get("job_id")
    if not jid:
        return
    try:
        job_id = int(jid)
    except (TypeError, ValueError):
        return
    if job_id <= 0:
        return
    threading.Thread(
        target=_do_done,
        args=(job_id, bool(aborted)),
        daemon=True,
        name="iot-local-run-done",
    ).start()
