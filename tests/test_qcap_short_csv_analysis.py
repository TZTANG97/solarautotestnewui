# -*- coding: utf-8 -*-
"""单帧 QCap CSV 不得当成功数据处理输入。"""
from __future__ import annotations

from pathlib import Path

from utils.iot_data_analysis_bridge import (
    _MIN_MEASUREMENT_DATA_ROWS,
    _csv_data_row_count,
    _usable_measurement_csvs,
    run_analysis_after_job,
)
from utils.wt_job_save import continuous_filename_for_test


def test_qcap_alias_maps_chinese_name():
    assert continuous_filename_for_test("无功能力范围") == "QCap_BR"
    assert continuous_filename_for_test("reactiveqcap") == "QCap_BR"


def test_csv_data_row_count_one_frame(tmp_path: Path):
    p = tmp_path / "QCap_BR_221049.csv"
    p.write_text(
        "Time [s],Urms-1,P-SIGMA\n0.0031,230.0,6664.2\n",
        encoding="utf-8-sig",
    )
    assert _csv_data_row_count(p) == 1
    assert _usable_measurement_csvs(tmp_path) == []


def test_csv_data_row_count_enough_rows(tmp_path: Path):
    p = tmp_path / "QCap_BR_ok.csv"
    rows = ["Time [s],Urms-1,P-SIGMA"] + [
        f"{i * 0.1:.1f},230.0,{6000 + i}" for i in range(_MIN_MEASUREMENT_DATA_ROWS)
    ]
    p.write_text("\n".join(rows) + "\n", encoding="utf-8-sig")
    usable = _usable_measurement_csvs(tmp_path)
    assert len(usable) == 1
    assert usable[0][1] == _MIN_MEASUREMENT_DATA_ROWS


def test_run_analysis_rejects_one_frame_csv(tmp_path: Path, monkeypatch):
    csv = tmp_path / "QCap_BR_221049.csv"
    csv.write_text(
        "Time [s],Urms-1,P-SIGMA\n0.0031,230.0,6664.2\n",
        encoding="utf-8-sig",
    )
    monkeypatch.setattr(
        "utils.iot_data_analysis_bridge._analysis_root",
        lambda: tmp_path,
    )
    # 伪造引擎存在，避免「未找到分析引擎」抢先返回
    (tmp_path / "run_headless.py").write_text("# stub\n", encoding="utf-8")
    result = {
        "status": "success",
        "result_summary": {
            "testType": "reactiveqcap",
            "analysis_input_dir": str(tmp_path),
            "report_files": [{"path": str(csv)}],
        },
    }
    job = {
        "id": 126,
        "testType": "reactiveqcap",
        "widgets": {"analysis_Pn": "10000", "solarStandard": "en50549"},
        "params": {},
    }
    info = run_analysis_after_job(repo_root=tmp_path, job=job, result=result)
    assert info.get("ran") is False
    assert info.get("quality") == "too_few_rows"
    assert "数据行不足" in str(info.get("reason") or "")
