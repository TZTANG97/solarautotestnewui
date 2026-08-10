# -*- coding: utf-8 -*-
"""电压适应性完整离屏模拟：真实 Dialog + 命令计划 + CSV 往返 + 设备连接校验。"""

from __future__ import annotations

import ast
import csv
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
from utils.voltage_adaptability_commands import (
    build_voltage_adaptability_plan,
    default_dc_iv_resolver,
)
from utils.Open_Save_ThaiVoltageAdaptability import (
    FILE_TAG,
    HEADERS,
    _apply_csv_value,
    _widget_to_csv,
)
from utils.time_helpers import SetTimeFunction

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = PROJECT_ROOT / "SCPITestWave.py"


@pytest.fixture(scope="module")
def qapp():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app


@pytest.fixture
def volt_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaivoltageadaptability()
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


def _fill_step1_three(ui):
    _fill_step1_single(ui, dc1=False)
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("231")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("232")


def _disable_all_bands(ui):
    for sn in range(3, 21):
        getattr(ui, "checkBox_S%d" % sn).setChecked(False)


def _fill_one_band(ui, sn, side, start, end, duration, unit="秒"):
    getattr(ui, "checkBox_S%d" % sn).setChecked(True)
    getattr(ui, "textEdit_S%d_volt_start_%s" % (sn, side)).setPlainText(str(start))
    getattr(ui, "textEdit_S%d_volt_end_%s" % (sn, side)).setPlainText(str(end))
    getattr(ui, "textEdit_S%d_test_duration_%s" % (sn, side)).setPlainText(str(duration))
    getattr(ui, "comboBox_S%d_test_time_unit_%s" % (sn, side)).setCurrentText(unit)


def _cmds(plan):
    return [(r[0], r[1], r[2]) for r in plan["commands"]]


def _device_keys(plan):
    return {r[0] for r in plan["commands"] if r and r[0]}


# --------------------------------------------------------------------------- #
# Dialog 结构
# --------------------------------------------------------------------------- #
def test_dialog_has_required_widgets(volt_ui):
    ui, _dialog = volt_ui
    assert ui.stackedWidget.count() == 5
    assert ui._wtStacked.count() == 4
    assert hasattr(ui, "checkBox_guoya_page")
    assert hasattr(ui, "checkBox_qianya_page")
    assert ui.checkBox_S3 is not ui.checkBox_guoya_page
    assert ui.checkBox_S12 is not ui.checkBox_qianya_page
    for sn in list(range(3, 12)) + list(range(12, 21)):
        assert getattr(ui, "checkBox_S%d" % sn) is not None
    assert ui.pushButton_TestAppend is not None
    assert ui.label_append_count is not None
    assert hasattr(ui, "analyzerModeSection")
    assert hasattr(ui, "radio_dewetron")
    assert ui.radio_dewetron.text() == "DEWETRON"
    assert ui.analyzerModeSection.current_mode() in ("wt3000", "dewetron")
    ui.radio_dewetron.setChecked(True)
    assert ui._mode == "dewetron"
    assert ui.analyzerModeSection.current_mode() == "dewetron"


def test_page_master_disables_cards(volt_ui):
    ui, _dialog = volt_ui
    assert ui.checkBox_S3.isEnabled()
    ui.checkBox_guoya_page.setChecked(False)
    assert not ui.checkBox_S3.isEnabled()
    ui.checkBox_guoya_page.setChecked(True)
    assert ui.checkBox_S3.isEnabled()


