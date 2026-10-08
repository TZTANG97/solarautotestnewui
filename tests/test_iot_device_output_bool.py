# -*- coding: utf-8 -*-
"""IOT 开/关输出：回调必须返回显式 True，void/None 会被当成失败。"""
from __future__ import annotations

from devices.ac_controller import ACController
from devices.dc_controller import DCController
from utils.iot_device_cmd_inbox import execute_device_cmd


class _FakeLogger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass


def test_execute_output_on_false_when_callback_returns_none():
    """回归：旧 open_output void→None，bool(None) 误报失败。"""
    result = execute_device_cmd(
        {"action": "output_on", "instrument": {"slot": "ac"}},
        output_on=lambda slot: None,
    )
    assert result["ok"] is False
    assert "失败" in result["message"]


def test_execute_output_on_true_when_callback_returns_true():
    result = execute_device_cmd(
        {"action": "output_on", "instrument": {"slot": "ac"}},
        output_on=lambda slot: True,
    )
    assert result["ok"] is True
    assert "成功" in result["message"]


def test_execute_output_off_true_when_callback_returns_true():
    result = execute_device_cmd(
        {"action": "output_off", "instrument": {"slot": "dc1"}},
        output_off=lambda slot: True,
    )
    assert result["ok"] is True
    assert "成功" in result["message"]


def test_ac_open_close_return_false_when_disconnected():
    ctrl = ACController(
        _FakeLogger(),
        lambda *a, **k: None,
        lambda: "t",
        ui_setting=None,
        rm=None,
        configure_scpi_resource=None,
    )
    assert ctrl.handle is None
    assert ctrl.open_output() is False
    assert ctrl.close_output() is False


def test_dc_open_close_return_bool_when_disconnected():
    ctrl = DCController(
        _FakeLogger(),
        lambda *a, **k: None,
        lambda: "t",
        ui_setting=None,
        rm=None,
        configure_scpi_resource=None,
    )
    assert ctrl.open_output("DC1", None, _FakeLogger()) is False
    assert ctrl.close_output("DC1", None, _FakeLogger()) is False
    assert (
        ctrl.close_output("DC1", None, _FakeLogger(), silent_if_disconnected=True) is True
    )
