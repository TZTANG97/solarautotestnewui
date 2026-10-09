# -*- coding: utf-8 -*-
from utils.wt_flicker_display import FLICKER_MODE_CMDS, switch_wt_flicker_display


def test_flicker_cmds_include_display_mode():
    assert "DISPLAY:MODE FLICker" in FLICKER_MODE_CMDS


def test_switch_reports_not_connected_when_no_controller(monkeypatch):
    import utils.wt_flicker_display as mod

    monkeypatch.setattr(mod, "_controller", lambda: None)
    out = switch_wt_flicker_display({"model": "WT3004E", "resource": "TCPIP0::1::INSTR"})
    assert out["ok"] is False
    assert "未连接" in out["message"]
    assert "WT3004E" in out["message"]


def test_switch_writes_display_mode(monkeypatch):
    import utils.wt_flicker_display as mod

    writes = []

    class _Handle:
        def write(self, cmd):
            writes.append(cmd)

    class _Ctrl:
        connected = True
        handle = _Handle()

    monkeypatch.setattr(mod, "_controller", lambda: _Ctrl())
    out = switch_wt_flicker_display({"model": "WT3004E"})
    assert out["ok"] is True
    assert ":COMMunicate:REMote ON" in writes
    assert "DISPLAY:MODE FLICker" in writes
    assert writes.index(":COMMunicate:REMote ON") < writes.index("DISPLAY:MODE FLICker")
