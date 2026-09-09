# -*- coding: utf-8 -*-
"""过载能力测试：录波方式（连续录 ASYNC / 分开录 col7）。"""

from __future__ import annotations

from utils.matrix_recording_commands import row_ac_wait_idn, row_wt_async_marker
from utils.wt_recording_mode import MODE_CONTINUOUS, overload_recommended_filenames


def build_overload_measure_rows(collect_01s, *, wt_continuous: bool, wt_on: bool):
    """生成过载测量段命令。

    连续录：ASYNC_START → 按采集时间等待 → WAIT_END。
    分开录：沿用原逻辑，*IDN? 的 col[7] 触发一轮阻塞测量。
    """
    rows = []
    if wt_on and wt_continuous:
        rows.append(row_wt_async_marker("ASYNC_START"))
        rows.append(row_ac_wait_idn(collect_01s, slot=9))
        rows.append(row_wt_async_marker("WAIT_END"))
        return rows
    row = ["" for _ in range(10)]
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[7] = collect_01s
    rows.append(row)
    return rows


def recommended_overload_names(mode: str = MODE_CONTINUOUS):
    return overload_recommended_filenames(mode)
