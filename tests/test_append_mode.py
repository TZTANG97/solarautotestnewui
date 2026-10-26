# -*- coding: utf-8 -*-
"""跨试验追加：覆盖 / 跨项追加 / 同项追加。"""
from __future__ import annotations

from utils.append_mode import apply_append_mode, mark_project_now, resolve_append_mode


def test_first_append_overwrites_when_queue_empty():
    flag, change, label = resolve_append_mode(
        project_name="谐波电流", local_count=0, queue=[], project_now=""
    )
    assert flag == "0"
    assert change == "0"
    assert label == "覆盖"


def test_second_project_does_not_wipe_queue():
    """先谐波后闪变：闪变计数仍为0，但队列非空 → 必须跨项追加，禁止覆盖清空。"""
    flag, change, label = resolve_append_mode(
        project_name="电压闪变",
        local_count=0,
        queue=[["AC", "write", "OUTP ON"]],
        project_now="谐波电流",
    )
    assert flag == "1"
    assert change == "1"
    assert label == "跨项追加"


def test_same_project_second_round():
    flag, change, label = resolve_append_mode(
        project_name="谐波电流",
        local_count=1,
        queue=[["AC"]],
        project_now="谐波电流",
    )
    assert flag == "1"
    assert change == "0"
    assert label == "追加"


def test_apply_and_mark():
    g = {"strArrayTest": [["x"]], "project_now": "谐波电流"}
    flag, change, label = apply_append_mode(
        g, project_name="电压闪变", local_count=0
    )
    assert flag == "1" and change == "1"
    assert g["strAddTestFlag"] == "1"
    assert g["project_change"] == "1"
    mark_project_now(g, "电压闪变")
    assert g["project_now"] == "电压闪变"
