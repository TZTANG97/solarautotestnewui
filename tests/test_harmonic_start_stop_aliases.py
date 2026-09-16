# -*- coding: utf-8 -*-
from enums.wt_auto_enums import (
    START_AND_STOP_ALIASES,
    START_AND_STOP_COORD,
    START_AND_STOP_LIST_INDEX,
)


def test_start_stop_aliases_map_zero_to_dc():
    assert START_AND_STOP_ALIASES["0"] == "DC"
    assert START_AND_STOP_ALIASES["51"] == "50"
    assert START_AND_STOP_ALIASES["dc".upper()] == "DC" or START_AND_STOP_ALIASES.get("DC") == "DC"
    for key in ("DC", "1", "50"):
        assert key in START_AND_STOP_COORD
        assert key in START_AND_STOP_LIST_INDEX
    # Total 是第 0 项；DC=1、数字 n=n+1、50=51
    assert START_AND_STOP_LIST_INDEX["DC"] == 1
    assert START_AND_STOP_LIST_INDEX["1"] == 2
    assert START_AND_STOP_LIST_INDEX["50"] == 51
    assert START_AND_STOP_COORD["DC"][1] == 48
    assert START_AND_STOP_COORD["50"][1] == -51 * 43


def test_harmonic_six_point_wait_estimate():
    from utils.time_helpers import SetTimeFunction

    startup = SetTimeFunction(5, "分钟")
    acq = SetTimeFunction(10, "分钟")
    # 0.1s units → minutes
    total_min = (startup + 6 * acq) / 10.0 / 60.0
    assert abs(total_min - 65.0) < 1e-6
