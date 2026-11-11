# -*- coding: utf-8 -*-
"""Soft Panel 常写出 FreqU-SIGMA / FreqI-SIGMA 空列（有表头无值）。

横河对频率总和项经常不填，但元素 1/2/3 有值。结案/分析前把空 SIGMA
填成对应元素列的均值，避免表头骗人。
"""
from __future__ import annotations

import csv
import os
import re
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


def recording_rank(path: Path) -> tuple:
    """文件名末尾 HHMMSS 优先于 mtime。旧录波被改写后 mtime 会变成最新。"""
    match = re.search(r"(\d{6})$", Path(path).stem)
    stamp = int(match.group(1)) if match else -1
    try:
        mtime = Path(path).stat().st_mtime
    except OSError:
        mtime = 0.0
    return (stamp, mtime)


def _mean_or_blank(vals: Sequence[str]) -> str:
    nums: List[float] = []
    for v in vals:
        text = str(v or "").strip()
        if not text:
            continue
        try:
            nums.append(float(text))
        except ValueError:
            continue
    if not nums:
        return ""
    return f"{(sum(nums) / len(nums)):.7f}"


def fill_empty_sigma_freq_columns(csv_path: str | Path) -> bool:
    """若 FreqU-SIGMA / FreqI-SIGMA 整列空，用 FreqU-1..3 / FreqI-1..3 均值回填。

    返回是否改写了文件。
    """
    path = Path(csv_path)
    if not path.is_file():
        return False
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
    except OSError:
        return False
    if len(rows) < 2:
        return False
    header = [str(c).strip() for c in rows[0]]
    changed = False

    def _fill(sigma_name: str, element_prefix: str) -> None:
        nonlocal changed
        try:
            si = header.index(sigma_name)
        except ValueError:
            return
        el_idx = []
        for i, name in enumerate(header):
            if name.startswith(element_prefix) and name != sigma_name:
                # FreqU-1 / FreqU-2 … 不要误收 FreqU-SIGMA
                suffix = name[len(element_prefix) :]
                if suffix[:1] == "-" and suffix[1:].isdigit():
                    el_idx.append(i)
        if not el_idx:
            return
        # 按行回填空 SIGMA（不要因首行偶发有值就跳过整列）
        for row in rows[1:]:
            while len(row) < len(header):
                row.append("")
            if str(row[si]).strip():
                continue
            vals = [row[i] if i < len(row) else "" for i in el_idx]
            filled = _mean_or_blank(vals)
            if filled:
                row[si] = filled
                changed = True

    _fill("FreqU-SIGMA", "FreqU")
    _fill("FreqI-SIGMA", "FreqI")
    if not changed:
        return False
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        os.replace(tmp, path)
    except OSError:
        try:
            if tmp.is_file():
                tmp.unlink()
        except OSError:
            pass
        return False
    return True


def fill_recent_csvs_in_dirs(
    dirs: Iterable[str | Path],
    *,
    name_hint: str = "",
    limit: int = 8,
    min_mtime: float = 0.0,
) -> List[str]:
    """在保存目录里找最近 CSV（可按文件名 hint）并回填空 SIGMA。

    min_mtime>0 时只处理本轮开录之后的文件，避免改写同目录旧录波并把它的 mtime 刷进本轮。
    """
    hint = str(name_hint or "").strip().lower()
    floor = float(min_mtime or 0.0)
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
                if floor > 0:
                    try:
                        if p.stat().st_mtime < floor - 2.0:
                            continue
                    except OSError:
                        continue
                cands.append(p)
        except OSError:
            continue
    cands.sort(key=recording_rank, reverse=True)
    filled: List[str] = []
    for p in cands[: max(1, int(limit))]:
        try:
            if fill_empty_sigma_freq_columns(p):
                filled.append(str(p))
        except Exception:
            continue
    return filled
