# -*- coding: utf-8 -*-
"""过载能力测试执行器。"""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agent.job_inbox import wait_result, write_pending_job, write_result, write_stop_request
from agent.runners.base import ProgressCb, RunResult


def _default_sim_fixture_dir() -> Path:
    env = str(os.environ.get("SOLAR_SIM_CSV_DIR") or "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    # tests/fixtures/brazil_overload_542
    return Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "brazil_overload_542"


class OverloadRunner:
    """
    execution_mode:
      - dry_run: 仅模拟进度（默认联调）
      - sim / sim_bench: 无真机工况机——落样例 CSV + success，结案可走分析/上传
      - handoff: 参数落盘，等待 UI/外部写回 results/job_{id}.json
      - live: 无 UI 直控仪器（尚未实现）
    """

    def __init__(self, execution_mode: str = "dry_run", repo_root=None):
        from agent.config import _repo_root

        self.execution_mode = (execution_mode or "dry_run").strip().lower()
        # 与桌面 UI handoff 共用安装根下的 iot_job_inbox（勿落到 agent/）
        self.repo_root = Path(repo_root) if repo_root else _repo_root()
        self._release_for_ui = None
        self._abort_check: Optional[Callable[[], Optional[str]]] = None

    def set_release_for_ui(self, callback) -> None:
        """handoff 落盘后回调，用于释放 agent 互斥锁以便 UI 占锁。"""
        self._release_for_ui = callback

    def set_abort_check(self, callback: Optional[Callable[[], Optional[str]]]) -> None:
        """handoff 等待期间轮询云端中止；返回非空原因则写 stop_request 并结案 aborted。"""
        self._abort_check = callback

    def run(self, job: Dict[str, Any], on_progress: ProgressCb) -> Dict[str, Any]:
        write_pending_job(self.repo_root, job)
        mode = self.execution_mode
        if mode in ("sim", "sim_bench", "simulate", "假工况", "模拟工况"):
            return self._sim_bench(job, on_progress).as_dict()
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

    def _plant_sim_csv(self, job: Dict[str, Any]) -> Path:
        """按 testType 落模拟 CSV（谐波不再写 sample_overload）。"""
        from utils.iot_sim_by_type import plant_sim_csv_for_job

        job_id = job.get("id") or job.get("jobId") or "x"
        dest = (
            self.repo_root
            / "command_save_files"
            / "command_data"
            / f"sim_job_{job_id}"
        )
        try:
            return plant_sim_csv_for_job(job, dest)
        except Exception:
            # 兜底：按类型最小 CSV，避免分析完全找不到文件
            dest.mkdir(parents=True, exist_ok=True)
            tt = str(job.get("testType") or job.get("test_type") or "").lower()
            if tt in ("harmonic", "harmonics", "谐波", "谐波电流", "谐波电流测试"):
                try:
                    from utils.iot_sim_by_type import plant_sim_harmonic_csv

                    return plant_sim_harmonic_csv(job, dest)
                except Exception:
                    pass
            src_dir = _default_sim_fixture_dir()
            copied: List[Path] = []
            if src_dir.is_dir():
                for src in sorted(src_dir.glob("*.csv")):
                    target = dest / src.name
                    shutil.copy2(src, target)
                    copied.append(target)
            if not copied:
                stub = dest / "sample_overload.csv"
                stub.write_text(
                    "Time [s],P-SIGMA,U-SIGMA,Irms-1\n0.0,10000,230,43.5\n1.0,10020,230,43.6\n",
                    encoding="utf-8",
                )
            return dest

    def _sim_bench(self, job: Dict[str, Any], on_progress: ProgressCb) -> RunResult:
        """无仪器模拟工况机：按 testType 造数 + 上报 measures。"""
        from utils.iot_sim_by_type import _job_tt, run_sim_timeline_for_job
        from utils.wt_scpi_session import set_cloud_measures_override

        job_id = job.get("id") or job.get("jobId") or "x"
        data_dir = (
            self.repo_root
            / "command_save_files"
            / "command_data"
            / f"sim_job_{job_id}"
        )
        plan = None
        rows: List[Dict[str, Any]] = []
        try:
            data_dir, plan, rows = run_sim_timeline_for_job(
                job,
                dest_dir=data_dir,
                on_progress=on_progress,
                set_measures=set_cloud_measures_override,
            )
        except Exception as exc:
            set_cloud_measures_override(None)
            on_progress(50, f"sim 步骤异常，回退静态 CSV: {exc}", "sim_fallback")
            data_dir = self._plant_sim_csv(job)
            time.sleep(0.3)
            on_progress(95, "sim_bench：收尾，准备结案分析", "finish")
            plan = None
            rows = []
        finally:
            set_cloud_measures_override(None)

        report_files = [
            {"path": str(p), "name": p.name}
            for p in sorted(data_dir.glob("*.csv"))
        ]
        tt = _job_tt(job) or "overload"
        # 写回 job，避免结案分析因缺 testType 误走默认过载
        job["testType"] = tt
        summary: Dict[str, Any] = {
            "sim_bench": True,
            "dry_run": True,
            "jobId": job.get("id"),
            "title": job.get("title"),
            "testType": tt,
            "analysis_input_dir": str(data_dir),
            "report_files": report_files,
        }
        if plan is not None:
            summary["sim_plan"] = {
                "un": plan.un,
                "pn": plan.pn,
                "freq": plan.freq,
                "load_pct": plan.load_pct,
                "ac_wait_s": plan.ac_wait_s,
                "s1_stabilize_s": plan.s1_stabilize_s,
                "hold_s": plan.hold_s,
                "wall_scale": plan.wall_scale,
                "points": len(rows),
            }
        result = RunResult(
            status="success",
            result_summary=summary,
            report_meta=[{"path": x["path"], "name": x["name"]} for x in report_files],
        )
        write_result(self.repo_root, int(job.get("id") or 0), result.as_dict())
        return result

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
        data = wait_result(
            self.repo_root,
            job_id,
            timeout_sec=timeout,
            poll_sec=2.0,
            on_progress=on_progress,
            abort_check=self._abort_check,
        )
        if not data:
            return RunResult(status="failed", fail_reason="handoff 超时：未收到 results/job_*.json")
        if data.get("_remote_abort"):
            reason = str(data.get("fail_reason") or "云端已中止")
            try:
                write_stop_request(self.repo_root, job_id, reason=reason)
            except Exception:
                pass
            on_progress(100, "handoff：云端远程中止，已请求本机关机", "remote_abort")
            return RunResult(
                status="aborted",
                fail_reason="云端远程中止，已请求本机关机",
                result_summary={
                    "handoff": True,
                    "remote_abort": True,
                    "cloud_reason": reason,
                },
            )
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
