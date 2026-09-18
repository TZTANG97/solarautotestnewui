# -*- coding: utf-8 -*-
"""频率适应性：巴西 Ordinance 5.4.20 流程（对齐「巴西过欠频稳定性」更新率扫频）。"""

from utils.safe_shutdown import (
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
)
from utils.time_helpers import SetTimeFunction
from utils.ac_scpi_commands import (
    append_ac_startup_from_ui,
    append_freq_set,
    resolve_chroma_61800,
)


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


def _row_wt_async_marker(marker):
    """连续录：col6=ASYNC_START 只启动不阻塞；WAIT_END 等停表。禁止用数字 col6（会卡死扫频）。"""
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[6] = marker
    return row


def _sum_wait_01s(rows):
    total = 0
    for r in rows or []:
        for slot in (8, 9):
            if len(r) <= slot:
                continue
            raw = r[slot]
            if raw in ("", None):
                continue
            try:
                total += int(float(raw))
            except (TypeError, ValueError):
                continue
    return total


def estimate_continuous_record_01s(band_rows, *, scpi_overhead_01s_per_step=2):
    """连续录 StopTime 墙钟（与电压适应性共用：按扫频驻留步数 + SCPI 开销）。"""
    from utils.voltage_adaptability_commands import estimate_continuous_record_01s as _volt_est

    wall_01s, wait_01s, _n_volt, n_dwell = _volt_est(
        band_rows, scpi_overhead_01s_per_step=scpi_overhead_01s_per_step
    )
    n_freq = sum(
        1
        for r in (band_rows or [])
        if len(r) > 2 and str(r[2]).strip().upper().startswith("FREQ")
    )
    return wall_01s, wait_01s, n_freq, n_dwell


def _row_device_write(device, cmd):
    row = _empty_row()
    row[0] = device
    row[1] = "write"
    row[2] = cmd
    return row


def _fmt_freq(hz):
    try:
        v = float(hz)
    except (TypeError, ValueError):
        return str(hz).strip()
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return ("%.4f" % v).rstrip("0").rstrip(".")


def build_freq_step_list(freq_start, freq_end, real_test_time_s, per_second_range, use_rate):
    """
    巴西过欠频稳定性同款：勾更新率时，在数据采集时间内均分扫频；
    不勾则只取起点。
    real_test_time_s / per_second_range 均为「秒」单位。
    """
    start = str(freq_start).strip()
    end = str(freq_end).strip()
    if not start and not end:
        return []
    if not start:
        start = end
    if not end:
        end = start
    if not use_rate or start == end:
        return [start]

    f0 = float(start)
    f1 = float(end)
    delta = abs(f1 - f0)
    total_count = max(1, int(float(real_test_time_s) * float(per_second_range)))
    step = delta / total_count
    out = []
    cur = f0
    ascending = f1 > f0
    while True:
        if ascending:
            if cur < f1:
                out.append(_fmt_freq(round(cur, 2)))
                cur = cur + step
            else:
                out.append(_fmt_freq(round(f1, 2)))
                break
        else:
            if f1 < cur:
                out.append(_fmt_freq(round(cur, 2)))
                cur = cur - step
            else:
                out.append(_fmt_freq(round(f1, 2)))
                break
    return out


def _interval_seconds(value, unit):
    """时间 → 秒（保留亚 0.1s，避免 SetTimeFunction 对 50ms 截成 0）。"""
    v = float(value)
    if unit == "小时":
        return v * 3600.0
    if unit == "分钟":
        return v * 60.0
    if unit == "秒":
        return v
    if unit == "毫秒":
        return v / 1000.0
    return v


