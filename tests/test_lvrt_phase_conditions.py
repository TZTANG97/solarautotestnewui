# -*- coding: utf-8 -*-
"""LVRT 时序表分相：对称回退 / A-B INDEPEND / PEA 模板。"""

from __future__ import annotations

import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thailvrt import Ui_Dialog_thailvrt
from utils.lvrt_commands import (
    append_lvrt_profile,
    build_lvrt_plan,
    pea_lvrt_template_profile,
    phase_masked_voltages,
)
from utils.timing_profile import LVRT_SCHEMA, validate_profile


def _checkbox(checked=True):
    return SimpleNamespace(isChecked=lambda checked=checked: checked)


def _combo(text):
    return SimpleNamespace(currentText=lambda text=text: text)


def _text(value):
    return SimpleNamespace(
        toPlainText=lambda value=value: str(value),
        currentText=lambda value=value: str(value),
    )


def _base_lvrt_ui(*, profile=None):
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
                "l1": True,
                "l2": True,
                "l3": True,
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
    )
    for ch in range(1, 5):
        setattr(ui, "checkBox_S1_DC%d" % ch, _checkbox(False))
        setattr(ui, "checkBox_S3_DC%d" % ch, _checkbox(False))
        setattr(ui, "checkBox_S_End_DC%d" % ch, _checkbox(False))
    return ui


def test_phase_masked_all_selected_scales_all():
    assert phase_masked_voltages((230.0, 230.0, 230.0), 0.9) == [207.0, 207.0, 207.0]


def test_phase_masked_ab_keeps_c_rated():
    assert phase_masked_voltages(
        (230.0, 230.0, 230.0), 0.9, l1=True, l2=True, l3=False
    ) == [207.0, 207.0, 230.0]


def test_symmetric_profile_no_independ():
    profile = [
        {
            "enabled": True,
            "label": "dip",
            "t_pre": 0,
            "t_pre_unit": "秒",
            "t_dwell": 0.2,
            "t_dwell_unit": "秒",
            "t_post": 0,
            "t_post_unit": "秒",
            "repeats": 1,
            "u_pu": 0.2,
            "l1": True,
            "l2": True,
            "l3": True,
        }
    ]
    rows = []
    append_lvrt_profile(
        rows,
        profile,
        phase_mode="三相",
        nominal_voltages=(230.0, 230.0, 230.0),
        chroma_61800=True,
    )
    cmds = [str(r[2]) for r in rows]
    assert "LIST" not in " | ".join(cmds).upper()
    assert "PHAS:THREE INDEPEND" not in cmds
    assert any("VOLT:AC 46" in c or c == "VOLT:AC 46" for c in cmds)
    # 单行末尾不再插并网等待
    assert "LVRT_GRID_RECOVERY" not in cmds


def test_grid_recovery_between_two_rows():
    profile = [
        {
            "enabled": True,
            "label": "a",
            "t_pre": 0,
            "t_pre_unit": "秒",
            "t_dwell": 1,
            "t_dwell_unit": "秒",
            "t_post": 0,
            "t_post_unit": "秒",
            "repeats": 1,
            "u_pu": 0.9,
            "l1": True,
            "l2": True,
            "l3": True,
        },
        {
            "enabled": True,
            "label": "b",
            "t_pre": 0,
            "t_pre_unit": "秒",
            "t_dwell": 1,
            "t_dwell_unit": "秒",
            "t_post": 0,
            "t_post_unit": "秒",
            "repeats": 1,
            "u_pu": 0.5,
            "l1": True,
            "l2": True,
            "l3": True,
        },
    ]
    rows = []
    append_lvrt_profile(
        rows,
        profile,
        phase_mode="三相",
        nominal_voltages=(230.0, 230.0, 230.0),
        chroma_61800=False,
        grid_wait_01s=50,
    )
    markers = [str(r[2]) for r in rows if r and r[1] == "wait"]
    assert markers.count("LVRT_GRID_RECOVERY") == 1
    # 回额定在并网等待之前：最后一条 wait 前应有 VOLT 230
    recovery_idx = next(
        i for i, r in enumerate(rows) if r and r[2] == "LVRT_GRID_RECOVERY"
    )
    before = [str(r[2]) for r in rows[:recovery_idx] if r and r[1] == "write"]
    assert "VOLT 230" in before
    assert rows[recovery_idx][9] == 50


