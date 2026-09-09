# -*- coding: utf-8 -*-
"""直流分量：录波方式（连续录 ASYNC / 分开录 col7）。"""

from __future__ import annotations

from utils.matrix_recording_commands import row_ac_wait_idn, row_wt_async_marker
from utils.wt_recording_mode import MODE_CONTINUOUS, dc_injection_recommended_filenames


def enabled_dc_injection_steps(ui):
    """返回已勾选的工况 [(step_no, power_pct), ...]。"""
    out = []
    for step_no in (3, 4, 5, 6):
        cb = getattr(ui, "checkBox_S%d" % step_no, None)
        if cb is None or not cb.isChecked():
            continue
        raw = getattr(ui, "textEdit_S%d_DC_PF" % step_no).toPlainText().strip()
        try:
            pct = float(raw)
        except ValueError:
            pct = float(step_no)
        out.append((step_no, pct))
    return out


def recommended_dc_injection_names(ui, mode: str = MODE_CONTINUOUS):
    return dc_injection_recommended_filenames(enabled_dc_injection_steps(ui), mode)


def append_dc_injection_measure(
    commands,
    step_rows,
    *,
    wait_01s,
    collect_01s,
    wt_continuous: bool,
    wt_on: bool,
    include_wait: bool,
    first_point: bool,
    last_point: bool,
):
    """每个功率点的等待+采集。连续录首点 ASYNC_START、末点 WAIT_END。"""
    if wt_on and wt_continuous and first_point:
        row = row_wt_async_marker("ASYNC_START")
        commands.append(row)
        step_rows.append(row)
    if include_wait:
        row = row_ac_wait_idn(wait_01s, slot=9)
        commands.append(row)
        step_rows.append(row)
    row = ["" for _ in range(10)]
    row[0], row[1], row[2] = "AC", "query", "*IDN?"
    if wt_on and wt_continuous:
        row[9] = collect_01s
    else:
        row[7] = collect_01s
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
