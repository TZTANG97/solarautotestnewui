# -*- coding: utf-8 -*-
"""台架冒烟：验证 WT SCPI ``:RATE`` + NUMERIC 能否压到 50/100ms。

用法（需已连上 WT，优先以太网）::

    uv run python code_example/bench_wt_scpi_rate.py --addr 192.168.1.10 --rate 50ms --seconds 5
    uv run python code_example/bench_wt_scpi_rate.py --addr ASRL6::INSTR --baud 19200 --rate 50ms

若 median 仍贴近 180–250ms：检查是否串口、是否 WTViewer 占着以太网唯一连接、
``:RATE?`` 是否真回到 50/100。
"""
from __future__ import annotations

import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pyvisa

from devices.wt_controller import WT3000Controller
from devices.wt_data_collector import WtScpiCollector
from devices.wt_scpi_rate import is_serial_resource, parse_rate_ms


class _PrintLogger:
    def info(self, msg):
        print(msg)


def main():
    parser = argparse.ArgumentParser(description="WT SCPI rate bench")
    parser.add_argument("--addr", required=True, help="IP / TCPIP... / ASRL...")
    parser.add_argument("--baud", default="9600")
    parser.add_argument("--rate", default="50ms")
    parser.add_argument("--seconds", type=float, default=5.0)
    parser.add_argument(
        "--out",
        default=os.path.join("code_example", "media", "wt_scpi_bench.csv"),
    )
    args = parser.parse_args()

    rm = pyvisa.ResourceManager()
    ctrl = WT3000Controller(_PrintLogger(), print, rm, baud_rate=args.baud)
    handle, flag = ctrl.connect(args.addr)
    if flag != "1" or handle is None:
        print("连接失败")
        return 1

    resource = ctrl.resource or getattr(handle, "resource_name", "")
    print(f"resource={resource} serial={is_serial_resource(resource)}")
    try:
        print("*IDN? ->", ctrl.query("*IDN?"))
    except Exception as exc:
        print(f"*IDN? 失败: {exc}")

    ok, actual, warn = ctrl.set_rate_ms(parse_rate_ms(args.rate))
    print(f"set_rate_ms ok={ok} actual={actual} warn={warn!r}")
    if not ok:
        ctrl.disconnect(lambda h: h.close() if h else None)
        return 2

    collector = WtScpiCollector(ctrl, _PrintLogger())
    collector.start()
    ready, items, warnings = collector.prepare(
        rate_text=args.rate, save_path=args.out
    )
    print(f"prepare ok={ready} items={len(items)} warnings={warnings}")
    if not ready:
        collector.stop()
        ctrl.disconnect(lambda h: h.close() if h else None)
        return 3

    collector.start_gathering()
    time.sleep(max(args.seconds, 0.5))
    collector.stop_gathering()
    stats = collector.sample_interval_stats()
    path = collector.export_to_csv(args.out)
    collector.stop()
    ctrl.disconnect(lambda h: h.close() if h else None)

    print("--- interval stats (PC receive spacing) ---")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print(f"csv: {path}")

    target = stats.get("target_ms") or parse_rate_ms(args.rate)
    median = stats.get("median_ms")
    if median is None:
        print("FAIL: 无有效采样")
        return 4
    # Allow ~1.5x slack for VISA overhead; serial will usually fail this.
    limit = max(target * 1.5, target + 30)
    if median > limit:
        print(
            f"FAIL: median {median}ms > {limit:.0f}ms —— 仍像旧的 ~180ms 地板；"
            "请改以太网并确认 :RATE? / 关闭 WTViewer 独占连接"
        )
        return 5
    print(f"PASS: median {median}ms within {limit:.0f}ms of target {target}ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
