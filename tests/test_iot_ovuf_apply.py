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


def test_apply_scan_list_writes_partial_phase_row(ovuf_ui):
    """IOT 工况表要写进桌面对话框：只勾 L1/L2 时 L3 不跟扫点。"""
    from utils.iot_ovuf_apply import apply_ovuf_critical_widgets

    bad = apply_ovuf_critical_widgets(
        ovuf_ui,
        {
            "textEdit_S3_AC_VOLT_End": "253",
            "textEdit_S3_TIME": "3",
            "comboBox_S3_TIME": "秒",
            "OVUF_SCAN_LIST_JSON": {
                "3": [
                    {
                        "enabled": True,
                        "kind": "V",
                        "value": "253",
                        "l1": True,
                        "l2": True,
                        "l3": False,
                        "dwell": "1",
                        "unit": "秒",
                    }
                ]
            },
        },
    )
    assert bad == []
    rows = ovuf_ui.ovufScanListS3.get_rows()
    assert len(rows) == 1
    assert rows[0]["value"] == "253"
    assert rows[0]["volt_start"] == "253" and rows[0]["volt_end"] == "253"
    assert rows[0]["l1"] is True and rows[0]["l2"] is True and rows[0]["l3"] is False
    # 没下发第 5 步列表时，保留这一页原来的一段
    assert len(ovuf_ui.ovufScanListS5.get_rows()) == 1


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


def test_empty_critical_payload_is_not_success():
    from utils.iot_ovuf_apply import apply_ovuf_critical_widgets

    # widgets 有内容但没有过欠压关键键 → 必须失败，禁止静默成功
    bad = apply_ovuf_critical_widgets(object(), {"radio_wt3000": "1"}, rounds=1)
    assert bad == ["__empty_critical__"]


def test_float_format_182_vs_182_0_equal(ovuf_ui):
    from utils.iot_ovuf_apply import apply_ovuf_critical_widgets, read_named_widget

    ovuf_ui.textEdit_S4_AC_VOLT_End.setPlainText("182")
    bad = apply_ovuf_critical_widgets(
        ovuf_ui, {"textEdit_S4_AC_VOLT_End": "182.0"}, rounds=1
    )
    assert bad == []
    assert read_named_widget(ovuf_ui, "textEdit_S4_AC_VOLT_End") in ("182", "182.0")


def test_iot_min_unit_maps_to_chinese_combo(ovuf_ui):
    """job110：IOT 下发 min，Dialog 只有「分钟」——必须写进并回读通过。"""
    from utils.iot_ovuf_apply import (
        apply_ovuf_critical_widgets,
        normalize_time_unit,
        read_named_widget,
    )

    assert normalize_time_unit("min") == "分钟"
    assert normalize_time_unit("sec") == "秒"
    ovuf_ui.comboBox_S1_TIME.setCurrentText("秒")
    ovuf_ui.comboBox_ovuf_grid_wait.setCurrentText("秒")
    bad = apply_ovuf_critical_widgets(
        ovuf_ui,
        {
            "comboBox_S1_TIME": "min",
            "textEdit_S1_TIME": "2",
            "comboBox_ovuf_grid_wait": "min",
            "textEdit_ovuf_grid_wait": "2",
        },
        rounds=2,
    )
    assert bad == []
    assert read_named_widget(ovuf_ui, "comboBox_S1_TIME") == "分钟"
    assert read_named_widget(ovuf_ui, "comboBox_ovuf_grid_wait") == "分钟"
