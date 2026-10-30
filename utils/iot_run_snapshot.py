# -*- coding: utf-8 -*-
"""从 status.json / 本机状态组装 IOT heartbeat.runSnapshot。"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

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
        "updated_at": str(_pick("updated_at", default="") or ""),
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


def heartbeat_should_push_progress(status: str) -> bool:
    """待开始/未开始不能写回云任务，否则本机追加会把上一单进度打回 0。"""
    return str(status or "").strip() in ("进行中", "暂停")


def snapshot_implies_busy(snap: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(snap, dict):
        return False
    st = str(snap.get("status") or "")
    if snap.get("operator_pause"):
        return True
    return st in ("进行中", "暂停")


# 锁文件丢了，但 status.json 仍在被桌面刷新时，不要把活着的试验收成已中止。
# 静态 Cos 连续录 / WT 宏等待可以远长于单点驻留，进度落盘若只靠命令边界，
# 3 分钟就会把正在跑的局收成已中止（任务 58：进度停在 2%）。
# 长等待里另有 touch_running_project 每 10 秒刷新；这里只收真正死掉的局。
UNLOCKED_STALE_MAX_AGE_SEC = 600.0
UNLOCKED_STALE_DETAIL = "本机无试验占用，收口陈旧进行中状态"
_last_touch_mono = 0.0


def activity_age_sec(
    snap: Optional[Dict[str, Any]],
    *,
    file_mtime: Optional[float] = None,
    now: Optional[float] = None,
) -> Optional[float]:
    """桌面最后一次写试验进度距今秒数。没有时间戳时退回文件 mtime。"""
    now_ts = time.time() if now is None else float(now)
    raw = ""
    if isinstance(snap, dict):
        raw = str(snap.get("updated_at") or "").strip()
    if raw:
        try:
            ts = time.mktime(time.strptime(raw, "%Y-%m-%d %H:%M:%S"))
            return max(0.0, now_ts - ts)
        except (TypeError, ValueError, OverflowError):
            pass
    if file_mtime:
        try:
            return max(0.0, now_ts - float(file_mtime))
        except (TypeError, ValueError):
            return None
    return None


def apply_unlocked_stale_policy(
    snap: Optional[Dict[str, Any]],
    *,
    busy: bool,
    owner: str,
    file_mtime: Optional[float] = None,
    now: Optional[float] = None,
    max_age_sec: float = UNLOCKED_STALE_MAX_AGE_SEC,
) -> Tuple[Optional[Dict[str, Any]], bool]:
    """
    锁还在，或进度刚写过：这局还在跑，心跳报 busy，不要改成已中止。
    锁空着且进度久未更新：才把内存快照收成已中止，供心跳结案。
    返回 (快照, busy)。
    """
    if not isinstance(snap, dict) or not snapshot_implies_busy(snap):
        return snap, busy
    owner_l = str(owner or "").strip().lower()
    if busy or owner_l in ("ui", "agent"):
        return snap, True
    age = activity_age_sec(snap, file_mtime=file_mtime, now=now)
    if age is not None and age < float(max_age_sec):
        return snap, True
    out = dict(snap)
    out["status"] = "已中止"
    out["operator_pause"] = False
    out["remain_text"] = ""
    out["remain_s"] = 0.0
    out["current_detail"] = UNLOCKED_STALE_DETAIL
    return out, False


def desktop_run_still_active(
    status_json_path: Optional[str] = None,
    *,
    now: Optional[float] = None,
    max_age_sec: float = UNLOCKED_STALE_MAX_AGE_SEC,
) -> bool:
    """status.json 仍是进行中/暂停，且最近仍有进度写入。Agent 此时不要再领下一单。"""
    path = _status_json_path(status_json_path)
    snap = build_run_snapshot_from_status(str(path))
    if not snapshot_implies_busy(snap):
        return False
    mtime = None
    try:
        if path.is_file():
            mtime = path.stat().st_mtime
    except OSError:
        mtime = None
    age = activity_age_sec(snap, file_mtime=mtime, now=now)
    if age is None:
        return False
    return age < float(max_age_sec)


def persist_coerced_terminal(status_json_path: str, snap: Dict[str, Any]) -> None:
    """把心跳收口写回 status.json，避免文件一直停在「进行中」把下一单带进停机。"""
    path = Path(status_json_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    proj = data.get("project")
    if not isinstance(proj, dict):
        proj = {}
    proj = dict(proj)
    proj["status"] = "已中止"
    proj["operator_pause"] = False
    proj["remain_text"] = ""
    proj["remain_s"] = 0.0
    proj["estimated_end_time"] = ""
    detail = str((snap or {}).get("current_detail") or UNLOCKED_STALE_DETAIL)
    proj["current_detail"] = detail
    if snap.get("progress") is not None:
        try:
            proj["progress"] = int(snap.get("progress") or 0)
        except (TypeError, ValueError):
            pass
    proj["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    data["project"] = proj
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def touch_running_project(*, min_interval_sec: float = 10.0) -> None:
    """测量/宏等待循环里调用。10 秒内只写一次 updated_at。"""
    global _last_touch_mono
    now = time.monotonic()
    if now - _last_touch_mono < float(min_interval_sec):
        return
    _last_touch_mono = now
    touch_project_activity()


def touch_project_activity(status_json_path: Optional[str] = None) -> None:
    """长驻留期间刷新 updated_at，避免心跳把正在跑的试验当成陈旧进行中。"""
    path = _status_json_path(status_json_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except Exception:
        return
    if not isinstance(data, dict):
        return
    proj = data.get("project")
    if not isinstance(proj, dict):
        return
    if str(proj.get("status") or "").strip() not in ("进行中", "暂停"):
        return
    proj = dict(proj)
    proj["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    data["project"] = proj
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return