def test_ab_profile_uses_independ_on_chroma():
    profile = [
        {
            "enabled": True,
            "label": "ab",
            "t_pre": 1,
            "t_pre_unit": "秒",
            "t_dwell": 10,
            "t_dwell_unit": "秒",
            "t_post": 3,
            "t_post_unit": "秒",
            "repeats": 1,
            "u_pu": 0.9,
            "l1": True,
            "l2": True,
            "l3": False,
        }
    ]
    rows = []
    metas = append_lvrt_profile(
        rows,
        profile,
        phase_mode="三相",
        nominal_voltages=(230.0, 230.0, 230.0),
        chroma_61800=True,
    )
    cmds = [str(r[2]) for r in rows]
    assert "PHAS:THREE INDEPEND" in cmds
    assert "VOLT:AC 207" in cmds
    assert "VOLT:AC 230" in cmds
    assert metas[0]["l3"] is False


def test_build_plan_with_phase_mask():
    profile = [
        {
            "enabled": True,
            "label": "l1_only",
            "t_pre": 0,
            "t_pre_unit": "秒",
            "t_dwell": 1,
            "t_dwell_unit": "秒",
            "t_post": 0,
            "t_post_unit": "秒",
            "repeats": 1,
            "u_pu": 0.5,
            "l1": True,
            "l2": False,
            "l3": False,
        }
    ]
    ui = _base_lvrt_ui(profile=profile)
    plan = build_lvrt_plan(ui, chroma_61800=False)
    assert plan["ok"] is True
    cmds = [str(r[2]) for r in plan["commands"]]
    assert "INST:EDIT EACH" in cmds
    assert "VOLT 115" in cmds
    assert "VOLT 230" in cmds


def test_pea_template_validates_and_has_ab():
    rows = pea_lvrt_template_profile()
    validated = validate_profile(rows, LVRT_SCHEMA)
    assert len(validated) >= 10
    ab = [r for r in validated if r["l1"] and r["l2"] and not r["l3"]]
    assert ab
    assert any(abs(r["u_pu"] - 0.9) < 1e-9 for r in ab)


def test_old_profile_without_l_flags_defaults_true():
    rows = validate_profile(
        [
            {
                "enabled": True,
                "label": "legacy",
                "t_pre": 1,
                "t_pre_unit": "秒",
                "t_dwell": 0.15,
                "t_dwell_unit": "秒",
                "t_post": 3,
                "t_post_unit": "秒",
                "repeats": 1,
                "u_pu": 0.2,
            }
        ],
        LVRT_SCHEMA,
    )
    assert rows[0]["l1"] is True
    assert rows[0]["l2"] is True
    assert rows[0]["l3"] is True


def test_enabled_row_requires_at_least_one_phase():
    from utils.timing_profile import TimingProfileValidationError

    with pytest.raises(TimingProfileValidationError):
        validate_profile(
            [
                {
                    "enabled": True,
                    "label": "none",
                    "t_pre": 0,
                    "t_pre_unit": "秒",
                    "t_dwell": 1,
                    "t_dwell_unit": "秒",
                    "t_post": 0,
                    "t_post_unit": "秒",
                    "repeats": 1,
                    "u_pu": 0.5,
                    "l1": False,
                    "l2": False,
                    "l3": False,
                }
            ],
            LVRT_SCHEMA,
        )


def test_file_names_include_phase_tag():
    profile = [
        {
            "enabled": True,
            "label": "ab",
            "t_pre": 0,
            "t_pre_unit": "秒",
            "t_dwell": 1,
            "t_dwell_unit": "秒",
            "t_post": 0,
            "t_post_unit": "秒",
            "repeats": 1,
            "u_pu": 0.9,
            "l1": True,
            "l2": True,
            "l3": False,
        }
    ]
    ui = _base_lvrt_ui(profile=profile)
    plan = build_lvrt_plan(ui, chroma_61800=False)
    assert plan["ok"] is True
    assert any("L12" in str(n) for n in plan.get("file_names") or [])


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_dialog_single_table_with_phase_columns(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thailvrt()
    ui.setupUi(dialog)
    assert hasattr(ui, "timingProfileTable")
    assert not hasattr(ui, "lvrtConditionList")
    assert hasattr(ui, "pushButton_PeaLvrtTemplate")
    ui.pushButton_PeaLvrtTemplate.click()
    profile = ui.timingProfileTable.get_profile()
    assert any(not r["l3"] for r in profile)
