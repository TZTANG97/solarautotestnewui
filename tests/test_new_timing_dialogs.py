# -*- coding: utf-8 -*-
"""Offscreen smoke tests for new timing-profile dialogs."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from Dialog_thailvrt import Ui_Dialog_thailvrt
from Dialog_thaiphasejump import Ui_Dialog_thaiphasejump
from Dialog_thaidynamicmppt import Ui_Dialog_thaidynamicmppt


@pytest.fixture(scope="module")
def qapp():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


@pytest.mark.parametrize(
    "ui_cls,title_part",
    (
        (Ui_Dialog_thailvrt, "LVRT"),
        (Ui_Dialog_thaiphasejump, "相角"),
        (Ui_Dialog_thaidynamicmppt, "动态"),
    ),
)
def test_new_timing_dialogs_build(qapp, ui_cls, title_part):
    dialog = QtWidgets.QDialog()
    ui = ui_cls()
    ui.setupUi(dialog)
    assert hasattr(ui, "analyzerModeSection")
    assert hasattr(ui, "timingProfileTable") or hasattr(ui, "checkBox_S3")
    assert hasattr(ui, "pushButton_TestAppend")
    assert hasattr(ui, "pushButton_ResetCount")
    assert hasattr(ui, "checkBox_S1_DC1")
    assert hasattr(ui, "checkBox_S_End") or hasattr(ui, "checkBox_S_END")
    assert title_part in dialog.windowTitle() or title_part in ui.WINDOW_TITLE