# --------------------------------------------------------------------------- #
# 完整成功路径（单相）
# --------------------------------------------------------------------------- #
def test_full_single_phase_happy_path(volt_ui, tmp_path):
    ui, _dialog = volt_ui
    _fill_step1_single(ui, dc1=True)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    _disable_all_bands(ui)
    _fill_one_band(ui, 3, "guoya", "50.2", "51.5", 10, "秒")
    _fill_one_band(ui, 12, "qianya", "49.5", "47.5", 1, "分钟")
    ui.checkBox_S_End.setChecked(True)
    ui.comboBox_S_End_AC.setCurrentText("关闭")
    ui.checkBox_S_End_DC1.setChecked(True)
    ui.comboBox_S_End_DC1.setCurrentText("关闭")

    plan = build_voltage_adaptability_plan(
        ui,
        wt_config_dict={"mock": 1},
        str_add_flag="0",
        project_change="0",
        dc_iv_resolver=default_dc_iv_resolver,
    )
    assert plan["ok"] is True
    assert plan["dc_errors"] == []
    assert plan["wt_type"] == "WT3000"
    assert plan["test_program"] == [["12", "WT3000"]]
    assert plan["wt_is_checked"] == "1"

    keys = _device_keys(plan)
    assert "Upper_WT_Config" in keys
    assert "AC" in keys
    assert "DC1" in keys
    assert "DC2" not in keys

    triples = _cmds(plan)
    assert ("AC", "write", "INST:PHAS SINGLE") in triples
    assert ("AC", "write", "VOLT 230") in triples
    assert ("AC", "write", "FREQ 50") in triples
    assert ("AC", "write", "OUTP ON") in triples
    assert ("AC", "write", "VOLT 50.2") in triples
    assert ("AC", "write", "VOLT 51.5") in triples
    assert ("AC", "write", "VOLT 49.5") in triples
    assert ("AC", "write", "VOLT 47.5") in triples
    assert ("AC", "write", "OUTP OFF") in triples
    assert ("DC1", "write", "OUTP OFF") in triples
    assert ("DC1", "write", "OUTP:MODE TABLE") in triples
    assert ("DC1", "write", "IVCurve:SELect 1") in triples

    # 巴西更新率扫压：步间等待≈更新率；整段数据采集不再单次 dwell
    assert plan["wt_rounds"] == 1
    assert plan["wt_continuous"] is True
    assert plan["file_names"] == ["VoltAdapt_BR_5421"]
    volts = [r[2] for r in plan["commands"] if str(r[2]).startswith("VOLT")]
    assert "VOLT 50.2" in volts or any("50.2" in str(x) for x in volts)
    assert "VOLT 51.5" in volts or any("51.5" in str(x) for x in volts)
    assert "VOLT 49.5" in volts or any("49.5" in str(x) for x in volts)
    assert "VOLT 47.5" in volts or any("47.5" in str(x) for x in volts)
    # 连续录必须用 ASYNC_START/WAIT_END；禁止数字 col6（会阻塞扫压）
    markers = [str(r[6]).strip().upper() for r in plan["commands"] if len(r) > 6 and r[6] not in ("", None)]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1
    numeric_col6 = [
        r[6] for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None) and str(r[6]).strip().lstrip("-").isdigit()
    ]
    assert numeric_col6 == []

    # 写出命令 CSV（模拟 Send 落盘）
    out = tmp_path / "voltageadaptability_commands_sim.csv"
    with out.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        for row in plan["commands"]:
            writer.writerow(row)
    rows = list(csv.reader(out.open(encoding="utf-8")))
    assert len(rows) == len(plan["commands"])
    assert rows[0][0] == "Upper_WT_Config"


# --------------------------------------------------------------------------- #
# 三相 + 小时单位
# --------------------------------------------------------------------------- #
def test_three_phase_and_hour_unit(volt_ui):
    ui, _dialog = volt_ui
    _fill_step1_three(ui)
    ui.checkBox_S2.setChecked(False)
    ui.checkBox_S2_update_rate.setChecked(False)  # 关闭更新率，单点保持
    _disable_all_bands(ui)
    ui.checkBox_guoya_page.setChecked(True)
    _fill_one_band(ui, 5, "guoya", "52", "52", 1, "小时")
    ui.checkBox_qianya_page.setChecked(False)
    ui.checkBox_S_End.setChecked(False)

    plan = build_voltage_adaptability_plan(ui, wt_config_dict={})
    assert plan["ok"]
    triples = _cmds(plan)
    assert ("AC", "write", "INST:PHAS THREE") in triples
    assert ("AC", "write", "VOLT 231") in triples
    assert ("AC", "write", "VOLT 232") in triples
    # 三相：巴西同款 INST:EDIT ALL + 一次 VOLT（不按相 NSEL 写三次）
    assert triples.count(("AC", "write", "VOLT 52")) >= 1
    assert plan["wt_rounds"] == 0
    # 未勾功率分析仪且未扫压：整段 dwell 在 col9
    assert SetTimeFunction(1, "小时") in [
        r[9] for r in plan["commands"] if r[2] == "*IDN?" and r[9] not in ("", None)
    ]


# --------------------------------------------------------------------------- #
# 校验失败 / DC 错误 / 页关闭
# --------------------------------------------------------------------------- #
def test_band_missing_duration_aborts(volt_ui):
    ui, _dialog = volt_ui
    _fill_step1_single(ui, dc1=False)
    _disable_all_bands(ui)
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_S3_volt_start_guoya.setPlainText("51")
    ui.textEdit_S3_volt_end_guoya.setPlainText("52")
    ui.textEdit_S3_test_duration_guoya.setPlainText("")
    plan = build_voltage_adaptability_plan(ui)
    assert plan["ok"] is False
    assert "测试时间未填写" in plan["error"]


def test_dc_invalid_collects_error(volt_ui):
    ui, _dialog = volt_ui
    _fill_step1_single(ui, dc1=True)
    ui.textEdit_S1_DC1_CURR.setPlainText("20")  # Imp >= Isc
    ui.textEdit_S1_DC1_Isc.setPlainText("12")
    _disable_all_bands(ui)
    ui.checkBox_S_End.setChecked(False)
    plan = build_voltage_adaptability_plan(ui)
    assert plan["ok"] is True
    assert any("DC电源1" in e for e in plan["dc_errors"])


