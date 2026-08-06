# -*- coding: utf-8 -*-
"""频率适应性：生成完整试验命令计划（可供 Send 与离屏模拟共用）。"""

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


def append_freq_set(out_rows, phase_mode, freq_hz):
    """按单相/三相写入 FREQ。"""
    freq_cmd = "FREQ " + str(freq_hz).strip()
    if phase_mode == "单相":
        out_rows.append(_row_ac_write(freq_cmd))
        return
    for nsel in (1, 2, 3):
        out_rows.append(_row_ac_write("INST:NSEL %d" % nsel))
        out_rows.append(_row_ac_write(freq_cmd))


def append_freq_band(out_rows, phase_mode, freq_start, freq_end, duration_01s):
    """
    频段策略：先设起点频率短暂稳定，再设终点频率并按测试时间保持。
    start==end 时只设一次并 dwell 全时长。
    """
    start = str(freq_start).strip()
    end = str(freq_end).strip()
    if not start and not end:
        return False
    if not start:
        start = end
    if not end:
        end = start

    settle = max(10, int(duration_01s * 0.05)) if duration_01s else 10
    if start == end:
        append_freq_set(out_rows, phase_mode, start)
        out_rows.append(_row_ac_wait_idn(duration_01s))
        return True

    append_freq_set(out_rows, phase_mode, start)
    out_rows.append(_row_ac_wait_idn(settle))
    append_freq_set(out_rows, phase_mode, end)
    out_rows.append(_row_ac_wait_idn(duration_01s))
    return True


def append_enabled_bands(ui, out_rows, phase_mode, step_nums, side_tag, page_attr):
    """
    若页总开关开启，则遍历各卡片：勾选且参数齐全时追加命令。
    返回 (ok, error_message)；ok=False 表示参数非法应中止。
    """
    page_cb = getattr(ui, page_attr, None)
    if page_cb is not None and not page_cb.isChecked():
        return True, ""

    for sn in step_nums:
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is None or not cb.isChecked():
            continue
        te_start = getattr(ui, "textEdit_S%d_freq_start_%s" % (sn, side_tag), None)
        te_end = getattr(ui, "textEdit_S%d_freq_end_%s" % (sn, side_tag), None)
        te_dur = getattr(ui, "textEdit_S%d_test_duration_%s" % (sn, side_tag), None)
        cmb_unit = getattr(ui, "comboBox_S%d_test_time_unit_%s" % (sn, side_tag), None)
        if te_start is None or te_end is None or te_dur is None or cmb_unit is None:
            return False, "频率适应性 step%d 控件缺失" % sn

        freq_start = te_start.toPlainText().strip()
        freq_end = te_end.toPlainText().strip()
        dur_text = te_dur.toPlainText().strip()
        if not freq_start and not freq_end:
            return False, "频率适应性 step%d 频率区间未填写" % sn
        if not dur_text:
            return False, "频率适应性 step%d 测试时间未填写" % sn
        try:
            duration_01s = SetTimeFunction(float(dur_text), cmb_unit.currentText())
        except (TypeError, ValueError):
            return False, "频率适应性 step%d 测试时间格式错误" % sn

        append_freq_band(out_rows, phase_mode, freq_start, freq_end, duration_01s)
    return True, ""


def default_dc_iv_resolver(vmp, imp, voc, isc, pf, dc_num):
    """
    轻量 DC IV 解析（模拟/无厂家配置时用）。
    返回 ("ok", [cmds]) 或 ("err1"|"err2", None)。
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
    return "ok", [
        "IVC:IT %.3f,%.3f" % (f_imp, f_isc),
        "IVC:VT %.3f,%.3f" % (f_vmp, f_voc),
    ]


def build_frequency_adaptability_plan(
    ui,
    *,
    wt_config_dict=None,
    str_add_flag="0",
    project_change="0",
    existing_commands=None,
    dc_iv_resolver=None,
):
    """
    根据 Dialog UI 生成完整命令计划。

    返回 dict:
      ok: bool
      error: str | None          # 频段参数错误（应中止）
      dc_errors: list[str]       # DC 校验错误（不写设定成功标志）
      commands: list
      steps: list
      wt_type: str | None
      test_program: list
      wt_is_checked: str
    """
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

    # step1
    if ui.checkBox_S1.isChecked():
        step_rows = []
        f_s1 = SetTimeFunction(float(ui.textEdit_S1_TIME.toPlainText()), ui.comboBox_S1_TIME.currentText())
        f_ac_wait = SetTimeFunction(
            float(ui.textEdit_S1_ACWaitTIME.toPlainText()),
            ui.comboBox_S1_ACWaitTIME.currentText(),
        )
        ac_status = ui.comboBox_S1_AC.currentText()

        if phase_mode == "单相":
            for cmd in ("INST:PHAS SINGLE", "INST:EDIT ALL"):
                row = _row_ac_write(cmd)
                commands.append(row)
                step_rows.append(row)
            volt = ui.textEdit_S1_AC_VOLT.toPlainText()
            fr = ui.textEdit_S1_AC_FR.toPlainText()
            for cmd in ("VOLT " + volt, "FREQ " + fr):
                row = _row_ac_write(cmd)
                commands.append(row)
                step_rows.append(row)
        elif phase_mode == "三相":
            for cmd in ("INST:PHAS THREE", "INST:EDIT EACH"):
                row = _row_ac_write(cmd)
                commands.append(row)
                step_rows.append(row)
            volts = [
                ui.textEdit_S1_AC_VOLT.toPlainText(),
                ui.textEdit_S1_AC_VOLT_2.toPlainText(),
                ui.textEdit_S1_AC_VOLT_3.toPlainText(),
            ]
            fr = ui.textEdit_S1_AC_FR.toPlainText()
            for idx, volt in enumerate(volts, start=1):
                for cmd in ("INST:NSEL %d" % idx, "VOLT " + volt, "FREQ " + fr):
                    row = _row_ac_write(cmd)
                    commands.append(row)
                    step_rows.append(row)

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

    # bands
    band_rows = []
    ok_bands, band_err = append_enabled_bands(
        ui, band_rows, phase_mode, list(range(3, 12)), "guopin", "checkBox_guopin_page",
    )
    if ok_bands:
        ok_bands, band_err = append_enabled_bands(
            ui, band_rows, phase_mode, list(range(12, 21)), "qianpin", "checkBox_qianpin_page",
        )
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
        }

    commands.extend(band_rows)
    if band_rows:
        steps.append(list(band_rows))

    # shutdown
    if ui.checkBox_S_End.isChecked():
        step_rows = []
        end_ac = ui.comboBox_S_End_AC.currentText()
        row = _row_ac_write("OUTP ON" if end_ac == "开启" else "OUTP OFF")
        commands.append(row)
        step_rows.append(row)
        wait = _row_ac_wait_idn(5, slot=8)
        commands.append(wait)
        step_rows.append(wait)

        for ch, device in ((1, "DC1"), (2, "DC2"), (3, "DC3"), (4, "DC4")):
            s1_cb = getattr(ui, "checkBox_S1_DC%d" % ch)
            end_cb = getattr(ui, "checkBox_S_End_DC%d" % ch)
            if not (s1_cb.isChecked() and end_cb.isChecked()):
                continue
            end_status = getattr(ui, "comboBox_S_End_DC%d" % ch).currentText()
            row = _row_device_write(device, "OUTP ON" if end_status == "开启" else "OUTP OFF")
            commands.append(row)
            step_rows.append(row)
            wait = _row_ac_wait_idn(5, slot=8)
            commands.append(wait)
            step_rows.append(wait)
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
    }
