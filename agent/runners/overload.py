# -*- coding: utf-8 -*-
"""过载能力测试执行器。"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

from agent.job_inbox import wait_result, write_pending_job, write_result
from agent.runners.base import ProgressCb, RunResult


class OverloadRunner:
    """
    execution_mode:
      - dry_run: 仅模拟进度（默认联调）
      - handoff: 参数落盘，等待 UI/外部写回 results/job_{id}.json
      - live: 无 UI 直控仪器（尚未实现）
    """

    def __init__(self, execution_mode: str = "dry_run", repo_root=None):
        from pathlib import Path

        self.execution_mode = (execution_mode or "dry_run").strip().lower()
        self.repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent
        self._release_for_ui = None

    def set_release_for_ui(self, callback) -> None:
        """handoff 落盘后回调，用于释放 agent 互斥锁以便 UI 占锁。"""
        self._release_for_ui = callback

    def run(self, job: Dict[str, Any], on_progress: ProgressCb) -> Dict[str, Any]:
        write_pending_job(self.repo_root, job)
        mode = self.execution_mode
        if mode in ("dry_run", "dryrun", "dry"):
            return self._dry_run(job, on_progress).as_dict()
        if mode in ("handoff", "ui", "ui_handoff"):
            return self._handoff(job, on_progress).as_dict()
        if mode in ("live", "real"):
            return self._live_run(job, on_progress).as_dict()
        return RunResult(
            status="failed",
            fail_reason=f"未知 execution_mode: {self.execution_mode}",
        ).as_dict()

    def _dry_run(self, job: Dict[str, Any], on_progress: ProgressCb) -> RunResult:
        on_progress(10, "dry_run：解析参数并已落盘 pending", "prepare")
        time.sleep(0.3)
        params = job.get("params") or {}
        on_progress(40, f"dry_run：模拟过载 params_keys={list(params)[:8]}", "S1")
        time.sleep(0.6)
        on_progress(75, "dry_run：模拟采集", "measure")
        time.sleep(0.4)
        on_progress(95, "dry_run：收尾", "finish")
        result = RunResult(
            status="success",
            result_summary={"dry_run": True, "jobId": job.get("id"), "title": job.get("title")},
            report_meta=[],
        )
        write_result(self.repo_root, int(job.get("id") or 0), result.as_dict())
        return result

    def _handoff(self, job: Dict[str, Any], on_progress: ProgressCb) -> RunResult:
        job_id = int(job.get("id") or 0)
        on_progress(5, "handoff：任务已写入 iot_job_inbox/pending，等待本机执行结果", "handoff")
        import os

        # 释放 agent 锁，让桌面 UI 可以 ui_try_acquire
        if callable(self._release_for_ui):
            try:
                self._release_for_ui()
                on_progress(8, "handoff：已释放本机 agent 锁，等待 UI", "handoff_unlock")
            except Exception as exc:
                on_progress(8, f"handoff：释放锁失败 {exc}", "handoff_unlock")

        timeout = float(os.environ.get("SOLAR_HANDOFF_TIMEOUT_SEC") or 7200)
        data = wait_result(self.repo_root, job_id, timeout_sec=timeout, poll_sec=2.0)
        if not data:
            return RunResult(status="failed", fail_reason="handoff 超时：未收到 results/job_*.json")
        status = str(data.get("status") or "failed")
        on_progress(100, "handoff：已收到本机结果", "done")
        return RunResult(
            status=status if status in ("success", "failed", "aborted") else "failed",
            fail_reason=str(data.get("fail_reason") or data.get("failReason") or ""),
            result_summary=data.get("result_summary") or data.get("resultSummary") or {},
            report_meta=data.get("report_meta") or data.get("reportMeta") or [],
        )

    def _live_run(self, job: Dict[str, Any], on_progress: ProgressCb) -> RunResult:
        on_progress(0, "live 模式尚未接入过载无 UI 入口", "blocked")
        return RunResult(
            status="failed",
            fail_reason=(
                "overload live 未实现。请用 dry_run 联调，或 execution_mode=handoff "
                "由本机 UI 读 pending 并写回 results"
            ),
        )
