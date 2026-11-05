# -*- coding: utf-8 -*-
"""过欠压_过欠频：按录波方式与勾选工况推荐文件名，并改写连续录/分开录触发。"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence

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


def _combo_text(ui, name, default=""):
    combo = getattr(ui, name, None)
    if combo is None:
        return default
    try:
        return (combo.currentText() or "").strip() or default
    except Exception:
        return default


def _to_01s(value: Any, unit: str) -> int:
    """把界面数值转成命令列等待单位（0.1s）。"""
    try:
        raw = float(str(value).strip())
    except (TypeError, ValueError):
        return 0
    u = str(unit or "秒").strip()
    if u in ("分钟", "分", "min", "minute", "minutes"):
        sec = raw * 60.0
    elif u in ("毫秒", "ms", "msec"):
        sec = raw / 1000.0
    else:
        sec = raw
    return max(0, int(round(sec * 10.0)))


def make_ovuf_boot_wait_row(boot_01s: Any) -> List[Any]:
    """启机等待：用 AC wait，禁止再用 query *IDN? 充当延时。

    历史实现把启机做成 ``AC query *IDN? + [9]=启机时长``；途哲台上 AC 句柄
    若 TCP 半开，``handle.query('*IDN?')`` 会永久卡住，进度一直停在
    ``[AC] query *IDN?``，表现为「设了 2 分钟启机却一直不进过欠压扫段」。
    """
    row: List[Any] = ["" for _ in range(10)]
    row[0] = "AC"
    row[1] = "wait"
    row[2] = "OVUF_BOOT"
    try:
        ticks = max(0, int(float(boot_01s)))
    except (TypeError, ValueError):
        ticks = 0
    row[9] = ticks
    return row


def ovuf_grid_wait_01s(ui) -> int:
    """段间回压后的并网等待（0.1s）。优先 textEdit_ovuf_grid_wait，其次 _ovufDwellSec，再退回启机时间。"""
    raw = _plain(ui, "textEdit_ovuf_grid_wait", "")
    unit = _combo_text(ui, "comboBox_ovuf_grid_wait", "秒")
    if raw:
        wait = _to_01s(raw, unit)
        if wait > 0:
            return wait
    meta = getattr(ui, "_ovufDwellSec", None)
    if meta not in (None, ""):
        wait = _to_01s(meta, "秒")
        if wait > 0:
            return wait
    # 勿回落到 S1 启机时间：默认单位常为「分钟」，会把段间等待拉成数分钟假死。
    return 50  # 默认 5s


def ovuf_has_later_segment(ui, after_step: int) -> bool:
    """after_step 之后是否还有已勾选的 S3~S8 段。"""
    try:
        cur = int(after_step)
    except (TypeError, ValueError):
        return False
    for step_no in range(cur + 1, 9):
        cb = getattr(ui, "checkBox_S%d" % step_no, None)
        if cb is not None and cb.isChecked():
            return True
    return False


def append_ovuf_segment_recovery(
    commands: List[Any],
    step_rows: Optional[List[Any]],
    ui,
    phase_mode: str,
    *,
    after_step: int,
    dwell_01s: Optional[int] = None,
) -> int:
    """段后恢复到 S1 额定；有下一段时再等并网。

    关键差异（爱科）：
    - 升频扫段每步只发 ``FREQ`` + 驻留，所以 50→51.7 一直成功；
    - 旧恢复发 ``VOLT``（带 SAVE）紧接 ``FREQ``（再 SAVE）。源在输出中连续两次
      SAVE 时，第二次频率常写不上，面板/输出就停在过频末点 51.7。
    因此：刚扫完频率的段只回 ``FREQ``（与扫段同路径）；刚扫完电压的段先
    ``VOLT``，短驻留后再 ``FREQ``，避免双 SAVE 撞车。
    并网等待单独成 AC wait 行（OVUF_GRID_RECOVERY），仅在还有后续段时插入。
    返回追加的等待（0.1s）；只回压回频、无等待时返回 0。
    """
    from utils.ac_scpi_commands import (
        append_ac_startup_setpoints,
        append_freq_set,
        append_volt_set,
    )

    volt_a = _plain(ui, "textEdit_S1_AC_VOLT", "230") or "230"
    volt_b = _plain(ui, "textEdit_S1_AC_VOLT_2", "") or volt_a
    volt_c = _plain(ui, "textEdit_S1_AC_VOLT_3", "") or volt_a
    freq = _plain(ui, "textEdit_S1_AC_FR", "50") or "50"
    batch_start = len(commands)
    just_swept = ovuf_sweep_project(int(after_step))
    same_volt = str(volt_a).strip() == str(volt_b).strip() == str(volt_c).strip()
    if just_swept == "过欠频":
        # 与升频步进同一路径：EDIT ALL + FREQ，不要夹 VOLT+SAVE
        append_freq_set(commands, phase_mode, freq)
    elif phase_mode == "三相" and not same_volt:
        # 异压三相：仍需完整 NSEL 序列
        append_ac_startup_setpoints(
            commands, phase_mode, volt_a, volt_b, volt_c, freq
        )
    else:
        # 扫压后电压已偏离额定：先回压，短等后再回频（两次 SAVE 错开）
        append_volt_set(commands, phase_mode, volt_a)
        settle = ["" for _ in range(10)]
        settle[0] = "AC"
        settle[1] = "wait"
        settle[2] = "OVUF_VOLT_SETTLE"
        settle[9] = 10  # 1s
        commands.append(settle)
        append_freq_set(commands, phase_mode, freq)

    has_later = ovuf_has_later_segment(ui, after_step)
    wait = 0
    if has_later:
        wait = int(dwell_01s) if dwell_01s is not None else ovuf_grid_wait_01s(ui)
        if wait <= 0:
            wait = 50
        # 强制等待：勿挂在 FREQ write 的 col9（连续录会提前跳过驻留）
        wait_row = ["" for _ in range(10)]
        wait_row[0] = "AC"
        wait_row[1] = "wait"
        wait_row[2] = "OVUF_GRID_RECOVERY"
        wait_row[9] = wait
        commands.append(wait_row)

    if step_rows is not None:
        step_rows.extend(commands[batch_start:])
    return wait


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


def ovuf_sweep_project(step_no: int) -> str:
    """步骤3/4扫电压，步骤5/6以及相位页附加段扫频率。

    不再跟步骤7上的「测试项目」走，避免四段被收成同一种过欠压。
    """
    if int(step_no) in (3, 4):
        return "过欠压"
    return "过欠频"


def enabled_ovuf_segments(ui):
    """已勾选 S3~S8 段。过压/欠压取电压，过频/欠频和附加段取频率。"""
    segs = []
    for step_no in (3, 4, 5, 6, 7, 8):
        cb = getattr(ui, "checkBox_S%d" % step_no, None)
        if cb is None or not cb.isChecked():
            continue
        if ovuf_sweep_project(step_no) == "过欠压":
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
        kinds = {seg["kind"] for seg in segs}
        if kinds == {"F"}:
            return ["OVUF_Freq_BR"]
        if kinds == {"V"}:
            return ["OVUF_Volt_BR"]
        return ["OVUF_BR"]
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


def rewrite_ac_idn_queries_as_wait(commands) -> int:
    """把「纯驻留」AC query *IDN? 改成 wait，避免半开 TCP 把跑环卡死。

    *IDN? 在队列里从不读返回值。但分开录时段首点把驻留放在 col6/col7
    触发 WT 测量——这类行必须留在 query 分支（由 run_loop 跳过真查询），
    若改成 wait 会丢掉测量触发，录波轮次会一直停在「等待」（job108）。
    """
    if not commands:
        return 0
    n = 0
    for row in commands:
        if not _is_idn_query(row):
            continue
        while len(row) < 10:
            row.append("")
        # 测量触发锚点：保留 query，真 *IDN? 由 is_idn_nop / 硬超时跳过
        if _numeric_slot(row[6]) is not None or _numeric_slot(row[7]) is not None:
            continue
        marker = str(row[6] or "").strip().upper()
        if marker in ("ASYNC_START", "WAIT_END", "WT_ASYNC_START", "WT_WAIT_END"):
            continue
        row[1] = "wait"
        row[2] = "IDN_NOP"
        n += 1
    return n


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


def ovuf_split_collect_sec(commands) -> int:
    """分开录：WT StopTime 应等于扫点驻留（col6/col9），禁止沿用 Soft Panel 默认 5 分钟。

    首点 col6 触发测量并阻塞到结束；若 StopTime 仍是 00:05:00，进度会停在
    「第16条 [AC] query *IDN?」空等整五分钟（job112）。
    """
    max_01s = 0
    for row in commands or []:
        if not row or len(row) < 3:
            continue
        # 扫点测量锚点（query *IDN? / wait IDN_NOP）上的驻留
        action = str(row[1] or "").strip().lower()
        cmd = str(row[2] or "").strip().upper()
        if action == "query" and cmd in ("*IDN?", "IDN?"):
            pass
        elif action == "wait" and cmd in ("IDN_NOP", "*IDN?", "IDN?"):
            pass
        else:
            continue
        for slot in (6, 7, 9):
            if len(row) <= slot:
                continue
            wait = _numeric_slot(row[slot])
            if wait is not None and wait > max_01s:
                max_01s = wait
    if max_01s <= 0:
        return 2
    return max(1, int(round(max_01s / 10.0)))


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
