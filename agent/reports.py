# -*- coding: utf-8 -*-
"""结案后要回传到 IOT 的本机文件。"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from agent.job_inbox import result_path

_MAX_BYTES = 20 * 1024 * 1024
_MAX_FILES = 8
_RECENT_GLOBS = (
    "command_save_files/command_data/**/*.*",
    "command_save_files/dewetron_data/**/*.*",
    "command_save_files/analysis_reports/**/*.*",
    "data_logs/**/*.log",
    "data_logs/**/*.csv",
)
_RECENT_SUFFIXES = {".csv", ".xlsx", ".xls", ".docx", ".pdf", ".txt", ".log", ".json"}


def _as_paths(items: Iterable[Any], repo_root: Path) -> List[Path]:
    out: List[Path] = []
    for item in items or []:
        if isinstance(item, dict):
            raw = item.get("path") or item.get("file") or item.get("filename") or ""
        else:
            raw = item
        text = str(raw or "").strip()
        if not text:
            continue
        p = Path(text)
        if not p.is_absolute():
            p = repo_root / p
        out.append(p)
    return out


def _job_time_window(result: Dict[str, Any], result_file: Path) -> tuple[float, float]:
    """返回 (since_ts, until_ts)。优先用结果里的耗时；否则默认最近 2 小时。"""
    until = time.time()
    try:
        until = max(until, result_file.stat().st_mtime)
    except OSError:
        pass
    summary = result.get("result_summary") or result.get("resultSummary") or {}
    if not isinstance(summary, dict):
        summary = {}
    elapsed = summary.get("elapsed_sec")
    try:
        elapsed_f = float(elapsed)
    except (TypeError, ValueError):
        elapsed_f = 0.0
    if elapsed_f > 0:
        since = until - elapsed_f - 120.0  # 前后各留 2 分钟余量
    else:
        since = until - 2 * 3600.0
    return since, until + 60.0


def _recent_output_files(repo_root: Path, since_ts: float, until_ts: float) -> List[Path]:
    found: List[Path] = []
    for pattern in _RECENT_GLOBS:
        for path in repo_root.glob(pattern):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _RECENT_SUFFIXES and "dewetron" not in str(path).lower():
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if since_ts <= mtime <= until_ts:
                found.append(path)
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found


def collect_report_files(
    repo_root: Path,
    job_id: int,
    result: Dict[str, Any] | None = None,
) -> List[Path]:
    """收集结案附件：results JSON、status.json、显式路径、试验窗口内新产生的 CSV/日志。"""
    root = Path(repo_root)
    result = result or {}
    summary = result.get("result_summary") or result.get("resultSummary") or {}
    if not isinstance(summary, dict):
        summary = {}

    candidates: List[Path] = []
    rp = result_path(root, job_id)
    if rp.is_file():
        candidates.append(rp)
    status = root / "status.json"
    if status.is_file():
        candidates.append(status)
    listed = []
    for key in ("report_files", "reportFiles", "report_paths", "reportPaths"):
        val = summary.get(key) or result.get(key)
        if isinstance(val, list):
            listed.extend(val)
    candidates.extend(_as_paths(listed, root))

    since_ts, until_ts = _job_time_window(result, rp if rp.is_file() else root)
    candidates.extend(_recent_output_files(root, since_ts, until_ts))

    seen = set()
    files: List[Path] = []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.is_file():
            continue
        try:
            size = resolved.stat().st_size
        except OSError:
            continue
        if size <= 0 or size > _MAX_BYTES:
            continue
        seen.add(resolved)
        files.append(resolved)
        if len(files) >= _MAX_FILES:
            break
    return files
