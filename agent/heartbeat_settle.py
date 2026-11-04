# -*- coding: utf-8 -*-
"""心跳结案兜底：同一个 job 确认结案后不再重复 done，并上传已有产物。"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("solar.agent")

LOCAL_TERMINAL = frozenset({"已结束", "已中止", "失败"})
CLOUD_TERMINAL = frozenset({"success", "failed", "aborted", "rejected"})
_MAX_FILES = 48
_MAX_BYTES = 20 * 1024 * 1024


class HeartbeatSettleState:
    """进程内记忆。云端已终态或本次 done 成功后，不再对该 job 发结案兜底。"""

    def __init__(self) -> None:
        self.done_ok: set[int] = set()
        self.reports_finished: set[int] = set()
        self.report_attempts: Dict[int, int] = {}
        self.seen_running: set[int] = set()

    def forget(self, job_id: int) -> None:
        jid = int(job_id)
        self.done_ok.discard(jid)
        self.reports_finished.discard(jid)
        self.report_attempts.pop(jid, None)
        self.seen_running.discard(jid)


_shared = HeartbeatSettleState()


def shared_settle_state() -> HeartbeatSettleState:
    return _shared


def heartbeat_should_settle_terminal(
    *,
    status: str,
    settle_terminal: bool,
    seen_running: bool,
) -> bool:
    """桌面已是终态时是否调用 done。

    交接过程里平时不结案，避免把上一单残留的「已结束」安到新任务上。
    这一单已经进过进行中、桌面又写成终态时必须结案，否则网页一直停在执行中。
    """
    if str(status or "").strip() not in LOCAL_TERMINAL:
        return False
    if settle_terminal:
        return True
    return bool(seen_running)


def note_job_status(state: HeartbeatSettleState, job_id: int, status: str) -> None:
    """非终态说明这单还没结完，不能沿用上一轮的「已结案」记忆。"""
    st = str(status or "").strip()
    jid = int(job_id)
    if st in ("进行中", "暂停"):
        state.seen_running.add(jid)
        state.done_ok.discard(jid)
        return
    if st not in LOCAL_TERMINAL:
        state.forget(jid)


def cloud_status_is_terminal(status: str) -> bool:
    return str(status or "").strip().lower() in CLOUD_TERMINAL


def publish_terminal_result_if_missing(repo_root: Path, job_id: int, status: str) -> bool:
    """交接线程还堵在 wait_result 时，先落下终态结果，避免超时后再把成功改成失败。"""
    from agent.job_inbox import result_path, write_result

    jid = int(job_id)
    if jid <= 0:
        return False
    path = result_path(Path(repo_root), jid)
    if path.is_file():
        return False
    st = str(status or "").strip()
    write_result(
        Path(repo_root),
        jid,
        {
            "status": local_status_to_done(st),
            "fail_reason": "" if st == "已结束" else f"台架状态={st}",
            "result_summary": {
                "source": "agent_heartbeat_status_json",
                "run_status": st,
            },
            "report_meta": [],
        },
    )
    logger.info("交接终态已写入 results job=%s status=%s", jid, st)
    return True


def local_status_to_done(status: str) -> str:
    st = str(status or "").strip()
    if st == "已结束":
        return "success"
    if st == "已中止":
        return "aborted"
    return "failed"


def _cloud_status_from_job(payload: Any) -> str:
    data = payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        data = payload["data"]
    if not isinstance(data, dict):
        return ""
    return str(data.get("status") or "").strip()


def _load_inbox_result(repo_root: Path, job_id: int) -> Dict[str, Any]:
    path = repo_root / "iot_job_inbox" / "results" / f"job_{int(job_id)}.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _usable_file(path: Path) -> bool:
    try:
        size = path.stat().st_size
    except OSError:
        return False
    return 0 < size <= _MAX_BYTES


def _merge_paths(primary: List[Path], extra: List[Path]) -> List[Path]:
    seen = set()
    out: List[Path] = []
    for path in list(primary) + list(extra):
        try:
            key = str(path.resolve()).lower()
        except OSError:
            key = str(path).lower()
        if key in seen or not _usable_file(path):
            continue
        seen.add(key)
        out.append(path)
        if len(out) >= _MAX_FILES:
            break
    return out


def _recording_token(test_name: str) -> str:
    from agent.reports import recording_token_for_test

    return recording_token_for_test(test_name)


def existing_settle_files(
    repo_root: Path,
    job_id: int,
    run_snapshot: Dict[str, Any],
) -> List[Path]:
    """收集这单已经存在的结果/录波，供结案元数据和 upload_report 使用。"""
    from agent.reports import collect_report_files, window_output_files_by_token

    root = Path(repo_root)
    result = _load_inbox_result(root, job_id)
    summary = result.get("result_summary")
    if not isinstance(summary, dict):
        summary = {}
        result["result_summary"] = summary
    try:
        elapsed = float(run_snapshot.get("elapsed_s") or summary.get("elapsed_sec") or 0)
    except (TypeError, ValueError):
        elapsed = 0.0
    if elapsed > 0 and not summary.get("elapsed_sec"):
        summary["elapsed_sec"] = elapsed
    test_name = str(
        run_snapshot.get("current_test")
        or run_snapshot.get("project")
        or summary.get("testType")
        or ""
    ).strip()
    if test_name and not summary.get("testType"):
        summary["testType"] = test_name
    files = collect_report_files(root, int(job_id), result)
    if elapsed > 0:
        until = time.time() + 60.0
        since = until - elapsed - 120.0
        files = _merge_paths(
            files,
            window_output_files_by_token(
                root,
                since,
                until,
                name_token=_recording_token(test_name),
            ),
        )
    else:
        files = _merge_paths(files, [])
    return files


def _file_meta(paths: List[Path]) -> List[Dict[str, str]]:
    meta: List[Dict[str, str]] = []
    for path in paths:
        meta.append({"path": str(path), "name": path.name, "filename": path.name})
    return meta


def _is_substantive_report(path: Path) -> bool:
    """status.json / job_*.json / *commands*.csv 不算正式试验产物。"""
    name = path.name.lower()
    if name == "status.json":
        return False
    if name.startswith("job_") and name.endswith(".json"):
        return False
    if name.endswith(".csv") and "commands" in name:
        return False
    return True


def apply_heartbeat_terminal_settle(
    client: Any,
    *,
    repo_root: Path,
    job_id: int,
    run_snapshot: Dict[str, Any],
    state: Optional[HeartbeatSettleState] = None,
) -> None:
    """本地终态时结案一次。done 成功或云端已是终态后，后续心跳不再发。"""
    state = state or shared_settle_state()
    jid = int(job_id)
    snap = run_snapshot if isinstance(run_snapshot, dict) else {}
    st = str(snap.get("status") or "").strip()
    if st not in LOCAL_TERMINAL:
        state.forget(jid)
        return
    # 重启后 status.json 往往仍是上一局的「已中止」。新任务号写上去之后，
    # 本进程若还没见过它在跑，不能据此把云端新单打成台架状态=已中止。
    if st == "已中止" and jid not in state.seen_running:
        logger.info(
            "心跳跳过结案 job=%s：本进程未见其进入进行中（status=%s）",
            jid,
            st,
        )
        return

    pending_files: Optional[List[Path]] = None
    if jid not in state.done_ok:
        cloud_st = ""
        try:
            cloud_st = _cloud_status_from_job(client.get_job(jid))
        except Exception as exc:
            logger.debug("心跳结案查询云端状态跳过 job=%s: %s", jid, exc)
            cloud_st = ""
        if cloud_status_is_terminal(cloud_st):
            state.done_ok.add(jid)
            logger.info(
                "心跳结案已确认云端终态，不再重复 job=%s cloud=%s",
                jid,
                cloud_st,
            )
        else:
            done_st = local_status_to_done(st)
            try:
                pending_files = existing_settle_files(Path(repo_root), jid, snap)
            except Exception as exc:
                logger.warning("心跳结案收集已有文件失败 job=%s: %s", jid, exc)
                pending_files = None
            meta = _file_meta(pending_files or [])
            summary: Dict[str, Any] = {
                "source": "agent_heartbeat_status_json",
                "run_status": st,
                "progress": int(snap.get("progress") or 0),
            }
            if meta:
                summary["report_files"] = meta
            try:
                client.done(
                    jid,
                    status=done_st,
                    fail_reason="" if done_st == "success" else f"台架状态={st}",
                    result_summary=summary,
                    report_meta=meta or None,
                )
            except Exception as exc:
                logger.debug("心跳结案兜底跳过 job=%s: %s", jid, exc)
                return
            state.done_ok.add(jid)
            logger.info(
                "心跳结案兜底 job=%s status=%s (status.json=%s)",
                jid,
                done_st,
                st,
            )

    if jid not in state.done_ok or jid in state.reports_finished:
        return
    attempts = int(state.report_attempts.get(jid) or 0) + 1
    state.report_attempts[jid] = attempts
    root = Path(repo_root)
    # 本地开测走心跳结案时也尽量跑一次分析，再重新收集（失败不阻断上传）
    if st == "已结束":
        try:
            result = _load_inbox_result(root, jid)
            if not isinstance(result, dict):
                result = {}
            summary = result.get("result_summary")
            if not isinstance(summary, dict):
                summary = {}
                result["result_summary"] = summary
            if not summary.get("testType"):
                summary["testType"] = str(
                    snap.get("current_test") or snap.get("project") or ""
                ).strip()
            if not result.get("status"):
                result["status"] = "success"
            try:
                from agent.reports import collect_report_files
                from utils.iot_data_analysis_bridge import (
                    remember_analysis_input_dir,
                    run_analysis_after_job,
                )

                # 与 main_loop 一致：分析前把已有 CSV/录波写入 report_files，供 _pick_input_dir
                try:
                    pre = collect_report_files(root, jid, result)
                    listed = list(summary.get("report_files") or [])
                    have = {
                        str(x.get("path") if isinstance(x, dict) else x) for x in listed
                    }
                    for p in pre:
                        s = str(p)
                        if s not in have:
                            listed.append({"path": s, "name": p.name})
                            have.add(s)
                    summary["report_files"] = listed
                except Exception as exc:
                    logger.warning("心跳结案预收集失败（继续分析）job=%s: %s", jid, exc)
                remember_analysis_input_dir(result, root)
                params0 = result.get("params") if isinstance(result.get("params"), dict) else {}
                job_snap = {
                    "id": jid,
                    "testType": summary.get("testType") or "",
                    "params": dict(params0),
                    "widgets": summary.get("widgets") or {},
                }
                sid = str(
                    summary.get("solarStandard")
                    or summary.get("solar_standard")
                    or params0.get("solarStandard")
                    or params0.get("solar_standard")
                    or ""
                ).strip()
                if sid:
                    job_snap["solarStandard"] = sid
                    job_snap["params"]["solarStandard"] = sid
                ana = run_analysis_after_job(repo_root=root, job=job_snap, result=result)
                if ana.get("skipped"):
                    logger.info(
                        "心跳结案分析跳过 job=%s: %s",
                        jid,
                        ana.get("reason") or "",
                    )
                elif ana.get("success"):
                    logger.info(
                        "心跳结案分析成功 job=%s files=%s",
                        jid,
                        len(ana.get("output_files") or []),
                    )
                elif ana.get("ran"):
                    logger.warning(
                        "心跳结案分析失败 job=%s: %s",
                        jid,
                        ana.get("reason") or "",
                    )
                try:
                    from agent.job_inbox import write_result

                    write_result(root, jid, result)
                except Exception:
                    pass
            except Exception as exc:
                logger.warning("心跳结案分析跳过 job=%s: %s", jid, exc)
            # 分析后重收集，避免只用 done 前那一版
            pending_files = None
        except Exception as exc:
            logger.debug("心跳结案分析前置跳过 job=%s: %s", jid, exc)

    if pending_files is None:
        try:
            files = existing_settle_files(root, jid, snap)
        except Exception as exc:
            logger.warning("心跳结案收集已有文件失败 job=%s: %s", jid, exc)
            if attempts >= 2:
                state.reports_finished.add(jid)
            return
    else:
        files = pending_files
    if not files:
        # 录波可能尚未落盘：前几次心跳不要永久放弃
        if attempts >= 3:
            state.reports_finished.add(jid)
            logger.info("心跳结案多次仍无结果文件可上传 job=%s", jid)
        else:
            logger.info(
                "心跳结案暂无结果文件，等待下次心跳重试 job=%s attempt=%s",
                jid,
                attempts,
            )
        return
    # 正式产物优先；status.json / inbox result 最后传，避免试验报告列表只剩运行快照
    def _upload_rank(path: Path) -> tuple:
        name = path.name.lower()
        if name == "status.json" or (name.startswith("job_") and name.endswith(".json")):
            return (2, name)
        if path.suffix.lower() in {".csv", ".xlsx", ".xls", ".docx", ".pdf"}:
            return (0, name)
        return (1, name)

    files = sorted(files, key=_upload_rank)
    failed = False
    uploaded = 0
    for path in files:
        try:
            client.upload_report(jid, str(path))
            uploaded += 1
        except Exception as exc:
            failed = True
            logger.warning("心跳结案上传已有文件失败 %s: %s", path.name, exc)
    # 仅 status.json / job_*.json / 命令记录 csv 不算正式产物齐套，继续等录波和报告
    substantive = [p for p in files if _is_substantive_report(p)]
    if (not failed and substantive) or attempts >= 3:
        state.reports_finished.add(jid)
    if uploaded:
        logger.info("心跳结案已上传已有产物 job=%s files=%s", jid, uploaded)
