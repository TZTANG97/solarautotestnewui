# -*- coding: utf-8 -*-
"""结案后要回传到 IOT 的本机文件。"""
from __future__ import annotations

import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from agent.job_inbox import result_path

_MAX_BYTES = 20 * 1024 * 1024
# Oxygen 原始录波常远超 20MB，单独放宽
_MAX_DMD_BYTES = 512 * 1024 * 1024
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
    ".dmd",
} | _IMAGE_SUFFIXES
def _is_config_snapshot(path: Path) -> bool:
    """任务/状态快照、命令队列：可上传到「参数配置」，不要当实验报告去扫目录。"""
    name = path.name.lower()
    if name in {"status.json"}:
        return True
    if name.startswith("job_") and name.endswith(".json"):
        return True
    if name.endswith(".csv") and "commands" in name:
        return True
    return False


def _is_junk_upload(path: Path) -> bool:
    """仪器配置 XML、结案 sidecar、无头元数据：根本不上传。"""
    name = path.name.lower()
    if name in {"headless_result.json", ".last_dew_export.json", "sim_plan.json"}:
        return True
    # Oxygen/德威创通道配置快照（dewetron_20261111_19.xml），不是试验报告
    if name.endswith(".xml") and name.startswith("dewetron_"):
        return True
    if name.endswith(".json") and (
        name.startswith(".")
        or "last_dew" in name
        or name == "headless_result.json"
    ):
        return True
    return False


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


def _unix_ts(value: Any) -> float:
    try:
        ts = float(value)
    except (TypeError, ValueError):
        return 0.0
    if ts > 1_000_000_000:
        return ts
    return 0.0


def _job_time_window(result: Dict[str, Any], result_file: Path) -> tuple[float, float]:
    """返回 (since_ts, until_ts)。优先用本单开始时刻，其次耗时，否则最近 2 小时。"""
    until = time.time()
    try:
        until = max(until, result_file.stat().st_mtime)
    except OSError:
        pass
    summary = result.get("result_summary") or result.get("resultSummary") or {}
    if not isinstance(summary, dict):
        summary = {}
    started = _unix_ts(summary.get("started_at") or summary.get("startedAt"))
    elapsed = summary.get("elapsed_sec")
    try:
        elapsed_f = float(elapsed)
    except (TypeError, ValueError):
        elapsed_f = 0.0
    if started > 0:
        since = started - 120.0
    elif elapsed_f > 0:
        since = until - elapsed_f - 120.0  # 前后各留 2 分钟余量
    else:
        since = until - 2 * 3600.0
    return since, until + 60.0


# 录波名尾部的 _HHMMSS，例如 Pdisp_BR_161912、FixedPF_P100_150316
_NAME_CLOCK_RE = re.compile(r"_(\d{6})$")


def _name_clock_in_window(path: Path, since_ts: float, until_ts: float) -> Optional[bool]:
    """文件名带时刻时，判断该时刻是否落在本单时间窗。没有时刻返回 None。"""
    match = _NAME_CLOCK_RE.search(path.stem)
    if match is None:
        return None
    hhmmss = match.group(1)
    hh, mm, ss = int(hhmmss[:2]), int(hhmmss[2:4]), int(hhmmss[4:6])
    if hh > 23 or mm > 59 or ss > 59:
        return None
    start_day = datetime.fromtimestamp(since_ts).date()
    end_day = datetime.fromtimestamp(until_ts).date()
    day = start_day
    while day <= end_day:
        clock = datetime.combine(day, datetime.min.time()) + timedelta(
            hours=hh, minutes=mm, seconds=ss
        )
        if since_ts <= clock.timestamp() <= until_ts:
            return True
        day += timedelta(days=1)
    return False


def _recording_family(path: Path) -> str:
    """去掉尾部 _HHMMSS，用来认出 Pdisp_BR.csv 和 Pdisp_BR_161912.csv 是同一路录波。"""
    match = _NAME_CLOCK_RE.search(path.stem)
    if match is None:
        return path.stem.lower()
    return path.stem[: match.start()].lower()


