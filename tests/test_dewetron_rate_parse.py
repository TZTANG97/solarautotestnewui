# -*- coding: utf-8 -*-
"""德威创 :RATE? 解析：禁止把 NUM ITEMs 残包抠成 3ms。"""

from devices.dewetron_data_collector import parse_rate_ms, scpi_poll_interval_s


def test_parse_rate_ms_normal():
    assert parse_rate_ms("100") == 100
    assert parse_rate_ms("100ms") == 100
    assert parse_rate_ms("0.1") == 100
    assert parse_rate_ms("1.0E-1") == 100
    assert parse_rate_ms("Default") == 100


def test_parse_rate_ms_rejects_num_items_echo():
    garbage = (
        ':NUM:ITEMS "ABS-TIME","U3_tRMS@POWER/0","U1_tRMS@POWER/0",'
        '"U2_tRMS@POWER/0","I1_tRMS@POWER/0"'
    )
    # 旧逻辑会从 U3 抠出 3 → 3ms 狂抽
    assert parse_rate_ms(garbage, allow_default=False) is None
    assert parse_rate_ms(garbage, default_ms=100) == 100


def test_scpi_poll_interval_follows_ms():
    assert abs(scpi_poll_interval_s(100) - 0.1) < 1e-9
    assert abs(scpi_poll_interval_s(0) - 0.1) < 1e-9
