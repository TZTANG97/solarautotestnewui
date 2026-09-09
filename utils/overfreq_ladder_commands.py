# -*- coding: utf-8 -*-
"""过频降载 / 欠频升载：频率 list 台阶命令（对齐静态 QU 电压 list）。"""
from __future__ import annotations

import re
from typing import Any, List, Sequence, Tuple

from utils.time_helpers import SetTimeFunction


def parse_freq_hz_list(raw_text: str) -> List[str]:
    """逗号/空白分隔的频率 list → 规范化字符串列表（保留小数）。"""
    out: List[str] = []
    for tok in re.split(r"[,，\s]+", (raw_text or "").strip()):
        tok = tok.strip().replace("Hz", "").replace("hz", "")
        if not tok or tok.startswith("#"):
            continue
        try:
            v = float(tok)
        except ValueError:
            continue
        if abs(v - round(v)) < 1e-9:
            out.append(str(int(round(v))))
        else:
            out.append(("%.4f" % v).rstrip("0").rstrip("."))
    return out


def _empty_row():
    return ["" for _ in range(10)]


def _row_ac_write(cmd: str):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "write"
    row[2] = cmd
    return row


def _row_ac_wait(dwell_01s):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[9] = dwell_01s
    return row


def _freq_equal(a, b) -> bool:
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def append_freq_point_rows(
    out_rows: List[list],
    phase_mode: str,
    volt: str,
    freq_hz: str,
    dwell_01s,
    *,
    skip_freq_write: bool = False,
) -> None:
    """单点：改频率后驻留。

    三相必须用 INST:EDIT ALL + 一次 FREQ（对齐过欠频免疫），禁止 EACH/NSEL
    分相逐相改频：分相切换期间三相频率短暂不一致，易触发逆变器延时跳机。
    电压已在 S1 设定，台阶内不再反复写 VOLT，避免额外扰动。

    skip_freq_write: 与上一频点（或 S1）相同时只驻留、不重发 FREQ，
    避免并网后再写同一频率造成短时扰动跳机。
    """
    volt = str(volt).strip() or "230"
    freq_hz = str(freq_hz).strip()
    if not skip_freq_write:
        if phase_mode == "单相":
            out_rows.append(_row_ac_write(f"VOLT {volt}"))
            out_rows.append(_row_ac_write(f"FREQ {freq_hz}"))
        else:
            out_rows.append(_row_ac_write("INST:EDIT ALL"))
            out_rows.append(_row_ac_write(f"FREQ {freq_hz}"))
    out_rows.append(_row_ac_wait(dwell_01s))


def collect_freq_ladder_from_ui(ui_dialog) -> Tuple[List[str], str, Any, str]:
    """
    优先读 FrequencyLadder list；若为空则回退 S3~S17 勾选卡片。
    返回 (freq_list, volt, dwell_01s, source) source in ('list','cards','').
    """
    ladder = getattr(ui_dialog, "textEdit_FrequencyLadder", None)
    ladder_text = ladder.toPlainText().strip() if ladder is not None else ""
    if ladder_text:
        freqs = parse_freq_hz_list(ladder_text)
        if not freqs:
            return [], "", 0, ""
        volt_w = getattr(ui_dialog, "textEdit_FrequencyLadder_VOLT", None)
        time_w = getattr(ui_dialog, "textEdit_FrequencyLadder_TIME", None)
        time_u = getattr(ui_dialog, "comboBox_FrequencyLadder_TIME", None)
        volt = (volt_w.toPlainText().strip() if volt_w is not None else "") or "230"
        dwell_raw = (time_w.toPlainText().strip() if time_w is not None else "60") or "60"
        dwell_unit = time_u.currentText() if time_u is not None else "秒"
        dwell_01s = SetTimeFunction(float(dwell_raw), dwell_unit)
        return freqs, volt, dwell_01s, "list"

    # 旧卡片回退
    freqs = []
    volt = "230"
    dwell_01s = None
    for i in range(3, 18):
        cb = getattr(ui_dialog, f"checkBox_S{i}", None)
        if cb is None or not cb.isChecked():
            continue
        fr_w = getattr(ui_dialog, f"textEdit_S{i}_AC_FR", None)
        volt_w = getattr(ui_dialog, f"textEdit_S{i}_AC_VOLT", None)
        time_w = getattr(ui_dialog, f"textEdit_S{i}_TIME", None)
        time_u = getattr(ui_dialog, f"comboBox_S{i}_TIME", None)
        fr = (fr_w.toPlainText().strip() if fr_w is not None else "")
        if not fr:
            continue
        freqs.append(parse_freq_hz_list(fr)[0] if parse_freq_hz_list(fr) else fr)
        if volt_w is not None and volt_w.toPlainText().strip():
            volt = volt_w.toPlainText().strip()
        if time_w is not None and time_u is not None:
            raw = (time_w.toPlainText() or "").strip() or "60"
            d = SetTimeFunction(float(raw), time_u.currentText())
            dwell_01s = d if dwell_01s is None else dwell_01s  # 用第一点驻留；各点不同时按点写入
    if not freqs:
        return [], "", 0, ""
    if dwell_01s is None:
        dwell_01s = SetTimeFunction(60.0, "秒")
    return freqs, volt, dwell_01s, "cards"


