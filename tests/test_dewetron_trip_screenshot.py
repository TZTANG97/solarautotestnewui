# -*- coding: utf-8 -*-
"""跳脱监视与截图路径单测（不连真机）。"""

from __future__ import annotations

import os
import time

from utils.dewetron_trip_monitor import (
    TripMonitor,
    find_current_indices,
    mean_current,
)
from utils.oxygen_screenshot import build_trip_screenshot_path


def test_find_current_indices_phase():
    names = ["U1_tRMS@AC", "I1_tRMS@AC", "I2_tRMS@AC", "I3_tRMS@AC", "P_t@AC"]
    phase, total = find_current_indices(names)
    assert phase == [1, 2, 3]
    assert total is None
    assert abs(mean_current([230, 10, 11, 12, 7000], phase, total) - 11.0) < 1e-6


def test_find_current_indices_ai_style():
    names = ["AI 1/U1", "AI 1/I1", "AI 1/I2", "AI 1/I3"]
    phase, total = find_current_indices(names)
    assert phase == [1, 2, 3]


def test_trip_monitor_matches_csv_drop():
    # 模拟 CSV：稳定 ~11A 后一拍掉到 0
    mon = TripMonitor(
        phase_indices=[0, 1, 2],
        window=5,
        armed_min_a=2.0,
        drop_ratio=0.2,
        floor_a=0.5,
        confirm_samples=2,
        cooldown_s=8.0,
    )
    t0 = 1000.0
    # 填满窗口
    for i in range(5):
        assert mon.feed([11.0, 11.0, 11.0], now_mono=t0 + i * 0.2) is None
    # 第一拍掉零：确认中
    assert mon.feed([0.0, 0.0, 0.0], now_mono=t0 + 1.2) is None
    # 第二拍确认跳脱
    ev = mon.feed([0.0, 0.0, 0.0], now_mono=t0 + 1.4)
    assert ev is not None
    assert ev.i_mean == 0.0
    assert ev.prev_mean > 5.0
    # 冷却内不再触发
    assert mon.feed([0.0, 0.0, 0.0], now_mono=t0 + 2.0) is None


def test_trip_monitor_no_false_on_noise():
    mon = TripMonitor(phase_indices=[0], window=5, confirm_samples=2, cooldown_s=1.0)
    t0 = time.monotonic()
    for i in range(8):
        v = 10.0 + (0.2 if i % 2 == 0 else -0.2)
        assert mon.feed([v], now_mono=t0 + i * 0.1) is None


def test_build_trip_screenshot_path_beside_csv(tmp_path):
    csv_path = str(tmp_path / "overload_20260920_120000.csv")
    png = build_trip_screenshot_path(csv_path, stamp="120001")
    assert png.endswith("overload_20260920_120000_trip_120001.png")
    assert os.path.dirname(png) == str(tmp_path)
