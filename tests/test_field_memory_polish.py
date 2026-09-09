# -*- coding: utf-8 -*-
"""设备页字段记忆：polish 不能因 Ui_Dialog 无 findChildren 而整段失败。"""
from __future__ import annotations

import pytest

pytest.importorskip("PyQt5.QtWidgets")

from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QStackedWidget, QWidget

from utils.ui_field_helpers import last_value, polish_input_widgets, remember_value


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_polish_ui_object_without_findchildren_uses_stackedwidget(qapp, tmp_path, monkeypatch):
    class UiLike:
        def __init__(self, stacked):
            self.stackedWidget = stacked

    win = QMainWindow()
    stacked = QStackedWidget(win)
    win.setCentralWidget(stacked)
    page = QWidget()
    edit = QLineEdit(page)
    edit.setObjectName("lineEdit_itech_AC_IP")
    stacked.addWidget(page)

    remember_value("ac.ip", "192.168.40.210")
    n = polish_input_widgets(UiLike(stacked))
    assert n >= 1
    assert last_value("ac.ip") == "192.168.40.210"
    assert edit.text() == "192.168.40.210"