def collect_freq_points_with_per_step_dwell(ui_dialog) -> Tuple[List[Tuple[str, str, Any]], str]:
    """
    返回 [(freq, volt, dwell_01s), ...] 与 source。
    list 模式：每点共用 volt/dwell；cards 模式：每点可用各自时间。
    """
    ladder = getattr(ui_dialog, "textEdit_FrequencyLadder", None)
    ladder_text = ladder.toPlainText().strip() if ladder is not None else ""
    master = getattr(ui_dialog, "checkBox_S3", None)
    if master is not None and not master.isChecked():
        return [], ""

    if ladder_text:
        freqs, volt, dwell_01s, src = collect_freq_ladder_from_ui(ui_dialog)
        if src != "list" or not freqs:
            return [], ""
        return [(f, volt, dwell_01s) for f in freqs], "list"

    points: List[Tuple[str, str, Any]] = []
    for i in range(3, 18):
        cb = getattr(ui_dialog, f"checkBox_S{i}", None)
        if cb is None or not cb.isChecked():
            continue
        fr_w = getattr(ui_dialog, f"textEdit_S{i}_AC_FR", None)
        volt_w = getattr(ui_dialog, f"textEdit_S{i}_AC_VOLT", None)
        time_w = getattr(ui_dialog, f"textEdit_S{i}_TIME", None)
        time_u = getattr(ui_dialog, f"comboBox_S{i}_TIME", None)
        fr = (fr_w.toPlainText().strip() if fr_w is not None else "")
        if not fr:
            continue
        parsed = parse_freq_hz_list(fr)
        freq = parsed[0] if parsed else fr
        volt = (volt_w.toPlainText().strip() if volt_w is not None else "") or "230"
        raw = (time_w.toPlainText().strip() if time_w is not None else "60") or "60"
        unit = time_u.currentText() if time_u is not None else "秒"
        dwell_01s = SetTimeFunction(float(raw), unit)
        points.append((freq, volt, dwell_01s))
    return points, ("cards" if points else "")


def sync_freq_list_to_legacy_cards(ui_dialog, max_cards: int = 15) -> None:
    """把 FrequencyLadder 展开写入 S3~S17，供旧 Open/Save 格式兼容。"""
    ladder = getattr(ui_dialog, "textEdit_FrequencyLadder", None)
    if ladder is None:
        return
    freqs = parse_freq_hz_list(ladder.toPlainText())
    volt_w = getattr(ui_dialog, "textEdit_FrequencyLadder_VOLT", None)
    time_w = getattr(ui_dialog, "textEdit_FrequencyLadder_TIME", None)
    time_u = getattr(ui_dialog, "comboBox_FrequencyLadder_TIME", None)
    volt = (volt_w.toPlainText().strip() if volt_w is not None else "") or "230"
    dwell = (time_w.toPlainText().strip() if time_w is not None else "") or "60"
    unit_idx = time_u.currentIndex() if time_u is not None else 0

    for i in range(max_cards):
        step = i + 3
        cb = getattr(ui_dialog, f"checkBox_S{step}", None)
        fr_w = getattr(ui_dialog, f"textEdit_S{step}_AC_FR", None)
        v_w = getattr(ui_dialog, f"textEdit_S{step}_AC_VOLT", None)
        t_w = getattr(ui_dialog, f"textEdit_S{step}_TIME", None)
        t_u = getattr(ui_dialog, f"comboBox_S{step}_TIME", None)
        if i < len(freqs):
            if cb is not None:
                cb.setChecked(True)
            if fr_w is not None:
                fr_w.setPlainText(freqs[i])
            if v_w is not None:
                v_w.setPlainText(volt)
            if t_w is not None:
                t_w.setPlainText(dwell)
            if t_u is not None:
                t_u.setCurrentIndex(unit_idx)
        else:
            if cb is not None:
                cb.setChecked(False)


