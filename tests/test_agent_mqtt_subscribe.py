# -*- coding: utf-8 -*-
"""MQTT 命令订阅：startexper 入队。"""
from __future__ import annotations

import json
from types import SimpleNamespace

from agent import mqtt_subscribe


def test_startexper_message_enqueued(monkeypatch):
    # 清空队列
    with mqtt_subscribe._lock:
        mqtt_subscribe._pending.clear()
    mqtt_subscribe.set_job_handler(None)

    payload = {
        "type": "startexper",
        "id": 77,
        "experid": "1001",
        "testType": "dccomponent",
        "title": "直流分量",
    }
    msg = SimpleNamespace(
        payload=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        topic="/EquCommand/SOLAR-PC-ABC",
    )
    mqtt_subscribe._on_message(None, None, msg)
    job = mqtt_subscribe.pop_pending_job()
    assert job is not None
    assert job["id"] == 77
    assert job["testType"] == "dccomponent"
    assert mqtt_subscribe.pop_pending_job() is None


def test_non_startexper_ignored():
    with mqtt_subscribe._lock:
        mqtt_subscribe._pending.clear()
    mqtt_subscribe.set_job_handler(None)
    msg = SimpleNamespace(
        payload=json.dumps({"type": "probe", "id": 1}).encode("utf-8"),
        topic="/EquCommand/x",
    )
    mqtt_subscribe._on_message(None, None, msg)
    assert mqtt_subscribe.pop_pending_job() is None
