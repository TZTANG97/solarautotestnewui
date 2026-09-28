# -*- coding: utf-8 -*-
"""试验进度：时长估算与文案（纯函数，供 SCPITestWave 进度条调用）。"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence


# 单条命令基础开销（发令/解析，不含显式等待列）
_CMD_OVERHEAD_S = 0.08
# Upper_WT_Config / WT 宏难以从等待列精确估计，给经验值
_UPPER_WT_CONFIG_S = 75.0
_WT_MACRO_S = 12.0


def format_duration(seconds: float) -> str:
    """把秒数格式化为中文时长，如「约 3 分 20 秒」。"""
    try:
        s = max(0.0, float(seconds))
    except (TypeError, ValueError):
        return "约 —"
    total = int(round(s))
    if total < 60:
        return f"约 {total} 秒"
    minutes, sec = divmod(total, 60)
    if minutes < 60:
        if sec == 0:
            return f"约 {minutes} 分"
        return f"约 {minutes} 分 {sec} 秒"
    hours, minutes = divmod(minutes, 60)
    if minutes == 0:
        return f"约 {hours} 小时"
    return f"约 {hours} 小时 {minutes} 分"


def _cell_wait_tenths(row: Sequence[Any], col: int) -> float:
    if col >= len(row):
        return 0.0
    val = row[col]
    if val is None or val == "":
        return 0.0
    try:
        return max(0.0, float(val))
    except (TypeError, ValueError):
        return 0.0


def estimate_planned_seconds(commands: Optional[Sequence[Sequence[Any]]]) -> float:
    """按命令表估算计划总时长（秒）。

    约定：col 7/8/9 为 0.1 秒单位等待（与 RunProject 一致）。
    Upper_WT_Config / WT 宏另加经验时长。
    """
    if not commands:
        return 0.0
    total = 0.0
    for row in commands:
        if not row:
            continue
        wait_tenths = (
            _cell_wait_tenths(row, 7)
            + _cell_wait_tenths(row, 8)
            + _cell_wait_tenths(row, 9)
        )
        dev = str(row[0] or "")
        if dev.strip().upper() == "QUEUE":
            continue
        total += wait_tenths * 0.1
        total += _CMD_OVERHEAD_S
        if dev == "Upper_WT_Config":
            total += _UPPER_WT_CONFIG_S
        elif dev == "WT":
            total += _WT_MACRO_S
    return total


def compute_eta(
    *,
    elapsed_s: float,
    progress_pct: int,
    planned_total_s: float,
    cmd_index: int = 0,
    cmd_total: int = 0,
) -> Dict[str, Any]:
    """综合「计划等待」与「已用时/进度」估算剩余与预计总时长。

    返回字段：
    - planned_total_s / elapsed_s / remain_s / eta_total_s
    - planned_text / elapsed_text / remain_text / eta_total_text
    """
    elapsed = max(0.0, float(elapsed_s or 0.0))
    planned = max(0.0, float(planned_total_s or 0.0))
    pct = max(0, min(100, int(progress_pct or 0)))

    # 计划剩余：按命令索引粗分未执行等待（若有 cmd_total）
    remain_by_plan = None
    if planned > 0 and cmd_total > 0 and cmd_index >= 0:
        # 已执行到 cmd_index（1-based）时，按比例扣减计划
        frac_done = min(1.0, max(0.0, float(cmd_index) / float(cmd_total)))
        remain_by_plan = max(0.0, planned * (1.0 - frac_done))
    elif planned > 0:
        remain_by_plan = max(0.0, planned - elapsed)

    # 进度剩余：用已用时 / 进度外推（进度太低时不可靠）
    remain_by_progress = None
    if pct >= 5 and pct < 100 and elapsed > 1.0:
        eta_total = elapsed / (pct / 100.0)
        remain_by_progress = max(0.0, eta_total - elapsed)

    candidates = [x for x in (remain_by_plan, remain_by_progress) if x is not None]
    if not candidates:
        remain = max(0.0, planned - elapsed) if planned > 0 else 0.0
    elif len(candidates) == 1:
        remain = candidates[0]
    else:
        # 计划与进度各半，避免 WT 配置等把计划拉偏或进度抖动
        remain = 0.5 * candidates[0] + 0.5 * candidates[1]

    if pct >= 100:
        remain = 0.0

    eta_total = elapsed + remain
    if planned > 0:
        # 展示用预计总时长：取计划与动态 ETA 的较大者，避免前期低估
        eta_total = max(eta_total, planned) if pct < 30 else eta_total

    return {
        "planned_total_s": planned,
        "elapsed_s": elapsed,
        "remain_s": remain,
        "eta_total_s": eta_total,
        "planned_text": format_duration(planned) if planned > 0 else "约 —",
        "elapsed_text": format_duration(elapsed),
        "remain_text": format_duration(remain),
        "eta_total_text": format_duration(eta_total) if eta_total > 0 else "约 —",
    }


def build_progress_summary(
    state: Mapping[str, Any],
    *,
    eta: Optional[Mapping[str, Any]] = None,
) -> str:
    """生成进度标签多行文案。"""
    project = state.get("project") or "-"
    status = state.get("status") or "未开始"
    current_round = int(state.get("current_round") or 0)
    total_rounds = int(state.get("total_rounds") or 0)
    cmd_index = int(state.get("cmd_index") or 0)
    cmd_total = int(state.get("cmd_total") or 0)
    progress = int(state.get("progress") or 0)
    detail = str(state.get("current_detail") or "").strip()
    queue = list(state.get("queue") or [])
    current_test = str(state.get("current_test") or "").strip()

    line1 = f"试验进度：{project} | {status} | {progress}%"
    if current_test and current_test != project:
        line1 += f" | 当前项 {current_test}"
    if queue:
        line1 += f" | 共 {len(queue)} 项试验"
    if total_rounds > 0:
        line1 += f" | 录波 {current_round}/{total_rounds} 轮"
    if cmd_total > 0:
        line1 += f" | 命令 {cmd_index}/{cmd_total}"

    lines = [line1]
    if detail:
        lines.append(f"当前步骤：{detail}")
    if queue:
        names = []
        for i, item in enumerate(queue):
            st = str(item.get("status") or "等待")
            nm = str(item.get("name") or f"试验{i + 1}")
            extra = " ·结束后暂停" if item.get("pause_after") else ""
            names.append(f"{i + 1}.{nm}({st}{extra})")
        lines.append("队列：" + " → ".join(names))

    if eta and status in ("进行中", "暂停", "待开始"):
        lines.append(
            f"已用 {eta.get('elapsed_text', '约 —')} | "
            f"剩余 {eta.get('remain_text', '约 —')} | "
            f"预计总时长 {eta.get('eta_total_text', '约 —')}"
            + (
                f"（计划 {eta.get('planned_text')}）"
                if float(eta.get("planned_total_s") or 0) > 0
                else ""
            )
        )
    elif eta and status in ("已结束", "已中止"):
        lines.append(f"本次用时 {eta.get('elapsed_text', '约 —')}")

    return "\n".join(lines)
