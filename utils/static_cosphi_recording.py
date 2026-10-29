# -*- coding: utf-8 -*-
"""静态 Cos(φ)：连续录 / 分开录 文件名与 StopTime 辅助。"""

from __future__ import annotations

import re
from typing import List, Tuple

from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT, resolve_continuous_filename

_COS_STEP_DEFS = (
    (3, "checkBox_S3", "cos0.0", "textEdit_S3_DC_PF"),
    (4, "checkBox_S4", "cos0.5", "textEdit_S4_DC_PF"),
    (5, "checkBox_S5", "cos0.8", "textEdit_S5_DC_PF"),
    (6, "checkBox_S6", "cos0.9", "textEdit_S6_DC_PF"),
    (7, "checkBox_S7", "cos1.0", "textEdit_S7_DC_PF"),
    (8, "checkBox_S8", "cos-0.5", "textEdit_S8_DC_PF"),
    (9, "checkBox_S9", "cos-0.8", "textEdit_S9_DC_PF"),
    (10, "checkBox_S10", "cos-0.9", "textEdit_S10_DC_PF"),
    (11, "checkBox_S11", "cos-1.0", "textEdit_S11_DC_PF"),
)


def _power_levels(ui) -> List[str]:
    ladder_widget = getattr(ui, "textEdit_PowerLadder", None)
    ladder_text = ladder_widget.toPlainText().strip() if ladder_widget is not None else ""
    if ladder_text:
        return [p.strip() for p in re.split(r"[,，]", ladder_text) if p.strip()]
    return []


def _enabled_cos_steps(ui):
    """全部 cosφ（0.0 … -1.0）。功率档是外循环，各步勾选不再过滤。"""
    del ui
    return [
        (step_num, cos_label, pf_name)
        for step_num, _cb_name, cos_label, pf_name in _COS_STEP_DEFS
    ]


def split_filenames(ui) -> List[str]:
    """功率档 × 勾选 cosφ → 分开录多文件名。"""
    levels = _power_levels(ui)
    steps = _enabled_cos_steps(ui)
    names: List[str] = []
    if levels:
        for power_pct in levels:
            for _sn, cos_label, _pf in steps:
                safe = str(power_pct).replace("%", "")
                names.append("P%s_%s" % (safe, cos_label))
    else:
        for _sn, cos_label, pf_name in steps:
            te = getattr(ui, pf_name, None)
            pct = (te.toPlainText().strip() if te is not None else "") or "100"
            safe = str(pct).replace("%", "")
            names.append("P%s_%s" % (safe, cos_label))
    return names or [resolve_continuous_filename(ui) or "CosPhi_BR"]


def recommended_filenames(ui, mode: str) -> List[str]:
    if mode == MODE_CONTINUOUS:
        return [resolve_continuous_filename(ui) or "CosPhi_BR"]
    return split_filenames(ui)


def apply_segment_recording(rows, file_list_text: str, stop_str: str, *, continuous: bool) -> bool:
    """把本段文件名和 StopTime 写到最后一行 Upper_WT_Config。

    连续追加时从队头写会改掉第一段的名单，第二段仍用第一次的文件名，
    停表时被当成已经录完，CSV 不会再落盘。
    """
    target = None
    for row in rows or []:
        if row and row[0] == "Upper_WT_Config" and isinstance(row[4], dict):
            target = row
    if target is None:
        return False
    cfg = target[4]
    cfg["textEdit_FileNameList"] = file_list_text
    cfg["textEdit_StopTime"] = stop_str
    if cfg.get("comboBox_AutoSave", 0) == 0:
        cfg["comboBox_AutoSave"] = 1
    if continuous:
        cfg.pop("wt_merge_single_file", None)
        cfg.pop("wt_merge_output_path", None)
    return True


def stoptime_hhmmss(stop_sec: int) -> str:
    stop_sec = max(1, int(stop_sec))
    hh, rem = divmod(stop_sec, 3600)
    mm, ss = divmod(rem, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def plan_stop_and_names(
    ui,
    dwell_01s,
    *,
    n_points: int,
    wt_on: bool,
    wt_continuous: bool,
    margin_sec: int = 30,
) -> Tuple[List[str], int, int, str]:
    """返回 (文件名列表, StopTime秒, 本轮录波次数, 模式说明)。"""
    dwell_sec = max(1, int(round(float(dwell_01s) / 10.0)))
    n = max(0, int(n_points))
    if not wt_on:
        return [resolve_continuous_filename(ui) or "CosPhi_BR"], dwell_sec, 0, "未勾选WT"
    if wt_continuous:
        names = recommended_filenames(ui, MODE_CONTINUOUS)
        if n <= 0:
            return names, max(20, dwell_sec), 0, "一条线连续录"
        stop_sec = max(20, n * dwell_sec + int(margin_sec))
        return names, stop_sec, 1, "一条线连续录"
    names = recommended_filenames(ui, MODE_SPLIT)
    stop_sec = max(20, dwell_sec)
    return names, stop_sec, len(names), "分开录"
