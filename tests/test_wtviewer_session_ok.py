# -*- coding: utf-8 -*-
"""空闲时 WT Soft Panel / 按钮态也要判已连，供 status.json → 网页上报。"""
from utils.wtviewer_session import wtviewer_window_alive


def test_wtviewer_alive_when_efree_title_present():
    assert wtviewer_window_alive(
        enum_windows=lambda: {1: "WTViewerEfree", 2: "数值详细设置"}
    )


def test_wtviewer_alive_ignores_detail_only():
    assert not wtviewer_window_alive(enum_windows=lambda: {1: "数值详细设置"})


def test_wtviewer_alive_false_when_no_windows():
    assert not wtviewer_window_alive(enum_windows=lambda: {})


def test_iot_slot_session_ok_wt_via_wtviewer(monkeypatch):
    import SCPITestWave as m

    monkeypatch.setattr(m, "wt3000_controller", None, raising=False)
    monkeypatch.setattr(m, "app_ctx", type("C", (), {"strConnectWT3000": "0"})(), raising=False)
    monkeypatch.setattr(m, "ui", type("U", (), {})(), raising=False)
    monkeypatch.setattr(
        "utils.wtviewer_session.wtviewer_window_alive", lambda: True
    )
    assert m._iot_slot_session_ok("wt") is True


def test_iot_slot_session_ok_wt_false_when_idle_no_soft_panel(monkeypatch):
    import SCPITestWave as m

    class Ctrl:
        connected = False
        handle = None

    monkeypatch.setattr(m, "wt3000_controller", Ctrl(), raising=False)
    monkeypatch.setattr(m, "app_ctx", type("C", (), {"strConnectWT3000": "0"})(), raising=False)
    monkeypatch.setattr(m, "ui", type("U", (), {})(), raising=False)
    monkeypatch.setattr(
        "utils.wtviewer_session.wtviewer_window_alive", lambda: False
    )
    assert m._iot_slot_session_ok("wt") is False


def test_iot_slot_session_ok_wt_via_handle_without_flag(monkeypatch):
    import SCPITestWave as m

    class Ctrl:
        connected = False
        handle = object()

    monkeypatch.setattr(m, "wt3000_controller", Ctrl(), raising=False)
    monkeypatch.setattr(m, "app_ctx", type("C", (), {"strConnectWT3000": "0"})(), raising=False)
    monkeypatch.setattr(m, "ui", type("U", (), {})(), raising=False)
    monkeypatch.setattr(
        "utils.wtviewer_session.wtviewer_window_alive", lambda: False
    )
    assert m._iot_slot_session_ok("wt") is True
