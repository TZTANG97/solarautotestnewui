# -*- coding: utf-8 -*-
"""桌面先追加，再从 IOT 追加：命令必须接在原队列后面。"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from utils.append_mode import apply_append_mode, commit_append_if_success
from utils.iot_ui_handoff import IotUiHandoffService
from utils.test_queue_markers import is_queue_end_row


def _bench(tmp_path: Path, *, queue, running: bool, project_now: str = "谐波电流"):
    g = {
        "strArrayTest": list(queue),
        "strArrayTestStep": [],
        "strAddTestFlag": "1",
        "project_change": "0",
        "project_now": project_now,
        "strSettingTestFlag": "1",
        "test_program": [],
        "total_save_file": 1,
        "wt_config_nums": 1,
    }
    fake = SimpleNamespace(
        strArrayTest=g["strArrayTest"],
        strTestStatusFlag="运行" if running else "",
        _iot_ui_handoff_svc=None,
    )
    calls = {"wipe": 0, "start": 0, "append": 0}

    def wipe():
        calls["wipe"] += 1
        g["strArrayTest"].clear()
        fake.strArrayTest = g["strArrayTest"]

    def append():
        calls["append"] += 1
        had = bool(g["strArrayTest"])
        flag, change, _label = apply_append_mode(
            g, project_name="电压闪变", local_count=0
        )
        if had:
            assert (flag, change) == ("1", "1")
        else:
            assert flag == "0"
        g["strArrayTest"].append(["AC", "write", "IOT-FLICKER"])
        g["strSettingTestFlag"] = "1"
        commit_append_if_success(g, "电压闪变", "0")
        fake.strArrayTest = g["strArrayTest"]

    def start():
        calls["start"] += 1

    calls["append_fn"] = append

    pending = tmp_path / "pending" / "job_77.json"
    pending.parent.mkdir(parents=True, exist_ok=True)
    pending.write_text("{}", encoding="utf-8")
    svc = IotUiHandoffService(
        repo_root=tmp_path,
        resolve_overload_ui=lambda: object(),
        overload_append=append,
        start_test=start,
        reset_append_count=wipe,
        get_run_status=lambda: "进行中" if running else "待开始",
        log=lambda _m: None,
        ensure_ready=None,
    )
    svc._job_ctx = {
        "job": {"id": 77, "testType": "flicker"},
        "pending_path": pending,
        "job_id": 77,
        "test_type": "flicker",
        "handler": {
            "append": append,
            "label": "电压闪变",
            "key": "flicker",
            "project_name": "电压闪变",
        },
        "real_ui": object(),
        "missing": [],
        "auto_append": True,
        "auto_start": True,
        "wait_finish": True,
        "params": {"auto_append": True, "auto_start": True},
        "widgets": {},
    }
    return g, fake, calls, svc, pending


def _result(tmp_path: Path) -> dict:
    path = tmp_path / "iot_job_inbox" / "results" / "job_77.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_desktop_append_then_iot_append_keeps_both(tmp_path, monkeypatch):
    """未开跑：桌面谐波命令还在，IOT 闪变接在后面，并开始这一条合并队列。"""
    g, fake, calls, svc, _pending = _bench(
        tmp_path,
        queue=[["AC", "write", "DESKTOP-HARM"]],
        running=False,
    )
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake)
    svc._continue_job_after_connect(None)

    assert calls["wipe"] == 0
    assert calls["append"] == 1
    assert calls["start"] == 1
    bodies = [
        row[2]
        for row in g["strArrayTest"]
        if len(row) > 2 and not is_queue_end_row(row)
    ]
    assert "DESKTOP-HARM" in bodies
    assert "IOT-FLICKER" in bodies
    assert is_queue_end_row(g["strArrayTest"][-1])
    assert g["project_now"] == "电压闪变"
    assert svc._awaiting is not None
    assert svc._awaiting["appended"] is True


def test_desktop_running_then_iot_append_joins_queue(tmp_path, monkeypatch):
    """已在跑：IOT 再追加只进队列，不清空、不二次开始、不新开等待结案。"""
    g, fake, calls, svc, _pending = _bench(
        tmp_path,
        queue=[["AC", "write", "DESKTOP-HARM"]],
        running=True,
    )
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake)
    svc._continue_job_after_connect(None)

    assert calls["wipe"] == 0
    assert calls["append"] == 1
    assert calls["start"] == 0
    bodies = [row[2] for row in g["strArrayTest"] if len(row) > 2]
    assert bodies[0] == "DESKTOP-HARM"
    assert "IOT-FLICKER" in bodies
    assert svc._awaiting is None
    assert svc._busy is False
    result = _result(tmp_path)
    assert result["status"] == "success"
    assert result["result_summary"]["joined_running_queue"] is True
    assert result["result_summary"]["started"] is False


class _Ui:
    pass


def _run_handle(tmp_path, monkeypatch, *, queue, flag, progress, params, job_id=88):
    """从 _handle_job 进，覆盖改绑任务号和缺省自动开始。"""
    g, fake, calls, svc, pending = _bench(
        tmp_path,
        queue=queue,
        running=flag in ("运行", "暂停"),
    )
    fake.strTestStatusFlag = flag
    pending.unlink()
    inbox_pending = tmp_path / "iot_job_inbox" / "pending" / f"job_{job_id}.json"
    inbox_pending.parent.mkdir(parents=True, exist_ok=True)
    job = {
        "id": job_id,
        "testType": "flicker",
        "params": params,
    }
    inbox_pending.write_text(json.dumps(job), encoding="utf-8")
    adopted = []

    def adopt(jid, exper_id=None):
        adopted.append((jid, exper_id))

    monkeypatch.setattr("utils.iot_local_run.adopt_cloud_job", adopt)
    monkeypatch.setattr("agent.ui_mutex.ui_try_acquire", lambda *a, **k: True)
    monkeypatch.setattr("agent.ui_mutex.ui_release", lambda *a, **k: None)
    monkeypatch.setattr(
        "utils.iot_bench_prefs.update_and_push", lambda patch: patch, raising=False
    )
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake)
    svc.get_run_status = lambda: progress
    svc.resolve_flicker_ui = lambda: _Ui()
    svc.flicker_append = calls["append_fn"]
    svc._job_ctx = None
    svc._handle_job(job, inbox_pending)
    return g, calls, adopted, svc


def test_handle_job_progress_ahead_of_flag_does_not_rebind(tmp_path, monkeypatch):
    """进度已是进行中、执行标志还空：不得改绑任务号，也不得再点开始。"""
    g, calls, adopted, svc = _run_handle(
        tmp_path,
        monkeypatch,
        queue=[["AC", "write", "DESKTOP-HARM"]],
        flag="",
        progress="进行中",
        params={"auto_append": True, "auto_start": True, "widgets": {}},
    )
    assert adopted == []
    assert calls["wipe"] == 0
    assert calls["append"] == 1
    assert calls["start"] == 0
    assert "DESKTOP-HARM" in [row[2] for row in g["strArrayTest"] if len(row) > 2]
    assert "IOT-FLICKER" in [row[2] for row in g["strArrayTest"] if len(row) > 2]
    assert svc._busy is False
    assert svc._job_ctx is None
    result = json.loads(
        (tmp_path / "iot_job_inbox" / "results" / "job_88.json").read_text(encoding="utf-8")
    )
    assert result["result_summary"]["joined_running_queue"] is True


def test_handle_job_omitted_auto_start_still_starts(tmp_path, monkeypatch):
    """参数没写 auto_start：与网页默认一致，空队列覆盖后开始。"""
    _g, calls, adopted, svc = _run_handle(
        tmp_path,
        monkeypatch,
        queue=[],
        flag="",
        progress="待开始",
        params={"auto_append": True, "widgets": {}},
        job_id=89,
    )
    assert adopted == [(89, None)]
    assert calls["wipe"] == 1
    assert calls["append"] == 1
    assert calls["start"] == 1
    assert svc._awaiting is not None
    assert svc._awaiting["job_id"] == 89


def test_empty_queue_iot_start_still_wipes(tmp_path, monkeypatch):
    """队列已空时，IOT 自动开始仍先覆盖，避免残留计数叠第二套。"""
    g, fake, calls, svc, _pending = _bench(tmp_path, queue=[], running=False, project_now="")
    monkeypatch.setitem(__import__("sys").modules, "SCPITestWave", fake)
    svc._continue_job_after_connect(None)
    assert calls["wipe"] == 1
    assert calls["append"] == 1
    assert calls["start"] == 1
    assert g["strArrayTest"] == [] or any(
        len(row) > 2 and row[2] == "IOT-FLICKER" for row in g["strArrayTest"]
    )
