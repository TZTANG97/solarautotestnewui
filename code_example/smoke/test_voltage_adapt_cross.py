# -*- coding: utf-8 -*-
"""电压适应性（巴西 5.4.21）软件交叉冒烟：三相 EDIT ALL + 过/欠压扫压 + 连续录。"""
from __future__ import annotations

import os
import sys

import pytest
from PyQt5.QtWidgets import QApplication, QDialog

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _fill_wt_chroma_profile(ui, *, with_uv=True, with_dc=False, with_end=False):
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("3")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.textEdit_S1_TIME.setPlainText("10")
    ui.comboBox_S1_TIME.setCurrentText("秒")

    for ch in range(1, 5):
        getattr(ui, "checkBox_S1_DC%d" % ch).setChecked(False)
    if with_dc:
        ui.checkBox_S1_DC1.setChecked(True)
        ui.comboBox_S1_DC1.setCurrentText("开启")
        ui.textEdit_S1_DC1_VOLT.setPlainText("400")
        ui.textEdit_S1_DC1_CURR.setPlainText("10")
        ui.textEdit_S1_DC1_Voc.setPlainText("500")
        ui.textEdit_S1_DC1_Isc.setPlainText("12")
        ui.textEdit_S1_DC1_PF.setPlainText("100")

    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    ui.checkBox_S2_update_rate.setChecked(True)
    ui.textEdit_S2_update_rate.setPlainText("50")
    ui.comboBox_S2_update_rate.setCurrentText("毫秒")

    for sn in range(3, 21):
        getattr(ui, "checkBox_S%d" % sn).setChecked(False)

    ui.checkBox_guoya_page.setChecked(True)
    ui.checkBox_qianya_page.setChecked(bool(with_uv))
    # list 优先：清空后走卡片，便于单测
    ui.textEdit_VoltageLadder_guoya.setPlainText("")
    ui.textEdit_VoltageLadder_qianya.setPlainText("")

    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S3_RATE.setChecked(True)
    ui.textEdit_S3_volt_start_guoya.setPlainText("230")
    ui.textEdit_S3_volt_end_guoya.setPlainText("253")
    ui.textEdit_S3_test_duration_guoya.setPlainText("2")
    ui.comboBox_S3_test_time_unit_guoya.setCurrentText("秒")

    if with_uv:
        ui.checkBox_S12.setChecked(True)
        ui.checkBox_S12_RATE.setChecked(True)
        ui.textEdit_S12_volt_start_qianya.setPlainText("230")
        ui.textEdit_S12_volt_end_qianya.setPlainText("195")
        ui.textEdit_S12_test_duration_qianya.setPlainText("2")
        ui.comboBox_S12_test_time_unit_qianya.setCurrentText("秒")
        ui.textEdit_VoltageLadder_qianya.setPlainText("230-195@2")

    ui.checkBox_S_End.setChecked(bool(with_end))
    if with_end:
        ui.comboBox_S_End_AC.setCurrentText("关闭")

    # 过压用 list
    ui.textEdit_VoltageLadder_guoya.setPlainText("230-253@2")


