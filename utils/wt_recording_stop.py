# -*- coding: utf-8 -*-
"""WT 一轮录完后：整单结束、切到下一项，还是同一项的下一个文件。"""
from __future__ import annotations


def decide_wt_recording_stop(
    *,
    count_now,
    total_save_file,
    name_count,
    program_count,
) -> str:
    """返回 ``all_done`` / ``project_done`` / ``next_file``。

    文件名列表被后一项覆盖成 1 个、但 ``total_save_file`` 和 ``test_program``
    仍表示后面还有试验时，不能把当前这一轮收成整单结束，否则下一项不会再开录。
    """
    try:
        idx = int(count_now or 0)
    except (TypeError, ValueError):
        idx = 0
    try:
        total = int(total_save_file or 0)
    except (TypeError, ValueError):
        total = 0
    try:
        n_names = int(name_count or 0)
    except (TypeError, ValueError):
        n_names = 0
    try:
        n_prog = int(program_count or 0)
    except (TypeError, ValueError):
        n_prog = 0

    rounds = total
    if n_names > 0:
        rounds = min(rounds, n_names) if rounds > 0 else n_names
    if rounds < 1:
        rounds = 1

    files_done = idx >= rounds - 1
    saves_remaining = total > (idx + 1)
    more_projects = n_prog > 1

    if files_done and more_projects and saves_remaining:
        return "project_done"
    if files_done:
        return "all_done"
    if n_names > 0 and idx >= n_names - 1 and more_projects:
        return "project_done"
    return "next_file"
