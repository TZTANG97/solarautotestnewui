# -*- coding: utf-8 -*-
from utils.run_progress_eta import (
    build_progress_summary,
    compute_eta,
    estimate_planned_seconds,
    format_duration,
)


def test_format_duration():
    assert format_duration(12) == "约 12 秒"
    assert "分" in format_duration(95)
    assert "小时" in format_duration(3700)


def test_estimate_planned_from_wait_cols():
    cmds = [
        ["AC", "write", "FREQ 50", "", "", "", "", "", 10, ""],  # 1.0s
        ["AC", "write", "OUTP ON", "", "", "", "", "", "", 20],  # 2.0s
        ["Upper_WT_Config", "", "", "", {}],
    ]
    secs = estimate_planned_seconds(cmds)
    assert secs >= 1.0 + 2.0 + 75.0


def test_compute_eta_blends_plan_and_progress():
    eta = compute_eta(
        elapsed_s=60,
        progress_pct=50,
        planned_total_s=200,
        cmd_index=50,
        cmd_total=100,
    )
    assert eta["remain_s"] > 0
    assert "remain_text" in eta
    assert eta["elapsed_s"] == 60


def test_build_progress_summary_multiline():
    state = {
        "project": "巴西过欠频稳定性",
        "status": "进行中",
        "progress": 40,
        "current_round": 1,
        "total_rounds": 1,
        "cmd_index": 40,
        "cmd_total": 100,
        "current_detail": "[AC] write FREQ 50.2",
    }
    eta = compute_eta(
        elapsed_s=120, progress_pct=40, planned_total_s=300, cmd_index=40, cmd_total=100
    )
    text = build_progress_summary(state, eta=eta)
    assert "巴西过欠频稳定性" in text
    assert "剩余" in text
    assert "当前步骤" in text
    assert "队列" in text or "FREQ" in text


def test_build_progress_summary_queue():
    state = {
        "project": "叠加",
        "status": "进行中",
        "progress": 20,
        "current_round": 1,
        "total_rounds": 2,
        "cmd_index": 10,
        "cmd_total": 50,
        "current_detail": "AC OUTP ON",
        "current_test": "谐波电流",
        "queue": [
            {"name": "谐波电流", "status": "进行中", "pause_after": True},
            {"name": "过载", "status": "等待", "pause_after": False},
        ],
    }
    text = build_progress_summary(state, eta=None)
    assert "共 2 项试验" in text
    assert "谐波电流" in text
    assert "结束后暂停" in text
