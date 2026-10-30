# -*- coding: utf-8 -*-
"""动态 QU / Test_PU：用户改过并保存的电压 Un% 名单，下次打开不要被长默认盖掉。"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5.QtWidgets import QApplication, QDialog

from utils.test_ui_preset import apply_test_preset, remember_voltage_ladder


LONG_DEFAULT = (
    "100,103,105,106,107,108,110,112,115,"
    "112,110,108,107,106,105,103,100,"
    "97,94,93,90,87,85"
)


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _fresh(ui_cls):
    ui = ui_cls()
    dialog = QDialog()
    ui.setupUi(dialog)
    ui._hold_dialog = dialog
    return ui


@pytest.mark.parametrize(
    "test_name,ui_cls_path,apply_name",
    [
        ("Test_PU", "Dialog_thaitestPU.Ui_Dialog_thaitestPU", "apply_testpu_standard_to_ui"),
        ("动态QU", "Dialog_thaidynamicQU.Ui_Dialog_thaidynamicQU", "apply_dynamicqu_standard_to_ui"),
    ],
)
def test_saved_voltage_list_survives_reopen_and_standard_force(
    qapp, tmp_path, monkeypatch, test_name, ui_cls_path, apply_name
):
    monkeypatch.setenv("SOLARAUTOTEST_TEST_PRESET_DIR", str(tmp_path))
    mod_name, cls_name = ui_cls_path.rsplit(".", 1)
    ui_cls = getattr(__import__(mod_name, fromlist=[cls_name]), cls_name)
    ui = _fresh(ui_cls)
    assert "103" in ui.textEdit_VoltageLadder.toPlainText()
    ui.textEdit_VoltageLadder.setPlainText("100,110,90")
    remember_voltage_ladder(test_name, ui)

    again = _fresh(ui_cls)
    # setupUi 仍会先写长默认；打开预设后才回到用户名单
    assert again.textEdit_VoltageLadder.toPlainText() == LONG_DEFAULT
    assert apply_test_preset(test_name, again)
    assert again.textEdit_VoltageLadder.toPlainText() == "100,110,90"

    if apply_name == "apply_testpu_standard_to_ui":
        from utils.iot_testpu_standard import apply_testpu_standard_to_ui

        apply_testpu_standard_to_ui(again, "de_vde", force=True, apply_defaults=True)
    else:
        from utils.iot_dynamicqu_standard import apply_dynamicqu_standard_to_ui

        apply_dynamicqu_standard_to_ui(again, "de_vde", force=True, apply_defaults=True)
    assert again.textEdit_VoltageLadder.toPlainText() == "100,110,90"
    assert "75" in again.textEdit_PowerLadder.toPlainText()


def test_cleared_voltage_list_is_remembered(qapp, tmp_path, monkeypatch):
    monkeypatch.setenv("SOLARAUTOTEST_TEST_PRESET_DIR", str(tmp_path))
    from Dialog_thaitestPU import Ui_Dialog_thaitestPU

    ui = _fresh(Ui_Dialog_thaitestPU)
    ui.textEdit_VoltageLadder.setPlainText("")
    remember_voltage_ladder("Test_PU", ui)
    again = _fresh(Ui_Dialog_thaitestPU)
    assert apply_test_preset("Test_PU", again)
    assert again.textEdit_VoltageLadder.toPlainText() == ""
