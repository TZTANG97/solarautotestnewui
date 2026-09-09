# -*- coding: utf-8 -*-
"""重连：录波方式（连续录 ASYNC / 分开录 col7）。"""

from __future__ import annotations

from utils.matrix_recording_commands import row_wt_async_marker
from utils.wt_recording_mode import MODE_CONTINUOUS, reconnect_recommended_filenames


def enabled_reconnect_steps(ui):
    """返回已勾选的重连工况步骤号 [3..7]。"""
    out = []
    for step_no in (3, 4, 5, 6, 7):
        cb = getattr(ui, "checkBox_S%d" % step_no, None)
        if cb is not None and cb.isChecked():
            out.append(step_no)
    return out


def recommended_reconnect_names(ui, mode: str = MODE_CONTINUOUS):
    return reconnect_recommended_filenames(enabled_reconnect_steps(ui), mode)


def append_reconnect_measure(
    commands,
    step_rows,
    *,
    dwell_01s,
    wt_continuous: bool,
    wt_on: bool,
    first_point: bool,
    last_point: bool,
):
    """每个重连点的采集等待。连续录首点 ASYNC_START、末点 WAIT_END。"""
    if wt_on and wt_continuous and first_point:
        row = row_wt_async_marker("ASYNC_START")
        commands.append(row)
        step_rows.append(row)
    row = ["" for _ in range(10)]
    row[0], row[1], row[2] = "AC", "query", "*IDN?"
    if wt_on and wt_continuous:
        row[9] = dwell_01s
    else:
        row[7] = dwell_01s
    commands.append(row)
    step_rows.append(row)
    if not (wt_on and wt_continuous):
        row = ["" for _ in range(10)]
        row[0], row[1], row[2] = "AC", "query", "*IDN?"
        row[8] = 10
        commands.append(row)
        step_rows.append(row)
    if wt_on and wt_continuous and last_point:
        row = row_wt_async_marker("WAIT_END")
        commands.append(row)
        step_rows.append(row)
