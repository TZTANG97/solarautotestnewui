# -*- coding: utf-8 -*-
"""电压适应性：巴西 5.4.21 更新率扫压冒烟。"""
from utils.voltage_adaptability_commands import build_volt_step_list
from utils.time_helpers import SetTimeFunction


def test_set_time_hours():
    assert SetTimeFunction(1, "小时") == 36000
    assert SetTimeFunction(1, "分钟") == 600


def test_build_volt_step_list_rate_sweep():
    # 230→253，1s，20步/秒
    steps = build_volt_step_list("230", "253", 1.0, 20.0, use_rate=True)
    assert steps[0] == "230"
    assert steps[-1] == "253"
    assert len(steps) >= 20


def test_build_volt_step_list_no_rate_single_point():
    assert build_volt_step_list("230", "253", 10.0, 20.0, use_rate=False) == ["230"]
