# -*- coding: utf-8 -*-
"""Device pages must expand with window; connect button must not clip text."""
from __future__ import annotations

import sys

import pytest

pytest.importorskip("PyQt5")


@pytest.fixture(scope="module")
def qapp():
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_connect_button_not_fixed_90(qapp):
    from PyQt5.QtWidgets import QMainWindow

    from components import ui_theme as theme
    from ui_files.SCPI_Test import Ui_Dialog

    theme.set_ui_scale(1.0)
    win = QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(win)

    btn = ui.pushButton_ConnectEQUWT3000
    assert btn.minimumWidth() >= 100
    # Must not be locked to 90px
    assert btn.maximumWidth() >= 1000 or btn.maximumWidth() > 200
    fm = btn.fontMetrics()
    need = fm.horizontalAdvance(btn.text()) + 24
    assert btn.minimumWidth() >= min(need, 108)


def test_dewetron_params_expanding(qapp):
    from PyQt5.QtWidgets import QDialog

    from dialogs.Dialog_DEWETRON_Setting import Ui_Dialog_DEWETRON_Setting

    dlg = QDialog()
    ui = Ui_Dialog_DEWETRON_Setting()
    ui.setupUi(dlg)

    assert ui.treeWidget_channels.maximumWidth() >= 100000 or ui.treeWidget_channels.maximumWidth() > 400
    assert ui.lineEdit_deviceIP.maximumWidth() >= 100000 or ui.lineEdit_deviceIP.maximumWidth() > 200
    assert ui.comboBox_maxRefreshRate.minimumWidth() >= 100
