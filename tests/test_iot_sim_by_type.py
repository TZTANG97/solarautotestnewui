# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from utils.iot_sim_by_type import plant_sim_harmonic_csv, plant_sim_csv_for_job
from utils.iot_data_analysis_map import resolve_analysis_target, PHASE1_AUTO_TESTS


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
    lines = (dest / "100%.csv").read_text(encoding="utf-8-sig").strip().splitlines()
    assert len(lines) >= 10


def test_plant_dispatch_not_overload_for_harmonic(tmp_path: Path):
    job = {"testType": "harmonic", "widgets": {"analysis_Pn": 10, "analysis_Un": 230}}
    dest = plant_sim_csv_for_job(job, tmp_path / "h")
    assert (dest / "33%.csv").is_file()
    assert not (dest / "sample_overload.csv").exists()


def test_map_harmonic_it_cei():
    t = resolve_analysis_target(test_type="harmonic", solar_standard="it_cei")
    assert t["standard_pack"] == "CEI_Nbis_BeiDe"
    assert t["test_code"] == "3.1"


def test_map_brazil_phase1_codes():
    assert resolve_analysis_target(test_type="flicker", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.16"
    assert resolve_analysis_target(test_type="harmonic", solar_standard="br_ord140")[
        "test_code"
    ] == "5.10"
    assert resolve_analysis_target(test_type="dccomponent", solar_standard="br_ord140")[
        "test_code"
    ] == "5.9"
    assert resolve_analysis_target(test_type="fixedpf", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.11"
    assert resolve_analysis_target(test_type="reconnect", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.22"
    assert resolve_analysis_target(test_type="ovuf", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.15"
    assert resolve_analysis_target(test_type="reactiveqin", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.13"
    assert "reactiveqin" in PHASE1_AUTO_TESTS
    assert resolve_analysis_target(test_type="activep", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.23"
    assert "activep" in PHASE1_AUTO_TESTS


def test_sim_phase2_brazil_types(tmp_path: Path):
    base = {"widgets": {"analysis_Pn": 10000, "analysis_Un": 230}}
    ap = plant_sim_csv_for_job({**base, "testType": "activep"}, tmp_path / "ap")
    assert (ap / "sample_activep.csv").is_file()
    assert "P-SIGMA" in (ap / "sample_activep.csv").read_text(encoding="utf-8-sig")
    assert not (ap / "sample_overload.csv").exists()

    fq = plant_sim_csv_for_job({**base, "testType": "fixedq"}, tmp_path / "fq")
    assert (fq / "sample_fixedq.csv").is_file()

    va = plant_sim_csv_for_job({**base, "testType": "voltageadaptability"}, tmp_path / "va")
    assert (va / "sample_voltageadaptability.csv").is_file()

    gp = plant_sim_csv_for_job({**base, "testType": "guopinjiangzai"}, tmp_path / "gp")
    assert (gp / "sample_guopinjiangzai.csv").is_file()

    sm = plant_sim_csv_for_job({**base, "testType": "staticmppt"}, tmp_path / "sm")
    assert (sm / "sample_staticmppt.csv").is_file()


def test_sim_dc_flicker_fixedpf_reconnect_ovuf(tmp_path: Path):
    base = {"widgets": {"analysis_Pn": 10000, "analysis_Un": 230}}
    dc = plant_sim_csv_for_job({**base, "testType": "dccomponent"}, tmp_path / "dc")
    assert (dc / "33%.csv").is_file()
    assert "I(k)-1-DC" in (dc / "33%.csv").read_text(encoding="utf-8-sig")

    fl = plant_sim_csv_for_job({**base, "testType": "flicker"}, tmp_path / "fl")
    assert (fl / "sample_flicker.csv").is_file()
    assert "Pst" in (fl / "sample_flicker.csv").read_text(encoding="utf-8-sig")

    pf = plant_sim_csv_for_job({**base, "testType": "fixedpf"}, tmp_path / "pf")
    assert (pf / "pf=1" / "100%.csv").is_file()
    assert (pf / "sample_fixedpf.csv").is_file()

    rc = plant_sim_csv_for_job({**base, "testType": "reconnect"}, tmp_path / "rc")
    assert (rc / "sample_reconnect.csv").is_file()
    lines = (rc / "sample_reconnect.csv").read_text(encoding="utf-8-sig").strip().splitlines()
    assert len(lines) > 100

    ov = plant_sim_csv_for_job({**base, "testType": "ovuf"}, tmp_path / "ov")
    assert (ov / "ovuf_47.5Hz.csv").is_file()
    assert (ov / "ovuf_51.5Hz.csv").is_file()
