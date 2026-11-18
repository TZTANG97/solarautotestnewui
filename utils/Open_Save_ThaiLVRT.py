# -*- coding: utf-8 -*-
"""LVRT settings persistence: UTF-8-sig, GBK fallback and named JSON tails."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from utils.timing_profile import LVRT_SCHEMA, TIMING_PROFILE_JSON_COLUMN
from utils.timing_profile_adapters import (
    append_dewetron_settings_tail,
    apply_settings_rows,
    build_settings_headers,
    read_csv_rows_with_fallback,
    restore_dewetron_settings_tail,
    write_settings_csv,
)


FILE_TAG = "ThaiLVRT"
TEST_TYPE = "lvrt"
PHASE_CONDITIONS_JSON_COLUMN = "LVRT_PHASE_CONDITIONS_JSON"
arrayRow1 = build_settings_headers()
HEADERS = arrayRow1


def _ui(kwargs):
    if isinstance(kwargs, dict):
        return kwargs.get("uiThaiLVRT") or kwargs.get("ui")
    return kwargs


def _append_dewetron_tail(values, ui):
    return append_dewetron_settings_tail(
        arrayRow1, values, ui, test_type=TEST_TYPE
    )


def _restore_dewetron_tail(headers, values, ui):
    return restore_dewetron_settings_tail(headers, values, ui)


def _inject_phase_header(headers):
    out = list(headers)
    if PHASE_CONDITIONS_JSON_COLUMN in out:
        return out
    if TIMING_PROFILE_JSON_COLUMN in out:
        idx = out.index(TIMING_PROFILE_JSON_COLUMN) + 1
    else:
        idx = len(out)
    out.insert(idx, PHASE_CONDITIONS_JSON_COLUMN)
    return out


def _phase_json_from_ui(ui) -> str:
    widget = getattr(ui, "lvrtConditionList", None)
    if widget is None:
        return "[]"
    try:
        rows = widget.get_rows(include_disabled=True)
    except Exception:
        rows = []
    return json.dumps(list(rows or []), ensure_ascii=False)


def _apply_phase_json(ui, raw) -> None:
    widget = getattr(ui, "lvrtConditionList", None)
    if widget is None:
        return
    try:
        rows = json.loads(raw or "[]")
    except (TypeError, ValueError, json.JSONDecodeError):
        rows = []
    if not isinstance(rows, list):
        rows = []
    widget.set_rows(rows)


def _rewrite_with_phase_column(path, ui) -> None:
    """Inject LVRT_PHASE_CONDITIONS_JSON into an already-written settings CSV."""
    rows = read_csv_rows_with_fallback(path)
    if len(rows) < 2:
        return
    old_headers = list(rows[0])
    old_values = list(rows[1])
    if len(old_values) < len(old_headers):
        old_values.extend([""] * (len(old_headers) - len(old_values)))

    headers = _inject_phase_header(old_headers)
    phase_json = _phase_json_from_ui(ui)
    if PHASE_CONDITIONS_JSON_COLUMN in old_headers:
        values = list(old_values)
        values[old_headers.index(PHASE_CONDITIONS_JSON_COLUMN)] = phase_json
    else:
        insert_at = headers.index(PHASE_CONDITIONS_JSON_COLUMN)
        values = list(old_values)
        values.insert(insert_at, phase_json)

    target = Path(path)
    with target.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerow(values)
        for extra in rows[2:]:
            writer.writerow(list(extra))


def Save_File_ThaiLVRT(kwargs):
    ui = _ui(kwargs)
    directory = QFileDialog.getSaveFileName(
        None, "保存设定", "./", "CSV Files (*.csv)"
    )
    if not directory[0]:
        return None
    try:
        result = write_settings_csv(
            directory[0],
            ui,
            build_settings_headers(),
            file_tag=FILE_TAG,
            schema=LVRT_SCHEMA,
            test_type=TEST_TYPE,
        )
        _rewrite_with_phase_column(directory[0], ui)
    except Exception as exc:
        QMessageBox.warning(None, "提示信息", "设定文件保存失败: %s" % exc)
        return None
    QMessageBox.information(None, "提示信息", "设定文件保存完成")
    return result


def Open_File_ThaiLVRT(kwargs):
    ui = _ui(kwargs)
    directory = QFileDialog.getOpenFileName(
        None, "读取设定", "./", "CSV Files (*.csv)"
    )
    if not directory[0]:
        return None
    try:
        rows = read_csv_rows_with_fallback(directory[0])
        result = apply_settings_rows(
            rows,
            ui,
            file_tag=FILE_TAG,
            schema=LVRT_SCHEMA,
        )
        if len(rows) >= 2:
            config = dict(zip(list(rows[0]), list(rows[1])))
            _apply_phase_json(
                ui, config.get(PHASE_CONDITIONS_JSON_COLUMN, "[]")
            )
        else:
            _apply_phase_json(ui, "[]")
    except Exception as exc:
        QMessageBox.warning(None, "提示信息", "设定文件读取失败: %s" % exc)
        return None
    QMessageBox.information(None, "提示信息", "设定文件读取完成")
    return result


Save_File_Thailvrt = Save_File_ThaiLVRT
Open_File_Thailvrt = Open_File_ThaiLVRT


__all__ = [
    "FILE_TAG",
    "HEADERS",
    "PHASE_CONDITIONS_JSON_COLUMN",
    "Open_File_ThaiLVRT",
    "Open_File_Thailvrt",
    "Save_File_ThaiLVRT",
    "Save_File_Thailvrt",
    "TEST_TYPE",
    "_append_dewetron_tail",
    "_apply_phase_json",
    "_phase_json_from_ui",
    "_restore_dewetron_tail",
    "arrayRow1",
]
