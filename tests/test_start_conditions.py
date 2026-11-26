# -*- coding: utf-8 -*-
from utils.start_conditions import compact_start_condition


def test_compact_keeps_only_filled_channels():
    item = compact_start_condition(
        "过欠压_过欠频",
        {
            "comboBox_S1_AC_2": "单相",
            "textEdit_S1_AC_VOLT": "220",
            "textEdit_S1_AC_VOLT_2": "",
            "textEdit_S1_AC_FR": "60",
            "solarStandard": "en50549",
            "checkBox_S1_DC1": True,
            "textEdit_S1_DC1_VOLT": "360",
            "textEdit_S1_DC1_CURR": "8",
            "textEdit_S1_DC1_Voc": "420",
            "textEdit_S1_DC1_Isc": "9.5",
            "textEdit_S1_DC1_PF": "80",
            "checkBox_S1_DC2": False,
            "textEdit_S1_DC2_VOLT": "400",
        },
    )
    labels = {row["label"]: row["value"] for row in item["items"]}
    assert item["name"] == "过欠压_过欠频"
    assert labels["交流相数"] == "单相"
    assert labels["交流电压"] == "220"
    assert "交流电压2" not in labels
    assert labels["频率"] == "60"
    assert labels["标准"] == "en50549"
    assert labels["直流1"] == "Vmp 360V · Imp 8A · Voc 420V · Isc 9.5A · 功率 80%"
    assert "直流2" not in labels
