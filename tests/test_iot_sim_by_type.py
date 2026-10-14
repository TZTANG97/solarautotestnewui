# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from utils.iot_sim_by_type import plant_sim_harmonic_csv, plant_sim_csv_for_job
from utils.iot_data_analysis_map import resolve_analysis_target


def test_harmonic_sim_files(tmp_path: Path):
    job = {
        "testType": "harmonic",
        "params": {
            "widgets": {
                "solarStandard": "it_cei",
                "analysis_Pn": "10000",
                "analysis_Un": "230",
            }
        },
    }
    dest = plant_sim_harmonic_csv(job, tmp_path / "sim")
    assert (dest / "33%.csv").is_file()
    assert (dest / "66%.csv").is_file()
    assert (dest / "100%.csv").is_file()
    assert (dest / "voltage harmonic.csv").is_file()
    assert not list(dest.glob("sample_overload*.csv"))


def test_plant_dispatch_not_overload_for_harmonic(tmp_path: Path):
    job = {"testType": "harmonic", "widgets": {"analysis_Pn": 10, "analysis_Un": 230}}
    dest = plant_sim_csv_for_job(job, tmp_path / "h")
    assert (dest / "33%.csv").is_file()
    assert not (dest / "sample_overload.csv").exists()


def test_map_harmonic_it_cei():
    t = resolve_analysis_target(test_type="harmonic", solar_standard="it_cei")
    assert t["standard_pack"] == "CEI_Nbis_NanDe"
    assert t["test_code"] == "harmonic"
