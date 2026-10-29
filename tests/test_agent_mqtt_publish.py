# -*- coding: utf-8 -*-
"""Solar Agent MQTT 上行报文。"""
from __future__ import annotations

from agent.mqtt_publish import (
    build_exper_auto_end_payload,
    build_experdata_payload,
    mqtt_config_from_dict,
    resolve_publish_topic,
)


def test_experdata_payload_shape():
    payload = build_experdata_payload(
        pythonid="SOLAR-PC-ABC",
        job_id=42,
        progress_percent=55,
        progress_text="直流分量 100%Pn",
        current_step="S3",
        exper_id="1001",
    )
    assert payload["type"] == "SolarEquipment_experdata_return"
    assert payload["pythonid"] == "SOLAR-PC-ABC"
    assert payload["experid"] == "42"
    assert payload["equs"][0]["progress_percent"] == 55
    assert payload["equs"][0]["experId"] == "1001"
    assert payload["equs"][0]["channel"] == "solar"
    assert resolve_publish_topic("/EquMessage", "SOLAR-PC-ABC") == "/EquMessage/SOLAR-PC-ABC"


def test_mqtt_config_from_nested():
    cfg = mqtt_config_from_dict(
        {
            "mqtt": {
                "enable": True,
                "host": "www.laidecloud.com",
                "port": 11883,
                "username": "mqtt_ops",
            }
        }
    )
    assert cfg.enable is True
    assert cfg.host == "www.laidecloud.com"
    assert cfg.port == 11883
    assert cfg.username == "mqtt_ops"


def test_auto_end_payload_and_command_topic():
    end = build_exper_auto_end_payload(
        pythonid="SOLAR-PC-ABC",
        job_id=9,
        status="OK",
        fail_reason="",
    )
    assert end["type"] == "SolarEquipment_experautoend_return"
    assert end["channel"] == "solar"
    assert end["experid"] == "9"
    assert end["status"] == "OK"
    # 下发命令主题与温箱一致
    assert f"/EquCommand/{end['pythonid']}" == "/EquCommand/SOLAR-PC-ABC"
