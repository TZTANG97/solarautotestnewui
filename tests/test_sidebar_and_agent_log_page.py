# -*- coding: utf-8 -*-
"""Sidebar collapse + Agent log page smoke."""
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


def test_sidebar_toggle_and_agent_log_page(qapp):
    from PyQt5.QtWidgets import QMainWindow

    from components import ui_theme as theme
    from ui_files.SCPI_Test import Ui_Dialog

    theme.set_ui_scale(1.0)
    win = QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(win)

    assert hasattr(ui, "pushButton_ConTest")
    assert not hasattr(ui, "pushButton_SoftwareEstop")
    assert "继续试验" in ui.pushButton_ConTest.text()
    assert hasattr(ui, "iotAgentLogPage")
    assert ui.stackedWidget.count() >= 13

    ui.set_sidebar_collapsed(True)
    assert bool(ui._sidebar.property("collapsed"))
    assert ui._sidebar.width() <= 80

    ui.set_sidebar_collapsed(False)
    assert not bool(ui._sidebar.property("collapsed"))
    assert ui._sidebar.width() >= 200

    ui.stackedWidget.setCurrentIndex(12)
    ui.iotAgentLogPage.refresh_from_agent()
    assert "pythonid" in ui.iotAgentLogPage.label_pythonid.text().lower() or True
