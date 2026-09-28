# -*- coding: utf-8 -*-
"""Cross-tests: field memory isolation + per-test presets + compact input fit."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PyQt5.QtWidgets")

from PyQt5.QtWidgets import (
    QApplication,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)

from utils.ui_field_helpers import history_key_for_object_name, polish_input_widgets
from utils import test_ui_preset as preset


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_device_and_test_keys_do_not_collide():
    assert history_key_for_object_name("textEdit_AC_VOLT", memory_scope="device") == "ac.volt"
    # Same-looking trial widget must NOT map to device ac.volt
    k1 = history_key_for_object_name(
        "textEdit_S1_AC_VOLT", memory_scope="test:过频降载"
    )
    k2 = history_key_for_object_name(
        "textEdit_S1_AC_VOLT", memory_scope="test:重连"
    )
    assert k1.startswith("test.")
    assert k2.startswith("test.")
    assert k1 != k2
    assert "ac.volt" not in k1
    assert history_key_for_object_name(
        "textEdit_S1_AC_VOLT", memory_scope="device"
    ) is None


def test_substring_no_longer_steals_device_keys():
    # Old bug: "_AC_VOLT" in "textEdit_AC_VOLT" also hit test.ac.volt
    assert history_key_for_object_name("textEdit_AC_VOLT") == "ac.volt"
    assert history_key_for_object_name("textEdit_S1_AC_VOLT") is None


def test_preset_roundtrip_isolates_tests(qapp, tmp_path, monkeypatch):
    monkeypatch.setenv("SOLARAUTOTEST_TEST_PRESET_DIR", str(tmp_path))

    class UiA(QWidget):
        def __init__(self):
            super().__init__()
            lay = QVBoxLayout(self)
            self.textEdit_S1_AC_FR = QTextEdit()
            self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
            self.textEdit_S1_AC_FR.setPlainText("50.5")
            lay.addWidget(self.textEdit_S1_AC_FR)

    class UiB(QWidget):
        def __init__(self):
            super().__init__()
            lay = QVBoxLayout(self)
            self.textEdit_S1_AC_FR = QTextEdit()
            self.textEdit_S1_AC_FR.setObjectName("textEdit_S1_AC_FR")
            self.textEdit_S1_AC_FR.setPlainText("49.5")
            lay.addWidget(self.textEdit_S1_AC_FR)

    a, b = UiA(), UiB()
    preset.snapshot_and_save_test_preset("过频降载", a)
    preset.snapshot_and_save_test_preset("重连", b)

    a2, b2 = UiA(), UiB()
    a2.textEdit_S1_AC_FR.setPlainText("0")
    b2.textEdit_S1_AC_FR.setPlainText("0")
    assert preset.apply_test_preset("过频降载", a2)
    assert preset.apply_test_preset("重连", b2)
    assert a2.textEdit_S1_AC_FR.toPlainText() == "50.5"
    assert b2.textEdit_S1_AC_FR.toPlainText() == "49.5"


def test_compact_textedit_not_clipped(qapp):
    root = QWidget()
    lay = QVBoxLayout(root)
    ed = QTextEdit()
    ed.setObjectName("textEdit_S1_AC_VOLT")
    ed.setFixedSize(80, 28)
    ed.setPlainText("230")
    lay.addWidget(ed)
    polish_input_widgets(root, with_memory=False, memory_scope="test:demo")
    assert ed.maximumHeight() >= 28
    ss = ed.styleSheet()
    assert "padding: 1px" in ss or "padding:1px" in ss.replace(" ", "")
    assert "font-size" not in ss
