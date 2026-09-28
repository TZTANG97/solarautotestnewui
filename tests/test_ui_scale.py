# -*- coding: utf-8 -*-
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets
import pytest

from utils.ui_scale import (
    clamp_scale,
    scale_for_size,
    apply_font_scale,
    quantize_scale,
    apply_startup_ui_scale,
    install_ui_scale_watcher,
    _reset_applied_for_tests,
    _FIXED_SCALE,
)


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture(autouse=True)
def _reset_flag():
    _reset_applied_for_tests()
    yield
    _reset_applied_for_tests()


def test_scale_for_size_always_one():
    assert scale_for_size(1600, 900) == _FIXED_SCALE
    assert scale_for_size(1920, 1080) == _FIXED_SCALE
    assert scale_for_size(800, 600) == _FIXED_SCALE


def test_clamp_and_quantize_locked():
    assert clamp_scale(0.1) == 1.0
    assert clamp_scale(3.0) == 1.0
    assert quantize_scale(1.2) == 1.0


def test_font_scale_stays_fixed(qapp):
    from components.ui_theme import apply_app_theme

    apply_app_theme(qapp, scale=1.0)
    before_ss = qapp.styleSheet()
    apply_font_scale(1.0)
    pt0 = qapp.font().pointSize()
    apply_font_scale(1.2)
    pt1 = qapp.font().pointSize()
    assert pt1 == pt0
    assert qapp.styleSheet() == before_ss


def test_local_qss_not_rewritten_on_fake_scale(qapp):
    from components.ui_theme import apply_app_theme

    apply_app_theme(qapp, scale=1.0)
    win = QtWidgets.QWidget()
    te = QtWidgets.QTextEdit(win)
    te.setStyleSheet("font-size: 13px; color: #111; min-height: 24px;")
    te.setProperty("_ui_ss_orig", te.styleSheet())
    apply_font_scale(1.2, window=win)
    assert "13px" in te.styleSheet()
    assert "24px" in te.styleSheet()


def test_design_box_stays_at_design(qapp):
    from components.ui_theme import apply_app_theme

    apply_app_theme(qapp, scale=1.0)
    win = QtWidgets.QWidget()
    te = QtWidgets.QTextEdit(win)
    te.setProperty("_ui_design_max_h", 40)
    te.setProperty("_ui_design_min_h", 36)
    te.setProperty("_ui_design_min_w", 120)
    te.setMinimumHeight(36)
    te.setMaximumHeight(40)
    te.setMinimumWidth(120)
    apply_font_scale(1.2, window=win)
    assert te.maximumHeight() == 40
    assert te.minimumHeight() == 36
    assert te.minimumWidth() == 120


def test_watcher_is_noop_on_resize(qapp):
    win = QtWidgets.QMainWindow()
    win.resize(1600, 900)
    from components.ui_theme import apply_app_theme

    apply_app_theme(qapp, scale=1.0)
    ss_before = qapp.styleSheet()
    pt_before = qapp.font().pointSize()
    w = install_ui_scale_watcher(win, apply_immediately=True)
    win.resize(1920, 1080)
    for _ in range(10):
        qapp.processEvents()
    assert qapp.styleSheet() == ss_before
    assert qapp.font().pointSize() == pt_before
    assert w._last == 1.0
    assert w._busy is False


def test_startup_scale_fixed(qapp):
    win = QtWidgets.QMainWindow()
    win.resize(1920, 1080)
    from components.ui_theme import apply_app_theme

    apply_app_theme(qapp, scale=1.0)
    s = apply_startup_ui_scale(win)
    assert s == 1.0
