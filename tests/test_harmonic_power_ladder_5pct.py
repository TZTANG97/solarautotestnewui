# -*- coding: utf-8 -*-
"""谐波电流：功率点 5/20/40/60/80/100% 必须各自下发 DC IV（含 5%）。"""
from __future__ import annotations

import io
import logging
import os
import sys

import pytest
from PyQt5.QtWidgets import QApplication, QDialog

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 卡片顺序与 Send / collect_harmonic_power_percents 一致
_HARM_STEPS = [
    ("checkBox_S3", "textEdit_S1_DC1_PF_2", "checkBox_S1_DC1_2"),
    ("checkBox_S3_2", "textEdit_S1_DC1_PF_3", "checkBox_S1_DC1_3"),
    ("checkBox_S3_3", "textEdit_S1_DC1_PF_4", "checkBox_S1_DC1_4"),
    ("checkBox_S3_4", "textEdit_S1_DC1_PF_5", "checkBox_S1_DC1_5"),
    ("checkBox_S3_5", "textEdit_S1_DC1_PF_6", "checkBox_S1_DC1_6"),
    ("checkBox_S3_10", "textEdit_S1_DC1_PF_10", "checkBox_S1_DC1_10"),
    ("checkBox_S3_6", "textEdit_S1_DC1_PF_9", "checkBox_S1_DC1_11"),
    ("checkBox_S3_7", "textEdit_S1_DC1_PF_7", "checkBox_S1_DC1_7"),
    ("checkBox_S3_9", "textEdit_S1_DC1_PF_11", "checkBox_S1_DC1_9"),
    ("checkBox_S3_8", "textEdit_S1_DC1_PF_8", "checkBox_S1_DC1_8"),
    ("checkBox_S3_11", "textEdit_S1_DC1_PF_12", "checkBox_S1_DC1_12"),
]


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _fake_iv(vmp, imp, voc, isc, pf, dc_num):
    """把功率百分比编码进命令，便于断言是否下发。"""
    return [f"IVC:PF {pf}", f"IVC:IT {imp}"]


def _setup_send(sw, ui, monkeypatch, *, iv_fn=_fake_iv):
    monkeypatch.setattr(sw, "DCGetIVValueFunction", iv_fn)
    sw.command_list_DC = {"chroma": ["OUTP:MODE TABLE", "IVCurve:SELect 1"]}
    sw.DC_num = {"DC1": "0", "DC2": "1", "DC3": "2", "DC4": "3"}
    sw.per_dc_factor = {"0": "chroma", "1": "chroma", "2": "chroma", "3": "chroma"}
    monkeypatch.setattr(
        sw,
        "QMessageBox",
        type(
            "QM",
            (),
            {
                "information": staticmethod(lambda *a, **k: None),
                "warning": staticmethod(lambda *a, **k: None),
                "Ok": 1,
            },
        ),
    )
    monkeypatch.setattr(sw, "reset_wt_automation_state", lambda: None)
    monkeypatch.setattr(sw, "_sync_start_end_buttons", lambda: None)
    monkeypatch.setattr(sw, "now_to_datenow", lambda: "t")
    monkeypatch.setattr(sw, "append_ac_startup_from_ui", lambda *a, **k: None)
    fake_logger = logging.getLogger("test_harmonic_5pct")
    fake_logger.info = lambda *a, **k: None
    fake_logger.warning = lambda *a, **k: None
    fake_logger.error = lambda *a, **k: None
    sw.thaixiebodianliuSend.__globals__["logger"] = fake_logger
    monkeypatch.setattr("builtins.open", lambda *a, **k: io.StringIO())
    monkeypatch.setattr(
        "utils.command_csv_io.write_command_csv",
        lambda *a, **k: None,
        raising=False,
    )

    class FakeUI:
        textEdit_ReturnMessage = type("T", (), {"append": staticmethod(lambda *a, **k: None)})()

    sw.ui = FakeUI()
    sw.uiThaiXieBoDianLiu = ui
    sw.dialog_windowxiebodianliu = type("LD", (), {"close": lambda self: None})()
    sw.strAddTestFlag = "0"
    sw.strArrayTest = []
    sw.strArrayTestStep = []
    sw.total_save_file = 0
    sw.test_program = []
    sw.wt_config_nums = 0
    sw.project_change = "0"
    sw.harmonic_append_count = 0
    sw.WT_is_checked = ""
    sw.wt_type = ""
    sw.command_save_file_path = os.path.join(ROOT, "command_save_files")
    ui.label_append_count = type("L", (), {"setText": lambda self, v: None})()

    monkeypatch.setattr(
        sw,
        "WT3000E_params_config",
        lambda finder: {
            "Style": "Thai_WT3000E_Config",
            "comboBox_AutoSave": 0,
            "textEdit_StopTime": "00:00:01",
            "textEdit_SavePath": r"D:\EnergyTest\wt_file_save_path",
            "textEdit_FileNameList": "old",
        },
    )
    monkeypatch.setattr(sw, "_PageWidgetFinder", lambda w: w)


def _fill_power_ladder(ui, percents):
    """只启用前 N 张卡并写入功率点；其余取消勾选。"""
    for cb, pf_te, dc_cb in _HARM_STEPS:
        getattr(ui, cb).setChecked(False)
    for i, pct in enumerate(percents):
        cb, pf_te, dc_cb = _HARM_STEPS[i]
        getattr(ui, cb).setChecked(True)
        getattr(ui, pf_te).setPlainText(str(pct))
        # 联动后 DC 应已勾选；再保险一次
        getattr(ui, dc_cb).setChecked(True)


