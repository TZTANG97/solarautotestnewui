# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from utils.iot_data_analysis_map import (
    PHASE1_AUTO_TESTS,
    resolve_analysis_target,
)
from utils.iot_data_analysis_bridge import (
    _collect_analysis_params,
    run_analysis_after_job,
)


def test_map_brazil_overload():
    t = resolve_analysis_target(test_type="overload", solar_standard="br_ord140")
    assert t is not None
    assert t["standard_pack"] == "BRAZIL_140"
    assert t["test_code"] == "5.4.2"


def test_map_thai_flicker_nande():
    t = resolve_analysis_target(test_type="flicker", solar_standard="thai")
    assert t is not None
    assert t["standard_pack"] == "CEI_Nbis_NanDe"
    assert t["test_code"] == "voltage.fluctuation"


def test_map_it_cei_harmonic_nande():
    t = resolve_analysis_target(test_type="harmonic", solar_standard="it_cei")
    assert t is not None
    assert t["standard_pack"] == "CEI_Nbis_NanDe"
    assert t["test_code"] == "harmonic"


def test_phase1_set():
    assert "overload" in PHASE1_AUTO_TESTS
    assert "harmonic" in PHASE1_AUTO_TESTS
    assert "flicker" in PHASE1_AUTO_TESTS
    # 二期巴西扩面
    assert "activep" in PHASE1_AUTO_TESTS
    assert "voltageadaptability" in PHASE1_AUTO_TESTS
    assert "staticmppt" in PHASE1_AUTO_TESTS


def test_map_brazil_phase2_codes():
    assert resolve_analysis_target(test_type="activep", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.23"
    assert resolve_analysis_target(
        test_type="voltageadaptability", solar_standard="br_ord140"
    )["test_code"] == "5.4.21"
    assert resolve_analysis_target(
        test_type="frequencyadaptability", solar_standard="br_ord140"
    )["test_code"] == "5.4.20"
    assert resolve_analysis_target(test_type="fixedq", solar_standard="br_ord140")[
        "test_code"
    ] == "5.24"
    assert resolve_analysis_target(test_type="cosphibrazil", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.12"
    assert resolve_analysis_target(test_type="staticmppt", solar_standard="br_ord140")[
        "test_code"
    ] == "5.4.26"
    assert resolve_analysis_target(
        test_type="guopinjiangzai", solar_standard="br_ord140"
    )["test_code"] == "5.4.19"


def test_collect_params_from_job():
    job = {
        "params": {"Pn": "10000", "analysisParams": {"SeMax": 11000}},
        "widgets": {"textEdit_S1_AC_VOLT": "230"},
    }
    p = _collect_analysis_params(job)
    assert p["Pn"] == 10000
    assert p["SeMax"] == 11000
    assert p["Un"] == 230


def test_collect_params_from_nested_widgets():
    """IOT 下发时 widgets / analysis_* 常在 params.widgets。"""
    from utils.iot_data_analysis_bridge import _job_test_type, _job_solar_standard

    job = {
        "params": {
            "testType": "overload",
            "widgets": {
                "solarStandard": "br_ord140",
                "analysis_Pn": "10000",
                "analysis_SeMax": "10000",
            },
        },
    }
    p = _collect_analysis_params(job)
    assert p["Pn"] == 10000
    assert p["SeMax"] == 10000
    assert _job_test_type(job) == "overload"
    assert _job_solar_standard(job, {}) == "br_ord140"


def test_skip_when_not_success(tmp_path: Path):
    info = run_analysis_after_job(
        repo_root=tmp_path,
        job={"testType": "overload", "widgets": {"solarStandard": "br_ord140"}},
        result={"status": "failed", "result_summary": {}},
    )
    assert info["skipped"] is True
    assert info["ran"] is False
