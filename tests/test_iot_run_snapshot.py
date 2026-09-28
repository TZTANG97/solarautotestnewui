# -*- coding: utf-8 -*-
"""本机进度 → heartbeat.runSnapshot。"""
from __future__ import annotations

import json
from pathlib import Path

from utils.iot_run_snapshot import build_run_snapshot_from_status, snapshot_implies_busy


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
