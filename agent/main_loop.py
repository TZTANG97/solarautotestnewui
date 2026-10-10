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
from agent.instruments_snapshot import collect_instruments_snapshot
from agent.local_endpoints import collect_local_endpoints
from agent.mutex import LocalMutex
from agent.runners import get_runner

logger = logging.getLogger("solar.agent")

# 当前执行中的任务；进程退出时尽量结案，避免云端永久 running
_current_job_id: Optional[int] = None
_client_ref: Optional[IotSolarClient] = None

# 云端试连：心跳领取后探测，下一轮心跳回传
_pending_probe_request_id: str = ""
_pending_probe_results: Optional[list] = None
_probe_lock = threading.Lock()

# 仪器控制结果回传
_pending_control_request_id: str = ""
_pending_control_result: Optional[dict] = None
_control_lock = threading.Lock()


def _consume_probe_payload() -> tuple:
    """取出待上报的试连结果（只发一次）。"""
    global _pending_probe_request_id, _pending_probe_results
    with _probe_lock:
        rid = _pending_probe_request_id
        results = _pending_probe_results
        _pending_probe_request_id = ""
        _pending_probe_results = None
    return rid, results


def _consume_control_payload() -> tuple:
    global _pending_control_request_id, _pending_control_result
    with _control_lock:
        rid = _pending_control_request_id
        result = _pending_control_result
        _pending_control_request_id = ""
        _pending_control_result = None
    return rid, result


def _handle_pending_actions(data_hb: dict) -> None:
    """处理心跳回包里的 pendingActions（probe / control_instrument）。"""
    global _pending_probe_request_id, _pending_probe_results
    global _pending_control_request_id, _pending_control_result
    if not isinstance(data_hb, dict):
        return
    actions = data_hb.get("pendingActions") or data_hb.get("pending_actions") or []
    if not isinstance(actions, list):
        return
    for action in actions:
        if not isinstance(action, dict):
            continue
        atype = str(action.get("type") or "")
        if atype == "probe_instruments":
            request_id = str(action.get("requestId") or action.get("request_id") or "")
            instruments = action.get("instruments") or []
            logger.info("收到试连任务 requestId=%s count=%s", request_id, len(instruments or []))
            try:
                from agent.instrument_probe import probe_instruments

                results = probe_instruments(instruments if isinstance(instruments, list) else [])
            except Exception as exc:
                logger.warning("试连执行失败: %s", exc)
                results = [
                    {
                        "resource": str((x or {}).get("resource") or ""),
                        "slot": str((x or {}).get("slot") or ""),
                        "connected": False,
                        "error": str(exc)[:255],
                    }
                    for x in (instruments or [])
                    if isinstance(x, dict)
                ]
            with _probe_lock:
                _pending_probe_request_id = request_id
                _pending_probe_results = results
            ok_n = sum(1 for r in results if r.get("connected"))
            logger.info("试连完成 requestId=%s ok=%s/%s", request_id, ok_n, len(results))
            continue

        if atype == "control_instrument":
            request_id = str(action.get("requestId") or action.get("request_id") or "")
            logger.info(
                "收到仪器控制 requestId=%s action=%s",
                request_id,
                action.get("action"),
            )

            def _run_ctrl(act=action, rid=request_id):
                global _pending_control_request_id, _pending_control_result
                try:
                    from agent.device_control import run_control_via_desktop

                    result = run_control_via_desktop(act, timeout_sec=25.0)
                except Exception as exc:
                    logger.warning("仪器控制失败: %s", exc)
                    result = {"ok": False, "message": str(exc)[:500], "requestId": rid}
                with _control_lock:
                    _pending_control_request_id = rid
                    _pending_control_result = result

            threading.Thread(target=_run_ctrl, name="iot-device-ctrl", daemon=True).start()
            continue


