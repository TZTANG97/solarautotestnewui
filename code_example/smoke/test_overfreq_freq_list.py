# -*- coding: utf-8 -*-
"""过频频率 list：解析与命令生成冒烟。"""
from __future__ import annotations

from utils.overfreq_ladder_commands import (
    append_freq_ladder_commands,
    parse_freq_hz_list,
)
from utils.time_helpers import SetTimeFunction


def test_parse_and_many_points():
    freqs = parse_freq_hz_list(
        "50, 50.25,50.7,51.15, 50.7,50.25,50, 50.1,50.2,50.3,"
        "50.4,50.5,50.6,50.8,50.9,51.0,51.1,51.2,51.3,51.4,51.5"
    )
    assert len(freqs) == 21  # >15, no longer capped
    assert freqs[0] == "50"
    assert freqs[3] == "51.15"

    dwell = SetTimeFunction(30.0, "秒")
    rows = []
    steps = []
    points = [(f, "230", dwell) for f in freqs]
    n, _start = append_freq_ladder_commands(rows, steps, "三相", points)
    assert n == 21
    freq_cmds = [r[2] for r in rows if r[1] == "write" and str(r[2]).startswith("FREQ ")]
    # 三相：每点 INST:EDIT ALL + 一次 FREQ（同步改三相）
    assert len(freq_cmds) == 21
    assert "FREQ 51.15" in freq_cmds
    edit_all = [r for r in rows if r[1] == "write" and r[2] == "INST:EDIT ALL"]
    assert len(edit_all) == 21
    waits = [r for r in rows if r[1] == "query" and r[9] not in ("", None)]
    assert len(waits) == 21


if __name__ == "__main__":
    test_parse_and_many_points()
    print("ok")
