# -*- coding: utf-8 -*-
"""试点全链路冒烟：overload + br_ord140 → BRAZIL_140/5.4.2 → 出报告文件。"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from utils.iot_data_analysis_bridge import run_analysis_after_job
from utils.iot_data_analysis_map import PHASE1_PILOT, resolve_analysis_target

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "brazil_overload_542"
ANALYSIS_ROOT = Path(r"E:\MyProject\SolarTestDataAnalysisApp")


@pytest.mark.skipif(
    not (ANALYSIS_ROOT / "CEI" / "run_headless.py").is_file(),
    reason="本机无 SolarTestDataAnalysisApp",
)
def test_overload_brazil_headless_e2e(tmp_path: Path, monkeypatch):
    assert FIXTURE_DIR.is_dir()
    assert list(FIXTURE_DIR.glob("*.csv")), "缺少样例 CSV"

    target = resolve_analysis_target(
        test_type=PHASE1_PILOT["test_type"],
        solar_standard=PHASE1_PILOT["solar_standard"],
    )
    assert target is not None
    assert target["standard_pack"] == "BRAZIL_140"
    assert target["test_code"] == "5.4.2"

    monkeypatch.setenv("SOLAR_DATA_ANALYSIS_ROOT", str(ANALYSIS_ROOT))

    # 模拟台架仓库根：把样例 CSV 放进 command_data
    data_dir = tmp_path / "command_save_files" / "command_data" / "overload_job1"
    data_dir.mkdir(parents=True)
    for src in FIXTURE_DIR.glob("*.csv"):
        (data_dir / src.name).write_bytes(src.read_bytes())

    job = {
        "id": 90001,
        "testType": "overload",
        "widgets": {
            "solarStandard": "br_ord140",
            "analysis_Pn": 10000,
            "analysis_SeMax": 10000,
        },
        "params": {},
    }
    result = {
        "status": "success",
        "result_summary": {
            "testType": "overload",
            "analysis_input_dir": str(data_dir),
            "report_files": [{"path": str(p), "name": p.name} for p in data_dir.glob("*.csv")],
        },
    }

    info = run_analysis_after_job(repo_root=tmp_path, job=job, result=result, timeout_sec=120)
    assert info.get("ran") is True, info
    assert info.get("success") is True, json.dumps(info, ensure_ascii=False, default=str)[:2000]

    files = info.get("output_files") or []
    assert files, "应产出报告文件"
    suffixes = {Path(f).suffix.lower() for f in files}
    assert ".csv" in suffixes or ".docx" in suffixes or ".xlsx" in suffixes

    listed = (result.get("result_summary") or {}).get("report_files") or []
    assert any(
        (isinstance(x, dict) and x.get("kind") == "analysis_report")
        or (isinstance(x, dict) and "analysis_reports" in str(x.get("path") or ""))
        for x in listed
    ), listed
