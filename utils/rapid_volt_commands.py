from utils.dc_channels import s1_dc_slots
# -*- coding: utf-8 -*-
"""快速电压变化：AC 电压阶跃（起压→阶跃到终点→保持），连续录。"""

from utils.time_helpers import SetTimeFunction
from utils.frequency_adaptability_commands import (
    _empty_row,
    _row_ac_write,
    _row_ac_wait_idn,
    _row_wt_async_marker,
    _row_device_write,
    default_dc_iv_resolver,
)
from utils.safe_shutdown import (
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
)
from utils.ac_scpi_commands import append_ac_startup_from_ui
from utils.voltage_adaptability_commands import append_volt_set, _fmt_volt


def append_rapid_volt_band(
    out_rows,
    phase_mode,
    volt_start,
    volt_end,
    pre_hold_01s,
    post_hold_01s,
    *,
    return_start,
    return_hold_01s,
    wt_first_trigger,
):
    """单次快速电压变化：起点驻留 → 阶跃到终点 → 终点保持 → 可选回起点。"""
    vs = str(volt_start).strip()
    ve = str(volt_end).strip()
    if not vs and not ve:
        return False, "电压区间未填写", False, 0
    if not vs:
        vs = ve
    if not ve:
        ve = vs
    vs = _fmt_volt(vs)
    ve = _fmt_volt(ve)

    triggered = False
    duration_01s = 0

    if wt_first_trigger and not triggered:
        out_rows.append(_row_wt_async_marker("ASYNC_START"))
        triggered = True

    append_volt_set(out_rows, phase_mode, vs)
    pre = int(pre_hold_01s) if pre_hold_01s else 0
    if pre > 0:
        out_rows.append(_row_ac_wait_idn(pre, slot=9))
        duration_01s += pre

    # 快速阶跃到终点
    append_volt_set(out_rows, phase_mode, ve)
    post = int(post_hold_01s) if post_hold_01s else 0
    if post > 0:
        out_rows.append(_row_ac_wait_idn(post, slot=9))
        duration_01s += post

    if return_start and vs != ve:
        append_volt_set(out_rows, phase_mode, vs)
        rh = int(return_hold_01s) if return_hold_01s else 0
        if rh > 0:
            out_rows.append(_row_ac_wait_idn(rh, slot=9))
            duration_01s += rh

    return True, "", triggered, duration_01s


def append_enabled_rapid_bands(ui, out_rows, phase_mode, step_nums, *, wt_armed=False):
    page_cb = getattr(ui, "checkBox_rapidvolt_page", None)
    if page_cb is not None and not page_cb.isChecked():
        return True, "", [], wt_armed

    metas = []
    for sn in step_nums:
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is None or not cb.isChecked():
            continue
        te_start = getattr(ui, "textEdit_S%d_volt_start_rvc" % sn, None)
        te_end = getattr(ui, "textEdit_S%d_volt_end_rvc" % sn, None)
        te_pre = getattr(ui, "textEdit_S%d_pre_hold_rvc" % sn, None)
        cmb_pre = getattr(ui, "comboBox_S%d_pre_hold_unit_rvc" % sn, None)
        te_post = getattr(ui, "textEdit_S%d_post_hold_rvc" % sn, None)
        cmb_post = getattr(ui, "comboBox_S%d_post_hold_unit_rvc" % sn, None)
        cb_ret = getattr(ui, "checkBox_S%d_return_rvc" % sn, None)
        if te_start is None or te_end is None or te_post is None or cmb_post is None:
            return False, "快速电压变化 step%d 控件缺失" % sn, [], wt_armed

        vs = te_start.toPlainText().strip()
        ve = te_end.toPlainText().strip()
        if not vs and not ve:
            return False, "快速电压变化 step%d 电压区间未填写" % sn, [], wt_armed
        post_txt = te_post.toPlainText().strip()
        if not post_txt:
            return False, "快速电压变化 step%d 终点保持未填写" % sn, [], wt_armed
        try:
            post_01s = SetTimeFunction(float(post_txt), cmb_post.currentText())
        except (TypeError, ValueError):
            return False, "快速电压变化 step%d 终点保持格式错误" % sn, [], wt_armed

        pre_01s = 10
        if te_pre is not None and cmb_pre is not None and te_pre.toPlainText().strip():
            try:
                pre_01s = SetTimeFunction(float(te_pre.toPlainText().strip()), cmb_pre.currentText())
            except (TypeError, ValueError):
                return False, "快速电压变化 step%d 起点保持格式错误" % sn, [], wt_armed

        return_start = True if cb_ret is None else cb_ret.isChecked()
        ret_hold = pre_01s if return_start else 0

        ok, err, triggered, dur = append_rapid_volt_band(
            out_rows,
            phase_mode,
            vs,
            ve,
            pre_01s,
            post_01s,
            return_start=return_start,
            return_hold_01s=ret_hold,
            wt_first_trigger=wt_armed,
        )
        if not ok:
            return False, err, [], wt_armed
        if triggered:
            wt_armed = False
        safe_s = str(vs or ve).replace(".", "p")
        safe_e = str(ve or vs).replace(".", "p")
        metas.append({
            "name": "RVC_S%d_%s-%s" % (sn, safe_s, safe_e),
            "duration_01s": dur,
            "step": sn,
        })
    return True, "", metas, wt_armed


def resolve_rapid_volt_file_name_list(band_metas, existing_names=None):
    """
    按已启用阶跃自动生成 WT 文件名；忽略 WT 模板残留（100%_ambient）及通用占位名。
    连续录 1 条时返回一个合成名；多段时形如 RVC_BR_230-207_230-253_230-184_230-276。
    """
    from utils.voltage_adaptability_commands import is_stale_wt_filename

    auto = [
        str(m.get("name") or "").strip()
        for m in (band_metas or [])
        if m and str(m.get("name") or "").strip()
    ]
    raw_existing = [str(p).strip() for p in (existing_names or []) if str(p).strip()]
    existing = [
        p
        for p in raw_existing
        if p and not is_stale_wt_filename(p) and not _is_generic_rvc_filename(p)
    ]

    if auto and len(existing) == len(auto):
        return existing

    if not auto:
        return ["RVC_BR"]

    if len(auto) == 1:
        return [auto[0]]

    suffixes = []
    for name in auto:
        if name.upper().startswith("RVC_S"):
            rest = name[5:]
            if "_" in rest:
                rest = rest.split("_", 1)[1]
            suffixes.append(rest)
        else:
            suffixes.append(name)
    composite = "RVC_BR_" + "_".join(suffixes)
    if len(composite) > 72:
        composite = "RVC_BR_%dstep" % len(auto)
    return [composite]


def _is_generic_rvc_filename(name):
    raw = str(name or "").strip().lower()
    return raw in (
        "rapidvolt_change",
        "rapid_volt_change",
        "rapidvolt",
        "rvc_br",
    )


def build_rapid_volt_plan(
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

    band_rows = []
    wt_armed = wt_is_checked == "1"
    ok_bands, band_err, band_metas, wt_armed = append_enabled_rapid_bands(
        ui, band_rows, phase_mode, list(range(3, 9)), wt_armed=wt_armed,
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

    file_names = resolve_rapid_volt_file_name_list(band_metas)
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
