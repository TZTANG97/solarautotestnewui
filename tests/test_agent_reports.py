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
    csv_dir = tmp_path / "command_save_files" / "command_data"
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


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        test_collect_includes_result_and_listed(root)
        test_collect_includes_recent_csv(root)
    print("reports collect PASS")
