# -*- coding: utf-8 -*-
"""从 status.json / 本机状态组装 IOT heartbeat.runSnapshot。"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _status_json_path(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit)
    return _repo_root() / "status.json"


def _resolve_job_ids() -> Dict[str, Optional[int]]:
    job_id = None
    exper_id = None
    try:
        from utils.iot_local_run import current_local_job_id

        jid = current_local_job_id()
        if jid:
            job_id = int(jid)
    except Exception:
        pass
    try:
        import SCPITestWave as sw

        svc = getattr(sw, "_iot_ui_handoff_svc", None)
        if svc is not None:
            aw = getattr(svc, "_awaiting", None) or {}
            ctx = getattr(svc, "_job_ctx", None) or {}
            for src in (aw, ctx):
                try:
                    j = int(src.get("job_id") or 0)
                    if j > 0:
                        job_id = j
                        break
                except (TypeError, ValueError, AttributeError):
                    continue
    except Exception:
        pass
    # local_run 也可能存了 exper_id
    try:
        import utils.iot_local_run as lr

        with lr._lock:
            eid = lr._state.get("exper_id")
        if eid:
            exper_id = int(eid)
    except Exception:
        pass
    return {"jobId": job_id, "experId": exper_id}


def build_run_snapshot_from_status(status_json_path: Optional[str] = None) -> Dict[str, Any]:
    """读取 status.json 的 project 段，拼白名单快照。

    Agent 多为独立进程，以 status.json 为准；同进程时再合并内存态。
    """
    path = _status_json_path(status_json_path)
    project: Dict[str, Any] = {}
    try:
        if path.is_file():
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and isinstance(raw.get("project"), dict):
                project = dict(raw["project"])
    except Exception as exc:
        logger.debug("读取 status.json 进度失败: %s", exc)

    # 同进程可叠内存态；Agent 独立进程 import SCPITestWave 会得到默认「未开始」，勿盖住 status.json
    mem: Dict[str, Any] = {}
    try:
        import SCPITestWave as sw

        state = getattr(sw, "_run_progress_state", None)
        if isinstance(state, dict) and state:
            st_m = str(state.get("status") or "")
            active = (
                st_m in ("进行中", "暂停")
                or bool(state.get("operator_pause"))
                or float(state.get("started_at") or 0) > 0
                or int(state.get("progress") or 0) > 0
                or int(state.get("cmd_total") or 0) > 0
            )
            if active:
                mem = dict(state)
                try:
                    import time

                    from utils.run_progress_eta import compute_eta

                    now_ts = time.time()
                    started = float(mem.get("started_at") or 0.0)
                    pause_acc = float(mem.get("pause_accumulated_s") or 0.0)
                    pause_started = float(mem.get("pause_started_at") or 0.0)
                    if bool(mem.get("operator_pause")) and pause_started > 0:
                        pause_acc += max(0.0, now_ts - pause_started)
                    elapsed = max(0.0, (now_ts - started) - pause_acc) if started > 0 else 0.0
                    if mem.get("status") in ("未开始", "待开始"):
                        elapsed = 0.0
                    pct = int(mem.get("progress") or project.get("progress") or 0)
                    cmds = getattr(sw, "strArrayTest", None) or []
                    freeze = bool(mem.get("operator_pause")) or str(mem.get("status") or "") == "暂停"
                    eta = compute_eta(
                        elapsed_s=elapsed,
                        progress_pct=pct,
                        planned_total_s=float(mem.get("planned_seconds") or 0.0),
                        cmd_index=int(mem.get("cmd_index") or 0),
                        cmd_total=int(mem.get("cmd_total") or 0),
                        commands=cmds,
                        freeze_remain=freeze,
                    )
                    mem.update(eta)
                    mem["progress"] = pct
                    try:
                        from utils.run_progress_eta import format_estimated_end_time

                        mem["estimated_end_time"] = format_estimated_end_time(
                            float(eta.get("remain_s") or 0.0),
                            status=str(mem.get("status") or ""),
                        )
                    except Exception:
                        pass
                except Exception:
                    pass
    except Exception:
        mem = {}

    def _pick(*keys, default=None):
        for k in keys:
            if k in mem and mem[k] is not None and mem[k] != "":
                return mem[k]
            if k in project and project[k] is not None and project[k] != "":
                return project[k]
        return default

    status = str(_pick("status", default="未开始") or "未开始")
    project_name = str(_pick("project", "name", default="") or "")
    current_test = str(_pick("current_test", default=project_name) or project_name)
    snap: Dict[str, Any] = {
        "status": status,
        "project": project_name,
        "current_test": current_test,
        "progress": int(_pick("progress", default=0) or 0),
        "current_detail": str(_pick("current_detail", default="") or ""),
        "current_round": int(_pick("current_round", default=0) or 0),
        "total_rounds": int(_pick("total_rounds", default=0) or 0),
        "cmd_index": int(_pick("cmd_index", default=0) or 0),
        "cmd_total": int(_pick("cmd_total", default=0) or 0),
        "operator_pause": bool(_pick("operator_pause", default=False)),
        "queue": list(_pick("queue", default=[]) or []),
        "rounds": list(_pick("rounds", default=[]) or []),
        "planned_seconds": float(_pick("planned_seconds", default=0.0) or 0.0),
        "elapsed_s": float(_pick("elapsed_s", default=0.0) or 0.0),
        "remain_s": float(_pick("remain_s", default=0.0) or 0.0),
        "eta_total_s": float(_pick("eta_total_s", default=0.0) or 0.0),
        "planned_text": str(_pick("planned_text", default="") or ""),
        "elapsed_text": str(_pick("elapsed_text", default="") or ""),
        "remain_text": str(_pick("remain_text", default="") or ""),
        "eta_total_text": str(_pick("eta_total_text", default="") or ""),
    }
    ids = _resolve_job_ids()
    # status.json 里也可能已写
    if not ids.get("jobId") and project.get("jobId"):
        try:
            ids["jobId"] = int(project["jobId"])
        except (TypeError, ValueError):
            pass
    if not ids.get("experId") and project.get("experId"):
        try:
            ids["experId"] = int(project["experId"])
        except (TypeError, ValueError):
            pass
    if ids.get("jobId"):
        snap["jobId"] = ids["jobId"]
    if ids.get("experId"):
        snap["experId"] = ids["experId"]
    return snap


def snapshot_implies_busy(snap: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(snap, dict):
        return False
    st = str(snap.get("status") or "")
    if snap.get("operator_pause"):
        return True
    return st in ("进行中", "暂停")
