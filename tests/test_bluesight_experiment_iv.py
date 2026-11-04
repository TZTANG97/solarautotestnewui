# -*- coding: utf-8 -*-
"""蓝点 SAS 曲线换算后，实验直流电源1 四点要跟上。"""
from utils.bluesight_experiment_iv import experiment_dc1_widgets, overlay_experiment_dc1
from utils.status_json_devices import bluesight_iv_fields


def test_sas_curve_becomes_experiment_dc_fields():
    iv = bluesight_iv_fields({"mode": "sas", "pmpp_kw": 12.5, "umpp_v": 750.0, "ff": 0.8})
    fields = experiment_dc1_widgets(iv)
    assert fields["textEdit_S1_DC1_VOLT"] == "750"
    assert fields["textEdit_S1_DC1_PF"] == "100"
    assert abs(float(fields["textEdit_S1_DC1_CURR"]) - (12500.0 / 750.0)) < 1e-3
    assert float(fields["textEdit_S1_DC1_Voc"]) > 750
    assert float(fields["textEdit_S1_DC1_Isc"]) > float(fields["textEdit_S1_DC1_CURR"])


def test_overlay_replaces_dialog_defaults_and_keeps_other_fields():
    iv = bluesight_iv_fields({"mode": "sas", "pmpp_kw": 8.0, "umpp_v": 650.0, "ff": 0.8})
    merged = overlay_experiment_dc1(
        {"textEdit_S1_DC1_VOLT": "400", "textEdit_S1_AC_VOLT": "230", "comboBox_Phase": "三相"},
        iv,
    )
    assert merged["textEdit_S1_DC1_VOLT"] == "650"
    assert merged["textEdit_S1_AC_VOLT"] == "230"
    assert merged["comboBox_Phase"] == "三相"
    assert merged["textEdit_S1_DC1_PF"] == "100"


def test_empty_sas_does_not_clear_existing_dc():
    merged = overlay_experiment_dc1(
        {"textEdit_S1_DC1_VOLT": "400"},
        {"vmp": "", "imp": "", "voc": "", "isc": "", "pf": ""},
    )
    assert merged["textEdit_S1_DC1_VOLT"] == "400"