def _do_heartbeat(
    client: IotSolarClient,
    *,
    agent_version: str,
    host_name: str,
    busy: bool,
    status_json_path: str,
) -> Optional[dict]:
    rid, probe_results = _consume_probe_payload()
    ctrl_rid, ctrl_result = _consume_control_payload()
    run_snapshot = None
    try:
        from utils.iot_run_snapshot import build_run_snapshot_from_status, snapshot_implies_busy

        run_snapshot = build_run_snapshot_from_status(status_json_path)
        if snapshot_implies_busy(run_snapshot):
            busy = True
    except Exception:
        run_snapshot = None
    try:
        hb = client.heartbeat(
            agent_version=agent_version,
            host_name=host_name,
            busy=busy,
            instruments=collect_instruments_snapshot(status_json_path=status_json_path),
            local_resources=collect_local_endpoints(),
            probe_results=probe_results,
            probe_request_id=rid,
            control_result=ctrl_result,
            control_request_id=ctrl_rid,
            run_snapshot=run_snapshot,
        )
    except Exception:
        # 回传失败时把结果塞回去，下一轮再试
        if probe_results is not None:
            with _probe_lock:
                if _pending_probe_results is None:
                    _pending_probe_request_id = rid
                    _pending_probe_results = probe_results
        if ctrl_result is not None:
            with _control_lock:
                if _pending_control_result is None:
                    _pending_control_request_id = ctrl_rid
                    _pending_control_result = ctrl_result
        raise
    data_hb = hb.get("data") if isinstance(hb, dict) else None
    if isinstance(data_hb, dict):
        if data_hb.get("pythonid"):
            client.pythonid = str(data_hb.get("pythonid") or "")
        _handle_pending_actions(data_hb)
    # 有关联 job 时额外打一枪 progress（任务详情页即时性更好）
    try:
        jid = int((run_snapshot or {}).get("jobId") or 0)
        if jid > 0 and run_snapshot:
            client.progress(
                jid,
                progress_percent=int(run_snapshot.get("progress") or 0),
                progress_text=str(
                    run_snapshot.get("remain_text")
                    or run_snapshot.get("current_detail")
                    or ""
                )[:255],
                current_step=str(
                    run_snapshot.get("current_detail")
                    or run_snapshot.get("current_test")
                    or ""
                )[:128],
            )
            # 本地开测结案兜底：桌面已写「已结束/已中止」但未调 done 时，实验管理会一直「测试中」
            st = str(run_snapshot.get("status") or "").strip()
            if st in ("已结束", "已中止", "失败"):
                done_st = (
                    "success"
                    if st == "已结束"
                    else ("aborted" if st == "已中止" else "failed")
                )
                try:
                    client.done(
                        jid,
                        status=done_st,
                        fail_reason="" if done_st == "success" else f"台架状态={st}",
                        result_summary={
                            "source": "agent_heartbeat_status_json",
                            "run_status": st,
                            "progress": int(run_snapshot.get("progress") or 0),
                        },
                    )
                    logger.info(
                        "心跳结案兜底 job=%s status=%s (status.json=%s)",
                        jid,
                        done_st,
                        st,
                    )
                except Exception as exc:
                    logger.debug("心跳结案兜底跳过 job=%s: %s", jid, exc)
    except Exception:
        pass
    # HTTPS 心跳成功后顺便经 WS 推一帧串口/仪器，供网页即时刷新
    try:
        from agent import ws_gateway

        ws_gateway.push_instrument_status()
    except Exception:
        pass
    return data_hb if isinstance(data_hb, dict) else None


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
    # HTTPS 任务主键用 id；协议 experid 可为 experiments.id（与 id 不同）
    raw_id = job.get("id")
    if raw_id is None:
        raw_id = job.get("experid")
    job_id = int(raw_id)
    test_type = job.get("testType") or ""
    if job.get("pythonid"):
        client.pythonid = str(job.get("pythonid") or client.pythonid)
    holder = mutex.is_held_by_other("agent")
    if holder:
        logger.warning("本机锁被 %s 占用，拒绝任务 %s", holder, job_id)
        client.reject(job_id, reason="本机试验进行中，已拒收云端任务")
        return
    if not mutex.acquire("agent", meta=f"job:{job_id}"):
        client.reject(job_id, reason="本机试验进行中，已拒收云端任务")
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
                _do_heartbeat(
                    client,
                    agent_version=agent_version,
                    host_name=host_name,
                    busy=True,
                    status_json_path=str((repo_root or Path(".")) / "status.json"),
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
            # 进度：MQTT 为主；失败则 HTTPS 兜底（避免实验管理无上报）
            measures = None
            try:
                from utils.wt_scpi_session import latest_cloud_measures

                measures = latest_cloud_measures()
            except Exception:
                measures = None
            mqtt_ok = False
            try:
                from agent.mqtt_publish import publish_experdata

                params = job.get("params") if isinstance(job.get("params"), dict) else {}
                exper_ref = ""
                if isinstance(params, dict):
                    exper_ref = str(params.get("experId") or params.get("experid") or "")
                mqtt_ok = bool(
                    publish_experdata(
                        pythonid=str(client.pythonid or job.get("pythonid") or ""),
                        job_id=job_id,
                        progress_percent=percent,
                        progress_text=text,
                        current_step=step,
                        exper_id=exper_ref,
                        measures=measures,
                    )
                )
            except Exception as exc:
                logger.warning("MQTT progress 失败: %s", exc)
            if not mqtt_ok:
                try:
                    client.progress(
                        job_id,
                        progress_percent=percent,
                        progress_text=text,
                        current_step=step,
                        measures=measures,
                    )
                except Exception as exc:
                    logger.warning("HTTPS progress 兜底失败: %s", exc)
            # WS 仅作本机网关即时推 web（非主通道）
            try:
                from agent import ws_gateway

                equ: dict = {
                    "equ_id": f"SOLAR-JOB-{job_id}",
                    "progress_percent": int(percent),
                    "progress_text": text,
                    "current_step": step,
                    "channel": "solar",
                }
                ws_body: dict = {
                    "type": "SolarEquipment_experdata_return",
                    "experid": str(job_id),
                    "time": "1",
                    "equs": [equ],
                }
                if isinstance(measures, dict) and measures:
                    equ["measures"] = dict(measures)
                    ws_body["measures"] = dict(measures)
                ws_gateway.send_json(ws_body)
            except Exception:
                pass

        from pathlib import Path as _Path

        from agent.config import _repo_root as _agent_repo_root

        root = _Path(repo_root) if repo_root else _agent_repo_root()
        result = runner.run(job, on_progress)
        # 结案状态：MQTT auto_end 为主；HTTPS done 仅兜底/补报告
        mqtt_end_ok = False
        try:
            from agent.mqtt_publish import publish_exper_auto_end

            proto_status = {
                "success": "OK",
                "aborted": "NG",
                "failed": "FAIL",
            }.get(str(result.get("status") or "").lower(), "FAIL")
            mqtt_end_ok = bool(
                publish_exper_auto_end(
                    pythonid=str(client.pythonid or job.get("pythonid") or ""),
                    job_id=job_id,
                    status=proto_status,
                    fail_reason=str(result.get("fail_reason") or ""),
                    result_summary=result.get("result_summary")
                    if isinstance(result.get("result_summary"), dict)
                    else None,
                )
            )
        except Exception as exc:
            logger.debug("MQTT auto_end 跳过: %s", exc)
        if not mqtt_end_ok:
            try:
                client.done(
                    job_id,
                    status=result.get("status") or "failed",
                    fail_reason=result.get("fail_reason") or "",
                    result_summary=result.get("result_summary"),
                    report_meta=None,
                )
            except Exception as exc:
                logger.warning("HTTPS done 兜底失败: %s", exc)
        else:
            # MQTT 已结案：仍尝试 HTTPS done 幂等补报告元数据（失败忽略）
            try:
                client.done(
                    job_id,
                    status=result.get("status") or "failed",
                    fail_reason=result.get("fail_reason") or "",
                    result_summary=result.get("result_summary"),
                    report_meta=None,
                )
            except Exception:
                pass
        try:
            from agent import ws_gateway

            proto_status = {
                "success": "OK",
                "aborted": "NG",
                "failed": "FAIL",
            }.get(str(result.get("status") or "").lower(), "FAIL")
            ws_gateway.send_json(
                {
                    "type": "SolarEquipment_experautoend_return",
                    "experid": str(job_id),
                    "status": proto_status,
                    "fail_reason": result.get("fail_reason") or "",
                    "result_summary": result.get("result_summary") or {},
                    "channel": "solar",
                }
            )
        except Exception:
            pass
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
        logger.info("任务 %s 结案: %s mqtt_end=%s", job_id, result.get("status"), mqtt_end_ok)
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

    try:
        from agent.mqtt_publish import configure as configure_mqtt

        configure_mqtt(cfg.mqtt)
    except Exception as exc:
        logger.warning("MQTT 配置加载失败: %s", exc)

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

    try:
        from agent.instruments_snapshot import set_identity

        set_identity(host_name=host, machine_id=machine_id, python_id=pythonid)
    except Exception:
        pass

    # 启动时拉取台架参数记忆（仪器/试验上次保存）
    try:
        from utils.iot_bench_prefs import pull_from_cloud

        pulled = pull_from_cloud()
        if pulled:
            logger.info(
                "已同步工控机参数记忆 instruments=%s testTypes=%s",
                len(pulled.get("instruments") or []),
                len(pulled.get("testParamsByType") or {}),
            )
    except Exception as exc:
        logger.debug("prefs pull skipped: %s", exc)

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

    # MQTT 订阅开测命令（WS 离线时仍可收 startexper）
    try:
        from agent.mqtt_subscribe import start_subscriber

        if pythonid:
            start_subscriber(pythonid=pythonid, cfg=cfg.mqtt)
    except Exception as exc:
        logger.warning("MQTT 订阅启动失败: %s", exc)

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
    try:
        from agent.config import _repo_root as _agent_repo_root

        repo_root = _agent_repo_root()
    except Exception:
        repo_root = Path(__file__).resolve().parents[1]

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
            _do_heartbeat(
                client,
                agent_version=cfg.agent_version,
                host_name=host,
                busy=agent_busy,
                status_json_path=str(repo_root / "status.json"),
            )
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
            job = None
            via = ""
            try:
                from agent import ws_gateway

                job = ws_gateway.pop_pending_job()
                if job:
                    via = "ws"
            except Exception:
                job = None
            if not job:
                try:
                    from agent import mqtt_subscribe

                    job = mqtt_subscribe.pop_pending_job()
                    if job:
                        via = "mqtt"
                except Exception:
                    job = None
            # WS/MQTT 优先；仍应用 HTTPS claim 兜底。
            # 否则「实验开测只入队、推送丢失」时任务会永久停在排队中。
            if not job:
                job = client.claim_next()
                if job:
                    via = "http-fallback"
        except Exception as exc:
            logger.warning("领任务失败: %s", exc)
            time.sleep(interval)
            continue

        if job:
            logger.info(
                "领取任务 experid=%s type=%s title=%s via=%s",
                job.get("experid") or job.get("id"),
                job.get("testType"),
                job.get("title"),
                via or ("ws" if job.get("type") == "startexper" else "http"),
            )
            # WS 下发的 startexper 可能尚未 HTTP claim；用 id 跑即可
            if job.get("commands") and isinstance(job.get("commands"), dict) and not job.get("testType"):
                try:
                    import json as _json

                    cmd = job["commands"].get("command") or ""
                    nested = _json.loads(cmd) if isinstance(cmd, str) else cmd
                    if isinstance(nested, dict):
                        job.setdefault("testType", nested.get("testType") or "")
                        job.setdefault("title", nested.get("title") or "")
                        job.setdefault("params", nested.get("params") or {})
                except Exception:
                    pass
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
