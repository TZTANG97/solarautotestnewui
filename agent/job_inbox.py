# -*- coding: utf-8 -*-
"""云任务落盘目录：供 Agent / 日后 UI 交接。"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def inbox_root(repo_root: Path) -> Path:
    return repo_root / "iot_job_inbox"


def write_pending_job(repo_root: Path, job: Dict[str, Any]) -> Path:
    root = inbox_root(repo_root)
    pending = root / "pending"
    pending.mkdir(parents=True, exist_ok=True)
    job_id = int(job.get("id") or 0)
    path = pending / f"job_{job_id}.json"
    payload = {
        "job": job,
        "written_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def result_path(repo_root: Path, job_id: int) -> Path:
    d = inbox_root(repo_root) / "results"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"job_{int(job_id)}.json"


def progress_path(repo_root: Path, job_id: int) -> Path:
    d = inbox_root(repo_root) / "progress"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"job_{int(job_id)}.json"


def write_progress(
    repo_root: Path,
    job_id: int,
    *,
    percent: int = 0,
    text: str = "",
    step: str = "",
) -> Path:
    path = progress_path(repo_root, job_id)
    payload = {
        "percent": max(0, min(100, int(percent or 0))),
        "text": str(text or ""),
        "step": str(step or ""),
        "written_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_progress(repo_root: Path, job_id: int) -> Optional[Dict[str, Any]]:
    path = progress_path(repo_root, job_id)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def write_result(repo_root: Path, job_id: int, result: Dict[str, Any]) -> Path:
    path = result_path(repo_root, job_id)
    payload = dict(result)
    payload["written_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def stop_requests_dir(repo_root: Path) -> Path:
    d = inbox_root(repo_root) / "stop_requests"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_stop_request(repo_root: Path, job_id: int, reason: str = "") -> Path:
    """写入远程停机请求，供 UI handoff 扫描后按关电源规则结束试验。"""
    d = stop_requests_dir(repo_root)
    jid = int(job_id)
    path = d / f"job_{jid}.json"
    payload = {
        "job_id": jid,
        "reason": str(reason or ""),
        "written_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def list_stop_requests(repo_root: Path) -> List[Dict[str, Any]]:
    d = inbox_root(repo_root) / "stop_requests"
    if not d.is_dir():
        return []
    out: List[Dict[str, Any]] = []
    for path in sorted(d.glob("job_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if "job_id" not in data:
            try:
                data = dict(data)
                data["job_id"] = int(path.stem.split("_", 1)[1])
            except (IndexError, ValueError):
                pass
        data["_path"] = str(path)
        out.append(data)
    return out


def _superseded_path(repo_root: Path) -> Path:
    return inbox_root(repo_root) / "superseded_jobs.json"


def remember_superseded_job(repo_root: Path, job_id: int) -> None:
    """记下已被新开试验替换的任务号。Agent 与界面进程都读这个文件。"""
    try:
        jid = int(job_id)
    except (TypeError, ValueError):
        return
    if jid <= 0:
        return
    path = _superseded_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    ids: List[int] = []
    if path.is_file():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                for item in raw:
                    try:
                        n = int(item)
                    except (TypeError, ValueError):
                        continue
                    if n > 0 and n not in ids:
                        ids.append(n)
        except (OSError, ValueError, json.JSONDecodeError):
            ids = []
    if jid not in ids:
        ids.append(jid)
    path.write_text(json.dumps(ids[-40:]), encoding="utf-8")


def is_superseded_job(repo_root: Path, job_id: int) -> bool:
    try:
        jid = int(job_id)
    except (TypeError, ValueError):
        return False
    if jid <= 0:
        return False
    path = _superseded_path(repo_root)
    if not path.is_file():
        return False
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    if not isinstance(raw, list):
        return False
    for item in raw:
        try:
            if int(item) == jid:
                return True
        except (TypeError, ValueError):
            continue
    return False


def ack_stop_request(repo_root: Path, job_id: int) -> bool:
    """确认已处理停机请求：移到 stop_requests/done/，不存在则返回 False。"""
    d = inbox_root(repo_root) / "stop_requests"
    path = d / f"job_{int(job_id)}.json"
    if not path.is_file():
        return False
    done = d / "done"
    done.mkdir(parents=True, exist_ok=True)
    dest = done / path.name
    try:
        if dest.exists():
            dest.unlink()
        shutil.move(str(path), str(dest))
        return True
    except OSError:
        try:
            path.unlink()
            return True
        except OSError:
            return False


def wait_result(
    repo_root: Path,
    job_id: int,
    *,
    timeout_sec: float = 3600,
    poll_sec: float = 2.0,
    on_progress=None,
    abort_check: Optional[Callable[[], Optional[str]]] = None,
) -> Optional[Dict[str, Any]]:
    """轮询 results；可选 abort_check 返回非空原因时提前返回远程中止哨兵。"""
    path = result_path(repo_root, job_id)
    deadline = time.time() + max(1.0, timeout_sec)
    last_prog_key = None
    while time.time() < deadline:
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return data
            except (OSError, ValueError, json.JSONDecodeError):
                pass
        if callable(abort_check):
            try:
                reason = abort_check()
            except Exception:
                reason = None
            if reason:
                return {
                    "status": "aborted",
                    "fail_reason": str(reason),
                    "_remote_abort": True,
                }
        if callable(on_progress):
            prog = read_progress(repo_root, job_id)
            if prog:
                key = (prog.get("percent"), prog.get("text"), prog.get("step"))
                if key != last_prog_key:
                    last_prog_key = key
                    try:
                        on_progress(
                            int(prog.get("percent") or 0),
                            str(prog.get("text") or ""),
                            str(prog.get("step") or "handoff"),
                        )
                    except Exception:
                        pass
        time.sleep(poll_sec)
    return None
