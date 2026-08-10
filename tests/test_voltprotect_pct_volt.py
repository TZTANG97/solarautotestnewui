# -*- coding: utf-8 -*-
"""10min过压保护：交流电压支持绝对值与 Un 百分比。"""
import os
import sys

import pytest
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.ac_volt_helpers import format_volt_for_scpi, resolve_ac_volt_input


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_resolve_absolute_and_percent():
    assert resolve_ac_volt_input("257.6", 230) == 257.6
    assert resolve_ac_volt_input("230V", 230) == 230.0
    assert resolve_ac_volt_input("112%", 230) == 257.6
    assert resolve_ac_volt_input("108％", 230) == 248.4
    assert resolve_ac_volt_input("100%", 230) == 230.0
    assert resolve_ac_volt_input("106%", 230) == 243.8
    assert resolve_ac_volt_input("114%", 230) == 262.2
    assert format_volt_for_scpi(257.6) == "257.6"
    assert format_volt_for_scpi(230.0) == "230"


def test_resolve_rejects_bad_input():
    with pytest.raises(ValueError):
        resolve_ac_volt_input("", 230)
    with pytest.raises(ValueError):
        resolve_ac_volt_input("abc%", 230)
    with pytest.raises(ValueError):
        resolve_ac_volt_input("112%", 0)


def test_dialog_labels_show_percent_hint(qapp):
    from Dialog_thaivoltprotect10min import Ui_Dialog_thaivoltprotect10min

    ui = Ui_Dialog_thaivoltprotect10min()
    dialog = QDialog()
    ui.setupUi(dialog)
    assert ui.label_21.text() == "V/%"
    assert ui.label_27.text() == "V/%"
    assert hasattr(ui, "textEdit_S3_AC_VOLT")
    assert hasattr(ui, "textEdit_S4_AC_VOLT")


def _prep_voltprotect_send(ui, sw, monkeypatch, tmp_path):
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
    ui.textEdit_S1_DC1_VOLT.setText("360")
    ui.textEdit_S1_DC1_CURR.setText("12")
    ui.textEdit_S1_DC1_Voc.setText("400")
    ui.textEdit_S1_DC1_Isc.setText("14")
    ui.textEdit_S1_DC1_PF.setText("100")
    ui.comboBox_S1_DC1.setCurrentText("开启")

    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)

    ui.checkBox_S3.setChecked(True)
    ui.textEdit_S3_TIME.setText("10")
    ui.comboBox_S3_TIME.setCurrentText("秒")

    ui.checkBox_S4.setChecked(True)
    ui.textEdit_S4_TIME.setText("3")
    ui.comboBox_S4_TIME.setCurrentText("秒")
    ui.textEdit_S4_AC_VOLT.setText("100%")
    ui.textEdit_S4_AC_VOLT_2.setText("100%")
    ui.textEdit_S4_AC_VOLT_3.setText("100%")

    ui.checkBox_S_End.setChecked(True)
    ui.comboBox_S_End_AC.setCurrentText("关闭")
    ui.comboBox_S_End_DC1.setCurrentText("关闭")

    sw.strAddTestFlag = "0"
    sw.strArrayTest = []
    sw.strArrayTestStep = []
    sw.total_save_file = 0
    sw.test_program = []
    sw.wt_config_nums = 0
    sw.project_change = "0"
    sw.WT_is_checked = ""
    sw.command_save_file_path = str(tmp_path)
    sw.voltprotect10min_append_count = 0
    sw.ArrayfDCCurrValue = [30.0, 30.0, 30.0, 30.0]
    os.makedirs(tmp_path / "command_data", exist_ok=True)

    monkeypatch.setattr(sw, "DCGetIVValueFunction", lambda *a, **k: ["IVC:IT 1", "IVC:VT 1"], raising=False)
    monkeypatch.setattr(sw, "command_list_DC", {"chroma": ["OUTP:MODE TABLE", "IVCurve:SELect 1"]}, raising=False)
    monkeypatch.setattr(sw, "DC_num", {"DC1": "0", "DC2": "1", "DC3": "2", "DC4": "3"}, raising=False)
    monkeypatch.setattr(sw, "per_dc_factor", {"0": "chroma", "1": "chroma", "2": "chroma", "3": "chroma"}, raising=False)
    monkeypatch.setattr(sw, "WT3000E_params_config", lambda ui: {
        "Style": "Thai_WT3000E_Config",
        "comboBox_AutoSave": 1,
        "textEdit_FileNameList": "",
        "textEdit_StopTime": "00:01:00",
        "textEdit_SavePath": str(tmp_path),
        "checkBox_AutoName": "0",
    }, raising=False)
    monkeypatch.setattr(sw, "_PageWidgetFinder", lambda page: page, raising=False)

    class _FakeTE:
        def __init__(self):
            self.lines = []

        def append(self, x):
            self.lines.append(str(x))

    class _FakeUI:
        textEdit_ReturnMessage = _FakeTE()

        def __getattr__(self, name):
            if name == "comboBox_PS":
                class C:
                    def currentText(self):
                        return "10min过压保护"
                return C()
            if name.startswith("pushButton_"):
                class B:
                    def setEnabled(self, *_a, **_k):
                        pass
                return B()
            raise AttributeError(name)

    sw.ui = _FakeUI()
    sw.uiThaiVoltProtect10min = ui
    sw.dialog_windowvoltprotect10min = type("D", (), {"close": lambda self: None})()
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: QMessageBox.Ok))
    monkeypatch.setattr(sw, "reset_wt_automation_state", lambda: None, raising=False)
    monkeypatch.setattr(sw, "_sync_start_end_buttons", lambda: None, raising=False)
    monkeypatch.setattr(sw, "_append_debug_log", lambda *_a, **_k: None, raising=False)
    monkeypatch.setattr(sw, "now_to_datenow", lambda: "2026-08-07", raising=False)
    sw.logger = type("L", (), {"info": lambda *a, **k: None, "error": lambda *a, **k: None, "warning": lambda *a, **k: None})()
    # 注入 Send 闭包可见的 logger
    sw.thaivoltprotect10minSend.__globals__["logger"] = sw.logger
    sw.DC_IV_Commands_Set.__globals__["logger"] = sw.logger
    sw.DC_IV_Commands_Set.__globals__["DC_num"] = sw.DC_num
    sw.DC_IV_Commands_Set.__globals__["command_list_DC"] = sw.command_list_DC
    sw.DC_IV_Commands_Set.__globals__["per_dc_factor"] = sw.per_dc_factor


