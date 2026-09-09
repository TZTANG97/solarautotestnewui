# -*- coding: utf-8 -*-
"""静态 MPPT — 蓝电 IP 分支：电压点 × Pn% × STC，不走 Soft Panel。"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from utils.ac_scpi_commands import append_ac_startup_from_ui
from utils.matrix_recording_commands import (
    append_matrix_dwell,
    get_record_mode,
    maybe_async_end,
    maybe_async_start,
    resolve_wt_rounds,
)
from utils.safe_shutdown import (
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
)
from utils.time_helpers import SetTimeFunction
from utils.wt_recording_mode import MODE_CONTINUOUS

VOLTAGE_BANDS = ("Vmin", "Vnom", "Vmax")
PN_PERCENT_CHECKS = (
    ("checkBox_S2_Pn_100", 100.0),
    ("checkBox_S2_Pn_75", 75.0),
    ("checkBox_S2_Pn_50", 50.0),
    ("checkBox_S2_Pn_30", 30.0),
    ("checkBox_S2_Pn_25", 25.0),
    ("checkBox_S2_Pn_20", 20.0),
    ("checkBox_S2_Pn_10", 10.0),
    ("checkBox_S2_Pn_5", 5.0),
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


def _row_device_write(device, cmd):
    row = _empty_row()
    row[0] = device
    row[1] = "write"
    row[2] = cmd
    return row


def is_bluesight_mode(ui) -> bool:
    radio = getattr(ui, "radio_Mode_Bluesight", None)
    if radio is not None:
        return bool(radio.isChecked())
    soft = getattr(ui, "radio_Mode_SoftPanel", None)
    if soft is not None:
        return not bool(soft.isChecked())
    return True


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


def _plain(ui, name: str, default: str = "") -> str:
    w = getattr(ui, name, None)
    if w is None:
        return default
    try:
        return str(w.toPlainText()).strip()
    except Exception:
        return default


def _band_enabled_on_any_dc(ui, band: str) -> bool:
    for ch in range(1, 5):
        cb = getattr(ui, "checkBox_S1_DC%d_%s" % (ch, band), None)
        dc = getattr(ui, "checkBox_S1_DC%d" % ch, None)
        if dc is not None and dc.isChecked() and cb is not None and cb.isChecked():
            return True
    return False


def _selected_pn_levels(ui) -> List[float]:
    levels = []
    for name, pct in PN_PERCENT_CHECKS:
        cb = getattr(ui, name, None)
        if cb is not None and cb.isChecked():
            levels.append(pct)
    return levels


def _read_band_iv(ui, band: str):
    return (
        _plain(ui, "textEdit_BS_%s_Vmp" % band),
        _plain(ui, "textEdit_BS_%s_Imp" % band),
        _plain(ui, "textEdit_BS_%s_Voc" % band),
        _plain(ui, "textEdit_BS_%s_Isc" % band),
    )


def _per_test_dwell_01s(ui) -> int:
    h = float(_plain(ui, "textEdit_S3_PER_H", "0") or "0")
    m = float(_plain(ui, "textEdit_S3_PER_M", "5") or "0")
    return int(round(h * 36000 + m * 600))


def build_static_mppt_bluesight_plan(
    ui,
    *,
    wt_config_dict=None,
    str_add_flag="0",
    project_change="0",
    existing_commands=None,
    dc_iv_resolver=None,
    per_dc_factor=None,
) -> Dict[str, Any]:
    """生成蓝电静态 MPPT 命令计划（普通 AC/DC/WT 行，无 MPPT_step*）。"""
    if wt_config_dict is None:
        wt_config_dict = {}
    if dc_iv_resolver is None:
        dc_iv_resolver = default_dc_iv_resolver
    if per_dc_factor is None:
        per_dc_factor = {}

    commands: List[List[Any]] = list(existing_commands or [])
    if str_add_flag == "0":
        commands = []

    steps: List[Any] = []
    dc_errors: List[str] = []
    test_program: List[Any] = []
    wt_type = None
    wt_is_checked = "0"
    file_names: List[str] = []
    point_metas: List[Dict[str, Any]] = []

    need_wt = str_add_flag == "0" or (str_add_flag == "1" and project_change == "1")
    analyzer_on = bool(
        getattr(ui, "checkBox_Analyzer", None)
        and ui.checkBox_Analyzer.isChecked()
    )

    if need_wt and analyzer_on:
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
            f_s1 = SetTimeFunction(
                float(ui.textEdit_S1_TIME.toPlainText()),
                ui.comboBox_S1_TIME.currentText(),
            )
            f_ac_wait = SetTimeFunction(
                float(ui.textEdit_S1_ACWaitTIME.toPlainText()),
                ui.comboBox_S1_ACWaitTIME.currentText(),
            )
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error": "静态MPPT 启机/等待时间格式错误",
                "dc_errors": [],
                "commands": commands,
                "steps": steps,
                "wt_type": None,
                "test_program": [],
                "wt_is_checked": "0",
                "file_names": [],
                "dwell_01s": 0,
                "wt_rounds": 0,
                "wt_continuous": False,
                "point_metas": [],
            }

        ac_status = ui.comboBox_S1_AC.currentText()
        append_ac_startup_from_ui(ui, commands, step_rows)
        row = _row_ac_write("OUTP ON" if ac_status == "开启" else "OUTP OFF")
        row[9] = f_ac_wait
        commands.append(row)
        step_rows.append(row)

        # 启机：用第一个启用电压点的 IV @100% 把 DC 拉起来
        startup_band = None
        for band in ("Vnom", "Vmin", "Vmax"):
            if _band_enabled_on_any_dc(ui, band):
                startup_band = band
                break
        if startup_band is None:
            dc_errors.append("请至少勾选一个电压点（建议 Vnom）")
        else:
            vmp, imp, voc, isc = _read_band_iv(ui, startup_band)
            for ch, device, dc_num, label in (
                (1, "DC1", 0, "DC电源1"),
                (2, "DC2", 1, "DC电源2"),
                (3, "DC3", 2, "DC电源3"),
                (4, "DC4", 3, "DC电源4"),
            ):
                if not getattr(ui, "checkBox_S1_DC%d" % ch).isChecked():
                    continue
                code, iv_cmds = dc_iv_resolver(vmp, imp, voc, isc, 100.0, dc_num)
                if code == "err1":
                    dc_errors.append("%s启机赋值错误" % label)
                elif code == "err2":
                    dc_errors.append("%s启机Isc超范围" % label)
                elif code == "err_brand":
                    dc_errors.append("%sDC命令与厂家不匹配" % label)
                elif code == "ok" and iv_cmds:
                    wait = _row_ac_wait_idn(2, slot=8)
                    commands.append(wait)
                    step_rows.append(wait)
                    for cmd in iv_cmds:
                        row = _row_device_write(device, cmd)
                        commands.append(row)
                        step_rows.append(row)
                dc_start = getattr(ui, "comboBox_S1_DC_START", None)
                status = dc_start.currentText() if dc_start is not None else "开启"
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

    if analyzer_on:
        wt_is_checked = "1"
        if need_wt:
            for radio_name, wtype in (
                ("radioButton_S2_WT3000", "WT3000"),
                ("radioButton_S2_WT1800", "WT1800"),
                ("radioButton_S2_WT1806E", "WT1806E"),
                ("radioButton_S2_WT5000", "WT5000"),
            ):
                rb = getattr(ui, radio_name, None)
                if rb is not None and rb.isChecked():
                    wt_type = wtype
                    break
            if wt_type:
                test_program.append(["12", wt_type])

    pn_levels = _selected_pn_levels(ui) if ui.checkBox_S2.isChecked() else []
    if not pn_levels:
        return {
            "ok": False,
            "error": "请至少勾选一个测试功率段（建议 100%）",
            "dc_errors": dc_errors,
            "commands": commands,
            "steps": steps,
            "wt_type": wt_type,
            "test_program": test_program,
            "wt_is_checked": wt_is_checked,
            "file_names": [],
            "dwell_01s": 0,
            "wt_rounds": 0,
            "wt_continuous": False,
            "point_metas": [],
        }

    bands = [b for b in VOLTAGE_BANDS if _band_enabled_on_any_dc(ui, b)]
    if not bands:
        return {
            "ok": False,
            "error": "请至少勾选一个电压点（Vmin/Vnom/Vmax）",
            "dc_errors": dc_errors,
            "commands": commands,
            "steps": steps,
            "wt_type": wt_type,
            "test_program": test_program,
            "wt_is_checked": wt_is_checked,
            "file_names": [],
            "dwell_01s": 0,
            "wt_rounds": 0,
            "wt_continuous": False,
            "point_metas": [],
        }

    try:
        dwell_01s = _per_test_dwell_01s(ui)
        if dwell_01s <= 0:
            raise ValueError("dwell")
    except (TypeError, ValueError):
        return {
            "ok": False,
            "error": "单次测试时长无效（请填 小时/分钟）",
            "dc_errors": dc_errors,
            "commands": commands,
            "steps": steps,
            "wt_type": wt_type,
            "test_program": test_program,
            "wt_is_checked": wt_is_checked,
            "file_names": [],
            "dwell_01s": 0,
            "wt_rounds": 0,
            "wt_continuous": False,
            "point_metas": [],
        }

    record_mode = get_record_mode(ui)
    wt_continuous = record_mode == MODE_CONTINUOUS
    point_index = 0
    total_points = len(bands) * len(pn_levels)
    split_names: List[str] = []

    for band in bands:
        vmp, imp, voc, isc = _read_band_iv(ui, band)
        for pct in pn_levels:
            point_rows: List[Any] = []
            maybe_async_start(
                commands,
                point_rows,
                wt_continuous=wt_continuous,
                wt_is_checked=wt_is_checked,
                point_index=point_index,
            )
            for ch, device, dc_num, label in (
                (1, "DC1", 0, "DC电源1"),
                (2, "DC2", 1, "DC电源2"),
                (3, "DC3", 2, "DC电源3"),
                (4, "DC4", 3, "DC电源4"),
            ):
                if not getattr(ui, "checkBox_S1_DC%d" % ch).isChecked():
                    continue
                band_cb = getattr(ui, "checkBox_S1_DC%d_%s" % (ch, band), None)
                if band_cb is None or not band_cb.isChecked():
                    continue
                code, iv_cmds = dc_iv_resolver(vmp, imp, voc, isc, pct, dc_num)
                if code == "err1":
                    dc_errors.append("%s@%s@%.0f%%赋值错误" % (label, band, pct))
                elif code == "err2":
                    dc_errors.append("%s@%s@%.0f%%Isc超范围" % (label, band, pct))
                elif code == "err_brand":
                    dc_errors.append("%sDC命令与厂家不匹配" % label)
                elif code == "ok" and iv_cmds:
                    for cmd in iv_cmds:
                        if point_index > 0 and (
                            "MODE" in cmd or "SELect" in cmd or "SAS:MODE" in cmd
                        ):
                            continue
                        row = _row_device_write(device, cmd)
                        commands.append(row)
                        point_rows.append(row)
            append_matrix_dwell(
                commands, point_rows, dwell_01s, wt_continuous=wt_continuous
            )
            tag = "StaticMPPT_%s_P%s" % (band, ("%g" % pct).replace(".", "p"))
            split_names.append(tag)
            point_metas.append({"band": band, "pn_pct": pct, "file": tag})
            point_index += 1

    maybe_async_end(
        commands,
        wt_continuous=wt_continuous,
        wt_is_checked=wt_is_checked,
        total_points=total_points,
    )

    if wt_continuous and wt_is_checked == "1" and total_points > 0:
        file_names = ["StaticMPPT_BR"]
    else:
        file_names = split_names

    if getattr(ui, "checkBox_S_End", None) is not None and ui.checkBox_S_End.isChecked():
        dc_channels = enabled_shutdown_dc_channels(ui)
        if not dc_channels:
            end_dc = getattr(ui, "checkBox_S_End_DC", None)
            end_combo = getattr(ui, "comboBox_S_End_DC", None)
            if end_dc is not None and end_dc.isChecked():
                want_off = True
                if end_combo is not None:
                    try:
                        want_off = end_combo.currentText() == "关闭"
                    except Exception:
                        want_off = True
                if want_off:
                    for ch in range(1, 5):
                        if getattr(ui, "checkBox_S1_DC%d" % ch).isChecked():
                            dc_channels.append(ch)
        if dc_channels:
            for row in build_forced_shutdown_rows(
                dc_channels=dc_channels,
                per_dc_factor=per_dc_factor,
            ):
                commands.append(row)
        else:
            # 仅 AC 关
            try:
                if ui.comboBox_S_End_AC.currentText() == "关闭":
                    commands.append(_row_device_write("AC", "OUTP OFF"))
            except Exception:
                commands.append(_row_device_write("AC", "OUTP OFF"))

    wt_rounds = resolve_wt_rounds(wt_is_checked, file_names, wt_continuous)
    ok = not dc_errors
    return {
        "ok": ok,
        "error": ("；".join(dc_errors) if dc_errors else ""),
        "dc_errors": dc_errors,
        "commands": commands,
        "steps": steps,
        "wt_type": wt_type,
        "test_program": test_program,
        "wt_is_checked": wt_is_checked,
        "file_names": file_names,
        "dwell_01s": dwell_01s,
        "wt_rounds": wt_rounds,
        "wt_continuous": wt_continuous,
        "point_metas": point_metas,
        "bands": bands,
        "pn_levels": pn_levels,
        "record_mode": record_mode if analyzer_on else "",
    }
