# -*- coding: utf-8 -*-
"""suggest_auto_jobs uniqueness rules."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.device_discovery import FoundDevice
from utils.iot_auto_connect import suggest_auto_jobs


def test_suggest_unique_kinds_and_skip_ambiguous(monkeypatch):
    monkeypatch.setattr("utils.iot_auto_connect.load_slot_map", lambda: {})
    monkeypatch.setattr("utils.iot_auto_connect.load_slot_prefs", lambda: {})
    monkeypatch.setattr("utils.iot_auto_connect.load_success_device_map", lambda: {})
    devices = [
        FoundDevice(resource="AC-1", kind_hint="ac"),
        FoundDevice(resource="WT-1", kind_hint="wt"),
        FoundDevice(resource="DEW-1", kind_hint="dew"),
        FoundDevice(resource="SCOPE-1", kind_hint="scope"),
        FoundDevice(resource="DC-only", kind_hint="dc"),
        FoundDevice(resource="DC-extra", kind_hint="dc"),
        FoundDevice(resource="MB-1", kind_hint="modbus", protocol="modbus"),
    ]
    jobs = suggest_auto_jobs(devices)
    slots = {s for s, _ in jobs}
    resources = {d.resource for _, d in jobs}
    assert slots == {"ac", "wt", "dew", "scope"}
    assert "DC-only" not in resources
    assert "DC-extra" not in resources
    assert "MB-1" not in resources


def test_suggest_single_dc_to_dc1(monkeypatch):
    monkeypatch.setattr("utils.iot_auto_connect.load_slot_map", lambda: {})
    monkeypatch.setattr("utils.iot_auto_connect.load_slot_prefs", lambda: {})
    devices = [
        FoundDevice(resource="AC-1", kind_hint="ac"),
        FoundDevice(resource="DC-1", kind_hint="dc"),
    ]
    jobs = dict(suggest_auto_jobs(devices))
    assert jobs.get("ac").resource == "AC-1"
    assert jobs.get("dc1").resource == "DC-1"


def test_suggest_remembered_slot(monkeypatch):
    monkeypatch.setattr(
        "utils.iot_auto_connect.load_slot_map",
        lambda: {"DC-remembered": "dc2"},
    )
    monkeypatch.setattr("utils.iot_auto_connect.load_slot_prefs", lambda: {})
    monkeypatch.setattr("utils.iot_auto_connect.load_success_device_map", lambda: {})
    devices = [
        FoundDevice(resource="DC-remembered", kind_hint="dc"),
        FoundDevice(resource="DC-other", kind_hint="dc"),
    ]
    jobs = dict(suggest_auto_jobs(devices))
    assert jobs.get("dc2").resource == "DC-remembered"
    assert jobs.get("dc1").resource == "DC-other"  # leftover unique DC -> dc1


def test_suggest_slot_pref_prefers_keysight_over_other_dc(monkeypatch):
    """重开后 dc1 应连回上次成功的是德，而不是另一台在线致茂。"""
    hislip = "TCPIP0::169.254.1.2::hislip0::INSTR"
    chroma = "USB0::0x0AAD::CHROMA::INSTR"
    monkeypatch.setattr("utils.iot_auto_connect.load_slot_map", lambda: {})
    monkeypatch.setattr(
        "utils.iot_auto_connect.load_slot_prefs",
        lambda: {"dc1": hislip},
    )
    monkeypatch.setattr("utils.iot_auto_connect.load_success_device_map", lambda: {})
    devices = [
        FoundDevice(resource=chroma, kind_hint="dc", brand_hint="chroma"),
        FoundDevice(
            resource=hislip,
            host="169.254.1.2",
            kind_hint="dc",
            brand_hint="keysight",
        ),
    ]
    jobs = dict(suggest_auto_jobs(devices))
    assert jobs["dc1"].resource == hislip


def test_wt_slot_pref_does_not_bind_same_host_power_port(monkeypatch):
    """上次 WT 是 :5025 时，不能因为同 IP 把电源口 :502 当成功率分析仪。"""
    monkeypatch.setattr("utils.iot_auto_connect.load_slot_map", lambda: {})
    monkeypatch.setattr(
        "utils.iot_auto_connect.load_slot_prefs",
        lambda: {"wt": "192.168.40.100:5025"},
    )
    monkeypatch.setattr("utils.iot_auto_connect.load_success_device_map", lambda: {})
    devices = [
        FoundDevice(
            resource="192.168.40.100:502",
            host="192.168.40.100",
            port=502,
            kind_hint="modbus",
        ),
        FoundDevice(
            resource="192.168.40.100:5025",
            host="192.168.40.100",
            port=5025,
            kind_hint="wt",
        ),
    ]
    jobs = dict(suggest_auto_jobs(devices))
    assert jobs["wt"].port == 5025
    assert jobs["wt"].resource.endswith(":5025")


def test_explain_wt_port_mismatch_covers_power_ports():
    from utils.iot_auto_connect import explain_wt_port_mismatch

    for port in (502, 2101, 8080):
        msg = explain_wt_port_mismatch(port=port)
        assert msg
        assert str(port) in msg
    assert explain_wt_port_mismatch(port=10001) == ""
    assert explain_wt_port_mismatch(port=5025) == ""


def test_remember_text_for_plan_uses_corrected_wt_port():
    from utils.device_discovery import FoundDevice, connect_plan
    from utils.device_finder_connect import remember_text_for_plan
    from utils.iot_auto_connect import apply_prepared_connect_jobs

    dev = FoundDevice(
        resource="192.168.40.100:502",
        host="192.168.40.100",
        port=502,
        kind_hint="wt",
    )
    plan = connect_plan("wt", dev)
    assert remember_text_for_plan(plan, dev) == "192.168.40.100:5025"

    remembered = {}

    def _fake_remember(resource, slot):
        remembered[slot] = resource

    def _apply(slot, plan, device):
        return None

    import utils.iot_auto_connect as iac

    orig = iac.remember_slot_for_resource
    iac.remember_slot_for_resource = _fake_remember
    try:
        summary = apply_prepared_connect_jobs(
            [("wt", plan, dev)],
            apply_plan=_apply,
            session_ok=lambda slot: True,
        )
    finally:
        iac.remember_slot_for_resource = orig

    assert remembered["wt"] == "192.168.40.100:5025"
    assert summary["connected"] == ["wt:192.168.40.100:5025"]
