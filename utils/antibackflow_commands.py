# -*- coding: utf-8 -*-
"""防逆流（UNE 217001 / anti-vertido）：AC/DC 启机 + 工况 DC 阶梯 + 连续/分文件录波。

台架无可编程负荷时：切负荷 / 通讯断开用 AC *IDN? 等待窗口留给试验员操作。
"""

from __future__ import annotations

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
from utils.active_p_commands import (
    _empty_row,
    _row_ac_write,
    _row_ac_wait_idn,
    _row_device_write,
    default_dc_iv_resolver,
    parse_ladder,
)


# 5.2 切负荷表（负荷由试验员切换；DC 保持 gen_pct 头寸）
_LOAD_STEPS = (
    ("5_2_1", 100.0, "90-100→60-70"),
    ("5_2_2", 100.0, "90-100→30-40"),
    ("5_2_3", 100.0, "90-100→0"),
    ("5_2_4", 70.0, "60-70→30-40"),
    ("5_2_5", 70.0, "60-70→0"),
    ("5_2_6", 40.0, "30-40→0"),
)


def _cb_on(ui, name, default=False):
    w = getattr(ui, name, None)
    if w is None:
        return default
    return bool(w.isChecked())


def collect_scenario_points(ui, dwell_01s, op_wait_01s):
    """返回 [{tag, dc_pct, dwell_01s, op_wait_01s, note}, ...]。"""
    half = max(1, int(dwell_01s) // 2)
    points = []

    if _cb_on(ui, "checkBox_S5_1", True):
        levels = parse_ladder(
            getattr(ui, "textEdit_PowerLadder", None).toPlainText()
            if hasattr(ui, "textEdit_PowerLadder")
            else "100,70,20,0"
        )
        if not levels:
            levels = [100.0, 70.0, 20.0, 0.0]
        for pct in levels:
            points.append(
                {
                    "tag": "5_1_P%g" % pct,
                    "dc_pct": float(pct),
                    "dwell_01s": int(dwell_01s),
                    "op_wait_01s": 0,
                    "note": "5.1 steady",
                }
            )

    if _cb_on(ui, "checkBox_S5_2", True):
        for tag, gen_pct, note in _LOAD_STEPS:
            points.append(
                {
                    "tag": tag + "_pre",
                    "dc_pct": float(gen_pct),
                    "dwell_01s": half,
                    "op_wait_01s": 0,
                    "note": "5.2 pre " + note,
                }
            )
            points.append(
                {
                    "tag": tag + "_op",
                    "dc_pct": float(gen_pct),
                    "dwell_01s": 0,
                    "op_wait_01s": int(op_wait_01s),
                    "note": "5.2 operator load change " + note,
                }
            )
            points.append(
                {
                    "tag": tag + "_post",
                    "dc_pct": float(gen_pct),
                    "dwell_01s": half,
                    "op_wait_01s": 0,
                    "note": "5.2 post " + note,
                }
            )

    if _cb_on(ui, "checkBox_S5_3", True):
        points.append(
            {
                "tag": "5_3_pre45",
                "dc_pct": 45.0,
                "dwell_01s": half,
                "op_wait_01s": 0,
                "note": "5.3 primary pre 45%",
            }
        )
        points.append(
            {
                "tag": "5_3_step90",
                "dc_pct": 90.0,
                "dwell_01s": half,
                "op_wait_01s": 0,
                "note": "5.3 primary step 90%",
            }
        )

    if _cb_on(ui, "checkBox_S5_4", True):
        points.append(
            {
                "tag": "5_4_op",
                "dc_pct": 100.0,
                "dwell_01s": 0,
                "op_wait_01s": int(op_wait_01s),
                "note": "5.4 operator disconnect anti-export comms",
            }
        )
        # 短测窗约 10 s（0.1s 单位 → 100）
        points.append(
            {
                "tag": "5_4_meas",
                "dc_pct": 100.0,
                "dwell_01s": 100,
                "op_wait_01s": 0,
                "note": "5.4 measure after comms loss",
            }
        )

    return points


def antibackflow_recommended_filenames(ui, mode: str = MODE_CONTINUOUS):
    if mode == MODE_CONTINUOUS:
        return ["AntiBackflow_BR"]
    points = collect_scenario_points(ui, dwell_01s=1200, op_wait_01s=300)
    # 分文件：只给有实质驻留的点（跳过纯人工等待点）
    names = []
    for p in points:
        if p["dwell_01s"] <= 0 and p["op_wait_01s"] > 0:
            continue
        names.append("AntiBF_%s" % p["tag"])
    return names or ["AntiBackflow_BR"]


def _apply_dc_pct(ui, commands, point_rows, dc_pct, dc_iv_resolver, point_index, dc_errors, tag):
    for ch, device, dc_num, label in (
        (1, "DC1", 0, "DC电源1"),
        (2, "DC2", 1, "DC电源2"),
        (3, "DC3", 2, "DC电源3"),
        (4, "DC4", 3, "DC电源4"),
    ):
        s1_on = getattr(ui, "checkBox_S1_DC%d" % ch).isChecked()
        s3_on = getattr(ui, "checkBox_S3_DC%d" % ch).isChecked()
        if not (s1_on and s3_on):
            continue
        vmp = getattr(ui, "textEdit_S1_DC%d_VOLT" % ch).toPlainText()
        imp = getattr(ui, "textEdit_S1_DC%d_CURR" % ch).toPlainText()
        voc = getattr(ui, "textEdit_S1_DC%d_Voc" % ch).toPlainText()
        isc = getattr(ui, "textEdit_S1_DC%d_Isc" % ch).toPlainText()
        code, iv_cmds = dc_iv_resolver(vmp, imp, voc, isc, dc_pct, dc_num)
        if code == "err1":
            dc_errors.append("%s@%s赋值错误" % (label, tag))
        elif code == "err2":
            dc_errors.append("%s@%sIsc超范围" % (label, tag))
        elif code == "err_brand":
            dc_errors.append("%sDC命令与厂家不匹配（已拦截致茂IVC混用）" % label)
        elif code == "ok" and iv_cmds:
            for cmd in iv_cmds:
                if point_index > 0 and (
                    "MODE" in cmd or "SELect" in cmd or "SAS:MODE" in cmd
                ):
                    continue
                row = _row_device_write(device, cmd)
                commands.append(row)
                point_rows.append(row)


def build_antibackflow_plan(
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
    op_wait_01s = 0
    dc_pct = 100.0

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
                "error": "防逆流测试 启机/等待时间格式错误",
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
        try:
            dwell_01s = SetTimeFunction(
                float(ui.textEdit_S3_TIME_2.toPlainText()),
                ui.comboBox_S3_TIME_2.currentText(),
            )
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "防逆流测试 驻留时间格式错误",
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
            op_te = getattr(ui, "textEdit_OpWait", None)
            op_cb = getattr(ui, "comboBox_OpWait", None)
            if op_te is not None and op_cb is not None:
                op_wait_01s = SetTimeFunction(float(op_te.toPlainText()), op_cb.currentText())
            else:
                op_wait_01s = 300
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "防逆流测试 人工操作等待时间格式错误",
                "dc_errors": dc_errors,
                "commands": commands,
                "steps": steps,
                "wt_type": wt_type,
                "test_program": test_program,
                "wt_is_checked": wt_is_checked,
                "power_levels": [],
                "file_names": [],
                "dwell_01s": dwell_01s,
                "dc_pct": dc_pct,
                "wt_rounds": 0,
            }

        points = collect_scenario_points(ui, dwell_01s, op_wait_01s)
        if not points:
            return {
                "ok": False,
                "error": "请至少勾选一段 UNE 工况（5.1～5.4）",
                "dc_errors": dc_errors,
                "commands": commands,
                "steps": steps,
                "wt_type": wt_type,
                "test_program": test_program,
                "wt_is_checked": wt_is_checked,
                "power_levels": [],
                "file_names": [],
                "dwell_01s": dwell_01s,
                "dc_pct": dc_pct,
                "wt_rounds": 0,
            }

        power_levels = [p["dc_pct"] for p in points]
        record_mode = get_record_mode(ui)
        wt_continuous = record_mode == MODE_CONTINUOUS
        point_index = 0
        total_points = len(points)
        split_names = []
        total_dwell_01s = 0

        for p in points:
            point_rows = []
            tag = p["tag"]
            pct = float(p["dc_pct"])
            dc_pct = pct
            maybe_async_start(
                commands,
                point_rows,
                wt_continuous=wt_continuous,
                wt_is_checked=wt_is_checked,
                point_index=point_index,
            )
            _apply_dc_pct(
                ui, commands, point_rows, pct, dc_iv_resolver, point_index, dc_errors, tag
            )
            if int(p.get("op_wait_01s") or 0) > 0:
                wait = _row_ac_wait_idn(int(p["op_wait_01s"]))
                commands.append(wait)
                point_rows.append(wait)
                total_dwell_01s += int(p["op_wait_01s"])
            if int(p.get("dwell_01s") or 0) > 0:
                append_matrix_dwell(
                    commands, point_rows, int(p["dwell_01s"]), wt_continuous=wt_continuous
                )
                total_dwell_01s += int(p["dwell_01s"])
            steps.append(point_rows)
            if int(p.get("dwell_01s") or 0) > 0 or int(p.get("op_wait_01s") or 0) == 0:
                split_names.append("AntiBF_%s" % tag)
            point_index += 1

        if wt_continuous and wt_is_checked == "1" and total_points > 0:
            file_names = ["AntiBackflow_BR"]
        else:
            file_names = split_names
        maybe_async_end(
            commands,
            wt_continuous=wt_continuous,
            wt_is_checked=wt_is_checked,
            total_points=total_points,
        )
        dwell_01s = total_dwell_01s  # for StopTime estimate in Send

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
        "scenario_count": len(power_levels),
    }
