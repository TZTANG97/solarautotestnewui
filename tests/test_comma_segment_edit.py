# -*- coding: utf-8 -*-
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="module")
def qapp():
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    return app


def test_rows_roundtrip_as_commas(qapp):
    from components.comma_segment_edit import CommaSegmentEdit

    box = CommaSegmentEdit(value_header="功率", unit="%")
    box.setText("100,70, 30，10")
    assert box.toPlainText() == "100,70,30,10"
    assert box.minimumWidth() >= 200
    box.setPlainText(",")
    assert box.toPlainText() == ""
    box.setPlaceholderText("功率%")
    assert box._btn_add.text() == "添加"
    assert box._btn_del.objectName() == "btnRemoveSegment"
    assert box._table.columnCount() == 2
    assert "功率" in box._table.horizontalHeaderItem(1).text()

    short = CommaSegmentEdit(value_header="Q", unit="%")
    short.setText("-100,-50,0,50,100")
    qapp.processEvents()
    assert short.toPlainText() == "-100,-50,0,50,100"
    assert short._table.rowCount() == 5

    long_box = CommaSegmentEdit()
    long_box.setText(",".join(str(100 - i) for i in range(24)))
    qapp.processEvents()
    assert long_box.toPlainText().count(",") == 23
    assert long_box._table.rowCount() == 24
    long_box._table.selectRow(0)
    long_box._remove_selected()
    assert long_box._table.rowCount() == 23


def test_ladder_matrix_preview_and_fixed_q(qapp):
    from PyQt5.QtWidgets import QDialog

    from components.ladder_matrix_panel import (
        MODE_PAIR,
        LadderMatrixPanel,
        plan_preview_text,
    )
    from dialogs.Dialog_thaifixedQ import Ui_Dialog_thaifixedQ

    text = plan_preview_text("100,70", "100,103,105", outer_name="功率", inner_name="电压")
    assert "4" in text or "3" in text
    assert "组合扫" in text
    assert "100" in text and "70" in text

    panel = LadderMatrixPanel(
        outer_default="100,70",
        inner_default="100,103,105",
    )
    qapp.processEvents()
    assert panel.outer.toPlainText() == "100,70"
    assert panel.inner.toPlainText() == "100,103,105"
    assert "组合扫" in panel.preview.text()

    pair = LadderMatrixPanel(
        mode=MODE_PAIR,
        outer_default="100,95",
        inner_default="100,103",
    )
    qapp.processEvents()
    assert "一一对应" in pair.preview.text()
    assert "外循环" not in pair.preview.text()

    dialog = QDialog()
    ui = Ui_Dialog_thaifixedQ()
    ui.setupUi(dialog)
    dialog.resize(1500, 860)
    ui._switch_step(2)
    dialog.show()
    qapp.processEvents()
    assert ui.textEdit_PowerLadder.toPlainText()
    assert ui.textEdit_QLadder.toPlainText()
    assert "组合扫" in ui._ladder_matrix.preview.text()
    dialog.close()


def test_read_app_version_from_file(tmp_path):
    from utils.app_version import read_app_version

    (tmp_path / "VERSION").write_text("20261029.1619\nbuilt=x\n", encoding="utf-8")
    assert read_app_version([tmp_path]) == "20261029.1619"
    assert read_app_version([tmp_path / "missing"]) == "源码未打包"
