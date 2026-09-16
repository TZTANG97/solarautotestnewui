# -*- coding: utf-8 -*-
"""stop_requests 收件箱：write / list / ack。"""
from __future__ import annotations

import json
from pathlib import Path

from agent.job_inbox import (
    ack_stop_request,
    list_stop_requests,
    wait_result,
    write_stop_request,
)


def test_write_list_ack_stop_request(tmp_path: Path) -> None:
    root = Path(tmp_path)
    path = write_stop_request(root, 42, reason="运维网页手动中止")
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["job_id"] == 42
    assert "运维" in data["reason"]

    listed = list_stop_requests(root)
    assert len(listed) == 1
    assert listed[0]["job_id"] == 42

    assert ack_stop_request(root, 42) is True
    assert list_stop_requests(root) == []
    done = root / "iot_job_inbox" / "stop_requests" / "done" / "job_42.json"
    assert done.is_file()
    assert ack_stop_request(root, 42) is False


def test_wait_result_abort_check(tmp_path: Path) -> None:
    root = Path(tmp_path)
    calls = {"n": 0}

    def abort_check():
        calls["n"] += 1
        if calls["n"] >= 2:
            return "云端已中止"
        return None

    data = wait_result(
        root,
        77,
        timeout_sec=5,
        poll_sec=0.05,
        abort_check=abort_check,
    )
    assert data is not None
    assert data.get("_remote_abort") is True
    assert data.get("status") == "aborted"
    assert "中止" in (data.get("fail_reason") or "")
    assert calls["n"] >= 2
