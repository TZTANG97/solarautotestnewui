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


if __name__ == "__main__":
    test_handoff_roundtrip()
    test_antibackflow_handler_maps()
