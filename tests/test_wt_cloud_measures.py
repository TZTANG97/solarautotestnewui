# -*- coding: utf-8 -*-
"""WT 最新行映射为云端 measures；experdata payload 附带 measures。"""
from agent.mqtt_publish import build_experdata_payload
from devices.wt_data_collector import WtScpiCollector


class _DummyCtrl:
    connected = False
    handle = None


def test_latest_cloud_measures_from_items():
    c = WtScpiCollector(_DummyCtrl())
    c._items = [
        "URMS,1",
        "URMS,2",
        "URMS,3",
        "IRMS,1",
        "IRMS,2",
        "IRMS,3",
        "P,SIGMA",
        "FU,1",
    ]
    with c._rows_lock:
        c._rows = [
            (
                1.0,
                [230.0, 231.0, 229.0, 1.0, 1.1, 0.9, 700.0, 50.02],
            )
        ]
    m = c.latest_cloud_measures()
    assert m is not None
    assert abs(m["u_rms"] - 230.0) < 1e-6
    assert abs(m["i_rms"] - 1.0) < 1e-6
    assert abs(m["p"] - 700.0) < 1e-6
    assert abs(m["freq"] - 50.02) < 1e-6


def test_latest_cloud_measures_empty():
    c = WtScpiCollector(_DummyCtrl())
    assert c.latest_cloud_measures() is None


def test_build_experdata_with_measures():
    payload = build_experdata_payload(
        pythonid="SOLAR-PC-X",
        job_id=42,
        progress_percent=12,
        progress_text="measuring",
        current_step="S1",
        measures={"u_rms": 220.0, "i_rms": 1.0, "p": 100.0, "freq": 50.0},
    )
    assert payload["type"] == "SolarEquipment_experdata_return"
    assert payload["measures"]["u_rms"] == 220.0
    assert payload["equs"][0]["measures"]["p"] == 100.0


def test_build_experdata_without_measures():
    payload = build_experdata_payload(
        pythonid="SOLAR-PC-X",
        job_id=1,
        progress_percent=0,
    )
    assert "measures" not in payload
    assert "measures" not in payload["equs"][0]
