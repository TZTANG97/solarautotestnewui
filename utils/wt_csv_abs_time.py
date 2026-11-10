# -*- coding: utf-8 -*-
"""WT CSV 绝对时间列，对齐德威创 Abs Time 格式。

德威创导出：``Abs Time,Time [s],...``，单元格形如 ``2025/12/17 16:58:07.971``。
WT Soft Panel / SCPI 原本只有相对 ``Time [s]``；用开录墙钟 + 相对秒回填 Abs Time。
"""
from __future__ import annotations

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional


ABS_HEADER = "Abs Time"
TIME_HEADERS = ("time [s]", "time[s]", "time (s)", "time")


def format_wall_time_for_csv(unix_ts: float) -> str:
    """墙钟 → 与德威创 ``format_abs_time_for_csv`` 同风格的 Excel 友好串。"""
    try:
        ts = float(unix_ts)
    except (TypeError, ValueError):
        return ""
    if ts <= 0:
        return ""
    dt = datetime.fromtimestamp(ts)
    ms = int(dt.microsecond / 1000)
    return dt.strftime("%Y/%m/%d %H:%M:%S") + f".{ms:03d}"


def _time_col_index(header: List[str]) -> int:
    for i, name in enumerate(header):
        if str(name or "").strip().casefold() in TIME_HEADERS:
            return i
    return -1


def inject_abs_time_column(
    csv_path: str | Path,
    gather_start_unix: float,
    *,
    force: bool = False,
) -> bool:
    """在 Time [s] 前插入 Abs Time；已有同名列且非 force 则跳过。

    Abs Time = gather_start_unix + 该行相对秒。
    """
    path = Path(csv_path)
    if not path.is_file():
        return False
    try:
        start = float(gather_start_unix)
    except (TypeError, ValueError):
        return False
    if start <= 0:
        return False
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
    except OSError:
        return False
    if len(rows) < 1:
        return False
    header = [str(c) for c in rows[0]]
    has_abs = bool(header) and str(header[0]).strip().casefold() in (
        "abs time",
        "abs_time",
        "absolute time",
    )
    time_idx = _time_col_index(header)
    if time_idx < 0:
        return False
    if has_abs and not force:
        return False

    # 重建：Abs Time + 原表（若已有 Abs Time 则替换首列）
    if has_abs:
        body_header = header[1:]
        body_rows = [r[1:] if len(r) > 1 else [] for r in rows[1:]]
        # time 列在去掉 Abs 后的下标
        time_idx_body = time_idx - 1
    else:
        body_header = header
        body_rows = [list(r) for r in rows[1:]]
        time_idx_body = time_idx

    if time_idx_body < 0 or time_idx_body >= len(body_header):
        return False

    new_rows: List[List[str]] = [[ABS_HEADER] + list(body_header)]
    for r in body_rows:
        while len(r) < len(body_header):
            r.append("")
        rel_raw = r[time_idx_body] if time_idx_body < len(r) else ""
        try:
            rel = float(str(rel_raw).strip() or "nan")
        except ValueError:
            rel = float("nan")
        if rel == rel:  # not NaN
            abs_cell = format_wall_time_for_csv(start + rel)
        else:
            abs_cell = ""
        new_rows.append([abs_cell] + list(r))

    tmp = path.with_suffix(path.suffix + ".abs.tmp")
    try:
        with open(tmp, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows(new_rows)
        os.replace(tmp, path)
    except OSError:
        try:
            if tmp.is_file():
                tmp.unlink()
        except OSError:
            pass
        return False
    return True


def inject_abs_time_in_dirs(
    dirs: Iterable[str | Path],
    gather_start_unix: float,
    *,
    name_hint: str = "",
    limit: int = 8,
) -> List[str]:
    """对保存目录内最近 CSV 注入 Abs Time。"""
    hint = str(name_hint or "").strip().lower()
    cands: List[Path] = []
    for d in dirs:
        root = Path(d) if d else None
        if root is None or not root.is_dir():
            continue
        try:
            for p in root.glob("*.csv"):
                if not p.is_file():
                    continue
                if hint and hint not in p.name.lower():
                    continue
                cands.append(p)
        except OSError:
            continue
    cands.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    done: List[str] = []
    for p in cands[: max(1, int(limit))]:
        try:
            if inject_abs_time_column(p, gather_start_unix):
                done.append(str(p))
        except Exception:
            continue
    return done
