# -*- coding: utf-8 -*-
"""闪变截图：默认存工控机，选 USB 才发 IMAGE:EXEC。"""
from __future__ import annotations

from utils.wt_screen_image import (
    CMD_SAVE_LOCAL,
    CMD_SAVE_USB,
    flicker_screen_save_command,
    flicker_screen_save_command_from_ui,
)


class _Combo:
    def __init__(self, text: str) -> None:
        self._text = text

    def currentText(self) -> str:
        return self._text


def test_default_and_blank_save_on_pc():
    assert flicker_screen_save_command("", "保存图片") == CMD_SAVE_LOCAL
    assert flicker_screen_save_command("保存至本地", "保存图片") == CMD_SAVE_LOCAL


def test_usb_sends_instrument_exec():
    assert flicker_screen_save_command("保存至USB", "保存图片") == CMD_SAVE_USB


def test_either_combo_can_skip_save():
    assert flicker_screen_save_command("保存至本地", "不保存图片") == ""
    assert flicker_screen_save_command("不保存图片", "保存图片") == ""
    assert flicker_screen_save_command("保存至USB", "不保存图片") == ""


def test_ui_reads_both_combos():
    ui = type("Ui", (), {})()
    ui.comboBox_S4_WT3000_2 = _Combo("保存图片")
    ui.comboBox_S4_WT3000_3 = _Combo("保存至USB")
    assert flicker_screen_save_command_from_ui(ui) == CMD_SAVE_USB
    ui.comboBox_S4_WT3000_3 = _Combo("保存至本地")
    assert flicker_screen_save_command_from_ui(ui) == CMD_SAVE_LOCAL
