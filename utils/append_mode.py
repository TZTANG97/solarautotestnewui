# -*- coding: utf-8 -*-
"""同项重复追加 / 跨项追加 统一判定。

历史问题：
1. 各试验 ``*_append_count==0`` 一律覆盖 → 换项追加会清空上一试验队列。
2. 跑完后队列已空但计数仍>0，再点追加仍走「同项追加」→ 跳过部分 WT/首启逻辑，第二轮无数据。
3. 跨项/多轮缺少 QUEUE/end_test 标记 → 进度与录波分段对不上。
"""
from __future__ import annotations

from typing import Any, MutableMapping, Optional, Tuple


def resolve_append_mode(
    *,
    project_name: str,
    local_count: int,
    queue: Any = None,
    project_now: str = "",
) -> Tuple[str, str, str]:
    """返回 ``(strAddTestFlag, project_change, mode_label)``。

    - 覆盖：命令队列为空（含同项跑完未点重置、首次追加）
    - 跨项追加：队列非空且项目切换（或本项计数为0但队列已有别项）
    - 同项追加：队列非空且仍是同一项目、计数>0
    """
    name = str(project_name or "").strip()
    try:
        count = int(local_count or 0)
    except (TypeError, ValueError):
        count = 0
    has_queue = bool(queue)
    prev = str(project_now or "").strip()
    switching = bool(prev and name and prev != name)

    # 空队列一律重建：避免「计数残留 + 队列已空」误走追加而跳过 WT 首配
    if not has_queue:
        return "0", "0", "覆盖"

    if switching:
        return "1", "1", "跨项追加"

    if count <= 0:
        # 队列里已有内容，但本项计数为0（常见：刚换到本项）
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


def _pause_checkbox_from_ui_obj(val: Any) -> Any:
    """取「后续试验暂停」勾选框。

    禁止对未创建的 LazyDialog 做 ``getattr(ui, 'checkBox_…')``：
    LazyDialog.__getattr__ 会先 ``_ensure_created()``，追加收尾若扫遍全部
    ``uiThai*`` 会一口气实例化几十个试验页，主线程表现为死机。
    """
    if val is None:
        return None

    # Duck-type LazyDialog：类上有 is_created 属性，且未创建则跳过
    # （用 type(val).is_created / __dict__，避免触发实例 __getattr__）
    cls = type(val)
    if "is_created" in getattr(cls, "__dict__", {}):
        try:
            created = bool(cls.is_created.__get__(val, cls))  # type: ignore[attr-defined]
        except Exception:
            try:
                created = bool(val.__dict__.get("_real_dialog") is not None)
            except Exception:
                created = False
        if not created:
            return None
        target = val.__dict__.get("_real_ui")
        if target is None:
            return None
    else:
        target = val

    try:
        return getattr(target, "checkBox_PauseAfterNext", None)
    except Exception:
        return None


def ensure_queue_end_marker(
    g: MutableMapping[str, Any],
    project_name: str,
    *,
    pause_after: Optional[bool] = None,
) -> bool:
    """保证队列末尾有 QUEUE/end_test，便于同项多轮 / 跨项分段。

    返回是否写入/更新了标记。
    """
    arr = g.get("strArrayTest")
    if not isinstance(arr, list) or not arr:
        return False
    name = str(project_name or "").strip() or "未命名试验"
    if pause_after is None:
        pause_after = False
        try:
            # 当前试验 Dialog 上的「后续试验暂停」——只扫已创建的 ui*
            for key, val in list(g.items()):
                if not str(key).startswith("ui"):
                    continue
                cb = _pause_checkbox_from_ui_obj(val)
                if cb is None:
                    continue
                try:
                    if cb.isChecked():
                        pause_after = True
                        break
                except Exception:
                    pass
        except Exception:
            pause_after = False

    try:
        from utils.test_queue_markers import is_queue_end_row, make_queue_end_row
    except Exception:
        return False

    row = make_queue_end_row(name, pause_after=bool(pause_after))
    if is_queue_end_row(arr[-1]):
        # 同项连续追加：更新末尾标记名/暂停意图即可
        arr[-1] = row
    else:
        arr.append(row)
    return True


def finalize_successful_append(
    g: MutableMapping[str, Any],
    project_name: str,
    *,
    pause_after: Optional[bool] = None,
) -> None:
    """追加成功收尾：记住项目 + 写入/刷新 QUEUE 分段标记。"""
    mark_project_now(g, project_name)
    ensure_queue_end_marker(g, project_name, pause_after=pause_after)


def begin_append_attempt(g: MutableMapping[str, Any]) -> str:
    """追加前清零成功标志。

    各 ``*Send`` 仅在校验通过时把 ``strSettingTestFlag`` 置 ``1``，失败时常
    原样返回。若不先清零，上次成功残留的 ``1`` 会让本轮失败仍走 finalize，
    误写 QUEUE/end_test。
    """
    prev = str(g.get("strSettingTestFlag") or "")
    g["strSettingTestFlag"] = "0"
    return prev


def commit_append_if_success(
    g: MutableMapping[str, Any],
    project_name: str,
    previous_flag: str,
    *,
    pause_after: Optional[bool] = None,
) -> bool:
    """Send 之后：成功则 finalize；失败则恢复先前的成功标志。"""
    if str(g.get("strSettingTestFlag") or "") == "1":
        finalize_successful_append(g, project_name, pause_after=pause_after)
        return True
    g["strSettingTestFlag"] = previous_flag
    return False
