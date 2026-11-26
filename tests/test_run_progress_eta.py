# -*- coding: utf-8 -*-
from datetime import datetime

from utils.run_progress_eta import (
    build_progress_summary,
    compute_eta,
    estimate_planned_seconds,
    format_duration,
    format_estimated_end_time,
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


def test_estimate_planned_start_index_skips_done_rows():
    cmds = [
        ["AC", "write", "A", "", "", "", "", "", 10, ""],  # 1s
        ["AC", "write", "B", "", "", "", "", "", "", 100],  # 10s
        ["AC", "write", "C", "", "", "", "", "", "", 200],  # 20s
    ]
    total = estimate_planned_seconds(cmds)
    remain = estimate_planned_seconds(cmds, start_index=1)
    # 后半（10+20）应远大于前半（1），且 remain ≈ total - first_row
    first = estimate_planned_seconds(cmds[:1])
    assert remain + first == total or abs((remain + first) - total) < 0.01
    assert remain > first * 5


def test_estimate_planned_includes_dewetron_io_overhead():
    cmds = [["DEWETRON", "write", "ACQUISITION:START", "", "", "", "", "", "", ""]]
    assert estimate_planned_seconds(cmds) >= 2.0


def test_compute_eta_uses_remaining_command_waits_not_linear():
    # 前 50 条几乎无等待，后 50 条很长 → 中点剩余应接近后半，而不是总计划一半
    cmds = []
    for _ in range(50):
        cmds.append(["AC", "write", "FAST", "", "", "", "", "", "", 1])  # 0.1s
    for _ in range(50):
        cmds.append(["AC", "write", "SLOW", "", "", "", "", "", "", 100])  # 10s
    planned = estimate_planned_seconds(cmds)
    eta = compute_eta(
        elapsed_s=10,
        progress_pct=50,
        planned_total_s=planned,
        cmd_index=50,
        cmd_total=100,
        commands=cmds,
    )
    remain_tail = estimate_planned_seconds(cmds, start_index=50)
    # 线性一半会远小于后半等待和
    linear_half = planned * 0.5
    assert remain_tail > linear_half
    assert abs(eta["remain_s"] - remain_tail) / remain_tail < 0.05


def test_compute_eta_freeze_remain_skips_progress_blend():
    cmds = [["AC", "write", "X", "", "", "", "", "", "", 100]] * 10
    planned = estimate_planned_seconds(cmds)
    eta_run = compute_eta(
        elapsed_s=1000,
        progress_pct=50,
        planned_total_s=planned,
        cmd_index=5,
        cmd_total=10,
        commands=cmds,
        freeze_remain=False,
    )
    eta_pause = compute_eta(
        elapsed_s=1000,
        progress_pct=50,
        planned_total_s=planned,
        cmd_index=5,
        cmd_total=10,
        commands=cmds,
        freeze_remain=True,
    )
    # cmd_index=5 表示第 5 条正在执行，剩余含本条整段加后面 5 条
    plan_remain = estimate_planned_seconds(cmds, start_index=4)
    assert abs(eta_pause["remain_s"] - plan_remain) < 0.01
    # 暂停冻结后不应被超大 elapsed/进度外推拉飞
    assert eta_pause["remain_s"] <= eta_run["remain_s"] + 1.0


def test_current_dwell_and_later_tests_stay_in_remain():
    """命令等待 20/100 秒时，不能因为条数或轮次已经走完就把剩余清成 0。"""
    cmds = [
        ["AC", "wait", "OVUF", "", "", "", "", "", "", 1000],  # 100s
        ["AC", "wait", "PF", "", "", "", "", "", "", 600],  # 60s，下一项
    ]
    eta = compute_eta(
        elapsed_s=276,
        progress_pct=100,
        planned_total_s=estimate_planned_seconds(cmds),
        cmd_index=1,
        cmd_total=2,
        commands=cmds,
        cmd_waited_s=20,
    )
    assert eta["remain_s"] > 130
    assert eta["progress_from_plan"] < 30
    assert eta["remain_text"] != "约 0 秒"


def test_format_estimated_end_time():
    now = datetime(2026, 9, 29, 10, 0, 0)
    text = format_estimated_end_time(90, now=now, status="进行中")
    assert text == "2026-09-29 10:01:30"
    assert format_estimated_end_time(90, now=now, status="已结束") == ""
    assert format_estimated_end_time(0, now=now, status="进行中") == ""


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