def test_send_percent_112_becomes_257_6(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaivoltprotect10min import Ui_Dialog_thaivoltprotect10min

    ui = Ui_Dialog_thaivoltprotect10min()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_voltprotect_send(ui, sw, monkeypatch, tmp_path)
    ui.textEdit_S3_AC_VOLT.setText("112%")
    ui.label_append_count = type("L", (), {"setText": lambda self, *_a, **_k: None})()

    sw.thaivoltprotect10minSend()

    # ASYNC_START 应在过压 VOLT 之前（含①额定保持）
    idxs = []
    for i, r in enumerate(sw.strArrayTest):
        if not r:
            continue
        if len(r) > 6 and r[6] == "ASYNC_START":
            idxs.append(("start", i))
        if r[0] == "AC" and str(r[2]).startswith("VOLT 257.6"):
            idxs.append(("ov", i))
        if len(r) > 6 and r[6] == "WAIT_END":
            idxs.append(("end", i))
    kinds = {k: i for k, i in idxs}
    assert "start" in kinds and "ov" in kinds and "end" in kinds
    assert kinds["start"] < kinds["ov"] < kinds["end"]
    volt_cmds = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and str(r[2]).startswith("VOLT ")]
    assert "VOLT 257.6" in volt_cmds
    assert "VOLT 230" in volt_cmds  # 恢复 100%
    # StopTime 含①1s + ③10s + ④3s +5 ≈ 00:00:19
    wt_cfg = next(r[4] for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config")
    h, m, s = [int(x) for x in wt_cfg["textEdit_StopTime"].split(":")]
    assert h * 3600 + m * 60 + s >= 19


def test_send_absolute_still_works(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaivoltprotect10min import Ui_Dialog_thaivoltprotect10min

    ui = Ui_Dialog_thaivoltprotect10min()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_voltprotect_send(ui, sw, monkeypatch, tmp_path)
    ui.textEdit_S3_AC_VOLT.setText("253")
    ui.textEdit_S4_AC_VOLT.setText("230")
    ui.label_append_count = type("L", (), {"setText": lambda self, *_a, **_k: None})()

    sw.thaivoltprotect10minSend()
    volt_cmds = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and str(r[2]).startswith("VOLT ")]
    assert "VOLT 253" in volt_cmds
    assert "VOLT 230" in volt_cmds
