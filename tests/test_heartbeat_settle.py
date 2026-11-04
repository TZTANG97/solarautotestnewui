# -*- coding: utf-8 -*-
"""心跳结案兜底：成功或云端已终态后不再重复，并上传已有文件。"""
from __future__ import annotations

import json
from pathlib import Path

from agent.heartbeat_settle import (
    HeartbeatSettleState,
    apply_heartbeat_terminal_settle,
    note_job_status,
)


class _Client:
    def __init__(self, status: str = "running", fail_done: int = 0):
        self.default_status = status
        self.status_by_job: dict[int, str] = {}
        self.fail_done = fail_done
        self.gets = 0
        self.done_calls = []
        self.uploads = []

    def get_job(self, job_id: int):
        self.gets += 1
        jid = int(job_id)
        return {"id": jid, "status": self.status_by_job.get(jid, self.default_status)}

    def done(self, job_id: int, **kwargs):
        jid = int(job_id)
        self.done_calls.append((jid, kwargs))
        if self.fail_done:
            self.fail_done -= 1
            raise RuntimeError("down")
        self.status_by_job[jid] = str(kwargs.get("status") or "success")
        return {"code": 0}

    def upload_report(self, job_id: int, file_path: str, filename=None):
        self.uploads.append((int(job_id), str(file_path)))
        return {"filename": filename or Path(file_path).name}


def _snap(status: str = "已结束", job_id: int = 70) -> dict:
    return {
        "status": status,
        "jobId": job_id,
        "progress": 100,
        "elapsed_s": 31,
        "current_test": "动态QU",
    }


def _plant(root: Path) -> Path:
    (root / "status.json").write_text(
        json.dumps({"project": {"status": "已结束", "jobId": 70, "progress": 100}}),
        encoding="utf-8",
    )
    folder = root / "command_save_files" / "command_data"
    folder.mkdir(parents=True)
    csv = folder / "QU_dyn_curve.csv"
    csv.write_text("t,q\n1,2\n", encoding="utf-8")
    (folder / "other_job.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    return csv


def test_stale_abort_does_not_settle_before_run_seen(tmp_path: Path) -> None:
    """重启后文件仍是已中止，新任务号刚写上时不能结成台架状态=已中止。"""
    client = _Client(status="running")
    state = HeartbeatSettleState()
    snap = _snap("已中止", 82)
    snap["progress"] = 8
    snap["current_detail"] = "软件已重新打开，上次未跑完的试验已标为中止"
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=82, run_snapshot=snap, state=state
    )
    assert client.done_calls == []


def test_handoff_settle_only_after_this_job_was_running() -> None:
    from agent.heartbeat_settle import heartbeat_should_settle_terminal

    assert heartbeat_should_settle_terminal(
        status="已结束", settle_terminal=False, seen_running=False
    ) is False
    assert heartbeat_should_settle_terminal(
        status="已结束", settle_terminal=False, seen_running=True
    ) is True
    assert heartbeat_should_settle_terminal(
        status="进行中", settle_terminal=True, seen_running=True
    ) is False


def test_publish_terminal_result_unblocks_wait(tmp_path: Path) -> None:
    from agent.heartbeat_settle import publish_terminal_result_if_missing
    from agent.job_inbox import result_path

    assert publish_terminal_result_if_missing(tmp_path, 88, "已结束") is True
    data = json.loads(result_path(tmp_path, 88).read_text(encoding="utf-8"))
    assert data["status"] == "success"
    assert publish_terminal_result_if_missing(tmp_path, 88, "已结束") is False


def test_abort_after_running_still_settles(tmp_path: Path) -> None:
    client = _Client(status="running")
    state = HeartbeatSettleState()
    note_job_status(state, 82, "进行中")
    snap = _snap("已中止", 82)
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=82, run_snapshot=snap, state=state
    )
    assert len(client.done_calls) == 1
    assert client.done_calls[0][1]["status"] == "aborted"
    assert client.done_calls[0][1]["fail_reason"] == "台架状态=已中止"


def test_done_once_then_skip(tmp_path: Path) -> None:
    csv = _plant(tmp_path)
    client = _Client(status="running")
    state = HeartbeatSettleState()
    snap = _snap()
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=snap, state=state
    )
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=snap, state=state
    )
    assert len(client.done_calls) == 1
    assert client.gets == 1
    assert client.done_calls[0][1]["status"] == "success"
    names = [item["name"] for item in client.done_calls[0][1]["report_meta"]]
    assert "QU_dyn_curve.csv" in names
    assert "other_job.csv" not in names
    uploaded = [Path(p).name for _, p in client.uploads]
    assert uploaded.count("QU_dyn_curve.csv") == 1
    assert Path(client.uploads[0][1]).name
    assert csv.name in uploaded


