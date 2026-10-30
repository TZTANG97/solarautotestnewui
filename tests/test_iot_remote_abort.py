# -*- coding: utf-8 -*-
"""二期：本机开测局也能收到云端远程中止。"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from agent.remote_abort import (
    job_id_from_run_snapshot,
    local_still_running,
    reset_remote_abort_state,
    sync_cloud_abort_to_stop_inbox,
)


def test_local_still_running_states():
    assert local_still_running({"status": "进行中", "jobId": 1}) is True
    assert local_still_running({"status": "暂停", "jobId": 1}) is True
    assert local_still_running({"status": "已结束", "jobId": 1}) is False
    assert local_still_running({"status": "已中止", "jobId": 1}) is False
    assert job_id_from_run_snapshot({"jobId": "26"}) == 26


def test_sync_writes_stop_when_cloud_aborted(tmp_path: Path):
    reset_remote_abort_state()
    written = []

    def _get_job(_jid):
        return {"status": "aborted", "failReason": "运维网页手动中止"}

    def _write(root, job_id, reason=""):
        written.append((int(job_id), reason))
        p = Path(root) / f"stop_{job_id}.json"
        p.write_text("{}", encoding="utf-8")
        return p

    client = SimpleNamespace(get_job=_get_job)
    snap = {"jobId": 99, "status": "进行中"}
    got = sync_cloud_abort_to_stop_inbox(
        client=client,
        repo_root=tmp_path,
        run_snapshot=snap,
        get_job=_get_job,
        write_stop=_write,
    )
    assert got == 99
    assert written == [(99, "运维网页手动中止")]
    # 同 job 不重复写
    got2 = sync_cloud_abort_to_stop_inbox(
        client=client,
        repo_root=tmp_path,
        run_snapshot=snap,
        get_job=_get_job,
        write_stop=_write,
    )
    assert got2 is None
    assert len(written) == 1


def test_sync_skips_stale_snapshot_while_another_job_is_active(tmp_path: Path):
    reset_remote_abort_state()
    written = []

    def _get_job(_jid):
        return {"status": "aborted", "failReason": "云端已终止"}

    got = sync_cloud_abort_to_stop_inbox(
        client=SimpleNamespace(),
        repo_root=tmp_path,
        run_snapshot={"jobId": 58, "status": "进行中"},
        get_job=_get_job,
        write_stop=lambda *a, **k: written.append(1),
        active_job_id=61,
    )
    assert got is None
    assert written == []


def test_sync_skips_job_replaced_by_a_fresh_start(tmp_path: Path):
    """重新打开后上一单已在云端中止，不能再写成这一局的远程停机。"""
    reset_remote_abort_state()
    from agent.job_inbox import remember_superseded_job

    remember_superseded_job(tmp_path, 81)
    written = []

    def _get_job(_jid):
        return {"status": "aborted", "failReason": "台架本地中止"}

    got = sync_cloud_abort_to_stop_inbox(
        client=SimpleNamespace(),
        repo_root=tmp_path,
        run_snapshot={"jobId": 81, "status": "进行中"},
        get_job=_get_job,
        write_stop=lambda *a, **k: written.append(1),
    )
    assert got is None
    assert written == []


def test_sync_skips_when_not_aborted(tmp_path: Path):
    reset_remote_abort_state()
    written = []

    def _get_job(_jid):
        return {"status": "running"}

    got = sync_cloud_abort_to_stop_inbox(
        client=SimpleNamespace(),
        repo_root=tmp_path,
        run_snapshot={"jobId": 7, "status": "进行中"},
        get_job=_get_job,
        write_stop=lambda *a, **k: written.append(1),
    )
    assert got is None
    assert written == []
