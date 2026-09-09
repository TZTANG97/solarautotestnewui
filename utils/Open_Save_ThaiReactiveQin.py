# -*- coding: utf-8 -*-
"""无功注入：读取/保存 CSV 设定。"""

import csv

from PyQt5.QtWidgets import QCheckBox, QComboBox, QFileDialog, QMessageBox, QTextEdit

from utils.Open_Save_ThaiWT3000_Config import Open_File_ThaiWT3000_Config, Save_File_ThaiWT3000_Config
from utils.Open_Save_ThaiWT1800_Config import Open_File_ThaiWT1800_Config, Save_File_ThaiWT1800_Config
from utils.Open_Save_ThaiWT1806E_Config import Open_File_ThaiWT1806E_Config, Save_File_ThaiWT1806E_Config
from utils.Open_Save_ThaiWT5000_Config import Open_File_ThaiWT5000_Config, Save_File_ThaiWT5000_Config
from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
from dewetron_autotest import (
    PROJECT_SPECS,
    append_dewetron_tail_columns,
    extract_ui_config,
    extract_ui_mode,
    read_dewetron_tail_columns,
)

_DEWETRON_SPEC = PROJECT_SPECS["无功注入"]
FILE_TAG = "ThaiReactiveQin"


def _append_dewetron_tail(values, ui):
    """Append or update this project's named DEWETRON persistence tail."""
    section = getattr(ui, "analyzerModeSection", None)
    source = section if section is not None else ui
    return append_dewetron_tail_columns(
        arrayRow1,
        values,
        extract_ui_config(source),
        mode=extract_ui_mode(source),
        test_type=_DEWETRON_SPEC.test_type,
        profile=_DEWETRON_SPEC.profile,
    )


def _restore_dewetron_tail(headers, values, ui):
    try:
        mode, config = read_dewetron_tail_columns(headers, values)
    except (IndexError, TypeError, ValueError):
        mode, config = read_dewetron_tail_columns([], [])
    section = getattr(ui, "analyzerModeSection", None)
    if section is not None:
        set_config = getattr(section, "set_dewetron_config", None) or getattr(section, "set_config", None)
        if callable(set_config):
            set_config(config)
        set_mode = getattr(section, "set_mode", None)
        if callable(set_mode):
            set_mode(mode)
    return mode, config


def _build_headers():
    h = ["Style", "checkBox_S1", "comboBox_S1_AC",
         "textEdit_S1_AC_VOLT", "textEdit_S1_AC_VOLT_2", "textEdit_S1_AC_VOLT_3",
         "textEdit_S1_AC_FR", "comboBox_S1_AC_2"]
    for d in range(1, 5):
        h += [
            "checkBox_S1_DC%d" % d, "comboBox_S1_DC%d" % d,
            "textEdit_S1_DC%d_VOLT" % d, "textEdit_S1_DC%d_CURR" % d,
            "textEdit_S1_DC%d_Voc" % d, "textEdit_S1_DC%d_Isc" % d,
            "textEdit_S1_DC%d_PF" % d,
        ]
    h += [
        "textEdit_S1_ACWaitTIME", "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME", "comboBox_S1_TIME",
        "checkBox_S2", "checkBox_S2_WT3000", "checkBox_S2_WT1800",
        "checkBox_S2_WT1806E", "checkBox_S2_WT5000",
        "checkBox_S3", "textEdit_PowerLadder", "textEdit_QLadder",
        "textEdit_S3_TIME_2", "comboBox_S3_TIME_2", "comboBox_S3_record_mode",
        "checkBox_S3_DC1", "checkBox_S3_DC2", "checkBox_S3_DC3", "checkBox_S3_DC4",
        "checkBox_S_END", "comboBox_S_END_AC",
        "checkBox_S_END_DC1", "comboBox_S_END_DC1",
        "checkBox_S_END_DC2", "comboBox_S_END_DC2",
        "checkBox_S_END_DC3", "comboBox_S_END_DC3",
        "checkBox_S_END_DC4", "comboBox_S_END_DC4",
    ]
    return h


HEADERS = _build_headers()
arrayRow1 = HEADERS