def sync_legacy_cards_to_freq_list(ui_dialog) -> None:
    """打开旧设定后：若 FrequencyLadder 为空，用已勾选 S3~S17 频率拼 list。"""
    ladder = getattr(ui_dialog, "textEdit_FrequencyLadder", None)
    if ladder is None:
        return
    if ladder.toPlainText().strip():
        return
    freqs = []
    volt = None
    dwell = None
    unit_idx = None
    for i in range(3, 18):
        cb = getattr(ui_dialog, f"checkBox_S{i}", None)
        if cb is None or not cb.isChecked():
            continue
        fr_w = getattr(ui_dialog, f"textEdit_S{i}_AC_FR", None)
        fr = fr_w.toPlainText().strip() if fr_w is not None else ""
        if fr:
            freqs.append(fr)
        if volt is None:
            v_w = getattr(ui_dialog, f"textEdit_S{i}_AC_VOLT", None)
            if v_w is not None and v_w.toPlainText().strip():
                volt = v_w.toPlainText().strip()
        if dwell is None:
            t_w = getattr(ui_dialog, f"textEdit_S{i}_TIME", None)
            t_u = getattr(ui_dialog, f"comboBox_S{i}_TIME", None)
            if t_w is not None and t_w.toPlainText().strip():
                dwell = t_w.toPlainText().strip()
            if t_u is not None:
                unit_idx = t_u.currentIndex()
    if not freqs:
        return
    ladder.setPlainText(",".join(freqs))
    volt_w = getattr(ui_dialog, "textEdit_FrequencyLadder_VOLT", None)
    time_w = getattr(ui_dialog, "textEdit_FrequencyLadder_TIME", None)
    time_u = getattr(ui_dialog, "comboBox_FrequencyLadder_TIME", None)
    if volt_w is not None and volt:
        volt_w.setPlainText(volt)
    if time_w is not None and dwell:
        time_w.setPlainText(dwell)
    if time_u is not None and unit_idx is not None:
        time_u.setCurrentIndex(unit_idx)


def append_freq_ladder_commands(
    str_array_test: List[list],
    str_array_test_step: List[list],
    phase_mode: str,
    points: Sequence[Tuple[str, str, Any]],
    *,
    initial_freq: str | None = None,
) -> Tuple[int, int]:
    """把频率台阶写入命令队列。

    返回 (点数, 台阶起始下标)。initial_freq 为 S1 已设定频率时，
    首点若相同则跳过 FREQ 重写，只保留驻留。
    """
    if not points:
        return 0, len(str_array_test)
    start_index = len(str_array_test)
    step_cmds: List[list] = []
    prev_freq = (str(initial_freq).strip() if initial_freq is not None else "") or None
    for freq, volt, dwell_01s in points:
        before = len(str_array_test)
        skip = prev_freq is not None and _freq_equal(prev_freq, freq)
        append_freq_point_rows(
            str_array_test,
            phase_mode,
            volt,
            freq,
            dwell_01s,
            skip_freq_write=skip,
        )
        step_cmds.extend(str_array_test[before:])
        prev_freq = str(freq).strip()
    if step_cmds:
        str_array_test_step.append(step_cmds)
    return len(points), start_index

