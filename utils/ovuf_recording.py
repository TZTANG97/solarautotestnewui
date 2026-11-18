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
    after_step: int = 3,
    dwell_01s: Optional[int] = None,
    just_kind: Optional[str] = None,
    has_later: Optional[bool] = None,
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

    ``just_kind``: ``\"V\"`` / ``\"F\"`` 或中文；工况列表模式直接传入，不依赖 S3–S8。
    ``has_later``: 显式指定是否还有后续工况；默认仍查 S3–S8 勾选。
    """
    from utils.ac_scpi_commands import (
        append_ac_startup_setpoints,
        append_chroma_phase_volts,
        append_freq_set,
        append_volt_set,
        resolve_chroma_61800,
    )

    volt_a = _plain(ui, "textEdit_S1_AC_VOLT", "230") or "230"
    volt_b = _plain(ui, "textEdit_S1_AC_VOLT_2", "") or volt_a
    volt_c = _plain(ui, "textEdit_S1_AC_VOLT_3", "") or volt_a
    freq = _plain(ui, "textEdit_S1_AC_FR", "50") or "50"
    batch_start = len(commands)
    if just_kind is not None:
        jk = str(just_kind).strip().upper()
        just_swept = "过欠频" if jk in ("F", "频率", "过欠频") else "过欠压"
    else:
        just_swept = ovuf_sweep_project(int(after_step))
    same_volt = str(volt_a).strip() == str(volt_b).strip() == str(volt_c).strip()
    chroma_61800 = resolve_chroma_61800()
    if just_swept == "过欠频":
        # 与升频步进同一路径：EDIT ALL + FREQ，不要夹 VOLT+SAVE
        append_freq_set(commands, phase_mode, freq, chroma_61800=chroma_61800)
    elif phase_mode == "三相" and not same_volt:
        # 异压三相：仍需完整 NSEL 序列
        append_ac_startup_setpoints(
            commands,
            phase_mode,
            volt_a,
            volt_b,
            volt_c,
            freq,
            chroma_61800=chroma_61800,
        )
    else:
        # 扫压后电压已偏离额定：先回压，短等后再回频（两次 SAVE 错开）
        # Chroma 分相扫压可能留在 INDEPEND：对称额定也走 SAMEFREQ 回压
        if phase_mode == "三相" and chroma_61800:
            append_chroma_phase_volts(commands, volt_a, volt_b, volt_c)
        else:
            append_volt_set(
                commands, phase_mode, volt_a, chroma_61800=chroma_61800
            )
        settle = ["" for _ in range(10)]
        settle[0] = "AC"
        settle[1] = "wait"
        settle[2] = "OVUF_VOLT_SETTLE"
        settle[9] = 10  # 1s
        commands.append(settle)
        append_freq_set(commands, phase_mode, freq, chroma_61800=chroma_61800)

    if has_later is None:
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


def read_ovuf_rated_phase_volts(ui) -> tuple:
    """步骤1 A/B/C 额定电压；B/C 空则回退到 A。"""
    va = _plain(ui, "textEdit_S1_AC_VOLT", "230") or "230"
    vb = _plain(ui, "textEdit_S1_AC_VOLT_2", "") or va
    vc = _plain(ui, "textEdit_S1_AC_VOLT_3", "") or va
    return va, vb, vc


def build_ovuf_phase_target_volts(step_volt, phase_check_list, rated_volts) -> tuple:
    """勾选相用扫点电压，未勾选相保持额定（PEA 类单相/两相故障）。

    三相全勾或一相都没勾 → 三相都用扫点（与旧「三相同压」一致）。
    """
    flags = list(phase_check_list or [])
    while len(flags) < 3:
        flags.append("")
    flags = flags[:3]
    rated = list(rated_volts or ())
    while len(rated) < 3:
        rated.append(rated[0] if rated else "230")
    rated = [str(x).strip() or "230" for x in rated[:3]]
    if "T" not in flags:
        flags = ["T", "T", "T"]
    step = str(step_volt).strip()
    return tuple(step if flags[i] == "T" else rated[i] for i in range(3))


def append_ovuf_sweep_volt(
    out_rows,
    phase_mode,
    step_volt,
    phase_check_list=None,
    rated_volts=None,
    *,
    chroma_61800=None,
) -> None:
    """过欠压扫点写压：全选/同压走 EDIT ALL；部分相勾选走 EDIT EACH 分相。

    不改变 ``append_volt_set`` 默认行为，其它试验不受影响。
    """
    from utils.ac_scpi_commands import append_volt_set
    from utils.timing_profile_adapters import append_ac_voltage

    if phase_mode == "单相":
        append_volt_set(out_rows, phase_mode, step_volt, chroma_61800=chroma_61800)
        return
    targets = build_ovuf_phase_target_volts(step_volt, phase_check_list, rated_volts)
    if targets[0] == targets[1] == targets[2]:
        append_volt_set(out_rows, phase_mode, targets[0], chroma_61800=chroma_61800)
        return
    append_ac_voltage(out_rows, phase_mode, targets, chroma_61800=chroma_61800)


def read_ovuf_condition_rows(ui) -> List[dict]:
    """工况列表已从过欠压 Dialog 移除；恒返回 []，始终走 S3–S8 扫段。"""
    return []


def _phase_flags_from_row(row: dict) -> list:
    return [
        "T" if row.get("l1", True) else "",
        "T" if row.get("l2", True) else "",
        "T" if row.get("l3", True) else "",
    ]


def _phase_tag(flags) -> str:
    letters = []
    for i, ch in enumerate(("1", "2", "3")):
        if i < len(flags) and flags[i] == "T":
            letters.append(ch)
    return ("L" + "".join(letters)) if letters else "L123"


def append_ovuf_condition_sequence(
    commands: List[Any],
    step_batches: List[Any],
    ui,
    phase_mode: str,
    rows: Sequence[dict],
    *,
    chroma_61800=None,
) -> float:
    """按工况列表顺序下发；返回累计测试时长（秒）。

    每行：改压/改频 → 驻留 →（非末行）回额定并网等待。
    """
    from utils.ac_scpi_commands import append_freq_set, resolve_chroma_61800
    from utils.time_helpers import SetTimeFunction

    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()
    rated = read_ovuf_rated_phase_volts(ui)
    total_sec = 0.0
    enabled = [r for r in rows if r.get("enabled", True)]
    for idx, row in enumerate(enabled):
        step_rows: List[Any] = []
        kind = str(row.get("kind", "V")).strip().upper()
        value = str(row.get("value", "")).strip() or ("50" if kind == "F" else "230")
        flags = _phase_flags_from_row(row)
        try:
            dwell_raw = float(str(row.get("dwell", "3")).strip() or "3")
        except (TypeError, ValueError):
            dwell_raw = 3.0
        unit = str(row.get("unit", "秒")).strip() or "秒"
        dwell_01s = int(SetTimeFunction(dwell_raw, unit))
        if dwell_01s <= 0:
            dwell_01s = 1

        _bs = len(commands)
        if kind == "F":
            append_freq_set(
                commands, phase_mode, value, chroma_61800=chroma_61800
            )
        else:
            append_ovuf_sweep_volt(
                commands,
                phase_mode,
                value,
                flags,
                rated,
                chroma_61800=chroma_61800,
            )
        step_rows.extend(commands[_bs:])

        dwell_row = ["" for _ in range(10)]
        dwell_row[0] = "AC"
        dwell_row[1] = "wait"
        dwell_row[2] = "OVUF_COND_DWELL"
        dwell_row[9] = dwell_01s
        commands.append(dwell_row)
        step_rows.append(dwell_row)
        total_sec += dwell_01s / 10.0

        has_later = idx < len(enabled) - 1
        _rec = []
        wait = append_ovuf_segment_recovery(
            commands,
            _rec,
            ui,
            phase_mode,
            after_step=3 if kind != "F" else 5,
            just_kind=kind,
            has_later=has_later,
        )
        step_rows.extend(_rec)
        if wait:
            total_sec += wait / 10.0
        step_batches.append(step_rows)
    return total_sec


def ovuf_sweep_project(step_no: int) -> str:
    """步骤3/4扫电压，步骤5/6以及相位页附加段扫频率。

    不再跟步骤7上的「测试项目」走，避免四段被收成同一种过欠压。
    """
    if int(step_no) in (3, 4):
        return "过欠压"
    return "过欠频"


def enabled_ovuf_segments(ui):
    """优先工况列表；否则已勾选 S3~S8 扫段。"""
    cond = read_ovuf_condition_rows(ui)
    if cond:
        segs = []
        for i, row in enumerate(cond, start=1):
            kind = "F" if str(row.get("kind", "V")).strip().upper() == "F" else "V"
            try:
                val = float(str(row.get("value", "0")).strip() or "0")
            except (TypeError, ValueError):
                val = 0.0
            flags = _phase_flags_from_row(row)
            # 频率行整机改频，文件名不带相标签
            tag = "F" if kind == "F" else _phase_tag(flags)
            segs.append(
                {
                    "step": i,
                    "kind": kind,
                    "start": val,
                    "end": val,
                    "points": [val],
                    "phase_tag": tag,
                    "from_list": True,
                }
            )
        return segs
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
    """连续录 OVUF_Volt_BR / OVUF_Freq_BR；分开录按列表行或旧扫段命名。"""
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
        if seg.get("from_list"):
            if prefix == "F":
                names.append(
                    "OVUF_R%02d_F%s"
                    % (int(seg["step"]), _format_setpoint_tag(seg["start"]))
                )
            else:
                names.append(
                    "OVUF_R%02d_%s%s_%s"
                    % (
                        int(seg["step"]),
                        prefix,
                        _format_setpoint_tag(seg["start"]),
                        seg.get("phase_tag") or "L123",
                    )
                )
        else:
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
    return (
        cmd.startswith("VOLT ")
        or cmd.startswith("VOLT:AC ")
        or cmd.startswith("FREQ ")
    )


def _is_ovuf_cond_dwell(row) -> bool:
    """工况列表行驻留：AC wait OVUF_COND_DWELL（col9=0.1s）。"""
    if not row or len(row) < 3:
        return False
    return (
        row[0] == "AC"
        and str(row[1] or "").strip().lower() == "wait"
        and str(row[2] or "").strip().upper() == "OVUF_COND_DWELL"
    )


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
    """扫点测量锚点下标：旧扫段 *IDN?，或工况列表 OVUF_COND_DWELL。"""
    out = []
    for i, row in enumerate(commands):
        if _is_ovuf_cond_dwell(row):
            _ensure_row10(row)
            out.append(i)
            continue
        if i == 0 or not _is_idn_query(row):
            continue
        if not _is_volt_or_freq_write(commands[i - 1]):
            # 分相 EDIT EACH 末尾可能是 INST:EDIT ALL；向前找最近 VOLT/FREQ
            prev_ok = False
            for j in range(i - 1, max(-1, i - 12), -1):
                if _is_volt_or_freq_write(commands[j]):
                    prev_ok = True
                    break
                if commands[j] and commands[j][0] == "AC" and commands[j][1] == "wait":
                    break
            if not prev_ok:
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
    工况列表行驻留 ``OVUF_COND_DWELL`` 同样计入。
    """
    max_01s = 0
    for row in commands or []:
        if not row or len(row) < 3:
            continue
        # 扫点测量锚点（query *IDN? / wait IDN_NOP / OVUF_COND_DWELL）
        action = str(row[1] or "").strip().lower()
        cmd = str(row[2] or "").strip().upper()
        if action == "query" and cmd in ("*IDN?", "IDN?"):
            pass
        elif action == "wait" and cmd in (
            "IDN_NOP",
            "*IDN?",
            "IDN?",
            "OVUF_COND_DWELL",
        ):
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

    # 分开录：每一段单独一条连续录（段首 ASYNC_START，段尾 WAIT_END）。
    # 扫点驻留留在 col9，电压在录波过程中继续变。
    # 禁止段首 col6 = 单点驻留：StopTime 会被收成 2 秒，第 16 条报
    # 「WT未启动录波，已跳过等待」，整段 CSV 不会出现（job114）。
    if not measures:
        return len(segs)

    ranges = []
    cursor = 0
    for seg in segs:
        n = len(seg["points"]) or 1
        if cursor >= len(measures):
            break
        last = min(cursor + n, len(measures)) - 1
        ranges.append((measures[cursor], measures[last]))
        for j in range(cursor, last + 1):
            _move_wait_to_col9(commands[measures[j]])
        cursor = last + 1
    while cursor < len(measures):
        _move_wait_to_col9(commands[measures[cursor]])
        cursor += 1

    for first_i, last_i in reversed(ranges):
        commands.insert(last_i + 1, row_wt_async_marker("WAIT_END"))
        commands.insert(first_i, row_wt_async_marker("ASYNC_START"))
    return len(ranges)


def ovuf_split_stop_str(commands) -> str:
    """分开录 StopTime：取最长那一段的扫点驻留合计，不是单点 2 秒。"""
    from utils.voltage_adaptability_commands import (
        estimate_continuous_record_01s,
        stoptime_str_from_wall_01s,
    )

    spans = []
    start = None
    for row in commands or []:
        marker = ""
        if row and len(row) > 6:
            marker = str(row[6] or "").strip().upper()
        if marker == "ASYNC_START":
            start = len(spans)
            spans.append([row])
        elif start is not None:
            spans[-1].append(row)
            if marker == "WAIT_END":
                start = None
    best = ""
    best_sec = 0
    for span in spans:
        if not any(str(r[6] if len(r) > 6 else "").strip().upper() == "WAIT_END" for r in span):
            continue
        wall, *_rest = estimate_continuous_record_01s(span)
        stop_str, stop_sec = stoptime_str_from_wall_01s(wall)
        if stop_sec >= best_sec:
            best_sec = stop_sec
            best = stop_str
    return best
