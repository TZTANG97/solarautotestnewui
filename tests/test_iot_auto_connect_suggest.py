# -*- coding: utf-8 -*-
"""suggest_auto_jobs uniqueness rules."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.device_discovery import FoundDevice
from utils.iot_auto_connect import suggest_auto_jobs


def test_suggest_unique_kinds_and_skip_ambiguous():
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
    devices = [
        FoundDevice(resource="DC-remembered", kind_hint="dc"),
        FoundDevice(resource="DC-other", kind_hint="dc"),
    ]
    jobs = dict(suggest_auto_jobs(devices))
    assert jobs.get("dc2").resource == "DC-remembered"
    assert jobs.get("dc1").resource == "DC-other"  # leftover unique DC -> dc1