def read_update_rate(ui):
    """
    读取全局更新率。返回 (ok, err, rate_interval_s, per_second)。
    rate_interval_s：每步间隔（秒）；per_second：每秒步数。
    """
    rate_on = getattr(ui, "checkBox_S2_update_rate", None)
    if rate_on is None or not rate_on.isChecked():
        return True, "", None, None
    te = getattr(ui, "textEdit_S2_update_rate", None)
    cmb = getattr(ui, "comboBox_S2_update_rate", None)
    if te is None or cmb is None:
        return False, "频率适应性 更新率控件缺失", None, None
    raw = te.toPlainText().strip()
    if not raw:
        return False, "频率适应性 更新率未填写", None, None
    try:
        interval_s = _interval_seconds(raw, cmb.currentText())
    except (TypeError, ValueError):
        return False, "频率适应性 更新率格式错误", None, None
    if interval_s <= 0:
        return False, "频率适应性 更新率必须大于 0", None, None
    return True, "", interval_s, 1.0 / interval_s


def append_freq_band_brazil(
    out_rows,
    phase_mode,
    freq_start,
    freq_end,
    duration_01s,
    *,
    use_rate,
    rate_interval_s,
    per_second_range,
    wt_first_trigger,
):
    """
    巴西 5.4.20 / 过欠频稳定性：扫频步进 + 每步等待。
    wt_first_trigger=True：首步前插入 ASYNC_START（不阻塞），所有 dwell 一律 col[9]。
    禁止把等待秒数写进 col[6]：数字 col6 会启动 WT 并阻塞到录完，扫频被卡在起点。
    返回 (ok, err, end_freq, used_wt_trigger)。
    """
    real_s = float(duration_01s) / 10.0
    steps = build_freq_step_list(
        freq_start,
        freq_end,
        real_s,
        per_second_range or 1.0,
        use_rate=bool(use_rate and rate_interval_s and per_second_range),
    )
    if not steps:
        return False, "频率区间未填写", None, False

    wait_01s = max(1, int(round(float(rate_interval_s) * 10))) if use_rate and rate_interval_s else int(duration_01s)

    triggered = False
    multi_step = use_rate and rate_interval_s and len(steps) > 1
    for i, step in enumerate(steps):
        if wt_first_trigger and not triggered:
            out_rows.append(_row_wt_async_marker("ASYNC_START"))
            triggered = True
        append_freq_set(out_rows, phase_mode, step, edit_all=(i == 0))
        if multi_step:
            out_rows.append(_row_ac_wait_idn(wait_01s, slot=9))
        else:
            # 单点 / 不扫频：保持整段数据采集时间（仍用 col9，勿用数字 col6）
            out_rows.append(_row_ac_wait_idn(int(duration_01s), slot=9))
            break
    return True, "", steps[-1], triggered


