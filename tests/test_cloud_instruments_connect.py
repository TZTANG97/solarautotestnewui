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


def test_ac_port_502_is_itech_modbus_not_chroma_scpi():
    """502 是 Modbus。占位品牌或空品牌都不能走 Chroma SCPI，否则桌面会在错误端口上空等。"""
    jobs = prepare_jobs_from_cloud_instruments(
        [
            {
                "slot": "ac",
                "kind": "ac",
                "resource": "192.168.40.210:502",
                "brand": "chroma / itech / bluesight",
            }
        ]
    )
    assert len(jobs) == 1
    _slot, plan, dev = jobs[0]
    assert plan.get("target") == "ac_itech"
    assert plan.get("port") == 502
    assert (dev.protocol or "") == "modbus"


def test_ac_serial_is_chroma_visa_not_modbus():
    jobs = prepare_jobs_from_cloud_instruments(
        [
            {
                "slot": "ac",
                "kind": "ac",
                "resource": "ASRL3::INSTR",
                "brand": "chroma",
            }
        ]
    )
    assert len(jobs) == 1
    _slot, plan, _dev = jobs[0]
    assert plan.get("target") == "ac_visa"
    assert str(plan.get("resource") or "").upper().startswith("ASRL")


def test_failed_session_is_not_connected():
    from utils.iot_auto_connect import apply_prepared_connect_jobs

    called = {"n": 0}

    def _apply(slot, plan, dev):
        called["n"] += 1

    summary = apply_prepared_connect_jobs(
        [("ac", {"target": "ac_itech"}, type("D", (), {"resource": "192.168.40.210:502"})())],
        apply_plan=_apply,
        session_ok=lambda slot: False,
    )
    assert called["n"] == 1
    assert summary["connected"] == []
    assert summary["errors"]
    assert "会话未建立" in summary["errors"][0]