def test_cross_three_phase_ov_uv_continuous(qapp):
    from dialogs.Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    from utils.voltage_adaptability_commands import build_voltage_adaptability_plan

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_wt_chroma_profile(ui, with_uv=True, with_dc=False, with_end=False)

    plan = build_voltage_adaptability_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1, "textEdit_FileNameList": "VoltAdapt_BR_5421"},
        chroma_61800=True,
    )
    assert plan["ok"], plan.get("error")
    assert not plan["dc_errors"]
    cmds = plan["commands"]

    writes = [str(r[2]) for r in cmds if r[0] == "AC" and r[1] == "write"]
    assert "INST:PHAS THREE" in writes
    assert "PHAS:THREE SAMEFREQ" in writes
    assert "CONF:COUP AC" in writes

    volts = [str(r[2]) for r in cmds if str(r[2]).startswith("VOLT")]
    assert "VOLT:AC 230" in volts
    assert "VOLT:AC 253" in volts
    assert "VOLT:AC 195" in volts
    assert len(volts) > 10

    # Chroma：扫压不发 EDIT ALL；启机末一次 EDIT ALL + 三相同压再写 VOLT:AC
    edit_all_n = sum(1 for w in writes if w.upper() == "INST:EDIT ALL")
    assert edit_all_n == 1

    markers = [
        str(r[6]).strip().upper()
        for r in cmds
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1
    for m in markers:
        assert m in ("ASYNC_START", "WAIT_END")

    assert plan["wt_continuous"] is True
    assert plan["wt_rounds"] == 1
    assert plan["file_names"] == ["VoltAdapt_BR_5421"]
    assert plan["wt_type"] == "WT3000"
    assert len(plan["band_metas"]) == 2

    # StopTime 必须覆盖扫压墙钟：驻留 + SCPI 开销，不能短于 UI 采集或实际 wait
    ui_01 = int(plan.get("ui_duration_01s") or 0)
    wait_01 = int(plan.get("sweep_wait_01s") or 0)
    band_01 = int(plan.get("band_duration_01s") or 0)
    n_volt = int(plan.get("sweep_volt_steps") or 0)
    n_dwell = int(plan.get("sweep_dwell_steps") or 0)
    assert n_volt > 10
    assert n_dwell >= n_volt
    assert wait_01 >= ui_01  # 50ms 量化成 0.1s 后驻留 ≥ UI 采集
    assert band_01 >= wait_01 + n_dwell * 2
    stop_sec = int(round(band_01 / 10.0 + 15))
    assert stop_sec >= int(round(wait_01 / 10.0)) + 15


def test_default_ui_uses_ov_ladder_only(qapp):
    """新对话框默认：过压 list 一段、欠压页关闭，无需逐个取消勾选。"""
    from dialogs.Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    from utils.voltage_adaptability_commands import build_voltage_adaptability_plan

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    assert ui.checkBox_guoya_page.isChecked()
    assert not ui.checkBox_qianya_page.isChecked()
    assert "230-253" in ui.textEdit_VoltageLadder_guoya.toPlainText()
    assert "253-230" in ui.textEdit_VoltageLadder_guoya.toPlainText()
    assert ui.checkBox_S3.isChecked()
    assert not ui.checkBox_S4.isChecked()
    te = ui._wtStacked.widget(0).findChild(type(ui.textEdit_VoltageLadder_guoya), "textEdit_FileNameList")
    # findChild by object name
    from PyQt5.QtWidgets import QTextEdit
    te = None
    for i in range(ui._wtStacked.count()):
        te = ui._wtStacked.widget(i).findChild(QTextEdit, "textEdit_FileNameList")
        if te is not None:
            break
    assert te is not None
    assert te.toPlainText().strip() == "VoltAdapt_BR_5421"

    plan = build_voltage_adaptability_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1, "textEdit_FileNameList": "100%_ambient"},
    )
    assert plan["ok"], plan.get("error")
    assert len(plan["band_metas"]) == 2
    volts = [str(r[2]) for r in plan["commands"] if str(r[2]).startswith("VOLT")]
    assert "VOLT 253" in volts or "VOLT:AC 253" in volts


def test_stoptime_covers_wall_clock_like_20260822(qapp):
    """回归：UI 采集 15+15=30s、更新率 50ms 时，旧逻辑 StopTime=45s 会早停表。"""
    from dialogs.Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    from utils.voltage_adaptability_commands import (
        build_voltage_adaptability_plan,
        estimate_continuous_record_01s,
    )

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_wt_chroma_profile(ui, with_uv=True, with_dc=False, with_end=False)
    ui.textEdit_VoltageLadder_guoya.setPlainText("230-253@15")
    ui.textEdit_VoltageLadder_qianya.setPlainText("230-195@15")

    plan = build_voltage_adaptability_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1, "textEdit_FileNameList": "VoltAdapt_BR_5421"},
        chroma_61800=True,
    )
    assert plan["ok"], plan.get("error")
    cmds = plan["commands"]
    async_i = next(
        i for i, r in enumerate(cmds)
        if len(r) > 6 and str(r[6]).strip().upper() == "ASYNC_START"
    )
    wait_i = next(
        i for i, r in enumerate(cmds)
        if len(r) > 6 and str(r[6]).strip().upper() == "WAIT_END"
    )
    band = cmds[async_i : wait_i + 1]
    wall_01, wait_01, n_volt, n_dwell = estimate_continuous_record_01s(band)
    assert n_volt >= 500  # 与真机约 602 步同量级
    assert n_dwell >= 500
    assert wait_01 >= 500  # ≥50s 驻留
    # 旧公式：UI30 + 15 = 45s，必然早停
    legacy_stop = int(round(int(plan["ui_duration_01s"]) / 10.0 + 15))
    assert legacy_stop == 45
    new_stop = int(round(int(plan["band_duration_01s"]) / 10.0 + 15))
    assert new_stop > legacy_stop
    assert new_stop >= int(round(wait_01 / 10.0 + 15))
    assert int(plan["band_duration_01s"]) >= wall_01


