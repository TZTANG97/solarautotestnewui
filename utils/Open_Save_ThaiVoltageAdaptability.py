# -*- coding: utf-8 -*-
"""棰戠巼閫傚簲鎬у�硅瘽妗嗭細璇诲彇/淇濆瓨 CSV 璁惧畾锛堜笌 ThaiGuoQianPin_Immun 绛夋ā鍧楅�庢牸涓€鑷达級銆�"""

import csv

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QTextEdit,
)

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

_DEWETRON_SPEC = PROJECT_SPECS["电压适应性"]


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
    """Restore named DEWETRON data without requiring a newer dialog build."""
    try:
        mode, config = read_dewetron_tail_columns(headers, values)
    except (IndexError, TypeError, ValueError):
        mode, config = read_dewetron_tail_columns([], [])
    section = getattr(ui, "analyzerModeSection", None)
    if section is not None:
        set_config = getattr(section, "set_dewetron_config", None)
        if not callable(set_config):
            set_config = getattr(section, "set_config", None)
        if callable(set_config):
            set_config(config)
        set_mode = getattr(section, "set_mode", None)
        if callable(set_mode):
            set_mode(mode)
    return mode, config


FILE_TAG = "ThaiVoltageAdaptability"


def _build_headers():
    """????????? Style??????????????????????????????"""
    h = ["Style"]
    h += [
        "checkBox_S1",
        "comboBox_S1_AC",
        "textEdit_S1_AC_VOLT",
        "textEdit_S1_AC_VOLT_2",
        "textEdit_S1_AC_VOLT_3",
        "textEdit_S1_AC_FR",
        "comboBox_S1_AC_2",
    ]
    for d in range(1, 5):
        h += [
            "checkBox_S1_DC%d" % d,
            "comboBox_S1_DC%d" % d,
            "textEdit_S1_DC%d_VOLT" % d,
            "textEdit_S1_DC%d_CURR" % d,
            "textEdit_S1_DC%d_Voc" % d,
            "textEdit_S1_DC%d_Isc" % d,
            "textEdit_S1_DC%d_PF" % d,
        ]
    h += [
        "textEdit_S1_ACWaitTIME",
        "comboBox_S1_ACWaitTIME",
        "textEdit_S1_TIME",
        "comboBox_S1_TIME",
        "checkBox_S2",
        "checkBox_S2_WT3000",
        "checkBox_S2_WT1800",
        "checkBox_S2_WT1806E",
        "checkBox_S2_WT5000",
        "checkBox_S2_update_rate",
        "textEdit_S2_update_rate",
        "comboBox_S2_update_rate",
    ]
    for i in range(9):
        gp = 3 + i
        qp = 12 + i
        h += [
            "checkBox_S%d" % gp,
            "checkBox_S%d_RATE" % gp,
            "textEdit_S%d_volt_start_guoya" % gp,
            "textEdit_S%d_volt_end_guoya" % gp,
            "textEdit_S%d_test_duration_guoya" % gp,
            "comboBox_S%d_test_time_unit_guoya" % gp,
            "checkBox_S%d" % qp,
            "checkBox_S%d_RATE" % qp,
            "textEdit_S%d_volt_start_qianya" % qp,
            "textEdit_S%d_volt_end_qianya" % qp,
            "textEdit_S%d_test_duration_qianya" % qp,
            "comboBox_S%d_test_time_unit_qianya" % qp,
        ]
    h += [
        "checkBox_S_End",
        "comboBox_S_End_AC",
        "checkBox_S_End_DC1",
        "comboBox_S_End_DC1",
        "checkBox_S_End_DC2",
        "comboBox_S_End_DC2",
        "checkBox_S_End_DC3",
        "comboBox_S_End_DC3",
        "checkBox_S_End_DC4",
        "comboBox_S_End_DC4",
    ]
    return h


HEADERS = _build_headers()
arrayRow1 = HEADERS


def _resolve_widget(ui, name):
    """Dialog step3~20 widgets live under QGroupBox children; prefer setattr attrs."""
    w = getattr(ui, name, None)
    if w is not None:
        return w
    # Ui_* 不是 QWidget，不能直接 findChild；若传入的是 QDialog 才可用
    find = getattr(ui, "findChild", None)
    if not callable(find):
        return None
    if name.startswith("checkBox"):
        return find(QCheckBox, name)
    if name.startswith("comboBox"):
        return find(QComboBox, name)
    if name.startswith("textEdit"):
        return find(QTextEdit, name)
    return None


def _widget_to_csv(ui, name):
    w = _resolve_widget(ui, name)
    if w is None:
        return ""
    if name.startswith("checkBox"):
        return "1" if w.isChecked() else "0"
    if name.startswith("comboBox"):
        return str(w.currentIndex())
    if name.startswith("textEdit"):
        return w.toPlainText()
    return ""


def _apply_csv_value(ui, name, val):
    if val is None:
        val = ""
    w = _resolve_widget(ui, name)
    if w is None:
        return
    if name.startswith("checkBox"):
        w.setChecked(val in ("1", "true", "True", "yes"))
    elif name.startswith("comboBox"):
        try:
            w.setCurrentIndex(int(val))
        except (ValueError, TypeError):
            pass
    elif name.startswith("textEdit"):
        w.setPlainText(str(val))