def append_enabled_bands(
    ui,
    out_rows,
    phase_mode,
    step_nums,
    side_tag,
    page_attr,
    *,
    rate_interval_s=None,
    per_second_range=None,
    global_rate_on=False,
    wt_armed=False,
):
    """
    遍历启用频带。返回 (ok, error, band_metas, wt_armed)。
    wt_armed：若仍为 True，表示尚未插入 ASYNC_START。
    """
    page_cb = getattr(ui, page_attr, None)
    if page_cb is not None and not page_cb.isChecked():
        return True, "", [], wt_armed

    metas = []
    for sn in step_nums:
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is None or not cb.isChecked():
            continue
        te_start = getattr(ui, "textEdit_S%d_freq_start_%s" % (sn, side_tag), None)
        te_end = getattr(ui, "textEdit_S%d_freq_end_%s" % (sn, side_tag), None)
        te_dur = getattr(ui, "textEdit_S%d_test_duration_%s" % (sn, side_tag), None)
        cmb_unit = getattr(ui, "comboBox_S%d_test_time_unit_%s" % (sn, side_tag), None)
        if te_start is None or te_end is None or te_dur is None or cmb_unit is None:
            return False, "频率适应性 step%d 控件缺失" % sn, [], wt_armed

        freq_start = te_start.toPlainText().strip()
        freq_end = te_end.toPlainText().strip()
        dur_text = te_dur.toPlainText().strip()
        if not freq_start and not freq_end:
            return False, "频率适应性 step%d 频率区间未填写" % sn, [], wt_armed
        if not dur_text:
            return False, "频率适应性 step%d 测试时间未填写" % sn, [], wt_armed
        try:
            duration_01s = SetTimeFunction(float(dur_text), cmb_unit.currentText())
        except (TypeError, ValueError):
            return False, "频率适应性 step%d 测试时间格式错误" % sn, [], wt_armed

        rate_cb = getattr(ui, "checkBox_S%d_RATE" % sn, None)
        card_rate = True if rate_cb is None else rate_cb.isChecked()
        use_rate = bool(global_rate_on and card_rate)

        ok, err, _end_f, triggered = append_freq_band_brazil(
            out_rows,
            phase_mode,
            freq_start,
            freq_end,
            duration_01s,
            use_rate=use_rate,
            rate_interval_s=rate_interval_s,
            per_second_range=per_second_range,
            wt_first_trigger=wt_armed,
        )
        if not ok:
            return False, err, [], wt_armed
        if triggered:
            wt_armed = False

        start = freq_start or freq_end
        end = freq_end or freq_start
        prefix = "OF" if side_tag == "guopin" else "UF"
        safe_start = str(start).replace(".", "p")
        safe_end = str(end).replace(".", "p")
        metas.append({
            "name": "%s_S%d_%s-%s" % (prefix, sn, safe_start, safe_end),
            "duration_01s": duration_01s,
            "step": sn,
            "side": side_tag,
        })
    return True, "", metas, wt_armed


def resolve_freq_file_name_list(band_metas, existing_names=None):
    """
    巴西流程默认整次连续录 1 条，推荐 FreqAdapt_BR_5420。
    不保留 WT 模板 / 其它试验残留名。
    """
    import re
    stale = re.compile(
        r"(ambient|voltadapt|guoya|qianya|rocof|pu_curve|qu_curve|cosphi|fixed.?pf)",
        re.I,
    )
    auto_names = [str(m.get("name") or "").strip() for m in (band_metas or []) if m]
    auto_names = [n for n in auto_names if n]
    existing = []
    for p in (existing_names or []):
        s = str(p).strip()
        if not s or "," in s or "，" in s or stale.search(s):
            continue
        existing.append(s)
    if len(existing) == 1:
        return existing
    if auto_names and len(existing) == len(auto_names):
        return existing
    return ["FreqAdapt_BR_5420"]


def default_dc_iv_resolver(vmp, imp, voc, isc, pf, dc_num):
    """轻量 DC IV 解析（模拟/无厂家配置时用）。

    默认按 Chroma 包一层 MODE TABLE + SELect，避免只下 IVC 点表却无输出功率。
    """
    try:
        f_vmp = float(str(vmp).strip())
        f_imp = float(str(imp).strip())
        f_voc = float(str(voc).strip())
        f_isc = float(str(isc).strip())
        _ = float(str(pf).strip().rstrip("%"))
    except (TypeError, ValueError):
        return "err1", None
    if min(f_vmp, f_imp, f_voc, f_isc) <= 0:
        return "err1", None
    if f_imp >= f_isc or f_vmp >= f_voc:
        return "err1", None
    if f_isc > 1000:
        return "err2", None
    _ = dc_num
    return "ok", [
        "OUTP:MODE TABLE",
        "IVC:IT %.3f,%.3f" % (f_imp, f_isc),
        "IVC:VT %.3f,%.3f" % (f_vmp, f_voc),
        "IVCurve:SELect 1",
    ]


