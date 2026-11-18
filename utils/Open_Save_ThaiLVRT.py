# -*- coding: utf-8 -*-
"""LVRT settings persistence: UTF-8-sig, GBK fallback and named JSON tails."""

from __future__ import annotations

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from utils.timing_profile import LVRT_SCHEMA
from utils.timing_profile_adapters import (
    append_dewetron_settings_tail,
    build_settings_headers,
    restore_dewetron_settings_tail,
    write_settings_csv,
    read_settings_csv,
)


FILE_TAG = "ThaiLVRT"
TEST_TYPE = "lvrt"
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
            arrayRow1,
            file_tag=FILE_TAG,
            schema=LVRT_SCHEMA,
            test_type=TEST_TYPE,
        )
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
        result = read_settings_csv(
            directory[0],
            ui,
            file_tag=FILE_TAG,
            schema=LVRT_SCHEMA,
        )
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
    "Open_File_ThaiLVRT",
    "Open_File_Thailvrt",
    "Save_File_ThaiLVRT",
    "Save_File_Thailvrt",
    "TEST_TYPE",
    "_append_dewetron_tail",
    "_restore_dewetron_tail",
    "arrayRow1",
]
