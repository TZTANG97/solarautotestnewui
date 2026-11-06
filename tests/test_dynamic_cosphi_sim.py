# -*- coding: utf-8 -*-
"""动态 Cosφ(P) 离屏模拟：Dialog + 命令计划 + Open/Save + Append 计数。"""

from __future__ import annotations

import ast
import csv
import os
import tempfile
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thaidynamiccosPhi import Ui_Dialog_thaidynamiccosPhi
from utils.dynamic_cosphi_commands import (
    DEFAULT_FILE_NAME,
    build_dynamic_cosphi_plan,
    default_dc_iv_resolver,
)
from utils.Open_Save_ThaiDynamicCosPhi import (
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
def dyn_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaidynamiccosPhi()
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


def _fill_ladder(ui, ladder="20,40,60", dwell="5", unit="秒", base_pf="100"):
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_PowerLadder.setPlainText(ladder)
    ui.textEdit_S3_TIME_2.setPlainText(dwell)
    ui.comboBox_S3_TIME_2.setCurrentText(unit)
    ui.textEdit_S3_DC_PF.setPlainText(base_pf)
    ui.checkBox_S3_DC1.setChecked(True)
    for ch in range(2, 5):
        getattr(ui, "checkBox_S3_DC%d" % ch).setChecked(False)


def _cmds(plan):
    return [(r[0], r[1], r[2]) for r in plan["commands"]]


def _markers(plan):
    return [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]


# --------------------------------------------------------------------------- #
# 1. Dialog 结构
# --------------------------------------------------------------------------- #
def test_dialog_has_four_steps_and_ladder(dyn_ui):
    ui, _dialog = dyn_ui
    assert ui.stackedWidget.count() == 4
    assert ui._wtStacked.count() == 4
    assert ui.textEdit_PowerLadder.toPlainText().startswith("20,40,60")
    assert ui.textEdit_S3_TIME_2 is not None
    assert ui.comboBox_S3_TIME_2 is not None
    assert ui.pushButton_TestAppend is not None
    assert ui.label_append_count is not None
    assert hasattr(ui, "analyzerModeSection")


# --------------------------------------------------------------------------- #
# 2–5. 命令矩阵 / DC 启动链 / WT 元数据 / 三相
# --------------------------------------------------------------------------- #
def test_ladder_async_wait_end_no_numeric_col6(dyn_ui):
    ui, _dialog = dyn_ui
    _fill_step1_single(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _fill_ladder(ui, "20,40,60,80", dwell="10", unit="秒")
    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")
    ui.checkBox_S_END_DC1.setChecked(True)
    ui.comboBox_S_END_DC1.setCurrentText("关闭")

    plan = build_dynamic_cosphi_plan(
        ui,
        wt_config_dict={"mock": 1},
        str_add_flag="0",
        dc_iv_resolver=default_dc_iv_resolver,
    )
    assert plan["ok"] is True
    assert plan["dc_errors"] == []
    assert plan["power_levels"] == [20.0, 40.0, 60.0, 80.0]
    assert plan["wt_rounds"] == 1
    assert plan["wt_continuous"] is True
    assert plan["file_name"] == DEFAULT_FILE_NAME

    # N 点阶梯 → N 次 IVC（step1 启机另有 1 次额定 IVC，故只统计 ASYNC_START 之后）
    async_idx = next(
        i for i, r in enumerate(plan["commands"]) if len(r) > 6 and str(r[6]).upper() == "ASYNC_START"
    )
    ladder_ivc = [
        r
        for r in plan["commands"][async_idx:]
        if r[0] == "DC1" and str(r[2]).startswith("IVC:IT")
    ]
    # 首档 IVC 在 ASYNC_START 之前写入，故再并入 ASYNC 前最近一条
    pre_ivc = [
        r
        for r in plan["commands"][:async_idx]
        if r[0] == "DC1" and str(r[2]).startswith("IVC:IT")
    ]
    assert len(pre_ivc) >= 1  # 启机 + 首档
    # 首档在 ASYNC 前：启机额定 + 首档缩放；其后 3 档在 ASYNC 后
    assert len(ladder_ivc) == 3
    assert len(pre_ivc) == 2

    markers = _markers(plan)
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1
    numeric_col6 = [
        r[6]
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None) and str(r[6]).strip().lstrip("-").isdigit()
    ]
    assert numeric_col6 == []

    triples = _cmds(plan)
    assert ("DC1", "write", "OUTP:MODE TABLE") in triples
    assert ("DC1", "write", "IVCurve:SELect 1") in triples
    assert ("DC1", "write", "OUTP ON") in triples
    assert ("AC", "write", "OUTP OFF") in triples
    assert ("DC1", "write", "OUTP OFF") in triples

    # StopTime 估算：总驻留 40s + 余量 → Send 侧会写；plan 暴露 band_duration
    assert plan["band_duration_01s"] == 400  # 10s * 4 * 10(0.1s)


def test_three_phase_voltage(dyn_ui):
    ui, _dialog = dyn_ui
    _fill_step1_single(ui, dc1=False)
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("231")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("232")
    ui.checkBox_S2.setChecked(False)
    ui.checkBox_S3.setChecked(False)
    ui.checkBox_S_END.setChecked(False)

    plan = build_dynamic_cosphi_plan(ui, wt_config_dict={})
    assert plan["ok"]
    triples = _cmds(plan)
    assert ("AC", "write", "INST:PHAS THREE") in triples
    assert ("AC", "write", "VOLT 230") in triples
    assert ("AC", "write", "VOLT 231") in triples
    assert ("AC", "write", "VOLT 232") in triples


def test_wt_metadata_stoptime_and_filename_via_send_logic(dyn_ui):
    """模拟 Send 写 FileNameList / StopTime（不依赖整机 globals）。"""
    ui, _dialog = dyn_ui
    _fill_step1_single(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _fill_ladder(ui, "20,40", dwell="30", unit="秒")
    ui.checkBox_S_END.setChecked(False)

    plan = build_dynamic_cosphi_plan(
        ui,
        wt_config_dict={"textEdit_FileNameList": "", "textEdit_StopTime": "00:00:10"},
        str_add_flag="0",
        dc_iv_resolver=default_dc_iv_resolver,
    )
    assert plan["ok"]
    assert plan["wt_rounds"] == 1
    # Send 侧：StopTime ≈ Σ驻留 + 15s
    stop_sec = int(round(int(plan["band_duration_01s"]) / 10.0 + 15))
    assert stop_sec >= 60 + 15
    file_name = plan["file_name"]
    assert file_name == "CosPhiP_curve"
    for cfg_row in plan["commands"]:
        if cfg_row and cfg_row[0] == "Upper_WT_Config" and isinstance(cfg_row[4], dict):
            cfg_row[4]["textEdit_FileNameList"] = file_name
            hh, rem = divmod(stop_sec, 3600)
            mm, ss = divmod(rem, 60)
            cfg_row[4]["textEdit_StopTime"] = f"{hh:02d}:{mm:02d}:{ss:02d}"
            assert cfg_row[4]["textEdit_FileNameList"] == "CosPhiP_curve"
            assert cfg_row[4]["textEdit_StopTime"] >= "00:01:15"
            break
    else:
        pytest.fail("missing Upper_WT_Config")


# --------------------------------------------------------------------------- #
# 6. Open/Save 往返
# --------------------------------------------------------------------------- #
def test_settings_csv_roundtrip(dyn_ui, tmp_path):
    ui, _dialog = dyn_ui
    _fill_step1_single(ui, dc1=True)
    _fill_ladder(ui, "25,50,75,100", dwell="8", unit="秒", base_pf="90")
    ui.checkBox_S_END.setChecked(True)

    path = tmp_path / "dynamic_cosphi_settings.csv"
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

    # 清空再读回
    ui.textEdit_PowerLadder.setPlainText("")
    ui.textEdit_S3_TIME_2.setPlainText("1")
    ui.textEdit_S3_DC_PF.setPlainText("100")
    with path.open("r", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    headers, vals = rows[0], rows[1]
    for i, name in enumerate(headers):
        if i == 0 or i >= len(vals):
            continue
        _apply_csv_value(ui, name, vals[i])

    assert ui.textEdit_PowerLadder.toPlainText() == "25,50,75,100"
    assert ui.textEdit_S3_TIME_2.toPlainText() == "8"
    assert ui.textEdit_S3_DC_PF.toPlainText() == "90"


# --------------------------------------------------------------------------- #
# 7. Append 计数（覆盖/追加标志）
# --------------------------------------------------------------------------- #
def test_append_flag_mode_from_count():
    """动态 Cos(φ) 追加走统一判定，不再用计数三元式覆盖跨项队列。"""
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "def thaidynamiccosPhiAppend():" in src
    assert "apply_append_mode(" in src
    assert "project_name='动态Cos(φ)'" in src
    assert "build_dynamic_cosphi_plan" in src
    assert "dynamiccosPhi_append_count" in src

    # AST：确认 Append 存在且调用 Send
    tree = ast.parse(src)
    append_fn = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "thaidynamiccosPhiAppend":
            append_fn = node
            break
    assert append_fn is not None
    calls = [n.func.id for n in ast.walk(append_fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert "thaidynamiccosPhiSend" in calls


# --------------------------------------------------------------------------- #
# 8. 关机联动：未勾 step1 DC 时不写对应 OUTP OFF
# --------------------------------------------------------------------------- #
def test_shutdown_requires_step1_dc(dyn_ui):
    ui, _dialog = dyn_ui
    _fill_step1_single(ui, dc1=False)
    ui.checkBox_S1_DC2.setChecked(False)
    ui.checkBox_S2.setChecked(False)
    ui.checkBox_S3.setChecked(False)
    ui.checkBox_S_END.setChecked(True)
    ui.comboBox_S_END_AC.setCurrentText("关闭")
    ui.checkBox_S_END_DC1.setChecked(True)
    ui.comboBox_S_END_DC1.setCurrentText("关闭")
    ui.checkBox_S_END_DC2.setChecked(True)
    ui.comboBox_S_END_DC2.setCurrentText("关闭")

    plan = build_dynamic_cosphi_plan(ui, wt_config_dict={})
    assert plan["ok"]
    triples = _cmds(plan)
    assert ("AC", "write", "OUTP OFF") in triples
    assert ("DC1", "write", "OUTP OFF") not in triples
    assert ("DC2", "write", "OUTP OFF") not in triples


def test_main_registers_dynamic_cosphi():
    src = MAIN_PATH.read_text(encoding="utf-8")
    assert "'动态Cos(φ)'" in src or '"动态Cos(φ)"' in src
    assert "dialog_windowdynamiccosPhi" in src
    assert "uiThaiDynamicCosPhi" in src
    assert "OpenFileDialogThaiDynamicCosPhi" in src
