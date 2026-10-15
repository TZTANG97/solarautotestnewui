# -*- coding: utf-8 -*-
"""模拟工况机 runner：落样例 CSV + success，可供结案分析桥接。"""
from __future__ import annotations

from pathlib import Path

from agent.runners.overload import OverloadRunner
from utils.iot_data_analysis_bridge import run_analysis_after_job


def test_sim_bench_plants_csv_and_analysis(tmp_path: Path, monkeypatch):
    analysis_root = Path(r"E:\MyProject\SolarTestDataAnalysisApp")
    if not (analysis_root / "CEI" / "run_headless.py").is_file():
        import pytest

        pytest.skip("本机无 SolarTestDataAnalysisApp")

    monkeypatch.setenv("SOLAR_DATA_ANALYSIS_ROOT", str(analysis_root))
    monkeypatch.setenv("SOLAR_SIM_TARGET_WALL_SEC", "3")
    monkeypatch.setenv("SOLAR_SIM_SAMPLE_DT_SEC", "30")
    runner = OverloadRunner(execution_mode="sim", repo_root=tmp_path)
    job = {
        "id": 92001,
        "testType": "overload",
        "title": "sim overload",
        "widgets": {
            "solarStandard": "br_ord140",
            "analysis_Pn": 10000,
            "analysis_SeMax": 10000,
            "textEdit_S1_ACWaitTIME": "1",
            "comboBox_S1_ACWaitTIME": "秒",
            "textEdit_S1_TIME": "1",
            "comboBox_S1_TIME": "分钟",
            "_overloadHoldMin": "2",
            "comboBox_S3_TIME_2": "分钟",
            "textEdit_S1_AC_VOLT": "230",
        },
        "params": {},
    }
    progress = []
    result = runner.run(job, lambda p, m, s=None: progress.append((p, m, s)))
    assert result["status"] == "success"
    summary = result.get("result_summary") or {}
    assert summary.get("sim_bench") is True
    data_dir = Path(str(summary.get("analysis_input_dir") or ""))
    assert data_dir.is_dir()
    assert list(data_dir.glob("*.csv"))

    info = run_analysis_after_job(
        repo_root=tmp_path, job=job, result=result, timeout_sec=120
    )
    assert info.get("success") is True, info
    assert info.get("output_files")
