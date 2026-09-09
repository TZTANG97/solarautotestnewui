# -*- coding: utf-8 -*-
"""电压适应性：巴西 5.4.21 连续录 + 更新率扫压。"""
import os
import sys

import pytest
from PyQt5.QtWidgets import QApplication, QDialog, QTextEdit

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _enable_brazil_band(ui):
    ui.checkBox_S1.setChecked(True)
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    for ch in range(1, 5):
        getattr(ui, "checkBox_S1_DC%d" % ch).setChecked(False)
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT5000.setChecked(True)
    ui.checkBox_S2_update_rate.setChecked(True)
    ui.textEdit_S2_update_rate.setPlainText("50")
    ui.comboBox_S2_update_rate.setCurrentText("毫秒")
    ui.checkBox_guoya_page.setChecked(True)
    ui.checkBox_qianya_page.setChecked(False)
    ui.textEdit_VoltageLadder_guoya.setPlainText("230-253@1")
    ui.textEdit_VoltageLadder_qianya.setPlainText("")
    for sn in range(3, 21):
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is not None:
            cb.setChecked(False)
    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S3_RATE.setChecked(True)
    ui.textEdit_S3_volt_start_guoya.setPlainText("230")
    ui.textEdit_S3_volt_end_guoya.setPlainText("253")
    ui.textEdit_S3_test_duration_guoya.setPlainText("1")
    ui.comboBox_S3_test_time_unit_guoya.setCurrentText("秒")
    ui.checkBox_S_End.setChecked(False)


def test_plan_brazil_rate_sweep_continuous(qapp):
    from Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    from utils.voltage_adaptability_commands import build_voltage_adaptability_plan

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _enable_brazil_band(ui)

    plan = build_voltage_adaptability_plan(ui, wt_config_dict={"comboBox_AutoSave": 1})
    assert plan["ok"]
    assert plan["wt_continuous"] is True
    assert plan["wt_rounds"] == 1
    assert plan["file_names"] == ["VoltAdapt_BR_5421"]
    volts = [r[2] for r in plan["commands"] if str(r[2]).startswith("VOLT")]
    assert "VOLT 230" in volts
    assert "VOLT 253" in volts
    assert len(volts) > 2  # 扫压多步（含启机 VOLT）
    markers = [
        str(r[6]).strip().upper()
        for r in plan["commands"]
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1


def test_send_replaces_stale_filename(qapp, monkeypatch):
    import SCPITestWave as sw
    from Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _enable_brazil_band(ui)

    for page_idx in range(ui._wtStacked.count()):
        page = ui._wtStacked.widget(page_idx)
        te = page.findChild(QTextEdit, "textEdit_FileNameList")
        if te is not None:
            te.setPlainText("freq_br_248")

    sw.uiThaiVoltageAdaptability = ui
    sw.dialog_windowvoltageadaptability = dialog
    sw.strAddTestFlag = "0"
    sw.strArrayTest = []
    sw.strArrayTestStep = []
    sw.test_program = []
    sw.total_save_file = 0
    sw.WT_is_checked = "0"
    sw.project_change = "0"
    sw.wt_config_nums = 0
    sw.strSettingTestFlag = "0"
    if "voltageadaptability_append_count" not in sw.__dict__:
        sw.voltageadaptability_append_count = 0

    monkeypatch.setattr(sw, "QMessageBox", type("QM", (), {
        "information": staticmethod(lambda *a, **k: None),
        "Ok": 1,
    }))
    monkeypatch.setattr(sw, "reset_wt_automation_state", lambda: None)
    monkeypatch.setattr(sw, "_sync_start_end_buttons", lambda: None)
    monkeypatch.setattr(sw, "logger", type("L", (), {"info": staticmethod(lambda *a, **k: None)})(), raising=False)
    monkeypatch.setattr(
        sw,
        "DCGetIVValueFunction",
        lambda *a, **k: ("", "", "", "", "", "", "", "", "", "", "", "", "", "", ""),
    )
    sw.command_save_file_path = os.path.join(ROOT, "command_save_files")
    os.makedirs(os.path.join(ROOT, "command_save_files", "command_data"), exist_ok=True)

    class _Msg:
        def append(self, *_a, **_k):
            pass

    sw.ui = type("U", (), {"textEdit_ReturnMessage": _Msg()})()
    sw.thaivoltageadaptabilitySend()

    wt_rows = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"]
    assert wt_rows
    assert wt_rows[0][4]["textEdit_FileNameList"] == "VoltAdapt_BR_5421"
    assert sw.total_save_file == 1


def test_send_keeps_voltadapt_custom_filename(qapp, monkeypatch):
    import SCPITestWave as sw
    from Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _enable_brazil_band(ui)

    for page_idx in range(ui._wtStacked.count()):
        page = ui._wtStacked.widget(page_idx)
        te = page.findChild(QTextEdit, "textEdit_FileNameList")
        if te is not None:
            te.setPlainText("VoltAdapt_MyLab")

    sw.uiThaiVoltageAdaptability = ui
    sw.dialog_windowvoltageadaptability = dialog
    sw.strAddTestFlag = "0"
    sw.strArrayTest = []
    sw.strArrayTestStep = []
    sw.test_program = []
    sw.total_save_file = 0
    sw.WT_is_checked = "0"
    sw.project_change = "0"
    sw.wt_config_nums = 0
    sw.strSettingTestFlag = "0"
    if "voltageadaptability_append_count" not in sw.__dict__:
        sw.voltageadaptability_append_count = 0

    monkeypatch.setattr(sw, "QMessageBox", type("QM", (), {
        "information": staticmethod(lambda *a, **k: None),
        "Ok": 1,
    }))
    monkeypatch.setattr(sw, "reset_wt_automation_state", lambda: None)
    monkeypatch.setattr(sw, "_sync_start_end_buttons", lambda: None)
    monkeypatch.setattr(sw, "logger", type("L", (), {"info": staticmethod(lambda *a, **k: None)})(), raising=False)
    monkeypatch.setattr(
        sw,
        "DCGetIVValueFunction",
        lambda *a, **k: ("", "", "", "", "", "", "", "", "", "", "", "", "", "", ""),
    )
    sw.command_save_file_path = os.path.join(ROOT, "command_save_files")
    os.makedirs(os.path.join(ROOT, "command_save_files", "command_data"), exist_ok=True)

    class _Msg:
        def append(self, *_a, **_k):
            pass

    sw.ui = type("U", (), {"textEdit_ReturnMessage": _Msg()})()
    sw.thaivoltageadaptabilitySend()

    wt_rows = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"]
    assert wt_rows
    assert wt_rows[0][4]["textEdit_FileNameList"] == "VoltAdapt_MyLab"
    assert sw.total_save_file == 1
