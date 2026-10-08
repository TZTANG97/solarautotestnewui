# -*- coding: utf-8 -*-
import sys
import types

from agent.local_endpoints import collect_local_endpoints


def test_collect_maps_com_to_asrl(monkeypatch):
    class _Port:
        device = "COM3"
        description = "USB-SERIAL CH340"

    import agent.local_endpoints as mod

    mod._cache = []
    mod._cache_at = 0.0

    # winreg 空：走 pyserial 假模块
    def _empty_winreg():
        return [], None

    monkeypatch.setattr(mod, "_enumerate_winreg", _empty_winreg)

    fake = types.ModuleType("serial")
    tools = types.ModuleType("serial.tools")
    list_ports = types.ModuleType("serial.tools.list_ports")
    list_ports.comports = lambda: [_Port()]
    tools.list_ports = list_ports
    fake.tools = tools
    monkeypatch.setitem(sys.modules, "serial", fake)
    monkeypatch.setitem(sys.modules, "serial.tools", tools)
    monkeypatch.setitem(sys.modules, "serial.tools.list_ports", list_ports)

    items = collect_local_endpoints(force=True)
    assert items == [
        {
            "kind": "serial",
            "resource": "ASRL3::INSTR",
            "label": "COM3 USB-SERIAL CH340",
            "com": "COM3",
        }
    ]


def test_collect_uses_winreg_without_pyserial(monkeypatch):
    import agent.local_endpoints as mod

    mod._cache = []
    mod._cache_at = 0.0

    monkeypatch.setattr(
        mod,
        "_enumerate_winreg",
        lambda: (
            [
                {
                    "kind": "serial",
                    "resource": "ASRL5::INSTR",
                    "label": "COM5 \\Device\\Serial0",
                    "com": "COM5",
                }
            ],
            None,
        ),
    )
    monkeypatch.setattr(mod, "_enumerate_pyserial", lambda: ([], "pyserial not installed"))

    items = collect_local_endpoints(force=True)
    assert items[0]["resource"] == "ASRL5::INSTR"
    assert items[0]["com"] == "COM5"


def test_collect_keeps_cache_when_empty(monkeypatch):
    import agent.local_endpoints as mod

    mod._cache = [{"kind": "serial", "resource": "ASRL1::INSTR", "label": "COM1", "com": "COM1"}]
    mod._cache_at = 0.0
    monkeypatch.setattr(mod, "_enumerate_winreg", lambda: ([], None))
    monkeypatch.setattr(mod, "_enumerate_pyserial", lambda: ([], "pyserial not installed"))

    items = collect_local_endpoints(force=True)
    assert items[0]["resource"] == "ASRL1::INSTR"


def test_serialcomm_missing_key_is_empty_not_error(monkeypatch):
    """无串口时 SERIALCOMM 键不存在（WinError 2）应视为空列表，不报故障。"""
    import agent.local_endpoints as mod

    class _FakeWinreg:
        HKEY_LOCAL_MACHINE = object()

        @staticmethod
        def OpenKey(_hive, _path):
            err = OSError(2, "The system cannot find the file specified")
            err.winerror = 2
            raise err

    monkeypatch.setitem(__import__("sys").modules, "winreg", _FakeWinreg)
    items, err = mod._enumerate_winreg()
    assert items == []
    assert err is None