def _widget_to_csv(ui, name):
    w = getattr(ui, name, None)
    if w is None:
        return ""
    if isinstance(w, QCheckBox):
        return "1" if w.isChecked() else "0"
    if isinstance(w, QComboBox):
        return str(w.currentIndex())
    if isinstance(w, QTextEdit):
        return w.toPlainText()
    return ""


def _apply_csv_value(ui, name, value):
    w = getattr(ui, name, None)
    if w is None:
        return
    if isinstance(w, QCheckBox):
        w.setChecked(str(value) in ("1", "True", "true", "yes"))
    elif isinstance(w, QComboBox):
        try:
            w.setCurrentIndex(int(value))
        except (TypeError, ValueError):
            pass
    elif isinstance(w, QTextEdit):
        w.setPlainText("" if value is None else str(value))


def Save_File_ThaiReactiveQin(kwargs):
    ui = kwargs["uiThaiReactiveQin"]
    path = QFileDialog.getSaveFileName(None, "单个文件保存", "./", "Text Files(*.csv)")
    if not path[0]:
        return
    values = [FILE_TAG]
    for name in HEADERS[1:]:
        if name == "checkBox_S2_WT3000":
            values.append("1" if ui.radioButton_S2_WT3000.isChecked() else "0")
        elif name == "checkBox_S2_WT1800":
            values.append("1" if ui.radioButton_S2_WT1800.isChecked() else "0")
        elif name == "checkBox_S2_WT1806E":
            values.append("1" if ui.radioButton_S2_WT1806E.isChecked() else "0")
        elif name == "checkBox_S2_WT5000":
            values.append("1" if ui.radioButton_S2_WT5000.isChecked() else "0")
        else:
            values.append(_widget_to_csv(ui, name))
    _append_dewetron_tail(values, ui)
    with open(path[0], "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(arrayRow1)
        w.writerow(values)
    finder = _PageWidgetFinder(ui._wtStacked)
    if ui.radioButton_S2_WT3000.isChecked():
        Save_File_ThaiWT3000_Config({"uiThiaWT3000E": finder, "dialog_window": None})
    elif ui.radioButton_S2_WT1800.isChecked():
        Save_File_ThaiWT1800_Config({"uiThiaWT1800": finder, "dialog_window": None})
    elif ui.radioButton_S2_WT1806E.isChecked():
        Save_File_ThaiWT1806E_Config({"uiThiaWT1806E": finder, "dialog_window": None})
    elif ui.radioButton_S2_WT5000.isChecked():
        Save_File_ThaiWT5000_Config({"uiThiaWT5000": finder, "dialog_window": None})
    QMessageBox.information(None, "提示", "无功注入 设定已保存", QMessageBox.Ok)


def Open_File_ThaiReactiveQin(kwargs):
    ui = kwargs["uiThaiReactiveQin"]
    path = QFileDialog.getOpenFileName(None, "打开设定文件", "./", "Text Files(*.csv)")
    if not path[0]:
        return
    with open(path[0], "r", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    if len(rows) < 2:
        QMessageBox.information(None, "错误", "设定文件为空", QMessageBox.Ok)
        return
    headers, values = rows[0], rows[1]
    if values and values[0] not in (FILE_TAG, "ThaiReactiveQin"):
        QMessageBox.information(None, "错误", "不是无功注入设定文件", QMessageBox.Ok)
        return
    for i, name in enumerate(headers):
        if i == 0 or i >= len(values):
            continue
        if name == "checkBox_S2_WT3000" and str(values[i]) == "1":
            ui.radioButton_S2_WT3000.setChecked(True)
        elif name == "checkBox_S2_WT1800" and str(values[i]) == "1":
            ui.radioButton_S2_WT1800.setChecked(True)
        elif name == "checkBox_S2_WT1806E" and str(values[i]) == "1":
            ui.radioButton_S2_WT1806E.setChecked(True)
        elif name == "checkBox_S2_WT5000" and str(values[i]) == "1":
            ui.radioButton_S2_WT5000.setChecked(True)
        else:
            _apply_csv_value(ui, name, values[i])
    _restore_dewetron_tail(headers, values, ui)
    QMessageBox.information(None, "提示", "无功注入 设定已读取", QMessageBox.Ok)
