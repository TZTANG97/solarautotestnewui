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


def test_stage_qcap_prefers_filename_stamp_over_touched_mtime(tmp_path: Path):
    import os
    import time

    src = tmp_path / "save"
    src.mkdir()
    old = src / "QCap_BR_222708.csv"
    new = src / "QCap_BR_224530.csv"
    body = "Time [s],P-SIGMA\n" + "\n".join(f"{i},1000" for i in range(10))
    old.write_text(body, encoding="utf-8")
    new.write_text(body, encoding="utf-8")
    now = time.time()
    os.utime(new, (now - 30, now - 30))
    os.utime(old, (now, now))
    staging = tmp_path / "stage"
    out = _stage_clean_analysis_input(
        src, prefer_keys=_prefer_keys_for_test("reactiveqcap"), staging_dir=staging
    )
    names = sorted(p.name for p in out.glob("*.csv"))
    assert names == ["QCap_BR_224530.csv"]


def test_fill_recent_prefers_filename_stamp_when_both_in_window(tmp_path: Path):
    import os
    import time

    from utils.wt_csv_sigma_fill import fill_recent_csvs_in_dirs

    header = "Time [s],FreqU-1,FreqU-2,FreqU-3,FreqU-SIGMA\n"
    rows = "0.1,50,50,50,\n0.2,50,50,50,\n0.3,50,50,50,\n"
    old = tmp_path / "QCap_BR_222708.csv"
    new = tmp_path / "QCap_BR_224530.csv"
    old.write_text(header + rows, encoding="utf-8-sig")
    new.write_text(header + rows, encoding="utf-8-sig")
    now = time.time()
    os.utime(new, (now - 20, now - 20))
    os.utime(old, (now, now))
    filled = fill_recent_csvs_in_dirs(
        [tmp_path], name_hint="QCap_BR", limit=1, min_mtime=now - 60
    )
    assert [Path(p).name for p in filled] == ["QCap_BR_224530.csv"]
    assert old.read_text(encoding="utf-8-sig").splitlines()[1].endswith(",")


def test_fill_recent_skips_files_before_gather(tmp_path: Path):
    import time

    from utils.wt_csv_sigma_fill import fill_recent_csvs_in_dirs

    old = tmp_path / "QCap_BR_222708.csv"
    old.write_text(
        "Time [s],FreqU-1,FreqU-2,FreqU-3,FreqU-SIGMA\n"
        "0.1,50,50,50,\n0.2,50,50,50,\n0.3,50,50,50,\n",
        encoding="utf-8-sig",
    )
    before = old.stat().st_mtime
    filled = fill_recent_csvs_in_dirs(
        [tmp_path], name_hint="QCap_BR", limit=4, min_mtime=time.time() + 5
    )
    assert filled == []
    assert old.stat().st_mtime == before


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


def test_short_qcap_does_not_fallback_to_harmonic(tmp_path: Path, monkeypatch):
    src = tmp_path / "save"
    src.mkdir()
    (src / "Harmonic_33.csv").write_text(
        "Time [s],U\n" + "\n".join(f"{i},230" for i in range(10)),
        encoding="utf-8",
    )
    (src / "QCap_BR_short.csv").write_text(
        "Time [s],P-SIGMA\n0.1,1000\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "utils.iot_data_analysis_bridge._analysis_root",
        lambda: tmp_path,
    )
    (tmp_path / "run_headless.py").write_text("# stub\n", encoding="utf-8")
    from utils.iot_data_analysis_bridge import run_analysis_after_job

    result = {
        "status": "success",
        "result_summary": {
            "testType": "reactiveqcap",
            "analysis_input_dir": str(src),
            "report_files": [{"path": str(src / "QCap_BR_short.csv")}],
        },
    }
    job = {
        "id": 127,
        "testType": "reactiveqcap",
        "widgets": {"analysis_Pn": "10000", "solarStandard": "en50549"},
        "params": {},
    }
    info = run_analysis_after_job(repo_root=tmp_path, job=job, result=result)
    assert info.get("ran") is False
    assert info.get("quality") == "too_few_rows"
    assert "QCap_BR_short" in str(info.get("reason") or "")