def test_replay_command_csv_stoptime_mismatch():
    """用 2026-08-22 真机命令表复现：StopTime=45s < 驻留 60.2s。"""
    import csv
    from pathlib import Path
    from utils.voltage_adaptability_commands import estimate_continuous_record_01s

    p = Path(ROOT) / "command_save_files/command_data/voltageadaptability_commands2026_08_22_10.csv"
    if not p.exists():
        pytest.skip("missing command csv")
    rows = list(csv.reader(p.open(encoding="utf-8-sig", newline="")))
    async_i = next(
        i for i, r in enumerate(rows)
        if any(str(c).strip().upper() == "ASYNC_START" for c in r)
    )
    wait_i = next(
        i for i, r in enumerate(rows)
        if any(str(c).strip().upper() == "WAIT_END" for c in r)
    )
    band = rows[async_i : wait_i + 1]
    wall_01, wait_01, n_volt, n_dwell = estimate_continuous_record_01s(band)
    assert n_volt == 602
    assert n_dwell == 602
    assert wait_01 == 602
    assert wall_01 == 602 + 602 * 2
    # 真机配置 StopTime 45s 早于驻留结束
    assert 45 < wait_01 / 10.0


def test_replay_20260822_13_command_csv_stoptime():
    """回归 13:50 真机：StopTime=04:12(252s) 短于扫压墙钟(~310s)。"""
    import csv
    from pathlib import Path
    from utils.voltage_adaptability_commands import (
        estimate_continuous_record_01s,
        recalculate_stoptime_from_band_rows,
    )

    p = Path(ROOT) / "command_save_files/command_data/voltageadaptability_commands2026_08_22_13.csv"
    if not p.exists():
        pytest.skip("missing command csv")
    rows = list(csv.reader(p.open(encoding="utf-8-sig", newline="")))
    async_i = next(
        i for i, r in enumerate(rows)
        if any(str(c).strip().upper() == "ASYNC_START" for c in r)
    )
    wait_i = next(
        i for i, r in enumerate(rows)
        if any(str(c).strip().upper() == "WAIT_END" for c in r)
    )
    band = rows[async_i : wait_i + 1]
    wall_01, wait_01, n_volt, n_dwell = estimate_continuous_record_01s(band)
    stop_str, stop_sec, _, _, _, _ = recalculate_stoptime_from_band_rows(band)
    assert n_volt == 582
    assert n_dwell == 1203
    assert stop_sec >= 310  # 覆盖 ASYNC→WAIT_END 真机墙钟
    assert stop_str != "00:04:12"  # 旧 Send 值过短


def test_cross_with_dc1_chroma_iv(qapp):
    from dialogs.Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    from utils.voltage_adaptability_commands import build_voltage_adaptability_plan

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_wt_chroma_profile(ui, with_uv=False, with_dc=True, with_end=True)

    plan = build_voltage_adaptability_plan(ui, wt_config_dict={"comboBox_AutoSave": 1})
    assert plan["ok"], plan.get("error")
    assert not plan["dc_errors"], plan["dc_errors"]
    cmds = plan["commands"]
    dc_writes = [str(r[2]) for r in cmds if r[0] == "DC1" and r[1] == "write"]
    assert any("IVC" in c or "MODE TABLE" in c for c in dc_writes)
    assert any("OUTP ON" in c for c in dc_writes)
    assert any(
        r[0] == "AC" and "OUTP OFF" in str(r[2])
        for r in cmds
    )


def test_split_ov_uv_two_files_recording(qapp):
    """分文件：过压 WAIT_END 后欠压 ASYNC_START，2 轮 WT。"""
    from dialogs.Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    from utils.voltage_adaptability_commands import build_voltage_adaptability_plan

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_wt_chroma_profile(ui, with_uv=True, with_dc=False, with_end=False)
    ui.checkBox_S2_split_ov_uv_files.setChecked(True)
    ui.textEdit_VoltageLadder_guoya.setPlainText("230-253@2")
    ui.textEdit_VoltageLadder_qianya.setPlainText("230-195@2")

    plan = build_voltage_adaptability_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1},
        chroma_61800=True,
    )
    assert plan["ok"], plan.get("error")
    assert plan["split_two_files"] is True
    assert plan["wt_rounds"] == 2
    assert plan["wt_continuous"] is False
    assert plan["file_names"] == ["VoltAdapt_OV_5421", "VoltAdapt_UV_5421"]

    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert markers.count("ASYNC_START") == 2
    assert markers.count("WAIT_END") == 2
    # OV 段结束先于 UV 段 ASYNC
    async_idxs = [i for i, m in enumerate(markers) if m == "ASYNC_START"]
    wait_idxs = [i for i, m in enumerate(markers) if m == "WAIT_END"]
    assert async_idxs[1] > wait_idxs[0]


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    test_cross_three_phase_ov_uv_continuous(app)
    test_default_ui_uses_ov_ladder_only(app)
    test_stoptime_covers_wall_clock_like_20260822(app)
    test_replay_command_csv_stoptime_mismatch()
    test_replay_20260822_13_command_csv_stoptime()
    test_cross_with_dc1_chroma_iv(app)
    print("VOLT_ADAPT_CROSS_ALL_OK")
