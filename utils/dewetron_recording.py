# -*- coding: utf-8 -*-
"""DEWETRON 录波：连续录（单 START/STOP）与分文件（每段采集一对 START/STOP）。"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Sequence, Tuple

from dewetron_autotest import (
    DEWETRON_DEVICE,
    DEWETRON_START_COMMAND,
    DEWETRON_STOP_COMMAND,
    WAIT_ACTION,
    make_command_row,
)
from utils.dew_catalog_sync import get_dew_acq_command
from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT


# Measure dwells are typically many seconds; skip tiny AC gap waits.
_MIN_MEASURE_WAIT_01S = 20


def _wait_01s(row: Sequence[Any]) -> int:
    if len(row) <= 9:
        return 0
    val = row[9]
    if val in ("", None):
        val = row[8] if len(row) > 8 else 0
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def is_measure_wait_row(row: Sequence[Any], *, min_01s: int = _MIN_MEASURE_WAIT_01S) -> bool:
    """True for executor wait rows that represent a measurement dwell."""
    if not row:
        return False
    if str(row[1]).strip().lower() != WAIT_ACTION:
        return False
    return _wait_01s(row) >= int(min_01s)


def make_acq_start_row() -> List[Any]:
    cmd = get_dew_acq_command("start", DEWETRON_START_COMMAND)
    return make_command_row(DEWETRON_DEVICE, "write", cmd)


def make_acq_stop_row() -> List[Any]:
    cmd = get_dew_acq_command("stop", DEWETRON_STOP_COMMAND)
    return make_command_row(DEWETRON_DEVICE, "write", cmd)


def _is_dew_start_row(row: Sequence[Any]) -> bool:
    if not row or len(row) < 3:
        return False
    if str(row[0]).strip().upper() != DEWETRON_DEVICE:
        return False
    cmd = str(row[2] or "").strip().upper()
    return DEWETRON_START_COMMAND.upper() in cmd or cmd.endswith("ACQUISITION:START")


def _is_dew_stop_row(row: Sequence[Any]) -> bool:
    if not row or len(row) < 3:
        return False
    if str(row[0]).strip().upper() != DEWETRON_DEVICE:
        return False
    cmd = str(row[2] or "").strip().upper()
    return DEWETRON_STOP_COMMAND.upper() in cmd or cmd.endswith("ACQUISITION:STOP")


def ensure_dewetron_acq_boundaries(
    rows: Sequence[Sequence[Any]],
    *,
    force_start: bool = True,
    force_stop: bool = True,
) -> List[List[Any]]:
    """兼容路径（闪变/谐波）兜底：缺 START/STOP 时补上，避免空 CSV。"""
    out = [list(row) for row in rows]
    has_start = any(_is_dew_start_row(r) for r in out)
    has_stop = any(_is_dew_stop_row(r) for r in out)
    if force_start and not has_start:
        out.insert(0, make_acq_start_row())
        has_start = True
    if force_stop and not has_stop:
        out.append(make_acq_stop_row())
    return out


def apply_dewetron_recording_boundaries(
    rows: Sequence[Sequence[Any]],
    *,
    continuous: bool = True,
    min_measure_01s: int = _MIN_MEASURE_WAIT_01S,
) -> List[List[Any]]:
    """Insert DEWETRON START/STOP according to continuous vs split recording.

    - continuous: prefer existing START/STOP (from ASYNC_START/WAIT_END 对齐);
      otherwise one START at head and one STOP at tail.
    - split: START/STOP around each measure wait row; if none found, fall back
      to continuous wrapping so the segment still records.
    """
    source = [list(row) for row in rows]
    start_row = make_acq_start_row()
    stop_row = make_acq_stop_row()
    if continuous or not source:
        has_start = any(_is_dew_start_row(r) for r in source)
        has_stop = any(_is_dew_stop_row(r) for r in source)
        if has_start:
            out = list(source)
            if not has_stop:
                out.append(list(stop_row))
            return out
        return [start_row, *source, stop_row]

    out: List[List[Any]] = []
    wrapped = 0
    for row in source:
        if is_measure_wait_row(row, min_01s=min_measure_01s):
            out.append(list(start_row))
            out.append(row)
            out.append(list(stop_row))
            wrapped += 1
        else:
            out.append(row)
    if wrapped == 0:
        return [start_row, *source, stop_row]
    return out




def _is_nan_number(value: Any) -> bool:
    try:
        return math.isnan(float(value))
    except (TypeError, ValueError):
        text = str(value or "").strip().lower()
        return text in {"nan", "null", "none", ""}


def row_values_all_nan(values: Sequence[Any]) -> bool:
    """True when every channel value is missing/NaN (leading empty Dewetron samples)."""
    if not values:
        return True
    return all(_is_nan_number(v) for v in values)


def trim_leading_all_nan_samples(
    rows: Sequence[Tuple[Any, Sequence[Any]]],
    *,
    rebase_time: bool = True,
) -> List[Tuple[float, List[float]]]:
    """Drop leading rows where all channels are NaN; optionally rebase time to 0 at first keep.

    Dewetron often emits ~0.3–0.5s of empty samples right after ACQUISITION:START.
    """
    source = list(rows or [])
    start = 0
    while start < len(source):
        _t, vals = source[start]
        if not row_values_all_nan(vals or []):
            break
        start += 1
    kept = source[start:]
    out: List[Tuple[float, List[float]]] = []
    if not kept:
        return out
    # Only rebase when we actually dropped leading empties (preserve absolute t otherwise).
    t0 = 0.0
    if rebase_time and start > 0:
        try:
            t0 = float(kept[0][0])
        except (TypeError, ValueError):
            t0 = 0.0
    for raw_t, vals in kept:
        try:
            tt = float(raw_t) - t0
        except (TypeError, ValueError):
            tt = 0.0
        nums: List[float] = []
        for v in list(vals or []):
            try:
                nums.append(float(v))
            except (TypeError, ValueError):
                nums.append(float("nan"))
        out.append((tt, nums))
    return out


def resolve_dewetron_save_paths(
    *,
    test_type: str,
    continuous: bool,
    file_names: Optional[Sequence[str]] = None,
    stamp: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> List[str]:
    """Build CSV paths under the configured DEWETRON save directory."""
    import os
    import time

    from utils.wt_save_path import ensure_dewetron_save_dir

    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    base = ensure_dewetron_save_dir(base_dir)
    names = [str(n).strip() for n in (file_names or []) if str(n).strip()]
    if continuous or not names:
        safe = (names[0] if names else test_type or "dewetron").replace("/", "_")
        return [os.path.join(base, f"{safe}_{stamp}.csv")]
    paths = []
    for idx, name in enumerate(names, start=1):
        safe = name.replace("/", "_")
        paths.append(os.path.join(base, f"{safe}_{stamp}_{idx:02d}.csv"))
    return paths


def normalize_record_mode(mode: Any) -> str:
    text = str(mode or "").strip().lower()
    if text in {MODE_SPLIT, "1", "split", "multi", "分文件", "分开录"}:
        return MODE_SPLIT
    return MODE_CONTINUOUS
