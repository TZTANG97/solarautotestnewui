# -*- coding: utf-8 -*-
"""跳脱时间段截图：单元验证 + 跌落回放验证。"""

from __future__ import annotations

import os

from utils.dewetron_trip_monitor import TripMonitor
from utils.dewetron_trip_period_shot import (
    build_trip_period_path,
    render_trip_period_png,
    slice_trip_period,
)


def test_slice_trip_period_only_window():
    samples = [(i * 0.2, [10.0, 10.0, 10.0]) for i in range(30)]
    samples[-2] = (samples[-2][0], [0.0, 0.0, 0.0])
    samples[-1] = (samples[-1][0], [0.0, 0.0, 0.0])
    trip_t = samples[-1][0]
    period = slice_trip_period(samples, pre_s=1.0, post_s=0.0)
    assert period
    assert all(trip_t - 1.0 - 1e-6 <= t <= trip_t + 1e-6 for t, _ in period)
    assert period[0][0] >= trip_t - 1.0 - 1e-6


def test_render_trip_period_png(tmp_path):
    channels = ["U1_tRMS@AC", "I1_tRMS@AC", "I2_tRMS@AC", "I3_tRMS@AC"]
    samples = []
    for i in range(40):
        t = i * 0.2
        if i < 30:
            samples.append((t, [230.0, 11.0, 11.0, 11.0]))
        else:
            samples.append((t, [230.0, 0.0, 0.0, 0.0]))
    period = slice_trip_period(samples, pre_s=2.0, post_s=1.0)
    out = str(tmp_path / "trip_period.png")
    ok, msg = render_trip_period_png(
        period, channels, out, title="unit", trip_time_s=samples[30][0]
    )
    assert ok, msg
    assert os.path.isfile(out)
    assert os.path.getsize(out) > 1000


def test_csv_style_drop_period_only(tmp_path):
    """模拟现场 Irms 跌落：截图时间窗只覆盖跳脱前后，不含更早稳态。"""
    channels = ["U1_tRMS", "I1_tRMS", "I2_tRMS", "I3_tRMS"]
    samples = []
    t = 0.0
    for _ in range(50):
        samples.append((t, [230.0, 10.7, 10.7, 11.1]))
        t += 0.2
    trip_t = t
    for _ in range(10):
        samples.append((t, [183.0, 0.0, 0.0, 0.0]))
        t += 0.2

    mon = TripMonitor(phase_indices=[1, 2, 3], window=5, confirm_samples=2, cooldown_s=8)
    buf = []
    pending = None
    for elapsed, vals in samples:
        buf.append((elapsed, vals))
        if pending is None:
            ev = mon.feed(vals, now_mono=1000.0 + elapsed)
            if ev:
                pending = elapsed
        if pending is not None and elapsed >= pending + 1.0:
            period = [s for s in buf if pending - 2.0 <= s[0] <= pending + 1.0]
            assert period[0][0] >= pending - 2.0 - 1e-6
            assert period[-1][0] <= pending + 1.0 + 1e-6
            # 不应包含试验很开头的点
            assert period[0][0] > 5.0
            means = [sum(vv[1:4]) / 3 for _tt, vv in period]
            assert max(means) > 5.0
            assert min(means) < 0.5
            out = build_trip_period_path(str(tmp_path / "demo.csv"), stamp="verify")
            ok, msg = render_trip_period_png(period, channels, out, trip_time_s=pending)
            assert ok, msg
            assert "trip_period" in out
            assert abs(pending - trip_t) < 0.5
            return
    raise AssertionError("未检测到跳脱，回放验证失败")
