# -*- coding: utf-8 -*-
from utils.active_p_commands import format_setpoint_tag, parse_ladder


def test_parse_p_ladder():
    assert parse_ladder("100,80, 60，0") == [100.0, 80.0, 60.0, 0.0]
    assert format_setpoint_tag(80) == "80"
