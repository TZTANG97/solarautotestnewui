# -*- coding: utf-8 -*-
"""交流源 SCPI 命令规划：连接识别 Chroma 61800 后全项目统一分支，勿在各试验重复写。"""

from __future__ import annotations

from utils.ac_source_catalog_sync import get_ac_scpi_verb


def _ac_volt_verb(*, chroma_61800: bool) -> str:
    default = "VOLT:AC" if chroma_61800 else "VOLT"
    fam = "61800" if chroma_61800 else "AC_GENERIC"
    return get_ac_scpi_verb("VOLT", default, family=fam)


def _fmt_volt_cmd(value, *, chroma_61800: bool) -> str:
    return f"{_ac_volt_verb(chroma_61800=chroma_61800)} {value}"


def _empty_row():
    return ["" for _ in range(10)]


def _row_ac_write(cmd):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "write"
    row[2] = cmd
    return row

_VOLT_STEP = 0.1


def resolve_chroma_61800(ac_controller=None) -> bool:
    """已连接 AC 且 *IDN? 为 Chroma 61800 时返回 True；未连接则 False。"""
    if ac_controller is not None:
        try:
            return bool(ac_controller.connected and ac_controller.is_chroma_61800())
        except Exception:
            return False
    try:
        import SCPITestWave as sw

        ctrl = getattr(sw, "ac_controller", None)
        if ctrl is not None and getattr(ctrl, "connected", False):
            return ctrl.is_chroma_61800()
    except Exception:
        pass
    return False


def _resolve_three_phase_volts(volt_a, volt_b=None, volt_c=None):
    a = str(volt_a or "").strip()
    b = str(volt_b or "").strip()
    c = str(volt_c or "").strip()
    fallback = a or b or c
    if not fallback:
        return None, None, None
    return a or fallback, b or fallback, c or fallback


def fmt_ac_volt(value, chroma_61800=False):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value).strip()
    if chroma_61800:
        v = round(v / _VOLT_STEP) * _VOLT_STEP
        v = round(v, 1)
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return "%.1f" % v
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return str(v)


def append_legacy_three_phase_setpoints(out_rows, volt_a, volt_b, volt_c, freq):
    """非 61800（含爱科）：同压用 EDIT ALL + 一次 VOLT/FREQ；异压才 EACH+NSEL，最后回到 EDIT ALL。"""
    ra, rb, rc = _resolve_three_phase_volts(volt_a, volt_b, volt_c)
    if not ra:
        return
    fr = str(freq).strip()
    # 与 devices/ac_controller._generic_scpi_three_phase_command_list / 国产矩阵一致
    if ra == rb == rc:
        for cmd in (
            "INST:PHAS THREE",
            "INST:EDIT ALL",
            _fmt_volt_cmd(ra, chroma_61800=False),
            f"FREQ {fr}",
        ):
            out_rows.append(_row_ac_write(cmd))
        return
    for cmd in ("INST:PHAS THREE", "INST:EDIT EACH"):
        out_rows.append(_row_ac_write(cmd))
    for idx, volt in enumerate((ra, rb, rc), start=1):
        for cmd in (
            f"INST:NSEL {idx}",
            _fmt_volt_cmd(volt, chroma_61800=False),
            f"FREQ {fr}",
        ):
            out_rows.append(_row_ac_write(cmd))
    # 恢复三相联动，避免爱科 0x0C48 留在独立模式导致只跟一相
    out_rows.append(_row_ac_write("INST:EDIT ALL"))


def append_chroma_phase_volts(out_rows, volt_a, volt_b, volt_c):
    """Chroma 61800 仅写三相电压（扫压/恢复用，不改频率）。

    同压：``PHAS:THREE SAMEFREQ`` + EACH 逐相 + ``EDIT ALL`` 再写一次；
    异压：``PHAS:THREE INDEPEND`` + EACH 逐相（留在独立模式，便于下一步异压）。
    """
    ra, rb, rc = _resolve_three_phase_volts(volt_a, volt_b, volt_c)
    if not ra:
        return
    va = fmt_ac_volt(ra, chroma_61800=True)
    vb = fmt_ac_volt(rb, chroma_61800=True)
    vc = fmt_ac_volt(rc, chroma_61800=True)
    mode = "PHAS:THREE SAMEFREQ" if va == vb == vc else "PHAS:THREE INDEPEND"
    for cmd in ("CONF:COUP AC", "INST:PHAS THREE", mode, "INST:EDIT EACH"):
        out_rows.append(_row_ac_write(cmd))
    for nsel, v in ((1, va), (2, vb), (3, vc)):
        out_rows.append(_row_ac_write(f"INST:NSEL {nsel}"))
        out_rows.append(_row_ac_write(_fmt_volt_cmd(v, chroma_61800=True)))
    if va == vb == vc:
        out_rows.append(_row_ac_write("INST:EDIT ALL"))
        out_rows.append(_row_ac_write(_fmt_volt_cmd(va, chroma_61800=True)))


