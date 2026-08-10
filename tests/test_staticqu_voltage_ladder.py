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


def test_dialog_voltage_list_only(qapp):
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)

    assert hasattr(ui, "textEdit_VoltageLadder")
    assert not hasattr(ui, "textEdit_TargetLadder")
    assert not hasattr(ui, "textEdit_VoltageLadder_Qmax")
    u_list = _parse_list(ui.textEdit_VoltageLadder.toPlainText())
    assert len(u_list) == 23
    assert u_list[0] == 100 and u_list[8] == 115 and u_list[-1] == 85
    assert max(u_list) == 115 and min(u_list) == 85
    assert ui.textEdit_VoltageLadder_Un.toPlainText() == "230"
    assert ui.textEdit_VoltageLadder_TIME.toPlainText() == "1"
    assert ui.comboBox_VoltageLadder_TIME.currentText() == "分钟"


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
    logs = _prep_send(ui, sw, monkeypatch, tmp_path, "100,103,105")
    sw.thaistaticQUSend()

    volts = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and r[1] == "write" and str(r[2]).startswith("VOLT ")]
    assert any(v.startswith("VOLT 230") for v in volts)
    assert any(v.startswith("VOLT 236.9") for v in volts)
    assert any(v.startswith("VOLT 241.5") for v in volts)
    assert sw.total_save_file == 3
    wt_cfg = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]
    names = [p.strip() for p in str(wt_cfg.get("textEdit_FileNameList") or "").split(",") if p.strip()]
    assert names == ["QU_100", "QU_103", "QU_105"]
    col6 = [r[6] for r in sw.strArrayTest if r and r[0] == "AC" and r[6] != ""]
    assert "ASYNC_START" not in col6
    assert "WAIT_END" not in col6
    assert sum(1 for c in col6 if str(c).lstrip("-").isdigit()) == 3
    assert any("逐点存盘" in m for m in logs)


def test_send_default_rise_fall_points(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    logs = _prep_send(ui, sw, monkeypatch, tmp_path, DEFAULT_U)
    ui.textEdit_VoltageLadder_TIME.setText("1")
    ui.comboBox_VoltageLadder_TIME.setCurrentText("分钟")
    sw.thaistaticQUSend()
    assert sw.total_save_file == 23
    assert any("逐点存盘 23 文件" in m and "23 点" in m for m in logs)
    names = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]["textEdit_FileNameList"]
    assert names.startswith("QU_100,") and names.endswith("QU_85")
    assert len(names.split(",")) == 23
    col6 = [r[6] for r in sw.strArrayTest if r and r[0] == "AC" and r[6] != ""]
    assert "ASYNC_START" not in col6 and "WAIT_END" not in col6
    assert sum(1 for c in col6 if str(c).lstrip("-").isdigit()) == 23


def test_send_three_phase_scales_all_phases(qapp, monkeypatch, tmp_path):
    import SCPITestWave as sw
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "100,110")
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setText("230")
    ui.textEdit_S1_AC_VOLT_2.setText("230")
    ui.textEdit_S1_AC_VOLT_3.setText("230")
    ui.textEdit_VoltageLadder_Un.setText("230")
    sw.thaistaticQUSend()

    nsel = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and str(r[2]).startswith("INST:NSEL")]
    assert nsel.count("INST:NSEL 1") >= 2
    assert nsel.count("INST:NSEL 2") >= 2
    assert nsel.count("INST:NSEL 3") >= 2
    volts = [r[2] for r in sw.strArrayTest if r and r[0] == "AC" and str(r[2]).startswith("VOLT ")]
    assert volts.count("VOLT 230.0") + volts.count("VOLT 230") >= 3  # 100% 三相
    assert any(v.startswith("VOLT 253") for v in volts)  # 110%
    assert sw.total_save_file == 2


def test_send_wt_smoke_list_three_points(qapp, monkeypatch, tmp_path):
    """短 list：100,107,93 覆盖额定 / 高压 / 低压段，逐点三文件。"""
    import SCPITestWave as sw
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "100,107,93")
    ui.textEdit_VoltageLadder_TIME.setText("5")
    sw.thaistaticQUSend()
    assert sw.total_save_file == 3
    wt_cfg = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]
    assert wt_cfg["textEdit_FileNameList"] == "QU_100,QU_107,QU_93"
    volts = [r[2] for r in sw.strArrayTest if r and str(r[2]).startswith("VOLT ")]
    assert any("230" in v for v in volts)
    assert any("246.1" in v for v in volts)  # 107%
    assert any("213.9" in v for v in volts)  # 93%
    col6 = [r[6] for r in sw.strArrayTest if r and r[0] == "AC" and r[6] != ""]
    assert "ASYNC_START" not in col6
    assert sum(1 for c in col6 if str(c).lstrip("-").isdigit()) == 3


def test_voltage_math_matrix():
    """关键 Un% → VOLT 换算，供真机对表。"""
    un = 230.0
    cases = [(100, 230.0), (103, 236.9), (107, 246.1), (115, 264.5), (93, 213.9), (85, 195.5)]
    for pct, expect in cases:
        assert round(un * pct / 100.0, 2) == expect


def test_wt_async_col6_helpers():
    import SCPITestWave as sw
    assert sw._is_wt_async_start("ASYNC_START")
    assert sw._is_wt_async_start("async_start")
    assert sw._is_wt_wait_end("WAIT_END")
    assert not sw._is_wt_async_start("100")
    assert not sw._is_wt_wait_end(100)


