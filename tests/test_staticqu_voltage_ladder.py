# -*- coding: utf-8 -*-
"""静态 QU：只填电压 list（同 WT），无功由 WT 实测。"""
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
    "97,94,93,90,87,85,87,90,93,94,97"
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


def test_dialog_voltage_list_only(qapp):
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)

    assert hasattr(ui, "textEdit_VoltageLadder")
    assert not hasattr(ui, "textEdit_TargetLadder")
    assert not hasattr(ui, "textEdit_VoltageLadder_Qmax")
    u_list = _parse_list(ui.textEdit_VoltageLadder.toPlainText())
    assert len(u_list) == 28
    assert u_list[0] == 100 and u_list[4] == 107 and u_list[8] == 115
    assert ui.textEdit_VoltageLadder_Un.toPlainText() == "230"


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
    ui.checkBox_S3.setChecked(False)
    ui.checkBox_S4.setChecked(False)
    ui.checkBox_S5.setChecked(False)
    ui.checkBox_S6.setChecked(False)
    ui.checkBox_S_End.setChecked(False)

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
    fake_logger = logging.getLogger("test_staticqu")
    sw.thaistaticQUSend.__globals__["logger"] = fake_logger
    sw.ui = type("UI", (), {
        "textEdit_ReturnMessage": type("TE", (), {
            "append": staticmethod(lambda *a, **k: logs.append(a[0] if a else ""))
        })(),
        "comboBox_PS": type("C", (), {"currentText": staticmethod(lambda: "静态QU")})(),
    })()
    sw.uiThaiStaticQU = ui
    sw.dialog_windowstaticQU = type("LD", (), {"close": lambda self: None})()
    sw.strAddTestFlag = "0"
    sw.strArrayTest = []
    sw.strArrayTestStep = []
    sw.total_save_file = 0
    sw.test_program = []
    sw.project_change = "0"
    sw.wt_config_nums = 0
    sw.WT_is_checked = ""
    sw.staticQU_append_count = 0
    sw.strSettingTestFlag = "0"
    (tmp_path / "command_data").mkdir(parents=True, exist_ok=True)
    return logs


def test_send_short_voltage_list(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "100,103,105")
    sw.thaistaticQUSend()

    volts = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and r[1] == "write" and str(r[2]).startswith("VOLT ")]
    assert any(v.startswith("VOLT 230") for v in volts)
    assert any(v.startswith("VOLT 236.9") for v in volts)
    assert any(v.startswith("VOLT 241.5") for v in volts)
    assert sw.total_save_file == 3
    wt_rows = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"]
    assert wt_rows[0][4].get("textEdit_FileNameList") == "U100,U103,U105"


def test_send_default_28_points(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    logs = _prep_send(ui, sw, monkeypatch, tmp_path, DEFAULT_U)
    sw.thaistaticQUSend()
    assert sw.total_save_file == 28
    assert any("电压 list 28" in m for m in logs)
    names = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]["textEdit_FileNameList"].split(",")
    assert names[4] == "U107" and names[19] == "U93"
