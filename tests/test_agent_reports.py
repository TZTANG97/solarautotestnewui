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


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        test_collect_includes_result_and_listed(Path(d))
    print("reports collect PASS")
