# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from utils.iot_sim_overload import (
    build_overload_sim_plan,
    generate_overload_series,
    plant_sim_overload_csv,
    write_overload_csv,
)


def test_plan_from_nested_widgets(monkeypatch):
    monkeypatch.setenv("SOLAR_SIM_TARGET_WALL_SEC", "30")
    job = {
        "params": {
            "widgets": {
                "textEdit_S1_AC_VOLT": "230",
                "textEdit_S1_ACWaitTIME": "3",
                "comboBox_S1_ACWaitTIME": "秒",
                "textEdit_S1_TIME": "5",
                "comboBox_S1_TIME": "分钟",
                "textEdit_S3_TIME_2": "90",
                "comboBox_S3_TIME_2": "分钟",
                "analysis_Pn": "10000",
                "_overloadLoadPct": "100",
                "_overloadHoldMin": "90",
            }
        }
    }
    plan = build_overload_sim_plan(job)
    assert plan.un == 230
    assert plan.pn == 10000
    assert plan.ac_wait_s == 3
    assert plan.s1_stabilize_s == 300
    assert plan.hold_s == 5400
    assert plan.wall_scale > 1


def test_generate_and_write_csv(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SOLAR_SIM_SAMPLE_DT_SEC", "60")
    monkeypatch.setenv("SOLAR_SIM_TARGET_WALL_SEC", "10")
    job = {
        "widgets": {
            "analysis_Pn": 10000,
            "textEdit_S1_AC_VOLT": 230,
            "textEdit_S1_ACWaitTIME": 2,
            "comboBox_S1_ACWaitTIME": "秒",
            "textEdit_S1_TIME": 1,
            "comboBox_S1_TIME": "分钟",
            "_overloadHoldMin": 2,
            "comboBox_S3_TIME_2": "分钟",
        }
    }
    csv_path, plan, rows = plant_sim_overload_csv(job, tmp_path / "sim")
    assert csv_path.is_file()
    assert plan.hold_s == 120
    assert len(rows) >= 3
    text = csv_path.read_text(encoding="utf-8")
    assert "P-SIGMA" in text
    assert "Time [s]" in text
