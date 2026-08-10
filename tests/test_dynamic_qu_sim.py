# -*- coding: utf-8 -*-
"""动态 Q(U) 离屏模拟：Dialog + 连续录计划 + Open/Save + 注册检查。"""

from __future__ import annotations

import ast
import csv
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from Dialog_thaidynamicQU import Ui_Dialog_thaidynamicQU
from utils.dynamic_qu_commands import (
    DEFAULT_FILE_NAME,
    build_dynamic_qu_plan,
    default_dc_iv_resolver,
)
from utils.Open_Save_ThaiDynamicQU import FILE_TAG, HEADERS, _apply_csv_value, _widget_to_csv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = PROJECT_ROOT / "SCPITestWave.py"


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def dyn_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaidynamicQU()
    ui.setupUi(dialog)
    yield ui, dialog
    dialog.close()
    dialog.deleteLater()


def _fill_step1(ui, *, three_phase=False, dc1=True):
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("三相" if three_phase else "单相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("231")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("232")
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


def _fill_ladder(ui, ladder="100,103,105", dwell="5", unit="秒"):
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_VoltageLadder.setPlainText(ladder)
    ui.textEdit_VoltageLadder_Un.setPlainText("230")
    ui.textEdit_VoltageLadder_FR.setPlainText("50")
    ui.textEdit_VoltageLadder_TIME.setPlainText(dwell)
    ui.comboBox_VoltageLadder_TIME.setCurrentText(unit)


def test_dialog_four_steps_and_default_list(dyn_ui):
    ui, _ = dyn_ui
    assert ui.stackedWidget.count() == 4
    u = [float(x) for x in ui.textEdit_VoltageLadder.toPlainText().replace(" ", "").split(",") if x]
    assert len(u) == 23
    assert u[0] == 100 and u[8] == 115 and u[-1] == 85
    assert ui.textEdit_VoltageLadder_TIME is not None


def test_continuous_async_no_numeric_col6(dyn_ui):
    ui, _ = dyn_ui
    _fill_step1(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _fill_ladder(ui, "100,103,105", dwell="10", unit="秒")
    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")
    ui.checkBox_S_END_DC1.setChecked(True)
    ui.comboBox_S_END_DC1.setCurrentText("关闭")

    plan = build_dynamic_qu_plan(
        ui, wt_config_dict={"mock": 1}, str_add_flag="0", dc_iv_resolver=default_dc_iv_resolver
    )
    assert plan["ok"]
    assert plan["u_pct_list"] == [100.0, 103.0, 105.0]
    assert plan["wt_rounds"] == 1
    assert plan["file_name"] == DEFAULT_FILE_NAME
    markers = [str(r[6]).upper() for r in plan["commands"] if len(r) > 6 and r[6] not in ("", None)]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1
    assert not any(str(m).lstrip("-").isdigit() for m in markers)
    triples = [(r[0], r[1], r[2]) for r in plan["commands"]]
    assert ("DC1", "write", "OUTP:MODE TABLE") in triples
    assert ("AC", "write", "OUTP OFF") in triples
    assert ("DC1", "write", "OUTP OFF") in triples


def test_three_phase_ladder(dyn_ui):
    ui, _ = dyn_ui
    _fill_step1(ui, three_phase=True, dc1=False)
    ui.checkBox_S2.setChecked(False)
    _fill_ladder(ui, "100,110", dwell="1", unit="秒")
    ui.checkBox_S_END.setChecked(False)
    plan = build_dynamic_qu_plan(ui, wt_config_dict={})
    assert plan["ok"]
    triples = [(r[0], r[1], r[2]) for r in plan["commands"]]
    assert ("AC", "write", "INST:PHAS THREE") in triples
    assert any(t[2] == "VOLT 253.0" or t[2] == "VOLT 254.1" for t in triples)


def test_settings_csv_roundtrip(dyn_ui, tmp_path):
    ui, _ = dyn_ui
    _fill_step1(ui)
    _fill_ladder(ui, "100,107,93", dwell="8", unit="秒")
    path = tmp_path / "dyn_qu.csv"
    values = [FILE_TAG]
    for name in HEADERS[1:]:
        if name.startswith("checkBox_S2_WT"):
            values.append("1" if name.endswith("WT3000") and ui.radioButton_S2_WT3000.isChecked() else "0")
        else:
            values.append(_widget_to_csv(ui, name))
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(list(HEADERS))
        w.writerow(values)
    ui.textEdit_VoltageLadder.setPlainText("")
    with path.open("r", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    for i, name in enumerate(rows[0]):
        if i == 0:
            continue
        _apply_csv_value(ui, name, rows[1][i])
    assert ui.textEdit_VoltageLadder.toPlainText() == "100,107,93"
    assert ui.textEdit_VoltageLadder_TIME.toPlainText() == "8"


def test_shutdown_requires_step1_dc(dyn_ui):
    ui, _ = dyn_ui
    _fill_step1(ui, dc1=False)
    ui.checkBox_S2.setChecked(False)
    ui.checkBox_S3.setChecked(False)
    ui.checkBox_S_END.setChecked(True)
    ui.checkBox_S_END_DC1.setChecked(True)
    ui.comboBox_S_END_DC1.setCurrentText("关闭")
    plan = build_dynamic_qu_plan(ui)
    triples = [(r[0], r[1], r[2]) for r in plan["commands"]]
    assert ("DC1", "write", "OUTP OFF") not in triples


def test_main_registers_dynamic_qu():
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "动态QU" in src
    assert "def thaidynamicQUAppend" in src
    assert "build_dynamic_qu_plan" in src
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "thaidynamicQUAppend")
    calls = [n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert "thaidynamicQUSend" in calls
