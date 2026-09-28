# -*- coding: utf-8 -*-
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets
import pytest

from utils.window_fit import clamp_window_size, fit_window_to_screen


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_clamp_shrinks_to_small_screen(monkeypatch):
    from PyQt5.QtCore import QRect
    import utils.window_fit as wf

    monkeypatch.setattr(
        wf,
        "available_screen_rect",
        lambda widget=None: QRect(0, 0, 1366, 768),
    )
    w, h = clamp_window_size(1600, 900, min_w=1100, min_h=700, margin=48)
    assert w <= 1366 - 48
    assert h <= 768 - 48
    assert w >= 1100 or w == 1366 - 48


def test_clamp_keeps_design_on_large_screen(monkeypatch):
    from PyQt5.QtCore import QRect
    import utils.window_fit as wf

    monkeypatch.setattr(
        wf,
        "available_screen_rect",
        lambda widget=None: QRect(0, 0, 2560, 1440),
    )
    w, h = clamp_window_size(1600, 900, min_w=1100, min_h=700, margin=48)
    assert (w, h) == (1600, 900)


def test_fit_window_unlocks_fixed_size(qapp, monkeypatch):
    from PyQt5.QtCore import QRect
    from PyQt5.QtWidgets import QMainWindow
    import utils.window_fit as wf

    monkeypatch.setattr(
        wf,
        "available_screen_rect",
        lambda widget=None: QRect(0, 0, 1400, 800),
    )
    win = QMainWindow()
    win.setFixedSize(1600, 900)
    w, h = fit_window_to_screen(win, design_w=1600, design_h=900, min_w=1100, min_h=700)
    assert win.maximumWidth() > 1600
    assert w <= 1400 - 48
    assert h <= 800 - 48
    assert win.width() == w
    assert win.height() == h
