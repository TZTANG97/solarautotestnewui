from utils.dc_channels import s1_dc_slots
# -*- coding: utf-8 -*-
"""ROCOF保护：按设定 Hz/s 扫频（df/dt），连续录。"""

from utils.time_helpers import SetTimeFunction
from utils.frequency_adaptability_commands import (
    _empty_row,
    _row_ac_write,
    _row_ac_wait_idn,
    _row_wt_async_marker,
    _row_device_write,
    _fmt_freq,
    default_dc_iv_resolver,
    read_update_rate,
)
from utils.ac_scpi_commands import (
    append_ac_startup_from_ui,
    append_freq_set,
    resolve_chroma_61800,
)
from utils.safe_shutdown import (
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
)


def build_rocof_step_list(freq_start, freq_end, rate_hz_s, dt_s=0.05):
    """按 ROCOF(Hz/s) 与步间隔 dt 生成频率点。"""
    start = str(freq_start).strip()
    end = str(freq_end).strip()
    if not start and not end:
        return [], 0.0
    if not start:
        start = end
    if not end:
        end = start
    f0 = float(start)
    f1 = float(end)
    rate = abs(float(rate_hz_s))
    if rate <= 0 or f0 == f1:
        return [_fmt_freq(f0)], 0.0
    step = max(rate * float(dt_s), 1e-6)
    out = []
    cur = f0
    ascending = f1 > f0
    for _ in range(20000):
        out.append(_fmt_freq(round(cur, 4)))
        if ascending:
            if cur >= f1 - 1e-9:
                break
            cur = min(cur + step, f1)
        else:
            if cur <= f1 + 1e-9:
                break
            cur = max(cur - step, f1)
    if not out or abs(float(out[-1]) - f1) > 1e-6:
        out.append(_fmt_freq(round(f1, 4)))
    sweep_s = abs(f1 - f0) / rate
    return out, sweep_s


def append_rocof_band(
    out_rows,
    phase_mode,
    freq_start,
    freq_end,
    rate_hz_s,
    hold_01s,
    *,
    dt_s,
    wt_first_trigger,
    chroma_61800=None,
):
    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()
    steps, sweep_s = build_rocof_step_list(freq_start, freq_end, rate_hz_s, dt_s=dt_s)
    if not steps:
        return False, "ROCOF 频率区间未填写", None, False, 0.0
    wait_01s = max(1, int(round(float(dt_s) * 10)))
    triggered = False
    multi = len(steps) > 1
    for i, step in enumerate(steps):
        if wt_first_trigger and not triggered:
            out_rows.append(_row_wt_async_marker("ASYNC_START"))
            triggered = True
        edit_all = (i == 0) if chroma_61800 and phase_mode == "三相" else True
        append_freq_set(
            out_rows,
            phase_mode,
            step,
            edit_all=edit_all,
            chroma_61800=chroma_61800,
        )
        if multi and i < len(steps) - 1:
            out_rows.append(_row_ac_wait_idn(wait_01s, slot=9))
    hold = int(hold_01s) if hold_01s else 0
    if hold > 0:
        out_rows.append(_row_ac_wait_idn(hold, slot=9))
    return True, "", steps[-1], triggered, sweep_s


def append_enabled_rocof_bands(
    ui,
    out_rows,
    phase_mode,
    step_nums,
    *,
    dt_s,
    wt_armed=False,
    chroma_61800=None,
):
    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()
    page_cb = getattr(ui, "checkBox_rocof_page", None)
    if page_cb is not None and not page_cb.isChecked():
        return True, "", [], wt_armed, 0.0

    metas = []
    total_sweep = 0.0
    for sn in step_nums:
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is None or not cb.isChecked():
            continue
        te_start = getattr(ui, "textEdit_S%d_freq_start_rocof" % sn, None)
        te_end = getattr(ui, "textEdit_S%d_freq_end_rocof" % sn, None)
        te_rate = getattr(ui, "textEdit_S%d_rocof_hz_s_rocof" % sn, None)
        te_dur = getattr(ui, "textEdit_S%d_test_duration_rocof" % sn, None)
        cmb_unit = getattr(ui, "comboBox_S%d_test_time_unit_rocof" % sn, None)
        if te_start is None or te_end is None or te_rate is None:
            return False, "ROCOF step%d 控件缺失" % sn, [], wt_armed, 0.0
        freq_start = te_start.toPlainText().strip()
        freq_end = te_end.toPlainText().strip()
        rate_txt = te_rate.toPlainText().strip()
        if not freq_start and not freq_end:
            return False, "ROCOF step%d 频率区间未填写" % sn, [], wt_armed, 0.0
        if not rate_txt:
            return False, "ROCOF step%d 变化率未填写" % sn, [], wt_armed, 0.0
        try:
            rate = float(rate_txt)
        except (TypeError, ValueError):
            return False, "ROCOF step%d 变化率格式错误" % sn, [], wt_armed, 0.0
        if rate <= 0:
            return False, "ROCOF step%d 变化率必须大于 0" % sn, [], wt_armed, 0.0
        hold_01s = 20
        if te_dur is not None and cmb_unit is not None and te_dur.toPlainText().strip():
            try:
                hold_01s = SetTimeFunction(float(te_dur.toPlainText().strip()), cmb_unit.currentText())
            except (TypeError, ValueError):
                return False, "ROCOF step%d 终点保持时间格式错误" % sn, [], wt_armed, 0.0

        ok, err, _end, triggered, sweep_s = append_rocof_band(
            out_rows,
            phase_mode,
            freq_start,
            freq_end,
            rate,
            hold_01s,
            dt_s=dt_s,
            wt_first_trigger=wt_armed,
            chroma_61800=chroma_61800,
        )
        if not ok:
            return False, err, [], wt_armed, 0.0
        if triggered:
            wt_armed = False
        total_sweep += sweep_s + (float(hold_01s) / 10.0)
        safe_r = ("%.2f" % rate).replace(".", "p")
        metas.append({
            "name": "ROCOF_S%d_%sHzps" % (sn, safe_r),
            "duration_01s": int(round(sweep_s * 10)) + int(hold_01s),
            "step": sn,
            "rate": rate,
        })
    return True, "", metas, wt_armed, total_sweep


