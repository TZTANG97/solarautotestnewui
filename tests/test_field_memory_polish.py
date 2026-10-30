# -*- coding: utf-8 -*-
"""设备页字段记忆：polish 不能因 Ui_Dialog 无 findChildren 而整段失败。"""
from __future__ import annotations

import pytest

pytest.importorskip("PyQt5.QtWidgets")

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QLineEdit,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from utils.ui_field_helpers import (
    capture_phase_memory,
    history_key_for_object_name,
    last_value,
    polish_input_widgets,
    remember_value,
    restore_phase_memory,
)


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


def test_phase_combo_remembers_three_phase(qapp, tmp_path, monkeypatch):
    ini = tmp_path / "field.ini"
    monkeypatch.setattr(
        "utils.ui_field_helpers._settings",
        lambda: QSettings(str(ini), QSettings.IniFormat),
    )
    page = QWidget()
    combo = QComboBox(page)
    combo.setObjectName("comboBox_S1_AC_2")
    combo.addItems(["单相", "三相"])
    key = history_key_for_object_name("comboBox_S1_AC_2", memory_scope="test:电压闪变")
    assert key
    remember_value(key, "三相")
    kept = capture_phase_memory(page, memory_scope="test:电压闪变")
    combo.setCurrentIndex(0)
    assert combo.currentText() == "单相"
    assert restore_phase_memory(page, kept) >= 1
    assert combo.currentText() == "三相"

    ac = QComboBox()
    ac.setObjectName("comboBox_Phase")
    ac.addItems(["单相", "三相"])
    remember_value("ac.phase", "三相")
    polish_input_widgets(ac)
    assert ac.currentText() == "三相"
    ac.setCurrentText("单相")
    assert last_value("ac.phase") == "单相"