def _only_this_run_files(
    paths: List[Path],
    since_ts: float,
    until_ts: float,
    listed: Set[Path],
) -> List[Path]:
    """共享保存目录里，只留下本单时间窗内生成的录波。

    文件名自带 15:03 这类时刻、却被改过修改时间的旧 CSV，不能跟着本单一起上传。
    已经有 Pdisp_BR_161912.csv 时，不再带上没有时刻的 Pdisp_BR.csv。
    调用方点名的路径（结案清单）保持原样。
    """
    kept: List[Path] = []
    for path in paths:
        if path in listed or _is_config_snapshot(path):
            kept.append(path)
            continue
        if path.suffix.lower() in {".csv", ".dmd"}:
            in_window = _name_clock_in_window(path, since_ts, until_ts)
            if in_window is False:
                continue
        kept.append(path)
    families_with_clock = set()
    for path in kept:
        if path.suffix.lower() != ".csv":
            continue
        if _NAME_CLOCK_RE.search(path.stem):
            families_with_clock.add(_recording_family(path))
    if not families_with_clock:
        return kept
    narrowed: List[Path] = []
    for path in kept:
        if (
            path not in listed
            and path.suffix.lower() == ".csv"
            and _NAME_CLOCK_RE.search(path.stem) is None
            and _recording_family(path) in families_with_clock
        ):
            continue
        narrowed.append(path)
    return narrowed


def _match_recent_file(path: Path, since_ts: float, until_ts: float) -> bool:
    if not path.is_file():
        return False
    if _is_junk_upload(path) or _is_config_snapshot(path):
        return False
    # 只按后缀收；勿因路径含 dewetron 就把配置 XML 一并收进来
    if path.suffix.lower() not in _RECENT_SUFFIXES:
        return False
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return False
    if since_ts > mtime or mtime > until_ts:
        return False
    if path.suffix.lower() in {".csv", ".dmd"}:
        named = _name_clock_in_window(path, since_ts, until_ts)
        if named is False:
            return False
    return True


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


def _widget_save_dirs(result: Dict[str, Any] | None) -> List[Path]:
    """从结案摘要 widgets 取 WT SavePath / 德威创保存目录。"""
    out: List[Path] = []
    seen = set()

    def _add(path: Path) -> None:
        try:
            key = str(path.resolve())
        except OSError:
            key = str(path)
        if key in seen:
            return
        seen.add(key)
        out.append(path)

    if not isinstance(result, dict):
        return out
    summary = result.get("result_summary") or result.get("resultSummary") or {}
    if not isinstance(summary, dict):
        summary = {}
    widgets = summary.get("widgets") or result.get("widgets") or {}
    if not isinstance(widgets, dict):
        widgets = {}
    for key in (
        "textEdit_SavePath",
        "SavePath",
        "lineEdit_DEW_SaveDir",
        "lineEdit_DEW_SavePath",
    ):
        text = str(widgets.get(key) or "").strip()
        if not text:
            continue
        try:
            p = Path(text)
            if p.is_dir():
                _add(p)
            elif p.parent.is_dir():
                _add(p.parent)
        except OSError:
            pass
    # 德威创默认落 LOCALAPPDATA\\SolarAutoTest\\dewetron_save（中途停机 CSV 常在这）
    try:
        from utils.wt_save_path import default_dewetron_save_dir, default_wt_save_path

        for raw in (default_dewetron_save_dir(), default_wt_save_path()):
            p = Path(str(raw or ""))
            if p.is_dir():
                _add(p)
    except Exception:
        pass
    return out


def _flicker_image_roots(repo_root: Path, result: Dict[str, Any] | None = None) -> List[Path]:
    """闪变图实际目录：配置的 WT 保存路径，加上仓库内 wt_save / screenshots。"""
    roots: List[Path] = [repo_root / "wt_save", repo_root / "screenshots"]
    roots.extend(_widget_save_dirs(result))
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


