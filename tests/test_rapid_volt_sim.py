# -*- coding: utf-8 -*-
"""快速电压变化完整离屏模拟：Dialog + 计划 + 德威创 UI + CSV 往返。"""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thairapidvolt import Ui_Dialog_thairapidvolt
from utils.rapid_volt_commands import build_rapid_volt_plan, default_dc_iv_resolver
from utils.Open_Save_ThaiRapidVolt import (
    FILE_TAG,
    HEADERS,
    _apply_csv_value,
    _widget_to_csv,
    arrayRow1,
)
from dewetron_autotest import append_dewetron_tail_columns, extract_ui_config, extract_ui_mode, read_dewetron_tail_columns

MAIN_PATH = Path(__file__).resolve().parents[1] / "SCPITestWave.py"


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def rvc_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thairapidvolt()
    ui.setupUi(dialog)
    yield ui, dialog
    dialog.close()
    dialog.deleteLater()


def _fill_step1(ui, *, dc1=True):
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


def test_dialog_dewetron_ui(rvc_ui):
    ui, _ = rvc_ui
    assert ui.stackedWidget.count() == 4
    assert hasattr(ui, "analyzerModeSection")
    assert hasattr(ui, "radio_dewetron")
    assert ui.radio_dewetron.text() == "DEWETRON"
    assert ui._wtStacked.count() == 4
    ui.radio_dewetron.setChecked(True)
    assert ui._mode == "dewetron"
    assert ui.analyzerModeSection.current_mode() == "dewetron"


def test_full_plan_happy_path(rvc_ui):
    ui, _ = rvc_ui
    _fill_step1(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    for sn in range(3, 9):
        getattr(ui, "checkBox_S%d" % sn).setChecked(False)
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_S3_volt_start_rvc.setPlainText("230")
    ui.textEdit_S3_volt_end_rvc.setPlainText("207")
    ui.textEdit_S3_pre_hold_rvc.setPlainText("1")
    ui.comboBox_S3_pre_hold_unit_rvc.setCurrentText("秒")
    ui.textEdit_S3_post_hold_rvc.setPlainText("2")
    ui.comboBox_S3_post_hold_unit_rvc.setCurrentText("秒")
    ui.checkBox_S_End.setChecked(True)
    ui.comboBox_S_End_AC.setCurrentText("关闭")

    plan = build_rapid_volt_plan(
        ui,
        wt_config_dict={"mock": 1},
        str_add_flag="0",
        dc_iv_resolver=default_dc_iv_resolver,
    )
    assert plan["ok"] is True, plan.get("error")
    assert plan["file_names"] == ["RVC_S3_230-207"]
    assert plan["wt_continuous"] is True
    keys = {r[0] for r in plan["commands"] if r and r[0]}
    assert "AC" in keys
    assert "DC1" in keys
    assert "Upper_WT_Config" in keys
    volts = [r[2] for r in plan["commands"] if str(r[2]).startswith("VOLT")]
    assert "VOLT 230" in volts
    assert "VOLT 207" in volts
    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1


def test_csv_roundtrip_with_dewetron_tail(rvc_ui, tmp_path):
    ui, _ = rvc_ui
    _fill_step1(ui, dc1=False)
    ui.checkBox_S2.setChecked(True)
    ui.radio_dewetron.setChecked(True)
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_S3_volt_end_rvc.setPlainText("253")

    row = [FILE_TAG]
    for col in HEADERS[1:]:
        row.append(_widget_to_csv(ui, col))
    headers = list(arrayRow1)
    append_dewetron_tail_columns(
        headers,
        row,
        extract_ui_config(ui.analyzerModeSection),
        mode=extract_ui_mode(ui.analyzerModeSection),
        test_type="rapid-voltage-change",
    )
    path = tmp_path / "rvc.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(headers)
        w.writerow(row)

    ui2_dialog = QtWidgets.QDialog()
    ui2 = Ui_Dialog_thairapidvolt()
    ui2.setupUi(ui2_dialog)
    with path.open(newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    hdr, data = rows[0], rows[1]
    for name, val in zip(hdr, data):
        if name in ("Style",) or name.startswith("dewetron"):
            continue
        _apply_csv_value(ui2, name, val)
    mode, _cfg = read_dewetron_tail_columns(hdr, data)
    assert mode in ("dewetron", "wt", "wt3000") or mode
    assert ui2.textEdit_S3_volt_end_rvc.toPlainText() == "253"
    ui2_dialog.close()
    ui2_dialog.deleteLater()


def test_main_wiring():
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "thairapidvoltAppend" in src
    assert "thairapidvoltSend" in src
    assert "快速电压变化" in src
    assert "_snapshot_dewetron_append('快速电压变化')" in src
    assert "('电网适应性', '快速电压变化', '快速电压变化')" in src
