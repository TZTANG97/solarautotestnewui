# -*- coding: utf-8 -*-
from utils.live_measure_chart import group_series, short_label, y_range


def test_group_series_by_quantity():
    names = [
        "U,1,TOTAL",
        "I,1,TOTAL",
        "P,SIGMA,TOTAL",
        "LAMBDA,1,TOTAL",
        "FU,1",
        "AI 1/U1",
        "AI 1/I1",
        "P_t@POWER/0",
        "Q_fund@POWER/0",
        "PF@POWER/0",
        "F@POWER/0",
    ]
    groups = dict(group_series(names))
    assert "U,1,TOTAL" in groups["电压 U"]
    assert "AI 1/U1" in groups["电压 U"]
    assert "I,1,TOTAL" in groups["电流 I"]
    assert "AI 1/I1" in groups["电流 I"]
    assert "P,SIGMA,TOTAL" in groups["功率 P/S/Q"]
    assert "P_t@POWER/0" in groups["功率 P/S/Q"]
    assert "Q_fund@POWER/0" in groups["功率 P/S/Q"]
    assert "LAMBDA,1,TOTAL" in groups["功率因数 / 相位"]
    assert "PF@POWER/0" in groups["功率因数 / 相位"]
    assert "FU,1" in groups["频率"]
    assert "F@POWER/0" in groups["频率"]


def test_short_label_and_y_range():
    assert short_label("U,1,TOTAL") == "U1"
    assert short_label("U,SIGMA,TOTAL") == "UΣ"
    assert short_label("AI 1/U1") == "U1"
    assert short_label("P_t@POWER/0") == "P_t"
    assert short_label("PF@POWER/0") == "PF"
    low, high = y_range([229.0, 231.0])
    assert low < 229.0
    assert high > 231.0
