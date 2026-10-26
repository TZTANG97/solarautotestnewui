# -*- coding: utf-8 -*-
"""跨试验追加：决定覆盖 / 同项追加 / 换项追加。

历史问题：各试验用自己的 ``*_append_count==0`` 一律当「覆盖」并 ``strArrayTest=[]``。
先追加 A 再追加 B（B 计数仍为 0）会把 A 的命令冲掉；或换项时未置
``project_change=1``，第二项跳过 WT/录波宏 →「第二次实验没有数据」。
"""
from __future__ import annotations

from typing import Any, Dict, MutableMapping, Optional, Tuple


def resolve_append_mode(
    *,
    project_name: str,
    local_count: int,
    queue: Any = None,
    project_now: str = "",
) -> Tuple[str, str, str]:
    """返回 ``(strAddTestFlag, project_change, mode_label)``。

    - 覆盖：本项计数为 0 且命令队列为空
    - 跨项追加：队列已有内容且本项是首次（或项目名切换）→ flag=1, project_change=1
    - 同项追加：本项计数>0 且未换项 → flag=1, project_change=0
    """
    name = str(project_name or "").strip()
    try:
        count = int(local_count or 0)
    except (TypeError, ValueError):
        count = 0
    has_queue = bool(queue)
    prev = str(project_now or "").strip()
    switching = bool(prev and name and prev != name)

    if count <= 0 and not has_queue:
        return "0", "0", "覆盖"
    if count <= 0 and has_queue:
        # 本项第一次，但队列里已有别的试验 → 绝不能清空
        return "1", "1", "跨项追加"
    if switching:
        return "1", "1", "跨项追加"
    return "1", "0", "追加"


def apply_append_mode(
    g: MutableMapping[str, Any],
    *,
    project_name: str,
    local_count: int,
) -> Tuple[str, str, str]:
    """写入 ``g['strAddTestFlag']`` / ``g['project_change']``，返回三元组。"""
    flag, change, label = resolve_append_mode(
        project_name=project_name,
        local_count=local_count,
        queue=g.get("strArrayTest"),
        project_now=str(g.get("project_now") or ""),
    )
    g["strAddTestFlag"] = flag
    g["project_change"] = change
    return flag, change, label


def mark_project_now(g: MutableMapping[str, Any], project_name: str) -> None:
    """追加成功后记住当前项目，供下次换项判断。"""
    name = str(project_name or "").strip()
    if name:
        g["project_now"] = name