def Save_File_ThaiVoltageAdaptability(kwargs):
    """????????????? Immun ?????????? WT ???????? 3??4 ????? WT ???????? WT ???????????????????"""
    dialog_window = kwargs["dialog_window"]
    ui = kwargs["uiThaiVoltageAdaptability"]
    ui_thia_wt3000e = kwargs["uiThiaWT3000E"]
    ui_thia_wt1800 = kwargs["uiThiaWT1800"]
    ui_thia_wt1806e = kwargs["uiThiaWT1806E"]
    ui_thia_wt5000 = kwargs["uiThiaWT5000"]

    directory = QFileDialog.getSaveFileName(
        None,
        "保存设定",
        "./",
        "Text Files(*.csv)",
    )
    if not directory[0]:
        return
    row = [FILE_TAG]
    for col in HEADERS[1:]:
        row.append(_widget_to_csv(ui, col))

    headers = list(arrayRow1)
    _append_dewetron_tail(row, ui)
    headers = list(arrayRow1)

    result = []
    if ui.radioButton_S2_WT3000.isChecked():
        result = Save_File_ThaiWT3000_Config(_PageWidgetFinder(ui._wtStacked.widget(0)))
    if ui.radioButton_S2_WT1800.isChecked():
        result = Save_File_ThaiWT1800_Config(_PageWidgetFinder(ui._wtStacked.widget(1)))
    if ui.radioButton_S2_WT1806E.isChecked():
        result = Save_File_ThaiWT1806E_Config(_PageWidgetFinder(ui._wtStacked.widget(2)))
    if ui.radioButton_S2_WT5000.isChecked():
        result = Save_File_ThaiWT5000_Config(_PageWidgetFinder(ui._wtStacked.widget(3)))

    with open(directory[0], "w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.writer(fp)
        writer.writerow(headers)
        writer.writerow(row)
        if len(result) > 0:
            writer.writerow(result[0])
            writer.writerow(result[1])
    QMessageBox.information(
        None,
        "提示信息",
        "设定文件保存完成",
        QMessageBox.Ok,
        QMessageBox.Ok,
    )


def Open_File_ThaiVoltageAdaptability(kwargs):
    dialog_window = kwargs["dialog_window"]
    ui = kwargs["uiThaiVoltageAdaptability"]
    ui_thia_wt3000e = kwargs["uiThiaWT3000E"]
    ui_thia_wt1800 = kwargs["uiThiaWT1800"]
    ui_thia_wt1806e = kwargs["uiThiaWT1806E"]
    ui_thia_wt5000 = kwargs["uiThiaWT5000"]

    directory = QFileDialog.getOpenFileName(
        None,
        "读取设定",
        "./",
        "Text Files(*.csv)",
    )
    if not directory[0]:
        return
    with open(directory[0], "r", newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    if len(rows) < 2:
        QMessageBox.warning(
            None,
            "提示信息",
            "设定文件内容不完整，无法读取",
            QMessageBox.Ok,
            QMessageBox.Ok,
        )
        return
    header_row = rows[0]
    data_row = rows[1]
    delta = len(header_row) - len(data_row)
    if delta > 0:
        data_row.extend([""] * delta)
    config = dict(zip(header_row, data_row))
    if config.get(HEADERS[0]) != FILE_TAG:
        QMessageBox.warning(
            None,
            "提示信息",
            "文件类型不匹配，需要 %s 格式" % FILE_TAG,
            QMessageBox.Ok,
            QMessageBox.Ok,
        )
        return

    wt_config_dict = {}
    if len(rows) >= 4:
        h_wt = rows[2]
        d_wt = list(rows[3])
        delta_wt = len(h_wt) - len(d_wt)
        if delta_wt > 0:
            d_wt.extend([""] * delta_wt)
        wt_config_dict = dict(zip(h_wt, d_wt))

    for col in HEADERS[1:]:
        if col in config:
            _apply_csv_value(ui, col, config[col])

    if ui.radioButton_S2_WT3000.isChecked():
        Open_File_ThaiWT3000_Config(_PageWidgetFinder(ui._wtStacked.widget(0)), wt_config_dict)
    if ui.radioButton_S2_WT1800.isChecked():
        Open_File_ThaiWT1800_Config(_PageWidgetFinder(ui._wtStacked.widget(1)), wt_config_dict)
    if ui.radioButton_S2_WT1806E.isChecked():
        Open_File_ThaiWT1806E_Config(_PageWidgetFinder(ui._wtStacked.widget(2)), wt_config_dict)
    if ui.radioButton_S2_WT5000.isChecked():
        Open_File_ThaiWT5000_Config(_PageWidgetFinder(ui._wtStacked.widget(3)), wt_config_dict)

    _restore_dewetron_tail(header_row, data_row, ui)

    QMessageBox.information(
        None,
        "提示信息",
        "设定文件读取完成",
        QMessageBox.Ok,
        QMessageBox.Ok,
    )
