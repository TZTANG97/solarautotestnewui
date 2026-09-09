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
    # Chroma 0.1 V：不应出现两位以上小数
    for s in steps:
        assert "." not in s or len(s.split(".")[1]) <= 1


def test_build_volt_step_list_quantized_0_1v():
    steps = build_volt_step_list("230", "230.5", 1.0, 50.0, use_rate=True)
    assert all(s in ("230", "230.1", "230.2", "230.3", "230.4", "230.5") or float(s) == round(float(s), 1) for s in steps)
    assert not any(len(s.split(".")[1]) > 1 for s in steps if "." in s)


def test_build_volt_step_list_no_rate_single_point():
    assert build_volt_step_list("230", "253", 10.0, 20.0, use_rate=False) == ["230"]
