# -*- coding: utf-8 -*-
"""status.json 设备行 upsert（供 Agent 心跳）。"""
from __future__ import annotations

from utils.status_json_devices import (
    apply_device_connection,
    empty_status_payload,
    ensure_device_rows,
    mark_stale_in_flight_project,
)


def test_empty_payload_has_all_slots():
    data = empty_status_payload()
    names = [d["name"] for d in data["devices"]]
    assert "交流电源" in names and "WT3000" in names and "DEWETRON" in names


def test_mark_stale_in_flight_project_aborts_running():
    raw = {
        "devices": [],
        "project": {
            "name": "电压闪变",
            "status": "进行中",
            "progress": 42,
            "rounds": [{"index": 1, "filename": "a", "status": "进行中"}],
            "queue": [{"name": "电压闪变", "status": "进行中"}],
            "estimated_end_time": "12:00",
        },
    }
    data, changed = mark_stale_in_flight_project(raw)
    assert changed is True
    assert data["project"]["status"] == "已中止"
    assert data["project"]["name"] == "电压闪变"
    assert data["project"]["rounds"][0]["status"] == "中止"
    assert data["project"]["estimated_end_time"] == ""


def test_live_run_is_not_a_cold_start_leftover():
    from utils.status_json_devices import (
        project_status_is_live_local_run,
        status_when_binding_new_job,
    )

    assert project_status_is_live_local_run({"status": "进行中", "started_at": 10.0}, "") is True
    assert project_status_is_live_local_run({"status": "未开始", "started_at": 0}, "") is False
    assert project_status_is_live_local_run({}, "运行") is True
    assert status_when_binding_new_job("已中止") == "待开始"
    assert status_when_binding_new_job("已结束") == "待开始"
    assert status_when_binding_new_job("进行中") == "进行中"
    assert status_when_binding_new_job("暂停") == "暂停"


def test_mark_stale_leaves_finished_alone():
    raw = {
        "devices": [],
        "project": {"name": "谐波电流", "status": "已结束", "progress": 100},
    }
    data, changed = mark_stale_in_flight_project(raw)
    assert changed is False
    assert data["project"]["status"] == "已结束"


def test_apply_upserts_when_devices_empty():
    data = apply_device_connection(
        {"devices": [], "project": {}},
        device_name="交流电源",
        connected=True,
        resource="192.168.1.10:502",
    )
    ac = next(d for d in data["devices"] if d["name"] == "交流电源")
    assert ac["connected"] is True
    assert ac["resource"] == "192.168.1.10:502"
    assert ac["last_connected"]


def test_ensure_preserves_existing_resource():
    raw = {
        "devices": [
            {
                "name": "交流电源",
                "connected": True,
                "resource": "10.0.0.1:502",
                "last_connected": "2026-01-01 00:00:00",
            }
        ]
    }
    data = ensure_device_rows(raw)
    ac = next(d for d in data["devices"] if d["name"] == "交流电源")
    assert ac["resource"] == "10.0.0.1:502"
    assert len(data["devices"]) >= 8


def test_apply_extra_widgets_for_dew():
    data = apply_device_connection(
        empty_status_payload(),
        device_name="DEWETRON",
        connected=True,
        resource="192.168.40.24:10001",
        extra={
            "brand": "dewetron",
            "widgets": {"comboBox_DEW_MaxRefreshRate": "200", "dew_wiring_type": 0},
        },
    )
    dew = next(d for d in data["devices"] if d["name"] == "DEWETRON")
    assert dew["brand"] == "dewetron"
    assert dew["widgets"]["comboBox_DEW_MaxRefreshRate"] == "200"


class _FakeCombo:
    def __init__(self, text):
        self._text = text

    def currentText(self):
        return self._text


class _FakeBtn:
    def __init__(self, checked):
        self._checked = checked

    def isChecked(self):
        return self._checked


def test_bluesight_sas_iv_uses_page_not_chroma_defaults():
    from utils.status_json_devices import bluesight_iv_fields, dc_connection_extra

    iv = bluesight_iv_fields(
        {"mode": "sas", "pmpp_kw": 8.0, "umpp_v": 650.0, "ff": 0.8}
    )
    assert iv["vmp"] == "650"
    assert iv["pf"] == "100"
    assert abs(float(iv["imp"]) - (8000.0 / 650.0)) < 1e-3
    # 致茂页默认 220；Sandia 示例 Imp 不是 8000/650
    assert iv["vmp"] != "220"
    assert iv["voc"] != "220"
    assert abs(float(iv["imp"]) - 19.154) > 1
    extra = dc_connection_extra(brand="Bluesight", iv=iv, slot="dc1", force_iv=True)
    assert extra["brand"] == "bluesight"
    assert extra["widgets"]["textEdit_Vmp"] == "650"
    assert extra["widgets"]["textEdit_Imp"] == iv["imp"]
    assert extra["measures"]["vmp"] == "650"


def test_bluesight_display_name_is_bluesight():
    from utils.status_json_devices import canonical_reported_brand, dc_connection_extra

    assert canonical_reported_brand("蓝点(Bluesight)（Modbus 网口）") == "bluesight"
    extra = dc_connection_extra(
        brand="bluesight",
        iv={"vmp": "0", "voc": "", "imp": "", "isc": "", "pf": ""},
        slot="dc1",
        force_iv=True,
    )
    assert "widgets" not in extra or "textEdit_Vmp" not in (extra.get("widgets") or {})


def test_bluesight_original_zero_voltage_is_not_vmp():
    from utils.status_json_devices import bluesight_iv_fields

    iv = bluesight_iv_fields({"mode": "original", "outmode": "cv", "voltage_v": 0})
    assert iv["vmp"] == ""
    assert iv["imp"] == ""


def test_bluesight_original_load_does_not_copy_other_brand_iv():
    from utils.status_json_devices import bluesight_iv_fields

    iv = bluesight_iv_fields({"mode": "original", "outmode": "cv", "voltage_v": 480})
    assert iv["vmp"] == "480"
    assert iv["voc"] == ""
    assert iv["imp"] == ""
    assert iv["isc"] == ""
    assert iv["pf"] == ""


def test_ac_itech_connection_extra_brand():
    from utils.status_json_devices import ac_connection_extra

    extra = ac_connection_extra(brand="itech", voltage="230", frequency="50", phase="三相")
    assert extra["brand"] == "itech"
    assert extra["voltage"] == "230"
    assert extra["widgets"]["textEdit_AC_VOLT"] == "230"
    assert extra["widgets"]["comboBox_Phase"] == "三相"


def test_read_dewetron_ui_snapshot():
    from utils.status_json_devices import read_dewetron_ui_snapshot

    class FakeUi:
        comboBox_maxRefreshRate = _FakeCombo("200")
        comboBox_downsampling = _FakeCombo("Auto")
        comboBox_frequencyChannel = _FakeCombo("AI 1/U1")
        _wiring_buttons = [(0, _FakeBtn(True)), (1, _FakeBtn(False))]

    snap = read_dewetron_ui_snapshot(FakeUi())
    assert snap["brand"] == "dewetron"
    assert snap["widgets"]["comboBox_DEW_MaxRefreshRate"] == "200"
    assert snap["widgets"]["dew_wiring_type"] == 0
