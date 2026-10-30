# -*- coding: utf-8 -*-
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="module")
def qapp():
    from PyQt5.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def test_voltage_power_same_row_defaults(qapp):
    from components.voltage_power_ladder_edit import VoltagePowerLadderEdit

    box = VoltagePowerLadderEdit(default_power="100", visible_rows=10)
    box.voltage.setObjectName("textEdit_VoltageLadder")
    box.power.setObjectName("textEdit_PowerLadder")
    box.voltage.setText("100,103,105")
    qapp.processEvents()
    assert box.voltage.toPlainText() == "100,103,105"
    assert box.power.toPlainText() == "100,100,100"
    assert box.voltage.objectName() == "textEdit_VoltageLadder"
    assert box.power.objectName() == "textEdit_PowerLadder"

    box.power.setText("100,95,90")
    assert box.power.toPlainText() == "100,95,90"
    box._fill_default_power()
    assert box.power.toPlainText() == "100,100,100"


def test_staticqu_dialog_uses_voltage_power_table(qapp):
    from PyQt5.QtWidgets import QDialog

    from dialogs.Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU

    dlg = QDialog()
    ui = Ui_Dialog_thaiStaticQU()
    ui.setupUi(dlg)
    qapp.processEvents()
    assert hasattr(ui, "_vp_ladder")
    assert ui.textEdit_VoltageLadder.objectName() == "textEdit_VoltageLadder"
    assert ui.textEdit_PowerLadder.objectName() == "textEdit_PowerLadder"
    assert "100" in ui.textEdit_VoltageLadder.toPlainText()
    assert ui.textEdit_PowerLadder.toPlainText().startswith("100")
    dlg.close()
