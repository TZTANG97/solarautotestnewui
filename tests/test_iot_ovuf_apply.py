# -*- coding: utf-8 -*-
"""IOT → 过欠压 Dialog：182/2秒 等关键字段必须写进控件，不被旧记忆盖掉。"""
from __future__ import annotations

import os

import pytest

pytest.importorskip("PyQt5.QtWidgets")

from PyQt5.QtWidgets import QApplication, QDialog

# offscreen：CI / 无显示环境可跑
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def ovuf_ui(qapp):
    from dialogs.Dialog_thaiguoqianya_pin import Ui_Dialog_thaiguoqianya_pin

    dlg = QDialog()
    ui = Ui_Dialog_thaiguoqianya_pin()
    ui.setupUi(dlg)
    # 模拟本机字段记忆旧脏值（用户看到的 181.7 / 11）
    ui.textEdit_S4_AC_VOLT_End.setPlainText("181.7")
    ui.textEdit_S4_TIME.setPlainText("11")
    ui.comboBox_S4_TIME.setCurrentText("秒")
    ui.textEdit_S5_AC_FR_End.setPlainText("51.5")
    ui.textEdit_S5_TIME.setPlainText("11")
    ui.textEdit_S6_AC_FR_End.setPlainText("47.5")
    yield ui
    dlg.close()


def test_apply_overwrites_stale_end_and_dwell(ovuf_ui):
    from utils.iot_ovuf_apply import apply_ovuf_critical_widgets, read_named_widget

    job_widgets = {
        "textEdit_S4_AC_VOLT_End": "182",
        "textEdit_S4_Step_Size": "1.15",
        "textEdit_S4_TIME": "2",
        "comboBox_S4_TIME": "秒",
        "textEdit_S5_AC_FR_End": "51.7",
        "textEdit_S5_Step_Size": "0.05",
        "textEdit_S5_TIME": "1",
        "comboBox_S5_TIME": "秒",
        "textEdit_S6_AC_FR_End": "47.2",
        "textEdit_S6_TIME": "1",
        "comboBox_S6_TIME": "秒",
    }
    bad = apply_ovuf_critical_widgets(ovuf_ui, job_widgets, rounds=2)
    assert bad == []
    assert read_named_widget(ovuf_ui, "textEdit_S4_AC_VOLT_End") == "182"
    assert read_named_widget(ovuf_ui, "textEdit_S4_TIME") == "2"
    assert read_named_widget(ovuf_ui, "textEdit_S5_AC_FR_End") == "51.7"
    assert read_named_widget(ovuf_ui, "textEdit_S5_TIME") == "1"
    assert read_named_widget(ovuf_ui, "textEdit_S6_AC_FR_End") == "47.2"


def test_uv_ladder_keeps_user_end_182():
    """扫压列表必须包含用户终点 182，不能只停在步长对齐点 181.7。"""
    start, end, step = 230.0, 182.0, 1.15
    pts = []
    cur = start
    while end < cur:
        pts.append(round(cur, 2))
        cur = cur - step
    pts.append(round(end, 2))
    assert pts[-1] == 182.0
    assert pts.count(182.0) == 1
    # 181.7 = 230-42*1.15，是越过终点后的瞬时 cur，不应单独作为终点写回 Dialog
    assert abs((230.0 - 42 * 1.15) - 181.7) < 1e-9
