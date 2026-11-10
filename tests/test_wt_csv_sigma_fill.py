# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from utils.wt_csv_sigma_fill import fill_empty_sigma_freq_columns
from utils.iot_data_analysis_bridge import _prefer_keys_for_test, _stage_clean_analysis_input


def test_fill_empty_frequ_sigma(tmp_path: Path):
    p = tmp_path / "QCap_BR_x.csv"
    p.write_text(
        "Time [s],FreqU-1,FreqU-2,FreqU-3,FreqU-SIGMA\n"
        "0.1,50.0000000,50.0000000,49.9950000,\n"
        "0.2,49.9970000,50.0000000,49.9950000,\n",
        encoding="utf-8-sig",
    )
    assert fill_empty_sigma_freq_columns(p) is True
    lines = p.read_text(encoding="utf-8-sig").strip().splitlines()
    row1 = lines[1].split(",")
    assert row1[-1]
    assert abs(float(row1[-1]) - 49.9983333) < 1e-5


def test_stage_qcap_ignores_harmonic_noise(tmp_path: Path):
    src = tmp_path / "save"
    src.mkdir()
    (src / "Harmonic_33.csv").write_text(
        "Time [s],U\n" + "\n".join(f"{i},230" for i in range(10)),
        encoding="utf-8",
    )
    q = src / "QCap_BR_222708.csv"
    q.write_text(
        "Time [s],P-SIGMA\n" + "\n".join(f"{i},1000" for i in range(10)),
        encoding="utf-8",
    )
    staging = tmp_path / "stage"
    out = _stage_clean_analysis_input(
        src, prefer_keys=_prefer_keys_for_test("reactiveqcap"), staging_dir=staging
    )
    names = sorted(p.name for p in out.glob("*.csv"))
    assert names == ["QCap_BR_222708.csv"]
