# -*- coding: utf-8 -*-
"""Test_PU：电压 list 连续录 PU_curve（与静态 QU 同结构，测有功）。"""
import logging
import os
import re
import sys

import pytest
from PyQt5.QtWidgets import QApplication, QDialog

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DEFAULT_U = (
    "100,103,105,106,107,108,110,112,115,"
    "112,110,108,107,106,105,103,100,"
    "97,94,93,90,87,85"
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _parse_list(text):
    vals = []
    for tok in re.split(r"[,，\s]+", (text or "").strip()):
        tok = tok.strip().replace("%", "")
        if not tok:
            continue
        vals.append(float(tok))
    return vals


def test_dialog_voltage_list_defaults(qapp):
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU

    ui = Ui_Dialog_thaitestPU()
    dialog = QDialog()
    ui.setupUi(dialog)

    assert hasattr(ui, "textEdit_VoltageLadder")
    u_list = _parse_list(ui.textEdit_VoltageLadder.toPlainText())
    assert len(u_list) == 23
    assert u_list[0] == 100 and u_list[8] == 115 and u_list[-1] == 85
    assert max(u_list) == 115 and min(u_list) == 85
    assert ui.textEdit_VoltageLadder_Un.toPlainText() == "230"
    assert ui.textEdit_VoltageLadder_TIME.toPlainText() == "1"
    assert ui.comboBox_VoltageLadder_TIME.currentText() == "分钟"
    assert ui.textEdit_PowerLadder.toPlainText() == "100,70,50,20"
    # 旧 20 点卡片仍在（list 为空时备用）
    assert hasattr(ui, "checkBox_S3") and hasattr(ui, "checkBox_S22")


def _prep_send(ui, sw, monkeypatch, tmp_path, u_text):
    ui.textEdit_VoltageLadder.setText(u_text)
    ui.textEdit_VoltageLadder_Un.setText("230")
    ui.textEdit_VoltageLadder_FR.setText("50")
    ui.textEdit_VoltageLadder_TIME.setText("1")
    ui.comboBox_VoltageLadder_TIME.setCurrentText("秒")

    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC_2.setCurrentText("单相")
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.textEdit_S1_AC_VOLT.setText("230")
    ui.textEdit_S1_AC_VOLT_2.setText("230")
    ui.textEdit_S1_AC_VOLT_3.setText("230")
    ui.textEdit_S1_AC_FR.setText("50")
    ui.textEdit_S1_TIME.setText("1")
    ui.comboBox_S1_TIME.setCurrentText("秒")
    ui.textEdit_S1_ACWaitTIME.setText("1")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.checkBox_S1_DC1.setChecked(True)
    ui.checkBox_S1_DC2.setChecked(False)
    ui.checkBox_S1_DC3.setChecked(False)
    ui.checkBox_S1_DC4.setChecked(False)
    ui.comboBox_S1_DC1.setCurrentText("开启")
    ui.textEdit_S1_DC1_VOLT.setText("400")
    ui.textEdit_S1_DC1_CURR.setText("10")
    ui.textEdit_S1_DC1_Voc.setText("500")
    ui.textEdit_S1_DC1_Isc.setText("12")
    ui.textEdit_S1_DC1_PF.setText("100")

    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT5000.setChecked(True)
    for n in range(3, 23):
        getattr(ui, f"checkBox_S{n}").setChecked(False)
    ui.checkBox_S_End.setChecked(False)
    # 旧用例只扫电压：功率名单留空则保持步骤①
    if hasattr(ui, "textEdit_PowerLadder"):
        ui.textEdit_PowerLadder.setPlainText("")

    monkeypatch.setattr(sw, "DCGetIVValueFunction", lambda *a, **k: ["IVC:IT 1", "IVC:VT 1"], raising=False)
    monkeypatch.setattr(sw, "command_list_DC", {"chroma": ["OUTP:MODE TABLE", "IVCurve:SELect 1"]}, raising=False)
    monkeypatch.setattr(sw, "DC_num", {"DC1": "0", "DC2": "1", "DC3": "2", "DC4": "3"}, raising=False)
    monkeypatch.setattr(sw, "per_dc_factor", {"0": "chroma", "1": "chroma", "2": "chroma", "3": "chroma"}, raising=False)
    monkeypatch.setattr(sw, "QMessageBox", type("QM", (), {
        "information": staticmethod(lambda *a, **k: None),
        "warning": staticmethod(lambda *a, **k: None),
        "Ok": 1,
    })(), raising=False)
    monkeypatch.setattr(sw, "reset_wt_automation_state", lambda: None, raising=False)
    monkeypatch.setattr(sw, "command_save_file_path", str(tmp_path), raising=False)
    monkeypatch.setattr(sw, "_sync_start_end_buttons", lambda: None, raising=False)
    monkeypatch.setattr(sw, "_PageWidgetFinder", lambda page: page, raising=False)
    monkeypatch.setattr(sw, "WT5000_params_config", lambda ui: {
        "Style": "Thai_WT5000_Config",
        "comboBox_AutoSave": 1,
        "textEdit_FileNameList": "",
        "textEdit_StopTime": "00:01:00",
        "textEdit_SavePath": str(tmp_path),
        "checkBox_AutoName": "0",
    }, raising=False)

    logs = []
    fake_logger = logging.getLogger("test_testpu")
    sw.thaitestPUSend.__globals__["logger"] = fake_logger
    sw.ui = type("UI", (), {
        "textEdit_ReturnMessage": type("TE", (), {
            "append": staticmethod(lambda *a, **k: logs.append(a[0] if a else ""))
        })(),
        "comboBox_PS": type("C", (), {"currentText": staticmethod(lambda: "Test_PU")})(),
    })()
    sw.uiThaiTestPU = ui
    sw.dialog_windowtestPU = type("LD", (), {"close": lambda self: None})()
    sw.strAddTestFlag = "0"
    sw.strArrayTest = []
    sw.strArrayTestStep = []
    sw.total_save_file = 0
    sw.test_program = []
    sw.project_change = "0"
    sw.wt_config_nums = 0
    sw.WT_is_checked = ""
    sw.testPU_append_count = 0
    sw.strSettingTestFlag = "0"
    (tmp_path / "command_data").mkdir(parents=True, exist_ok=True)
    return logs


def test_send_short_voltage_list(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU

    ui = Ui_Dialog_thaitestPU()
    dialog = QDialog()
    ui.setupUi(dialog)
    logs = _prep_send(ui, sw, monkeypatch, tmp_path, "100,103,105")
    sw.thaitestPUSend()

    volts = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and r[1] == "write" and str(r[2]).startswith("VOLT ")]
    assert any(v.startswith("VOLT 230") for v in volts)
    assert any(v.startswith("VOLT 236.9") for v in volts)
    assert any(v.startswith("VOLT 241.5") for v in volts)
    assert sw.total_save_file == 1
    wt_cfg = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]
    assert wt_cfg.get("textEdit_FileNameList") == "PU_curve"
    assert wt_cfg.get("textEdit_StopTime")
    col6 = [r[6] for r in sw.strArrayTest if r and r[0] == "AC" and r[6] != ""]
    assert col6.count("ASYNC_START") == 1
    assert col6.count("WAIT_END") == 1
    assert any("连续录 1 条" in m and "PU_curve" in m for m in logs)


