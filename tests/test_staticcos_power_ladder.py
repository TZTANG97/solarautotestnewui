# -*- coding: utf-8 -*-
"""静态 Cos 功率阶梯：Dialog 字段 + Send 矩阵命令生成。"""
import os
import sys

import io
import logging

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


def test_dialog_has_power_ladder_and_visible_dwell(qapp):
    from Dialog_thaistaticcosPhi import Ui_Dialog_thaistaticcosPhi

    ui = Ui_Dialog_thaistaticcosPhi()
    dialog = QDialog()
    ui.setupUi(dialog)

    assert hasattr(ui, "textEdit_PowerLadder")
    assert "100" in ui.textEdit_PowerLadder.toPlainText()
    assert ui.textEdit_S3_TIME_2.toPlainText() == "5"
    assert ui.comboBox_S3_TIME_2.count() >= 1


def test_staticcos_send_builds_power_times_cos_matrix(qapp, monkeypatch):
    import SCPITestWave as sw
    from Dialog_thaistaticcosPhi import Ui_Dialog_thaistaticcosPhi

    ui = Ui_Dialog_thaistaticcosPhi()
    dialog = QDialog()
    ui.setupUi(dialog)

    # 短驻留 + 2 档功率 + 仅勾选 2 个 cosφ → 4 轮
    ui.textEdit_PowerLadder.setText("100,80")
    ui.textEdit_S3_TIME_2.setText("1")
    ui.comboBox_S3_TIME_2.setCurrentText("秒")
    for name in [
        "checkBox_S3", "checkBox_S4", "checkBox_S5", "checkBox_S6", "checkBox_S7",
        "checkBox_S8", "checkBox_S9", "checkBox_S10", "checkBox_S11",
    ]:
        getattr(ui, name).setChecked(False)
    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S7.setChecked(True)
    ui.checkBox_S_END.setChecked(False)

    ui.checkBox_S1.setChecked(True)
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

    # stub DC IV + 避免弹窗/写盘副作用
    monkeypatch.setattr(sw, "DCGetIVValueFunction", lambda *a, **k: ["IVC:IT 1", "IVC:VT 1"])
    monkeypatch.setattr(sw, "command_list_DC", {"chroma": ["OUTP:MODE TABLE", "IVCurve:SELect 1"]})
    monkeypatch.setattr(sw, "DC_num", {"DC1": "0", "DC2": "1", "DC3": "2", "DC4": "3"})
    monkeypatch.setattr(sw, "per_dc_factor", {"0": "chroma", "1": "chroma", "2": "chroma", "3": "chroma"})
    monkeypatch.setattr(sw, "QMessageBox", type("QM", (), {
        "information": staticmethod(lambda *a, **k: None),
        "Ok": 1,
    }))
    monkeypatch.setattr(sw, "reset_wt_automation_state", lambda: None)
    monkeypatch.setattr(sw, "_sync_start_end_buttons", lambda: None)
    monkeypatch.setattr(sw, "now_to_datenow", lambda: "t")
    fake_logger = logging.getLogger("test_staticcos")
    fake_logger.info = lambda *a, **k: None
    fake_logger.warning = lambda *a, **k: None
    fake_logger.error = lambda *a, **k: None
    sw.thaistaticcosPhiSend.__globals__["logger"] = fake_logger
    monkeypatch.setattr("builtins.open", lambda *a, **k: io.StringIO())

    class FakeUI:
        textEdit_ReturnMessage = type("T", (), {"append": staticmethod(lambda *a, **k: None)})()
        comboBox_PS = type("C", (), {"currentText": staticmethod(lambda: "静态Cos(φ)")})()

    sw.ui = FakeUI()
    sw.uiThaiStaticCosPhi = ui
    sw.dialog_windowstaticcosPhi = type("LD", (), {"close": lambda self: None})()
    sw.strAddTestFlag = "0"
    sw.strArrayTest = []
    sw.strArrayTestStep = []
    sw.total_save_file = 0
    sw.test_program = []
    sw.wt_config_nums = 0
    sw.project_change = "0"
    sw.staticcosPhi_append_count = 0
    sw.WT_is_checked = ""
    sw.wt_type = ""
    sw.command_save_file_path = os.path.join(ROOT, "command_save_files")
    ui.label_append_count = type("L", (), {"setText": lambda self, v: None})()

    # 跳过真实 WT params：注入最小 dict
    monkeypatch.setattr(
        sw,
        "WT5000_params_config",
        lambda finder: {
            "Style": "Thai_WT5000_Config",
            "comboBox_AutoSave": 0,
            "textEdit_StopTime": "00:00:01",
            "textEdit_SavePath": r"D:\EnergyTest\wt_file_save_path",
            "textEdit_FileNameList": "old",
        },
    )
    monkeypatch.setattr(sw, "_PageWidgetFinder", lambda w: w)

    sw.thaistaticcosPhiSend()

    assert sw.total_save_file == 4, sw.total_save_file
    col6_rows = [r for r in sw.strArrayTest if len(r) > 6 and r[6] not in ("", None)]
    assert len(col6_rows) == 4, len(col6_rows)

    wt_row = next(r for r in sw.strArrayTest if r[0] == "Upper_WT_Config")
    names = wt_row[4]["textEdit_FileNameList"].split(",")
    assert names == ["P100_cos0.0", "P100_cos1.0", "P80_cos0.0", "P80_cos1.0"], names
    assert wt_row[4]["comboBox_AutoSave"] == 1
