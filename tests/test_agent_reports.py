# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.job_inbox import write_result
from agent.reports import collect_report_files


def test_collect_includes_result_and_listed(tmp_path: Path) -> None:
    job_id = 42
    write_result(tmp_path, job_id, {"status": "success"})
    extra = tmp_path / "notes.txt"
    extra.write_text("hello", encoding="utf-8")
    (tmp_path / "status.json").write_text('{"project":{}}', encoding="utf-8")
    files = collect_report_files(
        tmp_path,
        job_id,
        {
            "result_summary": {"report_files": ["notes.txt"]},
        },
    )
    names = {p.name for p in files}
    assert f"job_{job_id}.json" in names
    assert "notes.txt" in names
    assert "status.json" in names


def test_collect_includes_recent_csv(tmp_path: Path) -> None:
    job_id = 7
    write_result(
        tmp_path,
        job_id,
        {"status": "success", "result_summary": {"elapsed_sec": 30}},
    )
    # 结案只扫本任务目录，避免误收其它 job 的 CSV
    csv_dir = tmp_path / "command_save_files" / "command_data" / f"sim_job_{job_id}"
    csv_dir.mkdir(parents=True)
    recent = csv_dir / "wt_run.csv"
    recent.write_text("a,b\n1,2\n", encoding="utf-8")
    files = collect_report_files(
        tmp_path,
        job_id,
        {"result_summary": {"elapsed_sec": 30}},
    )
    names = {p.name for p in files}
    assert "wt_run.csv" in names


def test_collect_includes_staticqu_wt_save_csv(tmp_path: Path) -> None:
    """静态QU 连续录波在 wt_save/QU_curve*.csv，须能被结案收集。"""
    import os
    import time

    job_id = 77
    write_result(
        tmp_path,
        job_id,
        {
            "status": "success",
            "result_summary": {"elapsed_sec": 420, "testType": "静态QU"},
        },
    )
    wt = tmp_path / "wt_save"
    wt.mkdir(parents=True)
    csv = wt / "QU_curve.csv"
    csv.write_text("t,U,Q\n1,230,0\n", encoding="utf-8")
    old = wt / "QU_curve_old.csv"
    old.write_text("t,U,Q\n0,0,0\n", encoding="utf-8")
    os.utime(old, (time.time() - 86400, time.time() - 86400))
    files = collect_report_files(
        tmp_path,
        job_id,
        {"result_summary": {"elapsed_sec": 420, "testType": "静态QU"}},
    )
    names = {p.name for p in files}
    assert "QU_curve.csv" in names
    assert "QU_curve_old.csv" not in names


def test_collect_keeps_only_latest_qcap_csv(tmp_path: Path) -> None:
    job_id = 128
    save = tmp_path / "save"
    save.mkdir()
    body = "Time [s],P\n" + "\n".join(f"{i},1000" for i in range(5))
    for name in ("QCap_BR_193903.csv", "QCap_BR_222708.csv", "QCap_BR_224530.csv"):
        (save / name).write_text(body, encoding="utf-8")
    write_result(
        tmp_path,
        job_id,
        {"status": "failed", "result_summary": {"elapsed_sec": 300}},
    )
    files = collect_report_files(
        tmp_path,
        job_id,
        {
            "result_summary": {
                "elapsed_sec": 300,
                "testType": "reactiveqcap",
                "widgets": {"textEdit_SavePath": str(save)},
                "report_files": [str(save / "QCap_BR_224530.csv")],
            }
        },
    )
    names = {p.name for p in files}
    assert "QCap_BR_224530.csv" in names
    assert "QCap_BR_222708.csv" not in names
    assert "QCap_BR_193903.csv" not in names


def test_collect_includes_recent_flicker_image(tmp_path: Path) -> None:
    import os
    import time

    job_id = 8
    write_result(
        tmp_path,
        job_id,
        {"status": "success", "result_summary": {"elapsed_sec": 60, "testType": "flicker"}},
    )
    img_dir = tmp_path / "wt_save"
    img_dir.mkdir(parents=True)
    img = img_dir / "flicker_e1.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    old = img_dir / "old_flicker.png"
    old.write_bytes(b"\x89PNG\r\n\x1a\n")
    os.utime(old, (time.time() - 86400, time.time() - 86400))
    other = tmp_path / "command_save_files" / "job_1"
    other.mkdir(parents=True)
    (other / "other_job.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    files = collect_report_files(
        tmp_path,
        job_id,
        {"result_summary": {"elapsed_sec": 60, "testType": "flicker"}},
    )
    names = {p.name for p in files}
    assert "flicker_e1.png" in names
    assert "old_flicker.png" not in names
    assert "other_job.png" not in names


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        test_collect_includes_result_and_listed(root)
        test_collect_includes_recent_csv(root)
    print("reports collect PASS")
