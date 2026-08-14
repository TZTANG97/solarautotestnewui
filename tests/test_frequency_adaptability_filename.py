# -*- coding: utf-8 -*-
"""频率适应性：巴西 5.4.20 连续录 + 更新率扫频。"""
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
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT5000.setChecked(True)
    ui.checkBox_S2_update_rate.setChecked(True)
    ui.textEdit_S2_update_rate.setPlainText("50")
    ui.comboBox_S2_update_rate.setCurrentText("毫秒")
    ui.checkBox_guopin_page.setChecked(True)
    ui.checkBox_qianpin_page.setChecked(False)
    for sn in range(3, 21):
        cb = getattr(ui, "checkBox_S%d" % sn, None)
        if cb is not None:
            cb.setChecked(False)
    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S3_RATE.setChecked(True)
    ui.textEdit_S3_freq_start_guopin.setPlainText("50")
    ui.textEdit_S3_freq_end_guopin.setPlainText("52")
    ui.textEdit_S3_test_duration_guopin.setPlainText("1")
    ui.comboBox_S3_test_time_unit_guopin.setCurrentText("秒")
    ui.checkBox_S_End.setChecked(False)


def test_plan_brazil_rate_sweep_continuous(qapp):
    from Dialog_thaifrequencyadaptability import Ui_Dialog_thaifrequencyadaptability
    from utils.frequency_adaptability_commands import build_frequency_adaptability_plan

    ui = Ui_Dialog_thaifrequencyadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _enable_brazil_band(ui)

    plan = build_frequency_adaptability_plan(ui, wt_config_dict={"comboBox_AutoSave": 1})
    assert plan["ok"]
    assert plan["wt_continuous"] is True
    assert plan["wt_rounds"] == 1
    assert plan["file_names"] == ["FreqAdapt_BR_5420"]
    freqs = [r[2] for r in plan["commands"] if str(r[2]).startswith("FREQ")]
    assert "FREQ 50" in freqs
    assert "FREQ 52" in freqs
    assert len(freqs) > 2  # 扫频多步
    col6 = [r[6] for r in plan["commands"] if r[2] == "*IDN?" and r[6] not in ("", None)]
    assert col6 == ["ASYNC_START", "WAIT_END"]  # 首步启动 + 扫频结束后等停表


def test_send_keeps_custom_single_filename(qapp, monkeypatch):
    import SCPITestWave as sw
    from Dialog_thaifrequencyadaptability import Ui_Dialog_thaifrequencyadaptability

    ui = Ui_Dialog_thaifrequencyadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _enable_brazil_band(ui)

    for page_idx in range(ui._wtStacked.count()):
        page = ui._wtStacked.widget(page_idx)
        te = page.findChild(QTextEdit, "textEdit_FileNameList")
        if te is not None:
            te.setPlainText("freq_br_248")

    sw.uiThaiFrequencyAdaptability = ui
    sw.dialog_windowfrequencyadaptability = dialog
    sw.strAddTestFlag = "0"
    sw.strArrayTest = []
    sw.strArrayTestStep = []
    sw.test_program = []
    sw.total_save_file = 0
    sw.WT_is_checked = "0"
    sw.project_change = "0"
    sw.wt_config_nums = 0
    sw.strSettingTestFlag = "0"
    if "frequencyadaptability_append_count" not in sw.__dict__:
        sw.frequencyadaptability_append_count = 0

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
    sw.per_dc_factor = {"0": "Chroma", "1": "Chroma", "2": "Chroma", "3": "Chroma"}
    sw.command_list_DC = {"Chroma": ["OUTP:MODE TABLE", "IVCurve:SELect 1"]}
    sw.command_save_file_path = os.path.join(ROOT, "command_save_files")
    os.makedirs(os.path.join(ROOT, "command_save_files", "command_data"), exist_ok=True)

    class _Msg:
        def append(self, *_a, **_k):
            pass

    sw.ui = type("U", (), {"textEdit_ReturnMessage": _Msg()})()
    sw.thaifrequencyadaptabilitySend()

    wt_rows = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"]
    assert wt_rows
    assert wt_rows[0][4]["textEdit_FileNameList"] == "freq_br_248"
    assert sw.total_save_file == 1
