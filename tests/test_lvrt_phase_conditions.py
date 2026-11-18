# -*- coding: utf-8 -*-
"""LVRT PEA 分相工况：空表回退对称时序 / A-B INDEPEND / PEA 模板。"""

from __future__ import annotations

import json
import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from components.ovuf_condition_list import OvufConditionList, pea_vfrt_template_rows
from dialogs.Dialog_thailvrt import Ui_Dialog_thailvrt
from utils.Open_Save_ThaiLVRT import (
    PHASE_CONDITIONS_JSON_COLUMN,
    _apply_phase_json,
    _phase_json_from_ui,
)
from utils.lvrt_commands import (
    append_lvrt_phase_conditions,
    build_lvrt_plan,
    read_lvrt_phase_condition_rows,
)


def _checkbox(checked=True):
    return SimpleNamespace(isChecked=lambda checked=checked: checked)


def _combo(text):
    return SimpleNamespace(currentText=lambda text=text: text)


def _text(value):
    return SimpleNamespace(
        toPlainText=lambda value=value: str(value),
        currentText=lambda value=value: str(value),
    )


def _fake_condition_list(rows):
    return SimpleNamespace(
        get_rows=lambda include_disabled=False: [
            r
            for r in rows
            if include_disabled or r.get("enabled", True)
        ]
    )


def _base_lvrt_ui(*, cond_rows=None, profile=None):
    if profile is None:
        profile = [
            {
                "enabled": True,
                "label": "dip_0.2",
                "t_pre": 1,
                "t_pre_unit": "秒",
                "t_dwell": 0.2,
                "t_dwell_unit": "秒",
                "t_post": 1,
                "t_post_unit": "秒",
                "repeats": 1,
                "u_pu": 0.2,
            }
        ]
    ui = SimpleNamespace(
        checkBox_S1=_checkbox(False),
        checkBox_S2=_checkbox(False),
        checkBox_S3=_checkbox(True),
        checkBox_S_End=_checkbox(False),
        comboBox_S1_AC_2=_combo("三相"),
        textEdit_S1_AC_VOLT=_text("230"),
        textEdit_S1_AC_VOLT_2=_text("230"),
        textEdit_S1_AC_VOLT_3=_text("230"),
        textEdit_S1_AC_FR=_text("50"),
        timingProfileTable=SimpleNamespace(get_profile=lambda: profile),
        analyzerModeSection=SimpleNamespace(current_mode=lambda: "wt3000"),
        lvrtConditionList=_fake_condition_list(cond_rows or []),
    )
    for ch in range(1, 5):
        setattr(ui, "checkBox_S1_DC%d" % ch, _checkbox(False))
        setattr(ui, "checkBox_S3_DC%d" % ch, _checkbox(False))
        setattr(ui, "checkBox_S_End_DC%d" % ch, _checkbox(False))
    return ui


def test_empty_condition_list_falls_back_to_symmetric_profile():
    ui = _base_lvrt_ui(cond_rows=[])
    plan = build_lvrt_plan(ui, chroma_61800=False)
    assert plan["ok"] is True
    cmds = [str(r[2]) for r in plan["commands"]]
    assert "LIST" not in " | ".join(cmds).upper()
    # 0.2 * 230 = 46
    assert any("VOLT 46" in c or c == "VOLT 46" for c in cmds)
    assert any(c == "VOLT 230" for c in cmds)
    assert "PHAS:THREE INDEPEND" not in cmds


def test_ab_fault_uses_independ_on_chroma():
    rows = [
        {
            "enabled": True,
            "kind": "V",
            "value": "207",
            "l1": True,
            "l2": True,
            "l3": False,
            "dwell": "1",
            "unit": "秒",
        }
    ]
    out = []
    metas = append_lvrt_phase_conditions(
        out,
        rows,
        phase_mode="三相",
        nominal_voltages=(230.0, 230.0, 230.0),
        chroma_61800=True,
    )
    cmds = [str(r[2]) for r in out]
    assert "PHAS:THREE INDEPEND" in cmds
    assert "VOLT:AC 207" in cmds
    assert "VOLT:AC 230" in cmds
    assert metas[0]["phase_tag"] == "L12"
    assert "LIST" not in " | ".join(cmds).upper()


def test_three_phase_same_volt_no_independ():
    rows = [
        {
            "enabled": True,
            "kind": "V",
            "value": "207",
            "l1": True,
            "l2": True,
            "l3": True,
            "dwell": "0.5",
            "unit": "秒",
        }
    ]
    out = []
    append_lvrt_phase_conditions(
        out,
        rows,
        phase_mode="三相",
        nominal_voltages=(230.0, 230.0, 230.0),
        chroma_61800=True,
    )
    cmds = [str(r[2]) for r in out]
    assert "PHAS:THREE INDEPEND" not in cmds
    assert any("VOLT:AC 207" in c or c == "VOLT:AC 207" for c in cmds)


def test_build_plan_prefers_condition_list_over_profile():
    cond = [
        {
            "enabled": True,
            "kind": "V",
            "value": "115",
            "l1": True,
            "l2": False,
            "l3": False,
            "dwell": "1",
            "unit": "秒",
        }
    ]
    ui = _base_lvrt_ui(cond_rows=cond)
    plan = build_lvrt_plan(ui, chroma_61800=False)
    assert plan["ok"] is True
    cmds = [str(r[2]) for r in plan["commands"]]
    # Single-phase L1 fault → EACH path, not 0.2*230=46 from profile
    assert "VOLT 46" not in cmds
    assert "VOLT 115" in cmds
    assert "INST:EDIT EACH" in cmds


def test_pea_template_rows_scale_with_un():
    rows = pea_vfrt_template_rows(460)
    assert len(rows) >= 10
    values = {r["value"] for r in rows}
    assert "414.0" in values or "414" in values
    ab = [r for r in rows if r["l1"] and r["l2"] and not r["l3"]]
    assert ab
    assert all(r["kind"] == "V" for r in rows)


def test_read_lvrt_phase_condition_rows_skips_freq():
    ui = SimpleNamespace(
        lvrtConditionList=_fake_condition_list(
            [
                {
                    "enabled": True,
                    "kind": "F",
                    "value": "51",
                    "l1": True,
                    "l2": True,
                    "l3": True,
                    "dwell": "1",
                    "unit": "秒",
                },
                {
                    "enabled": True,
                    "kind": "V",
                    "value": "200",
                    "l1": True,
                    "l2": True,
                    "l3": True,
                    "dwell": "1",
                    "unit": "秒",
                },
            ]
        )
    )
    rows = read_lvrt_phase_condition_rows(ui)
    assert len(rows) == 1
    assert rows[0]["value"] == "200"


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_dialog_has_voltage_only_condition_list(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thailvrt()
    ui.setupUi(dialog)
    assert hasattr(ui, "lvrtConditionList")
    assert isinstance(ui.lvrtConditionList, OvufConditionList)
    ui.textEdit_S1_AC_VOLT.setPlainText("460")
    ui.lvrtConditionList.set_rows(pea_vfrt_template_rows(ui._lvrt_rated_un()))
    rows = ui.lvrtConditionList.get_rows()
    assert rows
    assert all(r["kind"] == "V" for r in rows)
    raw = _phase_json_from_ui(ui)
    parsed = json.loads(raw)
    assert len(parsed) == len(rows)
    assert PHASE_CONDITIONS_JSON_COLUMN == "LVRT_PHASE_CONDITIONS_JSON"
    ui.lvrtConditionList.clear_rows()
    _apply_phase_json(ui, raw)
    assert len(ui.lvrtConditionList.get_rows(include_disabled=True)) == len(parsed)
