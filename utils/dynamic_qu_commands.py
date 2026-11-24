# -*- coding: utf-8 -*-
"""动态 Q(U)：电压 Un% 与功率% 一一对应（同行配对），WT 连续录 1 条 QU_dyn_curve。"""

from __future__ import annotations

import re

from utils.dc_channels import s1_dc_slots
from utils.safe_shutdown import (
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
)
from utils.ac_scpi_commands import (
    append_ac_startup_from_ui,
    append_freq_set,
    append_legacy_three_phase_setpoints,
    append_volt_set,
)
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


def checked_s1_dc_channels(ui):
    """返回步骤①已勾选的直流通道 (ch, device, dc_num, label)。路数来自台架配置。"""
    out = []
    for ch, device, dc_num, label in s1_dc_slots(ui):
        cb = getattr(ui, "checkBox_S1_DC%d" % ch, None)
        if cb is None or not hasattr(cb, "isChecked") or not cb.isChecked():
            continue
        out.append((ch, device, dc_num, label))
    return out


def step1_dc_pf_matches(ui, power_pct) -> bool:
    """阶梯功率是否与步骤①各勾选直流的 PF 一致（一致则可跳过首点重复灌 IV）。"""
    try:
        target = float(power_pct)
    except (TypeError, ValueError):
        return False
    channels = checked_s1_dc_channels(ui)
    if not channels:
        return True
    for ch, _device, _dc_num, _label in channels:
        pf_w = getattr(ui, "textEdit_S1_DC%d_PF" % ch, None)
        raw = pf_w.toPlainText() if pf_w is not None and hasattr(pf_w, "toPlainText") else "100"
        try:
            pf = float(str(raw or "100").strip().replace("%", ""))
        except (TypeError, ValueError):
            pf = 100.0
        if 0 < pf <= 1:
            pf *= 100.0
        if abs(pf - target) > 1e-6:
            return False
    return True


def _append_dc_power_rows(
    ui,
    commands,
    steps,
    power_pct,
    dc_iv_resolver,
    dc_errors,
    *,
    full_chain,
):
    """按功率%重下已勾选直流通道的 IV。后续档跳过 MODE/SELECT。

    每个勾选的 DC1~DC4 各自用本通道 Vmp/Imp/Voc/Isc，统一缩放到 power_pct。
    """
    point_rows = []
    channels = checked_s1_dc_channels(ui)
    if not channels:
        dc_errors.append("功率阶梯需要至少勾选一路步骤①直流电源")
        return point_rows
    for ch, device, dc_num, label in channels:
        vmp_w = getattr(ui, "textEdit_S1_DC%d_VOLT" % ch, None)
        imp_w = getattr(ui, "textEdit_S1_DC%d_CURR" % ch, None)
        voc_w = getattr(ui, "textEdit_S1_DC%d_Voc" % ch, None)
        isc_w = getattr(ui, "textEdit_S1_DC%d_Isc" % ch, None)
        if None in (vmp_w, imp_w, voc_w, isc_w):
            dc_errors.append("%s缺少 Vmp/Imp/Voc/Isc 控件" % label)
            continue
        vmp = vmp_w.toPlainText()
        imp = imp_w.toPlainText()
        voc = voc_w.toPlainText()
        isc = isc_w.toPlainText()
        code, iv_cmds = dc_iv_resolver(vmp, imp, voc, isc, power_pct, dc_num)
        if code == "err1":
            dc_errors.append("%s@P%.0f%%赋值错误" % (label, power_pct))
        elif code == "err2":
            dc_errors.append("%s@P%.0f%%Isc超范围" % (label, power_pct))
        elif code == "err_brand":
            dc_errors.append("%sDC命令与厂家不匹配（已拦截致茂IVC混用）" % label)
        elif code == "ok" and iv_cmds:
            for cmd in iv_cmds:
                if not full_chain and (
                    "MODE" in cmd or "SELect" in cmd or "SAS:MODE" in cmd
                ):
                    continue
                row = _row_device_write(device, cmd)
                commands.append(row)
                point_rows.append(row)
    if point_rows and steps is not None:
        steps.append(point_rows)
    return point_rows


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
    power_levels = []
    dwell_01s = 0
    file_name = DEFAULT_FILE_NAME

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

        power_widget = getattr(ui, "textEdit_PowerLadder", None)
        power_levels = []
        if power_widget is not None and hasattr(power_widget, "toPlainText"):
            power_levels = parse_voltage_ladder(power_widget.toPlainText())
        # 一一对应：第 i 点功率配第 i 点电压。
        # 功率留空 → 全程步骤①功率；只填 1 个 → 全程固定该功率；
        # 多点长度不一致时按电压长度截断/补 100（与静态 QU 一致，避免整单失败）。
        if not power_levels:
            pair_powers = [None] * len(u_pct_list)
        elif len(power_levels) == 1:
            pair_powers = [power_levels[0]] * len(u_pct_list)
        elif len(power_levels) == len(u_pct_list):
            pair_powers = list(power_levels)
        else:
            pair_powers = []
            for i in range(len(u_pct_list)):
                pair_powers.append(power_levels[i] if i < len(power_levels) else 100.0)

        started = False
        prev_power = object()
        dc_full_chain_done = False
        for idx, (power_pct, pct) in enumerate(zip(pair_powers, u_pct_list)):
            point_rows = []
            if power_pct is not None and power_pct != prev_power:
                # 首点且与步骤①各路 PF 一致：不再重复灌 IV（与静态 QU 对齐）
                if idx == 0 and step1_dc_pf_matches(ui, power_pct):
                    prev_power = power_pct
                else:
                    _append_dc_power_rows(
                        ui,
                        commands,
                        steps,
                        power_pct,
                        dc_iv_resolver,
                        dc_errors,
                        full_chain=(not dc_full_chain_done),
                    )
                    dc_full_chain_done = True
                    prev_power = power_pct

            volt1 = round(base_un * pct / 100.0, 2)
            volt2 = round(base_un2 * pct / 100.0, 2)
            volt3 = round(base_un3 * pct / 100.0, 2)
            # 爱科同压：EDIT ALL + 一次 VOLT，避免 NSEL 逐相时输出掉回启机 230
            before = len(commands)
            if phase_mode == "单相":
                append_volt_set(commands, "单相", volt1)
                append_freq_set(commands, "单相", ladder_fr)
            elif abs(volt1 - volt2) < 1e-9 and abs(volt1 - volt3) < 1e-9:
                append_volt_set(commands, "三相", volt1, edit_all=True)
                append_freq_set(commands, "三相", ladder_fr, edit_all=True)
            else:
                append_legacy_three_phase_setpoints(
                    commands, volt1, volt2, volt3, ladder_fr
                )
            point_rows.extend(commands[before:])

            if not started and wt_is_checked == "1":
                row = _row_wt_async_marker("ASYNC_START")
                commands.append(row)
                point_rows.append(row)
                started = True

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

    # 配对扫：点数 = 电压点数（不是功率×电压）
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
        "power_levels": power_levels,
        "dwell_01s": int(dwell_01s),
        "file_name": file_name,
        "wt_rounds": wt_rounds,
        "band_duration_01s": band_duration_01s,
        "wt_continuous": True,
    }
