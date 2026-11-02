# -*- coding: utf-8 -*-
"""直流电源 2/3/4 设置页应具备与 DC1 对齐的 IV 控件。"""

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_dc2_iv_widgets_present():
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication, QDialog

    from dialogs.Dialog_DC2_Setting import Ui_Dialog_DC2_Setting

    app = QApplication.instance() or QApplication([])
    assert app is not None
    dialog = QDialog()
    ui = Ui_Dialog_DC2_Setting()
    ui.setupUi(dialog)
    assert ui.textEdit_Vmp.toPlainText() == "220"
    assert "IV" in ui.pushButton_SendMessage.text() or "下发" in ui.pushButton_SendMessage.text()
    assert hasattr(ui, "pushButton_SendQueryMessage")
    assert hasattr(ui, "textEdit_ReturnMessage")
    dialog.deleteLater()


def test_dc3_dc4_iv_widgets_present():
    pytest.importorskip("PyQt5")
    from PyQt5.QtWidgets import QApplication, QDialog

    from dialogs.Dialog_DC3_Setting import Ui_Dialog_DC3_Setting
    from dialogs.Dialog_DC4_Setting import Ui_Dialog_DC4_Setting

    app = QApplication.instance() or QApplication([])
    assert app is not None
    for Ui in (Ui_Dialog_DC3_Setting, Ui_Dialog_DC4_Setting):
        dialog = QDialog()
        ui = Ui()
        ui.setupUi(dialog)
        for name in (
            "textEdit_Vmp",
            "textEdit_Voc",
            "textEdit_Imp",
            "textEdit_Isc",
            "textEdit_PF",
            "pushButton_SendMessage",
            "pushButton_SendQueryMessage",
            "textEdit_ReturnMessage",
            "lineEdit",
        ):
            assert hasattr(ui, name), name
        dialog.deleteLater()
