# -*- coding: utf-8 -*-
"""动态 Q(U)：电压 Un% 阶梯扫 U + WT 连续录 1 条 QU_dyn_curve。"""

from __future__ import annotations

import re

from utils.safe_shutdown import (
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
)
from utils.ac_scpi_commands import append_ac_startup_from_ui
from utils.time_helpers import SetTimeFunction

DEFAULT_FILE_NAME = "QU_dyn_curve"


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


def _row_ac_wait_empty(wait_01s):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "wait"
    row[2] = ""
    row[9] = wait_01s
    return row


def _row_wt_async_marker(marker):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[6] = marker
    return row


def _row_device_write(device, cmd):
    row = _empty_row()
    row[0] = device
    row[1] = "write"
    row[2] = cmd
    return row


def parse_voltage_ladder(text):
    """逗号/空白分隔电压 Un%(%)。"""
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


def default_dc_iv_resolver(vmp, imp, voc, isc, pf, dc_num):
    """轻量 IV（含 Chroma MODE/SELECT）；生产由 Send 注入 DCGetIVValueFunction。"""
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


def build_dynamic_qu_plan(
    ui,
    *,
    wt_config_dict=None,
    str_add_flag="0",
    project_change="0",
    existing_commands=None,
    dc_iv_resolver=None,
    per_dc_factor=None,
):
    """根据 Dialog UI 生成动态 Q(U) 命令计划。"""
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
    u_pct_list = []
    dwell_01s = 0
    file_name = DEFAULT_FILE_NAME

    need_wt = str_add_flag == "0" or (str_add_flag == "1" and project_change == "1")
    if need_wt:
        row = _empty_row()
        row[0] = "Upper_WT_Config"
        row[3] = "config_dict"
        row[4] = wt_config_dict
        commands.append(row)

    if str_add_flag == "1" and project_change == "1":
        row = _empty_row()
        row[0] = "AC"
        row[1] = "wait"
        row[2] = ""
        row[9] = 3000
        commands.append(row)

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
                "error": "动态QU 启机/等待时间格式错误",
                "dc_errors": [],
                "commands": commands,
                "steps": steps,
                "wt_type": None,
                "test_program": [],
                "wt_is_checked": "0",
                "u_pct_list": [],
                "dwell_01s": 0,
                "file_name": file_name,
                "wt_rounds": 0,
                "band_duration_01s": 0,
            }
        ac_status = ui.comboBox_S1_AC.currentText()

        append_ac_startup_from_ui(ui, commands, step_rows)

        row = _row_ac_write("OUTP ON" if ac_status == "开启" else "OUTP OFF")
        row[9] = f_ac_wait
        commands.append(row)
        step_rows.append(row)

        for ch, device, dc_num, label in (
            (1, "DC1", 0, "DC电源1"),
            (2, "DC2", 1, "DC电源2"),
            (3, "DC3", 2, "DC电源3"),
            (4, "DC4", 3, "DC电源4"),
        ):
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
        ladder_text = ui.textEdit_VoltageLadder.toPlainText()
        u_pct_list = parse_voltage_ladder(ladder_text)
        if not u_pct_list:
            return {
                "ok": False,
                "error": "动态QU 电压阶梯未填写或格式错误",
                "dc_errors": dc_errors,
                "commands": commands,
                "steps": steps,
                "wt_type": wt_type,
                "test_program": test_program,
                "wt_is_checked": wt_is_checked,
                "u_pct_list": [],
                "dwell_01s": 0,
                "file_name": file_name,
                "wt_rounds": 0,
                "band_duration_01s": 0,
            }
        try:
            dwell_01s = SetTimeFunction(
                float(ui.textEdit_VoltageLadder_TIME.toPlainText()),
                ui.comboBox_VoltageLadder_TIME.currentText(),
            )
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "动态QU 驻留时间格式错误",
                "dc_errors": dc_errors,
                "commands": commands,
                "steps": steps,
                "wt_type": wt_type,
                "test_program": test_program,
                "wt_is_checked": wt_is_checked,
                "u_pct_list": u_pct_list,
                "dwell_01s": 0,
                "file_name": file_name,
                "wt_rounds": 0,
                "band_duration_01s": 0,
            }

        try:
            base_un = float(
                (ui.textEdit_VoltageLadder_Un.toPlainText() or "").strip()
                or ui.textEdit_S1_AC_VOLT.toPlainText()
                or "230"
            )
        except ValueError:
            base_un = 230.0
        ladder_fr = (
            (ui.textEdit_VoltageLadder_FR.toPlainText() or "").strip()
            or ui.textEdit_S1_AC_FR.toPlainText().strip()
            or "50"
        )
        try:
            base_un2 = float(ui.textEdit_S1_AC_VOLT_2.toPlainText().strip() or base_un)
        except ValueError:
            base_un2 = base_un
        try:
            base_un3 = float(ui.textEdit_S1_AC_VOLT_3.toPlainText().strip() or base_un)
        except ValueError:
            base_un3 = base_un

        for idx, pct in enumerate(u_pct_list):
            point_rows = []
            volt1 = round(base_un * pct / 100.0, 2)
            volt2 = round(base_un2 * pct / 100.0, 2)
            volt3 = round(base_un3 * pct / 100.0, 2)
            if phase_mode == "单相":
                for cmd in ("VOLT %s" % volt1, "FREQ %s" % ladder_fr):
                    row = _row_ac_write(cmd)
                    commands.append(row)
                    point_rows.append(row)
            else:
                for nsel, vv in ((1, volt1), (2, volt2), (3, volt3)):
                    for cmd in ("INST:NSEL %d" % nsel, "VOLT %s" % vv, "FREQ %s" % ladder_fr):
                        row = _row_ac_write(cmd)
                        commands.append(row)
                        point_rows.append(row)

            if idx == 0 and wt_is_checked == "1":
                row = _row_wt_async_marker("ASYNC_START")
                commands.append(row)
                point_rows.append(row)

            wait = _row_ac_wait_empty(int(dwell_01s))
            commands.append(wait)
            point_rows.append(wait)
            steps.append(point_rows)

        if u_pct_list and wt_is_checked == "1":
            row = _row_wt_async_marker("WAIT_END")
            commands.append(row)

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

    band_duration_01s = int(dwell_01s) * len(u_pct_list) if u_pct_list else 0
    wt_rounds = 1 if (wt_is_checked == "1" and u_pct_list) else 0

    return {
        "ok": True,
        "error": "",
        "dc_errors": dc_errors,
        "commands": commands,
        "steps": steps,
        "wt_type": wt_type,
        "test_program": test_program,
        "wt_is_checked": wt_is_checked,
        "u_pct_list": u_pct_list,
        "dwell_01s": int(dwell_01s),
        "file_name": file_name,
        "wt_rounds": wt_rounds,
        "band_duration_01s": band_duration_01s,
        "wt_continuous": True,
    }
