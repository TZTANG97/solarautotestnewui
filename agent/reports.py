# -*- coding: utf-8 -*-
"""结案后要回传到 IOT 的本机文件。"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from agent.job_inbox import result_path

_MAX_BYTES = 20 * 1024 * 1024
_MAX_FILES = 48
_RECENT_GLOBS = (
    "command_save_files/command_data/**/*.*",
    "command_save_files/dewetron_data/**/*.*",
    "command_save_files/analysis_reports/**/*.*",
    "data_logs/**/*.log",
    "data_logs/**/*.csv",
)
_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
_RECENT_SUFFIXES = {
    ".csv",
    ".xlsx",
    ".xls",
    ".docx",
    ".pdf",
    ".txt",
    ".log",
    ".json",
} | _IMAGE_SUFFIXES


def _job_scoped_globs(job_id: int) -> tuple[str, ...]:
    """优先只扫本任务目录，避免把别的 sim_job 的过载 CSV 误收进来。"""
    jid = int(job_id)
    return (
        f"command_save_files/command_data/sim_job_{jid}/**/*.*",
        f"command_save_files/command_data/job_{jid}/**/*.*",
        f"command_save_files/analysis_reports/job_{jid}*/**/*.*",
        f"command_save_files/dewetron_data/**/job_{jid}*/**/*.*",
    )


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


def _match_recent_file(path: Path, since_ts: float, until_ts: float) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() not in _RECENT_SUFFIXES and "dewetron" not in str(path).lower():
        return False
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return False
    return since_ts <= mtime <= until_ts


def _recent_output_files(
    repo_root: Path,
    since_ts: float,
    until_ts: float,
    *,
    job_id: int | None = None,
    prefer_dir: Path | None = None,
) -> List[Path]:
    found: List[Path] = []
    # Path.glob 不接受绝对模式；prefer_dir 单独扫
    if prefer_dir is not None and prefer_dir.is_dir():
        for path in prefer_dir.glob("**/*.*"):
            if _match_recent_file(path, since_ts, until_ts):
                found.append(path)
    patterns: List[str] = []
    if job_id is not None:
        # 只扫本任务目录，避免把其它 job 的报告一起上传
        patterns.extend(_job_scoped_globs(job_id))
    elif prefer_dir is None:
        patterns.extend(_RECENT_GLOBS)
    seen_pat = set()
    root = Path(repo_root)
    for pattern in patterns:
        if pattern in seen_pat:
            continue
        seen_pat.add(pattern)
        # 仅相对模式交给 repo_root.glob
        if Path(pattern).is_absolute():
            continue
        for path in root.glob(pattern):
            if _match_recent_file(path, since_ts, until_ts):
                found.append(path)
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found


def _flicker_image_roots(repo_root: Path) -> List[Path]:
    """闪变图实际目录：配置的 WT 保存路径，加上仓库内 wt_save / screenshots。"""
    roots: List[Path] = [repo_root / "wt_save", repo_root / "screenshots"]
    try:
        from utils.wt_save_path import default_wt_save_path, resolve_config_wt_save_path

        roots.append(Path(default_wt_save_path()))
        roots.append(Path(resolve_config_wt_save_path()))
    except Exception:
        pass
    uniq: List[Path] = []
    seen = set()
    for p in roots:
        try:
            key = str(p.resolve()).lower()
        except OSError:
            key = str(p).lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq


def _flicker_images(repo_root: Path, since_ts: float, until_ts: float) -> List[Path]:
    """只收 [since, until] 内的图片。调用方在没有 elapsed_sec 时不要调用。"""
    found: List[Path] = []
    for folder in _flicker_image_roots(repo_root):
        if not folder.is_dir():
            continue
        for path in folder.glob("**/*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _IMAGE_SUFFIXES:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if since_ts <= mtime <= until_ts:
                found.append(path)
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
    prefer_raw = summary.get("analysis_input_dir") or summary.get("analysisInputDir")
    prefer_dir = Path(str(prefer_raw)) if prefer_raw else None
    if prefer_dir and not prefer_dir.is_absolute():
        prefer_dir = root / prefer_dir
    candidates.extend(
        _recent_output_files(
            root,
            since_ts,
            until_ts,
            job_id=int(job_id) if job_id is not None else None,
            prefer_dir=prefer_dir if prefer_dir and prefer_dir.exists() else None,
        )
    )
    try:
        elapsed_img = float(summary.get("elapsed_sec") or 0)
    except (TypeError, ValueError):
        elapsed_img = 0.0
    if elapsed_img > 0:
        now_img = time.time()
        candidates.extend(_flicker_images(root, now_img - elapsed_img, now_img + 5.0))

    tt = str(summary.get("testType") or summary.get("test_type") or "").lower()
    drop_overload = tt in ("harmonic", "harmonics", "harmonic_current", "谐波", "谐波电流", "谐波电流测试")

    seen = set()
    files: List[Path] = []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.is_file():
            continue
        name_l = resolved.name.lower()
        if drop_overload and (
            name_l.startswith("sample_overload") or name_l == "sim_plan.json"
        ):
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
