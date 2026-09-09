# -*- coding: utf-8 -*-
"""连续录切换：文件名列表自动填各试验单文件名。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt5 import QtWidgets

from utils.wt_recording_mode import (
    MODE_CONTINUOUS,
    MODE_SPLIT,
    UI_CONTINUOUS_FILENAME,
    resolve_continuous_filename,
    default_names_for_mode,
    wire_recording_mode_autofill,
)


def test_registry_covers_common_dialogs():
    required = {
        "Ui_Dialog_thaichonglian": "Reconn_BR",
        "Ui_Dialog_thaiguoqianpin_immun": "Immun_BR",
        "Ui_Dialog_thaixiebodianliu": "Harmonic_BR",
        "Ui_Dialog_thaistaticQU": "QU_curve",
        "Ui_Dialog_thaiStaticQU": "QU_curve",
        "Ui_Dialog_thaiguopinjiangzai": "OF_curve",
        "Ui_Dialog_thaiqianpinshengzai": "UF_curve",
    }
    for cls, name in required.items():
        assert UI_CONTINUOUS_FILENAME[cls] == name


def test_default_names_continuous_uses_registry():
    class Ui_Dialog_thaiguoqianpin_immun:
        pass

    ui = Ui_Dialog_thaiguoqianpin_immun()
    assert resolve_continuous_filename(ui) == "Immun_BR"
    assert default_names_for_mode(ui, MODE_CONTINUOUS) == ["Immun_BR"]
    assert default_names_for_mode(ui, MODE_SPLIT) == ["Immun_BR"]


def test_dialog_open_continuous_autofill(qtbot=None):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    from Dialog_thaiguoqianpin_immun import Ui_Dialog_thaiguoqianpin_immun
    from Dialog_thaichonglian import Ui_Dialog_thaichonglian
    from Dialog_thaistaticQU import Ui_Dialog_thaiStaticQU
    from components.wt_recording_mode_row import WtRecordingModeRow

    cases = [
        (Ui_Dialog_thaiguoqianpin_immun, "Immun_BR"),
        (Ui_Dialog_thaichonglian, "Reconn_BR"),
        (Ui_Dialog_thaiStaticQU, "QU_curve"),
    ]
    for UiCls, expect in cases:
        dlg = QtWidgets.QDialog()
        ui = UiCls()
        ui.setupUi(dlg)
        app.processEvents()

        assert resolve_continuous_filename(ui) == expect
        te = None
        page = ui._wtStacked.currentWidget()
        te = page.findChild(QtWidgets.QTextEdit, "textEdit_FileNameList")
        assert te is not None
        text = te.toPlainText().strip()
        assert expect in text or text == expect, (UiCls.__name__, text, expect)

        row = page.findChild(WtRecordingModeRow)
        assert row is not None
        # 先切分开录再切回连续录，应仍是试验单文件
        row.set_mode(MODE_SPLIT)
        app.processEvents()
        row.set_mode(MODE_CONTINUOUS)
        app.processEvents()
        text2 = te.toPlainText().strip()
        assert text2 == expect, (UiCls.__name__, text2, expect)
        dlg.close()


def test_fixedpf_continuous_still_single_file():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from Dialog_thaifixedPF import Ui_Dialog_thaifixedPF
    from components.wt_recording_mode_row import WtRecordingModeRow
    from utils.wt_recording_mode import MODE_CONTINUOUS, MODE_SPLIT

    dlg = QtWidgets.QDialog()
    ui = Ui_Dialog_thaifixedPF()
    ui.setupUi(dlg)
    app.processEvents()

    page = ui._wtStacked.currentWidget()
    te = page.findChild(QtWidgets.QTextEdit, "textEdit_FileNameList")
    row = page.findChild(WtRecordingModeRow)
    row.set_mode(MODE_CONTINUOUS)
    app.processEvents()
    # S3 下拉同步
    if hasattr(ui, "comboBox_S3_record_mode"):
        ui.comboBox_S3_record_mode.setCurrentIndex(0)
        app.processEvents()
    assert te.toPlainText().strip() == "FixedPF_BR"
    row.set_mode(MODE_SPLIT)
    app.processEvents()
    if hasattr(ui, "comboBox_S3_record_mode"):
        ui.comboBox_S3_record_mode.setCurrentIndex(1)
        app.processEvents()
    split_text = te.toPlainText().strip()
    assert "FixedPF_P" in split_text or split_text.startswith("FixedPF_")
    row.set_mode(MODE_CONTINUOUS)
    app.processEvents()
    if hasattr(ui, "comboBox_S3_record_mode"):
        ui.comboBox_S3_record_mode.setCurrentIndex(0)
        app.processEvents()
    assert te.toPlainText().strip() == "FixedPF_BR"
    dlg.close()


if __name__ == "__main__":
    test_registry_covers_common_dialogs()
    test_default_names_continuous_uses_registry()
    test_dialog_open_continuous_autofill()
    test_fixedpf_continuous_still_single_file()
    print("OK: continuous recording filename autofill")
