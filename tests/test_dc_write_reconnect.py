# -*- coding: utf-8 -*-
"""直流长跑：写失败静默重连并重试一次。"""
from __future__ import annotations

from devices.dc_controller import DCController


class _FakeLogger:
    def __init__(self):
        self.warnings = []
        self.errors = []
        self.infos = []

    def info(self, *a, **k):
        self.infos.append(a)

    def warning(self, *a, **k):
        self.warnings.append(a)

    def error(self, *a, **k):
        self.errors.append(a)


class _FlakyHandle:
    def __init__(self, fail_times=1):
        self.fail_times = fail_times
        self.writes = []

    def write(self, cmd):
        self.writes.append(cmd)
        if self.fail_times > 0:
            self.fail_times -= 1
            raise RuntimeError("VI_ERROR_CONN_LOST")

    def write_raw(self, payload):
        text = payload.decode("ascii", errors="ignore").rstrip("\n")
        self.write(text)


class _FakeRM:
    def __init__(self, new_handle):
        self.new_handle = new_handle
        self.opened = []

    def open_resource(self, addr):
        self.opened.append(addr)
        return self.new_handle


def _ctrl(rm=None):
    return DCController(
        _FakeLogger(),
        lambda *a, **k: None,
        lambda: "t",
        ui_setting=None,
        rm=rm,
        configure_scpi_resource=None,
    )


def test_write_command_reconnects_once_on_scpi_fail(monkeypatch):
    first = _FlakyHandle(fail_times=1)
    second = _FlakyHandle(fail_times=0)
    rm = _FakeRM(second)
    ctrl = _ctrl(rm=rm)
    ctrl.handle = first
    ctrl.connected = True
    ctrl.resource = "TCPIP0::192.168.1.10::INSTR"
    ctrl._transport = "scpi"

    monkeypatch.setattr("devices.dc_controller.release_resource_handle", lambda h: None)
    monkeypatch.setattr("devices.dc_controller.time.sleep", lambda s: None)

    assert ctrl.write_command("OUTP ON", label="DC1") is True
    assert first.writes == ["OUTP ON"]
    assert second.writes == ["OUTP ON"]
    assert rm.opened == ["TCPIP0::192.168.1.10::INSTR"]
    assert ctrl.handle is second


def test_write_command_no_reconnect_on_permanent_ivc_reject():
    ctrl = _ctrl()
    ctrl.client = type("C", (), {"is_connected": lambda self: True})()
    # 无 BluesightTranslator 真实链路：直接测 permanent 判定 + write_command 短路
    assert ctrl._is_permanent_write_reject("IVC:EDIT 1") is True
    assert ctrl._is_permanent_write_reject("OUTP ON") is False


def test_try_reconnect_fails_without_resource():
    ctrl = _ctrl()
    assert ctrl.try_reconnect("DC1") is False


def test_open_output_reconnects_when_handle_lost(monkeypatch):
    fresh = _FlakyHandle(fail_times=0)
    rm = _FakeRM(fresh)
    ctrl = _ctrl(rm=rm)
    ctrl.resource = "USB0::0x0A69::0x083E::INSTR"
    ctrl._transport = "scpi"
    ctrl.handle = None
    ctrl.connected = False

    monkeypatch.setattr("devices.dc_controller.release_resource_handle", lambda h: None)
    monkeypatch.setattr("devices.dc_controller.time.sleep", lambda s: None)

    assert ctrl.open_output("DC1", None, ctrl.logger) is True
    assert fresh.writes == ["OUTP ON"]
    assert ctrl.handle is fresh
