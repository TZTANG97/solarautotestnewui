# -*- coding: utf-8 -*-
"""巴西过欠频稳定性：频率扫描点生成（限制点数，避免 100ms 更新率炸出上千点）。"""

from __future__ import annotations

from typing import List

# 单段最大扫频点数（含起止）。台架冒烟/正式均可接受的上限。
MAX_IMMUN_SWEEP_POINTS = 51


def build_immun_freq_sweep_points(
    start_hz: float,
    end_hz: float,
    *,
    duration_s: float,
    rate_s: float,
    use_rate: bool,
    max_points: int = MAX_IMMUN_SWEEP_POINTS,
) -> List[float]:
    """按更新率生成扫频点；超上限时按频率跨度均分，而不是按时长×频率爆炸。

    - use_rate=False：只返回起点
    - rate_s / duration_s 无效时：返回起点
    """
    start = float(start_hz)
    end = float(end_hz)
    if not use_rate:
        return [round(start, 2)]

    duration = float(duration_s)
    rate = float(rate_s)
    if duration <= 0 or rate <= 0:
        return [round(start, 2)]

    # 与旧逻辑一致：点数 ≈ 时长 / 更新间隔
    raw_count = max(1, int(duration / rate))
    count = min(int(max_points), raw_count)
    if count <= 1:
        return [round(start, 2), round(end, 2)] if abs(end - start) > 1e-9 else [round(start, 2)]

    delta = abs(end - start)
    step = delta / float(count)
    points: List[float] = []
    cur = start
    ascending = end >= start
    for _ in range(count):
        points.append(round(cur, 2))
        cur = cur + step if ascending else cur - step
        if ascending and cur >= end:
            break
        if (not ascending) and cur <= end:
            break
    if not points or abs(points[-1] - end) > 1e-6:
        points.append(round(end, 2))
    # 去重保序
    out: List[float] = []
    for p in points:
        if not out or abs(out[-1] - p) > 1e-9:
            out.append(p)
    return out[: max(1, int(max_points)) + 1]
