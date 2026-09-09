# -*- coding: utf-8 -*-
"""巴西 Cos(φ)：连续录 / 分开录 命令与文件名辅助。"""

from __future__ import annotations

import re
from typing import List, Tuple

from utils.matrix_recording_commands import row_wt_async_marker
from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT, resolve_continuous_filename

_STEP_PCT = (
    (3, "textEdit_S3_DC_PF", "P"),
    (4, "textEdit_S4_DC_PF", "P"),
    (5, "textEdit_S5_DC_PF", "P"),
    (6, "textEdit_S6_DC_PF", "P"),
    (7, "textEdit_S7_DC_PF", "P"),
    (8, "textEdit_S8_DC_PF", "P"),
    (9, "textEdit_S9_DC_PF", "AC"),
)


def split_filenames(ui) -> List[str]:
    """按勾选功率点生成分开录文件名列表。"""
    names: List[str] = []
    for sn, te_name, prefix in _STEP_PCT:
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is None or not cb.isChecked():
            continue
        te = getattr(ui, te_name, None)
        pct = (te.toPlainText().strip() if te is not None else "") or str(sn)
        safe = re.sub(r"[^\w.\-]+", "", pct)
        names.append("CosPhiBR_%s%s" % (prefix, safe))
    return names or [resolve_continuous_filename(ui) or "CosPhiBR_BR"]


def recommended_filenames(ui, mode: str) -> List[str]:
    if mode == MODE_CONTINUOUS:
        return [resolve_continuous_filename(ui) or "CosPhiBR_BR"]
    return split_filenames(ui)


def _row_is_power_dwell(row, dwell_01s) -> bool:
    if not row or len(row) < 7:
        return False
    if row[0] != "AC" or row[1] != "query" or row[2] != "*IDN?":
        return False
    v = row[6]
    if v in ("", None):
        return False
    if isinstance(v, str) and v in ("ASYNC_START", "WAIT_END"):
        return False
    try:
        return abs(float(v) - float(dwell_01s)) < 1e-6
    except (TypeError, ValueError):
        return False


def rewrite_power_point_dwells(
    commands: list,
    dwell_01s,
    *,
    wt_on: bool,
    wt_continuous: bool,
) -> int:
    """把功率点上的 col6=dwell 按录波模式改写。

    - 未勾选 WT：改为 col9 普通等待（不触发测量）
    - 分开录：保留 col6（每点触发一轮测量）
    - 连续录：改 col9 驻留，并在首/末插入 ASYNC_START / WAIT_END

    返回功率点个数。
    """
    idxs = [i for i, row in enumerate(commands) if _row_is_power_dwell(row, dwell_01s)]
    n = len(idxs)
    if n == 0:
        return 0

    if not wt_on:
        for i in idxs:
            commands[i][6] = ""
            commands[i][9] = dwell_01s
        return n

    if not wt_continuous:
        # 分开录：保持 col6 触发
        return n

    for i in idxs:
        commands[i][6] = ""
        commands[i][9] = dwell_01s

    first_i = idxs[0]
    last_i = idxs[-1]
    commands.insert(first_i, row_wt_async_marker("ASYNC_START"))
    # 插入 ASYNC 后 last 下标 +1；再插到 last 之后
    commands.insert(last_i + 2, row_wt_async_marker("WAIT_END"))
    return n


def stoptime_hhmmss(stop_sec: int) -> str:
    stop_sec = max(1, int(stop_sec))
    hh, rem = divmod(stop_sec, 3600)
    mm, ss = divmod(rem, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def plan_stop_and_names(
    ui,
    dwell_01s,
    *,
    wt_on: bool,
    wt_continuous: bool,
    margin_sec: int = 30,
) -> Tuple[List[str], int, int, str]:
    """返回 (文件名列表, StopTime秒, 本轮录波次数, 模式说明)。"""
    dwell_sec = max(1, int(round(float(dwell_01s) / 10.0)))
    n_points = sum(
        1
        for sn, _, _ in _STEP_PCT
        if (getattr(ui, "checkBox_S%d" % sn, None) is not None
            and getattr(ui, "checkBox_S%d" % sn).isChecked())
    )
    if n_points <= 0:
        n_points = 1

    if not wt_on:
        names = [resolve_continuous_filename(ui) or "CosPhiBR_BR"]
        return names, dwell_sec, 0, "未勾选WT"

    if wt_continuous:
        names = recommended_filenames(ui, MODE_CONTINUOUS)
        stop_sec = max(20, n_points * dwell_sec + int(margin_sec))
        return names, stop_sec, 1, "一条线连续录"
    names = recommended_filenames(ui, MODE_SPLIT)
    stop_sec = max(20, dwell_sec)
    return names, stop_sec, len(names), "分开录"
