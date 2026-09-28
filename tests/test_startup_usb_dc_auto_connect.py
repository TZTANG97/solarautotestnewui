# -*- coding: utf-8 -*-
"""Startup auto-connect: status.json USB DC + slot memory."""
from __future__ import annotations

import json
from pathlib import Path

from utils.device_discovery import FoundDevice, devices_from_status_json
from utils.iot_auto_connect import discover_for_auto_connect, suggest_auto_jobs


def test_devices_from_status_json_usb_dc(tmp_path):
    path = tmp_path / "status.json"
    path.write_text(
        json.dumps(
            {
                "devices": [
                    {
                        "name": "直流电源1",
                        "connected": False,
                        "resource": "USB0::0x0AAD::0x01D6::INSTR",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    devices = devices_from_status_json(str(path))
    assert len(devices) == 1
    assert devices[0].kind_hint == "dc"
    assert devices[0].extra.get("last_slot") == "dc1"
    assert devices[0].resource.startswith("USB0::")


def test_suggest_uses_status_last_slot(monkeypatch):
    monkeypatch.setattr("utils.iot_auto_connect.load_slot_map", lambda: {})
    monkeypatch.setattr("utils.iot_auto_connect.load_success_device_map", lambda: {})
    devices = [
        FoundDevice(
            resource="USB0::0x0AAD::DC1::INSTR",
            kind_hint="dc",
            extra={"last_slot": "dc1"},
        )
    ]
    jobs = dict(suggest_auto_jobs(devices))
    assert jobs["dc1"].resource == "USB0::0x0AAD::DC1::INSTR"


def test_discover_skips_idn_for_known_usb(monkeypatch, tmp_path):
    path = tmp_path / "status.json"
    usb = "USB0::0x0AAD::0x01D6::INSTR"
    path.write_text(
        json.dumps(
            {
                "devices": [
                    {"name": "直流电源1", "resource": usb, "connected": False}
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    class _RM:
        def list_resources(self):
            return (usb,)

    monkeypatch.setattr(
        "utils.iot_auto_connect.last_known_resources", lambda _p=None: []
    )
    monkeypatch.setattr(
        "utils.iot_auto_connect.devices_from_last_resources", lambda *_a, **_k: []
    )
    monkeypatch.setattr(
        "utils.iot_auto_connect.list_visa_resources", lambda *_a, **_k: [usb]
    )
    monkeypatch.setattr(
        "utils.iot_auto_connect.load_success_device_map", lambda: {}
    )

    called = {"enrich": 0}

    def _enrich(*_a, **_k):
        called["enrich"] += 1
        raise AssertionError("USB with known slot must not probe *IDN?")

    monkeypatch.setattr("utils.iot_auto_connect.enrich_device", _enrich)
    devices = discover_for_auto_connect(visa_rm=_RM(), status_json_path=str(path))
    assert called["enrich"] == 0
    assert len(devices) == 1
    assert not devices[0].extra.get("offline")
    jobs = dict(suggest_auto_jobs(devices))
    assert "dc1" in jobs
