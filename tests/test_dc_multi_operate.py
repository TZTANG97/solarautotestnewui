# -*- coding: utf-8 -*-
"""一台交流 + 一路直流的原路径，以及多路直流按路号各写各的。"""
from __future__ import annotations

import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from components.dc_channel_rows import ensure_dc_channels
from dialogs.Dialog_thaidynamicQU import Ui_Dialog_thaidynamicQU
from utils.dynamic_qu_commands import build_dynamic_qu_plan, default_dc_iv_resolver


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaidynamicQU()
    ui.setupUi(dialog)
    return ui, dialog


def _only_dc1(ui):
    ui.checkBox_S1.setChecked(True)
    ui.comboBox_S1_AC.setCurrentText("开启")
    ui.textEdit_S1_AC_VOLT.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_2.setPlainText("230")
    ui.textEdit_S1_AC_VOLT_3.setPlainText("230")
    ui.textEdit_S1_AC_FR.setPlainText("50")
    ui.textEdit_S1_ACWaitTIME.setPlainText("1")
    ui.comboBox_S1_ACWaitTIME.setCurrentText("秒")
    ui.textEdit_S1_TIME.setPlainText("1")
    ui.comboBox_S1_TIME.setCurrentText("秒")
    for ch in (1, 2, 3, 4):
        getattr(ui, "checkBox_S1_DC%d" % ch).setChecked(ch == 1)
        getattr(ui, "comboBox_S1_DC%d" % ch).setCurrentText("开启" if ch == 1 else "关闭")
    ui.textEdit_S1_DC1_VOLT.setPlainText("400")
    ui.textEdit_S1_DC1_CURR.setPlainText("10")
    ui.textEdit_S1_DC1_Voc.setPlainText("450")
    ui.textEdit_S1_DC1_Isc.setPlainText("12")
    ui.textEdit_S1_DC1_PF.setPlainText("100")
    ui.checkBox_S2.setChecked(False)
    ui.checkBox_S3.setChecked(False)
    ui.checkBox_S_END.setChecked(False)


def _writes(plan):
    return [(r[0], r[1], str(r[2])) for r in plan["commands"] if r[1] == "write"]


def test_one_ac_and_one_dc_stays_in_order(qapp):
    """以前的台架：只连交流和直流 1。命令先交流，再只有 DC1。"""
    ui, dialog = _ui(qapp)
    try:
        _only_dc1(ui)
        plan = build_dynamic_qu_plan(ui, wt_config_dict={}, dc_iv_resolver=default_dc_iv_resolver)
        assert plan["ok"], plan.get("error") or plan.get("dc_errors")
        writes = _writes(plan)
        devices = [d for d, _op, _cmd in writes]
        assert "AC" in devices
        assert "DC1" in devices
        assert devices.index("AC") < devices.index("DC1")
        assert not any(d in ("DC2", "DC3", "DC4", "DC5") for d in devices)
    finally:
        dialog.close()


def test_added_dc_keeps_step_name_and_own_commands(qapp, monkeypatch, tmp_path):
    """新加的第 5 路控件名仍是步骤①，命令跟在 DC1 后面，电流用自己的 IV。"""
    cfg = tmp_path / "dc_channels.json"
    cfg.write_text(json.dumps({"channels": [1, 2, 3, 4, 5]}), encoding="utf-8")
    monkeypatch.setattr("utils.dc_channels._CONFIG", cfg)

    ui, dialog = _ui(qapp)
    try:
        ensure_dc_channels(ui)
        assert ui.checkBox_S1_DC5.objectName() == "checkBox_S1_DC5"
        assert ui.checkBox_S1_DC5.text() == "直流电源5"
        assert ui.checkBox_S1_DC5.isChecked() is False

        _only_dc1(ui)
        ui.checkBox_S1_DC5.setChecked(True)
        ui.comboBox_S1_DC5.setCurrentText("开启")
        ui.textEdit_S1_DC5_VOLT.setPlainText("300")
        ui.textEdit_S1_DC5_CURR.setPlainText("4")
        ui.textEdit_S1_DC5_Voc.setPlainText("360")
        ui.textEdit_S1_DC5_Isc.setPlainText("5")
        ui.textEdit_S1_DC5_PF.setPlainText("100")

        plan = build_dynamic_qu_plan(ui, wt_config_dict={}, dc_iv_resolver=default_dc_iv_resolver)
        assert plan["ok"], plan.get("error") or plan.get("dc_errors")
        writes = _writes(plan)
        devices = [d for d, _op, _cmd in writes]
        assert devices.index("AC") < devices.index("DC1") < devices.index("DC5")
        assert not any(d in ("DC2", "DC3", "DC4") for d in devices)

        dc1_iv = [cmd for dev, _op, cmd in writes if dev == "DC1" and cmd.startswith("IVC:IT")]
        dc5_iv = [cmd for dev, _op, cmd in writes if dev == "DC5" and cmd.startswith("IVC:IT")]
        assert dc1_iv and dc5_iv
        assert any(cmd.startswith("IVC:IT 10.000") or "10.000," in cmd for cmd in dc1_iv)
        assert any(cmd.startswith("IVC:IT 4.000") or "4.000," in cmd for cmd in dc5_iv)
        assert all(not cmd.startswith("IVC:IT 4.000") for cmd in dc1_iv)
        assert all(not cmd.startswith("IVC:IT 10.000") for cmd in dc5_iv)
    finally:
        dialog.close()
