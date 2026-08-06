# -*- coding: utf-8 -*-
"""WTViewer 分轮 CSV → 单一合并文本。"""
from __future__ import annotations

import csv
import os
import time
from typing import Iterable, List, Optional


def candidate_save_dirs(save_path: str = "", extra: Optional[Iterable[str]] = None) -> List[str]:
    """按优先级列出可能落盘目录。"""
    dirs: List[str] = []
    sp = (save_path or "").strip().strip('"')
    if sp:
        dirs.append(sp)
    if extra:
        dirs.extend([d for d in extra if d])
    dirs.append(os.getcwd())
    # 去重保序
    seen = set()
    out = []
    for d in dirs:
        nd = os.path.normpath(d)
        key = os.path.normcase(nd)
        if key in seen:
            continue
        seen.add(key)
        out.append(nd)
    return out


def find_wt_csv(basename: str, search_dirs: Iterable[str], wait_s: float = 2.0) -> Optional[str]:
    """
    查找刚保存的 WT 文件。basename 不含或含扩展名均可。
    短等待，兼容 WT 落盘延迟。
    """
    stem = basename.strip()
    if not stem:
        return None
    names = []
    # 注意：测点名常含小数点（P100_cos0.9），不能用 splitext 判断扩展名
    known_ext = (".csv", ".txt", ".CSV", ".TXT")
    lower = stem.lower()
    has_known_ext = any(lower.endswith(e.lower()) for e in known_ext)
    if has_known_ext:
        root, ext = os.path.splitext(stem)
        names.append(stem)
        names.append(root + ext.upper())
        names.append(root + ext.lower())
    else:
        for e in (".CSV", ".csv", ".TXT", ".txt"):
            names.append(stem + e)

    deadline = time.time() + max(0.0, wait_s)
    last_hit = None
    while True:
        for d in search_dirs:
            if not d or not os.path.isdir(d):
                continue
            for name in names:
                fp = os.path.join(d, name)
                if os.path.isfile(fp) and os.path.getsize(fp) > 0:
                    # 取最新修改的一份
                    if last_hit is None or os.path.getmtime(fp) >= os.path.getmtime(last_hit):
                        last_hit = fp
        if last_hit is not None:
            return last_hit
        if time.time() >= deadline:
            return None
        time.sleep(0.2)


def append_round_to_merge(
    merge_path: str,
    source_path: str,
    round_label: str,
    *,
    delete_source: bool = True,
) -> int:
    """
    将 source CSV 追加到 merge_path，首列插入 Round。
    返回追加的数据行数。
    """
    if not source_path or not os.path.isfile(source_path):
        raise FileNotFoundError(f"source CSV missing: {source_path}")

    os.makedirs(os.path.dirname(os.path.abspath(merge_path)) or ".", exist_ok=True)

    with open(source_path, "r", encoding="utf-8-sig", errors="replace", newline="") as sf:
        reader = csv.reader(sf)
        rows = list(reader)
    if not rows:
        return 0

    header = rows[0]
    data_rows = rows[1:]
    write_header = not os.path.isfile(merge_path) or os.path.getsize(merge_path) == 0

    with open(merge_path, "a", encoding="utf-8-sig", newline="") as mf:
        writer = csv.writer(mf)
        if write_header:
            writer.writerow(["Round"] + header)
        for row in data_rows:
            writer.writerow([round_label] + row)

    if delete_source:
        try:
            # 合并目标若碰巧与源同路径则不删
            if os.path.abspath(source_path) != os.path.abspath(merge_path):
                os.remove(source_path)
        except OSError:
            pass

    return len(data_rows)
