"""云端仪器配置 → 连接计划。"""
from utils.iot_auto_connect import prepare_jobs_from_cloud_instruments


def test_prepare_jobs_from_cloud_instruments_ac_dc():
    jobs = prepare_jobs_from_cloud_instruments(
        [
            {"slot": "ac", "kind": "ac", "resource": "10.0.0.1:5025", "brand": "chroma"},
            {"slot": "dc1", "kind": "dc", "resource": "10.0.0.2:5025", "brand": "itech"},
            {"slot": "wt", "kind": "wt", "resource": "10.0.0.3:5025", "brand": ""},
            {"slot": "scope", "kind": "scope", "resource": "pending:scope", "brand": ""},
        ]
    )
    slots = [s for s, _, _ in jobs]
    assert "ac" in slots
    assert "dc1" in slots
    assert "wt" in slots
    assert "scope" not in slots  # pending 跳过
    ac_plan = next(p for s, p, _ in jobs if s == "ac")
    assert ac_plan.get("target") in ("ac_chroma_ip", "ac_itech", "ac_visa")


def test_prepare_skips_empty():
    assert prepare_jobs_from_cloud_instruments([]) == []
    assert prepare_jobs_from_cloud_instruments([{"slot": "ac", "resource": ""}]) == []
