# -*- coding: utf-8 -*-
"""Deep-check ovuf CSV: all channels max, trip name matching, parse alignment."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, r"E:\solarautotestnewui")

from utils.dewetron_trip_monitor import TripMonitor, find_current_indices

CSV = Path(r"E:\solarautotestnewui\docs\voltage-frequency-protection_20260921_141738.csv")
OLD = Path(r"E:\solarautotestnewui\docs\voltage-frequency-protection_20260921_134556.csv")


def load(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def short_of(header: str) -> str:
    # "I1_tRMS [A]@POWER/0" -> "I1_tRMS@POWER/0"
    if " [" in header and "@" in header:
        base = header.split(" [", 1)[0]
        suffix = header[header.index("@") :]
        return base + suffix
    return header


def analyze(path: Path):
    print("=" * 70)
    print(path.name)
    h, data = load(path)
    print(f"cols={len(h)} rows={len(data)}")
    shorts = [short_of(c) for c in h[1:]]
    print("ALL headers:")
    for i, (full, sh) in enumerate(zip(h[1:], shorts)):
        vals = [float(r[i + 1]) for r in data if r[i + 1] not in ("",)]
        if not vals:
            continue
        mx = max(abs(v) for v in vals)
        mn = min(vals)
        mxv = max(vals)
        flag = ""
        if sh.upper().startswith("I") or "I1" in sh or "I2" in sh or "I3" in sh or "I_t" in sh:
            flag = " <<I"
        if mx >= 0.5:
            flag += " **>=0.5**"
        if mx >= 2.0:
            flag += " **>=2A?**"
        print(
            f"  [{i:02d}] {sh:40s} min={mn:10.4f} max={mxv:10.4f} absmax={mx:10.4f}{flag}"
        )

    phase, total = find_current_indices(shorts)
    print(f"find_current_indices(short) -> phase={phase} total={total}")
    phase_raw, total_raw = find_current_indices(h[1:])
    print(f"find_current_indices(raw csv hdr) -> phase={phase_raw} total={total_raw}")

    # Simulate as collector would (short fields)
    mon = TripMonitor(phase_indices=phase, total_index=total)
    trips = []
    armed_seen = False
    max_i = 0.0
    for r in data:
        vals = [float(x) if x else 0.0 for x in r[1:]]
        from utils.dewetron_trip_monitor import mean_current

        im = mean_current(vals, phase, total)
        if im is not None:
            max_i = max(max_i, im)
            if im >= 2.0:
                armed_seen = True
        ev = mon.feed(vals, now_mono=float(r[0]))
        if ev:
            trips.append((float(r[0]), ev.reason))
    print(f"sim: max_Imean={max_i:.4f} ever_armed_capable={armed_seen} trips={len(trips)}")
    for t, reason in trips[:5]:
        print(f"  trip @ {t:.3f}: {reason}")


def test_regex_against_real_names():
    print("=" * 70)
    print("regex vs real Dewetron field names")
    samples = [
        "I1_tRMS@POWER/0",
        "I1_tRMS [A]@POWER/0",
        "I1_tRMS",
        "I_tRMS@POWER/0",
        "I_tRMS [A]@POWER/0",
        "C1_RMS@POWER/0",
        "AI 1/I1",
    ]
    for s in samples:
        print(f"  {s!r} -> {find_current_indices([s])}")


def test_trip_logic_ok():
    print("=" * 70)
    print("unit: trip fires when I drops from 8A to 0")
    mon = TripMonitor(phase_indices=[0, 1, 2])
    t = 0.0
    for _ in range(6):
        assert mon.feed([8, 8, 8], now_mono=t) is None
        t += 0.1
    assert mon.feed([0, 0, 0], now_mono=t) is None
    t += 0.1
    ev = mon.feed([0, 0, 0], now_mono=t)
    print("  fired:", ev is not None, getattr(ev, "reason", None))


if __name__ == "__main__":
    test_regex_against_real_names()
    test_trip_logic_ok()
    analyze(CSV)
    if OLD.exists():
        analyze(OLD)