def _keep_latest_token_csv(paths: List[Path], token: str) -> List[Path]:
    """连续录波同名多份时只留本轮那一份，避免把 SavePath 里的旧 CSV 都当成报告。"""
    token_l = str(token or "").strip().lower()
    if not token_l:
        return paths
    matched = [
        p
        for p in paths
        if p.suffix.lower() == ".csv" and token_l in p.name.lower()
    ]
    if len(matched) <= 1:
        return paths
    from utils.wt_csv_sigma_fill import recording_rank

    best = max(matched, key=recording_rank)
    try:
        best_key = best.resolve()
    except OSError:
        best_key = best
    drop = set()
    for path in matched:
        try:
            key = path.resolve()
        except OSError:
            key = path
        if key != best_key:
            drop.add(key)
    kept: List[Path] = []
    for path in paths:
        try:
            key = path.resolve()
        except OSError:
            key = path
        if key in drop:
            continue
        kept.append(path)
    return kept


def recording_token_for_test(test_name: str) -> str:
    """已知试验的连续录波文件名片段。对不上返回空，避免误收其它任务文件。"""
    raw = str(test_name or "").strip()
    if not raw:
        return ""
    try:
        from utils.wt_job_save import (
            CONTINUOUS_FILENAME_BY_TEST,
            _ALIASES,
            continuous_filename_for_test,
        )
    except Exception:
        low = raw.lower().replace(" ", "").replace("_", "")
        if low in {"动态qu", "dynamicqu"}:
            return "qu_dyn_curve"
        if low in {"静态qu", "staticqu"}:
            return "qu_curve"
        return ""
    low = raw.lower().replace(" ", "").replace("_", "")
    canon = _ALIASES.get(raw) or _ALIASES.get(low) or low
    if canon not in CONTINUOUS_FILENAME_BY_TEST and low not in CONTINUOUS_FILENAME_BY_TEST:
        if low in {"动态qu", "dynamicqu"}:
            return "qu_dyn_curve"
        if low in {"静态qu", "staticqu"}:
            return "qu_curve"
        # 德威创无功能力常写成 reactive-qcap_*.csv
        if "qcap" in low or low in {"无功能力范围", "无功能力"}:
            return "qcap"
        return ""
    name = str(continuous_filename_for_test(raw) or "").strip().lower()
    if not name or name == "record_br":
        return ""
    # 实际文件是 OVUF_Volt_BR / OVUF_Freq_BR / OVUF_S3_…，整词 ovuf_br 对不上。
    if name == "ovuf_br" or name.startswith("ovuf"):
        return "ovuf"
    # QCap_BR / reactive-qcap 都能被 "qcap" 命中
    if "qcap" in name.replace("_", "").replace("-", ""):
        return "qcap"
    return name


def window_output_files_by_token(
    repo_root: Path,
    since_ts: float,
    until_ts: float,
    *,
    name_token: str,
    result: Dict[str, Any] | None = None,
) -> List[Path]:
    """时间窗内、文件名含 token 的录波（含 wt_save / 界面 SavePath）。"""
    token = str(name_token or "").strip().lower()
    if not token:
        return []
    found: List[Path] = []
    root = Path(repo_root)

    def _named(path: Path) -> bool:
        return token in path.name.lower()

    for pattern in _RECENT_GLOBS:
        for path in root.glob(pattern):
            if _named(path) and _match_recent_file(path, since_ts, until_ts):
                found.append(path)
    for folder in _flicker_image_roots(root, result):
        if not folder.is_dir():
            continue
        for path in folder.glob("**/*"):
            if not path.is_file() or not _named(path):
                continue
            if path.suffix.lower() not in _RECENT_SUFFIXES:
                continue
            if _match_recent_file(path, since_ts, until_ts):
                found.append(path)
    return found