def test_send_default_rise_fall_points(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU

    ui = Ui_Dialog_thaitestPU()
    dialog = QDialog()
    ui.setupUi(dialog)
    logs = _prep_send(ui, sw, monkeypatch, tmp_path, DEFAULT_U)
    ui.textEdit_VoltageLadder_TIME.setText("1")
    ui.comboBox_VoltageLadder_TIME.setCurrentText("分钟")
    sw.thaitestPUSend()
    assert sw.total_save_file == 1
    assert any("连续录 1 条" in m and "23 点" in m for m in logs)
    names = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]["textEdit_FileNameList"]
    assert names == "PU_curve"
    waits = [r for r in sw.strArrayTest if r and r[0] == "AC" and r[1] == "wait" and r[9] != ""]
    assert len(waits) >= 23
    stop = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]["textEdit_StopTime"]
    assert stop == "00:23:05"


def test_send_three_phase_scales_all_phases(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU

    ui = Ui_Dialog_thaitestPU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "100,110")
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setText("230")
    ui.textEdit_S1_AC_VOLT_2.setText("230")
    ui.textEdit_S1_AC_VOLT_3.setText("230")
    ui.textEdit_VoltageLadder_Un.setText("230")
    sw.thaitestPUSend()

    nsel = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and str(r[2]).startswith("INST:NSEL")]
    assert nsel.count("INST:NSEL 1") >= 2
    assert nsel.count("INST:NSEL 2") >= 2
    assert nsel.count("INST:NSEL 3") >= 2
    volts = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and str(r[2]).startswith("VOLT ")]
    assert volts.count("VOLT 230.0") + volts.count("VOLT 230") >= 3
    assert any(v.startswith("VOLT 253") for v in volts)
    assert sw.total_save_file == 1


