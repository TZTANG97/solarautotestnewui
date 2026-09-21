# -*- coding: utf-8 -*-
"""
跳脱时间段截图验证脚本（可离线 / 可喂真 CSV）。

用法:
  .venv\\Scripts\\python.exe code_example/verify_dewetron_trip_period_shot.py
  .venv\\Scripts\\python.exe code_example/verify_dewetron_trip_period_shot.py --csv "D:\\path\\1.CSV"

输出:
  code_example/media/trip_period_verify_*.png
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.dewetron_trip_monitor import TripMonitor
from utils.dewetron_trip_period_shot import render_trip_period_png


def _load_wt_style_csv(path: str):
    """读取用户给的 WT 风格 CSV（Irms-1/2/3），转成 (t, [U1,I1,I2,I3])。"""
    samples = []
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        t0 = None
        for row in reader:
            try:
                # 用 StoreNo * 0.2 近似，或累积 ms
                ms = float(str(row.get("Millisecond") or "0").strip() or 0)
                # Date+Time 不稳定时用序号
                idx = float(str(row.get("StoreNo") or len(samples) + 1))
                t = (idx - 1) * 0.2
                u1 = float(row["Urms-1"])
                i1 = float(row["Irms-1"])
                i2 = float(row["Irms-2"])
                i3 = float(row["Irms-3"])
            except Exception:
                continue
            samples.append((t, [u1, i1, i2, i3]))
    return samples


def _synthetic():
    samples = []
    t = 0.0
    for _ in range(60):
        samples.append((t, [230.0, 10.7, 10.7, 11.1]))
        t += 0.2
    for _ in range(15):
        samples.append((t, [183.6, 0.0, 0.0, 0.0]))
        t += 0.2
    return samples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="", help="可选：现场 WT/导出 CSV（含 Irms-1/2/3）")
    ap.add_argument("--pre", type=float, default=2.0)
    ap.add_argument("--post", type=float, default=1.0)
    args = ap.parse_args()

    if args.csv and os.path.isfile(args.csv):
        samples = _load_wt_style_csv(args.csv)
        print(f"loaded csv n={len(samples)} from {args.csv}")
    else:
        samples = _synthetic()
        print(f"synthetic n={len(samples)}")

    channels = ["U1_tRMS", "I1_tRMS", "I2_tRMS", "I3_tRMS"]
    mon = TripMonitor(phase_indices=[1, 2, 3], window=5, confirm_samples=2, cooldown_s=8)
    buf = []
    pending = None
    for elapsed, vals in samples:
        buf.append((elapsed, vals))
        if pending is None:
            ev = mon.feed(vals, now_mono=1000.0 + elapsed)
            if ev:
                pending = elapsed
                print(f"trip at t={pending:.3f}s ({ev.reason})")
        if pending is not None and elapsed >= pending + args.post:
            period = [s for s in buf if pending - args.pre <= s[0] <= pending + args.post]
            out_dir = ROOT / "code_example" / "media"
            out_dir.mkdir(parents=True, exist_ok=True)
            stamp = time.strftime("%Y%m%d_%H%M%S")
            out = str(out_dir / f"trip_period_verify_{stamp}.png")
            ok, msg = render_trip_period_png(
                period, channels, out, title="verify trip period", trip_time_s=pending
            )
            print(msg)
            if not ok:
                return 2
            # 校验：窗口长度、含高低电流
            span = period[-1][0] - period[0][0]
            means = [sum(v[1:4]) / 3 for _, v in period]
            print(
                f"OK period n={len(period)} span={span:.3f}s "
                f"Imean[{min(means):.3f},{max(means):.3f}] -> {out}"
            )
            if span > args.pre + args.post + 0.5:
                print("FAIL: 时间窗过宽，可能截了整段试验")
                return 3
            if max(means) < 2.0 or min(means) > 1.0:
                print("FAIL: 窗口未同时覆盖运行电流与跳脱后近零")
                return 4
            return 0
    print("FAIL: 未检测到跳脱")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
