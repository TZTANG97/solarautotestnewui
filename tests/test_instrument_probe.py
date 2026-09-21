# -*- coding: utf-8 -*-
from agent.instrument_probe import probe_one_instrument


def test_probe_one_pending():
    r = probe_one_instrument({"resource": "pending:ac", "slot": "ac"})
    assert r["connected"] is False
    assert "pending" in (r["error"] or "").lower() or "无效" in (r["error"] or "")


def test_probe_one_tcp_fail(monkeypatch):
    import agent.instrument_probe as mod

    monkeypatch.setattr(
        "utils.device_discovery.tcp_open",
        lambda host, port, timeout=0.8: False,
        raising=False,
    )
    # patch via probe_one importing inside — mock at module used after import
    import utils.device_discovery as dd

    monkeypatch.setattr(dd, "tcp_open", lambda host, port, timeout=0.8: False)
    monkeypatch.setattr(dd, "probe_scpi_idn", lambda host, port, timeout=0.8: "")

    r = probe_one_instrument({"resource": "10.9.9.9:5025", "slot": "ac", "kind": "ac"})
    assert r["connected"] is False
    assert "TCP" in (r["error"] or "")


def test_probe_one_tcp_ok_modbus(monkeypatch):
    import utils.device_discovery as dd

    monkeypatch.setattr(dd, "tcp_open", lambda host, port, timeout=0.8: True)
    monkeypatch.setattr(dd, "probe_scpi_idn", lambda host, port, timeout=0.8: "SHOULD_NOT")

    r = probe_one_instrument({"resource": "10.0.0.5:502", "slot": "dc1", "kind": "dc", "brand": "itech"})
    assert r["connected"] is True
    assert r["error"] == ""
