# -*- coding: utf-8 -*-
"""Test_PU：每个功率档先改已勾选直流，再扫电压 Un%，WT 连续录 1 条 PU_curve。"""

from __future__ import annotations

from utils.dc_channels import s1_dc_slots

from utils.dynamic_qu_commands import parse_voltage_ladder
from utils.time_helpers import SetTimeFunction


def _empty_row():
    return ["" for _ in range(10)]


def _row_ac_write(cmd):
    row = _empty_row()
    row[0] = "AC"
    row[1] = "write"
    row[2] = cmd
    return row


def _row_device_write(device, cmd):
    row = _empty_row()
    row[0] = device
    row[1] = "write"
    row[2] = cmd
    return row


def _append_dc_power_rows(ui, power_pct, dc_iv_resolver, dc_errors, *, full_chain):
    """按功率%重下已勾选直流。后续档跳过 MODE/SELECT。"""
    point_rows = []
    for ch, device, dc_num, label in s1_dc_slots(ui):
        box = getattr(ui, "checkBox_S1_DC%d" % ch, None)
        if box is None or not box.isChecked():
            continue
        vmp = getattr(ui, "textEdit_S1_DC%d_VOLT" % ch).toPlainText()
        imp = getattr(ui, "textEdit_S1_DC%d_CURR" % ch).toPlainText()
        voc = getattr(ui, "textEdit_S1_DC%d_Voc" % ch).toPlainText()
        isc = getattr(ui, "textEdit_S1_DC%d_Isc" % ch).toPlainText()
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
                point_rows.append(_row_device_write(device, cmd))
    return point_rows


def _read_text(widget, fallback=""):
    if widget is None or not hasattr(widget, "toPlainText"):
        return fallback
    return widget.toPlainText()


def build_pu_voltage_power_rows(ui, *, phase_mode, dc_iv_resolver):
    """电压 list 非空时生成功率×电压命令。

    功率名单留空：不改直流，只扫电压（保持步骤①）。
    有名单：每个功率档先改已勾选直流，再扫一遍电压。
    全程只打一次 ASYNC_START / WAIT_END。
    """
    empty = {
        "ok": True,
        "error": "",
        "use_voltage_ladder": False,
        "rows": [],
        "steps": [],
        "u_pct_list": [],
        "power_levels": [],
        "dwell_01s": 0,
        "dwell_raw": "",
        "dwell_unit": "",
        "dc_errors": [],
    }
    ladder_widget = getattr(ui, "textEdit_VoltageLadder", None)
    ladder_text = _read_text(ladder_widget).strip()
    if not ladder_text:
        return empty

    u_pct_list = parse_voltage_ladder(ladder_text)
    un_w = getattr(ui, "textEdit_VoltageLadder_Un", None)
    fr_w = getattr(ui, "textEdit_VoltageLadder_FR", None)
    time_w = getattr(ui, "textEdit_VoltageLadder_TIME", None)
    time_u = getattr(ui, "comboBox_VoltageLadder_TIME", None)
    try:
        base_un = float(
            (_read_text(un_w).strip() or _read_text(getattr(ui, "textEdit_S1_AC_VOLT", None)).strip() or "230")
        )
    except ValueError:
        base_un = 230.0
    ladder_fr = (
        _read_text(fr_w).strip()
        or _read_text(getattr(ui, "textEdit_S1_AC_FR", None)).strip()
        or "50"
    )
    dwell_raw = _read_text(time_w).strip() or "10"
    dwell_unit = time_u.currentText() if time_u is not None and hasattr(time_u, "currentText") else "秒"
    try:
        dwell_01s = SetTimeFunction(float(dwell_raw), dwell_unit)
    except (TypeError, ValueError):
        out = dict(empty)
        out["ok"] = False
        out["error"] = "PU 电压驻留时间格式错误"
        out["use_voltage_ladder"] = True
        return out

    try:
        base_un2 = float(_read_text(getattr(ui, "textEdit_S1_AC_VOLT_2", None)).strip() or base_un)
    except ValueError:
        base_un2 = base_un
    try:
        base_un3 = float(_read_text(getattr(ui, "textEdit_S1_AC_VOLT_3", None)).strip() or base_un)
    except ValueError:
        base_un3 = base_un

    power_widget = getattr(ui, "textEdit_PowerLadder", None)
    power_levels = []
    if power_widget is not None and hasattr(power_widget, "toPlainText"):
        power_levels = parse_voltage_ladder(power_widget.toPlainText())
    # 留空：保持步骤①功率，只扫电压。
    power_groups = power_levels or [None]

    rows = []
    steps = []
    dc_errors = []
    started = False

    def _volt_rows(pct):
        volt1 = round(base_un * pct / 100.0, 2)
        volt2 = round(base_un2 * pct / 100.0, 2)
        volt3 = round(base_un3 * pct / 100.0, 2)
        point = []
        if phase_mode == "单相":
            for cmd in ("VOLT %s" % volt1, "FREQ %s" % ladder_fr):
                point.append(_row_ac_write(cmd))
        else:
            for nsel, vv in ((1, volt1), (2, volt2), (3, volt3)):
                point.append(_row_ac_write("INST:NSEL %d" % nsel))
                point.append(_row_ac_write("VOLT %s" % vv))
                point.append(_row_ac_write("FREQ %s" % ladder_fr))
        return point

    for p_idx, power_pct in enumerate(power_groups):
        if power_pct is not None and dc_iv_resolver is not None:
            dc_rows = _append_dc_power_rows(
                ui,
                power_pct,
                dc_iv_resolver,
                dc_errors,
                full_chain=(p_idx == 0),
            )
            if dc_rows:
                rows.extend(dc_rows)
                steps.append(list(dc_rows))
        for pct in u_pct_list:
            point_rows = _volt_rows(pct)
            if not started:
                marker = _empty_row()
                marker[0] = "AC"
                marker[1] = "query"
                marker[2] = "*IDN?"
                marker[6] = "ASYNC_START"
                point_rows.append(marker)
                started = True
            wait = _empty_row()
            wait[0] = "AC"
            wait[1] = "wait"
            wait[2] = ""
            wait[9] = dwell_01s
            point_rows.append(wait)
            rows.extend(point_rows)
            steps.append(point_rows)

    if u_pct_list:
        end = _empty_row()
        end[0] = "AC"
        end[1] = "query"
        end[2] = "*IDN?"
        end[6] = "WAIT_END"
        rows.append(end)

    return {
        "ok": True,
        "error": "",
        "use_voltage_ladder": True,
        "rows": rows,
        "steps": steps,
        "u_pct_list": u_pct_list,
        "power_levels": power_levels,
        "dwell_01s": dwell_01s,
        "dwell_raw": dwell_raw,
        "dwell_unit": dwell_unit,
        "dc_errors": dc_errors,
    }
