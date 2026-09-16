# -*- coding: utf-8 -*-
"""handoff：pending → Append/Start → progress → 等结束 → results。"""
from __future__ import annotations

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
            ),
            get_run_status=lambda: run_status["v"],
            get_run_progress=lambda: dict(run_prog),
            log=lambda m: print("ui:", m),
            interval_ms=200,
        )
        svc.poll_once()
        time.sleep(0.25)
        # 模拟进度刷新
        run_prog["percent"] = 70
        run_prog["text"] = "进行中 采集"
        svc.poll_once()
        time.sleep(0.2)
        run_status["v"] = "已结束"
        run_prog["percent"] = 100
        run_prog["text"] = "已结束"
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
    )
    h = svc._resolve_handler("antibackflow")
    assert h and h["project_name"] == "防逆流测试"
    h2 = svc._resolve_handler("防逆流测试")
    assert h2 and h2["label"] == "防逆流"
    print("antibackflow map PASS")


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
            ),
            get_run_status=lambda: run_status["v"],
            get_run_progress=lambda: dict(run_prog),
            log=lambda m: print("ui:", m),
            interval_ms=200,
        )
        svc.poll_once()
        time.sleep(0.25)
        run_prog["percent"] = 70
        run_prog["text"] = "进行中 采集"
        svc.poll_once()
        time.sleep(0.2)
        run_status["v"] = "已结束"
        run_prog["percent"] = 100
        run_prog["text"] = "已结束"
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