def append_chroma_three_phase_setpoints(out_rows, volt_a, volt_b, volt_c, freq):
    ra, rb, rc = _resolve_three_phase_volts(volt_a, volt_b, volt_c)
    if not ra:
        return
    va = fmt_ac_volt(ra, chroma_61800=True)
    vb = fmt_ac_volt(rb, chroma_61800=True)
    vc = fmt_ac_volt(rc, chroma_61800=True)
    fr = str(freq).strip()
    mode = "PHAS:THREE SAMEFREQ" if va == vb == vc else "PHAS:THREE INDEPEND"
    for cmd in ("CONF:COUP AC", "INST:PHAS THREE", mode, "INST:EDIT EACH"):
        out_rows.append(_row_ac_write(cmd))
    for nsel, v in ((1, va), (2, vb), (3, vc)):
        out_rows.append(_row_ac_write(f"INST:NSEL {nsel}"))
        out_rows.append(_row_ac_write(_fmt_volt_cmd(v, chroma_61800=True)))
        out_rows.append(_row_ac_write(f"FREQ {fr}"))
    if va == vb == vc:
        out_rows.append(_row_ac_write("INST:EDIT ALL"))
        out_rows.append(_row_ac_write(_fmt_volt_cmd(va, chroma_61800=True)))
        out_rows.append(_row_ac_write(f"FREQ {fr}"))


def append_single_phase_setpoints(out_rows, volt, freq, chroma_61800=False):
    fr = str(freq).strip()
    if chroma_61800:
        for cmd in ("CONF:COUP AC", "INST:PHAS SINGLE", "INST:EDIT ALL"):
            out_rows.append(_row_ac_write(cmd))
        volt_cmd = _fmt_volt_cmd(fmt_ac_volt(volt, chroma_61800=True), chroma_61800=True)
    else:
        for cmd in ("INST:PHAS SINGLE", "INST:EDIT ALL"):
            out_rows.append(_row_ac_write(cmd))
        volt_cmd = _fmt_volt_cmd(str(volt).strip(), chroma_61800=False)
    for cmd in (volt_cmd, "FREQ " + fr):
        out_rows.append(_row_ac_write(cmd))


def append_ac_startup_setpoints(
    out_rows,
    phase_mode,
    volt_a,
    volt_b,
    volt_c,
    freq,
    *,
    chroma_61800=None,
):
    """启机：单相/三相电压频率。chroma_61800=None 时按当前连接的 AC 自动识别。"""
    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()
    if phase_mode == "单相":
        append_single_phase_setpoints(out_rows, volt_a, freq, chroma_61800=chroma_61800)
    elif phase_mode == "三相":
        if chroma_61800:
            append_chroma_three_phase_setpoints(out_rows, volt_a, volt_b, volt_c, freq)
        else:
            append_legacy_three_phase_setpoints(out_rows, volt_a, volt_b, volt_c, freq)


def append_volt_set(
    out_rows,
    phase_mode,
    volt_v,
    *,
    edit_all=True,
    chroma_61800=None,
):
    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()
    v = fmt_ac_volt(volt_v, chroma_61800=chroma_61800)
    volt_cmd = _fmt_volt_cmd(v, chroma_61800=chroma_61800)
    if phase_mode == "单相":
        out_rows.append(_row_ac_write(volt_cmd))
        return
    if edit_all and not chroma_61800:
        out_rows.append(_row_ac_write("INST:EDIT ALL"))
    out_rows.append(_row_ac_write(volt_cmd))


def append_freq_set(
    out_rows,
    phase_mode,
    freq_hz,
    *,
    edit_all=True,
    chroma_61800=None,
):
    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()
    freq_cmd = "FREQ " + str(freq_hz).strip()
    if phase_mode == "单相":
        out_rows.append(_row_ac_write(freq_cmd))
        return
    if edit_all:
        out_rows.append(_row_ac_write("INST:EDIT ALL"))
    out_rows.append(_row_ac_write(freq_cmd))


def append_ac_startup_from_ui(ui, commands, step_rows, *, chroma_61800=None):
    """从标准 step1 控件写入启机 AC 命令，并追加到 step_rows。"""
    phase_mode = ui.comboBox_S1_AC_2.currentText()
    batch_start = len(commands)
    append_ac_startup_setpoints(
        commands,
        phase_mode,
        ui.textEdit_S1_AC_VOLT.toPlainText(),
        ui.textEdit_S1_AC_VOLT_2.toPlainText(),
        ui.textEdit_S1_AC_VOLT_3.toPlainText(),
        ui.textEdit_S1_AC_FR.toPlainText(),
        chroma_61800=chroma_61800,
    )
    step_rows.extend(commands[batch_start:])
