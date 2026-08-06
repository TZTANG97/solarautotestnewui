# -*- coding: utf-8 -*-
from utils.frequency_adaptability_commands import append_freq_band
from utils.time_helpers import SetTimeFunction


def test_set_time_hours():
    assert SetTimeFunction(1, "小时") == 36000
    assert SetTimeFunction(1, "分钟") == 600


def test_append_freq_band_same_start_end():
    rows = []
    assert append_freq_band(rows, "单相", "50.2", "50.2", 100)
    freqs = [r[2] for r in rows if str(r[2]).startswith("FREQ")]
    assert freqs == ["FREQ 50.2"]
    assert rows[-1][9] == 100


def test_append_freq_band_three_phase_ramp():
    rows = []
    assert append_freq_band(rows, "三相", "51", "52", 200)
    freqs = [r[2] for r in rows if str(r[2]).startswith("FREQ")]
    assert freqs == ["FREQ 51", "FREQ 51", "FREQ 51", "FREQ 52", "FREQ 52", "FREQ 52"]
