# -*- coding: utf-8 -*-
"""独立进程主循环：心跳 → 领任务 → 互斥 → 执行 → 回传。"""
from __future__ import annotations

import argparse
import logging
import os
import signal
import socket
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Optional

from agent.client import IotSolarClient
from agent.config import load_config
from agent.mutex import LocalMutex
from agent.runners import get_runner

logger = logging.getLogger("solar.agent")

# 当前执行中的任务；进程退出时尽量结案，避免云端永久 running
_current_job_id: Optional[int] = None
_client_ref: Optional[IotSolarClient] = None


def _setup_log() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _abort_current_on_exit(reason: str) -> None:
    global _current_job_id
    job_id = _current_job_id
    client = _client_ref
    if not job_id or not client:
        return
    try:
        client.done(job_id, status="aborted", fail_reason=reason[:500])
        logger.info("退出前已结案任务 %s: %s", job_id, reason)
    except Exception as exc:
        logger.warning("退出前结案失败 job=%s: %s", job_id, exc)
    _current_job_id = None


def run_once_job(
    client: IotSolarClient,
    mutex: LocalMutex,
    job: dict,
    dry_run: bool = True,
    execution_mode: str = "",
    repo_root=None,
    *,
    agent_version: str = "",
    host_name: str = "",
    heartbeat_interval_sec: float = 15.0,
) -> None:
    global _current_job_id
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
    _current_job_id = job_id

    def _release_for_ui() -> None:
        if not released_early["ok"]:
            mutex.release("agent")
            released_early["ok"] = True
            logger.info("handoff：已提前释放 agent 锁，供 UI 执行")

    # handoff 等待期间主循环被堵住，单独线程续心跳，避免云端误判离线又卡住任务
    stop_hb = threading.Event()

    def _hb_while_job() -> None:
        while not stop_hb.wait(max(5.0, float(heartbeat_interval_sec))):
            try:
                client.heartbeat(
                    agent_version=agent_version,
                    host_name=host_name,
                    busy=True,
                )
            except Exception as exc:
                logger.warning("任务中心跳失败: %s", exc)

    hb_thread = threading.Thread(target=_hb_while_job, name="solar-agent-hb", daemon=True)
    hb_thread.start()

    try:
        runner = get_runner(
            test_type,
            dry_run=dry_run,
            execution_mode=execution_mode,
            repo_root=repo_root,
        )
        if hasattr(runner, "set_release_for_ui"):
            runner.set_release_for_ui(_release_for_ui)

        if hasattr(runner, "set_abort_check"):

            def _cloud_abort_check() -> Optional[str]:
                try:
                    info = client.get_job(job_id)
                except Exception as exc:
                    logger.debug("abort 轮询失败: %s", exc)
                    return None
                st = str((info or {}).get("status") or "").strip().lower()
                if st != "aborted":
                    return None
                return str(
                    (info or {}).get("fail_reason")
                    or (info or {}).get("failReason")
                    or "运维网页手动中止"
                )

            runner.set_abort_check(_cloud_abort_check)

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

        from agent.config import _repo_root as _agent_repo_root

        root = _Path(repo_root) if repo_root else _agent_repo_root()
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
        stop_hb.set()
        _current_job_id = None
        if not released_early["ok"]:
            mutex.release("agent")


def main(argv: Optional[list] = None) -> int:
    global _client_ref
    _setup_log()
    parser = argparse.ArgumentParser(description="Solar AutoTest IOT Agent（独立进程）")
    parser.add_argument("--config", default="", help="配置文件路径，默认 config/solar_agent.json")
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config or None)
    except Exception as exc:
        logger.error("%s", exc)
        return 2

    host = socket.gethostname()
    pythonid = ""
    machine_id = ""
    try:
        import json
        from agent.config import default_config_path

        p = Path(args.config) if args.config else default_config_path()
        raw = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
        pythonid = str(raw.get("pythonid") or "").strip()
        machine_id = str(raw.get("machine_id") or "").strip()
    except Exception:
        pass

    # 无令牌也可先 WebSocket 上线，便于「添加设备」发现
    try:
        from agent.ws_gateway import start_presence

        if pythonid and cfg.iot_base:
            start_presence(
                iot_base=cfg.iot_base,
                pythonid=pythonid,
                machine_id=machine_id,
                host_name=host,
            )
            logger.info("WebSocket 上线 pythonid=%s", pythonid)
    except Exception as exc:
        logger.warning("WebSocket 上线失败: %s", exc)

    if not cfg.agent_token or cfg.agent_token.startswith("请填写"):
        logger.info("尚无 agent_token，进入等待「添加设备」领取令牌…")
        from agent.bootstrap import claim_once, config_has_token, resolve_iot_base, _is_local_iot

        while True:
            ok, msg, _ = claim_once()
            if ok and config_has_token():
                try:
                    cfg = load_config(args.config or None)
                except Exception as exc:
                    logger.warning("重新加载配置失败: %s", exc)
                if cfg.agent_token and not cfg.agent_token.startswith("请填写"):
                    if not _is_local_iot(cfg.iot_base):
                        logger.info("%s", msg)
                        break
            logger.info("%s", msg)
            time.sleep(5.0)

    client = IotSolarClient(cfg.iot_base, cfg.agent_token, pythonid=pythonid)
    _client_ref = client
    mutex = LocalMutex(cfg.mutex_file)

    def _on_signal(signum, _frame):
        logger.warning("收到信号 %s，准备退出并结案当前任务", signum)
        _abort_current_on_exit(f"Agent 进程收到信号 {signum} 退出")
        raise SystemExit(0)

    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig is None:
            continue
        try:
            signal.signal(sig, _on_signal)
        except Exception:
            pass

    logger.info(
        "Solar Agent 启动 base=%s mode=%s version=%s host=%s pythonid=%s",
        cfg.iot_base,
        cfg.resolved_execution_mode,
        cfg.agent_version,
        host,
        pythonid or client.pythonid,
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
                agent_version=cfg.agent_version,
                host_name=host,
                heartbeat_interval_sec=float(cfg.heartbeat_interval_sec or 15),
            )

        time.sleep(interval)


if __name__ == "__main__":
    # 允许 python -m agent 与直接脚本
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raise SystemExit(main())
