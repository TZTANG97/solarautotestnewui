# -*- coding: utf-8 -*-
from utils.iot_force_overwrite_append import (
    force_overwrite_before_iot_append,
    should_force_overwrite_for_iot_job,
)


def test_only_append_skips_force_wipe():
    assert should_force_overwrite_for_iot_job(auto_start=False) is False
    assert should_force_overwrite_for_iot_job(auto_start=True) is True


def test_force_overwrite_calls_reset():
    called = {"n": 0}
    logs = []

    def reset():
        called["n"] += 1

    ok = force_overwrite_before_iot_append(reset_count=reset, log=logs.append)
    assert ok is True
    assert called["n"] == 1
    assert any("强制覆盖" in m for m in logs)


def test_force_overwrite_without_callback():
    logs = []
    ok = force_overwrite_before_iot_append(reset_count=None, log=logs.append)
    assert ok is False
    assert any("未绑定" in m for m in logs)


def test_force_overwrite_reset_raises():
    logs = []

    def reset():
        raise RuntimeError("boom")

    ok = force_overwrite_before_iot_append(reset_count=reset, log=logs.append)
    assert ok is False
    assert any("失败" in m for m in logs)
