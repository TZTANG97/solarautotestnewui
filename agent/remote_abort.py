# -*- coding: utf-8 -*-
"""云端远程中止 → 本机 stop_request（含 local_ui 本机开测局）。

云任务 handoff 等待时已有 abort_check；本机开测时 Agent 不占 runner，
需在心跳里根据 status.json 的 jobId 轮询云端，aborted 则写 stop_request，
由 handoff 定时器执行 EndProjectPush（直流先关→交流）。
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger("solar.agent.remote_abort")

# 同一 job 只写一次 stop_request，避免心跳风暴
_last_stop_written_job: Optional[int] = None


def reset_remote_abort_state() -> None:
    global _last_stop_written_job
    _last_stop_written_job = None


def job_id_from_run_snapshot(run_snapshot: Any) -> int:
    if not isinstance(run_snapshot, dict):
        return 0
    try:
        return int(run_snapshot.get("jobId") or run_snapshot.get("job_id") or 0)
    except (TypeError, ValueError):
        return 0


def local_still_running(run_snapshot: Any) -> bool:
    """桌面仍在跑（未结束/中止）才需要远程停机。"""
    if not isinstance(run_snapshot, dict):
        return False
    st = str(run_snapshot.get("status") or "").strip()
    if not st:
        return True
    if st in ("已结束", "已中止", "失败", "空闲", "待机"):
        return False
    # 进行中 / 暂停 / 人工等待 / 运行 / 测试中 …
    return True


def sync_cloud_abort_to_stop_inbox(
    *,
    client: Any,
    repo_root: Path,
    run_snapshot: Any = None,
    get_job: Optional[Callable[[int], dict]] = None,
    write_stop: Optional[Callable[..., Path]] = None,
) -> Optional[int]:
    """
    若云端已把本局 job 标为 aborted，且本机仍在跑，则写 stop_request。
    返回写入的 job_id；无需动作返回 None。
    """
    global _last_stop_written_job

    jid = job_id_from_run_snapshot(run_snapshot)
    if jid <= 0:
        return None
    if not local_still_running(run_snapshot):
        return None
    if _last_stop_written_job == jid:
        return None

    getter = get_job or getattr(client, "get_job", None)
    if not callable(getter):
        return None
    try:
        info = getter(jid)
    except Exception as exc:
        logger.debug("远程中止轮询 get_job(%s) 失败: %s", jid, exc)
        return None
    if not isinstance(info, dict):
        return None
    st = str(info.get("status") or "").strip().lower()
    if st != "aborted":
        return None

    reason = str(
        info.get("fail_reason") or info.get("failReason") or "运维网页手动中止"
    ).strip() or "运维网页手动中止"

    writer = write_stop
    if writer is None:
        from agent.job_inbox import write_stop_request as writer  # type: ignore

    try:
        writer(Path(repo_root), jid, reason=reason)
    except Exception as exc:
        logger.warning("写 stop_request 失败 job=%s: %s", jid, exc)
        return None

    _last_stop_written_job = jid
    logger.info("云端已中止 job=%s，已写 stop_request（远程停机） reason=%s", jid, reason[:80])
    return jid
