# -*- coding: utf-8 -*-
"""Smoke tests for TimelineWidget card layout."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_timeline_steps_use_cards():
    from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit

    app = QApplication.instance() or QApplication([])
    from components.timeline import TimelineWidget, param_row, _DOT_COLOR, theme

    assert _DOT_COLOR == theme.ACCENT
    tw = TimelineWidget()
    tw.addStep("设备连接", param_row([("IP", QLineEdit())]))
    tw.addStep("相位选择", QLabel("单相"))
    tw.finalize()
    assert len(tw._steps) == 2
    card = tw._steps[0].findChild(type(tw._steps[0]), "timelineStepCard")
    # findChild by objectName
    from PyQt5.QtWidgets import QWidget

    cards = [
        c
        for c in tw._steps[0].findChildren(QWidget)
        if c.objectName() == "timelineStepCard"
    ]
    assert cards, "expected timeline step card"
    assert "border-radius" in cards[0].styleSheet()
