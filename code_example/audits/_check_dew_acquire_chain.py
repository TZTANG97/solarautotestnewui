# -*- coding: utf-8 -*-
"""采集链路排查：解析对齐、NUMERIC 配置、端到端假机、真实 CSV 物理一致性。"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, r"E:\solarautotestnewui")

from devices.dewetron_data_collector import DewetronDataCollector


class FakeLogger:
    def info(self, message):
        pass


class FakeController:
    def __init__(self, channels):
        self.connected = True
        self.channels = list(channels)
        self.state = "Stopped"
        self.numeric_items = ""
        self.values = []
        self.sent = []

    def query_command(self, command, timeout_ms=30000):
        if command == ":CHANNELLIST:NAMES?":
            return ",".join(
                f'"{i}","{ch}"' for i, ch in enumerate(self.channels, start=1)
            )
        if command == ":ACQUISITION:STATE?":
            return self.state
        if command == ":NUM:NORM:ITEMs?":
            return self.numeric_items
        if command == ":RATE?":
            return "100ms"
        if command == ":NUM:NORM:VALue?":
            if not self.values:
                return None
            return self.values.pop(0)
        return None

    def send_command(self, command, *args, **kwargs):
        self.sent.append(command)
        if command.startswith(":NUM:NORM:ITEMs "):
            self.numeric_items = command.split(" ", 1)[1]
        return True

    def stop_acquisition(self):
        self.sent.append(":ACQUISITION:STOP")
        self.state = "Stopped"
        return True


def section(title):
    print("=" * 70)
    print(title)


def test_parse_formats():
    section("1) _parse_value 各种 VALue? 响应格式")
    c = DewetronDataCollector(FakeController([]), FakeLogger(), db_path=":memory:")
    cases = [
        (
            "SCPI前缀+无空格时间",
            ':NUM:NORM:VALue? "14:17:38.1",230.0,10.5,7000.0',
            [230.0, 10.5, 7000.0],
        ),
        (
            "无前缀+无空格时间",
            '"14:17:38.1",230.0,10.5,7000.0',
            [230.0, 10.5, 7000.0],
        ),
        (
            "SCPI前缀+带空格日期时间",
            ':NUM:NORM:VALue? "2026-09-21 14:17:38",230.0,10.5,7000.0',
            [230.0, 10.5, 7000.0],
        ),
        (
            "无前缀+带空格日期时间(危险)",
            '"2026-09-21 14:17:38",230.0,10.5,7000.0',
            [230.0, 10.5, 7000.0],
        ),
        (
            "runtime单测同款",
            ':NUM:NORM:VALue? "t",1.25',
            [1.25],
        ),
    ]
    bugs = []
    for name, raw, expect in cases:
        got = c._parse_value(raw)
        ok = got == expect
        print(f"  [{('OK' if ok else 'BUG')}] {name}")
        print(f"       raw={raw!r}")
        print(f"       got={got} expect={expect}")
        if not ok:
            bugs.append(name)
    return bugs


def test_e2e_high_current(tmp_path: Path):
    section("2) 假机端到端：有 10A 电流时 CSV 是否保住")
    channels = [
        "U1_tRMS@POWER/0",
        "I1_tRMS@POWER/0",
        "I2_tRMS@POWER/0",
        "I3_tRMS@POWER/0",
        "P_t@POWER/0",
    ]
    ctrl = FakeController(channels)
    db = tmp_path / "e2e.sqlite"
    csv_path = tmp_path / "e2e.csv"
    col = DewetronDataCollector(ctrl, FakeLogger(), db_path=str(db))
    result = col.prepare(
        ["U1_tRMS", "I1_tRMS", "I2_tRMS", "I3_tRMS", "P_t"],
        "100",
        "voltage-frequency-protection",
        str(csv_path),
    )
    assert result.success, result.error
    print(f"  fields={col._fields}")
    print(f"  trip_monitor={col._trip_monitor is not None} phase={getattr(col._trip_monitor,'phase_indices',None)}")

    # ABS-TIME + 5 channels
    ctrl.values = [
        ':NUM:NORM:VALue? "t0",230.0,10.0,10.1,9.9,6900.0',
        ':NUM:NORM:VALue? "t1",230.0,10.0,10.1,9.9,6900.0',
        ':NUM:NORM:VALue? "t2",230.0,0.0,0.0,0.0,0.0',
        ':NUM:NORM:VALue? "t3",230.0,0.0,0.0,0.0,0.0',
    ]
    assert col.begin_run()
    col._gather_start_time = 1000.0
    with patch("devices.dewetron_data_collector.time.sleep"):
        for _ in range(4):
            assert col._collect_one_point(0.1)

    out = col.export_run_to_csv(col._last_run_id or col._run_id, str(csv_path))
    # finish_run may have cleared run_id; export via last
    if out is None:
        col.finish_run()
        out = col.export_run_to_csv(col._last_run_id, str(csv_path))
    print(f"  exported={out}")
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    print(f"  header={rows[0]}")
    for r in rows[1:]:
        print(f"  row={r}")
    # I1 col
    i1_idx = next(i for i, h in enumerate(rows[0]) if h.startswith("I1_tRMS"))
    i1_vals = [float(r[i1_idx]) for r in rows[1:]]
    print(f"  I1 values={i1_vals}")
    assert max(i1_vals) >= 9.0, "高电流应写入 CSV"
    assert min(i1_vals) <= 0.1, "跳脱后低电流应写入 CSV"
    trips = col._trip_shot_count
    print(f"  trip_shot_count={trips}")
    col.stop()
    return i1_vals, trips


def test_csv_physics(path: Path):
    section(f"3) 真实 CSV 物理一致性: {path.name}")
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    h = rows[0]
    data = rows[1:]

    def col(name_prefix):
        for i, c in enumerate(h):
            if c.startswith(name_prefix):
                return i
        return None

    iu = col("U_tRMS")
    i1 = col("I1_tRMS")
    i2 = col("I2_tRMS")
    i3 = col("I3_tRMS")
    ip = col("P_t [W]") or col("P_t@")
    # P_t header is like P_t [W]@POWER/0
    if ip is None:
        for i, c in enumerate(h):
            if c.startswith("P_t"):
                ip = i
                break
    print(f"  idx U={iu} I1={i1} I2={i2} I3={i3} P={ip} ncols={len(h)}")
    # sample mid and max-P row
    best = max(data, key=lambda r: abs(float(r[ip])))
    samples = [data[len(data) // 2], best, data[-5]]
    ok = True
    for r in samples:
        u = float(r[iu])
        a = (float(r[i1]) + float(r[i2]) + float(r[i3])) / 3
        p = float(r[ip])
        # rough |P| ~= 3 * U * I * PF ; PF~1 → 3UI; allow wide band for near-zero
        expect = 3 * u * a
        # if both near zero, ok
        if max(abs(p), abs(expect)) < 5:
            ratio_ok = True
        else:
            # within factor 3
            ratio_ok = 0.2 * abs(expect) <= abs(p) <= 5 * abs(expect) if expect else abs(p) < 50
        print(
            f"  t={float(r[0]):.2f} U={u:.2f} Imean={a:.4f} P={p:.2f} "
            f"3UI={expect:.2f} phys_ok={ratio_ok}"
        )
        ok = ok and ratio_ok
    # length: every data row must match header
    bad_len = sum(1 for r in data if len(r) != len(h))
    print(f"  rows_with_bad_length={bad_len}")
    return ok and bad_len == 0


def test_length_mismatch_silent():
    section("4) 设备少返回通道时是否静默错位")
    c = DewetronDataCollector(FakeController([]), FakeLogger(), db_path=":memory:")
    # configured 5 meas channels but response only 3 numbers after ABS-TIME
    got = c._parse_value(':NUM:NORM:VALue? "t",230,10,10')
    print(f"  parsed={got} len={len(got) if got else None}")
    print("  注意: collector 不校验 len(row)==len(fields)，少值会原样入库")
    return got


if __name__ == "__main__":
    bugs = test_parse_formats()
    tmp = Path(r"E:\solarautotestnewui\code_example\media\_dew_chain_tmp")
    tmp.mkdir(parents=True, exist_ok=True)
    i1_vals, trips = test_e2e_high_current(tmp)
    csv_new = Path(r"E:\solarautotestnewui\docs\voltage-frequency-protection_20260921_141738.csv")
    phys_ok = test_csv_physics(csv_new)
    test_length_mismatch_silent()
    section("结论摘要")
    print(f"  parse_format_bugs={bugs or '无'}")
    print(f"  e2e_I1_max={max(i1_vals):.3f} trip_shots={trips}")
    print(f"  real_csv_physics_ok={phys_ok}")
