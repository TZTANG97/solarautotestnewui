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
    # 同行功率默认开测 100%
    powers = [p for p in ui.textEdit_PowerLadder.toPlainText().split(",") if p.strip()]
    assert len(powers) == 23
    assert all(p.strip() == "100" for p in powers)
    assert ui.textEdit_VoltageLadder_TIME is not None
    assert hasattr(ui, "_vp_ladder")


def test_continuous_async_no_numeric_col6(dyn_ui):
    ui, _ = dyn_ui
    _fill_step1(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _fill_ladder(ui, "100,103,105", dwell="10", unit="秒")
    # 功率≠步骤① PF，才会在阶梯段灌 IV（=100% 时会跳过首点重复）
    ui.textEdit_PowerLadder.setPlainText("80")
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


def test_power_voltage_paired_not_outer_product(dyn_ui):
    """电压100%→功率100%，电压110%→功率50%：两点，不是 2×2 外循环。"""
    ui, _ = dyn_ui
    _fill_step1(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _fill_ladder(ui, "100,110", dwell="1", unit="秒")
    ui.textEdit_PowerLadder.setPlainText("100,50")
    ui.checkBox_S_END.setChecked(False)

    plan = build_dynamic_qu_plan(
        ui, wt_config_dict={}, str_add_flag="0", dc_iv_resolver=default_dc_iv_resolver
    )
    assert plan["ok"]
    assert plan["power_levels"] == [100.0, 50.0]
    assert plan["band_duration_01s"] == 10 * 2  # 两点驻留，不是 2×2
    triples = [(r[0], r[1], r[2]) for r in plan["commands"]]
    volts = [t[2] for t in triples if str(t[2]).startswith("VOLT ")]
    # 启机 + 配对第1点都可能写 230；第2点 110%→253，且不得再 NSEL 扩成 3 遍
    assert any(v in ("VOLT 230", "VOLT 230.0") for v in volts)
    assert sum(1 for v in volts if v.startswith("VOLT 253")) == 1
    assert not any(str(t[2]).startswith("INST:NSEL") for t in triples)
    ivc = [t[2] for t in triples if str(t[2]).startswith("IVC:IT")]
    assert len(ivc) >= 2
    assert any("5.000" in cmd or "5.0" in cmd for cmd in ivc)
    markers = [str(r[6]).upper() for r in plan["commands"] if len(r) > 6 and r[6] not in ("", None)]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1


def test_power_shorter_than_voltage_pads_default(dyn_ui):
    """同行表写入短功率 list 时，缺行补开测默认 100%，不再整单拒绝。"""
    ui, _ = dyn_ui
    _fill_step1(ui, dc1=True)
    ui.checkBox_S2.setChecked(False)
    _fill_ladder(ui, "100,110,120", dwell="1", unit="秒")
    ui.textEdit_PowerLadder.setPlainText("100,50")
    ui.checkBox_S_END.setChecked(False)
    assert ui.textEdit_PowerLadder.toPlainText() == "100,50,100"
    plan = build_dynamic_qu_plan(ui, wt_config_dict={})
    assert plan["ok"]
    assert plan["power_levels"] == [100.0, 50.0, 100.0]


def test_power_ladder_updates_all_checked_dc_channels(dyn_ui):
    """电压旁功率变化时，步骤①勾选的 DC1+DC2 都要按同一 Pn% 重下 IV。"""
    ui, _ = dyn_ui
    _fill_step1(ui, dc1=True)
    ui.checkBox_S1_DC2.setChecked(True)
    ui.comboBox_S1_DC2.setCurrentText("开启")
    ui.textEdit_S1_DC2_VOLT.setPlainText("380")
    ui.textEdit_S1_DC2_CURR.setPlainText("8")
    ui.textEdit_S1_DC2_Voc.setPlainText("420")
    ui.textEdit_S1_DC2_Isc.setPlainText("10")
    ui.textEdit_S1_DC2_PF.setPlainText("100")
    ui.checkBox_S2.setChecked(False)
    _fill_ladder(ui, "100,110", dwell="1", unit="秒")
    ui.textEdit_PowerLadder.setPlainText("100,50")
    ui.checkBox_S_END.setChecked(False)

    plan = build_dynamic_qu_plan(
        ui, wt_config_dict={}, str_add_flag="0", dc_iv_resolver=default_dc_iv_resolver
    )
    assert plan["ok"], plan.get("error") or plan.get("dc_errors")
    triples = [(r[0], r[1], r[2]) for r in plan["commands"]]
    dc1_ivc = [t for t in triples if t[0] == "DC1" and str(t[2]).startswith("IVC:IT")]
    dc2_ivc = [t for t in triples if t[0] == "DC2" and str(t[2]).startswith("IVC:IT")]
    assert len(dc1_ivc) >= 2
    assert len(dc2_ivc) >= 2
    # 50%：DC1 Imp 10→5；DC2 Imp 8→4
    assert any("5.000" in str(t[2]) or "5.0," in str(t[2]) for t in dc1_ivc)
    assert any("4.000" in str(t[2]) or "4.0," in str(t[2]) for t in dc2_ivc)
    # 未勾选的 DC3/DC4 不应出现写命令
    assert not any(t[0] in ("DC3", "DC4") and t[1] == "write" for t in triples)


def test_step1_pf_matches_helper(dyn_ui):
    from utils.dynamic_qu_commands import step1_dc_pf_matches

    ui, _ = dyn_ui
    _fill_step1(ui, dc1=True)
    assert step1_dc_pf_matches(ui, 100)
    ui.textEdit_S1_DC1_PF.setPlainText("80")
    assert not step1_dc_pf_matches(ui, 100)
    assert step1_dc_pf_matches(ui, 80)


def test_first_point_skips_dc_when_pf_matches(dyn_ui):
    """首点功率=步骤① PF 时不重复灌 IV（与静态 QU 对齐）。"""
    ui, _ = dyn_ui
    _fill_step1(ui, dc1=True)
    ui.textEdit_S1_DC1_PF.setPlainText("100")
    ui.checkBox_S2.setChecked(False)
    _fill_ladder(ui, "100,110", dwell="1", unit="秒")
    ui.textEdit_PowerLadder.setPlainText("100")
    ui.checkBox_S_END.setChecked(False)
    plan = build_dynamic_qu_plan(
        ui, wt_config_dict={}, str_add_flag="0", dc_iv_resolver=default_dc_iv_resolver
    )
    assert plan["ok"], plan.get("error") or plan.get("dc_errors")
    triples = [(r[0], r[1], r[2]) for r in plan["commands"]]
    # Step1 启机仍会写一次 MODE TABLE；阶梯全程 100% 不应再灌第二遍
    mode_table = [t for t in triples if t[0] == "DC1" and t[2] == "OUTP:MODE TABLE"]
    assert len(mode_table) == 1


def test_build_plan_pads_short_power_bypass_ui(dyn_ui):
    """handoff 短功率串（不经表格 pad）时，build_dynamic_qu_plan 仍按电压长度补 100%。"""
    ui, _ = dyn_ui
    _fill_step1(ui, dc1=True)
    ui.checkBox_S2.setChecked(False)
    _fill_ladder(ui, "100,105,110", dwell="1", unit="秒")
    ui.checkBox_S_END.setChecked(False)
    ui.textEdit_PowerLadder.toPlainText = lambda: "100,70"  # type: ignore[method-assign]
    plan = build_dynamic_qu_plan(
        ui, wt_config_dict={}, str_add_flag="0", dc_iv_resolver=default_dc_iv_resolver
    )
    assert plan["ok"], plan.get("error") or plan.get("dc_errors")
    assert plan["power_levels"] == [100.0, 70.0]
    assert len(plan["u_pct_list"]) == 3


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
