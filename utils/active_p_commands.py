# -*- coding: utf-8 -*-
"""有功调度：P 指令阶梯（%Pn）逐档改写直流曲线，数字 col6 逐点存盘。"""

from __future__ import annotations

from utils.dc_channels import s1_dc_slots

import re

from utils.matrix_recording_commands import (
    append_matrix_dwell,
    get_record_mode,
    maybe_async_end,
    maybe_async_start,
    resolve_wt_rounds,
)
from utils.wt_recording_mode import MODE_CONTINUOUS
from utils.safe_shutdown import (
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
)
from utils.ac_scpi_commands import append_ac_startup_from_ui
from utils.time_helpers import SetTimeFunction


def _empty_row():
    return ["" for _ in range(10)]


def _row_ac_write(cmd):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "write"
    row[2] = cmd
    return row


def _row_ac_wait_idn(wait_01s, slot=9):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[slot] = wait_01s
    return row


def _row_device_write(device, cmd):
    row = _empty_row()
    row[0] = device
    row[1] = "write"
    row[2] = cmd
    return row


def parse_ladder(text):
    vals = []
    for tok in re.split(r"[,，\s]+", (text or "").strip()):
        tok = tok.strip().replace("%", "")
        if not tok or tok.startswith("#"):
            continue
        try:
            vals.append(float(tok))
        except ValueError:
            continue
    return vals


def _skip_mode_on_later_point(cmd):
    """后续功率档不再重发「进入表格模式」，但必须重发曲线生效命令。

    致茂改完 IVC:IT / IVC:VT 后若不重发 IVCurve:SELect，输出口仍停在上一档。
    """
    text = str(cmd or "").upper()
    if "SELECT" in text:
        return False
    return "MODE" in text


def _dc_percent_for_step(ladder_pct, headroom_pct):
    """本档直流功率% = P 指令% × 头寸%。头寸 100 时与 P 指令相同。"""
    try:
        ladder = float(ladder_pct)
    except (TypeError, ValueError):
        ladder = 0.0
    try:
        headroom = float(headroom_pct)
    except (TypeError, ValueError):
        headroom = 100.0
    if headroom < 0:
        headroom = 0.0
    return ladder * headroom / 100.0


def format_setpoint_tag(value):
    s = ("%g" % value).replace(".", "p")
    if s.startswith("-"):
        return "m" + s[1:]
    return s


def default_dc_iv_resolver(vmp, imp, voc, isc, pf, dc_num):
    try:
        f_vmp = float(str(vmp).strip())
        f_imp = float(str(imp).strip())
        f_voc = float(str(voc).strip())
        f_isc = float(str(isc).strip())
        f_pf = float(str(pf).strip().rstrip("%"))
    except (TypeError, ValueError):
        return "err1", None
    if min(f_vmp, f_imp, f_voc, f_isc) <= 0:
        return "err1", None
    if f_imp >= f_isc or f_vmp >= f_voc:
        return "err1", None
    if f_isc > 1000:
        return "err2", None
    scale = max(f_pf, 0.0) / 100.0
    _ = dc_num
    return "ok", [
        "OUTP:MODE TABLE",
        "IVC:IT %.3f,%.3f" % (f_imp * scale, f_isc * scale),
        "IVC:VT %.3f,%.3f" % (f_vmp, f_voc),
        "IVCurve:SELect 1",
    ]


