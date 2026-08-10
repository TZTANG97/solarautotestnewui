# -*- coding: utf-8 -*-
"""无功注入：P×Q 命令构建。"""

from utils.reactive_qin_commands import (
    build_reactive_qin_plan,
    format_setpoint_tag,
    parse_ladder,
)


def test_parse_and_tag():
    assert parse_ladder("-100,-50,50,100") == [-100.0, -50.0, 50.0, 100.0]
    assert format_setpoint_tag(-50) == "m50"


def test_filename_prefix_qin():
    class U:
        pass

    # smoke: module exports plan builder
    assert callable(build_reactive_qin_plan)
