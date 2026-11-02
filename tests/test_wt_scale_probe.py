# -*- coding: utf-8 -*-
"""连接页比例系数试读：下发命令与读数解析。"""
from __future__ import annotations


class _FakeCtrl:
    def __init__(self, idn="YOKOGAWA,WT5000,0,0"):
        self.connected = True
        self.writes = []
        self._idn = idn
        self._items = {}

    def write(self, command):
        self.writes.append(command)
        if ":NUMERIC:NORMAL:ITEM" in command.upper() and "?" not in command:
            parts = command.split(None, 1)
            self._items[parts[0].upper()] = parts[1] if len(parts) > 1 else ""

    def query(self, command):
        u = command.upper().strip()
        if u == "*IDN?":
            return self._idn
        if u.startswith(":NUMERIC:NORMAL:ITEM") and u.endswith("?"):
            key = command.split("?")[0].upper()
            for stored, value in self._items.items():
                if stored == key:
                    return f"{stored} {value}"
            return ""
        if "VALUE?" in u:
            n = max(len(self._items), 1)
            return ",".join(f"{100 + i}.{i}" for i in range(n))
        return ""


def test_probe_items_and_parse():
    from utils.wt_scale_probe import (
        detect_model_from_idn,
        format_probe_text,
        parse_probe_values,
        probe_items,
    )

    assert detect_model_from_idn("YOKOGAWA,WT3000E,1,2") == "3000"
    assert detect_model_from_idn("YOKOGAWA,WT5000,1,2") == "5000"
    assert probe_items("3000", 2) == [
        "U,1,TOTAL",
        "I,1,TOTAL",
        "P,1,TOTAL",
        "FU,1",
        "U,2,TOTAL",
        "I,2,TOTAL",
        "P,2,TOTAL",
        "FU,2",
    ]
    assert probe_items("5000", 1) == ["URMS,1", "IRMS,1", "P,1", "FU,1"]
    measures = parse_probe_values(
        ["URMS,1", "IRMS,1", "P,1", "FU,1"],
        [230.1, 1.02, 234.0, 50.0],
    )
    assert measures == {"U1": 230.1, "I1": 1.02, "P1": 234.0, "F1": 50.0}
    text = format_probe_text(measures, 1)
    assert "E1" in text and "230.1" in text and "50" in text


def test_apply_and_probe_on_fake_wt5000():
    from utils.wt_scale_probe import apply_scales, prepare_probe, read_probe

    ctrl = _FakeCtrl("YOKOGAWA,WT5000,0,0")
    ok, msg, commands = apply_scales(
        ctrl,
        {"lineEdit_wt_vt_1": "100", "lineEdit_wt_ct_1": "20"},
        style="Thai_WT5000_Config",
    )
    assert ok, msg
    assert ":INPUT:SCALING:STATE:ELEMENT1 ON" in commands
    assert ":INPUT:SCALING:VT:ELEMENT1 100" in commands
    assert ":INPUT:SCALING:CT:ELEMENT1 20" in commands

    ok2, msg2, items = prepare_probe(ctrl)
    assert ok2, msg2
    assert items[0].startswith("URMS,")
    ok3, text, measures = read_probe(ctrl, items)
    assert ok3, text
    assert "U1" in measures
    assert "E1" in text


def test_prepare_probe_uses_wt3000_tokens():
    from utils.wt_scale_probe import prepare_probe

    ctrl = _FakeCtrl("YOKOGAWA,WT3000,0,0")
    ok, msg, items = prepare_probe(ctrl, element_count=1)
    assert ok, msg
    assert items == ["U,1,TOTAL", "I,1,TOTAL", "P,1,TOTAL", "FU,1"]


def test_apply_scales_limits_elements_by_idn_model():
    from utils.wt_scale_probe import apply_scales

    ctrl = _FakeCtrl("YOKOGAWA,WT3000,0,0")
    mapping = {f"lineEdit_wt_vt_{n}": "1" for n in range(1, 8)}
    mapping.update({f"lineEdit_wt_ct_{n}": "1" for n in range(1, 8)})
    ok, msg, commands = apply_scales(ctrl, mapping)
    assert ok, msg
    assert "3000" in msg
    assert any("ELEMENT4" in cmd for cmd in commands)
    assert all("ELEMENT5" not in cmd for cmd in commands)
    assert all("ELEMENT7" not in cmd for cmd in commands)
