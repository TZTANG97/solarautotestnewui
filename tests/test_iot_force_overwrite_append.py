# -*- coding: utf-8 -*-
from utils.iot_force_overwrite_append import (
    coerce_auto_append,
    coerce_auto_start,
    force_overwrite_before_iot_append,
    should_force_overwrite_for_iot_job,
)


def test_missing_auto_start_matches_web_default():
    assert coerce_auto_start({}) is True
    assert coerce_auto_start(None) is True
    assert coerce_auto_start({"auto_append": True}) is True
    assert coerce_auto_start({"auto_start": False}) is False
    assert coerce_auto_start({"auto_start": True}) is True


def test_experiment_start_forces_auto_start_and_append():
    poisoned = {
        "source": "experiment_start",
        "auto_start": False,
        "auto_append": False,
    }
    assert coerce_auto_start(poisoned) is True
    assert coerce_auto_append(poisoned) is True
    assert coerce_auto_append({"auto_append": False}) is False
    assert coerce_auto_append({}) is True


def test_only_append_skips_force_wipe():
    assert should_force_overwrite_for_iot_job(auto_start=False) is False
    assert should_force_overwrite_for_iot_job(auto_start=True) is True


def test_desktop_running_never_force_wipes():
    assert should_force_overwrite_for_iot_job(auto_start=True, desktop_running=True) is False
    assert should_force_overwrite_for_iot_job(auto_start=False, desktop_running=True) is False


def test_desktop_queue_blocks_wipe_even_if_auto_start():
    """桌面已追加、尚未开跑：IOT 再追加不得清队列。"""
    assert (
        should_force_overwrite_for_iot_job(
            auto_start=True, desktop_running=False, queue_nonempty=True
        )
        is False
    )
    assert (
        should_force_overwrite_for_iot_job(
            auto_start=True, desktop_running=False, queue_nonempty=False
        )
        is True
    )


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
