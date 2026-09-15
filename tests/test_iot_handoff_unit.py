# -*- coding: utf-8 -*-
"""handoff：pending →（模拟 UI）→ results → Agent wait_result。"""
from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.job_inbox import wait_result, write_pending_job
from agent.runners.overload import OverloadRunner
from utils.iot_ui_handoff import IotUiHandoffService


def test_handoff_roundtrip(tmp_path: Path | None = None) -> None:
    root = Path(tmp_path) if tmp_path else ROOT / "iot_job_inbox" / "_test_handoff_workspace"
    if root.exists():
        import shutil

        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    # 把 inbox 建在 root 下：修改 OverloadRunner repo_root
    job = {
        "id": 9001,
        "testType": "overload",
        "title": "handoff-unit",
        "params": {"widgets": {}, "auto_append": True, "e2e": True},
    }
    write_pending_job(root, job)

    released = {"ok": False}

    def release():
        released["ok"] = True

    runner = OverloadRunner(execution_mode="handoff", repo_root=root)
    runner.set_release_for_ui(release)

    progress = []

    def on_progress(p, t, s):
        progress.append((p, t, s))

    def ui_side():
        time.sleep(0.5)
        svc = IotUiHandoffService(
            repo_root=root,
            resolve_overload_ui=lambda: type("U", (), {})(),
            overload_append=lambda: None,
            log=lambda m: print("ui:", m),
            interval_ms=500,
        )
        # 直接处理一次，不启 timer
        svc.poll_once()

    th = threading.Thread(target=ui_side, daemon=True)
    th.start()
    result = runner.run(job, on_progress)
    th.join(timeout=10)
    assert released["ok"], "应释放 agent 锁"
    assert result["status"] == "success", result
    print("handoff unit PASS", result.get("result_summary"))


if __name__ == "__main__":
    test_handoff_roundtrip()
