# -*- coding: utf-8 -*-
"""追加试验队列标记：本试验结束后是否暂停等人工改逆变器。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

QUEUE_DEVICE = "QUEUE"
QUEUE_END_OP = "end_test"


def make_queue_end_row(project_name: str, *, pause_after: bool) -> List[Any]:
    name = (project_name or "").strip() or "未命名试验"
    return [
        QUEUE_DEVICE,
        QUEUE_END_OP,
        name,
        "1" if pause_after else "0",
        "",
        "",
        "",
        "",
        "",
        "",
    ]


def is_queue_end_row(row: Sequence[Any]) -> bool:
    if not row:
        return False
    return str(row[0] or "").strip().upper() == QUEUE_DEVICE and str(
        row[1] or ""
    ).strip() == QUEUE_END_OP


def row_pause_after(row: Sequence[Any]) -> bool:
    if not is_queue_end_row(row):
        return False
    flag = str(row[3] if len(row) > 3 else "").strip().lower()
    return flag in ("1", "true", "yes", "on")


def row_project_name(row: Sequence[Any]) -> str:
    if not row or len(row) < 3:
        return ""
    return str(row[2] or "").strip()


def parse_queue_segments(
    commands: Sequence[Sequence[Any]] | None,
    *,
    fallback_name: str = "",
) -> List[Dict[str, Any]]:
    """按 QUEUE/end_test 切分追加的多项试验。"""
    cmds = list(commands or [])
    segments: List[Dict[str, Any]] = []
    start = 0
    for i, row in enumerate(cmds):
        if not is_queue_end_row(row):
            continue
        body = cmds[start:i]
        planned = 0.0
        try:
            from utils.run_progress_eta import estimate_planned_seconds

            planned = float(estimate_planned_seconds(body))
        except Exception:
            planned = 0.0
        segments.append(
            {
                "name": row_project_name(row) or fallback_name or f"试验{len(segments) + 1}",
                "pause_after": row_pause_after(row),
                "cmd_start": start,
                "cmd_end": i,
                "marker_index": i,
                "planned_seconds": planned,
            }
        )
        start = i + 1
    if start < len(cmds):
        tail = cmds[start:]
        planned = 0.0
        try:
            from utils.run_progress_eta import estimate_planned_seconds

            planned = float(estimate_planned_seconds(tail))
        except Exception:
            planned = 0.0
        segments.append(
            {
                "name": fallback_name or "当前试验",
                "pause_after": False,
                "cmd_start": start,
                "cmd_end": len(cmds),
                "marker_index": -1,
                "planned_seconds": planned,
            }
        )
    if not segments and cmds:
        planned = 0.0
        try:
            from utils.run_progress_eta import estimate_planned_seconds

            planned = float(estimate_planned_seconds(cmds))
        except Exception:
            planned = 0.0
        segments.append(
            {
                "name": fallback_name or "当前试验",
                "pause_after": False,
                "cmd_start": 0,
                "cmd_end": len(cmds),
                "marker_index": -1,
                "planned_seconds": planned,
            }
        )
    return segments


QUEUE_DONE_STATUS = frozenset({"完成", "已结束", "已中止", "中止", "失败"})


def seal_unstarted_queue_items(queue: Sequence[Dict[str, Any]]) -> None:
    """整段命令已经结束：没开跑的段不再占本机队列。不补开始/结束时间。"""
    for item in queue or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").strip() in ("等待", "", "运行", "测试中"):
            item["status"] = "中止"


def close_queue_clocks(
    queue: Sequence[Dict[str, Any]], *, now_text: str, aborted: bool = False
) -> None:
    """整段试验结束时，给已经跑过的每一段补上结束时间。没开始的段不造时间。"""
    now = (now_text or "").strip()
    done = "中止" if aborted else "完成"
    for item in queue or []:
        if not isinstance(item, dict):
            continue
        st = str(item.get("status") or "").strip()
        started = str(item.get("started_at") or item.get("startedAt") or "").strip()
        ran = bool(started) or st in ("进行中", "暂停", "完成", "已结束", "已中止", "中止", "失败")
        if not ran:
            if aborted and st in ("等待", ""):
                item["status"] = "中止"
            continue
        if st in ("进行中", "暂停", ""):
            item["status"] = done
        if now and not str(item.get("finished_at") or item.get("finishedAt") or "").strip():
            item["finished_at"] = now


def stamp_queue_times(queue: Sequence[Dict[str, Any]], *, now_text: str) -> None:
    """进行中补开始时间，完成/中止补结束时间（已有则不覆盖）。"""
    now = (now_text or "").strip()
    if not now:
        return
    for item in queue or []:
        if not isinstance(item, dict):
            continue
        st = str(item.get("status") or "").strip()
        if st == "进行中" and not str(item.get("started_at") or "").strip():
            item["started_at"] = now
        if st in QUEUE_DONE_STATUS and not str(item.get("finished_at") or "").strip():
            item["finished_at"] = now
            if not str(item.get("started_at") or "").strip():
                item["started_at"] = now


def settle_finished_round_note(note: Any) -> str:
    """轮次已经结束时，去掉开录时写下的「执行中 / 测量中」。其它备注保留。"""
    text = str(note or "").strip()
    if text == "执行中" or text.startswith("测量中"):
        return ""
    return "" if note is None else str(note)


def segment_at_command(
    segments: Sequence[Dict[str, Any]], cmd_index_1based: int
) -> Optional[Dict[str, Any]]:
    if cmd_index_1based <= 0:
        return None
    idx0 = cmd_index_1based - 1
    for seg in segments:
        if int(seg.get("cmd_start") or 0) <= idx0 < int(seg.get("cmd_end") or 0):
            return dict(seg)
    return None
