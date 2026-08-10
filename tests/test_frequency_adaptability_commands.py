# -*- coding: utf-8 -*-
from utils.frequency_adaptability_commands import build_freq_step_list
from utils.time_helpers import SetTimeFunction


def test_set_time_hours():
    assert SetTimeFunction(1, "小时") == 36000
    assert SetTimeFunction(1, "分钟") == 600


def test_build_freq_step_list_rate_sweep():
    # 50→52，1s，20步/秒 → 步长 0.1
    steps = build_freq_step_list("50", "52", 1.0, 20.0, use_rate=True)
    assert steps[0] == "50"
    assert steps[-1] == "52"
    assert len(steps) >= 20


def test_build_freq_step_list_no_rate_single_point():
    assert build_freq_step_list("50.2", "51.5", 10.0, 20.0, use_rate=False) == ["50.2"]
