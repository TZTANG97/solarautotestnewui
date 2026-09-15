# -*- coding: utf-8 -*-
"""云任务落盘目录：供 Agent / 日后 UI 交接。"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


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


def wait_result(
    repo_root: Path,
    job_id: int,
    *,
    timeout_sec: float = 3600,
    poll_sec: float = 2.0,
    on_progress=None,
) -> Optional[Dict[str, Any]]:
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
