# -*- coding: utf-8 -*-
from utils.wt_measure_aliases import expand_wt_measure_checks


def test_u_and_i_copy_onto_wt5000_names():
    out = expand_wt_measure_checks(
        {
            "checkBox_SetU": True,
            "checkBox_SetI": True,
            "checkBox_SetP": True,
            "checkBox_SetLambda": False,
        }
    )
    assert out["checkBox_SetUrms"] is True
    assert out["checkBox_SetIrms"] is True
    assert out["checkBox_SetPF"] is False
    assert out["checkBox_SetP"] is True
    assert "checkBox_SetUrange" not in out


def test_existing_both_sides_are_not_overwritten():
    out = expand_wt_measure_checks(
        {"checkBox_SetU": True, "checkBox_SetUrms": False}
    )
    assert out["checkBox_SetU"] is True
    assert out["checkBox_SetUrms"] is False
