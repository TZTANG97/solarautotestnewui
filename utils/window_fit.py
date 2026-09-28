# -*- coding: utf-8 -*-
"""Fit Qt windows to the current screen (multi-resolution lab PCs)."""
from __future__ import annotations

from typing import Optional, Tuple

from PyQt5 import QtCore, QtWidgets


def available_screen_rect(
    widget: Optional[QtWidgets.QWidget] = None,
) -> QtCore.QRect:
    """Return available geometry of the screen that hosts ``widget`` (or primary)."""
    app = QtWidgets.QApplication.instance()
    screen = None
    if widget is not None:
        try:
            screen = widget.window().windowHandle().screen() if widget.windowHandle() else None
        except Exception:
            screen = None
        if screen is None:
            try:
                center = widget.frameGeometry().center()
                screen = QtWidgets.QApplication.screenAt(center)
            except Exception:
                screen = None
    if screen is None and app is not None:
        screen = app.primaryScreen()
    if screen is None:
        return QtCore.QRect(0, 0, 1600, 900)
    return screen.availableGeometry()


def clamp_window_size(
    design_w: int,
    design_h: int,
    *,
    min_w: int = 1024,
    min_h: int = 680,
    margin: int = 48,
    widget: Optional[QtWidgets.QWidget] = None,
) -> Tuple[int, int]:
    """
    Pick a window size for this screen.

    - Never larger than available desktop minus margin
    - Prefer design size when it fits
    - Never smaller than min_* (unless screen itself is smaller)
    """
    avail = available_screen_rect(widget)
    max_w = max(640, avail.width() - int(margin))
    max_h = max(480, avail.height() - int(margin))
    # If the screen is tiny, allow going below design mins
    eff_min_w = min(int(min_w), max_w)
    eff_min_h = min(int(min_h), max_h)
    w = min(max(int(design_w), eff_min_w), max_w)
    h = min(max(int(design_h), eff_min_h), max_h)
    return w, h


def fit_window_to_screen(
    window: QtWidgets.QWidget,
    *,
    design_w: int = 1600,
    design_h: int = 900,
    min_w: int = 1100,
    min_h: int = 700,
    margin: int = 48,
    center: bool = True,
    allow_maximize_hint: bool = True,
) -> Tuple[int, int]:
    """
    Unlock fixed size, apply min size, resize to fit this PC's screen.

    Returns the applied (width, height).
    """
    # Drop any previous hard lock from generated UI
    try:
        window.setMaximumSize(
            QtCore.QSize(QtWidgets.QWIDGETSIZE_MAX, QtWidgets.QWIDGETSIZE_MAX)
        )
    except Exception:
        pass

    avail = available_screen_rect(window)
    w, h = clamp_window_size(
        design_w,
        design_h,
        min_w=min_w,
        min_h=min_h,
        margin=margin,
        widget=window,
    )
    window.setMinimumSize(min(min_w, w), min(min_h, h))
    window.resize(w, h)

    if allow_maximize_hint:
        # Hint OS that maximize is allowed; do not force maximized.
        try:
            window.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)
        except Exception:
            pass

    if center:
        try:
            frame = window.frameGeometry()
            frame.setSize(QtCore.QSize(w, h))
            frame.moveCenter(avail.center())
            window.move(frame.topLeft())
        except Exception:
            pass

    return w, h
