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


FILE_TAG = "ThaiFrequencyAdaptability"


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
            "textEdit_S%d_freq_start_guopin" % gp,
            "textEdit_S%d_freq_end_guopin" % gp,
            "textEdit_S%d_test_duration_guopin" % gp,
            "comboBox_S%d_test_time_unit_guopin" % gp,
            "checkBox_S%d" % qp,
            "textEdit_S%d_freq_start_qianpin" % qp,
            "textEdit_S%d_freq_end_qianpin" % qp,
            "textEdit_S%d_test_duration_qianpin" % qp,
            "comboBox_S%d_test_time_unit_qianpin" % qp,
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


def _resolve_widget(ui, name):
    """Dialog step3~20 widgets live under QGroupBox children; use objectName + findChild."""
    w = getattr(ui, name, None)
    if w is not None:
        return w
    if name.startswith("checkBox"):
        return ui.findChild(QCheckBox, name)
    if name.startswith("comboBox"):
        return ui.findChild(QComboBox, name)
    if name.startswith("textEdit"):
        return ui.findChild(QTextEdit, name)
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


def Save_File_ThaiFrequencyAdaptability(kwargs):
    """????????????? Immun ?????????? WT ???????? 3??4 ????? WT ???????? WT ???????????????????"""
    dialog_window = kwargs["dialog_window"]
    ui = kwargs["uiThaiFrequencyAdaptability"]
    ui_thia_wt3000e = kwargs["uiThiaWT3000E"]
    ui_thia_wt1800 = kwargs["uiThiaWT1800"]
    ui_thia_wt1806e = kwargs["uiThiaWT1806E"]
    ui_thia_wt5000 = kwargs["uiThiaWT5000"]

    directory = QFileDialog.getSaveFileName(
        dialog_window,
        "???????????",
        "./",
        "Text Files(*.csv)",
    )
    if not directory[0]:
        return
    row = [FILE_TAG]
    for col in HEADERS[1:]:
        row.append(_widget_to_csv(ui, col))

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
        writer.writerow(HEADERS)
        writer.writerow(row)
        if len(result) > 0:
            writer.writerow(result[0])
            writer.writerow(result[1])
    QMessageBox.information(
        dialog_window,
        "????څ??????",
        "???????????????????????",
        QMessageBox.Ok,
        QMessageBox.Ok,
    )


def Open_File_ThaiFrequencyAdaptability(kwargs):
    dialog_window = kwargs["dialog_window"]
    ui = kwargs["uiThaiFrequencyAdaptability"]
    ui_thia_wt3000e = kwargs["uiThiaWT3000E"]
    ui_thia_wt1800 = kwargs["uiThiaWT1800"]
    ui_thia_wt1806e = kwargs["uiThiaWT1806E"]
    ui_thia_wt5000 = kwargs["uiThiaWT5000"]

    directory = QFileDialog.getOpenFileName(
        dialog_window,
        "??????????",
        "./",
        "Text Files(*.csv)",
    )
    if not directory[0]:
        return
    with open(directory[0], "r", newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    if len(rows) < 2:
        QMessageBox.warning(
            dialog_window,
            "????څ??????",
            "?????????????????????????????????????",
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
            dialog_window,
            "????څ??????",
            "??????????????????????????????? %s????" % FILE_TAG,
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

    QMessageBox.information(
        dialog_window,
        "????څ??????",
        "??????????????????????",
        QMessageBox.Ok,
        QMessageBox.Ok,
    )
