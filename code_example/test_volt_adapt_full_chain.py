# -*- coding: utf-8 -*-
"""全链路冒烟：AC(Chroma TCP) 上电/重连 → DC1 → WT 连续录 → 电压适应性扫压。

不连真机；用假句柄验证命令路径与分辨率约束。
"""
from __future__ import annotations

import logging
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

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


class _FakeScpi:
    """模拟 ScpiSocket：记录 write/query。"""

    def __init__(self):
        self.writes = []
        self.queries = []
        self.port = 2101

    def write(self, cmd):
        self.writes.append(str(cmd))

    def query(self, cmd):
        self.queries.append(str(cmd))
        if "ERR" in str(cmd).upper():
            return '0,"No error"'
        return "Chroma,61800-100,SIM,1.00"

    def close(self):
        pass


def _logger():
    lg = logging.getLogger("volt_adapt_full_chain")
    lg.setLevel(logging.INFO)
    if not lg.handlers:
        lg.addHandler(logging.NullHandler())
    return lg


def _fill_profile(ui, *, with_uv=True, with_dc=True, with_end=True):
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.comboBox_S1_AC_2.setCurrentText("三相")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("2")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.textEdit_S1_TIME.setPlainText("5")
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
    ui.textEdit_VoltageLadder_guoya.setPlainText("230-253@2")
    if with_uv:
        ui.textEdit_VoltageLadder_qianya.setPlainText("230-195@2")
        ui.checkBox_S12.setChecked(True)
        ui.checkBox_S12_RATE.setChecked(True)
    ui.checkBox_S3.setChecked(True)
    ui.checkBox_S3_RATE.setChecked(True)

    ui.checkBox_S_End.setChecked(bool(with_end))
    if with_end:
        ui.comboBox_S_End_AC.setCurrentText("关闭")
        ui.comboBox_S_End_DC1.setCurrentText("关闭")


def test_chroma_open_close_no_syst_run():
    """Chroma 上电/关机不得发 SYST:RUN / SYST:STANDBY。"""
    from devices.ac_controller import ACController

    fake = _FakeScpi()
    ac = ACController(_logger(), lambda *a, **k: None, lambda: "t")
    ac._set_handle(fake)
    ac._itech = None
    ac._store_idn("Chroma,61800-100,0,1.0")

    ac.open_output(setpoints=("230", "50", "三相"))
    assert "OUTP ON" in fake.writes
    assert not any("SYST:RUN" in w.upper() for w in fake.writes)
    assert "CONF:COUP AC" in fake.writes
    assert "PHAS:THREE SAMEFREQ" in fake.writes
    assert "VOLT:AC 230" in fake.writes
    assert any(w.startswith("VOLT") for w in fake.writes)

    fake.writes.clear()
    ac.close_output()
    assert "OUTP OFF" in fake.writes
    assert not any("SYST:STANDBY" in w.upper() for w in fake.writes)


def test_itech_open_still_uses_syst_run():
    """爱科路径仍须 SYST:RUN → OUTP ON。"""
    from devices.ac_controller import ACController

    ac = ACController(_logger(), lambda *a, **k: None, lambda: "t")
    fake = MagicMock()
    ac._set_handle(fake)
    ac._itech = MagicMock()
    ac._itech.translate.side_effect = lambda cmd: (True, ["ok"])

    ac.open_output(setpoints=None)
    calls = [c.args[0] for c in ac._itech.translate.call_args_list]
    assert calls == ["SYST:RUN", "OUTP ON"]


def test_reconnect_prefers_scpi_socket_not_visa(monkeypatch):
    """断线重连不得把 Chroma 换成坏 VISA 会话。"""
    from devices import ac_controller as ac_mod
    from devices.ac_controller import ACController

    created = []

    class _Sock:
        def __init__(self, host, port=None, timeout=10):
            self.host = host
            self.port = port or 2101
            self.timeout = timeout

        def connect(self):
            created.append((self.host, self.port))

        def close(self):
            pass

    monkeypatch.setattr(ac_mod, "ScpiSocket", _Sock)

    ac = ACController(_logger(), lambda *a, **k: None, lambda: "t", rm=MagicMock())
    ac.resource = "TCPIP::192.168.40.10::2101"
    old = _FakeScpi()
    ac._set_handle(old)

    # 误用 VISA 时会炸
    ac.rm.open_resource.side_effect = RuntimeError("should not use visa")

    assert ac.reconnect_scpi_tcp("192.168.40.10", None) is True
    assert created and created[0][0] == "192.168.40.10"
    assert ac.uses_scpi_socket() or isinstance(ac.handle, _Sock)
    assert str(ac.resource).startswith("TCPIP::192.168.40.10::")

    host, port = ACController._parse_scpi_tcp_endpoint(
        "TCPIP0::192.168.40.10::INSTR", "TCPIP::192.168.40.10::2101"
    )
    assert host == "192.168.40.10"
    assert port == 2101


def test_volt_normalize_0_1():
    from devices.ac_controller import _normalize_ac_volt_command, _normalize_chroma_ac_write

    assert _normalize_ac_volt_command("VOLT 230.04") == "VOLT 230"
    assert _normalize_chroma_ac_write("VOLT 230.04") == "VOLT:AC 230"
    assert _normalize_chroma_ac_write("VOLT:AC 230.61") == "VOLT:AC 230.6"
    assert _normalize_ac_volt_command("FREQ 50") == "FREQ 50"


