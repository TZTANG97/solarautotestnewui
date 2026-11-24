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
    ui._nav_buttons = []
    ui._nav_by_key = {}

    def make_nav_item(text, page_index, key=None):
        btn = QtWidgets.QPushButton(text)
        btn.setProperty("page", page_index)
        ui._nav_buttons.append(btn)
        if key:
            ui._nav_by_key[key] = btn
        return btn

    def unregister_nav(btn=None, key=None):
        target = btn
        if key:
            target = ui._nav_by_key.pop(key, target)
        ui._nav_buttons = [b for b in ui._nav_buttons if b is not target]
        for k, v in list(ui._nav_by_key.items()):
            if v is target:
                ui._nav_by_key.pop(k, None)

    ui.make_nav_item = make_nav_item
    ui.unregister_nav = unregister_nav
    ui.set_nav_active_by_key = lambda key: None
    install_extra_dc_pages(ui)
    ui._extra_dc_add_btn.click()
    assert 5 in ui._extra_dc_pages
    assert "直流电源5" in ui._nav_by_key
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
    assert "直流电源5" not in ui._nav_by_key
    assert app is not None


def test_set_nav_active_skips_deleted_button():
    """删页后侧栏表若残留死引用，选中态不得再崩。"""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from ui_files.SCPI_Test import Ui_Dialog

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(win)
    dead = QtWidgets.QPushButton("dead")
    ui._nav_buttons.append(dead)
    ui._nav_by_key["dead"] = dead
    dead.deleteLater()
    app.processEvents()
    # C++ 对象销毁后仍可能留在 Python 列表里
    ui.set_nav_active_by_key("首页")
    ui.set_nav_active(None)
    assert app is not None
