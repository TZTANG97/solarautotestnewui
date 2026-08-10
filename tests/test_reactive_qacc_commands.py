# -*- coding: utf-8 -*-
"""无功精度：命令构建冒烟。"""

from utils.reactive_qacc_commands import format_setpoint_tag, parse_ladder


def test_parse_fine_ladder():
    assert parse_ladder("-100,-75,-50,-25,0,25,50,75,100") == [
        -100.0, -75.0, -50.0, -25.0, 0.0, 25.0, 50.0, 75.0, 100.0
    ]
    assert format_setpoint_tag(-75) == "m75"