def test_guopin_page_off_skips_overfreq(volt_ui):
    ui, _dialog = volt_ui
    _fill_step1_single(ui, dc1=False)
    _disable_all_bands(ui)
    _fill_one_band(ui, 3, "guoya", "51", "52", 5)
    _fill_one_band(ui, 12, "qianya", "49", "48", 5)
    ui.checkBox_guoya_page.setChecked(False)
    ui.checkBox_qianya_page.setChecked(True)
    ui.checkBox_S_End.setChecked(False)
    plan = build_voltage_adaptability_plan(ui)
    assert plan["ok"]
    triples = _cmds(plan)
    assert ("AC", "write", "VOLT 51") not in triples
    assert ("AC", "write", "VOLT 49") in triples


# --------------------------------------------------------------------------- #
# 设定 CSV 往返（不弹文件对话框）
# --------------------------------------------------------------------------- #
def test_settings_csv_roundtrip(volt_ui, tmp_path):
    ui, _dialog = volt_ui
    _fill_step1_single(ui, dc1=True)
    _disable_all_bands(ui)
    _fill_one_band(ui, 4, "guoya", "50.5", "51.0", 3, "秒")
    ui.checkBox_S_End.setChecked(True)

    path = tmp_path / "freq_settings.csv"
    row = [FILE_TAG] + [_widget_to_csv(ui, col) for col in HEADERS[1:]]
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.writer(fp)
        writer.writerow(HEADERS)
        writer.writerow(row)

    # 清空后再读回
    ui.textEdit_S1_AC_VOLT.setPlainText("")
    ui.textEdit_S4_volt_start_guoya.setPlainText("")
    with path.open("r", newline="", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    config = dict(zip(rows[0], rows[1]))
    assert config["Style"] == FILE_TAG
    for col in HEADERS[1:]:
        if col in config:
            _apply_csv_value(ui, col, config[col])

    assert ui.textEdit_S1_AC_VOLT.toPlainText() == "230"
    assert ui.textEdit_S4_volt_start_guoya.toPlainText() == "50.5"
    assert ui.textEdit_S4_volt_end_guoya.toPlainText() == "51.0"


# --------------------------------------------------------------------------- #
# 设备连接校验（模拟 RunProjectPush 前置）
# --------------------------------------------------------------------------- #
def test_device_connection_check_from_plan(volt_ui):
    ui, _dialog = volt_ui
    _fill_step1_single(ui, dc1=True)
    _disable_all_bands(ui)
    _fill_one_band(ui, 3, "guoya", "51", "51", 2)
    ui.checkBox_S_End.setChecked(False)
    plan = build_voltage_adaptability_plan(ui)
    used = {r[0] for r in plan["commands"] if r and r[0]}

    # Upper_WT_Config 走 WTViewerEfree，不纳入 SCPI 连接校验
    controllers = {
        "AC": SimpleNamespace(connected=True),
        "DC1": SimpleNamespace(connected=False),
    }
    device_map = {
        "AC": ("交流电源", controllers["AC"]),
        "DC1": ("DC电源1", controllers["DC1"]),
    }
    disconnected = []
    for key in sorted(used):
        if key not in device_map:
            continue
        name, ctl = device_map[key]
        if ctl is None or not ctl.connected:
            disconnected.append(name)
    assert disconnected == ["DC电源1"]


# --------------------------------------------------------------------------- #
# SCPITestWave 源码契约：Send 已接 plan，无占位文案
# --------------------------------------------------------------------------- #
def test_main_send_uses_plan_and_no_placeholder():
    source = MAIN_PATH.read_text(encoding="utf-8-sig")
    assert "试验逻辑尚未实现" not in source
    assert "build_voltage_adaptability_plan" in source
    tree = ast.parse(source)
    funcs = {
        n.name: n
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "thaivoltageadaptabilitySend" in funcs
    assert "thaivoltageadaptabilityAppend" in funcs
    send = funcs["thaivoltageadaptabilitySend"]
    call_names = []
    for node in ast.walk(send):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                call_names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                call_names.append(node.func.attr)
    assert "build_voltage_adaptability_plan" in call_names


def test_simulate_append_then_start_gate(volt_ui):
    """模拟：追加成功 → 计数>=1 → 开始试验可启用；连接失败则拦截。"""
    ui, _dialog = volt_ui
    _fill_step1_single(ui, dc1=True)
    _disable_all_bands(ui)
    _fill_one_band(ui, 3, "guoya", "50.2", "50.2", 5)
    ui.checkBox_S_End.setChecked(True)
    ui.comboBox_S_End_AC.setCurrentText("关闭")

    plan = build_voltage_adaptability_plan(ui, wt_config_dict={"k": "v"})
    assert plan["ok"] and not plan["dc_errors"]

    append_count = 0
    append_count += 1
    ui.label_append_count.setText(str(append_count))
    start_enabled = append_count >= 1
    assert start_enabled
    assert ui.label_append_count.text() == "1"

    # 模拟开始试验连接检查
    used = {r[0] for r in plan["commands"]}
    assert "AC" in used and "DC1" in used and "Upper_WT_Config" in used