def test_send_chinese_comma_and_spaces(qapp, monkeypatch, tmp_path):
    """中文逗号/空格分隔：文件数=点数=col6 数字次数。"""
    import SCPITestWave as sw
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "100， 103  105%")
    ui.textEdit_VoltageLadder_TIME.setText("2")
    ui.comboBox_VoltageLadder_TIME.setCurrentText("秒")
    sw.thaistaticQUSend()

    assert sw.total_save_file == 3
    wt_cfg = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]
    assert wt_cfg["textEdit_FileNameList"] == "QU_100,QU_103,QU_105"
    col6_nums = [
        int(r[6])
        for r in sw.strArrayTest
        if r and r[0] == "AC" and r[6] not in ("", None) and str(r[6]).lstrip("-").isdigit()
    ]
    assert col6_nums == [20, 20, 20]  # 2s → 20 *0.1s


def test_send_decimal_pct_filename(qapp, monkeypatch, tmp_path):
    """小数 Un% → 文件名用 p 代替小数点。"""
    import SCPITestWave as sw
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "100,100.5,99.5")
    sw.thaistaticQUSend()
    assert sw.total_save_file == 3
    wt_cfg = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"][0][4]
    assert wt_cfg["textEdit_FileNameList"] == "QU_100,QU_100p5,QU_99p5"


def test_send_empty_ladder_no_point_files(qapp, monkeypatch, tmp_path):
    """电压 list 为空：不走逐点（无 QU_ 文件名）；旧逻辑仍记 1 轮。"""
    import SCPITestWave as sw
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    _prep_send(ui, sw, monkeypatch, tmp_path, "")
    sw.thaistaticQUSend()
    assert sw.total_save_file == 1  # 非阶梯时的旧 +1
    wt_rows = [r for r in sw.strArrayTest if r and r[0] == "Upper_WT_Config"]
    assert wt_rows
    names = str(wt_rows[0][4].get("textEdit_FileNameList") or "")
    assert "QU_" not in names
    col6_nums = [
        r[6]
        for r in sw.strArrayTest
        if r and r[0] == "AC" and r[6] not in ("", None) and str(r[6]).lstrip("-").isdigit()
    ]
    assert col6_nums == []


def test_voltage_ladder_settings_csv_roundtrip(qapp, tmp_path):
    """Open/Save 字段：VoltageLadder / Un / 驻留可往返。"""
    import csv
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU
    from utils.Open_Save_ThaiStaticQU import arrayRow1

    ui = Ui_Dialog_thaiStaticQU()
    dialog = QDialog()
    ui.setupUi(dialog)
    ui.textEdit_VoltageLadder.setText("100,107,93")
    ui.textEdit_VoltageLadder_Un.setText("240")
    ui.textEdit_VoltageLadder_FR.setText("60")
    ui.textEdit_VoltageLadder_TIME.setText("5")
    ui.comboBox_VoltageLadder_TIME.setCurrentText("秒")

    # 按 Save 字段列表写一行（Style + 控件）
    headers = list(arrayRow1) if arrayRow1 and arrayRow1[0] == "Style" else ["Style"] + list(arrayRow1)
    # Open_Save 里 arrayRow1 可能不含 Style；兼容两种
    if headers[0] != "Style":
        headers = ["Style"] + headers

    values = ["ThaiStaticQU"]
    for name in headers[1:]:
        w = getattr(ui, name, None)
        if w is None:
            values.append("")
        elif hasattr(w, "isChecked"):
            values.append("1" if w.isChecked() else "0")
        elif hasattr(w, "currentIndex"):
            values.append(str(w.currentIndex()))
        elif hasattr(w, "toPlainText"):
            values.append(w.toPlainText())
        else:
            values.append("")

    path = tmp_path / "staticqu_ladder.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as fp:
        csv.writer(fp).writerow(headers)
        csv.writer(fp).writerow(values)

    # 清空再按 Open 逻辑回填 VoltageLadder 相关字段
    ui.textEdit_VoltageLadder.setText("")
    ui.textEdit_VoltageLadder_Un.setText("230")
    ui.textEdit_VoltageLadder_TIME.setText("1")
    with path.open("r", encoding="utf-8-sig") as fp:
        rows = list(csv.reader(fp))
    h, v = rows[0], rows[1]
    cfg = dict(zip(h, v))
    ui.textEdit_VoltageLadder.setText(cfg.get("textEdit_VoltageLadder") or "")
    ui.textEdit_VoltageLadder_Un.setText(cfg.get("textEdit_VoltageLadder_Un") or "")
    ui.textEdit_VoltageLadder_FR.setText(cfg.get("textEdit_VoltageLadder_FR") or "")
    ui.textEdit_VoltageLadder_TIME.setText(cfg.get("textEdit_VoltageLadder_TIME") or "")
    try:
        ui.comboBox_VoltageLadder_TIME.setCurrentIndex(int(cfg.get("comboBox_VoltageLadder_TIME") or 0))
    except ValueError:
        pass

    assert ui.textEdit_VoltageLadder.toPlainText() == "100,107,93"
    assert ui.textEdit_VoltageLadder_Un.toPlainText() == "240"
    assert ui.textEdit_VoltageLadder_FR.toPlainText() == "60"
    assert ui.textEdit_VoltageLadder_TIME.toPlainText() == "5"
    assert ui.comboBox_VoltageLadder_TIME.currentText() == "秒"