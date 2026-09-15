# -*- coding: utf-8 -*-
"""结案后要回传到 IOT 的本机文件。"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

from agent.job_inbox import result_path

_MAX_BYTES = 20 * 1024 * 1024
_MAX_FILES = 8


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


def collect_report_files(
    repo_root: Path,
    job_id: int,
    result: Dict[str, Any] | None = None,
) -> List[Path]:
    """收集结案附件：results JSON、status.json、结果里列出的路径。"""
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
