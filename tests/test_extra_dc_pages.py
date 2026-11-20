# -*- coding: utf-8 -*-
"""左侧设备菜单可以新增直流电源配置页，不改直流 1～4。"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from components.extra_dc_pages import install_extra_dc_pages


def test_add_from_menu_creates_dc5_page(monkeypatch, tmp_path):
    monkeypatch.setattr("utils.dc_channels._CONFIG", tmp_path / "dc_channels.json")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    ui = QtWidgets.QWidget()
    ui.stackedWidget = QtWidgets.QStackedWidget()
    ui.stackedWidget.addWidget(QtWidgets.QWidget())
    host = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(host)
    ui._dev_menu_layout = lay
    dl850 = QtWidgets.QPushButton("DL850")
    dl850._nav_base_style = ""
    lay.addWidget(dl850)
    ui._dl850_nav_item = dl850

    def make_nav_item(text, page_index, key=None):
        btn = QtWidgets.QPushButton(text)
        btn.setProperty("page", page_index)
        return btn

    ui.make_nav_item = make_nav_item
    ui.set_nav_active_by_key = lambda key: None

    install_extra_dc_pages(ui)
    labels = [lay.itemAt(i).widget().text() for i in range(lay.count())]
    assert labels[0].strip().endswith("添加直流电源")
    assert labels[1] == "DL850"
    assert ui.stackedWidget.count() == 1

    ui._extra_dc_add_btn.click()
    labels = [lay.itemAt(i).widget().text() for i in range(lay.count())]
    assert labels[0] == "直流电源5"
    assert "添加直流电源" in labels[1]
    assert labels[2] == "DL850"
    assert ui.stackedWidget.count() == 2
    assert ui.comboBox_DC5 is not None
    assert getattr(ui, "pushButton_ConnectEQUDC5", None) is not None
    assert getattr(ui, "pushButton_SetDC5Options", None) is not None
    page = ui.stackedWidget.widget(1)
    assert getattr(page, "_grid_comboBox_DC5", None) is not None
    setting = getattr(ui, "uiDC5Setting", None)
    assert setting is not None
    assert getattr(setting, "textEdit_Vmp", None) is not None
    assert getattr(setting, "pushButton_SetDC5ON", None) is not None
    assert getattr(setting, "pushButton_SetDC5OFF", None) is not None
    page_del = page.findChild(QtWidgets.QPushButton, "pushButton_RemoveDC5")
    assert page_del is not None
    assert app is not None


def test_remove_channel_hides_extra_page(monkeypatch, tmp_path):
    monkeypatch.setattr("utils.dc_channels._CONFIG", tmp_path / "dc_channels.json")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    ui = QtWidgets.QWidget()
    ui.stackedWidget = QtWidgets.QStackedWidget()
    ui.stackedWidget.addWidget(QtWidgets.QWidget())
    host = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(host)
    ui._dev_menu_layout = lay
    dl850 = QtWidgets.QPushButton("DL850")
    dl850._nav_base_style = ""
    lay.addWidget(dl850)
    ui._dl850_nav_item = dl850
    ui.make_nav_item = lambda text, page_index, key=None: QtWidgets.QPushButton(text)
    ui.set_nav_active_by_key = lambda key: None
    install_extra_dc_pages(ui)
    ui._extra_dc_add_btn.click()
    assert 5 in ui._extra_dc_pages
    from components.extra_dc_pages import _remove_page
    from utils.dc_channels import channel_numbers

    monkeypatch.setattr(
        QtWidgets.QMessageBox,
        "question",
        lambda *a, **k: QtWidgets.QMessageBox.Yes,
    )
    _remove_page(ui, 5)
    assert 5 not in channel_numbers()
    assert 5 not in ui._extra_dc_pages
    assert app is not None
