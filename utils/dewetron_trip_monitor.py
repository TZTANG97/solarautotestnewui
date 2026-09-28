# -*- coding: utf-8 -*-
"""DEWETRON 实时电流跳脱检测（与人工看波形断流一致，不中断试验）。"""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional, Sequence, Tuple


# ShortId / 通道名里常见的三相电流标记
# 兼容 CSV 表头单位：I1_tRMS [A]@POWER/0
_I_PHASE_RE = re.compile(
    r"(?:^|[/_\s])I([123])(?:_t?RMS|_fundRMS)?(?:\s*\[[^\]]*\])?(?:@|$)|(?:^|[/_\s])I([123])$",
    re.IGNORECASE,
)
_I_TOTAL_RE = re.compile(
    r"(?:^|[/_\s])I(?:_t?RMS|_fundRMS|rms)?(?:\s*\[[^\]]*\])?(?:@|$)|(?:^AI\s*\d+/I$)",
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


def find_voltage_indices(channel_names: Sequence[str]) -> List[int]:
    """找相电压 U1/U2/U3（或单列 U）下标，优先三相。"""
    phase: dict = {}
    total: Optional[int] = None
    u_phase_re = re.compile(
        r"(?:^|[/_\s])U([123])(?:_t?RMS|_fundRMS)?(?:\s*\[[^\]]*\])?(?:@|$)",
        re.IGNORECASE,
    )
    u_total_re = re.compile(
        r"(?:^|[/_\s])U(?:_t?RMS|_fundRMS)?(?:\s*\[[^\]]*\])?(?:@|$)",
        re.IGNORECASE,
    )
    for idx, name in enumerate(channel_names or []):
        text = str(name or "").strip()
        if not text:
            continue
        compact = text.replace(" ", "")
        m = u_phase_re.search(compact)
        if m:
            digit = m.group(1)
            if digit and digit not in phase:
                phase[digit] = idx
            continue
        short = text.split("@", 1)[0]
        if u_total_re.search(short.replace(" ", "")) and not any(
            x in short.upper() for x in ("U1", "U2", "U3", "U12", "U23", "U31")
        ):
            if total is None:
                total = idx
    ordered = [phase[d] for d in ("1", "2", "3") if d in phase]
    if ordered:
        return ordered
    return [total] if total is not None else []


def find_frequency_index(channel_names: Sequence[str]) -> Optional[int]:
    """找频率通道下标（F_fund / Freq / Frequency）。"""
    for idx, name in enumerate(channel_names or []):
        text = str(name or "").strip()
        if not text:
            continue
        low = text.split("@", 1)[0].casefold().replace(" ", "")
        # 排除 PF_fund
        if low.startswith("pf"):
            continue
        if low in {"f_fund", "freq", "frequency", "f"}:
            return idx
        if low.startswith("f_fund") or low.startswith("freq"):
            return idx
    return None


def extract_trip_values(
    values: Sequence[float],
    channel_names: Sequence[str],
) -> dict:
    """
    从跳脱当拍 NUMERIC 取出跳脱值：相电压均值 U、频率 F。
    返回 dict: u_v, f_hz, u_phases, extras（缺测为 None）。
    """
    result = {"u_v": None, "f_hz": None, "u_phases": [], "i_mean": None}
    if not values:
        return result
    u_idx = find_voltage_indices(channel_names)
    phases = []
    for i in u_idx:
        if 0 <= i < len(values):
            try:
                phases.append(float(values[i]))
            except (TypeError, ValueError):
                pass
    result["u_phases"] = phases
    if phases:
        result["u_v"] = sum(phases) / len(phases)
    f_idx = find_frequency_index(channel_names)
    if f_idx is not None and 0 <= f_idx < len(values):
        try:
            result["f_hz"] = float(values[f_idx])
        except (TypeError, ValueError):
            pass
    phase_i, total_i = find_current_indices(channel_names)
    result["i_mean"] = mean_current(values, phase_i, total_i)
    return result


def format_trip_value_log(
    *,
    wall_clock: str,
    elapsed_s: float,
    reason: str,
    trip_values: Optional[dict] = None,
) -> str:
    """操作日志：跳脱时刻 + 测得跳脱值（不做截图/录波提示）。"""
    parts = [f"[DEWETRON][跳脱] 时刻 {wall_clock} (录波+{elapsed_s:.1f}s) {reason}"]
    tv = trip_values or {}
    bits = []
    if tv.get("u_v") is not None:
        bits.append(f"U={float(tv['u_v']):.3f}V")
    if tv.get("f_hz") is not None:
        bits.append(f"F={float(tv['f_hz']):.3f}Hz")
    if tv.get("i_mean") is not None:
        bits.append(f"I={float(tv['i_mean']):.3f}A")
    if bits:
        parts.append("跳脱值 " + " ".join(bits))
    else:
        parts.append("跳脱值未取到（请勾选 U 和/或 F_fund）")
    return "；".join(parts)


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

    启机保护：
    - ``startup_ignore_s``：采集开始后这段时间只建历史、不报跳脱（避免启机噪声误报）
    - ``arm_hold_s``：电流需持续高于门槛这么久才允许判定跳脱（避免毛刺武装后立刻掉零）
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
        startup_ignore_s: float = 0.0,
        arm_hold_s: float = 0.0,
    ):
        self.phase_indices = list(phase_indices or [])
        self.total_index = total_index
        self.window = max(2, int(window))
        self.armed_min_a = float(armed_min_a)
        self.drop_ratio = float(drop_ratio)
        self.floor_a = float(floor_a)
        self.confirm_samples = max(1, int(confirm_samples))
        self.cooldown_s = float(cooldown_s)
        self.startup_ignore_s = max(0.0, float(startup_ignore_s))
        self.arm_hold_s = max(0.0, float(arm_hold_s))

        self._hist: Deque[float] = deque(maxlen=self.window)
        self._drop_streak = 0
        self._sample_index = 0
        self._last_trip_mono: float = 0.0
        self._armed = False
        self._armed_since_mono: float = 0.0

    @property
    def has_current_channels(self) -> bool:
        return bool(self.phase_indices) or self.total_index is not None

    def reset(self) -> None:
        self._hist.clear()
        self._drop_streak = 0
        self._sample_index = 0
        self._armed = False
        self._armed_since_mono = 0.0
        self._last_trip_mono = 0.0

    def _mark_armed(self, now_mono: float) -> None:
        if not self._armed:
            self._armed = True
            self._armed_since_mono = float(now_mono)

    def _arm_ready(self, now_mono: float) -> bool:
        if not self._armed:
            return False
        if self.arm_hold_s <= 0:
            return True
        return (float(now_mono) - float(self._armed_since_mono)) >= self.arm_hold_s

    def feed(
        self,
        values: Sequence[float],
        *,
        now_mono: float,
        elapsed_s: Optional[float] = None,
    ) -> Optional[TripEvent]:
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

        # 启机窗口：只建历史，不武装、不报跳脱（避免启机噪声误报）
        if elapsed_s is not None and float(elapsed_s) < self.startup_ignore_s:
            self._drop_streak = 0
            return None

        if prev >= self.armed_min_a:
            self._mark_armed(now_mono)

        # 冷却期内只更新历史，不重复触发
        if self._last_trip_mono and (now_mono - self._last_trip_mono) < self.cooldown_s:
            self._drop_streak = 0
            return None

        dropped = i_mean <= self.floor_a or (
            self._armed and prev >= self.armed_min_a and i_mean <= prev * self.drop_ratio
        )
        if dropped and self._arm_ready(now_mono):
            self._drop_streak += 1
        else:
            self._drop_streak = 0
            if i_mean >= self.armed_min_a:
                self._mark_armed(now_mono)
            return None

        if self._drop_streak < self.confirm_samples:
            return None

        self._drop_streak = 0
        self._armed = False
        self._armed_since_mono = 0.0
        self._last_trip_mono = now_mono
        return TripEvent(
            sample_index=self._sample_index,
            i_mean=i_mean,
            prev_mean=prev,
            reason=f"I_mean {prev:.3f}A -> {i_mean:.3f}A",
        )
