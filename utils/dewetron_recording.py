# -*- coding: utf-8 -*-
"""DEWETRON 录波：连续录（单 START/STOP）与分文件（每段采集一对 START/STOP）。"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence

from dewetron_autotest import (
    DEWETRON_DEVICE,
    DEWETRON_START_COMMAND,
    DEWETRON_STOP_COMMAND,
    WAIT_ACTION,
    make_command_row,
)
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
    return make_command_row(DEWETRON_DEVICE, "write", DEWETRON_START_COMMAND)


def make_acq_stop_row() -> List[Any]:
    return make_command_row(DEWETRON_DEVICE, "write", DEWETRON_STOP_COMMAND)


def apply_dewetron_recording_boundaries(
    rows: Sequence[Sequence[Any]],
    *,
    continuous: bool = True,
    min_measure_01s: int = _MIN_MEASURE_WAIT_01S,
) -> List[List[Any]]:
    """Insert DEWETRON START/STOP according to continuous vs split recording.

    - continuous: one START at head, one STOP at tail (whole segment).
    - split: START/STOP around each measure wait row; if none found, fall back
      to continuous wrapping so the segment still records.
    """
    source = [list(row) for row in rows]
    start_row = make_acq_start_row()
    stop_row = make_acq_stop_row()
    if continuous or not source:
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


def resolve_dewetron_save_paths(
    *,
    test_type: str,
    continuous: bool,
    file_names: Optional[Sequence[str]] = None,
    stamp: Optional[str] = None,
) -> List[str]:
    """Build CSV paths under command_save_files/dewetron_data."""
    import os
    import time

    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    base = os.path.join("command_save_files", "dewetron_data")
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
