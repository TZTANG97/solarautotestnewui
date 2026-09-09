# -*- coding: utf-8 -*-
"""无功能力范围离屏模拟：Dialog + 命令计划 + Open/Save + 主程序接线。"""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from Dialog_thaireactiveQcap import Ui_Dialog_thaireactiveQcap
from utils.reactive_qcap_commands import (
    build_reactive_qcap_plan,
    default_dc_iv_resolver,
)
from utils.Open_Save_ThaiReactiveQCap import (
    FILE_TAG,
    HEADERS,
    _apply_csv_value,
    _widget_to_csv,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = PROJECT_ROOT / "SCPITestWave.py"


@pytest.fixture(scope="module")
def qapp():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app


@pytest.fixture
def qcap_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaireactiveQcap()
    ui.setupUi(dialog)
    yield ui, dialog
    dialog.close()
    dialog.deleteLater()


def _fill_step1_single(ui, *, dc1=True):
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("单相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("1")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.textEdit_S1_TIME.setPlainText("2")
    ui.comboBox_S1_TIME.setCurrentText("秒")
    for ch in range(1, 5):
        getattr(ui, "checkBox_S1_DC%d" % ch).setChecked(False)
    if dc1:
        ui.checkBox_S1_DC1.setChecked(True)
        ui.comboBox_S1_DC1.setCurrentText("开启")
        ui.textEdit_S1_DC1_VOLT.setPlainText("400")
        ui.textEdit_S1_DC1_CURR.setPlainText("10")
        ui.textEdit_S1_DC1_Voc.setPlainText("450")
        ui.textEdit_S1_DC1_Isc.setPlainText("12")
        ui.textEdit_S1_DC1_PF.setPlainText("100")


def _fill_ladder(ui, ladder="10,50,100", dwell="5", unit="秒", record_mode="split"):
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_PowerLadder.setPlainText(ladder)
    ui.textEdit_S3_TIME_2.setPlainText(dwell)
    ui.comboBox_S3_TIME_2.setCurrentText(unit)
    if hasattr(ui, "comboBox_S3_record_mode"):
        from utils.wt_recording_mode import mode_to_combo_index

        ui.comboBox_S3_record_mode.setCurrentIndex(mode_to_combo_index(record_mode))
    ui.checkBox_cos_pos09.setChecked(True)
    ui.checkBox_cos_neg09.setChecked(True)
    ui.checkBox_cos_1.setChecked(False)
    ui.checkBox_S3_DC1.setChecked(True)
    for ch in range(2, 5):
        getattr(ui, "checkBox_S3_DC%d" % ch).setChecked(False)


def test_dialog_has_four_steps_and_cos_points(qcap_ui):
    ui, _dialog = qcap_ui
    assert ui.stackedWidget.count() == 4
    assert ui._wtStacked.count() == 4
    assert "10" in ui.textEdit_PowerLadder.toPlainText()
    assert ui.checkBox_cos_pos09.isChecked()
    assert ui.checkBox_cos_neg09.isChecked()
    assert hasattr(ui, "analyzerModeSection")
    assert hasattr(ui, "comboBox_S3_record_mode")
    assert ui.pushButton_S3_fill_filenames is not None


def test_power_times_cos_numeric_col6(qcap_ui):
    ui, _dialog = qcap_ui
    _fill_step1_single(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _fill_ladder(ui, "20,40", dwell="3", unit="秒", record_mode="split")
    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")
    ui.checkBox_S_END_DC1.setChecked(True)
    ui.comboBox_S_END_DC1.setCurrentText("关闭")

    plan = build_reactive_qcap_plan(
        ui,
        wt_config_dict={"mock": 1},
        str_add_flag="0",
        dc_iv_resolver=default_dc_iv_resolver,
    )
    assert plan["ok"] is True
    assert plan["dc_errors"] == []
    assert plan["power_levels"] == [20.0, 40.0]
    assert plan["cos_labels"] == ["cos0.9", "cos-0.9"]
    assert plan["wt_rounds"] == 4
    assert plan["wt_continuous"] is False
    assert plan["file_names"] == [
        "QCap_P20_cos0.9",
        "QCap_P20_cos-0.9",
        "QCap_P40_cos0.9",
        "QCap_P40_cos-0.9",
    ]

    numeric_col6 = [
        r[6]
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None) and str(r[6]).strip().lstrip("-").isdigit()
    ]
    assert len(numeric_col6) == 4
    assert all(int(x) == 30 for x in numeric_col6)  # 3s → 30 *0.1s

    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert "ASYNC_START" not in markers
    assert "WAIT_END" not in markers

    triples = [(r[0], r[1], r[2]) for r in plan["commands"]]
    assert ("DC1", "write", "OUTP:MODE TABLE") in triples
    assert ("AC", "write", "OUTP OFF") in triples


def test_continuous_async_single_file(qcap_ui):
    ui, _dialog = qcap_ui
    _fill_step1_single(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _fill_ladder(ui, "20,40", dwell="3", unit="秒", record_mode="continuous")
    ui.checkBox_S_END.setChecked(False)

    plan = build_reactive_qcap_plan(
        ui,
        wt_config_dict={"mock": 1},
        str_add_flag="0",
        dc_iv_resolver=default_dc_iv_resolver,
    )
    assert plan["ok"] is True
    assert plan["wt_continuous"] is True
    assert plan["wt_rounds"] == 1
    assert plan["file_names"] == ["QCap_BR"]

    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert "ASYNC_START" in markers
    assert "WAIT_END" in markers
    assert sum(1 for m in markers if m.isdigit()) == 0

    slot9_waits = [
        r[9]
        for r in plan["commands"]
        if len(r) > 9 and r[9] not in ("", None) and str(r[9]).strip().lstrip("-").isdigit()
    ]
    assert len(slot9_waits) >= 4  # 2 power × 2 cos


def test_requires_cos_selection(qcap_ui):
    ui, _dialog = qcap_ui
    _fill_step1_single(ui)
    ui.checkBox_S2.setChecked(False)
    _fill_ladder(ui, "50")
    ui.checkBox_cos_pos09.setChecked(False)
    ui.checkBox_cos_neg09.setChecked(False)
    ui.checkBox_cos_1.setChecked(False)
    ui.checkBox_S_END.setChecked(False)

    plan = build_reactive_qcap_plan(ui, wt_config_dict={}, str_add_flag="0")
    assert plan["ok"] is False
    assert "cos" in plan["error"].lower() or "极限" in plan["error"]


def test_settings_csv_roundtrip(qcap_ui, tmp_path):
    ui, _dialog = qcap_ui
    _fill_step1_single(ui, dc1=True)
    _fill_ladder(ui, "15,30,45", dwell="8", unit="秒")
    ui.checkBox_cos_1.setChecked(True)

    path = tmp_path / "reactive_qcap_settings.csv"
    values = [FILE_TAG]
    for name in HEADERS[1:]:
        if name == "checkBox_S2_WT3000":
            values.append("1" if ui.radioButton_S2_WT3000.isChecked() else "0")
        elif name.startswith("checkBox_S2_WT"):
            values.append("0")
        else:
            values.append(_widget_to_csv(ui, name))
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.writer(fp)
        writer.writerow(list(HEADERS))
        writer.writerow(values)

    ui.textEdit_PowerLadder.setPlainText("")
    ui.checkBox_cos_1.setChecked(False)
    with path.open("r", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    headers, vals = rows[0], rows[1]
    for i, name in enumerate(headers):
        if i == 0 or i >= len(vals):
            continue
        _apply_csv_value(ui, name, vals[i])

    assert ui.textEdit_PowerLadder.toPlainText() == "15,30,45"
    assert ui.textEdit_S3_TIME_2.toPlainText() == "8"
    assert ui.checkBox_cos_1.isChecked()


def test_main_wiring_mentions_reactive_qcap():
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "无功能力范围" in src
    assert "thaireactiveQcapSend" in src
    assert "thaireactiveQcapAppend" in src
    assert "dialog_windowreactiveQcap" in src
    assert "uiThaiReactiveQCap" in src
    assert "Open_Save_ThaiReactiveQCap" in src
    assert "build_reactive_qcap_plan" in src
    assert "reactiveQcap_append_count" in src


def test_opensave_headers_have_combo_end_dc():
    assert HEADERS.count("comboBox_S_END_DC1") == 1
    assert HEADERS.count("checkBox_S_END_DC1") == 1
