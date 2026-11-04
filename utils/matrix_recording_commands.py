# -*- coding: utf-8 -*-
"""P×Q / P 阶梯矩阵试验：连续录 ASYNC 与分开录 col6 共用辅助。"""

from __future__ import annotations

from utils.wt_recording_mode import MODE_CONTINUOUS, combo_index_to_mode


def _empty_row():
    return ["" for _ in range(10)]


def row_wt_async_marker(marker: str):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[6] = marker
    return row


def row_ac_wait_idn(wait_01s, slot=9):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[slot] = wait_01s
    return row


def get_record_mode(ui) -> str:
    """Resolve continuous vs split from analyzer / step / WT page combos."""
    from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT, combo_index_to_mode

    # 云任务钉住的录波方式优先（OVUF 等对话框无 comboBox_S3_record_mode 时）
    pinned = getattr(ui, "_wt_record_mode_from_job", None) if ui is not None else None
    if pinned in (MODE_CONTINUOUS, MODE_SPLIT, "continuous", "split"):
        return MODE_SPLIT if str(pinned).lower() == MODE_SPLIT else MODE_CONTINUOUS

    # Shared analyzer row (visible in both WT and DEWETRON modes).
    for name in (
        "comboBox_analyzer_recording_mode",
        "comboBox_S3_record_mode",
    ):
        combo = getattr(ui, name, None)
        if combo is not None:
            try:
                return combo_index_to_mode(combo.currentIndex())
            except Exception:
                pass

    section = getattr(ui, "analyzerModeSection", None)
    if section is not None:
        combo = getattr(section, "comboBox_analyzer_recording_mode", None)
        if combo is not None:
            try:
                return combo_index_to_mode(combo.currentIndex())
            except Exception:
                pass

    stacked = getattr(ui, "_wtStacked", None)
    if stacked is not None:
        try:
            from PyQt5 import QtWidgets

            # Prefer any WT page combo (same index across pages when synced).
            for page_idx in range(stacked.count()):
                page = stacked.widget(page_idx)
                if page is None:
                    continue
                combo = page.findChild(QtWidgets.QComboBox, "comboBox_recording_mode")
                if combo is not None:
                    return combo_index_to_mode(combo.currentIndex())
        except Exception:
            pass
    return MODE_CONTINUOUS


def maybe_async_start(commands, point_rows, *, wt_continuous, wt_is_checked, point_index):
    if wt_continuous and wt_is_checked == "1" and point_index == 0:
        row = row_wt_async_marker("ASYNC_START")
        commands.append(row)
        point_rows.append(row)


def append_matrix_dwell(commands, point_rows, dwell_01s, *, wt_continuous):
    slot = 9 if wt_continuous else 6
    row = row_ac_wait_idn(int(dwell_01s), slot=slot)
    commands.append(row)
    point_rows.append(row)


def maybe_async_end(commands, *, wt_continuous, wt_is_checked, total_points):
    if wt_continuous and wt_is_checked == "1" and total_points > 0:
        commands.append(row_wt_async_marker("WAIT_END"))


def resolve_wt_rounds(wt_is_checked, file_names, wt_continuous) -> int:
    if wt_is_checked != "1" or not file_names:
        return 0
    return 1 if wt_continuous else len(file_names)
