# -*- coding: utf-8 -*-
"""本机进度 → heartbeat.runSnapshot。"""
from __future__ import annotations

import json
import time
from pathlib import Path

from utils.iot_run_snapshot import (
    build_run_snapshot_from_status,
    heartbeat_should_push_progress,
    snapshot_implies_busy,
)


def test_build_from_status_json(tmp_path: Path):
    p = tmp_path / "status.json"
    p.write_text(
        json.dumps(
            {
                "project": {
                    "name": "过载能力测试",
                    "status": "进行中",
                    "progress": 55,
                    "remain_text": "约 2 分",
                    "queue": [{"name": "电压闪变", "status": "等待"}],
                    "rounds": [{"index": 1, "filename": "x.csv", "status": "完成"}],
                    "jobId": 7,
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    snap = build_run_snapshot_from_status(str(p))
    assert snap["status"] == "进行中"
    assert snap["project"] == "过载能力测试"
    assert snap["progress"] == 55
    assert snap["remain_text"] == "约 2 分"
    assert snap["queue"][0]["name"] == "电压闪变"
    assert snap["jobId"] == 7
    assert snapshot_implies_busy(snap) is True


def test_idle_not_busy(tmp_path: Path):
    p = tmp_path / "status.json"
    p.write_text(
        json.dumps({"project": {"name": "", "status": "未开始", "progress": 0}}),
        encoding="utf-8",
    )
    snap = build_run_snapshot_from_status(str(p))
    assert snapshot_implies_busy(snap) is False


def test_missing_file_returns_idle():
    snap = build_run_snapshot_from_status(str(Path("/no/such/status.json")))
    assert snap["status"] == "未开始"
    assert snapshot_implies_busy(snap) is False


def test_fresh_progress_is_not_coerced_to_abort():
    """锁文件读不到时，刚写过的进行中不能收成已中止（任务 58 的误伤）。"""
    from utils.iot_run_snapshot import apply_unlocked_stale_policy

    snap = {"status": "进行中", "progress": 2, "jobId": 58, "updated_at": "2026-10-28 20:44:40"}
    now = time.mktime(time.strptime("2026-10-28 20:44:49", "%Y-%m-%d %H:%M:%S"))
    out, busy = apply_unlocked_stale_policy(
        snap, busy=False, owner="", now=now, max_age_sec=180
    )
    assert out["status"] == "进行中"
    assert busy is True
    assert out["progress"] == 2


def test_ui_lock_keeps_running_snapshot():
    from utils.iot_run_snapshot import apply_unlocked_stale_policy

    snap = {"status": "进行中", "progress": 2, "updated_at": "2020-01-01 00:00:00"}
    out, busy = apply_unlocked_stale_policy(
        snap, busy=False, owner="ui", now=time.time(), max_age_sec=180
    )
    assert out["status"] == "进行中"
    assert busy is True


def test_three_minute_gap_is_not_aborted():
    """任务 58：进度停在 2%，约 3 分钟没刷 updated_at，不能收成已中止。"""
    from utils.iot_run_snapshot import apply_unlocked_stale_policy

    snap = {
        "status": "进行中",
        "progress": 2,
        "jobId": 58,
        "updated_at": "2026-10-28 20:41:49",
    }
    now = time.mktime(time.strptime("2026-10-28 20:44:49", "%Y-%m-%d %H:%M:%S"))
    out, busy = apply_unlocked_stale_policy(snap, busy=False, owner="", now=now)
    assert out["status"] == "进行中"
    assert busy is True
    assert out["progress"] == 2


def test_stale_unlocked_snapshot_is_aborted_and_persisted(tmp_path: Path):
    from utils.iot_run_snapshot import apply_unlocked_stale_policy, persist_coerced_terminal

    snap = {
        "status": "进行中",
        "progress": 2,
        "jobId": 58,
        "updated_at": "2026-10-28 18:00:00",
    }
    now = time.mktime(time.strptime("2026-10-28 20:44:49", "%Y-%m-%d %H:%M:%S"))
    out, busy = apply_unlocked_stale_policy(
        snap, busy=False, owner="", now=now, max_age_sec=180
    )
    assert busy is False
    assert out["status"] == "已中止"
    assert "本机无试验占用" in out["current_detail"]
    path = tmp_path / "status.json"
    path.write_text(
        json.dumps({"devices": [], "project": {"status": "进行中", "progress": 2, "jobId": 58}}),
        encoding="utf-8",
    )
    persist_coerced_terminal(str(path), out)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["project"]["status"] == "已中止"
    assert saved["project"]["jobId"] == 58
    assert saved["project"]["progress"] == 2


def test_idle_append_does_not_push_progress_onto_previous_job():
    assert heartbeat_should_push_progress("进行中") is True
    assert heartbeat_should_push_progress("暂停") is True
    assert heartbeat_should_push_progress("待开始") is False
    assert heartbeat_should_push_progress("未开始") is False
