# -*- coding: utf-8 -*-
"""DEWETRON 实时电流跳脱检测（与人工看波形断流一致，不中断试验）。"""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional, Sequence, Tuple


# ShortId / 通道名里常见的三相电流标记
_I_PHASE_RE = re.compile(
    r"(?:^|[/_\s])I([123])(?:_t?RMS|_fundRMS)?(?:@|$)|(?:^|[/_\s])I([123])$",
    re.IGNORECASE,
)
_I_TOTAL_RE = re.compile(
    r"(?:^|[/_\s])I(?:_t?RMS|_fundRMS|rms)?(?:@|$)|(?:^AI\s*\d+/I$)",
    re.IGNORECASE,
)


def find_current_indices(channel_names: Sequence[str]) -> Tuple[List[int], Optional[int]]:
    """
    从 NUMERIC 通道名列表找电流列下标。
    返回 (三相 I1/I2/I3 下标列表, 总和/单列 I 下标或 None)。
    """
    phase: dict = {}
    total: Optional[int] = None
    for idx, name in enumerate(channel_names or []):
        text = str(name or "").strip()
        if not text:
            continue
        m = _I_PHASE_RE.search(text.replace(" ", ""))
        if m:
            digit = m.group(1) or m.group(2)
            if digit and digit not in phase:
                phase[digit] = idx
            continue
        short = text.split("@", 1)[0]
        if _I_TOTAL_RE.search(short.replace(" ", "")) and "I1" not in short and "I2" not in short and "I3" not in short:
            if total is None:
                total = idx
    ordered = [phase[d] for d in ("1", "2", "3") if d in phase]
    return ordered, total


def mean_current(values: Sequence[float], phase_idx: Sequence[int], total_idx: Optional[int]) -> Optional[float]:
    """取三相均值；无三相则用总和/单列。"""
    if not values:
        return None
    used = []
    for i in phase_idx:
        if 0 <= i < len(values):
            try:
                used.append(float(values[i]))
            except (TypeError, ValueError):
                pass
    if used:
        return sum(used) / len(used)
    if total_idx is not None and 0 <= total_idx < len(values):
        try:
            return float(values[total_idx])
        except (TypeError, ValueError):
            return None
    return None


@dataclass
class TripEvent:
    """一次跳脱事件快照。"""

    sample_index: int
    i_mean: float
    prev_mean: float
    reason: str


class TripMonitor:
    """
    滑动窗检测：运行电流 → 骤降到近零。
    参考 WT/德威创录波：Irms 从 ~10A 一拍掉到 0。
    """

    def __init__(
        self,
        *,
        phase_indices: Optional[Sequence[int]] = None,
        total_index: Optional[int] = None,
        window: int = 5,
        armed_min_a: float = 2.0,
        drop_ratio: float = 0.2,
        floor_a: float = 0.5,
        confirm_samples: int = 2,
        cooldown_s: float = 8.0,
    ):
        self.phase_indices = list(phase_indices or [])
        self.total_index = total_index
        self.window = max(2, int(window))
        self.armed_min_a = float(armed_min_a)
        self.drop_ratio = float(drop_ratio)
        self.floor_a = float(floor_a)
        self.confirm_samples = max(1, int(confirm_samples))
        self.cooldown_s = float(cooldown_s)

        self._hist: Deque[float] = deque(maxlen=self.window)
        self._drop_streak = 0
        self._sample_index = 0
        self._last_trip_mono: float = 0.0
        self._armed = False

    @property
    def has_current_channels(self) -> bool:
        return bool(self.phase_indices) or self.total_index is not None

    def reset(self) -> None:
        self._hist.clear()
        self._drop_streak = 0
        self._sample_index = 0
        self._armed = False
        self._last_trip_mono = 0.0

    def feed(self, values: Sequence[float], *, now_mono: float) -> Optional[TripEvent]:
        """喂入一拍 NUMERIC 数值；若判为跳脱返回 TripEvent，否则 None。"""
        if not self.has_current_channels:
            return None
        i_mean = mean_current(values, self.phase_indices, self.total_index)
        if i_mean is None:
            return None

        self._sample_index += 1
        self._hist.append(i_mean)

        if len(self._hist) < self.window:
            return None

        prev = sum(list(self._hist)[:-1]) / (len(self._hist) - 1)
        if prev >= self.armed_min_a:
            self._armed = True

        # 冷却期内只更新历史，不重复触发
        if self._last_trip_mono and (now_mono - self._last_trip_mono) < self.cooldown_s:
            self._drop_streak = 0
            return None

        dropped = i_mean <= self.floor_a or (
            self._armed and prev >= self.armed_min_a and i_mean <= prev * self.drop_ratio
        )
        if dropped and self._armed:
            self._drop_streak += 1
        else:
            self._drop_streak = 0
            if i_mean >= self.armed_min_a:
                self._armed = True
            return None

        if self._drop_streak < self.confirm_samples:
            return None

        self._drop_streak = 0
        self._armed = False
        self._last_trip_mono = now_mono
        return TripEvent(
            sample_index=self._sample_index,
            i_mean=i_mean,
            prev_mean=prev,
            reason=f"I_mean {prev:.3f}A -> {i_mean:.3f}A",
        )
