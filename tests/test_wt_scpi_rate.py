# -*- coding: utf-8 -*-
"""Unit tests for WT SCPI rate helpers (no instrument required)."""
from devices.wt_scpi_rate import (
    is_serial_resource,
    parse_rate_ms,
    rate_command,
    rates_match_ms,
    serial_too_slow_for_rate,
    snap_rate_ms,
)


def test_parse_rate_ms_variants():
    assert parse_rate_ms("50ms") == 50
    assert parse_rate_ms("100MS") == 100
    assert parse_rate_ms("1s") == 1000
    assert parse_rate_ms("0.05") == 50
    assert parse_rate_ms("5.0E-2") == 50
    assert parse_rate_ms(":RATE 100MS") == 100


def test_snap_and_command():
    assert snap_rate_ms(180) in (100, 200, 250)
    assert rate_command(50) == ":RATE 50MS"
    assert rate_command(1000) == ":RATE 1S"


def test_serial_guard():
    assert is_serial_resource("ASRL6::INSTR")
    assert serial_too_slow_for_rate("ASRL6::INSTR", 50)
    assert not serial_too_slow_for_rate("TCPIP0::192.168.1.10::10001::SOCKET", 50)
    assert rates_match_ms(50, 50)
    assert rates_match_ms(50, 52)
    assert not rates_match_ms(50, 180)
