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


def test_map_it_cei_harmonic_beide_cei016():
    """意大利 CEI 0-16 → 北德包 + 3.1（图喆/麦田报告，非南德 TDS）。"""
    t = resolve_analysis_target(test_type="harmonic", solar_standard="it_cei")
    assert t is not None
    assert t["standard_pack"] == "CEI_Nbis_BeiDe"
    assert t["test_code"] == "3.1"


def test_map_it_cei_flicker_beide_3_3():
    t = resolve_analysis_target(test_type="flicker", solar_standard="it_cei")
    assert t is not None
    assert t["standard_pack"] == "CEI_Nbis_BeiDe"
    assert t["test_code"] == "3.3"


def test_map_en50549_uses_50549_pack():
    """en50549 → CEI_Nbis_BeiDe_50549；de_vde 仍走北德 0-21。"""
    t = resolve_analysis_target(test_type="flicker", solar_standard="en50549")
    assert t is not None
    assert t["standard_pack"] == "CEI_Nbis_BeiDe_50549"
    assert t["test_code"] == "5.7.2.3.3"
    t2 = resolve_analysis_target(test_type="flicker", solar_standard="de_vde")
    assert t2["standard_pack"] == "CEI_Nbis_BeiDe"
    assert t2["test_code"] == "21.3c"


def test_map_en50549_core_codes():
    assert resolve_analysis_target(
        test_type="voltprotect10min", solar_standard="en50549"
    )["test_code"] == "5.8.3.3"
    assert resolve_analysis_target(test_type="voltprotect", solar_standard="en50549")[
        "test_code"
    ] == "5.8.3.3"
    # IOT「ROCOF保护」→ 5.8.3.4.1；复位 → 5.8.3.4.2
    assert resolve_analysis_target(test_type="rocof", solar_standard="en50549")[
        "test_code"
    ] == "5.8.3.4.1"
    assert resolve_analysis_target(test_type="rocofprotect", solar_standard="en50549")[
        "test_code"
    ] == "5.8.3.4.1"
    assert resolve_analysis_target(test_type="rocofreset", solar_standard="en50549")[
        "test_code"
    ] == "5.8.3.4.2"
    assert resolve_analysis_target(test_type="phasejump", solar_standard="en50549")[
        "test_code"
    ] == "5.3.2"
    assert resolve_analysis_target(test_type="lvrt", solar_standard="en50549")[
        "test_code"
    ] == "5.3.3"
    assert resolve_analysis_target(
        test_type="frequencyadaptability", solar_standard="en50549"
    )["test_code"] == "5.4.3"
    assert resolve_analysis_target(test_type="reactiveqcap", solar_standard="en50549")[
        "test_code"
    ] == "reactive.qcap"
    assert resolve_analysis_target(test_type="reactiveqacc", solar_standard="en50549")[
        "test_code"
    ] == "5.5.2.3.2"
    assert resolve_analysis_target(test_type="fixedq", solar_standard="en50549")[
        "test_code"
    ] == "5.5.2.3.2"
    assert resolve_analysis_target(test_type="ovuf", solar_standard="en50549")[
        "test_code"
    ] == "5.8.3.2"
    assert resolve_analysis_target(test_type="reconnect", solar_standard="en50549")[
        "test_code"
    ] == "5.9"
    assert resolve_analysis_target(test_type="activep", solar_standard="en50549")[
        "test_code"
    ] == "5.10.3.2"
    # 50549 包无谐波处理器：不得回落到 NanDe 默认码
    assert resolve_analysis_target(test_type="harmonic", solar_standard="en50549") is None
    assert resolve_analysis_target(test_type="overload", solar_standard="en50549") is None
    # 三相不平衡暂无 IOT testType
    assert resolve_analysis_target(test_type="unbalance", solar_standard="en50549") is None


def test_map_nande_activep_voltageadapt():
    assert resolve_analysis_target(test_type="activep", solar_standard="thai")[
        "test_code"
    ] == "active.power.control"
    assert resolve_analysis_target(
        test_type="voltageadaptability", solar_standard="thai"
    )["test_code"] == "operating.voltage.range"


def test_map_it_cei_rocof():
    t = resolve_analysis_target(test_type="rocof", solar_standard="it_cei")
    assert t["standard_pack"] == "CEI_Nbis_BeiDe"
    assert t["test_code"] == "A.4.3.4"


def test_no_cross_pack_default_for_en50549_only_types():
    """rocof/phasejump/lvrt/voltprotect 不得用默认码落到 thai/巴西。"""
    for tt in ("rocof", "phasejump", "lvrt", "voltprotect10min", "voltprotect"):
        assert resolve_analysis_target(test_type=tt, solar_standard="thai") is None
        assert resolve_analysis_target(test_type=tt, solar_standard="br_ord140") is None
    # de_vde 暂无真 VDE ROCOF 条款，不挂 CEI0-16 的 A.4.3.4
    assert resolve_analysis_target(test_type="rocof", solar_standard="de_vde") is None
    assert resolve_analysis_target(test_type="phasejump", solar_standard="de_vde") is None


def test_phase1_alias_voltprotect_normalized():
    from utils.iot_data_analysis_map import normalize_test_type_for_analysis, PHASE1_AUTO_TESTS

    assert normalize_test_type_for_analysis("voltprotect") == "voltprotect10min"
    assert normalize_test_type_for_analysis("voltprotect") in PHASE1_AUTO_TESTS


def test_phase1_set():
    assert "overload" in PHASE1_AUTO_TESTS
    assert "harmonic" in PHASE1_AUTO_TESTS
    assert "flicker" in PHASE1_AUTO_TESTS
    # 二期巴西扩面
    assert "activep" in PHASE1_AUTO_TESTS
    assert "voltageadaptability" in PHASE1_AUTO_TESTS
    assert "staticmppt" in PHASE1_AUTO_TESTS
    # EN50549 / 北德补充
    assert "voltprotect10min" in PHASE1_AUTO_TESTS
    assert "phasejump" in PHASE1_AUTO_TESTS
    assert "lvrt" in PHASE1_AUTO_TESTS
    assert "rocof" in PHASE1_AUTO_TESTS


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


def test_collect_flicker_analysis_aliases():
    p = _collect_analysis_params(
        {
            "widgets": {
                "analysis_Sk_fic": "800",
                "analysis_reconnect_time": "300",
            }
        }
    )
    assert p["Sk_fic"] == 800
    assert p["reconnect_time"] == 300


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


def test_loads_json_object_tolerates_extra_data():
    """并发写坏的 headless_result.json：Extra data 时取第一段对象。"""
    from utils.iot_data_analysis_bridge import _loads_json_object

    raw = (
        '{\n  "success": true,\n  "message": "ok",\n  "output_files": []\n}\n'
        '{\n  "success": false,\n  "message": "dup"\n}\n'
    )
    obj = _loads_json_object(raw)
    assert obj.get("success") is True
    assert obj.get("message") == "ok"
