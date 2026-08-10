# -*- coding: utf-8 -*-
"""欠频升载对话框冒烟：默认频率阶梯与控件存在。"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from Dialog_thaiqianpinshengzai import Ui_Dialog_thaiqianpinshengzai


def test_underfreq_default_ladder_and_controls():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaiqianpinshengzai()
    ui.setupUi(dialog)

    assert ui.textEdit_S1_AC_FR.toPlainText() == "50"
    expected = [round(49.5 - i * 0.25, 2) for i in range(15)]
    for i, hz in enumerate(expected):
        step = i + 3
        te = getattr(ui, f"textEdit_S{step}_AC_FR")
        assert te.toPlainText() == ("%g" % hz)

    assert hasattr(ui, "pushButton_TestAppend")
    assert hasattr(ui, "pushButton_ResetCount")
    assert hasattr(ui, "label_append_count")
    assert hasattr(ui, "analyzerModeSection")
    assert ui._wtStacked.count() == 4
    dialog.deleteLater()
