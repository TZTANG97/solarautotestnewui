# -*- coding: utf-8 -*-
"""同项重复追加 / 跨项追加。"""
from __future__ import annotations

from utils.append_mode import (
    apply_append_mode,
    begin_append_attempt,
    commit_append_if_success,
    ensure_queue_end_marker,
    finalize_successful_append,
    resolve_append_mode,
)
from utils.test_queue_markers import is_queue_end_row, parse_queue_segments


def test_empty_queue_always_overwrite_even_if_count_high():
    """跑完后队列空、计数仍>0：必须覆盖重建，不能误走同项追加。"""
    flag, change, label = resolve_append_mode(
        project_name="谐波电流",
        local_count=3,
        queue=[],
        project_now="谐波电流",
    )
    assert flag == "0"
    assert change == "0"
    assert label == "覆盖"


def test_first_append_overwrites_when_queue_empty():
    flag, change, label = resolve_append_mode(
        project_name="谐波电流", local_count=0, queue=[], project_now=""
    )
    assert (flag, change, label) == ("0", "0", "覆盖")


def test_same_project_second_round_keeps_queue():
    flag, change, label = resolve_append_mode(
        project_name="谐波电流",
        local_count=1,
        queue=[["AC", "write", "OUTP ON"]],
        project_now="谐波电流",
    )
    assert flag == "1"
    assert change == "0"
    assert label == "追加"


def test_cross_project_does_not_wipe():
    flag, change, label = resolve_append_mode(
        project_name="电压闪变",
        local_count=0,
        queue=[["AC", "write", "OUTP ON"]],
        project_now="谐波电流",
    )
    assert flag == "1"
    assert change == "1"
    assert label == "跨项追加"


def test_cross_when_count_positive_but_switching():
    flag, change, label = resolve_append_mode(
        project_name="重连",
        local_count=2,
        queue=[["Upper_WT_Config"]],
        project_now="谐波电流",
    )
    assert (flag, change) == ("1", "1")


def test_finalize_writes_queue_marker_for_segments():
    g = {
        "strArrayTest": [["AC", "write", "OUTP ON"], ["WT", "write", "xxx"]],
        "project_now": "",
    }
    finalize_successful_append(g, "谐波电流", pause_after=False)
    assert g["project_now"] == "谐波电流"
    assert is_queue_end_row(g["strArrayTest"][-1])

    # 同项再追加一轮：新命令接在上一标记后，再打新标记 → 两段同名
    g["strArrayTest"].extend([["AC", "query", "*IDN?"]])
    ensure_queue_end_marker(g, "谐波电流", pause_after=True)
    ends = [r for r in g["strArrayTest"] if is_queue_end_row(r)]
    assert len(ends) == 2
    assert ends[-1][3] == "1"

    # 跨项：新试验命令后再打标记
    g["strArrayTest"].extend([["AC", "write", "OUTP OFF"]])
    finalize_successful_append(g, "电压闪变", pause_after=False)
    segs = parse_queue_segments(g["strArrayTest"])
    assert len(segs) >= 3
    assert segs[0]["name"] == "谐波电流"
    assert segs[-1]["name"] == "电压闪变"


def test_apply_append_mode_writes_globals():
    g = {"strArrayTest": [["x"]], "project_now": "谐波电流"}
    flag, change, label = apply_append_mode(
        g, project_name="电压闪变", local_count=0
    )
    assert flag == "1" and change == "1" and "跨项" in label
    assert g["strAddTestFlag"] == "1"
    assert g["project_change"] == "1"


def test_failed_send_does_not_finalize_on_stale_flag():
    """上次成功残留 flag=1 时，本轮失败不得再写 QUEUE 标记。"""
    g = {
        "strSettingTestFlag": "1",
        "strArrayTest": [["AC", "write", "OUTP ON"]],
        "project_now": "谐波电流",
    }
    prev = begin_append_attempt(g)
    assert prev == "1"
    assert g["strSettingTestFlag"] == "0"
    # 模拟 Send 校验失败：不置回 1
    ok = commit_append_if_success(g, "谐波电流", prev)
    assert ok is False
    assert g["strSettingTestFlag"] == "1"  # 恢复，开测按钮逻辑仍可用
    assert not is_queue_end_row(g["strArrayTest"][-1])


def test_success_send_finalizes_after_clear():
    g = {
        "strSettingTestFlag": "1",
        "strArrayTest": [["AC", "write", "OUTP ON"], ["WT", "write", "x"]],
        "project_now": "",
    }
    prev = begin_append_attempt(g)
    g["strSettingTestFlag"] = "1"  # Send 成功
    assert commit_append_if_success(g, "电压闪变", prev) is True
    assert g["project_now"] == "电压闪变"
    assert is_queue_end_row(g["strArrayTest"][-1])
