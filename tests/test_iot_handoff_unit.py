# -*- coding: utf-8 -*-
"""handoff：pending → Append/Start → progress → 等结束 → results。"""
from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.job_inbox import read_progress
from agent.runners.overload import OverloadRunner
from utils.iot_ui_handoff import IotUiHandoffService


def test_handoff_roundtrip(tmp_path: Path | None = None) -> None:
    root = Path(tmp_path) if tmp_path else ROOT / "iot_job_inbox" / "_test_handoff_workspace"
    if root.exists():
        import shutil

        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    job = {
        "id": 9001,
        "testType": "overload",
        "title": "handoff-unit",
        "params": {
            "widgets": {},
            "auto_append": True,
            "auto_start": True,
            "start_grace_sec": 2,
            "wait_finish_timeout_sec": 30,
            "e2e": True,
        },
    }

    released = {"ok": False}
    started = {"ok": False}
    run_status = {"v": "未开始"}
    run_prog = {"percent": 0, "text": "未开始", "step": ""}

    def release():
        released["ok"] = True

    runner = OverloadRunner(execution_mode="handoff", repo_root=root)
    runner.set_release_for_ui(release)

    progress = []

    def on_progress(p, t, s):
        progress.append((p, t, s))

    def ui_side():
        time.sleep(0.4)
        svc = IotUiHandoffService(
            repo_root=root,
            resolve_overload_ui=lambda: type("U", (), {})(),
            overload_append=lambda: None,
            start_test=lambda: (
                started.__setitem__("ok", True),
                run_status.__setitem__("v", "进行中"),
                run_prog.__setitem__("percent", 40),
                run_prog.__setitem__("text", "进行中 S1"),
                run_prog.__setitem__("step", "进行中"),
                run_prog.__setitem__("cmd_index", 1),
                run_prog.__setitem__("cmd_total", 8),
            ),
            get_run_status=lambda: run_status["v"],
            get_run_progress=lambda: dict(run_prog),
            reset_append_count=lambda: None,
            log=lambda m: print("ui:", m),
            interval_ms=200,
        )
        svc.poll_once()
        time.sleep(0.25)
        # 模拟进度刷新
        run_prog["percent"] = 70
        run_prog["text"] = "进行中 采集"
        run_prog["cmd_index"] = 4
        svc.poll_once()
        time.sleep(0.2)
        run_status["v"] = "已结束"
        run_prog["percent"] = 100
        run_prog["text"] = "已结束"
        run_prog["cmd_index"] = 8
        svc.poll_once()

    th = threading.Thread(target=ui_side, daemon=True)
    th.start()
    result = runner.run(job, on_progress)
    th.join(timeout=15)
    assert released["ok"], "应释放 agent 锁"
    assert started["ok"], "auto_start=true 时应调用开始试验"
    assert result["status"] == "success", result
    summary = result.get("result_summary") or {}
    assert summary.get("waited_finish") is True, summary
    assert any(p[0] >= 40 for p in progress), progress
    prog_file = read_progress(root, 9001)
    assert prog_file is not None
    print("handoff unit PASS", summary, "progress_events=", len(progress))


def test_antibackflow_handler_maps() -> None:
    svc = IotUiHandoffService(
        resolve_antibackflow_ui=lambda: object(),
        antibackflow_append=lambda: None,
        resolve_overload_ui=lambda: object(),
        overload_append=lambda: None,
    )
    h = svc._resolve_handler("antibackflow")
    assert h and h["project_name"] == "防逆流测试"
    assert h.get("key") == "antibackflow"
    h2 = svc._resolve_handler("防逆流测试")
    assert h2 and h2["label"] == "防逆流"
    h3 = svc._resolve_handler("overload")
    assert h3 and h3.get("key") == "overload"
    print("antibackflow map PASS")


