# -*- coding: utf-8 -*-
"""过欠压_过欠频：按录波方式与勾选工况推荐文件名，并改写连续录/分开录触发。"""

from __future__ import annotations

from utils.matrix_recording_commands import row_wt_async_marker
from utils.wt_recording_mode import MODE_CONTINUOUS, _format_setpoint_tag


def build_ovuf_sweep_points(start, end, step_size):
    """与 thaiguoqianya_pinSend 一致的起止+步长扫点列表。"""
    try:
        a = float(start)
        b = float(end)
        step = float(step_size)
    except (TypeError, ValueError):
        return []
    if step <= 0:
        return [round(a, 2)]
    out = []
    if b > a:
        cur = a
        while cur < b:
            out.append(round(cur, 2))
            cur += step
        out.append(round(b, 2))
    elif b < a:
        cur = a
        while cur > b:
            out.append(round(cur, 2))
            cur -= step
        out.append(round(b, 2))
    else:
        out.append(round(a, 2))
    return out


def _plain(ui, name, default=""):
    te = getattr(ui, name, None)
    if te is None:
        return default
    try:
        return (te.toPlainText() or "").strip() or default
    except Exception:
        return default


def ovuf_test_project(ui) -> str:
    combo = getattr(ui, "comboBox_Test_Project", None)
    if combo is None:
        return "过欠压"
    try:
        return (combo.currentText() or "过欠压").strip()
    except Exception:
        return "过欠压"


def build_ovuf_phase_check_list(ui):
    """返回 ['T'|'', ...]；L1/L2/L3 可多选（勿用 elif）。"""
    out = ["", "", ""]
    for i, name in enumerate(("checkBox_AC_Test_L1", "checkBox_AC_Test_L2", "checkBox_AC_Test_L3")):
        cb = getattr(ui, name, None)
        if cb is not None and cb.isChecked():
            out[i] = "T"
    return out


def enabled_ovuf_segments(ui):
    """已勾选 S3~S8 段：按测试项目取电压或频率扫点。"""
    project = ovuf_test_project(ui)
    is_volt = project == "过欠压"
    segs = []
    for step_no in (3, 4, 5, 6, 7, 8):
        cb = getattr(ui, "checkBox_S%d" % step_no, None)
        if cb is None or not cb.isChecked():
            continue
        if is_volt:
            start = _plain(ui, "textEdit_S%d_AC_VOLT_Start" % step_no, "230")
            end = _plain(ui, "textEdit_S%d_AC_VOLT_End" % step_no, "230")
            kind = "V"
        else:
            start = _plain(ui, "textEdit_S%d_AC_FR_Start" % step_no, "50")
            end = _plain(ui, "textEdit_S%d_AC_FR_End" % step_no, "50")
            kind = "F"
        step = _plain(ui, "textEdit_S%d_Step_Size" % step_no, "5")
        points = build_ovuf_sweep_points(start, end, step)
        segs.append(
            {
                "step": step_no,
                "kind": kind,
                "start": float(start) if points else 0.0,
                "end": float(end) if points else 0.0,
                "points": points,
            }
        )
    return segs


def recommended_ovuf_names(ui, mode: str = MODE_CONTINUOUS):
    """连续录 OVUF_Volt_BR / OVUF_Freq_BR；分开录按勾选段生成 OVUF_S3_V230_253 等。"""
    segs = enabled_ovuf_segments(ui)
    if mode == MODE_CONTINUOUS:
        return ["OVUF_Volt_BR"] if ovuf_test_project(ui) == "过欠压" else ["OVUF_Freq_BR"]
    names = []
    for seg in segs:
        prefix = seg["kind"]
        names.append(
            "OVUF_S%d_%s%s_%s"
            % (
                seg["step"],
                prefix,
                _format_setpoint_tag(seg["start"]),
                _format_setpoint_tag(seg["end"]),
            )
        )
    return names or ["OVUF_S3_V230_230"]


def _is_volt_or_freq_write(row) -> bool:
    if not row or len(row) < 3:
        return False
    if row[0] != "AC" or row[1] != "write":
        return False
    cmd = str(row[2] or "").strip().upper()
    return cmd.startswith("VOLT ") or cmd.startswith("FREQ ")


def _is_idn_query(row) -> bool:
    if not row or len(row) < 3:
        return False
    return row[0] == "AC" and row[1] == "query" and str(row[2] or "").strip().upper() == "*IDN?"


def _numeric_slot(val):
    if val in ("", None):
        return None
    if isinstance(val, str) and val.strip().upper() in ("ASYNC_START", "WAIT_END", "WT_ASYNC_START", "WT_WAIT_END"):
        return None
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return None


def find_ovuf_sweep_measure_indices(commands):
    """扫压/扫频写命令后紧跟的 *IDN? 驻留行下标。"""
    out = []
    for i, row in enumerate(commands):
        if i == 0 or not _is_idn_query(row):
            continue
        if not _is_volt_or_freq_write(commands[i - 1]):
            continue
        while len(row) < 10:
            row.append("")
        if _numeric_slot(row[6]) is not None or _numeric_slot(row[9]) is not None or _numeric_slot(row[7]) is not None:
            out.append(i)
        elif row[6] in ("", None) and row[9] in ("", None) and row[7] in ("", None):
            # 无等待字段也视为扫点测量占位
            out.append(i)
    return out


def _ensure_row10(row):
    while len(row) < 10:
        row.append("")
    return row


def _move_wait_to_col9(row):
    _ensure_row10(row)
    wait = _numeric_slot(row[6])
    if wait is None:
        wait = _numeric_slot(row[7])
    if wait is None:
        wait = _numeric_slot(row[9])
    if wait is None:
        wait = 10
    row[6] = ""
    row[7] = ""
    row[9] = wait
    return wait


def apply_ovuf_recording_mode(commands, ui, *, continuous: bool, wt_on: bool) -> int:
    """按录波方式改写扫点测量触发。返回应累加的 total_save_file 增量。"""
    segs = enabled_ovuf_segments(ui)
    if not segs:
        return 0
    if not wt_on:
        return 0

    measures = find_ovuf_sweep_measure_indices(commands)
    expected = sum(len(s["points"]) for s in segs)
    if continuous:
        for idx in measures:
            _move_wait_to_col9(commands[idx])
        if not measures:
            return 1
        first = measures[0]
        last = measures[-1]
        commands.insert(first, row_wt_async_marker("ASYNC_START"))
        # WAIT_END 插在 last+1（因 insert 使 last 右移 1）
        commands.insert(last + 2, row_wt_async_marker("WAIT_END"))
        return 1

    # 分开录：每段首点 col6，其余 col9
    if not measures:
        return len(segs)

    cursor = 0
    for seg in segs:
        n = len(seg["points"]) or 1
        for j in range(n):
            if cursor >= len(measures):
                break
            row = _ensure_row10(commands[measures[cursor]])
            wait = _move_wait_to_col9(row)
            if j == 0:
                row[9] = ""
                row[6] = wait
            else:
                row[6] = ""
                row[9] = wait
            cursor += 1
    # 若实际测量行多于期望，剩余保持 col9
    while cursor < len(measures):
        _move_wait_to_col9(commands[measures[cursor]])
        cursor += 1
    return len(segs)
