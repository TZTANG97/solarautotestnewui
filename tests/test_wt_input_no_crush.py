# -*- coding: utf-8 -*-
"""Regression: polish must not crush WT FileNameList / SavePath."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets
import pytest

from components.ui_theme import apply_app_theme
from components.wt_config_content import build_wt3000_content
from utils.ui_field_helpers import polish_input_widgets
from utils.ui_scale import apply_font_scale, scale_for_size


@pytest.fixture
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_polish_does_not_crush_wt_filename_and_path(qapp):
    apply_app_theme(qapp, scale=1.0)

    class Host:
        pass

    host = Host()
    scroll = build_wt3000_content(host)
    polish_input_widgets(scroll, with_memory=False)

    fn = host.textEdit_FileNameList
    assert int(fn.maximumHeight()) >= 120, fn.maximumHeight()
    assert int(fn.minimumHeight()) >= 56, fn.minimumHeight()
    assert fn.minimumWidth() != fn.maximumWidth() or fn.maximumWidth() > 500

    path = host.textEdit_SavePath
    assert int(path.minimumWidth()) >= 220, path.minimumWidth()
    assert int(path.maximumHeight()) <= 56
    assert int(path.maximumHeight()) >= 40

    stop = host.textEdit_StopTime
    assert int(stop.maximumHeight()) >= 40
    assert int(stop.minimumWidth()) >= 120


def test_maximize_keeps_fixed_field_sizes(qapp):
    """Window grow must not blow up WT field heights (scale locked to 1.0)."""
    apply_app_theme(qapp, scale=1.0)

    class Host:
        pass

    host = Host()
    win = QtWidgets.QMainWindow()
    win.resize(1920, 1080)
    scroll = build_wt3000_content(host)
    win.setCentralWidget(scroll)
    polish_input_widgets(scroll, with_memory=False)
    apply_font_scale(scale_for_size(1920, 1080), window=win)
    qapp.processEvents()

    assert host.textEdit_SavePath.maximumHeight() <= 56
    assert host.textEdit_SavePath.minimumWidth() >= 220
    assert host.textEdit_FileNameList.maximumHeight() >= 120
    assert host.textEdit_StopTime.maximumHeight() <= 56