def resolve_rocof_file_name_list(band_metas, existing_names=None):
    existing = [str(p).strip() for p in (existing_names or []) if str(p).strip()]
    if len(existing) == 1:
        return existing
    auto = [str(m.get("name") or "").strip() for m in (band_metas or []) if m]
    auto = [n for n in auto if n]
    if auto and len(existing) == len(auto):
        return existing
    return ["ROCOF_protect"]


def build_rocof_plan(
    ui,
    *,
    wt_config_dict=None,
    str_add_flag="0",
    project_change="0",
    existing_commands=None,
    dc_iv_resolver=None,
    per_dc_factor=None,
    chroma_61800=None,
):
    if wt_config_dict is None:
        wt_config_dict = {}
    if dc_iv_resolver is None:
        dc_iv_resolver = default_dc_iv_resolver
    if chroma_61800 is None:
        chroma_61800 = resolve_chroma_61800()

    commands = list(existing_commands or [])
    if str_add_flag == "0":
        commands = []

    steps = []
    dc_errors = []
    test_program = []
    wt_type = None
    wt_is_checked = "0"

    need_wt = True  # 同项目追加也刷新 WT 文件名，避免多轮覆盖
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
        f_s1 = SetTimeFunction(float(ui.textEdit_S1_TIME.toPlainText()), ui.comboBox_S1_TIME.currentText())
        f_ac_wait = SetTimeFunction(
            float(ui.textEdit_S1_ACWaitTIME.toPlainText()),
            ui.comboBox_S1_ACWaitTIME.currentText(),
        )
        ac_status = ui.comboBox_S1_AC.currentText()

        append_ac_startup_from_ui(ui, commands, step_rows, chroma_61800=chroma_61800)

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

    ok_rate, rate_err, rate_interval_s, _per = read_update_rate(ui)
    if not ok_rate and rate_err:
        rate_interval_s = 0.05
    dt_s = float(rate_interval_s) if rate_interval_s else 0.05

    band_rows = []
    wt_armed = wt_is_checked == "1"
    ok_bands, band_err, band_metas, wt_armed, total_sweep = append_enabled_rocof_bands(
        ui,
        band_rows,
        phase_mode,
        list(range(3, 9)),
        dt_s=dt_s,
        wt_armed=wt_armed,
        chroma_61800=chroma_61800,
    )
    if not ok_bands:
        return {
            "ok": False, "error": band_err, "dc_errors": dc_errors,
            "commands": commands, "steps": steps, "wt_type": wt_type,
            "test_program": test_program, "wt_is_checked": wt_is_checked,
            "band_metas": [], "file_names": [], "wt_rounds": 0,
            "wt_continuous": False, "band_duration_01s": 0,
        }

    if wt_is_checked == "1" and band_rows and any(
        len(r) > 6 and str(r[6]).strip().upper() == "ASYNC_START" for r in band_rows
    ):
        band_rows.append(_row_wt_async_marker("WAIT_END"))

    commands.extend(band_rows)
    if band_rows:
        steps.append(list(band_rows))

    file_names = resolve_rocof_file_name_list(band_metas)
    wt_rounds = 1 if (wt_is_checked == "1" and band_metas) else 0
    band_duration_01s = sum(int(m.get("duration_01s") or 0) for m in band_metas)

    if ui.checkBox_S_End.isChecked():
        dc_channels = enabled_shutdown_dc_channels(
            ui, end_fmt="checkBox_S_End_DC%d"
        )
        step_rows = build_forced_shutdown_rows(
            dc_channels=dc_channels,
            per_dc_factor=per_dc_factor,
        )
        commands.extend(step_rows)
        steps.append(step_rows)

    return {
        "ok": True, "error": None, "dc_errors": dc_errors,
        "commands": commands, "steps": steps, "wt_type": wt_type,
        "test_program": test_program, "wt_is_checked": wt_is_checked,
        "band_metas": band_metas, "file_names": file_names,
        "wt_rounds": wt_rounds, "wt_continuous": wt_rounds == 1,
        "band_duration_01s": band_duration_01s,
        "max_band_duration_01s": band_duration_01s,
    }