def test_harmonic_send_includes_5pct_dc_iv(qapp, monkeypatch):
    import SCPITestWave as sw
    from dialogs.Dialog_thaixiebodianliu import Ui_Dialog_thaixiebodianliu

    ui = Ui_Dialog_thaixiebodianliu()
    dialog = QDialog()
    ui.setupUi(dialog)

    ladder = [5, 20, 40, 60, 80, 100]
    _fill_power_ladder(ui, ladder)

    # 启机功率 100%，与首点 5% 不同 → 首点必须重新下发 IV
    ui.checkBox_S1.setChecked(True)
    for ch in range(2, 5):
        getattr(ui, f"checkBox_S1_DC{ch}").setChecked(False)
    ui.checkBox_S1_DC1.setChecked(True)
    ui.comboBox_S1_DC1.setCurrentText("开启")
    ui.textEdit_S1_DC1_VOLT.setPlainText("400")
    ui.textEdit_S1_DC1_CURR.setPlainText("10")
    ui.textEdit_S1_DC1_Voc.setPlainText("450")
    ui.textEdit_S1_DC1_Isc.setPlainText("12")
    ui.textEdit_S1_DC1_PF.setPlainText("100")

    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    ui.textEdit_S3_TIME_2.setPlainText("1")
    ui.comboBox_S3_TIME_2.setCurrentText("秒")
    ui.textEdit_S3_TIME_3.setPlainText("1")
    ui.comboBox_S3_TIME_3.setCurrentText("秒")
    ui.checkBox_S5.setChecked(False)

    calls = []

    def tracking_iv(vmp, imp, voc, isc, pf, dc_num):
        calls.append(str(pf).strip())
        return _fake_iv(vmp, imp, voc, isc, pf, dc_num)

    _setup_send(sw, ui, monkeypatch, iv_fn=tracking_iv)
    sw.thaixiebodianliuSend()

    # step1@100 + 6 个功率点（含 5%）都应调用 IV
    assert "5" in calls, f"5% 未被 DCGetIVValueFunction 调用: {calls}"
    for p in ladder:
        assert str(p) in calls, f"{p}% 未调用 IV: {calls}"

    dc_writes = [
        str(r[2])
        for r in sw.strArrayTest
        if r and str(r[0]).startswith("DC") and r[1] == "write"
    ]
    joined = " | ".join(dc_writes)
    assert "IVC:PF 5" in joined, f"命令列表无 5% IV:\n{joined}"
    for p in ladder:
        assert f"IVC:PF {p}" in joined, f"缺少 {p}% IV:\n{joined}"


def test_first_card_same_as_step1_still_sends_iv(qapp, monkeypatch):
    """首卡功率与启机相同也必须再下发一次 IV（避免首点看起来没发）。"""
    import SCPITestWave as sw
    from dialogs.Dialog_thaixiebodianliu import Ui_Dialog_thaixiebodianliu

    ui = Ui_Dialog_thaixiebodianliu()
    dialog = QDialog()
    ui.setupUi(dialog)

    _fill_power_ladder(ui, [100, 5])  # 首卡 100=启机，次卡 5

    ui.checkBox_S1.setChecked(True)
    for ch in range(2, 5):
        getattr(ui, f"checkBox_S1_DC{ch}").setChecked(False)
    ui.checkBox_S1_DC1.setChecked(True)
    ui.comboBox_S1_DC1.setCurrentText("开启")
    ui.textEdit_S1_DC1_VOLT.setPlainText("400")
    ui.textEdit_S1_DC1_CURR.setPlainText("10")
    ui.textEdit_S1_DC1_Voc.setPlainText("450")
    ui.textEdit_S1_DC1_Isc.setPlainText("12")
    ui.textEdit_S1_DC1_PF.setPlainText("100")

    ui.checkBox_S2.setChecked(True)
    ui.radioButton_S2_WT3000.setChecked(True)
    ui.textEdit_S3_TIME_2.setPlainText("1")
    ui.comboBox_S3_TIME_2.setCurrentText("秒")
    ui.textEdit_S3_TIME_3.setPlainText("1")
    ui.comboBox_S3_TIME_3.setCurrentText("秒")
    ui.checkBox_S5.setChecked(False)

    calls = []

    def tracking_iv(vmp, imp, voc, isc, pf, dc_num):
        calls.append(str(pf).strip())
        return _fake_iv(vmp, imp, voc, isc, pf, dc_num)

    _setup_send(sw, ui, monkeypatch, iv_fn=tracking_iv)
    sw.thaixiebodianliuSend()

    # 启机 100 + 首卡 100 + 次卡 5
    assert calls.count("100") == 2, f"首卡同功率也须再下发 IV: {calls}"
    assert "5" in calls, f"5% 仍须下发: {calls}"


def test_real_chroma_iv_accepts_5pct(qapp):
    """真实 Chroma 公式：Imp<Isc 时 5% 不得返回错误码。"""
    import SCPITestWave as sw

    sw.per_dc_factor = {"0": "Chroma"}
    sw.ArrayfDCCurrValue = [100.0, 100.0, 100.0, 100.0]
    code = sw.DCGetIVValueFunction("400", "10", "450", "12", "5", 0)
    assert isinstance(code, list), f"5% 应生成 IV 列表，实际={code!r}"
    assert any("IVC" in str(c) or "IT" in str(c) or "," in str(c) for c in code)
