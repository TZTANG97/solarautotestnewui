# -*- coding: utf-8 -*-
"""统一安全关机命令测试。"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from utils.active_p_commands import build_active_p_plan
from utils.dynamic_cosphi_commands import build_dynamic_cosphi_plan
from utils.dynamic_qu_commands import build_dynamic_qu_plan
from utils.fixed_q_commands import build_fixed_q_plan
from utils.frequency_adaptability_commands import build_frequency_adaptability_plan
from utils.rapid_volt_commands import build_rapid_volt_plan
from utils.reactive_qacc_commands import build_reactive_qacc_plan
from utils.reactive_qcap_commands import build_reactive_qcap_plan
from utils.reactive_qin_commands import build_reactive_qin_plan
from utils.rocof_commands import build_rocof_plan
from utils.safe_shutdown import (
    BLUESIGHT_DC_OFF_SETTLE_01S,
    append_ui_forced_shutdown_step,
    build_forced_shutdown_rows,
    enabled_shutdown_dc_channels,
    force_end_combos_off,
    s1_and_step_dc,
)
from utils.voltage_adaptability_commands import build_voltage_adaptability_plan


class _CheckBox:
    def __init__(self, checked):
        self._checked = checked

    def isChecked(self):
        return self._checked


class _ComboBox:
    def __init__(self, text):
        self._text = text

    def currentText(self):
        return self._text

    def setCurrentText(self, text):
        self._text = text


def test_forced_shutdown_is_dc_then_bluesight_wait_then_ac():
    rows = build_forced_shutdown_rows(
        dc_channels=[3, 1, 2],
        per_dc_factor={"0": "Chroma", "1": "Bluesight", "2": "Itech"},
    )

    output_rows = [row for row in rows if row[1] == "write"]
    assert [(row[0], row[2]) for row in output_rows] == [
        ("DC1", "OUTP OFF"),
        ("DC2", "OUTP OFF"),
        ("DC3", "OUTP OFF"),
        ("AC", "OUTP OFF"),
    ]
    assert all(row[2] != "OUTP ON" for row in rows)

    ac_off_index = next(
        index
        for index, row in enumerate(rows)
        if row[0] == "AC" and row[1] == "write"
    )
    assert all(
        index < ac_off_index
        for index, row in enumerate(rows)
        if row[0].startswith("DC") and row[1] == "write"
    )
    assert any(
        row[0] == "AC"
        and row[1] == "query"
        and int(row[8]) >= BLUESIGHT_DC_OFF_SETTLE_01S
        for row in rows[:ac_off_index]
    )


def test_append_ui_forced_shutdown_step_forces_off_when_requested():
    ui = SimpleNamespace(
        checkBox_S1_DC1=_CheckBox(True),
        checkBox_S1_DC2=_CheckBox(False),
        checkBox_S1_DC3=_CheckBox(False),
        checkBox_S1_DC4=_CheckBox(False),
        checkBox_S_End_DC1=_CheckBox(True),
        checkBox_S_End_DC2=_CheckBox(False),
        checkBox_S_End_DC3=_CheckBox(False),
        checkBox_S_End_DC4=_CheckBox(False),
        comboBox_S_End_AC=_ComboBox("开启"),
        comboBox_S_End_DC1=_ComboBox("开启"),
        comboBox_S_End_DC2=_ComboBox("关闭"),
        comboBox_S_End_DC3=_ComboBox("关闭"),
        comboBox_S_End_DC4=_ComboBox("关闭"),
    )
    commands: list = []
    steps: list = []
    logs: list = []

    channels = append_ui_forced_shutdown_step(
        commands,
        steps,
        ui,
        per_dc_factor={"0": "Bluesight"},
        log=logs.append,
        tag="10min过压保护",
        respect_keep_on=False,
    )

    assert channels == [1]
    assert ui.comboBox_S_End_AC.currentText() == "关闭"
    assert ui.comboBox_S_End_DC1.currentText() == "关闭"
    writes = [(r[0], r[2]) for r in commands if r[1] == "write"]
    assert writes == [("DC1", "OUTP OFF"), ("AC", "OUTP OFF")]
    assert any("强制改为关闭" in m for m in logs)
    assert steps and steps[0] is not commands
    assert len(steps[0]) == len(commands)


def test_append_ui_keeps_output_when_combos_on():
    """追加中间轮：关机步设「开启」则不写 OUTP OFF。"""
    ui = SimpleNamespace(
        checkBox_S1_DC1=_CheckBox(True),
        checkBox_S1_DC2=_CheckBox(False),
        checkBox_S1_DC3=_CheckBox(False),
        checkBox_S1_DC4=_CheckBox(False),
        checkBox_S_End_DC1=_CheckBox(True),
        checkBox_S_End_DC2=_CheckBox(False),
        checkBox_S_End_DC3=_CheckBox(False),
        checkBox_S_End_DC4=_CheckBox(False),
        comboBox_S_End_AC=_ComboBox("开启"),
        comboBox_S_End_DC1=_ComboBox("开启"),
        comboBox_S_End_DC2=_ComboBox("关闭"),
        comboBox_S_End_DC3=_ComboBox("关闭"),
        comboBox_S_End_DC4=_ComboBox("关闭"),
    )
    commands: list = []
    steps: list = []
    logs: list = []

    channels = append_ui_forced_shutdown_step(
        commands,
        steps,
        ui,
        per_dc_factor={"0": "Bluesight"},
        log=logs.append,
        tag="10min过压保护",
    )

    assert channels == []
    assert commands == []
    assert steps == []
    assert ui.comboBox_S_End_AC.currentText() == "开启"
    assert ui.comboBox_S_End_DC1.currentText() == "开启"
    assert any("保持输出不关断" in m for m in logs)


def test_append_ui_shuts_down_only_channels_set_to_off():
    ui = SimpleNamespace(
        checkBox_S1_DC1=_CheckBox(True),
        checkBox_S1_DC2=_CheckBox(True),
        checkBox_S1_DC3=_CheckBox(False),
        checkBox_S1_DC4=_CheckBox(False),
        checkBox_S_End_DC1=_CheckBox(True),
        checkBox_S_End_DC2=_CheckBox(True),
        checkBox_S_End_DC3=_CheckBox(False),
        checkBox_S_End_DC4=_CheckBox(False),
        comboBox_S_End_AC=_ComboBox("关闭"),
        comboBox_S_End_DC1=_ComboBox("关闭"),
        comboBox_S_End_DC2=_ComboBox("开启"),
        comboBox_S_End_DC3=_ComboBox("关闭"),
        comboBox_S_End_DC4=_ComboBox("关闭"),
    )
    commands: list = []
    steps: list = []

    channels = append_ui_forced_shutdown_step(commands, steps, ui)
    assert channels == [1]
    writes = [(r[0], r[2]) for r in commands if r[1] == "write"]
    assert writes == [("DC1", "OUTP OFF"), ("AC", "OUTP OFF")]


def test_bluesight_wait_has_hard_minimum_and_only_for_selected_channel():
    rows = build_forced_shutdown_rows(
        dc_channels=[1],
        per_dc_factor={"0": "bluesight"},
        settle_01s=1,
    )
    assert max(int(row[8]) for row in rows if row[8] != "") >= 50

    rows_without_blue = build_forced_shutdown_rows(
        dc_channels=[1],
        per_dc_factor={"0": "Chroma", "1": "Bluesight"},
    )
    assert all(
        int(row[8]) < BLUESIGHT_DC_OFF_SETTLE_01S
        for row in rows_without_blue
        if row[8] != ""
    )


def test_shutdown_channels_require_s1_and_end():
    ui = SimpleNamespace(
        checkBox_S1_DC1=_CheckBox(True),
        checkBox_S1_DC2=_CheckBox(False),
        checkBox_S1_DC3=_CheckBox(True),
        checkBox_S_END_DC1=_CheckBox(True),
        checkBox_S_END_DC2=_CheckBox(True),
        checkBox_S_END_DC3=_CheckBox(False),
    )

    assert enabled_shutdown_dc_channels(
        ui,
        end_fmt="checkBox_S_END_DC%d",
        channels=range(1, 5),
    ) == [1]
    assert s1_and_step_dc(ui, "checkBox_S_END_DC%d", 1) is True
    assert s1_and_step_dc(ui, "checkBox_S_END_DC%d", 2) is False
    assert s1_and_step_dc(ui, "checkBox_S_END_DC%d", 4) is False


def test_force_end_combos_off_rewrites_only_on_values():
    messages = []
    ui = SimpleNamespace(
        comboBox_S_End_AC=_ComboBox("开启"),
        comboBox_S_End_DC1=_ComboBox("关闭"),
    )

    changed = force_end_combos_off(
        ui,
        ["comboBox_S_End_AC", "comboBox_S_End_DC1", "missing"],
        log=messages.append,
        tag="test",
    )

    assert changed == ["comboBox_S_End_AC"]
    assert ui.comboBox_S_End_AC.currentText() == "关闭"
    assert ui.comboBox_S_End_DC1.currentText() == "关闭"
    assert len(messages) == 1


_BUILDERS = [
    (build_active_p_plan, "checkBox_S_END", "checkBox_S_END_DC%d"),
    (build_fixed_q_plan, "checkBox_S_END", "checkBox_S_END_DC%d"),
    (build_reactive_qcap_plan, "checkBox_S_END", "checkBox_S_END_DC%d"),
    (build_reactive_qin_plan, "checkBox_S_END", "checkBox_S_END_DC%d"),
    (build_reactive_qacc_plan, "checkBox_S_END", "checkBox_S_END_DC%d"),
    (build_dynamic_cosphi_plan, "checkBox_S_END", "checkBox_S_END_DC%d"),
    (build_dynamic_qu_plan, "checkBox_S_END", "checkBox_S_END_DC%d"),
    (
        build_frequency_adaptability_plan,
        "checkBox_S_End",
        "checkBox_S_End_DC%d",
    ),
    (
        build_voltage_adaptability_plan,
        "checkBox_S_End",
        "checkBox_S_End_DC%d",
    ),
    (build_rocof_plan, "checkBox_S_End", "checkBox_S_End_DC%d"),
    (build_rapid_volt_plan, "checkBox_S_End", "checkBox_S_End_DC%d"),
]


def _minimal_shutdown_ui(end_step_name, end_dc_fmt):
    attrs = {
        "comboBox_S1_AC_2": _ComboBox("单相"),
        "checkBox_S1": _CheckBox(False),
        "checkBox_S2": _CheckBox(False),
        "checkBox_S3": _CheckBox(False),
        end_step_name: _CheckBox(True),
    }
    for channel in range(1, 5):
        attrs["checkBox_S1_DC%d" % channel] = _CheckBox(channel == 1)
        attrs[end_dc_fmt % channel] = _CheckBox(channel in (1, 2))
    return SimpleNamespace(**attrs)


@pytest.mark.parametrize("builder,end_step_name,end_dc_fmt", _BUILDERS)
def test_all_command_builders_use_forced_s1_and_end_shutdown(
    builder, end_step_name, end_dc_fmt
):
    ui = _minimal_shutdown_ui(end_step_name, end_dc_fmt)
    plan = builder(ui, per_dc_factor={"0": "Bluesight"})

    assert plan["ok"] is True
    shutdown_rows = plan["steps"][-1]
    output_rows = [row for row in shutdown_rows if row[1] == "write"]
    assert [(row[0], row[2]) for row in output_rows] == [
        ("DC1", "OUTP OFF"),
        ("AC", "OUTP OFF"),
    ]
    assert all(row[2] != "OUTP ON" for row in shutdown_rows)
    assert any(
        row[1] == "query"
        and row[8] != ""
        and int(row[8]) >= BLUESIGHT_DC_OFF_SETTLE_01S
        for row in shutdown_rows
    )
