# -*- coding: utf-8 -*-
from __future__ import annotations

from types import SimpleNamespace

from components.continue_test_button import sync_continue_test_button


class _Btn:
    def __init__(self):
        self.visible = False
        self.enabled = True

    def setVisible(self, v):
        self.visible = bool(v)

    def setEnabled(self, v):
        self.enabled = bool(v)


def test_sync_continue_shows_only_when_paused():
    btn = _Btn()
    ui = SimpleNamespace(pushButton_ConTest=btn)
    sync_continue_test_button(ui, paused=True)
    assert btn.visible is True
    assert btn.enabled is True
    sync_continue_test_button(ui, paused=False)
    assert btn.visible is False
    assert btn.enabled is False


def test_sync_continue_missing_button_is_noop():
    sync_continue_test_button(None, paused=True)
    sync_continue_test_button(SimpleNamespace(), paused=True)
