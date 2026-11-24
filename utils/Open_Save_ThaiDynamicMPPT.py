# -*- coding: utf-8 -*-
"""Dynamic-MPPT settings persistence (EN50530 bundle JSON)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from utils.timing_profile import TIMING_PROFILE_JSON_COLUMN
from utils.timing_profile_adapters import (
    apply_csv_widget_value,
    append_dewetron_settings_tail,
    build_settings_headers,
    read_csv_rows_with_fallback,
    restore_dewetron_settings_tail,
    widget_to_csv,
    _save_wt_rows,
    _restore_wt_rows,
    DEWETRON_CONFIG_COLUMN,
)
import csv

FILE_TAG = "ThaiDynamicMPPT"
TEST_TYPE = "dynamic-mppt"
arrayRow1 = build_settings_headers()
HEADERS = arrayRow1


def _ui(kwargs):
    if isinstance(kwargs, dict):
        return kwargs.get("uiThaiDynamicMPPT") or kwargs.get("ui")
    return kwargs


def _en50530_panel(ui):
    return getattr(ui, "en50530Panel", None) or getattr(ui, "timingProfileTable", None)


def _settings_row_from_ui(ui):
    headers = build_settings_headers()
    values = []
    for header in headers:
        if header == "Style":
            values.append(FILE_TAG)
        elif header == TIMING_PROFILE_JSON_COLUMN:
            panel = _en50530_panel(ui)
            values.append(panel.get_bundle_json() if panel is not None else "")
        else:
            values.append(widget_to_csv(ui, str(header)))
    append_dewetron_settings_tail(headers, values, ui, test_type=TEST_TYPE)
    return headers, values


def save_settings_to_path(ui: Any, path: Union[str, Path], *, show_message: bool = False) -> Path:
    """Write settings CSV (no file dialog). Used by UI Save and automated tests."""

    target = Path(path)
    headers, values = _settings_row_from_ui(ui)
    wt_rows = _save_wt_rows(ui)
    with target.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(list(headers))
        writer.writerow(values)
        writer.writerows(wt_rows)
    if show_message:
        QMessageBox.information(None, "提示信息", "设定文件保存完成")
    return target


def load_settings_from_path(ui: Any, path: Union[str, Path], *, show_message: bool = False) -> dict:
    """Load settings CSV (no file dialog). Used by UI Open and automated tests."""

    rows = read_csv_rows_with_fallback(str(path))
    if len(rows) < 2:
        raise ValueError("设定文件内容不完整")
    headers, values = list(rows[0]), list(rows[1])
    if len(values) < len(headers):
        values.extend([""] * (len(headers) - len(values)))
    config = dict(zip(headers, values))
    if config.get("Style") != FILE_TAG:
        raise ValueError("文件类型不匹配，需要 %s 格式" % FILE_TAG)
    for header, value in config.items():
        if header not in {"Style", TIMING_PROFILE_JSON_COLUMN, DEWETRON_CONFIG_COLUMN}:
            apply_csv_widget_value(ui, header, value)
    panel = _en50530_panel(ui)
    raw = config.get(TIMING_PROFILE_JSON_COLUMN)
    if panel is not None and raw:
        panel.set_bundle_json(raw)
    _restore_wt_rows(ui, rows[2:4])
    restore_dewetron_settings_tail(headers, values, ui)
    if show_message:
        QMessageBox.information(None, "提示信息", "设定文件读取完成")
    return config


def Save_File_ThaiDynamicMPPT(kwargs):
    ui = _ui(kwargs)
    directory = QFileDialog.getSaveFileName(
        None, "保存设定", "./", "CSV Files (*.csv)"
    )
    if not directory[0]:
        return None
    try:
        result = save_settings_to_path(ui, directory[0], show_message=True)
    except Exception as exc:
        QMessageBox.warning(None, "提示信息", "设定文件保存失败: %s" % exc)
        return None
    return result


def Open_File_ThaiDynamicMPPT(kwargs):
    ui = _ui(kwargs)
    directory = QFileDialog.getOpenFileName(
        None, "读取设定", "./", "CSV Files (*.csv)"
    )
    if not directory[0]:
        return None
    try:
        result = load_settings_from_path(ui, directory[0], show_message=True)
    except Exception as exc:
        QMessageBox.warning(None, "提示信息", "设定文件读取失败: %s" % exc)
        return None
    return result


def apply_send_wt_metadata(plan: dict, *, margin_s: int = 30, min_stop_s: int = 120) -> Optional[str]:
    """Mirror thaidynamicmpptSend WT FileNameList / StopTime writeback. Returns stop_str or None."""

    wt_rounds = int(plan.get("wt_rounds") or 0)
    file_names = list(plan.get("file_names") or [])
    if plan.get("wt_is_checked") != "1" or wt_rounds <= 0 or not file_names:
        return None
    file_list_text = file_names[0]
    stop_sec = int(round(int(plan.get("band_duration_01s") or 0) / 10.0 + margin_s))
    if stop_sec < min_stop_s:
        stop_sec = min_stop_s
    hh, rem = divmod(stop_sec, 3600)
    mm, ss = divmod(rem, 60)
    stop_str = "%02d:%02d:%02d" % (hh, mm, ss)
    from utils.wt_recording_mode import patch_last_upper_wt_config

    patch_last_upper_wt_config(
        plan.get("commands") or [],
        file_list_text=file_list_text,
        stop_time=stop_str,
    )
    return stop_str


Open_File_Thaidynamicmppt = Open_File_ThaiDynamicMPPT
Save_File_Thaidynamicmppt = Save_File_ThaiDynamicMPPT

__all__ = [
    "FILE_TAG",
    "HEADERS",
    "Open_File_ThaiDynamicMPPT",
    "Open_File_Thaidynamicmppt",
    "Save_File_ThaiDynamicMPPT",
    "Save_File_Thaidynamicmppt",
    "TEST_TYPE",
    "apply_send_wt_metadata",
    "arrayRow1",
    "load_settings_from_path",
    "save_settings_to_path",
]