def test_send_legacy_cards_when_list_empty(qapp, monkeypatch, tmp_path):
    """电压 list 为空时回退旧逐点卡片，且不再注入 ASYNC_START。"""
    import SCPITestWave as sw
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU

    ui = Ui_Dialog_thaitestPU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "")
    ui.checkBox_S3.setChecked(True)
    ui.textEdit_S3_AC_VOLT.setText("240")
    ui.textEdit_S3_TIME.setText("2")
    ui.comboBox_S3_TIME.setCurrentText("秒")
    sw.thaitestPUSend()

    col6 = [r[6] for r in sw.strArrayTest if r and r[0] == "AC" and r[6] != ""]
    assert "ASYNC_START" not in col6
    assert "WAIT_END" not in col6
    volts = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and str(r[2]).startswith("VOLT ")]
    assert any("240" in v for v in volts)
    assert sw.total_save_file == 1


def test_send_wt_smoke_list_three_points(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU

    ui = Ui_Dialog_thaitestPU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "100,107,93")
    ui.textEdit_VoltageLadder_TIME.setText("5")
    sw.thaitestPUSend()
    assert sw.total_save_file == 1
    wt_cfg = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]
    assert wt_cfg["textEdit_FileNameList"] == "PU_curve"
    assert wt_cfg["textEdit_StopTime"] == "00:00:20"
    volts = [r[2] for r in sw.strArrayTest if r and str(r[2]).startswith("VOLT ")]
    assert any("230" in v for v in volts)
    assert any("246.1" in v for v in volts)
    assert any("213.9" in v for v in volts)


def test_voltage_math_matrix():
    un = 230.0
    cases = [(100, 230.0), (103, 236.9), (107, 246.1), (115, 264.5), (93, 213.9), (85, 195.5)]
    for pct, expect in cases:
        assert round(un * pct / 100.0, 2) == expect


def test_send_each_power_then_voltage_still_one_recording(qapp, monkeypatch, tmp_path):
    """每个功率档先改已勾选直流，再扫电压；全程只录一条。"""
    import SCPITestWave as sw
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU

    ui = Ui_Dialog_thaitestPU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "100,110")
    ui.textEdit_PowerLadder.setPlainText("100,50")

    def _iv(vmp, imp, voc, isc, pf, dc_num):
        scale = float(str(pf).strip().rstrip("%") or "0") / 100.0
        return ["IVC:IT %.3f" % (float(imp) * scale)]

    monkeypatch.setattr(sw, "DCGetIVValueFunction", _iv, raising=False)
    sw.thaitestPUSend()

    cmds = [r[2] for r in sw.strArrayTest if r]
    assert "IVC:IT 5.000" in cmds
    assert cmds.count("VOLT 230.0") == 2
    assert cmds.count("VOLT 253.0") == 2
    col6 = [r[6] for r in sw.strArrayTest if r and r[0] == "AC" and r[6] != ""]
    assert col6.count("ASYNC_START") == 1
    assert col6.count("WAIT_END") == 1
    assert sw.total_save_file == 1
    # 先改 50% 直流，再出现该档的第二遍电压
    idx_half = cmds.index("IVC:IT 5.000")
    assert cmds.index("VOLT 253.0", idx_half) > idx_half


def test_empty_power_ladder_does_not_rewrite_dc(qapp):
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU
    from utils.dynamic_qu_commands import default_dc_iv_resolver
    from utils.test_pu_commands import build_pu_voltage_power_rows

    ui = Ui_Dialog_thaitestPU()
    dialog = QDialog()
    ui.setupUi(dialog)
    ui.textEdit_VoltageLadder.setPlainText("100,110")
    ui.textEdit_PowerLadder.setPlainText("")
    ui.textEdit_VoltageLadder_TIME.setPlainText("1")
    ui.comboBox_VoltageLadder_TIME.setCurrentText("秒")
    ui.checkBox_S1_DC1.setChecked(True)
    plan = build_pu_voltage_power_rows(
        ui, phase_mode="单相", dc_iv_resolver=default_dc_iv_resolver
    )
    assert plan["ok"] and plan["power_levels"] == []
    assert not any(r[0] == "DC1" for r in plan["rows"])
    assert [r[6] for r in plan["rows"]].count("ASYNC_START") == 1
    assert [r[6] for r in plan["rows"]].count("WAIT_END") == 1