def _flicker_images(
    repo_root: Path,
    since_ts: float,
    until_ts: float,
    *,
    result: Dict[str, Any] | None = None,
) -> List[Path]:
    """只收 [since, until] 内的图片。调用方在没有 elapsed_sec 时不要调用。"""
    found: List[Path] = []
    for folder in _flicker_image_roots(repo_root, result):
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
    listed_paths = _as_paths(listed, root)
    candidates.extend(listed_paths)
    listed_resolved: Set[Path] = set()
    for path in listed_paths:
        try:
            listed_resolved.add(path.resolve())
        except OSError:
            continue

    since_ts, until_ts = _job_time_window(result, rp if rp.is_file() else root)
    prefer_raw = summary.get("analysis_input_dir") or summary.get("analysisInputDir")
    prefer_dir = Path(str(prefer_raw)) if prefer_raw else None
    if prefer_dir and not prefer_dir.is_absolute():
        prefer_dir = root / prefer_dir
    # 无 analysis_input_dir 时，优先扫界面 SavePath（OVUF 等常写到 D:\xiebodianliu_test）
    if prefer_dir is None or not prefer_dir.exists():
        for save_dir in _widget_save_dirs(result):
            prefer_dir = save_dir
            break
    candidates.extend(
        _recent_output_files(
            root,
            since_ts,
            until_ts,
            job_id=int(job_id) if job_id is not None else None,
            prefer_dir=prefer_dir if prefer_dir and prefer_dir.exists() else None,
        )
    )
    # SavePath 可能不在 job 目录：即使有 job_id 也再扫一遍 SavePath
    for save_dir in _widget_save_dirs(result):
        candidates.extend(
            _recent_output_files(
                root,
                since_ts,
                until_ts,
                job_id=None,
                prefer_dir=save_dir,
            )
        )
    try:
        elapsed_img = float(summary.get("elapsed_sec") or 0)
    except (TypeError, ValueError):
        elapsed_img = 0.0
    if elapsed_img > 0:
        now_img = time.time()
        candidates.extend(
            _flicker_images(
                root, now_img - elapsed_img, now_img + 5.0, result=result
            )
        )

    tt = str(summary.get("testType") or summary.get("test_type") or "").lower()
    # 连续录波常落在 wt_save / SavePath（OVUF_BR.csv 等），job 目录扫不到时按试验名 token 补扫
    token = recording_token_for_test(
        str(
            summary.get("testType")
            or summary.get("test_type")
            or summary.get("current_test")
            or ""
        )
    )
    if not token:
        # 文件名列表里常有 OVUF_BR：无映射时仍按 ovuf 扫
        fn_list = ""
        widgets = summary.get("widgets") if isinstance(summary.get("widgets"), dict) else {}
        if isinstance(widgets, dict):
            fn_list = str(widgets.get("textEdit_FileNameList") or "").lower()
        if "ovuf" in fn_list:
            token = "ovuf"
    if token and (elapsed_img > 0 or since_ts > 0):
        candidates.extend(
            window_output_files_by_token(
                root,
                since_ts,
                until_ts,
                name_token=token,
                result=result,
            )
        )
    drop_overload = tt in ("harmonic", "harmonics", "harmonic_current", "谐波", "谐波电流", "谐波电流测试")

    def _keep(path: Path) -> bool:
        if _is_junk_upload(path):
            return False
        name_l = path.name.lower()
        if drop_overload and (
            name_l.startswith("sample_overload") or name_l == "sim_plan.json"
        ):
            return False
        try:
            size = path.stat().st_size
        except OSError:
            return False
        if size <= 0:
            return False
        limit = _MAX_DMD_BYTES if path.suffix.lower() == ".dmd" else _MAX_BYTES
        return size <= limit

    def _priority(path: Path) -> tuple:
        name_l = path.name.lower()
        suf = path.suffix.lower()
        if _is_config_snapshot(path):
            return (9, name_l)
        # 数据处理报告 / 录波优先
        if suf in {".xlsx", ".xls", ".docx", ".pdf"}:
            return (0, name_l)
        if token and token in name_l:
            return (1, name_l)
        if suf in {".csv", ".dmd"}:
            return (2, name_l)
        if suf in _IMAGE_SUFFIXES:
            return (3, name_l)
        return (4, name_l)

    resolved_list: List[Path] = []
    seen = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.is_file() or not _keep(resolved):
            continue
        seen.add(resolved)
        resolved_list.append(resolved)
    resolved_list = _only_this_run_files(
        resolved_list, since_ts, until_ts, listed_resolved
    )
    resolved_list = _keep_latest_token_csv(resolved_list, token)
    resolved_list.sort(key=_priority)
    return resolved_list[:_MAX_FILES]