def test_full_chain_plan_ac_dc_wt_sweep(qapp):
    """生成完整试验命令：AC 启机 → DC1 → WT 连续录 → 扫压 0.1V → 关机。"""
    from Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    from utils.voltage_adaptability_commands import build_voltage_adaptability_plan

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    _fill_profile(ui, with_uv=True, with_dc=True, with_end=True)

    plan = build_voltage_adaptability_plan(
        ui,
        wt_config_dict={
            "comboBox_AutoSave": 1,
            "textEdit_FileNameList": "VoltAdapt_BR_5421",
        },
        chroma_61800=True,
    )
    assert plan["ok"], plan.get("error")
    assert not plan["dc_errors"], plan["dc_errors"]
    cmds = plan["commands"]

    # --- AC 启机 ---
    ac_writes = [str(r[2]) for r in cmds if r[0] == "AC" and r[1] == "write"]
    assert "INST:PHAS THREE" in ac_writes
    assert "PHAS:THREE SAMEFREQ" in ac_writes
    assert "VOLT:AC 230" in ac_writes
    assert "FREQ 50" in ac_writes
    assert "OUTP ON" in ac_writes
    assert "OUTP OFF" in ac_writes
    assert not any("SYST:RUN" in w.upper() for w in ac_writes)
    assert not any("SYST:STANDBY" in w.upper() for w in ac_writes)

    # --- DC1 ---
    dc_writes = [str(r[2]) for r in cmds if r[0] == "DC1" and r[1] == "write"]
    assert dc_writes, "应有 DC1 命令"
    assert any("OUTP ON" in c for c in dc_writes)
    assert any("IVC" in c or "MODE TABLE" in c or "CURV" in c for c in dc_writes)

    # --- WT ---
    assert any(r[0] == "Upper_WT_Config" for r in cmds)
    assert plan["wt_type"] == "WT3000"
    assert plan["wt_continuous"] is True
    assert plan["file_names"] == ["VoltAdapt_BR_5421"]
    markers = [
        str(r[6]).strip().upper()
        for r in cmds
        if len(r) > 6 and r[6] not in ("", None)
    ]
    assert markers.count("ASYNC_START") == 1
    assert markers.count("WAIT_END") == 1

    # --- 扫压分辨率 ---
    volts = [str(r[2]) for r in cmds if str(r[2]).startswith("VOLT ")]
    for v in volts:
        body = v.split(None, 1)[1]
        if "." in body:
            assert len(body.split(".")[1]) <= 1, v
    assert "VOLT 253" in volts
    assert "VOLT 195" in volts

    # StopTime 覆盖墙钟
    wait_01 = int(plan["sweep_wait_01s"])
    band_01 = int(plan["band_duration_01s"])
    assert band_01 >= wait_01
    stop_sec = int(round(band_01 / 10.0 + 15))
    assert stop_sec >= int(round(wait_01 / 10.0)) + 15


def test_runloop_outp_on_routes_to_open_output(qapp):
    """试验循环写 OUTP ON 时走 open_output（Chroma 无 SYST:RUN）。"""
    from devices.ac_controller import ACController, _normalize_chroma_ac_write

    fake = _FakeScpi()
    ac = ACController(_logger(), lambda *a, **k: None, lambda: "t")
    ac._set_handle(fake)
    ac.connected = True
    ac._itech = None
    ac._store_idn("Chroma,61800-100,0,1.0")

    # 复刻 SCPITestWave AC write 分支
    def _dispatch(command):
        cmd_norm = str(command or "").strip().upper().replace(" ", "")
        if cmd_norm in ("OUTPON", "OUTP:ON"):
            ac.open_output()
        elif cmd_norm in ("OUTPOFF", "OUTP:OFF"):
            ac.close_output()
        else:
            if ac.is_chroma_61800():
                command = _normalize_chroma_ac_write(command)
            ac.handle.write(command)

    sequence = [
        "INST:PHAS THREE",
        "INST:EDIT ALL",
        "VOLT 230",
        "FREQ 50",
        "OUTP ON",
        "VOLT 230.04",
        "VOLT 230.61",
        "OUTP OFF",
    ]
    for cmd in sequence:
        _dispatch(cmd)

    assert "OUTP ON" in fake.writes
    assert "OUTP OFF" in fake.writes
    assert not any(w.upper() == "SYST:RUN" for w in fake.writes)
    assert "VOLT 230" in fake.writes
    assert "VOLT:AC 230.6" in fake.writes
    assert not any(w == "VOLT 230.04" for w in fake.writes)
    assert not any(w == "VOLT:AC 230.04" for w in fake.writes)


def test_default_filename_and_ov_only(qapp):
    from Dialog_thaivoltageadaptability import Ui_Dialog_thaivoltageadaptability
    from utils.voltage_adaptability_commands import build_voltage_adaptability_plan

    ui = Ui_Dialog_thaivoltageadaptability()
    dialog = QDialog()
    ui.setupUi(dialog)
    assert ui.checkBox_guoya_page.isChecked()
    assert not ui.checkBox_qianya_page.isChecked()

    te = None
    for i in range(ui._wtStacked.count()):
        te = ui._wtStacked.widget(i).findChild(QTextEdit, "textEdit_FileNameList")
        if te is not None:
            break
    assert te is not None and te.toPlainText().strip() == "VoltAdapt_BR_5421"

    plan = build_voltage_adaptability_plan(
        ui,
        wt_config_dict={"comboBox_AutoSave": 1, "textEdit_FileNameList": "junk"},
    )
    assert plan["ok"]
    assert plan["file_names"] == ["VoltAdapt_BR_5421"]
    assert len(plan["band_metas"]) == 1


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    test_chroma_open_close_no_syst_run()
    test_itech_open_still_uses_syst_run()
    # reconnect needs pytest monkeypatch — skip in __main__
    test_volt_normalize_0_1()
    test_full_chain_plan_ac_dc_wt_sweep(app)
    test_runloop_outp_on_routes_to_open_output(app)
    test_default_filename_and_ov_only(app)
    print("VOLT_ADAPT_FULL_CHAIN_OK")
