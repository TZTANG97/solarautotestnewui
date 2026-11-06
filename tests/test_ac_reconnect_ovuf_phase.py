# -*- coding: utf-8 -*-
"""AC 断线重试 / 过欠压多相勾选。"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5 import QtWidgets

from dialogs.Dialog_thaiguoqianya_pin import Ui_Dialog_thaiguoqianya_pin
from modbus_visa import ModbusVISA
from utils.ovuf_recording import build_ovuf_phase_check_list


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def ovuf_ui(qapp):
    dialog = QtWidgets.QDialog()
    ui = Ui_Dialog_thaiguoqianya_pin()
    ui.setupUi(dialog)
    ui._dialog = dialog  # 保持引用，避免 checkbox 被 GC
    return ui


def test_modbus_retry_on_winerror_10053():
    assert ModbusVISA._should_retry_send(
        "ConnectionAbortedError: [WinError 10053] 你的主机中的软件中止了一个已建立的连接。"
    )
    assert ModbusVISA._should_retry_send("VI_ERROR_CONN_LOST (1073807194)")
    assert ModbusVISA._should_retry_send("Connection reset by peer")
    assert not ModbusVISA._should_retry_send("MODBUS_EMPTY_RESPONSE: 应答缺失或过短")


def test_ovuf_phase_all_checked_default(ovuf_ui):
    # 默认 L1/L2/L3 全勾 → 三相全 T（走全相扫压分支）
    assert build_ovuf_phase_check_list(ovuf_ui) == ["T", "T", "T"]
    assert "" not in build_ovuf_phase_check_list(ovuf_ui)


def test_ovuf_phase_multi_select_independent(ovuf_ui):
    ovuf_ui.checkBox_AC_Test_L1.setChecked(True)
    ovuf_ui.checkBox_AC_Test_L2.setChecked(True)
    ovuf_ui.checkBox_AC_Test_L3.setChecked(False)
    assert build_ovuf_phase_check_list(ovuf_ui) == ["T", "T", ""]

    ovuf_ui.checkBox_AC_Test_L1.setChecked(False)
    ovuf_ui.checkBox_AC_Test_L2.setChecked(False)
    ovuf_ui.checkBox_AC_Test_L3.setChecked(True)
    assert build_ovuf_phase_check_list(ovuf_ui) == ["", "", "T"]
