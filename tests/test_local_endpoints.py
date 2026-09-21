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
