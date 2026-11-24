# -*- coding: utf-8 -*-
"""WT 控制器查找：__main__ / app.context 都能拿到已连接实例。"""
from __future__ import annotations

import sys


def test_get_controller_from_main_module(monkeypatch):
    import utils.wt_scpi_session as sess

    class _Ctrl:
        connected = True

    class _Main:
        wt3000_controller = _Ctrl()

    monkeypatch.setitem(sys.modules, "__main__", _Main())
    monkeypatch.delitem(sys.modules, "SCPITestWave", raising=False)
    got = sess._get_controller()
    assert got is not None
    assert got.connected is True


def test_prepare_skips_dew_slot(monkeypatch):
    from utils.device_discovery import FoundDevice
    from utils.iot_auto_connect import prepare_auto_connect_jobs

    devices = [
        FoundDevice(resource="192.168.40.19:5025", host="192.168.40.19", port=5025, kind_hint="wt"),
        FoundDevice(resource="192.168.40.50:10001", host="192.168.40.50", port=10001, kind_hint="dew"),
    ]
    monkeypatch.setattr(
        "utils.iot_auto_connect.discover_for_auto_connect",
        lambda **_k: devices,
    )
    monkeypatch.setattr(
        "utils.iot_auto_connect.suggest_auto_jobs",
        lambda _devs: [("wt", devices[0]), ("dew", devices[1])],
    )
    jobs, _ = prepare_auto_connect_jobs(skip_slots=("dew",))
    slots = [j[0] for j in jobs]
    assert "wt" in slots
    assert "dew" not in slots


def test_has_remembered_dew_from_success_map(monkeypatch):
    from utils.iot_auto_connect import has_remembered_slot

    monkeypatch.setattr("utils.iot_auto_connect.load_slot_map", lambda: {})
    monkeypatch.setattr(
        "utils.iot_auto_connect.load_success_device_map",
        lambda: {"192.168.40.24:10001": {"slot": "dew", "kind_hint": "dew"}},
    )
    monkeypatch.setattr(
        "utils.iot_auto_connect.devices_from_status_json",
        lambda *_a, **_k: [],
    )
    assert has_remembered_slot("dew") is True
    assert has_remembered_slot("wt") is False

def test_job_wants_dewetron_respects_wt_mode():
    from utils.iot_auto_connect import job_wants_dewetron

    assert job_wants_dewetron(widgets={'radio_wt': True}, instruments=[{'slot': 'dew'}, {'slot': 'wt'}]) is False
    assert job_wants_dewetron(widgets={'radio_dewetron': True}) is True
    assert job_wants_dewetron(instruments=[{'slot': 'wt'}]) is False
    assert job_wants_dewetron(instruments=[{'slot': 'dew'}]) is True
    assert job_wants_dewetron() is False
    # ac/dc + 残留 dew、未勾德威创 → 不得当要连德威创（否则过欠压乱弹连接失败）
    assert (
        job_wants_dewetron(
            instruments=[{"slot": "ac"}, {"slot": "dc1"}, {"slot": "dew"}]
        )
        is False
    )
    # 页内 WT 型号默认勾选不能盖掉显式德威创
    assert (
        job_wants_dewetron(
            widgets={"radio_dewetron": True, "radioButton_S2_WT3000": True}
        )
        is True
    )
    # 未勾德威创、仅型号页勾选：按仪器表判定（仅 dew → True，与无 widgets 一致）
    assert (
        job_wants_dewetron(
            widgets={"radioButton_S2_WT3000": True},
            instruments=[{"slot": "dew"}],
        )
        is True
    )
