# -*- coding: utf-8 -*-
"""同一组勾选，四种 WT 必须发出各自认识的 NUMERIC 命令。"""
from utils.live_measure_read import items_for_wt_checks

_CHECKS = {
    "checkBox_SetElement1": "1",
    "checkBox_SetElement6": "1",
    "checkBox_SetSigma": "1",
    "checkBox_SetU": "1",
    "checkBox_SetI": "1",
    "checkBox_SetP": "1",
    "checkBox_SetLambda": "1",
    "checkBox_SetFreqU": "1",
    "checkBox_SetUk": "1",
    "checkBox_SetUfnd": "1",
    "textEdit_SetStart": "1",
    "textEdit_SetStop": "1",
}


def test_wt3000_uses_u_total_not_urms():
    items = items_for_wt_checks(_CHECKS, "3000")
    assert "U,1,TOTAL" in items
    assert "I,SIGMA,TOTAL" in items
    assert "P,1,TOTAL" in items
    assert "LAMBDA,1,TOTAL" in items
    assert "FU,1" in items
    assert "U,1,1" in items
    assert "URMS,1" not in items
    assert "UK,1,1" not in items


def test_wt1800_and_1806_use_urms_without_total():
    for model in ("1800", "1806"):
        items = items_for_wt_checks(_CHECKS, model)
        assert "URMS,1" in items
        assert "URMS,6" in items
        assert "IRMS,SIGMA" in items
        assert "P,1" in items
        assert "LAMBDA,SIGMA" in items
        assert "FU,1" in items
        assert "UK,1,1" in items
        assert "UFND,1" in items
        assert "U,1,TOTAL" not in items
        assert "U,1,1" not in items


def test_wt5000_uses_urms_and_fundamental():
    items = items_for_wt_checks(_CHECKS, "5000")
    assert "URMS,1" in items
    assert "UFND,1" in items
    assert "UFND,SIGMA" in items
    assert "UK,1,1" in items
    assert "U,1,TOTAL" not in items