def test_cloud_terminal_does_not_post_done_but_uploads_once(tmp_path: Path) -> None:
    _plant(tmp_path)
    client = _Client(status="success")
    state = HeartbeatSettleState()
    snap = _snap()
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=snap, state=state
    )
    uploads_after_first = len(client.uploads)
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=snap, state=state
    )
    assert client.done_calls == []
    assert client.gets == 1
    assert uploads_after_first >= 1
    assert len(client.uploads) == uploads_after_first
    assert "QU_dyn_curve.csv" in [Path(p).name for _, p in client.uploads]


def test_failed_done_retries_then_stops(tmp_path: Path) -> None:
    _plant(tmp_path)
    client = _Client(status="running", fail_done=1)
    state = HeartbeatSettleState()
    snap = _snap()
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=snap, state=state
    )
    assert len(client.done_calls) == 1
    assert client.uploads == []
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=snap, state=state
    )
    assert len(client.done_calls) == 2
    assert client.uploads
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=snap, state=state
    )
    assert len(client.done_calls) == 2


def test_other_job_still_settles(tmp_path: Path) -> None:
    _plant(tmp_path)
    client = _Client(status="running")
    state = HeartbeatSettleState()
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=_snap(), state=state
    )
    apply_heartbeat_terminal_settle(
        client,
        repo_root=tmp_path,
        job_id=71,
        run_snapshot=_snap(job_id=71),
        state=state,
    )
    assert [jid for jid, _ in client.done_calls] == [70, 71]


def test_empty_files_retries_before_giving_up(tmp_path: Path) -> None:
    """录波未落盘时前几次心跳不得永久放弃上传。"""
    (tmp_path / "status.json").write_text(
        json.dumps({"project": {"status": "已结束", "jobId": 88, "progress": 100}}),
        encoding="utf-8",
    )
    # 故意不放任何可上传文件（status.json 在 collect 里有，这里测「仅快照」仍会上传；
    # 用空目录 + 删掉 status 路径不可行。改为：有 status 但无实质 CSV 时不标记 finished）
    client = _Client(status="running")
    state = HeartbeatSettleState()
    snap = {
        "status": "已结束",
        "jobId": 88,
        "progress": 100,
        "elapsed_s": 10,
        "current_test": "静态QU",
    }
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=88, run_snapshot=snap, state=state
    )
    assert 88 not in state.reports_finished
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=88, run_snapshot=snap, state=state
    )
    assert 88 not in state.reports_finished
    # 第 3 次仍无实质文件才放弃
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=88, run_snapshot=snap, state=state
    )
    assert 88 in state.reports_finished


def test_staticqu_collects_qu_curve_from_wt_save(tmp_path: Path) -> None:
    (tmp_path / "status.json").write_text(
        json.dumps({"project": {"status": "已结束", "jobId": 77, "progress": 100}}),
        encoding="utf-8",
    )
    wt = tmp_path / "wt_save"
    wt.mkdir(parents=True)
    csv = wt / "QU_curve.csv"
    csv.write_text("t,U,Q\n1,230,0\n", encoding="utf-8")
    client = _Client(status="running")
    state = HeartbeatSettleState()
    snap = {
        "status": "已结束",
        "jobId": 77,
        "progress": 100,
        "elapsed_s": 420,
        "current_test": "静态QU",
    }
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=77, run_snapshot=snap, state=state
    )
    uploaded = [Path(p).name for _, p in client.uploads]
    assert "QU_curve.csv" in uploaded
    # 正式 CSV 应先于 status.json
    assert uploaded.index("QU_curve.csv") < uploaded.index("status.json")


def test_running_status_is_not_settled(tmp_path: Path) -> None:
    _plant(tmp_path)
    client = _Client(status="running")
    state = HeartbeatSettleState()
    note_job_status(state, 70, "进行中")
    apply_heartbeat_terminal_settle(
        client,
        repo_root=tmp_path,
        job_id=70,
        run_snapshot=_snap(status="进行中"),
        state=state,
    )
    assert client.done_calls == []
    assert client.uploads == []
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=_snap(), state=state
    )
    assert len(client.done_calls) == 1


def test_back_to_running_clears_settled_memory(tmp_path: Path) -> None:
    _plant(tmp_path)
    client = _Client(status="running")
    state = HeartbeatSettleState()
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=_snap(), state=state
    )
    note_job_status(state, 70, "进行中")
    client.status_by_job[70] = "running"
    apply_heartbeat_terminal_settle(
        client, repo_root=tmp_path, job_id=70, run_snapshot=_snap(), state=state
    )
    assert len(client.done_calls) == 2
