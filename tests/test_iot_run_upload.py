# -*- coding: utf-8 -*-
from utils.iot_run_upload import (
    enrich_widgets_for_upload,
    procedure_steps_from_run_commands,
    snapshot_run_commands,
)


def test_enrich_fills_ac_from_dew_nominal():
    w = enrich_widgets_for_upload(
        {
            "textEdit_S1_AC_VOLT": "",
            "textEdit_S1_AC_FR": "",
            "textEdit_DEW_NominalVoltage": "230",
            "comboBox_DEW_WeightingType": "230V / 50Hz",
        }
    )
    assert w["textEdit_S1_AC_VOLT"] == "230"
    assert w["textEdit_S1_AC_FR"] == "50"


def test_snapshot_run_commands():
    rows = [
        ["AC", "write", "VOLT 230", "", "", "", "", "", 10, ""],
        ["WT", "write", "FLICKER:START", "", "", "", "ASYNC", "", "", ""],
        ["", "", ""],
    ]
    cmds = snapshot_run_commands(rows)
    assert len(cmds) == 2
    assert cmds[0]["device"] == "AC"
    assert cmds[0]["command"] == "VOLT 230"
    assert cmds[1]["flag"] == "ASYNC"
    steps = procedure_steps_from_run_commands(cmds)
    assert steps[0]["value"] == "VOLT 230"