def build_active_p_plan(
    ui,
    *,
    wt_config_dict=None,
    str_add_flag="0",
    project_change="0",
    existing_commands=None,
    dc_iv_resolver=None,
    per_dc_factor=None,
):
    if wt_config_dict is None:
        wt_config_dict = {}
    if dc_iv_resolver is None:
        dc_iv_resolver = default_dc_iv_resolver

    commands = list(existing_commands or [])
    if str_add_flag == "0":
        commands = []

    steps = []
    dc_errors = []
    test_program = []
    wt_type = None
    wt_is_checked = "0"
    power_levels = []
    file_names = []
    dwell_01s = 0
    dc_pct = 100.0

    need_wt = True  # 同项目追加也刷新 WT 文件名，避免多轮覆盖
    if need_wt:
        row = _empty_row()
        row[0] = "Upper_WT_Config"
        row[3] = "config_dict"
        row[4] = wt_config_dict
        commands.append(row)

    if str_add_flag == "1" and project_change == "1":
        from utils.wt_recording_mode import insert_project_gap_before_last_wt_config
        commands[:] = insert_project_gap_before_last_wt_config(commands)

    phase_mode = ui.comboBox_S1_AC_2.currentText()

    if ui.checkBox_S1.isChecked():
        step_rows = []
        try:
            f_s1 = SetTimeFunction(float(ui.textEdit_S1_TIME.toPlainText()), ui.comboBox_S1_TIME.currentText())
            f_ac_wait = SetTimeFunction(
                float(ui.textEdit_S1_ACWaitTIME.toPlainText()),
                ui.comboBox_S1_ACWaitTIME.currentText(),
            )
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "有功调度 启机/等待时间格式错误",
                "dc_errors": [],
                "commands": commands,
                "steps": steps,
                "wt_type": None,
                "test_program": [],
                "wt_is_checked": "0",
                "power_levels": [],
                "file_names": [],
                "dwell_01s": 0,
                "dc_pct": dc_pct,
                "wt_rounds": 0,
            }
        ac_status = ui.comboBox_S1_AC.currentText()

        append_ac_startup_from_ui(ui, commands, step_rows)

        row = _row_ac_write("OUTP ON" if ac_status == "开启" else "OUTP OFF")
        row[9] = f_ac_wait
        commands.append(row)
        step_rows.append(row)

        for ch, device, dc_num, label in s1_dc_slots(ui):
            if not getattr(ui, "checkBox_S1_DC%d" % ch).isChecked():
                continue
            vmp = getattr(ui, "textEdit_S1_DC%d_VOLT" % ch).toPlainText()
            imp = getattr(ui, "textEdit_S1_DC%d_CURR" % ch).toPlainText()
            voc = getattr(ui, "textEdit_S1_DC%d_Voc" % ch).toPlainText()
            isc = getattr(ui, "textEdit_S1_DC%d_Isc" % ch).toPlainText()
            pf = getattr(ui, "textEdit_S1_DC%d_PF" % ch).toPlainText()
            code, iv_cmds = dc_iv_resolver(vmp, imp, voc, isc, pf, dc_num)
            if code == "err1":
                dc_errors.append("%s赋值错误" % label)
            elif code == "err2":
                dc_errors.append("%sIsc,Imp赋值超范围" % label)
            elif code == "err_brand":
                dc_errors.append("%sDC命令与厂家不匹配（已拦截致茂IVC混用）" % label)
            elif code == "ok" and iv_cmds:
                wait = _row_ac_wait_idn(2, slot=8)
                commands.append(wait)
                step_rows.append(wait)
                for cmd in iv_cmds:
                    row = _row_device_write(device, cmd)
                    commands.append(row)
                    step_rows.append(row)
            status = getattr(ui, "comboBox_S1_DC%d" % ch).currentText()
            row = _row_device_write(device, "OUTP ON" if status == "开启" else "OUTP OFF")
            commands.append(row)
            step_rows.append(row)
            wait = _row_ac_wait_idn(2, slot=8)
            commands.append(wait)
            step_rows.append(wait)

        wait = _row_ac_wait_idn(f_s1)
        commands.append(wait)
        step_rows.append(wait)
        steps.append(step_rows)

    if ui.checkBox_S2.isChecked():
        wt_is_checked = "1"
        if need_wt:
            if ui.radioButton_S2_WT3000.isChecked():
                wt_type = "WT3000"
            elif ui.radioButton_S2_WT1800.isChecked():
                wt_type = "WT1800"
            elif ui.radioButton_S2_WT1806E.isChecked():
                wt_type = "WT1806E"
            elif ui.radioButton_S2_WT5000.isChecked():
                wt_type = "WT5000"
            if wt_type:
                test_program.append(["12", wt_type])

    if ui.checkBox_S3.isChecked():
        power_levels = parse_ladder(ui.textEdit_PowerLadder.toPlainText())
        dc_vals = parse_ladder(getattr(ui, "textEdit_DcPowerPct", None).toPlainText() if hasattr(ui, "textEdit_DcPowerPct") else "100")
        dc_pct = dc_vals[0] if dc_vals else 100.0
        if not power_levels:
            return {
                "ok": False,
                "error": "有功调度 P 指令阶梯未填写或格式错误",
                "dc_errors": dc_errors,
                "commands": commands,
                "steps": steps,
                "wt_type": wt_type,
                "test_program": test_program,
                "wt_is_checked": wt_is_checked,
                "power_levels": [],
                "file_names": [],
                "dwell_01s": 0,
                "dc_pct": dc_pct,
                "wt_rounds": 0,
            }
        try:
            dwell_01s = SetTimeFunction(
                float(ui.textEdit_S3_TIME_2.toPlainText()),
                ui.comboBox_S3_TIME_2.currentText(),
            )
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "有功调度 驻留时间格式错误",
                "dc_errors": dc_errors,
                "commands": commands,
                "steps": steps,
                "wt_type": wt_type,
                "test_program": test_program,
                "wt_is_checked": wt_is_checked,
                "power_levels": power_levels,
                "file_names": [],
                "dwell_01s": 0,
                "dc_pct": dc_pct,
                "wt_rounds": 0,
            }

        record_mode = get_record_mode(ui)
        wt_continuous = record_mode == MODE_CONTINUOUS
        point_index = 0
        total_points = len(power_levels)
        split_names = []

        for pct in power_levels:
            point_rows = []
            maybe_async_start(
                commands,
                point_rows,
                wt_continuous=wt_continuous,
                wt_is_checked=wt_is_checked,
                point_index=point_index,
            )
            for ch, device, dc_num, label in s1_dc_slots(ui):
                s1_on = getattr(ui, "checkBox_S1_DC%d" % ch).isChecked()
                s3_on = getattr(ui, "checkBox_S3_DC%d" % ch).isChecked()
                if not (s1_on and s3_on):
                    continue
                step_pct = _dc_percent_for_step(pct, dc_pct)
                if step_pct <= 0:
                    # 0% 电流做不出合法 IV 曲线，直接关输出，否则直流会停在上一档。
                    row = _row_device_write(device, "OUTP OFF")
                    commands.append(row)
                    point_rows.append(row)
                    continue
                vmp = getattr(ui, "textEdit_S1_DC%d_VOLT" % ch).toPlainText()
                imp = getattr(ui, "textEdit_S1_DC%d_CURR" % ch).toPlainText()
                voc = getattr(ui, "textEdit_S1_DC%d_Voc" % ch).toPlainText()
                isc = getattr(ui, "textEdit_S1_DC%d_Isc" % ch).toPlainText()
                code, iv_cmds = dc_iv_resolver(vmp, imp, voc, isc, step_pct, dc_num)
                if code == "err1":
                    dc_errors.append("%s@Pcmd%.0f%%赋值错误" % (label, pct))
                elif code == "err2":
                    dc_errors.append("%s@Pcmd%.0f%%Isc超范围" % (label, pct))
                elif code == "err_brand":
                    dc_errors.append("%sDC命令与厂家不匹配（已拦截致茂IVC混用）" % label)
                elif code == "ok" and iv_cmds:
                    row = _row_device_write(device, "OUTP ON")
                    commands.append(row)
                    point_rows.append(row)
                    for cmd in iv_cmds:
                        if point_index > 0 and _skip_mode_on_later_point(cmd):
                            continue
                        row = _row_device_write(device, cmd)
                        commands.append(row)
                        point_rows.append(row)

            append_matrix_dwell(
                commands, point_rows, dwell_01s, wt_continuous=wt_continuous
            )
            steps.append(point_rows)
            split_names.append("Pdisp_P%s" % format_setpoint_tag(pct))
            point_index += 1

        if wt_continuous and wt_is_checked == "1" and total_points > 0:
            file_names = ["Pdisp_BR"]
        else:
            file_names = split_names
        maybe_async_end(
            commands,
            wt_continuous=wt_continuous,
            wt_is_checked=wt_is_checked,
            total_points=total_points,
        )

    if ui.checkBox_S_END.isChecked():
        dc_channels = enabled_shutdown_dc_channels(
            ui, end_fmt="checkBox_S_END_DC%d"
        )
        step_rows = build_forced_shutdown_rows(
            dc_channels=dc_channels,
            per_dc_factor=per_dc_factor,
        )
        commands.extend(step_rows)
        steps.append(step_rows)

    wt_continuous_flag = (
        get_record_mode(ui) == MODE_CONTINUOUS if ui.checkBox_S3.isChecked() else False
    )
    wt_rounds = resolve_wt_rounds(wt_is_checked, file_names, wt_continuous_flag)
    return {
        "ok": True,
        "error": "",
        "dc_errors": dc_errors,
        "commands": commands,
        "steps": steps,
        "wt_type": wt_type,
        "test_program": test_program,
        "wt_is_checked": wt_is_checked,
        "power_levels": power_levels,
        "file_names": file_names,
        "dwell_01s": dwell_01s,
        "dc_pct": dc_pct,
        "wt_rounds": wt_rounds,
        "wt_continuous": wt_continuous_flag,
        "record_mode": get_record_mode(ui) if ui.checkBox_S3.isChecked() else "",
    }
