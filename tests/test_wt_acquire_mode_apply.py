# -*- coding: utf-8 -*-
"""网页下发的宏/SCPI 要写到每个 WT 型号页，而不是只写当前页。"""
from utils.iot_ui_handoff import apply_widget_values
from utils.wt_acquire_mode import COMBO_NAME, apply_mode_across


class _Combo:
    def __init__(self):
        self.idx = -1

    def setCurrentIndex(self, index):
        self.idx = index


class _Page:
    def __init__(self):
        self.combo = _Combo()

    def findChild(self, _cls, name):
        if name == COMBO_NAME:
            return self.combo
        return None


class _Stack:
    def __init__(self, pages):
        self.pages = pages

    def count(self):
        return len(self.pages)

    def widget(self, index):
        return self.pages[index]


class _Root:
    def __init__(self, pages):
        self._wtStacked = _Stack(pages)

    def findChild(self, _cls, _name):
        return None


def test_apply_mode_across_writes_every_wt_page():
    pages = [_Page(), _Page()]
    root = _Root(pages)
    assert apply_mode_across(root, "scpi") == 2
    assert pages[0].combo.idx == 1
    assert pages[1].combo.idx == 1
    assert apply_mode_across(root, "macro") == 2
    assert pages[0].combo.idx == 0


def test_handoff_accepts_web_acquire_mode():
    pages = [_Page(), _Page()]
    root = _Root(pages)
    missing = apply_widget_values(root, {"wt_acquire_mode": "scpi", "comboBox_wt_acquire_mode": 1})
    assert missing == []
    assert pages[0].combo.idx == 1
    assert pages[1].combo.idx == 1