def build_frequency_adaptability_plan(
    ui,
    *,
    wt_config_dict=None,
    str_add_flag="0",
    project_change="0",
    existing_commands=None,
    dc_iv_resolver=None,
    per_dc_factor=None,
):
    """根据 Dialog UI 生成巴西 5.4.20 命令计划。"""
    if wt_config_dict is None:
        wt_config_dict = {}
    if dc_iv_resolver is None:
        dc_iv_resolver = default_dc_iv_resolver
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

    # step1
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

    # step2 WT meta
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

    ok_rate, rate_err, rate_interval_s, per_second = read_update_rate(ui)
    if not ok_rate:
        return {
            "ok": False,
            "error": rate_err,
            "dc_errors": dc_errors,
            "commands": commands,
            "steps": steps,
            "wt_type": wt_type,
            "test_program": test_program,
            "wt_is_checked": wt_is_checked,
            "band_metas": [],
            "file_names": [],
            "wt_rounds": 0,
            "wt_continuous": False,
            "band_duration_01s": 0,
        }

    global_rate_on = rate_interval_s is not None
    band_rows = []
    band_metas = []
    wt_armed = wt_is_checked == "1"
    ok_bands, band_err, metas_of, wt_armed = append_enabled_bands(
        ui, band_rows, phase_mode, list(range(3, 12)), "guopin", "checkBox_guopin_page",
        rate_interval_s=rate_interval_s,
        per_second_range=per_second,
        global_rate_on=global_rate_on,
        wt_armed=wt_armed,
    )
    if ok_bands:
        band_metas.extend(metas_of)
        ok_bands, band_err, metas_uf, wt_armed = append_enabled_bands(
            ui, band_rows, phase_mode, list(range(12, 21)), "qianpin", "checkBox_qianpin_page",
            rate_interval_s=rate_interval_s,
            per_second_range=per_second,
            global_rate_on=global_rate_on,
            wt_armed=wt_armed,
        )
        if ok_bands:
            band_metas.extend(metas_uf)
    if not ok_bands:
        return {
            "ok": False,
            "error": band_err,
            "dc_errors": dc_errors,
            "commands": commands,
            "steps": steps,
            "wt_type": wt_type,
            "test_program": test_program,
            "wt_is_checked": wt_is_checked,
            "band_metas": [],
            "file_names": [],
            "wt_rounds": 0,
            "wt_continuous": False,
            "band_duration_01s": 0,
        }

    # 巴西连续录：频带跑完后再 WAIT_END，等 WT 停表（对齐静态QU/Test_PU）
    if wt_is_checked == "1" and band_rows and any(
        len(r) > 6 and str(r[6]).strip().upper() == "ASYNC_START" for r in band_rows
    ):
        band_rows.append(_row_wt_async_marker("WAIT_END"))

    commands.extend(band_rows)
    if band_rows:
        steps.append(list(band_rows))

    # 巴西：整次连续录 1 条（与过欠频稳定性一致）
    file_names = resolve_freq_file_name_list(band_metas)
    wt_rounds = 1 if (wt_is_checked == "1" and band_metas) else 0
    ui_duration_01s = sum(int(m.get("duration_01s") or 0) for m in band_metas)
    wall_01s, wait_01s, n_freq, n_dwell = estimate_continuous_record_01s(band_rows)
    band_duration_01s = max(ui_duration_01s, wall_01s)
    max_band_duration_01s = band_duration_01s

    # shutdown
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
        "ok": True,
        "error": None,
        "dc_errors": dc_errors,
        "commands": commands,
        "steps": steps,
        "wt_type": wt_type,
        "test_program": test_program,
        "wt_is_checked": wt_is_checked,
        "band_metas": band_metas,
        "file_names": file_names,
        "wt_rounds": wt_rounds,
        "wt_continuous": wt_rounds == 1,
        "band_duration_01s": band_duration_01s,
        "max_band_duration_01s": max_band_duration_01s,
        "ui_duration_01s": ui_duration_01s,
        "sweep_wait_01s": wait_01s,
        "sweep_freq_steps": n_freq,
        "sweep_dwell_steps": n_dwell,
    }
