# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from utils.wt_csv_abs_time import (
    format_wall_time_for_csv,
    inject_abs_time_column,
)


def test_format_wall_time_matches_dewetron_style():
    # 2025-12-17 16:58:07.971 local — use a fixed unix via datetime
    from datetime import datetime

    dt = datetime(2025, 12, 17, 16, 58, 7, 971000)
    text = format_wall_time_for_csv(dt.timestamp())
    assert text.startswith("2025/12/17 16:58:07.")
    assert text.endswith("971")


def test_inject_abs_time_before_time_s(tmp_path: Path):
    p = tmp_path / "QCap_BR.csv"
    p.write_text(
        "Time [s],P-SIGMA\n0.0000,100.0\n1.5000,200.0\n",
        encoding="utf-8-sig",
    )
    start = 1_700_000_000.0
    assert inject_abs_time_column(p, start) is True
    lines = p.read_text(encoding="utf-8-sig").strip().splitlines()
    assert lines[0].startswith("Abs Time,Time [s],")
    row1 = lines[1].split(",")
    assert row1[0]
    assert row1[1] == "0.0000"
    # second inject without force is no-op
    assert inject_abs_time_column(p, start) is False