def test_stop_for_previous_job_does_not_fire_when_no_handoff(tmp_path: Path) -> None:
    """58 的停机在还没记上 59/60 时 current_job=0，不能去点结束试验。"""
    from agent.job_inbox import list_stop_requests, write_stop_request

    root = Path(tmp_path)
    write_stop_request(root, 58, reason="台架状态=已中止")
    (root / "status.json").write_text(
        json.dumps(
            {"project": {"status": "进行中", "jobId": 60, "progress": 2}},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    stopped = {"n": 0}
    logs: list[str] = []
    svc = IotUiHandoffService(
        repo_root=root,
        stop_test=lambda: stopped.__setitem__("n", stopped["n"] + 1),
        log=lambda m: logs.append(m),
        interval_ms=200,
    )
    svc.get_run_status = lambda: "进行中"
    svc.poll_once()
    assert stopped["n"] == 0
    assert list_stop_requests(root) == []
    assert any("忽略过期停机" in m and "58" in m for m in logs)


def test_awaiting_ignores_previous_job_terminal(tmp_path: Path) -> None:
    """status.json 还是 58 的已中止时，不能把 60 收成试验状态=已中止。"""
    root = Path(tmp_path)
    (root / "status.json").write_text(
        json.dumps(
            {
                "project": {
                    "status": "已中止",
                    "jobId": 58,
                    "progress": 2,
                    "current_detail": "本机无试验占用，收口陈旧进行中状态",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    finished: list[dict] = []
    svc = IotUiHandoffService(
        repo_root=root,
        log=lambda _m: None,
        interval_ms=200,
    )
    svc._finish_job = lambda **kw: finished.append(kw)  # type: ignore[method-assign]
    svc._awaiting = {
        "job_id": 60,
        "pending_path": None,
        "started_at": time.time() - 30,
        "start_grace_sec": 8,
        "seen_running": False,
    }
    svc.get_run_status = lambda: "已中止"
    svc._check_awaiting_finish()
    assert finished
    reason = str(finished[0]["result"].get("fail_reason") or "")
    assert "未进入" in reason
    assert "试验状态=已中止" not in reason


def test_stale_finished_without_running_is_failed_not_success(tmp_path: Path) -> None:
    """新任务号挂着上一单残留的「已结束」时，宽限后必须失败，不能秒成功。"""
    root = Path(tmp_path)
    (root / "status.json").write_text(
        json.dumps(
            {
                "project": {
                    "status": "已结束",
                    "jobId": 91,
                    "progress": 100,
                    "current_detail": "上一单残留",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    finished: list[dict] = []
    svc = IotUiHandoffService(
        repo_root=root,
        log=lambda _m: None,
        interval_ms=200,
    )
    svc._finish_job = lambda **kw: finished.append(kw)  # type: ignore[method-assign]
    svc._awaiting = {
        "job_id": 91,
        "pending_path": None,
        "started_at": time.time() - 30,
        "start_grace_sec": 8,
        "seen_running": False,
        "desktop_finished": False,
    }
    svc.get_run_status = lambda: "已结束"
    svc.get_run_progress = lambda: {"cmd_index": 0, "cmd_total": 0}
    svc._check_awaiting_finish()
    assert finished
    assert finished[0]["result"].get("status") == "failed"
    assert "未见命令真正执行" in str(finished[0]["result"].get("fail_reason") or "")


def test_optimistic_running_then_finish_without_cmd_is_failed(tmp_path: Path) -> None:
    """开始按钮先写进行中(cmd=0)再空跑已结束：不得 success。"""
    finished: list[dict] = []
    progress = {"cmd_index": 0, "cmd_total": 12}
    svc = IotUiHandoffService(
        repo_root=Path(tmp_path),
        log=lambda _m: None,
        interval_ms=200,
    )
    svc._finish_job = lambda **kw: finished.append(kw)  # type: ignore[method-assign]
    svc._awaiting = {
        "job_id": 95,
        "pending_path": None,
        "started_at": time.time() - 1,
        "start_grace_sec": 20,
        "seen_running": False,
        "desktop_finished": False,
        "max_cmd_index": 0,
        "max_cmd_total": 0,
    }
    svc.get_run_status = lambda: "进行中"
    svc.get_run_progress = lambda: dict(progress)
    svc._check_awaiting_finish()
    assert not finished
    assert svc._awaiting["seen_running"] is False

    svc.get_run_status = lambda: "已结束"
    svc._awaiting["started_at"] = time.time() - 30
    svc._check_awaiting_finish()
    assert finished
    assert finished[0]["result"].get("status") == "failed"


def test_real_finish_after_seen_running_still_success(tmp_path: Path) -> None:
    """这一单真执行过命令再「已结束」，仍应收成 success。"""
    root = Path(tmp_path)
    finished: list[dict] = []
    svc = IotUiHandoffService(
        repo_root=root,
        log=lambda _m: None,
        interval_ms=200,
    )
    svc._finish_job = lambda **kw: finished.append(kw)  # type: ignore[method-assign]
    svc._awaiting = {
        "job_id": 92,
        "pending_path": None,
        "started_at": time.time() - 120,
        "start_grace_sec": 8,
        "seen_running": True,
        "desktop_finished": True,
        "max_cmd_index": 3,
        "max_cmd_total": 10,
    }
    svc.get_run_status = lambda: "已结束"
    svc.get_run_progress = lambda: {"cmd_index": 10, "cmd_total": 10}
    svc._check_awaiting_finish()
    assert finished
    assert finished[0]["result"].get("status") == "success"


def test_stop_request_for_other_job_does_not_stop_current(tmp_path: Path) -> None:
    """云端收口的上一单不能停掉正在跑的下一单（58 的停机掐掉 59/60）。"""
    from agent.job_inbox import list_stop_requests, write_stop_request

    root = Path(tmp_path)
    write_stop_request(root, 58, reason="台架状态=已中止")
    stopped = {"n": 0}
    logs: list[str] = []
    svc = IotUiHandoffService(
        repo_root=root,
        stop_test=lambda: stopped.__setitem__("n", stopped["n"] + 1),
        log=lambda m: logs.append(m),
        interval_ms=200,
    )
    svc._awaiting = {"job_id": 60, "started_at": time.time(), "start_grace_sec": 30}
    svc.get_run_status = lambda: "进行中"
    svc.poll_once()
    assert stopped["n"] == 0
    assert list_stop_requests(root) == []
    assert any("忽略过期停机" in m and "58" in m for m in logs)


def test_superseded_stop_does_not_stop_fresh_run(tmp_path: Path) -> None:
    """上一单的停机单不能在新开的电压闪变上再点一次结束。"""
    from agent.job_inbox import list_stop_requests, remember_superseded_job, write_stop_request

    root = Path(tmp_path)
    write_stop_request(root, 80, reason="台架本地中止")
    remember_superseded_job(root, 80)
    stopped = {"n": 0}
    logs: list[str] = []
    svc = IotUiHandoffService(
        repo_root=root,
        stop_test=lambda: stopped.__setitem__("n", stopped["n"] + 1),
        log=lambda m: logs.append(m),
        interval_ms=200,
    )
    svc.get_run_status = lambda: "进行中"
    svc.poll_once()
    assert stopped["n"] == 0
    assert list_stop_requests(root) == []
    assert any("上一单" in m and "80" in m for m in logs)


def test_mis_superseded_current_job_still_stops(tmp_path: Path) -> None:
    """开跑误把本单写入 superseded 后，IOT 中止当前任务仍必须停机。"""
    from agent.job_inbox import (
        is_superseded_job,
        list_stop_requests,
        remember_superseded_job,
        write_stop_request,
    )

    root = Path(tmp_path)
    write_stop_request(root, 106, reason="IOT中止")
    remember_superseded_job(root, 106)
    stopped = {"n": 0}
    logs: list[str] = []
    svc = IotUiHandoffService(
        repo_root=root,
        stop_test=lambda: stopped.__setitem__("n", stopped["n"] + 1),
        log=lambda m: logs.append(m),
        interval_ms=200,
    )
    svc._awaiting = {"job_id": 106, "started_at": time.time(), "start_grace_sec": 30}
    svc.get_run_status = lambda: "进行中"
    svc.poll_once()
    assert stopped["n"] == 1
    assert list_stop_requests(root) == []
    assert not is_superseded_job(root, 106)
    assert any("误标" in m and "106" in m for m in logs)


def test_stop_request_invokes_stop_test(tmp_path: Path) -> None:
    from agent.job_inbox import list_stop_requests, write_stop_request

    root = Path(tmp_path)
    write_stop_request(root, 9201, reason="单测远程停机")
    stopped = {"n": 0}
    logs: list[str] = []

    svc = IotUiHandoffService(
        repo_root=root,
        stop_test=lambda: stopped.__setitem__("n", stopped["n"] + 1),
        log=lambda m: logs.append(m),
        interval_ms=200,
    )
    svc._awaiting = {"job_id": 9201, "started_at": time.time(), "start_grace_sec": 30}
    svc.get_run_status = lambda: "进行中"
    svc.poll_once()
    assert stopped["n"] == 1
    assert list_stop_requests(root) == []
    assert any("远程停机" in m for m in logs)
    done = root / "iot_job_inbox" / "stop_requests" / "done" / "job_9201.json"
    assert done.is_file()


def test_handoff_abort_check_writes_stop(tmp_path: Path) -> None:
    """wait_result abort_check → OverloadRunner 写 stop_request 并返回 aborted。"""
    from agent.job_inbox import list_stop_requests

    root = Path(tmp_path)
    job = {
        "id": 9301,
        "testType": "overload",
        "title": "abort-unit",
        "params": {},
    }
    runner = OverloadRunner(execution_mode="handoff", repo_root=root)
    runner.set_abort_check(lambda: "运维网页手动中止")
    result = runner.run(job, lambda *a: None)
    assert result["status"] == "aborted"
    assert "本机关机" in (result.get("fail_reason") or "")
    listed = list_stop_requests(root)
    assert len(listed) == 1
    assert listed[0]["job_id"] == 9301


def test_antibackflow_handoff_roundtrip(tmp_path: Path | None = None) -> None:
    root = Path(tmp_path) if tmp_path else ROOT / "iot_job_inbox" / "_test_antibackflow_handoff_workspace"
    if root.exists():
        import shutil

        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    job = {
        "id": 9002,
        "testType": "antibackflow",
        "title": "antibackflow-handoff-unit",
        "params": {
            "widgets": {},
            "auto_append": True,
            "auto_start": True,
            "start_grace_sec": 2,
            "wait_finish_timeout_sec": 30,
            "e2e": True,
        },
    }

    released = {"ok": False}
    started = {"ok": False}
    run_status = {"v": "未开始"}
    run_prog = {"percent": 0, "text": "未开始", "step": ""}

    def release():
        released["ok"] = True

    runner = OverloadRunner(execution_mode="handoff", repo_root=root)
    runner.set_release_for_ui(release)

    progress = []

    def on_progress(p, t, s):
        progress.append((p, t, s))

    def ui_side():
        time.sleep(0.4)
        svc = IotUiHandoffService(
            repo_root=root,
            resolve_antibackflow_ui=lambda: type("U", (), {})(),
            antibackflow_append=lambda: None,
            start_test=lambda: (
                started.__setitem__("ok", True),
                run_status.__setitem__("v", "进行中"),
                run_prog.__setitem__("percent", 40),
                run_prog.__setitem__("text", "进行中 S1"),
                run_prog.__setitem__("step", "进行中"),
                run_prog.__setitem__("cmd_index", 1),
                run_prog.__setitem__("cmd_total", 6),
            ),
            get_run_status=lambda: run_status["v"],
            get_run_progress=lambda: dict(run_prog),
            reset_append_count=lambda: None,
            log=lambda m: print("ui:", m),
            interval_ms=200,
        )
        svc.poll_once()
        time.sleep(0.25)
        run_prog["percent"] = 70
        run_prog["text"] = "进行中 采集"
        run_prog["cmd_index"] = 3
        svc.poll_once()
        time.sleep(0.2)
        run_status["v"] = "已结束"
        run_prog["percent"] = 100
        run_prog["text"] = "已结束"
        run_prog["cmd_index"] = 6
        svc.poll_once()

    th = threading.Thread(target=ui_side, daemon=True)
    th.start()
    result = runner.run(job, on_progress)
    th.join(timeout=15)
    assert released["ok"], "应释放 agent 锁"
    assert started["ok"], "auto_start=true 时应调用开始试验"
    assert result["status"] == "success", result
    summary = result.get("result_summary") or {}
    assert summary.get("waited_finish") is True, summary
    assert any(p[0] >= 40 for p in progress), progress
    prog_file = read_progress(root, 9002)
    assert prog_file is not None
    print("antibackflow handoff unit PASS", summary, "progress_events=", len(progress))


def test_ensure_ready_fails_writes_failed(tmp_path: Path) -> None:
    root = Path(tmp_path)
    pending = root / "iot_job_inbox" / "pending"
    pending.mkdir(parents=True)
    job = {
        "id": 9101,
        "testType": "overload",
        "params": {"widgets": {}, "auto_append": True, "auto_start": False},
    }
    (pending / "job_9101.json").write_text(
        __import__("json").dumps({"job": job}, ensure_ascii=False),
        encoding="utf-8",
    )
    appended = {"n": 0}

    svc = IotUiHandoffService(
        repo_root=root,
        resolve_overload_ui=lambda: type("U", (), {})(),
        overload_append=lambda: appended.__setitem__("n", appended["n"] + 1),
        ensure_ready=lambda ui, tt: (False, "直流电源1厂家未识别（当前=空）；请先连接并识别厂家，禁止致茂IVC混用"),
        log=lambda m: None,
        interval_ms=200,
    )
    # bypass ui mutex for unit test
    import agent.ui_mutex as um

    um.ui_try_acquire = lambda **kw: True  # type: ignore
    um.ui_release = lambda **kw: None  # type: ignore
    svc.poll_once()
    result_path = root / "iot_job_inbox" / "results" / "job_9101.json"
    assert result_path.is_file(), "should write failed result"
    data = __import__("json").loads(result_path.read_text(encoding="utf-8"))
    body = data.get("result") or data
    assert body.get("status") == "failed"
    assert "厂家未识别" in (body.get("fail_reason") or "")
    assert appended["n"] == 0


def test_append_brand_qmessage_fails(tmp_path: Path) -> None:
    from PyQt5.QtWidgets import QMessageBox

    root = Path(tmp_path)
    pending = root / "iot_job_inbox" / "pending"
    pending.mkdir(parents=True)
    job = {
        "id": 9102,
        "testType": "overload",
        "params": {"widgets": {}, "auto_append": True, "auto_start": False},
    }
    (pending / "job_9102.json").write_text(
        __import__("json").dumps({"job": job}, ensure_ascii=False),
        encoding="utf-8",
    )

    def _append_bad():
        QMessageBox.information(None, "错误", "厂家未知，赋值失败")

    svc = IotUiHandoffService(
        repo_root=root,
        resolve_overload_ui=lambda: type("U", (), {})(),
        overload_append=_append_bad,
        ensure_ready=lambda ui, tt: (True, ""),
        wrap_append_errors=True,
        log=lambda m: None,
        interval_ms=200,
    )
    import agent.ui_mutex as um

    um.ui_try_acquire = lambda **kw: True  # type: ignore
    um.ui_release = lambda **kw: None  # type: ignore

    # avoid real dialog
    QMessageBox.information = staticmethod(lambda *a, **k: QMessageBox.Ok)  # type: ignore

    svc.poll_once()
    result_path = root / "iot_job_inbox" / "results" / "job_9102.json"
    assert result_path.is_file()
    data = __import__("json").loads(result_path.read_text(encoding="utf-8"))
    body = data.get("result") or data
    assert body.get("status") == "failed"
    assert any(k in (body.get("fail_reason") or "") for k in ("厂家", "错误", "赋值"))

if __name__ == "__main__":
    test_handoff_roundtrip()
    test_antibackflow_handler_maps()
    test_antibackflow_handoff_roundtrip()
    # ensure_ready / QMessageBox cases need tmp_path; run via pytest
