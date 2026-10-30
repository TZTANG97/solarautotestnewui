# -*- coding: utf-8 -*-
"""Agent 仪器快照：只上报真正连通过的仪。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import instruments_snapshot as snap


def test_typed_ip_never_connected_not_reported(tmp_path: Path, monkeypatch):
    """输入框里填过、从未成功连接 → 不应出现在心跳仪器列表。"""
    monkeypatch.setattr(snap, "_cache", [])
    monkeypatch.setattr(snap, "_cache_at", 0.0)
    status = tmp_path / "status.json"
    # 模拟首页占位：有名字但无 resource / 无 last_connected
    status.write_text(
        json.dumps(
            {
                "devices": [
                    {"name": "交流电源", "connected": False, "resource": ""},
                    {"name": "直流电源1", "connected": False, "resource": ""},
                ],
                "project": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    # 字段记忆里有乱填 IP（旧逻辑会扫这些）——新逻辑不应读它们
    out = snap.collect_instruments_snapshot(status_json_path=str(status), force=True)
    assert out == []


def test_connected_device_reported_online(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(snap, "_cache", [])
    monkeypatch.setattr(snap, "_cache_at", 0.0)
    status = tmp_path / "status.json"
    status.write_text(
        json.dumps(
            {
                "devices": [
                    {
                        "name": "交流电源",
                        "connected": True,
                        "resource": "192.168.1.10:5025",
                        "last_connected": "2026-09-18 10:00:00",
                    }
                ],
                "project": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out = snap.collect_instruments_snapshot(status_json_path=str(status), force=True)
    assert len(out) == 1
    assert out[0]["resource"] == "192.168.1.10:5025"
    assert out[0]["slot"] == "ac"
    assert out[0]["online"] is True
    assert out[0]["connected"] is True
    assert out[0]["source"] == "agent_status"


def test_dew_widgets_and_default_brand_reported(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(snap, "_cache", [])
    monkeypatch.setattr(snap, "_cache_at", 0.0)
    status = tmp_path / "status.json"
    status.write_text(
        json.dumps(
            {
                "devices": [
                    {
                        "name": "DEWETRON",
                        "connected": True,
                        "resource": "192.168.40.24:10001",
                        "last_connected": "2026-09-23 22:00:00",
                        "widgets": {
                            "comboBox_DEW_MaxRefreshRate": "200",
                            "comboBox_downsampling": "Auto",
                            "dew_wiring_type": 0,
                        },
                    }
                ],
                "project": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out = snap.collect_instruments_snapshot(status_json_path=str(status), force=True)
    assert len(out) == 1
    assert out[0]["slot"] == "dew"
    assert out[0]["brand"] == "DEWETRON"
    assert out[0]["serial"].startswith("SAT-DEW-")
    assert "::" not in out[0]["serial"]
    assert out[0]["widgets"]["comboBox_DEW_MaxRefreshRate"] == "200"
    assert out[0]["widgets"]["dew_wiring_type"] == 0


def test_disconnected_but_was_connected_reports_offline(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(snap, "_cache", [])
    monkeypatch.setattr(snap, "_cache_at", 0.0)
    status = tmp_path / "status.json"
    status.write_text(
        json.dumps(
            {
                "devices": [
                    {
                        "name": "直流电源1",
                        "connected": False,
                        "resource": "10.0.0.2:502",
                        "last_connected": "2026-09-17 12:00:00",
                    }
                ],
                "project": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out = snap.collect_instruments_snapshot(status_json_path=str(status), force=True)
    assert len(out) == 1
    assert out[0]["online"] is False
    assert out[0]["connected"] is False
    assert out[0]["slot"] == "dc1"


def test_resource_without_ever_connected_skipped(tmp_path: Path, monkeypatch):
    """异常残留 resource、无 last_connected、当前未连 → 不上报。"""
    monkeypatch.setattr(snap, "_cache", [])
    monkeypatch.setattr(snap, "_cache_at", 0.0)
    status = tmp_path / "status.json"
    status.write_text(
        json.dumps(
            {
                "devices": [
                    {
                        "name": "交流电源",
                        "connected": False,
                        "resource": "192.1",
                    }
                ],
                "project": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out = snap.collect_instruments_snapshot(status_json_path=str(status), force=True)
    assert out == []


def test_dc_bluesight_on_port_502_not_reported_as_itech(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(snap, "_cache", [])
    monkeypatch.setattr(snap, "_cache_at", 0.0)
    status = tmp_path / "status.json"
    status.write_text(
        json.dumps(
            {
                "devices": [
                    {
                        "name": "交流电源",
                        "connected": True,
                        "resource": "192.168.40.210:502",
                        "last_connected": "2026-10-29 21:00:00",
                        "brand": "itech",
                    },
                    {
                        "name": "直流电源1",
                        "connected": True,
                        "resource": "192.168.40.12:502",
                        "last_connected": "2026-10-29 21:00:00",
                        "brand": "bluesight",
                        "widgets": {
                            "textEdit_Vmp": "650",
                            "textEdit_Imp": "12.3077",
                            "textEdit_Voc": "726.722",
                            "textEdit_Isc": "13.7576",
                            "textEdit_PF": "100",
                        },
                    },
                ],
                "project": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out = snap.collect_instruments_snapshot(status_json_path=str(status), force=True)
    by_slot = {item["slot"]: item for item in out}
    assert by_slot["ac"]["brand"] == "ITECH"
    assert by_slot["dc1"]["brand"] == "Bluesight"
    assert by_slot["dc1"]["widgets"]["textEdit_Vmp"] == "650"
    assert by_slot["dc1"]["widgets"]["textEdit_Imp"] == "12.3077"


def test_usb_dc_chroma_serial_from_visa(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(snap, "_cache", [])
    monkeypatch.setattr(snap, "_cache_at", 0.0)
    status = tmp_path / "status.json"
    status.write_text(
        json.dumps(
            {
                "devices": [
                    {
                        "name": "直流电源1",
                        "connected": True,
                        "resource": "USB0::0x0A69::0x084B::S50000002314::INSTR",
                        "last_connected": "2026-09-28 09:00:00",
                    }
                ],
                "project": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out = snap.collect_instruments_snapshot(status_json_path=str(status), force=True)
    assert len(out) == 1
    assert out[0]["brand"] == "CHROMA"
    assert out[0]["serial"] == "S50000002314"
    assert out[0]["slot"] == "dc1"
