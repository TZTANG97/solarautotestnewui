# -*- coding: utf-8 -*-
"""独立进程主循环：心跳 → 领任务 → 互斥 → 执行 → 回传。"""
from __future__ import annotations

import argparse
import logging
import os
import socket
import sys
import time
import traceback
from typing import Optional

from agent.client import IotSolarClient
from agent.config import load_config
from agent.mutex import LocalMutex
from agent.runners import get_runner

logger = logging.getLogger("solar.agent")


def _setup_log() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_once_job(
    client: IotSolarClient,
    mutex: LocalMutex,
    job: dict,
    dry_run: bool = True,
    execution_mode: str = "",
    repo_root=None,
) -> None:
    # 协议 experid 与兼容 id
    raw_id = job.get("experid") or job.get("id")
    job_id = int(raw_id)
    test_type = job.get("testType") or ""
    if job.get("pythonid"):
        client.pythonid = str(job.get("pythonid") or client.pythonid)
    holder = mutex.is_held_by_other("agent")
    if holder:
        logger.warning("本机锁被 %s 占用，拒绝任务 %s", holder, job_id)
        client.reject(job_id, reason=f"busy_local:{holder}")
        return
    if not mutex.acquire("agent", meta=f"job:{job_id}"):
        client.reject(job_id, reason="busy_local")
        return
    released_early = {"ok": False}

    def _release_for_ui() -> None:
        if not released_early["ok"]:
            mutex.release("agent")
            released_early["ok"] = True
            logger.info("handoff：已提前释放 agent 锁，供 UI 执行")

    try:
        runner = get_runner(
            test_type,
            dry_run=dry_run,
            execution_mode=execution_mode,
            repo_root=repo_root,
        )
        if hasattr(runner, "set_release_for_ui"):
            runner.set_release_for_ui(_release_for_ui)

        def on_progress(percent: int, text: str, step: str) -> None:
            try:
                client.progress(
                    job_id,
                    progress_percent=percent,
                    progress_text=text,
                    current_step=step,
                )
            except Exception as exc:
                logger.warning("progress 上报失败: %s", exc)

        from pathlib import Path as _Path

        root = _Path(repo_root) if repo_root else _Path(__file__).resolve().parent.parent
        result = runner.run(job, on_progress)
        client.done(
            job_id,
            status=result.get("status") or "failed",
            fail_reason=result.get("fail_reason") or "",
            result_summary=result.get("result_summary"),
            report_meta=None,
        )
        try:
            from agent.reports import collect_report_files

            for path in collect_report_files(root, job_id, result):
                try:
                    client.upload_report(job_id, str(path))
                    logger.info("已上传报告 %s", path.name)
                except Exception as exc:
                    logger.warning("上传报告失败 %s: %s", path, exc)
        except Exception as exc:
            logger.warning("收集报告失败: %s", exc)
        logger.info("任务 %s 结案: %s", job_id, result.get("status"))
    except Exception as exc:
        logger.error("任务 %s 异常: %s\n%s", job_id, exc, traceback.format_exc())
        try:
            client.done(job_id, status="failed", fail_reason=str(exc)[:500])
        except Exception:
            pass
    finally:
        if not released_early["ok"]:
            mutex.release("agent")


def main(argv: Optional[list] = None) -> int:
    _setup_log()
    parser = argparse.ArgumentParser(description="Solar AutoTest IOT Agent（独立进程）")
    parser.add_argument("--config", default="", help="配置文件路径，默认 config/solar_agent.json")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config or None)
    except Exception as exc:
        logger.error("%s", exc)
        return 2
    if not cfg.agent_token or cfg.agent_token.startswith("请填写"):
        logger.error("请配置有效的 agent_token")
        return 2

    client = IotSolarClient(cfg.iot_base, cfg.agent_token)
    mutex = LocalMutex(cfg.mutex_file)
    host = socket.gethostname()
    logger.info(
        "Solar Agent 启动 base=%s mode=%s version=%s host=%s",
        cfg.iot_base,
        cfg.resolved_execution_mode,
        cfg.agent_version,
        host,
    )

    interval = max(3.0, float(cfg.poll_interval_sec))
    while True:
        data = mutex._read()
        owner = str((data or {}).get("owner") or "")
        agent_busy = owner == "agent"
        try:
            hb = client.heartbeat(
                agent_version=cfg.agent_version,
                host_name=host,
                busy=agent_busy,
            )
            data_hb = hb.get("data") if isinstance(hb, dict) else None
            if isinstance(data_hb, dict) and data_hb.get("pythonid"):
                client.pythonid = str(data_hb.get("pythonid") or "")
        except Exception as exc:
            logger.warning("心跳失败: %s", exc)
            time.sleep(interval)
            continue

        if owner == "ui":
            logger.info("本机 UI 占用中，本轮不领任务")
            time.sleep(interval)
            continue

        if agent_busy:
            time.sleep(interval)
            continue

        try:
            job = client.claim_next()
        except Exception as exc:
            logger.warning("领任务失败: %s", exc)
            time.sleep(interval)
            continue

        if job:
            logger.info(
                "领取任务 experid=%s type=%s title=%s",
                job.get("experid") or job.get("id"),
                job.get("testType"),
                job.get("title"),
            )
            run_once_job(
                client,
                mutex,
                job,
                dry_run=cfg.dry_run,
                execution_mode=cfg.resolved_execution_mode,
            )

        time.sleep(interval)


if __name__ == "__main__":
    # 允许 python -m agent 与直接脚本
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raise SystemExit(main())
