# -*- coding: utf-8 -*-
"""Smoke: DEWETRON :RATE? scientific-notation must map to ms correctly."""
from devices.dewetron_data_collector import parse_rate_ms, rates_match_ms


def test_default_and_ui_ms():
    assert parse_rate_ms("Default") == 100
    assert parse_rate_ms("100") == 100
    assert parse_rate_ms("100ms") == 100
    assert parse_rate_ms("200") == 200


def test_device_seconds_reply():
    # Device returns seconds; 0.1 s == 100 ms
    assert parse_rate_ms("1.0E-1") == 100
    assert parse_rate_ms(":RATE 1.0E-1") == 100
    assert parse_rate_ms("0.1") == 100
    assert parse_rate_ms("0.2s") == 200
    assert rates_match_ms(100, parse_rate_ms("1.0E-1"))


if __name__ == "__main__":
    test_default_and_ui_ms()
    test_device_seconds_reply()
    print("ok")
