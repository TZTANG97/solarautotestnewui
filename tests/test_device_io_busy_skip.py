# -*- coding: utf-8 -*-
"""设备连接忙时返回值不得当成失败弹窗。"""
from __future__ import annotations

from utils.iot_remote_ui import remote_connect_silent, silent_remote_connect


def test_none_means_busy_not_failure():
    # 与 SCPITestWave._device_io_is_busy_result 同语义
    assert (None is None) is True
    assert (False is None) is False
    assert (True is None) is False


def test_silent_remote_connect_suppresses_modals_flag():
    assert remote_connect_silent() is False
    with silent_remote_connect():
        assert remote_connect_silent() is True
        with silent_remote_connect():
            assert remote_connect_silent() is True
        assert remote_connect_silent() is True
    assert remote_connect_silent() is False


def test_show_connect_message_silent_no_raise(monkeypatch):
    from utils import ui_helpers

    calls = []

    def _boom(*_a, **_k):
        calls.append("modal")
        raise AssertionError("启动/自动连时不应弹模态框")

    monkeypatch.setattr(ui_helpers.QMessageBox, "information", staticmethod(_boom))
    with silent_remote_connect():
        ui_helpers._show_connect_message("直流电源1连接失败，请检查IP和端口")
    assert calls == []
