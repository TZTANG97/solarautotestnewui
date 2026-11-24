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


def test_collect_drops_dew_config_xml_and_sidecar(tmp_path: Path) -> None:
    """德威创配置 XML / sidecar / headless_result 不得进实验报告上传。"""
    job_id = 139
    dew = tmp_path / "dewetron_save"
    dew.mkdir()
    (dew / "dewetron_20261111_19.xml").write_bytes(b"<xml/>" * 100)
    (dew / ".last_dew_export.json").write_text('{"csv":"x"}', encoding="utf-8")
    (dew / "reactive-qcap_ok.csv").write_text("t,p\n0,1\n1,2\n", encoding="utf-8")
    (dew / "keep.dmd").write_bytes(b"dmd" * 100)
    ana = tmp_path / "command_save_files" / "analysis_reports" / f"job_{job_id}_1"
    ana.mkdir(parents=True)
    (ana / "headless_result.json").write_text('{"success":true}', encoding="utf-8")
    (ana / "无功能力范围.xlsx").write_bytes(b"PK\x03\x04fake")
    write_result(
        tmp_path,
        job_id,
        {"status": "success", "result_summary": {"elapsed_sec": 60}},
    )
    files = collect_report_files(
        tmp_path,
        job_id,
        {
            "result_summary": {
                "elapsed_sec": 60,
                "testType": "reactiveqcap",
                "analysis_input_dir": str(dew),
                "widgets": {"lineEdit_DEW_SaveDir": str(dew)},
                "report_files": [
                    str(dew / "reactive-qcap_ok.csv"),
                    str(dew / "keep.dmd"),
                    str(ana / "无功能力范围.xlsx"),
                    str(dew / "dewetron_20261111_19.xml"),
                    str(dew / ".last_dew_export.json"),
                    str(ana / "headless_result.json"),
                ],
            }
        },
    )
    names = {p.name for p in files}
    assert "reactive-qcap_ok.csv" in names
    assert "keep.dmd" in names
    assert "无功能力范围.xlsx" in names
    assert "dewetron_20261111_19.xml" not in names
    assert ".last_dew_export.json" not in names
    assert "headless_result.json" not in names


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


def test_collect_skips_older_recordings_in_shared_save(tmp_path: Path) -> None:
    """保存目录里上一次的 CSV 即使刚被改过时间，也不能算进本单。"""
    import os
    import time
    from datetime import datetime, timedelta

    job_id = 154
    save = tmp_path / "wt_save"
    save.mkdir()
    now = datetime.now().replace(microsecond=0)
    fresh = now.strftime("%H%M%S")
    old_clock = (now - timedelta(hours=3)).strftime("%H%M%S")
    if old_clock == fresh:
        old_clock = "000000" if fresh != "000000" else "030000"
    body = "Time [s],Urms-1,P-SIGMA\n0,230,1000\n"
    fresh_p = save / f"Pdisp_BR_{fresh}.csv"
    bare = save / "Pdisp_BR.csv"
    fresh_pf = save / f"FixedPF_P100_{fresh}.csv"
    old_pf = save / f"FixedPF_P100_{old_clock}.csv"
    for path in (fresh_p, bare, fresh_pf, old_pf):
        path.write_text(body, encoding="utf-8")
    os.utime(bare, None)
    os.utime(old_pf, None)
    write_result(
        tmp_path,
        job_id,
        {"status": "success", "result_summary": {"elapsed_sec": 120}},
    )
    files = collect_report_files(
        tmp_path,
        job_id,
        {
            "result_summary": {
                "elapsed_sec": 120,
                "started_at": time.time() - 60,
                "widgets": {"textEdit_SavePath": str(save)},
            }
        },
    )
    names = {p.name for p in files}
    assert fresh_p.name in names
    assert fresh_pf.name in names
    assert bare.name not in names
    assert old_pf.name not in names


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
