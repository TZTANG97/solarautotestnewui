# -*- coding: utf-8 -*-
"""Smoke tests for shared UI theme (no display required)."""

from __future__ import annotations

from components import ui_theme as theme


def test_palette_has_teal_accent():
    assert theme.ACCENT.startswith("#")
    assert theme.ACCENT == "#0d9488"
    assert theme.SIDEBAR == "#0f172a"


def test_global_qss_covers_core_widgets():
    qss = theme.global_app_qss()
    for needle in ("QPushButton", "QGroupBox", "QComboBox", "QProgressBar", "Segoe UI"):
        assert needle in qss


def test_shell_and_sidebar_qss():
    assert "QMainWindow" in theme.app_shell_qss()
    assert "sidebar" in theme.sidebar_qss()
    assert theme.ACCENT in theme.ITEM_ACTIVE_STYLE


def test_apply_app_theme_offscreen():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    theme.apply_app_theme(app)
    assert app.styleSheet()
    assert "QPushButton" in app.styleSheet()
